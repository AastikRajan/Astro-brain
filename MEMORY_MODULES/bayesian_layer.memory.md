# Module: bayesian_layer.py
## Last Updated: 2026-03-02

## PURPOSE
Implements Stage 2 of the prediction pipeline using Bayesian Beta-distribution updating. Models each domain's success probability as a Beta distribution, starting from a natal-based prior and updating it with time-specific evidence (dasha, transit, KP). Produces a posterior mean and credible interval rather than just a point estimate.

## KEY FUNCTIONS

### compute_bayesian_confidence(components, domain) → dict
- **Purpose:** Full Bayesian posterior update from prior + evidence
- **Inputs:** `components` dict (dasha_alignment, transit_support, ashtakvarga, kp, yoga, functional); `domain` str
- **Returns:** `{posterior_mean, credible_interval, evidence_weight, alpha, beta, verdict}`
- **Called by:** `engine.py:predict()`
- **Calls:** `_structural_prior()`, `_dasha_evidence()`, `_transit_evidence()`, `_kp_evidence()`, `_yoga_evidence()`
- **Key logic:**
  - Builds Beta prior from natal yoga+functional scores
  - Sequentially updates α,β with evidence pseudo-counts from each system
  - Computes posterior mean = α/(α+β); credible interval via Beta quantiles
  - Dasha carries most weight (3 obs), transit+BAV second (2 obs), KP binary (2 obs)

### _structural_prior(yoga, functional) → Tuple[float, float]
- **Purpose:** Build Beta(α,β) prior from natal chart strength signals
- **Inputs:** `yoga` float 0–1, `functional` float 0–1
- **Returns:** (alpha, beta) tuple
- **Called by:** `compute_bayesian_confidence()`
- **Key logic:**
  - natal = 0.55×yoga + 0.45×functional (house_lord removed §9.3)
  - concentration = 4.0 (weak prior — data dominates)
  - α = natal × 4, β = (1-natal) × 4

### _dasha_evidence(dasha_alignment) → Tuple[float, float]
- **Purpose:** Convert dasha alignment score to Beta pseudo-counts
- **Inputs:** `dasha_alignment` float 0–1
- **Returns:** (successes, failures) with total weight 3.0
- **Called by:** `compute_bayesian_confidence()`

### _transit_evidence(transit_support, ashtakvarga) → Tuple[float, float]
- **Purpose:** Composite transit+BAV evidence (weight 2.0)
- **Inputs:** `transit_support`, `ashtakvarga` floats
- **Returns:** (successes, failures); composite = 0.65×transit + 0.35×BAV
- **Called by:** `compute_bayesian_confidence()`

### _kp_evidence(kp_confirmation) → Tuple[float, float]
- **Purpose:** Binary KP sub-lord signal (weight 2.0)
- **Inputs:** `kp_confirmation` float
- **Returns:** Strong positive (2,0.2) if >0.5; strong negative (0.2,2) if <0.2; weak (0.5,0.5) otherwise
- **Called by:** `compute_bayesian_confidence()`

## IMPORTANT CONSTANTS
- Prior concentration: `4.0` (lines ~45)
- Dasha evidence strength: `3.0`
- Transit evidence strength: `2.0`
- KP evidence strength: `2.0` (binary split)
- Transit composite blend: `0.65×transit + 0.35×BAV`

## DEPENDENCIES
(none — pure Python math; all inputs injected by engine.py)

## RECENT CHANGES
- 2026-03-02: Removed house_lord_strength from _structural_prior() — was causing Bayesian double-count (§9.3); prior redistributed to yoga 55% + functional 45%
- 2026-03-02: Added dasha↔transit overlap detection — merges to single update when same planet triggers both systems
