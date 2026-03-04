# Module: varga_analysis.py
## Last Updated: 2026-03-02

## PURPOSE
Generates a comprehensive multi-divisional chart analysis report. Evaluates each planet's sign placement across D1, D9, D10, D7, D4, D2, D3 and produces dignity counts and domain-specific varga scores. Higher cross-varga dignity indicates more consistent planetary strength.

## KEY FUNCTIONS

### compute_varga_report(planet_longitudes) → dict
- **Purpose:** Cross-divisional dignity analysis for all planets
- **Inputs:** natal planet longitudes
- **Returns:** dict planet → `{varga_scores, dignity_by_varga, domain_scores}`
- **Called by:** `engine.py:analyze_static()`
- **Calls:** `divisional.compute_all_vargas()`, `vimshopak.compute_all_vimshopak()`
- **Key logic:**
  - Computes sign in each varga
  - Checks dignity (exalted/own/etc.) in each varga
  - Produces domain-specific composite score (D10 weight for career, D9 for marriage, etc.)

## DEPENDENCIES
divisional.py, vimshopak.py, config.py

## RECENT CHANGES
- 2026-03-02: No changes
