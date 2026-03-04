# Module: dispositor.py
## Last Updated: 2026-03-02

## PURPOSE
Computes the dispositor chain for each planet (each planet→its sign lord→that lord's sign lord→...until reaching own sign) and analyzes the dasha lord's dispositor for prediction quality. A dasha lord with a strong final dispositor (a planet in its own or exalted sign) enhances prediction reliability.

## KEY FUNCTIONS

### compute_dispositor_graph(planet_signs) → dict
- **Purpose:** Build full dispositor chain for all planets
- **Returns:** dict planet → `{chain: [p1, p2, ...], final: planet, depth, is_self_disposited}`
- **Called by:** `engine.py:analyze_static()`

### analyze_dasha_lord_dispositor(dasha_planet, dispositor_graph, shadbala) → dict
- **Purpose:** Analyze the dispositor chain quality for the active dasha lord
- **Returns:** `{final_dispositor, chain_strength, interpretation}`
- **Called by:** `engine.py:predict()`

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: No changes
