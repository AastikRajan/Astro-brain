"""
Jyotish Lookup Tables — Comprehensive Compatibility & Reference Data.

Contains:
  1. Yoni Koota: 27 nakshatra→animal mapping + 14×14 compatibility matrix
  2. Vashya Koota: 12 signs → 5 categories + 5×5 matrix
  3. Bhakoot Koota: 12×12 score matrix + cancellation rules
  4. Nara Chakra: 27 nakshatra → anatomical body-part mapping
  5. Extended Tajika Sahams (50 formulas, expanding existing 16)
  6. 16 Tajika Yoga definitions (full array)

Reference: Classical Ashtakoota, Bhrigu Sutras, Prashna Marga, Tajika Neelakanthi.
"""
from __future__ import annotations
from typing import Dict, Any, List, Tuple, Optional
import math


# ═══════════════════════════════════════════════════════════════
# 1. YONI KOOTA — 14 Animal Types × 27 Nakshatras
# ═══════════════════════════════════════════════════════════════

# Nakshatra index (0-based) → (animal, gender)
YONI_NAKSHATRA_MAP = {
    0:  ("HORSE",    "M"),   # Ashwini
    1:  ("ELEPHANT", "M"),   # Bharani
    2:  ("SHEEP",    "F"),   # Krittika
    3:  ("SERPENT",  "M"),   # Rohini
    4:  ("SERPENT",  "F"),   # Mrigashira
    5:  ("DOG",      "F"),   # Ardra
    6:  ("CAT",      "F"),   # Punarvasu
    7:  ("SHEEP",    "M"),   # Pushya
    8:  ("CAT",      "M"),   # Ashlesha
    9:  ("RAT",      "M"),   # Magha
    10: ("RAT",      "F"),   # Purva Phalguni
    11: ("COW",      "M"),   # Uttara Phalguni
    12: ("BUFFALO",  "F"),   # Hasta
    13: ("TIGER",    "F"),   # Chitra
    14: ("BUFFALO",  "M"),   # Swati
    15: ("TIGER",    "M"),   # Vishakha
    16: ("DEER",     "F"),   # Anuradha
    17: ("DEER",     "M"),   # Jyeshtha
    18: ("DOG",      "M"),   # Mula
    19: ("MONKEY",   "M"),   # Purva Ashadha
    20: ("MONGOOSE", "M"),   # Uttara Ashadha
    21: ("MONKEY",   "F"),   # Shravana
    22: ("LION",     "F"),   # Dhanishta
    23: ("HORSE",    "F"),   # Shatabhisha
    24: ("LION",     "M"),   # Purva Bhadrapada
    25: ("COW",      "F"),   # Uttara Bhadrapada
    26: ("ELEPHANT", "F"),   # Revati
}

# 14 animal types (order for matrix indexing)
YONI_ANIMALS = [
    "HORSE", "ELEPHANT", "SHEEP", "SERPENT", "DOG", "CAT", "RAT",
    "COW", "BUFFALO", "TIGER", "DEER", "MONKEY", "MONGOOSE", "LION"
]

# 14×14 Yoni Compatibility Matrix (symmetric)
# Row/col order matches YONI_ANIMALS above
# Score range: 0-4  (4=same animal, 0=hostile enemies)
YONI_MATRIX = [
    # HOR  ELE  SHE  SER  DOG  CAT  RAT  COW  BUF  TIG  DEE  MON  MON  LIO
    [  4,   2,   2,   3,   2,   2,   2,   1,   0,   1,   3,   2,   2,   1],  # Horse
    [  2,   4,   3,   3,   2,   2,   2,   2,   3,   1,   2,   3,   2,   0],  # Elephant
    [  2,   3,   4,   2,   1,   2,   1,   3,   2,   1,   2,   0,   2,   1],  # Sheep
    [  3,   3,   2,   4,   2,   1,   1,   1,   2,   2,   2,   2,   0,   2],  # Serpent
    [  2,   2,   1,   2,   4,   2,   1,   2,   2,   1,   0,   2,   2,   1],  # Dog
    [  2,   2,   2,   1,   2,   4,   0,   2,   2,   1,   2,   3,   1,   1],  # Cat
    [  2,   2,   1,   1,   1,   0,   4,   2,   2,   2,   2,   2,   1,   2],  # Rat
    [  1,   2,   3,   1,   2,   2,   2,   4,   2,   0,   3,   2,   2,   1],  # Cow
    [  0,   3,   2,   2,   2,   2,   2,   2,   4,   1,   2,   2,   2,   1],  # Buffalo
    [  1,   1,   1,   2,   1,   1,   2,   0,   1,   4,   1,   2,   1,   1],  # Tiger
    [  3,   2,   2,   2,   0,   2,   2,   3,   2,   1,   4,   2,   2,   1],  # Deer
    [  2,   3,   0,   2,   2,   3,   2,   2,   2,   2,   2,   4,   2,   1],  # Monkey
    [  2,   2,   2,   0,   2,   1,   1,   2,   2,   1,   2,   2,   4,   2],  # Mongoose
    [  1,   0,   1,   2,   1,   1,   2,   1,   1,   1,   1,   1,   2,   4],  # Lion
]


def get_yoni_score(nak_a: int, nak_b: int) -> Dict[str, Any]:
    """
    Yoni Koota score for two nakshatras.

    Args:
        nak_a, nak_b: Nakshatra indices 0-26

    Returns:
        Dict with score (0-4), animals, genders, quality.
    """
    a_info = YONI_NAKSHATRA_MAP.get(nak_a, ("HORSE", "M"))
    b_info = YONI_NAKSHATRA_MAP.get(nak_b, ("HORSE", "M"))

    a_animal, a_gender = a_info
    b_animal, b_gender = b_info

    a_idx = YONI_ANIMALS.index(a_animal) if a_animal in YONI_ANIMALS else 0
    b_idx = YONI_ANIMALS.index(b_animal) if b_animal in YONI_ANIMALS else 0

    score = YONI_MATRIX[a_idx][b_idx]

    quality_map = {4: "EXCELLENT", 3: "GOOD", 2: "AVERAGE", 1: "POOR", 0: "HOSTILE"}

    return {
        "score": score,
        "max_score": 4,
        "animal_a": a_animal, "gender_a": a_gender,
        "animal_b": b_animal, "gender_b": b_gender,
        "same_animal": a_animal == b_animal,
        "quality": quality_map.get(score, "UNKNOWN"),
        "yoni_dosha": score == 0,
    }


# ═══════════════════════════════════════════════════════════════
# 2. VASHYA KOOTA — Sign → Category + 5×5 Matrix
# ═══════════════════════════════════════════════════════════════

# Sign (0-based) → Vashya category
# Sagittarius: 0-15° = MANAV, 15-30° = CHATUSHPAD
# Capricorn: 0-15° = CHATUSHPAD, 15-30° = JALACHARA
def get_vashya_category(sign_index: int, degree_in_sign: float = 15.0) -> str:
    """Return Vashya category for a sign."""
    SIMPLE_MAP = {
        0: "CHATUSHPAD",   # Aries
        1: "CHATUSHPAD",   # Taurus
        2: "MANAV",        # Gemini
        3: "JALACHARA",    # Cancer
        4: "VANACHARA",    # Leo
        5: "MANAV",        # Virgo
        6: "MANAV",        # Libra
        7: "KEETA",        # Scorpio
        # 8: Sagittarius — split
        # 9: Capricorn — split
        10: "MANAV",       # Aquarius
        11: "JALACHARA",   # Pisces
    }
    if sign_index == 8:  # Sagittarius
        return "MANAV" if degree_in_sign < 15.0 else "CHATUSHPAD"
    if sign_index == 9:  # Capricorn
        return "CHATUSHPAD" if degree_in_sign < 15.0 else "JALACHARA"
    return SIMPLE_MAP.get(sign_index, "MANAV")


VASHYA_CATEGORIES = ["CHATUSHPAD", "MANAV", "JALACHARA", "VANACHARA", "KEETA"]

# 5×5 Vashya matrix (Bride ↓ × Groom →)
# Order: CHATUSHPAD, MANAV, JALACHARA, VANACHARA, KEETA
VASHYA_MATRIX = [
    # CHAT  MAN   JAL   VAN   KEE
    [ 2.0,  0.0,  0.0,  0.5,  0.0],  # Chatushpad
    [ 1.0,  2.0,  1.0,  0.5,  1.0],  # Manav
    [ 0.5,  1.0,  2.0,  1.0,  1.0],  # Jalachara
    [ 0.0,  0.0,  0.0,  2.0,  0.0],  # Vanachara
    [ 1.0,  1.0,  1.0,  0.0,  2.0],  # Keeta
]


def get_vashya_score(
    bride_sign: int, bride_deg: float,
    groom_sign: int, groom_deg: float,
) -> Dict[str, Any]:
    """
    Vashya Koota score.

    Args:
        bride_sign, groom_sign: 0-11
        bride_deg, groom_deg: degree within sign (0-30)

    Returns:
        Score (0-2), categories, quality.
    """
    b_cat = get_vashya_category(bride_sign, bride_deg)
    g_cat = get_vashya_category(groom_sign, groom_deg)

    b_idx = VASHYA_CATEGORIES.index(b_cat) if b_cat in VASHYA_CATEGORIES else 1
    g_idx = VASHYA_CATEGORIES.index(g_cat) if g_cat in VASHYA_CATEGORIES else 1

    score = VASHYA_MATRIX[b_idx][g_idx]

    return {
        "score": score,
        "max_score": 2.0,
        "bride_category": b_cat,
        "groom_category": g_cat,
        "quality": "GOOD" if score >= 1.5 else ("AVERAGE" if score >= 1.0 else "POOR"),
    }


# ═══════════════════════════════════════════════════════════════
# 3. BHAKOOT KOOTA — 12×12 Matrix + Cancellation
# ═══════════════════════════════════════════════════════════════

# Bhakoot 12×12 matrix (Bride_sign × Groom_sign, 0-indexed)
# Score: 7 (auspicious) or 0 (Bhakoot Dosha)
# Axes: 1/1=7, 1/7=7, 3/11=7, 4/10=7; 2/12=0, 5/9=0, 6/8=0
BHAKOOT_MATRIX = [
    # Ari Tau Gem Can Leo Vir Lib Sco Sag Cap Aqu Pis
    [ 7,  0,  7,  7,  0,  0,  7,  0,  0,  7,  7,  0],  # Aries
    [ 0,  7,  0,  7,  7,  0,  0,  7,  0,  0,  7,  7],  # Taurus
    [ 7,  0,  7,  0,  7,  7,  0,  0,  7,  0,  0,  7],  # Gemini
    [ 7,  7,  0,  7,  0,  7,  7,  0,  0,  7,  0,  0],  # Cancer
    [ 0,  7,  7,  0,  7,  0,  7,  7,  0,  0,  7,  0],  # Leo
    [ 0,  0,  7,  7,  0,  7,  0,  7,  7,  0,  0,  7],  # Virgo
    [ 7,  0,  0,  7,  7,  0,  7,  0,  7,  7,  0,  0],  # Libra
    [ 0,  7,  0,  0,  7,  7,  0,  7,  0,  7,  7,  0],  # Scorpio
    [ 0,  0,  7,  0,  0,  7,  7,  0,  7,  0,  7,  7],  # Sagittarius
    [ 7,  0,  0,  7,  0,  0,  7,  7,  0,  7,  0,  7],  # Capricorn
    [ 7,  7,  0,  0,  7,  0,  0,  7,  7,  0,  7,  0],  # Aquarius
    [ 0,  7,  7,  0,  0,  7,  0,  0,  7,  7,  0,  7],  # Pisces
]

# Sign lords (0-based sign → planet)
_SIGN_LORDS = {
    0: "MARS", 1: "VENUS", 2: "MERCURY", 3: "MOON",
    4: "SUN", 5: "MERCURY", 6: "VENUS", 7: "MARS",
    8: "JUPITER", 9: "SATURN", 10: "SATURN", 11: "JUPITER",
}

# Natural friendship
_NATURAL_FRIENDS = {
    "SUN":     {"MOON", "MARS", "JUPITER"},
    "MOON":    {"SUN", "MERCURY"},
    "MARS":    {"SUN", "MOON", "JUPITER"},
    "MERCURY": {"SUN", "VENUS"},
    "JUPITER": {"SUN", "MOON", "MARS"},
    "VENUS":   {"MERCURY", "SATURN"},
    "SATURN":  {"MERCURY", "VENUS"},
}


def check_bhakoot_cancellation(bride_sign: int, groom_sign: int) -> List[str]:
    """Check Bhakoot Dosha cancellation conditions."""
    cancellations = []
    b_lord = _SIGN_LORDS.get(bride_sign, "")
    g_lord = _SIGN_LORDS.get(groom_sign, "")

    # Condition 1: Same Rashi lord
    if b_lord == g_lord:
        cancellations.append("SAME_LORD")

    # Condition 2: Lords are natural mutual friends
    if b_lord in _NATURAL_FRIENDS.get(g_lord, set()) and g_lord in _NATURAL_FRIENDS.get(b_lord, set()):
        cancellations.append("MUTUAL_FRIENDS")

    # Condition 3: Same Rashi (always score=7, so won't have dosha)
    if bride_sign == groom_sign:
        cancellations.append("SAME_RASHI")

    # Condition 5: Bride's Moon 5th from Groom's Moon (trine override)
    if (bride_sign - groom_sign) % 12 == 4:
        cancellations.append("TRINE_5TH_OVERRIDE")

    return cancellations


def get_bhakoot_score(bride_sign: int, groom_sign: int) -> Dict[str, Any]:
    """
    Bhakoot Koota score with cancellation check.

    Args:
        bride_sign, groom_sign: 0-11

    Returns:
        Score (0 or 7), cancellation info.
    """
    raw_score = BHAKOOT_MATRIX[bride_sign % 12][groom_sign % 12]
    cancellations = []
    effective_score = raw_score

    if raw_score == 0:
        cancellations = check_bhakoot_cancellation(bride_sign, groom_sign)
        if cancellations:
            effective_score = 7  # Dosha cancelled

    offset = (bride_sign - groom_sign) % 12
    axis_type = "NEUTRAL"
    if offset in (0,):
        axis_type = "1/1"
    elif offset in (6,):
        axis_type = "1/7"
    elif offset in (2, 10):
        axis_type = "3/11"
    elif offset in (3, 9):
        axis_type = "4/10"
    elif offset in (1, 11):
        axis_type = "2/12"
    elif offset in (4, 8):
        axis_type = "5/9"
    elif offset in (5, 7):
        axis_type = "6/8"

    return {
        "raw_score": raw_score,
        "effective_score": effective_score,
        "max_score": 7,
        "axis": axis_type,
        "dosha": raw_score == 0,
        "cancelled": len(cancellations) > 0,
        "cancellation_reasons": cancellations,
    }


# ═══════════════════════════════════════════════════════════════
# 4. NARA CHAKRA — 27-Nakshatra Body Mapping
# ═══════════════════════════════════════════════════════════════

# Nakshatra (0-based) → body parts (surgery forbidden during Moon transit)
NARA_CHAKRA = {
    0:  {"nakshatra": "Ashwini",           "body": "Knees, top of feet"},
    1:  {"nakshatra": "Bharani",           "body": "Head, bottom of feet"},
    2:  {"nakshatra": "Krittika",          "body": "Waist, hip joints, crown of head"},
    3:  {"nakshatra": "Rohini",            "body": "Legs, forehead, ankles, shins, calves"},
    4:  {"nakshatra": "Mrigashira",        "body": "Eyes, eyebrows"},
    5:  {"nakshatra": "Ardra",             "body": "Hair, eyes, back/front of head (brain)"},
    6:  {"nakshatra": "Punarvasu",         "body": "Fingers, nose"},
    7:  {"nakshatra": "Pushya",            "body": "Mouth, face, bone joints, elbows"},
    8:  {"nakshatra": "Ashlesha",          "body": "Nails, knuckles, kneecaps, ears"},
    9:  {"nakshatra": "Magha",             "body": "Nose, lips, chin"},
    10: {"nakshatra": "Purva Phalguni",    "body": "Sexual organs, lips, right hand"},
    11: {"nakshatra": "Uttara Phalguni",   "body": "Sexual organs, left hand"},
    12: {"nakshatra": "Hasta",             "body": "Hands"},
    13: {"nakshatra": "Chitra",            "body": "Forehead, neck"},
    14: {"nakshatra": "Swati",             "body": "Teeth, chest, respiratory system"},
    15: {"nakshatra": "Vishakha",          "body": "Upper limbs, arms, breasts"},
    16: {"nakshatra": "Anuradha",          "body": "Heart, breasts, stomach, womb"},
    17: {"nakshatra": "Jyeshtha",          "body": "Tongue, neck, right torso"},
    18: {"nakshatra": "Mula",              "body": "Both feet, left torso, back"},
    19: {"nakshatra": "Purva Ashadha",     "body": "Both thighs"},
    20: {"nakshatra": "Uttara Ashadha",    "body": "Both thighs, waist"},
    21: {"nakshatra": "Shravana",          "body": "Ears, sexual organs, gait"},
    22: {"nakshatra": "Dhanishta",         "body": "Back, anus"},
    23: {"nakshatra": "Shatabhisha",       "body": "Chin, jaw, right thigh"},
    24: {"nakshatra": "Purva Bhadrapada",  "body": "Ribs, abdomen, sides of legs, left thigh, soles"},
    25: {"nakshatra": "Uttara Bhadrapada", "body": "Sides of body, legs, shins, soles"},
    26: {"nakshatra": "Revati",            "body": "Armpits, abdomen, groin"},
}


def check_surgical_contraindication(moon_nak_index: int, target_body_part: str) -> Dict[str, Any]:
    """
    Check if surgery on a body part is contraindicated during Moon's nakshatra transit.

    Args:
        moon_nak_index: Current Moon nakshatra (0-26)
        target_body_part: Body part being operated on (e.g., "knee", "eyes")

    Returns:
        Dict with contraindication flag and details.
    """
    nak_info = NARA_CHAKRA.get(moon_nak_index, {})
    ruled_body = nak_info.get("body", "")
    target_lower = target_body_part.lower()
    ruled_lower = ruled_body.lower()

    # Check if target body part matches ruled region
    is_contraindicated = any(
        part.strip() in target_lower or target_lower in part.strip()
        for part in ruled_lower.split(",")
    ) if target_lower and ruled_lower else False

    return {
        "moon_nakshatra": moon_nak_index,
        "nakshatra_name": nak_info.get("nakshatra", "Unknown"),
        "ruled_body_parts": ruled_body,
        "target_body_part": target_body_part,
        "contraindicated": is_contraindicated,
        "warning": f"Surgery on '{target_body_part}' is CONTRAINDICATED during {nak_info.get('nakshatra', '')} Moon transit" if is_contraindicated else None,
    }


# ═══════════════════════════════════════════════════════════════
# 5. EXTENDED TAJIKA SAHAMS (50 total)
# ═══════════════════════════════════════════════════════════════

# Format: (day_formula, night_formula)  where formula = (A, B, "ASC")
# Computation: (lon_A - lon_B + ASC) % 360
# Special keys: "PUNYA" = Punya Saham longitude, "H2C" = 2nd house cusp, etc.
EXTENDED_SAHAMS: Dict[str, Dict[str, Tuple[str, str, str]]] = {
    "Punya":          {"day": ("MOON", "SUN", "ASC"),   "night": ("SUN", "MOON", "ASC")},
    "Vidya":          {"day": ("SUN", "MOON", "ASC"),   "night": ("MOON", "SUN", "ASC")},
    "Yasa":           {"day": ("JUPITER", "PUNYA", "ASC"), "night": ("PUNYA", "JUPITER", "ASC")},
    "Mahatmya":       {"day": ("PUNYA", "MARS", "ASC"),    "night": ("MARS", "PUNYA", "ASC")},
    "Gaurava":        {"day": ("JUPITER", "MOON", "ASC"),  "night": ("MOON", "JUPITER", "ASC")},
    "Karma":          {"day": ("MARS", "MERCURY", "ASC"),  "night": ("MERCURY", "MARS", "ASC")},
    "Artha":          {"day": ("H2C", "H2L", "ASC"),       "night": ("H2L", "H2C", "ASC")},
    "Vanijya":        {"day": ("MARS", "SUN", "ASC"),      "night": ("SUN", "MARS", "ASC")},
    "Siddhi":         {"day": ("PUNYA", "SUN", "ASC"),     "night": ("SUN", "PUNYA", "ASC")},
    "Samarth":        {"day": ("MARS", "ASCL", "ASC"),     "night": ("ASCL", "MARS", "ASC")},
    "Bhrata":         {"day": ("JUPITER", "SATURN", "ASC"),"night": ("SATURN", "JUPITER", "ASC")},
    "Rajya":          {"day": ("SATURN", "SUN", "ASC"),    "night": ("SUN", "SATURN", "ASC")},
    "Taata":          {"day": ("SUN", "SATURN", "ASC"),    "night": ("SATURN", "SUN", "ASC")},
    "Mata":           {"day": ("MOON", "VENUS", "ASC"),    "night": ("VENUS", "MOON", "ASC")},
    "Suta":           {"day": ("JUPITER", "MOON", "ASC"),  "night": ("MOON", "JUPITER", "ASC")},
    "Jeevita":        {"day": ("SATURN", "JUPITER", "ASC"),"night": ("JUPITER", "SATURN", "ASC")},
    "Ambu":           {"day": ("CAN15", "MOON", "ASC"),    "night": ("MOON", "CAN15", "ASC")},
    "Kama":           {"day": ("VENUS", "ASC", "ASC"),     "night": ("ASC", "VENUS", "ASC")},
    "Mandya":         {"day": ("SATURN", "MOON", "ASC"),   "night": ("MOON", "SATURN", "ASC")},
    "Manmatha":       {"day": ("ASC", "MOON", "ASC"),      "night": ("MOON", "ASC", "ASC")},
    "Kali":           {"day": ("JUPITER", "MARS", "ASC"),  "night": ("MARS", "JUPITER", "ASC")},
    "Kshama":         {"day": ("JUPITER", "MARS", "ASC"),  "night": ("MARS", "JUPITER", "ASC")},
    "Shastra":        {"day": ("JUPITER", "SATURN", "ASC"),"night": ("SATURN", "JUPITER", "ASC")},
    "Bandhu":         {"day": ("MERCURY", "MOON", "ASC"),  "night": ("MOON", "MERCURY", "ASC")},
    "Bandhaka":       {"day": ("VENUS", "MOON", "ASC"),    "night": ("MOON", "VENUS", "ASC")},
    "Mrityu":         {"day": ("H8C", "MOON", "ASC"),      "night": ("MOON", "H8C", "ASC")},
    "Paradesa":       {"day": ("H9C", "H9L", "ASC"),       "night": ("H9L", "H9C", "ASC")},
    "Dhana":          {"day": ("VENUS", "MERCURY", "ASC"), "night": ("MERCURY", "VENUS", "ASC")},
    "Anya_Dara":      {"day": ("VENUS", "SUN", "ASC"),     "night": ("SUN", "VENUS", "ASC")},
    "Anya_Karma":     {"day": ("MERCURY", "SATURN", "ASC"),"night": ("SATURN", "MERCURY", "ASC")},
    "Vyapara":        {"day": ("MARS", "SATURN", "ASC"),   "night": ("SATURN", "MARS", "ASC")},
    "Satru":          {"day": ("MARS", "SATURN", "ASC"),   "night": ("SATURN", "MARS", "ASC")},
    "Daridra":        {"day": ("JUPITER", "MERCURY", "ASC"),"night": ("MERCURY", "JUPITER", "ASC")},
    "Bandhana":       {"day": ("PUNYA", "SATURN", "ASC"),  "night": ("SATURN", "PUNYA", "ASC")},
    "Roga":           {"day": ("ASC", "MOON", "ASC"),      "night": ("MOON", "ASC", "ASC")},
    "Apamrityu":      {"day": ("H8C", "MARS", "ASC"),      "night": ("MARS", "H8C", "ASC")},
    "Vivaha":         {"day": ("VENUS", "SATURN", "ASC"),  "night": ("SATURN", "VENUS", "ASC")},
    "Santapa":        {"day": ("SATURN", "MOON", "ASC"),   "night": ("MOON", "SATURN", "ASC")},
    "Sraddha":        {"day": ("VENUS", "MERCURY", "ASC"), "night": ("MERCURY", "VENUS", "ASC")},
    "Preeti":         {"day": ("VENUS", "MOON", "ASC"),    "night": ("MOON", "VENUS", "ASC")},
    "Bala":           {"day": ("MARS", "MOON", "ASC"),     "night": ("MOON", "MARS", "ASC")},
    "Tanu":           {"day": ("ASC", "MOON", "ASC"),      "night": ("MOON", "ASC", "ASC")},
    "Jadya":          {"day": ("MARS", "MERCURY", "ASC"),  "night": ("MERCURY", "MARS", "ASC")},
    "Paniya_Patana":  {"day": ("CAN15", "SATURN", "ASC"), "night": ("SATURN", "CAN15", "ASC")},
    "Shaurya":        {"day": ("MARS", "SATURN", "ASC"),   "night": ("SATURN", "MARS", "ASC")},
    "Upaya":          {"day": ("JUPITER", "MERCURY", "ASC"),"night": ("MERCURY", "JUPITER", "ASC")},
    "Guru_Saham":     {"day": ("SUN", "JUPITER", "ASC"),   "night": ("JUPITER", "SUN", "ASC")},
    "Ambu_Patha":     {"day": ("CAN15", "MARS", "ASC"),    "night": ("MARS", "CAN15", "ASC")},
    "Dharma":         {"day": ("MOON", "MERCURY", "ASC"),  "night": ("MERCURY", "MOON", "ASC")},
    "Karma_Siddhi":   {"day": ("SUN", "MERCURY", "ASC"),   "night": ("MERCURY", "SUN", "ASC")},
}


def compute_extended_saham(
    name: str,
    planet_lons: Dict[str, float],
    asc_lon: float,
    punya_lon: float,
    is_day: bool,
    house_cusps: Optional[Dict[str, float]] = None,
    asc_lord_lon: Optional[float] = None,
) -> Optional[float]:
    """
    Compute a single extended Saham longitude.

    Special keys: PUNYA, ASC, ASCL, H2C, H2L, H8C, H9C, H9L, CAN15=Cancer 15°=105°

    Returns longitude (0-360) or None.
    """
    formula = EXTENDED_SAHAMS.get(name, {}).get("day" if is_day else "night")
    if not formula:
        return None

    def resolve(key: str) -> Optional[float]:
        if key == "ASC":
            return asc_lon
        if key == "PUNYA":
            return punya_lon
        if key == "ASCL":
            return asc_lord_lon if asc_lord_lon is not None else asc_lon
        if key == "CAN15":
            return 105.0  # Cancer 15° = 90° + 15° = 105°
        if key.startswith("H") and house_cusps:
            return house_cusps.get(key, None)
        return planet_lons.get(key, None)

    a = resolve(formula[0])
    b = resolve(formula[1])
    c = resolve(formula[2])
    if a is None or b is None or c is None:
        return None

    return (a - b + c) % 360.0


# ═══════════════════════════════════════════════════════════════
# 6. 16 TAJIKA YOGA DEFINITIONS (Full Reference Array)
# ═══════════════════════════════════════════════════════════════

TAJIKA_YOGA_DEFINITIONS = [
    {"index": 1,  "name": "Ikkaval",      "quality": "POSITIVE",
     "rule": "All 7 planets in Kendra (1,4,7,10) and Panaphara (2,5,8,11) houses",
     "effect": "Immense gains, rise in status, massive wealth, overall good luck"},
    {"index": 2,  "name": "Induvara",     "quality": "NEGATIVE",
     "rule": "All 7 planets in Apoklima (3,6,9,12) houses",
     "effect": "Misfortune, failure, loss of status, sickness, deep disappointments"},
    {"index": 3,  "name": "Ithasala",     "quality": "POSITIVE",
     "rule": "Faster planet behind slower planet, both in mutual aspect, degrees overlap within combined orb",
     "effect": "Successful fulfillment and physical manifestation of desired event"},
    {"index": 4,  "name": "Easarapha",    "quality": "NEGATIVE",
     "rule": "Faster planet ahead of slower by 1°+, moving out of orb (separating)",
     "effect": "Failure, missed opportunities, moving away from success"},
    {"index": 5,  "name": "Nakta",        "quality": "POSITIVE",
     "rule": "No mutual aspect between two planets, but faster third planet between them aspects both",
     "effect": "Success through third party intervention (messenger/junior)"},
    {"index": 6,  "name": "Yamaya",       "quality": "POSITIVE",
     "rule": "No mutual aspect between two planets, but slower third planet between them aspects both",
     "effect": "Success through older/senior mediator"},
    {"index": 7,  "name": "Manau",        "quality": "NEGATIVE",
     "rule": "Two planets in Ithasala orb but malefic (Mars/Saturn) located exactly between their degrees",
     "effect": "Success violently destroyed at last minute by external enemy"},
    {"index": 8,  "name": "Kamboola",     "quality": "POSITIVE",
     "rule": "Ithasala between ASC lord and House lord + Moon also in Ithasala with either",
     "effect": "Moon catalyzes guaranteed success, joy, smooth execution"},
    {"index": 9,  "name": "Gairi-Kamboola","quality": "NEUTRAL",
     "rule": "Like Kamboola but Moon is debilitated/combust/afflicted",
     "effect": "Event happens but brings sorrow, stress, or pyrrhic victory"},
    {"index": 10, "name": "Khallasara",   "quality": "NEGATIVE",
     "rule": "ASC lord and House lord void of course — no Ithasala with Moon or any planet",
     "effect": "Complete stagnation, severe lack of energy, absolute failure"},
    {"index": 11, "name": "Rudda",        "quality": "NEGATIVE",
     "rule": "Ithasala forming but faster applying planet is combust/retrograde/afflicted",
     "effect": "Endeavor obstructed or rejected right before completion"},
    {"index": 12, "name": "Duhphali-Kuttha","quality": "NEGATIVE",
     "rule": "Slow planet exalted/own sign, but faster planet approaching is debilitated/enemy sign",
     "effect": "Despite good foundations, execution flawed leading to failure"},
    {"index": 13, "name": "Duthotha-Davira","quality": "POSITIVE",
     "rule": "Both planets weak/afflicted, but one forms secondary Ithasala with strong third planet",
     "effect": "Doomed situation miraculously rescued by powerful external benefactor"},
    {"index": 14, "name": "Tambira",      "quality": "POSITIVE",
     "rule": "Faster planet at 29°+ about to enter next sign to form Ithasala with slower planet",
     "effect": "Delayed success at major phase change or relocation"},
    {"index": 15, "name": "Kuttha",       "quality": "POSITIVE",
     "rule": "ASC aspected by planet in Kendra/Panaphara that is in own/exalted sign",
     "effect": "Immense personal power, protection, elevation, fulfillment"},
    {"index": 16, "name": "Durupha",      "quality": "NEGATIVE",
     "rule": "Planet in 6/8/12 debilitated/combust forms Ithasala with similarly afflicted planet",
     "effect": "Massive disaster, total ruin, severe health crises, imprisonment"},
]

# Tajika Deeptamshas (orbs of influence)
TAJIKA_DEEPTAMSHA = {
    "SUN": 15.0, "MOON": 12.0, "MARS": 8.0,
    "MERCURY": 7.0, "JUPITER": 9.0, "VENUS": 7.0, "SATURN": 9.0,
}

# Speed hierarchy (fastest to slowest)
TAJIKA_SPEED_ORDER = ["MOON", "MERCURY", "VENUS", "SUN", "MARS", "JUPITER", "SATURN"]


# ═══════════════════════════════════════════════════════════════
# 7. D60 EVEN-SIGN TABLE (Reversed + Polarity-Flipped)
# ═══════════════════════════════════════════════════════════════

# Even signs reverse the order AND flip benefic↔malefic
D60_EVEN_SIGN_TABLE = [
    # idx  Name              Nature for EVEN signs
    (1,  "Chandrarekha",   "BENEFIC"),
    (2,  "Bhramana",       "MALEFIC"),
    (3,  "Payodhi",        "BENEFIC"),
    (4,  "Sudha",          "MALEFIC"),
    (5,  "Atisheetala",    "BENEFIC"),
    (6,  "Krura",          "BENEFIC"),
    (7,  "Soumya",         "MALEFIC"),
    (8,  "Nirmala",        "MALEFIC"),
    (9,  "Dandayudh",      "BENEFIC"),
    (10, "Kalagni",        "BENEFIC"),
    (11, "Praveena",       "MALEFIC"),
    (12, "Indumukh",       "MALEFIC"),
    (13, "Drinshtakaral",  "BENEFIC"),
    (14, "Sheetala",       "MALEFIC"),
    (15, "Komala",         "MALEFIC"),
    (16, "Soumya",         "MALEFIC"),
    (17, "Kaal",           "BENEFIC"),
    (18, "Utpaat",         "BENEFIC"),
    (19, "Vanshakshaya",   "BENEFIC"),
    (20, "Kulnash",        "BENEFIC"),
    (21, "Vishdagdha",     "BENEFIC"),
    (22, "Purnachandra",   "BENEFIC"),
    (23, "Amrita",         "MALEFIC"),
    (24, "Sudha",          "MALEFIC"),
    (25, "Kantaka",        "BENEFIC"),
    (26, "Yama",           "BENEFIC"),
    (27, "Ghora",          "BENEFIC"),
    (28, "Davagni",        "BENEFIC"),
    (29, "Kaal",           "BENEFIC"),
    (30, "Mrityu",         "BENEFIC"),
    (31, "Gulika",         "BENEFIC"),
    (32, "Kamlakara",      "MALEFIC"),
    (33, "Kshitish",       "MALEFIC"),
    (34, "Kalinash",       "MALEFIC"),
    (35, "Ardra",          "BENEFIC"),
    (36, "Deva",           "MALEFIC"),
    (37, "Mahesh",         "BENEFIC"),
    (38, "Vishnu",         "MALEFIC"),
    (39, "Brahma",         "MALEFIC"),
    (40, "Heramb",         "MALEFIC"),
    (41, "Komala",         "MALEFIC"),
    (42, "Mridu",          "MALEFIC"),
    (43, "Indu",           "MALEFIC"),
    (44, "Amrit",          "MALEFIC"),
    (45, "Sarp",           "BENEFIC"),
    (46, "Kaal",           "BENEFIC"),
    (47, "Marut",          "MALEFIC"),
    (48, "Apampati",       "MALEFIC"),
    (49, "Purish",         "MALEFIC"),
    (50, "Maya",           "BENEFIC"),
    (51, "Agni",           "BENEFIC"),
    (52, "Garala",         "BENEFIC"),
    (53, "Kulaghna",       "BENEFIC"),
    (54, "Bhrasta",        "BENEFIC"),
    (55, "Kinnara",        "MALEFIC"),
    (56, "Yaksha",         "MALEFIC"),
    (57, "Kubera",         "MALEFIC"),
    (58, "Deva",           "MALEFIC"),
    (59, "Rakshasa",       "BENEFIC"),
    (60, "Ghora",          "BENEFIC"),
]


def get_d60_even_sign_entry(segment_index: int) -> Dict[str, Any]:
    """
    Get D60 entry for an even sign (1-60).
    Even signs use reversed order and flipped polarity.
    """
    if 1 <= segment_index <= 60:
        entry = D60_EVEN_SIGN_TABLE[segment_index - 1]
        return {"index": entry[0], "name": entry[1], "nature": entry[2]}
    return {"index": segment_index, "name": "UNKNOWN", "nature": "NEUTRAL"}


# ═══════════════════════════════════════════════════════════════
# COMBINED ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def compute_all_compatibility(
    bride_nak: int, groom_nak: int,
    bride_sign: int, groom_sign: int,
    bride_deg: float = 15.0, groom_deg: float = 15.0,
) -> Dict[str, Any]:
    """
    Compute Yoni + Vashya + Bhakoot compatibility scores.

    Returns combined dict with individual scores and total.
    """
    yoni = get_yoni_score(bride_nak, groom_nak)
    vashya = get_vashya_score(bride_sign, bride_deg, groom_sign, groom_deg)
    bhakoot = get_bhakoot_score(bride_sign, groom_sign)

    total = yoni["score"] + vashya["score"] + bhakoot["effective_score"]
    max_total = 4 + 2 + 7  # 13

    return {
        "yoni_koota": yoni,
        "vashya_koota": vashya,
        "bhakoot_koota": bhakoot,
        "total_score": total,
        "max_score": max_total,
        "percentage": round(total / max_total * 100, 1),
    }
