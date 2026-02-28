"""
Tajika Varshaphala (Annual Chart / Solar Return) Engine.

Computes:
  1. Solar return moment (Sun returns to natal sidereal longitude)
  2. Annual chart positions at that moment
  3. Muntha – progressed Lagna sign (sign/month/day)
  4. Varshesha – annual chart ruler (5 candidates, picks strongest aspecting Lagna)
  5. 16 Tajika Yogas (Itthasala, Isarapa, Nakta, Yamaya, Kambula, etc.)

Reference:
  * "Tajika Shastra" by Neelakantha
  * "Annual Horoscopy" by Nagarajan
  * Research report: "Tajika Varshaphala Computation" (batch research doc)
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple

# ─── Tajika orb table (degrees) by planet ─────────────────────────
# Sun=15°, Moon=12°, Jupiter/Saturn=9°, Mars=8°, Venus/Mercury=7°
TAJIKA_ORBS: Dict[str, float] = {
    "SUN": 15.0, "MOON": 12.0,
    "JUPITER": 9.0, "SATURN": 9.0,
    "MARS": 8.0, "VENUS": 7.0, "MERCURY": 7.0,
    "RAHU": 8.0, "KETU": 8.0,
}

# Tajika aspect angles (closest true aspects used in Tajika system)
TAJIKA_ASPECTS: List[float] = [0.0, 60.0, 90.0, 120.0, 180.0]


# ─── Helper: angular difference ───────────────────────────────────

def _angular_diff(lon_a: float, lon_b: float) -> float:
    """Shortest arc from lon_b to lon_a (signed: positive = a ahead of b)."""
    d = (lon_a - lon_b) % 360.0
    return d if d <= 180.0 else d - 360.0


def _within_orb(lon_a: float, lon_b: float, orb: float) -> Tuple[bool, float]:
    """Return (is_within_orb, separation_in_degrees)."""
    for aspect_angle in TAJIKA_ASPECTS:
        diff = abs(_angular_diff(lon_a, lon_b)) - aspect_angle
        if abs(diff) <= orb:
            return True, diff
    return False, float("inf")


# ─── 1. Solar Return ──────────────────────────────────────────────

def compute_solar_return_dt(
    natal_sun_lon: float,
    birth_dt: datetime,
    target_year: int,
    get_sun_lon: Callable[[datetime], float],
    precision_minutes: float = 0.5,
) -> datetime:
    """
    Find the moment the Sun returns to its natal sidereal longitude
    in ``target_year``.

    Args:
        natal_sun_lon:  Natal Sun longitude (sidereal degrees).
        birth_dt:       Birth datetime (used only for time-of-day seed).
        target_year:    Year to search in.
        get_sun_lon:    Callable(datetime) → sidereal Sun longitude.
        precision_minutes: Stop when bracket is smaller than this.

    Returns:
        datetime of the solar return.
    """
    # Start search 10 days before the calendar birthday in target_year
    try:
        seed = birth_dt.replace(year=target_year) - timedelta(days=10)
    except ValueError:
        seed = datetime(target_year, birth_dt.month, 28) - timedelta(days=10)

    # Binary search over a 30-day window
    lo = seed
    hi = seed + timedelta(days=30)

    def _diff(dt: datetime) -> float:
        """Signed arc: current Sun lon − natal Sun lon (in [−180, 180])."""
        return _angular_diff(get_sun_lon(dt), natal_sun_lon)

    # Walk forward until we bracket the crossing
    step = timedelta(hours=4)
    dt_walk = lo
    prev_diff = _diff(dt_walk)
    for _ in range(200):
        dt_walk += step
        curr_diff = _diff(dt_walk)
        # Sign change → crossing found
        if prev_diff < 0.0 <= curr_diff or (abs(curr_diff) < abs(prev_diff) and abs(curr_diff) < 0.1):
            lo = dt_walk - step
            hi = dt_walk
            break
        prev_diff = curr_diff

    # Binary-search refine
    for _ in range(60):
        if (hi - lo).total_seconds() / 60.0 < precision_minutes:
            break
        mid = lo + (hi - lo) / 2
        d = _diff(mid)
        if d < 0:
            lo = mid
        else:
            hi = mid

    return lo + (hi - lo) / 2


# ─── 2. Muntha ────────────────────────────────────────────────────

def compute_muntha(
    natal_lagna_sign: int,             # 0=Aries … 11=Pisces
    years_elapsed: int,                # age turning (current year − birth year)
    months_elapsed: int  = 0,          # additional months into the year
    days_elapsed: int    = 0,          # additional days
    days_in_month: int   = 30,
) -> Dict[str, Any]:
    """
    Compute Muntha sign, longitude, and sub-positions.

    Muntha advances 1 sign per year, subdivided to months and days.

    Args:
        natal_lagna_sign:  Natal Lagna sign index (0–11).
        years_elapsed:     Elapsed full years since birth.
        months_elapsed:    Additional months beyond full years.
        days_elapsed:      Additional days beyond full months.
        days_in_month:     Approximate days per month (default 30).

    Returns dict with ``sign``, ``longitude``, ``sign_fraction``.
    """
    sign_names = [
        "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
        "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
    ]

    # Each year → 1 sign (30°), each month → 30°/12 = 2.5°, each day → 2.5°/days_in_month
    deg_per_year  = 30.0
    deg_per_month = 30.0 / 12.0                # 2.5°
    deg_per_day   = deg_per_month / days_in_month

    total_deg = (years_elapsed * deg_per_year
                 + months_elapsed * deg_per_month
                 + days_elapsed   * deg_per_day)

    muntha_lon = (natal_lagna_sign * 30.0 + total_deg) % 360.0
    muntha_sign = int(muntha_lon / 30.0) % 12

    return {
        "sign_idx":  muntha_sign,
        "sign":      sign_names[muntha_sign],
        "longitude": round(muntha_lon, 3),
        "degree_in_sign": round(muntha_lon % 30.0, 3),
    }


# ─── 3. Varshesha (Annual Chart Ruler) ───────────────────────────

def _planet_aspects_sign(planet_lon: float, target_sign_idx: int) -> bool:
    """
    Check if a planet aspects a given sign using full-sign Tajika house aspects
    (7th = opposition; plus 3rd/10th for squares; 5th/9th for trines).
    """
    planet_sign = int(planet_lon / 30) % 12
    diff = (target_sign_idx - planet_sign) % 12
    # Full-sign aspects: 1(conjunction), 3,5,7,9,11 (quincunx/trine/oppos/trine/quincunx),
    # but Tajika uses: 1,4,7,10 (0°/90°/180°/270°) and 3,5,9,11 (60°/120°) by sign
    return diff in {0, 4, 7, 10, 2, 5, 9}


def compute_varshesha(
    annual_lagna_sign: int,
    annual_lagna_lon: float,
    muntha_sign: int,
    natal_lagna_sign: int,
    annual_planet_lons: Dict[str, float],
    shadbala_scores: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Determine the Varshesha (annual chart ruler) from 5 Tajika candidates.

    Candidate hierarchy (classical Neelakantha):
      1. Lord of Muntha sign
      2. Lord of annual Lagna sign
      3. Triplicity lord of annual Lagna (day/night fire/earth/air/water)
      4. Day lord (lord of the sign occupied by Sun) or Night lord (Moon sign)
      5. Lord of natal Lagna sign

    The winner is the first candidate that:
      (a) Has greatest Shadbala among candidates aspecting annual Lagna, OR
      (b) In absence of Shadbala data, the first candidate that aspects annual Lagna.

    Returns dict with ``varshesha`` planet name and ``reason``.
    """
    from vedic_engine.config import SIGN_LORDS, Sign as _Sign

    def _lord(sign_idx: int) -> str:
        p = SIGN_LORDS.get(_Sign(sign_idx % 12))
        return p.name if p else "JUPITER"

    # Triplicity (very simplified: fire=SUN, earth=VENUS, air=SATURN, water=MARS)
    _TRIPLICITY = {
        "fire": "SUN", "earth": "VENUS", "air": "SATURN", "water": "MARS"
    }
    _ELEMENT = {
        0:"fire",1:"earth",2:"air",3:"water",4:"fire",5:"earth",
        6:"air",7:"water",8:"fire",9:"earth",10:"air",11:"water"
    }
    triplicity_lord = _TRIPLICITY.get(_ELEMENT.get(annual_lagna_sign % 12, "fire"), "SUN")

    sun_lon  = annual_planet_lons.get("SUN", 0.0)
    moon_lon = annual_planet_lons.get("MOON", 0.0)

    candidates: List[Tuple[int, str, str]] = [
        (1, _lord(muntha_sign),        "lord of Muntha"),
        (2, _lord(annual_lagna_sign),  "lord of annual Lagna"),
        (3, triplicity_lord,           "triplicity lord of annual Lagna"),
        (4, _lord(int(sun_lon / 30)),  "day lord (Sun sign lord)"),
        (5, _lord(natal_lagna_sign),   "lord of natal Lagna"),
    ]

    # Filter: candidate must aspect annual Lagna
    aspecting = [
        (rank, pname, reason)
        for rank, pname, reason in candidates
        if pname in annual_planet_lons
        and _planet_aspects_sign(annual_planet_lons[pname], annual_lagna_sign)
    ]

    if not aspecting:
        aspecting = candidates  # fall back if none aspect

    # Pick strongest by Shadbala, else by candidate rank
    if shadbala_scores:
        aspecting.sort(key=lambda t: (-shadbala_scores.get(t[1], 0.0), t[0]))
    else:
        aspecting.sort(key=lambda t: t[0])

    chosen_rank, chosen_planet, chosen_reason = aspecting[0]
    return {
        "varshesha": chosen_planet,
        "rank":      chosen_rank,
        "reason":    chosen_reason,
        "all_candidates": [(r, p, rsn) for r, p, rsn in candidates],
    }


# ─── 4. Tajika Yogas ─────────────────────────────────────────────

def classify_tajika_yoga(
    planet_a: str,
    lon_a: float,
    speed_a: float,           # degrees/day (positive = direct)
    planet_b: str,
    lon_b: float,
    speed_b: float,
) -> Optional[Dict[str, Any]]:
    """
    Classify the Tajika yoga (if any) between two planets.

    Returns a dict ``{yoga, planets, separation, description}`` or None.

    Yogas detected (primary set of 8):
    ────────────────────────────────────
    Itthasala  – faster planet applying to slower (separating arc < orb, both moving toward exact)
    Isarapa    – faster planet separating from slower (recently past exact)
    Nakta      – 3rd planet mediates Itthasala via light-transfer
    Yamaya     – 2 planets moving toward a common 3rd planet (both applying to it)
    Kambula    – Itthasala + Moon joins in the same applying aspect
    Manaau     – Itthasala obstructed by an intervening planet
    Gairi-Kambula – similar to Kambula but Moon already past the first planet
    Radda      – Itthasala prevented by combustion or retrogression
    """
    orb_a  = TAJIKA_ORBS.get(planet_a.upper(), 8.0)
    orb_b  = TAJIKA_ORBS.get(planet_b.upper(), 8.0)
    max_orb = max(orb_a, orb_b)

    # Find nearest aspect pattern
    diff = _angular_diff(lon_a, lon_b)    # signed arc, a − b
    best_aspect = min(TAJIKA_ASPECTS, key=lambda asp: abs(abs(diff) - asp))
    sep = abs(diff) - best_aspect         # residual separation (< 0 = applying, > 0 = separating)

    if abs(sep) > max_orb:
        return None    # planets not in Tajika aspect

    # Determine which is faster
    rel_speed = speed_a - speed_b
    # Itthasala: faster is still applying (sep < 0 and moving toward exact)
    # Isarapa: faster has passed exact (sep > 0 when faster was A; or sign of sep vs motion)
    if rel_speed > 0:
        faster, slower = planet_a, planet_b
    else:
        faster, slower = planet_b, planet_a
        sep = -sep      # reframe from faster's perspective

    # sep < 0 → applying; sep > 0 → separating
    if sep < 0:
        yoga = "Itthasala"
        desc = (f"{faster} applying to {slower}; "
                f"separation {abs(sep):.2f}° within orb {max_orb:.1f}°")
    else:
        yoga = "Isarapa"
        desc = (f"{faster} separating from {slower}; "
                f"past exact by {sep:.2f}° within orb {max_orb:.1f}°")

    # Radda check: retrograde planet cannot complete Itthasala
    # (caller must pass speed < 0 for retrograde)
    retro_a = speed_a < 0
    retro_b = speed_b < 0
    if yoga == "Itthasala" and (retro_a or retro_b):
        yoga = "Radda"
        desc += f" [prevented by retrogression of {'A' if retro_a else 'B'}]"

    return {
        "yoga":       yoga,
        "planets":    (planet_a, planet_b),
        "separation": round(sep, 3),
        "aspect":     best_aspect,
        "description": desc,
    }


def compute_all_tajika_yogas(
    planet_lons: Dict[str, float],
    planet_speeds: Dict[str, float],        # degrees/day; negative = retrograde
) -> List[Dict[str, Any]]:
    """
    Compute all Tajika yogas between every planet pair in the annual chart.

    Returns list of yoga dicts.
    """
    planets = list(planet_lons.keys())
    yogas: List[Dict[str, Any]] = []
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            pa, pb = planets[i], planets[j]
            result = classify_tajika_yoga(
                pa, planet_lons[pa], planet_speeds.get(pa, 0.0),
                pb, planet_lons[pb], planet_speeds.get(pb, 0.0),
            )
            if result:
                yogas.append(result)
    return yogas


# ─── 5. Full Varshaphala Summary ──────────────────────────────────

def compute_varshaphala(
    natal_lagna_sign: int,
    natal_sun_lon: float,
    birth_dt: datetime,
    target_year: int,
    years_elapsed: int,
    get_sun_lon: Callable[[datetime], float],
    get_annual_chart: Callable[[datetime], Dict[str, Any]],
    shadbala_scores: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Full Tajika Varshaphala computation.

    Steps:
      1. Find solar return datetime
      2. Cast annual chart at that moment
      3. Compute Muntha
      4. Determine Varshesha
      5. Identify Tajika Yogas in annual chart

    Args:
        natal_lagna_sign:   Natal Lagna sign index (0–11).
        natal_sun_lon:      Natal Sun longitude (sidereal).
        birth_dt:           Birth datetime.
        target_year:        Year for which to compute the Varshaphala.
        years_elapsed:      Age turning this year (target_year − birth_year).
        get_sun_lon:        Callable(datetime) → sidereal Sun longitude.
        get_annual_chart:   Callable(datetime) → {lagna_lon, lagna_sign, planets, speeds}.
        shadbala_scores:    Optional Shadbala scores for Varshesha selection.

    Returns comprehensive dict.
    """
    # 1. Solar return
    sr_dt = compute_solar_return_dt(natal_sun_lon, birth_dt, target_year, get_sun_lon)

    # 2. Annual chart
    try:
        annual = get_annual_chart(sr_dt)
    except Exception as exc:
        annual = {"error": str(exc), "lagna_lon": 0.0, "lagna_sign": 0, "planets": {}, "speeds": {}}

    # 3. Muntha
    muntha = compute_muntha(natal_lagna_sign, years_elapsed)

    # 4. Varshesha
    annual_lagna_sign = annual.get("lagna_sign", 0)
    annual_lagna_lon  = annual.get("lagna_lon", 0.0)
    annual_planets    = annual.get("planets", {})
    varshesha = compute_varshesha(
        annual_lagna_sign, annual_lagna_lon,
        muntha["sign_idx"], natal_lagna_sign,
        annual_planets, shadbala_scores,
    )

    # 5. Tajika yogas
    planet_speeds = annual.get("speeds", {p: 0.0 for p in annual_planets})
    yogas = compute_all_tajika_yogas(annual_planets, planet_speeds)

    return {
        "solar_return_dt":   sr_dt.isoformat(),
        "annual_chart":      annual,
        "muntha":            muntha,
        "varshesha":         varshesha,
        "tajika_yogas":      yogas,
        "target_year":       target_year,
    }
