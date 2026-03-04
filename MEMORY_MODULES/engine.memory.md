# Module: engine.py
## Last Updated: 2026-03-02

## PURPOSE
Main prediction pipeline orchestrator for the Vedic astrology engine. Coordinates all submodules to produce a complete natal analysis and domain-specific prediction report. Implements the 4-step pipeline: static analysis → dynamic analysis → domain scoring → confidence.

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

### predict(chart, domain, on_date, static_data) → dict
- **Purpose:** Generate domain-specific prediction for a given date
- **Inputs:** `chart` (VedicChart), `domain` (str), `on_date` (datetime), `static_data` (dict)
- **Returns:** Full prediction report dict with promise, confidence, intervals, windows
- **Called by:** `main.py:main()`
- **Calls:** `get_transit_positions()`, `evaluate_all_transits()`, `get_active_dasha()`, `evaluate_promise()`, `compute_confidence()`, `compute_bayesian_confidence()`, `compute_fuzzy_confidence()`, `calibrate_confidence()`
- **Key logic:**
  - Gets live transit positions for on_date
  - Runs Promise Gate (Stage 1) — aborts if promise_pct < 0.15
  - Computes raw 8-component confidence score
  - Runs Bayesian update (Stage 2) with dasha+transit+KP evidence
  - Runs Fuzzy convergence (Stage 3) for non-linear compounding
  - Applies Double Transit hard gate (Jupiter+Saturn cap at 50% if absent)
  - Applies calibration, returns final report

## IMPORTANT CONSTANTS
- `SIGN_NAMES_LIST` — 12 sign names for display
- `SIGN_LORDS_MAP` — sign index → lord planet name
- `_CAREER_CHECKLIST_AVAILABLE` — feature flag for optional module
- `_MARRIAGE_SYNTHESIS_AVAILABLE` — feature flag for optional module

## DEPENDENCIES
All prediction/, analysis/, strength/, timing/, core/, data/ submodules. This is the top-level orchestrator.

## RECENT CHANGES
- 2026-03-02: Wired karaka_bav_data dict into confidence.py call
- 2026-03-02: Added Longevity guardrails (Alpa/Madhya/Purna bands)
- 2026-03-02: Jaimini scoring wired in (was constant 0.3)
- 2026-03-02: Added Ishta/Kashta Phala, Special Degrees, Bhrigu Bindu, Double Transit gate
