# Module: karakamsha.py
## Last Updated: 2026-03-02

## PURPOSE
Computes the Karakamsha — the sign in the D9 (Navamsha) chart where the Atmakaraka (AK) planet is placed. This sign becomes significant for spiritual and life-purpose predictions in Jaimini Astrology. Planets in Karakamsha indicate life themes and soul's desires.

## KEY FUNCTIONS

### compute_karakamsha(atmakaraka_planet, planet_longitudes) → dict
- **Purpose:** Find the Karakamsha sign and analyze its implications
- **Inputs:** Atmakaraka planet name, natal longitudes
- **Returns:** `{karakamsha_sign, sign_name, lord, planets_in_karakamsha, interpretation}`
- **Called by:** `engine.py:analyze_static()`

## DEPENDENCIES
divisional.py (D9 computation), config.py

## RECENT CHANGES
- 2026-03-02: No changes
