"""
Dasha Lord Transit Tracker.

The single most important transit in Vedic astrology:
THE ACTIVE DASHA LORD'S CURRENT TRANSIT POSITION.

Classical principles:
  1. Gochar (transit) of the Mahadasha lord over natal moon → emotional activation
  2. Dasha lord transiting own natal house → activates natal promise strongly
  3. Dasha lord transiting 11th, 5th, 9th, 2nd from natal moon → auspicious
  4. Dasha lord transiting 6th, 8th, 12th from natal moon → obstacles/illness
  5. Dasha lord transiting over natal position of Antardasha lord → powerful
  6. Transit dasha lord aspected by its own natal position → reinforcement

This module computes:
  - House position of transiting dasha lord from natal Moon (Gochar rules)
  - House position from natal Lagna
  - Whether it's over a sensitive natal point (natal planet, dasha lord, karaka)
  - Combined transit quality score for the dasha lord specifically
  - Next sign change date estimate

Also computes DOUBLE TRANSIT (Guru-Shani yoga):
  When Jupiter AND Saturn both transit favorable positions simultaneously,
  classical astrology treats this as doubly activating.

Integration:
  This adds a NEW confidence component: dasha_lord_transit_score
  It upgrades the simple "transit_support" average to a weighted approach
  where the dasha lord's own transit carries extra weight.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


# ─── Gochar rules: house from Moon for transiting Mahadasha lord ─────────────

# Each house from natal Moon: (score, description)
# Based on classical Gochar phala (transit results) for any planet
GOCHAR_FROM_MOON = {
    1:  (0.30, "Moderate — mental prominence, variable results"),
    2:  (0.70, "Good — wealth, speech, family income flow"),
    3:  (0.20, "Mixed — effort and courage required, no easy gains"),
    4:  (0.10, "Challenging — domestic stress, property issues"),
    5:  (0.80, "Excellent — intelligence, children, gains from past karma"),
    6:  (-0.20,"Obstacle — enemies, illness, hidden opposition"),
    7:  (0.40, "Moderate — partnerships activate, travel possible"),
    8:  (-0.40,"Difficult — hidden obstacles, delays, health concerns"),
    9:  (0.90, "Excellent — dharma activates, fortune, guru blessings"),
    10: (0.60, "Good — career and status elevation, public recognition"),
    11: (1.00, "Best — gains, fulfillment, network benefits"),
    12: (-0.30,"Loss — expenses, distant travel, isolation possible"),
}

# Refined scores by planet (some planets have different Gochar strength per house)
# These are additive adjustments to the base score above
PLANET_GOCHAR_ADJUSTMENTS = {
    "SATURN": {1:-0.4, 2:-0.2, 4:-0.3, 8: 0.1, 12: 0.1},  # Sade Sati effect
    "RAHU":   {3: 0.2, 6: 0.2, 11: 0.2},                    # Rahu favors 3/6/11
    "KETU":   {3: 0.2, 6: 0.2, 12: 0.4},                    # Ketu favors moksha houses
    "JUPITER":{2: 0.1, 5: 0.1, 7: 0.1, 9: 0.1, 11: 0.1},   # Jupiter universally beneficial
    "VENUS":  {1: 0.1, 2: 0.1, 5: 0.1, 11: 0.1},
    "MARS":   {3: 0.2, 6: 0.3, 11: 0.1},                    # Mars benefits 3/6
    "MERCURY":{2: 0.1, 6: 0.1, 10: 0.1},
    "SUN":    {1: 0.1, 10: 0.2, 11: 0.1},
    "MOON":   {2: 0.1, 3: 0.1, 11: 0.2},
}

# Mean daily motion (degrees/day) for next sign change estimate
MEAN_SPEED_PER_DAY = {
    "SUN":     0.9856,
    "MOON":   13.1760,
    "MARS":    0.5240,
    "MERCURY": 1.3870,
    "JUPITER": 0.0831,
    "VENUS":   1.2000,
    "SATURN":  0.0335,
    "RAHU":   -0.0529,
    "KETU":   -0.0529,
}

SIGN_NAMES = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
              "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]


# ─── Key functions ───────────────────────────────────────────────────────────

def house_from_moon(planet_transit_lon: float, natal_moon_lon: float) -> int:
    """Calculate which house a transiting planet is in, counted from natal Moon."""
    moon_sign = int(natal_moon_lon / 30.0) % 12
    planet_sign = int(planet_transit_lon / 30.0) % 12
    return (planet_sign - moon_sign) % 12 + 1


def house_from_lagna(planet_transit_lon: float, lagna_lon: float) -> int:
    """Calculate which house a transiting planet is in, counted from Lagna."""
    lagna_sign = int(lagna_lon / 30.0) % 12
    planet_sign = int(planet_transit_lon / 30.0) % 12
    return (planet_sign - lagna_sign) % 12 + 1


def gochar_score(planet: str, transit_lon: float, natal_moon_lon: float) -> Tuple[float, str]:
    """
    Compute Gochar (transit) score for a planet from natal Moon.
    Returns (score, description) where score is in [-0.5, 1.0].
    """
    h = house_from_moon(transit_lon, natal_moon_lon)
    base_score, desc = GOCHAR_FROM_MOON[h]
    adj = PLANET_GOCHAR_ADJUSTMENTS.get(planet, {}).get(h, 0.0)
    final = max(-0.5, min(1.0, base_score + adj))
    return final, desc


def days_to_next_sign_change(
    planet: str,
    current_transit_lon: float,
    on_date: datetime,
    retrograde: bool = False,
) -> Optional[Tuple[int, str]]:
    """
    Estimate days until planet enters next sign and which sign that will be.
    Returns (days, next_sign_name) or None if unknown.
    """
    speed = MEAN_SPEED_PER_DAY.get(planet)
    if speed is None:
        return None
    if retrograde:
        speed = -speed

    deg_in_sign = current_transit_lon % 30.0
    if speed > 0:
        degrees_to_go = 30.0 - deg_in_sign
        next_sign_idx = (int(current_transit_lon / 30.0) + 1) % 12
    else:
        degrees_to_go = deg_in_sign
        next_sign_idx = (int(current_transit_lon / 30.0) - 1) % 12

    days = int(abs(degrees_to_go / speed))
    next_sign = SIGN_NAMES[next_sign_idx]
    next_date = (on_date + timedelta(days=days)).strftime("%Y-%m-%d")
    return days, next_sign, next_date


def check_natal_activation(
    transit_planet: str,
    transit_lon: float,
    natal_positions: Dict[str, float],
    threshold_deg: float = 3.0,
) -> List[Dict]:
    """
    Check if a transiting planet is within `threshold_deg` of any natal planet.
    "Activation" — a transiting dasha lord over its natal position or over
    the natal position of the antardasha lord is a classical trigger.
    """
    activations = []
    transit_sign = int(transit_lon / 30.0)
    for natal_planet, natal_lon in natal_positions.items():
        natal_sign = int(natal_lon / 30.0)
        if transit_sign != natal_sign:
            continue
        diff = abs((transit_lon % 30.0) - (natal_lon % 30.0))
        if diff < threshold_deg:
            activations.append({
                "natal_planet": natal_planet,
                "orb_degrees": round(diff, 2),
                "significance": (
                    "EXACT NATAL POSITION" if diff < 1.0 else
                    "CLOSE ACTIVATION" if diff < 2.0 else "WITHIN ORB"
                ),
            })
    return activations


# ─── Main tracker ─────────────────────────────────────────────────────────────

def analyze_dasha_lord_transit(
    mahadasha_lord: str,
    antardasha_lord: str,
    transit_positions: Dict[str, float],
    natal_positions: Dict[str, float],
    natal_moon_lon: float,
    natal_lagna_lon: float,
    on_date: datetime,
) -> Dict:
    """
    Comprehensive transit analysis for the active dasha lord(s).

    Parameters
    ----------
    mahadasha_lord      : string name (e.g. "RAHU")
    antardasha_lord     : string name (e.g. "SATURN")
    transit_positions   : {planet: sidereal_lon} of transiting planets today
    natal_positions     : {planet: sidereal_lon} of natal planets
    natal_moon_lon      : natal Moon's sidereal longitude
    natal_lagna_lon     : natal Lagna's sidereal longitude
    on_date             : analysis date

    Returns
    -------
    dict with scores, house from Moon, house from Lagna, activations, ingress info
    """
    results = {}

    for lord_type, lord_name in [("mahadasha", mahadasha_lord), ("antardasha", antardasha_lord)]:
        transit_lon = transit_positions.get(lord_name)
        if transit_lon is None:
            results[lord_type] = {"lord": lord_name, "error": "transit position unavailable"}
            continue

        score, gochar_desc = gochar_score(lord_name, transit_lon, natal_moon_lon)
        h_moon  = house_from_moon(transit_lon, natal_moon_lon)
        h_lagna = house_from_lagna(transit_lon, natal_lagna_lon)

        # Check if dasha lord transits own natal position or AD lord's natal position
        activations = check_natal_activation(lord_name, transit_lon, natal_positions)

        # Also check if it transits natal position of the other lord
        cross_planet = antardasha_lord if lord_type == "mahadasha" else mahadasha_lord
        cross_lon = natal_positions.get(cross_planet)
        if cross_lon is not None:
            diff = abs((transit_lon % 30.0) - (cross_lon % 30.0))
            cross_sign_match = int(transit_lon / 30.0) == int(cross_lon / 30.0)
            if cross_sign_match and diff < 3.0:
                activations.append({
                    "natal_planet": cross_planet,
                    "orb_degrees": round(diff, 2),
                    "significance": f"DASHA LORDS CONJUNCT IN TRANSIT (powerful!)",
                })

        # Ingress / sign change
        ingress = days_to_next_sign_change(lord_name, transit_lon, on_date)

        current_sign_idx = int(transit_lon / 30.0) % 12
        results[lord_type] = {
            "lord": lord_name,
            "transit_lon": round(transit_lon, 3),
            "transit_sign": SIGN_NAMES[current_sign_idx],
            "house_from_moon": h_moon,
            "gochar_score": round(score, 3),
            "gochar_desc": gochar_desc,
            "house_from_lagna": h_lagna,
            "natal_activations": activations,
            "next_sign_change": {
                "days": ingress[0] if ingress else None,
                "sign": ingress[1] if ingress else None,
                "date": ingress[2] if ingress else None,
            } if ingress else None,
        }

    # Double transit check (Jupiter + Saturn in key houses simultaneously)
    jup_transit = transit_positions.get("JUPITER")
    sat_transit = transit_positions.get("SATURN")
    double_transit = None
    if jup_transit and sat_transit:
        jup_h = house_from_moon(jup_transit, natal_moon_lon)
        sat_h = house_from_moon(sat_transit, natal_moon_lon)
        jup_good = jup_h in [2, 5, 7, 9, 11]
        sat_good = sat_h in [2, 3, 6, 11]
        if jup_good and sat_good:
            double_transit = {
                "active": True,
                "type": "BENEFIC DOUBLE TRANSIT",
                "jupiter_house": jup_h,
                "saturn_house": sat_h,
                "note": "Classical Guru-Shani double transit — powerful activation period",
            }
        else:
            double_transit = {
                "active": False,
                "jupiter_house": jup_h,
                "saturn_house": sat_h,
                "note": f"Jup H{jup_h}, Sat H{sat_h} — not double-transit configuration",
            }
    results["double_transit"] = double_transit

    # Combined dasha lord transit score (weighted: MD=60%, AD=40%)
    md_score = results.get("mahadasha", {}).get("gochar_score", 0.3)
    ad_score = results.get("antardasha", {}).get("gochar_score", 0.3)
    combined = 0.60 * md_score + 0.40 * ad_score

    # Activation bonus
    md_acts = len(results.get("mahadasha", {}).get("natal_activations", []))
    ad_acts = len(results.get("antardasha", {}).get("natal_activations", []))
    if md_acts > 0:
        combined = min(1.0, combined + 0.10 * md_acts)
    if ad_acts > 0:
        combined = min(1.0, combined + 0.05 * ad_acts)

    # Double transit bonus
    if double_transit and double_transit.get("active"):
        combined = min(1.0, combined + 0.15)

    results["combined_transit_score"] = round(combined, 3)

    # Quality label
    if combined >= 0.75:
        results["transit_quality"] = "EXCELLENT"
    elif combined >= 0.50:
        results["transit_quality"] = "GOOD"
    elif combined >= 0.25:
        results["transit_quality"] = "MODERATE"
    elif combined >= 0.0:
        results["transit_quality"] = "WEAK"
    else:
        results["transit_quality"] = "CHALLENGING"

    return results


# ─── Transit ingress calendar ─────────────────────────────────────────────────

def compute_ingress_calendar(
    transit_positions: Dict[str, float],
    on_date: datetime,
    planets_to_track: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Compute next sign change dates for slow planets.
    Returns list sorted by soonest ingress.
    """
    if planets_to_track is None:
        planets_to_track = ["JUPITER", "SATURN", "RAHU", "MARS", "SUN"]

    ingress_list = []
    for planet in planets_to_track:
        lon = transit_positions.get(planet)
        if lon is None:
            continue
        result = days_to_next_sign_change(planet, lon, on_date)
        if result:
            days, next_sign, next_date = result
            ingress_list.append({
                "planet": planet,
                "current_sign": SIGN_NAMES[int(lon / 30.0) % 12],
                "next_sign": next_sign,
                "days": days,
                "date": next_date,
            })

    ingress_list.sort(key=lambda x: x["days"])
    return ingress_list
