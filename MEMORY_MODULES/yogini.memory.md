# Module: yogini.py
## Last Updated: 2026-03-02

## PURPOSE
Implements the Yogini Dasha system — an 8-planet cycle totaling 36 years. Each of 8 Yoginis rules a period determined by the Moon's natal nakshatra. Used as a secondary corroborating timing system alongside Vimshottari in the engine.

## KEY FUNCTIONS

### compute_yogini_periods(moon_longitude, birth_date) → List[dict]
- **Purpose:** Full Yogini Dasha period list from birth
- **Inputs:** natal Moon longitude, birth date
- **Returns:** List of period dicts (yogini name, lord, start, end, sub-periods)

### get_active_yogini(periods, on_date) → dict
- **Purpose:** Find the active Yogini and sub-Yogini for a date
- **Called by:** `engine.py:predict()`

### _yogini_start(moon_longitude) → Tuple[int, float]
- **Purpose:** Determine starting Yogini and balance from Moon's nakshatra

### _yogini_sub_periods(main_idx, main_start, main_end) → List[dict]
- **Purpose:** Compute sub-periods within a Yogini maha-period

## IMPORTANT CONSTANTS
8 Yoginis: Mangala(1yr), Pingala(2yr), Dhanya(3yr), Bhramari(4yr), Bhadrika(5yr), Ulka(6yr), Siddha(7yr), Sankata(8yr); total=36yr

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: Initial full implementation
