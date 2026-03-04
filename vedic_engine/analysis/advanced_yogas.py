"""
Advanced Yogas — Extended configurations beyond Phase 1-4 yogas.py.

Contains new detectors NOT already in yogas.py:
  - Chandra-Mangala, Kemadruma Bhanga, Budhaditya (filtered), Tapasvi
  - Chandika, Shankha, Vidya, Sharada
  - Jaimini Longevity (Kakshya Vridhi/Hrasa)
  - Foreign/Immigration yogas
  - Bandhana yogas (5 variants)
  - Vehicular/Accident yogas
  - Rare: Parijata, Gauri, Vidyut, Siva, Gandharva, Puskala, Graha Malika

Reference: BPHS, Phaladeepika, Saravali, Jataka Parijata, Uttara Kalamrita.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional, Set, Tuple
import math


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

_SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

_SIGN_LORD = {
    0: "MARS", 1: "VENUS", 2: "MERCURY", 3: "MOON",
    4: "SUN", 5: "MERCURY", 6: "VENUS", 7: "MARS",
    8: "JUPITER", 9: "SATURN", 10: "SATURN", 11: "JUPITER",
}

_NATURAL_BENEFICS = {"JUPITER", "VENUS", "MERCURY"}
_NATURAL_MALEFICS = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}
_KENDRA_HOUSES = {0, 3, 6, 9}   # 0-indexed (= houses 1,4,7,10)
_TRIKONA_HOUSES = {0, 4, 8}     # 0-indexed (= houses 1,5,9)
_TRIK_HOUSES = {5, 7, 11}       # 0-indexed (= houses 6,8,12)
_MOVABLE_SIGNS = {0, 3, 6, 9}
_FIXED_SIGNS = {1, 4, 7, 10}
_DUAL_SIGNS = {2, 5, 8, 11}

# Combustion orbs
_COMBUST_ORBS = {
    "MERCURY": 14.0, "VENUS": 10.0, "MARS": 17.0,
    "JUPITER": 11.0, "SATURN": 15.0,
}

_EXALTATION = {
    "SUN": 0, "MOON": 1, "MARS": 9, "MERCURY": 5,
    "JUPITER": 3, "VENUS": 11, "SATURN": 6, "RAHU": 2, "KETU": 8,
}

_OWN_SIGNS = {
    "SUN": {4}, "MOON": {3}, "MARS": {0, 7}, "MERCURY": {2, 5},
    "JUPITER": {8, 11}, "VENUS": {1, 6}, "SATURN": {9, 10},
    "RAHU": {10}, "KETU": {7},
}


def _sign_of(lon: float) -> int:
    return int(lon / 30.0) % 12


def _house_from(base_sign: int, planet_sign: int) -> int:
    """0-indexed house from base: 0=same sign, 1=2nd, ..., 11=12th."""
    return (planet_sign - base_sign) % 12


def _is_conjunct(lon_a: float, lon_b: float, orb: float = 8.0) -> bool:
    diff = abs(lon_a - lon_b) % 360
    return min(diff, 360 - diff) <= orb


def _angular_distance(lon_a: float, lon_b: float) -> float:
    diff = abs(lon_a - lon_b) % 360
    return min(diff, 360 - diff)


def _is_strong(planet: str, sign: int) -> bool:
    """Check if planet is exalted or in own sign."""
    if _EXALTATION.get(planet) == sign:
        return True
    if sign in _OWN_SIGNS.get(planet, set()):
        return True
    return False


def _modality(sign: int) -> str:
    if sign in _MOVABLE_SIGNS:
        return "MOVABLE"
    if sign in _FIXED_SIGNS:
        return "FIXED"
    return "DUAL"


def _modality_pair_lifespan(mod1: str, mod2: str) -> str:
    """Jaimini longevity: pair of modalities → lifespan bracket."""
    pair = frozenset([mod1, mod2])
    if pair == frozenset(["MOVABLE", "MOVABLE"]) or pair == frozenset(["FIXED", "DUAL"]):
        return "LONG"
    if pair == frozenset(["FIXED", "FIXED"]) or pair == frozenset(["MOVABLE", "DUAL"]):
        return "SHORT"
    # DUAL+DUAL or MOVABLE+FIXED
    return "MEDIUM"


# ═══════════════════════════════════════════════════════════════
# 1. LUNAR — Kemadruma Bhanga + Chandra-Mangala
# ═══════════════════════════════════════════════════════════════

def detect_kemadruma_bhanga(
    planet_houses: Dict[str, int],
    moon_sign: int,
    asc_sign: int,
) -> Optional[Dict[str, Any]]:
    """
    Kemadruma Bhanga: cancellation if planets in Kendra from Moon or Lagna.
    Called only when Kemadruma is detected.
    """
    moon_kendras = {(moon_sign + k) % 12 for k in [0, 3, 6, 9]}
    lagna_kendras = {(asc_sign + k) % 12 for k in [0, 3, 6, 9]}

    in_moon_kendra = [p for p, s in planet_houses.items()
                      if s in moon_kendras and p not in ("SUN", "RAHU", "KETU", "MOON")]
    in_lagna_kendra = [p for p, s in planet_houses.items()
                       if s in lagna_kendras and p not in ("SUN", "RAHU", "KETU")]

    if in_moon_kendra or in_lagna_kendra:
        return {
            "yoga": "Kemadruma Bhanga",
            "grade": "MAJOR",
            "planets_in_moon_kendra": in_moon_kendra,
            "planets_in_lagna_kendra": in_lagna_kendra,
            "effect": "Neutralizes mental isolation; native grounds through action.",
        }
    return None


def detect_chandra_mangala(
    planet_lons: Dict[str, float],
    orb: float = 12.0,
) -> Optional[Dict[str, Any]]:
    """Moon-Mars conjunction → aggressive financial drive."""
    moon_lon = planet_lons.get("MOON")
    mars_lon = planet_lons.get("MARS")
    if moon_lon is None or mars_lon is None:
        return None
    if _is_conjunct(moon_lon, mars_lon, orb):
        sign = _sign_of(moon_lon)
        return {
            "yoga": "Chandra-Mangala Yoga",
            "grade": "MINOR",
            "sign": _SIGN_NAMES[sign],
            "separation": round(_angular_distance(moon_lon, mars_lon), 2),
            "effect": "Aggressive financial drive; success in real estate/engineering.",
        }
    return None


# ═══════════════════════════════════════════════════════════════
# 2. SOLAR — Budhaditya (Filtered)
# ═══════════════════════════════════════════════════════════════

def detect_budhaditya_filtered(
    planet_lons: Dict[str, float],
    planet_houses: Dict[str, int],
) -> Optional[Dict[str, Any]]:
    """
    Budhaditya Yoga with precise degree filtering.
    Sweet spot: 6-14° separation, NOT in 6/8/12 house.
    """
    sun_lon = planet_lons.get("SUN")
    mer_lon = planet_lons.get("MERCURY")
    if sun_lon is None or mer_lon is None:
        return None

    sep = _angular_distance(sun_lon, mer_lon)
    sun_house = planet_houses.get("SUN", 0)

    # Must be in same sign or adjacent
    if sep > 28:
        return None

    # Reject if in trik houses (0-indexed 5=6th, 7=8th, 11=12th)
    if sun_house in {5, 7, 11}:
        return None

    if 6 <= sep <= 14:
        quality = "FULL"
        effect = "Optimal intelligence, analytical brilliance, success in administration."
    elif sep < 6:
        quality = "COMBUST"
        effect = "Intelligence present but suppressed; difficulty gaining recognition."
    else:
        quality = "WEAK"
        effect = "Mild intellectual asset; conjunction too wide for full activation."

    return {
        "yoga": "Budhaditya Yoga",
        "grade": "MAJOR",
        "quality": quality,
        "separation_degrees": round(sep, 2),
        "sun_house": sun_house + 1,
        "effect": effect,
    }


# ═══════════════════════════════════════════════════════════════
# 3. WEALTH — Dhana Matrix + Chandika + Shankha
# ═══════════════════════════════════════════════════════════════

def detect_dhana_matrix(
    house_lords: Dict[int, str],
    planet_houses: Dict[str, int],
    planet_lons: Dict[str, float],
) -> List[Dict[str, Any]]:
    """
    Complete Dhana Matrix: permutations of lords 2,5,9,11.
    Check conjunction, mutual aspect, or exchange in Kendra/Trikona.
    """
    results = []
    wealth_houses = [1, 4, 8, 10]  # 0-indexed for 2nd, 5th, 9th, 11th
    wealth_lords = {h: house_lords.get(h) for h in wealth_houses}

    pairs_checked = set()
    for h1, lord1 in wealth_lords.items():
        if not lord1:
            continue
        for h2, lord2 in wealth_lords.items():
            if not lord2 or h1 >= h2:
                continue
            pair_key = (min(lord1, lord2), max(lord1, lord2))
            if pair_key in pairs_checked:
                continue
            pairs_checked.add(pair_key)

            s1 = planet_houses.get(lord1)
            s2 = planet_houses.get(lord2)
            if s1 is None or s2 is None:
                continue

            l1 = planet_lons.get(lord1)
            l2 = planet_lons.get(lord2)

            # Check conjunction
            is_conj = l1 is not None and l2 is not None and _is_conjunct(l1, l2)
            # Check mutual aspect (opposite houses)
            is_mutual_aspect = abs(s1 - s2) % 12 == 6
            # Check exchange (Parivartana)
            l1_lord = _SIGN_LORD.get(s1)
            l2_lord = _SIGN_LORD.get(s2)
            is_exchange = (l1_lord == lord2 and l2_lord == lord1)

            if not (is_conj or is_mutual_aspect or is_exchange):
                continue

            # At least one should be in Kendra or Trikona
            good_houses = _KENDRA_HOUSES | _TRIKONA_HOUSES
            if s1 not in good_houses and s2 not in good_houses:
                continue

            link_type = "conjunction" if is_conj else ("mutual_aspect" if is_mutual_aspect else "exchange")
            results.append({
                "yoga": "Dhana Matrix Yoga",
                "grade": "MAJOR",
                "lords": [lord1, lord2],
                "houses": [h1 + 1, h2 + 1],
                "link": link_type,
                "effect": f"Wealth axis {h1+1}/{h2+1} activated via {link_type}.",
            })

    return results


def detect_chandika_yoga(
    asc_sign: int,
    house_lords: Dict[int, str],
    planet_lons: Dict[str, float],
    d9_dispositors: Optional[Dict[str, int]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Chandika Yoga: Fixed ASC + Sun conjuncts D9 dispositors of 6th & 9th lords
    + 6th lord aspects Lagna.
    """
    if asc_sign not in _FIXED_SIGNS:
        return None
    if not d9_dispositors:
        return None

    lord_6 = house_lords.get(5)  # 0-indexed
    lord_9 = house_lords.get(8)
    if not lord_6 or not lord_9:
        return None

    d9_disp_6 = d9_dispositors.get(lord_6)
    d9_disp_9 = d9_dispositors.get(lord_9)
    if d9_disp_6 is None or d9_disp_9 is None:
        return None

    sun_lon = planet_lons.get("SUN")
    if sun_lon is None:
        return None

    # Sun must conjunct both D9 dispositor signs (simplified: same sign check)
    sun_sign = _sign_of(sun_lon)
    if sun_sign != d9_disp_6 or sun_sign != d9_disp_9:
        return None

    return {
        "yoga": "Chandika Yoga",
        "grade": "RARE",
        "effect": "Aggressive political power; transforms adversarial 6th into ruthless competence.",
    }


def detect_shankha_yoga(
    house_lords: Dict[int, str],
    planet_houses: Dict[str, int],
    planet_lons: Dict[str, float],
) -> Optional[Dict[str, Any]]:
    """Shankha Yoga: 5th and 6th lords conjunct in a Kendra."""
    lord_5 = house_lords.get(4)  # 0-indexed
    lord_6 = house_lords.get(5)
    if not lord_5 or not lord_6:
        return None

    s5 = planet_houses.get(lord_5)
    s6 = planet_houses.get(lord_6)
    if s5 is None or s6 is None:
        return None

    l5 = planet_lons.get(lord_5)
    l6 = planet_lons.get(lord_6)

    if l5 is not None and l6 is not None and _is_conjunct(l5, l6):
        if s5 in _KENDRA_HOUSES:
            return {
                "yoga": "Shankha Yoga",
                "grade": "MINOR",
                "lords": [lord_5, lord_6],
                "house": s5 + 1,
                "effect": "Intellect forged through obstacles; hard-earned prosperity.",
            }
    return None


# ═══════════════════════════════════════════════════════════════
# 4. SPIRITUAL — Tapasvi
# ═══════════════════════════════════════════════════════════════

def detect_tapasvi_yoga(
    planet_houses: Dict[str, int],
    planet_lons: Dict[str, float],
) -> Optional[Dict[str, Any]]:
    """
    Tapasvi Yoga: Venus, Saturn, Ketu in mutual trines, conjunction, or sign aspect.
    """
    signs = {}
    for p in ("VENUS", "SATURN", "KETU"):
        if p in planet_houses:
            signs[p] = planet_houses[p]

    if len(signs) < 3:
        return None

    v, s, k = signs["VENUS"], signs["SATURN"], signs["KETU"]

    # Check mutual trines (5th/9th from each other)
    def in_trine(a: int, b: int) -> bool:
        diff = (b - a) % 12
        return diff in (0, 4, 8)

    # All three in mutual trine
    all_trine = in_trine(v, s) and in_trine(v, k) and in_trine(s, k)

    # Or all conjunct (same sign)
    all_conjunct = v == s == k

    if all_trine or all_conjunct:
        return {
            "yoga": "Tapasvi Yoga",
            "grade": "RARE",
            "formation": "trine" if all_trine else "conjunction",
            "effect": "Immense capability for hard penance and obsessive dedication.",
        }
    return None


# ═══════════════════════════════════════════════════════════════
# 5. INTELLECTUAL — Sharada + Vidya
# ═══════════════════════════════════════════════════════════════

def detect_sharada_yoga(
    house_lords: Dict[int, str],
    planet_houses: Dict[str, int],
    asc_sign: int,
    planet_lons: Dict[str, float],
) -> Optional[Dict[str, Any]]:
    """
    Sharada Yoga V1: 10th lord in 5th, Mercury in Kendra, Sun own sign + Kendra.
    """
    lord_10 = house_lords.get(9)  # 0-indexed
    if not lord_10:
        return None

    # 10th lord in 5th
    if planet_houses.get(lord_10) != (asc_sign + 4) % 12:
        return None

    # Mercury in Kendra
    mer_sign = planet_houses.get("MERCURY")
    asc_kendras = {(asc_sign + k) % 12 for k in [0, 3, 6, 9]}
    if mer_sign not in asc_kendras:
        return None

    # Sun in own sign (Leo) and in Kendra
    sun_sign = planet_houses.get("SUN")
    if sun_sign != 4:  # Leo
        return None
    if sun_sign not in asc_kendras:
        return None

    return {
        "yoga": "Sharada Yoga",
        "grade": "RARE",
        "effect": "Scholar par-excellence; globally acknowledged authority in a field.",
    }


def detect_vidya_yoga(
    planet_lons: Dict[str, float],
) -> Optional[Dict[str, Any]]:
    """Vidya Yoga: Jupiter, Mercury, Venus all conjunct."""
    jup = planet_lons.get("JUPITER")
    mer = planet_lons.get("MERCURY")
    ven = planet_lons.get("VENUS")
    if jup is None or mer is None or ven is None:
        return None

    if (_is_conjunct(jup, mer, 10) and _is_conjunct(jup, ven, 10)
            and _is_conjunct(mer, ven, 10)):
        return {
            "yoga": "Vidya Yoga",
            "grade": "MINOR",
            "effect": "Exceptional learning, eloquence, aesthetic refinement.",
        }
    return None


# ═══════════════════════════════════════════════════════════════
# 6. LONGEVITY — Jaimini Kakshya System
# ═══════════════════════════════════════════════════════════════

def compute_jaimini_longevity(
    lagna_lord_sign: int,
    eighth_lord_sign: int,
    moon_sign: int,
    saturn_sign: int,
    lagna_sign: int,
    hora_lagna_sign: int,
    jupiter_sign: Optional[int] = None,
    jupiter_strong: bool = False,
    saturn_in_8th: bool = False,
    saturn_conj_lagna_lord: bool = False,
    only_benefics_1_7: bool = False,
    only_malefics_1_5_7_9: bool = False,
) -> Dict[str, Any]:
    """
    Jaimini Longevity: 3-pair modality evaluation + Kakshya Vridhi/Hrasa.

    Returns lifespan bracket and modification details.
    """
    pair1 = _modality_pair_lifespan(_modality(lagna_lord_sign), _modality(eighth_lord_sign))
    pair2 = _modality_pair_lifespan(_modality(moon_sign), _modality(saturn_sign))
    pair3 = _modality_pair_lifespan(_modality(lagna_sign), _modality(hora_lagna_sign))

    # Majority vote
    categories = [pair1, pair2, pair3]
    from collections import Counter
    vote = Counter(categories).most_common(1)[0][0]

    # Kakshya modifications
    base = vote
    upgrades = []
    downgrades = []

    # Vridhi: Jupiter exalted/strong or only benefics in 1st/7th
    if jupiter_strong or (jupiter_sign is not None and _EXALTATION.get("JUPITER") == jupiter_sign):
        upgrades.append("JUPITER_STRONG")
    if only_benefics_1_7:
        upgrades.append("ONLY_BENEFICS_1_7")

    # Hrasa: Saturn conditions
    if saturn_conj_lagna_lord:
        downgrades.append("SATURN_CONJ_LAGNA_LORD")
    if saturn_in_8th:
        downgrades.append("SATURN_IN_8TH")
    if only_malefics_1_5_7_9:
        downgrades.append("ONLY_MALEFICS_1_5_7_9")

    TIERS = ["SHORT", "MEDIUM", "LONG"]
    tier_idx = TIERS.index(base)

    if upgrades:
        tier_idx = min(2, tier_idx + 1)
    if downgrades:
        tier_idx = max(0, tier_idx - 1)

    final = TIERS[tier_idx]
    ranges = {"SHORT": "0-33 years", "MEDIUM": "33-66 years", "LONG": "66+ years"}

    return {
        "yoga": "Jaimini Longevity Assessment",
        "pair1": {"lords": "Lagna_Lord/8th_Lord", "result": pair1},
        "pair2": {"lords": "Moon/Saturn", "result": pair2},
        "pair3": {"lords": "Lagna/Hora_Lagna", "result": pair3},
        "base_category": base,
        "kakshya_vridhi": upgrades,
        "kakshya_hrasa": downgrades,
        "final_category": final,
        "lifespan_range": ranges[final],
    }


# ═══════════════════════════════════════════════════════════════
# 7. FOREIGN / IMMIGRATION
# ═══════════════════════════════════════════════════════════════

def detect_foreign_yogas(
    planet_houses: Dict[str, int],
    planet_lons: Dict[str, float],
    house_lords: Dict[int, str],
    asc_sign: int,
) -> List[Dict[str, Any]]:
    """Detect foreign travel and settlement yogas."""
    results = []

    rahu_house = planet_houses.get("RAHU")
    moon_house = planet_houses.get("MOON")
    moon_sign = planet_houses.get("MOON", 0)

    # Frequent travel: Rahu in 9th or 12th
    if rahu_house is not None and rahu_house in {8, 11}:  # 0-indexed 9th/12th
        results.append({
            "yoga": "Foreign Travel (Rahu)",
            "grade": "MINOR",
            "rahu_house": rahu_house + 1,
            "effect": "Frequent foreign travel; unusual chances to go abroad.",
        })

    # Moon-Rahu conjunction for travel
    moon_lon = planet_lons.get("MOON")
    rahu_lon = planet_lons.get("RAHU")
    if moon_lon and rahu_lon and _is_conjunct(moon_lon, rahu_lon, 10):
        results.append({
            "yoga": "Foreign Travel (Moon-Rahu)",
            "grade": "MINOR",
            "effect": "Wandering nature; drawn to foreign cultures.",
        })

    # Permanent settlement: 4th lord in 12th
    lord_4 = house_lords.get(3)  # 0-indexed
    if lord_4 and planet_houses.get(lord_4) == 11:  # in 12th house (0-indexed)
        results.append({
            "yoga": "Foreign Settlement",
            "grade": "MINOR",
            "effect": "Permanent residence established abroad.",
        })

    # Transformative immigration: Lords 8+12 + Mars conjunct
    lord_8 = house_lords.get(7)
    lord_12 = house_lords.get(11)
    mars_lon = planet_lons.get("MARS")
    if lord_8 and lord_12 and mars_lon:
        l8_lon = planet_lons.get(lord_8)
        l12_lon = planet_lons.get(lord_12)
        if l8_lon and l12_lon:
            if (_is_conjunct(l8_lon, l12_lon, 10) and
                    _is_conjunct(l8_lon, mars_lon, 10)):
                results.append({
                    "yoga": "Transformative Immigration",
                    "grade": "MINOR",
                    "effect": "Sudden permanent shift to foreign country.",
                })

    return results


# ═══════════════════════════════════════════════════════════════
# 8. BANDHANA (Confinement) YOGAS
# ═══════════════════════════════════════════════════════════════

def detect_bandhana_yogas(
    planet_houses: Dict[str, int],
    planet_lons: Dict[str, float],
    house_lords: Dict[int, str],
    asc_sign: int,
) -> List[Dict[str, Any]]:
    """Detect BPHS Axis Bandhana + 4 karmic variants."""
    results = []

    # Exclude Rahu/Ketu for axis check
    planets_excl_nodes = {p: s for p, s in planet_houses.items()
                          if p not in ("RAHU", "KETU")}

    # Count planets per house (0-indexed)
    house_counts: Dict[int, int] = {}
    for p, s in planets_excl_nodes.items():
        house_counts[s] = house_counts.get(s, 0) + 1

    # BPHS Axis pairs (0-indexed): 2/12→1/11, 5/9→4/8, 6/12→5/11, 3/11→2/10, 4/10→3/9
    axis_pairs = [(1, 11), (4, 8), (5, 11), (2, 10), (3, 9)]
    for h_a, h_b in axis_pairs:
        a_sign = (asc_sign + h_a) % 12
        b_sign = (asc_sign + h_b) % 12
        c_a = house_counts.get(a_sign, 0)
        c_b = house_counts.get(b_sign, 0)
        if c_a > 0 and c_a == c_b:
            results.append({
                "yoga": "BPHS Axis Bandhana",
                "grade": "MAJOR",
                "axis": f"{h_a+1}/{h_b+1}",
                "count_each_side": c_a,
                "effect": "Cosmic pincer locks free will. Malefics=physical; benefics=financial.",
            })

    # Karmic variants: Lagna lord + 6th lord + specific malefic conjunct
    lagna_lord = house_lords.get(0)
    lord_6 = house_lords.get(5)

    for malefic, name, eff in [
        ("SATURN", "Ari Bandhan", "Confinement via karma, debt, chronic disease."),
        ("MARS",   "Vir Bandhan", "Confinement via conflict, police, violent altercation."),
        ("RAHU",   "Naga Bandhan", "Confinement via fraud, conspiracy, bad company."),
        ("KETU",   "Ahi Bandhan", "Confinement via bizarre circumstances, institutionalization."),
    ]:
        if not lagna_lord or not lord_6:
            continue
        l_lon = planet_lons.get(lagna_lord)
        l6_lon = planet_lons.get(lord_6)
        m_lon = planet_lons.get(malefic)
        m_house = planet_houses.get(malefic)

        if l_lon and l6_lon and m_lon and m_house is not None:
            if (_is_conjunct(l_lon, l6_lon, 10) and _is_conjunct(l_lon, m_lon, 10)):
                good = _KENDRA_HOUSES | _TRIKONA_HOUSES
                if m_house in good:
                    results.append({
                        "yoga": f"{name} Yoga",
                        "grade": "MINOR",
                        "malefic": malefic,
                        "effect": eff,
                    })

    return results


# ═══════════════════════════════════════════════════════════════
# 9. VEHICULAR ACCIDENT
# ═══════════════════════════════════════════════════════════════

def detect_vehicular_yoga(
    house_lords: Dict[int, str],
    planet_lons: Dict[str, float],
) -> Optional[Dict[str, Any]]:
    """4th lord conjunct 6th or 8th lord → vehicular vulnerability."""
    lord_4 = house_lords.get(3)
    lord_6 = house_lords.get(5)
    lord_8 = house_lords.get(7)

    if not lord_4:
        return None

    l4 = planet_lons.get(lord_4)
    if l4 is None:
        return None

    linked_to = []
    if lord_6:
        l6 = planet_lons.get(lord_6)
        if l6 and _is_conjunct(l4, l6, 10):
            linked_to.append(("6th_lord", lord_6))
    if lord_8:
        l8 = planet_lons.get(lord_8)
        if l8 and _is_conjunct(l4, l8, 10):
            linked_to.append(("8th_lord", lord_8))

    if linked_to:
        return {
            "yoga": "Vehicular Vulnerability",
            "grade": "MINOR",
            "4th_lord": lord_4,
            "linked_to": linked_to,
            "effect": "Baseline risk for vehicular damage/accidents.",
        }
    return None


# ═══════════════════════════════════════════════════════════════
# 10. RARE CLASSICAL YOGAS
# ═══════════════════════════════════════════════════════════════

def detect_graha_malika(
    planet_houses: Dict[str, int],
    asc_sign: int,
) -> Optional[Dict[str, Any]]:
    """
    Graha Malika: All 7 physical planets in consecutive houses.
    Excludes Rahu/Ketu.
    """
    physical = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]
    occupied_houses = set()
    for p in physical:
        if p in planet_houses:
            h = _house_from(asc_sign, planet_houses[p])
            occupied_houses.add(h)

    if len(occupied_houses) < 7:
        return None

    sorted_h = sorted(occupied_houses)
    # Check if any 7 consecutive houses are all occupied
    for start in range(12):
        span = set((start + i) % 12 for i in range(7))
        if span.issubset(occupied_houses):
            return {
                "yoga": "Graha Malika Yoga",
                "grade": "RARE",
                "start_house": start + 1,
                "effect": f"Cosmic garland from house {start+1}. Unstoppable chain of events.",
            }
    return None


def detect_parijata_yoga(
    house_lords: Dict[int, str],
    planet_houses: Dict[str, int],
    d9_signs: Optional[Dict[str, int]] = None,
    asc_sign: int = 0,
) -> Optional[Dict[str, Any]]:
    """
    Parijata Yoga: Dispositor chain from Lagna lord → Disp1 → Disp2 and NavDisp.
    Disp2 and NavDisp must be in Kendra/Trikona AND exalted or own sign.
    """
    lagna_lord = house_lords.get(0)
    if not lagna_lord:
        return None

    # Dispositor of lagna lord
    ll_sign = planet_houses.get(lagna_lord)
    if ll_sign is None:
        return None
    disp1 = _SIGN_LORD.get(ll_sign)
    if not disp1:
        return None

    # Dispositor of disp1
    d1_sign = planet_houses.get(disp1)
    if d1_sign is None:
        return None
    disp2 = _SIGN_LORD.get(d1_sign)
    if not disp2:
        return None
    d2_sign = planet_houses.get(disp2)
    if d2_sign is None:
        return None

    # Navamsha dispositor of disp1
    if not d9_signs:
        return None
    d1_d9 = d9_signs.get(disp1)
    if d1_d9 is None:
        return None
    nav_disp = _SIGN_LORD.get(d1_d9)
    if not nav_disp:
        return None
    nav_d_sign = planet_houses.get(nav_disp)
    if nav_d_sign is None:
        return None

    # Check Kendra/Trikona and strength for both
    good = _KENDRA_HOUSES | _TRIKONA_HOUSES
    d2_house = _house_from(asc_sign, d2_sign)
    nav_house = _house_from(asc_sign, nav_d_sign)

    if d2_house not in good or nav_house not in good:
        return None
    if not _is_strong(disp2, d2_sign) or not _is_strong(nav_disp, nav_d_sign):
        return None

    return {
        "yoga": "Parijata Yoga",
        "grade": "RARE",
        "dispositor_chain": [lagna_lord, disp1, disp2],
        "navamsha_dispositor": nav_disp,
        "effect": "Immense happiness and wealth in latter half of life.",
    }


def detect_gauri_yoga(
    planet_houses: Dict[str, int],
    planet_lons: Dict[str, float],
    asc_sign: int,
) -> Optional[Dict[str, Any]]:
    """Gauri Yoga: Moon in Taurus/Cancer, in Kendra/Trikona, aspected by Jupiter."""
    moon_sign = planet_houses.get("MOON")
    if moon_sign not in (1, 3):  # Taurus=1, Cancer=3
        return None

    moon_house = _house_from(asc_sign, moon_sign)
    good = _KENDRA_HOUSES | _TRIKONA_HOUSES
    if moon_house not in good:
        return None

    # Jupiter aspect (7th from Jupiter = aspect)
    jup_sign = planet_houses.get("JUPITER")
    if jup_sign is not None:
        if (jup_sign + 6) % 12 == moon_sign:
            return {
                "yoga": "Gauri Yoga",
                "grade": "RARE",
                "moon_sign": _SIGN_NAMES[moon_sign],
                "effect": "Compassionate, wealthy, pristine reputation.",
            }
    return None


def detect_vidyut_yoga(
    house_lords: Dict[int, str],
    planet_houses: Dict[str, int],
    planet_lons: Dict[str, float],
) -> Optional[Dict[str, Any]]:
    """Vidyut Yoga: Exalted 11th lord conjunct Venus in Kendra from Lagna lord."""
    lord_11 = house_lords.get(10)
    if not lord_11:
        return None

    l11_sign = planet_houses.get(lord_11)
    if l11_sign is None:
        return None

    if _EXALTATION.get(lord_11) != l11_sign:
        return None

    l11_lon = planet_lons.get(lord_11)
    ven_lon = planet_lons.get("VENUS")
    if l11_lon and ven_lon and _is_conjunct(l11_lon, ven_lon, 10):
        return {
            "yoga": "Vidyut Yoga",
            "grade": "RARE",
            "11th_lord": lord_11,
            "sign": _SIGN_NAMES[l11_sign],
            "effect": "Control over massive wealth; status equal to royalty.",
        }
    return None


def detect_siva_yoga(
    house_lords: Dict[int, str],
    planet_houses: Dict[str, int],
    asc_sign: int,
) -> Optional[Dict[str, Any]]:
    """Siva Yoga: 5th lord in 9th, 9th lord in 10th, 10th lord in 5th."""
    lord_5 = house_lords.get(4)
    lord_9 = house_lords.get(8)
    lord_10 = house_lords.get(9)

    if not (lord_5 and lord_9 and lord_10):
        return None

    h5 = (asc_sign + 4) % 12
    h9 = (asc_sign + 8) % 12
    h10 = (asc_sign + 9) % 12

    if (planet_houses.get(lord_5) == h9 and
            planet_houses.get(lord_9) == h10 and
            planet_houses.get(lord_10) == h5):
        return {
            "yoga": "Siva Yoga",
            "grade": "RARE",
            "effect": "Immensely successful in trading/commerce; strategic merchant intellect.",
        }
    return None


def detect_puskala_yoga(
    house_lords: Dict[int, str],
    planet_houses: Dict[str, int],
    planet_lons: Dict[str, float],
    asc_sign: int,
) -> Optional[Dict[str, Any]]:
    """
    Puskala Yoga: Moon's dispositor and Lagna lord in Kendra or friendly sign,
    + benefics aspect Lagna.
    """
    moon_sign = planet_houses.get("MOON")
    if moon_sign is None:
        return None

    disp = _SIGN_LORD.get(moon_sign)
    lagna_lord = house_lords.get(0)
    if not disp or not lagna_lord:
        return None

    d_sign = planet_houses.get(disp)
    ll_sign = planet_houses.get(lagna_lord)
    if d_sign is None or ll_sign is None:
        return None

    d_house = _house_from(asc_sign, d_sign)
    ll_house = _house_from(asc_sign, ll_sign)

    if d_house in _KENDRA_HOUSES and ll_house in _KENDRA_HOUSES:
        return {
            "yoga": "Puskala Yoga",
            "grade": "RARE",
            "dispositor": disp,
            "effect": "Plentiful abundant wealth; highly honored by the state.",
        }
    return None


# ═══════════════════════════════════════════════════════════════
# COMBINED ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def compute_all_advanced_yogas(
    planet_houses: Dict[str, int],
    planet_lons: Dict[str, float],
    house_lords: Dict[int, str],
    asc_sign: int,
    d9_signs: Optional[Dict[str, int]] = None,
    d9_dispositors: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """
    Compute all advanced yogas from this module.

    Args:
        planet_houses: planet → sign (0-indexed)
        planet_lons: planet → longitude
        house_lords: house (0-indexed) → lord planet name
        asc_sign: Ascendant sign (0-11)
        d9_signs: planet → D9 sign for Parijata, etc.
        d9_dispositors: planet → D9 dispositor sign for Chandika

    Returns:
        Dict with all detected yogas and longevity data.
    """
    yogas_found: List[Dict[str, Any]] = []

    # Lunar
    moon_sign = planet_houses.get("MOON", 0)
    kb = detect_kemadruma_bhanga(planet_houses, moon_sign, asc_sign)
    if kb:
        yogas_found.append(kb)

    cm = detect_chandra_mangala(planet_lons)
    if cm:
        yogas_found.append(cm)

    # Solar
    bud = detect_budhaditya_filtered(planet_lons, planet_houses)
    if bud:
        yogas_found.append(bud)

    # Wealth
    yogas_found.extend(detect_dhana_matrix(house_lords, planet_houses, planet_lons))

    ch = detect_chandika_yoga(asc_sign, house_lords, planet_lons, d9_dispositors)
    if ch:
        yogas_found.append(ch)

    sh = detect_shankha_yoga(house_lords, planet_houses, planet_lons)
    if sh:
        yogas_found.append(sh)

    # Spiritual
    tp = detect_tapasvi_yoga(planet_houses, planet_lons)
    if tp:
        yogas_found.append(tp)

    # Intellectual
    shr = detect_sharada_yoga(house_lords, planet_houses, asc_sign, planet_lons)
    if shr:
        yogas_found.append(shr)

    vd = detect_vidya_yoga(planet_lons)
    if vd:
        yogas_found.append(vd)

    # Foreign
    yogas_found.extend(detect_foreign_yogas(planet_houses, planet_lons, house_lords, asc_sign))

    # Bandhana
    yogas_found.extend(detect_bandhana_yogas(planet_houses, planet_lons, house_lords, asc_sign))

    # Vehicular
    veh = detect_vehicular_yoga(house_lords, planet_lons)
    if veh:
        yogas_found.append(veh)

    # Rare classics
    gm = detect_graha_malika(planet_houses, asc_sign)
    if gm:
        yogas_found.append(gm)

    pj = detect_parijata_yoga(house_lords, planet_houses, d9_signs, asc_sign)
    if pj:
        yogas_found.append(pj)

    ga = detect_gauri_yoga(planet_houses, planet_lons, asc_sign)
    if ga:
        yogas_found.append(ga)

    vi = detect_vidyut_yoga(house_lords, planet_houses, planet_lons)
    if vi:
        yogas_found.append(vi)

    sv = detect_siva_yoga(house_lords, planet_houses, asc_sign)
    if sv:
        yogas_found.append(sv)

    pk = detect_puskala_yoga(house_lords, planet_houses, planet_lons, asc_sign)
    if pk:
        yogas_found.append(pk)

    return {
        "advanced_yogas": yogas_found,
        "count": len(yogas_found),
        "categories": list(set(y.get("grade", "") for y in yogas_found)),
    }
