"""
27 Nakshatra Database.

Contains all classical attributes for the 27 lunar nakshatras:
- Span (sidereal degrees)
- Vimshottari dasha lord
- Gana (Deva / Manushya / Rakshasa)
- Varna (Brahmin / Kshatriya / Vaishya / Shudra)
- Yoni (animal symbol + gender)
- Nadi (Aadi / Madhya / Antya)
- Body part
- Guna (Sattvic / Rajasic / Tamasic)
- Category (Swift, Stable, etc.)

Sources: BPHS, Varaha Mihira, DrikPanchang classical tables.
"""
from __future__ import annotations
from typing import Dict, List, NamedTuple, Tuple, Optional


class Nakshatra(NamedTuple):
    index: int           # 0-based (Ashwini=0 … Revati=26)
    name: str
    deity: str
    symbol: str
    start_deg: float     # sidereal start longitude
    end_deg: float       # sidereal end longitude
    lord: str            # Vimshottari dasha lord
    gana: str            # "Deva" | "Manushya" | "Rakshasa"
    varna: str           # "Brahmin" | "Kshatriya" | "Vaishya" | "Shudra"
    yoni_animal: str     # animal name
    yoni_gender: str     # "M" (male) | "F" (female)
    nadi: str            # "Aadi" | "Madhya" | "Antya"
    body_part: str
    guna: str            # "S" (Sattvic) | "R" (Rajasic) | "T" (Tamasic)
    category: str        # Kshipra/Dhruva/Mridu/Tikshna/Chara/Ugra/Mishra/Sthira


NAKSHATRAS: List[Nakshatra] = [
    Nakshatra(0,  "Ashwini",         "Ashwini Kumars",  "Horse's head",             0.0,    13.333, "KETU",    "Deva",      "Kshatriya", "Horse",      "M", "Aadi",   "Head",                 "R", "Kshipra"),
    Nakshatra(1,  "Bharani",         "Yama",            "Yoni (womb)",              13.333, 26.667, "VENUS",   "Rakshasa",  "Shudra",    "Elephant",   "F", "Madhya", "Private parts",        "T", "Ugra"),
    Nakshatra(2,  "Krittika",        "Agni",            "Razor/knife",              26.667, 40.0,   "SUN",     "Deva",      "Vaishya",   "Sheep",      "M", "Antya",  "Face, eyes",           "S", "Mishra"),
    Nakshatra(3,  "Rohini",          "Prajapati/Brahma","Chariot",                  40.0,   53.333, "MOON",    "Manushya",  "Vaishya",   "Serpent",    "M", "Antya",  "Tongue",               "R", "Dhruva"),
    Nakshatra(4,  "Mrigashira",      "Soma (Moon)",     "Deer's head",              53.333, 66.667, "MARS",    "Rakshasa",  "Shudra",    "Deer",       "F", "Madhya", "Neck, throat",         "T", "Mridu"),
    Nakshatra(5,  "Ardra",           "Rudra",           "Teardrop/tree",            66.667, 80.0,   "RAHU",    "Rakshasa",  "Shudra",    "Goat",       "F", "Antya",  "Eye",                  "T", "Tikshna"),
    Nakshatra(6,  "Punarvasu",       "Aditi",           "Bow and quiver",           80.0,   93.333, "JUPITER", "Deva",      "Kshatriya", "Cat",        "F", "Aadi",   "Hands",                "S", "Chara"),
    Nakshatra(7,  "Pushya",          "Brihaspati",      "Cow's udder",              93.333, 106.667,"SATURN",  "Deva",      "Kshatriya", "Buffalo",    "M", "Madhya", "Chest, breasts",       "S", "Kshipra"),
    Nakshatra(8,  "Ashlesha",        "Naga (Serpent)",  "Coiled serpent",           106.667,120.0,  "MERCURY", "Rakshasa",  "Shudra",    "Cat",        "M", "Antya",  "Stomach",              "T", "Tikshna"),
    Nakshatra(9,  "Magha",           "Pitris",          "Throne room",              120.0,  133.333,"KETU",    "Rakshasa",  "Kshatriya", "Lion",       "F", "Aadi",   "Heart",                "T", "Ugra"),
    Nakshatra(10, "Purva Phalguni",  "Bhaga",           "Front legs of bed",        133.333,146.667,"VENUS",   "Manushya",  "Vaishya",   "Elephant",   "F", "Madhya", "Thighs",               "T", "Ugra"),
    Nakshatra(11, "Uttara Phalguni", "Aryaman",         "Back legs of bed",         146.667,160.0,  "SUN",     "Deva",      "Kshatriya", "Horse",      "F", "Madhya", "Finger",               "S", "Sthira"),
    Nakshatra(12, "Hasta",           "Savitar",         "Hand",                     160.0,  173.333,"MOON",    "Manushya",  "Vaishya",   "Buffalo",    "F", "Aadi",   "Palm",                 "S", "Kshipra"),
    Nakshatra(13, "Chitra",          "Tvashtar",        "Bright jewel/art",         173.333,186.667,"MARS",    "Rakshasa",  "Kshatriya", "Cat",        "F", "Madhya", "Heart",                "S", "Mridu"),
    Nakshatra(14, "Swati",           "Vayu",            "Young plant",              186.667,200.0,  "RAHU",    "Manushya",  "Vaishya",   "Buffalo",    "M", "Aadi",   "Skin",                 "T", "Chara"),
    Nakshatra(15, "Vishakha",        "Indra-Agni",      "Triumphal arch",           200.0,  213.333,"JUPITER", "Rakshasa",  "Vaishya",   "Tiger",      "M", "Antya",  "Rectum",               "T", "Mishra"),
    Nakshatra(16, "Anuradha",        "Mitra",           "Lotus",                    213.333,226.667,"SATURN",  "Deva",      "Vaishya",   "Deer",       "F", "Madhya", "Heart",                "S", "Mridu"),
    Nakshatra(17, "Jyeshtha",        "Indra",           "Circular amulet",          226.667,240.0,  "MERCURY", "Manushya",  "Kshatriya", "Elephant",   "F", "Antya",  "Lower back",           "T", "Tikshna"),
    Nakshatra(18, "Moola",           "Nirriti",         "Tied bunch",               240.0,  253.333,"KETU",    "Deva",      "Shudra",    "Dog",        "M", "Antya",  "Genitals",             "T", "Tikshna"),
    Nakshatra(19, "Purva Ashadha",   "Apah",            "Front legs of bed",        253.333,266.667,"VENUS",   "Rakshasa",  "Vaishya",   "Dog",        "F", "Madhya", "Reproductive organs",  "T", "Ugra"),
    Nakshatra(20, "Uttara Ashadha",  "Vishvadevas",     "Back legs of bed",         266.667,280.0,  "SUN",     "Deva",      "Kshatriya", "Elephant",   "M", "Antya",  "Hips",                 "S", "Sthira"),
    Nakshatra(21, "Shravana",        "Vishnu",          "Ear",                      280.0,  293.333,"MOON",    "Deva",      "Kshatriya", "Monkey",     "M", "Antya",  "Ears",                 "R", "Chara"),
    Nakshatra(22, "Dhanishta",       "Eight Vasus",     "Drum",                     293.333,306.667,"MARS",    "Deva",      "Kshatriya", "Lion",       "M", "Antya",  "Knees",                "R", "Chara"),
    Nakshatra(23, "Shatabhisha",     "Varuna",          "Empty circle",             306.667,320.0,  "RAHU",    "Manushya",  "Vaishya",   "Horse",      "M", "Aadi",   "Skin (all over)",      "R", "Chara"),
    Nakshatra(24, "Purva Bhadra",    "Ajaikapad (Varaha)","Stage bed",             320.0,  333.333,"JUPITER", "Rakshasa",  "Kshatriya", "Elephant",   "M", "Madhya", "Thighs",               "R", "Ugra"),
    Nakshatra(25, "Uttara Bhadra",   "Ahirbudhnya",     "Stage bed",               333.333,346.667,"SATURN",  "Deva",      "Kshatriya", "Elephant",   "F", "Antya",  "Feet",                 "S", "Sthira"),
    Nakshatra(26, "Revati",          "Pushan",          "Fish",                     346.667,360.0,  "MERCURY", "Manushya",  "Vaishya",   "Frog",       "M", "Antya",  "Feet",                 "S", "Mridu"),
]

# Quick lookup by index
_BY_INDEX: Dict[int, Nakshatra] = {n.index: n for n in NAKSHATRAS}

# Quick lookup by name (lower-case, no spaces)
_BY_NAME: Dict[str, Nakshatra] = {n.name.lower().replace(" ", ""): n for n in NAKSHATRAS}


def get_nakshatra(longitude: float) -> Nakshatra:
    """Return the Nakshatra for a given sidereal longitude (0-360°)."""
    lon = longitude % 360.0
    idx = int(lon / (360.0 / 27)) % 27
    return _BY_INDEX[idx]


def get_nakshatra_index(longitude: float) -> int:
    """Return 0-based nakshatra index for a sidereal longitude."""
    return int((longitude % 360.0) / (360.0 / 27)) % 27


def get_nakshatra_by_index(idx: int) -> Nakshatra:
    """Return Nakshatra by 0-based index."""
    return _BY_INDEX[idx % 27]


def get_nakshatra_by_name(name: str) -> Optional[Nakshatra]:
    """Return Nakshatra by name (case-insensitive, ignores spaces)."""
    key = name.lower().replace(" ", "")
    return _BY_NAME.get(key)


def nakshatra_pada(longitude: float) -> Tuple[Nakshatra, int]:
    """
    Return (Nakshatra, pada) for a sidereal longitude.
    Pada is 1-4, dividing each nakshatra's 13°20' into four 3°20' segments.
    """
    lon = longitude % 360.0
    nak_size = 360.0 / 27.0  # ≈ 13.3333°
    pada_size = nak_size / 4.0  # ≈ 3.3333°
    idx = int(lon / nak_size) % 27
    offset = lon - idx * nak_size
    pada = int(offset / pada_size) + 1
    pada = min(pada, 4)
    return _BY_INDEX[idx], pada


# ── Yoni compatibility table ───────────────────────────────────────────────
# Animals that are friendly, neutral, inimical pairs
# Score: same=4, friendly=3, neutral=2, inimical=1, hostile=0
YONI_COMPATIBILITY: Dict[Tuple[str, str], int] = {}

# Hostile pairs (classical) — opposite-sex of same animal also matters but  
# the primary inimical pairs are:
_YONI_HOSTILE: List[Tuple[str, str]] = [
    ("Horse", "Buffalo"),
    ("Elephant", "Lion"),
    ("Sheep", "Monkey"),
    ("Serpent", "Mongoose"),  # Mongoose not in list but enemy
    ("Dog", "Deer"),
    ("Cat", "Mouse"),
    ("Tiger", "Deer"),
    ("Goat", "Tiger"),
]

_YONI_INIMICAL: List[Tuple[str, str]] = [
    ("Horse", "Lion"),
    ("Elephant", "Buffalo"),
    ("Sheep", "Dog"),
    ("Cat", "Monkey"),
]

_YONI_FRIENDLY: List[Tuple[str, str]] = [
    ("Horse", "Elephant"),
    ("Dog", "Lion"),
    ("Sheep", "Deer"),
    ("Monkey", "Frog"),
    ("Cat", "Deer"),
    ("Goat", "Frog"),
]


def yoni_score(animal_a: str, animal_b: str) -> int:
    """
    Compute Yoni compatibility score (0-4) between two nakshatra animals.
    Score: same=4, friendly=3, neutral=2, inimical=1, hostile=0
    """
    if animal_a == animal_b:
        return 4
    pair = frozenset({animal_a, animal_b})
    for a, b in _YONI_HOSTILE:
        if pair == frozenset({a, b}):
            return 0
    for a, b in _YONI_INIMICAL:
        if pair == frozenset({a, b}):
            return 1
    for a, b in _YONI_FRIENDLY:
        if pair == frozenset({a, b}):
            return 3
    return 2  # neutral
