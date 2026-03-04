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
# Formula (Research File 2 / BPHS): HL = Sun_lon + minutes_from_sunrise × 0.5°
# Anchor = Sun longitude (advances 30°/hr = 0.5°/min from Sun at sunrise).
# FIX 2026-03-02: was anchoring at Lagna; correct anchor is Sun longitude.

def compute_hora_lagna(
    birth_dt: datetime,
    sun_lon: float,
    sunrise_hour: float = 6.0,
) -> float:
    """
    Compute Hora Lagna sidereal longitude.
    HL = Sun_lon + (minutes_from_sunrise) × 0.5°
    Advances at 30°/hr (1 sign/hora) anchored to Sun at sunrise.
    Used for wealth and financial analysis.
    FIX 2026-03-02: anchor corrected from Lagna to Sun longitude.
    """
    hour = birth_dt.hour + birth_dt.minute / 60.0
    minutes_since_sunrise = (hour - sunrise_hour) * 60.0
    hora_lon = normalize(sun_lon + minutes_since_sunrise * 0.5)
    return round(hora_lon, 3)


# ─── Ghati Lagna ──────────────────────────────────────────────────
# Formula (Research File 2): GL = Sun_lon + minutes_from_sunrise × 1.25°
# (30° per Ghati = 30°/24min = 1.25°/min)
# Used for gauging native's authority and kingly/powerful periods.
# FIX 2026-03-02: anchor corrected from Lagna to Sun longitude.

def compute_ghati_lagna(
    birth_dt: datetime,
    sun_lon: float,
    sunrise_hour: float = 6.0,
) -> float:
    """
    Compute Ghati Lagna sidereal longitude.
    GL = Sun_lon + (minutes_from_sunrise) × 1.25°
    Advances 30° per Ghati (24 minutes of clock time).
    FIX 2026-03-02: anchor corrected from Lagna to Sun longitude.
    """
    hour = birth_dt.hour + birth_dt.minute / 60.0
    minutes_since_sunrise = (hour - sunrise_hour) * 60.0
    ghati_lon = normalize(sun_lon + minutes_since_sunrise * 1.25)
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


# ─── Varnada Lagna ─────────────────────────────────────────────────────────
# Primary domain: Varna (social class), vocational trajectory, karmic burdens.
# Research File 2 (Part C.3) — sign-parity vector algorithm.
# ADDED 2026-03-02: Phase 1B.

_ODD_SIGNS_SET = {0, 2, 4, 6, 8, 10}   # Aries, Gemini, Leo, Libra, Sag, Aquarius

def compute_varnada_lagna(lagna_lon: float, hora_lagna_lon: float) -> float:
    """
    Compute Varnada Lagna using the sign-parity vector algorithm (Research File 2).

    Steps:
      1. Count L_count: if Lagna is ODD → forward from Aries (1-based);
                        if EVEN → backward from Pisces (1-based).
      2. Count H_count: same rule for Hora Lagna sign.
      3. Shift V = L_count + H_count  [if same parity]
               V = |L_count - H_count| [if different parity; 0 → 12]
      4. Project VL: if original Lagna is ODD → count V signs forward from Aries;
                     if EVEN → count V signs backward from Pisces.
    Returns approximate sidereal longitude (0° of the resulting sign).
    """
    lagna_sign = int(lagna_lon / 30) % 12
    hl_sign    = int(hora_lagna_lon / 30) % 12

    lagna_odd  = lagna_sign in _ODD_SIGNS_SET
    hl_odd     = hl_sign    in _ODD_SIGNS_SET

    # Count from Aries (forward) or Pisces (backward)
    L_count = (lagna_sign + 1)          if lagna_odd else (12 - lagna_sign)
    H_count = (hl_sign    + 1)          if hl_odd    else (12 - hl_sign)

    # Shift vector
    if lagna_odd == hl_odd:   # same parity
        V = L_count + H_count
    else:                     # different parity
        V = abs(L_count - H_count)
        if V == 0:
            V = 12

    # Project V signs from Aries (odd lagna) or backward from Pisces (even lagna)
    if lagna_odd:
        vl_sign = (V - 1) % 12        # 0-based sign index
    else:
        vl_sign = (12 - V) % 12       # backward from Pisces

    vl_lon = vl_sign * 30.0
    return round(vl_lon, 3)


# ─── Pranapada Lagna ────────────────────────────────────────────────────────
# Primary domain: breath rhythm, physiological vitality, birth time rectification.
# Research File 2 (Part C.4) — Vighati / Sun modality formula.
# ADDED 2026-03-02: Phase 1B.

_PRANAPADA_BASE_BY_MODALITY = {
    "movable":  0.0,    # Aries = 0°
    "fixed":    270.0,  # Capricorn = 270°
    "dual":     180.0,  # Libra = 180°
}
_MOVABLE_SIGNS = {0, 3, 6, 9}   # Aries, Cancer, Libra, Capricorn
_FIXED_SIGNS   = {1, 4, 7, 10}  # Taurus, Leo, Scorpio, Aquarius

def compute_pranapada_lagna(
    birth_dt: datetime,
    sun_lon: float,
    sunrise_hour: float = 6.0,
) -> float:
    """
    Compute Pranapada Lagna (Research File 2, Part C.4).

    Steps:
      1. Elapsed vighatis since sunrise (1 Ghati=24 min; 1 Vighati=24 sec).
         Total_vighatis = elapsed_seconds / 24
      2. Signs advanced  = floor(total_vighatis / 15)
         Degrees in sign = (total_vighatis % 15) × 2°   [30°/15 = 2°/vighati]
      3. Base longitude from Sun modality:
         Movable → 0° (Aries), Fixed → 270° (Capricorn), Dual → 180° (Libra)
      4. Pranapada = base + signs×30 + remainder_degrees  (mod 360)
    """
    birth_hour     = birth_dt.hour + birth_dt.minute / 60.0 + birth_dt.second / 3600.0
    elapsed_sec    = (birth_hour - sunrise_hour) * 3600.0
    if elapsed_sec < 0:
        elapsed_sec += 86400.0
    total_vighatis = elapsed_sec / 24.0      # 1 vighati = 24 seconds

    full_signs     = int(total_vighatis / 15)
    remainder_vig  = total_vighatis % 15
    remainder_deg  = remainder_vig * 2.0     # 2 degrees per vighati

    sun_sign = int(sun_lon / 30) % 12
    if sun_sign in _MOVABLE_SIGNS:
        base = 0.0
    elif sun_sign in _FIXED_SIGNS:
        base = 270.0
    else:
        base = 180.0

    pranapada_lon = normalize(base + full_signs * 30.0 + remainder_deg)
    return round(pranapada_lon, 3)


# ─── Sri Lagna ──────────────────────────────────────────────────────────────
# Primary domain: seat of Lakshmi; supreme fortune, abundant wealth.
# Research File 2 (Part C.6) — fractional Moon nakshatra traversal × 360°.
# ADDED 2026-03-02: Phase 1B.

_NAK_SPAN = 360.0 / 27.0   # 13.3333... degrees per nakshatra

def compute_sri_lagna(lagna_lon: float, moon_lon: float) -> float:
    """
    Compute Sri Lagna sidereal longitude (Research File 2, Part C.6).

    Formula:
      nak_start  = floor(moon_lon / nak_span) × nak_span  [start of Moon's nakshatra]
      traveled   = moon_lon - nak_start                   [degrees traversed so far]
      fraction   = traveled / nak_span                    [0.0 – 1.0]
      shift      = fraction × 360°
      Sri Lagna  = (lagna_lon + shift) mod 360°
    """
    nak_idx    = int(moon_lon / _NAK_SPAN)
    nak_start  = nak_idx * _NAK_SPAN
    traveled   = moon_lon - nak_start
    fraction   = traveled / _NAK_SPAN
    shift      = fraction * 360.0
    sri_lon    = normalize(lagna_lon + shift)
    return round(sri_lon, 3)


# ─── Natal Sahams (Arabic Parts / Classical Lots) ────────────────────────────
# 19 classical Sahams per Research File 2 (Part D) Algebraic Matrix.
# General formula (day birth): ASC + A - B
# Night reversal (unless marked NO_REVERSAL): ASC + B - A
# ADDED 2026-03-02: Phase 1B.

# Format: name → {day: (A, B, anchor), night: (A, B, anchor), no_reversal: bool}
# Anchor: "ASC" or specific planet key ("SUN", "VENUS", ...)
# Special: "PUNYA" = use pre-computed Punya Saham longitude
_NATAL_SAHAM_FORMULAS: Dict = {
    #  name        day (A, B)                       anchor  no_rev
    "Punya":    {"day": ("MOON",   "SUN"),    "anchor": "ASC",    "no_rev": False},
    "Vidya":    {"day": ("SUN",    "MOON"),   "anchor": "ASC",    "no_rev": False},
    "Yasas":    {"day": ("JUPITER","PUNYA"),  "anchor": "ASC",    "no_rev": False},
    "Mitra":    {"day": ("JUPITER","PUNYA"),  "anchor": "VENUS",  "no_rev": False},
    "Mahatmya": {"day": ("PUNYA",  "MARS"),   "anchor": "ASC",    "no_rev": False},
    "Asha":     {"day": ("SATURN", "MARS"),   "anchor": "ASC",    "no_rev": False},
    "Samartha": {"day": ("MARS",   "L1"),     "anchor": "ASC",    "no_rev": False},
    "Bhratri":  {"day": ("JUPITER","SATURN"), "anchor": "ASC",    "no_rev": True },
    "Gaurava":  {"day": ("JUPITER","MOON"),   "anchor": "SUN",    "no_rev": False},
    "Pitri":    {"day": ("SATURN", "SUN"),    "anchor": "ASC",    "no_rev": False},
    "Matri":    {"day": ("MOON",   "VENUS"),  "anchor": "ASC",    "no_rev": False},
    "Putra":    {"day": ("JUPITER","MOON"),   "anchor": "ASC",    "no_rev": False},
    "Jeeva":    {"day": ("SATURN", "JUPITER"),"anchor": "ASC",    "no_rev": False},
    "Karma":    {"day": ("MARS",   "MERCURY"),"anchor": "ASC",    "no_rev": False},
    "Roga":     {"day": ("ASC",    "MOON"),   "anchor": "ASC",    "no_rev": True },  # ASC+ASC-Moon
    "Kali":     {"day": ("JUPITER","MARS"),   "anchor": "ASC",    "no_rev": False},
    "Mrityu":   {"day": ("H8",     "MOON"),   "anchor": "ASC",    "no_rev": True },  # house cusp
    "Paradesa": {"day": ("H9",     "L9"),     "anchor": "ASC",    "no_rev": True },  # house cusp
    "Vivaha":   {"day": ("VENUS",  "SATURN"), "anchor": "ASC",    "no_rev": False},
}

_SAHAM_SIGNIFICATIONS_NATAL: Dict[str, str] = {
    "Punya":    "Fortune, dharma, protective shield",
    "Vidya":    "Education, intellect, learning",
    "Yasas":    "Fame, public prominence",
    "Mitra":    "Friends, alliances, networking",
    "Mahatmya": "Greatness, grandeur, status",
    "Asha":     "Hope, unfulfilled desires",
    "Samartha": "Enterprise, capability, potential",
    "Bhratri":  "Siblings, courage, initiative",
    "Gaurava":  "Respect, social regard, honor",
    "Pitri":    "Father, paternal lineage, authority",
    "Matri":    "Mother, maternal lineage, property",
    "Putra":    "Children, progeny, creativity",
    "Jeeva":    "Life, vitality, longevity",
    "Karma":    "Career, action, profession",
    "Roga":     "Disease, physical ailment, debt",
    "Kali":     "Strife, great misfortune, conflict",
    "Mrityu":   "Death, transformation, endings",
    "Paradesa": "Foreign travel, exile",
    "Vivaha":   "Marriage, unions, partnerships",
}


def compute_natal_sahams(
    planet_lons: Dict[str, float],
    asc_lon: float,
    house_cusps: Optional[Dict[int, float]] = None,    # {1: lon, 2: lon,...}
    lagna_lord_lon: Optional[float] = None,            # longitude of L1 planet
    is_daytime: bool = True,
) -> Dict[str, Dict]:
    """
    Compute 19 classical natal Sahams (Arabic Parts) — Research File 2 (Part D).

    Day formula:   Saham = anchor + A - B  (mod 360)
    Night formula: Saham = anchor + B - A  (if no_reversal=False)
    30-degree rule: if anchor \u2228 Saham not on shortest path B\u2192A, add 30\u00b0.

    Special keys:
      PUNYA   = Punya Saham longitude (computed first)
      H8/H9   = 8th/9th house cusp longitude
      L1      = Ascendant lord longitude (lagna_lord_lon)
      ASC     = asc_lon
    ADDED 2026-03-02: Phase 1B.
    """
    def _resolve(key: str, punya_lon: float, cusps: Dict[int, float]) -> Optional[float]:
        if key == "ASC":       return asc_lon
        if key == "PUNYA":     return punya_lon
        if key == "L1":
            return lagna_lord_lon if lagna_lord_lon is not None else asc_lon
        if key.startswith("H"):
            house_num = int(key[1:])
            return cusps.get(house_num, asc_lon)
        p = key.upper()
        aliases = {"JUPITER": "JUPITER", "SATURN": "SATURN", "MARS": "MARS",
                   "MERCURY": "MERCURY", "VENUS": "VENUS", "MOON": "MOON",
                   "SUN": "SUN", "RAHU": "RAHU", "KETU": "KETU"}
        pname = aliases.get(p, p)
        return planet_lons.get(pname, asc_lon)

    cusps = house_cusps or {}
    results = {}

    # Punya Saham computed first (others reference it)
    punya_formula = _NATAL_SAHAM_FORMULAS["Punya"]
    if is_daytime:
        A_key, B_key = punya_formula["day"]
    else:
        A_key, B_key = punya_formula["day"][::-1]   # reverse
    A_lon    = _resolve(A_key, 0.0, cusps) or 0.0
    B_lon    = _resolve(B_key, 0.0, cusps) or 0.0
    punya_lon = normalize(asc_lon + A_lon - B_lon)

    for name, formula in _NATAL_SAHAM_FORMULAS.items():
        no_rev   = formula.get("no_rev", False)
        anchor_k = formula.get("anchor", "ASC")
        A_key, B_key = formula["day"]

        if is_daytime or no_rev:
            A_lon = _resolve(A_key, punya_lon, cusps) or 0.0
            B_lon = _resolve(B_key, punya_lon, cusps) or 0.0
        else:
            # Night reversal
            A_lon = _resolve(B_key, punya_lon, cusps) or 0.0
            B_lon = _resolve(A_key, punya_lon, cusps) or 0.0

        anchor_lon = _resolve(anchor_k, punya_lon, cusps) or asc_lon

        # Samartha edge-case: if Mars = Lagna lord, swap to Jupiter/Mars pair
        if name == "Samartha" and lagna_lord_lon is not None:
            mars_lon = planet_lons.get("MARS", 0.0)
            if abs((mars_lon - lagna_lord_lon + 180) % 360 - 180) < 0.5:
                A_lon = planet_lons.get("JUPITER", asc_lon)
                B_lon = mars_lon

        saham_lon = normalize(anchor_lon + A_lon - B_lon)
        sign_idx  = int(saham_lon / 30) % 12
        _SIGN_NAMES = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                       "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        results[name] = {
            "longitude":    round(saham_lon, 3),
            "sign":         _SIGN_NAMES[sign_idx],
            "sign_idx":     sign_idx,
            "significance": _SAHAM_SIGNIFICATIONS_NATAL.get(name, ""),
        }
    return results


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
    planet_lons: Optional[Dict[str, float]] = None,
    house_cusps: Optional[Dict[int, float]] = None,
    lagna_lord_lon: Optional[float] = None,
    is_daytime: bool = True,
) -> Dict:
    """
    Compute all special sensitive points for a birth chart.

    Uses SWE-precise sunrise/sunset for Gulika, Mandi, Hora/Ghati Lagna.

    Now returns (UPDATED 2026-03-02):
      gulika, mandi, hora_lagna (FIX: anchors to Sun), ghati_lagna (FIX: anchors to Sun),
      indu_lagna, varnada_lagna (NEW), pranapada (NEW), sri_lagna (NEW),
      upagrahas, yogi_avayogi, bhrigu_bindu, lagna_drekkana,
      natal_sahams (NEW — 19 classical Arabic Parts).

    Args:
        planet_lons:    {planet_name: longitude} — for natal sahams
        house_cusps:    {1..12: cusp_longitude}  — for Mrityu/Paradesa sahams
        lagna_lord_lon: longitude of Lagna lord planet — for Samartha saham
        is_daytime:     True if birth is between sunrise and sunset
    """
    from vedic_engine.core.coordinates import sign_of as _sign_of
    sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                  "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

    # ── Compute real sunrise/sunset ──────────────────────────────────────────
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
    # FIX 2026-03-02: hora and ghati lagna now anchored to sun_lon (not lagna_lon)
    hora_lagna  = compute_hora_lagna(birth_dt, sun_lon if sun_lon else lagna_lon, sunrise_h)
    ghati_lagna = compute_ghati_lagna(birth_dt, sun_lon if sun_lon else lagna_lon, sunrise_h)
    indu_lagna  = compute_indu_lagna(lagna_lon, moon_lon, house_lords or {})

    # NEW 2026-03-02: Varnada, Pranapada, Sri Lagnas
    varnada_lagna  = compute_varnada_lagna(lagna_lon, hora_lagna)
    pranapada      = compute_pranapada_lagna(birth_dt, sun_lon if sun_lon else lagna_lon, sunrise_h)
    sri_lagna      = compute_sri_lagna(lagna_lon, moon_lon)

    def _describe(lon: float) -> Dict:
        s = _sign_of(lon)
        return {"longitude": lon, "sign": sign_names[s], "sign_idx": s}

    result = {
        "gulika":        _describe(gulika),
        "mandi":         _describe(mandi),
        "hora_lagna":    _describe(hora_lagna),
        "ghati_lagna":   _describe(ghati_lagna),
        "indu_lagna":    _describe(indu_lagna),
        "varnada_lagna": _describe(varnada_lagna),
        "pranapada":     _describe(pranapada),
        "sri_lagna":     _describe(sri_lagna),
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

    # NEW 2026-03-02: 19 classical natal Sahams
    if planet_lons:
        result["natal_sahams"] = compute_natal_sahams(
            planet_lons, lagna_lon,
            house_cusps=house_cusps,
            lagna_lord_lon=lagna_lord_lon,
            is_daytime=is_daytime,
        )

    return result

