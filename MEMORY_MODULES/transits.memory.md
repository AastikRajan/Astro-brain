# Module: transits.py
## Last Updated: 2026-03-02

## PURPOSE
Real-time planetary transit position engine and Gochar (transit) evaluator. Fetches live sidereal positions using a 4-tier ephemeris cascade (pyswisseph → skyfield → astropy → approximate). Evaluates each planet's transit quality using Gochar rules, Ashtakvarga bindus, Vedha obstruction, Kakshya, and manifestation zone factors.

## KEY FUNCTIONS

### get_transit_positions(on_date) → Dict[str, float]
- **Purpose:** Get sidereal longitudes for all 9 planets on a given date
- **Inputs:** `on_date` datetime
- **Returns:** dict planet_name → sidereal longitude (0–360°)
- **Called by:** `engine.py:predict()`
- **Calls:** `_get_positions_swisseph()`, `_get_positions_skyfield()`, `_get_positions_astropy()`, `_get_positions_approximate()`
- **Key logic:** Cascades through ephemeris tiers; approximate fallback uses mean speeds from APPROX_POSITIONS_FEB2026

### evaluate_transit(planet, transit_lon, natal_moon_lon, natal_positions, bhinna_ashtakvarga, ...) → dict
- **Purpose:** Full transit evaluation for one planet on one date
- **Inputs:** planet name, transit longitude, natal moon longitude, natal positions dict, BAV data
- **Returns:** `{house_from_moon, gochar_score, av_bindus, vedha_reduced, kakshya_lord, manifestation_mult, net_score}`
- **Called by:** `evaluate_all_transits()`
- **Calls:** `_vedha_reduction_factor()`, `_manifestation_multiplier()`, `_kakshya_info()`
- **Key logic:**
  - Computes house from natal Moon for Gochar
  - Looks up gochar score from GOCHAR_EFFECTS
  - Checks Vedha obstruction and applies VEDHA_REDUCTION factor
  - Scores Kakshya lord match bonus
  - Applies manifestation zone multiplier for 0–3.3° and 26.7–30° zones

### evaluate_all_transits(transit_positions, natal_data, av_data) → Dict[str, dict]
- **Purpose:** Run evaluate_transit for all 9 planets
- **Inputs:** transit positions dict, natal data dict, ashtakvarga data
- **Returns:** dict planet → evaluation result
- **Called by:** `engine.py:predict()`

### detect_sade_sati(transit_saturn_lon, natal_moon_sign) → dict
- **Purpose:** Detect Sade Sati (7.5-yr Saturn transit affecting Moon) phase
- **Inputs:** Saturn's current longitude, natal Moon sign
- **Returns:** `{is_sade_sati, phase, paya, intensity}`
- **Called by:** `engine.py:predict()`
- **Calls:** `_compute_paya()`

## IMPORTANT CONSTANTS
- `MEAN_SPEEDS` — mean sidereal speeds deg/day per planet
- `APPROX_POSITIONS_FEB2026` — reference positions for approximate fallback
- `REFERENCE_DATE = datetime(2026, 2, 27)` — fallback reference epoch

## DEPENDENCIES
config.py (TRANSIT_FAVORABLE, VEDHA_TABLE, GOCHAR_EFFECTS, COMBUSTION_DEGREES, etc.), coordinates.py, special_points.py

## RECENT CHANGES
- 2026-03-02: Added 4-tier ephemeris cascade with Skyfield and Astropy tiers
- 2026-03-02: Added manifestation zone multiplier for degree-precise scoring
- 2026-03-02: Added Kakshya lord bonus scoring
