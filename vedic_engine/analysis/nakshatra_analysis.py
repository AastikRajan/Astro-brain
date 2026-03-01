"""
Nakshatra Analysis Engine — File 2 Integration.

Implements:
1. Extended 27-Nakshatra database (Tatwa, Dosha, Guna, Purpose, Direction, Body Part)
2. 108 Pada syllable lookup (Bija Akshara for naming star computation)
3. Enhanced Tarabala with exact 9-category multipliers
4. Enhanced Chandrabala with severity tiers + 8th-count exception
5. Pushkara Navamsa detection (auspiciousness multiplier 2.0)
6. Pushkara Bhaga detection (auspiciousness multiplier 3.0)
7. Vargottama detection (D1 sign == D9 sign)
8. Dwisaptati Sama Dasha eligibility check (conditional 72-year dasha)
9. Nakshatra transit karmic activation tags

Sources: BPHS, Muhurta Chintamani, Taittiriya Brahmana, Jyotish Pradeepika.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from vedic_engine.data.nakshatra_db import get_nakshatra, get_nakshatra_index, nakshatra_pada, NAKSHATRAS

# ═══════════════════════════════════════════════════════════════════
# SECTION 1: EXTENDED NAKSHATRA ATTRIBUTES
# ═══════════════════════════════════════════════════════════════════

# Extended data: tatwa (element), dosha, guna, nature, purpose, direction, body_part
# Indexed by 0-based nakshatra index (0=Ashwini … 26=Revati)
# Data source: research file Section 1 comprehensive table
NAKSHATRA_EXTENDED: List[Dict] = [
    # 0 Ashwini
    {"tatwa": "Earth",  "dosha": "Vata",  "guna": "Sattvic", "nature": "Swift",
     "purpose": "Dharma", "yoni": "Horse",    "direction": "South", "body_part": "Knees, Top of feet"},
    # 1 Bharani
    {"tatwa": "Earth",  "dosha": "Pitta", "guna": "Rajasic", "nature": "Fierce",
     "purpose": "Artha",  "yoni": "Elephant", "direction": "West",  "body_part": "Head, Bottom of feet"},
    # 2 Krittika
    {"tatwa": "Earth",  "dosha": "Kapha", "guna": "Rajasic", "nature": "Mixed",
     "purpose": "Kama",   "yoni": "Sheep",    "direction": "North", "body_part": "Waist, Hips, Crown"},
    # 3 Rohini
    {"tatwa": "Earth",  "dosha": "Kapha", "guna": "Rajasic", "nature": "Fixed",
     "purpose": "Moksha", "yoni": "Serpent",  "direction": "East",  "body_part": "Legs, Forehead, Ankles"},
    # 4 Mrigashira
    {"tatwa": "Earth",  "dosha": "Pitta", "guna": "Tamasic", "nature": "Soft",
     "purpose": "Moksha", "yoni": "Serpent",  "direction": "South", "body_part": "Eyes, Eyebrows"},
    # 5 Ardra
    {"tatwa": "Water",  "dosha": "Vata",  "guna": "Tamasic", "nature": "Sharp",
     "purpose": "Kama",   "yoni": "Dog",      "direction": "West",  "body_part": "Hair, Front/Back of head"},
    # 6 Punarvasu
    {"tatwa": "Water",  "dosha": "Vata",  "guna": "Sattvic", "nature": "Movable",
     "purpose": "Artha",  "yoni": "Cat",      "direction": "North", "body_part": "Fingers, Nose"},
    # 7 Pushya
    {"tatwa": "Water",  "dosha": "Pitta", "guna": "Tamasic", "nature": "Swift",
     "purpose": "Dharma", "yoni": "Sheep",    "direction": "East",  "body_part": "Mouth, Face, Joints"},
    # 8 Ashlesha
    {"tatwa": "Water",  "dosha": "Kapha", "guna": "Sattvic", "nature": "Sharp",
     "purpose": "Dharma", "yoni": "Cat",      "direction": "South", "body_part": "Nails, Knuckles, Ears"},
    # 9 Magha
    {"tatwa": "Water",  "dosha": "Kapha", "guna": "Tamasic", "nature": "Fierce",
     "purpose": "Artha",  "yoni": "Rat",      "direction": "West",  "body_part": "Nose, Lip, Chin"},
    # 10 Purva Phalguni
    {"tatwa": "Water",  "dosha": "Pitta", "guna": "Rajasic", "nature": "Fierce",
     "purpose": "Kama",   "yoni": "Rat",      "direction": "North", "body_part": "Sexual organs, R-hand"},
    # 11 Uttara Phalguni
    {"tatwa": "Fire",   "dosha": "Vata",  "guna": "Rajasic", "nature": "Fixed",
     "purpose": "Moksha", "yoni": "Cow",      "direction": "East",  "body_part": "Sexual organs, L-hand"},
    # 12 Hasta
    {"tatwa": "Fire",   "dosha": "Vata",  "guna": "Rajasic", "nature": "Swift",
     "purpose": "Moksha", "yoni": "Buffalo",  "direction": "South", "body_part": "Hands"},
    # 13 Chitra
    {"tatwa": "Fire",   "dosha": "Pitta", "guna": "Tamasic", "nature": "Soft",
     "purpose": "Kama",   "yoni": "Tiger",    "direction": "West",  "body_part": "Forehead, Neck"},
    # 14 Swati
    {"tatwa": "Fire",   "dosha": "Kapha", "guna": "Tamasic", "nature": "Movable",
     "purpose": "Artha",  "yoni": "Buffalo",  "direction": "North", "body_part": "Teeth, Chest, Breathing"},
    # 15 Vishakha
    {"tatwa": "Fire",   "dosha": "Kapha", "guna": "Sattvic", "nature": "Mixed",
     "purpose": "Dharma", "yoni": "Tiger",    "direction": "East",  "body_part": "Upper limbs, Breasts"},
    # 16 Anuradha
    {"tatwa": "Fire",   "dosha": "Pitta", "guna": "Tamasic", "nature": "Soft",
     "purpose": "Dharma", "yoni": "Hare",     "direction": "South", "body_part": "Stomach, Womb"},
    # 17 Jyeshtha
    {"tatwa": "Air",    "dosha": "Vata",  "guna": "Sattvic", "nature": "Sharp",
     "purpose": "Artha",  "yoni": "Hare",     "direction": "West",  "body_part": "Tongue, Neck, R-torso"},
    # 18 Mula
    {"tatwa": "Air",    "dosha": "Vata",  "guna": "Tamasic", "nature": "Fierce",
     "purpose": "Kama",   "yoni": "Dog",      "direction": "North", "body_part": "Feet, L-torso, Back"},
    # 19 Purva Ashadha
    {"tatwa": "Air",    "dosha": "Pitta", "guna": "Rajasic", "nature": "Fierce",
     "purpose": "Moksha", "yoni": "Monkey",   "direction": "East",  "body_part": "Both thighs"},
    # 20 Uttara Ashadha
    {"tatwa": "Air",    "dosha": "Kapha", "guna": "Sattvic", "nature": "Fixed",
     "purpose": "Moksha", "yoni": "Mongoose", "direction": "South", "body_part": "Thighs, Waist"},
    # 21 Shravana
    {"tatwa": "Air",    "dosha": "Kapha", "guna": "Rajasic", "nature": "Movable",
     "purpose": "Artha",  "yoni": "Monkey",   "direction": "West",  "body_part": "Ears, Gait, Sex organs"},
    # 22 Dhanishta
    {"tatwa": "Air",    "dosha": "Pitta", "guna": "Tamasic", "nature": "Movable",
     "purpose": "Dharma", "yoni": "Lion",     "direction": "North", "body_part": "Back, Anus"},
    # 23 Shatabhisha
    {"tatwa": "Air",    "dosha": "Vata",  "guna": "Tamasic", "nature": "Movable",
     "purpose": "Dharma", "yoni": "Horse",    "direction": "East",  "body_part": "Chin, Jaw, R-thigh"},
    # 24 Purva Bhadrapada
    {"tatwa": "Ether",  "dosha": "Vata",  "guna": "Sattvic", "nature": "Fierce",
     "purpose": "Artha",  "yoni": "Lion",     "direction": "South", "body_part": "Ribs, L-thigh, Soles"},
    # 25 Uttara Bhadrapada
    {"tatwa": "Ether",  "dosha": "Pitta", "guna": "Tamasic", "nature": "Fixed",
     "purpose": "Kama",   "yoni": "Cow",      "direction": "West",  "body_part": "Sides of legs, Shins"},
    # 26 Revati
    {"tatwa": "Ether",  "dosha": "Kapha", "guna": "Sattvic", "nature": "Soft",
     "purpose": "Moksha", "yoni": "Elephant", "direction": "North", "body_part": "Armpits, Abdomen, Groin"},
]


def get_nakshatra_extended(nak_index: int) -> Dict:
    """Return extended attributes for nakshatra by 0-based index."""
    return NAKSHATRA_EXTENDED[nak_index % 27]


# ═══════════════════════════════════════════════════════════════════
# SECTION 2: 108 PADA SYLLABLE ARRAY (BIJA AKSHARA)
# Source: Research file Section 1 — 108 pada syllable table
# ═══════════════════════════════════════════════════════════════════

# Each nakshatra has 4 padas, each pada a Sanskrit syllable
# Indexed: PADA_SYLLABLES[nak_idx][pada_0based] → syllable string
PADA_SYLLABLES: List[List[str]] = [
    ["Chu", "Che", "Cho", "La"],    # 0 Ashwini
    ["Li",  "Lu",  "Le",  "Lo"],    # 1 Bharani
    ["A",   "I",   "U",   "E"],     # 2 Krittika
    ["O",   "Va",  "Vi",  "Vu"],    # 3 Rohini
    ["Ve",  "Vo",  "Ka",  "Ki"],    # 4 Mrigashira
    ["Ku",  "Gha", "Ng",  "Chha"], # 5 Ardra
    ["Ke",  "Ko",  "Ha",  "Hi"],    # 6 Punarvasu
    ["Hu",  "He",  "Ho",  "Da"],    # 7 Pushya
    ["Di",  "Du",  "De",  "Do"],    # 8 Ashlesha
    ["Ma",  "Mi",  "Mu",  "Me"],    # 9 Magha
    ["Mo",  "Ta",  "Ti",  "Tu"],    # 10 Purva Phalguni
    ["Te",  "To",  "Pa",  "Pi"],    # 11 Uttara Phalguni
    ["Pu",  "Sha", "Na",  "Tha"],   # 12 Hasta
    ["Pe",  "Po",  "Ra",  "Ri"],    # 13 Chitra
    ["Ru",  "Re",  "Ro",  "Ta"],    # 14 Swati
    ["Ti",  "Tu",  "Te",  "To"],    # 15 Vishakha
    ["Na",  "Ni",  "Nu",  "Ne"],    # 16 Anuradha
    ["No",  "Ya",  "Yi",  "Yu"],    # 17 Jyeshtha
    ["Ye",  "Yo",  "Ba",  "Bi"],    # 18 Mula
    ["Bu",  "Dha", "Bha", "Dha"],   # 19 Purva Ashadha
    ["Be",  "Bo",  "Ja",  "Ji"],    # 20 Uttara Ashadha
    ["Ju",  "Je",  "Jo",  "Gha"],   # 21 Shravana
    ["Ga",  "Gi",  "Gu",  "Ge"],    # 22 Dhanishta
    ["Go",  "Sa",  "Si",  "Su"],    # 23 Shatabhisha
    ["Se",  "So",  "Da",  "Di"],    # 24 Purva Bhadrapada
    ["Du",  "Tha", "Jna", "Da"],    # 25 Uttara Bhadrapada
    ["De",  "Do",  "Cha", "Chi"],   # 26 Revati
]


def get_pada_syllable(longitude: float) -> Dict:
    """
    Return pada number (1-4), nakshatra name, and Bija Akshara syllable
    for the given sidereal longitude.
    """
    nak, pada = nakshatra_pada(longitude)
    syllable = PADA_SYLLABLES[nak.index][pada - 1]
    ext = NAKSHATRA_EXTENDED[nak.index]
    return {
        "nakshatra": nak.name,
        "nak_index": nak.index,
        "pada": pada,
        "syllable": syllable,
        "tatwa": ext["tatwa"],
        "dosha": ext["dosha"],
        "purpose": ext["purpose"],
        "body_part": ext["body_part"],
    }


# ═══════════════════════════════════════════════════════════════════
# SECTION 3: ENHANCED TARABALA
# Source: Research file Section 2 — precise 9-category multipliers
# ═══════════════════════════════════════════════════════════════════

# Exact multipliers for Tarabala (1=Janma through 9=Ati-Mitra)
# Score: -1.0 (most negative) to +1.0 (most positive)
TARA_DATA: List[Dict] = [
    {"num": 1, "name": "Janma",       "nature": "negative_neutral", "multiplier":  0.0},
    {"num": 2, "name": "Sampat",      "nature": "positive",         "multiplier":  0.65},
    {"num": 3, "name": "Vipat",       "nature": "negative",         "multiplier": -0.55},
    {"num": 4, "name": "Kshema",      "nature": "positive",         "multiplier":  0.75},
    {"num": 5, "name": "Pratyak",     "nature": "negative",         "multiplier": -0.50},
    {"num": 6, "name": "Sadhana",     "nature": "positive",         "multiplier":  0.70},
    {"num": 7, "name": "Naidhana",    "nature": "highly_negative",  "multiplier": -1.00},
    {"num": 8, "name": "Mitra",       "nature": "positive",         "multiplier":  0.80},
    {"num": 9, "name": "Ati-Mitra",   "nature": "highly_positive",  "multiplier":  1.00},
]


def compute_tarabala_enhanced(
    natal_moon_nak: int,
    transit_moon_nak: int,
) -> Dict:
    """
    Enhanced Tarabala with precise 9-category multipliers.
    Args:
        natal_moon_nak: birth Moon nakshatra index (0-26)
        transit_moon_nak: transit Moon nakshatra index (0-26)
    Returns:
        tara_num, tara_name, nature, multiplier, transit_boost_factor
    """
    diff = (transit_moon_nak - natal_moon_nak) % 27
    tara_idx_0based = diff % 9
    tara_num = tara_idx_0based + 1
    tara = TARA_DATA[tara_idx_0based]

    # Transit boost factor for confidence scoring:  +/- based on multiplier
    # Map multiplier -1.0→+1.0 to a ±0.20 confidence adjustment
    transit_boost = tara["multiplier"] * 0.20

    return {
        "tara_num": tara_num,
        "tara_name": tara["name"],
        "nature": tara["nature"],
        "multiplier": tara["multiplier"],
        "transit_boost_factor": round(transit_boost, 3),
        "is_favorable": tara["multiplier"] > 0,
        "is_highly_negative": tara["nature"] == "highly_negative",
    }


# ═══════════════════════════════════════════════════════════════════
# SECTION 4: ENHANCED CHANDRABALA
# Source: Research file Section 3 — severity tiers + 8th exception
# ═══════════════════════════════════════════════════════════════════

# Chandrabala house quality tiers (1-12 from natal Moon sign)
_CHANDRA_FAVORABLE  = frozenset({1, 3, 6, 7, 10, 11})
_CHANDRA_SEVERE     = frozenset({8})           # Astama — severe dosha
_CHANDRA_DIFFICULT  = frozenset({2, 12})       # Financial/isolation stress
_CHANDRA_NEUTRAL    = frozenset({4, 5, 9})     # Moderate


def compute_chandrabala_enhanced(
    natal_moon_sign: int,
    transit_moon_sign: int,
    natal_lagna_lord: str = "",
    natal_8th_lord: str = "",
) -> Dict:
    """
    Enhanced Chandrabala with severity tiers and 8th-count exception.

    8th-count exception (Uttara Kalamrita): if the 8th lord from natal Moon
    is the same as the 1st lord (lagna lord) OR if 8th lord is a natural
    benefic, the Astama dosha is negated.

    Returns:
        house_from_natal_moon: 1-12
        quality_tier: 'favorable' | 'neutral' | 'difficult' | 'severe'
        score: 0.0-1.0
        chandrabala_note: explanation
    """
    house = (transit_moon_sign - natal_moon_sign) % 12 + 1

    # Base quality
    if house in _CHANDRA_FAVORABLE:
        quality = "favorable"
        score = 0.80
    elif house in _CHANDRA_SEVERE:
        # Check 8th-count exception
        exception_active = (
            natal_8th_lord and natal_lagna_lord and
            (natal_8th_lord == natal_lagna_lord)
        )
        if exception_active:
            quality = "favorable_exception"  # Astama dosha negated
            score = 0.65
            note = "Astama exception: 8th lord matches Lagna lord — dosha negated"
        else:
            quality = "severe"
            score = 0.10
            note = "Astama Chandrabala (8th from natal Moon) — severe psychological stress"
    elif house in _CHANDRA_DIFFICULT:
        quality = "difficult"
        score = 0.30
        note = f"House {house} from natal Moon — financial/isolation stress"
    else:  # neutral: 4, 5, 9
        quality = "neutral"
        score = 0.50
        note = f"House {house} from natal Moon — moderate"

    if "note" not in dir():
        note = f"House {house} from natal Moon — {quality}"

    # Confidence adjustment factor
    boost = (score - 0.50) * 0.30  # ±0.15 max

    return {
        "house_from_natal_moon": house,
        "quality_tier": quality,
        "score": round(score, 3),
        "chandrabala_note": note,
        "transit_boost_factor": round(boost, 3),
    }


# ═══════════════════════════════════════════════════════════════════
# SECTION 5: PUSHKARA NAVAMSA & PUSHKARA BHAGA DETECTION
# Source: Research file Section 5 + Pushkara Navamsha classical lists
# ═══════════════════════════════════════════════════════════════════

# Pushkara Navamsas: specific degree ranges within each zodiac sign
# that are "nourishing" — multiplier = 2.0 for benefic planets
# Format: (sign_idx_0based, start_degree_in_sign, end_degree_in_sign)
# Degree within sign = (longitude % 30.0)
_PUSHKARA_NAVAMSA_RANGES: List[Tuple[int, float, float]] = [
    (0,  6.667, 10.000),   # Aries: Rohini pada range → Navamsa Leo (auspicious)
    (1,  16.667, 20.000),  # Taurus: Rohini-4/Mrigashira-1 range
    (2,  13.333, 16.667),  # Gemini: Ardra-1 range
    (3,  20.000, 23.333),  # Cancer: Pushya range
    (4,  13.333, 16.667),  # Leo: Purva Phalguni-1 range
    (5,  23.333, 26.667),  # Virgo: Chitra-2 range
    (6,  6.667, 10.000),   # Libra: Swati-1 range
    (7,  16.667, 20.000),  # Scorpio: Anuradha-1 range
    (8,  3.333, 6.667),    # Sagittarius: Mula-2 range
    (9,  10.000, 13.333),  # Capricorn: Shravana range
    (10, 6.667, 10.000),   # Aquarius: Shatabhisha-1 range
    (11, 16.667, 20.000),  # Pisces: Revati-1 range
]

# Pushkara Bhagas: exact degrees per sign (auspiciousness multiplier = 3.0)
# sign_idx → degree_within_sign
_PUSHKARA_BHAGA: Dict[int, float] = {
    0:  21.0,   # Aries 21°
    1:  14.0,   # Taurus 14°
    2:   7.0,   # Gemini 7°
    3:  12.0,   # Cancer 12°
    4:  19.0,   # Leo 19°
    5:   6.0,   # Virgo 6°
    6:  19.0,   # Libra 19°
    7:  11.0,   # Scorpio 11°
    8:  14.0,   # Sagittarius 14°
    9:  23.0,   # Capricorn 23°
    10: 20.0,   # Aquarius 20°
    11:  9.0,   # Pisces 9°
}

# Nakshatra lords excluded from Pushkara Bhaga (Ketu, Mars, Mercury domains)
# Classical rule: PB does not occur in Ketu/Mars/Mercury nakshatra padas
_PUSHKARA_EXCLUDED_LORDS = {"KETU", "MARS", "MERCURY"}


def check_pushkara(longitude: float, planet_name: str = "") -> Dict:
    """
    Check if a planet's longitude falls in a Pushkara Navamsa or Pushkara Bhaga.

    Returns:
        is_pushkara_navamsa: bool
        is_pushkara_bhaga: bool
        multiplier: 1.0 (normal) | 2.0 (navamsa) | 3.0 (bhaga) | 0.0 (excluded)
        note: explanation string
    """
    lon = longitude % 360.0
    sign_idx = int(lon / 30.0)
    deg_in_sign = lon % 30.0

    # Check nakshatra lord for exclusion
    nak = get_nakshatra(lon)
    nak_lord = nak.lord if hasattr(nak, 'lord') else ""
    if nak_lord in _PUSHKARA_EXCLUDED_LORDS:
        return {
            "is_pushkara_navamsa": False,
            "is_pushkara_bhaga": False,
            "multiplier": 1.0,
            "note": f"Pushkara not applicable in {nak_lord}-ruled nakshatra ({nak.name})",
        }

    # Check Pushkara Bhaga first (higher multiplier)
    pb_deg = _PUSHKARA_BHAGA.get(sign_idx)
    if pb_deg is not None and abs(deg_in_sign - pb_deg) <= 0.5:
        return {
            "is_pushkara_navamsa": True,   # Bhaga is within navamsa too
            "is_pushkara_bhaga": True,
            "multiplier": 3.0,
            "note": (
                f"PUSHKARA BHAGA at {deg_in_sign:.1f}° in {nak.name}. "
                f"Multiplier 3.0 — supreme auspiciousness. Debilitation overridden."
            ),
        }

    # Check Pushkara Navamsa
    for s_idx, start, end in _PUSHKARA_NAVAMSA_RANGES:
        if s_idx == sign_idx and start <= deg_in_sign < end:
            return {
                "is_pushkara_navamsa": True,
                "is_pushkara_bhaga": False,
                "multiplier": 2.0,
                "note": (
                    f"PUSHKARA NAVAMSA in {nak.name} at {deg_in_sign:.1f}° in sign. "
                    f"Multiplier 2.0 — benefic results doubled, debilitation partial override."
                ),
            }

    return {
        "is_pushkara_navamsa": False,
        "is_pushkara_bhaga": False,
        "multiplier": 1.0,
        "note": "",
    }


# ═══════════════════════════════════════════════════════════════════
# SECTION 6: VARGOTTAMA DETECTION
# Source: Research file Section 5 — sign modality based algorithm
# ═══════════════════════════════════════════════════════════════════

def is_vargottama(longitude: float) -> bool:
    """
    A planet is Vargottama when its D1 (Rashi) sign == D9 (Navamsa) sign.
    Algorithm based on sign modality:
    - Movable (Aries/Cancer/Libra/Cap): Vargottama in 1st pada (0°0'-3°20' of sign)
    - Fixed (Taurus/Leo/Scorpio/Aquarius): Vargottama in 5th navamsa (13°20'-16°40')
    - Dual (Gemini/Virgo/Sagittarius/Pisces): Vargottama in 9th navamsa (26°40'-30°00')
    """
    lon = longitude % 360.0
    sign_idx = int(lon / 30.0)  # 0-based sign
    deg_in_sign = lon % 30.0
    pada_size = 30.0 / 9.0  # 3.3333° per navamsa

    # Sign modality
    movable = sign_idx in {0, 3, 6, 9}   # Aries, Cancer, Libra, Capricorn
    fixed   = sign_idx in {1, 4, 7, 10}  # Taurus, Leo, Scorpio, Aquarius
    # dual   = sign_idx in {2, 5, 8, 11}  # Gemini, Virgo, Sagittarius, Pisces

    if movable:
        return deg_in_sign < pada_size  # 1st navamsa: 0°-3°20'
    elif fixed:
        return 4 * pada_size <= deg_in_sign < 5 * pada_size  # 5th: 13°20'-16°40'
    else:  # dual
        return deg_in_sign >= 8 * pada_size  # 9th: 26°40'-30°00'


def compute_vargottama_planets(planet_lons: Dict[str, float]) -> Dict[str, bool]:
    """Return dict of {planet_name: is_vargottama} for all planets."""
    return {p: is_vargottama(lon) for p, lon in planet_lons.items()}


# ═══════════════════════════════════════════════════════════════════
# SECTION 7: DWISAPTATI SAMA DASHA ELIGIBILITY
# Source: Research file Section 4 — conditional 72-year dasha system
# ═══════════════════════════════════════════════════════════════════

# Dwisaptati dasha periods (72-year cycle, 8 planets × 9 years each)
# Excludes Ketu, uses Sun-Moon-Mars-Mercury-Jupiter-Venus-Saturn-Rahu
_DWISAPTATI_ORDER = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU"]
_DWISAPTATI_YEARS = {p: 9 for p in _DWISAPTATI_ORDER}  # 9 years each = 72 total


def check_dwisaptati_eligibility(
    planet_houses: Dict[str, int],
    house_lords: Dict[int, str],
) -> Dict:
    """
    Check if Dwisaptati Sama Dasha applies (overrides Vimshottari).
    Conditions (BPHS):
    - Lagna lord placed in 7th house, OR
    - 7th lord placed in Lagna (1st house)
    Returns:
        eligible: bool
        reason: str
        dasha_period_years: int (72 if eligible)
        dasha_system: 'dwisaptati' | 'vimshottari'
    """
    l1 = house_lords.get(1, "")
    l7 = house_lords.get(7, "")

    lagna_lord_in_7th = (l1 and planet_houses.get(l1, 0) == 7)
    seventh_lord_in_1st = (l7 and planet_houses.get(l7, 0) == 1)

    eligible = lagna_lord_in_7th or seventh_lord_in_1st
    if lagna_lord_in_7th:
        reason = f"Lagna lord ({l1}) placed in 7th house"
    elif seventh_lord_in_1st:
        reason = f"7th lord ({l7}) placed in Lagna (1st house)"
    else:
        reason = "Standard Vimshottari conditions"

    return {
        "eligible": eligible,
        "reason": reason,
        "dasha_system": "dwisaptati" if eligible else "vimshottari",
        "dasha_period_years": 72 if eligible else 120,
        "dasha_planets": _DWISAPTATI_ORDER if eligible else None,
        "note": (
            "DWISAPTATI SAMA DASHA: 72-year cycle with 8 planets (9 years each). "
            "Ketu excluded. Overrides Vimshottari per BPHS conditional rule."
            if eligible else ""
        ),
    }


# ═══════════════════════════════════════════════════════════════════
# SECTION 8: NAKSHATRA TRANSIT KARMIC ACTIVATION TAGS
# Source: Research file Section 6 — transit through 27 nakshatras
# Maps each nakshatra to its primary karmic domain + deity theme
# ═══════════════════════════════════════════════════════════════════

NAKSHATRA_TRANSIT_THEMES: List[Dict] = [
    # 0 Ashwini
    {"domain": "health",    "theme": "healing & swift action", "deity": "Ashvins",
     "favorable_for": ["medicine", "new beginnings", "travel", "healing rituals"]},
    # 1 Bharani
    {"domain": "mortality", "theme": "transformation & restriction", "deity": "Yama",
     "favorable_for": ["legal matters", "discipline", "endings", "creative work"]},
    # 2 Krittika
    {"domain": "purification", "theme": "sharp cutting & clarity", "deity": "Agni",
     "favorable_for": ["cooking", "surgery", "financial cutting", "determination"]},
    # 3 Rohini
    {"domain": "wealth",    "theme": "growth & material abundance", "deity": "Brahma",
     "favorable_for": ["business", "agriculture", "love", "luxury", "accumulation"]},
    # 4 Mrigashira
    {"domain": "seeking",   "theme": "searching & sensory exploration", "deity": "Soma",
     "favorable_for": ["research", "travel", "romance", "artistic exploration"]},
    # 5 Ardra
    {"domain": "storms",    "theme": "destruction & renewal", "deity": "Rudra",
     "favorable_for": ["storms", "clearing obstacles", "scientific research"]},
    # 6 Punarvasu
    {"domain": "renewal",   "theme": "restoration & return", "deity": "Aditi",
     "favorable_for": ["return journeys", "renovation", "recovery", "education"]},
    # 7 Pushya
    {"domain": "nourishment", "theme": "support & devotion", "deity": "Brihaspati",
     "favorable_for": ["learning", "banking", "spiritual practice", "family care"]},
    # 8 Ashlesha
    {"domain": "kundalini", "theme": "serpentine wisdom & control", "deity": "Nagas",
     "favorable_for": ["psychology", "mysticism", "research", "occult"]},
    # 9 Magha
    {"domain": "authority", "theme": "royal power & ancestral karma", "deity": "Pitrs",
     "favorable_for": ["governance", "ancestral rituals", "leadership assertion"]},
    # 10 Purva Phalguni
    {"domain": "pleasure",  "theme": "creative enjoyment & leisure", "deity": "Bhaga",
     "favorable_for": ["arts", "romance", "entertainment", "luxury goods"]},
    # 11 Uttara Phalguni
    {"domain": "service",   "theme": "commitment & social contracts", "deity": "Aryaman",
     "favorable_for": ["marriage", "contracts", "employment", "trade"]},
    # 12 Hasta
    {"domain": "skill",     "theme": "craftsmanship & healing hands", "deity": "Savitri",
     "favorable_for": ["crafts", "healing", "farming", "detailed work"]},
    # 13 Chitra
    {"domain": "architecture", "theme": "creative beauty & construction", "deity": "Tvastar",
     "favorable_for": ["art", "design", "engineering", "jewelry", "construction"]},
    # 14 Swati
    {"domain": "independence", "theme": "independent growth & commerce", "deity": "Vayu",
     "favorable_for": ["trade", "commerce", "travel", "new ventures"]},
    # 15 Vishakha
    {"domain": "ambition",  "theme": "focused goal-pursuit", "deity": "Indra-Agni",
     "favorable_for": ["competitive events", "activism", "goal-setting", "politics"]},
    # 16 Anuradha
    {"domain": "devotion",  "theme": "friendship & organizational ability", "deity": "Mitra",
     "favorable_for": ["friendships", "group work", "devotion", "teamwork"]},
    # 17 Jyeshtha
    {"domain": "power",     "theme": "seniority & protective authority", "deity": "Indra",
     "favorable_for": ["leadership", "protection", "authority assertion", "elder roles"]},
    # 18 Mula
    {"domain": "roots",     "theme": "dissolution & getting to core truth", "deity": "Nirriti",
     "favorable_for": ["research", "deconstruction", "spiritual seeking", "medicine"]},
    # 19 Purva Ashadha
    {"domain": "invincibility", "theme": "purification through water", "deity": "Apah",
     "favorable_for": ["purification", "motivation", "competitive endeavors"]},
    # 20 Uttara Ashadha
    {"domain": "victory",   "theme": "final victory & universal dharma", "deity": "Vishvadevas",
     "favorable_for": ["completing tasks", "victory in disputes", "long-term projects"]},
    # 21 Shravana
    {"domain": "learning",  "theme": "listening & wisdom transmission", "deity": "Vishnu",
     "favorable_for": ["education", "listening", "Vedic study", "networking"]},
    # 22 Dhanishta
    {"domain": "wealth",    "theme": "abundant gifts & music", "deity": "Vasus",
     "favorable_for": ["music", "wealth acquisition", "social networking", "real estate"]},
    # 23 Shatabhisha
    {"domain": "healing",   "theme": "mystical healing & secret knowledge", "deity": "Varuna",
     "favorable_for": ["medicine", "occult", "astrology", "healing circles"]},
    # 24 Purva Bhadrapada
    {"domain": "austerity", "theme": "intense spiritual transformation", "deity": "Ajaikapada",
     "favorable_for": ["spiritual disciplines", "charity", "detachment practices"]},
    # 25 Uttara Bhadrapada
    {"domain": "wisdom",    "theme": "deep wisdom & cosmic serpent", "deity": "Ahirbudhnya",
     "favorable_for": ["meditation", "wisdom sharing", "long-term projects", "rain"]},
    # 26 Revati
    {"domain": "completion", "theme": "nourishment, journey's end", "deity": "Pushan",
     "favorable_for": ["travel", "completing cycles", "caring for animals", "closure"]},
]


def get_transit_theme(longitude: float) -> Dict:
    """Return karmic activation theme for a planet transiting this longitude."""
    nak = get_nakshatra(longitude)
    theme = NAKSHATRA_TRANSIT_THEMES[nak.index]
    ext   = NAKSHATRA_EXTENDED[nak.index]
    return {
        "nakshatra": nak.name,
        "nak_index": nak.index,
        "nak_lord":  nak.lord,
        "domain":    theme["domain"],
        "theme":     theme["theme"],
        "deity":     theme["deity"],
        "favorable_for": theme["favorable_for"],
        "tatwa":     ext["tatwa"],
        "dosha":     ext["dosha"],
        "purpose":   ext["purpose"],
    }


# ═══════════════════════════════════════════════════════════════════
# SECTION 9: MASTER NAKSHATRA ANALYSIS FUNCTION
# ═══════════════════════════════════════════════════════════════════

def compute_full_nakshatra_analysis(
    planet_lons: Dict[str, float],
    natal_moon_lon: float,
    transit_moon_lon: float,
    planet_houses: Dict[str, int] = None,
    house_lords: Dict[int, str] = None,
) -> Dict:
    """
    Master nakshatra analysis: runs all nakshatra sub-engines.
    Returns comprehensive dict with all nakshatra-level data.
    """
    planet_houses = planet_houses or {}
    house_lords   = house_lords   or {}

    # Natal Moon nakshatra
    natal_moon_nak  = get_nakshatra_index(natal_moon_lon)
    natal_moon_sign = int(natal_moon_lon % 360 / 30)
    transit_moon_nak  = get_nakshatra_index(transit_moon_lon)
    transit_moon_sign = int(transit_moon_lon % 360 / 30)

    # Tarabala
    tara = compute_tarabala_enhanced(natal_moon_nak, transit_moon_nak)

    # Chandrabala (need 8th lord for exception check)
    l1 = house_lords.get(1, "")
    l8 = house_lords.get(8, "")
    chandra = compute_chandrabala_enhanced(
        natal_moon_sign, transit_moon_sign,
        natal_lagna_lord=l1, natal_8th_lord=l8,
    )

    # Pushkara analysis for each planet
    pushkara_data = {}
    for pname, lon in planet_lons.items():
        pk = check_pushkara(lon, pname)
        if pk["multiplier"] > 1.0:
            pushkara_data[pname] = pk

    # Vargottama
    vargottama_planets = compute_vargottama_planets(planet_lons)
    vargottama_list = [p for p, v in vargottama_planets.items() if v]

    # Natal Moon pada syllable
    moon_pada_info = get_pada_syllable(natal_moon_lon)

    # Dwisaptati eligibility
    dwisaptati = check_dwisaptati_eligibility(planet_houses, house_lords)

    # Transit themes for all planets
    transit_themes = {}
    for pname, lon in planet_lons.items():
        transit_themes[pname] = get_transit_theme(lon)

    return {
        "tarabala":           tara,
        "chandrabala":        chandra,
        "combined_moon_score": round(
            (tara["transit_boost_factor"] + chandra["transit_boost_factor"]) / 2, 3
        ),
        "pushkara_planets":   pushkara_data,
        "vargottama_planets": vargottama_list,
        "moon_naming_star":   moon_pada_info,
        "dwisaptati":         dwisaptati,
        "natal_moon_nakshatra": NAKSHATRAS[natal_moon_nak].name,
        "transit_moon_nakshatra": NAKSHATRAS[transit_moon_nak].name,
        "transit_themes":     transit_themes,
    }
