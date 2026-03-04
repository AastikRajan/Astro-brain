"""
Configuration and Constants for the Vedic Astrology Engine.
All lookup tables, fixed values, and configurable flags live here.
This is the single source of truth for the entire system.
"""

from enum import IntEnum, Enum
from typing import Dict, List, Tuple, FrozenSet

# =============================================================================
# ENUMERATIONS
# =============================================================================

class Planet(IntEnum):
    """The 9 Vedic planets (grahas) in Vimshottari sequence order."""
    SUN = 0
    MOON = 1
    MARS = 2
    MERCURY = 3
    JUPITER = 4
    VENUS = 5
    SATURN = 6
    RAHU = 7
    KETU = 8

class Sign(IntEnum):
    """12 zodiac signs, 0-indexed from Aries."""
    ARIES = 0
    TAURUS = 1
    GEMINI = 2
    CANCER = 3
    LEO = 4
    VIRGO = 5
    LIBRA = 6
    SCORPIO = 7
    SAGITTARIUS = 8
    CAPRICORN = 9
    AQUARIUS = 10
    PISCES = 11

class SignQuality(Enum):
    """Sign modality/quality."""
    MOVABLE = "movable"    # Aries, Cancer, Libra, Capricorn
    FIXED = "fixed"        # Taurus, Leo, Scorpio, Aquarius
    DUAL = "dual"          # Gemini, Virgo, Sagittarius, Pisces

class Element(Enum):
    """Sign elements."""
    FIRE = "fire"      # Aries, Leo, Sagittarius
    EARTH = "earth"    # Taurus, Virgo, Capricorn
    AIR = "air"        # Gemini, Libra, Aquarius
    WATER = "water"    # Cancer, Scorpio, Pisces

class Gender(Enum):
    """Planet gender classification (for Drekkana Bala)."""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class Dignity(Enum):
    """Planet dignity levels."""
    EXALTED = "exalted"
    MOOLATRIKONA = "moolatrikona"
    OWN = "own"
    GREAT_FRIEND = "great_friend"
    FRIEND = "friend"
    NEUTRAL = "neutral"
    ENEMY = "enemy"
    GREAT_ENEMY = "great_enemy"
    DEBILITATED = "debilitated"

class HouseCategory(Enum):
    """House classification for Kendradi Bala."""
    KENDRA = "kendra"       # 1, 4, 7, 10
    PANAPARA = "panapara"   # 2, 5, 8, 11
    APOKLIMA = "apoklima"    # 3, 6, 9, 12

class Friendship(Enum):
    """Planetary friendship levels."""
    INTIMATE = "intimate"
    FRIEND = "friend"
    NEUTRAL = "neutral"
    ENEMY = "enemy"
    BITTER = "bitter"

# =============================================================================
# SIGN PROPERTIES
# =============================================================================

SIGN_LORDS: Dict[Sign, Planet] = {
    Sign.ARIES: Planet.MARS,
    Sign.TAURUS: Planet.VENUS,
    Sign.GEMINI: Planet.MERCURY,
    Sign.CANCER: Planet.MOON,
    Sign.LEO: Planet.SUN,
    Sign.VIRGO: Planet.MERCURY,
    Sign.LIBRA: Planet.VENUS,
    Sign.SCORPIO: Planet.MARS,
    Sign.SAGITTARIUS: Planet.JUPITER,
    Sign.CAPRICORN: Planet.SATURN,
    Sign.AQUARIUS: Planet.SATURN,
    Sign.PISCES: Planet.JUPITER,
}

SIGN_ELEMENTS: Dict[Sign, Element] = {
    Sign.ARIES: Element.FIRE, Sign.TAURUS: Element.EARTH,
    Sign.GEMINI: Element.AIR, Sign.CANCER: Element.WATER,
    Sign.LEO: Element.FIRE, Sign.VIRGO: Element.EARTH,
    Sign.LIBRA: Element.AIR, Sign.SCORPIO: Element.WATER,
    Sign.SAGITTARIUS: Element.FIRE, Sign.CAPRICORN: Element.EARTH,
    Sign.AQUARIUS: Element.AIR, Sign.PISCES: Element.WATER,
}

SIGN_QUALITIES: Dict[Sign, SignQuality] = {
    Sign.ARIES: SignQuality.MOVABLE, Sign.TAURUS: SignQuality.FIXED,
    Sign.GEMINI: SignQuality.DUAL, Sign.CANCER: SignQuality.MOVABLE,
    Sign.LEO: SignQuality.FIXED, Sign.VIRGO: SignQuality.DUAL,
    Sign.LIBRA: SignQuality.MOVABLE, Sign.SCORPIO: SignQuality.FIXED,
    Sign.SAGITTARIUS: SignQuality.DUAL, Sign.CAPRICORN: SignQuality.MOVABLE,
    Sign.AQUARIUS: SignQuality.FIXED, Sign.PISCES: SignQuality.DUAL,
}

# Odd (Oja) = male signs; Even (Yugma) = female signs
SIGN_IS_ODD: Dict[Sign, bool] = {
    s: (s.value % 2 == 0) for s in Sign  # Aries(0)=even-index but ODD sign
}
# Correction: Aries=1st=odd, Taurus=2nd=even, etc.
# sign number = sign.value + 1; odd if (sign.value % 2 == 0)

# =============================================================================
# PLANET PROPERTIES
# =============================================================================

PLANET_GENDER: Dict[Planet, Gender] = {
    Planet.SUN: Gender.MALE,
    Planet.MOON: Gender.FEMALE,
    Planet.MARS: Gender.MALE,
    Planet.MERCURY: Gender.NEUTRAL,
    Planet.JUPITER: Gender.MALE,
    Planet.VENUS: Gender.FEMALE,
    Planet.SATURN: Gender.NEUTRAL,
}

# Natural benefic/malefic classification (base, Moon depends on phase)
NATURAL_BENEFICS: FrozenSet[Planet] = frozenset({
    Planet.JUPITER, Planet.VENUS, Planet.MERCURY  # Mercury if unafflicted
})
NATURAL_MALEFICS: FrozenSet[Planet] = frozenset({
    Planet.SUN, Planet.MARS, Planet.SATURN, Planet.RAHU, Planet.KETU
})

# =============================================================================
# EXALTATION / DEBILITATION POINTS (absolute degrees 0-360)
# =============================================================================

# Exaltation points - exact degrees where planet reaches max Uccha Bala
EXALTATION_DEGREES: Dict[Planet, float] = {
    Planet.SUN: 10.0,        # 10° Aries
    Planet.MOON: 33.0,       # 3° Taurus
    Planet.MARS: 298.0,      # 28° Capricorn
    Planet.MERCURY: 165.0,   # 15° Virgo
    Planet.JUPITER: 95.0,    # 5° Cancer
    Planet.VENUS: 357.0,     # 27° Pisces
    Planet.SATURN: 200.0,    # 20° Libra
}

# Debilitation = 180° from exaltation
DEBILITATION_DEGREES: Dict[Planet, float] = {
    p: (d + 180.0) % 360.0 for p, d in EXALTATION_DEGREES.items()
}

# =============================================================================
# MOOLATRIKONA RANGES (sign, start_degree, end_degree within sign)
# =============================================================================

MOOLATRIKONA: Dict[Planet, Tuple[Sign, float, float]] = {
    Planet.SUN: (Sign.LEO, 0.0, 20.0),
    Planet.MOON: (Sign.TAURUS, 3.0, 30.0),
    Planet.MARS: (Sign.ARIES, 0.0, 12.0),
    Planet.MERCURY: (Sign.VIRGO, 15.0, 20.0),
    Planet.JUPITER: (Sign.SAGITTARIUS, 0.0, 10.0),
    Planet.VENUS: (Sign.LIBRA, 0.0, 15.0),
    Planet.SATURN: (Sign.AQUARIUS, 0.0, 20.0),
}

# Own signs (where planet is lord)
OWN_SIGNS: Dict[Planet, List[Sign]] = {
    Planet.SUN: [Sign.LEO],
    Planet.MOON: [Sign.CANCER],
    Planet.MARS: [Sign.ARIES, Sign.SCORPIO],
    Planet.MERCURY: [Sign.GEMINI, Sign.VIRGO],
    Planet.JUPITER: [Sign.SAGITTARIUS, Sign.PISCES],
    Planet.VENUS: [Sign.TAURUS, Sign.LIBRA],
    Planet.SATURN: [Sign.CAPRICORN, Sign.AQUARIUS],
}

# =============================================================================
# NAISARGIKA (NATURAL) FRIENDSHIP TABLE
# =============================================================================

# Each planet's natural friends, enemies, neutrals
NAISARGIKA_FRIENDS: Dict[Planet, FrozenSet[Planet]] = {
    Planet.SUN: frozenset({Planet.MOON, Planet.MARS, Planet.JUPITER}),
    Planet.MOON: frozenset({Planet.SUN, Planet.MERCURY}),
    Planet.MARS: frozenset({Planet.SUN, Planet.MOON, Planet.JUPITER}),
    Planet.MERCURY: frozenset({Planet.SUN, Planet.VENUS}),
    Planet.JUPITER: frozenset({Planet.SUN, Planet.MOON, Planet.MARS}),
    Planet.VENUS: frozenset({Planet.MERCURY, Planet.SATURN}),
    Planet.SATURN: frozenset({Planet.MERCURY, Planet.VENUS}),
}

NAISARGIKA_ENEMIES: Dict[Planet, FrozenSet[Planet]] = {
    Planet.SUN: frozenset({Planet.VENUS, Planet.SATURN}),
    Planet.MOON: frozenset(set()),  # Moon has no natural enemies
    Planet.MARS: frozenset({Planet.MERCURY}),
    Planet.MERCURY: frozenset({Planet.MOON}),
    Planet.JUPITER: frozenset({Planet.MERCURY, Planet.VENUS}),
    Planet.VENUS: frozenset({Planet.SUN, Planet.MOON}),
    Planet.SATURN: frozenset({Planet.SUN, Planet.MOON, Planet.MARS}),
}
# Neutrals = everyone not in friends or enemies (excluding self)

# =============================================================================
# NAKSHATRA DATA
# =============================================================================

NAKSHATRA_SPAN = 13.0 + 20.0 / 60.0  # 13°20' = 13.3333...°
PADA_SPAN = NAKSHATRA_SPAN / 4.0      # 3°20' = 3.3333...°

# Nakshatra lords in sequence (repeats 3 times across 27 nakshatras)
# The VIMSHOTTARI sequence: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury
VIMSHOTTARI_SEQUENCE: List[Planet] = [
    Planet.KETU, Planet.VENUS, Planet.SUN, Planet.MOON, Planet.MARS,
    Planet.RAHU, Planet.JUPITER, Planet.SATURN, Planet.MERCURY,
]

NAKSHATRA_NAMES: List[str] = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purvashadha",
    "Uttarashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

def get_nakshatra_lord(nakshatra_index: int) -> Planet:
    """Get the Vimshottari lord for a nakshatra (0-26)."""
    return VIMSHOTTARI_SEQUENCE[nakshatra_index % 9]

# =============================================================================
# VIMSHOTTARI DASHA DURATIONS (years)
# =============================================================================

VIMSHOTTARI_YEARS: Dict[Planet, int] = {
    Planet.KETU: 7, Planet.VENUS: 20, Planet.SUN: 6,
    Planet.MOON: 10, Planet.MARS: 7, Planet.RAHU: 18,
    Planet.JUPITER: 16, Planet.SATURN: 19, Planet.MERCURY: 17,
}

VIMSHOTTARI_TOTAL = 120  # Sum of all dasha years

# =============================================================================
# YOGINI DASHA DATA
# =============================================================================

YOGINI_NAMES: List[str] = [
    "Mangala", "Pingala", "Dhanya", "Bhramari",
    "Bhadrika", "Ulka", "Siddha", "Sankata",
]

YOGINI_PLANETS: List[Planet] = [
    Planet.MOON, Planet.SUN, Planet.JUPITER, Planet.MARS,
    Planet.MERCURY, Planet.SATURN, Planet.VENUS, Planet.RAHU,
]

YOGINI_YEARS: List[int] = [1, 2, 3, 4, 5, 6, 7, 8]
YOGINI_TOTAL = 36

# =============================================================================
# DIG BALA - POWERLESS POINTS
# =============================================================================

# Each planet's POWERLESS direction (house cusp longitude)
# Dig Bala = angular_distance_from_powerless_point / 3
# Max at opposite point = 60 shashtiamsas
DIG_BALA_POWERLESS_HOUSE: Dict[Planet, int] = {
    Planet.SUN: 4,       # Sun powerless at IC (4th cusp)
    Planet.MARS: 4,      # Mars powerless at IC
    Planet.JUPITER: 7,   # Jupiter powerless at DC (7th cusp)
    Planet.MERCURY: 7,   # Mercury powerless at DC
    Planet.MOON: 10,     # Moon powerless at MC (10th cusp)
    Planet.VENUS: 10,    # Venus powerless at MC
    Planet.SATURN: 1,    # Saturn powerless at ASC (1st cusp)
}

# =============================================================================
# KENDRADI BALA - HOUSE CATEGORY SCORES
# =============================================================================

KENDRADI_SCORES: Dict[HouseCategory, float] = {
    HouseCategory.KENDRA: 60.0,
    HouseCategory.PANAPARA: 30.0,
    HouseCategory.APOKLIMA: 15.0,
}

def get_house_category(house_num: int) -> HouseCategory:
    """1-indexed house number → category."""
    if house_num in (1, 4, 7, 10):
        return HouseCategory.KENDRA
    elif house_num in (2, 5, 8, 11):
        return HouseCategory.PANAPARA
    else:
        return HouseCategory.APOKLIMA

# =============================================================================
# NAISARGIKA BALA - FIXED NATURAL STRENGTH (in Shashtiamsas)
# =============================================================================

NAISARGIKA_BALA: Dict[Planet, float] = {
    Planet.SUN: 60.0,
    Planet.MOON: 51.43,
    Planet.MARS: 17.14,
    Planet.MERCURY: 25.71,
    Planet.JUPITER: 34.29,
    Planet.VENUS: 42.86,
    Planet.SATURN: 8.57,
}

# =============================================================================
# KALA BALA - TIME LORD BOOSTS (Shashtiamsas)
# =============================================================================

ABDA_BALA_POINTS = 15.0    # Year lord gets 15
MASA_BALA_POINTS = 30.0    # Month lord gets 30
VARA_BALA_POINTS = 45.0    # Day lord gets 45
HORA_BALA_POINTS = 60.0    # Hour lord gets 60

# Day-of-week → lord mapping (0=Sunday, 1=Monday, ...)
WEEKDAY_LORDS: Dict[int, Planet] = {
    0: Planet.SUN,
    1: Planet.MOON,
    2: Planet.MARS,
    3: Planet.MERCURY,
    4: Planet.JUPITER,
    5: Planet.VENUS,
    6: Planet.SATURN,
}

# Planets strong during DAY (diurnal) vs NIGHT (nocturnal)
DAY_STRONG_PLANETS: FrozenSet[Planet] = frozenset({
    Planet.SUN, Planet.JUPITER, Planet.VENUS
})
NIGHT_STRONG_PLANETS: FrozenSet[Planet] = frozenset({
    Planet.MOON, Planet.MARS, Planet.SATURN
})
# Mercury is ALWAYS strong (60 shashtiamsas for Nathonnatha)

# =============================================================================
# SAPTAVARGAJA BALA - DIGNITY SCORES PER VARGA
# =============================================================================

# Points awarded in each varga for each dignity level (in shashtiamsas)
# Based on standard BPHS interpretation
SAPTAVARGAJA_SCORES: Dict[Dignity, float] = {
    # Research File 1 (Saravali / BPHS Ch.27) exact classical values:
    # Exalted: bypassed in Saptavargaja context → treated as Own Sign (30)
    # Debilitated: bypassed → treated as Adhi Satru (2)
    Dignity.EXALTED: 30.0,       # Classical bypass: no exaltation bonus in varga context → OWN equivalent
    Dignity.MOOLATRIKONA: 45.0,  # Root Trine
    Dignity.OWN: 30.0,           # Swakshetra
    Dignity.GREAT_FRIEND: 20.0,  # Adhi Mitra (Extreme Friend)  [was 22.5 — FIXED]
    Dignity.FRIEND: 15.0,        # Mitra
    Dignity.NEUTRAL: 10.0,       # Sama (Neutral)               [was 7.5  — FIXED]
    Dignity.ENEMY: 4.0,          # Satru                        [was 3.75 — FIXED]
    Dignity.GREAT_ENEMY: 2.0,    # Adhi Satru (Extreme Enemy)   [was 1.875 — FIXED]
    Dignity.DEBILITATED: 2.0,    # Classical bypass → Adhi Satru equivalent
}

# The 7 vargas used for Saptavargaja
SAPTAVARGA_CHARTS: List[int] = [1, 2, 3, 7, 9, 12, 30]

# =============================================================================
# ASPECT (DRISHTI) RULES
# =============================================================================

# Standard: all planets aspect 7th from themselves (180°)
# Special aspects:
SPECIAL_ASPECTS: Dict[Planet, List[int]] = {
    Planet.MARS: [4, 8],       # Mars also aspects 4th and 8th
    Planet.JUPITER: [5, 9],    # Jupiter also aspects 5th and 9th
    Planet.SATURN: [3, 10],    # Saturn also aspects 3rd and 10th
}

# Aspect strength by angular separation (piecewise linear from BPHS)
# These are the "drishti values" for special aspects
# Full aspect (180°) = 60, 3/4 aspect = 45, 1/2 = 30, 1/4 = 15
ASPECT_STRENGTHS: Dict[int, float] = {
    3: 15.0,   # 1/4 aspect (Saturn special)
    4: 45.0,   # 3/4 aspect (Mars special)
    5: 30.0,   # 1/2 aspect (Jupiter special)
    7: 60.0,   # Full aspect (all planets)
    8: 45.0,   # 3/4 aspect (Mars special)
    9: 30.0,   # 1/2 aspect (Jupiter special)
    10: 15.0,  # 1/4 aspect (Saturn special)
}

# =============================================================================
# BHAVA DIGBALA - HOUSE DIRECTIONAL STRENGTH
# =============================================================================

# Sign type classification for Bhava Digbala
# Nara (human): Gemini, Virgo, Libra, first half Sagittarius, Aquarius
# Jalachara (water): Cancer, Pisces, second half Capricorn
# Chatushpada (quadruped): Aries, Taurus, Leo, second half Sagittarius, first half Capricorn
# Keeta (insect): Scorpio

BHAVA_DIG_BALA: Dict[int, float] = {
    1: 60.0, 2: 40.0, 3: 10.0, 4: 30.0, 5: 20.0, 6: 50.0,
    7: 30.0, 8: 20.0, 9: 20.0, 10: 0.0, 11: 50.0, 12: 40.0,
}

# =============================================================================
# ASHTAKVARGA - BENEFIC CONTRIBUTION RULES (BPHS)
# =============================================================================
# For each RECIPIENT planet, each DONOR gives a bindu (1) at specific
# house-offsets from the donor's position. These are 1-indexed house numbers.

ASHTAKVARGA_RULES: Dict[Planet, Dict] = {
    Planet.SUN: {
        Planet.SUN:     [1, 2, 4, 7, 8, 9, 10, 11],
        Planet.MOON:    [3, 6, 10, 11],
        Planet.MARS:    [1, 2, 4, 7, 8, 9, 10, 11],
        Planet.MERCURY: [3, 5, 6, 9, 10, 11, 12],
        Planet.JUPITER: [5, 6, 9, 11],
        Planet.VENUS:   [6, 7, 12],
        Planet.SATURN:  [1, 2, 4, 7, 8, 9, 10, 11],
        'ASC':          [3, 4, 6, 10, 11, 12],
    },
    Planet.MOON: {
        Planet.SUN:     [3, 6, 7, 8, 10, 11],
        Planet.MOON:    [1, 3, 6, 7, 10, 11],
        Planet.MARS:    [2, 3, 5, 6, 9, 10, 11],
        Planet.MERCURY: [1, 3, 4, 5, 7, 8, 10, 11],
        Planet.JUPITER: [1, 4, 7, 8, 10, 11, 12],
        Planet.VENUS:   [3, 4, 5, 7, 9, 10, 11],
        Planet.SATURN:  [3, 5, 6, 11],
        'ASC':          [3, 6, 10, 11],
    },
    Planet.MARS: {
        Planet.SUN:     [3, 5, 6, 10, 11],
        Planet.MOON:    [3, 6, 11],
        Planet.MARS:    [1, 2, 4, 7, 8, 10, 11],
        Planet.MERCURY: [3, 5, 6, 11],
        Planet.JUPITER: [6, 10, 11, 12],
        Planet.VENUS:   [6, 8, 11, 12],
        Planet.SATURN:  [1, 4, 7, 8, 9, 10, 11],
        'ASC':          [1, 3, 6, 10, 11],
    },
    Planet.MERCURY: {
        Planet.SUN:     [5, 6, 9, 11, 12],
        Planet.MOON:    [2, 4, 6, 8, 10, 11],
        Planet.MARS:    [1, 2, 4, 7, 8, 9, 10, 11],
        Planet.MERCURY: [1, 3, 5, 6, 9, 10, 11, 12],
        Planet.JUPITER: [6, 8, 11, 12],
        Planet.VENUS:   [1, 2, 3, 4, 5, 8, 9, 11],
        Planet.SATURN:  [1, 2, 4, 7, 8, 9, 10, 11],
        'ASC':          [1, 2, 4, 6, 8, 10, 11],
    },
    Planet.JUPITER: {
        Planet.SUN:     [1, 2, 3, 4, 7, 8, 9, 10, 11],
        Planet.MOON:    [2, 5, 7, 9, 11],
        Planet.MARS:    [1, 2, 4, 7, 8, 10, 11],
        Planet.MERCURY: [1, 2, 4, 5, 6, 9, 10, 11],
        Planet.JUPITER: [1, 2, 3, 4, 7, 8, 10, 11],
        Planet.VENUS:   [2, 5, 6, 9, 10, 11],
        Planet.SATURN:  [3, 5, 6, 12],
        'ASC':          [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    Planet.VENUS: {
        Planet.SUN:     [8, 11, 12],
        Planet.MOON:    [1, 2, 3, 4, 5, 8, 9, 11, 12],
        Planet.MARS:    [3, 4, 6, 8, 11, 12],        # BPHS: 6 bindus (removed 9)
        Planet.MERCURY: [3, 5, 6, 9, 11],
        Planet.JUPITER: [5, 8, 9, 10, 11],
        Planet.VENUS:   [1, 2, 3, 4, 5, 8, 9, 10, 11],
        Planet.SATURN:  [3, 4, 5, 8, 9, 10, 11],
        'ASC':          [1, 2, 3, 4, 5, 8, 9, 11],
    },  # Total = 52 ✓
    Planet.SATURN: {
        Planet.SUN:     [1, 2, 4, 7, 8, 10, 11],       # BPHS: 7 bindus (removed 9)
        Planet.MOON:    [3, 6, 11],
        Planet.MARS:    [3, 5, 6, 10, 11, 12],
        Planet.MERCURY: [6, 8, 9, 10, 11, 12],
        Planet.JUPITER: [5, 6, 11, 12],
        Planet.VENUS:   [6, 11, 12],
        Planet.SATURN:  [3, 5, 6, 11],
        'ASC':          [1, 3, 4, 6, 10, 11],
    },
}

# Checksum: total bindus per planet should be fixed
ASHTAKVARGA_TOTALS: Dict[Planet, int] = {
    Planet.SUN: 48, Planet.MOON: 49, Planet.MARS: 39,
    Planet.MERCURY: 54, Planet.JUPITER: 56, Planet.VENUS: 52,
    Planet.SATURN: 39,
}
SARVASHTAKVARGA_TOTAL = 337  # Sum of all planet totals

# =============================================================================
# VEDHA (TRANSIT OBSTRUCTION) TABLE
# =============================================================================

# For each planet: {favorable_house: vedha_house}
# When transit planet is in favorable house but ANY planet transits vedha house,
# the benefit is cancelled.
VEDHA_TABLE: Dict[Planet, Dict[int, int]] = {
    Planet.SUN:     {3: 9, 6: 12, 10: 4, 11: 5},
    Planet.MOON:    {1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8},
    Planet.MARS:    {3: 12, 6: 9, 11: 5},
    Planet.MERCURY: {2: 5, 4: 3, 6: 9, 8: 1, 10: 8, 11: 12},  # fixed: Mercury favored in 2,4,6,8,10,11
    Planet.JUPITER: {2: 12, 5: 4, 7: 3, 9: 10, 11: 8},
    Planet.VENUS:   {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 3, 12: 6},
    Planet.SATURN:  {3: 12, 6: 9, 11: 5},
    Planet.RAHU:    {3: 12, 6: 9, 11: 5},
    Planet.KETU:    {3: 12, 6: 9, 11: 5},
}

# Vipareeta Vedha: when transit planet is in INAUSPICIOUS house, if another
# planet is in the paired house the adverse effect is cancelled.
# Format: Planet → {inauspicious_house: cancelling_house}
VIPAREETA_VEDHA_TABLE: Dict[Planet, Dict[int, int]] = {
    Planet.SUN:     {4: 10, 5: 11, 9: 3, 12: 6},
    Planet.MOON:    {2: 7, 4: 10, 5: 1, 8: 11, 9: 3, 12: 6},
    Planet.MARS:    {5: 11, 9: 6, 12: 3},
    Planet.MERCURY: {1: 8, 3: 4, 5: 2, 9: 6, 12: 11},
    Planet.JUPITER: {3: 7, 4: 5, 8: 11, 10: 9, 12: 2},
    Planet.VENUS:   {6: 11, 7: 2, 10: 4},
    Planet.SATURN:  {5: 11, 9: 6, 12: 3},
    Planet.RAHU:    {5: 11, 9: 6, 12: 3},
    Planet.KETU:    {5: 11, 9: 6, 12: 3},
}

# Exception: Sun and Saturn do NOT obstruct each other
# Moon and Mercury do NOT obstruct each other
# Sun and Venus do NOT obstruct each other (classical Gochar Phaladeepika)
VEDHA_EXCEPTIONS: List[FrozenSet[Planet]] = [
    frozenset({Planet.SUN, Planet.SATURN}),
    frozenset({Planet.MOON, Planet.MERCURY}),
    frozenset({Planet.SUN, Planet.VENUS}),
]

# =============================================================================
# VEDHA QUANTITATIVE REDUCTION (not binary — per classical Phala-deepika)
# =============================================================================
# Reduction percentage applied to the favorable gochar score when blocked.
# Key = relationship of obstructing planet to the transiting planet.
# Source: Deep Dive research — "friend obstructing = 50% reduction" etc.
VEDHA_REDUCTION: Dict[str, float] = {
    "great_friend": 0.25,   # closest ally — weak obstruction
    "friend":       0.50,
    "neutral":      0.75,
    "enemy":        1.00,   # full nullification
    "great_enemy":  1.00,
    "same":         0.25,   # same lordship / same category
}

# =============================================================================
# KAKSHYA PRAVESHA — 8 sub-divisions per sign, 3°45' each
# =============================================================================
# Fixed lord sequence within every sign: Saturn → Jupiter → Mars → Sun →
#   Venus → Mercury → Moon → Lagna
# When transiting planet enters a Kakshya whose lord contributed a BINDU
# in the planet's BAV for that sign → highly auspicious sub-period.
# When lord gave REKHA (0) → negative/null sub-period.

KAKSHYA_LORDS: List[str] = [
    "SATURN", "JUPITER", "MARS", "SUN", "VENUS", "MERCURY", "MOON", "LAGNA"
]
KAKSHYA_SPAN: float = 30.0 / 8  # = 3.75° per sub-division

# =============================================================================
# ASYMMETRIC MANIFESTATION ZONES (primary result window within sign transit)
# =============================================================================
# Each planet delivers its primary transit results in a specific degree window
# within the sign. Outside this window the result still occurs but is muted.
# (start_deg, end_deg) — inclusive, 0-based within sign (0°–30°)

MANIFESTATION_ZONES: Dict[str, Tuple[float, float]] = {
    "SUN":     (0.0,  10.0),    # first 10° → strongest results
    "MARS":    (0.0,  10.0),
    "JUPITER": (10.0, 20.0),    # middle 10°
    "VENUS":   (10.0, 20.0),
    "SATURN":  (20.0, 30.0),    # final 10° (last ~10 months of 2.5-yr transit)
    "MOON":    (20.0, 30.0),
    "MERCURY": (0.0,  30.0),    # throughout
    "RAHU":    (0.0,  30.0),
    "KETU":    (0.0,  30.0),
}
# Multiplier applied when planet is OUTSIDE its primary zone (still active but reduced)
MANIFESTATION_OUTSIDE_MULTIPLIER: float = 0.55

# =============================================================================
# TRANSIT FAVORABLE HOUSES (from Moon sign) - GOCHAR
# =============================================================================

TRANSIT_FAVORABLE: Dict[Planet, List[int]] = {
    Planet.SUN:     [3, 6, 10, 11],
    Planet.MOON:    [1, 3, 6, 7, 10, 11],
    Planet.MARS:    [3, 6, 11],
    Planet.MERCURY: [6, 8, 10, 11],          # Research: 6,8,10,11 only (NOT 2,4)
    Planet.JUPITER: [2, 5, 7, 9, 11],
    Planet.VENUS:   [1, 2, 3, 4, 5, 8, 9, 11, 12],
    Planet.SATURN:  [3, 6, 11],
    Planet.RAHU:    [3, 6, 11],              # Research: 3,6,11 only (NOT 10)
    Planet.KETU:    [3, 6, 11],              # Research: 3,6,11 only (NOT 10)
}

# =============================================================================
# GOCHAR SCORES — Full classical 9-planet × 12-house matrix (from Moon)
# Score: +1 = Shubha (auspicious), -1 = Ashubha (inauspicious), 0 = mixed/neutral
# Source: BPHS, Phaladeepika, as researched from classical texts
# =============================================================================

GOCHAR_SCORES: Dict[Planet, Dict[int, int]] = {
    # key = house from Moon (1-12), value = score (+1 / -1 / 0)
    Planet.SUN: {
        1: 0, 2: -1, 3: 1, 4: 0, 5: -1, 6: 1,
        7: 0, 8: -1, 9: -1, 10: 1, 11: 1, 12: -1,
    },
    Planet.MOON: {
        1: 1, 2: -1, 3: 1, 4: -1, 5: -1, 6: 1,
        7: 1, 8: -1, 9: -1, 10: 1, 11: 1, 12: -1,
    },
    Planet.MARS: {
        1: -1, 2: -1, 3: 1, 4: -1, 5: -1, 6: 1,
        7: -1, 8: -1, 9: -1, 10: -1, 11: 1, 12: -1,
    },
    Planet.MERCURY: {
        1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: 1,
        7: -1, 8: 1, 9: -1, 10: 1, 11: 1, 12: -1,
    },
    Planet.JUPITER: {
        1: -1, 2: 1, 3: -1, 4: -1, 5: 1, 6: -1,
        7: 1, 8: 0, 9: 1, 10: -1, 11: 1, 12: 0,
    },
    Planet.VENUS: {
        1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: -1,
        7: -1, 8: 1, 9: 1, 10: -1, 11: 1, 12: 1,
    },
    Planet.SATURN: {
        1: -1, 2: -1, 3: 1, 4: -1, 5: -1, 6: 1,
        7: -1, 8: -1, 9: 1, 10: -1, 11: 1, 12: -1,
    },
    Planet.RAHU: {
        1: -1, 2: -1, 3: 1, 4: -1, 5: -1, 6: 1,
        7: -1, 8: -1, 9: -1, 10: -1, 11: 1, 12: -1,
    },
    Planet.KETU: {
        1: -1, 2: -1, 3: 1, 4: -1, 5: -1, 6: 1,
        7: -1, 8: -1, 9: -1, 10: -1, 11: 1, 12: -1,
    },
}

# Classical Gochar effects (domain and description)
# (planet, house_from_moon) → (domain, description)
GOCHAR_EFFECTS: Dict = {
    ("SUN", 3):  ("communication", "Good health, income, promotion, leadership opportunities"),
    ("SUN", 6):  ("health",        "Health management, victory over enemies, work recognition"),
    ("SUN", 10): ("career",        "Career visibility, authority, promotion, new responsibilities"),
    ("SUN", 11): ("gains",         "Income increase, social status, fulfillment of goals"),
    ("SUN", 2):  ("family",        "Defeats, losses, conflicts in family"),
    ("SUN", 5):  ("children",      "Diseases, expenditure, troubles from children"),
    ("SUN", 8):  ("health",        "Diseases, no success, defeat in lawsuits"),
    ("SUN", 9):  ("luck",          "Excess expenditure, diseases, reduced fortune"),
    ("SUN", 12): ("expenses",      "Excess expenditure, defeat, isolation"),
    ("MOON", 1): ("self",          "Facilities increased, income, emotional comfort"),
    ("MOON", 3): ("communication", "Travel, communication, growth in facilities"),
    ("MOON", 6): ("health",        "Victory over enemies, income, health improvement"),
    ("MOON", 7): ("relationships", "Good results in partnerships, income, partnerships active"),
    ("MOON", 10):("career",        "Career gains, professional recognition"),
    ("MOON", 11):("gains",         "Emotional fulfillment, income increase, social connections"),
    ("MOON", 2): ("family",        "Sorrows, miseries, unwanted expenditure"),
    ("MOON", 4): ("home",          "Sorrows, obstruction, domestic difficulties"),
    ("MOON", 5): ("children",      "Sorrows, miseries, obstacles"),
    ("MOON", 8): ("health",        "Mental agony, trouble to mother, hidden losses"),
    ("MOON", 9): ("luck",          "Expenditure, loss of reputation, reduced fortune"),
    ("MOON", 12):("expenses",      "Misery, loss of reputation, isolation"),
    ("MARS", 3): ("courage",       "Happiness, comforts, income, courageous actions rewarded"),
    ("MARS", 6): ("enemies",       "Victory in conflicts, good health, competition won"),
    ("MARS", 11):("gains",         "Income through effort and initiative, goals achieved"),
    ("MARS", 7): ("relationships", "Quarrel, loss, maximum malefic results for partnerships"),
    ("MARS", 10):("career",        "Sorrows, defeat, career setbacks"),
    ("MERCURY", 6):  ("work",      "Good health, happiness, education, income, problem-solving"),
    ("MERCURY", 8):  ("finances",  "Good health, overall happiness, income, occult gains"),
    ("MERCURY", 10): ("career",    "Happiness, income, career gains through intellect"),
    ("MERCURY", 11): ("gains",     "Networking, gains through intellect and communication"),
    ("MERCURY", 2):  ("speech",    "Maximum bad results, obstruction, loss of wealth"),
    ("JUPITER", 2):  ("wealth",    "Wealth increase, speech improvement, family growth"),
    ("JUPITER", 5):  ("children",  "Intelligence, creativity, good news around children"),
    ("JUPITER", 7):  ("marriage",  "Relationships and partnerships prosper"),
    ("JUPITER", 9):  ("fortune",   "Luck, divine grace, mentor, auspicious travel"),
    ("JUPITER", 11): ("gains",     "Gains, income increase, fulfillment of desires"),
    ("JUPITER", 1):  ("health",    "Bad results, fear, loss of status and health"),
    ("JUPITER", 3):  ("siblings",  "Loss of respect, humiliation"),
    ("JUPITER", 4):  ("property",  "Bad results, worry, domestic losses"),
    ("JUPITER", 6):  ("battles",   "Loss of respect, humiliation, conflicts"),
    ("JUPITER", 10): ("career",    "Bad health, worries, career setbacks"),
    ("VENUS", 1):  ("self",        "Personal charm, health, comforts, increased income"),
    ("VENUS", 2):  ("wealth",      "Wealth, family happiness, enjoyment, increased income"),
    ("VENUS", 3):  ("communication","Easy life, comforts, income increase"),
    ("VENUS", 4):  ("property",    "Domestic happiness, comforts, property gains"),
    ("VENUS", 5):  ("children",    "Creative success, children related positive news"),
    ("VENUS", 8):  ("legacy",      "Hidden gains, comforts, income through inheritance"),
    ("VENUS", 9):  ("fortune",     "Luck, pleasures, income, divine grace"),
    ("VENUS", 11): ("gains",       "Social gains, income through creative work"),
    ("VENUS", 12): ("spiritual",   "Comforts, easy life, spiritual development"),
    ("VENUS", 6):  ("health",      "Maximum malefic results, sexual disease, heavy loss"),
    ("VENUS", 7):  ("relationships","Bad results, sorrow, heavy loss in relationships"),
    ("VENUS", 10): ("career",      "Bad results, sorrow, loss of comforts"),
    ("SATURN", 3): ("courage",     "Gains, comforts, income, effort rewarded"),
    ("SATURN", 6): ("enemies",     "Victory over enemies, health improvement, recognition"),
    ("SATURN", 9): ("luck",        "Gains, comforts, spiritual progress"),
    ("SATURN", 11):("gains",       "Steady income, discipline rewarded, long-term gains"),
    ("SATURN", 1): ("health",      "Excess expenditure, loans, physical challenges"),
    ("SATURN", 2): ("family",      "Excess expenditure, financial strain"),
    ("SATURN", 4): ("property",    "Domestic difficulties, malefic home results"),
    ("SATURN", 8): ("losses",      "Malefic results, hidden obstacles, chronic issues"),
    ("SATURN", 10):("career",      "Career malefic results, authority challenges"),
    ("SATURN", 12):("expenses",    "Malefic results, isolation, losses"),
    ("RAHU", 3):  ("communication","Success, gains, prosperity, good health"),
    ("RAHU", 6):  ("enemies",      "Victory, gains, success over obstacles"),
    ("RAHU", 11): ("gains",        "Good health, income, social success, gains"),
    ("RAHU", 9):  ("luck",         "Severe obstacles, diseases — most malefic house for Rahu"),
    ("KETU", 3):  ("communication","Success, gains, prosperity, spiritual gains"),
    ("KETU", 6):  ("enemies",      "Victory, gains, success over obstacles"),
    ("KETU", 11): ("gains",        "Good health, income, gains, fulfillment"),
    ("KETU", 9):  ("luck",         "Severe obstacles, diseases — most malefic house for Ketu"),
}

# =============================================================================
# COMBUSTION RANGES (degrees from Sun)
# =============================================================================

COMBUSTION_DEGREES: Dict[Planet, float] = {
    Planet.MOON: 12.0,
    Planet.MARS: 17.0,
    Planet.MERCURY: 14.0,   # direct; 12° when retrograde
    Planet.JUPITER: 11.0,
    Planet.VENUS: 10.0,     # direct; 8° when retrograde
    Planet.SATURN: 15.0,
}

# Retrograde combustion orbs (tighter — retrograde planets escape combustion earlier)
COMBUSTION_DEGREES_RETRO: Dict[Planet, float] = {
    Planet.MERCURY: 12.0,
    Planet.VENUS: 8.0,
}

# =============================================================================
# VIMSHOPAK BALA WEIGHTS (16-chart scheme)
# =============================================================================

VIMSHOPAK_WEIGHTS: Dict[int, float] = {
    1: 3.5, 2: 1.0, 3: 1.0, 4: 0.5, 7: 0.5,
    9: 3.0, 10: 0.5, 12: 0.5, 16: 1.0, 20: 0.5,
    24: 0.5, 27: 0.5, 30: 1.0, 40: 0.5, 45: 0.5, 60: 4.0,
}
VIMSHOPAK_MAX = 20.0

# =============================================================================
# KP SUB-LORD PROPORTIONS
# =============================================================================

# Sub-divisions within each nakshatra proportional to Vimshottari years
# Order starts from the nakshatra lord and follows Vimshottari sequence
KP_SUB_PROPORTIONS: Dict[Planet, float] = {
    p: years / VIMSHOTTARI_TOTAL for p, years in VIMSHOTTARI_YEARS.items()
}

# =============================================================================
# TRIKONA SHODHANA GROUPS (for Ashtakvarga reduction)
# =============================================================================

TRIKONA_GROUPS: List[Tuple[Sign, Sign, Sign]] = [
    (Sign.ARIES, Sign.LEO, Sign.SAGITTARIUS),
    (Sign.TAURUS, Sign.VIRGO, Sign.CAPRICORN),
    (Sign.GEMINI, Sign.LIBRA, Sign.AQUARIUS),
    (Sign.CANCER, Sign.SCORPIO, Sign.PISCES),
]

# =============================================================================
# PINDA SADHANA - RASHI MULTIPLIERS
# =============================================================================

RASHI_MULTIPLIERS: Dict[Sign, int] = {
    Sign.ARIES: 7, Sign.TAURUS: 10, Sign.GEMINI: 8, Sign.CANCER: 4,
    Sign.LEO: 10, Sign.VIRGO: 5, Sign.LIBRA: 7, Sign.SCORPIO: 8,
    Sign.SAGITTARIUS: 9, Sign.CAPRICORN: 5, Sign.AQUARIUS: 11, Sign.PISCES: 12,
}

GRAHA_MULTIPLIERS: Dict[Planet, int] = {
    Planet.SUN: 5, Planet.MOON: 5, Planet.MARS: 8,
    Planet.MERCURY: 5, Planet.JUPITER: 10, Planet.VENUS: 7, Planet.SATURN: 5,
}

# =============================================================================
# SHADBALA MINIMUM REQUIREMENTS (in Rupas)
# =============================================================================

SHADBALA_MINIMUMS: Dict[Planet, float] = {
    Planet.SUN: 6.5,    # BPHS Table 4: Sun = 6.5 Rupas (same as Jupiter)
    Planet.MOON: 6.0,
    Planet.MARS: 5.0,
    Planet.MERCURY: 7.0,
    Planet.JUPITER: 6.5,
    Planet.VENUS: 5.5,
    Planet.SATURN: 5.0,
}
