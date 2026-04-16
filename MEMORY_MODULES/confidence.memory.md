# Module: confidence.py
## Last Updated: 2026-04-14

## PURPOSE
Computes the weighted confidence core for a domain prediction, including gate-state adaptive weighting, promise/KP/dasha caps, and dasha-throttle modifiers. This output feeds the engine blend and final arbitration stage.

## KEY FUNCTIONS

### compute_confidence(...) → dict
- **Purpose:** Build component scores, apply adaptive weights/caps, and return normalized confidence diagnostics
- **Inputs:** domain + dasha/transit/kp/yoga/varga bundles, promise gate output, and runtime throttles (`dasha_lord_gochar_mult`, `dasha_pravesha_mult`)
- **Returns:** dict with `overall`, `gate_status`, `components`, and `weights_used`
- **Called by:** `engine.py:predict()`
- **Key logic:**
  - Computes component stack: dasha alignment, transit support, ashtakvarga support, yoga activation, KP confirmation, functional alignment, house-lord (weight zero), Jaimini sub-score, D9 quality
  - Applies adaptive weights by gate state (`BOTH_GATES_PASSED`, `DASHA_NOT_CONFIRMED`, `PROMISE_FAILED`)
  - Applies geometric/combustion/retrograde adjustments on dasha component
  - Applies dasha-lord gochar multiplier and bounded Dasha Pravesha multiplier on dasha component
  - Applies promise and KP caps before final `overall`

### score_dasha_alignment(...) → float
- **Purpose:** Score active MD/AD/PD domain signaling quality
- **Called by:** `compute_confidence()`
- **Key logic:** blends domain relevance, strength modifiers, and classical dampeners

### score_transit_support(transit_scores, domain_planets) → float
- **Purpose:** Aggregate net transit support for domain-relevant planets
- **Called by:** `compute_confidence()`

### _tiered_bav(values, signs) → float
- **Purpose:** Shared non-linear bindu scorer for SAV/BAV-derived support
- **Called by:** `compute_confidence()` and Ashtakvarga sub-routines

### multi_system_agreement(...) → dict
- **Purpose:** Summarize cross-system timing agreement and lock-level diagnostics
- **Called by:** `engine.py:predict()`

## IMPORTANT CONSTANTS
- `W_DASHA = 0.25` — Dasha component weight
- `W_TRANSIT = 0.20` — Transit support weight
- `W_ASHTAKVARGA = 0.15` — Natal SAV/BAV weight
- `W_YOGA = 0.13` — Active yoga weight
- `W_KP = 0.12` — KP sub-lord weight
- `W_FUNCTIONAL = 0.08` — Functional role weight
- `W_HOUSE_LORD = 0.00` — Zeroed to avoid Promise double-count
- `DOMAIN_KARAKA_BAV_MAP` — domain-specific karaka BAV map

## DEPENDENCIES
config.py, score helpers in same module, and engine-provided dynamic payloads.

## RECENT CHANGES
- 2026-04-14: Dasha Pravesha multiplier (`dasha_pravesha_mult`) integrated into dasha alignment path and exposed in confidence components
- 2026-04-14: Gate/cap diagnostics aligned for downstream deterministic arbitration stage
- 2026-03-02: Added `DOMAIN_KARAKA_BAV_MAP` and shared `_tiered_bav()`
- 2026-03-02: Set `W_HOUSE_LORD=0.00` to prevent Promise double-counting
