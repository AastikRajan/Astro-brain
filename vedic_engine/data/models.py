"""
Data Models for the Vedic Astrology Engine.
These dataclasses are the central data carriers between all modules.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# ─── Birth / Meta ──────────────────────────────────────────────────────────────

@dataclass
class BirthInfo:
    name: str
    date: str          # "YYYY-MM-DD"
    time: str          # "HH:MM:SS" (local)
    place: str
    latitude: float
    longitude: float
    timezone: float    # +5.5 for IST
    ayanamsa: float    # degrees at birth (e.g., 23.XX for Lahiri)
    ayanamsa_model: str = "Lahiri"


# ─── Planet Position ───────────────────────────────────────────────────────────

@dataclass
class PlanetPosition:
    planet: str                          # "SUN", "MOON", etc.
    longitude: float                     # sidereal absolute 0-360°
    sign_index: int                      # 0-11
    degree_in_sign: float                # 0-30
    nakshatra_index: int                 # 0-26
    nakshatra_name: str
    nakshatra_lord: str
    pada: int                            # 1-4
    is_retrograde: bool = False
    is_combust: bool = False
    speed: float = 0.0                   # deg/day (negative = retrograde)

    # KP layers
    kp_rashi_lord: str = ""
    kp_nak_lord: str = ""
    kp_sub_lord: str = ""
    kp_sub_sub_lord: str = ""

    # Computed later
    house_num: int = 0                   # 1-12 from lagna
    dignity: str = "neutral"            # exalted/own/friend/neutral/enemy/debilitated


# ─── House Cusp ────────────────────────────────────────────────────────────────

@dataclass
class HouseCusp:
    house_num: int       # 1-12
    longitude: float     # sidereal absolute 0-360°
    sign_index: int      # 0-11
    sign_name: str
    lord: str
    kp_nak_lord: str = ""
    kp_sub_lord: str = ""


# ─── Shadbala ──────────────────────────────────────────────────────────────────

@dataclass
class ShadbalaPlanet:
    planet: str
    sthana_bala: float       # position strength (shashtiamsas)
    dig_bala: float          # directional strength
    kala_bala: float         # time strength
    cheshta_bala: float      # motional strength
    naisargika_bala: float   # natural strength (constant)
    drik_bala: float         # aspectual strength
    total: float = 0.0
    rupas: float = 0.0       # total / 60
    minimum_required: float = 0.0
    ratio: float = 0.0       # rupas / minimum

    def compute(self):
        self.total = (self.sthana_bala + self.dig_bala + self.kala_bala +
                      self.cheshta_bala + self.naisargika_bala + self.drik_bala)
        self.rupas = self.total / 60.0
        if self.minimum_required > 0:
            self.ratio = self.rupas / self.minimum_required


# ─── Bhavabala ─────────────────────────────────────────────────────────────────

@dataclass
class BhavaStrength:
    house_num: int
    bhavadhipati_bala: float    # = lord's shadbala rupas
    bhava_dig_bala: float       # fixed table value
    bhava_drishti_bala: float   # net aspect score
    total: float = 0.0

    def compute(self):
        self.total = self.bhavadhipati_bala + self.bhava_dig_bala + self.bhava_drishti_bala


# ─── Ashtakvarga ───────────────────────────────────────────────────────────────

@dataclass
class AshtakavargaData:
    # bhinna[planet][sign_index] = bindu count (0-8)
    bhinna: Dict[str, List[int]] = field(default_factory=dict)
    # sarva[sign_index] = total across all planets (0-56)
    sarva: List[int] = field(default_factory=lambda: [0] * 12)
    # reduced after shodhana
    shodhya_pinda: Dict[str, int] = field(default_factory=dict)


# ─── Dasha Period ──────────────────────────────────────────────────────────────

@dataclass
class DashaPeriod:
    planet: str
    start_date: datetime
    end_date: datetime
    duration_years: float
    level: int = 1   # 1=Maha, 2=Antar, 3=Pratyantar, 4=Sookshma

    sub_periods: List['DashaPeriod'] = field(default_factory=list)

    @property
    def is_active(self) -> bool:
        now = datetime.now()
        return self.start_date <= now <= self.end_date

    @property
    def days_remaining(self) -> int:
        now = datetime.now()
        if self.end_date > now:
            return (self.end_date - now).days
        return 0


# ─── Yoga ──────────────────────────────────────────────────────────────────────

@dataclass
class Yoga:
    name: str
    category: str           # "raj", "dhana", "moksha", "health", etc.
    planets_involved: List[str]
    houses_involved: List[int]
    description: str
    strength: float = 0.0   # 0-1, based on planet strength
    is_cancelled: bool = False
    cancellation_reason: str = ""
    activating_dasha: str = ""  # which planet dasha activates this


# ─── Jaimini Karaka ────────────────────────────────────────────────────────────

@dataclass
class JaiminiKaraka:
    role: str        # AK, AmK, BK, MK, PK, GK, DK
    role_name: str   # Atma Karaka, Amatya Karaka, etc.
    planet: str
    degree: float    # degree within sign (used for ranking)
    signifies: str   # what this karaka represents


# ─── KP Signification ──────────────────────────────────────────────────────────

@dataclass
class KPSignification:
    planet: str
    houses_signified: List[int]   # combined from occupied + owned + star-lord houses
    star_lord: str
    sub_lord: str
    is_positive_for_career: bool = False
    is_positive_for_finance: bool = False
    is_positive_for_marriage: bool = False
    is_positive_for_health: bool = False


# ─── Transit Score ─────────────────────────────────────────────────────────────

@dataclass
class TransitScore:
    planet: str
    transit_sign: str
    transit_house_from_moon: int
    is_favorable: bool
    sav_score: int              # Sarvashtakvarga score for sign
    bav_score: int              # Planet's own BAV score for sign
    vedha_blocked: bool = False
    vedha_by: str = ""
    net_score: float = 0.0      # composite, 0-1


# ─── Full Chart ────────────────────────────────────────────────────────────────

@dataclass
class VedicChart:
    birth_info: BirthInfo
    lagna_sign: int              # 0-11
    lagna_degree: float          # sidereal absolute
    planets: Dict[str, PlanetPosition] = field(default_factory=dict)
    houses: List[HouseCusp] = field(default_factory=list)
    shadbala: Dict[str, ShadbalaPlanet] = field(default_factory=dict)
    bhavabala: List[BhavaStrength] = field(default_factory=list)
    ashtakvarga: Optional[AshtakavargaData] = None
    vimshottari: List[DashaPeriod] = field(default_factory=list)
    yogini: List[DashaPeriod] = field(default_factory=list)
    yogas: List[Yoga] = field(default_factory=list)
    karakas: List[JaiminiKaraka] = field(default_factory=list)
    kp_significations: Dict[str, KPSignification] = field(default_factory=dict)

    # Divisional charts: div_charts[D][planet] = sign_index
    div_charts: Dict[int, Dict[str, int]] = field(default_factory=dict)
