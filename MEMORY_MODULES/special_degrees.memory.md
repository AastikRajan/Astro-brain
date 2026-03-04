# Module: special_degrees.py
## Last Updated: 2026-03-02

## PURPOSE
Detects spiritually and karmically sensitive natal degree positions: Mrityu Bhaga (death degrees), Gandanta zones (junction of Water-Fire sign boundaries at nakshatra boundaries), and Pushkara Navamshas (auspicious degrees amplifying positive results). Wired into engine static analysis.

## KEY FUNCTIONS

### compute_special_degrees(planet_longitudes) → dict
- **Purpose:** Check all planets for sensitive degree placements
- **Returns:** dict planet → `{mrityu_bhaga: bool, gandanta: bool, pushkara: bool, notes}`
- **Called by:** `engine.py:analyze_static()`

## IMPORTANT CONSTANTS
- Mrityu Bhaga degrees: specific per planet and sign (from classical texts)
- Gandanta zones: 0°–0°48' and 29°12'–30° of Cancer/Scorpio/Pisces
- Pushkara Navamshas: specific navamsha positions per sign

## DEPENDENCIES
config.py, coordinates.py

## RECENT CHANGES
- 2026-03-02: Created as new module; wired into engine.py analyze_static()
