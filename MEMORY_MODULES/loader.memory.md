# Module: loader.py
## Last Updated: 2026-03-02

## PURPOSE
Loads birth chart data from JSON files or dicts, and optionally builds full VedicChart objects using Swiss Ephemeris (build_chart_swe). Translates raw kundli export format (from astrology software) into the typed VedicChart model used by the engine. Handles DMS-to-decimal conversion and field validation.

## KEY FUNCTIONS

### load_sample_chart() → VedicChart
- **Purpose:** Load the built-in sample chart (from astrosage data/ JSON)
- **Called by:** `main.py:main()`
- **Returns:** VedicChart

### load_from_dict(data: dict) → VedicChart
- **Purpose:** Build VedicChart from a raw JSON-compatible dict
- **Inputs:** `data` dict with birth info + planet positions
- **Returns:** VedicChart
- **Called by:** `main.py:main()`, tests

### build_chart_swe(birth_dt, lat, lon, tz_offset, ayanamsa_model) → VedicChart
- **Purpose:** Compute full chart from scratch using Swiss Ephemeris
- **Inputs:** birth datetime, latitude, longitude, timezone offset
- **Returns:** VedicChart with precisely computed positions
- **Called by:** `main.py:main()` when --swe flag or coordinates provided
- **Calls:** `swisseph_bridge.compute_positions_swe()`

### _dms_to_deg(dms_str) → float
- **Purpose:** Convert "24°14'18\"" or "24:14:18" format to decimal degrees
- **Called by:** `load_from_dict()`

## DEPENDENCIES
models.py, config.py (Planet, Sign, SIGN_LORDS, NAKSHATRA_NAMES, etc.)

## RECENT CHANGES
- 2026-03-02: Added build_chart_swe() for real-time computation
