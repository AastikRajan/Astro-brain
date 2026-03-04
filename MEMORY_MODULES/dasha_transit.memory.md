# Module: dasha_transit.py
## Last Updated: 2026-03-02

## PURPOSE
Analyzes the transit of the active dasha lord and builds an ingress calendar showing when the dasha lord moves through each sign during the dasha period. The dasha lord's own transit through key houses is a powerful activation signal (Double Transit principle).

## KEY FUNCTIONS

### analyze_dasha_lord_transit(dasha_planet, transit_positions, natal_data) → dict
- **Purpose:** Evaluate the Maha Dasha lord's current transit position significance
- **Returns:** `{house_from_moon, house_from_lagna, gochar_score, double_transit_active}`
- **Called by:** `engine.py:predict()`

### compute_ingress_calendar(planet, start_date, end_date) → List[dict]
- **Purpose:** Compute dates when the planet ingresses into each sign over a period
- **Returns:** List of `{date, sign, house_from_lagna, house_from_moon}`
- **Called by:** `engine.py` for timing windows

## DEPENDENCIES
transits.py, vimshottari.py, config.py

## RECENT CHANGES
- 2026-03-02: Created as dedicated module (was inline in engine.py)
