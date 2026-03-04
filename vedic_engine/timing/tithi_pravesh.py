"""
Tithi Pravesh — Luni-Solar Annual Return.

Algorithm: Find the exact moment each year when:
  1. Sun is in its natal sidereal Rashi (sign)
  2. (Transit_Moon - Transit_Sun) ≡ (Natal_Moon - Natal_Sun) (mod 360°)

This differs from Varshaphala (solar return to exact natal Sun longitude).
Tithi Pravesh is especially used for relationship and lunar-themed events.

Reference: Classical Tajika; TP charts read via Tajika methods.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List


# ── Weekday → Planet Year Lord ─────────────────────────────────
WEEKDAY_LORDS = {
    0: "SUN",       # Sunday
    1: "MOON",      # Monday
    2: "MARS",      # Tuesday
    3: "MERCURY",   # Wednesday
    4: "JUPITER",   # Thursday
    5: "VENUS",     # Friday
    6: "SATURN",    # Saturday
}

# ── Lagna-to-natal relation quality ────────────────────────────
# Kendra (1/4/7/10) → successful, Trikona (5/9) → prosperous,
# Dusthana (6/8/12) → problematic, Others → moderate
def _lagna_relation_quality(offset: int) -> str:
    """Return quality label for TP lagna's house offset from natal lagna."""
    offset = offset % 12
    if offset in (0, 3, 6, 9):   # houses 1,4,7,10
        return "KENDRA_SUCCESS"
    if offset in (4, 8):          # houses 5,9
        return "TRIKONA_PROSPERITY"
    if offset in (5, 7, 11):      # houses 6,8,12
        return "DUSTHANA_TROUBLE"
    return "MODERATE"


def compute_natal_tithi_angle(natal_moon_lon: float, natal_sun_lon: float) -> float:
    """Compute natal tithi angle = (Moon - Sun) mod 360."""
    return (natal_moon_lon - natal_sun_lon) % 360.0


def get_natal_tithi_number(natal_moon_lon: float, natal_sun_lon: float) -> int:
    """Tithi = floor((Moon - Sun) / 12) + 1, range 1..30."""
    angle = (natal_moon_lon - natal_sun_lon) % 360.0
    return int(angle / 12.0) + 1


def compute_tithi_pravesh(
    natal_sun_lon: float,
    natal_moon_lon: float,
    natal_lagna_sign: int,
    year: int,
    transit_sun_lon: Optional[float] = None,
    transit_moon_lon: Optional[float] = None,
    pravesh_weekday: Optional[int] = None,
    pravesh_lagna_sign: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Compute Tithi Pravesh analysis for a given year.

    Without an ephemeris, we cannot solve for the exact moment iteratively.
    This function computes the diagnostic framework: natal tithi angle,
    year lord from weekday, lagna relation quality, and hora-lord assessment.

    Args:
        natal_sun_lon:      Natal Sun longitude (sidereal)
        natal_moon_lon:     Natal Moon longitude (sidereal)
        natal_lagna_sign:   Natal Lagna sign index (0-11)
        year:               Calendar year for TP
        transit_sun_lon:    Transit Sun longitude at TP moment (if known)
        transit_moon_lon:   Transit Moon longitude at TP moment (if known)
        pravesh_weekday:    Weekday of TP moment (0=Sun..6=Sat, if known)
        pravesh_lagna_sign: Lagna sign of TP chart (if known)

    Returns:
        Comprehensive TP analysis dict.
    """
    natal_tithi_angle = compute_natal_tithi_angle(natal_moon_lon, natal_sun_lon)
    natal_tithi = get_natal_tithi_number(natal_moon_lon, natal_sun_lon)
    natal_sun_sign = int(natal_sun_lon / 30) % 12

    # Year Lord from weekday
    year_lord = WEEKDAY_LORDS.get(pravesh_weekday, "UNKNOWN") if pravesh_weekday is not None else "UNKNOWN"

    # Lagna relation
    lagna_quality = "UNKNOWN"
    lagna_offset = None
    if pravesh_lagna_sign is not None:
        lagna_offset = (pravesh_lagna_sign - natal_lagna_sign) % 12
        lagna_quality = _lagna_relation_quality(lagna_offset)

    # Hora lord (simplified: Sun for odd hours from sunrise, Moon for even)
    hora_lord = "UNKNOWN"

    # Muntha: sign = natal lagna + completed years
    completed_years = max(0, year - 1)  # placeholder
    muntha_sign = (natal_lagna_sign + completed_years) % 12

    # Verify tithi match if transit positions provided
    tithi_match = False
    if transit_sun_lon is not None and transit_moon_lon is not None:
        tp_angle = (transit_moon_lon - transit_sun_lon) % 360.0
        tp_tithi = int(tp_angle / 12.0) + 1
        tithi_match = (tp_tithi == natal_tithi)

    return {
        "year": year,
        "natal_tithi": natal_tithi,
        "natal_tithi_angle": round(natal_tithi_angle, 4),
        "natal_sun_sign": natal_sun_sign,
        "year_lord": year_lord,
        "year_lord_weekday": pravesh_weekday,
        "pravesh_lagna_sign": pravesh_lagna_sign,
        "lagna_offset_from_natal": lagna_offset,
        "lagna_quality": lagna_quality,
        "muntha_sign": muntha_sign,
        "hora_lord": hora_lord,
        "tithi_match": tithi_match,
        "interpretation": {
            "year_lord_note": f"Year Lord {year_lord} — assess its dignity/house in TP chart for annual fortune",
            "lagna_note": f"TP Lagna quality: {lagna_quality}",
        },
    }


def solve_tithi_pravesh_iterative(
    natal_tithi_angle: float,
    natal_sun_sign: int,
    approximate_date: datetime,
    get_sun_lon,
    get_moon_lon,
    max_iterations: int = 100,
    tolerance_deg: float = 0.01,
) -> Optional[datetime]:
    """
    Iterative solver for exact Tithi Pravesh moment.

    Requires callable ephemeris functions:
        get_sun_lon(datetime) -> float  (sidereal longitude)
        get_moon_lon(datetime) -> float (sidereal longitude)

    Algorithm:
    1. Start near solar ingress into natal Sun sign
    2. Compute current tithi angle: (Moon - Sun) mod 360
    3. Compare to natal tithi angle
    4. Adjust by Moon's daily motion (~13°/day) to converge

    Returns datetime of TP moment or None if not converged.
    """
    dt = approximate_date
    sign_start = natal_sun_sign * 30.0
    sign_end = sign_start + 30.0

    for _ in range(max_iterations):
        sun_lon = get_sun_lon(dt)
        moon_lon = get_moon_lon(dt)

        # Check Sun is in natal sign
        sun_in_sign = (sign_start <= (sun_lon % 360) < sign_end)
        if not sun_in_sign:
            # Move forward 1 day toward sign
            dt += timedelta(days=1)
            continue

        current_angle = (moon_lon - sun_lon) % 360.0
        diff = (current_angle - natal_tithi_angle + 180) % 360 - 180

        if abs(diff) < tolerance_deg:
            return dt

        # Moon moves ~13.2°/day, adjust
        days_adjust = -diff / 13.2
        dt += timedelta(days=days_adjust)

    return None
