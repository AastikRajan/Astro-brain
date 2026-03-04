# Module: skyfield_positions.py
## Last Updated: 2026-03-02

## PURPOSE
Provides planet position computation via the Skyfield library with JPL DE440s/DE421 ephemeris. This is the second-tier ephemeris source in the cascade, used when pyswisseph is unavailable. Pure Python — no C extension required. Downloads BSP files on first use.

## KEY FUNCTIONS

### get_positions_skyfield(on_date) → Dict[str, float]
- **Purpose:** Compute sidereal longitudes for all planets using Skyfield
- **Inputs:** datetime (UTC)
- **Returns:** dict planet → sidereal longitude
- **Called by:** `transits.py:_get_positions_skyfield()`

## DEPENDENCIES
skyfield (optional), numpy

## RECENT CHANGES
- 2026-03-02: Extracted from transits.py into dedicated module
