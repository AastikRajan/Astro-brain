"""
Kalachakra Dasha Engine (Branch B).

Described by Parashara as the supreme Dasha system.
Based on Navamsa (Pada) of the natal Moon's Nakshatra.

Key structures:
  - Savya (Clockwise) groups 1,2,3
  - Apasavya (Counter-Clockwise) groups 4,5,6
  - Each sign has a fixed duration in years
  - Antardasha = (Maha_years × Sub_years) / Paramayus
  - Deha sign = Body sign; Jeeva sign = Soul sign
  - Gatis: Manduki (2-sign leap) and Simhavalokana (trinal leap)
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any

# ── Sign durations (years per sign) ──────────────────────────────────────────
SIGN_YEARS: Dict[str, int] = {
    "Aries": 7, "Taurus": 16, "Gemini": 9, "Cancer": 21,
    "Leo": 5, "Virgo": 9, "Libra": 16, "Scorpio": 7,
    "Sagittarius": 10, "Capricorn": 4, "Aquarius": 4, "Pisces": 10,
}

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# ── Nakshatra groupings ───────────────────────────────────────────────────────
# Each nakshatra is 0-indexed (Ashwini=0 ... Revati=26)
# Group number (1-6), Savya = groups 1,2,3; Apasavya = 4,5,6

_NAK_GROUP: Dict[int, int] = {
    # Savya Group 1: Ashwini(0), Punarvasu(6), Hasta(12), Moola(18), PurvaBhadra(24)
    0: 1, 6: 1, 12: 1, 18: 1, 24: 1,
    # Savya Group 2: Bharani(1), Pushya(7), Chitra(13), Purvashadha(19), UttaraBhadra(25)
    1: 2, 7: 2, 13: 2, 19: 2, 25: 2,
    # Savya Group 3: Krittika(2), Ashlesha(8), Swati(14), Uttarashadha(20), Revati(26)
    2: 3, 8: 3, 14: 3, 20: 3, 26: 3,
    # Apasavya Group 4: Rohini(4), Magha(9), Vishakha(15), Shravana(21)
    4: 4, 9: 4, 15: 4, 21: 4,
    # Apasavya Group 5: Mrigashira(5), PurvaPhalguni(10), Anuradha(16), Dhanishta(22)
    5: 5, 10: 5, 16: 5, 22: 5,
    # Apasavya Group 6: Ardra(3), UttaraPhalguni(11), Jyeshtha(17), Shatabhisha(23)
    3: 6, 11: 6, 17: 6, 23: 6,
}

# Pada (quarter) of Moon within nakshatra: 0-3 for each 3°20' quarter
# To compute: position_in_nak / (13.333/4) => floor => 0..3

# ── Sequence arrays per group per pada ───────────────────────────────────────
# Format: (sign_sequence_list, paramayus, deha_sign, jeeva_sign)

_SEQUENCE_TABLE: Dict[Tuple[int, int], Tuple[List[str], int, str, str]] = {
    # Savya Groups 1 and 3
    (1, 0): (["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius"], 100, "Aries", "Sagittarius"),
    (1, 1): (["Capricorn","Aquarius","Pisces","Scorpio","Libra","Virgo","Cancer","Leo","Gemini"], 85, "Taurus", "Cancer"),
    (1, 2): (["Taurus","Aries","Pisces","Aquarius","Capricorn","Sagittarius","Aries","Taurus","Gemini"], 83, "Taurus", "Gemini"),
    (1, 3): (["Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"], 86, "Cancer", "Pisces"),
    (3, 0): (["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius"], 100, "Aries", "Sagittarius"),
    (3, 1): (["Capricorn","Aquarius","Pisces","Scorpio","Libra","Virgo","Cancer","Leo","Gemini"], 85, "Taurus", "Cancer"),
    (3, 2): (["Taurus","Aries","Pisces","Aquarius","Capricorn","Sagittarius","Aries","Taurus","Gemini"], 83, "Taurus", "Gemini"),
    (3, 3): (["Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"], 86, "Cancer", "Pisces"),
    # Savya Group 2
    (2, 0): (["Scorpio","Libra","Virgo","Cancer","Leo","Gemini","Taurus","Aries","Pisces"], 100, "Scorpio", "Pisces"),
    (2, 1): (["Aquarius","Capricorn","Sagittarius","Aries","Taurus","Gemini","Cancer","Leo","Virgo"], 85, "Aquarius", "Virgo"),
    (2, 2): (["Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces","Scorpio","Libra","Virgo"], 83, "Libra", "Virgo"),
    (2, 3): (["Cancer","Leo","Gemini","Taurus","Aries","Pisces","Aquarius","Capricorn","Sagittarius"], 86, "Cancer", "Sagittarius"),
    # Apasavya Groups 4 and 6
    (4, 0): (["Sagittarius","Capricorn","Aquarius","Pisces","Aries","Taurus","Gemini","Leo","Cancer"], 86, "Sagittarius", "Cancer"),
    (4, 1): (["Virgo","Libra","Scorpio","Pisces","Aquarius","Capricorn","Sagittarius","Scorpio","Libra"], 83, "Virgo", "Libra"),
    (4, 2): (["Virgo","Leo","Cancer","Gemini","Taurus","Aries","Sagittarius","Capricorn","Aquarius"], 85, "Virgo", "Aquarius"),
    (4, 3): (["Pisces","Aries","Taurus","Gemini","Leo","Cancer","Virgo","Libra","Scorpio"], 100, "Pisces", "Scorpio"),
    (6, 0): (["Sagittarius","Capricorn","Aquarius","Pisces","Aries","Taurus","Gemini","Leo","Cancer"], 86, "Sagittarius", "Cancer"),
    (6, 1): (["Virgo","Libra","Scorpio","Pisces","Aquarius","Capricorn","Sagittarius","Scorpio","Libra"], 83, "Virgo", "Libra"),
    (6, 2): (["Virgo","Leo","Cancer","Gemini","Taurus","Aries","Sagittarius","Capricorn","Aquarius"], 85, "Virgo", "Aquarius"),
    (6, 3): (["Pisces","Aries","Taurus","Gemini","Leo","Cancer","Virgo","Libra","Scorpio"], 100, "Pisces", "Scorpio"),
    # Apasavya Group 5
    (5, 0): (["Pisces","Aquarius","Capricorn","Sagittarius","Scorpio","Libra","Virgo","Leo","Cancer"], 86, "Pisces", "Cancer"),
    (5, 1): (["Gemini","Taurus","Aries","Sagittarius","Capricorn","Aquarius","Pisces","Aries","Taurus"], 83, "Gemini", "Taurus"),
    (5, 2): (["Gemini","Leo","Cancer","Virgo","Libra","Scorpio","Pisces","Aquarius","Capricorn"], 85, "Gemini", "Capricorn"),
    (5, 3): (["Sagittarius","Scorpio","Libra","Virgo","Leo","Cancer","Gemini","Taurus","Aries"], 100, "Sagittarius", "Aries"),
}

_NAKSHATRA_SPAN = 13.333333  # degrees per nakshatra
_PADA_SPAN = _NAKSHATRA_SPAN / 4.0  # 3.333... degrees per pada


def _get_nak_pada(moon_longitude: float) -> Tuple[int, int]:
    """Return (nakshatra_index 0-26, pada 0-3) for a given Moon longitude."""
    lon = moon_longitude % 360.0
    nak_idx = int(lon / _NAKSHATRA_SPAN)
    pos_in_nak = lon - nak_idx * _NAKSHATRA_SPAN
    pada = int(pos_in_nak / _PADA_SPAN)
    if pada > 3:
        pada = 3
    return nak_idx, pada


def _remaining_pada_fraction(moon_longitude: float) -> float:
    """Fraction of current pada remaining (0.0 to 1.0)."""
    lon = moon_longitude % 360.0
    nak_idx = int(lon / _NAKSHATRA_SPAN)
    pos_in_nak = lon - nak_idx * _NAKSHATRA_SPAN
    pada = int(pos_in_nak / _PADA_SPAN)
    if pada > 3:
        pada = 3
    start_of_pada = nak_idx * _NAKSHATRA_SPAN + pada * _PADA_SPAN
    pos_in_pada = lon - start_of_pada
    remaining = 1.0 - (pos_in_pada / _PADA_SPAN)
    return max(0.0, min(1.0, remaining))


def _is_savya(group: int) -> bool:
    return group in (1, 2, 3)


def _detect_gati(seq: List[str], i: int) -> Optional[str]:
    """
    Detect Gati (leap) between position i and i+1 in the sequence.
    Manduki Gati: 2-sign jump (e.g., Virgo → Cancer = skip 1 sign)
    Simhavalokana Gati: trinal (4-sign) jump
    """
    if i + 1 >= len(seq):
        return None
    from_idx = SIGN_NAMES.index(seq[i])
    to_idx = SIGN_NAMES.index(seq[i + 1])
    diff = abs(to_idx - from_idx)
    if diff > 6:
        diff = 12 - diff
    if diff == 2 or diff == 10:
        return "Manduki (Frog's Leap) — sudden status shift"
    if diff == 4 or diff == 8:
        return "Simhavalokana (Lion's Leap) — drastic life transformation"
    return None


def compute_kalachakra_dasha(
        moon_longitude: float,
        birth_year: int = 1990,
        max_periods: int = 9,
) -> Dict[str, Any]:
    """
    Compute Kalachakra Dasha sequence.

    Returns dict with:
      group, pada, is_savya, paramayus, deha_sign, jeeva_sign,
      sequence: list of {sign, years, cumulative_years, antardasha_periods, gati}
    """
    nak_idx, pada = _get_nak_pada(moon_longitude)
    group = _NAK_GROUP.get(nak_idx, 1)
    key = (group, pada)
    data = _SEQUENCE_TABLE.get(key)

    if data is None:
        # Fallback to group 1, pada 0
        key = (1, 0)
        data = _SEQUENCE_TABLE[key]

    seq, paramayus, deha_sign, jeeva_sign = data
    savya = _is_savya(group)

    # Balance of first period
    frac_remaining = _remaining_pada_fraction(moon_longitude)
    first_period_full = SIGN_YEARS.get(seq[0], 7)
    balance_years = first_period_full * frac_remaining

    periods: List[Dict] = []
    cumulative = 0.0

    for i, sign in enumerate(seq[:max_periods]):
        full_years = SIGN_YEARS.get(sign, 7)
        if i == 0:
            effective_years = balance_years
        else:
            effective_years = float(full_years)

        # Antardasha: sub-periods within this Maha
        antardashas: List[Dict] = []
        for sub_sign in seq:
            sub_years = SIGN_YEARS.get(sub_sign, 7)
            antar_years = (full_years * sub_years) / paramayus
            antardashas.append({
                "sign": sub_sign,
                "years": round(antar_years, 3),
                "is_deha": sub_sign == deha_sign,
                "is_jeeva": sub_sign == jeeva_sign,
            })

        # Gati
        gati = _detect_gati(seq, i)

        # Prediction tags
        tags = []
        if sign == deha_sign:
            tags.append("DEHA — physical transformation/health crisis")
        if sign == jeeva_sign:
            tags.append("JEEVA — psychological/spiritual shift")

        periods.append({
            "maha_sign": sign,
            "years": round(effective_years, 3),
            "full_years": full_years,
            "start_birth_offset_years": round(cumulative, 3),
            "end_birth_offset_years": round(cumulative + effective_years, 3),
            "is_deha": sign == deha_sign,
            "is_jeeva": sign == jeeva_sign,
            "gati": gati,
            "prediction_tags": tags,
            "antardashas": antardashas[:5],  # top 5 for display
        })

        cumulative += effective_years

    return {
        "system": "Kalachakra Dasha",
        "nakshatra_index": nak_idx,
        "pada": pada + 1,  # display as 1-4
        "group": group,
        "is_savya": savya,
        "direction": "Clockwise (Savya)" if savya else "Counter-Clockwise (Apasavya)",
        "paramayus": paramayus,
        "deha_sign": deha_sign,
        "jeeva_sign": jeeva_sign,
        "total_cycle_years": sum(SIGN_YEARS[s] for s in seq),
        "sequence": seq,
        "periods": periods,
    }


def get_active_kalachakra_period(
        kalachakra: Dict[str, Any],
        age_years: float,
) -> Optional[Dict]:
    """Return the active Kalachakra Maha period for a given age."""
    for p in kalachakra["periods"]:
        if p["start_birth_offset_years"] <= age_years < p["end_birth_offset_years"]:
            return p
    return None


def analyze_deha_jeeva_transits(
        deha_sign: str,
        jeeva_sign: str,
        saturn_sign: str,
        rahu_sign: str,
) -> Dict[str, Any]:
    """
    Check if transiting Saturn or Rahu afflict Deha/Jeeva signs.
    Simultaneous affliction of both = high mortality indicator.
    """
    deha_afflicted = deha_sign in (saturn_sign, rahu_sign)
    jeeva_afflicted = jeeva_sign in (saturn_sign, rahu_sign)

    verdict = "SAFE"
    note = "No simultaneous Deha-Jeeva affliction."

    if deha_afflicted and jeeva_afflicted:
        verdict = "CRITICAL — terminal indicator (both Deha & Jeeva afflicted)"
        note = (f"Transit Saturn/Rahu on both Deha ({deha_sign}) and "
                f"Jeeva ({jeeva_sign}) simultaneously. High mortality risk.")
    elif deha_afflicted:
        verdict = "PHYSICAL ALERT"
        note = f"Transit malefic on Deha sign ({deha_sign}) — bodily threat."
    elif jeeva_afflicted:
        verdict = "MENTAL/SPIRITUAL ALERT"
        note = f"Transit malefic on Jeeva sign ({jeeva_sign}) — psychological crisis."

    return {
        "deha_sign": deha_sign,
        "jeeva_sign": jeeva_sign,
        "deha_afflicted": deha_afflicted,
        "jeeva_afflicted": jeeva_afflicted,
        "verdict": verdict,
        "note": note,
    }
