# Arbitration Calibration Snapshot (2026-04-15)

Derived from parsing `full_engine_run_report*.txt` corpus using `DOMAIN: ... | Confidence: ...` lines.

## Data Coverage

- Report files matched: 30
- Reports with usable domain confidence lines: 29
- Domains covered: CAREER, FINANCE, HEALTH, MARRIAGE
- Metric extracted: final displayed domain confidence percent

## Observed Confidence Distribution

| Domain | Count | Min | Median | Mean | P90 | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CAREER | 29 | 31.3 | 55.7 | 56.53 | 64.9 | 64.9 |
| FINANCE | 29 | 25.0 | 43.2 | 42.53 | 44.4 | 44.4 |
| HEALTH | 29 | 20.9 | 43.6 | 43.14 | 46.9 | 47.1 |
| MARRIAGE | 29 | 22.0 | 36.1 | 35.97 | 38.02 | 38.1 |

## Applied Domain Arbitration Profiles (R3)

These profiles are applied in `PredictionEngine._apply_confidence_arbitration_gate(...)` as domain-specific caps and contradiction dampeners.

- `career`
  - promise_failed_cap: 0.31
  - promise_failed_elevated_cap: 0.48
  - dasha_not_confirmed_cap: 0.56
  - lock_below_2_cap: 0.50
  - d9_contradiction_cap: 0.60
  - bayes_high_uncertainty_cap: 0.66
  - bayes_moderate_uncertainty_cap: 0.74
  - bayes_weak_verdict_cap: 0.58

- `finance`
  - promise_failed_cap: 0.24
  - promise_failed_elevated_cap: 0.39
  - dasha_not_confirmed_cap: 0.44
  - lock_below_2_cap: 0.39
  - d9_contradiction_cap: 0.50
  - bayes_high_uncertainty_cap: 0.46
  - bayes_moderate_uncertainty_cap: 0.53
  - bayes_weak_verdict_cap: 0.45

- `health`
  - promise_failed_cap: 0.24
  - promise_failed_elevated_cap: 0.39
  - dasha_not_confirmed_cap: 0.46
  - lock_below_2_cap: 0.41
  - d9_contradiction_cap: 0.54
  - bayes_high_uncertainty_cap: 0.50
  - bayes_moderate_uncertainty_cap: 0.58
  - bayes_weak_verdict_cap: 0.48

- `marriage`
  - promise_failed_cap: 0.21
  - promise_failed_elevated_cap: 0.34
  - dasha_not_confirmed_cap: 0.40
  - lock_below_2_cap: 0.36
  - d9_contradiction_cap: 0.43
  - bayes_high_uncertainty_cap: 0.40
  - bayes_moderate_uncertainty_cap: 0.46
  - bayes_weak_verdict_cap: 0.38

## Notes

- This snapshot supersedes the prior 2026-04-14 28-report baseline for active runtime profile metadata.
- Generic/default profile remains active for unknown domains.
- Broader benchmark expansion re-fit remains open after this pass.
