# Module: dasha_quality.py
## Last Updated: 2026-03-02

## PURPOSE
Computes Ishta Phala (benefic potential) and Kashta Phala (malefic potential) scores for each planet as a dasha lord, and combines them into an overall dasha quality score. Also models planetary maturity effects (Naisargika Pakvata) that modify dasha results by native's age.

## KEY FUNCTIONS

### compute_ishta_kashta(planet, longitude, shadbala_virupas, ...) → dict
- **Purpose:** Ishta and Kashta Phala for a planet in the natal chart
- **Inputs:** planet name, longitude, shadbala, dignity info
- **Returns:** `{ishta, kashta, net_score, quality_band}`
- **Called by:** `engine.py:analyze_static()` for all planets

### maturity_modifier(planet, native_age) → dict
- **Purpose:** Age-based maturity factor — planets reach full results at maturity age
- **Inputs:** planet name, native's current age
- **Returns:** `{maturity_age, current_modifier, stage}`
- **Key logic:** Saturn matures at 36, Rahu at 42, etc.

### dasha_quality_score(md_planet, ad_planet, ishta_kashta_data, maturity_data, yoga_data) → dict
- **Purpose:** Combined dasha quality assessment for active Maha+Antar dasha
- **Returns:** `{overall_score, band, modifiers_applied}`
- **Called by:** `engine.py:predict()`

### dasha_quality_for_all_planets(planet_lons, shadbala, native_age) → dict
- **Purpose:** Compute dasha quality for all 9 planets at once
- **Called by:** `engine.py:analyze_static()`

## IMPORTANT CONSTANTS
Maturity ages: SUN=22, MOON=24, MARS=28, MERCURY=32, JUPITER=16, VENUS=25, SATURN=36, RAHU=42, KETU=48

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: Ishta/Kashta Phala wired into engine static analysis and Bayesian prior
