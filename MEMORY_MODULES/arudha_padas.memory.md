# Module: arudha_padas.py
## Last Updated: 2026-03-02

## PURPOSE
Computes Arudha Padas (maya/image signs) for all 12 houses using the Jaimini system. The Arudha Lagna (AL/A1) shows how the native is perceived by the world. A2 through A12 show the public image of each house's significations. Used in Jaimini analysis.

## KEY FUNCTIONS

### arudha_summary(planet_lons, lagna_sign, house_lords) → dict
- **Purpose:** Compute all 12 Arudha Padas and their significations
- **Inputs:** planet longitudes, lagna sign, house lords map
- **Returns:** dict `{A1..A12: {sign, lord, planets_in_pada, interpretation}}`
- **Called by:** `engine.py:predict()` and `engine.py:analyze_static()`
- **Key logic:**
  - Arudha of Bhava X = count from lord to X, then same count again from lord
  - Special rule: if result = X itself or exactly 7th from X, use 10th from result

## DEPENDENCIES
config.py, coordinates.py

## RECENT CHANGES
- 2026-03-02: Created as standalone module
