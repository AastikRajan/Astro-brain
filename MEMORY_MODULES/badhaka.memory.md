# Module: badhaka.py
## Last Updated: 2026-03-02

## PURPOSE
Computes the Badhaka (obstructing) planet and sign for a native's Lagna. The Badhaka sign is the 11th from movable lagnas, 9th from fixed lagnas, and 7th from dual lagnas. The lord of this sign becomes the Badhaka planet — can cause unexplained delays when transiting or in dasha.

## KEY FUNCTIONS

### compute_badhaka(lagna_sign, planet_signs, planet_houses) → dict
- **Purpose:** Identify Badhaka sign and planet, assess strength
- **Inputs:** lagna sign index, planet placement dicts
- **Returns:** `{badhaka_sign, badhaka_lord, lord_house, lord_strength, impact_assessment}`
- **Called by:** `engine.py:analyze_static()`

## IMPORTANT CONSTANTS
Badhaka sign offset: Movable Lagna → 11th sign; Fixed Lagna → 9th sign; Dual Lagna → 7th sign

## DEPENDENCIES
config.py, coordinates.py

## RECENT CHANGES
- 2026-03-02: Created as standalone module
