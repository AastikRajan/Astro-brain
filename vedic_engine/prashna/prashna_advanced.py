"""
Advanced Prashna Shastra — Extended Horary Systems.

Implements:
  1. Ashtamangala Enhanced (108-cell board, remainder→planet, Tambula math)
  2. Aksharachakra (phoneme-to-sign mapping)
  3. Nimitta Shastra (direction→house, omen classification, Shakuna)
  4. Prashna Timing (speaking/mute signs, timing multipliers, fructification)
  5. Trisphutam (Lagna+Moon+Gulika vitality index, zone interpretation)

Reference: Prashna Marga (Kerala), Prashna Tantra, Tajika Neelakanthi.
"""
from __future__ import annotations
from typing import Dict, Any, Optional, List, Tuple


# ═══════════════════════════════════════════════════════════════
# 1. ASHTAMANGALA ENHANCED
# ═══════════════════════════════════════════════════════════════

# Remainder → Ruling Planet mapping (after modulo-8)
ASHTAMANGALA_PLANETS = {
    1: {"planet": "SUN",     "quality": "ODD_FAVORABLE",   "domain": "Authority, soul, vitality, father"},
    2: {"planet": "MARS",    "quality": "EVEN_UNFAVORABLE", "domain": "Conflict, injury, siblings, surgery"},
    3: {"planet": "JUPITER", "quality": "ODD_FAVORABLE",   "domain": "Wisdom, expansion, children, divinity"},
    4: {"planet": "MERCURY", "quality": "EVEN_UNFAVORABLE", "domain": "Logic, speech, commerce, blocks"},
    5: {"planet": "VENUS",   "quality": "ODD_FAVORABLE",   "domain": "Harmony, luxury, marriage, emotion"},
    6: {"planet": "SATURN",  "quality": "EVEN_UNFAVORABLE", "domain": "Discipline, suffering, delays, karma"},
    7: {"planet": "MOON",    "quality": "ODD_FAVORABLE",   "domain": "Mind, mother, nurturing, fluctuation"},
    8: {"planet": "RAHU",    "quality": "EVEN_UNFAVORABLE", "domain": "Illusions, shocks, foreign influences"},
}

# 108-cell board: House → Cell range → Temporal domain
ASHTAMANGALA_108_BOARD = {
    "PAST":    {"houses": [1, 2, 3, 4],   "cells": (1, 36),  "description": "Ancestral influences, prarabdha karma, past-life origins"},
    "PRESENT": {"houses": [5, 6, 7, 8],   "cells": (37, 72), "description": "Current agency, immediate obstacles, present health"},
    "FUTURE":  {"houses": [9, 10, 11, 12], "cells": (73, 108),"description": "Next birth, spiritual progression, moksha potential"},
}


def compute_ashtamangala_enhanced(
    pile_left: int,
    pile_center: int,
    pile_right: int,
) -> Dict[str, Any]:
    """
    Enhanced Ashtamangala with full planet mapping and trend analysis.

    Args:
        pile_left:   Count of shells in left pile (Past)
        pile_center: Count of shells in center pile (Present)
        pile_right:  Count of shells in right pile (Future)

    Returns:
        Full diagnosis with planet rulers, quality, and trend.
    """
    def mod8(n: int) -> int:
        r = n % 8
        return 8 if r == 0 else r

    left_r = mod8(pile_left)
    center_r = mod8(pile_center)
    right_r = mod8(pile_right)

    left_p = ASHTAMANGALA_PLANETS[left_r]
    center_p = ASHTAMANGALA_PLANETS[center_r]
    right_p = ASHTAMANGALA_PLANETS[right_r]

    # Odd=favorable, Even=unfavorable
    score_past = 1 if left_r % 2 == 1 else -1
    score_present = 1 if center_r % 2 == 1 else -1
    score_future = 1 if right_r % 2 == 1 else -1

    # Ascending/Descending trend
    sequence = [left_r, center_r, right_r]
    if sequence[0] < sequence[1] < sequence[2]:
        trend = "ASCENDING_IMPROVEMENT"
    elif sequence[0] > sequence[1] > sequence[2]:
        trend = "DESCENDING_DECLINE"
    elif sequence == sorted(sequence):
        trend = "ASCENDING_PARTIAL"
    else:
        trend = "MIXED"

    overall_score = score_past + score_present + score_future

    return {
        "piles": {"left": pile_left, "center": pile_center, "right": pile_right},
        "remainders": {"past": left_r, "present": center_r, "future": right_r},
        "planets": {
            "past": left_p,
            "present": center_p,
            "future": right_p,
        },
        "trend": trend,
        "overall_score": overall_score,
        "overall_quality": "FAVORABLE" if overall_score > 0 else ("UNFAVORABLE" if overall_score < 0 else "MIXED"),
        "board_zones": ASHTAMANGALA_108_BOARD,
    }


def compute_tambula_number(betel_leaf_count: int) -> Dict[str, Any]:
    """
    Tambula (betel leaf) math for Ashtamangala cross-verification.

    Formula: remainder = betel_leaf_count mod 7
    If remainder == 0, use 7.
    Remainder 1-7 → planetary reference for Arudha verification.

    Args:
        betel_leaf_count: Number of betel leaves provided by querent.

    Returns:
        Dict with remainder and corresponding planet.
    """
    TAMBULA_PLANETS = {
        1: "SUN", 2: "MOON", 3: "MARS",
        4: "MERCURY", 5: "JUPITER", 6: "VENUS", 7: "SATURN",
    }
    r = betel_leaf_count % 7
    if r == 0:
        r = 7
    return {
        "betel_count": betel_leaf_count,
        "remainder": r,
        "planet": TAMBULA_PLANETS[r],
        "note": f"Tambula planet {TAMBULA_PLANETS[r]} cross-verifies the Arudha",
    }


def cell_to_temporal_domain(cell_number: int) -> str:
    """Map D-108 cell number (1-108) to temporal domain."""
    if 1 <= cell_number <= 36:
        return "PAST"
    elif 37 <= cell_number <= 72:
        return "PRESENT"
    elif 73 <= cell_number <= 108:
        return "FUTURE"
    return "UNKNOWN"


def check_final_birth(atmakaraka_d108_house: int, atmakaraka_dignity: str) -> Dict[str, Any]:
    """
    Check if querent is in final birth per D-108 board.

    If Atmakaraka is in 12th house of D-108 with strength (own sign/exalted),
    it signifies final incarnation.
    """
    is_12th = (atmakaraka_d108_house == 12)
    strong = atmakaraka_dignity in ("OWN_SIGN", "EXALTED", "MULATRIKONA")
    final_birth = is_12th and strong
    return {
        "atmakaraka_d108_house": atmakaraka_d108_house,
        "dignity": atmakaraka_dignity,
        "final_birth_indicated": final_birth,
        "note": "Final birth indicated — Atmakaraka strong in D-108 12th house" if final_birth else "Not final birth",
    }


# ═══════════════════════════════════════════════════════════════
# 2. AKSHARACHAKRA — Phoneme-to-Sign Mapping
# ═══════════════════════════════════════════════════════════════

# Phonetic category → zodiac sign index (0-based)
# Following Prashna Marga / Kerala tradition
AKSHARACHAKRA = {
    "SVARA":    {"sign_index": 0,  "sign": "ARIES",       "phonemes": "a, ā, i, ī, u, ū, ṛ, ṝ, ḷ, e, ai, o, au",      "category": "Vowels (Throat/Head)"},
    "KA_VARGA": {"sign_index": 2,  "sign": "GEMINI",      "phonemes": "ka, kha, ga, gha, ṅa",                             "category": "Guttural"},
    "CA_VARGA": {"sign_index": 3,  "sign": "CANCER",      "phonemes": "ca, cha, ja, jha, ña",                              "category": "Palatal"},
    "TA_VARGA_CEREBRAL": {"sign_index": 4,  "sign": "LEO",        "phonemes": "ṭa, ṭha, ḍa, ḍha, ṇa",                     "category": "Cerebral (Retroflex)"},
    "TA_VARGA_DENTAL":   {"sign_index": 5,  "sign": "VIRGO",      "phonemes": "ta, tha, da, dha, na",                       "category": "Dental"},
    "PA_VARGA": {"sign_index": 6,  "sign": "LIBRA",       "phonemes": "pa, pha, ba, bha, ma",                              "category": "Labial"},
    "YA_VARGA": {"sign_index": 7,  "sign": "SCORPIO",     "phonemes": "ya, ra, la, va",                                    "category": "Semivowel"},
    "SA_VARGA": {"sign_index": 9,  "sign": "CAPRICORN",   "phonemes": "śa, ṣa, sa, ha",                                   "category": "Sibilant/Aspirate"},
}

# Latin / Romanized phoneme lookup (lowercase first letter → category)
_PHONEME_MAP = {}
for _cat, _info in AKSHARACHAKRA.items():
    for _ph in _info["phonemes"].replace(",", "").split():
        _clean = _ph.strip().lower().replace("ā", "a").replace("ī", "i").replace("ū", "u")
        _clean = _clean.replace("ṛ", "r").replace("ṝ", "r").replace("ḷ", "l")
        _clean = _clean.replace("ṭ", "t").replace("ṭh", "th").replace("ḍ", "d")
        _clean = _clean.replace("ḍh", "dh").replace("ṇ", "n").replace("ñ", "ny")
        _clean = _clean.replace("ṅ", "ng").replace("ś", "sh").replace("ṣ", "sh")
        if _clean:
            _PHONEME_MAP[_clean] = _cat

# Simple English letter → category mapping for practical use
_ENGLISH_LETTER_MAP = {
    # Vowels → Aries
    'a': "SVARA", 'e': "SVARA", 'i': "SVARA", 'o': "SVARA", 'u': "SVARA",
    # K/G → Gemini
    'k': "KA_VARGA", 'g': "KA_VARGA",
    # C/J → Cancer
    'c': "CA_VARGA", 'j': "CA_VARGA",
    # T/D (retroflex) → Leo (use capital or context)
    # T/D (dental) → Virgo (default for t/d)
    't': "TA_VARGA_DENTAL", 'd': "TA_VARGA_DENTAL",
    'n': "TA_VARGA_DENTAL",
    # P/B/M → Libra
    'p': "PA_VARGA", 'b': "PA_VARGA", 'f': "PA_VARGA", 'm': "PA_VARGA",
    # Y/R/L/V/W → Scorpio
    'y': "YA_VARGA", 'r': "YA_VARGA", 'l': "YA_VARGA", 'v': "YA_VARGA", 'w': "YA_VARGA",
    # S/H → Capricorn
    's': "SA_VARGA", 'h': "SA_VARGA", 'z': "SA_VARGA",
}


def get_aksharachakra_sign(first_syllable: str) -> Dict[str, Any]:
    """
    Determine Arudha Lagna from first syllable of question.

    Args:
        first_syllable: The first syllable/letter uttered by the querent.

    Returns:
        Dict with matching sign, category, and phonetic details.
    """
    cleaned = first_syllable.strip().lower()
    if not cleaned:
        return {"sign_index": -1, "sign": "UNKNOWN", "category": "EMPTY", "matched": False}

    # Try exact phoneme match first
    if cleaned in _PHONEME_MAP:
        cat = _PHONEME_MAP[cleaned]
        info = AKSHARACHAKRA[cat]
        return {**info, "matched": True, "input": first_syllable, "match_type": "exact_phoneme"}

    # Fall back to first English letter
    first_char = cleaned[0]
    if first_char in _ENGLISH_LETTER_MAP:
        cat = _ENGLISH_LETTER_MAP[first_char]
        info = AKSHARACHAKRA[cat]
        return {**info, "matched": True, "input": first_syllable, "match_type": "english_letter"}

    return {"sign_index": -1, "sign": "UNKNOWN", "category": "UNMATCHED", "matched": False, "input": first_syllable}


def check_arudha_lagna_harmony(phonetic_sign_index: int, udaya_lagna_index: int) -> Dict[str, Any]:
    """
    Check if phonetic Arudha and Udaya Lagna are harmonious.

    Kendra/Trikona relationship = sincere question, favorable.
    Dusthana = hidden agenda or inauspicious question.
    """
    offset = (phonetic_sign_index - udaya_lagna_index) % 12
    if offset in (0, 3, 6, 9):
        relation = "KENDRA"
        quality = "SINCERE_FAVORABLE"
    elif offset in (4, 8):
        relation = "TRIKONA"
        quality = "SINCERE_FAVORABLE"
    elif offset in (5, 7, 11):
        relation = "DUSTHANA"
        quality = "HIDDEN_AGENDA"
    else:
        relation = "NEUTRAL"
        quality = "MODERATE"

    return {
        "phonetic_sign": phonetic_sign_index,
        "udaya_lagna": udaya_lagna_index,
        "offset": offset,
        "relation": relation,
        "quality": quality,
    }


# ═══════════════════════════════════════════════════════════════
# 3. NIMITTA SHASTRA — Omen & Direction Systems
# ═══════════════════════════════════════════════════════════════

# Direction → activated signs and house domains
DIRECTION_HOUSE_MAP = {
    "EAST":       {"signs": [0, 1],  "houses": [1],     "domain": "Self, vitality"},
    "SOUTH_EAST": {"signs": [2],     "houses": [3],     "domain": "Communication, initiative"},
    "SOUTH":      {"signs": [3, 4],  "houses": [4, 5],  "domain": "Home, status"},
    "SOUTH_WEST": {"signs": [5],     "houses": [6],     "domain": "Debts, obstacles"},
    "WEST":       {"signs": [6, 7],  "houses": [7, 8],  "domain": "Partnerships, transformation"},
    "NORTH_WEST": {"signs": [8],     "houses": [9],     "domain": "Foreign travel, wisdom"},
    "NORTH":      {"signs": [9, 10], "houses": [10, 11],"domain": "Career, gains"},
    "NORTH_EAST": {"signs": [11],    "houses": [12],    "domain": "Loss, isolation"},
}

# Omen classification
OMEN_TYPES = {
    "SHARIRIKA": {
        "name": "Bodily Omens",
        "examples": {
            "LEFT_EYE_TWITCH_FEMALE":  {"quality": "AUSPICIOUS", "note": "Success indicated"},
            "RIGHT_EYE_TWITCH_FEMALE": {"quality": "INAUSPICIOUS", "note": "Delay or failure"},
            "SINGLE_SNEEZE":           {"quality": "WARNING", "note": "Delay the task"},
            "DOUBLE_SNEEZE":           {"quality": "CLEARING", "note": "Path cleared"},
            "RIGHT_HAND_ITCH":         {"quality": "AUSPICIOUS", "note": "Incoming wealth"},
            "LEFT_HAND_ITCH":          {"quality": "INAUSPICIOUS", "note": "Expenses incoming"},
        },
    },
    "DRISHYA": {
        "name": "Visual / Object Omens",
        "examples": {
            "BROKEN_GLASS":        {"quality": "RELEASE", "note": "Breaking of evil eye, negative cycle ends"},
            "GHEE_FLAME_SOUTH":    {"quality": "INAUSPICIOUS", "note": "Yamakantaka influence, destruction"},
            "GHEE_FLAME_STEADY":   {"quality": "AUSPICIOUS", "note": "Stability and protection"},
            "BLOOMING_FLOWERS":    {"quality": "AUSPICIOUS", "note": "Jupiter protection, growth"},
        },
    },
    "SHAKUNA": {
        "name": "Bird/Animal Omens",
        "examples": {
            "CROW_RIGHT_SHOULDER": {"planet": "SUN_JUPITER", "quality": "AUSPICIOUS", "note": "Success in travel/career"},
            "CAT_LEFT_TO_RIGHT":   {"planet": "SATURN",      "quality": "INAUSPICIOUS", "note": "Obstruction, delays, failure"},
            "DOG_BARKING_INCESSANT":{"planet": "KETU_MARS",  "quality": "INAUSPICIOUS", "note": "Illness or litigation"},
            "SEEING_SCHOLAR":      {"planet": "JUPITER_VENUS","quality": "AUSPICIOUS", "note": "Authority support, divine grace"},
            "FUNERAL_PROCESSION":  {"planet": "SATURN_YAMA", "quality": "INAUSPICIOUS", "note": "End of cycle, non-recovery if sick"},
            "FALLING_OBJECTS":     {"planet": "RAHU",        "quality": "INAUSPICIOUS", "note": "Sudden shocks, betrayal"},
        },
    },
}


def classify_nimitta(direction_faced: str, omens_observed: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Classify Nimitta (environmental omens) for a Prashna session.

    Args:
        direction_faced: One of EAST, SOUTH_EAST, SOUTH, etc.
        omens_observed: List of omen keys from OMEN_TYPES examples.

    Returns:
        Nimitta classification with direction activation and omen analysis.
    """
    dir_info = DIRECTION_HOUSE_MAP.get(direction_faced.upper(), {})

    omen_results = []
    auspicious_count = 0
    inauspicious_count = 0

    if omens_observed:
        for omen_key in omens_observed:
            found = False
            for otype, odata in OMEN_TYPES.items():
                if omen_key.upper() in odata["examples"]:
                    entry = odata["examples"][omen_key.upper()]
                    omen_results.append({
                        "omen": omen_key,
                        "type": otype,
                        **entry,
                    })
                    if entry["quality"] in ("AUSPICIOUS", "RELEASE", "CLEARING"):
                        auspicious_count += 1
                    elif entry["quality"] in ("INAUSPICIOUS", "WARNING"):
                        inauspicious_count += 1
                    found = True
                    break
            if not found:
                omen_results.append({"omen": omen_key, "type": "UNKNOWN", "quality": "UNCLASSIFIED"})

    # Decision tree: multiple omens same direction = certain
    consensus = None
    if auspicious_count > 1 and inauspicious_count == 0:
        consensus = "CERTAIN_FAVORABLE"
    elif inauspicious_count > 1 and auspicious_count == 0:
        consensus = "CERTAIN_UNFAVORABLE"
    elif auspicious_count > 0 and inauspicious_count > 0:
        consensus = "CONFLICTED"
    elif auspicious_count == 1:
        consensus = "MILD_FAVORABLE"
    elif inauspicious_count == 1:
        consensus = "MILD_UNFAVORABLE"
    else:
        consensus = "NEUTRAL"

    return {
        "direction_faced": direction_faced.upper(),
        "direction_info": dir_info,
        "omens_analyzed": omen_results,
        "auspicious_count": auspicious_count,
        "inauspicious_count": inauspicious_count,
        "consensus": consensus,
    }


# ═══════════════════════════════════════════════════════════════
# 4. PRASHNA TIMING — Speaking/Mute Signs & Multipliers
# ═══════════════════════════════════════════════════════════════

# Speaking (voice) signs → rapid manifestation
SPEAKING_SIGNS = {2, 6, 10}    # Gemini, Libra, Aquarius (0-indexed)
SECONDARY_SPEAKING = {5, 8}     # Virgo, Sagittarius
# Mute signs → delays (Cancer, Scorpio, Pisces)
MUTE_SIGNS = {3, 7, 11}

# Planet timing units
TIMING_MULTIPLIERS = {
    "SUN":     {"standard": "AYANA",     "standard_days": 182.5,  "advanced_years": 70},
    "MOON":    {"standard": "MUHURTHA",  "standard_days": 0.033,  "advanced_years": 1},
    "MARS":    {"standard": "VARA",      "standard_days": 7,      "advanced_years": 2},
    "MERCURY": {"standard": "RTU",       "standard_days": 60,     "advanced_years": 9},
    "JUPITER": {"standard": "MASA",      "standard_days": 30,     "advanced_years": 18},
    "VENUS":   {"standard": "PAKSHA",    "standard_days": 14,     "advanced_years": 20},
    "SATURN":  {"standard": "VARSHA",    "standard_days": 365.25, "advanced_years": 50},
}


def compute_prashna_timing(
    lagna_navamsa_lord: str,
    navamsas_traversed: int,
    significator_sign: int,
    significator_house: int,
) -> Dict[str, Any]:
    """
    Calculate Prashna fructification timing.

    Algorithm:
    1. Find timing unit from Lagna Navamsa lord.
    2. Multiply by navamsas traversed.
    3. Adjust for visible/invisible hemisphere.
    4. Adjust for speaking/mute signs.

    Args:
        lagna_navamsa_lord: Planet ruling lagna's navamsa (e.g., "JUPITER")
        navamsas_traversed: Number of navamsas lord has traversed in current sign (1-9)
        significator_sign:  Sign index (0-11) of the signifying planet
        significator_house: House (1-12) of the signifying planet

    Returns:
        Timing estimate dict.
    """
    planet_key = lagna_navamsa_lord.upper()
    tm = TIMING_MULTIPLIERS.get(planet_key)
    if not tm:
        return {"error": f"Unknown planet: {planet_key}", "timing_days": None}

    base_days = tm["standard_days"] * navamsas_traversed

    # Hemisphere rule: houses 7-12 = visible (first half), 1-6 = invisible (latter half)
    if 7 <= significator_house <= 12:
        hemisphere = "VISIBLE"
        adjusted_days = base_days * 0.5
    else:
        hemisphere = "INVISIBLE"
        adjusted_days = base_days * 1.5

    # Mute / Speaking adjustment
    sign_type = "SPEAKING" if significator_sign in SPEAKING_SIGNS else (
        "SECONDARY_SPEAKING" if significator_sign in SECONDARY_SPEAKING else (
            "MUTE" if significator_sign in MUTE_SIGNS else "NEUTRAL"
        )
    )
    if sign_type == "SPEAKING":
        adjusted_days *= 0.75  # Faster
    elif sign_type == "SECONDARY_SPEAKING":
        adjusted_days *= 0.85
    elif sign_type == "MUTE":
        adjusted_days *= 2.0  # Doubled (delay)

    return {
        "lagna_navamsa_lord": planet_key,
        "navamsas_traversed": navamsas_traversed,
        "timing_unit": tm["standard"],
        "base_days": round(base_days, 2),
        "hemisphere": hemisphere,
        "sign_type": sign_type,
        "adjusted_days": round(adjusted_days, 2),
        "advanced_years_per_unit": tm["advanced_years"],
        "note": f"Event in ~{round(adjusted_days)} days ({hemisphere} hemisphere, {sign_type} sign)",
    }


# ═══════════════════════════════════════════════════════════════
# 5. TRISPHUTAM — Vitality & Honesty Index
# ═══════════════════════════════════════════════════════════════

# Trisphutam zone classification
TRISPHUTA_ZONES = {
    # Sign index → zone
    0: "SRISHTI",  1: "SRISHTI",  2: "SRISHTI",  3: "SRISHTI",   # Ari,Tau,Gem,Can
    4: "STHITI",   5: "STHITI",   6: "STHITI",   7: "STHITI",    # Leo,Vir,Lib,Sco
    8: "SAMHARA",  9: "SAMHARA",  10: "SAMHARA", 11: "SAMHARA",  # Sag,Cap,Aqu,Pis
}

ZONE_MEANINGS = {
    "SRISHTI":  {"name": "Creation",    "health": "Vitality, fast recovery, expansion of life force"},
    "STHITI":   {"name": "Sustenance",  "health": "Stable condition, slow recovery, protection from evil"},
    "SAMHARA":  {"name": "Destruction", "health": "Deterioration, chronic suffering, high karmic debt"},
}

# Sign quality for Rasi interpretation
SIGN_QUALITY = {
    0: "MOVABLE",  1: "FIXED",    2: "DUAL",
    3: "MOVABLE",  4: "FIXED",    5: "DUAL",
    6: "MOVABLE",  7: "FIXED",    8: "DUAL",
    9: "MOVABLE",  10: "FIXED",   11: "DUAL",
}

# Nakshatra lords for disease mapping (27 nakshatras)
NAK_LORDS = ["KETU", "VENUS", "SUN", "MOON", "MARS", "RAHU", "JUPITER", "SATURN", "MERCURY"] * 3

NAK_DISEASE_MAP = {
    "SUN":     "Fever, eye problems, heart issues",
    "MOON":    "Fluid imbalances, mental disturbance, cold",
    "MARS":    "Sores, wounds, blood disorders, surgery",
    "MERCURY": "Speech/mental blocks, skin rashes, nerve issues",
    "JUPITER": "Liver, fat-related, diabetes, tumors",
    "VENUS":   "Reproductive, kidney, urinary, STDs",
    "SATURN":  "Chronic pain, joints, slow debilitation",
    "RAHU":    "Mysterious illness, poisoning, foreign disease",
    "KETU":    "Psychosomatic, viral, sudden onset, karmic illness",
}


def compute_trisphutam(
    lagna_lon: float,
    moon_lon: float,
    gulika_lon: float,
) -> Dict[str, Any]:
    """
    Compute Trisphutam = (Lagna + Moon + Gulika) mod 360.

    Diagnostic:
      - Rasi = Present health state
      - Navamsa = Future state
      - Nakshatra lord = disease nature

    Args:
        lagna_lon: Sidereal longitude of Lagna
        moon_lon:  Sidereal longitude of Moon
        gulika_lon: Sidereal longitude of Gulika

    Returns:
        Full Trisphutam analysis.
    """
    total = (lagna_lon + moon_lon + gulika_lon) % 360.0

    rasi_index = int(total / 30) % 12
    degree_in_sign = total % 30
    navamsa_index = int((total % 30) / (30 / 9)) % 12
    nak_index = int(total / (360 / 27)) % 27
    nak_lord = NAK_LORDS[nak_index]

    zone = TRISPHUTA_ZONES[rasi_index]
    zone_info = ZONE_MEANINGS[zone]
    rasi_quality = SIGN_QUALITY[rasi_index]
    navamsa_quality = SIGN_QUALITY[navamsa_index]

    # Rasi interpretation (present)
    if rasi_quality == "DUAL":
        present_state = "DETERIORATING"
    elif rasi_quality == "MOVABLE":
        present_state = "DYNAMIC_RECOVERABLE"
    else:
        present_state = "STABLE_FIXED"

    # Navamsa interpretation (future)
    if navamsa_quality == "MOVABLE":
        future_state = "QUICK_RECOVERY"
    elif navamsa_quality == "FIXED":
        future_state = "PROLONGED_CONDITION"
    else:
        future_state = "UNCERTAIN_FLUCTUATING"

    return {
        "trisphutam_longitude": round(total, 4),
        "rasi_index": rasi_index,
        "degree_in_sign": round(degree_in_sign, 4),
        "navamsa_index": navamsa_index,
        "nakshatra_index": nak_index,
        "nakshatra_lord": nak_lord,
        "zone": zone,
        "zone_name": zone_info["name"],
        "zone_health": zone_info["health"],
        "present_state": present_state,
        "future_state": future_state,
        "disease_indication": NAK_DISEASE_MAP.get(nak_lord, "Unknown"),
        "rasi_quality": rasi_quality,
        "navamsa_quality": navamsa_quality,
        "chart_valid": zone != "SAMHARA",  # Samhara = highly afflicted, chart may be poisoned
        "note": f"Trisphutam at {round(total, 2)}° — Zone: {zone_info['name']} — Present: {present_state}, Future: {future_state}",
    }


def validate_prashna_chart(trisphutam_zone: str, gulika_conjunct_trisphuta: bool = False) -> Dict[str, Any]:
    """
    Validate the honesty/clarity of a Prashna chart via Trisphutam.

    If Trisphutam in Samhara zone AND Gulika conjuncts Trisphuta Rasi,
    the chart is "poisoned" — predictions unreliable.
    """
    poisoned = (trisphutam_zone == "SAMHARA" and gulika_conjunct_trisphuta)
    if poisoned:
        validity = "POISONED"
        note = "Chart is poisoned — Gulika conjunct Trisphuta in Samhara zone. Predictions unreliable."
    elif trisphutam_zone == "SAMHARA":
        validity = "WEAK"
        note = "Trisphutam in Samhara zone — high karmic debt, treat predictions cautiously."
    elif gulika_conjunct_trisphuta:
        validity = "COMPROMISED"
        note = "Gulika conjuncts Trisphuta Rasi — querent may be insincere."
    else:
        validity = "VALID"
        note = "Chart is valid for prediction."

    return {
        "trisphutam_zone": trisphutam_zone,
        "gulika_conjunct": gulika_conjunct_trisphuta,
        "validity": validity,
        "note": note,
    }


# ═══════════════════════════════════════════════════════════════
# COMBINED ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def compute_all_advanced_prashna(
    pile_left: int = 0,
    pile_center: int = 0,
    pile_right: int = 0,
    betel_leaf_count: int = 0,
    first_syllable: str = "",
    udaya_lagna_index: int = -1,
    direction_faced: str = "",
    omens: Optional[List[str]] = None,
    lagna_lon: float = 0.0,
    moon_lon: float = 0.0,
    gulika_lon: float = 0.0,
) -> Dict[str, Any]:
    """
    Combined Advanced Prashna analysis.

    Returns dict with all sub-system results.
    """
    result: Dict[str, Any] = {}

    # Ashtamangala
    if pile_left > 0 or pile_center > 0 or pile_right > 0:
        result["ashtamangala"] = compute_ashtamangala_enhanced(pile_left, pile_center, pile_right)
    if betel_leaf_count > 0:
        result["tambula"] = compute_tambula_number(betel_leaf_count)

    # Aksharachakra
    if first_syllable:
        akshara = get_aksharachakra_sign(first_syllable)
        result["aksharachakra"] = akshara
        if akshara.get("matched") and udaya_lagna_index >= 0:
            result["arudha_harmony"] = check_arudha_lagna_harmony(
                akshara["sign_index"], udaya_lagna_index
            )

    # Nimitta
    if direction_faced:
        result["nimitta"] = classify_nimitta(direction_faced, omens)

    # Trisphutam
    if lagna_lon > 0 or moon_lon > 0 or gulika_lon > 0:
        result["trisphutam"] = compute_trisphutam(lagna_lon, moon_lon, gulika_lon)

    return result
