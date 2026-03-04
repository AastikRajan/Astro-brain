# Module: astropy_positions.py
## Last Updated: 2026-03-02

## PURPOSE
Provides planet position computation via the Astropy library. Third-tier ephemeris source in the 4-tier cascade. Uses Astropy's built-in ERFA/IAU coordinates. Less precise than Skyfield but widely available via pip.

## KEY FUNCTIONS

### get_positions_astropy(on_date) → Dict[str, float]
- **Purpose:** Compute sidereal longitudes using Astropy
- **Inputs:** datetime
- **Returns:** dict planet → sidereal longitude
- **Called by:** `transits.py:_get_positions_astropy()`

## DEPENDENCIES
astropy (optional)

## RECENT CHANGES
- 2026-03-02: Extracted from transits.py into dedicated module
