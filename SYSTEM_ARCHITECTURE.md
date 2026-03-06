# Vedic Astrology Prediction Engine — System Architecture

> **Purpose**: Complete reference for anyone to understand the full system — all inputs, outputs, weights, scales, wiring, categories, and data flow. Read this to build a mental map for debugging, extending, or auditing any layer.

---

## Table of Contents

1. [High-Level Pipeline](#1-high-level-pipeline)
2. [Input Requirements](#2-input-requirements)
3. [Domain System](#3-domain-system)
4. [Stage 1: Static Analysis](#4-stage-1-static-analysis)
5. [Stage 2: Dynamic Analysis](#5-stage-2-dynamic-analysis)
6. [Stage 3: Prediction Scoring](#6-stage-3-prediction-scoring)
7. [Confidence Architecture](#7-confidence-architecture)
8. [Post-Confidence Modifiers](#8-post-confidence-modifiers)
9. [Calibration Layer](#9-calibration-layer)
10. [Bridge System (External Validation)](#10-bridge-system)
11. [AI Layer](#11-ai-layer)
12. [Module Inventory](#12-module-inventory)
13. [Weight Reference Table](#13-weight-reference-table)
14. [Output Structure](#14-output-structure)

---

## 1. High-Level Pipeline

```
Birth Data (date, time, lat, lon, tz)
          │
          ▼
   ┌──────────────┐
   │ VedicChart    │  ← SwissEph (Lahiri ayanamsa, <0.001° accuracy)
   │ Construction  │     Planets: lon, sign, house, retrograde
   └──────┬───────┘     Houses: Placidus cusps
          │
          ▼
   ┌──────────────┐
   │  STAGE 1     │  ← ALL date-independent calculations
   │  analyze_    │     ~60 modules, ~150 computed features
   │  static()    │     Runs ONCE per chart
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  STAGE 2     │  ← Date-dependent calculations
   │  analyze_    │     Dashas, transits, progressions
   │  dynamic()   │     Runs PER prediction date
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  STAGE 3     │  ← Domain-specific scoring
   │  predict()   │     Gates → Confidence → Modifiers → Blend
   │              │     Runs PER domain (career/finance/marriage/health)
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  STAGE 4     │  ← Raw score → calibrated probability
   │  calibrate() │     Isotonic regression, reliability band
   └──────┬───────┘
          │
          ▼
   Final Report (JSON dict with ~40 top-level keys)
```

---

## 2. Input Requirements

| Field | Type | Example | Used By |
|-------|------|---------|---------|
| Date of Birth | `YYYY-MM-DD` | `1889-11-14` | SwissEph, all dashas |
| Time of Birth | `HH:MM:SS` | `23:11:00` | Lagna, house cusps, divisional charts |
| Latitude | float | `25.4358` | House system, sunrise, daytime |
| Longitude | float | `81.8463` | House system, ayanamsa |
| Timezone | float (hours) | `5.5` | UTC conversion |
| Domain | string | `"career"` | Which life area to predict |
| Prediction Date | datetime | `2024-01-01` | Transit positions, dasha activation |

---

## 3. Domain System

### 3.1 Domain Houses (which houses matter for each domain)

| Domain | Primary Houses | Negator Houses | Domain Planets |
|--------|---------------|----------------|----------------|
| **Career** | 2, 6, 10, 11 | 8, 12 | SUN, SATURN, MERCURY, JUPITER |
| **Finance** | 2, 6, 11 | 8, 12 | JUPITER, VENUS, MERCURY |
| **Marriage** | 2, 7, 11 | 6, 8, 12 | VENUS, JUPITER, MOON |
| **Health** | 1, 6, 8, 12 | — | SUN, MOON, MARS |
| Children | 2, 5 | 6, 8 | JUPITER |
| Property | 4 | 6, 8 | MARS, VENUS |
| Spiritual | 5, 9, 12 | — | KETU, JUPITER |
| Travel | 3, 9, 12 | — | RAHU, JUPITER |

### 3.2 Domain Configuration (DOMAIN_CONFIG)

Each domain has:

| Setting | Career | Finance | Marriage | Health |
|---------|--------|---------|----------|--------|
| **Primary House** | 10 | 11 | 7 | 1 |
| **Karaka** (significator) | SATURN | JUPITER | VENUS | SUN |
| **House Lord Key** | 10th lord | 11th lord | 7th lord | 1st lord |
| **Key Divisional** | D10 | D2 | D9 | D30 |
| **KP Cusp** | 10 | 11 | 7 | 1 |
| **Yoga Tags** | raja, mahapurusha | dhana, wealth, lakshmi | marriage, kalatra | health, longevity, aristha |

### 3.3 Domain Signal Weights (DOMAIN_SIGNALS)

Top 5 primary signals per domain (weight scale 1–10):

**Career:**
| Signal | Weight |
|--------|--------|
| KP Sublord 10th | 10.0 |
| D10 10th Lord | 9.5 |
| Vimshottari Dasha 10th | 9.0 |
| D10 10th House Lord | 8.5 |
| Double Transit 10+1 | 8.0 |

**Finance:**
| Signal | Weight |
|--------|--------|
| 11th Lord | 10.0 |
| 2nd Lord | 9.5 |
| SAV at 11th & 2nd | 9.0 |
| Dasha Dhana Activation | 8.5 |
| D2 Hora Dignity | 8.0 |

**Marriage:**
| Signal | Weight |
|--------|--------|
| BVB MD-AD 1-7 | 10.0 |
| D9 7th House Lord | 10.0 |
| BVB Lagna 7th Lord | 9.8 |
| Chara Dasha DK-UL | 9.6 |
| Upapada Lagna | 9.0 |

**Health:**
| Signal | Weight |
|--------|--------|
| Lagna Lord | 10.0 |
| Dasha 6-8-12 | 9.5 |
| D30 Trimsamsha | 9.0 |
| Moon Dignity | 8.5 |
| Maraka Lord Dasha | 8.0 |

---

## 4. Stage 1: Static Analysis (`analyze_static()`)

All computations that depend only on the birth chart, NOT on any prediction date. Runs once per chart. Returns a dict with ~30 top-level keys.

### Phase 1: Core Computations

| Module | What It Computes | Input | Output Scale | Key |
|--------|-----------------|-------|-------------|-----|
| **SwissEph Bridge** | Planet positions | Birth data → pyswisseph | Degrees (0–360) | Lahiri ayanamsa |
| **Divisional Charts** | Planet signs in D1–D60 | Longitude | Sign index (0–11) | D9: Fire→Aries, Earth→Capricorn, Air→Libra, Water→Cancer. D30 (BPHS): Odd=Mars(5°)→Saturn(5°)→Jupiter(8°)→Mercury(7°)→Venus(5°); Even=Venus(5°)→Mercury(7°)→Jupiter(8°)→Saturn(5°)→Mars(5°). |
| **Aspects** | Planet-to-planet aspects (all 9 grahas) | House numbers | Shashtiamsas (0–60) | All 9 planets cast 7th=60; Mars 4/8=45, Jupiter 5/9=30, Saturn 3/10=15. Rahu/Ketu: standard 7th aspect only (malefic). |
| **Shadbala** | 6-fold planet strength | Planets + cusps + birth DT | Rupas (total/60) | 6 components: Sthana, Dig, Kala, Cheshta, Naisargika, Drik |
| **Ashtakvarga** | Bindu points per sign | Planet signs + lagna | 0–8 per sign, SAV total=337 | BAV per planet + SAV + Shodhana + Pinda |
| **Bhavabala** | House strength | Lagna + Shadbala + houses | Rupas | >8=Strong, 6.5–7.5=Avg, <6=Weak |
| **Vimshopak** | Multi-varga dignity | Longitudes | 0–20 score | 15–20=HIGH, 10–15=AVG, <10=LOW |
| **Yogas** | Planetary combinations | Houses + lons + aspects | YogaResult objects | ~30 classical yogas, graded S/A/B/C |
| **Extended Yogas** | Graded yoga system | Same + more context | Dict with grade, score, domain | Replaces basic yogas with domain tags |
| **KP Sublord** | 4-layer lord chain | Longitude | {rashi, nakshatra, sub, sub-sub} lord | Signification = union of all houses |
| **Functional Analysis** | Benefic/malefic per lagna | Lagna sign | Role + score (-1 to +2) | Yogakaraka, benefic, malefic, maraka, badhaka |
| **Karakas** | Chara (variable) karakas | Planet degrees | AK, AmK, BK, MK, PK, GnK, DK | Highest degree = Atmakaraka. Tie-breaking: natural planet order (Sun > Moon > Mars > ... > Saturn > Rahu). |
| **Bhava Chalit Shifts** | Rashi vs Chalit house comparison | Planet lons + cusp lons | List of shifted planets | Detects planets occupying different houses in Rashi vs Placidus cusp chart |
| **Arudha Padas** | Jaimini pada system | Lagna + signs | A1–A12 sign indices | A10=career, A7=marriage, A2=finance |

### Phase 2: Jaimini Extended (File 4)

| Sub-Module | Output |
|------------|--------|
| Sthira Karakas | Fixed significators |
| Karakamsha | AK in D9 — analysis of house placements |
| Svamsha | AK's D9 sign characteristics |
| Jaimini Yogas | Sign-based yoga combinations |
| Arudha Extended | Bhava + Argala from Arudha |
| 7 Jaimini Dashas | Shoola, Niryana Shoola, Brahma, Navamsha, Sudasa, Drig, Trikona |
| Narayana Dasha | Sign-based timing (replaces Chara for some lagnas) |

### Phase 3A: Nadi Jyotish Timing

| Signal | What |
|--------|------|
| BCP Active House | Bhrigu Chakra Paddati position |
| Nadi Saturn Activated Planets | Planets energized by Saturn's cycle |
| Patel Marriage Candidates | Marriage timing per Patel system |
| BNN Graph | Bhrigu Nandi Nadi connectivity |
| Spouse Career Sign | 7th-from-7th analysis |

### Phase 3B: Hellenistic Signals

| Signal | What |
|--------|------|
| Annual Profection | Time Lord for current year |
| Hellenistic Sect | Day/night chart → sect benefics |
| Lot of Fortune/Spirit | Arabic Parts calculation |
| Zodiacal Releasing | Spirit & Fortune releasing periods |
| Midpoints | Planet-pair midpoint analysis |

### Phase 4: Doshas & Advanced

| Dosha | Detection | Impact |
|-------|-----------|--------|
| **Kala Sarpa** | All 7 planets between Rahu-Ketu | 12 variants (Anant to Sheshnag), partial if orb>5° |
| **Manglik** | Mars in 1/2/4/7/8/12 from Lagna/Moon/Venus | Severity 0–3, cancellation rules |
| **Pitru Dosha** | Sun-Saturn-Rahu in 9th house combinations | Ancestral karma marker |
| **Combustion** | Planet within X° of Sun | Planet energy absorbed |
| **Gandanta** | Planet at water-fire sign junction | Karmic knot, 3 zones |

**Advanced Techniques (Phase 4.2–4.7):**
- D60/D30 analysis, Sapta/Dasha Varga, Kashinath Hora, Vargottama status
- Nakshatra classification, Tarabala, Panchaka
- Panchanga Shuddhi, Tithi/Vara classification
- Medical: Marakas, Arishta Yoga, Disease Yogas, Psychiatric Yogas, Beeja/Kshetra Sphuta
- Sudarshana balance, Patyayini Dasha, Ashtaka Dasha
- Bhrigu Sutras, Nadi Amsa 150, Chaturthamsha, Drekkana variants, Ashtamsha
- Neechabhanga Extended, Saptha Shalaka Vedha, Competition, Travel, Theft analysis

### Phase 5: Final Static Modules

- Tithi Pravesh (solar return)
- Pancha Pakshi (bird system)
- Lal Kitab
- Advanced Prashna (horary)
- Compatibility Lookup Tables (Nara Chakra, Tajika Yoga defs)
- Rare Dashas (Mandooka, Padanadhamsha)
- Advanced Yogas, Jaimini Longevity
- Kota Chakra, SBC Grid

### Phase 6: External Bridges (runs in `analyze_static`)

| Bridge | Positioning | Reason |
|--------|------------|--------|
| **PyJHora** | TOP of analyze_static (before any SWE call) | Avoids ayanamsa state conflict with SwissEph |
| **VedAstro** | END of analyze_static | API call, no state conflict |

Both bridge outputs are stored in `static["computed"]["pyjhora"]` and `static["computed"]["vedastro"]`.

---

## 5. Stage 2: Dynamic Analysis (`analyze_dynamic()`)

Date-dependent calculations. Runs per prediction date.

| Module | Input | Output | Key |
|--------|-------|--------|-----|
| **Vimshottari Dasha** | Moon lon + birth date, 3 levels | Active MD/AD/PD + sandhi | 120-year cycle, Ketu(7)→Venus(20)→...Mercury(17) |
| **Dasha Diagnostic Matrix** | Active dasha lords + chart | 6-factor analysis | House, combust, retrograde, dignity |
| **Ashtottari Dasha** | Moon + lagna + Rahu position | Active MD/AD (if eligible) | 108-year cycle, 8 planets (no Ketu) |
| **Yogini Dasha** | Moon lon + birth date | Active Yogini + planet | 36-year cycle, 8 Yoginis |
| **Transit Positions** | Prediction date | All planet longitudes | pyswisseph real-time |
| **Transit Evaluation** | Transits + natal Moon + BAV | Per-planet Gochar scores | Favorable/unfavorable + Vedha blocking |
| **Sudarshana Chakra** | Transit signs + 3 lagnas | Triple-frame eval per planet | Lagna/Moon/Sun reference frames |
| **Sade Sati** | Saturn transit sign vs Moon sign | Active/phase/intensity | Saturn in 12th/1st/2nd from Moon |
| **Chara Dasha** | Lagna + signs + lons + karakas | Active Chara sign + enrichment | Jaimini sign-based, forward/backward |
| **Dasha-Transit Interaction** | MD/AD lords + transit positions | Double transit, activation | Lord transit through natal houses |
| **Transit Aspects** | Transit lons + natal lons | Continuous orb weights | Applying vs separating |
| **Progressions** | Birth DT + analysis date | Secondary + Solar Arc | Day-for-year symbolic chart |
| **Panchanga** | Sun/Moon transit | Tithi, Nakshatra, Yoga, Karana, Vara | 5 limbs of Vedic calendar |
| **Ruling Planets** | Moon + Lagna at query time | KP ruling planet set | Current moment significators |

---

## 6. Stage 3: Prediction Scoring (`predict()`)

This is the core scoring pipeline. For a given domain + date, it produces the final confidence score.

### 6.1 Data Gathering

```
predict(chart, domain="career", on_date=now)
  │
  ├── static = analyze_static(chart)       ← if not provided
  ├── dynamic = analyze_dynamic(chart, static, on_date)
  │
  ├── Extract active dasha lords (MD, AD)
  ├── Extract yogini lord
  ├── Extract AV data (SAV, BAV, dasha planet BAV)
  ├── Build karaka-BAV data bundle
  ├── Compute domain houses, negator houses, domain planets
  └── Compute relevant signs from lagna
```

### 6.2 Transit Adjustment Pipeline

```
Raw Transit Scores
       │
       ▼
  Phase 2C: Vedha Nullification
       │  Favorable transit blocked by Vedha → 80% reduction
       │  Unfavorable transit + Vipareeta Vedha → lift to 0.50
       ▼
  Phase 2D: Sudarshana Blend
       │  60% existing + 40% Sudarshana triple-frame
       ▼
  Phase 2I: Upagraha Affliction
       │  Transit into Gulika/Mandi/Dhuma/Vyatipata natal sign → 12% penalty
       ▼
  Phase 2K: Shodhya Pinda Scaling
       │  Net bindu strength → multiplier [0.80, 1.20], reference = 350
       ▼
  Phase 3F.2: Nadi Saturn Activation
       │  Activated domain planet → +10%
       ▼
  Adjusted Transit Scores (used for confidence)
```

### 6.3 Gate Architecture

```
                  GATE 0: Three Pillar Promise
                  (Bhava + Bhavesha + Karaka)
                        │
              ┌─────────┼─────────┐
              │         │         │
           DENIED   SUPPRESSED   PASSED
           conf=0.05  cap=0.45   uncapped
           (RETURN)    │          │
                       │          │
                  GATE 1: KP Promise
                  (Sublord signifies domain?)
                        │
              ┌─────────┤
              │         │
          FAILED     PASSED
          cap=0.22     │
              │         │
              │    GATE 2: Dasha Confirmation
              │    (Dasha lord activates domain?)
              │         │
              │    ┌────┤
              │    │    │
              │  FAILED PASSED
              │  cap=0.38  │
              │    │       │
              ▼    ▼       ▼
         Weighted Component Scoring
         (different weight sets per gate state)
```

### 6.4 Promise Gate (Gate 0) — Three Pillar Rule

Checks if the birth chart structurally permits the domain event.

| Pillar | What | Scoring |
|--------|------|---------|
| **Bhava** (House) | Strength of domain house | Lord strength×0.5 + location×0.3 + benefic bonus |
| **Bhavesha** (House Lord) | Quality of domain house lord | Shadbala + dignity + D9 placement |
| **Karaka** (Significator) | Strength of natural karaka | Shadbala ratio + house placement |

| Strong Pillars | Promise % | Effect |
|---------------|-----------|--------|
| 3 of 3 | 100% | Full promise, no cap |
| 2 of 3 | 67% | Cap at 0.70 |
| 1 of 3 | 33% | Cap at 0.40 |
| 0 of 3 | 0% | **DENIED** — hard 0.05, cannot be overridden by dasha/transit |

**Domain Karakas:** Career=SATURN, Finance=JUPITER, Marriage=VENUS, Health=SUN, Children=JUPITER, Spiritual=KETU

---

## 7. Confidence Architecture

### 7.1 Eight Component Scores (each 0.0–1.0)

| # | Component | What It Measures | Formula |
|---|-----------|-----------------|---------|
| 1 | **Dasha Alignment** | MD/AD lords signify domain | 0.6 if MD matches + 0.4 if AD matches, × shadbala mod |
| 2 | **Transit Support** | Average net_score of domain planets | Mean of transiting domain planets' scores |
| 3 | **Ashtakvarga** | Bindu strength at domain signs | 40% SAV + 35% Karaka BAV + 25% Dasha BAV (tiered) |
| 4 | **Yoga Activation** | Domain-relevant yogas active | count (cap 5) × grade premium (C=1.0, S=1.5) |
| 5 | **KP Confirmation** | Sublord signifies domain houses | 60% MD overlap + 40% AD overlap − negator penalty |
| 6 | **Functional Alignment** | Lagna-specific benefic/malefic role | Yogakaraka=1.0, benefic=0.7, malefic=0.15, badhaka=0.05 |
| 7 | **House Lord Strength** | Domain house lord quality | Shadbala/1.5 × placement mod × varga dignity |
| 8 | **Jaimini Sub** | Chara+Karakamsha+Arudha+Rashi Drishti | 30% Chara + 25% Karakamsha + 25% Arudha + 20% Rashi |

### 7.2 Adaptive Weights (change based on gate state)

| Component | Gate Failed (KP) | Dasha Not Confirmed | Both Gates Passed |
|-----------|-----------------|--------------------|--------------------|
| Dasha | 0.20 | **0.30** | 0.20 |
| Transit | 0.16 | 0.185 | **0.35** ← dominant |
| Ashtakvarga | 0.11 | 0.135 | 0.15 |
| Yoga | 0.08 | 0.12 | 0.12 |
| KP | **0.30** ← dominant | 0.14 | 0.10 |
| Functional | 0.10 | 0.07 | 0.05 |
| House Lord | 0.00 | 0.00 | 0.00 (removed: already in Promise gate) |
| Jaimini | 0.05 | 0.05 | 0.03 |

**Key insight:** When both gates pass, Transit becomes dominant (0.35) for precise timing. When KP promise fails, KP weight is 0.30 (so low KP directly drives low confidence).

### 7.3 MD/AD Geometric Modifier

| AD position from MD | Effect | Multiplier on Dasha Score |
|---------------------|--------|--------------------------|
| 6th, 8th, 12th | Friction (Shadashtaka) | × 0.55 |
| 1, 4, 5, 7, 9, 10 | Boost (Kendra/Trikona) | × 1.25 |
| Other | Neutral | × 1.00 |

**Dasha Lord Dignity:**
- Combust → × 0.50 ("burned")
- Retrograde → × 0.75 (delayed/erratic)

### 7.4 Ashtakvarga Tiered Scoring

| Average BAV Bindus | Score Range | Interpretation |
|--------------------|-------------|----------------|
| 0–3 | 0.00–0.15 | Malefic/disastrous |
| 4 | 0.40 | Neutral equilibrium |
| 5–8 | 0.55–1.00 | Exponentially positive |

---

## 8. Post-Confidence Modifiers

After `compute_confidence()` returns the base score, multiple modifier layers are applied sequentially:

### 8.1 Modifier Chain

```
Base Confidence (from 8 components + gates)
       │
       ▼
  [1] Baladi Avastha Modifier
       │  Shadbala ratios × avastha multiplier (Deepta=1.0 ... Mrita=0.15 floor)
       ▼
  [2] Classical Modifier
       │  60% Planet Effectiveness + 40% Bhava Effectiveness
       │  Planet Eff = 45% Shadbala + 35% Vimshopak + 20% BAV × Avastha coeff
       │  Bhava Eff = Bhavabala rupas/7 × lord factor
       │  Range: [0.10, 2.0]
       ▼
  [3] Dasha Convergence (weighted multi-system agreement)
       │  CONVERGENCE_TABLE: 0%→0.05, 20%→0.10, 40%→0.325, 60%→0.725, 80%→0.965, 100%→0.999
       ▼
  [4] Dosha Modifier
       │  Manglik (marriage): severity≥3 → ×0.70, severity≥1 → ×0.85
       │  Kala Sarpa: partial → ×0.50, full → ×0.85
       │  Pitru (health): ×0.80
       │  Range: [0.05, 1.5]
       ▼
  [5] Yoga Domain Boost
       │  Per-domain yoga_boosts dict, dasha-lord activation = full value, else 30%
       │  Diminishing returns: boost[i] / (1 + i×0.5)
       │  Cap: +50%
       ▼
  [6] Bridge Cross-Validation Modifier (§ Phase 6 L3)
       │  10 sub-functions cross-validate PyJHora + VedAstro
       │  Range: [0.88, 1.15] multiplicative
       │  See Section 10 for details
       ▼
  [7] Multi-System Agreement Boost
       │  Vimshottari + Yogini → additive confidence_boost
       ▼
  [8] Fuzzy Inference Blend
       │  3 inputs: timing, transit, structural → 27-rule fuzzy system
       │  Blend: 55% linear + 45% fuzzy
       ▼
  [9] Bayesian Posterior (Beta-conjugate update)
       │  Prior: 55% yoga + 45% functional, concentration=4.0
       │  Evidence: Dasha(3.0) + Transit(2.0) + KP(binary) + Convergence(1.5) + Varshaphala(1.0)
       │  Triple-blend: 45% linear + 35% fuzzy + 20% Bayesian
       ▼
  [10] Vimshopak Boost
       │  Dasha lord multi-varga dignity → ±4%
       ▼
  [11] Special Lagnas (Phase 2J)
       │  Domain-specific lagnas (Ghati, Hora, Indu, Sri, Varnada, Pranapada)
       │  Kendra/trikona → +, dusthana → −
       │  Cap: ±4%
       ▼
  [12] Hellenistic Sect Bonus (Phase 3F.3)
       │  In-sect domain planet → +5% each, cap +10%
       ▼
  [13] Lunar Health Modifier (Phase 3F.4, health only)
       │  -3% × cos(moon-sun phase) — science-based correlation
       ▼
  [14] Argala Modifier
       │  Natal argala from dasha/antardasha lord houses
       │  Combined confidence modification
       ▼
  [15] Transit Aspect Score
       │  Continuous orb weighting, applying/separating
       │  ±5% modifier
       ▼
  [16] Progressions Boost
       │  Secondary progressions + Solar arc
       │  ±8% cap
       ▼
  FINAL BOOSTED SCORE
```

### 8.2 Master Overrides (can bypass everything)

| Condition | Override Confidence | When |
|-----------|-------------------|------|
| Extreme Sade Sati + Moon SAV < 25 | **0.05** | Extreme stress, no outcomes |
| Dasha Sandhi active | **0.10** | Transition chaos |
| Transit Saturn-Rahu conjunction near Lagna/Moon | **0.15** | Karmic crisis window |
| Vipreet Raja Yoga + active dasha lord | **0.85** | Crisis → massive gain |
| Dasha lord Vimshopak ≥ 18 | **0.90** | Guaranteed excellence |

### 8.3 Double Transit Gate

If Jupiter + Saturn are NOT in beneficial houses from natal Moon → cap at 0.50 (event unlikely to fully manifest).

---

## 9. Calibration Layer

Raw engine scores are well-ordered but not numerically calibrated. Isotonic regression maps raw → true probability:

| Raw Score | Calibrated | Meaning |
|-----------|------------|---------|
| 0.00 | 0.03 | Near-zero signal |
| 0.30 | 0.28 | Weak signals |
| 0.50 | 0.48 | Exactly neutral |
| 0.68 | 0.67 | Dasha+transit agreement |
| 0.80 | 0.78 | Strong all-system |
| 0.90 | 0.85 | Very strong |
| 1.00 | 0.90 | Maximum (never >90%) |

**Reliability Bands:**
| Calibrated | Band | Interpretation |
|------------|------|----------------|
| ≥ 0.78 | Strong | Multiple systems converge. High reliability. |
| 0.65–0.78 | Moderate-Strong | Good convergence. Timing may vary ±2–4 weeks. |
| 0.52–0.65 | Moderate | Partial convergence. Broad trends only. |
| 0.38–0.52 | Weak | Limited signal. Tendency uncertain. |
| < 0.38 | Insufficient | Systems contradict. No prediction advisable. |

**Confidence Labels (pre-calibration):**
| Score Range | Label |
|-------------|-------|
| 0.00–0.08 | Highly Unlikely |
| 0.08–0.15 | Event Latent / No Trigger |
| 0.15–0.35 | Unlikely but Possible |
| 0.35–0.58 | Average Results / High Friction |
| 0.58–0.63 | Neutral Results |
| 0.63–0.70 | Likely |
| 0.70–0.78 | Moderate Success |
| 0.78–0.88 | Highly Probable |
| 0.88–1.00 | Will Definitely Happen |

---

## 10. Bridge System (External Validation)

### 10.1 Architecture

```
                    ┌───────────────┐
                    │  Core Engine   │
                    │  (SwissEph)    │
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌──────────┐ ┌──────────┐ ┌────────────┐
        │ PyJHora  │ │ VedAstro │ │  JyotishG  │
        │ Bridge   │ │ Bridge   │ │  (future)  │
        └────┬─────┘ └────┬─────┘ └────────────┘
             │             │
             └──────┬──────┘
                    ▼
        ┌─────────────────────┐
        │ bridge_integration  │ → 10 cross-validation functions
        │ .py                 │ → modifier [0.88, 1.15]
        └─────────────────────┘
```

### 10.2 PyJHora Bridge

- **Runs:** TOP of analyze_static (before SwissEph to avoid ayanamsa conflict)
- **Library:** `jhora.panchanga.drik`, `jhora.horoscope.chart.*`, `jhora.horoscope.main.Horoscope`
- **Data:** 22 dasha systems, yogas, doshas, ashtakvarga, arudhas, charts, compatibility
- **Output:** `static["computed"]["pyjhora"]` dict with all sub-results

### 10.3 VedAstro Bridge

- **Runs:** END of analyze_static
- **Method:** Isolated subprocess in separate venv (`vedastro_isolated/.venv`)
- **Communication:** JSON markers in stdout (`__VEDASTRO_JSON_START__` / `__VEDASTRO_JSON_END__`)
- **Timeout:** 120 seconds
- **Data:** Horoscope predictions, planetary calculations, dasha periods
- **Output:** `static["computed"]["vedastro"]` dict

### 10.4 Bridge Cross-Validation Functions (bridge_integration.py)

| Function | What It Cross-Validates | Boost/Penalty |
|----------|------------------------|---------------|
| `cross_validate_yogas` | Our yogas vs PyJHora yogas | Confirmed: +2%/yoga (cap +10%), Extra PJ: +0.6%/yoga (cap +3%) |
| `cross_validate_doshas` | Dosha agreement | Match: confirm factor |
| `cross_validate_dashas` | Dasha lord planet matching | Same lord: boost |
| `cross_validate_strengths` | Harsha/Shad Bala comparison | Weak planet: penalty |
| `cross_validate_ashtakvarga` | BAV bindu agreement | Correlation boost |
| `vedastro_domain_predictions` | VedAstro career/finance predictions | Count-based scoring |
| `vedastro_dasha_cross` | VedAstro active dasha vs ours | Lord match: boost |
| `extra_dasha_support` | Multiple dasha systems agree | Supporting ratio → boost |
| `harsha_bala_check` | PyJHora harsha/shad bala | Weak domain planet: penalty |
| `rasi_dasha_check` | Rasi-based dasha in domain houses | Sign in domain: boost |

**Master Modifier:** Product of all sub-boosts, clamped to **[0.88, 1.15]**. Applied multiplicatively to `base_final`.

---

## 11. AI Layer

### GPT-4o-mini Reasoner (4 decision points)

| Function | When Called | What GPT Decides | Fallback |
|----------|-----------|------------------|----------|
| `resolve_yoga_fructification` | Before yoga scoring | Is this yoga actually active in current dasha? Returns strength_multiplier | yoga counted at face value |
| `resolve_dasha_conflict` | When timing systems disagree | Which system to trust? | Equal weight |
| `resolve_kp_ambiguity` | Sublord signifies domain + negator | Adjusted KP score | Raw overlap ratio |
| `get_adaptive_weights` | Per-chart calibration | Custom weight vector | Default weights |

**Config:** model=gpt-4o-mini, temperature=0.2, response_format=json_object, session-cached by MD5

---

## 12. Module Inventory

### 12.1 Strength Layer (`vedic_engine/strength/`)

| Module | Purpose | Scale |
|--------|---------|-------|
| `shadbala.py` | 6-fold planet strength | Rupas (total shashtiamsas / 60) |
| `ashtakvarga.py` | Bindu point system | 0–8 per sign, SAV invariant = 337 |
| `bhavabala.py` | House strength | Rupas (>8 Strong, <6 Weak) |
| `vimshopak.py` | Multi-varga dignity | 0–20 score (Shadvarga: D1=6, D9=5, D3=4, D2=2, D12=2, D30=1) |

### 12.2 Timing Layer (`vedic_engine/timing/`)

| Module | Cycle | When Used |
|--------|-------|-----------|
| `vimshottari.py` | 120 years, 9 planets | **Primary** for all domains |
| `yogini.py` | 36 years, 8 yoginis | **Secondary** for all domains |
| `ashtottari.py` | 108 years, 8 planets (no Ketu) | **Conditional** — Rahu in kendra/trikona from LL |
| `chara_dasha.py` | Variable (sign-based) | Career (0.25), Marriage (0.25) |
| `kp.py` | Sublord chains | KP Promise gate |
| `jaimini_dashas.py` | 7+ systems (Shoola, Niryana, Brahma...) | Jaimini sub-score |
| `sudarshana.py` | Triple-frame (Lagna/Moon/Sun) | Transit adjustment Phase 2D |
| `panchanga.py` | 5 limbs (Tithi/Nakshatra/Yoga/Karana/Vara) | Muhurta timing |
| `varshaphala.py` | Annual solar return | Varshaphala score (Phase 2H) |
| `kalachakra.py` | Deha/Jeeva | Health domain timing |
| `conditional_dashas.py` | 9 conditional systems | If eligibility met |

**Dasha Weights per Domain:**

| System | Career | Finance | Marriage | Health |
|--------|--------|---------|----------|--------|
| Vimshottari | 0.40 | 0.45 | 0.40 | 0.20 |
| Chara | 0.25 | 0.15 | 0.25 | — |
| Yogini | 0.15 | 0.10 | 0.20 | — |
| Ashtottari | 0.10 | 0.25 | 0.10 | — |
| Niryana Shoola | — | — | — | **0.40** |
| Kalachakra | — | — | — | **0.20** |
| Sudarshana | — | — | — | 0.15 |
| Other | 0.10 | 0.05 | 0.05 | 0.05 |

### 12.3 Analysis Layer (`vedic_engine/analysis/`)

| Module | Purpose |
|--------|---------|
| `yogas.py` | ~30 classical yogas (Raja, Dhana, Mahapurusha, etc.) |
| `extended_yogas.py` | Graded (S/A/B/C) + domain-tagged yoga system |
| `doshas.py` | 5 dosha detectors (Kala Sarpa, Manglik, Pitru, Combustion, Gandanta) |
| `functional.py` | Lagna-specific benefic/malefic classification |
| `karakas.py` | Chara (variable) + Sthira (fixed) karaka calculation |
| `avasthas.py` | Baladi, Shayanadi, Deeptadi avastha states |
| `dispositor.py` | Chain analysis for dasha lords |
| `argala.py` | Natal argala from houses to houses |
| `lunations.py` | New/Full Moon timing impact |
| `special_points.py` | Gulika, Hora/Ghati Lagna, Varnada, Pranapada, Sri Lagna, Sahams |
| `special_degrees.py` | Mrityu Bhaga, Gandanta, Pushkara Navamsha/Bhaga |
| `graha_yuddha.py` | Planetary war detection + shadbala penalties |
| `nadi_timing.py` | Nadi Jyotish (BCP, Saturn activation, Patel, BNN) |
| `hellenistic.py` | Profections, Sect, Lots, Zodiacal Releasing, Midpoints |
| `compatibility.py` | Kuta matching tables |
| `medical.py` | Arishta, Disease, Psychiatric, Marakas |
| `nakshatra_*.py` | Classification, Tarabala, Panchaka |
| `muhurta_ext.py` | Panchanga Shuddhi, Tithi/Vara classification |
| `varga_interp.py` | D60, D30, Sapta/Dasha Varga, Kashinath Hora |
| `advanced_techniques.py` | Bhrigu Sutras, Neechabhanga Extended, Saptha Shalaka |
| `lalkitab.py` | Lal Kitab remedial system |

### 12.4 Core Layer (`vedic_engine/core/`)

| Module | Purpose |
|--------|---------|
| `divisional.py` | D1–D60 sign computations from longitude |
| `aspects.py` | BPHS piecewise aspects + Drik Bala (all 9 grahas incl. Rahu/Ketu) |
| `coordinates.py` | `sign_of()`, degree conversion utilities |
| `swisseph_bridge.py` | pyswisseph wrapper (Lahiri, Placidus, natal+transit) + Bhava Chalit shift detection |
| `btr_montecarlo.py` | Birth time rectification (Monte Carlo simulation) |
| `sunrise_utils.py` | Daytime/nighttime, Paksha computation |
| `varga_interpretations.py` | D30, D60, Hora, Drekkana analysis |

### 12.5 Prediction Layer (`vedic_engine/prediction/`)

| Module | Purpose |
|--------|---------|
| `engine.py` | **Master orchestrator** — 4-stage pipeline |
| `confidence.py` | 8-component weighted scoring + gate logic |
| `classical_modifiers.py` | Planet/Bhava effectiveness + convergence + dosha + yoga boost |
| `domain_signal_weights.py` | DOMAIN_SIGNALS reference (primary/secondary per domain) |
| `bridge_integration.py` | 10-function bridge cross-validation |
| `bayesian_layer.py` | Beta-conjugate posterior update |
| `fuzzy_confidence.py` | 27-rule fuzzy inference |
| `calibration.py` | Isotonic regression calibration |
| `promise.py` | Three Pillar Rule (Gate 0) |
| `prediction_overrides.py` | 5 master override rules |
| `transits.py` | Gochar evaluation + Vedha + Sade Sati |
| `timing_optimizer.py` | Best timing window identification |

---

## 13. Weight Reference Table

### Confidence Component Weights

| Component | Both Gates Passed | KP Failed | Dasha Not Confirmed |
|-----------|------------------|-----------|---------------------|
| Dasha | 0.20 | 0.20 | 0.30 |
| Transit | **0.35** | 0.16 | 0.185 |
| Ashtakvarga | 0.15 | 0.11 | 0.135 |
| Yoga | 0.12 | 0.08 | 0.12 |
| KP | 0.10 | **0.30** | 0.14 |
| Functional | 0.05 | 0.10 | 0.07 |
| House Lord | 0.00 | 0.00 | 0.00 |
| Jaimini | 0.03 | 0.05 | 0.05 |

### Dasha Convergence Table

| Weighted Agreement | Confidence Multiplier |
|-------------------|----------------------|
| 0% | 0.05 |
| 20% | 0.10 |
| 40% | 0.325 |
| 60% | 0.725 |
| 80% | 0.965 |
| 100% | 0.999 |

### Planet Effectiveness Weights

| Factor | Weight |
|--------|--------|
| Shadbala ratio | 45% |
| Vimshopak score/20 | 35% |
| BAV score/8 | 20% |
| × Avastha coefficient | multiplier (Deepta=1.0 → Mrita=0.0, floor 0.15) |

### Ashtakvarga Blend

| Signal | Weight |
|--------|--------|
| SAV (collective) | 40% |
| Karaka BAV (domain-specific) | 35% |
| Dasha lord BAV | 25% |

### Triple Confidence Blend

| Method | Weight |
|--------|--------|
| Linear weighted | 45% |
| Fuzzy inference | 35% |
| Bayesian posterior | 20% |

### Bayesian Evidence Strengths

| Source | Pseudo-observations |
|--------|-------------------|
| Natal prior (yoga + functional) | 4.0 concentration |
| Dasha | 3.0 |
| Transit (65%) + AV (35%) | 2.0 |
| KP | 2.0 (binary: confirmed/denied) |
| Multi-dasha convergence | 1.5 |
| Varshaphala | 1.0 |

### Yoga Domain Boosts

**Career:** Dharma-Karmadhipati(0.35), Adhi(0.25), Bhadra(0.20), Ruchaka(0.20), Saraswati(0.20)
**Finance:** Maha Dhan(0.40), Dhana(0.30), Lakshmi(0.25), Gajakesari(0.15)
**Marriage:** Parivartana 7H(0.25), Early Marriage(0.20), Love Marriage(0.15), Gajakesari(0.10)
**Health:** Balarishta Bhanga(0.40), Purna Ayush(0.35), Arishta(-0.30), Vipreet Raja(0.30)

---

## 14. Output Structure

The `predict()` function returns a dict with these top-level keys:

```
{
  "domain":              "career",
  "date":                "2024-01-01T00:00:00",
  "dasha": {
    "maha_dasha":        "SATURN",
    "antar_dasha":       "MERCURY",
    "yogini_lord":       "JUPITER"
  },
  "confidence": {
    "overall":           0.434,          ← post-modifiers score
    "overall_boosted":   0.401,          ← after fuzzy+bayesian+small mods
    "final":             0.434,          ← may equal override if active
    "raw":               0.380,          ← 8-component base score
    "level":             "MODERATE",
    "gate_status":       "BOTH_GATES_PASSED",
    "promise_pct":       100,
    "components": {                      ← all 8 scores (0–1 each)
      "dasha_alignment", "transit_support", "ashtakvarga_support",
      "yoga_activation", "kp_confirmation", "functional_alignment",
      "house_lord_strength", "jaimini_sub"
    },
    "weights_used":      {...},          ← which weight set applied
    "classical_modifier": 0.89,
    "convergence":       0.725,
    "dosha_modifier":    1.0,
    "yoga_boost":        0.0,
    "bridge_cross_validation": {
      "modifier": 1.055, "available": true, "diagnostics": {...}
    },
    "bayesian":          {...},
    "fuzzy":             {...},
    "consensus_ratio":   0.667,
    "domain_signals":    {...}
  },
  "calibrated_confidence": {
    "raw":               0.401,
    "calibrated":        0.383,
    "reliability_band":  "Weak",
    "confidence_interval": [0.35, 0.41],
    "interpretation":    "Limited signal strength..."
  },
  "transits":            {...},          ← domain-relevant transit data
  "active_yogas":        [...],          ← yoga name list
  "sade_sati":           {...},
  "karakas":             {...},
  "prediction":          "Narrative text...",
  "dispositor":          {...},
  "promise":             {...},
  "dasha_diagnostic":    {...},
  "multi_dasha_consensus": {...},
  "chara_dasha":         {...},
  "badhaka":             {...},
  "bhavabala_domain_modifier": {...},
  "graha_yuddha":        [...],
  "dhana_stacking":      {...},
  "nakshatra_analysis":  {...},
  "panchanga":           {...},
  "dasha_transit":       {...},
  "argala":              {...},
  "transit_aspects":     {...},
  "progressions":        {...},
  "solar_terms":         [...],
  "lunations":           {...},
  "timing_windows":      {...},
  "remedies":            [...],
  "career_checklist":    {...},
  "varga_report":        {...},
  "dispositor_graph":    {...},
  "chalit_shifts":       [...]           ← planets that shifted houses between Rashi and Chalit
}
```

---

## Quick Reference: Full Scoring Formula

```
score = Σ(component_i × weight_i)        # 8 components × adaptive weights
      ↓ cap by promise (Gate 0: 0.05/0.40/0.70/1.0)
      ↓ cap by KP (Gate 1: 0.22)
      ↓ cap by Dasha (Gate 2: 0.38)
      × Baladi avastha modifier
      × Classical modifier (planet eff × bhava eff)
      × Dasha convergence (0.05–0.999)
      × Dosha modifier (0.05–1.5)
      × (1 + yoga boost) (cap +50%)
      × Bridge cross-validation (0.88–1.15)
      ↓ + multi-system agreement boost
      ↓ blend: 55% linear + 45% fuzzy
      ↓ triple: 45% linear + 35% fuzzy + 20% Bayesian
      ↓ + vimshopak boost (±4%)
      ↓ + special lagna mod (±4%)
      ↓ + sect bonus (up to +10%)
      ↓ + lunar health mod (±3%, health only)
      ↓ + argala mod
      ↓ + transit aspect mod (±5%)
      ↓ + progressions boost (±8%)
      ↓ override check (5 rules can replace entire score)
      ↓ double transit gate (cap 0.50 if inactive)
      → calibrate(raw_score) → final calibrated probability
```

---

*Document generated from codebase analysis. Module count: ~115 Python files across 10 directories.*
*Last verified against engine.py ~3200 lines, confidence.py ~740 lines, classical_modifiers.py ~310 lines.*

---

## Revision Log

| Date | Changes |
|------|---------|
| 2026-03-05 | **6 Classical Jyotish Fixes Applied:** |
| | 1. Career Karaka corrected: SUN → **SATURN** (BPHS Sthira Karaka for 10th house) — `promise.py` + `classical_modifiers.py` |
| | 2. Health Karaka unified: MOON → **SUN** (vitality/prana primary) — `classical_modifiers.py` aligned with `promise.py` |
| | 3. D30 Trimsamsha BPHS sequence fixed in `divisional.py`: Odd signs now Mars→Saturn→Jupiter→Mercury→Venus (was Mars→Venus→Mercury→Jupiter→Saturn) |
| | 4. Rahu/Ketu standard 7th aspect (60 shashtiamsa, malefic) added — `aspects.py` `_get_planet_enum()` + `PLANET_NAMES_9`. Propagates to Drik Bala, Bhava Bala, aspect map, yoga detection. |
| | 5. Bhava Chalit shift detection added — `compute_chalit_shifts()` in `swisseph_bridge.py`, wired into `analyze_static()` output as `chalit_shifts` |
| | 6. Chara Karaka tie-breaking added — natural planet order precedence (Sun > Moon > Mars > ... > Saturn > Rahu) in `karakas.py` |
