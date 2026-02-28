"""
Muhūrta (Electional Astrology) Engine.

Implements Part B rules from addditonal.md (classical muhurta treatises):
  1. Filter globally inauspicious times (eclipses, Amavasya/Purnima for rites,
     bad tithis, Vishti karana, inauspicious yogas)
  2. Event-type weekday filters (wedding avoids Tue/Sat; business avoids Sat)
  3. Nakshatra filters per event type
  4. Tithi suitability per event type
  5. Score and rank remaining windows

Requires: panchanga.py (same package). No external dependencies beyond stdlib.
Uses ephem if available for precise sun/moon positions (falls back to ~1°/day step).
"""
from __future__ import annotations
import datetime
from typing import Dict, List, Optional, Tuple

from vedic_engine.timing.panchanga import (
    tithi, vara, nakshatra_info, yoga, karana, compute_panchanga,
    NAKSHATRA_NAMES,
)

# ─── Event-Type Configuration ─────────────────────────────────────────────────

# Good nakshatras per event (0-indexed, from classical muhurta texts)
GOOD_NAKSHATRAS: Dict[str, List[int]] = {
    "wedding": [
        3,   # Rohini  ← considered best
        4,   # Mrigashira
        6,   # Punarvasu
        7,   # Pushya
        11,  # Uttara Phalguni
        12,  # Hasta
        14,  # Swati
        15,  # Vishakha
        16,  # Anuradha
        20,  # Uttara Ashadha
        22,  # Dhanishtha
        25,  # Uttara Bhadrapada
        26,  # Revati
    ],
    "business": [
        1,   # Bharani (enterprise)
        3,   # Rohini
        6,   # Punarvasu
        7,   # Pushya   ← highly auspicious for commerce
        11,  # Uttara Phalguni
        12,  # Hasta (swift/commerce)
        14,  # Swati
        20,  # Uttara Ashadha
        22,  # Dhanishtha (wealth)
        26,  # Revati
    ],
    "medical": [
        3,   # Rohini
        6,   # Punarvasu
        7,   # Pushya
        11,  # Uttara Phalguni
        12,  # Hasta (surgical Laghu nature)
        13,  # Chitra
        16,  # Anuradha
        21,  # Shravana
        25,  # Uttara Bhadrapada
        26,  # Revati
    ],
    "property": [
        3,   # Rohini
        6,   # Punarvasu
        11,  # Uttara Phalguni
        12,  # Hasta
        14,  # Swati
        20,  # Uttara Ashadha
        21,  # Shravana
        25,  # Uttara Bhadrapada
    ],
}

BAD_NAKSHATRAS: Dict[str, List[int]] = {
    "wedding": [
        0,   # Ashwini (unstable)
        1,   # Bharani (Ugra)
        8,   # Ashlesha (Tikshna)
        17,  # Jyeshtha
        18,  # Moola
        23,  # Shatabhisha
        24,  # Purva Bhadrapada
    ],
    "business": [
        1,   # Bharani
        5,   # Ardra
        8,   # Ashlesha
        9,   # Magha
        17,  # Jyeshtha
        18,  # Moola
        24,  # Purva Bhadrapada
    ],
    "medical": [
        1,   # Bharani (death nakshatra)
        8,   # Ashlesha (serpent)
        10,  # Purva Phalguni
        17,  # Jyeshtha
        18,  # Moola
    ],
    "property": [
        1,   # Bharani
        5,   # Ardra
        8,   # Ashlesha
        17,  # Jyeshtha
        18,  # Moola
        24,  # Purva Bhadrapada
    ],
}

# Bad weekdays per event (Vedic day index: 0=Sun,1=Mon,2=Tue,3=Wed,4=Thu,5=Fri,6=Sat)
BAD_VARA: Dict[str, List[int]] = {
    "wedding":  [2, 6],   # Tuesday, Saturday
    "business": [6],      # Saturday
    "medical":  [],
    "property": [2, 6],
}

# Bad tithis per event (Vedic tithi numbers 1-30)
BAD_TITHIS: Dict[str, List[int]] = {
    # Universal bad for major ceremonies: 4, 8, 9, 14, 30 (Amavasya)
    "wedding":  [4, 8, 9, 14, 30],
    "business": [4, 8, 14, 30],
    "medical":  [10, 14, 30],   # Dashami, Chaturdashi, Amavasya
    "property": [2, 11, 30],    # Dvitiya, Ekadashi, Amavasya
}

# Bonus score for special good tithis (event-specific)
GOOD_TITHIS_BONUS: Dict[str, List[int]] = {
    "wedding":  [1, 2, 3, 5, 7, 10, 11, 12, 13],
    "business": [1, 2, 3, 5, 7, 10, 11, 12],
    "medical":  [1, 3, 5, 7, 11, 12, 13],
    "property": [1, 3, 5, 7, 10, 13],
}


# ─── Scoring ─────────────────────────────────────────────────────────────────

def score_window(panchanga: Dict, event_type: str, eclipse: bool = False) -> Tuple[float, List[str], List[str]]:
    """
    Score a panchanga window for a given event type.
    Returns (score 0-1, favorable_flags, disqualifying_flags).
    score=0 for disqualified windows (hard filters).
    """
    good: List[str] = []
    disqualify: List[str] = []
    score = 0.5   # neutral start

    # ── Hard disqualifiers ──────────────────────────────────────────────────
    if eclipse:
        disqualify.append("Eclipse — universally inauspicious for ceremonies")

    t_num = panchanga["tithi"]["number"]
    if t_num in BAD_TITHIS.get(event_type, []):
        disqualify.append(f"Bad tithi for {event_type}: {panchanga['tithi']['name']}")

    v_num = panchanga["vara"]["number"]
    if v_num in BAD_VARA.get(event_type, []):
        disqualify.append(f"Bad weekday for {event_type}: {panchanga['vara']['name']}")

    nak_idx = panchanga["nakshatra"]["index"]
    if nak_idx in BAD_NAKSHATRAS.get(event_type, []):
        disqualify.append(f"Inauspicious nakshatra for {event_type}: {panchanga['nakshatra']['name']}")

    if panchanga["karana"]["is_vishti_bhadra"]:
        disqualify.append("Vishti/Bhadra karana — avoid all important starts")

    if disqualify:
        return 0.0, good, disqualify

    # ── Positive scoring ────────────────────────────────────────────────────
    if t_num in GOOD_TITHIS_BONUS.get(event_type, []):
        score += 0.10
        good.append(f"Auspicious tithi: {panchanga['tithi']['name']}")

    if nak_idx in GOOD_NAKSHATRAS.get(event_type, []):
        score += 0.15
        good.append(f"Favorable nakshatra: {panchanga['nakshatra']['name']}")

    # Panchanga aggregate
    pan_score = panchanga["timing_score"]   # -1 to +1
    score += pan_score * 0.20

    # Yoga
    if panchanga["yoga"]["quality_score"] > 0:
        score += 0.08
        good.append(f"Auspicious yoga: {panchanga['yoga']['name']}")
    elif panchanga["yoga"]["quality_score"] < 0:
        score -= 0.08

    # Weekday bonus
    if v_num in {1, 4, 5}:   # Monday, Thursday, Friday
        score += 0.05
        good.append(f"Favorable weekday: {panchanga['vara']['name']}")

    # Moon waxing
    if panchanga.get("moon_waxing"):
        score += 0.05
        good.append("Moon waxing (Shukla Paksha) → increasing growth energy")

    score = max(0.01, min(1.0, score))
    return round(score, 3), good, disqualify


# ─── Window Finder ────────────────────────────────────────────────────────────

def find_muhurta_windows(
    sun_lon_start: float,
    moon_lon_start: float,
    start_date: datetime.date,
    event_type: str = "wedding",
    days_ahead: int = 90,
    eclipse_dates: Optional[List[datetime.date]] = None,
    top_k: int = 5,
) -> List[Dict]:
    """
    Scan days_ahead from start_date to find top Muhurta windows.

    Approximation: Sun moves ~0.9856°/day, Moon ~13.18°/day.
    For precise positions pass in updated sun/moon lons at each step.
    eclipse_dates: list of dates that are eclipse days (hard disqualify).

    Returns: List of top_k scored windows sorted by score descending.
    """
    eclipse_set = set(eclipse_dates or [])
    event_type = event_type.lower()
    if event_type not in GOOD_NAKSHATRAS:
        event_type = "wedding"

    windows: List[Dict] = []

    sun_lon  = sun_lon_start
    moon_lon = moon_lon_start
    current  = start_date if isinstance(start_date, datetime.date) else start_date.date()

    # Try ephem for better positions
    try:
        import ephem as _ephem
        USE_EPHEM = True
    except ImportError:
        USE_EPHEM = False

    for day_offset in range(days_ahead):
        check_date = start_date + datetime.timedelta(days=day_offset)

        if USE_EPHEM:
            try:
                obs = _ephem.Observer()
                obs.date = check_date.strftime("%Y/%m/%d")
                sun  = _ephem.Sun(obs)
                moon = _ephem.Moon(obs)
                # Convert from astronomical RA to ecliptic sidereal (~approximate)
                # Use ecliptic longitude minus ayanamsha (Lahiri ~24.13° for 2025)
                AYANAMSHA = 24.13
                sun_lon_day  = (float(sun.hlong)  * 57.2957795 - AYANAMSHA) % 360
                moon_lon_day = (float(moon.hlong) * 57.2957795 - AYANAMSHA) % 360
            except Exception:
                sun_lon_day  = (sun_lon  + day_offset * 0.9856)  % 360
                moon_lon_day = (moon_lon + day_offset * 13.176)  % 360
        else:
            sun_lon_day  = (sun_lon  + day_offset * 0.9856)  % 360
            moon_lon_day = (moon_lon + day_offset * 13.176)  % 360

        pan = compute_panchanga(sun_lon_day, moon_lon_day, check_date)
        check_date_obj = check_date if isinstance(check_date, datetime.date) else check_date.date()
        is_eclipse = check_date_obj in eclipse_set

        sc, good_fl, disq_fl = score_window(pan, event_type, eclipse=is_eclipse)

        if sc > 0:
            windows.append({
                "date":         str(check_date_obj),
                "score":        sc,
                "event_type":   event_type,
                "tithi":        pan["tithi"]["name"],
                "vara":         pan["vara"]["name"],
                "nakshatra":    pan["nakshatra"]["name"],
                "yoga":         pan["yoga"]["name"],
                "karana":       pan["karana"]["name"],
                "moon_phase":   pan["moon_phase"],
                "favorable":    good_fl,
                "disqualified": disq_fl,
                "panchanga_quality": pan["timing_quality"],
            })

    # Sort by score and return top_k
    windows.sort(key=lambda x: x["score"], reverse=True)
    return windows[:top_k]


# ─── Quick Muhurta Check for a Specific Date ──────────────────────────────────

def check_muhurta_date(
    sun_lon: float,
    moon_lon: float,
    check_date: datetime.date,
    event_type: str = "wedding",
    is_eclipse: bool = False,
) -> Dict:
    """
    Score a single specific date for the given event type.
    Returns score + analysis dict.
    """
    pan = compute_panchanga(sun_lon, moon_lon, check_date)
    sc, good_fl, disq_fl = score_window(pan, event_type, eclipse=is_eclipse)
    verdict = ("DISQUALIFIED" if disq_fl
               else "EXCELLENT" if sc >= 0.75
               else "GOOD" if sc >= 0.60
               else "MODERATE" if sc >= 0.45
               else "POOR")
    return {
        "date":         str(check_date),
        "score":        sc,
        "verdict":      verdict,
        "event_type":   event_type,
        "panchanga":    pan,
        "favorable":    good_fl,
        "disqualified": disq_fl,
    }
