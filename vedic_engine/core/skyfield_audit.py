"""
Skyfield + JPL Ephemeris Audit Backend.

Purpose
-------
Acts as a high-accuracy, astronomy-first AUDIT layer for our primary astropy
or swisseph computation tier.

- Skyfield uses official JPL BSP (Binary SPK) ephemeris files (DE421, DE440).
- DE421: covers 1900–2050, ~17 MB.  Excellent for historical chart validation.
- DE440: covers 1550–2650, ~32 MB.  Use for long-range transit forecasting.
- Accuracy: sub-arcsecond, on par with Swiss Ephemeris.

Workflow
--------
1. On first use: auto-downloads DE421.bsp to vedic_engine/data/ephemeris/.
2. Computes geocentric APPARENT positions in the ecliptic frame (J2000 epoch).
3. Applies Lahiri ayanamsa (same formula as astropy_positions.py) → sidereal.
4. Provides `audit_chart()` to compare Skyfield vs our engine's positions.
5. `audit_random_sample()` runs spot-checks on randomly generated datetimes
   and reports any planet longitude discrepancies above threshold.

Install requirement (already in .venv): pip install skyfield
BSP files: auto-downloaded to vedic_engine/data/ephemeris/ on first run.

References
----------
- Skyfield: https://rhodesmill.org/skyfield/
- DE421: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/
- Lahiri ayanamsa source: Lahiri's original tables + IAU 1976 precession rate
"""

from __future__ import annotations

import os
import math
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ─── Ephemeris storage location ──────────────────────────────────────────────

_HERE = Path(__file__).parent.parent  # vedic_engine/
_EPH_DIR = _HERE / "data" / "ephemeris"
_EPH_DIR.mkdir(parents=True, exist_ok=True)

# Preferred BSP files in order (smaller first so initial download is fast)
_BSP_CANDIDATES = ["de421.bsp", "de440.bsp", "de438.bsp"]

# Planet name mapping: our internal names → Skyfield body names
# Use barycenter names — works for both DE421 and DE440s (DE440s lacks individual Mars/Venus/Mercury)
_SKYFIELD_BODY_MAP = {
    "SUN":     "sun",
    "MOON":    "moon",
    "MARS":    "mars barycenter",
    "MERCURY": "mercury barycenter",
    "JUPITER": "jupiter barycenter",
    "VENUS":   "venus barycenter",
    "SATURN":  "saturn barycenter",
    # Uranus/Neptune included for outer-planet transit work
    "URANUS":  "uranus barycenter",
    "NEPTUNE": "neptune barycenter",
    # RAHU/KETU: no direct BSP entry; computed from Moon's ascending node separately
}

# ─── Lahiri ayanamsa (same formula as astropy_positions.py for consistency) ──

_J2000_JD = 2451545.0
_LAHIRI_AT_J2000 = 23.85  # degrees at J2000 epoch
_LAHIRI_RATE     = 50.288 / 3600.0 / 365.25   # degrees/day (50.288"/yr)


def _lahiri_ayanamsa(dt_utc: datetime) -> float:
    """Lahiri ayanamsa in degrees for a given UTC datetime."""
    import astropy.time as apt
    try:
        t = apt.Time(dt_utc.isoformat(), format="isot", scale="utc")
        days_from_j2000 = t.jd - _J2000_JD
    except Exception:
        # Fallback: rough Julian day calculation
        days_from_j2000 = (dt_utc - datetime(2000, 1, 1, 12)).total_seconds() / 86400.0
    return _LAHIRI_AT_J2000 + days_from_j2000 * _LAHIRI_RATE


# ─── Loader ──────────────────────────────────────────────────────────────────

_loader = None
_timescale = None
_ephemeris = None


def _get_skyfield_loader():
    """Return a Skyfield Loader pointed at our ephemeris directory."""
    global _loader
    if _loader is None:
        try:
            from skyfield.api import Loader
            _loader = Loader(str(_EPH_DIR))
        except ImportError:
            raise RuntimeError(
                "skyfield not installed. Run: pip install skyfield"
            )
    return _loader


def _get_timescale():
    global _timescale
    if _timescale is None:
        _timescale = _get_skyfield_loader().timescale()
    return _timescale


def _get_ephemeris(bsp_name: str = "de421.bsp"):
    """
    Load (and auto-download if missing) a JPL BSP ephemeris file.

    Downloads from JPL's official server on first use.
    File is cached in vedic_engine/data/ephemeris/.
    """
    global _ephemeris
    if _ephemeris is not None:
        return _ephemeris

    load = _get_skyfield_loader()

    # Try candidates in order
    for candidate in _BSP_CANDIDATES:
        bsp_path = _EPH_DIR / candidate
        if bsp_path.exists():
            logger.info(f"[skyfield_audit] Loading cached {candidate}")
            _ephemeris = load(candidate)
            return _ephemeris

    # Download preferred BSP
    logger.info(f"[skyfield_audit] Downloading {bsp_name} (~17 MB) to {_EPH_DIR} …")
    try:
        _ephemeris = load(bsp_name)
        return _ephemeris
    except Exception as e:
        raise RuntimeError(
            f"Failed to download {bsp_name}: {e}\n"
            f"Manually place a BSP file in {_EPH_DIR} and retry."
        )


# ─── Core computation ─────────────────────────────────────────────────────────

def get_positions_skyfield(
    dt_utc: datetime,
    planets: Optional[List[str]] = None,
    bsp_name: str = "de421.bsp",
) -> Dict[str, float]:
    """
    Compute geocentric sidereal longitudes (Lahiri) using Skyfield + JPL BSP.

    Parameters
    ----------
    dt_utc  : UTC datetime (naive or timezone-aware)
    planets : list of planet keys (e.g. ["SUN","MOON","MARS"]); None = all
    bsp_name: BSP file to use ("de421.bsp" recommended)

    Returns
    -------
    dict: {planet_key: sidereal_longitude_degrees (0–360)}
          Also includes "_ayanamsa" as a metadata key.

    Notes
    -----
    - RAHU is computed from Moon's orbital node direction using Meeus formula
      (same approach as astropy_positions.py) — DE421 has no dedicated Rahu body.
    - Longitudes are apparent (light-travel corrected), geocentric, ecliptic J2000,
      then converted to sidereal via Lahiri ayanamsa.
    """
    try:
        from skyfield.api import N, S, E, W
        from skyfield.framelib import ecliptic_J2000_frame
    except ImportError:
        raise RuntimeError("skyfield not installed.")

    eph = _get_ephemeris(bsp_name)
    ts  = _get_timescale()
    earth = eph["earth"]

    if planets is None:
        planets = list(_SKYFIELD_BODY_MAP.keys())

    # Build Skyfield time object from UTC datetime
    t = ts.utc(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour, dt_utc.minute, dt_utc.second + dt_utc.microsecond / 1e6,
    )

    ayanamsa = _lahiri_ayanamsa(dt_utc)
    result: Dict[str, float] = {"_ayanamsa": round(ayanamsa, 6)}

    for pname in planets:
        if pname in ("RAHU", "KETU"):
            continue   # handled separately below
        body_key = _SKYFIELD_BODY_MAP.get(pname)
        if body_key is None:
            continue
        try:
            body = eph[body_key]
            # Apparent geocentric position, corrected for light-travel time
            astrometric = earth.at(t).observe(body).apparent()
            lat, lon, distance = astrometric.frame_latlon(ecliptic_J2000_frame)
            tropical_lon = lon.degrees % 360.0
            sidereal_lon = (tropical_lon - ayanamsa) % 360.0
            result[pname] = round(sidereal_lon, 6)
        except Exception as e:
            logger.warning(f"[skyfield_audit] Could not compute {pname}: {e}")

    # ── Rahu via Meeus (same as astropy_positions.py) ─────────────────────
    if "RAHU" in planets or "KETU" in planets:
        rahu_lon = _compute_rahu_meeus(dt_utc)
        if "RAHU" in planets:
            result["RAHU"] = round((rahu_lon - ayanamsa) % 360.0, 6)
        if "KETU" in planets:
            result["KETU"] = round((rahu_lon + 180 - ayanamsa) % 360.0, 6)

    return result


def _compute_rahu_meeus(dt_utc: datetime) -> float:
    """
    Tropical longitude of Moon's Mean Ascending Node using Meeus Ch.47.
    Accurate to <0.05° for 1800–2100.
    Returns tropical degrees (ayanama NOT subtracted — caller subtracts).
    """
    days_j2000 = (dt_utc - datetime(2000, 1, 1, 12)).total_seconds() / 86400.0
    T = days_j2000 / 36525.0  # Julian centuries from J2000
    omega = (125.04452 - 1934.136261 * T
             + 0.0020708 * T**2
             + T**3 / 450000.0) % 360.0
    return omega % 360.0


# ─── Audit functions ──────────────────────────────────────────────────────────

def audit_chart(
    dt_utc: datetime,
    engine_positions: Dict[str, float],
    threshold_deg: float = 0.5,
    bsp_name: str = "de421.bsp",
) -> Dict[str, Any]:
    """
    Compare engine-computed sidereal longitudes against Skyfield/JPL reference.

    Parameters
    ----------
    dt_utc           : UTC datetime of the chart
    engine_positions : dict of {planet: sidereal_lon_deg} from our engine
    threshold_deg    : report discrepancies above this angle (default 0.5°)
    bsp_name         : JPL BSP ephemeris to use

    Returns
    -------
    {
      "skyfield_positions": {...},        # Skyfield JPL values
      "engine_positions":   {...},        # Our engine values (passed in)
      "discrepancies": [                  # Planets above threshold
          {"planet": str, "engine": float, "skyfield": float, "delta": float}
      ],
      "max_error_deg": float,             # Worst-case planet error
      "mean_error_deg": float,            # Mean absolute error
      "pass": bool,                       # True if all within threshold
      "ayanamsa": float,
      "datetime_utc": str,
    }
    """
    skyfield_pos = get_positions_skyfield(dt_utc, bsp_name=bsp_name)
    ayanamsa = skyfield_pos.pop("_ayanamsa", None)

    discrepancies = []
    errors = []

    planets_to_check = [
        p for p in engine_positions if p in skyfield_pos
    ]

    for planet in planets_to_check:
        eng = engine_positions[planet]
        sky = skyfield_pos[planet]
        # Shortest angular difference (handles 0°/360° wrap)
        delta = abs((eng - sky + 180) % 360 - 180)
        errors.append(delta)
        if delta >= threshold_deg:
            discrepancies.append({
                "planet":   planet,
                "engine":   round(eng, 4),
                "skyfield": round(sky, 4),
                "delta_deg": round(delta, 4),
            })

    discrepancies.sort(key=lambda x: x["delta_deg"], reverse=True)

    return {
        "skyfield_positions": skyfield_pos,
        "engine_positions":   engine_positions,
        "discrepancies":      discrepancies,
        "max_error_deg":      round(max(errors), 4) if errors else 0.0,
        "mean_error_deg":     round(sum(errors) / len(errors), 4) if errors else 0.0,
        "pass":               len(discrepancies) == 0,
        "threshold_deg":      threshold_deg,
        "ayanamsa":           ayanamsa,
        "datetime_utc":       dt_utc.isoformat(),
        "planets_checked":    len(planets_to_check),
    }


def audit_random_sample(
    n_samples: int = 20,
    year_range: Tuple[int, int] = (1900, 2050),
    threshold_deg: float = 0.5,
    engine_fn=None,
    bsp_name: str = "de421.bsp",
) -> Dict[str, Any]:
    """
    Spot-check our engine against Skyfield/JPL over N random datetimes.

    Parameters
    ----------
    n_samples   : number of random UTC datetimes to test
    year_range  : (start_year, end_year) for random datetime generation
    threshold_deg : discrepancy threshold in degrees
    engine_fn   : callable(dt_utc) → {planet: sidereal_lon_deg}
                  If None, uses get_positions_skyfield() itself (sanity check)
    bsp_name    : JPL BSP file

    Returns
    -------
    {
      "samples_tested": int,
      "samples_passed": int,
      "pass_rate": float,
      "worst_case": dict,       # audit result with largest max_error
      "summary": [              # per-sample one-liner stats
          {"dt": str, "max_err": float, "pass": bool}
      ],
    }
    """
    y0, y1 = year_range
    summaries = []
    worst_case = None
    worst_error = -1.0
    passed = 0

    for _ in range(n_samples):
        try:
            # Random UTC datetime in range
            start = datetime(y0, 1, 1)
            end   = datetime(y1, 12, 31)
            dt_utc = start + timedelta(
                seconds=random.randint(0, int((end - start).total_seconds()))
            )

            if engine_fn is not None:
                eng_pos = engine_fn(dt_utc)
            else:
                # Default: use astropy backend for comparison
                try:
                    from vedic_engine.prediction.astropy_positions import (
                        get_positions_astropy
                    )
                    eng_pos = get_positions_astropy(dt_utc)
                except Exception:
                    continue

            result = audit_chart(dt_utc, eng_pos, threshold_deg, bsp_name)
            ok = result["pass"]
            if ok:
                passed += 1

            summaries.append({
                "dt":      dt_utc.strftime("%Y-%m-%d %H:%M UTC"),
                "max_err": result["max_error_deg"],
                "mean_err": result["mean_error_deg"],
                "pass":    ok,
                "failures": [d["planet"] for d in result["discrepancies"]],
            })

            if result["max_error_deg"] > worst_error:
                worst_error = result["max_error_deg"]
                worst_case  = result

        except Exception as exc:
            logger.warning(f"[audit_random_sample] iteration failed: {exc}")

    return {
        "samples_tested":   n_samples,
        "samples_passed":   passed,
        "pass_rate":        round(passed / n_samples, 3) if n_samples else 0.0,
        "worst_case":       worst_case,
        "threshold_deg":    threshold_deg,
        "summary":          summaries,
    }


# ─── Convenience: planet speeds ───────────────────────────────────────────────

def get_planet_speeds_skyfield(
    dt_utc: datetime,
    delta_hours: float = 24.0,
    planets: Optional[List[str]] = None,
) -> Dict[str, float]:
    """
    Compute daily motion (degrees/day) via forward finite difference.

    Parameters
    ----------
    dt_utc       : reference UTC datetime
    delta_hours  : time step for finite difference (24h = daily motion)
    planets      : subset of planets (None = all)

    Returns
    -------
    dict: {planet: speed_deg_per_day}  — negative = retrograde
    """
    dt2 = dt_utc + timedelta(hours=delta_hours)
    pos1 = get_positions_skyfield(dt_utc, planets)
    pos2 = get_positions_skyfield(dt2, planets)

    speeds: Dict[str, float] = {}
    for pname in pos1:
        if pname.startswith("_"):
            continue
        if pname in pos2:
            raw_diff = pos2[pname] - pos1[pname]
            # Normalize to [-180, 180] before scaling
            motion = ((raw_diff + 180) % 360 - 180)
            daily = motion * (24.0 / delta_hours)
            speeds[pname] = round(daily, 6)
    return speeds


# ─── Diagnostics ─────────────────────────────────────────────────────────────

def print_audit_report(result: Dict[str, Any]) -> None:
    """Human-readable print of an audit_chart() result."""
    print(f"\n{'='*60}")
    print(f"  Skyfield / JPL Audit Report")
    print(f"  UTC : {result.get('datetime_utc', 'N/A')}")
    print(f"  Ayanamsa (Lahiri): {result.get('ayanamsa', '?'):.4f}°")
    print(f"  Threshold : ±{result.get('threshold_deg', 0.5):.2f}°")
    print(f"{'='*60}")

    sky_pos = result.get("skyfield_positions", {})
    eng_pos = result.get("engine_positions", {})

    print(f"  {'Planet':<10}  {'Engine°':>10}  {'Skyfield°':>10}  {'Δ°':>8}")
    print(f"  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*8}")
    planets_sorted = sorted(
        set(sky_pos.keys()) | set(eng_pos.keys()),
        key=lambda p: ["SUN","MOON","MARS","MERCURY","JUPITER","VENUS","SATURN","RAHU","KETU"].index(p)
            if p in ["SUN","MOON","MARS","MERCURY","JUPITER","VENUS","SATURN","RAHU","KETU"] else 99
    )
    for p in planets_sorted:
        eng_v = eng_pos.get(p, float("nan"))
        sky_v = sky_pos.get(p, float("nan"))
        delta = abs((eng_v - sky_v + 180) % 360 - 180) if (eng_v == eng_v and sky_v == sky_v) else float("nan")
        flag = " ⚠" if delta >= result.get("threshold_deg", 0.5) else ""
        print(f"  {p:<10}  {eng_v:>10.4f}  {sky_v:>10.4f}  {delta:>8.4f}{flag}")

    print(f"{'='*60}")
    status = "✓ PASS" if result.get("pass") else f"✗ FAIL ({len(result.get('discrepancies',[]))} planets)"
    print(f"  Mean error: {result.get('mean_error_deg',0):.4f}°  "
          f"Max error: {result.get('max_error_deg',0):.4f}°  "
          f"Status: {status}")
    print(f"{'='*60}\n")
