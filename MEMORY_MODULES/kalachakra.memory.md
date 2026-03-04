# Module: kalachakra.py
## Last Updated: 2026-03-02

## PURPOSE
Implements the Kalachakra Dasha system — a complex nakshatra-pada based timing system derived from the Kalachakra Tantra. Divides nakshatras into Savya (clockwise) and Apasavya (counter-clockwise) groups and assigns dasha years to each nakshatra-pada. Also provides Deha and Jeeva sign identification for transit analysis.

## KEY FUNCTIONS

### compute_kalachakra_dasha(moon_longitude, birth_date) → List[dict]
- **Purpose:** Full Kalachakra period sequence from birth Moon nakshatra-pada
- **Calls:** `_get_nak_pada()`, `_is_savya()`, `_detect_gati()`
- **Called by:** `engine.py:analyze_static()`

### get_active_kalachakra_period(periods, on_date) → dict
- **Purpose:** Find active Kalachakra period for a date

### analyze_deha_jeeva_transits(deha_sign, jeeva_sign, transit_positions) → dict
- **Purpose:** Check if transits are activating Deha or Jeeva signs
- **Called by:** `engine.py:predict()`

### _get_nak_pada(moon_longitude) → Tuple[int, int]
- **Purpose:** Get nakshatra index and pada (1–4) from longitude

### _is_savya(group) → bool
- **Purpose:** Determine if nakshatra group is Savya (forward) or Apasavya (reverse)

### _detect_gati(seq, i) → Optional[str]
- **Purpose:** Detect special Gati (Manduka, Markata etc.) transitions

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: Full implementation added
