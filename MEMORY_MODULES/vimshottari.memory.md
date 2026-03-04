# Module: vimshottari.py
## Last Updated: 2026-03-02

## PURPOSE
Computes the Vimshottari Dasha system — the primary 120-year planetary period cycle in Jyotish. Generates the full hierarchy of Maha-dasha, Antar-dasha, Pratyantar-dasha, and Sookshma periods from birth Moon nakshatra. The active dasha is the primary timing signal in the prediction pipeline.

## KEY FUNCTIONS

### compute_mahadasha_periods(moon_longitude, birth_date) → List[dict]
- **Purpose:** Generate full Vimshottari dasha tree from birth
- **Inputs:** `moon_longitude` float (0–360°), `birth_date` datetime
- **Returns:** List of period dicts with start/end dates and sub-period nesting
- **Called by:** `engine.py:analyze_static()`
- **Calls:** `_birth_dasha_balance()`, `_dasha_sequence_from()`, `_compute_sub_periods()`

### get_active_dasha(periods, on_date) → dict
- **Purpose:** Find the currently active Maha + Antar + Pratyantar dasha period
- **Inputs:** `periods` (from compute_mahadasha_periods), `on_date` datetime
- **Returns:** `{mahadasha, antardasha, pratyantar, lords, start, end}`
- **Called by:** `engine.py:predict()`

### detect_dasha_sandhi(periods, on_date, window_days) → dict
- **Purpose:** Detect if we're in a dasha transition zone (sandhi)
- **Inputs:** periods list, current date, lookahead window in days
- **Returns:** `{in_sandhi, days_to_change, outgoing, incoming}`
- **Called by:** `engine.py:predict()`

### dasha_diagnostic_matrix(periods, on_date) → dict
- **Purpose:** Full diagnostic matrix of all running periods for debugging
- **Called by:** `main.py` (display section)

### analyze_retrograde_dasha_lord(planet, is_retrograde, natal_house, planet_houses) → dict
- **Purpose:** Assess retrograde modification to dasha lord effects
- **Called by:** `engine.py:predict()`

## IMPORTANT CONSTANTS
- `VIMSHOTTARI_YEARS` from config.py — planet → dasha years mapping (total 120)
- `VIMSHOTTARI_SEQUENCE` from config.py — fixed order of 9 planets

## DEPENDENCIES
config.py (Planet, VIMSHOTTARI_YEARS, VIMSHOTTARI_SEQUENCE)

## RECENT CHANGES
- 2026-03-02: Added dasha_diagnostic_matrix() for debugging
- 2026-03-02: Added analyze_retrograde_dasha_lord()
