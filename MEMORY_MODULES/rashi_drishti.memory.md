# Module: rashi_drishti.py
## Last Updated: 2026-03-02

## PURPOSE
Implements the Jaimini Rashi Drishti (sign aspect) system, distinct from the Parashari Graha Drishti. All movable signs aspect fixed signs (except adjacent); all fixed signs aspect movable signs (except adjacent); dual signs aspect each other. Used in Jaimini dasha and yoga analysis.

## KEY FUNCTIONS

### rashi_drishti_summary(planet_signs, lagna_sign) → dict
- **Purpose:** Compute which signs aspect each of the 12 signs + Lagna
- **Inputs:** planet signs dict, lagna sign
- **Returns:** dict sign → `{aspected_by_signs, aspecting_signs, planets_receiving_drishti}`
- **Called by:** `engine.py:analyze_static()`

## IMPORTANT CONSTANTS
Aspect rules: Movable→Fixed (not adjacent), Fixed→Movable (not adjacent), Dual→Dual

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: Created as standalone module
