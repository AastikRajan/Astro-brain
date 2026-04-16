# Arbitration Calibration Snapshot (2026-04-14)

Derived from parsing `full_engine_run_report*.txt` (UTF-16 text reports).

## Data Coverage

- Report files parsed: 28
- Domains covered: CAREER, FINANCE, HEALTH, MARRIAGE
- Metric extracted: final displayed domain confidence percent from each report

## Observed Confidence Distribution

| Domain | Count | Min | Median | Mean | P90 | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CAREER | 28 | 50.3 | 58.35 | 57.43 | 64.9 | 64.9 |
| FINANCE | 28 | 35.3 | 43.2 | 43.15 | 44.4 | 44.4 |
| HEALTH | 28 | 37.7 | 43.6 | 43.94 | 46.9 | 47.1 |
| MARRIAGE | 28 | 28.9 | 36.1 | 36.47 | 38.0 | 38.1 |

## Applied Domain Arbitration Profiles

These profiles are applied in `PredictionEngine._apply_confidence_arbitration_gate(...)` as domain-specific caps and contradiction dampeners.

- `career`
  - promise_failed_cap: 0.32
  - promise_failed_elevated_cap: 0.50
  - dasha_not_confirmed_cap: 0.58
  - lock_below_2_cap: 0.52
  - d9_contradiction_cap: 0.62
  - bayes_high_uncertainty_cap: 0.68
  - bayes_moderate_uncertainty_cap: 0.76
  - bayes_weak_verdict_cap: 0.60

- `finance`
  - promise_failed_cap: 0.25
  - promise_failed_elevated_cap: 0.40
  - dasha_not_confirmed_cap: 0.45
  - lock_below_2_cap: 0.40
  - d9_contradiction_cap: 0.52
  - bayes_high_uncertainty_cap: 0.48
  - bayes_moderate_uncertainty_cap: 0.55
  - bayes_weak_verdict_cap: 0.46

- `health`
  - promise_failed_cap: 0.27
  - promise_failed_elevated_cap: 0.42
  - dasha_not_confirmed_cap: 0.48
  - lock_below_2_cap: 0.43
  - d9_contradiction_cap: 0.56
  - bayes_high_uncertainty_cap: 0.52
  - bayes_moderate_uncertainty_cap: 0.60
  - bayes_weak_verdict_cap: 0.50

- `marriage`
  - promise_failed_cap: 0.22
  - promise_failed_elevated_cap: 0.35
  - dasha_not_confirmed_cap: 0.42
  - lock_below_2_cap: 0.38
  - d9_contradiction_cap: 0.45
  - bayes_high_uncertainty_cap: 0.42
  - bayes_moderate_uncertainty_cap: 0.48
  - bayes_weak_verdict_cap: 0.40

## Notes

- Generic/default profile remains active for unknown domains.
- This is a first empirical calibration pass and should be re-fit after fresh benchmark campaigns.
