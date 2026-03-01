"""
Shadbala Engine – Six-fold planetary strength calculator.
Every formula derived from deep-research-report.md + research_questions_for_gemini.md.

All intermediate scores in Shashtiamsas (0-60 scale per component).
Final Shadbala = sum of 6 components.
Rupas = Shadbala / 60.

=== The 6 Components ===
1. Sthana Bala  (positional)
   = Uccha + Saptavargaja + Ojhayugma + Kendradi + Drekkana

2. Dig Bala     (directional – distance from powerless point)

3. Kala Bala    (time-based)
   = Nathonnatha + Paksha + Tribhaga + Abda + Masa + Vara + Hora + Ayana

4. Cheshta Bala (motional – retrograde/speed-based)

5. Naisargika Bala (fixed natural strength)

6. Drik Bala    (aspectual – benefic - malefic)
"""
from __future__ import annotations
from datetime import datetime
from typing import Dict, Optional

from vedic_engine.config import (
    Planet, Sign, Dignity, SignQuality,
    EXALTATION_DEGREES, DEBILITATION_DEGREES,
    MOOLATRIKONA, OWN_SIGNS,
    NAISARGIKA_FRIENDS, NAISARGIKA_ENEMIES,
    NAISARGIKA_BALA, KENDRADI_SCORES,
    DIG_BALA_POWERLESS_HOUSE, SAPTAVARGAJA_SCORES,
    SAPTAVARGA_CHARTS,
    SIGN_LORDS, SIGN_ELEMENTS, SIGN_QUALITIES,
    SHADBALA_MINIMUMS, NAKSHATRA_SPAN,
    WEEKDAY_LORDS, DAY_STRONG_PLANETS, NIGHT_STRONG_PLANETS,
    ABDA_BALA_POINTS, MASA_BALA_POINTS, VARA_BALA_POINTS, HORA_BALA_POINTS,
    VIMSHOTTARI_TOTAL, VIMSHOTTARI_YEARS,
    get_house_category, HouseCategory, Element,
)
from vedic_engine.core.coordinates import (
    normalize, sign_of, degree_in_sign, angular_distance, nakshatra_of
)
from vedic_engine.core.divisional import get_varga
from vedic_engine.core.aspects import compute_drik_bala

PLANET_NAMES_7 = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]

_P = {
    "SUN": Planet.SUN, "MOON": Planet.MOON, "MARS": Planet.MARS,
    "MERCURY": Planet.MERCURY, "JUPITER": Planet.JUPITER,
    "VENUS": Planet.VENUS, "SATURN": Planet.SATURN,
}


# ─── 1. Sthana Bala ───────────────────────────────────────────────

def uccha_bala(planet: str, longitude: float) -> float:
    """
    Exaltation strength.
    Formula: D = |lon - debilitation_point|, reduce to [0,180].
    Uccha = D / 3  (0 to 60 shashtiamsas).
    """
    p = _P.get(planet)
    if p is None:
        return 0.0
    deb = DEBILITATION_DEGREES[p]
    d = abs(normalize(longitude) - deb)
    if d > 180:
        d = 360 - d
    return d / 3.0


def _get_dignity(
    planet: str,
    lon: float,
    planet_d1_sign: Optional[int] = None,
    planet_signs: Optional[Dict[str, int]] = None,
) -> Dignity:
    """
    Determine planet dignity at a given longitude.

    Args:
        planet:         planet name string
        lon:            longitude in degrees (typically varga sign midpoint)
        planet_d1_sign: D1 sign index (0-11) of the planet, used as position
                        anchor for Tatkalika Maitri computation
        planet_signs:   dict {planet_name: D1_sign_index} of all planets;
                        enables Panchadha Maitri for friendship classification
    """
    p = _P.get(planet)
    if p is None:
        return Dignity.NEUTRAL

    s = Sign(sign_of(lon))
    d = degree_in_sign(lon)

    # Exalted?
    exalt_lon = EXALTATION_DEGREES[p]
    if abs(angular_distance(lon, exalt_lon)) < 1.0:
        return Dignity.EXALTED  # within 1° of exact exaltation

    # Full exaltation sign check
    if sign_of(exalt_lon) == s.value:
        return Dignity.EXALTED

    # Debilitated?
    if sign_of(DEBILITATION_DEGREES[p]) == s.value:
        return Dignity.DEBILITATED

    # Moolatrikona?
    mt = MOOLATRIKONA.get(p)
    if mt and mt[0] == s and mt[1] <= d < mt[2]:
        return Dignity.MOOLATRIKONA

    # Own sign?
    if s in [Sign(o) for o in OWN_SIGNS.get(p, [])]:
        return Dignity.OWN

    # Friendship based on sign lord — uses Panchadha Maitri when D1 positions
    # are available, otherwise falls back to Naisargika (natural friendship only).
    lord = SIGN_LORDS[s]
    lord_name: str = lord.name  # e.g. "SUN", "MOON", ...

    if planet_d1_sign is not None and planet_signs is not None:
        # Panchadha Maitri: compound of Naisargika + Tatkalika
        from vedic_engine.analysis.panchadha_maitri import (
            panchadha_score, panchadha_to_dignity
        )
        lord_d1_sign = planet_signs.get(lord_name)
        if lord_d1_sign is not None:
            score = panchadha_score(planet, planet_d1_sign, lord_name, lord_d1_sign)
            return panchadha_to_dignity(score)
        # Sign lord's D1 position unknown — fall through to Naisargika

    # Naisargika (natural friendship) fallback
    friends = NAISARGIKA_FRIENDS.get(p, frozenset())
    enemies = NAISARGIKA_ENEMIES.get(p, frozenset())
    if lord in friends:
        return Dignity.FRIEND
    elif lord in enemies:
        return Dignity.ENEMY
    return Dignity.NEUTRAL


def saptavargaja_bala(
    planet: str,
    longitude: float,
    planet_signs: Optional[Dict[str, int]] = None,
) -> float:
    """
    Saptavargaja Bala: evaluate dignity across 7 divisional charts.
    Sum scores from SAPTAVARGAJA_SCORES for dignity in each varga.
    Uses sign midpoint (sign*30 + 15°) so moolatrikona degree-range
    checks work correctly for sign-level varga placements.

    Args:
        planet:       planet name ("SUN", "MOON", etc.)
        longitude:    D1 ecliptic longitude (degrees)
        planet_signs: optional dict {planet_name: D1_sign_index (0-11)}.
                      When provided, friendship classification uses the full
                      Panchadha Maitri (5-fold compound: Naisargika + Tatkalika)
                      enabling GREAT_FRIEND / GREAT_ENEMY distinctions.
                      When absent, falls back to Naisargika-only (3-level).
    """
    planet_d1_sign: Optional[int] = sign_of(longitude) if planet_signs is not None else None
    total = 0.0
    for d in SAPTAVARGA_CHARTS:
        varga_sign = get_varga(longitude, d)          # 0-11
        varga_lon = varga_sign * 30.0 + 15.0          # midpoint of varga sign
        dignity = _get_dignity(
            planet, varga_lon,
            planet_d1_sign=planet_d1_sign,
            planet_signs=planet_signs,
        )
        total += SAPTAVARGAJA_SCORES[dignity]
    return total


def ojhayugma_bala(planet: str, d1_lon: float, d9_lon: float) -> float:
    """
    Odd/Even sign parity bala.
    Moon and Venus gain in even signs (Taurus, Cancer, ...); others in odd.
    Applied at D1 and D9 level.  Each valid placement adds 15 shashtiamsas.
    """
    even_planets = {"MOON", "VENUS"}
    score = 0.0
    for lon in (d1_lon, d9_lon):
        s = sign_of(lon)
        is_even = (s % 2 == 1)  # 0=Aries(odd), 1=Taurus(even), ...
        if planet in even_planets:
            if is_even:
                score += 15.0
        else:
            if not is_even:
                score += 15.0
    return score


def kendradi_bala(planet_house: int) -> float:
    """
    Angular/Succedent/Cadent placement score.
    Kendra (1/4/7/10) → 60, Panapara (2/5/8/11) → 30, Apoklima (3/6/9/12) → 15.
    """
    cat = get_house_category(planet_house)
    return KENDRADI_SCORES[cat]


def drekkana_bala(planet: str, longitude: float) -> float:
    """
    Decanate (10°-segment) strength based on planet gender (BPHS).
    Male   (Sun, Mars, Jupiter)  in 1st decanate (0–10°)   → 15
    Neutral (Mercury, Saturn)    in 2nd decanate (10–20°)  → 15
    Female  (Moon, Venus)        in 3rd decanate (20–30°)  → 15
    """
    d = degree_in_sign(longitude)
    dec = int(d / 10)   # 0, 1, 2
    male = {"SUN", "MARS", "JUPITER"}
    female = {"MOON", "VENUS"}
    neutral = {"MERCURY", "SATURN"}
    if (planet in male and dec == 0) or \
       (planet in neutral and dec == 1) or \
       (planet in female and dec == 2):
        return 15.0
    return 0.0


def sthana_bala(
        planet: str, longitude: float, planet_house: int,
        d9_longitude: Optional[float] = None,
        planet_signs: Optional[Dict[str, int]] = None,
) -> float:
    """
    Total Sthana Bala = Uccha + Saptavargaja + Ojhayugma + Kendradi + Drekkana

    planet_signs: optional {planet_name: D1_sign_index} dict. When supplied,
    Saptavargaja Bala uses full Panchadha Maitri (5-fold compound friendship)
    instead of Naisargika-only classification.
    """
    if d9_longitude is None:
        d9_longitude = get_varga(longitude, 9) * 30.0
    return (
        uccha_bala(planet, longitude)
        + saptavargaja_bala(planet, longitude, planet_signs=planet_signs)
        + ojhayugma_bala(planet, longitude, d9_longitude)
        + kendradi_bala(planet_house)
        + drekkana_bala(planet, longitude)
    )


# ─── 2. Dig Bala ──────────────────────────────────────────────────

def dig_bala(planet: str, planet_longitude: float, cusp_longitudes: Dict[int, float]) -> float:
    """
    Directional strength.
    Formula (BPHS): distance from powerless-point cusp / 3.
    Max = 60 (at opposite cusp), Min = 0 (at powerless cusp).
    """
    p = _P.get(planet)
    if p is None:
        return 0.0
    powerless_house = DIG_BALA_POWERLESS_HOUSE.get(p, 4)
    powerless_lon = cusp_longitudes.get(powerless_house, 0.0)
    arc = angular_distance(planet_longitude, powerless_lon)
    return arc / 3.0


# ─── 3. Kala Bala ─────────────────────────────────────────────────

def nathonnatha_bala(planet: str, birth_dt: datetime, sunrise_lon: float = 0,
                     is_day_birth: bool = True) -> float:
    """
    Day/Night birth strength (Nathonnatha Bala) — BPHS Ch.27 formula.

    Let ghatīs from midnight = hour × 2.5  (30 ghatīs = 12 hrs, 60 ghatīs = 24 hrs).
    Unnata = distance from nearest midnight (0–30 ghatīs).
    Nata   = 30 − Unnata  (distance from noon, 0–30).

    Day planets (Sun, Jupiter, Venus)  : Nathonnatha = 60 − Nata  → range 30–60
    Night planets (Moon, Mars, Saturn) : Nathonnatha = 2 × Nata   → range 0–60
    Mercury                            : always 60.

    Effect: Day planets peak at noon (60) and are weakest at midnight (30).
            Night planets peak at midnight (60) and are weakest at noon (0).
    """
    p = _P.get(planet)
    if p is None:
        return 0.0

    if planet == "MERCURY":
        return 60.0

    hour = birth_dt.hour + birth_dt.minute / 60.0
    ghatis = hour * 2.5                        # 0–60 over 24h
    unnata = min(ghatis, 60.0 - ghatis)        # 0–30: dist from nearest midnight
    nata   = 30.0 - unnata                     # 0–30: dist from noon

    if p in DAY_STRONG_PLANETS:
        return max(0.0, 60.0 - nata)           # 30–60 (peak at noon)
    elif p in NIGHT_STRONG_PLANETS:
        return max(0.0, 2.0 * nata)            # 0–60  (peak at midnight)
    return 30.0  # fallback


def paksha_bala(planet: str, moon_lon: float, sun_lon: float) -> float:
    """
    Fortnight (lunar phase) strength.
    Elongation = Moon - Sun (angular separation 0-360).
    Benefics: elongation / 3 → 0-60.
    Malefics: (180 - elongation_in_half_circle) / 3.
    Moon itself uses elongation directly.
    """
    p = _P.get(planet)
    if p is None:
        return 0.0

    elongation = normalize(moon_lon - sun_lon)

    # Reduce to [0, 180] half-circle
    if elongation > 180:
        elong_half = 360 - elongation
    else:
        elong_half = elongation

    from vedic_engine.config import NATURAL_BENEFICS, NATURAL_MALEFICS
    if p in NATURAL_BENEFICS or planet == "MOON":
        return elong_half / 3.0
    else:
        return (180.0 - elong_half) / 3.0


def vara_bala(planet: str, birth_dt: datetime) -> float:
    """
    Day-of-week (Vara) lord strength. Lord of weekday gets 45 shashtiamsas.
    """
    weekday = birth_dt.weekday()  # Mon=0 … Sun=6
    # Python weekday: Mon=0, Sun=6; we need Sun=0, Mon=1 …
    day_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}  # Mon→1…Sun→0
    wd = day_map[weekday]
    lord = WEEKDAY_LORDS.get(wd)
    p = _P.get(planet)
    if p and lord and p == lord:
        return VARA_BALA_POINTS
    return 0.0


def hora_bala(planet: str, birth_dt: datetime,
              sunrise_hour: float = 6.0) -> float:
    """
    Planetary hour (Hora) lord strength. Lord of birth hora gets 60.
    Hora sequence starts from weekday lord at sunrise, changes every 1 hour.
    Order: Sun, Venus, Mercury, Moon, Saturn, Jupiter, Mars (Chaldean order).

    sunrise_hour: actual local sunrise in decimal hours (SWE-precise or NOAA).
    """
    chaldean = [Planet.SUN, Planet.VENUS, Planet.MERCURY, Planet.MOON,
                Planet.SATURN, Planet.JUPITER, Planet.MARS]

    weekday = birth_dt.weekday()
    day_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}
    wd = day_map[weekday]
    # Day lord = weekday lord
    day_lord = WEEKDAY_LORDS.get(wd, Planet.SUN)
    start_idx = chaldean.index(day_lord)

    # Hours since actual sunrise — each hora = 1 hour
    hour = birth_dt.hour + birth_dt.minute / 60.0
    hora_num = int(max(0, hour - sunrise_hour))  # hours since sunrise
    hora_lord = chaldean[(start_idx + hora_num) % 7]

    p = _P.get(planet)
    if p and p == hora_lord:
        return HORA_BALA_POINTS
    return 0.0


def abda_bala(planet: str, birth_dt: datetime) -> float:
    """
    Varsha (Year) lord strength: 15 shashtiamsas to lord of the year.
    Year lord = weekday lord of Mesha Sankranti.
    Uses SWE-precise Mesha Sankranti date when available, else April 14.
    """
    import datetime as _dt
    # Tier-1: SWE precise Mesha Sankranti
    try:
        from vedic_engine.core.swisseph_bridge import (
            compute_mesha_sankranti_jd, jd_to_datetime
        )
        jd_mesha = compute_mesha_sankranti_jd(birth_dt.year)
        mesha_dt = jd_to_datetime(jd_mesha)
        mesha = mesha_dt.date()
    except Exception:
        # Tier-2: Approximate April 14
        mesha = _dt.date(birth_dt.year, 4, 14)
    # Python weekday: Mon=0…Sun=6. Map to Sun=0…Sat=6
    day_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}
    wd = day_map[mesha.weekday()]
    lord = WEEKDAY_LORDS.get(wd)
    p = _P.get(planet)
    if p and lord and p == lord:
        return ABDA_BALA_POINTS   # 15.0
    return 0.0


def masa_bala(planet: str, birth_dt: datetime, sun_lon: float = 0.0) -> float:
    """
    Masa (Month) lord strength: 30 shashtiamsas to lord of the month.
    Month lord = weekday lord of last solar ingress into current sign.
    Sun moves ~1°/day → approximate ingress date = birth_dt - (deg_in_sign) days.
    """
    from datetime import timedelta
    import datetime as _dt
    deg_in_sign = sun_lon % 30.0
    ingress_date = (birth_dt - timedelta(days=deg_in_sign)).date()
    day_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}
    wd = day_map[ingress_date.weekday()]
    lord = WEEKDAY_LORDS.get(wd)
    p = _P.get(planet)
    if p and lord and p == lord:
        return MASA_BALA_POINTS   # 30.0
    return 0.0


def tribhaga_bala(planet: str, birth_dt: datetime,
                  sunrise_hour: float = 6.0,
                  sunset_hour: float = 18.0) -> float:
    """
    Tri-section of day/night (Tribhaga Bala) — BPHS Ch.27.
    Day divided into 3 equal parts: Mercury (1st), Sun (2nd), Saturn (3rd).
    Night divided into 3 equal parts: Moon (1st), Venus (2nd), Mars (3rd).
    The ruling planet of the active section gets 60 virupas.
    **Jupiter always receives 60 virupas** regardless of time.

    sunrise_hour / sunset_hour: actual local sunrise/sunset in decimal hours
    (SWE-precise or NOAA). Replaces the old hardcoded 6am/6pm assumption.
    """
    p = _P.get(planet)
    if p is None:
        return 0.0

    # Jupiter always gets full Tribhaga Bala
    if p == Planet.JUPITER:
        return 60.0

    hour = birth_dt.hour + birth_dt.minute / 60.0

    day_lords = {0: Planet.MERCURY, 1: Planet.SUN, 2: Planet.SATURN}
    night_lords = {0: Planet.MOON, 1: Planet.VENUS, 2: Planet.MARS}

    day_dur = sunset_hour - sunrise_hour
    night_dur = 24.0 - day_dur
    day_third = day_dur / 3.0
    night_third = night_dur / 3.0

    if sunrise_hour <= hour < sunset_hour:  # Day
        section = min(int((hour - sunrise_hour) / day_third), 2)
        lord = day_lords[section]
    else:                                   # Night
        night_hour = (hour - sunset_hour) % 24.0
        section = min(int(night_hour / night_third), 2)
        lord = night_lords[section]

    return 60.0 if p == lord else 0.0


def ayana_bala(planet: str, birth_dt: datetime,
               tz_offset: float = 5.5) -> float:
    """
    Solstice/declination strength (Ayana Bala) — BPHS Ch.27.

    Tier-1: Uses Swiss Ephemeris solar declination (exact astronomical value).
    Tier-2: Falls back to month-based approximation if SWE unavailable.

    Formula (precise):  Ayana = (declination / 23.44) × 30 + 30.
      At summer solstice (+23.44°): Day planets get 60, Night planets get 0.
      At winter solstice (−23.44°): Night planets get 60, Day planets get 0.
      At equinox (0°): All get 30.
    """
    p = _P.get(planet)
    if p is None:
        return 0.0

    # Tier-1: SWE precise solar declination
    declination = None
    try:
        from vedic_engine.core.swisseph_bridge import compute_solar_declination
        declination = compute_solar_declination(birth_dt, tz_offset)
    except Exception:
        pass

    if declination is not None:
        # Normalized: -1.0 (winter solstice) to +1.0 (summer solstice)
        norm = max(-1.0, min(1.0, declination / 23.44))
        if p in DAY_STRONG_PLANETS:
            return 30.0 + norm * 30.0    # 0–60: peaks at northern solstice
        elif p in NIGHT_STRONG_PLANETS:
            return 30.0 - norm * 30.0    # 60–0: peaks at southern solstice
        else:
            return 30.0  # Mercury neutral

    # Tier-2: Month-based fallback
    month = birth_dt.month
    if month <= 6:
        progress = (month - 1) / 6.0
        hemisph = "north"
    else:
        progress = (month - 7) / 6.0
        hemisph = "south"

    if (p in DAY_STRONG_PLANETS and hemisph == "north") or \
       (p in NIGHT_STRONG_PLANETS and hemisph == "south"):
        return 30.0 + progress * 30.0
    else:
        return 30.0 - progress * 30.0


def kala_bala(
        planet: str,
        birth_dt: datetime,
        moon_lon: float,
        sun_lon: float,
        sunrise_hour: float = 6.0,
        sunset_hour: float = 18.0,
        tz_offset: float = 5.5,
) -> float:
    """
    Total Kala Bala = Nathonnatha + Paksha + Tribhaga + Vara + Hora + Ayana
                    + Abda (year lord 15) + Masa (month lord 30)

    sunrise_hour / sunset_hour: actual decimal hours (SWE-precise).
    tz_offset: for SWE solar declination in Ayana Bala.
    """
    return (
        nathonnatha_bala(planet, birth_dt)
        + paksha_bala(planet, moon_lon, sun_lon)
        + tribhaga_bala(planet, birth_dt, sunrise_hour, sunset_hour)
        + vara_bala(planet, birth_dt)
        + hora_bala(planet, birth_dt, sunrise_hour)
        + ayana_bala(planet, birth_dt, tz_offset)
        + abda_bala(planet, birth_dt)
        + masa_bala(planet, birth_dt, sun_lon)
    )


# ─── 4. Cheshta Bala ──────────────────────────────────────────────

def cheshta_bala(planet: str, is_retrograde: bool, speed: float = 0.0) -> float:
    """
    Motional strength (Cheshta Bala) — granular 8-state model (BPHS / Phaladeepika).

    States and virupas (shashtiamsas):
      Vakra (retrograde)            → 60   (maximum — planet intensely energised)
      Anuvakra (slowing, ~retro)    → 45   (decelerating before station)
      Vikala (stationary)           → 30   (at station point)
      Mandatara (extra slow direct) → 15   (slower than normal by >50%)
      Manda (slow direct)           → 15   (below average speed)
      Sama (average speed)          → 7.5  (normal motion)
      Chari/Vichala (fast direct)   → 30   (above average speed)
      Ati-Chara (very fast)         → 45   (much faster than average)

    Sun always has medium Cheshta (30). Moon Cheshta is handled via Paksha Bala.
    """
    if planet == "SUN":
        return 30.0   # Sun never retrograde; medium motion
    if planet == "MOON":
        return 30.0   # Moon Cheshta handled separately via Paksha Bala

    # Average daily speeds (degrees/day) for each planet
    _AVG_SPEED = {
        "MARS": 0.52, "MERCURY": 1.38, "JUPITER": 0.083,
        "VENUS": 1.2,  "SATURN": 0.033,
    }
    avg = _AVG_SPEED.get(planet, 0.5)
    abs_spd = abs(speed)

    if is_retrograde:
        # Differentiate Vakra vs Anuvakra by speed magnitude
        if abs_spd > 0.01:                   # clearly moving retrograde
            return 60.0                       # Vakra
        else:
            return 45.0                       # Anuvakra (slowing before/after station)

    # Direct motion states
    if abs_spd < 0.005:                       # effectively stationary
        return 30.0                            # Vikala (station)

    ratio = abs_spd / avg if avg > 0 else 1.0
    if ratio >= 1.5:
        return 45.0                            # Ati-Chara (very fast)
    elif ratio >= 0.9:
        return 30.0                            # Chari/Vichala (normal-fast)
    elif ratio >= 0.5:
        return 15.0                            # Manda (slow)
    else:
        return 7.5                             # Mandatara (very slow)


# ─── 5. Naisargika Bala ───────────────────────────────────────────

def naisargika_bala(planet: str) -> float:
    """Fixed natural strength (constant lookup)."""
    p = _P.get(planet)
    if p is None:
        return 0.0
    return NAISARGIKA_BALA.get(p, 0.0)


# ─── 6. Drik Bala ─────────────────────────────────────────────────
# (delegated to core.aspects.compute_drik_bala)


# ─── Full Shadbala ────────────────────────────────────────────────

def compute_shadbala(
        planet: str,
        longitude: float,
        planet_house: int,
        birth_dt: datetime,
        moon_lon: float,
        sun_lon: float,
        cusp_longitudes: Dict[int, float],
        planet_houses: Dict[str, int],
        is_retrograde: bool = False,
        speed: float = 0.0,
        moon_waxing: bool = True,
        planet_signs: Optional[Dict[str, int]] = None,
        sunrise_hour: float = 6.0,
        sunset_hour: float = 18.0,
        tz_offset: float = 5.5,
) -> Dict[str, float]:
    """
    Compute all 6 Shadbala components for a planet.
    Returns dict with each component and totals.

    sunrise_hour / sunset_hour: actual decimal hours for Kala Bala precision.
    tz_offset: for SWE solar declination in Ayana Bala.
    """
    sb = sthana_bala(planet, longitude, planet_house, planet_signs=planet_signs)
    db = dig_bala(planet, longitude, cusp_longitudes)
    kb = kala_bala(planet, birth_dt, moon_lon, sun_lon,
                   sunrise_hour, sunset_hour, tz_offset)
    cb = cheshta_bala(planet, is_retrograde, speed)
    nb = naisargika_bala(planet)
    rb = compute_drik_bala(planet, planet_house, planet_houses, moon_waxing)

    total = sb + db + kb + cb + nb + rb
    rupas = total / 60.0
    p = _P.get(planet)
    min_req = SHADBALA_MINIMUMS.get(p, 5.0) if p else 5.0
    ratio = rupas / min_req if min_req > 0 else 0.0

    return {
        "sthana_bala": round(sb, 2),
        "dig_bala": round(db, 2),
        "kala_bala": round(kb, 2),
        "cheshta_bala": round(cb, 2),
        "naisargika_bala": round(nb, 2),
        "drik_bala": round(rb, 2),
        "total": round(total, 2),
        "rupas": round(rupas, 3),
        "minimum_required": min_req,
        "ratio": round(ratio, 3),
        "meets_minimum": ratio >= 1.0,
    }


def compute_all_shadbala(
        planet_data: dict,             # {pname: PlanetPosition}
        birth_dt: datetime,
        cusp_longitudes: Dict[int, float],
        latitude: float = 0.0,
        longitude: float = 0.0,
        tz_offset: float = 5.5,
) -> Dict[str, Dict]:
    """
    Compute Shadbala for all 7 classical planets.
    planet_data: dict of PlanetPosition objects keyed by planet name.

    latitude/longitude/tz_offset: enables SWE-precise sunrise/sunset for
    Hora Bala, Tribhaga Bala, and Ayana Bala (via solar declination).
    """
    moon_lon = planet_data["MOON"].longitude if "MOON" in planet_data else 0.0
    sun_lon  = planet_data["SUN"].longitude  if "SUN" in planet_data else 0.0
    moon_sun_sep = normalize(moon_lon - sun_lon)
    moon_waxing = moon_sun_sep <= 180.0

    planet_houses = {pn: pp.house_num for pn, pp in planet_data.items()
                     if pn in PLANET_NAMES_7}

    # Planet D1 sign index dict — enables Panchadha Maitri in Saptavargaja Bala
    planet_signs: Dict[str, int] = {
        pn: getattr(pp, "sign_index", (int(getattr(pp, "longitude", 0)) // 30) % 12)
        for pn, pp in planet_data.items()
    }

    # Also add Rahu/Ketu signs for Tatkalika Maitri context
    for pn in ("RAHU", "KETU"):
        if pn in planet_data:
            pp = planet_data[pn]
            planet_signs[pn] = getattr(pp, "sign_index",
                                       (int(getattr(pp, "longitude", 0)) // 30) % 12)

    # ── Get precise sunrise/sunset for Kala Bala sub-components ──
    sunrise_h, sunset_h = 6.0, 18.0
    if latitude != 0.0 or longitude != 0.0:
        try:
            from vedic_engine.core.sunrise_utils import get_sunrise_sunset_hours
            sunrise_h, sunset_h = get_sunrise_sunset_hours(
                birth_dt, latitude, longitude, tz_offset
            )
        except Exception:
            pass  # keep 6.0 / 18.0 defaults

    results = {}
    for pname in PLANET_NAMES_7:
        if pname not in planet_data:
            continue
        pp = planet_data[pname]
        results[pname] = compute_shadbala(
            planet=pname,
            longitude=pp.longitude,
            planet_house=pp.house_num,
            birth_dt=birth_dt,
            moon_lon=moon_lon,
            sun_lon=sun_lon,
            cusp_longitudes=cusp_longitudes,
            planet_houses=planet_houses,
            is_retrograde=pp.is_retrograde,
            speed=pp.speed,
            moon_waxing=moon_waxing,
            planet_signs=planet_signs,
            sunrise_hour=sunrise_h,
            sunset_hour=sunset_h,
            tz_offset=tz_offset,
        )
    return results
