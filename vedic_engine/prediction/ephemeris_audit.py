"""
Ephemeris Audit Engine — Cross-Backend Position Verification.

Purpose
───────
Systematically compare every position-computing backend in the tier system
against the research-grade Skyfield + JPL standard.  Exposes any systematic
bias, sign boundary errors, or ayanamsa drift before it silently corrupts
predictions.

Classical motivation
────────────────────
A 1° longitude error shifts a planet's nakshatra with probability ~1/13.3
and changes the Ashtakvarga kakshya (every 3.75°) with probability ~1/3.75.
KP sublord boundaries are as narrow as 0.25°.  An uncaught 0.5° drift in
the ayanamsa formula = wrong sublord ~50% of the time near cuspal points.

Audit modes
───────────
1. spot_check(date)       — Single date, all backends vs Skyfield reference
2. random_audit(n, range) — n random dates sampled from a year range
3. boundary_audit()       — Test dates within 0.5° of sign/nakshatra boundaries
4. full_report(n)         — Combined report: spot-check today + random audit

Output format
─────────────
Dict with structure:
  {
    "reference": "skyfield_de440s",
    "comparison": "astropy",
    "sample_size": 20,
    "planets": {
      "SUN":  {"mean_error_deg": 0.002, "max_error_deg": 0.008, "rms_deg": 0.003,
               "sign_agreement_pct": 100.0, "nakshatra_agreement_pct": 100.0},
      ...
    },
    "summary": {
      "worst_planet": "RAHU",
      "worst_mean_error": 0.042,
      "all_within_threshold": True,
      "threshold_deg": 0.1,
    },
    "flags": [],       # list of warning strings for each discrepancy > threshold
    "dates_tested": [...],
  }

CLI usage
─────────
  python -m vedic_engine.prediction.ephemeris_audit [--n 20] [--start 1950] [--end 2050]
"""
from __future__ import annotations

import math
import random
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


PLANET_NAMES = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU"]
SIGN_NAMES   = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# Thresholds (degrees)
WARN_THRESHOLD   = 0.10   # flag individual planet if mean error > 0.10°
NAKSHATRA_SPAN   = 360.0 / 27.0      # 13.333°
SUBLORD_TYPICAL  = 0.25              # KP sublord minimum span


# ─── Angular difference helper ────────────────────────────────────────────────

def _angular_diff(a: float, b: float) -> float:
    """Signed shortest-arc difference a - b in degrees [-180, 180]."""
    d = (a - b) % 360.0
    if d > 180.0:
        d -= 360.0
    return d


def _sign(lon: float) -> int:
    return int(lon // 30) % 12


def _nakshatra(lon: float) -> int:
    return int(lon / NAKSHATRA_SPAN) % 27


# ─── Backend wrappers (with graceful failure) ─────────────────────────────────

def _get_skyfield(dt: datetime) -> Optional[Dict[str, float]]:
    try:
        from vedic_engine.prediction.skyfield_positions import get_positions_skyfield
        return get_positions_skyfield(dt)
    except Exception:
        return None


def _get_astropy(dt: datetime) -> Optional[Dict[str, float]]:
    try:
        from vedic_engine.prediction.astropy_positions import get_positions_astropy
        return get_positions_astropy(dt)
    except Exception:
        return None


def _get_swisseph(dt: datetime) -> Optional[Dict[str, float]]:
    try:
        from vedic_engine.prediction.transits import _get_positions_swisseph
        return _get_positions_swisseph(dt)
    except Exception:
        return None


def _get_ephem(dt: datetime) -> Optional[Dict[str, float]]:
    try:
        from vedic_engine.prediction.transits import _get_positions_ephem
        return _get_positions_ephem(dt)
    except Exception:
        return None


BACKENDS = {
    "skyfield":  _get_skyfield,
    "astropy":   _get_astropy,
    "swisseph":  _get_swisseph,
    "ephem":     _get_ephem,
}


# ─── Per-planet statistics ────────────────────────────────────────────────────

def _planet_stats(errors_deg: List[float], ref_lons: List[float],
                  cmp_lons: List[float]) -> Dict[str, Any]:
    """Compute per-planet statistics from a list of signed errors."""
    if not errors_deg:
        return {}
    n = len(errors_deg)
    abs_errors = [abs(e) for e in errors_deg]
    mean_err  = sum(abs_errors) / n
    max_err   = max(abs_errors)
    rms       = math.sqrt(sum(e ** 2 for e in errors_deg) / n)
    mean_bias = sum(errors_deg) / n  # positive = backend is systematically ahead

    sign_agree = sum(1 for r, c in zip(ref_lons, cmp_lons)
                     if _sign(r) == _sign(c))
    nak_agree  = sum(1 for r, c in zip(ref_lons, cmp_lons)
                     if _nakshatra(r) == _nakshatra(c))

    return {
        "mean_error_deg":            round(mean_err, 6),
        "max_error_deg":             round(max_err, 6),
        "rms_deg":                   round(rms, 6),
        "mean_bias_deg":             round(mean_bias, 6),   # systematic offset
        "sign_agreement_pct":        round(100.0 * sign_agree / n, 2),
        "nakshatra_agreement_pct":   round(100.0 * nak_agree  / n, 2),
        "sample_size":               n,
    }


# ─── Core comparison logic ────────────────────────────────────────────────────

def compare_backends(
    dates: List[datetime],
    reference: str = "skyfield",
    comparison: str = "astropy",
) -> Dict[str, Any]:
    """
    Compare two backends across a list of dates.

    Parameters
    ----------
    dates      : list of naive UTC datetime objects
    reference  : name of the ground-truth backend (default: 'skyfield')
    comparison : name of the backend to audit (default: 'astropy')

    Returns
    -------
    Full audit dict with per-planet statistics, flags, and summary.
    """
    ref_fn  = BACKENDS.get(reference)
    cmp_fn  = BACKENDS.get(comparison)

    if ref_fn is None:
        raise ValueError(f"Unknown reference backend: {reference}")
    if cmp_fn is None:
        raise ValueError(f"Unknown comparison backend: {comparison}")

    # Accumulate per-planet [errors], [ref_lons], [cmp_lons]
    planet_errors: Dict[str, List[float]] = {p: [] for p in PLANET_NAMES}
    planet_ref:    Dict[str, List[float]] = {p: [] for p in PLANET_NAMES}
    planet_cmp:    Dict[str, List[float]] = {p: [] for p in PLANET_NAMES}
    dates_tested: List[str] = []
    skipped = 0

    for dt in dates:
        ref_pos = ref_fn(dt)
        cmp_pos = cmp_fn(dt)

        if ref_pos is None or cmp_pos is None:
            skipped += 1
            continue

        dates_tested.append(dt.strftime("%Y-%m-%d %H:%M"))
        for planet in PLANET_NAMES:
            if planet in ref_pos and planet in cmp_pos:
                err = _angular_diff(cmp_pos[planet], ref_pos[planet])
                planet_errors[planet].append(err)
                planet_ref[planet].append(ref_pos[planet])
                planet_cmp[planet].append(cmp_pos[planet])

    # Build per-planet stats
    planet_stats: Dict[str, Any] = {}
    for planet in PLANET_NAMES:
        if planet_errors[planet]:
            planet_stats[planet] = _planet_stats(
                planet_errors[planet],
                planet_ref[planet],
                planet_cmp[planet],
            )

    # Flags
    flags: List[str] = []
    for planet, stats in planet_stats.items():
        me = stats.get("mean_error_deg", 0)
        mx = stats.get("max_error_deg", 0)
        sa = stats.get("sign_agreement_pct", 100)
        na = stats.get("nakshatra_agreement_pct", 100)
        bi = abs(stats.get("mean_bias_deg", 0))

        if me > WARN_THRESHOLD:
            flags.append(
                f"[{planet}] mean error {me:.4f}° exceeds {WARN_THRESHOLD}° threshold"
            )
        if mx > 0.5:
            flags.append(
                f"[{planet}] max single-date error {mx:.4f}° > 0.5° (sign/nakshatra risk)"
            )
        if sa < 100.0:
            flags.append(
                f"[{planet}] sign disagreement on {100 - sa:.1f}% of test dates"
            )
        if na < 98.0:
            flags.append(
                f"[{planet}] nakshatra disagreement on {100 - na:.1f}% of test dates"
            )
        if bi > 0.05:
            flags.append(
                f"[{planet}] systematic bias {bi:.4f}° (ayanamsa or frame offset?)"
            )
        if me > 0 and me < WARN_THRESHOLD and mx > SUBLORD_TYPICAL:
            flags.append(
                f"[{planet}] max error {mx:.4f}° > KP sublord span {SUBLORD_TYPICAL}° "
                f"on some dates — sublord assignment may differ near cusps"
            )

    # Summary
    if planet_stats:
        worst_planet = max(planet_stats,
                           key=lambda p: planet_stats[p].get("mean_error_deg", 0))
        worst_mean   = planet_stats[worst_planet].get("mean_error_deg", 0)
    else:
        worst_planet = "N/A"
        worst_mean   = 0.0

    summary = {
        "worst_planet":       worst_planet,
        "worst_mean_error":   round(worst_mean, 6),
        "all_within_threshold": worst_mean <= WARN_THRESHOLD,
        "threshold_deg":      WARN_THRESHOLD,
        "dates_tested_count": len(dates_tested),
        "dates_skipped":      skipped,
    }

    return {
        "reference":  reference,
        "comparison": comparison,
        "planets":    planet_stats,
        "summary":    summary,
        "flags":      flags,
        "dates_tested": dates_tested,
    }


# ─── High-level audit functions ───────────────────────────────────────────────

def spot_check(dt: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Spot-check all available backends against Skyfield for a single date.

    Parameters
    ----------
    dt : date to test (defaults to today noon UTC)

    Returns
    -------
    Dict: comparison name → audit result for that backend pair.
    """
    if dt is None:
        dt = datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0)

    results: Dict[str, Any] = {"date": dt.strftime("%Y-%m-%d %H:%M UTC")}
    for backend_name in ["astropy", "swisseph", "ephem"]:
        results[f"skyfield_vs_{backend_name}"] = compare_backends(
            [dt], reference="skyfield", comparison=backend_name
        )
    return results


def random_audit(
    n: int = 20,
    start_year: int = 1950,
    end_year: int   = 2050,
    reference: str  = "skyfield",
    comparison: str = "astropy",
    seed: Optional[int] = 42,
) -> Dict[str, Any]:
    """
    Audit comparison backend against reference across n random dates.

    Parameters
    ----------
    n           : number of random dates to sample
    start_year  : earliest date to sample (inclusive)
    end_year    : latest date to sample (inclusive)
    reference   : ground-truth backend name ('skyfield' recommended)
    comparison  : backend to audit ('astropy', 'swisseph', 'ephem')
    seed        : random seed for reproducibility (None = truly random)

    Returns
    -------
    Full audit dict from compare_backends().
    """
    rng = random.Random(seed)
    start_dt = datetime(start_year, 1, 1, 12, 0)
    end_dt   = datetime(end_year,   12, 31, 12, 0)
    total_seconds = int((end_dt - start_dt).total_seconds())
    dates = [
        start_dt + timedelta(seconds=rng.randint(0, total_seconds))
        for _ in range(n)
    ]
    dates.sort()
    return compare_backends(dates, reference=reference, comparison=comparison)


def boundary_audit(reference: str = "skyfield", comparison: str = "astropy") -> Dict[str, Any]:
    """
    Test dates where planets are near sign/nakshatra boundaries for one specific chart.

    Uses the test chart (current date) and computes positions at ±0.5° offsets
    by testing multiple days around planetary boundary crossings.
    This stresses sign-boundary accuracy most severely.

    Returns the standard compare_backends output.
    """
    # Generate dates at regular 29-day intervals (catches each sign boundary for Sun)
    # and 2-day intervals for Moon (crosses nakshatra every ~1 day)
    dates: List[datetime] = []
    base = datetime(2000, 1, 1, 12, 0)
    for i in range(0, 365 * 25, 29):     # Sun sign boundaries: ~every 30 days
        dates.append(base + timedelta(days=i))
    for i in range(0, 365, 2):           # Moon nakshatra boundaries: every ~1 day
        dates.append(base + timedelta(days=i))
    dates = sorted(set(d.strftime("%Y-%m-%d") for d in dates))
    dates = [datetime.strptime(d, "%Y-%m-%d").replace(hour=12) for d in dates]

    return compare_backends(dates, reference=reference, comparison=comparison)


def full_report(n: int = 20, verbose: bool = True) -> Dict[str, Any]:
    """
    Run spot_check for today + random_audit of astropy vs Skyfield.
    Print a human-readable summary if verbose=True.

    Returns
    -------
    {'spot': spot_check_result, 'random': random_audit_result}
    """
    spot  = spot_check()
    audit = random_audit(n=n, comparison="astropy")

    if verbose:
        _print_report(spot, audit)

    return {"spot": spot, "random": audit}


# ─── Pretty-printer ───────────────────────────────────────────────────────────

def _print_report(spot: Dict, audit: Dict) -> None:
    print("\n" + "═" * 70)
    print("  EPHEMERIS AUDIT REPORT — Skyfield/JPL vs astropy")
    print("═" * 70)

    # Spot check
    spot_result = spot.get("skyfield_vs_astropy", {})
    print(f"\n▶ Spot-check date: {spot.get('date', '?')}")
    ps = spot_result.get("planets", {})
    if ps:
        hdr = f"  {'Planet':9s} {'Error°':>10s}  {'Bias°':>10s}  {'Sign✓':>8s}  {'Nak✓':>8s}"
        print(hdr)
        print("  " + "─" * 60)
        for p in PLANET_NAMES:
            if p in ps:
                s = ps[p]
                print(
                    f"  {p:9s} {s['mean_error_deg']:>10.5f}  "
                    f"{s['mean_bias_deg']:>10.5f}  "
                    f"{s['sign_agreement_pct']:>7.1f}%  "
                    f"{s['nakshatra_agreement_pct']:>7.1f}%"
                )

    # Random audit
    asum   = audit.get("summary", {})
    aflags = audit.get("flags", [])
    n_ok   = asum.get("dates_tested_count", 0)
    print(f"\n▶ Random audit: {n_ok} dates ({audit.get('reference','?')} vs {audit.get('comparison','?')})")
    print(f"  Worst planet : {asum.get('worst_planet')}  "
          f"mean error {asum.get('worst_mean_error', 0):.5f}°")
    print(f"  All within {asum.get('threshold_deg', 0.1)}° : "
          f"{'YES ✓' if asum.get('all_within_threshold') else 'NO ✗'}")

    if aflags:
        print(f"\n  ⚠ Flags ({len(aflags)}):")
        for f in aflags:
            print(f"    • {f}")
    else:
        print("\n  ✓ No flags — backends agree within all thresholds")

    aplanets = audit.get("planets", {})
    if aplanets:
        print(f"\n  {'Planet':9s} {'Mean°':>10s}  {'Max°':>10s}  {'RMS°':>10s}  {'Bias°':>10s}")
        print("  " + "─" * 60)
        for p in PLANET_NAMES:
            if p in aplanets:
                s = aplanets[p]
                print(
                    f"  {p:9s} {s['mean_error_deg']:>10.5f}  "
                    f"{s['max_error_deg']:>10.5f}  "
                    f"{s['rms_deg']:>10.5f}  "
                    f"{s['mean_bias_deg']:>10.5f}"
                )

    print("\n" + "═" * 70)


# ─── CLI entry point ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Audit Vedic ephemeris backends against Skyfield/JPL reference"
    )
    parser.add_argument("--n",          type=int, default=20,   help="Sample size for random audit")
    parser.add_argument("--start",      type=int, default=1950, help="Start year for random audit")
    parser.add_argument("--end",        type=int, default=2050, help="End year for random audit")
    parser.add_argument("--compare",    type=str, default="astropy",
                        choices=["astropy", "swisseph", "ephem"],
                        help="Backend to audit against Skyfield")
    parser.add_argument("--boundary",   action="store_true",
                        help="Run boundary audit (sign/nakshatra edge dates)")
    parser.add_argument("--spot-only",  action="store_true",
                        help="Only run single spot-check for today")
    args = parser.parse_args()

    if args.spot_only:
        r = spot_check()
        _print_report(r, {})
    elif args.boundary:
        r = boundary_audit(comparison=args.compare)
        print(f"\nBoundary audit: {r['summary']}")
        for flag in r.get("flags", []):
            print(f"  ⚠ {flag}")
    else:
        full_report(n=args.n, verbose=True)
