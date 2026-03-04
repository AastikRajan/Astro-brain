"""
Phase 3B — Hellenistic Astrology Timing Systems.

Implements five Hellenistic computational modules:
  1. Annual Profections — one sign per year Time-Lord system
  2. Hellenistic Sect (Haeresis) — day/night chart benefic/malefic toggle
  3. Lots of Fortune and Spirit — Hermetic Lots (Kleroi)
  4. Zodiacal Releasing — Vettius Valens time-lord system (Spirit + Fortune)
  5. Midpoints (Cosmobiology) — geometric planetary midpoints

Note on Secondary Progressions:
  Already implemented in vedic_engine/timing/progressions.py as
  compute_secondary_progressions(). Phase 3B.4 delegates to that module;
  no reimplementation is needed here.

Architecture Note: ALL functions are pure computation.
No prediction weights or domain blending — those belong in engine.py (3F).

References:
  - Multi-Tradition Astrology Engine Comparison.md
  - Hellenistic Time Lord Procedures (Scribd)
  - Zodiacal Releasing: An Ancient Timing Technique (YouTube)
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple


# ─── Constants ────────────────────────────────────────────────────────────────

SIGN_NAMES: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Sign-lord strings (0=Aries … 11=Pisces) — Hellenistic 7-planet system
_SIGN_LORD_NAMES: List[str] = [
    "MARS", "VENUS", "MERCURY", "MOON", "SUN", "MERCURY",
    "VENUS", "MARS", "JUPITER", "SATURN", "SATURN", "JUPITER",
]

# Zodiacal Releasing sign periods (years), keyed by sign lord
# Moon=25, Sun=19, Mercury=20, Venus=8, Mars=15, Jupiter=12, Saturn=30
# Source: Vettius Valens — Anthologies (2nd century CE)
_ZR_PERIODS: List[int] = [
    15,   # 0 Aries    (Mars)
    8,    # 1 Taurus   (Venus)
    20,   # 2 Gemini   (Mercury)
    25,   # 3 Cancer   (Moon)
    19,   # 4 Leo      (Sun)
    20,   # 5 Virgo    (Mercury)
    8,    # 6 Libra    (Venus)
    15,   # 7 Scorpio  (Mars)
    12,   # 8 Sagittarius (Jupiter)
    30,   # 9 Capricorn   (Saturn)
    30,   # 10 Aquarius  (Saturn)
    12,   # 11 Pisces    (Jupiter)
]

# Angular signs by index (0=Aries, 3=Cancer, 6=Libra, 9=Capricorn)
_ANGULAR_SIGNS = {0, 3, 6, 9}

# Day-sect planets (Sun above horizon)
_DAY_SECT    = {"SUN", "JUPITER", "SATURN"}
# Night-sect planets (Moon above horizon, i.e. nocturnal chart)
_NIGHT_SECT  = {"MOON", "VENUS", "MARS"}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _normalize(lon: float) -> float:
    """Normalize longitude to [0, 360)."""
    return lon % 360.0


def _sign_of(lon: float) -> int:
    """Return sign index (0=Aries…11=Pisces) for a longitude."""
    return int(_normalize(lon) // 30) % 12


def _zr_period_days(sign_idx: int) -> float:
    """Return the ZR period in days for a sign (1 ZR year = 365.25 days)."""
    return _ZR_PERIODS[sign_idx % 12] * 365.25


# ─── 1. Annual Profections ────────────────────────────────────────────────────

def compute_annual_profection(
    natal_asc_sign_idx: int,
    age_years: int,
) -> Dict[str, Any]:
    """
    Compute the Annual Profection Time-Lord for the current year.

    System: The Ascendant shifts one whole sign per year, cycling every 12 years.
    The ruling planet of the activated sign is the Time Lord for that solar year.

    At age 0 → H1 (natal ASC sign); at age 1 → H2; etc.
    At ages 12, 24, 36, … → returns to H1 (the natal ASC sign).

    Args:
        natal_asc_sign_idx:  Natal ascendant sign index (0=Aries…11=Pisces).
        age_years:           Age in whole years (int).

    Returns:
        {
          "profection_house": int (1–12),
          "active_sign":      int (0–11),
          "active_sign_name": str,
          "time_lord":        str  (planet name),
          "age":              int,
        }
    """
    if age_years < 0:
        age_years = 0
    profection_shift   = age_years % 12
    active_sign        = (natal_asc_sign_idx + profection_shift) % 12
    profection_house   = profection_shift + 1   # 1-indexed

    return {
        "profection_house":  profection_house,
        "active_sign":       active_sign,
        "active_sign_name":  SIGN_NAMES[active_sign],
        "time_lord":         _SIGN_LORD_NAMES[active_sign],
        "age":               age_years,
    }


# ─── 2. Hellenistic Sect (Haeresis) ──────────────────────────────────────────

def compute_hellenistic_sect(is_daytime: bool) -> Dict[str, Any]:
    """
    Determine sect membership and sect-quality for all seven classical planets.

    Hellenistic sect doctrine:
      Day charts:   Sun, Jupiter, Saturn are "in sect" (perform constructively).
                    Moon, Venus, Mars are "out of sect" (less controlled).
      Night charts: Moon, Venus, Mars are "in sect".
                    Sun, Jupiter, Saturn are "out of sect".
      Mercury:      Joins the sect of the predominant luminary (Sun → day, Moon → night).
                    For simplicity always included as "neutral/both".

    Args:
        is_daytime:  True if the Sun is above the horizon at birth moment.

    Returns:
        {
          "chart_sect":    "day" or "night",
          "sect_light":    "SUN" or "MOON",
          "sect_benefics": list[str],   # in-sect benefics for this chart
          "sect_malefics": list[str],   # in-sect malefics (constructive mode)
          "out_of_sect":   list[str],   # planets that are out-of-sect
          "mercury_sect":  str,         # "day" or "night"
        }
    """
    if is_daytime:
        chart_sect    = "day"
        sect_light    = "SUN"
        sect_benefics = ["SUN", "JUPITER"]   # Full in-sect benefics
        sect_malefics = ["SATURN"]            # Malefic activated constructively
        out_of_sect   = ["MOON", "VENUS", "MARS"]
        mercury_sect  = "day"
    else:
        chart_sect    = "night"
        sect_light    = "MOON"
        sect_benefics = ["MOON", "VENUS"]    # Full in-sect benefics
        sect_malefics = ["MARS"]              # Malefic activated constructively
        out_of_sect   = ["SUN", "JUPITER", "SATURN"]
        mercury_sect  = "night"

    # Include Mercury in the in-sect group (Hermaphrodite — joins chart sect)
    all_in_sect = sect_benefics + sect_malefics + ["MERCURY"]

    return {
        "chart_sect":    chart_sect,
        "sect_light":    sect_light,
        "sect_benefics": sect_benefics,
        "sect_malefics": sect_malefics,
        "all_in_sect":   all_in_sect,
        "out_of_sect":   out_of_sect,
        "mercury_sect":  mercury_sect,
    }


# ─── 3. Lots of Fortune and Spirit ───────────────────────────────────────────

def compute_lot_of_fortune(
    asc_lon: float,
    sun_lon: float,
    moon_lon: float,
    is_daytime: bool,
) -> float:
    """
    Compute the Hellenistic Lot of Fortune (Tyche).

    Formula:
      Day:   Fortune = (ASC + Moon - Sun) mod 360
      Night: Fortune = (ASC + Sun - Moon) mod 360

    Represents: Body, material circumstances, and fortune.

    Returns:
        Longitude of Lot of Fortune in [0, 360).
    """
    if is_daytime:
        lot = asc_lon + moon_lon - sun_lon
    else:
        lot = asc_lon + sun_lon - moon_lon
    return _normalize(lot)


def compute_lot_of_spirit(
    asc_lon: float,
    sun_lon: float,
    moon_lon: float,
    is_daytime: bool,
) -> float:
    """
    Compute the Hellenistic Lot of Spirit (Daimon).

    Formula (reverse of Fortune):
      Day:   Spirit = (ASC + Sun - Moon) mod 360
      Night: Spirit = (ASC + Moon - Sun) mod 360

    Represents: Mind, soul, career, and deliberate intentions.

    Returns:
        Longitude of Lot of Spirit in [0, 360).
    """
    if is_daytime:
        lot = asc_lon + sun_lon - moon_lon
    else:
        lot = asc_lon + moon_lon - sun_lon
    return _normalize(lot)


# ─── 4. Zodiacal Releasing (ZR) ──────────────────────────────────────────────

def compute_zodiacal_releasing(
    lot_longitude: float,
    birth_date:    date,
    target_date:   date,
    lot_name:      str = "spirit",
) -> Dict[str, Any]:
    """
    Compute the Zodiacal Releasing time-lord at a target date.

    ZR system (Vettius Valens) partitions life into sign-chapters based on
    the Lot's natal sign and fixed planetary period lengths.

    Each sign has a year-count based on its lord (see _ZR_PERIODS).
    The sequence cycles: Lot's sign → next sign → … continuously.

    Level 1 (L1): Major period (years of the sign).
    Level 2 (L2): Sub-period within L1 (signs in sub-sequence, each × (L1 years / 12)).

    This implementation computes only L1 and the active sign within it.

    Args:
        lot_longitude:  Longitude of the Lot (Fortune or Spirit) in [0, 360).
        birth_date:     Date of birth.
        target_date:    Date to evaluate.
        lot_name:       "spirit" or "fortune" (informational only).

    Returns:
        {
          "lot_name":          str,
          "lot_longitude":     float,
          "lot_sign":          int (0–11),
          "lot_sign_name":     str,
          "current_period": {
               "sign":        int,
               "sign_name":   str,
               "period_lord": str,
               "period_years":int,
               "years_elapsed":float,
               "years_remaining":float,
               "is_angular":  bool,     # angular signs = peak/eminence
               "days_elapsed": int,
          },
          "error":             str or None,
        }
    """
    lot_sign = _sign_of(lot_longitude)
    out: Dict[str, Any] = {
        "lot_name":      lot_name,
        "lot_longitude": round(lot_longitude, 4),
        "lot_sign":      lot_sign,
        "lot_sign_name": SIGN_NAMES[lot_sign],
        "current_period": {},
        "error": None,
    }

    try:
        if target_date < birth_date:
            out["error"] = "target_date before birth_date"
            return out

        elapsed_days = (target_date - birth_date).days
        elapsed_total = float(elapsed_days)

        # Walk through sign periods sequentially from birth to target
        current_sign = lot_sign
        remaining_days = elapsed_total

        while True:
            period_days = _zr_period_days(current_sign)
            if remaining_days < period_days:
                # We are in this sign's period
                years_elapsed    = remaining_days / 365.25
                years_remaining  = (period_days - remaining_days) / 365.25
                out["current_period"] = {
                    "sign":            current_sign,
                    "sign_name":       SIGN_NAMES[current_sign],
                    "period_lord":     _SIGN_LORD_NAMES[current_sign],
                    "period_years":    _ZR_PERIODS[current_sign],
                    "years_elapsed":   round(years_elapsed, 3),
                    "years_remaining": round(years_remaining, 3),
                    "is_angular":      current_sign in _ANGULAR_SIGNS,
                    "days_elapsed":    int(remaining_days),
                }
                break
            remaining_days -= period_days
            current_sign = (current_sign + 1) % 12

    except Exception as e:
        out["error"] = str(e)

    return out


# ─── 5. Midpoints ─────────────────────────────────────────────────────────────

def compute_midpoints(
    planet_longitudes: Dict[str, float],
) -> Dict[str, float]:
    """
    Compute all pairwise Cosmobiology midpoints between planets.

    A midpoint is the exact geometric average of two planetary longitudes,
    always taken as the shorter arc midpoint (0–180° range from each planet).

    Returned as: {"SUN/MOON": midpoint_lon, "MOON/MARS": midpoint_lon, ...}
    Pairs are sorted alphabetically (e.g., "JUPITER/SATURN" not "SATURN/JUPITER").

    Key mid-points of interpretive significance (automatically labeled):
      SUN/MOON  → life balance / marriage axis
      ASC/MC    → personality-career axis
      VENUS/MARS→ relationship / drive axis
      JUPITER/SATURN → growth-restriction axis

    Args:
        planet_longitudes:  {planet_name: longitude_in_degrees}

    Returns:
        {"{P1}/{P2}": midpoint_lon_in_degrees, ...}
        Midpoint longitude ∈ [0, 360).
    """
    planets = sorted(planet_longitudes.keys())
    midpoints: Dict[str, float] = {}

    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1, p2 = planets[i], planets[j]
            lon1, lon2 = planet_longitudes[p1], planet_longitudes[p2]

            # Compute the two possible midpoints and pick the shorter-arc one
            mid1 = (lon1 + lon2) / 2.0
            mid2 = (mid1 + 180.0) % 360.0

            # Use the midpoint closer to both planets via angular distance
            sep = abs(lon1 - lon2) % 360.0
            if sep > 180.0:
                sep = 360.0 - sep

            # For arcs ≤ 180°, mid1 is the nearby midpoint;
            # for wider arcs, antiscial midpoint mid2 is primary.
            primary_mid = mid1 if sep <= 180.0 else mid2
            primary_mid = _normalize(primary_mid)

            key = f"{p1}/{p2}"
            midpoints[key] = round(primary_mid, 4)

    return midpoints


# ─── Convenience: compute all Hellenistic signals ─────────────────────────────

def compute_all_hellenistic_signals(
    natal_asc_lon:    float,
    natal_asc_sign:   int,
    sun_lon:          float,
    moon_lon:         float,
    planet_longitudes: Dict[str, float],
    birth_date:       date,
    target_date:      date,
    age_years:        int,
    is_daytime:       bool,
) -> Dict[str, Any]:
    """
    Convenience wrapper — compute all Hellenistic signals in one call.

    Args:
        natal_asc_lon:    Natal ascendant longitude [0,360).
        natal_asc_sign:   Natal ascendant sign index (0–11).
        sun_lon:          Natal Sun longitude.
        moon_lon:         Natal Moon longitude.
        planet_longitudes:{planet_name: longitude} for all natal planets.
        birth_date:       Date of birth.
        target_date:      Analysis date.
        age_years:        Age in whole years.
        is_daytime:       True if birth was in daytime.

    Returns:
        {
          "annual_profection":         dict,
          "hellenistic_sect":          dict,
          "lot_of_fortune_lon":        float,
          "lot_of_spirit_lon":         float,
          "zodiacal_releasing_spirit": dict,
          "zodiacal_releasing_fortune":dict,
          "midpoints":                 dict,
          "errors":                    list[str],
        }
    """
    out: Dict[str, Any] = {"errors": []}

    try:
        out["annual_profection"] = compute_annual_profection(natal_asc_sign, age_years)
    except Exception as e:
        out["annual_profection"] = {}
        out["errors"].append(f"Profection: {e}")

    try:
        out["hellenistic_sect"] = compute_hellenistic_sect(is_daytime)
    except Exception as e:
        out["hellenistic_sect"] = {}
        out["errors"].append(f"Sect: {e}")

    try:
        lot_f = compute_lot_of_fortune(natal_asc_lon, sun_lon, moon_lon, is_daytime)
        out["lot_of_fortune_lon"] = round(lot_f, 4)
    except Exception as e:
        lot_f = 0.0
        out["lot_of_fortune_lon"] = 0.0
        out["errors"].append(f"LotFortune: {e}")

    try:
        lot_s = compute_lot_of_spirit(natal_asc_lon, sun_lon, moon_lon, is_daytime)
        out["lot_of_spirit_lon"] = round(lot_s, 4)
    except Exception as e:
        lot_s = 0.0
        out["lot_of_spirit_lon"] = 0.0
        out["errors"].append(f"LotSpirit: {e}")

    try:
        out["zodiacal_releasing_spirit"] = compute_zodiacal_releasing(
            lot_s, birth_date, target_date, lot_name="spirit"
        )
    except Exception as e:
        out["zodiacal_releasing_spirit"] = {}
        out["errors"].append(f"ZR_Spirit: {e}")

    try:
        out["zodiacal_releasing_fortune"] = compute_zodiacal_releasing(
            lot_f, birth_date, target_date, lot_name="fortune"
        )
    except Exception as e:
        out["zodiacal_releasing_fortune"] = {}
        out["errors"].append(f"ZR_Fortune: {e}")

    try:
        out["midpoints"] = compute_midpoints(planet_longitudes)
    except Exception as e:
        out["midpoints"] = {}
        out["errors"].append(f"Midpoints: {e}")

    return out
