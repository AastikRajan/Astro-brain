"""
Phase 4 — File 3: Extended Nakshatra Compatibility & Classification.

Supplements the existing compatibility.py (8-koot) with:
  1. Rajju (Rope) 5-body-part compatibility
  2. Vedha (Obstruction) Nakshatra pairs for synastry
  3. Stree Deergha — minimum 15-star distance check
  4. Enhanced Nadi Dosha cancellation (6 exception rules)
  5. Panchaka danger check
  6. Nakshatra electional classification (7 categories)
  7. Maha / Tikshna Nakshatra flags
  8. Tarabala 9-category interpretation (extended)

Sources: Nakshatra Astrology Data and Algorithms.txt (new4/ File 3)

Architecture: Pure functions. No weights, no blending, no prediction logic.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

# ═══════════════════════════════════════════════════════════════════════════════
# NAKSHATRA NAMES (0-indexed, standard order)
# ═══════════════════════════════════════════════════════════════════════════════

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Moola", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati",
]

# ── Nadi per nakshatra (0-indexed): Adi=0, Madhya=1, Antya=2 ──
_NAK_NADI = [
    0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2,
]
_NADI_NAMES = {0: "Adi", 1: "Madhya", 2: "Antya"}

# ── Gana per nakshatra ──
_NAK_GANA = [
    "Deva", "Manushya", "Rakshasa", "Manushya", "Deva", "Manushya",
    "Deva", "Deva", "Rakshasa", "Rakshasa", "Manushya",
    "Manushya", "Deva", "Rakshasa", "Deva", "Rakshasa",
    "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya",
    "Deva", "Rakshasa", "Rakshasa", "Manushya",
    "Manushya", "Deva",
]

# ═══════════════════════════════════════════════════════════════════════════════
# 1. RAJJU (ROPE) COMPATIBILITY — 5-BODY-PART SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

# Mapping: nakshatra index → Rajju body zone
# Shira=0(Head), Kantha=1(Neck), Nabhi=2(Navel), Kati=3(Waist), Pada=4(Foot)

_RAJJU_MAP: Dict[int, int] = {
    # Shira (Head): Ashwini, Ardra, Punarvasu, Hasta, Jyeshtha, Shravana, Revati
    0: 0, 5: 0, 6: 0, 12: 0, 17: 0, 21: 0, 26: 0,
    # Kantha (Neck): Bharani, Pushya, Magha, Chitra, Anuradha, Dhanishta, Uttara Bhadra
    1: 1, 7: 1, 9: 1, 13: 1, 16: 1, 22: 1, 25: 1,
    # Nabhi (Navel): Krittika, Ashlesha, Purva Phalguni, Swati, Vishakha, Shatabhisha, Purva Bhadra
    2: 2, 8: 2, 10: 2, 14: 2, 15: 2, 23: 2, 24: 2,
    # Kati (Waist): Rohini, Mrigashira, Uttara Phalguni, Uttara Ashadha
    3: 3, 4: 3, 11: 3, 20: 3,
    # Pada (Foot): Moola, Purva Ashadha
    18: 4, 19: 4,
}

_RAJJU_NAMES = {0: "Shira (Head)", 1: "Kantha (Neck)", 2: "Nabhi (Navel)",
                3: "Kati (Waist)", 4: "Pada (Foot)"}

_RAJJU_DANGER = {
    0: "High risk to husband's longevity",
    1: "Risk to wife's health and longevity",
    2: "Severe complications regarding fertility/progeny",
    3: "Financial instability, systemic poverty",
    4: "Perpetual physical separation of the couple",
}


def compute_rajju(bride_nak: int, groom_nak: int) -> Dict[str, Any]:
    """
    Compute Rajju compatibility.
    Same Rajju body zone = danger. Different = safe.

    Returns:
        {
          "bride_rajju": str, "groom_rajju": str,
          "same_rajju": bool, "danger": str,
          "is_compatible": bool,
        }
    """
    b_rajju = _RAJJU_MAP.get(bride_nak % 27, 2)
    g_rajju = _RAJJU_MAP.get(groom_nak % 27, 2)
    same = (b_rajju == g_rajju)
    danger = _RAJJU_DANGER.get(b_rajju, "") if same else ""

    return {
        "bride_rajju":    _RAJJU_NAMES.get(b_rajju, ""),
        "groom_rajju":    _RAJJU_NAMES.get(g_rajju, ""),
        "same_rajju":     same,
        "danger":         danger,
        "is_compatible":  not same,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. VEDHA (OBSTRUCTION) NAKSHATRA PAIRS — SYNASTRY
# ═══════════════════════════════════════════════════════════════════════════════

# 13 mutually destructive pairs (0-indexed nakshatra indices)
_VEDHA_PAIRS: List[Tuple[int, int]] = [
    (0, 17),   # Ashwini – Jyeshtha
    (1, 16),   # Bharani – Anuradha
    (2, 15),   # Krittika – Vishakha
    (3, 14),   # Rohini – Swati
    (5, 21),   # Ardra – Shravana
    (6, 20),   # Punarvasu – Uttara Ashadha
    (7, 19),   # Pushya – Purva Ashadha
    (8, 18),   # Ashlesha – Moola
    (9, 26),   # Magha – Revati
    (10, 25),  # Purva Phalguni – Uttara Bhadrapada
    (11, 24),  # Uttara Phalguni – Purva Bhadrapada
    (12, 23),  # Hasta – Shatabhisha
    (4, 22),   # Mrigashira – Dhanishta
]

# Build a set for fast lookup
_VEDHA_SET: Set[frozenset] = {frozenset({a, b}) for a, b in _VEDHA_PAIRS}


def check_vedha_nakshatra(bride_nak: int, groom_nak: int) -> Dict[str, Any]:
    """
    Check if bride and groom nakshatras form a Vedha (obstruction) pair.
    Vedha pairs are mutually destructive — union is strictly forbidden.
    """
    bn = bride_nak % 27
    gn = groom_nak % 27
    is_vedha = frozenset({bn, gn}) in _VEDHA_SET

    return {
        "is_vedha":        is_vedha,
        "bride_nakshatra": NAKSHATRA_NAMES[bn],
        "groom_nakshatra": NAKSHATRA_NAMES[gn],
        "warning":         ("VEDHA active — mutually destructive pairing. "
                            "Union strictly forbidden by classical rules."
                            if is_vedha else ""),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. STREE DEERGHA — MINIMUM 15-STAR DISTANCE
# ═══════════════════════════════════════════════════════════════════════════════

def compute_stree_deergha(
    bride_nak: int, groom_nak: int, min_distance: int = 15,
) -> Dict[str, Any]:
    """
    Stree Deergha: forward distance from bride's nakshatra to groom's.
    Minimum 15 stars required for long-term prosperity of the wife.
    """
    bn = bride_nak % 27
    gn = groom_nak % 27
    distance = ((gn - bn) % 27) + 1  # inclusive forward count
    is_satisfied = distance >= min_distance

    return {
        "distance":     distance,
        "min_required": min_distance,
        "is_satisfied": is_satisfied,
        "note":         ("" if is_satisfied else
                         f"Stree Deergha not met ({distance} < {min_distance}). "
                         "Long-term financial security of wife may be affected."),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. ENHANCED NADI DOSHA CANCELLATION (6 EXCEPTION RULES)
# ═══════════════════════════════════════════════════════════════════════════════

# Nakshatras exempt from Nadi Dosha (classical texts)
_NADI_EXEMPT_NAKSHATRAS: Set[int] = {
    3,   # Rohini
    4,   # Mrigashira
    5,   # Ardra
    2,   # Krittika
    7,   # Pushya
    17,  # Jyeshtha
    9,   # Magha
    15,  # Vishakha
    21,  # Shravana
    26,  # Revati
    25,  # Uttara Bhadrapada
}

# Cross-Nakshatra synergistic pairs (same Nadi OK)
_NADI_SYNERGISTIC_PAIRS: Set[frozenset] = {
    frozenset({2, 3}),    # Krittika – Rohini
    frozenset({5, 6}),    # Ardra – Punarvasu
    frozenset({11, 12}),  # Uttara Phalguni – Hasta
    frozenset({24, 23}),  # Purva Bhadrapada – Shatabhisha
    frozenset({20, 21}),  # Uttara Ashadha – Shravana
}


def check_nadi_dosha_enhanced(
    bride_nak: int, groom_nak: int,
    bride_moon_sign: int, groom_moon_sign: int,
    bride_pada: int = 0, groom_pada: int = 0,
    same_gotra: bool = False,
) -> Dict[str, Any]:
    """
    Enhanced Nadi Dosha check with 6 cancellation rules.

    Cancellations:
      1. Same Rashi, Different Nakshatra
      2. Same Nakshatra, Different Rashi
      3. Same Nakshatra, Different Pada
      4. Exempt Nakshatra (either partner)
      5. Cross-Nakshatra Synergistic Pair
      6. Different Gotra

    Returns:
        {"has_nadi_dosha": bool, "is_cancelled": bool, "cancellation_rules": list, ...}
    """
    bn = bride_nak % 27
    gn = groom_nak % 27
    b_nadi = _NAK_NADI[bn]
    g_nadi = _NAK_NADI[gn]

    # No dosha if different Nadi
    if b_nadi != g_nadi:
        return {
            "has_nadi_dosha": False,
            "is_cancelled":   False,
            "bride_nadi":     _NADI_NAMES[b_nadi],
            "groom_nadi":     _NADI_NAMES[g_nadi],
            "cancellation_rules": [],
            "score": 8,
        }

    # Same Nadi — check 6 cancellations
    cancellations: List[str] = []

    bs = bride_moon_sign % 12
    gs = groom_moon_sign % 12

    # Rule 1: Same Rashi, Different Nakshatra
    if bs == gs and bn != gn:
        cancellations.append("Same Rashi different Nakshatra — genetic variance sufficient")

    # Rule 2: Same Nakshatra, Different Rashi (boundary nakshatras)
    if bn == gn and bs != gs:
        cancellations.append("Same Nakshatra different Rashi — structural shift neutralizes dosha")

    # Rule 3: Same Nakshatra, Different Pada
    if bn == gn and bride_pada != groom_pada and bride_pada > 0 and groom_pada > 0:
        cancellations.append(f"Same Nakshatra different Pada ({bride_pada} vs {groom_pada})")

    # Rule 4: Exempt Nakshatras
    if bn in _NADI_EXEMPT_NAKSHATRAS or gn in _NADI_EXEMPT_NAKSHATRAS:
        exempt_names = []
        if bn in _NADI_EXEMPT_NAKSHATRAS:
            exempt_names.append(NAKSHATRA_NAMES[bn])
        if gn in _NADI_EXEMPT_NAKSHATRAS:
            exempt_names.append(NAKSHATRA_NAMES[gn])
        cancellations.append(f"Exempt Nakshatra(s): {', '.join(exempt_names)}")

    # Rule 5: Cross-Nakshatra Synergistic Pair
    if frozenset({bn, gn}) in _NADI_SYNERGISTIC_PAIRS:
        cancellations.append(f"Synergistic pair: {NAKSHATRA_NAMES[bn]}-{NAKSHATRA_NAMES[gn]}")

    # Rule 6: Different Gotra
    if not same_gotra:
        cancellations.append("Different Gotra — biological divergence minimizes dosha")

    is_cancelled = len(cancellations) > 0

    return {
        "has_nadi_dosha":     True,
        "is_cancelled":       is_cancelled,
        "bride_nadi":         _NADI_NAMES[b_nadi],
        "groom_nadi":         _NADI_NAMES[g_nadi],
        "cancellation_rules": cancellations,
        "score":              8 if is_cancelled else 0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 5. PANCHAKA DANGER CHECK
# ═══════════════════════════════════════════════════════════════════════════════

_PANCHAKA_TYPES = {
    1: ("Mrityu Panchaka", "Death/mortal danger"),
    2: ("Agni Panchaka", "Fire-related danger"),
    4: ("Raja Panchaka", "Government/authority trouble"),
    6: ("Chora Panchaka", "Theft/robbery danger"),
    8: ("Roga Panchaka", "Disease/health danger"),
}


def compute_panchaka(
    tithi_num: int, weekday: int, nakshatra_idx: int, lagna_sign: int,
) -> Dict[str, Any]:
    """
    Panchaka danger check.
    Sum = tithi + weekday + nakshatra + lagna, divide by 9.
    Remainders 1, 2, 4, 6, 8 = danger types.

    Args:
        tithi_num:     1-30
        weekday:       1=Sunday ... 7=Saturday
        nakshatra_idx: 1-27
        lagna_sign:    1-12

    Returns: {"is_danger": bool, "panchaka_type": str, "description": str}
    """
    total = tithi_num + weekday + nakshatra_idx + lagna_sign
    remainder = total % 9

    if remainder in _PANCHAKA_TYPES:
        ptype, desc = _PANCHAKA_TYPES[remainder]
        return {
            "is_danger":     True,
            "panchaka_type": ptype,
            "description":   desc,
            "remainder":     remainder,
            "total":         total,
        }

    return {
        "is_danger":     False,
        "panchaka_type": "",
        "description":   "",
        "remainder":     remainder,
        "total":         total,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 6. NAKSHATRA ELECTIONAL CLASSIFICATION (7 Categories)
# ═══════════════════════════════════════════════════════════════════════════════

_NAKSHATRA_CLASSIFICATION: Dict[str, Dict[str, Any]] = {
    # Sthira (Fixed/Stable)
    "Rohini":          {"class": "Sthira", "nature": "Fixed/Stable"},
    "Uttara Phalguni": {"class": "Sthira", "nature": "Fixed/Stable"},
    "Uttara Ashadha":  {"class": "Sthira", "nature": "Fixed/Stable"},
    "Uttara Bhadrapada": {"class": "Sthira", "nature": "Fixed/Stable"},

    # Chara (Movable/Swift)
    "Punarvasu":   {"class": "Chara", "nature": "Movable/Swift"},
    "Swati":       {"class": "Chara", "nature": "Movable/Swift"},
    "Shravana":    {"class": "Chara", "nature": "Movable/Swift"},
    "Dhanishta":   {"class": "Chara", "nature": "Movable/Swift"},
    "Shatabhisha": {"class": "Chara", "nature": "Movable/Swift"},

    # Mridu (Tender/Soft)
    "Chitra":     {"class": "Mridu", "nature": "Tender/Soft"},
    "Anuradha":   {"class": "Mridu", "nature": "Tender/Soft"},
    "Mrigashira": {"class": "Mridu", "nature": "Tender/Soft"},
    "Revati":     {"class": "Mridu", "nature": "Tender/Soft"},

    # Ugra (Fierce/Violent)
    "Bharani":          {"class": "Ugra", "nature": "Fierce/Violent"},
    "Magha":            {"class": "Ugra", "nature": "Fierce/Violent"},
    "Purva Phalguni":   {"class": "Ugra", "nature": "Fierce/Violent"},
    "Purva Ashadha":    {"class": "Ugra", "nature": "Fierce/Violent"},
    "Purva Bhadrapada": {"class": "Ugra", "nature": "Fierce/Violent"},

    # Tikshna (Sharp/Cruel)
    "Moola":    {"class": "Tikshna", "nature": "Sharp/Cruel"},
    "Jyeshtha": {"class": "Tikshna", "nature": "Sharp/Cruel"},
    "Ardra":    {"class": "Tikshna", "nature": "Sharp/Cruel"},
    "Ashlesha": {"class": "Tikshna", "nature": "Sharp/Cruel"},

    # Kshipra (Swift/Light)
    "Ashwini": {"class": "Kshipra", "nature": "Swift/Light"},
    "Pushya":  {"class": "Kshipra", "nature": "Swift/Light"},
    "Hasta":   {"class": "Kshipra", "nature": "Swift/Light"},

    # Mishra (Mixed)
    "Krittika": {"class": "Mishra", "nature": "Mixed"},
    "Vishakha": {"class": "Mishra", "nature": "Mixed"},
}

# Prescribed activities by classification
_ELECTIONAL_ACTIVITIES = {
    "Sthira":  "Planting, buying property, foundations, long-term investments",
    "Chara":   "Purchasing vehicles, travel, gardening, dynamic transactions",
    "Mridu":   "Fine arts, new apparel, romance, forming friendships",
    "Ugra":    "Demolition, fire, confrontation, assertive tactics",
    "Tikshna": "Divorce, exorcism, severe punishment, destruction rituals",
    "Kshipra": "Medications, swift commerce, short travel, rapid communications",
    "Mishra":  "Routine worship, fire ceremonies, electronics, maintenance",
}

# Maha Nakshatras — override for synastry
_MAHA_NAKSHATRAS: Set[int] = {7, 9, 16, 4}  # Pushya, Magha, Anuradha, Mrigashira

# Tikshna (Sharp) Nakshatras — forbidden for creation/growth
_TIKSHNA_NAKSHATRAS: Set[int] = {18, 17, 5, 8}  # Moola, Jyeshtha, Ardra, Ashlesha


def get_nakshatra_classification(nakshatra_idx: int) -> Dict[str, Any]:
    """
    Get electional classification for a nakshatra.

    Returns category, nature, prescribed activities, and special flags.
    """
    idx = nakshatra_idx % 27
    name = NAKSHATRA_NAMES[idx]
    info = _NAKSHATRA_CLASSIFICATION.get(name, {"class": "Unknown", "nature": ""})
    cls = info["class"]

    return {
        "nakshatra":   name,
        "index":       idx,
        "class":       cls,
        "nature":      info["nature"],
        "activities":  _ELECTIONAL_ACTIVITIES.get(cls, ""),
        "is_maha":     idx in _MAHA_NAKSHATRAS,
        "is_tikshna":  idx in _TIKSHNA_NAKSHATRAS,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 7. TARABALA — EXTENDED 9-CATEGORY INTERPRETATION
# ═══════════════════════════════════════════════════════════════════════════════

_TARABALA_CATEGORIES = {
    1: {"name": "Janma",      "quality": "Mixed",     "description": "High emotional sensitivity, sibling-like friction"},
    2: {"name": "Sampat",     "quality": "Very Good",  "description": "Financial influx, asset accumulation, commercial success"},
    3: {"name": "Vipat",      "quality": "Bad",        "description": "Unexpected crises, accidents, severe delays"},
    4: {"name": "Kshema",     "quality": "Good",       "description": "Protection, stability, steady growth, medical recovery"},
    5: {"name": "Pratyari",   "quality": "Bad",        "description": "Interpersonal conflicts, blocked energy, opposition"},
    6: {"name": "Sadhaka",    "quality": "Very Good",  "description": "Goal accomplishment, ambition realization, breakthroughs"},
    7: {"name": "Naidhana",   "quality": "Terrible",   "description": "Severe danger, physical risk, complete failure"},
    8: {"name": "Mitra",      "quality": "Good",       "description": "Collaborative success, harmonious social interactions"},
    9: {"name": "Ati-Mitra",  "quality": "Very Good",  "description": "Highly auspicious, deep gains, effortless progress"},
}


def compute_tarabala_extended(
    birth_nak: int, transit_nak: int,
) -> Dict[str, Any]:
    """
    Compute Tarabala (Star Strength) with full 9-category interpretation.

    Formula: ((transit_nak - birth_nak) % 27 + 1) % 9
    If remainder = 0, treat as 9.
    """
    bn = birth_nak % 27
    tn = transit_nak % 27
    count = ((tn - bn) % 27) + 1
    remainder = count % 9
    if remainder == 0:
        remainder = 9

    info = _TARABALA_CATEGORIES.get(remainder, {"name": "Unknown", "quality": "", "description": ""})

    return {
        "tara_number":  remainder,
        "tara_name":    info["name"],
        "quality":      info["quality"],
        "description":  info["description"],
        "count":        count,
        "is_auspicious": info["quality"] in {"Very Good", "Good", "Mixed"},
        "is_dangerous":  remainder == 7,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 8. COMPREHENSIVE SYNASTRY REPORT (combines all checks)
# ═══════════════════════════════════════════════════════════════════════════════

def compute_extended_compatibility(
    bride_nak: int, groom_nak: int,
    bride_moon_sign: int, groom_moon_sign: int,
    bride_pada: int = 0, groom_pada: int = 0,
    same_gotra: bool = False,
) -> Dict[str, Any]:
    """
    Compute all extended compatibility checks beyond Ashta-Koot.

    Returns combined report with Rajju, Vedha, Stree Deergha,
    enhanced Nadi, and Maha Nakshatra override.
    """
    rajju = compute_rajju(bride_nak, groom_nak)
    vedha = check_vedha_nakshatra(bride_nak, groom_nak)
    stree = compute_stree_deergha(bride_nak, groom_nak)
    nadi  = check_nadi_dosha_enhanced(
        bride_nak, groom_nak, bride_moon_sign, groom_moon_sign,
        bride_pada, groom_pada, same_gotra,
    )

    # Maha Nakshatra override
    bride_maha = (bride_nak % 27) in _MAHA_NAKSHATRAS
    groom_maha = (groom_nak % 27) in _MAHA_NAKSHATRAS
    maha_override = bride_maha or groom_maha

    # Aggregate flags
    warnings: List[str] = []
    if rajju["same_rajju"]:
        warnings.append(f"Rajju mismatch: {rajju['danger']}")
    if vedha["is_vedha"]:
        warnings.append("Vedha Nakshatra pair: mutually destructive")
    if not stree["is_satisfied"]:
        warnings.append(f"Stree Deergha not met (distance={stree['distance']})")
    if nadi["has_nadi_dosha"] and not nadi["is_cancelled"]:
        warnings.append("Nadi Dosha active (no cancellation found)")

    return {
        "rajju":            rajju,
        "vedha":            vedha,
        "stree_deergha":    stree,
        "nadi_enhanced":    nadi,
        "maha_override":    maha_override,
        "bride_is_maha":    bride_maha,
        "groom_is_maha":    groom_maha,
        "warnings":         warnings,
        "extended_ok":      len(warnings) == 0 or maha_override,
    }
