# Module: functional.py
## Last Updated: 2026-03-02

## PURPOSE
Computes the functional benefic/malefic status of each planet based on the native's Lagna (Ascendant sign). Functionals differ from Lagna to Lagna — the same planet may be a yoga-karaka for one Lagna but a strong malefic for another. This is a key input to the Bayesian prior.

## KEY FUNCTIONS

### compute_functional_analysis(lagna_sign, planet_houses, house_lords, shadbala) → dict
- **Purpose:** Classify each planet's functional role for the given lagna
- **Inputs:** lagna sign index, planet placement dicts
- **Returns:** dict planet → `{role, yogakaraka, maraka, score}`
- **Called by:** `engine.py:analyze_static()`
- **Key logic:**
  - Lords of Kendra + Trikona → Yoga Karakas (most benefic)
  - Lords of 6,8,12 (Dusthana) → functional malefics
  - Lords of 2,7 (Maraka houses) → Maraka (death-inflicting) classification
  - Naturally benefic planets owning Dusthana = compromised

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: Added maraka classification to output dict
