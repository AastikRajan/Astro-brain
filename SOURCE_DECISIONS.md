# Source Decisions

## 2026-03-26 — Milestone A Scaffold

- decision_id: SD-2026-03-26-A1
- scope: Feature-flag scaffold only (no rule computation changes)
- source_of_truth: TECHNICAL_IMPLEMENTATION_AUDIT.md
- rationale:
  - Audit confirms Pravesha and Tripataki are missing in native runtime.
  - Audit confirms Harsha Bala is bridge-only.
  - User requested default-OFF for new logic until explicitly safe.
- implementation_notes:
  - Added OFF-by-default flags in prediction engine.
  - Added runtime flag snapshot debug payload to confidence output.
  - Did not alter prediction math in this milestone.
- unresolved_gaps:
  - Tripataki exact vedha geometry table not finalized from runtime-native sources.
  - Pravesha school choice conflict (tropical-month mixed-zodiac vs fallback) pending explicit confirmation.

## 2026-03-26 — Milestone B Harsha Bala Resolution

- decision_id: SD-2026-03-26-B1
- scope: Native Harsha Bala rule implementation in annual module (flagged)
- source_of_truth: User-approved Tajika/Varshaphala rule resolution + TECHNICAL_IMPLEMENTATION_AUDIT.md
- accepted_classical_mapping:
  - female_houses: 1,2,3,7,8,9
  - male_houses: 4,5,6,10,11,12
  - sthana_houses: Sun=9, Moon=3, Mars=6, Saturn=12, Mercury=1, Jupiter=11, Venus=5
  - no conditional suppression of Stri-Purusha component
  - no forced reassignment of house 9 to masculine
- implementation_notes:
  - Native Harsha Bala added to varshaphala payload as `harsha_bala.by_planet`.
  - Engine consumes Harsha only when `VE_ENABLE_NATIVE_HARSHA_BALA=1`.
  - Added debug field `harsha_bala_native_2h` in confidence payload.
  - Revised validation logic to treat Sun's classical max as 15 in the stated conflict setup.
- unresolved_gaps:
  - No unresolved rule conflicts for Harsha Bala after this decision.

## 2026-03-26 — Milestone C Tripataki Progression Core

- decision_id: SD-2026-03-26-C1
- scope: Native Tripataki progression + debug integration (no invented vedha geometry)
- source_of_truth: TECHNICAL_IMPLEMENTATION_AUDIT.md + user constraints
- implemented_rules:
  - running_year = completed_years + 1
  - Moon index by modulo 9 (0 remainder uses divisor)
  - Sun/Mercury/Jupiter/Venus/Saturn index by modulo 4 (0 remainder uses divisor)
  - Mars/Rahu/Ketu index by modulo 6 (0 remainder uses divisor)
  - Rahu/Ketu progression direction reverse (negative step)
- implementation_notes:
  - Added `tripataki` payload to annual analysis with `status=progression_only`.
  - Engine flag `VE_ENABLE_TRIPATAKI` now exposes `tripataki_native_2h` debug field.
  - Confidence delta remains 0.0 until explicit vedha-line geometry map is available.
- unresolved_gaps:
  - Full Tripataki vedha-line coordinate map is not present in runtime-native sources.
  - Modifier weighting for benefic/malefic vedha is deferred pending explicit line map.

## 2026-03-26 — Milestone D Pravesha Scaffold

- decision_id: SD-2026-03-26-D1
- scope: Native Pravesha timing scaffold in annual integration path (debug-first)
- source_of_truth: TECHNICAL_IMPLEMENTATION_AUDIT.md + user constraints
- implemented_rules:
  - Use existing native `tithi_pravesh` payload as diagnostic input when flag is enabled.
  - Keep confidence `delta_applied` at 0.0 until school/epoch policy is finalized.
  - Expose calendar basis from feature flag (`sidereal_month` vs `tropical_month`) in debug output.
- implementation_notes:
  - Added backward-compatible aliases in `compute_tithi_pravesh` for existing engine callsites.
  - Added engine debug field `pravesha_native_2h` with status, diagnostic score, basis, and source-gap.
  - No behavior change when flag is OFF (default).
- unresolved_gaps:
  - Tropical-month policy is supported by flag but not finalized as runtime default.
  - Exact iterative epoch solver is not wired in this milestone; scaffold remains diagnostic.

## 2026-03-26 — Milestone E Shodasha Domain Fusion

- decision_id: SD-2026-03-26-E1
- scope: Domain-isolated Shodashavarga quality fusion in annual confidence path
- source_of_truth: Existing native `vimshopak` (Shodashavarga) output + user constraints
- implemented_rules:
  - Use only domain-relevant planets for domain quality average.
  - Compare domain average against chart-wide Vimshopak baseline.
  - Convert relative difference to a bounded annual-score delta (cap ±0.06).
  - Apply only when `VE_ENABLE_SHODASHA_FUSION=1`.
- implementation_notes:
  - Added helper `_compute_shodasha_domain_fusion(...)` in prediction engine.
  - Integrated into Phase 2H as `shodasha_fusion_2h` with debug diagnostics.
  - Default OFF preserves prior behavior unchanged.
- unresolved_gaps:
  - Domain-specific per-varga weighting policy (e.g., D10-heavy for career) is not introduced in this milestone.

## 2026-03-26 — Milestone F Pravesha Precision Solver

- decision_id: SD-2026-03-26-F1
- scope: Implement precise Nakshatra/Yoga Pravesha epoch solver and wire into runtime payload
- source_of_truth: Jyotish implementation brief + existing Swiss Ephemeris bridge in codebase
- implemented_rules:
  - Find tropical Sun sign window for target year.
  - Solve sidereal Moon return root inside that window (Nakshatra Pravesha).
  - Solve sidereal (Sun+Moon) yoga-sum root inside that window (Yoga Pravesha).
  - Return UTC/local epoch with residual angular error and solver status.
- implementation_notes:
  - Added core solver module: `vedic_engine/core/astronomy.py`.
  - Extended `compute_tithi_pravesh` to emit `precise_pravesha` diagnostics.
  - Engine now passes birth context and enables precision solver under `VE_ENABLE_PRAVESHA_TIMING`.
- unresolved_gaps:
  - Dasha Pravesha commencement chart generation and 1/5/9 vs 6/8/12 gating is not implemented in this milestone.
  - Tropical-month default policy remains configurable; default is unchanged.

## 2026-04-14 — Milestone G Dasha Pravesha Gating Integration

- decision_id: SD-2026-04-14-G1
- scope: Native Dasha Pravesha commencement chart analysis and confidence-path gating
- source_of_truth: Jyotish implementation brief (Priority 1) + user request for one-precise-topic continuation
- implemented_rules:
  - Compute active MD/AD commencement charts from Vimshottari bounds.
  - Apply lagna relation mapping from natal lagna:
    - 1/5/9 => support multiplier 1.30
    - 6/8/12 => friction multiplier 0.70
    - others => neutral 1.00
  - Apply conservative additional dampener when active period lord is debilitated in its own Pravesha chart.
  - Aggregate MD/AD effects with configured dasha weights and clamp final multiplier to 0.70..1.30.
- implementation_notes:
  - Added `PredictionEngine._compute_dasha_pravesha_context(...)` and integrated output in dynamic payload.
  - Passed `dasha_pravesha_mult` into `compute_confidence(...)` and applied as multiplicative dasha throttle.
  - Added debug block `confidence["dasha_pravesha"]` for status, multiplier, details, and source-gap.
  - Added regressions: `test_dasha_pravesha_gate.py`, `test_dasha_pravesha_relation.py`, `test_dasha_pravesha_context.py`.
- unresolved_gaps:
  - No unresolved rule conflict for Dasha Pravesha lagna-relation gating after this decision.

## 2026-04-14 — Milestone H Precise Pravesha Anchor Fidelity

- decision_id: SD-2026-04-14-H1
- scope: Ensure precise Nakshatra/Yoga solver path consumes computed natal anchor values directly
- source_of_truth: Jyotish implementation brief mixed-zodiac requirement + runtime audit expectations
- implemented_rules:
  - Use computed natal tropical Sun sign from anchor module for both precise solvers.
  - Use computed natal sidereal Moon longitude for Nakshatra Pravesha solver input.
  - Use computed natal sidereal yoga sum for Yoga Pravesha solver input.
  - Mark `source_scope` as `diagnostic_plus_precise_pravesha_solver` when precision block status is `ok`.
- implementation_notes:
  - Updated `vedic_engine/timing/tithi_pravesh.py` precise path to pass anchor-derived values.
  - Extended `precise_pravesha` payload with anchor diagnostics for moon longitude and yoga sum.
  - Added regression `test_pravesha_anchor_usage.py`.
- unresolved_gaps:
  - Tropical-month runtime default remains configurable and unchanged.

## 2026-04-14 — Milestone I Tripataki Vedha Activation

- decision_id: SD-2026-04-14-I1
- scope: Promote Tripataki from progression-only diagnostics to geometry-backed annual modifier
- source_of_truth: Jyotish implementation brief Rule Set 3 + bundled pyjhora Tripataki line geometry in workspace
- implemented_rules:
  - Keep existing modulo progression logic for Moon/4-group/6-group and reverse node counting.
  - Map annual lagna to Tripataki anchor point a and distribute remaining signs anti-clockwise.
  - Build vedha adjacency from runtime Tripataki line map and evaluate direct vedha on progressed Moon.
  - Score vedha hits by natural benefic/malefic classes and convert to bounded annual delta (cap +/-0.08).
- implementation_notes:
  - Updated `compute_tripataki_progression(...)` to emit `moon_vedha` diagnostics and `vedha_geometry_available=True`.
  - Added `PredictionEngine._compute_tripataki_varsha_delta(...)` and wired Tripataki delta into Phase 2H varshaphala scoring.
  - Added regressions: `test_tripataki_progression.py` updates and `test_tripataki_varsha_modifier.py`.
- unresolved_gaps:
  - No unresolved runtime gap for Tripataki line-map availability after this milestone.

## 2026-04-14 — Milestone J Confidence Arbitration Final Gate

- decision_id: SD-2026-04-14-J1
- scope: Add deterministic contradiction-resolution gate over post-blend confidence
- source_of_truth: Jyotish implementation brief arbitration directive + existing runtime gate semantics
- implemented_rules:
  - Apply final-stage cap logic when gate-state semantics and late-stage score inflation conflict.
  - Enforce hard caps for `PROMISE_FAILED`, softer caps for `DASHA_NOT_CONFIRMED`, and lock-level cap when multi-dasha agreement is below 2.
  - Add contradiction dampeners for KP-vs-transit and Dasha-vs-transit disagreement.
  - Route Bayesian uncertainty and weak Bayesian verdict into bounded caps on final confidence.
- implementation_notes:
  - Added `PredictionEngine._apply_confidence_arbitration_gate(...)`.
  - Added feature flag `VE_ENABLE_CONFIDENCE_ARBITRATION` (default ON) and surfaced it in feature snapshots.
  - Applied arbitration after all major blend modifiers and before narrative/calibration.
  - Added regression file `test_confidence_arbitration_gate.py`.
- unresolved_gaps:
  - Rule coefficients/caps are conservative first-pass defaults and should be tuned with benchmark calibration data.

## 2026-04-14 — Milestone K Domain-Calibrated Arbitration Coefficients

- decision_id: SD-2026-04-14-K1
- scope: Tune arbitration caps/dampeners by domain using historical engine run distributions
- source_of_truth: `full_engine_run_report*.txt` corpus (28 snapshots/domain) + active runtime gate semantics
- implemented_rules:
  - Introduce domain-aware arbitration profiles for career/finance/health/marriage.
  - Apply stricter caps in low-signal domains (finance/marriage) and moderated caps in higher-signal domains (career).
  - Preserve generic fallback profile for unknown domains.
- implementation_notes:
  - Updated `PredictionEngine._apply_confidence_arbitration_gate(...)` with domain profile map.
  - Added calibration snapshot doc: `research_prompts/arbitration_calibration_snapshot_2026-04-14.md`.
  - Added regressions to verify domain-profile behavior and weak-Bayesian cap handling.
- unresolved_gaps:
  - Profiles are calibrated against internal run reports, not real-world outcome-labeled benchmark data.
  - Precedence ordering is still rule-based and may need domain-specific conflict matrices.

## 2026-04-14 — Milestone L Pravesha Default Policy Finalization

- decision_id: SD-2026-04-14-L1
- scope: Finalize runtime default month-basis policy for Pravesha computations
- source_of_truth: Jyotish implementation brief mixed-zodiac directive + existing precision solver architecture
- implemented_rules:
  - Set runtime default of `VE_USE_TROPICAL_MONTH_FOR_PRAVESHA` to ON (tropical-month anchor by default).
  - Keep env override support intact for explicit sidereal-month fallback (`VE_USE_TROPICAL_MONTH_FOR_PRAVESHA=0`).
  - Remove obsolete diagnostic gap text that previously marked tropical-month default as unresolved.
- implementation_notes:
  - Updated engine feature flag default in `vedic_engine/prediction/engine.py`.
  - Updated feature-flag regression expectations and added override-off regression in `test_feature_flags.py`.
  - Pravesha diagnostics now reflect computed status without stale policy-gap text.
- unresolved_gaps:
  - No unresolved default-policy conflict; further work is accuracy benchmarking under both policy modes.
