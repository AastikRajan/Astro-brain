# Module: engine.py
## Last Updated: 2026-04-15

## PURPOSE
Main prediction pipeline orchestrator for the Vedic astrology engine. Coordinates all submodules to produce a complete natal analysis and domain-specific prediction report. Implements the 4-step pipeline: static analysis → dynamic analysis → domain scoring → confidence + final deterministic arbitration.

## KEY FUNCTIONS

### analyze_static(chart: VedicChart) → dict
- **Purpose:** Compute all chart features that don't change with date (natal analysis)
- **Inputs:** `chart` (VedicChart)
- **Returns:** `static_data` dict with vargas, shadbala, ashtakvarga, yogas, karakas, KP layers, dasha periods
- **Called by:** `main.py:main()`, `predict()`
- **Calls:** `compute_all_vargas()`, `compute_all_shadbala()`, `compute_full_ashtakvarga()`, `detect_all_yogas()`, `compute_chara_karakas()`, `compute_mahadasha_periods()`, `get_kp_layers()`, `compute_all_special_points()`, `compute_all_bhavabala()`
- **Key logic:**
  - Builds planet_lons, planet_signs, planet_houses, retrogrades from chart
  - Computes every divisional chart (D1–D60) via divisional.py
  - Detects all yogas and computes yoga compounding tiers
  - Builds karaka_bav_data dict for domain-specific BAV scoring in confidence.py
  - Wires Ishta/Kashta Phala from dasha_quality.py into static data

### analyze_dynamic(chart: VedicChart, static: dict, on_date: datetime) → dict
- **Purpose:** Compute time-dependent dashas, transits, and annual context for the queried date
- **Inputs:** `chart` (VedicChart), `static` dict, `on_date` (datetime)
- **Returns:** Dynamic dict containing active dashas, transit scores, annual context, dynamic Varshaphala, dynamic Tithi Pravesh, and Dasha Pravesha context
- **Called by:** `predict()`, `full_report()`
- **Calls:** `get_active_dasha()`, `evaluate_all_transits()`, `compute_solar_return()`, `compute_varsha_analysis()`, `compute_tithi_pravesh()`, `_compute_dasha_pravesha_context()`
- **Key logic:**
  - Resolves the active solar-return year for `on_date` before building annual modifiers
  - Recomputes Varshaphala from the SWE solar-return chart instead of reusing natal placeholders
  - Recomputes Tithi Pravesh for the active annual year so annual diagnostics are date-specific
  - Computes MD/AD commencement-chart context and exports bounded `dasha_pravesha` multiplier payload

### predict(chart, domain, on_date, static_data) → dict
- **Purpose:** Generate domain-specific prediction for a given date
- **Inputs:** `chart` (VedicChart), `domain` (str), `on_date` (datetime), `static_data` (dict)
- **Returns:** Full prediction report dict with promise, confidence, intervals, windows
- **Called by:** `main.py:main()`
- **Calls:** `get_transit_positions()`, `evaluate_all_transits()`, `get_active_dasha()`, `evaluate_promise()`, `compute_confidence()`, `compute_bayesian_confidence()`, `compute_fuzzy_confidence()`, `calibrate_confidence()`
- **Key logic:**
  - Gets live transit positions for on_date
  - Prefers dynamic annual payloads (`dynamic["varshaphala"]`, `dynamic["tithi_pravesh"]`) in Phase 2H and report output
  - Pulls `dynamic["dasha_pravesha"]` and passes bounded multiplier into confidence dasha alignment path
  - Maps native Tripataki moon-vedha payload into annual confidence delta when enabled
  - Runs Promise Gate (Stage 1) — aborts if promise_pct < 0.15
  - Computes weighted confidence component stack
  - Runs Bayesian update (Stage 2) with dasha+transit+KP evidence
  - Runs Fuzzy convergence (Stage 3) for non-linear compounding
  - Applies deterministic final arbitration gate (domain-aware caps/dampeners)
  - Enforces structural-first arbitration precedence (promise/dasha lock tiers before contradiction stack)
  - Applies Double Transit hard gate (Jupiter+Saturn cap at 50% if absent)
  - Applies calibration, returns final report

### _apply_confidence_arbitration_gate(confidence) → dict
- **Purpose:** Final deterministic confidence correction layer after all blend/modifier stages
- **Called by:** `predict()` at final confidence stage
- **Key logic:**
  - Applies domain-calibrated profile caps for promise-failed / dasha-not-confirmed / low lock-level states
  - Uses structural-first precedence tiers:
    - `structural_promise`: promise caps only
    - `structural_dasha`: structural + uncertainty checks
    - `full`: structural + contradiction + uncertainty stack
  - Emits arbitration diagnostics payload (`precedence_stage`, `profile_version`, calibration source snapshot)

### _compute_shodasha_domain_fusion(vimshopak_data, domain_planets, domain="generic") → dict
- **Purpose:** Compute bounded Shodasha quality delta with domain-specific varga subsets to reduce cross-domain bleed
- **Called by:** `predict()` Phase 2H annual-layer blend when `VE_ENABLE_SHODASHA_FUSION` is enabled
- **Key logic:**
  - Selects policy varga subset from `_SHODASHA_DOMAIN_VARGA_POLICY` (career/finance/marriage/health/etc.)
  - Uses per-varga Vimshopak breakdown contributions when available; falls back to legacy planet percentage
  - Computes domain policy average vs policy-global average and emits bounded `delta_applied` (±0.06)
  - Returns diagnostics (`policy_vargas`, `policy_global_source`, planets used/total) for auditability

## IMPORTANT CONSTANTS
- `SIGN_NAMES_LIST` — 12 sign names for display
- `SIGN_LORDS_MAP` — sign index → lord planet name
- `_CAREER_CHECKLIST_AVAILABLE` — feature flag for optional module
- `_MARRIAGE_SYNTHESIS_AVAILABLE` — feature flag for optional module

## DEPENDENCIES
All prediction/, analysis/, strength/, timing/, core/, data/ submodules. This is the top-level orchestrator.

## RECENT CHANGES
- 2026-04-15: Arbitration R3 calibration re-fit — domain cap profile refreshed against 29-report snapshot; metadata now points to `arbitration_calibration_snapshot_2026-04-15.md`
- 2026-04-15: Arbitration R2 re-fit — structural-first precedence stages added to `_apply_confidence_arbitration_gate`; non-structural penalties are suppressed in `PROMISE_FAILED` stage and payload now includes calibration metadata
- 2026-04-14: Milestone E refinement — Shodasha fusion now applies domain-specific varga policy (`_SHODASHA_DOMAIN_VARGA_POLICY`) with breakdown-aware scoring fallback
- 2026-04-14: Milestone L finalized `VE_USE_TROPICAL_MONTH_FOR_PRAVESHA` default to ON (override retained)
- 2026-04-14: Milestones J/K added final deterministic `arbitration_gate` with domain-calibrated cap profiles
- 2026-04-14: Milestone I wired Tripataki moon-vedha annual delta into Phase 2H confidence
- 2026-04-14: Milestone G wired Dasha Pravesha commencement-chart multiplier into confidence (`dasha_pravesha_mult`)
- 2026-04-14: Dynamic annual context now resolves the active solar-return year and feeds Phase 2H/report output with date-specific Varshaphala + Tithi Pravesh
- 2026-03-02: Wired karaka_bav_data dict into confidence.py call
- 2026-03-02: Added Longevity guardrails (Alpa/Madhya/Purna bands)
- 2026-03-02: Jaimini scoring wired in (was constant 0.3)
- 2026-03-02: Added Ishta/Kashta Phala, Special Degrees, Bhrigu Bindu, Double Transit gate
