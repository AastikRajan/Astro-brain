"""
Bhavabala (House Strength) Engine.
Formula: Bhavabala = Bhavadhipati Bala + Bhava Dig Bala + Bhava Drishti Bala

- Bhavadhipati Bala = Shadbala (in Rupas) of the house lord
- Bhava Dig Bala    = fixed positional value from BHAVA_DIG_BALA table
- Bhava Drishti Bala = net aspect score on the house cusp longitude

Research Brief (Jyotish Logic Architecture):
  Bhavabala thresholds:
    > 8.0 Rupas  → HIGH:    house forcefully delivers, compensates weak Karaka
    6.5–7.5 Rupas → AVERAGE: needs Dasha+transit support
    < 6.0 Rupas  → WEAK:    structural failure; 40-60% dampening of all predictions

  Minimum Shadbala thresholds (Parashara) in Virupas:
    Mercury=420, Sun=390, Jupiter=390, Moon=360, Venus=330, Mars=300, Saturn=300

  Occupant modifier:
    Jupiter/Mercury in house → +1.0 Rupa
    Saturn/Mars/Sun in house → -1.0 Rupa

  Digbala by sign type:
    Human signs (Gemini/Virgo/Libra/Aquarius/1st half of Sagittarius): max in H1
    Aquatic signs (Cancer/Pisces/2nd half of Capricorn): max in H4
    Quadruped (Aries/Taurus/Leo/2nd half of Sagittarius/1st half of Capricorn): max in H10
    Insect/Keeta (Scorpio): max in H7
"""
from __future__ import annotations
from typing import Dict, List, Optional

from vedic_engine.config import BHAVA_DIG_BALA, SIGN_LORDS, Sign, ASPECT_STRENGTHS, NATURAL_BENEFICS
from vedic_engine.core.aspects import houses_aspected, _get_planet_enum, _is_benefic

# ─── Minimum Shadbala thresholds (Virupas) from BPHS ─────────────────────
# 1 Rupa = 60 Virupas
MIN_SHADBALA_VIRUPAS: Dict[str, int] = {
    "MERCURY": 420,   # 7.0 Rupas
    "SUN":     390,   # 6.5 Rupas
    "JUPITER": 390,   # 6.5 Rupas
    "MOON":    360,   # 6.0 Rupas
    "VENUS":   330,   # 5.5 Rupas
    "MARS":    300,   # 5.0 Rupas
    "SATURN":  300,   # 5.0 Rupas
}

# ─── Bhavabala strength tiers (Research Brief) ───────────────────────────
_BHAVABALA_HIGH    = 8.0   # > 8.0 Rupas: forceful delivery
_BHAVABALA_AVERAGE = 6.5   # 6.5–7.5 Rupas: standard
_BHAVABALA_WEAK    = 6.0   # < 6.0 Rupas: structural weakness

# ─── Occupant modifiers (±1 Rupa based on planet in house) ──────────────
_OCCUPANT_BONUS   = {"JUPITER", "MERCURY"}   # +1 Rupa
_OCCUPANT_PENALTY = {"SATURN", "MARS", "SUN"}  # -1 Rupa

# ─── Sign-type → peak Digbala house (approximate) ────────────────────────
# Human signs: Gemini(2), Virgo(5), Libra(6), Aquarius(10) → peak H1
# Aquatic: Cancer(3), Pisces(11), late Capricorn(9) → peak H4
# Quadruped: Aries(0), Taurus(1), Leo(4), 2nd half Sagittarius, 1st half Capricorn → peak H10
# Insect/Keeta: Scorpio(7) → peak H7
_SIGN_TYPE: Dict[int, str] = {
    0: "quadruped",   # Aries
    1: "quadruped",   # Taurus
    2: "human",       # Gemini
    3: "aquatic",     # Cancer
    4: "quadruped",   # Leo
    5: "human",       # Virgo
    6: "human",       # Libra
    7: "keeta",       # Scorpio
    8: "quadruped",   # Sagittarius (dual; simplified as quadruped)
    9: "quadruped",   # Capricorn (dual; simplified)
    10: "human",      # Aquarius
    11: "aquatic",    # Pisces
}
_SIGN_TYPE_PEAK_HOUSE: Dict[str, int] = {
    "human":     1,
    "aquatic":   4,
    "quadruped": 10,
    "keeta":     7,
}


def get_shadbala_ratio(planet: str, shadbala_virupas: float) -> float:
    """
    Compute actual/minimum ratio for a planet.
    ratio >= 1.0 → planet meets minimum; < 1.0 → weak delivery.
    """
    minimum = MIN_SHADBALA_VIRUPAS.get(planet.upper(), 300)
    return round(shadbala_virupas / minimum, 3) if minimum > 0 else 1.0


def classify_bhavabala(total_rupas: float) -> Dict:
    """
    Classify Bhavabala total (in Rupas) into tier with confidence modifier.

    Research Brief Architecture:
      HIGH   (> 8.0):  forcefully delivers, +0.20 boost; compensates weak Karaka
      AVERAGE (6.5-8.0): standard, modifier = 0
      WEAK   (< 6.0):  -0.30 penalty; structural failure regardless of planet strength
    """
    if total_rupas > _BHAVABALA_HIGH:
        return {
            "tier": "HIGH",
            "confidence_modifier": +0.20,
            "detail": (f"Bhavabala {total_rupas:.2f} Rupas → Exceptional. "
                       "House forcefully delivers its domain; compensates weak Karaka."),
        }
    elif total_rupas >= _BHAVABALA_AVERAGE:
        delta = (total_rupas - _BHAVABALA_AVERAGE) / (_BHAVABALA_HIGH - _BHAVABALA_AVERAGE)
        return {
            "tier": "AVERAGE",
            "confidence_modifier": round(delta * 0.10, 3),   # 0 to +0.10 linearly
            "detail": (f"Bhavabala {total_rupas:.2f} Rupas → Standard. "
                       "Needs Dasha+transit support to fully manifest domain."),
        }
    elif total_rupas >= _BHAVABALA_WEAK:
        return {
            "tier": "BELOW_AVERAGE",
            "confidence_modifier": -0.10,
            "detail": (f"Bhavabala {total_rupas:.2f} Rupas → Below threshold. "
                       "Results require strong Dasha lord to compensate."),
        }
    else:
        return {
            "tier": "WEAK",
            "confidence_modifier": -0.30,
            "detail": (f"Bhavabala {total_rupas:.2f} Rupas → Structurally weak. "
                       "Domain lacks sufficient delivery capacity. External circumstances "
                       "obstruct manifestation regardless of planetary strength."),
        }


def bhava_drishti_bala(
        house_num: int,
        planet_houses: Dict[str, int],
        moon_waxing: bool = True,
) -> float:
    """
    Net aspect strength received by a house from all planets.
    Benefic aspects add, malefic aspects subtract.
    Scaled to shashtiamsas (divide full aspect by 2 as per convention).
    """
    total = 0.0
    for pname, p_house in planet_houses.items():
        p_enum = _get_planet_enum(pname)
        if p_enum is None:
            continue
        aspect_map = houses_aspected(p_house, p_enum)
        strength = aspect_map.get(house_num, 0.0)
        if strength == 0:
            continue
        scaled = strength / 2.0
        if _is_benefic(p_enum, moon_waxing):
            total += scaled
        else:
            total -= scaled
    return total


def _occupant_modifier(house_num: int, planet_houses: Dict[str, int]) -> float:
    """
    Research Brief: Occupants modify bhavabala by ±1 Rupa.
    Jupiter/Mercury in house → +1 Rupa
    Saturn/Mars/Sun in house → -1 Rupa
    """
    modifier = 0.0
    for pname, p_house in planet_houses.items():
        if p_house == house_num:
            up = pname.upper()
            if up in _OCCUPANT_BONUS:
                modifier += 1.0
            elif up in _OCCUPANT_PENALTY:
                modifier -= 1.0
    return modifier


def compute_bhavabala(
        house_num: int,
        house_lord: str,
        shadbala_rupas: Dict[str, float],    # {planet_name: rupas}
        planet_houses: Dict[str, int],
        moon_waxing: bool = True,
        lagna_sign: int = 0,
) -> Dict:
    """
    Compute Bhavabala for one house.
    Includes occupant modifiers and tier classification per Research Brief.
    """
    lord_rupas = shadbala_rupas.get(house_lord, 0.0)
    dig_bala = BHAVA_DIG_BALA.get(house_num, 30.0)
    drishti = bhava_drishti_bala(house_num, planet_houses, moon_waxing)
    occupant_mod = _occupant_modifier(house_num, planet_houses)

    # Bhava sign type → Digbala classification
    bhava_sign = (lagna_sign + house_num - 1) % 12
    sign_type = _SIGN_TYPE.get(bhava_sign, "human")
    peak_house = _SIGN_TYPE_PEAK_HOUSE.get(sign_type, 1)

    total = lord_rupas + (dig_bala / 60.0) + drishti + occupant_mod   # Convert dig_bala to Rupas

    tier_data = classify_bhavabala(total)

    return {
        "house_num": house_num,
        "house_lord": house_lord,
        "bhavadhipati_bala": round(lord_rupas, 2),
        "bhava_dig_bala": round(dig_bala / 60.0, 2),
        "bhava_drishti_bala": round(drishti, 2),
        "occupant_modifier": round(occupant_mod, 2),
        "total": round(total, 2),
        "tier": tier_data["tier"],
        "confidence_modifier": tier_data["confidence_modifier"],
        "sign_type": sign_type,
        "digbala_peak_house": peak_house,
        "detail": tier_data["detail"],
    }


def compute_all_bhavabala(
        lagna_sign: int,
        shadbala_rupas: Dict[str, float],
        planet_houses: Dict[str, int],
        moon_waxing: bool = True,
) -> List[Dict]:
    """Compute Bhavabala for all 12 houses."""
    results = []
    for h in range(1, 13):
        lord_sign = (lagna_sign + h - 1) % 12
        lord = SIGN_LORDS[Sign(lord_sign)].name
        results.append(compute_bhavabala(
            house_num=h,
            house_lord=lord,
            shadbala_rupas=shadbala_rupas,
            planet_houses=planet_houses,
            moon_waxing=moon_waxing,
            lagna_sign=lagna_sign,
        ))
    return results


def get_bhavabala_modifier_for_domain(
        bhavabala_list: List[Dict],
        domain_houses: List[int],
) -> Dict:
    """
    Compute net Bhavabala confidence modifier for a set of domain houses.

    Research Brief: HIGH tier (+0.20), AVERAGE (0 to +0.10), WEAK (-0.30).
    Returns the average modifier and the weakest house (bottleneck).
    """
    if not bhavabala_list or not domain_houses:
        return {"modifier": 0.0, "bottleneck_house": None, "tier_summary": {}}

    by_house = {r["house_num"]: r for r in bhavabala_list}
    modifiers = []
    tiers = {}
    bottleneck = None
    bottleneck_score = 999.0

    for h in domain_houses:
        if h in by_house:
            data = by_house[h]
            modifiers.append(data["confidence_modifier"])
            tiers[h] = data["tier"]
            if data["total"] < bottleneck_score:
                bottleneck_score = data["total"]
                bottleneck = h

    avg_mod = round(sum(modifiers) / len(modifiers), 3) if modifiers else 0.0
    return {
        "modifier": avg_mod,
        "bottleneck_house": bottleneck,
        "bottleneck_total": round(bottleneck_score, 2) if bottleneck else None,
        "tier_summary": tiers,
    }
