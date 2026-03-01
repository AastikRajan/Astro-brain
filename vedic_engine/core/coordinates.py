"""
Core coordinate math: sign, nakshatra, pada, varga decomposition.
Every formula here is derived from the deep-research-report.md.
All inputs/outputs in decimal degrees unless noted.
"""
from __future__ import annotations
from typing import Dict, Tuple

from vedic_engine.config import (
    Sign, Element, SignQuality, SIGN_ELEMENTS, SIGN_QUALITIES,
    NAKSHATRA_SPAN, PADA_SPAN, NAKSHATRA_NAMES, VIMSHOTTARI_SEQUENCE,
    SIGN_LORDS
)

SIGN_NAMES = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
              "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]


def normalize(lon: float) -> float:
    """Force 0 ≤ lon < 360."""
    return lon % 360.0


def sign_of(lon: float) -> int:
    """Return 0-11 sign index for absolute sidereal longitude."""
    return int(normalize(lon) / 30) % 12


def degree_in_sign(lon: float) -> float:
    """Return 0-30 degree position within sign."""
    return normalize(lon) % 30.0


def nakshatra_of(lon: float) -> int:
    """Return 0-26 nakshatra index."""
    return min(int(normalize(lon) / NAKSHATRA_SPAN), 26)


def pada_of(lon: float) -> int:
    """Return 1-4 pada within nakshatra."""
    pos_in_nak = normalize(lon) % NAKSHATRA_SPAN
    return int(pos_in_nak / PADA_SPAN) + 1


def nakshatra_lord_of(lon: float):
    """Return Planet enum for the nakshatra lord."""
    return VIMSHOTTARI_SEQUENCE[nakshatra_of(lon) % 9]


def angular_distance(lon_a: float, lon_b: float) -> float:
    """
    Shortest angular distance between two longitudes.
    Returns value in [0, 180].
    """
    diff = abs(normalize(lon_a) - normalize(lon_b))
    if diff > 180.0:
        diff = 360.0 - diff
    return diff


def signed_distance(from_lon: float, to_lon: float) -> float:
    """
    Directional arc: to_lon - from_lon, normalised to (-180, 180].
    Positive = to_lon is ahead (counter-clockwise / zodiac forward).
    """
    d = normalize(to_lon) - normalize(from_lon)
    if d > 180:
        d -= 360
    elif d <= -180:
        d += 360
    return d


def house_from(planet_sign: int, lagna_sign: int) -> int:
    """Return 1-indexed house number of planet from lagna."""
    return (planet_sign - lagna_sign) % 12 + 1


def house_from_moon(planet_sign: int, moon_sign: int) -> int:
    """Return 1-indexed house number of planet counted from Moon sign."""
    return (planet_sign - moon_sign) % 12 + 1


def sign_name(idx: int) -> str:
    return SIGN_NAMES[idx % 12]


def full_position_info(lon: float) -> dict:
    """
    Given an absolute sidereal longitude, return a complete breakdown dict.
    This is the 'single number maps to all overlays' principle.
    """
    lon = normalize(lon)
    s = sign_of(lon)
    n = nakshatra_of(lon)
    p = pada_of(lon)
    nak_lord = VIMSHOTTARI_SEQUENCE[n % 9]
    pos_in_nak = lon % NAKSHATRA_SPAN
    pos_in_pada = lon % PADA_SPAN

    return {
        "longitude": lon,
        "sign_index": s,
        "sign_name": SIGN_NAMES[s],
        "sign_lord": SIGN_LORDS[Sign(s)].name,
        "degree_in_sign": lon % 30,
        "nakshatra_index": n,
        "nakshatra_name": NAKSHATRA_NAMES[n],
        "nakshatra_lord": nak_lord.name,
        "pos_in_nakshatra": pos_in_nak,
        "pada": p,
        "pos_in_pada": pos_in_pada,
        "element": SIGN_ELEMENTS[Sign(s)].value,
        "quality": SIGN_QUALITIES[Sign(s)].value,
        "decanate": int((lon % 30) / 10) + 1,  # 1, 2, or 3
    }


# ─── Topocentric Lunar Parallax Correction ───────────────────────────────────
# Classical Jyotish requires TOPOCENTRIC positions, not geocentric.
# The Moon can shift by up to 1° due to observer latitude/longitude,
# altering the Vimshottari Dasha balance, KP Sub-Lord, and Navamsha (D9/D60).
#
# TIER-1: Swiss Ephemeris FLG_TOPOCTR (sub-arcsecond, actual Moon distance)
#         → via swisseph_bridge.compute_topocentric_moon_swe()
# TIER-2: Manual IAU simplified horizontal parallax method (this code)
#         → uses actual Moon distance if available, else mean 384400 km.

import math as _math

EARTH_RADIUS_KM = 6378.137            # WGS-84 equatorial radius
MOON_MEAN_DISTANCE_KM = 384400.0     # mean centre-to-centre distance

# ─── SWE-powered topocentric Moon (tier-1) ───────────────────────────────────

_SWE_TOPO_AVAILABLE = False
try:
    from vedic_engine.core.swisseph_bridge import compute_topocentric_moon_swe
    _SWE_TOPO_AVAILABLE = True
except ImportError:
    pass


def get_topocentric_moon(
    moon_lon_geo: float,
    moon_lat_geo: float,
    observer_lat_deg: float,
    observer_lon_deg: float,
    local_sidereal_time_deg: float,
    moon_distance_km: float = MOON_MEAN_DISTANCE_KM,
    birth_dt=None,
    tz_offset: float = 5.5,
) -> Dict:
    """
    High-level topocentric Moon API with tiered backend.

    Tier-1: Swiss Ephemeris FLG_TOPOCTR (if birth_dt provided and SWE available).
    Tier-2: Manual IAU parallax correction (this module).

    Returns the same dict format as apply_topocentric_moon().
    """
    # Tier-1: Swiss Ephemeris
    if _SWE_TOPO_AVAILABLE and birth_dt is not None:
        try:
            swe_result = compute_topocentric_moon_swe(
                birth_dt, observer_lat_deg, observer_lon_deg,
                tz_offset=tz_offset,
            )
            # Convert to same format as apply_topocentric_moon
            delta = swe_result["delta_lon"]
            topo_lon = swe_result["lon_topocentric"]
            nak_span = 360.0 / 27.0
            nak_pre = int(normalize(moon_lon_geo) / nak_span)
            nak_post = int(topo_lon / nak_span)
            sign_pre = int(normalize(moon_lon_geo) / 30)
            sign_post = int(topo_lon / 30)
            kp_div_size = 360.0 / 249.0
            kp_risk = (kp_div_size - (topo_lon % kp_div_size) < 0.30
                       or (topo_lon % kp_div_size) < 0.30)
            advisories = []
            if abs(delta) >= 0.5:
                advisories.append(f"SIGNIFICANT parallax ({delta:+.3f}°) — verify Moon Nakshatra")
            if nak_pre != nak_post:
                advisories.append("Topocentric correction CROSSES nakshatra boundary — Vimshottari balance changes")
            if sign_pre != sign_post:
                advisories.append("Topocentric correction CROSSES sign boundary — Moon Rashi changes")
            if kp_risk:
                advisories.append("Moon near KP sub-lord boundary — Sub-Lord assignment may flip")
            return {
                "lon_geo": round(moon_lon_geo, 6),
                "lat_geo": round(moon_lat_geo, 6),
                "delta_lon": round(delta, 6),
                "delta_lat": 0.0,
                "lon_topo": round(topo_lon, 6),
                "lat_topo": round(swe_result.get("lat_topocentric", moon_lat_geo), 6),
                "HP_arcmin": round(_math.degrees(_math.asin(EARTH_RADIUS_KM / swe_result.get("distance_km", MOON_MEAN_DISTANCE_KM))) * 60, 3),
                "nakshatra_shift": nak_pre != nak_post,
                "sign_shift": sign_pre != sign_post,
                "kp_sublord_risk": kp_risk,
                "advisory": " | ".join(advisories) if advisories else "Within normal range — no boundary crossing",
                "source": "swisseph_FLG_TOPOCTR",
                "distance_km": swe_result.get("distance_km", MOON_MEAN_DISTANCE_KM),
            }
        except Exception:
            pass  # fall through to tier-2

    # Tier-2: Manual IAU correction
    return apply_topocentric_moon(
        moon_lon_geo, moon_lat_geo,
        observer_lat_deg, observer_lon_deg,
        local_sidereal_time_deg, moon_distance_km,
    )


def topocentric_moon_correction(
    moon_lon_geo: float,
    moon_lat_geo: float,
    observer_lat_deg: float,
    observer_lon_deg: float,
    local_sidereal_time_deg: float,
    moon_distance_km: float = MOON_MEAN_DISTANCE_KM,
) -> Tuple[float, float]:
    """
    Compute topocentric correction for the Moon's ecliptic longitude and latitude.

    Because the observer is on the Earth's surface (not its centre), the Moon
    appears shifted toward the horizon.  This correction is the "equatorial
    horizontal parallax" effect and can alter Moon longitude by up to ±1°.

    Parameters
    ----------
    moon_lon_geo        : geocentric ecliptic longitude (decimal degrees)
    moon_lat_geo        : geocentric ecliptic latitude  (decimal degrees)
    observer_lat_deg    : geographic latitude of birthplace (+ = North)
    observer_lon_deg    : geographic longitude of birthplace (+ = East)
    local_sidereal_time_deg : Local Apparent Sidereal Time in degrees (0-360)
    moon_distance_km    : Earth-Moon centre-to-centre distance (km).
                          Use mean value 384400 if not known precisely.

    Returns
    -------
    (delta_lon, delta_lat) : topocentric corrections in decimal degrees.
        Apply: moon_lon_topo = moon_lon_geo + delta_lon
               moon_lat_topo = moon_lat_geo + delta_lat

    Algorithm
    ---------
    Horizontal parallax:  HP = arcsin(Re / Dmoon)
    Hour angle:           H = LST - moon_RA  (approximated via ecliptic longitude)
    Δlon ≈ -HP × sin(H) × cos(φ) / cos(β_moon)
    Δlat ≈ -HP × (sin(φ) - sin(δ_moon) × cos(H) × cos(φ)) × sin(β_moon)  [minor]

    For Vedic purposes the latitude correction Δlat is second-order (Moon's
    ecliptic latitude β_moon is typically < 5°) and is included for completeness.
    """
    rad = _math.radians

    # 1. Horizontal parallax (radians)
    HP_rad = _math.asin(EARTH_RADIUS_KM / moon_distance_km)
    HP_deg = _math.degrees(HP_rad)   # ≈ 0.9507° at mean distance

    # 2. Approximate Moon Right Ascension from ecliptic lon (obliquity ≈ 23.44°)
    #    This is a geocentric approximation; good to within 1° for parallax purposes.
    epsilon = 23.4397   # mean obliquity (degrees)
    lam = rad(moon_lon_geo)
    bet = rad(moon_lat_geo)
    eps = rad(epsilon)
    # Ecliptic → equatorial conversion for RA (hour angle is what matters)
    ra_moon_deg = _math.degrees(
        _math.atan2(
            _math.sin(lam) * _math.cos(eps) - _math.tan(bet) * _math.sin(eps),
            _math.cos(lam)
        )
    ) % 360.0

    # 3. Local Hour Angle of Moon (degrees; positive = Moon west of meridian)
    H_deg = (local_sidereal_time_deg - ra_moon_deg) % 360.0
    H_rad = rad(H_deg)

    # 4. Observer latitude
    phi_rad = rad(observer_lat_deg)

    # 5. Longitude correction (dominant term)
    cos_lat_moon = _math.cos(bet)
    if abs(cos_lat_moon) < 1e-9:
        cos_lat_moon = 1e-9   # safety against pole singularity
    delta_lon = -HP_deg * _math.sin(H_rad) * _math.cos(phi_rad) / cos_lat_moon

    # 6. Latitude correction (secondary term — included for fidelity)
    dec_moon = _math.degrees(
        _math.asin(
            _math.sin(bet) * _math.cos(eps)
            + _math.cos(bet) * _math.sin(eps) * _math.sin(lam)
        )
    )
    dec_rad = rad(dec_moon)
    delta_lat = -HP_deg * (
        _math.sin(phi_rad) - _math.sin(dec_rad) * _math.cos(H_rad) * _math.cos(phi_rad)
    ) * _math.sin(bet) if abs(_math.sin(bet)) > 0.001 else 0.0

    return round(delta_lon, 6), round(delta_lat, 6)


def apply_topocentric_moon(
    moon_lon_geo: float,
    moon_lat_geo: float,
    observer_lat_deg: float,
    observer_lon_deg: float,
    local_sidereal_time_deg: float,
    moon_distance_km: float = MOON_MEAN_DISTANCE_KM,
) -> Dict:
    """
    Convenience wrapper: return topocentric Moon longitude/latitude + diagnostics.

    Returns
    -------
    dict with:
        lon_geo        : original geocentric longitude
        lat_geo        : original geocentric latitude
        delta_lon      : longitude correction applied (degrees)
        delta_lat      : latitude correction applied (degrees)
        lon_topo       : corrected topocentric longitude
        lat_topo       : corrected topocentric latitude
        HP_arcmin      : horizontal parallax in arc-minutes
        nakshatra_shift: True if correction crosses a nakshatra boundary (13°20')
        sign_shift     : True if correction crosses a sign boundary (30°)
        kp_sublord_risk: True if Moon is within 0.3° of a KP sub-division
        advisory       : human-readable advisory string
    """
    HP_deg = _math.degrees(_math.asin(EARTH_RADIUS_KM / moon_distance_km))
    delta_lon, delta_lat = topocentric_moon_correction(
        moon_lon_geo, moon_lat_geo,
        observer_lat_deg, observer_lon_deg,
        local_sidereal_time_deg, moon_distance_km,
    )
    lon_topo = normalize(moon_lon_geo + delta_lon)
    lat_topo = moon_lat_geo + delta_lat

    # Check boundary sensitivity
    nak_span = 360.0 / 27.0   # ≈ 13.333°
    nak_pre  = int(normalize(moon_lon_geo) / nak_span)
    nak_post = int(lon_topo / nak_span)
    nakshatra_shift = (nak_pre != nak_post)

    sign_pre  = int(normalize(moon_lon_geo) / 30)
    sign_post = int(lon_topo / 30)
    sign_shift = (sign_pre != sign_post)

    # KP sub-lord risk: Moon within 0.3° of any 1/249th division boundary
    kp_div_size = 360.0 / 249.0   # ≈ 1.4458°
    dist_to_kp_boundary = kp_div_size - (lon_topo % kp_div_size)
    kp_sublord_risk = (dist_to_kp_boundary < 0.30) or ((lon_topo % kp_div_size) < 0.30)

    # Advisory
    advisories = []
    if abs(delta_lon) >= 0.5:
        advisories.append(f"SIGNIFICANT parallax ({delta_lon:+.3f}°) — verify Moon Nakshatra")
    if nakshatra_shift:
        advisories.append("Topocentric correction CROSSES nakshatra boundary — Vimshottari balance changes")
    if sign_shift:
        advisories.append("Topocentric correction CROSSES sign boundary — Moon Rashi changes")
    if kp_sublord_risk:
        advisories.append("Moon near KP sub-lord boundary — Sub-Lord assignment may flip")
    advisory = " | ".join(advisories) if advisories else "Within normal range — no boundary crossing"

    return {
        "lon_geo":          round(moon_lon_geo, 6),
        "lat_geo":          round(moon_lat_geo, 6),
        "delta_lon":        delta_lon,
        "delta_lat":        delta_lat,
        "lon_topo":         round(lon_topo, 6),
        "lat_topo":         round(lat_topo, 6),
        "HP_arcmin":        round(HP_deg * 60, 3),
        "nakshatra_shift":  nakshatra_shift,
        "sign_shift":       sign_shift,
        "kp_sublord_risk":  kp_sublord_risk,
        "advisory":         advisory,
    }
