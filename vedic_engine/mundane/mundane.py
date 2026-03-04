"""
Phase 3D — Mundane Astrology Computational Framework.

Implements four core mundane astrology modules:
  1. Ingress Validity — modality rule for how many ingress charts are needed
  2. Eclipse Duration Mapping — hours of totality → years/months of terrestrial impact
  3. Great Conjunction Phase — Jupiter-Saturn synodic phase tracker (elemental epoch)
  4. Gann Price-to-Degree — W.D. Gann's formula mapping market prices to zodiacal degrees

Architecture Note: ALL functions are pure computation.
No prediction weights or domain logic — those belong in engine.py (3F).

References: Mundane Astrology Framework For Engine.md
"""
from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple


# ─── Constants ────────────────────────────────────────────────────────────────

SIGN_NAMES: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Jupiter-Saturn 2020 conjunction (Great Mutation baseline)
_JS_CONJ_2020 = date(2020, 12, 21)
_JS_SYNODIC_PERIOD_DAYS = 7253.4   # ≈ 19.86 Julian years

# Elemental triplicities (sign index modulo 4 pattern)
# Fire: 0,4,8 (Aries,Leo,Sagittarius)
# Earth: 1,5,9 (Taurus,Virgo,Capricorn)
# Air: 2,6,10 (Gemini,Libra,Aquarius)
# Water: 3,7,11 (Cancer,Scorpio,Pisces)
_ELEMENT_NAMES = {0: "Fire", 1: "Earth", 2: "Air", 3: "Water"}

# Sign modalities by sign index (0=Aries…)
_CARDINAL_SIGNS = {0, 3, 6, 9}
_FIXED_SIGNS    = {1, 4, 7, 10}
_MUTABLE_SIGNS  = {2, 5, 8, 11}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _sign_of(lon: float) -> int:
    """Return sign index (0-indexed) for a longitude."""
    return int(lon % 360.0 // 30) % 12


def _sign_element(sign_idx: int) -> str:
    """Return element name for a sign ('Fire','Earth','Air','Water')."""
    return _ELEMENT_NAMES.get(sign_idx % 4, "Unknown")


def _sign_modality(sign_idx: int) -> str:
    """Return modality of a sign ('cardinal','fixed','mutable')."""
    s = sign_idx % 12
    if s in _CARDINAL_SIGNS:
        return "cardinal"
    if s in _FIXED_SIGNS:
        return "fixed"
    return "mutable"


# ─── 1. Ingress Validity ─────────────────────────────────────────────────────

def compute_ingress_validity(
    aries_ingress_asc_lon: float,
) -> Dict[str, Any]:
    """
    Apply Persian ingress rules to determine how many ingress charts govern the year.

    Classical rule (from Mundane Astrology Framework):
      - Fixed ASC sign   → 1 chart governs entire year (stable year)
      - Mutable ASC sign → 2 charts: Aries Ingress (H1) + Libra Ingress (H2)
      - Cardinal ASC sign→ 4 charts: all four seasonal ingresses (volatile year)

    Args:
        aries_ingress_asc_lon:  Ascendant longitude (degrees) of the Aries Ingress chart.
                                Computed by caller using ephemeris at exact Aries ingress moment.

    Returns:
        {
          "asc_sign":          int,
          "asc_sign_name":     str,
          "modality":          str ("fixed"|"mutable"|"cardinal"),
          "charts_needed":     int (1, 2, or 4),
          "ingress_seasons":   list[str],   # which ingresses are valid
          "political_climate": str,
          "description":       str,
        }
    """
    asc_sign = _sign_of(aries_ingress_asc_lon)
    modality = _sign_modality(asc_sign)

    if modality == "fixed":
        charts_needed   = 1
        seasons         = ["Aries"]
        climate         = "Stable"
        description     = ("Fixed ASC: one chart governs the entire year. "
                           "Geopolitical conditions are stable; no major systemic pivots expected.")
    elif modality == "mutable":
        charts_needed   = 2
        seasons         = ["Aries", "Libra"]
        climate         = "Semi-volatile"
        description     = ("Mutable ASC: two ingress charts needed. "
                           "Aries governs H1; Libra Ingress governs H2. "
                           "Moderate instability; shifts at the autumn equinox.")
    else:   # cardinal
        charts_needed   = 4
        seasons         = ["Aries", "Cancer", "Libra", "Capricorn"]
        climate         = "Highly volatile"
        description     = ("Cardinal ASC: all four seasonal ingresses are active. "
                           "Each governs its quarter. Year characterized by rapid geopolitical flux.")

    return {
        "asc_sign":          asc_sign,
        "asc_sign_name":     SIGN_NAMES[asc_sign],
        "modality":          modality,
        "charts_needed":     charts_needed,
        "ingress_seasons":   seasons,
        "political_climate": climate,
        "description":       description,
    }


# ─── 2. Eclipse Duration Mapping ─────────────────────────────────────────────

def compute_eclipse_impact(
    eclipse_type: str,
    totality_hours: float,
    eclipse_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Map eclipse totality duration to terrestrial impact duration.

    Classical Ptolemaic / traditional mundane rules:
      Solar eclipse: duration in hours → duration of impact in YEARS
      Lunar eclipse: duration in hours → duration of impact in MONTHS

    Args:
        eclipse_type:    "solar" or "lunar".
        totality_hours:  Duration of maximum obscuration in hours (decimal).
        eclipse_date:    Date of the eclipse (for computing impact end date). Optional.

    Returns:
        {
          "eclipse_type":       str,
          "totality_hours":     float,
          "impact_unit":        "years" or "months",
          "impact_duration":    float,
          "impact_end_date":    date or None,
          "description":        str,
        }
    """
    eclipse_type = eclipse_type.lower().strip()
    if eclipse_type not in ("solar", "lunar"):
        raise ValueError("eclipse_type must be 'solar' or 'lunar'")

    if eclipse_type == "solar":
        unit     = "years"
        dur      = totality_hours        # 1 hour totality = 1 year of impact
        days_off = int(round(dur * 365.25))
    else:
        unit     = "months"
        dur      = totality_hours        # 1 hour totality = 1 month of impact
        days_off = int(round(dur * 30.44))

    impact_end: Optional[date] = None
    if eclipse_date is not None:
        try:
            from datetime import timedelta
            impact_end = eclipse_date + timedelta(days=days_off)
        except Exception:
            pass

    description = (f"A {eclipse_type} eclipse lasting {totality_hours:.2f} hours of totality "
                   f"generates approximately {dur:.1f} {unit} of terrestrial geopolitical impact.")

    return {
        "eclipse_type":    eclipse_type,
        "totality_hours":  totality_hours,
        "impact_unit":     unit,
        "impact_duration": round(dur, 3),
        "impact_end_date": impact_end,
        "description":     description,
    }


# ─── 3. Great Conjunction Phase ──────────────────────────────────────────────

def compute_great_conjunction_phase(
    target_date: date,
    jupiter_lon: Optional[float] = None,
    saturn_lon: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Compute the current Jupiter-Saturn Great Conjunction phase.

    The 2020 Great Mutation (Dec 21, 2020 at 0° Aquarius) began the Air epoch.
    Subsequent conjunctions occur every ~19.86 years.

    If jupiter_lon and saturn_lon are provided, compute the actual synodic phase
    angle (0° = conjunction, 180° = opposition).

    Args:
        target_date:   Date to evaluate.
        jupiter_lon:   Current Jupiter longitude (optional).
        saturn_lon:    Current Saturn longitude (optional).

    Returns:
        {
          "days_since_2020_conj":    int,
          "years_since_2020_conj":   float,
          "synodic_phase_pct":       float,   # 0.0-1.0 of full cycle elapsed
          "estimated_next_conj_year":int,
          "elemental_epoch":         str,     # "Air" (current ~2020-2219)
          "epoch_description":       str,
          "current_phase_degrees":   float or None,   # JS separation if lons given
          "current_phase_name":      str or None,
          "element_of_last_conj":    str,
        }
    """
    days_since = (target_date - _JS_CONJ_2020).days
    years_since = days_since / 365.25
    synodic_pct = (days_since % _JS_SYNODIC_PERIOD_DAYS) / _JS_SYNODIC_PERIOD_DAYS

    # Estimate next conjunction
    next_in_days  = _JS_SYNODIC_PERIOD_DAYS - (days_since % _JS_SYNODIC_PERIOD_DAYS)
    next_conj_date = _JS_CONJ_2020
    from datetime import timedelta
    next_conj_date = target_date + timedelta(days=int(next_in_days))
    next_conj_year = next_conj_date.year

    # Current epoch
    epoch       = "Air"
    epoch_desc  = ("Air epoch (c. 2020–2219): eras of decentralisation, technological "
                   "innovation, digital networks, and ideological globalisation.")

    # Synodic phase name
    phase_deg: Optional[float] = None
    phase_name: Optional[str]  = None
    if jupiter_lon is not None and saturn_lon is not None:
        phase_deg = round((jupiter_lon - saturn_lon) % 360.0, 2)
        if phase_deg < 30:
            phase_name = "Conjunction"
        elif phase_deg < 90:
            phase_name = "Waxing Crescent"
        elif phase_deg < 120:
            phase_name = "Waxing Square"
        elif phase_deg < 180:
            phase_name = "Waxing Trine"
        elif phase_deg < 210:
            phase_name = "Opposition"
        elif phase_deg < 270:
            phase_name = "Waning Trine"
        elif phase_deg < 330:
            phase_name = "Waning Square"
        else:
            phase_name = "Waning Crescent"

    return {
        "days_since_2020_conj":    days_since,
        "years_since_2020_conj":   round(years_since, 3),
        "synodic_phase_pct":       round(synodic_pct, 4),
        "estimated_next_conj_year":next_conj_year,
        "elemental_epoch":         epoch,
        "epoch_description":       epoch_desc,
        "current_phase_degrees":   phase_deg,
        "current_phase_name":      phase_name,
        "element_of_last_conj":    "Air",  # 0° Aquarius = Air sign
    }


# ─── 4. Gann Price-to-Degree Conversion ──────────────────────────────────────

def compute_gann_price_to_degree(price: float) -> Dict[str, Any]:
    """
    Convert a market price or time unit to a zodiacal degree using W.D. Gann's formula.

    Gann's formula:
        degree = ((√price × 180) − 225) mod 360

    The resulting degree is overlaid on an ephemeris. If a planet is currently
    transiting that degree, a market reversal or breakout is flagged.

    Args:
        price:  Market price or time (must be > 0).

    Returns:
        {
          "price":          float,
          "sqrt_price":     float,
          "gann_degree":    float,   # 0–360
          "gann_sign":      int,     # zodiac sign (0–11)
          "gann_sign_name": str,
          "gann_degree_in_sign": float,   # degrees within the sign (0–30)
          "formula":        str,
        }
    """
    if price <= 0:
        raise ValueError("price must be positive")

    sqrt_p = math.sqrt(price)
    raw    = (sqrt_p * 180.0) - 225.0
    degree = raw % 360.0
    sign   = int(degree // 30)
    deg_in_sign = degree - sign * 30.0

    return {
        "price":               price,
        "sqrt_price":          round(sqrt_p, 6),
        "gann_degree":         round(degree, 4),
        "gann_sign":           sign,
        "gann_sign_name":      SIGN_NAMES[sign],
        "gann_degree_in_sign": round(deg_in_sign, 4),
        "formula":             "((√price × 180) − 225) mod 360",
    }


def check_gann_planet_alignment(
    gann_degree: float,
    planet_longitudes: Dict[str, float],
    orb: float = 2.0,
) -> List[Dict[str, Any]]:
    """
    Check if any planet is near the Gann converted degree, flagging market signals.

    Args:
        gann_degree:        Degree from compute_gann_price_to_degree().
        planet_longitudes:  {planet_name: longitude} for current transit sky.
        orb:                Degrees of orb to consider alignment (default 2°).

    Returns:
        List of aligned planet dicts: [{
            "planet": str,
            "planet_lon": float,
            "separation": float,
            "signal": "REVERSAL_OR_BREAKOUT",
        }]
    """
    aligned: List[Dict[str, Any]] = []
    for planet, lon in planet_longitudes.items():
        raw_sep = abs(lon - gann_degree) % 360.0
        sep = raw_sep if raw_sep <= 180.0 else 360.0 - raw_sep
        if sep <= orb:
            aligned.append({
                "planet":     planet,
                "planet_lon": round(lon, 4),
                "separation": round(sep, 4),
                "signal":     "REVERSAL_OR_BREAKOUT",
            })
    aligned.sort(key=lambda x: x["separation"])
    return aligned
