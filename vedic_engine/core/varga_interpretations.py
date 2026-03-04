"""
Phase 4 — File 2: Varga Interpretation Engine.

Implements:
  1. D60 Shashtiamsha full 60-deity lookup (Parashari)
  2. D30 Trimsamsha planet-ruler mapping (odd/even signs)
  3. Sapta Varga (7-chart) and Dasha Varga (10-chart) Vimshopak schemes
  4. Kashinath Hora (D2) day/night sign classification
  5. D10 Dashamsha career vector mapping
  6. Varga domain interpretation heuristics

Sources: Divisional Chart Interpretation Rules.txt (new4/ File 2)

Architecture: Pure functions. No weights, no blending, no prediction logic.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════════════════
# 1. D60 SHASHTIAMSHA — FULL 60-DEITY LOOKUP (PARASHARA)
# ═══════════════════════════════════════════════════════════════════════════════

# (name, nature): nature = "saumya" (benefic) or "krura" (malefic)
# For ODD signs: count 1→60.  For EVEN signs: reverse 60→1.
# Each amsha = 0°30' arc.

_D60_DEITIES: List[Tuple[str, str]] = [
    # idx 1-10
    ("Ghora",          "krura"),
    ("Rakshasa",       "krura"),
    ("Deva",           "saumya"),
    ("Kubera",         "saumya"),
    ("Yaksha",         "saumya"),
    ("Kinnara",        "saumya"),
    ("Bhrashta",       "krura"),
    ("Kulaghna",       "krura"),
    ("Garala",         "krura"),
    ("Vahni",          "krura"),
    # idx 11-20
    ("Maya",           "krura"),
    ("Purishaka",      "krura"),
    ("Apampathi",      "saumya"),
    ("Marutwan",       "saumya"),
    ("Kaala",          "krura"),
    ("Sarpa",          "krura"),
    ("Amrita",         "saumya"),
    ("Indu",           "saumya"),
    ("Mridu",          "saumya"),
    ("Komala",         "saumya"),
    # idx 21-30
    ("Heramba",        "saumya"),
    ("Brahma",         "saumya"),
    ("Vishnu",         "saumya"),
    ("Maheshwara",     "saumya"),
    ("Deva",           "saumya"),
    ("Ardra",          "saumya"),
    ("Kalinasa",       "saumya"),
    ("Kshiteesa",      "saumya"),
    ("Kamalakar",      "saumya"),
    ("Gulika",         "krura"),
    # idx 31-40
    ("Mrityu",         "krura"),
    ("Kaala",          "krura"),
    ("Davagni",        "krura"),
    ("Ghora",          "krura"),
    ("Yama",           "krura"),
    ("Kantaka",        "krura"),
    ("Suddha",         "saumya"),
    ("Amrita",         "saumya"),
    ("Purnachandra",   "saumya"),
    ("Vishadagdha",    "krura"),
    # idx 41-50
    ("Kulanasa",       "krura"),
    ("Vamshakshaya",   "krura"),
    ("Utpata",         "krura"),
    ("Kaala",          "krura"),
    ("Saumya",         "saumya"),
    ("Komala",         "saumya"),
    ("Sheetala",       "saumya"),
    ("Karaladamshtra", "krura"),
    ("Candramukhi",    "saumya"),
    ("Praveena",       "saumya"),
    # idx 51-60
    ("Kaalpavaka",     "krura"),
    ("Dhannayudha",    "krura"),
    ("Nirmala",        "saumya"),
    ("Saumya",         "saumya"),
    ("Krura",          "krura"),
    ("Atisheetala",    "saumya"),
    ("Amrita",         "saumya"),
    ("Payodhi",        "saumya"),
    ("Brahmana",       "saumya"),
    ("Chandrarekha",   "saumya"),
]


def get_d60_deity(longitude: float) -> Dict[str, Any]:
    """
    Look up the D60 Shashtiamsha deity for a given longitude.

    For ODD signs (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius):
        Deities count forward 1→60.
    For EVEN signs (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces):
        Deities count backward 60→1.

    Returns:
        {
          "segment":    1-60,
          "deity_name": str,
          "nature":     "saumya" | "krura",
          "sign_index": 0-11,
          "degree_arc": str (e.g. "14°30'-15°00'"),
          "effect":     str,
        }
    """
    lon = longitude % 360
    sign_idx = int(lon / 30) % 12
    deg_in_sign = lon % 30.0

    # Segment 1-60: each = 0.5°
    seg = int(deg_in_sign / 0.5) + 1
    seg = min(seg, 60)

    # Odd sign = Aries(0), Gemini(2), Leo(4), Libra(6), Sag(8), Aquarius(10)
    is_odd = (sign_idx % 2 == 0)

    if is_odd:
        deity_idx = seg - 1  # 0-based index into _D60_DEITIES
    else:
        deity_idx = 60 - seg  # reverse: seg 1→#60, seg 60→#1

    deity_idx = max(0, min(59, deity_idx))
    deity_name, nature = _D60_DEITIES[deity_idx]

    # Degree arc string
    arc_start = (seg - 1) * 0.5
    arc_end   = seg * 0.5
    arc_str = f"{int(arc_start)}°{int((arc_start % 1) * 60):02d}'-{int(arc_end)}°{int((arc_end % 1) * 60):02d}'"

    if nature == "saumya":
        effect = (f"Benefic D60 ({deity_name}) — past-life spiritual merit amplifies D1 results. "
                  "Unexpected success even if D1 is weak.")
    else:
        effect = (f"Malefic D60 ({deity_name}) — past-life karmic debt undermines D1 promise. "
                  "Material success may collapse or bring pain.")

    return {
        "segment":    seg,
        "deity_name": deity_name,
        "nature":     nature,
        "sign_index": sign_idx,
        "degree_arc": arc_str,
        "effect":     effect,
    }


def analyze_d60_full(planet_lons: Dict[str, float]) -> Dict[str, Dict]:
    """D60 deity analysis for all planets."""
    return {p: get_d60_deity(lon) for p, lon in planet_lons.items()}


# ═══════════════════════════════════════════════════════════════════════════════
# 2. D30 TRIMSAMSHA — PLANET-RULER MAPPING
# ═══════════════════════════════════════════════════════════════════════════════

# Odd signs: Mars 0-5, Saturn 5-10, Jupiter 10-18, Mercury 18-25, Venus 25-30
# Even signs: Venus 0-5, Mercury 5-12, Jupiter 12-20, Saturn 20-25, Mars 25-30

_D30_ODD = [
    (0.0,  5.0,  "MARS",    "Agni (Fire)"),
    (5.0,  10.0, "SATURN",  "Vayu (Air)"),
    (10.0, 18.0, "JUPITER", "Akash (Ether)"),
    (18.0, 25.0, "MERCURY", "Prithvi (Earth)"),
    (25.0, 30.0, "VENUS",   "Jala (Water)"),
]

_D30_EVEN = [
    (0.0,  5.0,  "VENUS",   "Jala (Water)"),
    (5.0,  12.0, "MERCURY", "Prithvi (Earth)"),
    (12.0, 20.0, "JUPITER", "Akash (Ether)"),
    (20.0, 25.0, "SATURN",  "Vayu (Air)"),
    (25.0, 30.0, "MARS",    "Agni (Fire)"),
]

# Misfortune types by D30 ruler (8th house or affliction)
_D30_MISFORTUNE = {
    "MARS":    "Weapons, surgery errors, conflict, fire",
    "SATURN":  "Vehicle accidents, severe delays, debilitating chronic diseases",
    "JUPITER": "Religious conflicts, altitude issues, law/court",
    "MERCURY": "Trade disputes, IP theft, financial ruin",
    "VENUS":   "Scandal, excess indulgence, venereal disease",
}


def get_d30_ruler(longitude: float) -> Dict[str, Any]:
    """
    Get the Trimsamsha ruler and element for a given longitude.

    The D30 divides 30° of each sign into 5 unequal parts ruled by the
    five tara grahas (Mars, Saturn, Jupiter, Mercury, Venus).
    Sequence differs for odd vs even signs.
    """
    lon = longitude % 360
    sign_idx = int(lon / 30) % 12
    deg = lon % 30.0

    is_odd = (sign_idx % 2 == 0)
    table = _D30_ODD if is_odd else _D30_EVEN

    for start, end, ruler, element in table:
        if start <= deg < end or (deg == 30.0 and end == 30.0):
            return {
                "ruler":        ruler,
                "element":      element,
                "sign_index":   sign_idx,
                "degree":       round(deg, 3),
                "is_odd_sign":  is_odd,
                "misfortune":   _D30_MISFORTUNE.get(ruler, ""),
            }

    # Fallback (should not reach)
    return {"ruler": "UNKNOWN", "element": "", "sign_index": sign_idx,
            "degree": deg, "is_odd_sign": is_odd, "misfortune": ""}


def analyze_d30(planet_lons: Dict[str, float]) -> Dict[str, Dict]:
    """D30 Trimsamsha ruler analysis for all planets."""
    return {p: get_d30_ruler(lon) for p, lon in planet_lons.items()}


# ═══════════════════════════════════════════════════════════════════════════════
# 3. SAPTA VARGA (7-CHART) AND DASHA VARGA (10-CHART) VIMSHOPAK SCHEMES
# ═══════════════════════════════════════════════════════════════════════════════

# Weight tables from the research file (Parashara)
SAPTA_VARGA_WEIGHTS: Dict[int, float] = {
    1:  5.0,    # D1 Rashi
    2:  2.0,    # D2 Hora
    3:  3.0,    # D3 Drekkana
    7:  1.0,    # D7 Saptamsha
    9:  2.5,    # D9 Navamsha
    12: 4.5,    # D12 Dwadashamsha
    30: 2.0,    # D30 Trimsamsha
}
SAPTA_VARGA_MAX = 20.0

DASHA_VARGA_WEIGHTS: Dict[int, float] = {
    1:  3.0,    # D1 Rashi
    2:  1.5,    # D2 Hora
    3:  1.5,    # D3 Drekkana
    7:  1.5,    # D7 Saptamsha
    9:  1.5,    # D9 Navamsha
    10: 1.5,    # D10 Dashamsha
    12: 1.5,    # D12 Dwadashamsha
    16: 1.5,    # D16 Shodashamsha
    30: 1.5,    # D30 Trimsamsha
    60: 5.0,    # D60 Shashtiamsha
}
DASHA_VARGA_MAX = 20.0

# Dignity point values (same as existing Vimshopak but with the exact research values)
_DIGNITY_POINTS = {
    "own":          20,   # Own / Moolatrikona / Exaltation
    "moolatrikona": 20,
    "exalted":      20,
    "great_friend": 18,   # Adhi Mitra
    "friend":       15,   # Mitra
    "neutral":      10,   # Sama
    "enemy":         7,   # Shatru
    "great_enemy":   5,   # Adhi Shatru / Debilitation
    "debilitated":   5,
}


def compute_sapta_varga(planet: str, natal_longitude: float) -> Dict[str, Any]:
    """
    Compute Vimshopak Bala using Sapta Varga scheme (7 charts).
    Weights: D1=5, D2=2, D3=3, D7=1, D9=2.5, D12=4.5, D30=2 → total=20.
    """
    return _compute_scheme(planet, natal_longitude, SAPTA_VARGA_WEIGHTS,
                           SAPTA_VARGA_MAX, "sapta_varga")


def compute_dasha_varga(planet: str, natal_longitude: float) -> Dict[str, Any]:
    """
    Compute Vimshopak Bala using Dasha Varga scheme (10 charts).
    Weights: D1=3, D2=1.5, D3=1.5, D7=1.5, D9=1.5, D10=1.5, D12=1.5,
             D16=1.5, D30=1.5, D60=5 → total=20.
    The Dasha Varga is traditionally the most emphasized by Parashara.
    """
    return _compute_scheme(planet, natal_longitude, DASHA_VARGA_WEIGHTS,
                           DASHA_VARGA_MAX, "dasha_varga")


def _compute_scheme(
    planet: str, natal_longitude: float,
    weights: Dict[int, float], max_score: float, scheme_name: str,
) -> Dict[str, Any]:
    """
    Generic Vimshopak computation for any scheme.
    Uses divisional.py for varga computation and shadbala._get_dignity for dignity.
    """
    try:
        from vedic_engine.core.divisional import get_varga, VARGA_FUNCTIONS
        from vedic_engine.strength.shadbala import _get_dignity, _P
        from vedic_engine.config import Dignity
    except ImportError:
        return {"planet": planet, "score": 0.0, "scheme": scheme_name, "error": "import_failed"}

    p = _P.get(planet)
    if p is None:
        return {"planet": planet, "score": 0.0, "scheme": scheme_name}

    # Dignity → multiplier
    _DIG_MULT = {
        Dignity.EXALTED: 1.000, Dignity.MOOLATRIKONA: 1.000, Dignity.OWN: 1.000,
        Dignity.GREAT_FRIEND: 0.900, Dignity.FRIEND: 0.750,
        Dignity.NEUTRAL: 0.500, Dignity.ENEMY: 0.350,
        Dignity.GREAT_ENEMY: 0.250, Dignity.DEBILITATED: 0.000,
    }

    total = 0.0
    breakdown = {}
    for d, weight in weights.items():
        if d not in VARGA_FUNCTIONS:
            continue
        varga_sign = get_varga(natal_longitude, d)
        varga_lon = varga_sign * 30.0
        dignity = _get_dignity(planet, varga_lon)
        mult = _DIG_MULT.get(dignity, 0.5)
        contribution = weight * mult
        total += contribution
        breakdown[f"D{d}"] = {
            "sign": varga_sign, "dignity": dignity.value,
            "weight": weight, "contribution": round(contribution, 3),
        }

    pct = round(total / max_score * 100, 1) if max_score > 0 else 0.0
    tier = "HIGH" if total >= 15 else ("AVERAGE" if total >= 10 else "LOW")

    return {
        "planet": planet, "scheme": scheme_name,
        "score": round(total, 3), "max": max_score,
        "pct": pct, "tier": tier, "breakdown": breakdown,
    }


def compute_all_sapta_varga(planet_lons: Dict[str, float]) -> Dict[str, Dict]:
    """Compute Sapta Varga Vimshopak for all planets."""
    return {p: compute_sapta_varga(p, lon) for p, lon in planet_lons.items()}


def compute_all_dasha_varga(planet_lons: Dict[str, float]) -> Dict[str, Dict]:
    """Compute Dasha Varga Vimshopak for all planets."""
    return {p: compute_dasha_varga(p, lon) for p, lon in planet_lons.items()}


# ═══════════════════════════════════════════════════════════════════════════════
# 4. KASHINATH HORA (D2) — ADVANCED WEALTH CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

# Day-strong signs (Sun's Hora): Leo, Virgo, Libra, Scorpio, Aquarius, Pisces
# Night-strong signs (Moon's Hora): Aries, Taurus, Gemini, Cancer, Sag, Cap
_DAY_STRONG_SIGNS  = {4, 5, 6, 7, 10, 11}   # Leo, Virgo, Libra, Scorpio, Aq, Pi
_NIGHT_STRONG_SIGNS = {0, 1, 2, 3, 8, 9}     # Aries, Tau, Gem, Cancer, Sag, Cap

# Male planets (Sun, Mars, Jupiter) → strong in Sun's Hora (day signs)
# Female planets (Moon, Venus) + Saturn → strong in Moon's Hora (night signs)
# Mercury → strong in both
_HORA_AFFINITY = {
    "SUN":     "day",
    "MARS":    "day",
    "JUPITER": "day",
    "MOON":    "night",
    "VENUS":   "night",
    "SATURN":  "night",
    "MERCURY": "both",
    "RAHU":    "night",
    "KETU":    "day",
}

# D2 wealth-stream by dominant planet
_D2_WEALTH_STREAM = {
    "SUN":     "Self-employment, government, authority positions",
    "MOON":    "Public relations, hospitality, agriculture, collective resources",
    "MARS":    "Real estate, engineering, military, sports",
    "MERCURY": "Commerce, trading, IT, intellectual property, writing",
    "JUPITER": "Consulting, education, banking, financial expansion",
    "VENUS":   "Luxury, beauty, fashion, entertainment, arts",
    "SATURN":  "Heavy industry, labour management, slow systemic growth",
    "RAHU":    "Foreign trade, technology, unconventional markets",
    "KETU":    "Research, esoteric, backend work, isolation-based income",
}


def analyze_kashinath_hora(
    planet: str, d2_sign: int,
) -> Dict[str, Any]:
    """
    Evaluate a planet's strength in Kashinath D2 Hora system.

    Returns:
        {
          "planet": str,
          "d2_sign": int,
          "hora_type": "day" | "night",
          "planet_affinity": "day" | "night" | "both",
          "is_strong_hora": bool,
          "wealth_stream": str,
        }
    """
    hora_type = "day" if d2_sign in _DAY_STRONG_SIGNS else "night"
    affinity = _HORA_AFFINITY.get(planet.upper(), "both")
    is_strong = (affinity == "both" or affinity == hora_type)

    return {
        "planet":          planet,
        "d2_sign":         d2_sign,
        "hora_type":       hora_type,
        "planet_affinity": affinity,
        "is_strong_hora":  is_strong,
        "wealth_stream":   _D2_WEALTH_STREAM.get(planet.upper(), ""),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 5. D10 DASHAMSHA — CAREER VECTOR MAPPING
# ═══════════════════════════════════════════════════════════════════════════════

_D10_CAREER_VECTORS = {
    "SUN":     ["Administration", "IAS/Government", "Politics", "Executive leadership"],
    "MOON":    ["Public relations", "Caregiving", "HR", "Fluid/variable professions"],
    "MARS":    ["Engineering", "Military", "Sports", "Police", "Surgery"],
    "MERCURY": ["IT", "Journalism", "Marketing", "Trading", "Communications"],
    "JUPITER": ["Judiciary", "Academia", "Banking", "Law", "Consulting"],
    "VENUS":   ["Fashion", "Arts", "Luxury markets", "Diplomacy", "Entertainment"],
    "SATURN":  ["Heavy industry", "Labour management", "Slow systemic growth"],
    "RAHU":    ["Unconventional tech", "Foreign affairs", "Media", "AI"],
    "KETU":    ["Deep research", "Esoteric sciences", "Backend dev", "Isolation work"],
}


def get_d10_career_vector(
    d10_10th_house_planets: List[str],
    d10_10th_lord: str,
    d10_lagna_lord_house: int = 0,
) -> Dict[str, Any]:
    """
    Map D10 10th house/lord to career vectors.

    Args:
        d10_10th_house_planets: Planets in D10's 10th house
        d10_10th_lord:          Lord of D10's 10th house
        d10_lagna_lord_house:   House of D10 Lagna lord (for entrepreneur check)

    Returns career analysis dict.
    """
    career_vectors: List[str] = []
    dominant_planets: List[str] = []

    # Planets in 10th house are most direct career indicators
    for p in d10_10th_house_planets:
        pu = p.upper()
        if pu in _D10_CAREER_VECTORS:
            career_vectors.extend(_D10_CAREER_VECTORS[pu])
            dominant_planets.append(pu)

    # 10th lord contributes as well
    lord_u = d10_10th_lord.upper()
    if lord_u in _D10_CAREER_VECTORS:
        career_vectors.extend(_D10_CAREER_VECTORS[lord_u])
        if lord_u not in dominant_planets:
            dominant_planets.append(lord_u)

    # Malefics in 10th: success after struggle
    malefics_in_10th = [p for p in d10_10th_house_planets
                        if p.upper() in {"MARS", "SATURN", "RAHU", "KETU"}]
    struggle_flag = len(malefics_in_10th) > 0

    # Entrepreneur vs employee check: 1st/3rd/7th strong → entrepreneur
    entrepreneur_houses = {1, 3, 7}
    incline_entrepreneur = d10_lagna_lord_house in entrepreneur_houses

    return {
        "career_vectors":       list(set(career_vectors)),
        "dominant_planets":     dominant_planets,
        "struggle_then_success": struggle_flag,
        "incline_entrepreneur": incline_entrepreneur,
        "malefics_in_10th":     [p.upper() for p in malefics_in_10th],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 6. VARGOTTAMA DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

def is_vargottama(d1_longitude: float) -> Dict[str, Any]:
    """
    Check if a planet at given D1 longitude is Vargottama (same sign in D1 and D9).

    Vargottama degrees:
      Movable signs (0,3,6,9): 0°00'-3°20'  (navamsha 1)
      Fixed signs   (1,4,7,10): 13°20'-16°40' (navamsha 5)
      Dual signs    (2,5,8,11): 26°40'-30°00' (navamsha 9)
    """
    lon = d1_longitude % 360
    sign_idx = int(lon / 30) % 12
    deg = lon % 30

    modality_map = {0: 0, 3: 0, 6: 0, 9: 0,    # movable
                    1: 1, 4: 1, 7: 1, 10: 1,    # fixed
                    2: 2, 5: 2, 8: 2, 11: 2}    # dual
    modality = modality_map.get(sign_idx, 0)

    if modality == 0:     # movable: navamsha 1 = 0°-3°20'
        is_v = (0.0 <= deg < 3.333)
    elif modality == 1:   # fixed: navamsha 5 = 13°20'-16°40'
        is_v = (13.333 <= deg < 16.667)
    else:                 # dual: navamsha 9 = 26°40'-30°00'
        is_v = (26.667 <= deg <= 30.0)

    return {
        "is_vargottama": is_v,
        "sign_index":    sign_idx,
        "degree":        round(deg, 3),
        "strength_bonus": "Equivalent to own-sign placement" if is_v else "",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 7. DOMAIN-SPECIFIC VARGA HEURISTICS
# ═══════════════════════════════════════════════════════════════════════════════

# Which varga maps to which D1 house domain
VARGA_DOMAIN_MAP = {
    2:  {"house": 2,  "domain": "Wealth, assets, financial trajectory"},
    3:  {"house": 3,  "domain": "Siblings, courage, initiative"},
    4:  {"house": 4,  "domain": "Property, real estate, fortune"},
    5:  {"house": 5,  "domain": "Spiritual merit, authority, judgment"},
    7:  {"house": 5,  "domain": "Progeny, creativity, legacy"},
    9:  {"house": 7,  "domain": "Dharma, marriage, microscopic inner strength"},
    10: {"house": 10, "domain": "Career, status, great achievements"},
    12: {"house": 9,  "domain": "Parents, ancestry, lineage"},
    16: {"house": 4,  "domain": "Vehicles, comforts, accidents"},
    20: {"house": 5,  "domain": "Spiritual progress, meditation"},
    24: {"house": 4,  "domain": "Education, learning"},
    27: {"house": 3,  "domain": "Subconscious strengths, vulnerabilities"},
    30: {"house": 6,  "domain": "Evils, misfortunes, karmic diseases"},
    40: {"house": 4,  "domain": "Auspicious/inauspicious effects, maternal karma"},
    45: {"house": 9,  "domain": "General character, paternal karma"},
    60: {"house": 12, "domain": "Past life karma, ultimate override (Sanchita)"},
}


def get_varga_domain(divisor: int) -> Dict[str, Any]:
    """Return the domain info for a given varga divisor."""
    info = VARGA_DOMAIN_MAP.get(divisor)
    if info:
        return {"divisor": divisor, **info}
    return {"divisor": divisor, "house": 0, "domain": "Unknown divisor"}
