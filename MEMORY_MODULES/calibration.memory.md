# Module: calibration.py
## Last Updated: 2026-03-02

## PURPOSE
Maps raw composite confidence scores (from weighted sum + Bayesian + Fuzzy stages) to a calibrated output using a Platt-scaling sigmoid approach. Prevents extreme outputs (always near 0 or 1) by mapping to a reasonable practical range. Applies domain-specific calibration offsets.

## KEY FUNCTIONS

### calibrate_confidence(raw_score, domain, promise_pct, method) → dict
- **Purpose:** Calibrate raw confidence to practical prediction scale
- **Inputs:** raw_score float, domain str, promise_pct float, method str ("bayesian"/"fuzzy"/"linear")
- **Returns:** `{calibrated_score, band, lower_bound, upper_bound}`
- **Called by:** `engine.py:predict()`
- **Key logic:**
  - Applies Platt sigmoid: 1/(1+exp(-k×(x-x0)))
  - Clips to [0.10, 0.95] range (never certitude)
  - Domain-specific offset for typically harder domains (health vs finance)

## DEPENDENCIES
(none — pure math)

## RECENT CHANGES
- 2026-03-02: Added domain-specific offset table
