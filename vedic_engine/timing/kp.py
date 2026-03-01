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


# ── PRASHNA (BRANCH A) ────────────────────────────────────────────────────────

# House arrays for YES/NO query resolution (KP method)
PRASHNA_HOUSE_ARRAYS: Dict[str, Dict[str, list]] = {
    "marriage":       {"yes": [2, 7, 11],       "no": [1, 6, 10, 12]},
    "job":            {"yes": [2, 6, 10, 11],   "no": [1, 5, 9, 12]},
    "promotion":      {"yes": [2, 6, 10, 11],   "no": [1, 5, 9, 12]},
    "health_recovery":{"yes": [1, 5, 11],       "no": [6, 8, 12]},
    "financial_gain": {"yes": [2, 6, 11],       "no": [5, 8, 12]},
    "foreign_travel": {"yes": [3, 9, 12],       "no": [2, 4, 11]},
    "legal_victory":  {"yes": [6, 11],          "no": [7, 12]},
}

# Primary cusp for each query type
PRASHNA_PRIMARY_CUSP: Dict[str, int] = {
    "marriage": 7, "job": 10, "promotion": 10,
    "health_recovery": 6, "financial_gain": 2,
    "foreign_travel": 9, "legal_victory": 6,
}


def resolve_prashna_query(
        query_type: str,
        cusp_kp: Dict[int, Dict],        # from build_cusp_significations
        kp_sigs: Dict[str, Dict],        # from build_kp_significations
        ruling_planets: Dict,            # from compute_ruling_planets
        moon_nak_lord: str = "",
        lagna_cusp_sublord: str = "",
) -> Dict:
    """
    KP Prashna YES/NO resolution.

    Algorithm:
      1. Get primary cusp for the query type.
      2. Find sub-lord of that cusp.
      3. Check if star-lord of sub-lord signifies the YES array.
      4. Confirm via Ruling Planets intersection.
      5. Return verdict + timing hint.
    """
    qt = query_type.lower().replace(" ", "_")
    arrays = PRASHNA_HOUSE_ARRAYS.get(qt)
    cusp_num = PRASHNA_PRIMARY_CUSP.get(qt)

    if arrays is None or cusp_num is None:
        return {"verdict": "UNKNOWN", "reason": f"Query type '{query_type}' not in ruleset."}

    yes_houses = set(arrays["yes"])
    no_houses = set(arrays["no"])

    # Sub-lord of primary cusp
    cusp_data = cusp_kp.get(cusp_num, {})
    sub_lord = cusp_data.get("sub_lord", "")
    sub_lord_signifies = set(cusp_data.get("sub_lord_signifies", []))

    # Star-lord (nak_lord) of sub-lord
    sub_lord_nak = kp_sigs.get(sub_lord, {}).get("nak_lord", "")
    sub_lord_nak_sigs = set(kp_sigs.get(sub_lord_nak, {}).get("signified_houses", []))
    sub_lord_nak_sigs.update(sub_lord_signifies)  # combine sub-lord + its nak-lord

    yes_match = bool(sub_lord_nak_sigs & yes_houses)
    no_match = bool(sub_lord_nak_sigs & no_houses)

    # Ruling Planet confirmation
    rp_set = set(ruling_planets.get("ruling_planets", []))
    rp_confirmed = sub_lord in rp_set or sub_lord_nak in rp_set

    # Determine verdict
    if yes_match and not no_match:
        verdict = "YES — EVENT PROMISED"
    elif no_match and not yes_match:
        verdict = "NO — EVENT DENIED"
    elif yes_match and no_match:
        verdict = "CONDITIONAL — Mixed signals; timing may delay or modify"
    else:
        verdict = "UNCLEAR — Insufficient house signification"

    if rp_confirmed:
        verdict += " (RP Confirmed)"

    return {
        "query_type": query_type,
        "primary_cusp": cusp_num,
        "cusp_sub_lord": sub_lord,
        "cusp_sub_lord_nak": sub_lord_nak,
        "sub_lord_signifies": sorted(sub_lord_nak_sigs),
        "yes_houses": sorted(yes_houses),
        "no_houses": sorted(no_houses),
        "yes_match": yes_match,
        "no_match": no_match,
        "rp_confirmed": rp_confirmed,
        "verdict": verdict,
    }


def compute_prashna_panchaka(
        tithi: int,       # 1-30 lunar day
        nakshatra: int,   # 1-27
        weekday: int,     # 1=Sun, 2=Mon, ... 7=Sat
        asc_sign: int,    # 1-12
) -> Dict:
    """
    Prashna Panchaka: (Tithi + Nakshatra + Weekday + Asc_Sign) mod 9.
    Remainder in {1,2,4,6,8} = flawed/obstacle timing.

    Meanings:
      1 = Mrityu (Death/Danger)
      2 = Agni (Fire/Destruction)
      4 = Raja (Authority Clash)
      6 = Chora (Theft)
      8 = Roga (Disease)
      3,5,7,0 = Neutral/Auspicious
    """
    PANCHAKA_MEANINGS = {
        0: ("Neutral", "No special obstacle."),
        1: ("Mrityu", "Danger — unfavorable for new ventures."),
        2: ("Agni", "Fire/Destruction — risk of loss or conflict."),
        3: ("Neutral/Rajya", "Authority — generally auspicious."),
        4: ("Raja", "Authority clash — friction with superiors."),
        5: ("Neutral/Mitra", "Friendship — positive outcome."),
        6: ("Chora", "Theft / betrayal risk."),
        7: ("Neutral/Sukha", "Comfort — moderate support."),
        8: ("Roga", "Disease — health-related timing flaw."),
    }
    total = tithi + nakshatra + weekday + asc_sign
    remainder = total % 9
    name, meaning = PANCHAKA_MEANINGS[remainder]
    flawed = remainder in (1, 2, 4, 6, 8)

    return {
        "tithi": tithi,
        "nakshatra": nakshatra,
        "weekday": weekday,
        "asc_sign": asc_sign,
        "total": total,
        "remainder": remainder,
        "panchaka": name,
        "meaning": meaning,
        "timing_flawed": flawed,
        "verdict": ("TIMING FLAWED — severe operational obstacles" if flawed
                    else "TIMING AUSPICIOUS — proceed with query"),
    }


def analyze_ithasala_yoga(
        faster_planet_lon: float,
        slower_planet_lon: float,
        faster_daily_motion: float,
        slower_daily_motion: float,
        orb_degrees: float = 5.0,
) -> Dict:
    """
    Ithasala Yoga: faster planet applying to aspect slower planet.

    Ithasala (Positive): faster planet approaching slower within orb.
    Easarapha (Negative): faster planet past the slower (separating).

    The Moon's applying aspect = primary indicator for imminent events.
    """
    diff = (slower_planet_lon - faster_planet_lon) % 360.0
    if diff > 180:
        diff = 360.0 - diff

    applying = faster_daily_motion > slower_daily_motion

    if diff <= orb_degrees:
        if applying:
            yoga = "Ithasala (Applying Aspect) — POSITIVE"
            verdict = "Future event indicated; faster planet approaching slower."
        else:
            yoga = "Easarapha (Separating Aspect) — NEGATIVE"
            verdict = "Historical context; event already past or denied for future."
    else:
        yoga = "Out of Orb"
        verdict = f"No active Ithasala/Easarapha within {orb_degrees}° orb."

    return {
        "faster_planet_lon": round(faster_planet_lon, 3),
        "slower_planet_lon": round(slower_planet_lon, 3),
        "angular_separation": round(diff, 3),
        "orb": orb_degrees,
        "applying": applying,
        "yoga": yoga,
        "verdict": verdict,
    }


def analyze_missing_person_prashna(planet_houses: Dict[str, int]) -> Dict:
    """
    Classical Prashna rules for missing person / traveller return.

    Positive indicators (safe/quick return):
      - Benefics in 2nd, 3rd, or 5th from Prashna Lagna
      - Moon un-afflicted in 7th

    Negative indicators (confinement/restriction):
      - Malefics in 7th or 8th

    Death indicator:
      - Prishthodaya Lagna heavily aspected by malefics
      - Afflicted Mercury in 6th
    """
    MALEFICS = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}
    BENEFICS = {"MOON", "MERCURY", "JUPITER", "VENUS"}

    benefics_in_235 = [p for p, h in planet_houses.items() if h in (2, 3, 5) and p in BENEFICS]
    moon_in_7 = planet_houses.get("MOON", 0) == 7
    malefics_in_78 = [p for p, h in planet_houses.items() if h in (7, 8) and p in MALEFICS]
    mercury_in_6_afflicted = planet_houses.get("MERCURY", 0) == 6 and bool(
        [p for p, h in planet_houses.items() if h == 6 and p in MALEFICS]
    )

    if benefics_in_235 or moon_in_7:
        status = "SAFE RETURN — imminent safe return of missing person"
        indicators = benefics_in_235 + (["MOON in 7th"] if moon_in_7 else [])
    elif mercury_in_6_afflicted:
        status = "POSSIBLE DEATH — afflicted Mercury in 6th + malefic conjunction"
        indicators = ["Mercury afflicted in 6th"]
    elif malefics_in_78:
        status = "CONFINEMENT OR RESTRICTION — person in constraint"
        indicators = malefics_in_78
    else:
        status = "UNCERTAIN — no strong indicator; await transit confirmation"
        indicators = []

    return {
        "benefics_in_235": benefics_in_235,
        "moon_in_7th": moon_in_7,
        "malefics_in_7_or_8": malefics_in_78,
        "mercury_6th_afflicted": mercury_in_6_afflicted,
        "status": status,
        "indicators": indicators,
    }
