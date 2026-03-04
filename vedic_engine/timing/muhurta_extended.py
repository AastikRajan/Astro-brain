"""
Extended Muhurta (Electional Astrology) Computations.

Supplements existing panchanga.py and muhurta.py with:
  - Panchanga Shuddhi weighted 221-point scoring
  - Tithi 5-fold classification (Nanda/Bhadra/Jaya/Rikta/Purna)
  - Hora (planetary hour) computation using Chaldean sequence
  - Choghadiya 8-period day/night system
  - Abhijit Muhurta (universal midday window)
  - Durmuhurta (inauspicious pockets by weekday)
  - Rahu Kaal, Yamagandam, Gulika Kaal (shadow-planet sectors)
  - Directional Shoolas (travel taboo directions by weekday)
  - Marriage Muhurta Boolean checklist (full classical constraints)
  - Surgery Muhurta constraints + 12-sign & 27-nakshatra body mapping
  - Griha Pravesh (housewarming) rules
  - Business start rules
  - Travel Muhurta rules

Architecture: PURE FUNCTIONS only. No weights, no blending, no prediction logic.
All results stored in static['computed'] by the prediction layer (Phase 5).

References: BPHS Muhurta chapters, Muhurta Chintamani, Brihat Samhita.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

# ════════════════════════════════════════════════════════════════════════════════
# 1. TITHI CLASSIFICATION (5-fold: Nanda/Bhadra/Jaya/Rikta/Purna)
# ════════════════════════════════════════════════════════════════════════════════

# Tithi classification cycles every 5: Nanda(1,6,11), Bhadra(2,7,12),
# Jaya(3,8,13), Rikta(4,9,14), Purna(5,10,15/30)
TITHI_CLASSES = {
    "Nanda":  {"ruler": "VENUS",   "nature": "Joyous",     "tithis": {1, 6, 11, 16, 21, 26}},
    "Bhadra": {"ruler": "MERCURY", "nature": "Fortunate",  "tithis": {2, 7, 12, 17, 22, 27}},
    "Jaya":   {"ruler": "MARS",    "nature": "Victorious", "tithis": {3, 8, 13, 18, 23, 28}},
    "Rikta":  {"ruler": "SATURN",  "nature": "Empty",      "tithis": {4, 9, 14, 19, 24, 29}},
    "Purna":  {"ruler": "JUPITER", "nature": "Full",       "tithis": {5, 10, 15, 20, 25, 30}},
}


def classify_tithi(tithi_num: int) -> Dict:
    """
    Classify a tithi (1-30) into one of 5 groups.
    Returns classification name, ruler, nature, and whether it's Rikta (inauspicious).
    """
    for cls_name, info in TITHI_CLASSES.items():
        if tithi_num in info["tithis"]:
            return {
                "class": cls_name,
                "ruler": info["ruler"],
                "nature": info["nature"],
                "is_rikta": cls_name == "Rikta",
                "is_purna": cls_name == "Purna",
            }
    return {"class": "Unknown", "ruler": "Unknown", "nature": "Unknown",
            "is_rikta": False, "is_purna": False}


# ════════════════════════════════════════════════════════════════════════════════
# 2. VARA ELEMENTAL AFFINITY
# ════════════════════════════════════════════════════════════════════════════════

VARA_ELEMENTS = {
    0: {"day": "Sunday",    "ruler": "SUN",     "element": "Agni",    "element_en": "Fire"},
    1: {"day": "Monday",    "ruler": "MOON",    "element": "Jala",    "element_en": "Water"},
    2: {"day": "Tuesday",   "ruler": "MARS",    "element": "Agni",    "element_en": "Fire"},
    3: {"day": "Wednesday", "ruler": "MERCURY", "element": "Prithvi", "element_en": "Earth"},
    4: {"day": "Thursday",  "ruler": "JUPITER", "element": "Akasha",  "element_en": "Ether"},
    5: {"day": "Friday",    "ruler": "VENUS",   "element": "Jala",    "element_en": "Water"},
    6: {"day": "Saturday",  "ruler": "SATURN",  "element": "Vayu",    "element_en": "Air"},
}


def get_vara_element(vedic_weekday: int) -> Dict:
    """Return elemental affinity for a Vedic weekday (0=Sun..6=Sat)."""
    return VARA_ELEMENTS.get(vedic_weekday % 7, VARA_ELEMENTS[0])


# ════════════════════════════════════════════════════════════════════════════════
# 3. PANCHANGA SHUDDHI SCORING (221-point system)
# ════════════════════════════════════════════════════════════════════════════════

# Weighted points per limb (classical Muhurta Chintamani)
PANCHANGA_WEIGHTS = {
    "tithi": 1,
    "nakshatra": 4,
    "vara": 8,
    "karana": 16,
    "yoga": 32,
}
# Max from limbs = 1+4+8+16+32 = 61
# Tarabala bonus = 60
# Chandrabala bonus = 100
# Grand total possible = 221


def compute_panchanga_shuddhi(
    tithi_quality: int,
    nakshatra_quality: int,
    vara_quality: int,
    karana_quality: int,
    yoga_quality: int,
    birth_nakshatra_idx: int,
    electional_nakshatra_idx: int,
    birth_moon_sign: int,
    transit_moon_sign: int,
) -> Dict:
    """
    Compute Panchanga Shuddhi score (max 221 points).

    Quality scores: 1=auspicious, 0=neutral, -1=inauspicious
    Nakshatra indices: 0-26
    Moon signs: 0-11 (Ari=0 ... Pis=11)

    Components:
      - Limb score (max 61): Tithi×1 + Nakshatra×4 + Vara×8 + Karana×16 + Yoga×32
        (only auspicious limbs contribute their weight)
      - Tarabala (max 60): birth→electional nakshatra mod-9 check
      - Chandrabala (max 100): transit Moon not in 6/8/12 from natal Moon sign
    """
    # Limb points: only award if quality >= 1
    limb_score = 0
    if tithi_quality >= 1:
        limb_score += PANCHANGA_WEIGHTS["tithi"]
    if nakshatra_quality >= 1:
        limb_score += PANCHANGA_WEIGHTS["nakshatra"]
    if vara_quality >= 1:
        limb_score += PANCHANGA_WEIGHTS["vara"]
    if karana_quality >= 1:
        limb_score += PANCHANGA_WEIGHTS["karana"]
    if yoga_quality >= 1:
        limb_score += PANCHANGA_WEIGHTS["yoga"]

    # Tarabala: count from birth nakshatra to electional, mod 9
    tara_distance = ((electional_nakshatra_idx - birth_nakshatra_idx) % 27) + 1
    tara_remainder = tara_distance % 9
    # Auspicious: 2(Sampat), 4(Kshema), 6(Sadhaka), 8(Mitra), 0(Parama Mitra)
    TARA_AUSPICIOUS = {0, 2, 4, 6, 8}
    TARA_NAMES = {
        1: "Janma (Danger)",
        2: "Sampat (Wealth)",
        3: "Vipat (Loss)",
        4: "Kshema (Prosperity)",
        5: "Pratyak (Obstacle)",
        6: "Sadhaka (Achievement)",
        7: "Naidhana (Death)",
        8: "Mitra (Friend)",
        0: "Parama Mitra (Great Friend)",
    }
    tarabala_score = 60 if tara_remainder in TARA_AUSPICIOUS else 0
    tarabala_name = TARA_NAMES.get(tara_remainder, "Unknown")

    # Chandrabala: transit Moon house from natal Moon sign
    moon_house = ((transit_moon_sign - birth_moon_sign) % 12) + 1
    CHANDRABALA_BAD = {6, 8, 12}
    chandrabala_score = 0 if moon_house in CHANDRABALA_BAD else 100
    chandrabala_ok = moon_house not in CHANDRABALA_BAD

    total = limb_score + tarabala_score + chandrabala_score

    # Label
    if total >= 180:
        verdict = "EXCELLENT"
    elif total >= 130:
        verdict = "GOOD"
    elif total >= 80:
        verdict = "MODERATE"
    elif total >= 40:
        verdict = "POOR"
    else:
        verdict = "REJECT"

    return {
        "limb_score": limb_score,
        "limb_max": 61,
        "tarabala_score": tarabala_score,
        "tarabala_max": 60,
        "tarabala_name": tarabala_name,
        "tarabala_remainder": tara_remainder,
        "chandrabala_score": chandrabala_score,
        "chandrabala_max": 100,
        "chandrabala_ok": chandrabala_ok,
        "chandrabala_house": moon_house,
        "total": total,
        "max_possible": 221,
        "verdict": verdict,
    }


# ════════════════════════════════════════════════════════════════════════════════
# 4. HORA (PLANETARY HOUR) SYSTEM
# ════════════════════════════════════════════════════════════════════════════════

# Chaldean order: Saturn→Jupiter→Mars→Sun→Venus→Mercury→Moon
CHALDEAN_ORDER = ["SATURN", "JUPITER", "MARS", "SUN", "VENUS", "MERCURY", "MOON"]

# Weekday lords (Vedic: 0=Sun..6=Sat)
_WEEKDAY_LORDS = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]

# Activity suitability per Hora planet
HORA_ACTIVITIES = {
    "SUN":     "Government, authority, oaths, vitality, medical treatments",
    "MOON":    "Gardening, food business, emotional bonding, maternal affairs, sea travel",
    "MARS":    "Courage, sports, engineering, surgery, confrontation. AVOID peace/diplomacy",
    "MERCURY": "Commerce, signing contracts, communications, intellectual/educational pursuits",
    "JUPITER": "Marriage, banking, teaching, legal judgments, spiritual initiations",
    "VENUS":   "Romance, jewelry, artistic endeavors, cosmetic procedures, luxury purchases",
    "SATURN":  "Discipline, long-term foundational work, agriculture. AVOID swift tasks",
}


def compute_hora(
    vedic_weekday: int,
    sunrise_minutes: float,
    sunset_minutes: float,
    query_minutes: float,
) -> Dict:
    """
    Compute the ruling Hora (planetary hour) for a given moment.

    vedic_weekday: 0=Sunday..6=Saturday
    sunrise_minutes: minutes from midnight for sunrise
    sunset_minutes: minutes from midnight for sunset
    query_minutes: minutes from midnight for the query time

    Returns: ruling planet, hora number, start/end times, activity guidance.
    """
    day_lord = _WEEKDAY_LORDS[vedic_weekday % 7]
    # Find Chaldean index of day lord
    chaldean_start = CHALDEAN_ORDER.index(day_lord)

    day_len = sunset_minutes - sunrise_minutes
    night_len = 1440.0 - day_len  # remaining minutes in 24h

    hora_day_len = day_len / 12.0
    hora_night_len = night_len / 12.0

    if query_minutes >= sunrise_minutes and query_minutes < sunset_minutes:
        # Daytime hora
        hora_num = int((query_minutes - sunrise_minutes) / hora_day_len)
        hora_num = min(hora_num, 11)
        hora_start = sunrise_minutes + hora_num * hora_day_len
        hora_end = hora_start + hora_day_len
        is_day = True
    else:
        # Nighttime hora
        if query_minutes >= sunset_minutes:
            elapsed = query_minutes - sunset_minutes
        else:
            # After midnight, before sunrise
            elapsed = (1440.0 - sunset_minutes) + query_minutes
        hora_num = int(elapsed / hora_night_len)
        hora_num = min(hora_num, 11)
        hora_start_offset = hora_num * hora_night_len
        hora_end_offset = hora_start_offset + hora_night_len
        hora_start = (sunset_minutes + hora_start_offset) % 1440
        hora_end = (sunset_minutes + hora_end_offset) % 1440
        is_day = False
        hora_num += 12  # offset for counting (13th hora is 1st night hora)

    # Absolute hora count from sunrise (0-23)
    absolute_hora = hora_num if is_day else hora_num
    # Planet: cycle through Chaldean from day lord
    planet_idx = (chaldean_start + (hora_num if is_day else hora_num)) % 7
    ruling_planet = CHALDEAN_ORDER[planet_idx]

    def _mins_to_time(m):
        m = m % 1440
        h = int(m // 60)
        mn = int(m % 60)
        return f"{h:02d}:{mn:02d}"

    return {
        "ruling_planet": ruling_planet,
        "hora_number": (hora_num % 12) + 1,  # 1-12
        "is_daytime": is_day,
        "hora_start": _mins_to_time(hora_start),
        "hora_end": _mins_to_time(hora_end),
        "activities": HORA_ACTIVITIES.get(ruling_planet, ""),
    }


def get_full_hora_sequence(vedic_weekday: int) -> List[str]:
    """
    Get the full 24-hora planetary sequence for a weekday.
    Returns list of 24 planet names (12 day + 12 night).
    """
    day_lord = _WEEKDAY_LORDS[vedic_weekday % 7]
    chaldean_start = CHALDEAN_ORDER.index(day_lord)
    return [CHALDEAN_ORDER[(chaldean_start + i) % 7] for i in range(24)]


# ════════════════════════════════════════════════════════════════════════════════
# 5. CHOGHADIYA (8-PERIOD DAY/NIGHT DIVISION)
# ════════════════════════════════════════════════════════════════════════════════

# 7 Choghadiya types with quality
CHOGHADIYA_TYPES = {
    "Udveg":  {"ruler": "SUN",     "quality": "Inauspicious", "nature": "Anxiety, stress"},
    "Amrit":  {"ruler": "MOON",    "quality": "Highly Auspicious", "nature": "Nectar, life-giving"},
    "Rog":    {"ruler": "MARS",    "quality": "Inauspicious", "nature": "Disease, conflict"},
    "Labh":   {"ruler": "MERCURY", "quality": "Auspicious", "nature": "Profit, gain"},
    "Shubh":  {"ruler": "JUPITER", "quality": "Highly Auspicious", "nature": "Purity, success"},
    "Char":   {"ruler": "VENUS",   "quality": "Auspicious", "nature": "Movement, travel"},
    "Kaal":   {"ruler": "SATURN",  "quality": "Inauspicious", "nature": "Severe delays, loss"},
}

# Day sequence start index per weekday (Sun=0..Sat=6)
# Sun: Udveg, Mon: Amrit, Tue: Rog, Wed: Labh, Thu: Shubh, Fri: Char, Sat: Kaal
_CHOG_DAY_NAMES = ["Udveg", "Amrit", "Rog", "Labh", "Shubh", "Char", "Kaal"]
_CHOG_DAY_START = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}  # day start index

# Night sequence start index (shifted):
# Sun: Shubh, Mon: Char, Tue: Kaal, Wed: Udveg, Thu: Amrit, Fri: Rog, Sat: Labh
_CHOG_NIGHT_NAMES = ["Shubh", "Char", "Kaal", "Udveg", "Amrit", "Rog", "Labh"]
_CHOG_NIGHT_START = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}


def compute_choghadiya(
    vedic_weekday: int,
    sunrise_minutes: float,
    sunset_minutes: float,
    query_minutes: float,
) -> Dict:
    """
    Compute active Choghadiya period for a given time.

    Returns: period name, quality, ruler, start/end, period number (1-8).
    """
    day_len = sunset_minutes - sunrise_minutes
    night_len = 1440.0 - day_len
    chog_day = day_len / 8.0
    chog_night = night_len / 8.0

    def _mins_to_time(m):
        m = m % 1440
        return f"{int(m // 60):02d}:{int(m % 60):02d}"

    wd = vedic_weekday % 7

    if sunrise_minutes <= query_minutes < sunset_minutes:
        # Daytime
        period = int((query_minutes - sunrise_minutes) / chog_day)
        period = min(period, 7)
        start_idx = _CHOG_DAY_START[wd]
        name = _CHOG_DAY_NAMES[(start_idx + period) % 7]
        p_start = sunrise_minutes + period * chog_day
        p_end = p_start + chog_day
        is_day = True
    else:
        # Nighttime
        if query_minutes >= sunset_minutes:
            elapsed = query_minutes - sunset_minutes
        else:
            elapsed = (1440.0 - sunset_minutes) + query_minutes
        period = int(elapsed / chog_night)
        period = min(period, 7)
        start_idx = _CHOG_NIGHT_START[wd]
        name = _CHOG_NIGHT_NAMES[(start_idx + period) % 7]
        p_start = (sunset_minutes + period * chog_night) % 1440
        p_end = (p_start + chog_night) % 1440
        is_day = False

    info = CHOGHADIYA_TYPES.get(name, {})
    return {
        "name": name,
        "quality": info.get("quality", "Unknown"),
        "ruler": info.get("ruler", "Unknown"),
        "nature": info.get("nature", ""),
        "period_number": period + 1,
        "is_daytime": is_day,
        "start": _mins_to_time(p_start),
        "end": _mins_to_time(p_end),
    }


def get_full_choghadiya_schedule(
    vedic_weekday: int,
    sunrise_minutes: float,
    sunset_minutes: float,
) -> Dict:
    """
    Get full 16-period Choghadiya schedule (8 day + 8 night) for a weekday.
    """
    day_len = sunset_minutes - sunrise_minutes
    night_len = 1440.0 - day_len
    chog_day = day_len / 8.0
    chog_night = night_len / 8.0
    wd = vedic_weekday % 7

    def _mins_to_time(m):
        m = m % 1440
        return f"{int(m // 60):02d}:{int(m % 60):02d}"

    schedule = {"day": [], "night": []}
    ds = _CHOG_DAY_START[wd]
    for i in range(8):
        name = _CHOG_DAY_NAMES[(ds + i) % 7]
        s = sunrise_minutes + i * chog_day
        e = s + chog_day
        info = CHOGHADIYA_TYPES.get(name, {})
        schedule["day"].append({
            "period": i + 1, "name": name,
            "quality": info.get("quality", ""), "ruler": info.get("ruler", ""),
            "start": _mins_to_time(s), "end": _mins_to_time(e),
        })
    ns = _CHOG_NIGHT_START[wd]
    for i in range(8):
        name = _CHOG_NIGHT_NAMES[(ns + i) % 7]
        s = (sunset_minutes + i * chog_night) % 1440
        e = (s + chog_night) % 1440
        info = CHOGHADIYA_TYPES.get(name, {})
        schedule["night"].append({
            "period": i + 1, "name": name,
            "quality": info.get("quality", ""), "ruler": info.get("ruler", ""),
            "start": _mins_to_time(s), "end": _mins_to_time(e),
        })
    return schedule


# ════════════════════════════════════════════════════════════════════════════════
# 6. ABHIJIT MUHURTA (Universal Midday Window)
# ════════════════════════════════════════════════════════════════════════════════

def compute_abhijit_muhurta(
    sunrise_minutes: float,
    sunset_minutes: float,
    vedic_weekday: int = -1,
    direction: str = "",
) -> Dict:
    """
    Compute the Abhijit Muhurta window — the 8th of 15 daytime muhurtas.

    Abhijit incinerates minor doshas; grants "victory".
    Exception: Invalid on Wednesday for Southern travel.

    Returns start, end, duration, validity.
    """
    day_len = sunset_minutes - sunrise_minutes
    local_noon = sunrise_minutes + day_len / 2.0
    # Delta = half a muhurta = day_length / 30
    delta = day_len / 30.0

    start = local_noon - delta
    end = local_noon + delta
    duration_minutes = 2 * delta

    def _mins_to_time(m):
        m = m % 1440
        return f"{int(m // 60):02d}:{int(m % 60):02d}"

    # Wednesday + Southern direction exception
    is_valid = True
    exception_note = ""
    if vedic_weekday == 3 and direction.lower() in ("south", "s"):
        is_valid = False
        exception_note = "Invalid on Wednesday for Southern travel direction"

    return {
        "start": _mins_to_time(start),
        "end": _mins_to_time(end),
        "start_minutes": round(start, 2),
        "end_minutes": round(end, 2),
        "duration_minutes": round(duration_minutes, 2),
        "is_valid": is_valid,
        "exception": exception_note,
    }


# ════════════════════════════════════════════════════════════════════════════════
# 7. DURMUHURTA (Inauspicious Windows by Weekday)
# ════════════════════════════════════════════════════════════════════════════════

# Hours after sunrise for each Durmuhurta pocket (each ~48 minutes = 1/15 of day)
# Format: list of (hours_after_sunrise, is_night_pocket)
DURMUHURTA_OFFSETS = {
    0: [(10.24, False)],                          # Sunday
    1: [(6.24, False), (8.48, False)],             # Monday
    2: [(2.24, False), (5.36, True)],              # Tuesday (night: after sunset)
    3: [(5.36, False)],                            # Wednesday
    4: [(4.00, False), (8.48, False)],             # Thursday
    5: [(2.24, False), (8.48, False)],             # Friday
    6: [(6.24, False)],                            # Saturday
}


def compute_durmuhurta(
    vedic_weekday: int,
    sunrise_minutes: float,
    sunset_minutes: float,
) -> List[Dict]:
    """
    Compute Durmuhurta (malefic ~48-minute pockets) for a weekday.
    Returns list of windows with start/end times.
    """
    day_len = sunset_minutes - sunrise_minutes
    muhurta_dur = day_len / 15.0  # ~48 min for 12-hour day

    def _mins_to_time(m):
        m = m % 1440
        return f"{int(m // 60):02d}:{int(m % 60):02d}"

    wd = vedic_weekday % 7
    offsets = DURMUHURTA_OFFSETS.get(wd, [])
    windows = []

    for hrs_offset, is_night in offsets:
        if is_night:
            start = sunset_minutes + hrs_offset * 60
        else:
            start = sunrise_minutes + hrs_offset * 60
        end = start + muhurta_dur
        windows.append({
            "start": _mins_to_time(start),
            "end": _mins_to_time(end),
            "start_minutes": round(start, 2),
            "end_minutes": round(end, 2),
            "is_night": is_night,
            "label": "Durmuhurta",
        })

    return windows


# ════════════════════════════════════════════════════════════════════════════════
# 8. RAHU KAAL, YAMAGANDAM, GULIKA KAAL
# ════════════════════════════════════════════════════════════════════════════════

# Sector assignments (1-based) per weekday (0=Sun..6=Sat)
# Rahu Kaal mnemonic: Mother Saw Father Wearing The Turban Suddenly
# Mon=2, Sat=3, Fri=4, Wed=5, Thu=6, Tue=7, Sun=8
RAHU_KAAL_SECTOR = {0: 8, 1: 2, 2: 7, 3: 5, 4: 6, 5: 4, 6: 3}

# Yamagandam: Thu=1, Wed=2, Tue=3, Mon=4, Sun=5, Sat=6, Fri=7
YAMAGANDAM_SECTOR = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 7, 6: 6}

# Gulika Kaal: Sat=1, Fri=2, Thu=3, Wed=4, Tue=5, Mon=6, Sun=7
GULIKA_KAAL_SECTOR = {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}


def _compute_sector_window(
    sector: int,
    sunrise_minutes: float,
    sunset_minutes: float,
) -> Tuple[float, float]:
    """Compute start/end for a 1-based sector of the daytime (divided into 8)."""
    day_len = sunset_minutes - sunrise_minutes
    sector_len = day_len / 8.0
    start = sunrise_minutes + (sector - 1) * sector_len
    end = start + sector_len
    return start, end


def compute_rahu_kaal(
    vedic_weekday: int,
    sunrise_minutes: float,
    sunset_minutes: float,
) -> Dict:
    """Compute Rahu Kaal window for a given weekday."""
    sector = RAHU_KAAL_SECTOR.get(vedic_weekday % 7, 8)
    start, end = _compute_sector_window(sector, sunrise_minutes, sunset_minutes)

    def _m2t(m):
        m = m % 1440
        return f"{int(m // 60):02d}:{int(m % 60):02d}"

    return {
        "label": "Rahu Kaal",
        "sector": sector,
        "start": _m2t(start),
        "end": _m2t(end),
        "start_minutes": round(start, 2),
        "end_minutes": round(end, 2),
        "warning": "No new auspicious activity should be initiated",
    }


def compute_yamagandam(
    vedic_weekday: int,
    sunrise_minutes: float,
    sunset_minutes: float,
) -> Dict:
    """Compute Yamagandam window for a given weekday."""
    sector = YAMAGANDAM_SECTOR.get(vedic_weekday % 7, 5)
    start, end = _compute_sector_window(sector, sunrise_minutes, sunset_minutes)

    def _m2t(m):
        m = m % 1440
        return f"{int(m // 60):02d}:{int(m % 60):02d}"

    return {
        "label": "Yamagandam",
        "sector": sector,
        "start": _m2t(start),
        "end": _m2t(end),
        "start_minutes": round(start, 2),
        "end_minutes": round(end, 2),
        "warning": "Stagnation/death of endeavor — avoid all starts",
    }


def compute_gulika_kaal(
    vedic_weekday: int,
    sunrise_minutes: float,
    sunset_minutes: float,
) -> Dict:
    """Compute Gulika Kaal (Saturn's offspring) window."""
    sector = GULIKA_KAAL_SECTOR.get(vedic_weekday % 7, 7)
    start, end = _compute_sector_window(sector, sunrise_minutes, sunset_minutes)

    def _m2t(m):
        m = m % 1440
        return f"{int(m // 60):02d}:{int(m % 60):02d}"

    return {
        "label": "Gulika Kaal",
        "sector": sector,
        "start": _m2t(start),
        "end": _m2t(end),
        "start_minutes": round(start, 2),
        "end_minutes": round(end, 2),
        "warning": "Severe delays; actions may need repetition",
    }


def compute_all_inauspicious_windows(
    vedic_weekday: int,
    sunrise_minutes: float,
    sunset_minutes: float,
) -> Dict:
    """Compute all daily inauspicious windows (Rahu Kaal, Yamagandam, Gulika, Durmuhurta)."""
    return {
        "rahu_kaal": compute_rahu_kaal(vedic_weekday, sunrise_minutes, sunset_minutes),
        "yamagandam": compute_yamagandam(vedic_weekday, sunrise_minutes, sunset_minutes),
        "gulika_kaal": compute_gulika_kaal(vedic_weekday, sunrise_minutes, sunset_minutes),
        "durmuhurta": compute_durmuhurta(vedic_weekday, sunrise_minutes, sunset_minutes),
    }


# ════════════════════════════════════════════════════════════════════════════════
# 9. DIRECTIONAL SHOOLAS (Travel Taboo Directions)
# ════════════════════════════════════════════════════════════════════════════════

# Forbidden travel directions per weekday
DIRECTIONAL_SHOOLAS = {
    0: ["West"],                 # Sunday: West
    1: ["East"],                 # Monday: East
    2: ["North"],                # Tuesday: North
    3: ["North"],                # Wednesday: North
    4: ["South"],                # Thursday: South
    5: ["West"],                 # Friday: West
    6: ["East"],                 # Saturday: East
}


def check_directional_shoola(vedic_weekday: int, travel_direction: str) -> Dict:
    """
    Check if travel in a direction is blocked by a Directional Shoola.
    travel_direction: "North", "South", "East", "West" (case-insensitive)
    """
    wd = vedic_weekday % 7
    forbidden = DIRECTIONAL_SHOOLAS.get(wd, [])
    direction = travel_direction.strip().capitalize()
    is_blocked = direction in forbidden

    return {
        "direction": direction,
        "weekday": ["Sunday", "Monday", "Tuesday", "Wednesday",
                     "Thursday", "Friday", "Saturday"][wd],
        "is_blocked": is_blocked,
        "forbidden_directions": forbidden,
        "warning": f"Shoola active: {direction} travel forbidden on {['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][wd]}" if is_blocked else "",
    }


# ════════════════════════════════════════════════════════════════════════════════
# 10. MARRIAGE MUHURTA BOOLEAN CHECKLIST
# ════════════════════════════════════════════════════════════════════════════════

MARRIAGE_APPROVED_MONTHS = {"Magha", "Phalguna", "Vaisakha", "Jyeshtha"}
MARRIAGE_APPROVED_TITHIS = {2, 3, 5, 7, 10, 11, 13}  # both Shukla and Krishna
MARRIAGE_APPROVED_WEEKDAYS = {1, 3, 4, 5}  # Mon, Wed, Thu, Fri
MARRIAGE_APPROVED_NAKSHATRAS = {
    3,   # Rohini
    4,   # Mrigashira
    9,   # Magha
    11,  # Uttara Phalguni
    12,  # Hasta
    14,  # Swati
    16,  # Anuradha
    18,  # Moola
    20,  # Uttara Ashadha
    25,  # Uttara Bhadrapada
    26,  # Revati
}
MARRIAGE_OPTIMAL_LAGNAS = {"Gemini", "Virgo", "Libra"}
MARRIAGE_ACCEPTABLE_LAGNAS = {"Taurus", "Cancer", "Leo", "Sagittarius", "Aquarius"}
MARRIAGE_AVOIDED_LAGNAS = {"Aries", "Scorpio", "Capricorn", "Pisces"}
INAUSPICIOUS_SOLAR_MONTHS = {"Sagittarius", "Pisces"}  # Kharmas


def check_marriage_muhurta(
    venus_combust: bool,
    jupiter_combust: bool,
    jupiter_retrograde: bool,
    is_adhik_maas: bool,
    solar_sign: str,
    lunar_month: str,
    tithi_adj_num: int,
    vedic_weekday: int,
    nakshatra_idx: int,
    lagna_sign: str,
    eighth_house_planets: List[str],
    lagna_lord_7th_lord_hard_aspect: bool,
) -> Dict:
    """
    Complete Marriage Muhurta Boolean checklist.

    Returns dict with each condition's pass/fail + overall verdict.
    """
    checks = {}

    # Hard disqualifiers (must be FALSE)
    checks["venus_not_combust"] = not venus_combust
    checks["jupiter_not_combust"] = not jupiter_combust
    checks["jupiter_not_retrograde"] = not jupiter_retrograde
    checks["no_adhik_maas"] = not is_adhik_maas
    checks["no_kharmas_month"] = solar_sign not in INAUSPICIOUS_SOLAR_MONTHS

    # Must be TRUE
    checks["8th_house_empty"] = len(eighth_house_planets) == 0
    checks["approved_lunar_month"] = lunar_month in MARRIAGE_APPROVED_MONTHS
    checks["approved_tithi"] = tithi_adj_num in MARRIAGE_APPROVED_TITHIS
    checks["approved_weekday"] = (vedic_weekday % 7) in MARRIAGE_APPROVED_WEEKDAYS
    checks["approved_nakshatra"] = nakshatra_idx in MARRIAGE_APPROVED_NAKSHATRAS

    # Lagna quality
    if lagna_sign in MARRIAGE_OPTIMAL_LAGNAS:
        checks["lagna_quality"] = True
        lagna_grade = "Optimal"
    elif lagna_sign in MARRIAGE_ACCEPTABLE_LAGNAS:
        checks["lagna_quality"] = True
        lagna_grade = "Acceptable"
    else:
        checks["lagna_quality"] = False
        lagna_grade = "Avoided"

    checks["no_lagna_7th_hard_aspect"] = not lagna_lord_7th_lord_hard_aspect

    # Count passes/fails
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    failed = [k for k, v in checks.items() if not v]

    # Verdict
    if len(failed) == 0:
        verdict = "APPROVED"
    elif len(failed) <= 2 and "venus_not_combust" not in failed and "8th_house_empty" not in failed:
        verdict = "MARGINAL — minor flaws"
    else:
        verdict = "REJECTED"

    return {
        "checks": checks,
        "lagna_grade": lagna_grade,
        "passed": passed,
        "total": total,
        "failed": failed,
        "verdict": verdict,
    }


# ════════════════════════════════════════════════════════════════════════════════
# 11. GRIHA PRAVESH (HOUSEWARMING) RULES
# ════════════════════════════════════════════════════════════════════════════════

GRIHA_PRAVESH_MONTHS = {"Magha", "Phalguna", "Vaisakha", "Jyeshtha"}
GRIHA_PRAVESH_BAD_WEEKDAYS = {0, 2}  # Sunday, Tuesday
GRIHA_PRAVESH_NAKSHATRAS = {
    3,   # Rohini
    4,   # Mrigashira
    11,  # Uttara Phalguni
    13,  # Chitra
    16,  # Anuradha
    20,  # Uttara Ashadha
    25,  # Uttara Bhadrapada
    26,  # Revati
}
# Uttarayan signs (Northern course of Sun)
UTTARAYAN_SIGNS = {"Capricorn", "Aquarius", "Pisces", "Aries", "Taurus", "Gemini", "Cancer"}


def check_griha_pravesh(
    lunar_month: str,
    vedic_weekday: int,
    nakshatra_idx: int,
    solar_sign: str,
    twelfth_house_planets: List[str],
    entry_type: str = "Apoorva",
) -> Dict:
    """
    Check Griha Pravesh (housewarming) conditions.

    entry_type: "Apoorva" (new house), "Sapoorva" (after renovation), "Dwandwah" (after disaster)
    """
    checks = {}
    checks["approved_month"] = lunar_month in GRIHA_PRAVESH_MONTHS
    checks["good_weekday"] = (vedic_weekday % 7) not in GRIHA_PRAVESH_BAD_WEEKDAYS
    checks["approved_nakshatra"] = nakshatra_idx in GRIHA_PRAVESH_NAKSHATRAS
    checks["uttarayan"] = solar_sign in UTTARAYAN_SIGNS
    checks["12th_house_empty"] = len(twelfth_house_planets) == 0

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    failed = [k for k, v in checks.items() if not v]

    verdict = "APPROVED" if len(failed) == 0 else ("MARGINAL" if len(failed) <= 1 else "REJECTED")

    return {
        "entry_type": entry_type,
        "checks": checks,
        "passed": passed,
        "total": total,
        "failed": failed,
        "verdict": verdict,
    }


# ════════════════════════════════════════════════════════════════════════════════
# 12. BUSINESS START MUHURTA RULES
# ════════════════════════════════════════════════════════════════════════════════

BUSINESS_WEEKDAY_QUALITY = {
    0: "Moderate — authority, leadership businesses",
    1: "Good — nurturing, food, hospitality",
    2: "AVOID unless martial/surgical/defense industry",
    3: "Ideal — commerce, trade, consulting",
    4: "Ideal — expansion, banking, wealth, education",
    5: "Ideal — luxury, hospitality, clientele attraction",
    6: "AVOID — agricultural OK if long-term foundation",
}

# Nakshatra type suitability for business type
BUSINESS_NAK_TYPES = {
    "stable": {3, 11, 20, 25},   # Dhruva/Fixed: Rohini, U.Phalguni, U.Ashadha, U.Bhadrapada
    "fast_moving": {0, 7, 12},    # Kshipra/Swift: Ashwini, Pushya, Hasta
    "general": {3, 7, 11, 12, 14, 20, 22, 25, 26},  # broad set
}


def check_business_muhurta(
    vedic_weekday: int,
    nakshatra_idx: int,
    lagna_sign_modality: str,
    tarabala_ok: bool,
    chandrabala_ok: bool,
    business_type: str = "general",
) -> Dict:
    """
    Check Business Start Muhurta conditions.
    lagna_sign_modality: "Fixed", "Cardinal", "Dual"
    business_type: "stable", "fast_moving", "general"
    """
    wd = vedic_weekday % 7
    weekday_quality = BUSINESS_WEEKDAY_QUALITY.get(wd, "Unknown")
    weekday_ok = wd not in {2, 6}  # Tuesday and Saturday bad

    nak_set = BUSINESS_NAK_TYPES.get(business_type, BUSINESS_NAK_TYPES["general"])
    nak_ok = nakshatra_idx in nak_set

    # Lagna suitability
    if business_type == "stable":
        lagna_ok = lagna_sign_modality in ("Fixed",)
    elif business_type == "fast_moving":
        lagna_ok = lagna_sign_modality in ("Cardinal", "Dual")
    else:
        lagna_ok = lagna_sign_modality in ("Fixed", "Dual")

    checks = {
        "weekday_ok": weekday_ok,
        "nakshatra_ok": nak_ok,
        "lagna_ok": lagna_ok,
        "tarabala_ok": tarabala_ok,
        "chandrabala_ok": chandrabala_ok,
    }
    failed = [k for k, v in checks.items() if not v]
    passed = sum(1 for v in checks.values() if v)

    return {
        "business_type": business_type,
        "weekday_quality": weekday_quality,
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "failed": failed,
        "verdict": "APPROVED" if len(failed) == 0 else ("MARGINAL" if len(failed) <= 1 else "REJECTED"),
    }


# ════════════════════════════════════════════════════════════════════════════════
# 13. TRAVEL MUHURTA RULES
# ════════════════════════════════════════════════════════════════════════════════

def check_travel_muhurta(
    vedic_weekday: int,
    travel_direction: str,
    moon_house: int,
    jupiter_in_kendra: bool,
    venus_in_kendra: bool,
    moon_in_lagna: bool,
) -> Dict:
    """
    Check Travel Muhurta conditions.
    moon_house: house of transit Moon (1-12)
    """
    shoola = check_directional_shoola(vedic_weekday, travel_direction)

    checks = {
        "no_directional_shoola": not shoola["is_blocked"],
        "moon_not_in_dusthana": moon_house not in {6, 8, 12},
        "benefic_in_kendra": jupiter_in_kendra or venus_in_kendra,
    }
    bonuses = []
    if moon_in_lagna:
        bonuses.append("Moon in Lagna — strong protection")
    if jupiter_in_kendra and venus_in_kendra:
        bonuses.append("Both Jupiter and Venus in Kendra — maximum protection")

    failed = [k for k, v in checks.items() if not v]
    return {
        "checks": checks,
        "directional_shoola": shoola,
        "bonuses": bonuses,
        "passed": sum(1 for v in checks.values() if v),
        "total": len(checks),
        "failed": failed,
        "verdict": "APPROVED" if len(failed) == 0 else "REJECTED",
    }


# ════════════════════════════════════════════════════════════════════════════════
# 14. SURGERY MUHURTA RULES + BODY-PART MAPPING
# ════════════════════════════════════════════════════════════════════════════════

# 12-sign macro body mapping (Moon's transit sign → forbidden surgical zones)
SIGN_BODY_MAP = {
    0:  "Head, Brain, Face, Arteries",                           # Aries
    1:  "Eyes, Throat, Neck, Lips, Speech organs",               # Taurus
    2:  "Lungs, Hands, Arms, Shoulders",                         # Gemini
    3:  "Chest, Breasts, Stomach, Ribs",                         # Cancer
    4:  "Heart, Spine, Forearms",                                # Leo
    5:  "Intestines, Lower stomach, Spleen",                     # Virgo
    6:  "Kidneys, Lumbar region, Skin, Groin",                   # Libra
    7:  "Excretory organs, Bladder, Private parts, Appendix",    # Scorpio
    8:  "Hips, Thighs, Arteries, Nerves",                       # Sagittarius
    9:  "Knees, Joints, Bones, Teeth",                           # Capricorn
    10: "Calves, Ankles, Blood circulation",                     # Aquarius
    11: "Feet, Toes, Lymphatic system",                          # Pisces
}

# 27-nakshatra micro body mapping
NAKSHATRA_BODY_MAP = {
    0:  "Knees, top of feet",                                    # Ashwini
    1:  "Head, bottom of feet",                                  # Bharani
    2:  "Waist, hip joints, crown of head",                      # Krittika
    3:  "Legs, forehead, ankles, shins, calves",                 # Rohini
    4:  "Eyes, eyebrows",                                        # Mrigashira
    5:  "Hair, eyes, front/back of head (brain)",                # Ardra
    6:  "Fingers, nose",                                         # Punarvasu
    7:  "Mouth, face, bone joints, elbows",                      # Pushya
    8:  "Nails, knuckles, kneecaps, ears",                       # Ashlesha
    9:  "Nose, lips, chin",                                      # Magha
    10: "Sexual organs, right hand",                             # Purva Phalguni
    11: "Sexual organs, left hand",                              # Uttara Phalguni
    12: "Hands",                                                 # Hasta
    13: "Forehead, neck",                                        # Chitra
    14: "Teeth, chest, respiratory process",                     # Swati
    15: "Upper limbs, arms, breasts",                            # Vishakha
    16: "Heart, breasts, stomach, womb",                         # Anuradha
    17: "Tongue, neck, right side of torso",                     # Jyeshtha
    18: "Both feet, left side of torso, back",                   # Moola
    19: "Both thighs",                                           # Purva Ashadha
    20: "Thighs, waist",                                        # Uttara Ashadha
    21: "Ears, sex organs, gait mechanisms",                     # Shravana
    22: "Back, anus",                                            # Dhanishtha
    23: "Jaw, chin, right thigh",                                # Shatabhisha
    24: "Ribs, abdomen, sides of legs, left thigh, soles",       # Purva Bhadrapada
    25: "Sides of body, shins, soles of feet",                   # Uttara Bhadrapada
    26: "Armpits, abdomen, groin",                               # Revati
}

# Optimal nakshatras for surgery (Tikshna/Sharp types)
SURGERY_OPTIMAL_NAKSHATRAS = {5, 8, 17, 18}  # Ardra, Ashlesha, Jyeshtha, Moola


def check_surgery_muhurta(
    moon_sign: int,
    moon_nakshatra_idx: int,
    moon_waxing: bool,
    is_full_moon: bool,
    is_new_moon: bool,
    is_eclipse: bool,
    mars_strong: bool,
    mars_in_8th: bool,
    moon_house: int,
    natal_moon_sign: int,
    surgical_body_region: str = "",
) -> Dict:
    """
    Check Surgery Muhurta constraints.

    moon_sign: 0-11 transit Moon sign
    moon_nakshatra_idx: 0-26 transit Moon nakshatra
    moon_house: house of transit Moon in electional chart (1-12)
    natal_moon_sign: 0-11

    Returns checks + forbidden body zones + overall verdict.
    """
    # Shadashtaka: Moon 6/8 from natal Moon
    moon_dist = ((moon_sign - natal_moon_sign) % 12) + 1
    shadashtaka = moon_dist in {6, 8}

    checks = {}
    checks["moon_waxing"] = moon_waxing
    checks["no_full_moon"] = not is_full_moon
    checks["no_new_moon"] = not is_new_moon
    checks["no_eclipse"] = not is_eclipse
    checks["mars_strong"] = mars_strong
    checks["mars_not_in_8th"] = not mars_in_8th
    checks["moon_not_in_dusthana"] = moon_house not in {6, 8, 12}
    checks["no_shadashtaka"] = not shadashtaka

    # Body mapping  warnings
    forbidden_sign = SIGN_BODY_MAP.get(moon_sign, "")
    forbidden_nak = NAKSHATRA_BODY_MAP.get(moon_nakshatra_idx, "")

    # Check if surgical region overlaps forbidden zones
    body_conflict = False
    if surgical_body_region:
        region_lower = surgical_body_region.lower()
        if region_lower in forbidden_sign.lower() or region_lower in forbidden_nak.lower():
            body_conflict = True
    checks["no_body_conflict"] = not body_conflict

    # Optimal nakshatra bonus
    optimal_nak = moon_nakshatra_idx in SURGERY_OPTIMAL_NAKSHATRAS

    failed = [k for k, v in checks.items() if not v]
    passed = sum(1 for v in checks.values() if v)

    if len(failed) == 0:
        verdict = "APPROVED"
    elif len(failed) <= 1 and "no_eclipse" not in failed:
        verdict = "MARGINAL"
    else:
        verdict = "REJECTED"

    return {
        "checks": checks,
        "forbidden_sign_zones": forbidden_sign,
        "forbidden_nakshatra_zones": forbidden_nak,
        "shadashtaka": shadashtaka,
        "optimal_nakshatra": optimal_nak,
        "passed": passed,
        "total": len(checks),
        "failed": failed,
        "verdict": verdict,
    }


def get_forbidden_surgery_zones(
    moon_sign: int,
    moon_nakshatra_idx: int,
) -> Dict:
    """
    Get all forbidden body zones for surgery based on current Moon position.
    Pure lookup function.
    """
    return {
        "moon_sign": moon_sign,
        "moon_nakshatra": moon_nakshatra_idx,
        "sign_zones": SIGN_BODY_MAP.get(moon_sign, ""),
        "nakshatra_zones": NAKSHATRA_BODY_MAP.get(moon_nakshatra_idx, ""),
    }


# ════════════════════════════════════════════════════════════════════════════════
# 15. COMPOSITE DAILY MUHURTA ANALYSIS
# ════════════════════════════════════════════════════════════════════════════════

def analyze_daily_muhurta(
    vedic_weekday: int,
    sunrise_minutes: float,
    sunset_minutes: float,
    sun_lon: float,
    moon_lon: float,
    birth_nakshatra_idx: int = 0,
    birth_moon_sign: int = 0,
) -> Dict:
    """
    Comprehensive daily Muhurta analysis combining all timing systems.
    Pure function — computes all sub-systems and returns composite result.

    vedic_weekday: 0=Sun..6=Sat
    sunrise/sunset_minutes: from midnight
    sun_lon/moon_lon: sidereal longitudes
    """
    from vedic_engine.timing.panchanga import (
        tithi as _tithi, vara as _vara, nakshatra_info as _nak,
        yoga as _yoga, karana as _karana,
    )
    import datetime

    # Panchanga elements
    t = _tithi(sun_lon, moon_lon)
    n = _nak(moon_lon)
    y = _yoga(sun_lon, moon_lon)
    k = _karana(sun_lon, moon_lon)

    # Tithi classification
    t_class = classify_tithi(t["number"])

    # Vara element
    v_elem = get_vara_element(vedic_weekday)

    # Panchanga Shuddhi
    moon_sign = int(moon_lon / 30.0) % 12
    shuddhi = compute_panchanga_shuddhi(
        tithi_quality=t["quality_score"],
        nakshatra_quality=n["quality_score"],
        vara_quality=1 if vedic_weekday in {1, 3, 4, 5} else 0,
        karana_quality=k["quality_score"],
        yoga_quality=y["quality_score"],
        birth_nakshatra_idx=birth_nakshatra_idx,
        electional_nakshatra_idx=n["index"],
        birth_moon_sign=birth_moon_sign,
        transit_moon_sign=moon_sign,
    )

    # Inauspicious windows
    inausp = compute_all_inauspicious_windows(vedic_weekday, sunrise_minutes, sunset_minutes)

    # Abhijit Muhurta
    abhijit = compute_abhijit_muhurta(sunrise_minutes, sunset_minutes, vedic_weekday)

    # Surgery forbidden zones
    surgery_zones = get_forbidden_surgery_zones(moon_sign, n["index"])

    return {
        "tithi": t,
        "tithi_class": t_class,
        "vara_element": v_elem,
        "nakshatra": n,
        "yoga": y,
        "karana": k,
        "panchanga_shuddhi": shuddhi,
        "abhijit_muhurta": abhijit,
        "inauspicious_windows": inausp,
        "surgery_forbidden_zones": surgery_zones,
    }
