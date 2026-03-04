# Module: jyotishganit_bridge.py
## Last Updated: 2026-03-02

## PURPOSE
Wraps the JyotishGanit Python library as an alternative chart computation backend. Provides an additional position source for validation and cross-checking. Currently not integrated into the main ephemeris cascade.

## KEY FUNCTIONS

### compute_positions_jg(birth_dt, lat, lon) → dict
- **Purpose:** Compute chart positions via JyotishGanit library
- **Returns:** dict with planet positions and lagna

## DEPENDENCIES
jyotishganit (optional — rarely installed)

## RECENT CHANGES
- 2026-03-02: No changes (validation utility)
