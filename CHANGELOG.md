# CHANGELOG — Vedic Astrology Prediction Engine

## Format: [DATE] [FILE] [TYPE] — [Description]

---

### 2026-03-03

2026-03-03 timing/nadi_timing.py ADD — Phase 3A: BCP active house/planets, Nadi Saturn activation, Patel marriage dates, BNN graph, BNN connectivity scores, spouse career sign
2026-03-03 timing/hellenistic.py ADD — Phase 3B: Annual Profections (one sign/year, time lord), Hellenistic Sect (day=Sun+Jup+Sat; night=Moon+Ven+Mar), Lot of Fortune+Spirit, ZR Spirit+Fortune, Midpoints
2026-03-03 prashna/prashna.py ADD — Phase 3C: 7 Prashna sub-modules (YES/NO Ithasala/Ishrafa, Lost Object, Medical Tridosha, Legal, Travel, Pregnancy, Timing Matrix) + 1-108 Kalidas number system
2026-03-03 prashna/__init__.py ADD — Phase 3C: Package init
2026-03-03 mundane/mundane.py ADD — Phase 3D: Ingress validity (Fixed=1/Mutable=2/Cardinal=4 charts), Eclipse duration→impact, Great Conjunction 2020 Air epoch phase, Gann price-to-degree
2026-03-03 mundane/__init__.py ADD — Phase 3D: Package init
2026-03-03 science/correlations.py ADD — Phase 3E: Lunar phase health modifier (δ-wave/melatonin; −0.03 at Full Moon), Birth month disease risk (schizophrenia/MS/atopy RR curves), Chronotherapy hora hook (Chaldean hours → circadian phase)
2026-03-03 science/__init__.py ADD — Phase 3E: Package init
2026-03-03 prediction/engine.py WIRE — Phase 3F.1: BCP+Profection+ZR Spirit boolean signals appended to _dasha_signals convergence list
2026-03-03 prediction/engine.py WIRE — Phase 3F.2: Nadi Saturn activation +10% net_score boost in 2I/2K transit second-pass loop
2026-03-03 prediction/engine.py WIRE — Phase 3F.3: Hellenistic Sect in-sect domain planet bonus (+5% per planet, cap 10%) → confidence["overall_boosted"]
2026-03-03 prediction/engine.py WIRE — Phase 3F.4: Lunar phase health modifier (cos formula, ±3%) → confidence["overall_boosted"] for health domain only
2026-03-03 prediction/engine.py ADD — Phase 3F imports: try-import blocks for nadi_timing, hellenistic, science.correlations (graceful fallback if missing)
2026-03-03 prediction/engine.py ADD — Phase 3 computation blocks in analyze_static(): _nadi_3a, _hellen_3b, _sci_3e; expanded static["computed"] with 15 new keys

---

### 2026-03-02

2026-03-02 confidence.py ADD — Karaka-specific BAV 3-signal blend (40% SAV + 35% karaka BAV + 25% dasha BAV)
2026-03-02 confidence.py ADD — DOMAIN_KARAKA_BAV_MAP with classical planet-house mappings per domain (career/finance/marriage/health)
2026-03-02 confidence.py REFACTOR — Extracted shared _tiered_bav() helper (used by SAV and individual planet BAV scoring)
2026-03-02 confidence.py REMOVE — W_HOUSE_LORD set to 0.00 in all gate states (was double-counting with Promise gate) → affects bayesian_layer.py prior
2026-03-02 confidence.py REFACTOR — W_DASHA: 0.30 → 0.25, W_TRANSIT: 0.22 → 0.20 (weight redistributed after BAV karaka addition)
2026-03-02 bayesian_layer.py FIX — Dasha↔transit overlap detection; merges to single update when same planet triggers both
2026-03-02 bayesian_layer.py REFACTOR — Removed house_lord_strength from _structural_prior() (was double-counting §9.3); prior now yoga 55% + functional 45%
2026-03-02 engine.py WIRE — Builds karaka_bav_data dict, injects dasha_planet + strong_transit_planets into confidence call
2026-03-02 engine.py ADD — Longevity guardrails (Alpa/Madhya/Purna ayur bands) based on lagna lord + moon + sun strength
2026-03-02 engine.py ADD — Jaimini scoring wired into prediction pipeline (was hardcoded 0.3 placeholder)
2026-03-02 engine.py ADD — Ishta/Kashta Phala for dasha quality fed into bayesian prior
2026-03-02 engine.py ADD — Special Degrees computation (Mrityu Bhaga, Gandanta, Pushkara) in static analysis
2026-03-02 engine.py ADD — Bhrigu Bindu transit activation check
2026-03-02 engine.py ADD — Double Transit hard gate (Jupiter+Saturn both transiting relevant house) caps ceiling at 50% if absent
2026-03-02 timing/chara_dasha.py ADD — Full Chara Dasha computation + chara_dasha_details_on_date() wired into engine
2026-03-02 timing/ashtottari.py ADD — Eligibility check (is_ashtottari_eligible) + full period computation
2026-03-02 timing/kalachakra.py ADD — Kalachakra Dasha computation with Deha/Jeeva transit analysis
2026-03-02 timing/jaimini_dashas.py ADD — Shoola, Brahma, Sudasa, Drig, Trikona dasha systems
2026-03-02 timing/conditional_dashas.py ADD — 8 conditional dasha systems with eligibility checks
2026-03-02 timing/varshaphala.py ADD — Full Tajika Varshaphala: Muntha, Varshesha, PVB, Mudda Dasha, all Tajika yogas, Sahams
2026-03-02 analysis/arudha_padas.py ADD — Full Arudha Pada (AL, A2–A12) computation with arudha_summary()
2026-03-02 analysis/rashi_drishti.py ADD — Rashi (sign) aspect system with rashi_drishti_summary()
2026-03-02 analysis/career_checklist.py ADD — Comprehensive domain-specific career checklist (compute_career_checklist)
2026-03-02 analysis/marriage_synthesis.py ADD — Marriage readiness synthesis + timing computation
2026-03-02 analysis/special_degrees.py ADD — Mrityu Bhaga, Gandanta, Pushkara detection
2026-03-02 analysis/argala.py ADD — Argala (intervention/obstruction) analysis (compute_all_argala)
2026-03-02 analysis/badhaka.py ADD — Badhaka obstruction analysis
2026-03-02 prediction/aspect_transits.py ADD — Transit-to-natal aspect scoring (compute_transit_aspects, compute_natal_activation_score)
2026-03-02 prediction/fuzzy_confidence.py ADD — scikit-fuzzy 3-input inference system for non-linear convergence scoring
2026-03-02 timing/progressions.py ADD — Secondary progressions + solar terms computation
2026-03-02 core/swisseph_bridge.py ADD — pyswisseph bridge for Swiss Ephemeris positions
2026-03-02 core/btr_montecarlo.py ADD — Birth Time Rectification Monte Carlo simulation
2026-03-02 config.py FIX — SAPTAVARGAJA_SCORES: EXALTED 45→30, GREAT_FRIEND 22.5→20, NEUTRAL 7.5→10, ENEMY 3.75→4, GREAT_ENEMY 1.875→2, DEBILITATED 0→2 (Research File 1 bypass rules)
2026-03-02 shadbala.py FIX — ojhayugma_bala: Mercury+Saturn return 0.0 (neutral planets have no odd-sign bonus)
2026-03-02 shadbala.py FIX — paksha_bala: Moon output ×2 (BPHS doubling; max 120 virupas)
2026-03-02 shadbala.py FIX — hora_bala: proportional unequal temporal horas using day_dur/12 and night_dur/12; sunset_hour param added
2026-03-02 shadbala.py REWRITE — ayana_bala: per-planet tropical declination; north-strong vs south-strong per BPHS; Mercury=abs(dec); Sun doubled; planet_trop_lon param
2026-03-02 shadbala.py REWRITE — cheshta_bala: Seeghrocha circular-mean formula as primary; speed-state as fallback; true_lon param; Sun+Moon return 0.0 (caller overrides)
2026-03-02 shadbala.py ADD — compute_yuddha_adjustments: Planetary War Bimba Parimana mass-transfer ±delta per combatant pair
2026-03-02 shadbala.py ADD — _SEEGHROCHA, _BIMBA_PARIMANA module-level dicts for Cheshta+Yuddha Bala
2026-03-02 shadbala.py UPDATE — compute_shadbala: Sun Cheshta→Ayana; Moon Cheshta→Paksha; planet_trop_lon + yuddha_adjustment params wired
2026-03-02 shadbala.py UPDATE — compute_all_shadbala: computes tropical lons via get_ayanamsa(); pre-computes Yuddha adjustments; passes both to each planet
2026-03-02 AUDIT — bhavabala.py: Bhavabala formula verified CORRECT (Bhavadhipati+Dig+Drishti; occupant mods; tier thresholds per Research Brief)
2026-03-02 AUDIT — dasha_quality.py: Ishta/Kashta formula verified CORRECT (√(U×C) / √((60-U)×(60-C)); classical BPHS)
2026-03-02 AUDIT — shadbala.py minimums: SHADBALA_MINIMUMS verified CORRECT (Sun=6.5,Moon=6.0,Mars=5.0,Mer=7.0,Jup=6.5,Ven=5.5,Sat=5.0 Rupas)
2026-03-02 ml/ml_pipeline.py ADD — ML training/inference pipeline scaffold2026-03-02 analysis/avasthas.py ADD — Phase 1B: New module — Baladi (5-state 6°-segment), Shayanadi (12-state formula), Deeptadi (9-state dignity hierarchy) avastha systems
2026-03-02 analysis/special_points.py FIX — hora_lagna + ghati_lagna: anchor changed from lagna_lon to sun_lon (Research File 2 — Sun-anchored formulas)
2026-03-02 analysis/special_points.py ADD — compute_varnada_lagna: sign-parity vector algorithm (ODD forward from Aries, EVEN backward from Pisces)
2026-03-02 analysis/special_points.py ADD — compute_pranapada_lagna: Vighati-since-sunrise formula with Sun-modality base points
2026-03-02 analysis/special_points.py ADD — compute_sri_lagna: fractional Moon nakshatra traversal × 360° + lagna
2026-03-02 analysis/special_points.py ADD — compute_natal_sahams: 19 classical Arabic Parts with full day/night reversal logic
2026-03-02 analysis/special_points.py UPDATE — compute_all_special_points: new params (planet_lons, house_cusps, lagna_lord_lon, is_daytime); calls all new special lagnas + natal sahams
2026-03-02 prediction/engine.py ADD — avasthas import + compute_all_avasthas call in analyze_static(); results stored under "avasthas" key
2026-03-02 prediction/engine.py UPDATE — compute_all_special_points call: added planet_lons, house_cusps, lagna_lord_lon, is_daytime params2026-03-02 config.py FIX -- RASHI_MULTIPLIERS[Virgo]: 8 -> 5 (Research File 5 canonical value)
2026-03-02 strength/ashtakvarga.py ADD -- compute_shodhya_pinda (Rashi Pinda + Graha Pinda, correct BPHS formula)
2026-03-02 strength/ashtakvarga.py ADD -- compute_prastharashtakavarga: full PAV 8-contributor x 12-sign matrix (_PAV_TABLES from Research File 5)
2026-03-02 strength/ashtakvarga.py ADD -- kakshya_lord_of_degree utility (3.75 deg intervals)
2026-03-02 strength/ashtakvarga.py UPDATE -- compute_full_ashtakvarga: returns shodhya_pinda + pav keys
2026-03-02 timing/jaimini_dashas.py ADD -- compute_narayana_dasha: Jaimini sign-based dasha (6-rule start, modality sequence, Saturn/Ketu overrides)
2026-03-02 timing/jaimini_dashas.py ADD -- get_active_narayana: active period finder
2026-03-02 prediction/engine.py ADD -- narayana_dasha wired in jaimini_extended dict
2026-03-02 analysis/yogas.py ADD -- has_sambandha(): conjunction + mutual aspect + parivartana relation check (Phase 1D.1)
2026-03-02 analysis/yogas.py ADD -- grade_yoga(): universal S/A/B/C tier grader with score 1.0/0.75/0.5/0.25 (Phase 1D.2)
2026-03-02 analysis/yogas.py ADD -- _daridra_yogas(): L11/L2 in dusthana + Kemadruma Daridra; Viparita override (Phase 1D.4)
2026-03-02 analysis/yogas.py ADD -- _aristha_yogas(): Balarishta (Moon+node, Moon+dusthana+malefic, luminaries+node); Bhanga cancellation (Phase 1D.5)
2026-03-02 analysis/yogas.py ADD -- _pravrajya_yogas(): 4+ planets in sign; flavored by highest Shadbala; Ketu 12th trigger; combust cancel (Phase 1D.8)
2026-03-02 analysis/yogas.py ADD -- compute_all_extended_yogas(): unified List[Dict] output with name/type/planets/grade/score/domain/active/cancellation (Phase 1D.9)
2026-03-02 prediction/engine.py ADD -- compute_all_extended_yogas imported; called after detect_all_yogas; stored in static["computed"]["yogas"] (Phase 1D.9)
