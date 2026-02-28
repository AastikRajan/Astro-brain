"""
Panchanga (Hindu Calendar) Engine.

The five limbs (Pancha = 5, Anga = limb) of the Vedic calendar:
  1. Tithi      — Lunar day (30 per lunar month)
  2. Vara       — Weekday (7, each ruled by a planet)
  3. Nakshatra  — Moon's asterism (27, approximately 1 day each)
  4. Yoga       — Sun+Moon longitude combined (27 yogas)
  5. Karana     — Half of a Tithi (60 per month, 11 types)

ALL FIVE are computed for any given Sun/Moon longitude pair.
Each has a quality rating (Bala/Shubha/Ashubha) used for timing.

Integration: These act as a DAILY TIMING QUALITY LAYER:
  - All 5 favorable → excellent day for predictions to manifest
  - Mixed → partial support
  - Multiple inauspicious → delays/obstacles indicated classically

References: BPHS Chapter on Muhurta, Jataka Parijata, Brihat Samhita.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple


# ─── Constants ────────────────────────────────────────────────────────────────

NAKSHATRA_NAMES = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
    "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
    "Moola","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha",
    "Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati",
]

# Nakshatra nature/quality for event timing
# Dhruva=Fixed(stable,permanent), Chara=Movable(travel,change), 
# Ugra=Fierce(force,conflict), Mridu=Soft(gentle,arts),
# Tikshna=Sharp(cutting,weapons), Mishra=Mixed, Laghu=Light(swift,commerce)
NAKSHATRA_NATURE = {
    0:"Laghu",  1:"Ugra",   2:"Mishra", 3:"Dhruva", 4:"Mridu",  5:"Tikshna",
    6:"Mishra", 7:"Mridu",  8:"Tikshna",9:"Ugra",   10:"Mridu", 11:"Dhruva",
    12:"Laghu", 13:"Mridu", 14:"Chara", 15:"Mishra",16:"Mridu", 17:"Tikshna",
    18:"Tikshna",19:"Ugra", 20:"Dhruva",21:"Mridu", 22:"Chara", 23:"Chara",
    24:"Ugra",  25:"Dhruva",26:"Mridu",
}

# Nakshatra lords (Vimshottari sequence repeating across 27)
NAKSHATRA_LORDS = [
    "KETU","VENUS","SUN","MOON","MARS","RAHU","JUPITER","SATURN","MERCURY",  # 0-8
    "KETU","VENUS","SUN","MOON","MARS","RAHU","JUPITER","SATURN","MERCURY",  # 9-17
    "KETU","VENUS","SUN","MOON","MARS","RAHU","JUPITER","SATURN","MERCURY",  # 18-26
]

# 30 Tithis in a lunar month
TITHI_NAMES = [
    "Pratipada","Dvitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dvadashi","Trayodashi","Chaturdashi","Purnima/Amavasya",
]

# Tithi quality: 1=auspicious, 0=neutral, -1=inauspicious (classical muhurta rules)
TITHI_QUALITY = {
    1:1, 2:1, 3:1, 4:0, 5:1, 6:0, 7:1, 8:-1, 9:0, 10:1,
    11:1, 12:1, 13:0, 14:-1, 15:1,                        # Shukla paksha
    16:0, 17:1, 18:1, 19:1, 20:0, 21:1, 22:0, 23:1,
    24:-1, 25:0, 26:1, 27:1, 28:1, 29:0, 30:-1,           # Krishna paksha
}

# 27 Yogas (Sun + Moon longitude divided)
YOGA_NAMES = [
    "Vishkambha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda",
    "Sukarma","Dhriti","Shula","Ganda","Vriddhi","Dhruva","Vyaghata",
    "Harshana","Vajra","Siddhi","Vyatipata","Variyan","Parigha","Shiva",
    "Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti",
]

# Yoga quality
YOGA_QUALITY = {
    0:-1, 1:1, 2:1, 3:1, 4:1, 5:-1, 6:1, 7:1, 8:-1, 9:-1,
    10:1, 11:1, 12:-1, 13:1, 14:-1, 15:1, 16:-1, 17:1, 18:-1, 19:1,
    20:1, 21:1, 22:1, 23:1, 24:1, 25:1, 26:-1,
}

# Karana types (60 per month, 11 types cycling)
# Fixed Karanas: Shakuni(57), Chatushpada(58), Naga(59), Kimstughna(60/0)
KARANA_NAMES = [
    "Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti/Bhadra",
    # These 7 repeat 8 times (positions 0-55), then 4 fixed
    "Shakuni","Chatushpada","Naga","Kimstughna",
]

KARANA_QUALITY = {
    0:1, 1:1, 2:1, 3:1, 4:0, 5:1, 6:-1,  # Vishti/Bhadra is inauspicious
    7:-1, 8:-1, 9:-1, 10:1,               # Fixed karanas mostly inauspicious
}

# Vara (weekday) planets and quality
VARA_PLANETS = ["SUN","MOON","MARS","MERCURY","JUPITER","VENUS","SATURN"]
VARA_NAMES   = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
VARA_QUALITY = {0:1, 1:1, 2:0, 3:1, 4:1, 5:1, 6:0}   # Mars/Saturn moderate


# ─── Core computations ───────────────────────────────────────────────────────

def tithi(sun_lon: float, moon_lon: float) -> Dict:
    """
    Compute Tithi from Sun and Moon sidereal longitudes (Lahiri).
    Tithi = (Moon_lon - Sun_lon) / 12°, ceiling to 1-30.
    """
    diff = (moon_lon - sun_lon) % 360.0
    tithi_num = int(diff / 12.0) + 1   # 1-30
    paksha = "Shukla" if tithi_num <= 15 else "Krishna"
    adj_num = tithi_num if tithi_num <= 15 else tithi_num - 15
    name = TITHI_NAMES[(adj_num - 1) % 15]
    quality_score = TITHI_QUALITY.get(tithi_num, 0)
    quality = {1: "Auspicious", 0: "Neutral", -1: "Inauspicious"}[quality_score]
    return {
        "number": tithi_num,
        "paksha": paksha,
        "name": f"{paksha} {name}",
        "quality": quality,
        "quality_score": quality_score,
        "degrees_elapsed": round(diff % 12.0, 3),
    }


def vara(analysis_date) -> Dict:
    """Compute Vara (weekday) from a datetime object."""
    import datetime as dt_module
    if hasattr(analysis_date, 'date'):
        day_of_week = analysis_date.weekday()  # 0=Monday in Python
    else:
        day_of_week = 0
    # Convert Python weekday to Vedic weekday (0=Sunday)
    # Python: Mon=0 ... Sun=6  → Vedic: Sun=0 Mon=1 ... Sat=6
    vedic_day = (day_of_week + 1) % 7
    return {
        "number": vedic_day,
        "name": VARA_NAMES[vedic_day],
        "planet": VARA_PLANETS[vedic_day],
        "quality": {1:"Auspicious",0:"Neutral",-1:"Inauspicious"}[VARA_QUALITY[vedic_day]],
        "quality_score": VARA_QUALITY[vedic_day],
    }


def nakshatra_info(moon_lon: float) -> Dict:
    """Compute Nakshatra from Moon's sidereal longitude."""
    nak_idx = int(moon_lon / (360.0 / 27.0)) % 27
    pada = int((moon_lon % (360.0 / 27.0)) / (360.0 / 27.0 / 4)) + 1
    nature = NAKSHATRA_NATURE.get(nak_idx, "Mixed")
    lord = NAKSHATRA_LORDS[nak_idx]
    # Quality based on nature
    nature_quality = {
        "Mridu": (1,"Auspicious - soft events, arts, relations"),
        "Laghu": (1,"Auspicious - commerce, swift actions"),
        "Dhruva": (1,"Excellent - permanent, stable events"),
        "Chara": (0,"Neutral - travel, change"),
        "Mishra": (0,"Mixed - general activities"),
        "Ugra":  (-1,"Fierce - aggressive actions, challenges"),
        "Tikshna": (-1,"Sharp - cutting events, surgery, conflict"),
    }.get(nature, (0,"Mixed"))
    return {
        "index": nak_idx,
        "name": NAKSHATRA_NAMES[nak_idx],
        "pada": pada,
        "lord": lord,
        "nature": nature,
        "quality": nature_quality[1],
        "quality_score": nature_quality[0],
    }


def yoga(sun_lon: float, moon_lon: float) -> Dict:
    """
    Compute Yoga from Sun+Moon longitude sum.
    Yoga = floor((Sun_lon + Moon_lon) / (360/27)) mod 27
    """
    combined = (sun_lon + moon_lon) % 360.0
    yoga_idx = int(combined / (360.0 / 27.0)) % 27
    quality_score = YOGA_QUALITY.get(yoga_idx, 0)
    quality = {1:"Auspicious",0:"Neutral",-1:"Inauspicious"}[quality_score]
    return {
        "index": yoga_idx,
        "name": YOGA_NAMES[yoga_idx],
        "quality": quality,
        "quality_score": quality_score,
    }


def karana(sun_lon: float, moon_lon: float) -> Dict:
    """
    Compute Karana from tithi elapsed fraction.
    Each tithi has 2 karanas (first half = odd karana, second = even).
    """
    diff = (moon_lon - sun_lon) % 360.0
    karana_num = int(diff / 6.0)   # 0-59 for the lunar month
    
    if karana_num >= 57:
        # Fixed karanas at end
        k_idx = 7 + (karana_num - 57)
    else:
        k_idx = karana_num % 7

    quality_score = KARANA_QUALITY.get(k_idx, 0)
    is_vishti = (karana_num % 7 == 6)   # Bhadra karana is especially inauspicious
    return {
        "number": karana_num + 1,
        "name": KARANA_NAMES[k_idx],
        "quality": {1:"Auspicious",0:"Neutral",-1:"Inauspicious"}[quality_score],
        "quality_score": quality_score,
        "is_vishti_bhadra": is_vishti,
    }


# ─── Composite Panchanga ────────────────────────────────────────────────────

def compute_panchanga(
    sun_lon: float,
    moon_lon: float,
    analysis_date,
) -> Dict:
    """
    Compute full Panchanga for a given Sun longitude, Moon longitude, and date.

    Returns dict with all 5 limbs + aggregate timing quality score.
    """
    t = tithi(sun_lon, moon_lon)
    v = vara(analysis_date)
    n = nakshatra_info(moon_lon)
    y = yoga(sun_lon, moon_lon)
    k = karana(sun_lon, moon_lon)

    # Aggregate quality: average of 5 quality scores (-1 to +1 each)
    scores = [t["quality_score"], v["quality_score"], n["quality_score"],
              y["quality_score"], k["quality_score"]]
    avg = sum(scores) / len(scores)

    # Moon phase
    diff = (moon_lon - sun_lon) % 360.0
    if diff < 15:
        moon_phase = "New Moon"
    elif diff < 90:
        moon_phase = "Waxing Crescent"
    elif diff < 165:
        moon_phase = "Waxing Gibbous"
    elif diff < 195:
        moon_phase = "Full Moon"
    elif diff < 270:
        moon_phase = "Waning Gibbous"
    elif diff < 345:
        moon_phase = "Waning Crescent"
    else:
        moon_phase = "Near New Moon"

    moon_waxing = diff < 180.0

    if avg >= 0.6:
        timing_quality = "EXCELLENT"
    elif avg >= 0.2:
        timing_quality = "GOOD"
    elif avg >= -0.2:
        timing_quality = "MIXED"
    elif avg >= -0.6:
        timing_quality = "CHALLENGING"
    else:
        timing_quality = "INAUSPICIOUS"

    # Count Vishti Bhadra karana (major obstacle indicator)
    warnings = []
    if k["is_vishti_bhadra"]:
        warnings.append("Vishti/Bhadra karana active — avoid important starts")
    if y["quality_score"] < 0:
        warnings.append(f"{y['name']} yoga — delays/obstacles possible")
    if t["quality_score"] < 0:
        warnings.append(f"Tithi {t['name']} — generally inauspicious timing")

    return {
        "tithi": t,
        "vara": v,
        "nakshatra": n,
        "yoga": y,
        "karana": k,
        "moon_phase": moon_phase,
        "moon_waxing": moon_waxing,
        "timing_quality": timing_quality,
        "timing_score": round(avg, 3),
        "auspicious_count": sum(1 for s in scores if s > 0),
        "inauspicious_count": sum(1 for s in scores if s < 0),
        "warnings": warnings,
    }
