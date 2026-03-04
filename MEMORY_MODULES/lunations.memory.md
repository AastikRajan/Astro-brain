# Module: lunations.py
## Last Updated: 2026-03-02

## PURPOSE
Computes upcoming New Moons, Full Moons, and Solar/Lunar Eclipses with their significance ratings. Eclipse dates are flagged as high-caution periods in Muhurta analysis and as potential activation triggers in transit analysis (especially when near natal degrees).

## KEY FUNCTIONS

### compute_upcoming_lunations(on_date, count, moon_lon, sun_lon) → List[dict]
- **Purpose:** Compute next N New/Full Moon dates from a given date
- **Returns:** List of `{date, type, sun_lon, moon_lon, eclipse, significance}`
- **Called by:** `engine.py:predict()`

### get_eclipse_alerts(lunations, natal_positions) → List[dict]
- **Purpose:** Flag upcoming eclipses that conjunct or oppose natal planet positions
- **Returns:** List of `{date, type, natal_planet, separation_degrees, alert_level}`
- **Called by:** `engine.py:predict()`

### get_high_significance_lunations(lunations) → List[dict]
- **Purpose:** Filter to only high-significance lunations (eclipses or near sensitive degrees)
- **Called by:** `engine.py` for report summary

## DEPENDENCIES
transits.py (for position data), config.py

## RECENT CHANGES
- 2026-03-02: Wired eclipse alerts into engine.py Muhurta output
