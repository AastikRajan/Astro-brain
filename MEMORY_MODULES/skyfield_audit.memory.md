# Module: skyfield_audit.py
## Last Updated: 2026-03-02

## PURPOSE
Audit and validation tool that compares Skyfield JPL ephemeris positions against reference values from published astronomical almanacs. Used during development to validate that the 2nd-tier ephemeris source meets accuracy requirements (< 0.1° error for outer planets, < 1° for inner planets).

## KEY FUNCTIONS

### run_skyfield_audit(test_dates, reference_data, verbose) → dict
- **Purpose:** Run accuracy audit for Skyfield positions against reference
- **Returns:** `{passed, errors_by_planet, max_error_deg, report}`

## DEPENDENCIES
skyfield, skyfield_positions.py

## RECENT CHANGES
- 2026-03-02: Created as development utility
