# Module: timezone_utils.py
## Last Updated: 2026-03-02

## PURPOSE
Handles timezone conversion and Local Mean Time (LMT) calculations. LMT is used prior to standard time zones in historical births (before ~1900). Converts between local time, LMT, and UTC as needed by the chart computation modules.

## KEY FUNCTIONS

### to_utc(local_dt, timezone_offset) → datetime
- **Purpose:** Convert local time to UTC using a fixed offset
- **Called by:** `loader.py`, `swisseph_bridge.py`

### local_to_utc(local_dt, place_name_or_tz) → datetime
- **Purpose:** Convert using timezone name string (pytz-based)
- **Called by:** `loader.py`

### lmt_to_utc(local_dt, longitude) → datetime
- **Purpose:** Convert Local Mean Time using geographic longitude (4 min/degree)

## DEPENDENCIES
pytz (optional), datetime

## RECENT CHANGES
- 2026-03-02: No changes
