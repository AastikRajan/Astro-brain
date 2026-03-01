"""
Timezone Utilities — Auto-resolve correct UTC offset from geographic coordinates.

Uses timezonefinder (shapefile-based, offline) + pytz to:
  1. Determine IANA timezone name from lat/lon
  2. Apply DST-aware pytz localization
  3. Return the correct UTC offset (handles IST, EST, PST and all DST transitions)

Falls back to user-supplied float offset if either library is unavailable.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional


def resolve_timezone(
    latitude: float,
    longitude: float,
    date_str: str,
    time_str: str,
    fallback_tz: float = 5.5,
) -> float:
    """
    Return the correct UTC offset (float hours) for a birth datetime at a location.

    Parameters
    ----------
    latitude    : decimal degrees, positive = North
    longitude   : decimal degrees, positive = East
    date_str    : "YYYY-MM-DD"
    time_str    : "HH:MM:SS" or "HH:MM"
    fallback_tz : float hours — used if libraries are absent or lookup fails

    Returns
    -------
    UTC offset in decimal hours (e.g. 5.5 for IST, -5.0 for EST, 5.0 for PKT)

    Notes
    -----
    - timezonefinder uses offline polygons; no internet required.
    - pytz.localize() correctly handles DST: same geographic zone returns different
      offsets for winter vs summer dates.
    - If the location is in an unknown zone (open ocean, etc.), falls back to
      fallback_tz.
    """
    try:
        from timezonefinder import TimezoneFinder
        import pytz

        tf = TimezoneFinder()
        tz_name: Optional[str] = tf.timezone_at(lat=latitude, lng=longitude)

        if not tz_name:
            return fallback_tz

        tz = pytz.timezone(tz_name)
        # Parse birth datetime — naive (no tzinfo yet)
        try:
            birth_dt_naive = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                birth_dt_naive = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                return fallback_tz

        # Localize to IANA zone — this applies DST automatically
        birth_dt_local = tz.localize(birth_dt_naive, is_dst=None)
        offset_seconds = birth_dt_local.utcoffset().total_seconds()
        return round(offset_seconds / 3600.0, 4)

    except ImportError:
        # timezonefinder or pytz not installed — use supplied value
        return fallback_tz
    except Exception:
        return fallback_tz


def get_iana_timezone_name(latitude: float, longitude: float) -> Optional[str]:
    """Return the IANA timezone name string (e.g. 'Asia/Kolkata') or None."""
    try:
        from timezonefinder import TimezoneFinder
        tf = TimezoneFinder()
        return tf.timezone_at(lat=latitude, lng=longitude)
    except Exception:
        return None
