# Module: ephemeris_audit.py
## Last Updated: 2026-03-02

## PURPOSE
Audits ephemeris accuracy by comparing positions from multiple sources (pyswisseph, skyfield, astropy, approximate) against each other for a set of test dates. Reports mean error per planet across sources. Used for development validation of the 4-tier ephemeris cascade.

## KEY FUNCTIONS

### run_ephemeris_audit(n, verbose) → dict
- **Purpose:** Run N random date accuracy comparisons across all ephemeris tiers
- **Inputs:** `n` number of test points, `verbose` bool
- **Returns:** `{errors_by_planet, source_comparison, max_error, mean_error}`
- **Called by:** `transits.py:run_ephemeris_audit()` (re-exported)

## DEPENDENCIES
transits.py (all position backends), skyfield_positions.py, astropy_positions.py, swisseph_bridge.py

## RECENT CHANGES
- 2026-03-02: Created as dedicated audit module
