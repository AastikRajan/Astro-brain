"""
Sunrise / Sunset Utilities — Tiered astronomical computation.

Tier-1: Swiss Ephemeris ``swe.rise_trans()`` — accurate to < 1 second.
Tier-2: NOAA Solar Position Algorithm (Spencer/Meeus) — ±2 minute fallback.

Purpose
-------
Provides ``calc_sunrise_sunset()``, ``is_daytime()`` and ``get_paksha()`` for
the prediction engine.  Sunrise/sunset precision is critical because it drives
Gulika/Mandi, Hora Bala, Tribhaga Bala, and the day/night birth classification.
"""
from __future__ import annotations
import math
from datetime import datetime, timedelta, date as date_type
from typing import Optional, Tuple

# ─── Swiss Ephemeris tier-1 ───────────────────────────────────────────────────

_SWE_RISE_AVAILABLE = False
try:
    from vedic_engine.core.swisseph_bridge import compute_sunrise_sunset_swe
    _SWE_RISE_AVAILABLE = True
except ImportError:
    pass


# ─── Core NOAA algorithm ─────────────────────────────────────────────────────

def _julian_day(year: int, month: int, day: int) -> float:
    """Compute Julian Day Number for noon UTC on given date."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return float(jdn) - 0.5  # midnight UTC


def _solar_declination_and_eot(jd: float) -> Tuple[float, float]:
    """
    Compute solar declination (radians) and equation of time (minutes).

    Algorithm: Spencer (1971) as refined by NOAA.
    Returns (declination_radians, eot_minutes).
    """
    n = jd - 2451545.0          # days from J2000.0
    L = (280.460 + 0.9856474 * n) % 360.0          # mean longitude (deg)
    g = math.radians((357.528 + 0.9856003 * n) % 360.0)  # mean anomaly (rad)

    # Apparent ecliptic longitude
    lam = math.radians(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))

    # Obliquity of ecliptic
    eps = math.radians(23.439 - 0.0000004 * n)

    # Declination
    sin_dec = math.sin(eps) * math.sin(lam)
    dec = math.asin(sin_dec)

    # Right ascension
    ra = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))

    # Equation of Time (degrees → converted to minutes)
    eot_deg = math.degrees(math.radians(L) - 0.0057183 - ra)
    # Normalize to ±180
    eot_deg = ((eot_deg + 180) % 360) - 180
    eot_min = eot_deg * 4.0  # 1 degree = 4 minutes of time

    return dec, eot_min


def calc_sunrise_sunset(
    latitude: float,
    longitude: float,
    target_date: date_type,
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Return (sunrise_utc, sunset_utc) as naive datetime objects (UTC).

    Returns
    -------
    (sunrise_utc, sunset_utc) — naive datetimes at the given date (UTC)
    (None, None)              — polar night (sun never rises)
    Both are approximate: accurate to ±2 minutes for latitudes < 72°.

    Parameters
    ----------
    latitude    : decimal degrees, positive = North
    longitude   : decimal degrees, positive = East
    target_date : date object for the day of interest
    """
    year, month, day = target_date.year, target_date.month, target_date.day
    jd = _julian_day(year, month, day)

    dec, eot_min = _solar_declination_and_eot(jd)

    # Solar noon in UTC hours
    solar_noon_utc = 12.0 - longitude / 15.0 - eot_min / 60.0

    # Hour angle at sunrise: cos(HA) = (sin(-0.833°) - sin(lat)·sin(dec)) / (cos(lat)·cos(dec))
    # -0.833° accounts for refraction + solar disc radius
    lat_rad = math.radians(latitude)
    numerator = math.sin(math.radians(-0.8333)) - math.sin(lat_rad) * math.sin(dec)
    denominator = math.cos(lat_rad) * math.cos(dec)

    if abs(denominator) < 1e-10:
        # At exact pole
        return None, None

    cos_ha = numerator / denominator

    if cos_ha > 1.0:
        return None, None   # Polar night — sun never rises

    if cos_ha < -1.0:
        # Polar day — sun never sets; return midnight-to-midnight
        d_start = datetime(year, month, day, 0, 0, 0)
        d_end   = datetime(year, month, day, 23, 59, 59)
        return d_start, d_end

    ha_deg = math.degrees(math.acos(cos_ha))  # hours-of-arc

    sunrise_utc_h = solar_noon_utc - ha_deg / 15.0
    sunset_utc_h  = solar_noon_utc + ha_deg / 15.0

    def _h_to_dt(h: float) -> datetime:
        total_sec = int(round(h * 3600))
        return datetime(year, month, day, 0, 0, 0) + timedelta(seconds=total_sec)

    return _h_to_dt(sunrise_utc_h), _h_to_dt(sunset_utc_h)


# ─── Engine helpers ───────────────────────────────────────────────────────────

def compute_is_daytime(
    latitude: float,
    longitude: float,
    birth_dt_local: datetime,
    tz_offset_hours: float,
) -> bool:
    """
    Return True if birth was during daytime (between sunrise and sunset).

    Parameters
    ----------
    latitude          : decimal degrees
    longitude         : decimal degrees
    birth_dt_local    : naive datetime in local standard/DST time
    tz_offset_hours   : UTC offset in decimal hours (e.g. 5.5 for IST)

    Algorithm
    ---------
    1. Convert birth_dt_local → UTC
    2. Compute sunrise/sunset UTC for that date at the location
    3. Compare UTC birth time with sunrise/sunset window
    """
    try:
        birth_dt_utc = birth_dt_local - timedelta(hours=tz_offset_hours)

        sunrise_utc, sunset_utc = calc_sunrise_sunset(
            latitude, longitude, birth_dt_utc.date()
        )

        if sunrise_utc is None:
            # Polar night — treat as nighttime
            return False

        return sunrise_utc <= birth_dt_utc <= sunset_utc

    except Exception:
        return True   # safe default (matches the old hardcoded value)


def compute_paksha(sun_lon: float, moon_lon: float) -> str:
    """
    Return 'shukla' or 'krishna' based on Tithi number from Sun/Moon longitudes.

    Shukla Paksha : Tithi 1-15 (Moon ahead of Sun, diff 0°–180°)
    Krishna Paksha: Tithi 16-30 (Moon 180°–360° ahead of Sun)
    """
    diff = (moon_lon - sun_lon) % 360.0
    return "shukla" if diff < 180.0 else "krishna"


# ─── High-level API: decimal-hour sunrise/sunset ─────────────────────────────

def get_sunrise_sunset_hours(
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    tz_offset: float = 5.5,
) -> Tuple[float, float]:
    """
    Return (sunrise_hour_local, sunset_hour_local) as decimal hours in local time.

    Tier-1 : Swiss Ephemeris ``swe.rise_trans()`` — sub-second accuracy.
    Tier-2 : NOAA pure-Python algorithm — ±2 minute accuracy.
    Tier-3 : Fallback default 6.0, 18.0 if both fail.

    This is the SINGLE entry-point that Shadbala, Gulika, Hora Lagna, etc.
    should call to get precise sunrise/sunset hours.
    """
    # Tier-1 : Swiss Ephemeris
    if _SWE_RISE_AVAILABLE:
        try:
            swe_data = compute_sunrise_sunset_swe(
                birth_dt, latitude, longitude, tz_offset
            )
            return swe_data["sunrise_hour_local"], swe_data["sunset_hour_local"]
        except Exception:
            pass  # fall through to NOAA

    # Tier-2 : NOAA pure-Python
    try:
        birth_utc = birth_dt - timedelta(hours=tz_offset)
        sunrise_utc, sunset_utc = calc_sunrise_sunset(
            latitude, longitude, birth_utc.date()
        )
        if sunrise_utc is not None and sunset_utc is not None:
            sr_local = sunrise_utc + timedelta(hours=tz_offset)
            ss_local = sunset_utc + timedelta(hours=tz_offset)
            sr_h = sr_local.hour + sr_local.minute / 60.0 + sr_local.second / 3600.0
            ss_h = ss_local.hour + ss_local.minute / 60.0 + ss_local.second / 3600.0
            return sr_h, ss_h
    except Exception:
        pass

    # Tier-3 : Safe defaults
    return 6.0, 18.0
