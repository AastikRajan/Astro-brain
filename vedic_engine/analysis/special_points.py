"""
Special Sensitive Points (Upagrahas and Special Lagnas).

Computed for a birth chart:
  Gulika (Mandi)   – shadow planet, son of Saturn; very malefic
  Hora Lagna       – for wealth/finance analysis
  Ghati Lagna      – for power and authority
  Indu Lagna       – alternative wealth indicator (Parashara system)

Tarabala (natal-star to transit-star navamsa) is also computed here.

Reference: BPHS Ch. 4 (Gulika), BPHS Hora/Ghati Lagna, Jataka Parijata.
"""
from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional

from vedic_engine.core.coordinates import normalize, nakshatra_of, sign_of

# Swiss Ephemeris-powered precise sunrise/sunset (falls back to NOAA, then 6.0/18.0)
try:
    from vedic_engine.core.sunrise_utils import get_sunrise_sunset_hours
    _HAS_SUNRISE_API = True
except ImportError:
    _HAS_SUNRISE_API = False


# ─── Gulika (Mandi) ───────────────────────────────────────────────
# Day is split into 8 equal parts (Praharas). Gulika owns a specific
# part for each weekday. We compute the time-start of that part and
# then find the Ascendant longitude at that moment.
#
# Weekday: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
# (note: we remap Python's Mon=0 weekday to Sun=0)

# Which portion-index (0-7) Gulika occupies during the day per weekday
GULIKA_DAY_PORTION: Dict[int, int] = {
    0: 6,   # Sun  → 7th portion  (index 6)
    1: 5,   # Mon  → 6th
    2: 4,   # Tue  → 5th
    3: 3,   # Wed  → 4th
    4: 2,   # Thu  → 3rd
    5: 1,   # Fri  → 2nd
    6: 0,   # Sat  → 1st
}

# Night portions (counted from sunset)
GULIKA_NIGHT_PORTION: Dict[int, int] = {
    0: 2,
    1: 1,
    2: 0,
    3: 6,
    4: 5,
    5: 4,
    6: 3,
}


def _weekday_sun_zero(birth_dt: datetime) -> int:
    """Convert Python weekday (Mon=0) to Sun=0 system."""
    return {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}[birth_dt.weekday()]


def compute_gulika(
    birth_dt: datetime,
    lagna_lon: float,
    sunrise_hour: float = 6.0,
    sunset_hour: float = 18.0,
) -> float:
    """
    Compute Gulika (Mandi) sidereal longitude.

    Method:
      1. Find which 1/8 portion of the day/night Gulika occupies.
      2. Compute clock-time at the START of that portion.
      3. Ascendant moves ~1°/4min (15°/hr). Offset lagna_lon by
         the time difference from birth time.

    Returns approximate sidereal longitude (0-360).
    """
    hour = birth_dt.hour + birth_dt.minute / 60.0 + birth_dt.second / 3600.0
    wd   = _weekday_sun_zero(birth_dt)

    day_dur   = sunset_hour - sunrise_hour          # e.g. 12 hrs
    night_dur = 24.0 - day_dur

    is_day = sunrise_hour <= hour < sunset_hour

    if is_day:
        portion_idx = GULIKA_DAY_PORTION.get(wd, 6)
        portion_dur = day_dur / 8.0                 # hours per portion
        gulika_start_time = sunrise_hour + portion_idx * portion_dur
    else:
        portion_idx = GULIKA_NIGHT_PORTION.get(wd, 2)
        portion_dur = night_dur / 8.0
        night_start = sunset_hour
        gulika_start_time = (night_start + portion_idx * portion_dur) % 24.0

    # Offset: how many hours before/after birth the Gulika moment is
    time_diff_hours = gulika_start_time - hour

    # Lagna moves 360° in 24 sidereal hours ≈ 15°/hr
    lagna_offset = time_diff_hours * 15.0
    gulika_lon = normalize(lagna_lon + lagna_offset)
    return round(gulika_lon, 3)


# ─── Hora Lagna ───────────────────────────────────────────────────
# "Hora" = 1 hour. The Hora Lagna advances ~30° (1 sign) per hora
# from the Lagna position at sunrise.

def compute_hora_lagna(
    birth_dt: datetime,
    lagna_lon: float,
    sunrise_hour: float = 6.0,
) -> float:
    """
    Compute Hora Lagna sidereal longitude.
    Hora Lagna = Lagna + (hours since sunrise) × 30°
    Used as an alternate lagna for wealth and financial analysis.
    """
    hour = birth_dt.hour + birth_dt.minute / 60.0
    hours_since_sunrise = hour - sunrise_hour
    hora_lon = normalize(lagna_lon + hours_since_sunrise * 30.0)
    return round(hora_lon, 3)


# ─── Ghati Lagna ──────────────────────────────────────────────────
# 1 Ghati = 24 minutes. Lagna rises ~1.25°/minute = 30°/ghati.
# Used for gauging native's authority and kingly/powerful periods.

def compute_ghati_lagna(
    birth_dt: datetime,
    lagna_lon: float,
    sunrise_hour: float = 6.0,
) -> float:
    """
    Compute Ghati Lagna sidereal longitude.
    Ghati Lagna = Lagna + (minutes since sunrise) × 1.25°
    """
    hour = birth_dt.hour + birth_dt.minute / 60.0
    minutes_since_sunrise = (hour - sunrise_hour) * 60.0
    ghati_lon = normalize(lagna_lon + minutes_since_sunrise * 1.25)
    return round(ghati_lon, 3)


# ─── Indu Lagna ───────────────────────────────────────────────────
# Parashara's wealth indicator.
# The 9th house lord from Lagna has a point value; so does the 9th
# lord from Moon. Sum them, mod 12 from Lagna → Indu Lagna sign.
#
# Point values (Parashara): Sun=30, Moon=16, Mars=6, Mer=8, Jup=10,
# Ven=12, Sat=1. Divide the sum by 12 and take the remainder as the
# sign offset from the Moon sign; add Moon longitude offset.

INDU_WEIGHTS: Dict[str, int] = {
    "SUN": 30, "MOON": 16, "MARS": 6, "MERCURY": 8,
    "JUPITER": 10, "VENUS": 12, "SATURN": 1,
}


def compute_indu_lagna(
    lagna_lon: float,
    moon_lon: float,
    house_lords: Dict[int, str],        # {house_num: planet_name}
) -> float:
    """
    Compute Indu Lagna sidereal longitude (Parashara method).

    Formula:
      1. Get 9th lord from Lagna → w1 = its Indu weight
      2. Get 9th lord from Moon sign → w2 = its Indu weight
      3. total = (w1 + w2) % 12
      4. Indu Lagna = Moon longitude + total × 30°

    Returns approximate sidereal longitude.
    """
    # 9th lord from Lagna
    l9_lagna = house_lords.get(9, "JUPITER")
    w1 = INDU_WEIGHTS.get(l9_lagna, 10)

    # 9th lord from Moon sign
    moon_sign = sign_of(moon_lon)
    # lagna_sign = sign_of(lagna_lon)
    # The 9th from Moon: house-lord of (moon_sign + 8) % 12
    from vedic_engine.config import SIGN_LORDS, Sign as _Sign
    ninth_from_moon_sign = (moon_sign + 8) % 12
    l9_moon_planet = SIGN_LORDS.get(_Sign(ninth_from_moon_sign))
    l9_moon = l9_moon_planet.name if l9_moon_planet else "JUPITER"
    w2 = INDU_WEIGHTS.get(l9_moon, 10)

    total_offset = (w1 + w2) % 12
    indu_lon = normalize(moon_lon + total_offset * 30.0)
    return round(indu_lon, 3)


# ─── Tarabala ─────────────────────────────────────────────────────
# Relationship of the current transit Moon nakshatra to the natal
# Moon nakshatra. The 9-nakshatra cycle from the natal Moon repeats
# 3 times; each has a benefit/harm classification.

TARA_NAMES: List[str] = [
    "Janma",      # 1 – birth nakshatra – mixed (can cause illness/events)
    "Sampat",     # 2 – wealth / prosperity
    "Vipat",      # 3 – danger/loss
    "Kshema",     # 4 – well-being
    "Pratyak",    # 5 – obstacle
    "Sadhana",    # 6 – accomplishment / beneficial
    "Naidhana",   # 7 – death-like / most harmful
    "Mitra",      # 8 – friend / beneficial
    "Parama-Mitra", # 9 – best friend / most beneficial
]

TARA_FAVORABLE = frozenset({2, 4, 6, 8, 9})   # by index (1-based → index+1)
TARA_HARMFUL   = frozenset({3, 5, 7})
TARA_MIXED     = frozenset({1})


def compute_tarabala(
    natal_moon_nak: int,       # 0-26
    transit_moon_nak: int,     # 0-26
) -> Dict:
    """
    Compute Tarabala for the current transit Moon.

    Args:
        natal_moon_nak:   birth nakshatra index (0 = Ashwini)
        transit_moon_nak: transit Moon's nakshatra index

    Returns dict with:
        tara_num:    1-9 Tara number
        tara_name:   Tara name
        quality:     'favorable' | 'harmful' | 'mixed'
        score:       float -1.0 to +1.0
    """
    diff = (transit_moon_nak - natal_moon_nak) % 27
    tara_idx_0based = diff % 9          # 0-8
    tara_num = tara_idx_0based + 1      # 1-9

    tara_name = TARA_NAMES[tara_idx_0based]

    if tara_num in TARA_FAVORABLE:
        quality = "favorable"
        score   = 0.5 + (0.5 if tara_num == 9 else 0.0)  # Parama-Mitra = 1.0
    elif tara_num in TARA_HARMFUL:
        quality = "harmful"
        score   = -0.5 + (-0.5 if tara_num == 7 else 0.0)  # Naidhana = -1.0
    else:
        quality = "mixed"
        score   = 0.0

    return {
        "tara_num":  tara_num,
        "tara_name": tara_name,
        "quality":   quality,
        "score":     score,
    }


# ─── Chandrabala (Moon strength from transit Moon) ────────────────

CHANDRABALA_GOOD_HOUSES = frozenset({1, 3, 6, 7, 10, 11})

def compute_chandrabala(
    natal_moon_sign: int,    # 0-11
    transit_moon_sign: int,  # 0-11
) -> Dict:
    """
    Chandrabala: strength of the transit Moon relative to natal Moon position.
    Houses 1, 3, 6, 7, 10, 11 from natal Moon are considered good.
    Returns score from 0 to 1.
    """
    house_from_moon = (transit_moon_sign - natal_moon_sign) % 12 + 1
    good = house_from_moon in CHANDRABALA_GOOD_HOUSES
    score = 0.75 if good else 0.25
    return {
        "house_from_natal_moon": house_from_moon,
        "is_good":               good,
        "score":                 score,
    }


# ─── True Mandi (32-part division) ───────────────────────────────
# Mandi uses a 32-part division (not 8-part like Gulika).
# Weekday (Sun=0..Sat=6) determines which 32nd-part it rises in.
# Research source: "Gulika / Mandi computational teaching document"
#   Day parts (Sun→Sat):   26, 22, 18, 14, 10, 6, 2
#   Night parts (Sun→Sat): 10,  6,  2, 30, 26, 22, 18

MANDI_DAY_PART:   Dict[int, int] = {0: 26, 1: 22, 2: 18, 3: 14, 4: 10, 5: 6,  6: 2}
MANDI_NIGHT_PART: Dict[int, int] = {0: 10, 1: 6,  2: 2,  3: 30, 4: 26, 5: 22, 6: 18}


def compute_mandi(
    birth_dt: datetime,
    lagna_lon: float,
    sunrise_hour: float = 6.0,
    sunset_hour: float  = 18.0,
) -> float:
    """
    Compute true Mandi longitude (32-part method, distinct from Gulika 8-part).
    Returns the Ascendant degree at the moment Mandi rises.
    """
    hour = birth_dt.hour + birth_dt.minute / 60.0 + birth_dt.second / 3600.0
    wd   = _weekday_sun_zero(birth_dt)

    day_dur   = sunset_hour - sunrise_hour
    night_dur = 24.0 - day_dur
    is_day    = sunrise_hour <= hour < sunset_hour

    if is_day:
        part_idx  = MANDI_DAY_PART.get(wd, 26)
        part_dur  = day_dur / 32.0
        mandi_time = sunrise_hour + (part_idx - 1) * part_dur
    else:
        part_idx  = MANDI_NIGHT_PART.get(wd, 10)
        part_dur  = night_dur / 32.0
        mandi_time = (sunset_hour + (part_idx - 1) * part_dur) % 24.0

    time_diff  = mandi_time - hour
    mandi_lon  = normalize(lagna_lon + time_diff * 15.0)
    return round(mandi_lon, 3)


# ─── 5 Upagrahas (Aprakasha Sub-Planets from Sun) ─────────────────
# All are malefic shadow points derived from Sun's longitude.
# Source: "Aprakasha upagraha computational note" (special_points lit.)
#
#   Dhuma       = Sun + 133°20'
#   Vyatipata   = 360° − Dhuma
#   Parivesha   = 180° + Vyatipata
#   Indrachapa  = 360° − Parivesha
#   Upaketu     = Indrachapa + 16°40'

def compute_upagrahas(sun_lon: float) -> Dict[str, float]:
    """
    Compute the 5 Aprakasha (non-luminous) upagrahas from Sun longitude.
    All results in degrees [0, 360).
    """
    dhuma      = normalize(sun_lon + 133.0 + 20.0 / 60.0)    # 133°20'
    vyatipata  = normalize(360.0 - dhuma)
    parivesha  = normalize(180.0 + vyatipata)
    indrachapa = normalize(360.0 - parivesha)
    upaketu    = normalize(indrachapa + 16.0 + 40.0 / 60.0)  # 16°40'
    return {
        "dhuma":      round(dhuma,      3),
        "vyatipata":  round(vyatipata,  3),
        "parivesha":  round(parivesha,  3),
        "indrachapa": round(indrachapa, 3),
        "upaketu":    round(upaketu,    3),
    }


# ─── Yogi, Avayogi, Duplicate Yogi ────────────────────────────────
# Source: detailed Yogi point instructional writeup.
#   Yogi point   = (Sun lon + Moon lon + 93°20') mod 360
#   Avayogi pt   = (Yogi point + 186°40') mod 360
#   Yogi planet  = nakshatra lord of Yogi point
#   Dup. Yogi    = sign lord of Yogi point
#   Avayogi pl.  = nakshatra lord of Avayogi point

_NAK_LORDS_9 = [
    "KETU","VENUS","SUN","MOON","MARS","RAHU",
    "JUPITER","SATURN","MERCURY",
]  # repeating sequence for 27 nakshatras

def _nak_lord_from_lon(lon: float) -> str:
    nak_idx = int(lon / (360.0 / 27)) % 27
    return _NAK_LORDS_9[nak_idx % 9]


def compute_yogi_avayogi(sun_lon: float, moon_lon: float) -> Dict[str, any]:
    """
    Compute Yogi, Duplicate Yogi, and Avayogi points and their ruling planets.
    """
    from vedic_engine.config import SIGN_LORDS, Sign as _Sign
    sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                  "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

    yogi_pt    = normalize(sun_lon + moon_lon + 93.0 + 20.0 / 60.0)   # 93°20'
    avayogi_pt = normalize(yogi_pt + 186.0 + 40.0 / 60.0)             # +186°40'

    yogi_planet    = _nak_lord_from_lon(yogi_pt)
    avayogi_planet = _nak_lord_from_lon(avayogi_pt)

    yogi_sign_idx  = int(yogi_pt / 30) % 12
    dup_yogi_enum  = SIGN_LORDS.get(_Sign(yogi_sign_idx))
    dup_yogi       = dup_yogi_enum.name if dup_yogi_enum else "JUPITER"

    return {
        "yogi_point":       round(yogi_pt, 3),
        "yogi_sign":        sign_names[yogi_sign_idx],
        "yogi_planet":      yogi_planet,
        "duplicate_yogi":   dup_yogi,
        "avayogi_point":    round(avayogi_pt, 3),
        "avayogi_sign":     sign_names[int(avayogi_pt / 30) % 12],
        "avayogi_planet":   avayogi_planet,
    }


# ─── Bhrigu Bindu ─────────────────────────────────────────────────
# Midpoint on the Rahu–Moon arc.
# Formula (zodiac-safe):
#   d  = (Moon_lon − Rahu_lon) mod 360
#   BB = (Rahu_lon + d/2) mod 360
# Sensitive degree: transits/aspects over BB correlate with eventful periods.

def compute_bhrigu_bindu(moon_lon: float, rahu_lon: float) -> float:
    """
    Compute Bhrigu Bindu longitude (midpoint of Rahu–Moon axis).
    Returns sidereal longitude in degrees [0, 360).
    """
    d  = (moon_lon - rahu_lon) % 360.0
    bb = normalize(rahu_lon + d / 2.0)
    return round(bb, 3)


def check_bhrigu_bindu_transit(
    bb_degree: float,
    transit_planet_lons: Dict[str, float],
    natal_house_map: Optional[Dict[str, int]] = None,
) -> Dict:
    """
    Check whether slow-moving planets are in triggering orb of Bhrigu Bindu.

    Classical rule (ad.md §5.4): Jupiter, Saturn, and Rahu/Ketu transiting
    over the Bhrigu Bindu correlate with karmic event activation.

      Exact zone    : within ±1°  → strong activation (strength ~1.0)
      Influence zone: within ±5°  → approaching activation (strength scaled
                                     linearly from 0.20 at 5° to 1.0 at 0°)
      Beyond 5°     : no activation for that planet

    Args:
        bb_degree          : Bhrigu Bindu longitude in degrees [0,360)
        transit_planet_lons: {planet_name: longitude} for current transits
        natal_house_map    : Optional {longitude_deg: house_num} for sign-to-house mapping

    Returns:
        Dict with:
          triggered       : bool — at least one planet in exact zone
          approaching     : bool — at least one planet in influence zone but not exact
          activating_planets: list of dicts per planet in range
          bb_degree       : float
    """
    # Trigger planets — classical slow-movers per Bhrigu Nadi tradition
    TRIGGER_PLANETS = {"JUPITER", "SATURN", "RAHU", "KETU"}
    EXACT_ORB = 1.0      # degrees — strong trigger
    INFLUENCE_ORB = 5.0  # degrees — building / separating influence

    activating = []
    triggered = False
    approaching = False

    for planet, lon in transit_planet_lons.items():
        p = planet.upper()
        if p not in TRIGGER_PLANETS:
            continue

        # Arc distance (shortest path around zodiac)
        arc = abs((lon - bb_degree + 180.0) % 360.0 - 180.0)

        if arc <= EXACT_ORB:
            strength = 1.0
            zone = "EXACT"
            triggered = True
        elif arc <= INFLUENCE_ORB:
            # Linear decay from 1.0 at orb=1° to 0.20 at orb=5°
            strength = round(1.0 - (arc - EXACT_ORB) / (INFLUENCE_ORB - EXACT_ORB) * 0.80, 3)
            zone = "INFLUENCE"
            approaching = True
        else:
            continue

        activating.append({
            "planet":       p,
            "transit_lon":  round(lon, 2),
            "bb_degree":    round(bb_degree, 2),
            "arc_degrees":  round(arc, 2),
            "zone":         zone,
            "strength":     strength,
            "note": (
                f"{p} is {'exactly' if zone == 'EXACT' else 'approaching'} "
                f"Bhrigu Bindu ({bb_degree:.1f}°) — orb {arc:.1f}°"
            ),
        })

    return {
        "bb_degree":          round(bb_degree, 2),
        "triggered":          triggered,
        "approaching":        approaching,
        "activating_planets": activating,
        "transit_summary": (
            f"{len(activating)} planet(s) in BB orb"
            if activating else "No slow-moving planet in Bhrigu Bindu orb"
        ),
    }


# ─── Drekkana Nature (Sarpa / Pakshi classification) ──────────────
# Each 10° decanate of every sign has a traditional "nature" label.
# Index: (sign_index 0-11, drekkana 0=first/1=second/2=third)
# Source: "Drekkana nature table" classical / Phaladeepika tradition.

_SIGN_NAMES_12 = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                   "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# (sign_idx, drek_idx) → nature label string
DREKKANA_NATURE: Dict[tuple, str] = {
    # Aries
    (0,0):"Narada", (0,1):"Agni", (0,2):"Chatuspada",
    # Taurus
    (1,0):"Chatuspada", (1,1):"Sarpa/Chatuspada", (1,2):"Manushya",
    # Gemini
    (2,0):"Manushya", (2,1):"Ayudha/Pakshi", (2,2):"Manushya",
    # Cancer
    (3,0):"Manushya", (3,1):"Sarpa", (3,2):"Sarpa",
    # Leo
    (4,0):"Ayudha/Pakshi/Chatuspada", (4,1):"Chatuspada", (4,2):"Chatuspada",
    # Virgo
    (5,0):"Pakshi", (5,1):"Pakshi", (5,2):"Pakshi",
    # Libra
    (6,0):"Pakshi", (6,1):"Pakshi", (6,2):"Chatuspada",
    # Scorpio
    (7,0):"Sarpa", (7,1):"Sarpa/Pasha", (7,2):"Manushya",
    # Sagittarius
    (8,0):"Pakshi", (8,1):"Manushya", (8,2):"Chatuspada",
    # Capricorn
    (9,0):"Pakshi/Chatuspada", (9,1):"Chatuspada/Manushya", (9,2):"Manushya",
    # Aquarius
    (10,0):"Manushya", (10,1):"Manushya", (10,2):"Chatuspada",
    # Pisces
    (11,0):"Manushya", (11,1):"Manushya", (11,2):"Sarpa",
}

SARPA_DREKKANAS  = {k for k, v in DREKKANA_NATURE.items() if "Sarpa"  in v}
PAKSHI_DREKKANAS = {k for k, v in DREKKANA_NATURE.items() if "Pakshi" in v}


def classify_drekkana(longitude: float) -> Dict[str, any]:
    """
    Return the drekkana classification for a given planetary longitude.
    Returns sign, drekkana index (0/1/2), nature, and whether Sarpa/Pakshi.
    """
    sign_idx  = int(longitude / 30) % 12
    deg       = longitude % 30
    drek_idx  = int(deg / 10)        # 0 = first 0-10°, 1 = 10-20°, 2 = 20-30°
    key       = (sign_idx, drek_idx)
    nature    = DREKKANA_NATURE.get(key, "Manushya")
    return {
        "sign":       _SIGN_NAMES_12[sign_idx],
        "drekkana":   drek_idx + 1,      # 1/2/3 (human-readable)
        "nature":     nature,
        "is_sarpa":   key in SARPA_DREKKANAS,
        "is_pakshi":  key in PAKSHI_DREKKANAS,
        "health_risk": key in SARPA_DREKKANAS,  # Sarpa = health/danger risk
    }


# ─── Main API ─────────────────────────────────────────────────────

def compute_all_special_points(
    birth_dt: datetime,
    lagna_lon: float,
    moon_lon: float,
    house_lords: Optional[Dict[int, str]] = None,
    sun_lon: float = 0.0,
    rahu_lon: float = 0.0,
    latitude: float = 0.0,
    longitude: float = 0.0,
    tz_offset: float = 5.5,
) -> Dict:
    """
    Compute all special sensitive points for a birth chart.

    Now uses SWE-precise sunrise/sunset (via get_sunrise_sunset_hours) for
    Gulika, Mandi, Hora Lagna, and Ghati Lagna instead of hardcoded 6am/6pm.

    Args:
        birth_dt:    birth datetime
        lagna_lon:   Ascendant longitude (sidereal)
        moon_lon:    Moon longitude (sidereal)
        house_lords: {house_num: planet_name} (needed for Indu Lagna)
        sun_lon:     Sun longitude (needed for Upagrahas, Yogi)
        rahu_lon:    Rahu longitude (needed for Bhrigu Bindu)
        latitude:    birth latitude (for precise sunrise)
        longitude:   birth longitude (for precise sunrise)
        tz_offset:   UTC offset hours (for precise sunrise)

    Returns dict with all computed points and their sign placements.
    """
    from vedic_engine.core.coordinates import sign_of as _sign_of
    sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                  "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

    # ── Compute real sunrise/sunset for this birth date & location ──
    sunrise_h, sunset_h = 6.0, 18.0
    if _HAS_SUNRISE_API and (latitude != 0.0 or longitude != 0.0):
        try:
            sunrise_h, sunset_h = get_sunrise_sunset_hours(
                birth_dt, latitude, longitude, tz_offset
            )
        except Exception:
            pass  # keep defaults

    gulika      = compute_gulika(birth_dt, lagna_lon, sunrise_h, sunset_h)
    mandi       = compute_mandi(birth_dt, lagna_lon, sunrise_h, sunset_h)
    hora_lagna  = compute_hora_lagna(birth_dt, lagna_lon, sunrise_h)
    ghati_lagna = compute_ghati_lagna(birth_dt, lagna_lon, sunrise_h)
    indu_lagna  = compute_indu_lagna(lagna_lon, moon_lon, house_lords or {})

    def _describe(lon: float) -> Dict:
        s = _sign_of(lon)
        return {"longitude": lon, "sign": sign_names[s], "sign_idx": s}

    result = {
        "gulika":      _describe(gulika),
        "mandi":       _describe(mandi),
        "hora_lagna":  _describe(hora_lagna),
        "ghati_lagna": _describe(ghati_lagna),
        "indu_lagna":  _describe(indu_lagna),
    }

    # Upagrahas (from Sun)
    if sun_lon:
        upagrahas = compute_upagrahas(sun_lon)
        result["upagrahas"] = {k: _describe(v) for k, v in upagrahas.items()}
        # Yogi / Avayogi
        result["yogi_avayogi"] = compute_yogi_avayogi(sun_lon, moon_lon)

    # Bhrigu Bindu (from Rahu + Moon)
    if rahu_lon:
        bb = compute_bhrigu_bindu(moon_lon, rahu_lon)
        result["bhrigu_bindu"] = _describe(bb)

    # Lagna drekkana nature
    result["lagna_drekkana"] = classify_drekkana(lagna_lon)

    return result
