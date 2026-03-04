# Module: fuzzy_confidence.py
## Last Updated: 2026-03-02

## PURPOSE
Implements Stage 3 of the prediction pipeline using a fuzzy logic inference system (scikit-fuzzy). Models the non-linear compounding of three orthogonal evidence streams: timing (dasha+KP), transit (gochar+BAV), and structural (yogas+functional+natal). Falls back to the linear Bayesian score if scikit-fuzzy is unavailable.

## KEY FUNCTIONS

### compute_fuzzy_confidence(timing, transit, structural) → dict
- **Purpose:** 3-input fuzzy inference returning compound confidence
- **Inputs:** `timing` float 0–1, `transit` float 0–1, `structural` float 0–1
- **Returns:** `{fuzzy_confidence, verdict, method}` — method is "fuzzy" or "fallback"
- **Called by:** `engine.py:predict()`
- **Calls:** `_build_fuzzy_system()`
- **Key logic:**
  - All three inputs HIGH → confidence compounds to HIGH
  - Two HIGH + one LOW → medium-high (strong opposition suppresses)
  - All LOW → very low output
  - Uses centroid defuzzification

### aggregate_for_fuzzy(components) → dict
- **Purpose:** Aggregate raw component scores into the 3 fuzzy inputs
- **Inputs:** `components` dict from compute_confidence
- **Returns:** `{timing, transit, structural}` floats
- **Called by:** `engine.py:predict()`
- **Key logic:**
  - timing = 0.6×dasha_alignment + 0.4×kp_confirmation
  - transit = 0.65×transit_support + 0.35×ashtakvarga
  - structural = 0.5×yoga + 0.5×functional

### _build_fuzzy_system() → ControlSystem
- **Purpose:** Build and cache the scikit-fuzzy control system
- **Inputs:** (none)
- **Returns:** cached ControlSystem object
- **Called by:** `compute_fuzzy_confidence()`
- **Key logic:**
  - 3 antecedents (timing, transit, structural), 1 consequent (confidence)
  - 3 membership levels each: low [0,0,0.4], medium [0.2,0.5,0.8], high [0.6,1,1]
  - ~9 rules covering all combination cases

## IMPORTANT CONSTANTS
- `_fuzzy_ctrl = None` — module-level cache of the ControlSystem
- Membership function ranges: low=[0,0,0.4], medium=[0.2,0.5,0.8], high=[0.6,1,1]

## DEPENDENCIES
scikit-fuzzy (optional), numpy (via scikit-fuzzy)

## RECENT CHANGES
- 2026-03-02: Created as new module replacing linear fallback in engine.py
