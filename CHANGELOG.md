# CHANGELOG — Vedic Astrology Prediction Engine

## Format: [DATE] [FILE] [TYPE] — [Description]

---

### 2026-03-03 (Phase 5)

2026-03-03 timing/tithi_pravesh.py ADD — Phase 5 File 1a: Luni-Solar Annual Return (Tithi Pravesh), natal tithi angle, iterative solver, weekday lords
2026-03-03 timing/pancha_pakshi.py ADD — Phase 5 File 1b: Five Bird Timing System, 5 birds × 5 activities × day/night sequences, birth bird from nakshatra
2026-03-03 analysis/lal_kitab.py ADD — Phase 5 File 1c: Lal Kitab diagnostics — sleeping planets (4 rules), karmic debts (6 scenarios), varshphal (planet age triggers)
2026-03-03 prashna/prashna_advanced.py ADD — Phase 5 File 2: 5 advanced prashna subsystems — Ashtamangala Enhanced, Aksharachakra (52 letters), Nimitta (15 types), Prashna Timing (hora + sunrise fraction), Trisphutam
2026-03-03 data/validation_data.py ADD — Phase 5 File 3: 10 benchmark charts, BVB marriage parameters (P1–P8), 5 edge case types (rashi sandhi, kala sarpa, neechabhanga, retrograde combustion, nodes in angles)
2026-03-03 data/lookup_tables.py ADD — Phase 5 File 4: Yoni 14×14 matrix, Vashya 5×5 matrix, Bhakoot 12×12 matrix + 6 cancellation rules, Nara Chakra 27-entry body map, 50 Extended Sahams, 16 Tajika Yoga definitions + Deeptamsha, D60 even sign table (60 entries)
2026-03-03 timing/rare_dashas.py ADD — Phase 5 File 5: Mandooka Dasha (eligibility: 4+ planets in Kendras; 12 precomputed sequences; Cardinal=7/Fixed=8/Dual=9 yr), Padanadhamsha Dasha (6 pattern variants by polarity+modality; D9-based duration)
2026-03-03 analysis/advanced_yogas.py ADD — Phase 5 File 6: 20+ new yoga detectors — Kemadruma Bhanga, Chandra-Mangala, Budhaditya filtered (6–14° sweet spot), Dhana Matrix, Chandika, Shankha, Tapasvi, Sharada, Vidya, Jaimini Longevity (Kakshya Vridhi/Hrasa), Foreign (3 types), Bandhana (5 variants), Vehicular, Graha Malika, Parijata, Gauri, Vidyut, Siva, Puskala
2026-03-03 prediction/engine.py ADD — Phase 5 imports: 7 try/except blocks for tithi_pravesh, pancha_pakshi, lal_kitab, prashna_advanced, lookup_tables, rare_dashas, advanced_yogas
2026-03-03 prediction/engine.py ADD — Phase 5 computation blocks (§5.1–5.7) in analyze_static(): tithi_pravesh, pancha_pakshi, lal_kitab, advanced_prashna, nara_chakra+tajika_yoga_defs, rare_dashas, advanced_yogas+jaimini_longevity
2026-03-03 prediction/engine.py ADD — Phase 5 results merged into static["computed"] via **_p5_computed spread (NO prediction logic, pure classical computation) → content40 Exit 0 (CAREER 48.8%, FINANCE 34.6%, MARRIAGE 34.3%, HEALTH 44.1%)

---

### 2026-03-03 (Phase 4)

2026-03-03 analysis/doshas.py ADD — Phase 4 File 1: 13 pure functions — Kala Sarpa (12 variants, partial, cancellation), Manglik (6 houses × 3 lagnas, 13 cancellations), Pitru Dosha (5 triggers, Mahan 1.5×), Combustion (Rx-adjusted orbs), Gandanta (4-tier 10pt), Graha Shanti (Kali Yuga ×4), Agni Vasa, Ashtamangala, Tambula Lagna, Trisphutam, Pushkara Navamsha/Bhaga, Abhijit Nakshatra
2026-03-03 core/varga_interpretations.py ADD — Phase 4 File 2: 10 functions — D60 (60 named deities, saumya/krura), D30 Trimsamsha, Sapta Varga (7-chart weights), Dasha Varga (10-chart weights), Kashinath Hora, D10 career vector, Vargottama check, Varga domain lookup
2026-03-03 analysis/nakshatra_extended.py ADD — Phase 4 File 3: 8 functions — Rajju (5 body parts), Vedha (13 pairs), Stree Deergha, Nadi Dosha Enhanced (6 cancellations), Panchaka, Nakshatra Classification (7 categories), Tarabala Extended (9 categories), Extended Compatibility
2026-03-03 timing/muhurta_extended.py ADD — Phase 4 File 4: ~20 functions — Panchanga Shuddhi (221-point), Hora (Chaldean), Choghadiya (7 types), Abhijit Muhurta, Durmuhurta, Rahu Kaal/Yamagandam/Gulika Kaal, Directional Shoola, Marriage/Griha Pravesh/Business/Travel/Surgery Muhurta checkers
2026-03-03 analysis/medical_extended.py ADD — Phase 4 File 5: 15 functions — Triple Map (12-house organ/dosha/karaka), Drekkana Body Map (36-part), Dasha Disease Patterns, Maraka identification + period assessment, Arishta + cancellation, 7 Disease Yogas, Psychiatric Yogas (Kemadruma/Psychosis/Anxiety), Beeja/Kshetra Sphuta, Gender prediction (Vighati + Sign methods), Decumbiture
2026-03-03 timing/advanced_dashas.py ADD — Phase 4 File 6a: 5 functions — Sudarshana degree balance/sequence/event, Patyayini Dasha (Tajika, Krishamsha→Patyamsha, 8 entities), Ashtaka Dasha (BAV-proportional, SAV_CONSTANT=337)
2026-03-03 analysis/advanced_techniques.py ADD — Phase 4 File 6b: 16+ functions — Bhrigu Sutras (9×12=108 aphorisms), Nadi Amsa (150-part 0.2°), Chaturthamsha D4, 3 Drekkana variants (Parashari/Parivritta/Somnath), Ashtamsha D8, Extended Neechabhanga (Jataka Tatva: Upachaya/D9/Mutual), Saptha Shalaka Vedha, Phala Jyotish (theft/litigation/travel/competition), Jataka Tatva Arishta
2026-03-03 prediction/engine.py ADD — Phase 4 imports: 7 try/except blocks for doshas, varga_interpretations, nakshatra_extended, muhurta_extended, medical_extended, advanced_dashas, advanced_techniques
2026-03-03 prediction/engine.py ADD — Phase 4 computation blocks (§4.1–4.7) in analyze_static(): ~30 calls producing classical analysis results
2026-03-03 prediction/engine.py ADD — Phase 4 results merged into static["computed"] via **_p4_computed spread (NO prediction logic, pure classical computation)

---

### 2026-03-03 (Phase 3)

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
