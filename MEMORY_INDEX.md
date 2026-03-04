# MEMORY INDEX — Vedic Astrology Prediction Engine
> READ THIS FIRST before touching any code. Under 3000 tokens by design.

---

## SECTION A: Architecture Overview

This is a **Vedic astrology prediction engine** that generates domain-specific life predictions (career, marriage, finance, health, etc.) from a birth chart using classical Jyotish rules augmented by probabilistic scoring.

**Entry point:** `main.py` → `PredictionEngine` (in `vedic_engine/prediction/engine.py`)

**3-Stage Pipeline:**
1. **Promise Gate** (`promise.py:evaluate_promise`) — Three Pillar Rule: Bhava + Bhavesha + Karaka must confirm natal potential exists. Returns `promise_pct` (0–1) and `promise_ceiling`. Score < 0.15 → prediction aborted.
2. **Bayesian Posterior** (`bayesian_layer.py:compute_bayesian_confidence`) — Updates Beta(α,β) prior (natal yogas + functional role) with evidence from dasha, transit+BAV, and KP sub-lord. Returns calibrated posterior mean + credible interval.
3. **Fuzzy Convergence** (`fuzzy_confidence.py:compute_fuzzy_confidence`) — 3-input fuzzy inference (timing, transit, structural) that compounds agreement non-linearly. Falls back to linear score if scikit-fuzzy unavailable.

**Raw confidence** (`confidence.py:compute_confidence`) feeds Stages 2 & 3. Final score is calibrated via `calibration.py`.

---

## SECTION B: Module Registry

| File | Purpose | Key Functions | Depends On | Last Modified |
|------|---------|---------------|-----------|--------------|
| `main.py` | CLI entry point; renders full report | `print_static_summary()`, `print_domain_report()`, `main()` | engine.py, loader.py, interpreter.py | 2026-03-02 |
| `vedic_engine/__init__.py` | Package init | — | — | 2026-03-02 |
| `vedic_engine/config.py` | All constants, enums, lookup tables (single source of truth) | Planet, Sign, VIMSHOTTARI_YEARS, SIGN_LORDS, GOCHAR_EFFECTS, VEDHA_TABLE | — | 2026-03-02 |
| **prediction/** | | | | |
| `prediction/engine.py` | Main pipeline orchestrator; builds static + dynamic analysis | `analyze_static()`, `predict()`, `_build_domain_report()` | All submodules | 2026-03-02 |
| `prediction/promise.py` | Three Pillar natal promise evaluation; hard gate | `evaluate_promise()`, `_score_bhava()`, `_score_bhavesha()`, `_score_karaka()` | config.py | 2026-03-02 |
| `prediction/confidence.py` | 8-component weighted confidence scoring | `compute_confidence()`, `score_dasha_alignment()`, `score_transit_support()`, `_tiered_bav()` | config.py | 2026-03-02 |
| `prediction/bayesian_layer.py` | Beta-distribution Bayesian posterior update | `compute_bayesian_confidence()`, `_structural_prior()`, `_dasha_evidence()`, `_transit_evidence()` | — | 2026-03-02 |
| `prediction/fuzzy_confidence.py` | 3-input fuzzy inference via scikit-fuzzy | `compute_fuzzy_confidence()`, `aggregate_for_fuzzy()`, `_build_fuzzy_system()` | scikit-fuzzy (optional) | 2026-03-02 |
| `prediction/transits.py` | Real-time transit positions + Gochar scoring | `get_transit_positions()`, `evaluate_transit()`, `evaluate_all_transits()`, `detect_sade_sati()` | config.py, ashtakvarga.py | 2026-03-02 |
| `prediction/calibration.py` | Maps raw confidence to calibrated Platt-scale score | `calibrate_confidence()` | — | 2026-03-02 |
| `prediction/dasha_transit.py` | Dasha lord transit + ingress calendar | `analyze_dasha_lord_transit()`, `compute_ingress_calendar()` | transits.py, vimshottari.py | 2026-03-02 |
| `prediction/timing_optimizer.py` | Finds best/worst prediction windows | `find_best_windows()`, `find_worst_windows()` | engine.py | 2026-03-02 |
| `prediction/aspect_transits.py` | Transit-to-natal aspect computation | `compute_transit_aspects()`, `compute_natal_activation_score()`, `top_transit_aspects()` | config.py | 2026-03-02 |
| `prediction/ephemeris_audit.py` | Validates ephemeris accuracy | `run_ephemeris_audit()` | transits.py | 2026-03-02 |
| `prediction/skyfield_positions.py` | Skyfield JPL-based planet positions | `get_positions_skyfield()` | skyfield | 2026-03-02 |
| `prediction/astropy_positions.py` | Astropy-based planet positions | `get_positions_astropy()` | astropy | 2026-03-02 |
| **strength/** | | | | |
| `strength/shadbala.py` | Full 6-fold Shadbala computation per planet | `compute_shadbala()`, `compute_all_shadbala()`, `sthana_bala()`, `kala_bala()` | config.py | 2026-03-02 |
| `strength/ashtakvarga.py` | Bhinna + Sarva Ashtakvarga; BAV transit scoring | `compute_full_ashtakvarga()`, `compute_bhinna_ashtakvarga()`, `transit_av_score()`, `domain_specific_bav_score()` | config.py | 2026-03-02 |
| `strength/bhavabala.py` | House strength (Bhava Bala) | `compute_all_bhavabala()`, `bhava_drishti_bala()`, `get_bhavabala_modifier_for_domain()` | shadbala.py | 2026-03-02 |
| `strength/vimshopak.py` | Vimshopaka Bala (divisional dignity score) | `compute_all_vimshopak()`, `compute_vimshopak()`, `compute_shadvarga_vimshopak()` | divisional.py | 2026-03-02 |
| **timing/** | | | | |
| `timing/vimshottari.py` | Vimshottari dasha computation (120-yr cycle) | `compute_mahadasha_periods()`, `get_active_dasha()`, `detect_dasha_sandhi()`, `dasha_diagnostic_matrix()` | config.py | 2026-03-02 |
| `timing/chara_dasha.py` | Jaimini Chara Dasha (sign-based) | `compute_chara_dasha()`, `get_active_chara_dasha()`, `chara_dasha_details_on_date()` | config.py | 2026-03-02 |
| `timing/yogini.py` | Yogini Dasha (36-yr cycle, 8 yoginis) | `compute_yogini_periods()`, `get_active_yogini()` | config.py | 2026-03-02 |
| `timing/ashtottari.py` | Ashtottari Dasha (108-yr, conditional) | `compute_ashtottari_periods()`, `ashtottari_details_on_date()`, `is_ashtottari_eligible()` | config.py | 2026-03-02 |
| `timing/kalachakra.py` | Kalachakra Dasha (nakshatra-pada based) | `compute_kalachakra_dasha()`, `get_active_kalachakra_period()`, `analyze_deha_jeeva_transits()` | config.py | 2026-03-02 |
| `timing/jaimini_dashas.py` | Multiple Jaimini dasha variants | `compute_shoola_dasha()`, `compute_brahma_dasha()`, `compute_sudasa()`, `compute_drig_dasha()` | config.py | 2026-03-02 |
| `timing/conditional_dashas.py` | 8 conditional dasha systems with eligibility checks | `check_all_conditional_eligibility()`, `compute_shodashottari()`, `compute_moola_dasha()` | config.py | 2026-03-02 |
| `timing/varshaphala.py` | Annual solar return (Varshaphala / Tajika) | `compute_varshaphala()`, `compute_varsha_analysis()`, `detect_tajika_yogas()`, `compute_all_sahams()` | config.py | 2026-03-02 |
| `timing/panchanga.py` | Daily Panchanga (Tithi, Vara, Nakshatra, Yoga, Karana) | `compute_panchanga()`, `tithi()`, `vara()`, `nakshatra_info()` | config.py | 2026-03-02 |
| `timing/muhurta.py` | Auspicious timing windows | `find_muhurta_windows()`, `score_window()`, `check_muhurta_date()` | panchanga.py | 2026-03-02 |
| `timing/muhurta_extended.py` | Extended Muhurta: Panchanga Shuddhi, Hora, Choghadiya, Abhijit, inauspicious windows, domain muhurtas | `compute_panchanga_shuddhi()`, `compute_hora()`, `compute_choghadiya()`, `compute_abhijit_muhurta()`, `compute_all_inauspicious_windows()`, `check_marriage_muhurta()`, `check_surgery_muhurta()` | — | 2026-03-03 |
| `timing/advanced_dashas.py` | Sudarshana degree balance, Patyayini Dasha (Tajika), Ashtaka Dasha (BAV-proportional) | `compute_sudarshana_balance()`, `compute_sudarshana_dasha_sequence()`, `compute_patyayini_dasha()`, `compute_ashtaka_dasha()` | — | 2026-03-03 |
| `timing/tithi_pravesh.py` | Luni-Solar Annual Return (Tithi Pravesh) | `compute_natal_tithi_angle()`, `compute_tithi_pravesh()`, `solve_tithi_pravesh_iterative()` | — | 2026-03-03 |
| `timing/pancha_pakshi.py` | Five Bird Timing System | `get_birth_bird()`, `get_current_activity()`, `compute_pancha_pakshi()` | — | 2026-03-03 |
| `timing/rare_dashas.py` | Mandooka Dasha + Padanadhamsha Dasha (2 rare systems) | `check_mandooka_eligible()`, `compute_mandooka_dasha()`, `compute_padanadhamsha_dasha()`, `compute_all_rare_dashas()` | — | 2026-03-03 |
| `timing/kp.py` | KP (Krishnamurti Paddhati) sub-lord system | `get_kp_layers()`, `build_kp_significations()`, `compute_ruling_planets()`, `resolve_prashna_query()` | config.py | 2026-03-02 |
| `timing/progressions.py` | Secondary progressions + solar terms | `compute_secondary_progressions()`, `score_progression_activation()`, `compute_solar_terms()` | — | 2026-03-02 |
| `timing/dasha_quality.py` | Ishta/Kashta Phala + dasha quality scoring | `compute_ishta_kashta()`, `dasha_quality_score()`, `maturity_modifier()` | config.py | 2026-03-02 |
| **analysis/** | | | | |
| `analysis/yogas.py` | ~30+ yoga detectors + compounding logic | `detect_all_yogas()`, `compute_yoga_compounding()`, `compute_dhana_stacking_tier()`, `score_md_ad_relationship()` | config.py, coordinates.py | 2026-03-02 |
| `analysis/karakas.py` | Chara Karaka + karaka relationship analysis | `compute_chara_karakas()`, `analyze_karaka_relationships()` | config.py | 2026-03-02 |
| `analysis/karakamsha.py` | Karakamsha (AK sign in D9) analysis | `compute_karakamsha()` | divisional.py | 2026-03-02 |
| `analysis/functional.py` | Functional benefic/malefic by Lagna | `compute_functional_analysis()` | config.py | 2026-03-02 |
| `analysis/dispositor.py` | Dispositor chain + dasha lord dispositor | `analyze_dasha_lord_dispositor()`, `compute_dispositor_graph()` | config.py | 2026-03-02 |
| `analysis/graha_yuddha.py` | Planetary war (Graha Yuddha) detection + penalties | `detect_planetary_wars()`, `apply_war_penalties()` | config.py | 2026-03-02 |
| `analysis/argala.py` | Argala (intervention/obstruction) system | `compute_all_argala()` | config.py | 2026-03-02 |
| `analysis/arudha_padas.py` | Arudha Pada (AL, A2–A12) computation | `arudha_summary()` | config.py | 2026-03-02 |
| `analysis/rashi_drishti.py` | Rashi (sign) aspect system | `rashi_drishti_summary()` | config.py | 2026-03-02 |
| `analysis/varga_analysis.py` | Multi-divisional chart analysis | `compute_varga_report()` | divisional.py | 2026-03-02 |
| `analysis/nakshatra_analysis.py` | Nakshatra-level analysis | `compute_nakshatra_analysis()` | config.py | 2026-03-02 |
| `analysis/special_points.py` | Tarabala, Chandrabala, special chart points | `compute_all_special_points()`, `compute_tarabala()`, `compute_chandrabala()` | config.py | 2026-03-02 |
| `analysis/special_degrees.py` | Mrityu Bhaga, Gandanta, Pushkara degrees | `compute_special_degrees()` | config.py | 2026-03-02 |
| `analysis/significations.py` | Domain-planet signification mapping | `get_planet_domain_map()` | config.py | 2026-03-02 |
| `analysis/compatibility.py` | Kundli matching (Ashtakoot) | `compute_compatibility()` | config.py | 2026-03-02 |
| `analysis/badhaka.py` | Badhaka (obstructor) analysis | `compute_badhaka()` | config.py | 2026-03-02 |
| `analysis/career_checklist.py` | Comprehensive career domain checklist | `compute_career_checklist()` | yogas.py, shadbala.py | 2026-03-02 |
| `analysis/marriage_synthesis.py` | Marriage readiness + timing synthesis | `compute_marriage_synthesis()` | yogas.py, karakas.py | 2026-03-02 |
| `analysis/medical_astrology.py` | Health domain analysis | `compute_medical_analysis()` | config.py | 2026-03-02 |
| `analysis/doshas.py` | Classical doshas: KSY, Manglik, Pitru, Combustion, Gandanta, Pushkara | `detect_kala_sarpa()`, `detect_manglik_dosha()`, `detect_pitru_dosha()`, `compute_combustion()`, `compute_gandanta_detailed()`, `compute_trisphutam()`, `is_pushkara_navamsha()`, `is_pushkara_bhaga()` | config.py | 2026-03-03 |
| `analysis/nakshatra_extended.py` | Extended nakshatra compatibility | `compute_rajju()`, `check_vedha_nakshatra()`, `compute_stree_deergha()`, `check_nadi_dosha_enhanced()`, `compute_panchaka()`, `get_nakshatra_classification()`, `compute_tarabala_extended()`, `compute_extended_compatibility()` | — | 2026-03-03 |
| `analysis/medical_extended.py` | Advanced medical: Marakas, disease yogas, psychiatric, Beeja/Kshetra | `identify_marakas()`, `assess_maraka_period()`, `detect_arishta_yoga()`, `check_disease_yogas()`, `detect_psychiatric_yogas()`, `compute_beeja_sphuta()`, `compute_kshetra_sphuta()`, `compute_decumbiture_critical_days()` | — | 2026-03-03 |
| `analysis/advanced_techniques.py` | Bhrigu Sutras, Nadi Amsa 150, D4/D8, Drekkana variants, Neechabhanga ext, Saptha Shalaka, Phala Jyotish | `lookup_bhrigu_all_planets()`, `compute_nadi_amsa()`, `compute_chaturthamsha()`, `compute_parashari_drekkana()`, `compute_ashtamsha()`, `check_neechabhanga_extended()`, `check_saptha_shalaka_vedha()`, `check_competition_success()`, `check_jataka_tatva_arishta()` | — | 2026-03-03 |
| `analysis/longevity.py` | Pindayu + Amsayu + Nisargayu + Three Pairs Band | `compute_longevity()`, `compute_pindayu()`, `compute_amsayu()`, `compute_nisargayu()` | config.py | 2026-03-03 |
| `analysis/nadi_amsha.py` | Nadi Amsha (0.2° intervals, 150 per sign) | `compute_nadi_amsha()`, `longitude_to_nadi_amsha()` | — | 2026-03-03 |
| `analysis/sarvatobhadra.py` | SBC 9×9 grid + Vedha ray detection | `construct_sbc_grid()`, `check_sbc_vedha()` | config.py | 2026-03-03 |
| `analysis/kota_chakra.py` | Kota Chakra fortress + transit direction | `compute_kota_chakra()`, `evaluate_kota_transit()`, `compute_kota_status()` | — | 2026-03-03 |
| `timing/sudarshana.py` | Sudarshana Chakra triple-frame eval + Dasha | `evaluate_sudarshana()`, `compute_sudarshana_dasha()`, `evaluate_sudarshana_all_planets()` | — | 2026-03-03 |
| `timing/nadi_timing.py` | Nadi Jyotish timing — BCP, Saturn activation, Patel marriage, BNN graph, spouse sign | `compute_bcp_active_house()`, `check_nadi_saturn_activation()`, `compute_patel_marriage_dates()`, `compute_bnn_graph()`, `compute_all_nadi_signals()` | — | 2026-03-03 |
| `timing/hellenistic.py` | Hellenistic timing — Profections, Sect, Lots, ZR, Midpoints | `compute_annual_profection()`, `compute_hellenistic_sect()`, `compute_lot_of_fortune()`, `compute_zodiacal_releasing()`, `compute_midpoints()`, `compute_all_hellenistic_signals()` | — | 2026-03-03 |
| `prashna/prashna.py` | Prashna horary — 7 sub-modules + 1-108 Kalidas number system | `evaluate_yes_no()`, `evaluate_medical_prashna()`, `evaluate_legal_prashna()`, `compute_prashna_timing()`, `compute_number_prashna()` | — | 2026-03-03 |
| `prashna/prashna_advanced.py` | Advanced Prashna: Ashtamangala Enhanced, Aksharachakra, Nimitta, Prashna Timing, Trisphutam | `compute_all_advanced_prashna()`, `compute_ashtamangala_enhanced()`, `compute_aksharachakra()`, `evaluate_nimitta()`, `compute_advanced_prashna_timing()` | — | 2026-03-03 |
| `mundane/mundane.py` | Mundane — Ingress validity, Eclipse duration-to-impact, Great Conjunction phase, Gann degree | `compute_ingress_validity()`, `compute_eclipse_impact()`, `compute_great_conjunction_phase()`, `compute_gann_price_to_degree()` | — | 2026-03-03 |
| `science/correlations.py` | Scientific hooks — lunar health, birth month disease risk, chronotherapy hora | `compute_lunar_phase()`, `compute_birth_month_risk()`, `compute_hora_chronotherapy()`, `compute_all_science_signals()` | — | 2026-03-03 |
| `analysis/lunations.py` | New/Full Moon + eclipse alerts | `compute_upcoming_lunations()`, `get_eclipse_alerts()`, `get_high_significance_lunations()` | transits.py | 2026-03-02 |
| `analysis/dispositor.py` | Dispositor chain tracing | `compute_dispositor_graph()`, `analyze_dasha_lord_dispositor()` | config.py | 2026-03-02 |
| `analysis/panchadha_maitri.py` | Compound friendship computation | `compute_panchadha_maitri()` | config.py | 2026-03-02 |
| `analysis/lal_kitab.py` | Lal Kitab diagnostics: sleeping planets, karmic debts, varshphal | `detect_sleeping_planets()`, `detect_karmic_debts()`, `compute_lalkitab_varshphal()`, `compute_all_lalkitab()` | — | 2026-03-03 |
| `analysis/advanced_yogas.py` | 20+ new yoga detectors: Kemadruma Bhanga, Chandra-Mangala, Budhaditya filtered, Dhana Matrix, Chandika, Shankha, Tapasvi, Sharada, Vidya, Jaimini Longevity, Foreign, Bandhana (5 variants), Vehicular, Graha Malika, Parijata, Gauri, Vidyut, Siva, Puskala | `compute_all_advanced_yogas()`, `compute_jaimini_longevity()`, `detect_kemadruma_bhanga()`, `detect_dhana_matrix()`, `detect_bandhana_yogas()`, `detect_graha_malika()` | — | 2026-03-03 |
| `analysis/remedial.py` | Remedial measures by planet/domain | `get_remedies()` | config.py | 2026-03-02 |
| `analysis/sthira_karakas.py` | Fixed (Sthira) Karaka assignments | `get_sthira_karaka()` | config.py | 2026-03-02 |
| `analysis/__init__.py` | Package init | — | — | 2026-03-02 |
| **core/** | | | | |
| `core/divisional.py` | All varga chart calculators (D1–D60) | `compute_all_vargas()`, `D9()`, `D10()`, `D7()`, `D4()` | coordinates.py, config.py | 2026-03-02 |
| `core/varga_interpretations.py` | Varga interpretation: D60 deities, D30 rulers, Sapta/Dasha Varga, Kashinath Hora, D10 career, Vargottama | `analyze_d60_full()`, `analyze_d30()`, `compute_all_sapta_varga()`, `compute_all_dasha_varga()`, `analyze_kashinath_hora()`, `is_vargottama()` | divisional.py | 2026-03-03 |
| `core/aspects.py` | Drik Bala (aspectual strength) | `compute_all_drik_bala()`, `get_aspect_map()` | config.py | 2026-03-02 |
| `core/coordinates.py` | Longitude math utilities | `sign_of()`, `nakshatra_of()`, `angular_distance()`, `house_from_moon()`, `normalize()` | — | 2026-03-02 |
| `core/swisseph_bridge.py` | pyswisseph wrapper for ephemeris | `compute_positions_swe()` | pyswisseph | 2026-03-02 |
| `core/jyotishganit_bridge.py` | JyotishGanit library wrapper | — | jyotishganit | 2026-03-02 |
| `core/skyfield_audit.py` | Skyfield position audit tool | `run_skyfield_audit()` | skyfield | 2026-03-02 |
| `core/btr_montecarlo.py` | Birth Time Rectification via Monte Carlo | `run_btr_montecarlo()` | engine.py | 2026-03-02 |
| `core/timezone_utils.py` | Timezone + LMT conversion | `to_utc()`, `local_to_utc()` | pytz | 2026-03-02 |
| `core/sunrise_utils.py` | Sunrise/sunset computation | `get_sunrise()`, `get_sunset()` | — | 2026-03-02 |
| `core/__init__.py` | Package init | — | — | 2026-03-02 |
| **data/** | | | | |
| `data/models.py` | Core dataclasses (VedicChart, BirthInfo, PlanetPosition, etc.) | VedicChart, BirthInfo, PlanetPosition, HouseCusp, DashaPeriod | — | 2026-03-02 |
| `data/loader.py` | JSON/dict chart loader; builds VedicChart | `load_sample_chart()`, `load_from_dict()`, `build_chart_swe()` | models.py, config.py | 2026-03-02 |
| `data/nakshatra_db.py` | Nakshatra metadata + mythology | — | config.py | 2026-03-02 |
| `data/__init__.py` | Package init | — | — | 2026-03-02 |
| `data/validation_data.py` | Benchmark charts (10), BVB marriage params, edge cases (5 types) | `BENCHMARK_CHARTS`, `BVB_MARRIAGE_PARAMETERS`, `EDGE_CASES`, `check_rashi_sandhi()`, `check_kala_sarpa()`, `check_neechabhanga()` | — | 2026-03-03 |
| `data/lookup_tables.py` | Yoni 14×14 + Vashya 5×5 + Bhakoot 12×12 matrices, Nara Chakra, 50 Extended Sahams, 16 Tajika Yoga defs, D60 even sign table | `get_yoni_score()`, `get_vashya_score()`, `get_bhakoot_score()`, `check_surgical_contraindication()`, `compute_extended_saham()`, `compute_all_compatibility()` | — | 2026-03-03 |
| **ai/** | | | | |
| `ai/interpreter.py` | GPT-4o narrative interpreter | `VedicInterpreter.interpret()` | openai | 2026-03-02 |
| `ai/gpt_reasoner.py` | GPT chain-of-thought reasoning | `reason_about_chart()` | openai | 2026-03-02 |
| `ai/agent_swarm.py` | Multi-agent orchestration | `run_agent_swarm()` | openai | 2026-03-02 |
| `ai/__init__.py` | Package init | — | — | 2026-03-02 |
| **ml/** | | | | |
| `ml/ml_pipeline.py` | ML training/inference pipeline | `train_model()`, `predict_ml()` | sklearn | 2026-03-02 |
| `ml/__init__.py` | Package init | — | — | 2026-03-02 |

---

## SECTION C: Data Flow Map

```
main.py:main()
  → loader.py:build_chart_swe() / load_from_dict()   → VedicChart object

  → engine.py:analyze_static(chart)
      → divisional.py:compute_all_vargas()
      → shadbala.py:compute_all_shadbala()
      → ashtakvarga.py:compute_full_ashtakvarga()
      → bhavabala.py:compute_all_bhavabala()
      → vimshopak.py:compute_all_vimshopak()
      → aspects.py:compute_all_drik_bala()
      → yogas.py:detect_all_yogas()
      → karakas.py:compute_chara_karakas()
      → functional.py:compute_functional_analysis()
      → special_points.py:compute_all_special_points()
      → vimshottari.py:compute_mahadasha_periods()
      → kp.py:get_kp_layers()
      → Returns: static_data dict

  → engine.py:predict(chart, domain, on_date)
      → transits.py:get_transit_positions(on_date)
      → transits.py:evaluate_all_transits()
      → vimshottari.py:get_active_dasha()
      → promise.py:evaluate_promise()          ← STAGE 1: Hard gate (min 0.15)
          └─ Returns: {promise_pct, promise_ceiling, pillars}
      → confidence.py:compute_confidence()     ← Raw 8-component score
          └─ score_dasha_alignment() × W_DASHA (0.25)
          └─ score_transit_support() × W_TRANSIT (0.20)
          └─ score_ashtakvarga() × W_ASHTAKVARGA (0.15)
          └─ score_yoga_activation() × W_YOGA (0.13)
          └─ score_kp_confirmation() × W_KP (0.12)
          └─ score_functional_role() × W_FUNCTIONAL (0.08)
          └─ W_HOUSE_LORD = 0.00 (zeroed, counted in Promise)
      → bayesian_layer.py:compute_bayesian_confidence()  ← STAGE 2
          └─ Prior: yoga (55%) + functional (45%)
          └─ Updates: dasha (3 obs), transit+BAV (2 obs), KP (binary 2 obs)
          └─ Returns: {posterior_mean, credible_interval, evidence_weight}
      → fuzzy_confidence.py:compute_fuzzy_confidence()   ← STAGE 3
          └─ Inputs: timing_support, transit_support, structural_support
          └─ Returns: {fuzzy_confidence, verdict, method}
      → calibration.py:calibrate_confidence()
      → Returns: final prediction report dict
```

---

## SECTION D: Constants & Config

| Constant | Value | File:Line | Purpose |
|----------|-------|-----------|---------|
| `W_DASHA` | 0.25 | confidence.py:16 | Vimshottari dasha component weight |
| `W_TRANSIT` | 0.20 | confidence.py:17 | Transit support component weight |
| `W_ASHTAKVARGA` | 0.15 | confidence.py:18 | Natal SAV/BAV component weight |
| `W_YOGA` | 0.13 | confidence.py:19 | Active yoga relevance weight |
| `W_KP` | 0.12 | confidence.py:20 | KP sub-lord confirmation weight |
| `W_FUNCTIONAL` | 0.08 | confidence.py:21 | Functional benefic/malefic weight |
| `W_HOUSE_LORD` | 0.00 | confidence.py:22 | ZEROED — double-counted with Promise |
| `PROMISE_HARD_GATE` | 0.15 | engine.py (check) | Min promise to proceed with prediction |
| `PILLAR_STRENGTH_THRESHOLD` | 0.50 | promise.py:29 | Min score for pillar to be "strong" |
| `DOMAIN_KARAKA_BAV_MAP` | dict | confidence.py:76 | Planet-domain BAV karaka mappings |
| `VIMSHOTTARI_YEARS` | 120-yr cycle | config.py | Planet dasha year assignments |
| `ASHTOTTARI_YEARS` | 108-yr cycle | timing/ashtottari.py | Ashtottari dasha year assignments |
| `SHADBALA_MINIMUMS` | per-planet | config.py | Required Shadbala virupa minimums |
| `COMBUSTION_DEGREES` | per-planet | config.py | Orbs for combustion by planet |
| `VEDHA_TABLE` | 12×n dict | config.py | Vedha obstruction positions |
| `GOCHAR_EFFECTS` | 12-house dict | config.py | Gochar house quality ratings |
| `MANIFESTATION_ZONES` | 0–3.3°,26.7–30° | config.py | High-manifestation degree zones |

---

## SECTION E: Known Issues / TODO

- [x] Avasthas not implemented — DONE Phase 1B (Baladi, Shayanadi, Deeptadi)
- [x] Missing dasha systems — DONE Phase 1C (Yogini, Kalachakra, Narayana, conditional)
- [x] Missing yogas — DONE Phase 1D (Daridra, Aristha, Pravrajya; has_sambandha; grade_yoga; 32 Nabhasa was existing; unified format in static["computed"]["yogas"])
- [x] Ashtakavarga Shodhana reductions — DONE Phase 1C (compute_shodhya_pinda, PAV)
- [ ] Upagrahas (Gulika/Mandi) not computed
- [x] Special Lagnas — DONE Phase 1B (Hora, Ghati, Varnada, Pranapada, Sri Lagna)
- [x] Sahams/Lots — DONE Phase 1B (19 natal sahams in compute_all_special_points)
- [x] Vedha pairs — DONE Phase 1E (check_vedha standalone; VIPAREETA_VEDHA_TABLE; Mercury table fixed)
- [x] Kota Chakra — DONE Phase 1E (compute_kota_chakra, evaluate_kota_transit → static["computed"]["kota_chakra"])
- [x] Sudarshana Chakra — DONE Phase 1E (evaluate_sudarshana_all_planets, compute_sudarshana_dasha → dynamic["sudarshana"])
- [x] SBC grid + Vedha — DONE Phase 1E (construct_sbc_grid, check_sbc_vedha → static["computed"]["sbc_grid"])
- [x] Longevity methods — DONE Phase 1F (Pindayu, Amsayu, Nisargayu, Three Pairs Band → static["computed"]["longevity"])
- [x] Nadi Amsha — DONE Phase 1F (compute_nadi_amsha 0.2°/150 per sign → static["computed"]["nadi_amsha"])
- [x] Functional classification — DONE Phase 1F (verified algorithmic coverage all 12 lagnas in analysis/functional.py)
- [x] KP house groupings — DONE Phase 1F (added career:{yes:[2,6,10,11],no:[5,8,12]} to PRASHNA_HOUSE_ARRAYS)
- [x] Tajika/Varshaphala — already done (timing/varshaphala.py with Muntha, Ithasala, Varsheshvara)
- [x] Phase 4 Classical Doshas — DONE (analysis/doshas.py: KSY, Manglik, Pitru, Combustion, Gandanta, Pushkara)
- [x] Phase 4 Varga Interpretations — DONE (core/varga_interpretations.py: D60, D30, Sapta/Dasha Varga, Kashinath Hora)
- [x] Phase 4 Extended Nakshatra — DONE (analysis/nakshatra_extended.py: Rajju, Vedha, Stree Deergha, Nadi Dosha, Panchaka, Tarabala)
- [x] Phase 4 Muhurta Extended — DONE (timing/muhurta_extended.py: Panchanga Shuddhi, Hora, Choghadiya, Abhijit, all domain muhurtas)
- [x] Phase 4 Medical Extended — DONE (analysis/medical_extended.py: Marakas, Arishta, Disease/Psychiatric Yogas, Beeja/Kshetra)
- [x] Phase 4 Advanced Dashas — DONE (timing/advanced_dashas.py: Sudarshana balance, Patyayini, Ashtaka Dasha)
- [x] Phase 4 Advanced Techniques — DONE (analysis/advanced_techniques.py: Bhrigu Sutras, Nadi Amsa 150, D4/D8, Drekkana variants, Neechabhanga ext, Saptha Shalaka, Phala Jyotish)
- [x] Phase 4 Engine Wiring — DONE (engine.py: 7 import blocks + §4.1–4.7 computation blocks + **_p4_computed spread → content39 Exit 0)
- [x] Phase 5 Tithi Pravesh — DONE (timing/tithi_pravesh.py: Luni-Solar annual return)
- [x] Phase 5 Pancha Pakshi — DONE (timing/pancha_pakshi.py: Five Bird timing system)
- [x] Phase 5 Lal Kitab — DONE (analysis/lal_kitab.py: Sleeping planets, karmic debts, varshphal)
- [x] Phase 5 Advanced Prashna — DONE (prashna/prashna_advanced.py: Ashtamangala Enhanced, Aksharachakra, Nimitta, Timing, Trisphutam)
- [x] Phase 5 Validation Data — DONE (data/validation_data.py: 10 benchmark charts, BVB marriage params, 5 edge case types)
- [x] Phase 5 Lookup Tables — DONE (data/lookup_tables.py: Yoni/Vashya/Bhakoot matrices, Nara Chakra, 50 Sahams, 16 Tajika Yoga defs, D60 even sign)
- [x] Phase 5 Rare Dashas — DONE (timing/rare_dashas.py: Mandooka + Padanadhamsha)
- [x] Phase 5 Advanced Yogas — DONE (analysis/advanced_yogas.py: 20+ new detectors incl. Jaimini Longevity, Foreign, Bandhana, Vehicular, Graha Malika)
- [x] Phase 5 Engine Wiring — DONE (engine.py: 7 import blocks + §5.1–5.7 computation blocks + **_p5_computed spread → content40 Exit 0)
