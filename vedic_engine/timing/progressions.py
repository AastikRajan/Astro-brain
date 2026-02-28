"""
Secondary Progressions and Solar Arc Directions.

From deep-research-report1.md (Progressions & Solar Arc):

  Secondary progressions (day-for-a-year):
      progressed_time = birth_time + age_in_years (days)

  Solar arc directions:
      arc = progressed_sun_longitude − natal_sun_longitude
      directed_planet[p] = (natal_longitude[p] + arc) mod 360°

These two techniques overlay a "symbolic future chart" on the natal to
detect medium-term life triggers.  They are distinct from transits:
  • Transits  = where the REAL sky planets are now
  • Progressions = where the sky was 'age_days' after birth (1 day = 1 year)
  • Solar arc  = every natal planet advanced by the sun's progressed arc

Confidence modifier: if a progressed or solar-arc planet conjoins a
natal domain-planet within a 1°-2° orb, the domain is considered
"activated" and the confidence receives a small boost.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List


SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

LUNATION_PHASES = [
    "New Moon",      "Crescent",    "First Quarter", "Gibbous",
    "Full Moon",     "Disseminating","Last Quarter",  "Balsamic",
]


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _sign_of(lon: float) -> str:
    return SIGN_NAMES[int(lon // 30) % 12]


def _separation(a: float, b: float) -> float:
    """Minimal arc 0–180 between two longitudes."""
    raw = abs(a - b) % 360.0
    return raw if raw <= 180.0 else 360.0 - raw


# ─── Core progression computation ─────────────────────────────────────────────

def compute_secondary_progressions(
    natal_positions:  Dict[str, float],
    birth_datetime:   datetime,
    analysis_date:    datetime,
    position_fn:      Callable[[datetime], Dict[str, float]],
    orb_degrees:      float = 1.5,
) -> Dict[str, Any]:
    """
    Compute secondary progressed chart and solar arc directions.

    Parameters
    ----------
    natal_positions : {planet: sidereal_lon}   — from the birth chart
    birth_datetime  : datetime of birth (local or UTC, consistent with position_fn)
    analysis_date   : the date you want to analyse (e.g. today)
    position_fn     : callable(datetime) -> {planet: sidereal_lon}
                      (uses the same 4-tier ephemeris from transits.py)
    orb_degrees     : conjoinment orb for activation detection (default 1.5°)

    Returns
    -------
    {
      progressed_date, solar_arc_degrees,
      progressed_sun_sign, progressed_moon_sign, progressed_lunation,
      progressed_positions: {planet: lon},
      solar_arc_positions:  {planet: lon},
      progressed_activations: [{planet, natal_planet, orb, method}],
      solar_arc_activations:  [{planet, natal_planet, orb, method}],
      combined_boost: float,   # confidence modifier [-0.08 .. +0.08]
    }
    """
    # Age in days → symbolic progressed date (1 day = 1 year of life)
    age_days = max(0, (analysis_date - birth_datetime).days)
    # Day-for-year: each calendar year of life = 1 progressed day
    age_years = age_days / 365.25
    progressed_date = birth_datetime + timedelta(days=age_years)

    try:
        prog_pos = position_fn(progressed_date)
    except Exception as exc:
        return {
            "error": f"Progressed ephemeris failed: {exc}",
            "progressed_date": str(progressed_date.date()),
        }

    # Solar arc = how far progressed Sun has moved from natal Sun
    natal_sun  = natal_positions.get("SUN", 0.0)
    prog_sun   = prog_pos.get("SUN", natal_sun)
    solar_arc  = (prog_sun - natal_sun) % 360.0

    # Solar arc directed positions: shift every natal planet by that arc
    sa_pos: Dict[str, float] = {
        planet: round((lon + solar_arc) % 360.0, 2)
        for planet, lon in natal_positions.items()
    }

    # Progressed lunation phase
    prog_moon       = prog_pos.get("MOON", 0.0)
    prog_elongation = (prog_moon - prog_sun) % 360.0
    phase_idx       = int(prog_elongation / 45.0) % 8
    lunation_phase  = LUNATION_PHASES[phase_idx]

    # Activation detection: progressed planet conjunct natal planet
    prog_activations: List[dict] = []
    for p_planet, p_lon in prog_pos.items():
        for n_planet, n_lon in natal_positions.items():
            orb = _separation(p_lon, n_lon)
            if orb <= orb_degrees:
                prog_activations.append({
                    "progressed_planet": p_planet,
                    "natal_planet":      n_planet,
                    "orb":               round(orb, 2),
                    "method":            "secondary_progression",
                })

    # Solar arc activation: SA-directed planet conjunct natal planet
    sa_activations: List[dict] = []
    for sa_planet, sa_lon in sa_pos.items():
        for n_planet, n_lon in natal_positions.items():
            if sa_planet == n_planet:
                continue   # skip trivial self-conjunction at 0° arc < 1.5°
            orb = _separation(sa_lon, n_lon)
            if orb <= orb_degrees:
                sa_activations.append({
                    "directed_planet": sa_planet,
                    "natal_planet":    n_planet,
                    "orb":             round(orb, 2),
                    "method":          "solar_arc",
                })

    # Combined boost: each activation adds a small confidence lift
    n_activations = len(prog_activations) + len(sa_activations)
    combined_boost = round(min(0.08, n_activations * 0.015), 4)  # cap at +8%

    return {
        "progressed_date":      str(progressed_date.date()),
        "solar_arc_degrees":    round(solar_arc, 2),
        "progressed_sun_sign":  _sign_of(prog_sun),
        "progressed_moon_sign": _sign_of(prog_moon),
        "progressed_lunation":  lunation_phase,
        "progressed_positions": {p: round(v, 2) for p, v in prog_pos.items()},
        "solar_arc_positions":  sa_pos,
        "progressed_activations": sorted(prog_activations, key=lambda x: x["orb"]),
        "solar_arc_activations":  sorted(sa_activations,  key=lambda x: x["orb"]),
        "combined_boost":       combined_boost,
    }


def score_progression_activation(
    prog_data:       Dict[str, Any],
    domain_planets:  List[str],
    orb_degrees:     float = 2.0,
) -> float:
    """
    Return a domain activation score [0.0, 1.0] based on how many
    progressed / solar-arc planets hit natal domain planets.

    0.5 = no activation, higher = more activation.
    """
    if "error" in prog_data:
        return 0.5

    hits = 0
    prog_positions = prog_data.get("progressed_positions", {})
    sa_positions   = prog_data.get("solar_arc_positions",  {})
    natal_needed   = set(domain_planets)

    for pos_dict, label in [(prog_positions, "prog"), (sa_positions, "sa")]:
        for p_planet, p_lon in pos_dict.items():
            for n_planet in natal_needed:
                # This function doesn't have natal_positions here, so we check
                # activations that were already computed with the orb threshold.
                pass

    # Use pre-computed activations instead
    for act in prog_data.get("progressed_activations", []):
        if act["natal_planet"] in natal_needed:
            hits += 1
    for act in prog_data.get("solar_arc_activations", []):
        if act["natal_planet"] in natal_needed:
            hits += 1

    return round(min(1.0, 0.5 + hits * 0.05), 3)


def compute_solar_terms(
    transit_sun_lon: float,
    analysis_date:   datetime,
) -> List[dict]:
    """
    Solar term crossings: Sun at every 15° boundary (24 solar terms per year).
    Returns a list of upcoming crossings within the next ~200 days.
    """
    from math import floor
    SUN_SPEED = 0.9856   # degrees / day (mean)

    current_lon = transit_sun_lon % 360.0
    results = []

    for step in range(1, 25):          # look-ahead up to 24 terms
        next_boundary = (floor(current_lon / 15.0) + step) * 15.0
        next_boundary_mod = next_boundary % 360.0
        # Arc remaining in degrees
        arc = (next_boundary - current_lon) % 360.0
        days = arc / SUN_SPEED
        if days > 200:
            break
        crossing_date = analysis_date + timedelta(days=days)
        sign_idx  = int(next_boundary_mod // 30) % 12
        deg_in_sign = next_boundary_mod % 30
        results.append({
            "term_longitude": round(next_boundary_mod, 1),
            "sign":           SIGN_NAMES[sign_idx],
            "degree":         round(deg_in_sign, 1),
            "days":           round(days, 0),
            "date":           str(crossing_date.date()),
            "note":           f"Sun enters {deg_in_sign:.0f}° {SIGN_NAMES[sign_idx]}" if deg_in_sign > 0
                              else f"Sun ingress {SIGN_NAMES[sign_idx]} (Sankranti)",
        })

    return results
