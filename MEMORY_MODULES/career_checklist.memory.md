# Module: career_checklist.py
## Last Updated: 2026-03-02

## PURPOSE
Implements a comprehensive career domain checklist that systematically evaluates career potential from multiple angles: 10th house strength, 10th lord, Sun (natural career karaka), Saturn (profession), Amatyakaraka (career soul significator), D10 Dashamsha chart, and relevant yogas. Returns a structured checklist with scores per factor.

## KEY FUNCTIONS

### compute_career_checklist(planet_houses, planet_signs, planet_lons, lagna_sign, shadbala, varga_data, yogas, karakas) → dict
- **Purpose:** Run all career strength checks
- **Inputs:** Full chart data, shadbala, varga reports, yoga list, karaka assignments
- **Returns:** `{checklist: [factor: str, score: float, notes: str], total_score, band, strong_factors, weak_factors}`
- **Called by:** `engine.py:predict()` when domain="career"
- **Key logic:**
  - Checks 10th house lord sign and strength
  - Checks Sun placement and dignity
  - D10 dashamsha lagna lord strength
  - Amatyakaraka (AmK) house placement
  - Checks for career yogas (10th lord in Kendra/Trikona, Raja conjunctions)

## DEPENDENCIES
yogas.py, shadbala.py, divisional.py, config.py

## RECENT CHANGES
- 2026-03-02: Created as new module
