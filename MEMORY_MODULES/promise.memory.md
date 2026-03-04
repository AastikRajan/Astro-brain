# Module: promise.py
## Last Updated: 2026-03-02

## PURPOSE
Implements Stage 1 (the Promise Gate) of the prediction pipeline using the classical Three Pillar Rule from BPHS. A domain can only manifest if natal promise exists: Bhava (house) + Bhavesha (house lord) + Karaka (universal significator) must collectively confirm the potential. Scores < 0.15 abort the prediction entirely.

## KEY FUNCTIONS

### evaluate_promise(domain, planet_houses, house_lords, shadbala_ratios, planet_lons, chart_data) → dict
- **Purpose:** Full Three Pillar promise evaluation for a domain
- **Inputs:** domain str, planet placement dicts, shadbala ratios, longitudes
- **Returns:** `{promise_pct, promise_ceiling, pillars, status, suppressed_vs_denied}`
- **Called by:** `engine.py:predict()`
- **Calls:** `_score_bhava()`, `_score_bhavesha()`, `_score_karaka()`
- **Key logic:**
  - Identifies domain house from DOMAIN_PRIMARY_HOUSE map
  - Scores each pillar 0–1; pillar is "strong" if ≥ PILLAR_STRENGTH_THRESHOLD (0.50)
  - 3 strong → 100%; 2 strong → 67%; 1 strong → 33%; 0 strong → 0% (hard denial)
  - Distinguishes "suppressed" (1-2 pillars weak from malefic) vs "denied" (all flat 0)

### _score_bhava(planet_houses, house_lords, shadbala_ratios, domain_house, planet_lons) → float
- **Purpose:** Score the domain house itself
- **Inputs:** planet placement dicts, domain house number
- **Returns:** float 0–1
- **Called by:** `evaluate_promise()`
- **Key logic:**
  - Checks planets occupying the house (benefic vs malefic)
  - Factors in lord strength and affliction by heavy malefics
  - Upachaya houses (3,6,10,11) treat malefics more leniently

### _score_bhavesha(house_lords, shadbala_ratios, planet_houses, domain_house) → float
- **Purpose:** Score the house lord's strength and placement
- **Inputs:** house lords dict, shadbala ratios
- **Returns:** float 0–1
- **Called by:** `evaluate_promise()`

### _score_karaka(domain, planet_lons, planet_houses, shadbala_ratios) → float
- **Purpose:** Score the universal karaka's strength
- **Inputs:** domain str, planet data
- **Returns:** float 0–1
- **Called by:** `evaluate_promise()`

## IMPORTANT CONSTANTS
- `PILLAR_STRENGTH_THRESHOLD = 0.50` — minimum for a pillar to count as "strong"
- `DOMAIN_KARAKA` — domain → universal karaka planet
- `DOMAIN_PRIMARY_HOUSE` — domain → primary house number
- `_KENDRA = {1, 4, 7, 10}`, `_TRIKONA = {1, 5, 9}`, `_DUSTHANA = {6, 8, 12}`, `_UPACHAYA = {3, 6, 10, 11}`
- `_NATURAL_BENEFICS = {MOON, MERCURY, JUPITER, VENUS}`
- `_NATURAL_MALEFICS = {SUN, MARS, SATURN, RAHU, KETU}`

## DEPENDENCIES
config.py (for constants, via local definitions)

## RECENT CHANGES
- 2026-03-02: Created as standalone module (was inline in engine.py)
- 2026-03-02: Added "suppressed vs denied" distinction logic
