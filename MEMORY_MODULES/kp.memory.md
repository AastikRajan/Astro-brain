# Module: kp.py
## Last Updated: 2026-03-02

## PURPOSE
Implements the Krishnamurti Paddhati (KP) system — a sub-lord based prediction method that divides each nakshatra into unequal sub-divisions (proportional to Vimshottari years). The KP sub-lord confirms or denies a house event with binary precision. Also implements cuspal significations, ruling planets, and Prashna (horary) queries.

## KEY FUNCTIONS

### get_kp_layers(longitude) → Dict[str, str]
- **Purpose:** Get the 4-layer KP hierarchy for any longitude
- **Inputs:** absolute sidereal longitude (0–360°)
- **Returns:** `{rashi_lord, nak_lord, sub_lord, sub_sub_lord}`
- **Called by:** `engine.py:analyze_static()` for each planet, `build_kp_significations()`

### build_kp_significations(planet_lons, planet_houses, ...) → dict
- **Purpose:** Build full signification table: each planet→list of signified houses
- **Inputs:** planet longitudes, houses, house lords
- **Returns:** dict planet → list of signified house numbers
- **Called by:** `engine.py:analyze_static()`

### build_cusp_significations(cusp_lons, planet_houses, ...) → dict
- **Purpose:** Signification table keyed by house cusp
- **Called by:** `engine.py:analyze_static()`

### compute_ruling_planets(ascendant_lon, moon_lon, ...) → dict
- **Purpose:** KP Ruling Planets at a moment in time
- **Called by:** `engine.py:predict()`

### resolve_prashna_query(query_house, ruling_planets, kp_table, ...) → dict
- **Purpose:** Yes/No Prashna resolution based on sub-lord and ruling planets
- **Called by:** `main.py` (prashna mode)

### analyze_ithasala_yoga(planet_a, planet_b, lons, speeds) → dict
- **Purpose:** KP Ithasala (applying aspect) yoga detection for Tajika

## IMPORTANT CONSTANTS
- Sub-lord span calculation uses `VIMSHOTTARI_YEARS` proportions from config.py
- `KAKSHYA_LORDS`, `KAKSHYA_SPAN` from config.py

## DEPENDENCIES
config.py (Planet, VIMSHOTTARI_SEQUENCE, VIMSHOTTARI_YEARS, KAKSHYA_LORDS, KAKSHYA_SPAN)

## RECENT CHANGES
- 2026-03-02: Added compute_prashna_panchaka() for Prashna mode
- 2026-03-02: Added analyze_missing_person_prashna()
