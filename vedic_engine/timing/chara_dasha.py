"""
Jaimini Chara Dasha Engine.

Sign-based (rashi) Mahadasha system from Jaimini Sutras.

Rules:
  - Starts from Lagna sign.
  - Direction: forward (Savya) or backward (Apasavya) based on Lagna sign.
    Forward (Savya)    : Aries, Leo, Virgo, Libra, Aquarius, Pisces
    Backward (Apasavya): Taurus, Gemini, Cancer, Scorpio, Sagittarius, Capricorn
  - Each sign's Dasha length: k−1 years, where k = houses from sign to its lord.
    Exception: lord in same sign → 12 years.
    Adjustment: +1 if lord exalted, −1 if lord debilitated. Min=1, Max=12.
  - Dual-lord signs (Scorpio, Aquarius): if one lord is in sign, use the other.
    If both lords in sign → 12 years.
  - Antardasha: 12 sub-periods, each N months (N = Mahadasha years).
    Order: same direction as Mahadasha, with Mahadasha sign's sub-period LAST.

Sources: Jaimini Sutras, K.N. Rao commentary.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

try:
    from vedic_engine.analysis.rashi_drishti import planets_with_rashi_drishti
except ImportError:
    def planets_with_rashi_drishti(planet_positions, target_sign):  # type: ignore
        return []


SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# 0-based sign → primary lord
SIGN_LORD: Dict[int, str] = {
    0: "MARS",    # Aries
    1: "VENUS",   # Taurus
    2: "MERCURY", # Gemini
    3: "MOON",    # Cancer
    4: "SUN",     # Leo
    5: "MERCURY", # Virgo
    6: "VENUS",   # Libra
    7: "MARS",    # Scorpio  (co-lord: KETU)
    8: "JUPITER", # Sagittarius
    9: "SATURN",  # Capricorn
    10: "SATURN", # Aquarius  (co-lord: RAHU)
    11: "JUPITER",# Pisces
}

# Dual-lord signs and their co-lords
DUAL_LORD_SIGNS: Dict[int, Tuple[str, str]] = {
    7: ("MARS", "KETU"),   # Scorpio
    10: ("SATURN", "RAHU"),# Aquarius
}

# Exact exaltation degrees (planet: degree)
EXALTATION: Dict[str, float] = {
    "SUN": 10.0, "MOON": 33.0, "MARS": 298.0, "MERCURY": 165.0,
    "JUPITER": 95.0, "VENUS": 177.0, "SATURN": 200.0,
    "RAHU": 50.0, "KETU": 230.0,
}
DEBILITATION: Dict[str, float] = {
    "SUN": 190.0, "MOON": 213.0, "MARS": 118.0, "MERCURY": 345.0,
    "JUPITER": 275.0, "VENUS": 357.0, "SATURN": 20.0,
    "RAHU": 230.0, "KETU": 50.0,
}


def _sign_of(longitude: float) -> int:
    """0-based sign index from sidereal longitude."""
    return int(longitude % 360.0 / 30.0) % 12


def _is_exalted(planet: str, longitude: float) -> bool:
    exalt = EXALTATION.get(planet)
    if exalt is None:
        return False
    return _sign_of(longitude) == _sign_of(exalt)


def _is_debilitated(planet: str, longitude: float) -> bool:
    debil = DEBILITATION.get(planet)
    if debil is None:
        return False
    return _sign_of(longitude) == _sign_of(debil)


# ── Direction (Savya / Apasavya) ──────────────────────────────────────────────

# Savya (forward, anti-clockwise): Aries, Leo, Virgo, Libra, Aquarius, Pisces
_SAVYA = frozenset({0, 4, 5, 6, 10, 11})
# Apasavya (backward, clockwise): Taurus, Gemini, Cancer, Scorpio, Sagittarius, Capricorn
_APASAVYA = frozenset({1, 2, 3, 7, 8, 9})


def chara_dasha_direction(lagna_sign: int) -> str:
    """Return 'forward' (Savya) or 'backward' (Apasavya) for the Lagna sign."""
    return "forward" if (lagna_sign % 12) in _SAVYA else "backward"


def _generate_sign_order(start_sign: int, direction: str) -> List[int]:
    """12-sign sequence starting from start_sign in chosen direction."""
    step = 1 if direction == "forward" else -1
    return [(start_sign + i * step) % 12 for i in range(12)]


def _count_houses_to_lord(from_sign: int, to_sign: int, direction: str) -> int:
    """
    Count houses from `from_sign` to `to_sign` in the given direction.
    Returns 1 if same sign (lord in own sign), 2 for adjacent, etc.
    """
    if direction == "forward":
        diff = (to_sign - from_sign) % 12
    else:
        diff = (from_sign - to_sign) % 12
    return diff if diff != 0 else 12  # 0 diff = 12 full rounds (own sign → 12)


def _compute_dasha_years(
    sign: int,
    direction: str,
    planet_signs: Dict[str, int],
    planet_lons: Dict[str, float],
) -> int:
    """
    Compute Chara Dasha length for a sign.

    Returns integer years (1-12).
    """
    # Resolve lords
    if sign in DUAL_LORD_SIGNS:
        lord_a, lord_b = DUAL_LORD_SIGNS[sign]
        a_sign = planet_signs.get(lord_a, -1)
        b_sign = planet_signs.get(lord_b, -1)
        a_in_sign = (a_sign == sign)
        b_in_sign = (b_sign == sign)
        if a_in_sign and b_in_sign:
            return 12  # both lords in sign
        elif a_in_sign:
            # Ignore A (in sign), use B
            primary_lord = lord_b
        elif b_in_sign:
            # Ignore B (in sign), use A
            primary_lord = lord_a
        else:
            # Both outside — choose the one further from the sign (stronger)
            # Simplified: use the primary lord (first in tuple)
            primary_lord = lord_a
    else:
        primary_lord = SIGN_LORD.get(sign, "MARS")

    lord_sign = planet_signs.get(primary_lord, sign)

    # Own sign exception
    if lord_sign == sign:
        return 12

    # Houses from sign to lord in chosen direction
    k = _count_houses_to_lord(sign, lord_sign, direction)
    years = k - 1

    # Exaltation / Debilitation adjustment
    lord_lon = planet_lons.get(primary_lord)
    if lord_lon is not None:
        if _is_exalted(primary_lord, lord_lon):
            years += 1
        elif _is_debilitated(primary_lord, lord_lon):
            years -= 1

    # Clamp 1-12
    return max(1, min(12, years))


def _antardasha_order(main_sign: int, direction: str) -> List[int]:
    """
    Generate antardasha sign sequence: all 12 signs in direction starting
    AFTER main_sign, with main_sign appended LAST.
    """
    step = 1 if direction == "forward" else -1
    # Start from the sign AFTER main_sign
    order = [(main_sign + (i + 1) * step) % 12 for i in range(11)]
    order.append(main_sign)
    return order


def compute_chara_dasha(
    lagna_sign: int,
    planet_signs: Dict[str, int],
    planet_lons: Dict[str, float],
    birth_date: datetime,
    levels: int = 2,
) -> List[Dict]:
    """
    Compute Jaimini Chara Dasha periods.

    Args:
        lagna_sign: 0-based Ascendant sign index
        planet_signs: {planet_name: sign_idx} for all planets
        planet_lons: {planet_name: sidereal_longitude} for all planets
        birth_date: datetime of birth
        levels: 1=Mahadasha only, 2=include Antardashas

    Returns:
        List of dicts with keys:
          sign, sign_name, start, end, years,
          [sub_periods (if levels>=2)]
    """
    direction = chara_dasha_direction(lagna_sign)
    sign_order = _generate_sign_order(lagna_sign, direction)

    periods = []
    current = birth_date

    for sign in sign_order:
        years = _compute_dasha_years(sign, direction, planet_signs, planet_lons)
        # Approximate: 1 year = 365.25 days
        end = current + timedelta(days=years * 365.25)

        period: Dict = {
            "sign": sign,
            "sign_name": SIGN_NAMES[sign],
            "years": years,
            "start": current,
            "end": end,
        }

        if levels >= 2:
            # Antardashas: each lasts `years` months
            ad_signs = _antardasha_order(sign, direction)
            months_per_sub = years
            ad_current = current
            sub_periods = []
            for ad_sign in ad_signs:
                # months → days (approx 30.44 days/month)
                ad_days = months_per_sub * 30.4375
                ad_end = ad_current + timedelta(days=ad_days)
                sub_periods.append({
                    "sign": ad_sign,
                    "sign_name": SIGN_NAMES[ad_sign],
                    "months": months_per_sub,
                    "start": ad_current,
                    "end": ad_end,
                })
                ad_current = ad_end
            period["sub_periods"] = sub_periods

        periods.append(period)
        current = end

    return periods


def get_active_chara_dasha(periods: List[Dict], on_date: datetime) -> Dict:
    """
    Return the active Chara Dasha (and optionally Antardasha) for a given date.
    """
    for p in periods:
        if p["start"] <= on_date < p["end"]:
            result = {
                "mahadasha": p["sign_name"],
                "mahadasha_sign": p["sign"],
                "mahadasha_years": p["years"],
                "mahadasha_start": p["start"],
                "mahadasha_end": p["end"],
            }
            for sp in p.get("sub_periods", []):
                if sp["start"] <= on_date < sp["end"]:
                    result["antardasha"] = sp["sign_name"]
                    result["antardasha_sign"] = sp["sign"]
                    result["antardasha_months"] = sp["months"]
                    result["antardasha_start"] = sp["start"]
                    result["antardasha_end"] = sp["end"]
                    break
            return result
    return {}


def chara_dasha_details_on_date(
    lagna_sign: int,
    planet_signs: Dict[str, int],
    planet_lons: Dict[str, float],
    birth_date: datetime,
    on_date: datetime,
    levels: int = 2,
    # ── New enrichment parameters ─────────────────────────────
    karakas: Optional[Dict[str, str]] = None,   # {AK, AmK, BK, ...} → planet name
    ul_sign: Optional[int] = None,              # Upapada Lagna sign (0-based)
    dara_karaka: Optional[str] = None,          # Name of Dara Karaka planet
) -> Dict:
    """
    Convenience function: compute all Chara Dasha periods and return active one.

    Enhanced with Research Brief interpretive layers:
      - house_from_lagna: active sign's house position from natal lagna
        (= atmospheric reality / temporary ascendant of the period)
      - resident_planets: planets in the active Dasha sign
      - rashi_drishti_on_dasha: planets aspecting dasha sign via Jaimini Rashi Drishti
      - ak_position: "in_dasha_sign" | "trikona_from_dasha" | "other"
        AK in dasha sign or 1/5/9 from it → soul-level events, major life realignment
      - amk_career_boost: AmK in 10th or 11th from dasha sign → career/status spike
      - marriage_flag: dasha sign 7th from UL, or contains Dara Karaka planet
      - rashi_drishti_nature: summary of aspecting planets (benefic/malefic/mixed)
    """
    periods = compute_chara_dasha(lagna_sign, planet_signs, planet_lons, birth_date, levels)
    active  = get_active_chara_dasha(periods, on_date)

    # ── Enrichment ────────────────────────────────────────────────────────────
    enrichment: Dict = {}

    if active:
        dasha_sign = active.get("mahadasha_sign")
        if dasha_sign is not None:
            # 1. House from lagna (temporary ascendant of the period)
            house_from_lagna = (dasha_sign - lagna_sign) % 12 + 1
            enrichment["house_from_lagna"] = house_from_lagna
            enrichment["house_from_lagna_meaning"] = _house_meaning(house_from_lagna)

            # 2. Resident planets in dasha sign
            resident_planets = [p for p, s in planet_signs.items() if s == dasha_sign]
            enrichment["resident_planets"] = resident_planets
            enrichment["resident_planet_count"] = len(resident_planets)

            # 3. Rashi Drishti planets on dasha sign
            rd_planets = planets_with_rashi_drishti(planet_signs, dasha_sign)
            enrichment["rashi_drishti_on_dasha"] = rd_planets

            # Nature of Rashi Drishti influence
            _NAT_BEN = {"MOON", "MERCURY", "JUPITER", "VENUS"}
            _NAT_MAL = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}
            ben_count = sum(1 for p in rd_planets if p in _NAT_BEN)
            mal_count = sum(1 for p in rd_planets if p in _NAT_MAL)
            enrichment["rashi_drishti_nature"] = (
                "benefic" if ben_count > mal_count else
                "malefic" if mal_count > ben_count else
                ("mixed" if rd_planets else "neutral")
            )

            # 4. Atma Karaka (AK) position relative to dasha sign
            ak_position = "other"
            if karakas:
                ak_planet = karakas.get("AK") or karakas.get("atma_karaka")
                if ak_planet:
                    ak_sign = planet_signs.get(ak_planet)
                    if ak_sign is not None:
                        ak_from_dasha = (ak_sign - dasha_sign) % 12 + 1
                        if ak_sign == dasha_sign or ak_from_dasha == 1:
                            ak_position = "in_dasha_sign"
                        elif ak_from_dasha in (5, 9):
                            ak_position = "trikona_from_dasha"
                        elif ak_from_dasha in (1, 5, 9):
                            ak_position = "trikona_from_dasha"
            enrichment["ak_position"] = ak_position
            enrichment["ak_soul_event_flag"] = ak_position in ("in_dasha_sign", "trikona_from_dasha")

            # 5. AmatyaKaraka (AmK) position — career/status spike
            amk_career_boost = False
            if karakas:
                amk_planet = karakas.get("AmK") or karakas.get("amatya_karaka")
                if amk_planet:
                    amk_sign = planet_signs.get(amk_planet)
                    if amk_sign is not None:
                        amk_from_dasha = (amk_sign - dasha_sign) % 12 + 1
                        amk_career_boost = amk_from_dasha in (10, 11)
            enrichment["amk_career_boost"] = amk_career_boost

            # 6. Marriage flag
            marriage_flag    = False
            marriage_reasons = []

            # a) Dasha sign is 7th from UL
            if ul_sign is not None:
                dist_from_ul = (dasha_sign - ul_sign) % 12 + 1
                if dist_from_ul == 7:
                    marriage_flag = True
                    marriage_reasons.append("dasha_sign_7th_from_UL")

            # b) Dasha sign contains Dara Karaka planet
            if dara_karaka and planet_signs.get(dara_karaka) == dasha_sign:
                marriage_flag = True
                marriage_reasons.append(f"{dara_karaka}_Dara_Karaka_in_dasha_sign")

            enrichment["marriage_flag"]    = marriage_flag
            enrichment["marriage_reasons"] = marriage_reasons

            # 7. Antardasha sign enrichment (if present)
            ad_sign = active.get("antardasha_sign")
            if ad_sign is not None:
                ad_house_from_lagna = (ad_sign - lagna_sign) % 12 + 1
                enrichment["antardasha_house_from_lagna"] = ad_house_from_lagna

    return {
        "direction": chara_dasha_direction(lagna_sign),
        "active": active,
        "enrichment": enrichment,
        "all_periods": [
            {
                "sign_name": p["sign_name"],
                "years": p["years"],
                "start": p["start"].strftime("%Y-%m-%d"),
                "end": p["end"].strftime("%Y-%m-%d"),
            }
            for p in periods
        ],
    }


def _house_meaning(h: int) -> str:
    """Brief atmospheric meaning of each house as temporary ascendant."""
    meanings = {
        1:  "Identity, health, personality − very personal period",
        2:  "Wealth, speech, family − focus on accumulation and communication",
        3:  "Courage, siblings, short travels − efforts and self-initiative",
        4:  "Home, mother, inner peace − domestic/emotional focus",
        5:  "Creativity, children, intelligence − speculative/learning period",
        6:  "Obstacles, enemies, service − competitive/health struggles",
        7:  "Partnerships, marriage, business − relational focus",
        8:  "Transformation, hidden matters, longevity − crisis and renewal",
        9:  "Fortune, dharma, father, travel − expansive/philosophical period",
        10: "Career, authority, public life − achievement and recognition",
        11: "Gains, networks, aspirations − income and goal fulfilment",
        12: "Losses, liberation, foreign, expenses − withdrawal/spiritual",
    }
    return meanings.get(h, "unknown")
