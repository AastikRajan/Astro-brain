# Full Corpus Implementation Tracker

As of 2026-04-14. Derived from full-corpus audit outputs, implementation brief priorities, and SOURCE_DECISIONS milestones.

## Corpus Scale

- Total files in research_prompts folder: 72
- Main formats: markdown, text, json
- Existing deep corpus audit confirms broad ingestion and topic density in dasha, yoga, transit, and varga domains.

## Canonical Priority Matrix (Implementation Brief -> Runtime Status)

| Feature | Priority in brief | Current status | Notes |
| --- | --- | --- | --- |
| Yoga Pravesha | Priority 1 | Implemented | Precise solver and anchor fidelity are integrated; tropical-month runtime default is finalized (override still supported). |
| Nakshatra Pravesha | Priority 1 | Implemented | Precise mixed-zodiac return logic integrated with finalized tropical-month default policy. |
| Dasha Pravesha | Priority 1 | Implemented | Native commencement-chart gating integrated with bounded multiplier. |
| Tripataki Chakra | Priority 2 | Implemented | Geometry-backed vedha scoring integrated with annual confidence delta. |
| Harsha Bala | Priority 2 | Implemented | Native annual Harsha score is integrated behind flag path and consumed in Phase 2H. |
| Shodasha Varga Fusion | Priority 3 | Partially implemented | Domain-isolated baseline fusion is integrated; per-domain varga policy refinement remains open. |
| Confidence Arbitration | Priority 4 | Partially implemented | Deterministic final arbitration gate is active with domain-aware coefficients calibrated from a 29-report snapshot (R3); structural precedence re-fit is landed, while broader benchmark expansion re-fit remains open. |

## Confirmed Milestones Already Landed

- Milestone B: Harsha Bala native annual path.
- Milestone C: Tripataki progression core.
- Milestone D: Pravesha scaffold.
- Milestone E: Domain-isolated Shodasha fusion baseline.
- Milestone F: Precise Nakshatra/Yoga Pravesha solver path.
- Milestone G: Dasha Pravesha gating integration.
- Milestone H: Pravesha anchor fidelity.
- Milestone I: Tripataki vedha activation.
- Milestone J: Deterministic confidence arbitration final gate.
- Milestone K: Domain-calibrated arbitration coefficients.
- Milestone L: Pravesha tropical-month default policy finalization.

## Open Work Across the Full Deep-Research Corpus

### Critical (Do Next)

1. Confidence arbitration calibration
- Re-fit arbitration coefficients/caps against expanded benchmark datasets beyond the current 29-report snapshot baseline.
- Refine and validate precedence ordering for cross-system conflicts (promise vs dasha vs transit vs annual modifiers) against fresh runs.
- Add domain-specific arbitration thresholds once calibration baselines are finalized.

2. Shodasha domain policy refinement
- Add explicit per-domain varga subsets/weights (career, marriage, progeny, health, finance).
- Add calibration tests to avoid cross-domain signal bleed.

### High Value Expansion (From Batch Research Themes)

3. Missing dasha systems
- Jaimini Chara Dasha full production variant.
- Sudarshana triple-wheel timing convergence logic.
- Ashtottari, Kalachakra, Narayana completion quality checks.

4. Missing yoga families
- Full Neecha Bhanga Raja Yoga conditions and stacking policy.
- Vipareeta Raja Yoga strict handling.
- Parivartana taxonomy and weighting.
- Kartari and expanded wealth-yoga coverage.

5. Varga and strength formalism
- Full Shodasavarga mapping validations.
- Vimshopaka variant tables and strict selection policy.
- Shadbala sub-component consistency checks and threshold policies.

6. Ashtakavarga reductions and timing precision
- Trikona/Ekadhipatya reduction verification and test coverage.
- Kakshya-aware transit modulation where applicable.

### Extended Domains (After Core Stability)

7. Special points and sensitive degrees
- Upagraha pipelines (Mandi, Dhuma, Vyatipata, etc.)
- Bhrigu bindu and advanced trigger points.

8. Cross-tradition and specialized frameworks
- Prashna and Nadi modules only after core arbitration stabilizes.
- Keep these as optional modules with strict isolation from core confidence until validated.

## Recommended Execution Sequence

1. Calibrate confidence arbitration architecture.
2. Refine Shodasha per-domain varga weighting.
3. Add missing dasha systems in order of predictive impact.
4. Expand yoga families with strict test vectors.
5. Add extended/specialized modules behind flags.

## Validation Discipline for Each New Topic

- Add SOURCE_DECISIONS entry with source citations and explicit unresolved gaps.
- Add focused regression tests for both positive and negative cases.
- Add confidence payload diagnostics for every new modifier.
- Keep all new logic feature-flagged until benchmarked.
