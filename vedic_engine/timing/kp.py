"""
KP (Krishnamurti Paddhati) Engine.
Computes sublords, sub-sub lords, house significations, and ruling planets.

Core KP algorithm (from deep-research-report.md):
  Each nakshatra (13°20') is divided into 9 sub-divisions proportional
  to Vimshottari dasha years [7,20,6,10,7,18,16,19,17] / 120.
  Starting sub within each nakshatra = nakshatra lord's position in sequence.

KP Signification chain:
  Planet → occupies house H
         → is lord of house L
         → star lord occupies house HS
         → star lord lords house LS
         → sub lord occupies house SS
         → sub lord lords house SLS
  Final signification = union of H, L, HS, LS, SS, SLS
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

from vedic_engine.config import (
    Planet, Sign, VIMSHOTTARI_SEQUENCE, VIMSHOTTARI_YEARS,
    VIMSHOTTARI_TOTAL, NAKSHATRA_SPAN, SIGN_LORDS,
    WEEKDAY_LORDS,
)
from vedic_engine.core.coordinates import (
    normalize, nakshatra_of, sign_of
)

PLANET_NAMES = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU"]
SIGN_NAMES = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
              "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

_P_IDX = {p.name: i for i, p in enumerate(VIMSHOTTARI_SEQUENCE)}


def _sub_span(planet: Planet) -> float:
    """Width of this planet's sub-division within a nakshatra in degrees."""
    return (VIMSHOTTARI_YEARS[planet] / VIMSHOTTARI_TOTAL) * NAKSHATRA_SPAN


def get_kp_layers(longitude: float) -> Dict[str, str]:
    """
    Return the Rashi Lord, Nakshatra Lord, Sub Lord, and Sub-Sub Lord
    for any given absolute sidereal longitude.
    """
    lon = normalize(longitude)

    # Rashi lord
    rashi_sign = sign_of(lon)
    rashi_lord = SIGN_LORDS[Sign(rashi_sign)].name

    # Nakshatra
    nak_idx = nakshatra_of(lon)
    nak_lord = VIMSHOTTARI_SEQUENCE[nak_idx % 9]
    pos_in_nak = lon % NAKSHATRA_SPAN

    # Sub lord: 9 unequal subs within nakshatra, starting from nak lord
    nak_lord_idx = _P_IDX[nak_lord.name]
    accumulated = 0.0
    sub_lord = nak_lord
    for i in range(9):
        p = VIMSHOTTARI_SEQUENCE[(nak_lord_idx + i) % 9]
        span = _sub_span(p)
        if pos_in_nak < accumulated + span:
            sub_lord = p
            # Sub-sub lord within this sub
            span_in_sub = pos_in_nak - accumulated
            sub_lord_idx = _P_IDX[sub_lord.name]
            ss_accumulated = 0.0
            ss_lord = sub_lord
            for j in range(9):
                ss_p = VIMSHOTTARI_SEQUENCE[(sub_lord_idx + j) % 9]
                ss_span = (VIMSHOTTARI_YEARS[ss_p] / VIMSHOTTARI_TOTAL) * span
                if span_in_sub < ss_accumulated + ss_span:
                    ss_lord = ss_p
                    break
                ss_accumulated += ss_span
            return {
                "rashi_lord": rashi_lord,
                "nak_lord": nak_lord.name,
                "sub_lord": sub_lord.name,
                "sub_sub_lord": ss_lord.name,
            }
        accumulated += span

    return {
        "rashi_lord": rashi_lord,
        "nak_lord": nak_lord.name,
        "sub_lord": nak_lord.name,
        "sub_sub_lord": nak_lord.name,
    }


def build_kp_significations(
        planet_houses: Dict[str, int],      # {planet: house_num}
        kp_layers: Dict[str, Dict[str, str]],  # {planet: {nak_lord, sub_lord...}}
        house_lords: Dict[int, str],         # {house_num: lord_planet_name}
        lagna_sign: int,
) -> Dict[str, Dict]:
    """
    Build KP signification table for all planets.

    For each planet P:
      Signified houses = {house P is in}
                       ∪ {houses P lords}
                       ∪ {house star-lord of P is in}
                       ∪ {houses star-lord of P lords}
                       ∪ {house sub-lord of P is in}
                       ∪ {houses sub-lord of P lords}
    """
    # Reverse map: planet → list of houses it lords
    planet_lord_of: Dict[str, List[int]] = {}
    for h, lord in house_lords.items():
        planet_lord_of.setdefault(lord, []).append(h)

    result = {}

    for pname in PLANET_NAMES:
        occupied_house = planet_houses.get(pname, 0)
        layers = kp_layers.get(pname, {})
        nak_lord = layers.get("nak_lord", "")
        sub_lord = layers.get("sub_lord", "")

        houses = set()
        if occupied_house:
            houses.add(occupied_house)
        houses.update(planet_lord_of.get(pname, []))

        if nak_lord:
            nak_house = planet_houses.get(nak_lord, 0)
            if nak_house:
                houses.add(nak_house)
            houses.update(planet_lord_of.get(nak_lord, []))

        if sub_lord:
            sub_house = planet_houses.get(sub_lord, 0)
            if sub_house:
                houses.add(sub_house)
            houses.update(planet_lord_of.get(sub_lord, []))

        result[pname] = {
            "planet": pname,
            "occupied_house": occupied_house,
            "nak_lord": nak_lord,
            "sub_lord": sub_lord,
            "signified_houses": sorted(houses),
            "is_positive_finance": bool(houses & {2, 6, 10, 11}),
            "is_positive_career": bool(houses & {2, 6, 10, 11}),
            "is_positive_marriage": bool(houses & {2, 7, 11}),
            "is_negative": bool(houses & {5, 8, 12}),
        }

    return result


def build_cusp_significations(
        cusp_kp_layers: Dict[int, Dict[str, str]],  # {house: {nak_lord, sub_lord}}
        planet_houses: Dict[str, int],
        house_lords: Dict[int, str],
) -> Dict[int, Dict]:
    """
    KP cusp signification: each house cusp's sub-lord decides the event.
    Sub-lord of the cusp must signify the cusp's house number for
    events related to that house to manifest.
    """
    planet_lord_of: Dict[str, List[int]] = {}
    for h, lord in house_lords.items():
        planet_lord_of.setdefault(lord, []).append(h)

    result = {}
    for house_num, layers in cusp_kp_layers.items():
        sub_lord = layers.get("sub_lord", "")
        sub_house = planet_houses.get(sub_lord, 0)
        sub_signifies = set()
        if sub_house:
            sub_signifies.add(sub_house)
        sub_signifies.update(planet_lord_of.get(sub_lord, []))

        # Also follow sub-lord's star lord
        nak_lord = layers.get("nak_lord", "")
        nak_house = planet_houses.get(nak_lord, 0)
        if nak_house:
            sub_signifies.add(nak_house)
        sub_signifies.update(planet_lord_of.get(nak_lord, []))

        result[house_num] = {
            "house": house_num,
            "sub_lord": sub_lord,
            "sub_lord_signifies": sorted(sub_signifies),
            "sublord_permits_house": house_num in sub_signifies,
        }
    return result


def compute_ruling_planets(
        current_dt: datetime,
        current_moon_longitude: float,
        lagna_longitude: float,
) -> Dict:
    """
    KP Ruling Planets for a given moment (for event timing).

    1. Lord of the day (weekday lord)
    2. Lord of Moon's current nakshatra
    3. Lord of Moon's current sign
    4. Lord of Ascendant's current sign
    5. Lord of nakshatra in which Ascendant transits

    These are the 5 ruling planets used for timing in KP.
    """
    weekday = current_dt.weekday()
    day_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}
    wd = day_map[weekday]
    day_lord = WEEKDAY_LORDS.get(wd, Planet.SUN)

    moon_nak_lord = VIMSHOTTARI_SEQUENCE[nakshatra_of(current_moon_longitude) % 9]
    moon_sign_lord = SIGN_LORDS[Sign(sign_of(current_moon_longitude))]
    lagna_sign_lord = SIGN_LORDS[Sign(sign_of(lagna_longitude))]
    lagna_nak_lord = VIMSHOTTARI_SEQUENCE[nakshatra_of(lagna_longitude) % 9]

    ruling = [
        day_lord, moon_nak_lord, moon_sign_lord, lagna_sign_lord, lagna_nak_lord
    ]

    return {
        "day_lord": day_lord.name,
        "moon_nak_lord": moon_nak_lord.name,
        "moon_sign_lord": moon_sign_lord.name,
        "lagna_sign_lord": lagna_sign_lord.name,
        "lagna_nak_lord": lagna_nak_lord.name,
        "ruling_planets": list({p.name for p in ruling}),
    }
