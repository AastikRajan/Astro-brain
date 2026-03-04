# Module: argala.py
## Last Updated: 2026-03-02

## PURPOSE
Computes Argala (intervention/obstruction) from the Jaimini system. Argala occurs when planets occupy the 2nd, 4th, or 11th from a reference sign, providing positive intervention. Planets in 3rd, 10th, 12th provide Virodha-Argala (obstruction). Used in the Jaimini analysis section of the report.

## KEY FUNCTIONS

### compute_all_argala(planet_signs, planet_houses) → dict
- **Purpose:** Compute Argala and Virodha-Argala for all 12 signs and Lagna
- **Inputs:** planet signs and houses
- **Returns:** dict sign → `{argala_planets, virodha_planets, net_argala, interpretation}`
- **Called by:** `engine.py:analyze_static()`

## IMPORTANT CONSTANTS
Argala positions: 2nd, 4th, 11th from reference sign (positive).
Virodha positions: 3rd, 10th, 12th from reference sign (obstructing).

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: Created as standalone module
