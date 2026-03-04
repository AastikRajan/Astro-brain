# Module: aspect_transits.py
## Last Updated: 2026-03-02

## PURPOSE
Computes transit-to-natal aspects using both Parashari (graha drishti) and exact orb-based methods. Scores which transiting planets are forming significant aspects to natal planets, especially domain-relevant ones. Provides natal activation score — how strongly transits are triggering the natal promise.

## KEY FUNCTIONS

### compute_transit_aspects(transit_lons, natal_lons, orb_degrees) → List[dict]
- **Purpose:** Find all significant transit-to-natal aspects
- **Inputs:** current transit longitudes, natal longitudes, orb threshold
- **Returns:** List of `{transiting, natal, aspect_type, orb, score}`
- **Called by:** `engine.py:predict()`

### compute_natal_activation_score(transit_aspects, domain_planets) → float
- **Purpose:** Aggregate activation score for domain-relevant natal positions
- **Returns:** float 0–1
- **Called by:** `engine.py:predict()`

### top_transit_aspects(transit_aspects, n) → List[dict]
- **Purpose:** Return top N most significant transit aspects for report display
- **Called by:** `main.py` for report rendering

## DEPENDENCIES
config.py, coordinates.py

## RECENT CHANGES
- 2026-03-02: Created as new module; added natal_activation_score for Bayesian input
