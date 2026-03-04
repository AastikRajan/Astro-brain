# Module: chara_dasha.py
## Last Updated: 2026-03-02

## PURPOSE
Implements Jaimini's Chara Dasha system — a sign-based dasha cycle where each of the 12 Rashis gets a period determined by counting houses from the sign to its lord. Uses Rashi Drishti (sign aspects) for karaka analysis. Wired into the main engine as a secondary timing system alongside Vimshottari.

## KEY FUNCTIONS

### compute_chara_dasha(planet_lons, lagna_sign, birth_date, shadbala) → List[dict]
- **Purpose:** Full Chara Dasha period tree from birth
- **Inputs:** planet longitudes, lagna sign, birth date
- **Returns:** List of sign-based periods with sub-periods
- **Called by:** `engine.py:analyze_static()`
- **Calls:** `_compute_dasha_years()`, `chara_dasha_direction()`, `_antardasha_order()`

### get_active_chara_dasha(periods, on_date) → dict
- **Purpose:** Find active Chara Dasha and Antar Dasha for a date
- **Called by:** `chara_dasha_details_on_date()`

### chara_dasha_details_on_date(planet_lons, lagna_sign, birth_date, on_date, ...) → dict
- **Purpose:** Full Chara Dasha details including Atmakaraka activation analysis
- **Called by:** `engine.py:predict()`
- **Returns:** `{main_sign, sub_sign, lord, dates, atmakaraka_active, interpretation}`

### chara_dasha_direction(lagna_sign) → str
- **Purpose:** "forward" or "backward" based on lagna sign type (movable/dual/fixed)

### _compute_dasha_years(sign, direction, planet_lons) → int
- **Purpose:** Compute dasha years for a sign (houses from sign to its lord)
- **Key logic:** Count in direction of dasha; exalted lord → +1; debilitated → -1; adjust for Rahu/Ketu

## DEPENDENCIES
config.py, coordinates.py

## RECENT CHANGES
- 2026-03-02: Added full implementation and chara_dasha_details_on_date() wired into engine
