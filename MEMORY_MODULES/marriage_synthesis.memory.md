# Module: marriage_synthesis.py
## Last Updated: 2026-03-02

## PURPOSE
Synthesizes marriage readiness and timing from multiple indicators: 7th house strength, Venus (natural karaka), DK (Darakaraka), D9 Navamsha analysis, relevant yogas (Vivaha yoga), and active dasha compatibility. Produces a readiness score and identifies the optimal marriage timing window.

## KEY FUNCTIONS

### compute_marriage_synthesis(planet_houses, planet_signs, planet_lons, lagna_sign, shadbala, varga_data, yogas, karakas, dasha_periods, on_date) → dict
- **Purpose:** Full marriage timing and readiness analysis
- **Returns:** `{readiness_score, optimal_windows, delaying_factors, supporting_factors, dk_analysis, d9_analysis}`
- **Called by:** `engine.py:predict()` when domain="marriage"
- **Key logic:**
  - Evaluates 7th lord strength and placement
  - Venus karaka condition in D1 and D9
  - DK planet strength and current dasha activation
  - Cross-checks for delay yoga patterns (Manglik, Saturn 7th, etc.)

## DEPENDENCIES
yogas.py, karakas.py, divisional.py, config.py

## RECENT CHANGES
- 2026-03-02: Created as new module
