# Module: confidence.py
## Last Updated: 2026-03-02

## PURPOSE
Computes the raw 8-component weighted confidence score for a domain prediction. Each component is normalized to 0–1 before weighting. This raw score feeds both the Bayesian and Fuzzy stages. Implements the primary evidence-aggregation layer.

## KEY FUNCTIONS

### compute_confidence(components, domain, gate_state) → float
- **Purpose:** Weighted sum of 8 normalized component scores
- **Inputs:** `components` dict with dasha_alignment, transit_support, ashtakvarga, yoga, kp, functional, karaka_bav; `domain` str; `gate_state` str
- **Returns:** float 0–1 raw confidence
- **Called by:** `engine.py:predict()`
- **Calls:** `score_dasha_alignment()`, `score_transit_support()`, `_tiered_bav()`, sub-scorers
- **Key logic:**
  - Applies adaptive weights based on gate_state (FULL/PARTIAL/WEAK)
  - W_HOUSE_LORD = 0.00 always (zeroed to prevent double-count with Promise)
  - Blends karaka BAV: 40% SAV + 35% karaka-specific BAV + 25% dasha BAV

### score_dasha_alignment(dasha_planet, antardasha_planet, domain, planet_domain_map, shadbala_ratios) → float
- **Purpose:** Score how well active dasha lord signals the queried domain
- **Inputs:** dasha/antardasha planet names, domain str, domain map, shadbala ratios
- **Returns:** float 0–1
- **Called by:** `compute_confidence()`
- **Calls:** (none)
- **Key logic:**
  - +0.60 if MD planet signifies domain; +0.40 if AD planet also signifies
  - Modulated by shadbala ratio (0.5–1.5 range normalized to 50–100% score)

### score_transit_support(transit_scores, domain_planets) → float
- **Purpose:** Average net_score of domain-relevant transiting planets
- **Inputs:** transit_scores dict, domain_planets list
- **Returns:** float 0–1 (neutral 0.3 if no data)
- **Called by:** `compute_confidence()`
- **Calls:** (none)

### _tiered_bav(values, signs) → float
- **Purpose:** Tiered Ashtakvarga bindu scorer shared by SAV and planet BAV signals
- **Inputs:** `values` list of bindu counts per sign, `signs` list of sign indices
- **Returns:** float 0–1
- **Called by:** `compute_confidence()`, ashtakvarga scoring helpers
- **Key logic:**
  - ≤2 bindus → 0.0; 3 → ~0.10; 4 → ~0.40; 5+ → ~0.60+
  - Non-linear scaling rewards high-bindu zones

### multi_system_agreement(components) → dict
- **Purpose:** Checks how many systems agree (cross-validation metric)
- **Inputs:** components dict
- **Returns:** {count_agreeing, verdict}
- **Called by:** `engine.py:predict()`

## IMPORTANT CONSTANTS
- `W_DASHA = 0.25` — Dasha component weight
- `W_TRANSIT = 0.20` — Transit support weight
- `W_ASHTAKVARGA = 0.15` — Natal SAV/BAV weight
- `W_YOGA = 0.13` — Active yoga weight
- `W_KP = 0.12` — KP sub-lord weight
- `W_FUNCTIONAL = 0.08` — Functional role weight
- `W_HOUSE_LORD = 0.00` — ZEROED (§9.3 double-count fix)
- `DOMAIN_KARAKA_BAV_MAP` — per-domain planet-house BAV mapping dict

## DEPENDENCIES
config.py (implicit via engine.py injection)

## RECENT CHANGES
- 2026-03-02: Added DOMAIN_KARAKA_BAV_MAP with classical karaka assignments
- 2026-03-02: Extracted _tiered_bav() shared helper
- 2026-03-02: W_HOUSE_LORD zeroed (was 0.07)
- 2026-03-02: W_DASHA reduced 0.30→0.25, W_TRANSIT reduced 0.22→0.20
