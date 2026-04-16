# Remaining vs System Architecture vs Code Audit

Date: 2026-04-15  
Scope: Revalidated [remaing.md](remaing.md), [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md), and current implementation under [vedic_engine](vedic_engine).

## Verdict

The previous 2026-03-26 reconciliation is now partially stale. Several items that were marked missing are implemented and integrated after Milestones G-L, while a smaller set of true gaps and runtime-readiness risks remain.

## 1) Resolved Since 2026-03-26

### Annual + Tajika integration
- Tripataki is now native and integrated via annual vedha scoring:
  - [vedic_engine/timing/varshaphala.py](vedic_engine/timing/varshaphala.py)
  - [vedic_engine/prediction/engine.py](vedic_engine/prediction/engine.py)
- Harsha Bala has a native annual path (bridge path remains optional cross-validation):
  - [vedic_engine/timing/varshaphala.py](vedic_engine/timing/varshaphala.py)
  - [vedic_engine/prediction/bridge_integration.py](vedic_engine/prediction/bridge_integration.py)

### Pravesha family
- Precise Nakshatra/Yoga Pravesha solver is implemented and wired:
  - [vedic_engine/core/astronomy.py](vedic_engine/core/astronomy.py)
  - [vedic_engine/timing/tithi_pravesh.py](vedic_engine/timing/tithi_pravesh.py)
- Dasha Pravesha commencement-chart context is integrated into confidence flow:
  - [vedic_engine/prediction/engine.py](vedic_engine/prediction/engine.py)
  - [vedic_engine/prediction/confidence.py](vedic_engine/prediction/confidence.py)

### Confidence architecture
- Deterministic contradiction-resolution arbitration gate is implemented with domain-calibrated profiles:
  - [vedic_engine/prediction/engine.py](vedic_engine/prediction/engine.py)
  - [test_confidence_arbitration_gate.py](test_confidence_arbitration_gate.py)

### Earlier D12 lagna risk (now addressed)
- The conditional dasha path now computes D12 lagna via divisional helper with fallback, rather than blindly mirroring D1 lagna.
  - [vedic_engine/prediction/engine.py](vedic_engine/prediction/engine.py)

### Transit modularization
- Dedicated Moorti Nirnaya computation module is now present and used by transit scoring.
  - [vedic_engine/timing/moorti_nirnaya.py](vedic_engine/timing/moorti_nirnaya.py)
  - [vedic_engine/prediction/transits.py](vedic_engine/prediction/transits.py)
  - [test_moorti_nirnaya.py](test_moorti_nirnaya.py)
- Dedicated Chandravali computation module is now present and used for transit Moon daily-strength payloads.
  - [vedic_engine/timing/chandravali.py](vedic_engine/timing/chandravali.py)
  - [vedic_engine/prediction/transits.py](vedic_engine/prediction/transits.py)
  - [test_chandravali.py](test_chandravali.py)
- Dedicated Latta (planetary kick) computation module is now present and wired into transit diagnostics payloads.
  - [vedic_engine/timing/latta.py](vedic_engine/timing/latta.py)
  - [vedic_engine/prediction/transits.py](vedic_engine/prediction/transits.py)
  - [test_latta.py](test_latta.py)
- Sarvatobhadra/Kota modules are present and integrated into static + dynamic transit evaluation payload generation.
  - [vedic_engine/analysis/sarvatobhadra.py](vedic_engine/analysis/sarvatobhadra.py)
  - [vedic_engine/analysis/kota_chakra.py](vedic_engine/analysis/kota_chakra.py)
  - [vedic_engine/prediction/transits.py](vedic_engine/prediction/transits.py)
  - [vedic_engine/prediction/engine.py](vedic_engine/prediction/engine.py)
- Sanghatta Chakra is now implemented and integrated into static + dynamic transit evaluation plus confidence-path scoring adjustment.
  - [vedic_engine/analysis/sanghatta_chakra.py](vedic_engine/analysis/sanghatta_chakra.py)
  - [vedic_engine/prediction/transits.py](vedic_engine/prediction/transits.py)
  - [vedic_engine/prediction/engine.py](vedic_engine/prediction/engine.py)
  - [test_sanghatta_integration.py](test_sanghatta_integration.py)

## 2) Items Still Genuinely Missing or Partial

- D5, D6, D11 remain absent as core divisional constructors in [vedic_engine/core/divisional.py](vedic_engine/core/divisional.py).
- D81, D108, D144 are not implemented as chart constructors.
- Shodasha fusion is baseline-only; per-domain varga weighting policy remains open.
- Arbitration is rule-calibrated on internal run reports, not outcome-labeled benchmark datasets.

## 3) Runtime-Readiness Risk Watchlist

- Birth time rectification retains explicit not-implemented branches:
  - [vedic_engine/core/btr_montecarlo.py](vedic_engine/core/btr_montecarlo.py)
- ML pipeline still includes scaffold-level not-implemented paths:
  - [vedic_engine/ml/ml_pipeline.py](vedic_engine/ml/ml_pipeline.py)
- Broad exception swallowing remains a partial risk in scoring-critical areas, though key predict-path fallbacks now emit diagnostics:
  - [vedic_engine/prediction/engine.py](vedic_engine/prediction/engine.py) now captures non-fatal fallback warnings under `runtime_warnings` for transit-adjustment, promise-gate, override-gate, and calibration fallbacks.
  - [vedic_engine/prediction/confidence.py](vedic_engine/prediction/confidence.py) now logs D9 and dignity-import fallback diagnostics instead of fully silent pass-throughs.
  - [vedic_engine/bridges/pyjhora_bridge.py](vedic_engine/bridges/pyjhora_bridge.py) now logs panchanga extra-function fallback failures instead of silent suppression.
  - A broader sweep of remaining `except Exception` blocks is still pending.

## 4) Documentation Alignment Notes

- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) required module inventory refresh (old placeholder names vs real file names).
- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) needed explicit post-Milestone-L status notes for Tripataki/Pravesha/arbitration.

## 5) Suggested Next Fixes (Priority)

1. Add per-domain Shodasha varga weighting matrices and regression calibration.
2. Refit arbitration caps and precedence with outcome-labeled benchmarks.
3. Continue replacing remaining broad exception handlers with diagnostics and narrower exception classes.
4. Complete BTR/ML scaffold placeholders or hard-disable those paths in production mode.
