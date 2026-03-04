# Module: divisional.py
## Last Updated: 2026-03-02

## PURPOSE
Computes all divisional (Varga) charts from a planet's natal longitude. Each D-n chart divides each sign into n equal sections and maps the planet to a resulting sign. Implements D1 through D60 with BPHS-verified formulas. Contains a critical implementation note: D9 Earth signs start from Capricorn (not Cancer — a common bug).

## KEY FUNCTIONS

### compute_all_vargas(planet_longitudes) → Dict[str, Dict[str, int]]
- **Purpose:** Compute all standard divisional charts for all planets
- **Inputs:** `planet_longitudes` dict planet → longitude
- **Returns:** dict varga_name → dict planet → sign_index
- **Called by:** `engine.py:analyze_static()`
- **Calls:** `D9()`, `D10()`, `D7()`, `D4()`, `_generic_division()`

### D9(longitude) → int
- **Purpose:** Navamsha sign — element-based start rule (CRITICAL: Earth→Capricorn)
- **Inputs:** absolute sidereal longitude
- **Returns:** sign index 0–11
- **Called by:** `compute_all_vargas()`, `engine.py`, `vimshopak.py`

### D10(longitude) → int
- **Purpose:** Dashamsha (career) — 9th sign start for even signs
- **Called by:** `compute_all_vargas()`

### D7(longitude) → int
- **Purpose:** Saptamsha (children)
- **Called by:** `compute_all_vargas()`

### D4(longitude) → int
- **Purpose:** Chaturthamsha (property/fortune)
- **Called by:** `compute_all_vargas()`

### _generic_division(lon, n, start_rule) → int
- **Purpose:** Generic D-n calculator with configurable start rule
- **Inputs:** longitude, division number, "same"/"9th"/"navamsa" start rule

## IMPORTANT CONSTANTS
- `_navamsa_start(sign_idx)` — internal: Fire→0, Earth→9, Air→6, Water→3
- **BUG WARNING**: Earth signs D9 start from Capricorn (9), NOT Cancer — common implementation error

## DEPENDENCIES
coordinates.py, config.py (Sign, SIGN_ELEMENTS, Element)

## RECENT CHANGES
- 2026-03-02: Verified navamsa start rule against BPHS (Earth=Capricorn confirmed)
