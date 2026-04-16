# Module: swisseph_bridge.py
## Last Updated: 2026-04-14

## PURPOSE
Wraps the pyswisseph library to compute precise sidereal planetary positions using the Swiss Ephemeris (SE). This is the highest-accuracy position source in the engine. Returns heliocentric-corrected sidereal longitudes with optional speed data. Falls back gracefully if pyswisseph not installed.

## KEY FUNCTIONS

### compute_positions_swe(birth_dt, lat, lon, ayanamsa_model) → dict
- **Purpose:** Compute all 9 planet positions + Lagna via Swiss Ephemeris
- **Inputs:** birth datetime (UTC), lat/lon, ayanamsa model string
- **Returns:** dict planet → `{longitude, speed, is_retrograde}` + `{lagna, house_cusps}`
- **Called by:** `loader.py:build_chart_swe()`, `transits.py:_get_positions_swisseph()`

### compute_solar_return(birth_dt, year, latitude, longitude, tz_offset, ayanamsa) → dict
- **Purpose:** Compute the active Varshaphala solar return chart for a target year
- **Returns:** UTC/local return timestamps plus a loader-compatible SWE chart payload
- **Called by:** `prediction/engine.py:_build_dynamic_annual_context()`
- **Key logic:** Solves against the natal sidereal Sun longitude using the ayanamsa valid at the candidate return moment

## DEPENDENCIES
pyswisseph (optional C extension)

## RECENT CHANGES
- 2026-04-14: `compute_solar_return()` now solves the return against sidereal Sun longitude and is used by engine dynamic annual wiring
- 2026-03-02: Created as dedicated bridge module
