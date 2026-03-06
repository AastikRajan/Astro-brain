"""
Swiss Ephemeris Bridge — Gold-Standard Astronomical Backend.

pyswisseph (Swiss Ephemeris) is the INDUSTRY GOLD STANDARD for astrological
position computation.  Now that it is installed, this module provides:

1. NATAL CHART COMPUTATION from birth data (date/time/place) — replacing
   the JSON-import-only path with a COMPUTE-FROM-SCRATCH capability.
2. TRANSIT POSITIONS (already tier-1 in transits.py, now enhanced with
   speed, retrograde detection, and house cusps).
3. HOUSE CUSPS (Placidus for KP, Whole-Sign for Parashari, Sripathi).
4. DIVISIONAL CHART COMPUTATION using precise longitudes.
5. AYANAMSA — official Lahiri (Chitra Paksha), consistent with Indian
   government Rashtriya Panchang.
6. PLANETARY SPEEDS — exact daily motion for retrograde detection, combust
   orb calculations, and Cheshta Bala.

Accuracy: < 0.001° for all classical planets, <0.01° for Rahu/Ketu.
This is the most precise backend available — Skyfield/astropy/ephem are kept
as cross-validation tiers but Swiss Ephemeris is now the primary.

Usage:
    from vedic_engine.core.swisseph_bridge import (
        compute_natal_positions,
        compute_house_cusps,
        build_chart_from_birth_data,
        get_transit_positions_swe,
    )
"""
from __future__ import annotations

import math
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ─── Availability guard ───────────────────────────────────────────────────────

try:
    import swisseph as swe
    _SWE_AVAILABLE = True
except ImportError:
    _SWE_AVAILABLE = False
    logger.warning("[swisseph_bridge] pyswisseph not installed — bridge disabled.")

# ─── Constants ────────────────────────────────────────────────────────────────

# Planet ID mapping (pyswisseph constants)
_SWE_PLANETS = {
    "SUN":     0,   # swe.SUN
    "MOON":    1,   # swe.MOON
    "MERCURY": 2,   # swe.MERCURY
    "VENUS":   3,   # swe.VENUS
    "MARS":    4,   # swe.MARS
    "JUPITER": 5,   # swe.JUPITER
    "SATURN":  6,   # swe.SATURN
    "RAHU":   10,   # swe.MEAN_NODE (mean lunar node)
}

# For True Node (oscillating Rahu) — more precise but jittery
_SWE_TRUE_NODE = 11  # swe.TRUE_NODE

PLANET_ORDER = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU"]

# Nakshatra data
NAKSHATRA_SPAN = 360.0 / 27.0  # 13.333...°
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]
NAKSHATRA_LORDS = [
    "KETU", "VENUS", "SUN", "MOON", "MARS", "RAHU",
    "JUPITER", "SATURN", "MERCURY", "KETU", "VENUS", "SUN",
    "MOON", "MARS", "RAHU", "JUPITER", "SATURN", "MERCURY",
    "KETU", "VENUS", "SUN", "MOON", "MARS", "RAHU",
    "JUPITER", "SATURN", "MERCURY",
]

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Combustion orbs (degrees from Sun) — BPHS / Surya Siddhanta
COMBUSTION_ORBS = {
    "MOON": 12.0, "MARS": 17.0, "MERCURY": 14.0,  # 12° when retrograde
    "JUPITER": 11.0, "VENUS": 10.0, "SATURN": 15.0,
}

# House system codes for swe.houses_ex
HOUSE_SYSTEMS = {
    "placidus":   b'P',
    "whole_sign": b'W',
    "equal":      b'E',
    "koch":       b'K',
    "sripathi":   b'P',  # Sripathi ≈ Placidus in classical Indian usage
    "campanus":   b'C',
    "porphyry":   b'O',
}


# ─── Initialization ──────────────────────────────────────────────────────────

def _init_swe(ayanamsa: str = "lahiri", ephe_path: Optional[str] = None):
    """Initialize Swiss Ephemeris with Lahiri ayanamsa."""
    if not _SWE_AVAILABLE:
        raise ImportError("pyswisseph is not installed. Run: pip install pyswisseph")

    if ephe_path:
        swe.set_ephe_path(ephe_path)
    else:
        swe.set_ephe_path("")  # use built-in Moshier ephemeris (no external files needed)

    # Ayanamsa selection
    ayan_map = {
        "lahiri":      swe.SIDM_LAHIRI,
        "raman":       swe.SIDM_RAMAN,
        "krishnamurti": swe.SIDM_KRISHNAMURTI,
        "kp":          swe.SIDM_KRISHNAMURTI,
        "fagan_bradley": swe.SIDM_FAGAN_BRADLEY,
        "true_chitra": swe.SIDM_TRUE_CITRA,
    }
    sid_mode = ayan_map.get(ayanamsa.lower(), swe.SIDM_LAHIRI)
    swe.set_sid_mode(sid_mode)


def _datetime_to_jd(dt: datetime, tz_offset: float = 0.0) -> float:
    """Convert datetime + timezone offset to Julian Day (UT)."""
    # Convert local time to UTC
    utc_dt = dt - timedelta(hours=tz_offset)
    hour_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)


# ─── Core Position Computation ────────────────────────────────────────────────

def compute_natal_positions(
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
    use_true_node: bool = False,
) -> Dict[str, Dict[str, Any]]:
    """
    Compute precise sidereal planetary positions for a birth chart.

    Returns a rich dict per planet with:
      longitude        : sidereal absolute 0-360°
      tropical_lon     : tropical longitude (for reference)
      sign_index       : 0-11
      sign_name        : "Aries"..."Pisces"
      degree_in_sign   : 0-30°
      nakshatra_index  : 0-26
      nakshatra_name   : e.g. "Ashwini"
      nakshatra_lord   : e.g. "KETU"
      pada             : 1-4
      speed            : deg/day (negative = retrograde)
      is_retrograde    : bool
      latitude         : ecliptic latitude (for Graha Yuddha)
      distance         : AU from Earth

    Args:
        birth_dt    : Local datetime of birth
        latitude    : Birth place latitude (degrees, N positive)
        longitude   : Birth place longitude (degrees, E positive)
        tz_offset   : UTC offset in hours (5.5 for IST)
        ayanamsa    : "lahiri" (default), "krishnamurti", "raman", etc.
        use_true_node: True for oscillating Rahu, False for mean node (default)
    """
    _init_swe(ayanamsa)
    jd = _datetime_to_jd(birth_dt, tz_offset)
    ayanamsa_value = swe.get_ayanamsa(jd)

    positions: Dict[str, Dict[str, Any]] = {}

    for planet_name, swe_id in _SWE_PLANETS.items():
        # Use True Node if requested
        if planet_name == "RAHU" and use_true_node:
            swe_id = _SWE_TRUE_NODE

        result, ret_flag = swe.calc_ut(jd, swe_id)
        # result = (longitude, latitude, distance, speed_lon, speed_lat, speed_dist)
        tropical_lon = result[0]
        ecl_lat      = result[1]
        distance_au  = result[2]
        speed        = result[3]  # deg/day

        sidereal_lon = (tropical_lon - ayanamsa_value) % 360.0
        sign_idx     = int(sidereal_lon / 30.0) % 12
        deg_in_sign  = sidereal_lon % 30.0
        nak_idx      = int(sidereal_lon / NAKSHATRA_SPAN) % 27
        pos_in_nak   = sidereal_lon % NAKSHATRA_SPAN
        pada         = min(int(pos_in_nak / (NAKSHATRA_SPAN / 4.0)) + 1, 4)

        positions[planet_name] = {
            "longitude":       round(sidereal_lon, 6),
            "tropical_lon":    round(tropical_lon, 6),
            "sign_index":      sign_idx,
            "sign_name":       SIGN_NAMES[sign_idx],
            "degree_in_sign":  round(deg_in_sign, 4),
            "nakshatra_index": nak_idx,
            "nakshatra_name":  NAKSHATRA_NAMES[nak_idx],
            "nakshatra_lord":  NAKSHATRA_LORDS[nak_idx],
            "pada":            pada,
            "speed":           round(speed, 6),
            "is_retrograde":   speed < 0,
            "latitude":        round(ecl_lat, 4),
            "distance_au":     round(distance_au, 6),
        }

    # Ketu = 180° from Rahu
    if "RAHU" in positions:
        rahu = positions["RAHU"]
        ketu_sid = (rahu["longitude"] + 180.0) % 360.0
        ketu_sign = int(ketu_sid / 30.0) % 12
        ketu_deg  = ketu_sid % 30.0
        ketu_nak  = int(ketu_sid / NAKSHATRA_SPAN) % 27
        ketu_pos  = ketu_sid % NAKSHATRA_SPAN
        ketu_pada = min(int(ketu_pos / (NAKSHATRA_SPAN / 4.0)) + 1, 4)

        positions["KETU"] = {
            "longitude":       round(ketu_sid, 6),
            "tropical_lon":    round((rahu["tropical_lon"] + 180.0) % 360.0, 6),
            "sign_index":      ketu_sign,
            "sign_name":       SIGN_NAMES[ketu_sign],
            "degree_in_sign":  round(ketu_deg, 4),
            "nakshatra_index": ketu_nak,
            "nakshatra_name":  NAKSHATRA_NAMES[ketu_nak],
            "nakshatra_lord":  NAKSHATRA_LORDS[ketu_nak],
            "pada":            ketu_pada,
            "speed":           rahu["speed"],  # same magnitude
            "is_retrograde":   True,  # Ketu always retrograde
            "latitude":        0.0,
            "distance_au":     rahu["distance_au"],
        }

    # ── Combustion check ──────────────────────────────────────────────────
    sun_lon = positions.get("SUN", {}).get("longitude", 0.0)
    for pname, pdata in positions.items():
        if pname in ("SUN", "RAHU", "KETU"):
            pdata["is_combust"] = False
            continue
        orb = COMBUSTION_ORBS.get(pname, 15.0)
        # Special: Mercury retrograde has tighter orb (12°)
        if pname == "MERCURY" and pdata["is_retrograde"]:
            orb = 12.0
        arc = abs((pdata["longitude"] - sun_lon + 180.0) % 360.0 - 180.0)
        pdata["is_combust"] = arc <= orb
        pdata["combustion_arc"] = round(arc, 2)

    return positions


# ─── House Cusp Computation ──────────────────────────────────────────────────

def compute_house_cusps(
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
    house_system: str = "placidus",
) -> Dict[str, Any]:
    """
    Compute house cusps and Ascendant/MC using Swiss Ephemeris.

    Supports: Placidus (KP standard), Whole Sign, Equal, Koch, Campanus.

    Returns:
        cusps         : list of 12 sidereal longitudes [house1...house12]
        ascendant     : sidereal Ascendant longitude
        mc            : sidereal MC longitude
        armc          : sidereal ARMC (for progressions)
        vertex        : sidereal Vertex
        lagna_sign    : 0-11
        lagna_degree  : absolute sidereal longitude
        ayanamsa_value: ayanamsa used (degrees)
        house_system  : system name
    """
    _init_swe(ayanamsa)
    jd = _datetime_to_jd(birth_dt, tz_offset)
    ayanamsa_value = swe.get_ayanamsa(jd)

    hsys = HOUSE_SYSTEMS.get(house_system.lower(), b'P')

    cusps_trop, angles_trop = swe.houses(jd, latitude, longitude, hsys)
    # cusps_trop: tuple of 12 tropical longitudes (house 1-12)
    # angles_trop: (ascendant, MC, ARMC, vertex, ...)

    # Convert to sidereal
    cusps_sid = [round((c - ayanamsa_value) % 360.0, 4) for c in cusps_trop]
    asc_sid   = (angles_trop[0] - ayanamsa_value) % 360.0
    mc_sid    = (angles_trop[1] - ayanamsa_value) % 360.0
    armc_sid  = angles_trop[2]  # ARMC doesn't need ayanamsa correction
    vertex    = (angles_trop[3] - ayanamsa_value) % 360.0

    lagna_sign = int(asc_sid / 30.0) % 12

    return {
        "cusps":          cusps_sid,
        "ascendant":      round(asc_sid, 4),
        "mc":             round(mc_sid, 4),
        "armc":           round(armc_sid, 4),
        "vertex":         round(vertex, 4),
        "lagna_sign":     lagna_sign,
        "lagna_sign_name": SIGN_NAMES[lagna_sign],
        "lagna_degree":   round(asc_sid, 4),
        "ayanamsa_value": round(ayanamsa_value, 4),
        "house_system":   house_system,
    }


# ─── Full Chart Builder ─────────────────────────────────────────────────────

def build_chart_from_birth_data(
    name: str,
    date_str: str,
    time_str: str,
    place: str,
    latitude: float,
    longitude: float,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
    house_system: str = "placidus",
    use_true_node: bool = False,
) -> Dict[str, Any]:
    """
    Build a complete natal chart from birth data using Swiss Ephemeris.

    This is the PRIMARY chart computation path — no JSON export needed.
    Returns a dict that can be fed directly to load_from_dict() to create
    a VedicChart object, or used standalone.

    Args:
        name        : Native's name
        date_str    : "YYYY-MM-DD"
        time_str    : "HH:MM:SS"
        place       : Place name string
        latitude    : Birth latitude (N positive)
        longitude   : Birth longitude (E positive)
        tz_offset   : UTC offset hours (5.5 for IST)
        ayanamsa    : "lahiri", "krishnamurti", "raman"
        house_system: "placidus", "whole_sign", "equal"
        use_true_node: True for oscillating Rahu

    Returns:
        Dict compatible with load_from_dict() — contains birth_info, lagna,
        planets, houses, with all positions computed by Swiss Ephemeris.
    """
    # Parse birth datetime
    birth_dt = datetime.fromisoformat(f"{date_str}T{time_str}")

    # ── Compute positions ──────────────────────────────────────────────
    planet_positions = compute_natal_positions(
        birth_dt, latitude, longitude, tz_offset, ayanamsa, use_true_node
    )

    # ── Compute house cusps ────────────────────────────────────────────
    house_data = compute_house_cusps(
        birth_dt, latitude, longitude, tz_offset, ayanamsa, house_system
    )

    asc_lon  = house_data["ascendant"]
    lagna_sign = house_data["lagna_sign"]

    # ── Build loader-compatible dict ───────────────────────────────────
    chart_dict: Dict[str, Any] = {
        "birth_info": {
            "name":          name,
            "date":          date_str,
            "time":          time_str,
            "place":         place,
            "latitude":      latitude,
            "longitude":     longitude,
            "timezone":      tz_offset,
            "ayanamsa":      house_data["ayanamsa_value"],
            "ayanamsa_model": ayanamsa.capitalize(),
        },
        "lagna": {
            "sign":    SIGN_NAMES[lagna_sign],
            "degree":  asc_lon,   # absolute sidereal
        },
        "planets": {},
        "houses": {},
        "_swe_metadata": {
            "house_system":   house_system,
            "ayanamsa_value": house_data["ayanamsa_value"],
            "ayanamsa_model": ayanamsa,
            "mc":             house_data["mc"],
            "armc":           house_data["armc"],
            "vertex":         house_data["vertex"],
            "use_true_node":  use_true_node,
            "engine":         "pyswisseph",
        },
    }

    # ── Planets ────────────────────────────────────────────────────────
    sun_lon = planet_positions.get("SUN", {}).get("longitude", 0.0)
    for pname in PLANET_ORDER:
        if pname not in planet_positions:
            continue
        p = planet_positions[pname]
        chart_dict["planets"][pname] = {
            "sign":            p["sign_name"],
            "degree_in_sign":  p["degree_in_sign"],
            "longitude":       p["longitude"],
            "retrograde":      p["is_retrograde"],
            "combust":         p.get("is_combust", False),
            "speed":           p["speed"],
            "nakshatra":       p["nakshatra_name"],
            "nakshatra_lord":  p["nakshatra_lord"],
            "pada":            p["pada"],
            "latitude":        p.get("latitude", 0.0),
        }

    # ── Houses ─────────────────────────────────────────────────────────
    cusps = house_data["cusps"]
    from vedic_engine.config import SIGN_LORDS, Sign
    for i in range(12):
        cusp_lon = cusps[i]
        sign_idx = int(cusp_lon / 30.0) % 12
        try:
            lord = SIGN_LORDS[Sign(sign_idx)].name
        except (KeyError, ValueError):
            lord = ""
        chart_dict["houses"][str(i + 1)] = {
            "house":     i + 1,
            "longitude": cusp_lon,
            "sign":      SIGN_NAMES[sign_idx],
            "lord":      lord,
        }

    return chart_dict


# ─── Bhava Chalit Shift Detection ────────────────────────────────────────────

def compute_chalit_shifts(
    planet_lons: Dict[str, float],
    cusp_lons: List[float],
) -> List[Dict[str, Any]]:
    """
    Compare Rashi-based house placement vs Bhava Chalit (cusp-based) placement.
    Returns a list of planets that shift houses between the two systems.

    Args:
        planet_lons: {planet_name: sidereal_longitude}
        cusp_lons:   list of 12 sidereal cusp longitudes (house 1-12)

    Returns:
        List of dicts with keys: planet, rashi_house, chalit_house
        (only for planets that shifted)
    """
    shifts: List[Dict[str, Any]] = []
    for pname, lon in planet_lons.items():
        rashi_house = int(lon / 30.0) % 12 + 1

        # Determine chalit house from cusp boundaries
        chalit_house = 12  # default: last house
        for i in range(12):
            cusp_start = cusp_lons[i]
            cusp_end = cusp_lons[(i + 1) % 12]
            if cusp_start < cusp_end:
                if cusp_start <= lon < cusp_end:
                    chalit_house = i + 1
                    break
            else:  # wraps around 360°
                if lon >= cusp_start or lon < cusp_end:
                    chalit_house = i + 1
                    break

        if rashi_house != chalit_house:
            shifts.append({
                "planet": pname,
                "rashi_house": rashi_house,
                "chalit_house": chalit_house,
            })
    return shifts


# ─── Transit Positions (enhanced) ────────────────────────────────────────────

def get_transit_positions_swe(
    on_date: datetime,
    ayanamsa: str = "lahiri",
    use_true_node: bool = False,
) -> Dict[str, float]:
    """
    Get sidereal transit positions using Swiss Ephemeris.
    Returns simple {planet: longitude} dict compatible with transits.py.
    """
    _init_swe(ayanamsa)
    # Treat naive datetime as UTC (standard astrological convention)
    jd = swe.julday(on_date.year, on_date.month, on_date.day,
                    on_date.hour + on_date.minute / 60.0 + on_date.second / 3600.0)
    ayanamsa_value = swe.get_ayanamsa(jd)

    positions: Dict[str, float] = {}
    for pname, swe_id in _SWE_PLANETS.items():
        if pname == "RAHU" and use_true_node:
            swe_id = _SWE_TRUE_NODE
        result, _ = swe.calc_ut(jd, swe_id)
        sidereal_lon = (result[0] - ayanamsa_value) % 360.0
        positions[pname] = round(sidereal_lon, 5)

    if "RAHU" in positions:
        positions["KETU"] = round((positions["RAHU"] + 180.0) % 360.0, 5)

    return positions


def get_transit_speeds_swe(
    on_date: datetime,
    ayanamsa: str = "lahiri",
) -> Dict[str, float]:
    """
    Get planetary speeds (deg/day) from Swiss Ephemeris.
    Negative speed = retrograde.
    """
    _init_swe(ayanamsa)
    jd = swe.julday(on_date.year, on_date.month, on_date.day,
                    on_date.hour + on_date.minute / 60.0)

    speeds: Dict[str, float] = {}
    for pname, swe_id in _SWE_PLANETS.items():
        result, _ = swe.calc_ut(jd, swe_id)
        speeds[pname] = round(result[3], 6)

    if "RAHU" in speeds:
        speeds["KETU"] = speeds["RAHU"]  # same speed, always retrograde

    return speeds


# ─── Solar Return (Varshaphala) ──────────────────────────────────────────────

def compute_solar_return(
    birth_dt: datetime,
    year: int,
    latitude: float,
    longitude: float,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """
    Compute the exact moment the Sun returns to its natal sidereal longitude
    in the given year (Solar Return / Varshaphala / Tajaka annual chart).

    Returns:
        solar_return_dt : exact UTC datetime of Sun's return
        chart           : full chart dict for that moment (same format as
                          build_chart_from_birth_data output)
    """
    _init_swe(ayanamsa)
    birth_jd = _datetime_to_jd(birth_dt, tz_offset)
    ayanamsa_birth = swe.get_ayanamsa(birth_jd)

    # Get natal Sun tropical longitude
    natal_sun, _ = swe.calc_ut(birth_jd, _SWE_PLANETS["SUN"])
    natal_sun_trop = natal_sun[0]

    # Search for the moment Sun reaches the same tropical longitude in target year
    # Start searching from ~10 days before the birthday in the target year
    search_start = datetime(year, birth_dt.month, max(1, birth_dt.day - 10))
    jd_search = swe.julday(search_start.year, search_start.month, search_start.day, 12.0)

    # Iterative search (Newton-Raphson style)
    for _iteration in range(50):
        sun_now, _ = swe.calc_ut(jd_search, _SWE_PLANETS["SUN"])
        diff = (sun_now[0] - natal_sun_trop + 180.0) % 360.0 - 180.0
        if abs(diff) < 0.0001:  # < 0.36 arc-seconds
            break
        speed = sun_now[3]  # deg/day
        if abs(speed) > 0.01:
            jd_search -= diff / speed
        else:
            jd_search += 0.5

    # Convert JD back to datetime
    sr_tuple = swe.revjul(jd_search)  # (year, month, day, hour_decimal)
    sr_hour = sr_tuple[3]
    sr_dt = datetime(
        int(sr_tuple[0]), int(sr_tuple[1]), int(sr_tuple[2]),
        int(sr_hour), int((sr_hour % 1) * 60), int(((sr_hour * 60) % 1) * 60)
    )
    # sr_dt is UTC; convert to local
    sr_local = sr_dt + timedelta(hours=tz_offset)

    # Build chart for that moment
    chart = build_chart_from_birth_data(
        name=f"Solar Return {year}",
        date_str=sr_local.strftime("%Y-%m-%d"),
        time_str=sr_local.strftime("%H:%M:%S"),
        place="Solar Return",
        latitude=latitude,
        longitude=longitude,
        tz_offset=tz_offset,
        ayanamsa=ayanamsa,
    )

    return {
        "solar_return_utc":   sr_dt.isoformat(),
        "solar_return_local": sr_local.isoformat(),
        "natal_sun_tropical": round(natal_sun_trop, 6),
        "chart":              chart,
    }


# ─── Ayanamsa Query ─────────────────────────────────────────────────────────

def get_ayanamsa(
    dt: datetime,
    tz_offset: float = 0.0,
    model: str = "lahiri",
) -> float:
    """Return the ayanamsa value in degrees for a given datetime."""
    _init_swe(model)
    jd = _datetime_to_jd(dt, tz_offset)
    return round(swe.get_ayanamsa(jd), 6)


# ─── Utility: Planetary War Detection ───────────────────────────────────────

def detect_graha_yuddha_precise(
    birth_dt: datetime,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """
    Detect Graha Yuddha (planetary war) using precise ecliptic latitudes
    from Swiss Ephemeris. Two planets in war when within 1° longitude AND
    both have similar ecliptic latitude (both visible to naked eye).

    Only applies to the 5 true planets: Mars, Mercury, Jupiter, Venus, Saturn.
    """
    WAR_PLANETS = ["MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]
    _init_swe(ayanamsa)
    jd = _datetime_to_jd(birth_dt, tz_offset)
    ayanamsa_value = swe.get_ayanamsa(jd)

    planet_data = {}
    for pname in WAR_PLANETS:
        result, _ = swe.calc_ut(jd, _SWE_PLANETS[pname])
        planet_data[pname] = {
            "longitude": (result[0] - ayanamsa_value) % 360.0,
            "latitude":  result[1],
            "speed":     result[3],
        }

    wars = []
    for i, p1 in enumerate(WAR_PLANETS):
        for p2 in WAR_PLANETS[i+1:]:
            d1 = planet_data[p1]
            d2 = planet_data[p2]
            arc = abs((d1["longitude"] - d2["longitude"] + 180.0) % 360.0 - 180.0)
            if arc <= 1.0:
                # Closer latitude to ecliptic = brighter, higher → winner
                # In classical war: northern latitude (positive) = winner
                if d1["latitude"] > d2["latitude"]:
                    winner, loser = p1, p2
                else:
                    winner, loser = p2, p1
                wars.append({
                    "planet1":       p1,
                    "planet2":       p2,
                    "arc_degrees":   round(arc, 4),
                    "winner":        winner,
                    "loser":         loser,
                    "lat_p1":        round(d1["latitude"], 4),
                    "lat_p2":        round(d2["latitude"], 4),
                })
    return wars


# ─── Precise Sunrise / Sunset (swe.rise_trans) ──────────────────────────────

def compute_sunrise_sunset_swe(
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """
    Compute precise sunrise & sunset using Swiss Ephemeris ``swe.rise_trans()``.

    Accuracy: < 1 second (vs ±2 minutes for the NOAA pure-Python algorithm).
    This is critical for:
      - Gulika / Mandi calculation (day portions depend on sunrise/sunset)
      - Hora Bala (planetary hour lord depends on sunrise)
      - Tribhaga Bala (day/night thirds depend on sunrise/sunset)
      - Daytime / nighttime birth classification

    Returns dict with sunrise/sunset in UTC, local, and as decimal hours.
    """
    if not _SWE_AVAILABLE:
        raise ImportError("pyswisseph not installed")

    _init_swe(ayanamsa)

    # JD at midnight UTC of the local birth date
    local_midnight = datetime(birth_dt.year, birth_dt.month, birth_dt.day)
    utc_midnight = local_midnight - timedelta(hours=tz_offset)
    jd_midnight = swe.julday(utc_midnight.year, utc_midnight.month,
                             utc_midnight.day,
                             utc_midnight.hour + utc_midnight.minute / 60.0)

    # swe.rise_trans flags:  1 = rise, 2 = set
    CALC_RISE = 1
    CALC_SET = 2

    geopos = (longitude, latitude, 0.0)  # (lon, lat, altitude_m)

    try:
        rise_result = swe.rise_trans(jd_midnight, swe.SUN, geopos=geopos,
                                     rsmi=CALC_RISE)
        jd_sunrise = rise_result[1][0]

        set_result = swe.rise_trans(jd_midnight, swe.SUN, geopos=geopos,
                                    rsmi=CALC_SET)
        jd_sunset = set_result[1][0]

        def _jd_to_dt(jd_val: float) -> datetime:
            tup = swe.revjul(jd_val)
            h = tup[3]
            return datetime(int(tup[0]), int(tup[1]), int(tup[2]),
                            int(h), int((h % 1) * 60),
                            int(((h * 60) % 1) * 60))

        sunrise_utc = _jd_to_dt(jd_sunrise)
        sunset_utc = _jd_to_dt(jd_sunset)
        sunrise_local = sunrise_utc + timedelta(hours=tz_offset)
        sunset_local = sunset_utc + timedelta(hours=tz_offset)

        sr_h = sunrise_local.hour + sunrise_local.minute / 60.0 + sunrise_local.second / 3600.0
        ss_h = sunset_local.hour + sunset_local.minute / 60.0 + sunset_local.second / 3600.0
        day_dur = (jd_sunset - jd_sunrise) * 24.0
        night_dur = 24.0 - day_dur

        return {
            "sunrise_utc": sunrise_utc,
            "sunset_utc": sunset_utc,
            "sunrise_local": sunrise_local,
            "sunset_local": sunset_local,
            "sunrise_hour_local": round(sr_h, 4),
            "sunset_hour_local": round(ss_h, 4),
            "day_duration_hrs": round(day_dur, 4),
            "night_duration_hrs": round(night_dur, 4),
            "source": "swisseph_rise_trans",
        }
    except Exception as e:
        logger.warning("[swisseph_bridge] rise_trans failed: %s", e)
        raise


# ─── Topocentric Moon (SWE FLG_TOPOCTR) ─────────────────────────────────────

def compute_topocentric_moon_swe(
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    altitude_m: float = 0.0,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """
    Compute precise TOPOCENTRIC Moon using ``swe.FLG_TOPOCTR``.

    Applies the observer's lat/lon/altitude correction directly, giving the
    Moon's position as seen from the birth place — not the Earth's centre.
    Corrects up to ±1° of parallax.

    Critical for Vimshottari Dasha balance, KP Sub-Lord, Navamsha/D60.
    """
    if not _SWE_AVAILABLE:
        raise ImportError("pyswisseph not installed")

    _init_swe(ayanamsa)
    jd = _datetime_to_jd(birth_dt, tz_offset)
    ayanamsa_value = swe.get_ayanamsa(jd)

    # Set observer location for topocentric computation
    swe.set_topo(longitude, latitude, altitude_m)

    # Geocentric Moon
    geo_result, _ = swe.calc_ut(jd, swe.MOON)
    geo_lon_sid = (geo_result[0] - ayanamsa_value) % 360.0

    # Topocentric Moon
    topo_flags = swe.FLG_SWIEPH | swe.FLG_TOPOCTR
    topo_result, _ = swe.calc_ut(jd, swe.MOON, topo_flags)
    topo_lon_sid = (topo_result[0] - ayanamsa_value) % 360.0

    delta_lon = ((topo_lon_sid - geo_lon_sid) + 180.0) % 360.0 - 180.0

    distance_km = topo_result[2] * 149597870.7  # AU → km

    nak_geo = int(geo_lon_sid / NAKSHATRA_SPAN) % 27
    nak_topo = int(topo_lon_sid / NAKSHATRA_SPAN) % 27
    sign_geo = int(geo_lon_sid / 30.0) % 12
    sign_topo = int(topo_lon_sid / 30.0) % 12

    return {
        "lon_geocentric": round(geo_lon_sid, 6),
        "lon_topocentric": round(topo_lon_sid, 6),
        "delta_lon": round(delta_lon, 6),
        "lat_topocentric": round(topo_result[1], 6),
        "distance_km": round(distance_km, 1),
        "speed": round(topo_result[3], 6),
        "nakshatra_geo": nak_geo,
        "nakshatra_topo": nak_topo,
        "sign_geo": sign_geo,
        "sign_topo": sign_topo,
        "boundary_crossed": (nak_geo != nak_topo) or (sign_geo != sign_topo),
        "source": "swisseph_FLG_TOPOCTR",
    }


# ─── Solar Declination (for Ayana Bala) ─────────────────────────────────────

def compute_solar_declination(
    birth_dt: datetime,
    tz_offset: float = 5.5,
) -> float:
    """
    Sun's declination (degrees) at birth time via SWE.
    Replaces the month-based Ayana Bala approximation with exact value.
    Positive = North of equator (Uttarayana), Negative = South (Dakshinayana).
    """
    if not _SWE_AVAILABLE:
        raise ImportError("pyswisseph not installed")
    _init_swe()
    jd = _datetime_to_jd(birth_dt, tz_offset)
    result, _ = swe.calc_ut(jd, swe.SUN)
    lam = math.radians(result[0])    # tropical longitude
    beta = math.radians(result[1])   # ecliptic latitude (~0)
    eps = math.radians(23.4393)      # mean obliquity
    sin_dec = (math.sin(beta) * math.cos(eps)
               + math.cos(beta) * math.sin(eps) * math.sin(lam))
    return round(math.degrees(math.asin(sin_dec)), 4)


# ─── Lunation — SWE-based New/Full Moon Search ──────────────────────────────

def _elongation_at(jd: float) -> float:
    """Return (Moon - Sun) elongation in 0..360 at given JD, with speed."""
    flags = swe.FLG_SPEED
    sun_r, _ = swe.calc_ut(jd, swe.SUN, flags)
    moon_r, _ = swe.calc_ut(jd, swe.MOON, flags)
    elong = (moon_r[0] - sun_r[0]) % 360.0
    speed = moon_r[3] - sun_r[3]  # relative speed, ~11-14 deg/day
    return elong, speed


def _find_lunation_jd(jd_start: float, target_elong: float) -> float:
    """
    Robust lunation finder — returns JD of NEXT time Sun-Moon elongation
    equals *target_elong* (0 for New Moon, 180 for Full Moon).

    Strategy:
      1. Coarse scan forward in 1-day steps until we bracket the target.
      2. Bisection to narrow to ±0.01 days.
      3. Newton-Raphson polish for sub-second accuracy.
    """
    SYNODIC = 29.530589  # mean synodic month

    def _diff(jd):
        """Signed angular difference from target, in [-180, 180]."""
        e, spd = _elongation_at(jd)
        d = (e - target_elong + 180.0) % 360.0 - 180.0
        return d, spd

    # ── Step 1: coarse scan (1-day steps, up to 35 days) ──────────────
    jd_prev = jd_start
    d_prev, _ = _diff(jd_prev)
    jd_a = jd_b = None

    for i in range(1, 36):
        jd_cur = jd_start + i
        d_cur, _ = _diff(jd_cur)
        # Sign change means the target was crossed in [jd_prev, jd_cur]
        if d_prev * d_cur <= 0 and abs(d_prev - d_cur) < 300:
            jd_a, jd_b = jd_prev, jd_cur
            break
        jd_prev, d_prev = jd_cur, d_cur

    if jd_a is None:
        # Fallback: advance by half a synodic month and retry
        return _find_lunation_jd(jd_start + SYNODIC / 2, target_elong)

    # ── Step 2: bisection to ±0.01 days (~14 min) ────────────────────
    for _ in range(30):
        jd_mid = (jd_a + jd_b) / 2.0
        d_mid, _ = _diff(jd_mid)
        if abs(d_mid) < 0.001:
            break
        d_a, _ = _diff(jd_a)
        if d_a * d_mid <= 0:
            jd_b = jd_mid
        else:
            jd_a = jd_mid

    # ── Step 3: Newton polish (up to 10 iterations) ──────────────────
    jd = (jd_a + jd_b) / 2.0
    for _ in range(10):
        d, spd = _diff(jd)
        if abs(d) < 0.00001:  # ~1 second of arc
            break
        if abs(spd) < 0.01:
            break
        correction = d / spd
        correction = max(-2.0, min(2.0, correction))  # clamp
        jd -= correction

    return jd


def compute_next_new_moon_jd(jd_start: float) -> float:
    """Find JD of next New Moon (Sun-Moon elongation = 0°)."""
    if not _SWE_AVAILABLE:
        raise ImportError("pyswisseph not installed")
    _init_swe()
    return _find_lunation_jd(jd_start, 0.0)


def compute_next_full_moon_jd(jd_start: float) -> float:
    """Find JD of next Full Moon (elongation = 180°)."""
    if not _SWE_AVAILABLE:
        raise ImportError("pyswisseph not installed")
    _init_swe()
    return _find_lunation_jd(jd_start, 180.0)


def get_sidereal_longitude_at(
    jd: float, planet_id: int, ayanamsa: str = "lahiri",
) -> float:
    """Get sidereal longitude for any planet at a given Julian Day."""
    if not _SWE_AVAILABLE:
        raise ImportError("pyswisseph not installed")
    _init_swe(ayanamsa)
    ayanamsa_value = swe.get_ayanamsa(jd)
    result, _ = swe.calc_ut(jd, planet_id)
    return (result[0] - ayanamsa_value) % 360.0


def jd_to_datetime(jd: float) -> datetime:
    """Convert Julian Day → naive datetime (UTC)."""
    if not _SWE_AVAILABLE:
        raise ImportError("pyswisseph not installed")
    tup = swe.revjul(jd)
    h = tup[3]
    return datetime(int(tup[0]), int(tup[1]), int(tup[2]),
                    int(h), int((h % 1) * 60), int(((h * 60) % 1) * 60))


def datetime_to_jd_utc(dt: datetime) -> float:
    """Convert a UTC datetime to Julian Day."""
    if not _SWE_AVAILABLE:
        raise ImportError("pyswisseph not installed")
    _init_swe()
    return swe.julday(dt.year, dt.month, dt.day,
                      dt.hour + dt.minute / 60.0 + dt.second / 3600.0)


# ─── Precise Mesha Sankranti (for Abda Bala) ─────────────────────────────────

def compute_mesha_sankranti_jd(year: int, ayanamsa: str = "lahiri") -> float:
    """
    Exact JD when Sun enters sidereal Aries (0° sid) in given year.
    Used for Abda Bala year-lord. Replaces hardcoded April 14 with
    Newton-Raphson search — can differ by ±1 day, changing the weekday lord.
    """
    if not _SWE_AVAILABLE:
        raise ImportError("pyswisseph not installed")
    _init_swe(ayanamsa)
    jd = swe.julday(year, 4, 13, 12.0)
    for _ in range(50):
        result, _ = swe.calc_ut(jd, swe.SUN)
        sid_lon = (result[0] - swe.get_ayanamsa(jd)) % 360.0
        diff = sid_lon
        if diff > 180.0:
            diff -= 360.0
        if abs(diff) < 0.0001:
            break
        speed = result[3]
        if abs(speed) > 0.01:
            jd -= diff / speed
        else:
            jd += 0.5
    return jd


# ─── Self-test ────────────────────────────────────────────────────────────────

def self_test():
    """Quick self-test: compute positions for the sample chart and print."""
    if not _SWE_AVAILABLE:
        print("[swisseph_bridge] pyswisseph not installed — cannot run self-test.")
        return

    # Sample chart from loader.py
    birth_dt = datetime(1994, 2, 27, 6, 30, 0)
    lat, lon = 20.5937, 78.9629

    print("═══ Swiss Ephemeris Bridge — Self-Test ═══")
    print(f"Birth: {birth_dt} IST, {lat}°N {lon}°E\n")

    # Ayanamsa
    ayan = get_ayanamsa(birth_dt, tz_offset=5.5)
    print(f"Lahiri Ayanamsa: {ayan:.4f}°\n")

    # Positions
    positions = compute_natal_positions(birth_dt, lat, lon, tz_offset=5.5)
    print("Planet Positions (Sidereal / Lahiri):")
    print(f"  {'Planet':9s}  {'Longitude':>10s}  {'Sign':12s}  {'Deg':>6s}  {'Nakshatra':16s}  {'Pada':>4s}  {'Speed':>8s}  {'R':>3s}  {'C':>3s}")
    for pname in PLANET_ORDER:
        p = positions.get(pname)
        if not p:
            continue
        retro = "R" if p["is_retrograde"] else ""
        comb  = "C" if p.get("is_combust") else ""
        print(f"  {pname:9s}  {p['longitude']:10.4f}°  {p['sign_name']:12s}  {p['degree_in_sign']:6.2f}°  {p['nakshatra_name']:16s}  {p['pada']:>4d}  {p['speed']:>8.4f}  {retro:>3s}  {comb:>3s}")

    # House cusps (Placidus)
    print("\nHouse Cusps (Placidus):")
    houses = compute_house_cusps(birth_dt, lat, lon, tz_offset=5.5)
    print(f"  Ascendant: {houses['ascendant']:.4f}° ({houses['lagna_sign_name']})")
    print(f"  MC: {houses['mc']:.4f}°")
    for i, cusp in enumerate(houses["cusps"]):
        sign = SIGN_NAMES[int(cusp / 30.0) % 12]
        print(f"  House {i+1:2d}: {cusp:8.4f}° ({sign})")

    # Full chart build
    print("\n═══ Full Chart Builder Test ═══")
    chart = build_chart_from_birth_data(
        name="Test Subject", date_str="1994-02-27", time_str="06:30:00",
        place="India", latitude=lat, longitude=lon, tz_offset=5.5,
    )
    print(f"  Lagna: {chart['lagna']['sign']} ({chart['lagna']['degree']:.4f}°)")
    print(f"  Planets: {len(chart['planets'])} computed")
    print(f"  Houses: {len(chart['houses'])} computed")
    print(f"  Ayanamsa: {chart['_swe_metadata']['ayanamsa_value']:.4f}°")
    print(f"  Engine: {chart['_swe_metadata']['engine']}")
    print("\n✓ Self-test complete.")


if __name__ == "__main__":
    self_test()
