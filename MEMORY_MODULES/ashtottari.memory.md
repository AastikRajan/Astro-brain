# Module: ashtottari.py
## Last Updated: 2026-03-02

## PURPOSE
Implements the Ashtottari Dasha system — a conditional 108-year cycle used only when eligible (Rahu in a Trikona from Lagna or Moon in certain positions). Uses 8 planets (no Ketu) with different year allocations than Vimshottari.

## KEY FUNCTIONS

### is_ashtottari_eligible(planet_houses, lagna_sign, moon_sign) → dict
- **Purpose:** Check eligibility conditions for Ashtottari Dasha
- **Returns:** `{eligible, reason}`

### compute_ashtottari_periods(moon_longitude, birth_date) → List[dict]
- **Purpose:** Full 108-year period tree

### get_active_ashtottari(periods, on_date) → dict
- **Purpose:** Find active Ashtottari maha/antar period

### ashtottari_details_on_date(moon_longitude, birth_date, on_date, ...) → dict
- **Purpose:** Full details for engine integration
- **Called by:** `engine.py:analyze_static()`

## IMPORTANT CONSTANTS
- `ASHTOTTARI_YEARS` — 8-planet year dict (SUN=6,MOON=15,MARS=8,MERCURY=17,SATURN=10,JUPITER=19,RAHU=12,VENUS=21; total=108)

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: Added eligibility check and full dasha computation
