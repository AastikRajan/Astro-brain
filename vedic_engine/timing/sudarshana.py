"""
Sudarshana Chakra — Phase 1E.2 / 1E.3
=======================================
Triple-reference-frame transit evaluation and year-by-year dasha progression.

The Sudarshana Chakra evaluates any transit from THREE concurrent anchors:
  1. Lagna (Ascendant) — physical body / manifestation
  2. Moon (Chandra Lagna) — mind / emotional experience
  3. Sun (Surya Lagna) — soul / vitality / authority

Source: BPHS + Research File 3 (Vedic Astrology Computational Systems)
"""
from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional

from vedic_engine.config import Planet, NATURAL_BENEFICS, NATURAL_MALEFICS

# ── Scoring constants (from research file) ────────────────────────
# Benefics in kendra/trikona/8th → positive
# Malefics in upachaya (3,6,11) → positive
# Malefics in kendra/trikona → negative

_KENDRA     = {1, 4, 7, 10}
_TRIKONA    = {5, 9}
_UPACHAYA   = {3, 6, 11}
_DUSTHANA   = {6, 8, 12}


def _sudarshana_house_score(transit_planet: str, house_from_anchor: int) -> float:
    """
    Score a transit for a single reference-frame house.
    Returns a value in [-3, +3].
    """
    is_natural_benefic = transit_planet in {p.name for p in NATURAL_BENEFICS}
    is_natural_malefic = transit_planet in {p.name for p in NATURAL_MALEFICS}

    h = house_from_anchor
    if is_natural_benefic:
        if h in _KENDRA or h in _TRIKONA or h == 8:
            return 3.0
        if h in _UPACHAYA:
            return 1.0
        if h in _DUSTHANA:
            return -2.0
        return -1.0
    elif is_natural_malefic:
        if h in _UPACHAYA:
            return 3.0     # malefics thrive in upachaya
        if h in _KENDRA or h in _TRIKONA:
            return -3.0   # malefics in angular/trine = severe
        if h == 8 or h == 12:
            return -2.0
        return -1.0
    else:
        # Neutral (Mercury depends on association; treat as weak benefic)
        if h in _KENDRA or h in _TRIKONA:
            return 1.5
        if h in _UPACHAYA:
            return 1.0
        if h in _DUSTHANA:
            return -1.0
        return 0.0


def evaluate_sudarshana(
        transit_planet: str,
        transit_sign: int,           # 0-based sidereal sign index
        lagna_sign: int,             # natal lagna sign 0-based
        moon_sign: int,              # natal moon sign 0-based
        sun_sign: int,               # natal sun sign 0-based
        weights: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Evaluate a single planet's transit using all three Sudarshana frames.

    Returns:
        {
          "lagna_house": int, "lagna_score": float,
          "moon_house": int,  "moon_score": float,
          "sun_house": int,   "sun_score": float,
          "final_score": float,        # weighted sum, range ~ [-3, +3]
          "agreement": str,            # "all_positive" / "mixed" / "all_negative"
          "interpretation": str,
        }
    """
    if weights is None:
        weights = {"lagna": 0.40, "moon": 0.35, "sun": 0.25}

    def _house(transit_s: int, anchor_s: int) -> int:
        return ((transit_s - anchor_s) % 12) + 1

    lagna_h = _house(transit_sign, lagna_sign)
    moon_h  = _house(transit_sign, moon_sign)
    sun_h   = _house(transit_sign, sun_sign)

    l_score = _sudarshana_house_score(transit_planet, lagna_h)
    m_score = _sudarshana_house_score(transit_planet, moon_h)
    s_score = _sudarshana_house_score(transit_planet, sun_h)

    final = (
        weights["lagna"] * l_score +
        weights["moon"]  * m_score +
        weights["sun"]   * s_score
    )

    positives = sum(1 for sc in [l_score, m_score, s_score] if sc > 0)
    negatives = sum(1 for sc in [l_score, m_score, s_score] if sc < 0)

    if positives == 3:
        agreement = "all_positive"
        interp = (
            f"{transit_planet} transit uniformly auspicious from all three anchors. "
            "Maximum kinetic realization: event manifests physically, emotionally, and spiritually."
        )
    elif negatives == 3:
        agreement = "all_negative"
        interp = (
            f"{transit_planet} transit uniformly adverse. "
            "Challenges manifest across body (Lagna), mind (Moon), and soul (Sun)."
        )
    elif positives > negatives:
        agreement = "mostly_positive"
        lagna_qual = "positive" if l_score > 0 else "challenged"
        moon_qual  = "positive" if m_score > 0 else "challenged"
        sun_qual   = "positive" if s_score > 0 else "challenged"
        interp = (
            f"{transit_planet} transit mixed but favorable. "
            f"Lagna={lagna_qual}, Moon={moon_qual}, Sun={sun_qual}."
        )
    else:
        agreement = "mostly_negative"
        interp = (
            f"{transit_planet} transit mostly adverse with partial relief."
        )

    return {
        "lagna_house": lagna_h, "lagna_score": round(l_score, 2),
        "moon_house":  moon_h,  "moon_score":  round(m_score, 2),
        "sun_house":   sun_h,   "sun_score":   round(s_score, 2),
        "final_score": round(final, 3),
        "agreement":   agreement,
        "interpretation": interp,
    }


def compute_sudarshana_dasha(
        natal_lagna_sign: int,   # 0-based (Aries=0)
        age_completed_years: int,
        month_index: int = 0,    # 0-11 within the current year
        block_index: int = 0,    # 0-11 within the current month (~2.5 day blocks)
) -> Dict:
    """
    Compute current Sudarshana Dasha signs at three fractal levels.

    Macro (yearly):   progressed_annual  = (lagna + age) % 12
    Micro (monthly):  progressed_monthly = (annual + month) % 12
    Nano (daily):     progressed_daily   = (monthly + block) % 12

    All values are 0-based sign indices.

    Returns:
        {
          "annual_sign": int,   "annual_sign_name": str,
          "monthly_sign": int,  "monthly_sign_name": str,
          "daily_sign": int,    "daily_sign_name": str,
        }
    """
    _SIGN_NAMES = [
        "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
        "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
    ]
    annual  = (natal_lagna_sign + age_completed_years) % 12
    monthly = (annual + month_index) % 12
    daily   = (monthly + block_index) % 12
    return {
        "annual_sign":       annual,
        "annual_sign_name":  _SIGN_NAMES[annual],
        "monthly_sign":      monthly,
        "monthly_sign_name": _SIGN_NAMES[monthly],
        "daily_sign":        daily,
        "daily_sign_name":   _SIGN_NAMES[daily],
    }


def evaluate_sudarshana_all_planets(
        transit_signs: Dict[str, int],   # {planet_name: sign_idx 0-based}
        lagna_sign: int,
        moon_sign: int,
        sun_sign: int,
        weights: Optional[Dict[str, float]] = None,
) -> List[Dict]:
    """
    Run evaluate_sudarshana for all transiting planets; return sorted list.
    """
    results = []
    for planet, sign in transit_signs.items():
        ev = evaluate_sudarshana(planet, sign, lagna_sign, moon_sign, sun_sign, weights)
        ev["planet"] = planet
        results.append(ev)
    results.sort(key=lambda x: -x["final_score"])
    return results
