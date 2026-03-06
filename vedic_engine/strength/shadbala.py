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
    Odd/Even sign parity bala (Ojayugmarasyamsa Bala).
    Research File 1 — classical BPHS Ch.27 / Saravali:
      Male   (Sun, Mars, Jupiter)  → 15 in ODD signs (Aries, Gemini, ...)
      Female (Moon, Venus)         → 15 in EVEN signs (Taurus, Cancer, ...)
      Neutral (Mercury, Saturn)    → 0 (neither parity gains; bypassed)
    Applied independently at D1 and D9.  Each valid placement adds 15.
    FIXED 2026-03-02: Mercury/Saturn were erroneously getting odd-sign bonus.
    """
    male_planets   = {"SUN", "MARS", "JUPITER"}
    female_planets = {"MOON", "VENUS"}
    # Neutral planets (Mercury, Saturn) explicitly get 0 — no parity bonus
    if planet not in male_planets and planet not in female_planets:
        return 0.0
    score = 0.0
    for lon in (d1_lon, d9_lon):
        s = sign_of(lon)
        is_even = (s % 2 == 1)  # 0=Aries(odd), 1=Taurus(even), ...
        if planet in female_planets:
            if is_even:
                score += 15.0
        else:  # male
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
    Fortnight (lunar phase) strength (Paksha Bala).
    Research File 1 — BPHS Ch.27 / Saravali:
      Elongation E = Moon − Sun (forward arc, 0-360°).
      Half-circle E_h = min(E, 360−E) → 0-180.
      Benefics (Jup, Ven, waxing Moon, benefic Merc): E_h / 3 → 0-60.
      Malefics (Sun, Mars, Sat, waning Moon):        (180 − E_h) / 3 → 0-60.
      MOON DOUBLING RULE: Moon's final value is multiplied by 2 (max 120).
    FIXED 2026-03-02: Moon doubling was missing.
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

    from vedic_engine.config import NATURAL_BENEFICS
    is_benefic = (p in NATURAL_BENEFICS)
    # Moon is benefic when waxing (elongation ≤ 180), malefic when waning
    if planet == "MOON":
        is_benefic = (elongation <= 180.0)

    if is_benefic:
        base = elong_half / 3.0
    else:
        base = (180.0 - elong_half) / 3.0

    # Classical Moon-doubling rule: Paksha Bala for Moon = 2× (max 120 virupas)
    if planet == "MOON":
        return base * 2.0
    return base


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
              sunrise_hour: float = 6.0,
              sunset_hour: float = 18.0) -> float:
    """
    Planetary hour (Hora) lord strength. Lord of birth hora gets 60.
    Research File 1 — BPHS Ch.27: hora lengths are UNEQUAL (temporal horas),
    proportional to actual day/night duration — not fixed 60-minute chunks.
      Day hora length   = (sunset − sunrise) / 12
      Night hora length = (24 − day_dur) / 12
    Sequence starts from weekday lord at sunrise (Chaldean order).
    FIXED 2026-03-02: was using fixed 1-hour horas; now uses proportional lengths.
    """
    chaldean = [Planet.SUN, Planet.VENUS, Planet.MERCURY, Planet.MOON,
                Planet.SATURN, Planet.JUPITER, Planet.MARS]

    weekday = birth_dt.weekday()
    day_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}
    wd = day_map[weekday]
    day_lord = WEEKDAY_LORDS.get(wd, Planet.SUN)
    start_idx = chaldean.index(day_lord)

    hour = birth_dt.hour + birth_dt.minute / 60.0
    day_dur   = max(0.1, sunset_hour - sunrise_hour)
    night_dur = 24.0 - day_dur
    day_hora_len   = day_dur   / 12.0
    night_hora_len = night_dur / 12.0

    if sunrise_hour <= hour < sunset_hour:
        # Day hora: 0-11
        hora_num = min(int((hour - sunrise_hour) / day_hora_len), 11)
    else:
        # Night hora: 12-23
        night_hour = (hour - sunset_hour) % 24.0
        hora_num = 12 + min(int(night_hour / night_hora_len), 11)

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
               tz_offset: float = 5.5,
               planet_trop_lon: Optional[float] = None) -> float:
    """
    Solstice/declination strength (Ayana Bala) — BPHS Ch.27 / Saravali.
    Research File 1 formula:
      dec = arcsin(sin(obliquity) × sin(tropical_longitude))
      Ayana = (23.45 + declination) / 46.9 × 60  [for north-strong planets]
      Ayana = (23.45 - declination) / 46.9 × 60  [for south-strong planets]
    Planet polarity:
      Sun, Mars, Jupiter, Venus → + for north (peaking at summer solstice)
      Moon, Saturn             → + for south (reversed polarity)
      Mercury                  → always + using abs(declination)
      Sun final value           → DOUBLED (max 120 virupas, per BPHS)
    FIXED 2026-03-02: was using Sun\'s declination for all planets;
      now computes per-planet declination from tropical longitude when available.
    """
    import math
    OBLIQUITY_DEG = 23.4393          # J2000 mean obliquity
    OBLIQUITY_RAD = math.radians(OBLIQUITY_DEG)

    p = _P.get(planet)
    if p is None:
        return 0.0

    declination: Optional[float] = None

    # Tier-1a: per-planet from tropical longitude (most accurate)
    if planet_trop_lon is not None:
        trop_rad = math.radians(planet_trop_lon % 360.0)
        dec_rad  = math.asin(math.sin(OBLIQUITY_RAD) * math.sin(trop_rad))
        declination = math.degrees(dec_rad)

    # Tier-1b: SWE solar declination for the Sun (fallback when no lon given)
    if declination is None and planet == "SUN":
        try:
            from vedic_engine.core.swisseph_bridge import compute_solar_declination
            declination = compute_solar_declination(birth_dt, tz_offset)
        except Exception:
            pass

    # Tier-2: month-based season approximation
    if declination is None:
        month = birth_dt.month
        # Approximate: max +23.45 at June 21, min -23.45 at Dec 21
        day_of_year = birth_dt.timetuple().tm_yday
        declination = -OBLIQUITY_DEG * math.cos(math.radians((day_of_year + 10) * 360 / 365.25))

    # Apply planet-specific polarity and scale to 0-60 virupas
    # Formula: (obliquity ± dec) / (2 × obliquity) × 60
    #   North-strong: (obq + dec) / (2*obq) × 60
    #   South-strong: (obq - dec) / (2*obq) × 60
    north_strong = {Planet.SUN, Planet.MARS, Planet.JUPITER, Planet.VENUS}
    south_strong = {Planet.MOON, Planet.SATURN}

    if p == Planet.MERCURY:
        # Mercury always benefits from declination (abs value)
        raw = (OBLIQUITY_DEG + abs(declination)) / (2 * OBLIQUITY_DEG) * 60.0
    elif p in north_strong:
        raw = (OBLIQUITY_DEG + declination) / (2 * OBLIQUITY_DEG) * 60.0
    elif p in south_strong:
        raw = (OBLIQUITY_DEG - declination) / (2 * OBLIQUITY_DEG) * 60.0
    else:
        raw = 30.0  # neutral fallback

    raw = max(0.0, min(60.0, raw))  # clamp 0-60

    # Sun\'s Ayana Bala is DOUBLED per BPHS (max 120)
    if p == Planet.SUN:
        raw = raw * 2.0

    return raw


# Classical Seeghrocha (apogee) constants for Cheshta Bala — Research File 1
# Format: degrees (signs × 30 + degrees + minutes/60)
_SEEGHROCHA: Dict[str, float] = {
    "MARS":    238.667,   # 7s 28°40\'  = 210 + 28 + 40/60
    "MERCURY": 220.567,   # 7s 10°34\'  = 210 + 10 + 34/60
    "JUPITER": 192.183,   # 6s 12°11\'  = 180 + 12 + 11/60
    "VENUS":   224.950,   # 7s 14°57\'  = 210 + 14 + 57/60
    "SATURN":  301.400,   # 10s 01°24\' = 300 + 1  + 24/60
}


def kala_bala(
        planet: str,
        birth_dt: datetime,
        moon_lon: float,
        sun_lon: float,
        sunrise_hour: float = 6.0,
        sunset_hour: float = 18.0,
        tz_offset: float = 5.5,
        planet_trop_lon: Optional[float] = None,
        yuddha_adjustment: float = 0.0,
) -> float:
    """
    Total Kala Bala = Nathonnatha + Paksha + Tribhaga + Vara + Hora + Ayana
                    + Abda (year lord 15) + Masa (month lord 30)
                    + Yuddha adjustment (mass-transfer ± for planetary war)
    sunrise_hour / sunset_hour: actual decimal hours (SWE-precise).
    tz_offset: for per-planet Ayana Bala declination computation.
    planet_trop_lon: tropical (sayana) longitude for Ayana Bala computation.
    yuddha_adjustment: ± virupas from Yuddha Bala (pre-computed by caller).
    UPDATED 2026-03-02: hora_bala now proportional; ayana_bala per-planet;
      yuddha_adjustment integrated.
    """
    return (
        nathonnatha_bala(planet, birth_dt)
        + paksha_bala(planet, moon_lon, sun_lon)
        + tribhaga_bala(planet, birth_dt, sunrise_hour, sunset_hour)
        + vara_bala(planet, birth_dt)
        + hora_bala(planet, birth_dt, sunrise_hour, sunset_hour)
        + ayana_bala(planet, birth_dt, tz_offset, planet_trop_lon)
        + abda_bala(planet, birth_dt)
        + masa_bala(planet, birth_dt, sun_lon)
        + yuddha_adjustment
    )


# ─── 4. Cheshta Bala ──────────────────────────────────────────────

def cheshta_bala(planet: str, is_retrograde: bool, speed: float = 0.0,
                 true_lon: Optional[float] = None) -> float:
    """
    Motional strength (Cheshta Bala) — Research File 1 / BPHS Ch.27.

    Classical Seeghrocha formula (preferred, requires true_lon):
      avg_lon       = (true_lon + seeghrocha) / 2          [circular]
      cheshta_kendra = angular_distance(seeghrocha, avg_lon) → 0-180°
      cheshta_bala  = cheshta_kendra / 3                  → 0-60 virupas
    Physically: planet near its seeghrocha (fast moving) → low score;
      planet opposite seeghrocha (retrograde zone) → high score.

    Speed-state fallback (when true_lon unavailable):
      Retrograde (Vakra)=60, Station=30, Fast Direct=45,
      Normal Direct=30, Slow=15, Very Slow=7.5

    Sun:  Cheshta = Ayana Bala (computed separately in compute_shadbala)
    Moon: Cheshta = Paksha Bala (computed separately in compute_shadbala)
    These are handled by caller; stubs return 0.0 here.
    UPDATED 2026-03-02: Seeghrocha classical formula now primary.
    """
    if planet in ("SUN", "MOON"):
        # Caller (compute_shadbala) overrides with Ayana/Paksha values
        return 0.0

    # ── Seeghrocha method (classical primary) ──
    if true_lon is not None and planet in _SEEGHROCHA:
        seegh = _SEEGHROCHA[planet]
        # circular average of true_lon and seeghrocha
        # circular mean via vector addition:
        import math
        t_rad = math.radians(true_lon)
        s_rad = math.radians(seegh)
        avg_sin = (math.sin(t_rad) + math.sin(s_rad)) / 2
        avg_cos = (math.cos(t_rad) + math.cos(s_rad)) / 2
        avg_lon = math.degrees(math.atan2(avg_sin, avg_cos)) % 360
        # Cheshta Kendra = seeghrocha - avg_lon (shortest arc)
        ck = abs(seegh - avg_lon)
        if ck > 180:
            ck = 360 - ck
        return ck / 3.0  # 0-60 virupas

    # ── Speed-state fallback ──
    _AVG_SPEED = {
        "MARS": 0.52, "MERCURY": 1.38, "JUPITER": 0.083,
        "VENUS": 1.2,  "SATURN": 0.033,
    }
    avg = _AVG_SPEED.get(planet, 0.5)
    abs_spd = abs(speed)

    if is_retrograde:
        return 60.0 if abs_spd > 0.01 else 45.0   # Vakra / Anuvakra
    if abs_spd < 0.005:
        return 30.0   # Vikala (stationary)
    ratio = abs_spd / avg if avg > 0 else 1.0
    if ratio >= 1.5:
        return 45.0   # Ati-Chara
    elif ratio >= 0.9:
        return 30.0   # Chari
    elif ratio >= 0.5:
        return 15.0   # Manda
    return 7.5        # Mandatara


# ─── Yuddha Bala (Planetary War Mass-Transfer) ────────────────────

# Bimba Parimana (planetary disc circumference constants) — Research File 1
_BIMBA_PARIMANA: Dict[str, float] = {
    "MARS":    9.4,
    "MERCURY": 6.6,
    "JUPITER": 190.4,
    "VENUS":   16.6,
    "SATURN":  158.0,
}


def compute_yuddha_adjustments(
        planet_data: dict,       # {pname: PlanetPosition}
        planet_shadbala_pre: Dict[str, float],  # pre-war Kala Bala (excl. Ayana) per planet
) -> Dict[str, float]:
    """
    Yuddha Bala — Planetary War Mass-Transfer (BPHS Ch.27).
    Research File 1 formula:
      Trigger: two non-luminary planets within 1° longitude arc.
      Victor: planet with LOWER ecliptic longitude.
      Mass-transfer differential Δ = |disc_victor - disc_loser|.
      Victor final Kala Bala += Δ;  Loser final Kala Bala -= Δ.
      (Ayana Bala strictly EXCLUDED from pre-war strength sum.)
    Note: Sun, Moon, Rahu, Ketu cannot be combatants.
    Returns dict of virupas adjustment per planet (default 0.0).
    ADDED 2026-03-02: was not previously implemented.
    """
    WAR_ELIGIBLE = {"MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"}
    adjustments = {p: 0.0 for p in PLANET_NAMES_7}

    eligible = [
        pn for pn in WAR_ELIGIBLE
        if pn in planet_data
    ]

    for i, p1 in enumerate(eligible):
        for p2 in eligible[i + 1:]:
            lon1 = planet_data[p1].longitude
            lon2 = planet_data[p2].longitude
            arc = abs(lon1 - lon2)
            if arc > 180:
                arc = 360 - arc
            if arc > 1.0:   # Not in war
                continue
            # Victor = lower longitude; Loser = higher longitude
            if normalize(lon1) < normalize(lon2):
                victor, loser = p1, p2
            else:
                victor, loser = p2, p1
            disc_v = _BIMBA_PARIMANA.get(victor, 0.0)
            disc_l = _BIMBA_PARIMANA.get(loser, 0.0)
            delta = abs(disc_v - disc_l)
            adjustments[victor] += delta
            adjustments[loser]  -= delta

    return adjustments


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
        planet_trop_lon: Optional[float] = None,
        yuddha_adjustment: float = 0.0,
) -> Dict[str, float]:
    """
    Compute all 6 Shadbala components for a planet.
    Returns dict with each component and totals.

    planet_trop_lon: tropical (sayana) longitude for Ayana Bala + Cheshta Bala.
    yuddha_adjustment: ± virupas from Yuddha Bala (pre-computed by caller).
    sunrise_hour / sunset_hour: actual decimal hours for Kala Bala precision.
    tz_offset: for SWE solar declination in Ayana Bala.
    UPDATED 2026-03-02: Sun/Moon Cheshta overrides; Yuddha integration;
      per-planet tropical longitude propagation.
    """
    sb = sthana_bala(planet, longitude, planet_house, planet_signs=planet_signs)
    # Compute saptavargaja separately for net Shadbala (avoids Vimshopak overlap)
    svb = saptavargaja_bala(planet, longitude, planet_signs=planet_signs)
    db = dig_bala(planet, longitude, cusp_longitudes)
    kb = kala_bala(planet, birth_dt, moon_lon, sun_lon,
                   sunrise_hour, sunset_hour, tz_offset,
                   planet_trop_lon=planet_trop_lon,
                   yuddha_adjustment=yuddha_adjustment)

    # Cheshta Bala: Sun = Ayana Bala; Moon = Paksha Bala (classical BPHS rule)
    if planet == "SUN":
        cb = ayana_bala(planet, birth_dt, tz_offset, planet_trop_lon)
    elif planet == "MOON":
        cb = paksha_bala(planet, moon_lon, sun_lon)
    else:
        cb = cheshta_bala(planet, is_retrograde, speed, true_lon=planet_trop_lon)

    nb = naisargika_bala(planet)
    rb = compute_drik_bala(planet, planet_house, planet_houses, moon_waxing)

    total = sb + db + kb + cb + nb + rb
    rupas = total / 60.0
    p = _P.get(planet)
    min_req = SHADBALA_MINIMUMS.get(p, 5.0) if p else 5.0
    ratio = rupas / min_req if min_req > 0 else 0.0

    # Net Shadbala = Total - Saptavargaja (Research File 1: avoids
    # double-counting with Vimshopak which also measures varga dignity)
    net_total = total - svb
    net_rupas = net_total / 60.0
    net_ratio = net_rupas / min_req if min_req > 0 else 0.0

    return {
        "sthana_bala": round(sb, 2),
        "saptavargaja_bala": round(svb, 2),
        "dig_bala": round(db, 2),
        "kala_bala": round(kb, 2),
        "cheshta_bala": round(cb, 2),
        "naisargika_bala": round(nb, 2),
        "drik_bala": round(rb, 2),
        "total": round(total, 2),
        "rupas": round(rupas, 3),
        "minimum_required": min_req,
        "ratio": round(ratio, 3),
        "net_ratio": round(net_ratio, 3),
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
    UPDATED 2026-03-02: now computes tropical longitudes (sidereal + ayanamsa)
    and pre-computes Yuddha Bala adjustments before per-planet shadbala pass.
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

    # ── Compute tropical (sayana) longitudes for Ayana Bala + Cheshta Bala ──
    # tropical = sidereal + ayanamsa; attempt to get ayanamsa from engine
    ayanamsa: float = 0.0
    try:
        from vedic_engine.core.swisseph_bridge import get_ayanamsa
        ayanamsa = get_ayanamsa(birth_dt, tz_offset)
    except Exception:
        pass  # 0-ayanamsa means tropical ≈ sidereal (error ≤24°; ayana_bala degrades gracefully)

    planet_trop_lons: Dict[str, float] = {
        pn: (getattr(pp, "longitude", 0.0) + ayanamsa) % 360.0
        for pn, pp in planet_data.items()
        if pn in PLANET_NAMES_7
    }

    # ── Pre-compute Yuddha Bala (Planetary War) adjustments ──
    # Uses pre-war strength (rough total); no circular dependency needed
    yuddha_adjustments = compute_yuddha_adjustments(planet_data, {})

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
            planet_trop_lon=planet_trop_lons.get(pname),
            yuddha_adjustment=yuddha_adjustments.get(pname, 0.0),
        )
    return results
