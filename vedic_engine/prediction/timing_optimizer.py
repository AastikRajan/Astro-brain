"""
Timing Optimizer — Best/Worst Window Finder for the next N months.

Uses scipy.signal to find local maxima in a confidence time-series and
rank the best prediction windows for a domain.

Methodology:
  1. For each day in the look-ahead period, compute a quick transit score
     (ashtakvarga house score + favourable transit count).
  2. Weight by the active dasha period alignment (changes monthly).
  3. Apply scipy.signal.find_peaks to locate peak windows.
  4. Return the top K windows with date range and score.

This gives the "best month" / "best window" output that users want.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import math

# ─── Domain relevance weights (which planets matter per domain) ───────────────
_DOMAIN_PLANETS: Dict[str, List[str]] = {
    "career":       ["JUPITER", "SUN", "SATURN", "MARS"],
    "finance":      ["JUPITER", "VENUS", "MOON", "MERCURY"],
    "health":       ["SUN", "MARS", "SATURN", "MOON"],
    "relationships":["VENUS", "MOON", "JUPITER", "MARS"],
    "spiritual":    ["KETU", "JUPITER", "SATURN", "MOON"],
    "education":    ["JUPITER", "MERCURY", "SUN", "VENUS"],
    "travel":       ["JUPITER", "RAHU", "MARS", "SUN"],
    "property":     ["MARS", "SATURN", "VENUS", "MOON"],
    "marriage":     ["VENUS", "JUPITER", "MOON", "MARS"],
}

# ─── Transit house favorability by domain ─────────────────────────────────────
# house_from_moon → raw score for that domain
_TRANSIT_HOUSE_SCORE: Dict[str, Dict[int, float]] = {
    "career": {1: 0.3, 2: 0.4, 3: 0.5, 4: 0.2, 5: 0.4, 6: 0.1,
               7: 0.5, 8: 0.0, 9: 0.7, 10: 0.9, 11: 0.8, 12: 0.1},
    "finance":{1: 0.4, 2: 0.9, 3: 0.3, 4: 0.3, 5: 0.5, 6: 0.2,
               7: 0.4, 8: 0.1, 9: 0.6, 10: 0.5, 11: 0.9, 12: 0.0},
    "health": {1: 0.5, 2: 0.4, 3: 0.6, 4: 0.4, 5: 0.5, 6: 0.0,
               7: 0.3, 8: 0.0, 9: 0.5, 10: 0.4, 11: 0.7, 12: 0.1},
    "relationships":{1:0.4,2:0.5,3:0.4,4:0.5,5:0.7,6:0.1,
                     7:0.9,8:0.1,9:0.6,10:0.4,11:0.7,12:0.2},
    "spiritual":{1:0.3,2:0.3,3:0.3,4:0.5,5:0.5,6:0.2,
                 7:0.4,8:0.7,9:0.9,10:0.3,11:0.4,12:0.8},
    "education":{1:0.4,2:0.4,3:0.5,4:0.6,5:0.8,6:0.2,
                 7:0.4,8:0.1,9:0.9,10:0.5,11:0.6,12:0.2},
}
_DEFAULT_HOUSE_SCORE = {h: 0.5 for h in range(1, 13)}


# ─── Daily score computation ──────────────────────────────────────────────────

def _daily_transit_score(
        transit_lons: Dict[str, float],   # planet → current sidereal lon
        natal_moon_sign: int,             # 0-11
        domain: str,
        sarva_av: Optional[List[int]],    # Sarvashtakvarga (12 sign scores)
        dasha_alignment: float = 0.5,     # 0-1 from active dasha
) -> float:
    """
    Quick daily transit score for a domain.
    Returns float [0, 1].
    """
    planets = _DOMAIN_PLANETS.get(domain, ["JUPITER", "SATURN"])
    house_scores = _TRANSIT_HOUSE_SCORE.get(domain, _DEFAULT_HOUSE_SCORE)

    total = 0.0
    count = 0
    for pname in planets:
        if pname not in transit_lons:
            continue
        sign = int(transit_lons[pname] / 30.0) % 12
        house_from_moon = ((sign - natal_moon_sign) % 12) + 1

        h_score = house_scores.get(house_from_moon, 0.5)

        # Ashtakvarga boost: sarva_av[sign] / expected_avg(28)
        if sarva_av and len(sarva_av) == 12:
            av_score = sarva_av[sign] / 28.0   # normalize; >1 = above average
            h_score = h_score * (0.6 + 0.4 * min(av_score, 1.5))

        total += h_score
        count += 1

    transit_score = total / count if count else 0.5

    # Weight transit by dasha alignment (dasha is 3× more important)
    combined = (3.0 * dasha_alignment + 1.5 * transit_score) / 4.5
    return max(0.0, min(1.0, combined))


def _compute_approximate_transit_lons(
        base_lons: Dict[str, float],
        reference_date: datetime,
        target_date: datetime,
) -> Dict[str, float]:
    """
    Approximate planet positions on target_date from known base_lons.
    Uses mean motion rates (degrees/day, sidereal).
    Accurate enough for monthly window finding.
    """
    _MEAN_MOTION: Dict[str, float] = {
        "SUN":     0.9856,
        "MOON":    13.1764,
        "MARS":    0.5240,
        "MERCURY": 1.3830,
        "JUPITER": 0.0831,
        "VENUS":   1.2000,
        "SATURN":  0.0335,
        "RAHU":   -0.0529,
        "KETU":   -0.0529,
    }
    days = (target_date - reference_date).total_seconds() / 86400.0
    result = {}
    for p, base_lon in base_lons.items():
        rate = _MEAN_MOTION.get(p, 0.0)
        result[p] = (base_lon + rate * days) % 360.0
    return result


# ─── Peak finder using scipy ──────────────────────────────────────────────────

def find_best_windows(
        base_transit_lons: Dict[str, float],   # transit lons on reference_date
        reference_date: datetime,
        natal_moon_sign: int,
        domain: str = "career",
        months_ahead: int = 12,
        sarva_av: Optional[List[int]] = None,
        dasha_alignment_map: Optional[Dict[str, float]] = None,
        resolution_days: int = 3,
        top_k: int = 5,
) -> List[Dict]:
    """
    Find the top K best prediction windows over the next N months.

    Returns list of dicts:
      {
        "window_start": str,  # ISO date
        "window_end": str,
        "peak_date": str,
        "score": float,
        "domain": str,
        "description": str,
      }
    """
    try:
        from scipy.signal import find_peaks
        use_scipy = True
    except ImportError:
        use_scipy = False

    total_days = int(months_ahead * 30.44)
    dates: List[datetime] = []
    scores: List[float] = []

    # Build dasha alignment lookup (coarse: constant per 30-day window)
    def _da(day_num: int) -> float:
        if not dasha_alignment_map:
            return 0.5
        # monthly keys like "2026-03"
        d = reference_date + timedelta(days=day_num)
        key = d.strftime("%Y-%m")
        return dasha_alignment_map.get(key, 0.5)

    for day in range(0, total_days, resolution_days):
        target = reference_date + timedelta(days=day)
        lons = _compute_approximate_transit_lons(
            base_transit_lons, reference_date, target)
        da = _da(day)
        s = _daily_transit_score(lons, natal_moon_sign, domain, sarva_av, da)
        dates.append(target)
        scores.append(s)

    if not scores:
        return []

    # ── Find peaks ─────────────────────────────────────────────────────────────
    windows: List[Dict] = []

    if use_scipy and len(scores) >= 5:
        import numpy as np
        arr = np.array(scores)
        prominence = 0.05
        min_distance = max(3, 30 // resolution_days)  # ≥30 days between peaks
        peaks, props = find_peaks(arr, prominence=prominence,
                                  distance=min_distance)
        # Sort by score
        peak_list = sorted(peaks, key=lambda i: -scores[i])
        for peak_idx in peak_list[:top_k]:
            date_at_peak = dates[peak_idx]
            score_at_peak = scores[peak_idx]

            # Window = ±15 days around peak
            w_start = date_at_peak - timedelta(days=15)
            w_end   = date_at_peak + timedelta(days=15)
            # Clamp to look-ahead range
            w_start = max(w_start, reference_date)
            w_end   = min(w_end, reference_date + timedelta(days=total_days))

            desc = _describe_window(score_at_peak, domain)
            windows.append({
                "window_start": w_start.strftime("%Y-%m-%d"),
                "window_end": w_end.strftime("%Y-%m-%d"),
                "peak_date": date_at_peak.strftime("%Y-%m-%d"),
                "score": round(score_at_peak, 3),
                "domain": domain,
                "description": desc,
            })
    else:
        # Fallback: sliding window max, no scipy
        chunk_size = 30 // resolution_days  # ~30-day window
        for i in range(0, len(scores) - chunk_size, chunk_size // 2):
            chunk_scores = scores[i:i + chunk_size]
            max_s = max(chunk_scores)
            max_i = i + chunk_scores.index(max_s)
            windows.append({
                "window_start": dates[i].strftime("%Y-%m-%d"),
                "window_end": dates[min(i + chunk_size, len(dates) - 1)].strftime("%Y-%m-%d"),
                "peak_date": dates[max_i].strftime("%Y-%m-%d"),
                "score": round(max_s, 3),
                "domain": domain,
                "description": _describe_window(max_s, domain),
            })
        windows = sorted(windows, key=lambda w: -w["score"])[:top_k]

    # Remove duplicates (overlapping windows)
    filtered: List[Dict] = []
    last_end = None
    for w in sorted(windows, key=lambda x: x["score"], reverse=True):
        pk = datetime.strptime(w["peak_date"], "%Y-%m-%d")
        if last_end is None or (pk - last_end).days >= 20:
            filtered.append(w)
            last_end = datetime.strptime(w["window_end"], "%Y-%m-%d")

    return sorted(filtered[:top_k], key=lambda x: x["window_start"])


def _describe_window(score: float, domain: str) -> str:
    if score >= 0.78:
        return f"Excellent window for {domain} — strong planetary support, act decisively."
    elif score >= 0.65:
        return f"Good opportunity for {domain} — proceed with moderate effort."
    elif score >= 0.52:
        return f"Neutral/mixed period for {domain} — consolidate, avoid big risks."
    elif score >= 0.40:
        return f"Caution for {domain} — delays and obstacles likely."
    else:
        return f"Unfavourable period for {domain} — rest, recover, don't initiate."


# ─── Worst windows ────────────────────────────────────────────────────────────

def find_worst_windows(
        base_transit_lons: Dict[str, float],
        reference_date: datetime,
        natal_moon_sign: int,
        domain: str = "career",
        months_ahead: int = 12,
        sarva_av: Optional[List[int]] = None,
        dasha_alignment_map: Optional[Dict[str, float]] = None,
        resolution_days: int = 3,
        top_k: int = 3,
) -> List[Dict]:
    """Return the worst windows (lowest scores) — periods to avoid."""
    try:
        from scipy.signal import find_peaks
        import numpy as np
    except ImportError:
        return []

    total_days = int(months_ahead * 30.44)
    dates: List[datetime] = []
    scores: List[float] = []

    def _da(day_num: int) -> float:
        if not dasha_alignment_map:
            return 0.5
        d = reference_date + timedelta(days=day_num)
        return dasha_alignment_map.get(d.strftime("%Y-%m"), 0.5)

    for day in range(0, total_days, resolution_days):
        target = reference_date + timedelta(days=day)
        lons = _compute_approximate_transit_lons(
            base_transit_lons, reference_date, target)
        scores.append(_daily_transit_score(lons, natal_moon_sign, domain, sarva_av, _da(day)))
        dates.append(target)

    if not scores:
        return []

    arr = np.array(scores)
    troughs, _ = find_peaks(-arr, prominence=0.04,
                             distance=max(3, 20 // resolution_days))
    troughs_sorted = sorted(troughs, key=lambda i: scores[i])

    windows = []
    for t_idx in troughs_sorted[:top_k]:
        dt = dates[t_idx]
        w_start = max(dt - timedelta(days=10), reference_date)
        w_end   = min(dt + timedelta(days=10), reference_date + timedelta(days=total_days))
        windows.append({
            "window_start": w_start.strftime("%Y-%m-%d"),
            "window_end": w_end.strftime("%Y-%m-%d"),
            "trough_date": dt.strftime("%Y-%m-%d"),
            "score": round(scores[t_idx], 3),
            "domain": domain,
            "description": _describe_window(scores[t_idx], domain),
        })
    return sorted(windows, key=lambda x: x["window_start"])
