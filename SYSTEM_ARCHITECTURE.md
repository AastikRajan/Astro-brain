# Vedic Astrology Prediction Engine — System Architecture

> **Purpose**: Complete reference for anyone to understand the full system — all inputs, outputs, weights, scales, wiring, categories, and data flow. Read this to build a mental map for debugging, extending, or auditing any layer.

## 0. Status Addendum (2026-04-14)

- Native Dasha Pravesha commencement-chart gating is integrated and passed into confidence as a bounded dasha multiplier.
- Precise Nakshatra/Yoga Pravesha solver path is wired through active annual context, with anchor diagnostics.
- Native Tripataki now includes vedha geometry and contributes a bounded annual confidence delta.
- Deterministic confidence arbitration gate is active with domain-calibrated profiles.
- `VE_USE_TROPICAL_MONTH_FOR_PRAVESHA` default is finalized to ON, with env override retained.

**Open depth-work**:
- Per-domain Shodasha weighting policy refinement.
- Outcome-labeled benchmark calibration for arbitration and annual modifiers.

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
| **Career** | 2, 6, 10, 11 | 1, 5, 9 | SUN, SATURN, MERCURY, MARS, JUPITER |
| **Finance** | 2, 6, 11 | 12 | VENUS, JUPITER, MERCURY, MOON |
| **Marriage** | 2, 7, 11 | 1, 6, 10 | VENUS, JUPITER, MOON, MARS |
| **Health** | 1, 6, 8, 12 | — | MARS, SUN, SATURN, MOON |
| Children | 2, 5, 11 | — | JUPITER, VENUS, MOON |
| Property | 4, 12 | — | MOON, JUPITER, MARS |
| Spiritual | 4, 8, 9, 12 | — | JUPITER, SATURN, KETU, MOON |
| Travel | 3, 9, 12 | — | MERCURY, RAHU, MARS, SATURN |

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

Note: `TRANSIT_FRAME_WEIGHTS` is now actively consumed in `engine.py` during Classical Phase-1 composition (Lagna + Moon + Dasha-lord weighted support).

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
| **Ashtakvarga** | Bindu points + SAV diagnostics + timing helpers | Planet signs + lagna | 0–8 per sign, SAV total=337 | BAV + SAV + Shodhana + Shodhya Pinda + PAV + `sav_profile` (Vittya/Teertha/H2:H12/H1:H8) + transit quality helpers |
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
| **Transit Evaluation** | Transits + natal Moon + natal Lagna + BAV/SAV/PAV | Per-planet Gochar scores | Uses full `GOCHAR_SCORES` matrix + `BAV_TRANSIT_MULTIPLIERS`, with quantitative Vedha reduction, Kakshya precision, and Moon+Lagna frame scoring |
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
  ├── Extract active dasha lords (MD, AD, PD)
  ├── Extract yogini lord
  ├── Extract AV data (SAV, BAV, dasha planet BAV)
  ├── Build karaka-BAV data bundle (bhinna + planet_signs + house_lords)
  ├── Compute domain houses, negator houses, domain planets
  ├── Compute relevant signs from lagna
  ├── Build Jaimini data + AK dignity info (§Fix 47)
  ├── Pre-compute dasha lord gochar multiplier (§Fix 48)
  └── Compute effective Shadbala (raw × Baladi avastha multiplier)
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
              (Bhava + Bhavesha + Karaka, §Fix 33-34)
                        │
              ┌─────────┼─────────┐
              │         │         │
           DENIED   SUPPRESSED   GREY ZONE     PASSED
         conf=0.05  cap=0.45    cap=0.48      uncapped
         (RETURN)    │            │              │
                     └────────────┼──────────────┘
                                  │
                  GATE 1: KP Promise
                  (Sublord signifies domain?)
                        │
              ┌─────────┤
              │         │
          FAILED     PASSED
          cap=0.25     │    (elevated to 0.35 if c_dasha≥0.70 + c_transit≥0.50)
              │         │
              │    GATE 2: Dasha Confirmation
              │    (c_dasha ≥ 0.25?)
              │         │
              │    ┌────┤
              │    │    │
              │  FAILED PASSED
              │  cap=0.38  │
              │    │       │
              ▼    ▼       ▼
         Weighted Component Scoring
         (different weight sets per gate state)

         D9 Quality Filter (cap/boost promise ceiling)
         Dasha Lord Gochar Multiplier on c_dasha (§Fix 48)
         MD lord excluded from transit average (§Fix 49)
```

### 6.4 Promise Gate (Gate 0) — Three Pillar Rule (§Fixes 33-35)

Checks if the birth chart structurally permits the domain event. Implemented in `promise.py`.

**Thresholds** (Fix 33-34):

| Setting | Value | Notes |
|---------|-------|-------|
| Default threshold | **0.55** | A pillar must score ≥ 0.55 to count as "strong" |
| Grey zone | **0.45–0.55** | Ambiguous — not strong, not weak. Flagged for downstream |
| Marriage threshold | 0.45 | Most forgiving — Venus/7th house often afflicted |
| Career threshold | 0.60 | Most demanding — requires structural excellence |
| Finance threshold | 0.55 | Standard |
| Health threshold | 0.50 | Moderate |

| Pillar | What | Scoring |
|--------|------|---------|
| **Bhava** (House) | Strength of domain house | Lord strength×0.5 + location×0.3 + benefic bonus |
| **Bhavesha** (House Lord) | Quality of domain house lord | Shadbala(60%) + placement(20%) + D9 dignity(20%) — hard-cap 0.38 if D9 veto |
| **Karaka** (Significator) | Strength of natural karaka | Shadbala(60%) + placement(25%) + D9(15%) |

| Strong Pillars | Grey Count | Promise % | Ceiling | Notes |
|---------------|------------|-----------|---------|-------|
| 3 of 3 | — | 100% | 1.00 | Full promise, uncapped |
| 2 of 3 | — | 67% | 0.70 | Moderate effort required |
| 1 of 3 | — | 33% | 0.40 | Significant delay |
| 0 of 3 | 0 grey | 0% | **0.05** | **DENIED** — unbreakable |
| 0 of 3 | ≥1 grey, total ≥2 | 0% | 0.48 | **GREY ELEVATED** — borderline |

**Exemptions from Denial** (Fix 35):
- **Viparita Raja Yoga**: Dusthana lord in different dusthana → double negation → SUPPRESSED (cap 0.45)
- **Retrograde Debilitation**: Debilitated + retrograde → treated as exalted → SUPPRESSED
- **Combustion**: If only pillar failing is combustion, and other pillars grey zone → SUPPRESSED (not denied)
- **NBRY/Upachaya check**: Bhavesha or Karaka in NBRY sign or Upachaya house → SUPPRESSED (delayed but possible)

**Domain Karakas:** Career=SATURN, Finance=JUPITER, Marriage=VENUS, Health=SUN, Children=JUPITER, Spiritual=KETU

### 6.5 Jaimini Data Bundle

Constructed in `engine.py` before `compute_confidence()`. Enriched with AK dignity data for veto power (§Fix 47):

```python
jaimini_data = {
    "chara_alignment":     float,   # Chara Dasha sign in domain house? (0.3–0.75)
    "karakamsha_score":    float,   # Benefic influence in Karakamsha domain houses
    "arudha_alignment":    float,   # Relevant Arudha Pada well-placed?
    "rashi_drishti_score": float,   # Benefic sign aspects to domain houses
    "ak_planet":           str,     # Atmakaraka planet name (§Fix 47)
    "ak_combust":          bool,    # AK within combustion orb of Sun
    "ak_debilitated":      bool,    # AK in debilitation sign
    "ak_enemy_sign":       bool,    # AK in great enemy's sign
    "ak_shadbala":         float,   # AK's Shadbala ratio (BPHS minimum = 1.0)
}
```

### 6.6 Dasha Lord Gochar Pre-Computation (§Fix 48)

Before `compute_confidence()` is called, the engine pre-computes a multiplicative gochar throttle:

```
1. Get combined_transit_score from dasha_transit analysis
2. Look up BAV bindus in dasha lord's current transit sign
3. Apply BAV tier multiplier:
     0→0.40  1→0.45  2→0.55  3→0.70  4→1.00  5→1.30  6→1.60  7→1.85  8→2.00
4. Compute deviation: (combined_score − 0.50) × BAV_mult × 0.40
5. Clamp to [0.70, 1.30]:  dasha_lord_gochar_mult = 1.0 + deviation
```

This multiplier is passed into `compute_confidence()` and applied directly to `c_dasha` — replacing the old additive post-hoc modifier. Research mandate: "Effective_Dasha_Strength = Natal_Dasha_Quality × σ(Gochar_Score)"

---

## 7. Confidence Architecture

### 7.1 Nine Component Scores (each 0.0–1.0)

| # | Component | What It Measures | Formula | File |
|---|-----------|-----------------|---------|------|
| 1 | **Dasha Alignment** | MD/AD/PD lords signify domain | 0.6 if MD matches + 0.2 if AD matches + 0.2 if PD matches, × shadbala mod. Then **× gochar multiplier** (§Fix 48) | `confidence.py` |
| 2 | **Transit Support** | Average net_score of domain planets | Mean of domain planets' scores, **excluding MD lord** to prevent double-counting with gochar (§Fix 49) | `confidence.py` |
| 3 | **Ashtakvarga** | Bindu strength at domain signs | 40% SAV + 35% Karaka BAV + 25% Dasha BAV (tiered 0-8 scoring) | `confidence.py` |
| 4 | **Yoga Activation** | Domain-relevant yogas active | count (cap 5) × grade premium (C=1.0, B=1.125, A=1.25, S=1.5). Cancelled yogas = 50% weight. Modulated by **Manduka Gati age coefficient** (§Fix 46) | `confidence.py` |
| 5 | **KP Confirmation** | Sublord signifies domain houses | 60% MD overlap + 40% AD overlap − negator penalty | `confidence.py` |
| 6 | **Functional Alignment** | Lagna-specific benefic/malefic role | Yogakaraka=1.0, benefic=0.7, malefic=0.15, badhaka=0.05 | `confidence.py` |
| 7 | **House Lord Strength** | Domain house lord quality | **Weight = 0.00** (removed §9.3: already evaluated in Promise gate) | `confidence.py` |
| 8 | **Jaimini Sub** | Chara+Karakamsha+Arudha+Rashi Drishti + **AK dignity veto** (§Fix 47) | Domain-specific weights (see §7.6). AK dignity-based veto can cap score to 0.25/0.40 | `confidence.py` |
| 9 | **D9 Quality** | Navamsha chart quality | Marriage: D9 Lagna Lord + 7th Lord D9 dignity + Venus D9 + Jupiter D9. General: domain lord D9 dignity | `confidence.py` |

### 7.2 Adaptive Weights (change based on gate state)

| Component | Gate 1 Failed (KP) | Dasha Not Confirmed | Both Gates Passed |
|-----------|-------------------|--------------------|--------------------|
| Dasha | 0.20 | **0.30** | 0.20 |
| Transit | 0.16 | 0.185 | **0.35** ← dominant |
| Ashtakvarga | 0.11 | 0.135 | 0.15 |
| Yoga | 0.08 | 0.12 | 0.12 |
| KP | **0.30** ← dominant | 0.14 | 0.10 |
| Functional | 0.10 | 0.07 | 0.05 |
| House Lord | 0.00 | 0.00 | 0.00 |
| Jaimini | 0.05 | 0.05 | 0.03 |
| **Total** | **1.00** | **1.00** | **1.00** |

**Key insight:** When both gates pass, Transit becomes dominant (0.35) for precise event timing. When KP promise fails, KP weight is 0.30 (so low KP directly drives low confidence).

### 7.3 c_dasha Modifier Pipeline (applied sequentially inside `compute_confidence()`)

The dasha alignment score (`c_dasha`) undergoes a chain of multiplicative modifiers before entering the weighted sum:

```
Raw c_dasha
   │
   ▼
Shadbala Hard Minimum (BPHS Mandate)
   │  MD lord ratio < 1.0 → c_dasha × max(0.15, ratio)
   ▼
MD/AD Geometric Relationship (§7.4)
   │  Based on house distance: ×0.55 to ×1.25
   ▼
MD/AD Natural Friendship/Enmity
   │  Enemy: ×0.80, Friend: ×1.10
   ▼
Combustion — Bifurcated (Phaladeepika)
   │  MD lord IS domain karaka → ×0.35 (karakatwa destroyed)
   │  MD lord is lord only → ×0.70 (lordship survives)
   ▼
Retrograde — Bifurcated (Uttara Kalamrita)
   │  Natural benefic retro → ×0.85 (delayed then massive spike)
   │  Natural malefic retro → ×0.65 (erratic, struggle)
   ▼
Dasha Lord Gochar Multiplier (§Fix 48)  ← NEW
   │  c_dasha × gochar_mult (range 0.70–1.30)
   │  Research: Effective_Dasha_Strength = Natal_Quality × σ(Gochar)
   ▼
Final c_dasha (enters weighted sum)
```

### 7.4 MD/AD Geometric Modifier

| AD position from MD | Effect | Multiplier | Notes |
|---------------------|--------|------------|-------|
| 6th, 8th | Shadashtaka friction | × 0.55 | Great danger, enmity |
| 12th | Vyaya friction | × 0.60 | Losses, expenditure |
| 2nd | Dwidwadasha friction | × 0.70 | Mild inauspiciousness |
| 3rd, 11th | Upachaya supportive | × 1.15 | Growth axis |
| 1, 4, 5, 7, 9, 10 | Kendra/Trikona boost | × 1.25 | Fruitful, overrides MD negativity |
| Other | Neutral | × 1.00 | No modification |

### 7.5 Promise Ceiling System

After the weighted sum is computed, the result is capped by the promise ceiling:

| Condition | Ceiling | Notes |
|-----------|---------|-------|
| Promise DENIED (Gate 0) | **0.05** | Hard boundary — unbreakable |
| Promise SUPPRESSED | 0.45 | Delayed but possible at maturity |
| Grey Zone Elevated | 0.48 | Borderline between suppressed and weak |
| Weak promise (≤33%) | 0.40 | Moderate cap |
| Moderate promise (34-67%) | 0.70 | High possible but not very high |
| Full promise (>67%) | 1.00 | Uncapped |

**D9 Quality Filter on ceiling** (multiplicative):
- D9 < 0.30: Marriage → cap min(ceiling, 0.55) ("The Illusion" — occurs but fails); Other → cap min(ceiling, 0.60)
- D9 > 0.75: ceiling += 0.10 (quality confirmed)

**KP Gate caps** (applied after promise ceiling):
- KP failed + strong dasha (c_dasha≥0.70, c_transit≥0.50) → cap 0.35 (elevated weak)
- KP failed otherwise → cap 0.25
- Dasha not confirmed → cap 0.38

### 7.6 Jaimini Sub-Score Architecture (§Fixes 38-39, 47)

#### Domain-Specific Weighting

| Domain | Chara Alignment | Karakamsha | Arudha | Rashi Drishti | Rationale |
|--------|----------------|------------|--------|---------------|-----------|
| Spiritual/Moksha/Dharma | 0.20 | **0.40** | 0.20 | 0.20 | AK's Karakamsha is ultimate diagnostic |
| Career/Profession | **0.35** | 0.30 | 0.15 | 0.20 | AmK-to-AK spatial relationship dominant |
| Marriage | 0.25 | 0.15 | **0.40** | 0.20 | DK + Upapada (A12) dominant |
| Default Phalita | 0.30 | 0.25 | 0.25 | 0.20 | Balanced |
| Health/Longevity (Ayur) | — | — | 0.30 | 0.30 | Chara bypassed, Sthira only (40%) |

#### AK Veto Power — Dignity-Based (§Fix 47)

The Atmakaraka is the "king" of the chart. Its condition governs whether other karakas can deliver:

| AK Condition | Affliction Count | Effect | Cap |
|-------------|-----------------|--------|-----|
| **Severely afflicted**: ≥2 afflictions, or debilitated + Shadbala < 1.0 | 2+ | Full veto — king incapacitated, secondary karakas cannot deliver | score ≤ 0.25 |
| **Mildly afflicted**: 1 affliction, or Shadbala < 1.0 only | 1 | Partial suppression — karakas weakened | score ≤ 0.40 |
| **Strong**: 0 afflictions + Shadbala ≥ 1.0 | 0 | Protective insulation — floor guarantee (shield, NOT multiplicative boost) | score ≥ 0.35 |

**Affliction types** (3 classical sources):
1. **Debilitation**: AK in its debilitation sign (e.g., Sun in Libra, Moon in Scorpio)
2. **Combustion**: AK within combustion orb of Sun
3. **Enemy sign**: AK placed in great-enemy house (per BPHS Naisargika Maitri)

**BPHS Shadbala Minimum**: AK ratio < 1.0 = below minimum required rupas → "fundamentally incapacitated"

**Key distinction from old logic**: Previous version used flat `ak_strength < 0.30` ratio threshold with `1.15×` multiplicative boost for strong AK. Research showed:
- Strong AK gives **protection** (insulation floor), NOT amplification
- Affliction must be detected via **classical dignity markers**, not generic strength ratio

### 7.7 Manduka Gati Age Modulation (§Fix 37, 46)

BPHS "Frog's Leap" sequence divides the 108-year lifespan into chronological epochs. Yogas in houses outside their epoch are modulated:

| Epoch | Age Range | Active Houses | Coefficient |
|-------|-----------|---------------|-------------|
| Early Life | 0–36 | 4, 2, 8, 10 | **1.00** (fully active) |
| Middle Life | 36–72 | 12, 6, 5, 11 | **1.00** (fully active) |
| Late Life | 72–108 | 1, 7, 9, 3 | **1.00** (fully active) |

| Timing Mismatch | Coefficient | Meaning |
|----------------|-------------|---------|
| Yoga in FUTURE epoch (1 away) | **0.20** | Latent — only 20% manifests now |
| Yoga in PAST epoch (1 ago) | **0.85** | Residual — 85% remains as established pattern |
| Two epochs away | **0.10** | Almost completely dormant |

### 7.8 Ashtakvarga Tiered Scoring

The AV component uses non-linear tiered scoring:

| Average BAV Bindus | Score Range | Interpretation |
|--------------------|-------------|----------------|
| 0–3 | 0.00–0.15 | Malefic/disastrous |
| 4 | 0.40 | Neutral equilibrium |
| 5–8 | 0.55–1.00 | Exponentially positive |

**Three-signal blend**: 40% SAV + 35% Karaka BAV (domain sthira karaka) + 25% Dasha lord BAV

### 7.9 Yoga Hierarchy Integration (Fix 52)

`score_yoga_activation()` now follows a dasha-gated classical hierarchy instead of simple yoga counting.

| Rule | Implementation |
|------|----------------|
| Dasha interlock | Yoga weight strongest when both MD and AD match yoga carrier planets |
| Partial interlock | One of MD/AD matching carrier gives reduced but meaningful activation |
| Latent state | No MD/AD carrier match keeps yoga as low latent potential |
| Nabhasa exception | `type="nabhasa"` yogas are always-on background modifiers (domain-damped, not fully timed) |
| Contradiction resolver | Positive support vs negative pressure compared; stronger side prevails via ratio damping |

Current interlock multipliers:
- MD+AD both in carriers: `1.00`
- Either MD or AD in carriers: `0.75`
- Neither active: `0.35`
- Nabhasa: always-on interlock bypass

Current contradiction handling:
- If positive support >= negative pressure: confidence retained with conservative damping.
- If negative pressure > positive support: yoga confidence suppressed toward low-confidence floor.

---

## 8. Post-Confidence Modifiers

After `compute_confidence()` returns the base score, multiple modifier layers are applied sequentially in `engine.py`:

### 8.1 Modifier Chain

```
Base Confidence (from 9 components + gates + promise ceiling)
       │
       ▼
  [1] Deeptadi Avastha Hard-Gate (Phaladeepika)
       │  MD lord avastha state → multiplicative gate
       │  Deepta=1.0, Swastha=0.625, Pramudita=0.375, Shanta=0.25,
       │  Dina=0.125, Vikala=0.05, Khala/Kopa/Mrita=0.00 (hard floor 0.15)
       ▼
  [2] Baladi Avastha Pre-Modifier (before confidence call)
       │  Shadbala ratios × avastha multiplier per planet
       │  Mrita = 0.00 strictly (NO floor). Mercury exempt (always 1.0).
       │  Applied to effective_shadbala BEFORE compute_confidence()
       ▼
  [3] Classical Modifier
       │  60% Planet Effectiveness + 40% Bhava Effectiveness
       │  Planet Eff = 45% Shadbala + 35% Vimshopak + 20% BAV × Avastha coeff
       │  Bhava Eff = Bhavabala rupas/7 × lord factor
       │  Range: [0.10, 2.0]
       ▼
  [4] Dasha Convergence (weighted multi-system agreement)
       │  CONVERGENCE_TABLE: 0%→0.05, 20%→0.10, 40%→0.325, 60%→0.725, 80%→0.965, 100%→0.999
       ▼
  [5] Dosha Modifier
       │  Manglik (marriage): severity≥3 → ×0.70, severity≥1 → ×0.85
       │  Kala Sarpa: partial → ×0.50, full → ×0.85
       │  Pitru (health): ×0.80
       │  Range: [0.05, 1.5]
       ▼
  [6] Yoga Domain Boost
       │  Per-domain yoga_boosts dict, dasha-lord activation = full value, else 30%
       │  Diminishing returns: boost[i] / (1 + i×0.5)
       │  Cap: +50%
       ▼
  [7] Bridge Cross-Validation Modifier (§ Phase 6 L3)
       │  10 sub-functions cross-validate PyJHora + VedAstro
       │  Range: [0.88, 1.15] multiplicative
       │  See Section 10 for details
       ▼
  [8] Multi-System Agreement Boost
       │  Vimshottari + Yogini → additive confidence_boost
       ▼
  [9] Fuzzy Inference Blend
       │  3 inputs: timing, transit, structural → 27-rule fuzzy system
       │  Blend: 55% linear + 45% fuzzy
       ▼
  [10] Bayesian Posterior (Beta-conjugate update)
       │  Prior: 55% yoga + 45% functional, concentration=4.0
       │  Evidence: Dasha(3.0) + Transit(2.0) + KP(binary) + Convergence(1.5) + Varshaphala(1.0)
       │  Triple-blend: 45% linear + 35% fuzzy + 20% Bayesian
       ▼
  [11] Vimshopak Boost
       │  Dasha lord multi-varga dignity → ±4%
       ▼
  [12] Special Lagnas (Phase 2J)
       │  Domain-specific lagnas (Ghati, Hora, Indu, Sri, Varnada, Pranapada)
       │  Kendra/trikona → +, dusthana → −
       │  Cap: ±4%
       ▼
  [13] Hellenistic Sect Bonus (Phase 3F.3)
       │  In-sect domain planet → +5% each, cap +10%
       ▼
  [14] Lunar Health Modifier (Phase 3F.4, health only)
       │  -3% × cos(moon-sun phase) — science-based correlation
       ▼
  [15] Argala Modifier
       │  Natal argala from dasha/antardasha lord houses
       │  Combined confidence modification
       │  Includes weighted Argala houses, pure-virodha handling, and
       │  unobstructable (3+ planets) diagnostics
       ▼
  [15.5] Classical Phase-1 Bundle (diagnostic-first)
       │  Pushkara × Moorti × Tarabala composite multiplier
       │  Always computes baseline + adjusted candidate
       │  Applies adjusted only when `VE_ENABLE_CLASSICAL_MULTIPLIERS=1`
       │  Safety clamp: total multiplier capped to [0.20, 2.50]
       ▼
  [16] Transit Aspect Score (§Fix 41)
       │  Longitude-based continuous orb weighting
       │  Dynamic orbs: 1° (strong natal), 2° (medium), 5° (weak)
       │  Stationing multiplier: 2.5× (speed < 15% of mean), 1.8× (speed < 30%)
       │  Partile bonus: +30% within precision orb
       │  Applying aspect bonus: ×1.15
       │  Nakshatra Pada micro-trigger: flagged if orb < 3.33°
       │  Cap: ±5%
       ▼
  [17] Progressions Boost
       │  Secondary progressions + Solar arc
       │  ±8% cap
       ▼
  [18] Double Transit Gate (§Fix 40)
       │  Jupiter AND Saturn must aspect/conjoin domain houses
       │  Domain-specific check (not just generic from Moon)
       │  If inactive → confidence capped at 0.50
       ▼
  [19] Triple Transit — Multiplicative Accelerator (§Fix 43)
       │  Rahu/Ketu joining Jupiter-Saturn double transit
       │  Applied as MULTIPLICATIVE factor (not additive):
       │
       │  RAHU (domain-specific multipliers):
       │    Career: ×1.25   Finance: ×1.22   Property: ×1.18
       │    Travel: ×1.18   Marriage: ×1.12   Children: ×1.10
       │    Health: ×1.05   Spiritual: ×1.05  Default: ×1.15
       │
       │  KETU:
       │    Spiritual/Moksha: ×1.20 (empowers renunciation)
       │    All material domains: ×0.80 (forced dissolution, structural collapse)
       ▼
  [20] Dasha Lord Transit Quality — Diagnostic (§Fix 48)
       │  Gochar scoring now moved INSIDE compute_confidence() as c_dasha multiplier
       │  This block retained for BAV diagnostic data in output only
       │  Reports: gochar_mult value, BAV bindus in transit sign
       ▼
  [21] Domain Lord Transit Boost (§Fix 42, 45)
       │  BAV tiered exponential scoring for domain lord transits
       │  _BAV_TIER: 0→−0.04, 1→−0.03, ..., 4→+0.02, 5→+0.08, 6→+0.14, 7→+0.18, 8→+0.22
       │  Own-house transit: BAV≤3 neutralizes dignity (negative boost)
       │  BAV 5+ own-house: Kakshya refinement bonus (+4%)
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

### 8.3 Domain Lord Transit Boost (§Fix 42, 45 — BAV Exponential)

Two independent boost paths:

**Path A — Domain Lord BAV Tier** (exponential, not linear):

| BAV Bindus | Boost | Interpretation |
|-----------|-------|----------------|
| 0 | −0.04 | Severely weakened transit |
| 1 | −0.03 | Weak |
| 2 | −0.02 | Below threshold |
| 3 | −0.01 | Marginal negative |
| 4 | +0.02 | Neutral-positive |
| **5** | **+0.08** | Tipping point — begins exponential |
| 6 | +0.14 | Strong positive |
| 7 | +0.18 | Very strong |
| 8 | +0.22 | Maximum exponential — near-certain manifestation |

**Path B — Dasha Lord Own-House Transit** (BAV cross-verified):
- Dasha lord transiting its own natal house AND:
  - BAV ≤ 3 → Own-house neutralized (boost becomes **negative**: −0.03 for MD, −0.02 for AD)
  - BAV 4 → Neutral own-house effect
  - BAV ≥ 5 → Full own-house boost + **Kakshya refinement bonus** (+0.04)
    - Kakshya: 3.75° sub-divisions, 8 lords (Saturn→Jupiter→Mars→Sun→Venus→Mercury→Moon→Asc)

### 8.4 Dasha Lord Gochar — Before vs. After (§Fix 44 → 48)

| Aspect | Old (Fix 44, additive) | New (Fix 48, multiplicative) |
|--------|----------------------|------------------------------|
| **Location** | Post-confidence in engine.py | Inside compute_confidence() on c_dasha |
| **Mechanism** | `confidence += (combined − 0.50) × 0.40 × BAV_mult` | `c_dasha × gochar_mult` where gochar_mult ∈ [0.70, 1.30] |
| **BAV cross-verification** | Same tier table | Same tier table (0→0.40 ... 8→2.00) |
| **Research basis** | "15-25% primary weight" | "Effective_Dasha_Strength = Natal_Quality × σ(Gochar)" |
| **Double-counting** | Could double-count with transit average | Separated: MD lord excluded from transit average (Fix 49) |

### 8.5 Transit Double-Counting Prevention (§Fix 49)

**Problem**: When the Maha-Dasha lord is also a domain planet (e.g., Saturn for career), it was scored in:
- **Path A**: Transit average (score_transit_support) — as a domain planet
- **Path B**: Dasha lord gochar — as the active dasha lord

Both paths measured the same planet's transit quality, inflating its impact.

**Solution**: Two coordinated fixes:
1. **Fix 49**: `score_transit_support()` now receives `dasha_planet` and **excludes** it from the domain planet average
2. **Fix 48**: Dasha lord gochar is applied as a **multiplier on c_dasha** (not additive to final), so the transit information flows through the dasha channel only

### 8.6 Argala Modernization (Post-Fix 49)

Recent Argala upgrades were integrated without replacing the existing confidence hook:

| Upgrade | Behavior | Diagnostics/Controls |
|---------|----------|----------------------|
| House weighting | 2/4/11 full, 5 secondary half, 7 special half | Exposed in per-pair `house_weight` fields |
| Unobstructable rule | 3+ planets in Argala house cannot be obstructed | `unobstructable=true`, aggregated `unobstructable_count` |
| Pure Virodha | Empty Argala house + occupied Virodha contributes controlled negative | `net_type="PURE_VIRODHA"`, `pure_virodha=true` |
| Node reverse modes | Ketu reverse mode retained by default; optional Rahu+Ketu mode | Env: `VE_ARGALA_NODE_REVERSE_MODE=ketu|both` |

Report surface:
- `Argala Modifier` still shows net confidence impact.
- `Argala details` now prints unobstructable count and node mode for continuation/debug.

### 8.7 Classical Phase-1 Rollout Controls

Classical bundle integration is intentionally diagnostic-first and controlled via env flags.

| Env Flag | Default | Effect |
|---------|---------|--------|
| `VE_ENABLE_CLASSICAL_MULTIPLIERS` | `0` | Computes classical multipliers but does not apply unless set to `1` |
| `VE_ENABLE_NAKSHATRA_SIGNALS` | `1` | Enables integration of Nakshatra diagnostic signals (`combined_moon_score`, `pushkara_diagnostic`, `transit_themes`, `moon_naming_star`) into classical multiplier composition |
| `VE_APPLY_MOORTI_TO_TRANSIT` | `0` | Controls whether Moorti-adjusted transit score replaces raw `net_score` in transit layer |

Classical bundle currently included in `confidence["classical_phase1"]`:

| Field | Meaning |
|------|---------|
| `enabled` | Whether adjusted candidate is applied (`VE_ENABLE_CLASSICAL_MULTIPLIERS`) |
| `baseline_before_classical` | Score before phase-1 classical bundle |
| `pushkara_multiplier` | Domain karaka/lord Pushkara contribution |
| `moorti_multiplier` | Mean Moorti factor from relevant slow movers |
| `tarabala_multiplier` | Paryaya-adjusted Tarabala factor |
| `transit_frame_multiplier` | Weighted Lagna+Moon+Dasha transit support (`TRANSIT_FRAME_WEIGHTS`) |
| `nakshatra_signals_enabled` | Whether Nakshatra diagnostic signal bundle is active (`VE_ENABLE_NAKSHATRA_SIGNALS`) |
| `nakshatra_signal_multiplier` | Composite multiplier from Nakshatra signal sub-factors |
| `nakshatra_moon_multiplier` | Multiplier derived from `combined_moon_score` |
| `nakshatra_pushkara_multiplier` | Multiplier derived from `pushkara_diagnostic.effective_factor` |
| `nakshatra_theme_multiplier` | Multiplier from domain-vs-theme alignment over domain planets |
| `nakshatra_theme_hits` | Count of domain planets whose transit theme domain matches target domain |
| `nakshatra_theme_total` | Total domain planets considered for theme alignment |
| `nakshatra_combined_moon_score` | Raw integrated Moon signal used for bounded modulation |
| `tarabala_source` | Tarabala data source (`transit_moon` preferred, `nakshatra_analysis` fallback) |
| `tara_number` | Resolved 9-Tara index (1-9) used to derive Tarabala multiplier |
| `total_multiplier_capped` | Composite multiplier after safety clamp |
| `adjusted_candidate` | `baseline × total_multiplier_capped` candidate |
| `policy` | Current rollout strategy (`diagnostic-first`) |

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
| `ashtakvarga.py` | Bindu point system + advanced SAV profile + transit helpers | 0–8 per sign, SAV invariant = 337; `sav_profile` includes Vittya/Teertha/H2:H12/H1:H8; includes kakshya/transit quality utility functions |
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
| `advanced_yogas.py` | 20+ advanced yoga detectors (including graded/domanized signals) |
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
| `timing/nadi_timing.py` | Nadi Jyotish (BCP, Saturn activation, Patel, BNN) |
| `timing/hellenistic.py` | Profections, Sect, Lots, Zodiacal Releasing, Midpoints |
| `compatibility.py` | Kuta matching tables |
| `medical_astrology.py` | Core medical astrology analysis |
| `medical_extended.py` | Arishta, disease, psychiatric, maraka and extended medical logic |
| `nakshatra_*.py` | Classification, Tarabala, Panchaka |
| `timing/muhurta_extended.py` | Panchanga Shuddhi, Hora/Choghadiya and domain Muhurta checks |
| `core/varga_interpretations.py` | D60, D30, Sapta/Dasha Varga, Kashinath Hora |
| `advanced_techniques.py` | Bhrigu Sutras, Neechabhanga Extended, Saptha Shalaka |
| `lal_kitab.py` | Lal Kitab diagnostics and annual indicators |

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
| `engine.py` | **Master orchestrator** — 4-stage pipeline (~3600+ lines). Pre-computes gochar and dasha-pravesha multipliers, manages Tripataki/annual integration, and applies final arbitration gate |
| `confidence.py` | 9-component weighted scoring + 4-gate logic + AK dignity veto + gochar multiplier + MD lord transit exclusion (~1100 lines) |
| `classical_modifiers.py` | Planet/Bhava effectiveness + convergence + dosha + yoga boost |
| `domain_signal_weights.py` | DOMAIN_SIGNALS reference (primary/secondary per domain) |
| `bridge_integration.py` | 10-function bridge cross-validation |
| `bayesian_layer.py` | Beta-conjugate posterior update |
| `fuzzy_confidence.py` | 27-rule fuzzy inference |
| `calibration.py` | Isotonic regression calibration |
| `promise.py` | Three Pillar Rule (Gate 0) — domain-specific thresholds, grey zone, VRY/retro-debil exemptions |
| `prediction_overrides.py` | 5 master override rules |
| `transits.py` | Gochar evaluation + Vedha + Sade Sati |
| `dasha_transit.py` | Dasha lord transit analysis, double/triple transit, domain lord BAV boost, own-house transit |
| `aspect_transits.py` | Longitude-based transit aspects — dynamic orbs (1°/2°/5°), stationing 2.5×, partile bonus, nakshatra pada |
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

### BAV Gochar Cross-Verification Tiers (§Fixes 44-45, 48)

| BAV Bindus | Gochar Multiplier | Domain Lord Boost | Interpretation |
|-----------|-------------------|-------------------|----------------|
| 0 | 0.40 | −0.04 | Severely weakened, gochar neutralized |
| 1 | 0.45 | −0.03 | Very weak |
| 2 | 0.55 | −0.02 | Below threshold |
| 3 | 0.70 | −0.01 | Marginal negative |
| 4 | 1.00 (neutral) | +0.02 | Equilibrium |
| **5** | **1.30** | **+0.08** | **Tipping point** |
| 6 | 1.60 | +0.14 | Strong positive |
| 7 | 1.85 | +0.18 | Very strong |
| 8 | 2.00 | +0.22 | Maximum — near-certain |

### Triple Transit Multipliers (§Fix 43)

| Node | Career | Finance | Property | Travel | Marriage | Children | Health | Spiritual | Default |
|------|--------|---------|----------|--------|----------|----------|--------|-----------|---------|
| **RAHU** | ×1.25 | ×1.22 | ×1.18 | ×1.18 | ×1.12 | ×1.10 | ×1.05 | ×1.05 | ×1.15 |
| **KETU** (material) | ×0.80 | ×0.80 | ×0.80 | ×0.80 | ×0.80 | ×0.80 | ×0.80 | — | ×0.80 |
| **KETU** (spiritual) | — | — | — | — | — | — | — | ×1.20 | — |

### AK Dignity Veto Decision Table (§Fix 47)

| AK Debilitated | AK Combust | AK Enemy Sign | Shadbala < 1.0 | Veto | Cap |
|:-:|:-:|:-:|:-:|------|-----|
| ✓ | ✓ | — | — | **Severe** | ≤ 0.25 |
| ✓ | — | ✓ | — | **Severe** | ≤ 0.25 |
| — | ✓ | ✓ | — | **Severe** | ≤ 0.25 |
| ✓ | — | — | ✓ | **Severe** | ≤ 0.25 |
| ✓ | — | — | — | Mild | ≤ 0.40 |
| — | ✓ | — | — | Mild | ≤ 0.40 |
| — | — | ✓ | — | Mild | ≤ 0.40 |
| — | — | — | ✓ | Mild | ≤ 0.40 |
| — | — | — | — | **Protective** | ≥ 0.35 |

### Manduka Gati Coefficients (§Fix 46)

| Timing Relation | Coefficient | Classical Source |
|----------------|-------------|-----------------|
| Active epoch | 1.00 | BPHS: full manifestation |
| One epoch FUTURE | 0.20 | Latent — 20% seepage |
| One epoch PAST | 0.85 | Residual — 85% persistence |
| Two epochs away | 0.10 | Near-dormant |

### Yoga Domain Boosts

**Career:** Dharma-Karmadhipati(0.35), Adhi(0.25), Bhadra(0.20), Ruchaka(0.20), Saraswati(0.20)
**Finance:** Maha Dhan(0.40), Dhana(0.30), Lakshmi(0.25), Gajakesari(0.15)
**Marriage:** Parivartana 7H(0.25), Early Marriage(0.20), Love Marriage(0.15), Gajakesari(0.10)
**Health:** Balarishta Bhanga(0.40), Purna Ayush(0.35), Arishta(-0.30), Vipreet Raja(0.30)

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
    "raw":               0.380,          ← 9-component base score (+ d9_quality)
    "level":             "MODERATE",
    "gate_status":       "BOTH_GATES_PASSED",
    "promise_pct":       100,
    "components": {                      ← all 9 scores (0–1 each)
      "dasha_alignment", "transit_support", "ashtakvarga_support",
      "yoga_activation", "kp_confirmation", "functional_alignment",
      "house_lord_strength", "jaimini_sub", "d9_quality"
    },
    "weights_used":      {...},          ← which weight set applied
    "classical_modifier": 0.89,
          "classical_phase1": {                ← diagnostic-first classical bundle
               "enabled":        false,
               "baseline_before_classical": 0.434,
               "pushkara_multiplier": 1.50,
               "moorti_multiplier": 0.62,
               "tarabala_multiplier": 1.00,
               "tarabala_source": "transit_moon",
               "tara_number": 7,
               "total_multiplier_capped": 0.94,
               "adjusted_candidate": 0.408,
               "policy": "diagnostic-first"
          },
    "convergence":       0.725,
    "dosha_modifier":    1.0,
     "argala_mod":        -0.073,        ← net Argala confidence delta
    "yoga_boost":        0.0,
    "dasha_lord_gochar_mult": 1.30,      ← §Fix 48: BAV-based gochar multiplier on c_dasha
    "dasha_lord_bav_in_transit": 5,      ← §Fix 48: BAV bindus of MD lord in transit sign
    "bridge_cross_validation": {
      "modifier": 1.055, "available": true, "diagnostics": {...}
    },
    "bayesian":          {...},
    "fuzzy":             {...},
    "consensus_ratio":   0.667,
    "domain_signals":    {...},
    "triple_transit": {                  ← §Fix 43: triple transit details
      "active":          true,
      "rahu_mult":       1.25,           ← domain-specific Rahu multiplier
      "ketu_mult":       0.80,           ← material domain Ketu damper
      "combined":        1.25
    },
    "ak_veto": {                         ← §Fix 47: AK dignity diagnostics
      "ak_planet":       "JUPITER",
      "ak_combust":      false,
      "ak_debilitated":  false,
      "ak_enemy_sign":   false,
      "ak_shadbala":     1.45,
      "veto_level":      "none",         ← "severe"|"mild"|"protective"|"none"
      "cap_applied":     null
    }
  },
  "calibrated_confidence": {
    "raw":               0.401,
    "calibrated":        0.383,
    "reliability_band":  "Weak",
    "confidence_interval": [0.35, 0.41],
    "interpretation":    "Limited signal strength..."
  },
  "promise": {                            ← §Fix 33-36: promise gate details
    "score":             0.72,
    "passed":            true,
    "threshold":         0.55,           ← domain-specific (e.g. marriage=0.45)
    "grey_zone":         false,          ← [threshold, threshold+0.10)
    "grey_elevated":     false,          ← §Fix 36: weak → eligible by D9/Navamsha
    "suppressed":        false,          ← no promise = cap 0.05
    "vry_exempt":        false,          ← §Fix 35: VRY/retro-debil bypass
    "domain_threshold":  0.55
  },
  "transits":            {...},          ← domain-relevant transit data
  "active_yogas":        [...],          ← yoga name list
  "sade_sati":           {...},
  "karakas":             {...},
  "prediction":          "Narrative text...",
  "dispositor":          {...},
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

Additional nested outputs now commonly present:

```
"ashtakvarga": {
     "sarva": [...],
     "sarva_total": 337,
     "sav_profile": {
          "vittya": {"score": 142, "threshold": 164, "status": "STRAINED", "ratio": 0.87},
          "teertha": {"score": 80, "threshold": 76, "status": "VULNERABLE", "ratio": 1.05},
          "savings_capacity": {"h2": 26, "h12": 21, "can_save": true, "ratio": 1.238},
          "h1_vs_h8": {"h1": 29, "h8": 33, "healthy_balance": false}
     }
}

"argala": {
     "lagna": {
          "node_reverse_mode": "ketu",
          "unobstructable_count": 0,
          "argala_list": [...],
          "virodha_list": [...]
     }
}
```

---

## Quick Reference: Full Scoring Formula

```
GATE 0 — Promise Check (§Fixes 33-36):
  promise_score = evaluate_promise(static_data, domain)
  threshold = DOMAIN_THRESHOLDS[domain]     # marriage=0.45, career=0.60, etc.
  IF promise < threshold AND NOT vry_exempt:
    IF promise in [threshold, threshold+0.10):   # Grey zone
      weak_promise_elevation via D9/Navamsha check → may pass
    ELSE:
      cap = 0.05 (suppressed)
  
score = Σ(component_i × weight_i)        # 9 components × adaptive weights
      ↓ cap by promise (Gate 0: 0.05/0.40/0.70/1.0)
     ↓ cap by KP (Gate 1: 0.25 standard, 0.35 elevated when c_dasha≥0.70 and c_transit≥0.50)
      ↓ cap by Dasha (Gate 2: 0.38)

INSIDE compute_confidence() — c_dasha modifier pipeline:
     c_dasha × MD/AD geometry alignment (0.55–1.25 by house-distance relationship)
  c_dasha × Baladi avastha modifier
  c_dasha × Classical modifier (planet eff × bhava eff)
  c_dasha × Dasha convergence (0.05–0.999 from table)
  c_dasha × GOCHAR MULTIPLIER (§Fix 48: BAV-tiered 0.40–2.00)   ← NEW
  c_dasha floor/clamp to [0.0, 1.0]

OUTSIDE compute_confidence() — post-confidence modifiers (21 steps):
  × Dosha modifier (0.05–1.5)
  × (1 + yoga boost) (cap +50%)
  × Bridge cross-validation (0.88–1.15)
  + multi-system agreement boost
  blend: 55% linear + 45% fuzzy → blended
  triple: 45% linear + 35% fuzzy + 20% Bayesian → tripled
  + vimshopak boost (±4%)
  + special lagna mod (±4%)
  + sect bonus (up to +10%)
  + lunar health mod (±3%, health only)
  + argala mod
  + transit aspect mod (±5%)
  + progressions boost (±8%)
  × TRIPLE TRANSIT (§Fix 43: Rahu domain-specific, Ketu material/spiritual)  ← NEW
  × DOMAIN LORD TRANSIT BOOST (§Fix 44: BAV exponential −0.04 to +0.22)     ← NEW
  override check (5 rules can replace entire score)
  double transit gate (cap 0.50 if inactive)
  → calibrate(raw_score) → final calibrated probability

TRANSIT SPECIAL RULES:
  - MD lord EXCLUDED from transit average (§Fix 49: prevent double-counting)
     - Lagna transit support now uses actual house-from-lagna evaluation when natal lagna is available
     - Tarabala in classical phase uses live transit Moon signal first, static Nakshatra fallback second
       - Transit gochar base now uses full `GOCHAR_SCORES` matrix (with mixed-house support) and applies `BAV_TRANSIT_MULTIPLIERS`
       - Classical Phase-1 now includes weighted transit-frame factor (`TRANSIT_FRAME_WEIGHTS`) and optional Nakshatra signal bundle
  - Transit orbs: dynamic 30%/50%/100%/150% with stationing ×2.5 (§Fix 42)
  - Partile conjunction (<1°): +0.05 bonus
```

---

*Document generated from codebase analysis. Module count: ~115 Python files across 10 directories.*
*Last verified against engine.py ~3600 lines, confidence.py ~1100 lines, classical_modifiers.py ~310 lines.*

---

## Revision Log

| Date | Changes |
|------|---------|
| 2026-03-05 | **Session 1-5: 6 Classical Jyotish Fixes Applied (Fixes 1-6):** |
| | 1. Career Karaka corrected: SUN → **SATURN** (BPHS Sthira Karaka for 10th house) — `promise.py` + `classical_modifiers.py` |
| | 2. Health Karaka unified: MOON → **SUN** (vitality/prana primary) — `classical_modifiers.py` aligned with `promise.py` |
| | 3. D30 Trimsamsha BPHS sequence fixed in `divisional.py`: Odd signs now Mars→Saturn→Jupiter→Mercury→Venus |
| | 4. Rahu/Ketu standard 7th aspect (60 shashtiamsa, malefic) added — `aspects.py` |
| | 5. Bhava Chalit shift detection added — `compute_chalit_shifts()` in `swisseph_bridge.py` |
| | 6. Chara Karaka tie-breaking added — natural planet order precedence in `karakas.py` |
| 2026-03-05 | **Sessions 1-5: Fixes 7-32** — Structural improvements to pipeline, VedAstro bridge integration, calibration layer, remedies, timing windows, multi-system consensus, Bayesian+fuzzy confidence, etc. |
| 2026-03-06 | **Session 6: Fix 33 — Promise Threshold Tightening** |
| | Raised global promise threshold from 0.50 → **0.55** to reduce false-positive predictions. `promise.py` |
| 2026-03-06 | **Session 6: Fix 34 — Domain-Specific Promise Thresholds** |
| | Added per-domain overrides: marriage=0.45, children=0.48, spiritual=0.42, career=0.60, finance=0.58, health=0.52. `promise.py` |
| 2026-03-06 | **Session 6: Fix 35 — VRY / Retro-Debilitated / Combustion Exemptions** |
| | Planets with Vipreet Raja Yoga, retrograde-debilitated (Neechabhanga), or combust-but-in-own-sign bypass promise suppression. `promise.py` |
| 2026-03-06 | **Session 6: Fix 36 — Weak Promise Grey-Zone Elevation** |
| | Promise scores in [threshold, threshold+0.10) get D9/Navamsha re-evaluation; if dignified in Navamsha, elevated to pass. `promise.py` |
| 2026-03-06 | **Session 6: Fix 37 — Manduka Gati (Frog Jump) Dasha Integration** |
| | Manduka Gati coefficients: active=1.0, future=0.20, past=0.85, two-away=0.10. Multiplied onto c_dasha inside `confidence.py`. |
| 2026-03-06 | **Session 6: Fix 38 — Chara Karaka Routing** |
| | Jaimini data bundle now fed through `score_jaimini_sub()` with AK, AmK, DK, PK matched to domain-specific karakas. `confidence.py` |
| 2026-03-06 | **Session 6: Fix 39 — Chara Karaka Routing (Expanded)** |
| | Jaimini scoring expanded: domain-karaka relevance matrix, AK positioning in kendras/trikonas, karaka dignity weighting. `confidence.py` |
| 2026-03-06 | **Session 6: Fix 40 — Triple Transit with Rahu/Ketu** |
| | Jupiter + Saturn + Rahu/Ketu triple transit detection. Rahu amplifies material houses (10, 11, 2, 7). `dasha_transit.py` + `engine.py` |
| 2026-03-06 | **Session 6: Fix 41 — Triple Transit Wiring into Pipeline** |
| | Triple transit result consumed as multiplicative modifier in post-confidence chain. `engine.py` |
| 2026-03-06 | **Session 6: Fix 42 — Transit Orb Precision** |
| | Dynamic orbs: partile (<1°), close (1-3°), standard (3-7°), wide (5-10°). Stationing multiplier ×2.5. `aspect_transits.py` |
| 2026-03-06 | **Session 6: Fix 43 — Triple Transit Domain-Specific Rahu/Ketu Multipliers** |
| | Per-domain Rahu multipliers (career=1.25, marriage=1.12, spiritual=1.05, etc.). Ketu: material=0.80, spiritual=1.20. `engine.py` |
| 2026-03-06 | **Session 6: Fix 44 — Domain Lord Transit Boost** |
| | BAV exponential curve for domain lord in transit: bindus 0→−0.04, 5→+0.08, 8→+0.22. Applied as post-confidence modifier. `dasha_transit.py` + `engine.py` |
| 2026-03-06 | **Session 6: Fix 45 — BAV Tiered Exponential Scoring** |
| | Ashtakvarga scoring in `score_ashtakvarga_support()` uses exponential tier table instead of linear interpolation. `confidence.py` |
| 2026-03-06 | **Session 6: Fix 46 — Manduka Gati Coefficients Refinement** |
| | Refined frog-jump coefficients with classical BPHS sourcing. Applied multiplicatively on c_dasha. `confidence.py` |
| 2026-03-06 | **Session 7: Fix 47 — AK Veto → Dignity-Based** |
| | Replaced binary AK veto with dignity-based 3-tier system: Severe (debil+combust/enemy, cap 0.25), Mild (single affliction, cap 0.40), Protective (strong AK, floor 0.35). Uses debilitation signs, enemy signs, combust list, Shadbala < 1.0 checks. `confidence.py` + `engine.py` |
| 2026-03-06 | **Session 7: Fix 48 — Dasha Lord Gochar as Multiplicative on c_dasha** |
| | Moved gochar from post-hoc additive to multiplicative on c_dasha inside `compute_confidence()`. BAV-tier table (0.40–2.00). Old post-hoc block retained as diagnostic-only. `confidence.py` + `engine.py` |
| 2026-03-06 | **Session 7: Fix 49 — Exclude MD Lord from Transit Average** |
| | `score_transit_support()` now takes `dasha_planet` param and filters it out of transit average to prevent double-counting (already captured in c_dasha gochar). `confidence.py` + `engine.py` |
| 2026-03-26 | **Session 8: Argala Phase Upgrade (Fix 50)** |
| | Argala internals updated with weighted houses (2/4/11 full; 5/7 half), explicit 3+ unobstructable rule, pure-virodha contribution, and node reverse mode toggle (`VE_ARGALA_NODE_REVERSE_MODE=ketu|both`). Added report diagnostics: unobstructable count + node mode. `analysis/argala.py` + `main.py` |
| 2026-03-26 | **Session 8: Advanced Ashtakvarga Diagnostics (Fix 51)** |
| | Added `sav_profile` to Ashtakvarga output with house threshold status, Vittya (164 threshold), Teertha (76 threshold), H2 vs H12 savings check, and H1 vs H8 protective check. Added helper functions for transit quality and kakshya/PAV evaluation; surfaced Advanced SAV lines in report. `strength/ashtakvarga.py` + `main.py` |
| 2026-03-26 | **Session 8: Yoga Hierarchy Integration (Fix 52)** |
| | Upgraded `score_yoga_activation()` with dasha interlock weighting (MD/AD carrier matching), Nabhasa always-on background handling, and positive-vs-negative contradiction resolution where stronger cluster prevails. Wired with active MD/AD inputs in confidence aggregation. `prediction/confidence.py` |
| 2026-03-26 | **Session 9: Nakshatra Tarabala Source Priority + 9-Tara Mapping (Fix 53)** |
| | Classical Phase-1 Tarabala now prefers live transit Moon Tarabala with static Nakshatra fallback, applies explicit 9-Tara multiplier mapping with Naidhana hard floor, and emits diagnostics (`tarabala_source`, `tara_number`). `prediction/engine.py` |
| 2026-03-26 | **Session 10: Classical Transit House + Vedha Table Alignment (Fix 54)** |
| | Updated `TRANSIT_FAVORABLE`, `VEDHA_TABLE`, and `VIPAREETA_VEDHA_TABLE` for Mercury and Nodes to align with the supplied classical gochara matrix (Mercury includes 2/4; Rahu/Ketu include 10th and corresponding Vedha pairs). `config.py` |
| 2026-03-26 | **Session 10: Ayurdaya Combustion Exemption for Venus/Saturn (Fix 55)** |
| | In longevity Harana logic, combustion halving now excludes Venus and Saturn (classical Ayurdaya exception), while retaining standard combustion handling for other planets. `analysis/medical_astrology.py` |
| 2026-03-26 | **Session 10: Graha Yuddha Venus-Victory Exception (Fix 56)** |
| | Planetary war winner selection now enforces the classical exception that Venus is always victor when involved in Graha Yuddha; non-Venus pairs still use strength hierarchy. `analysis/graha_yuddha.py` |
| 2026-03-26 | **Session 10: Gochar Interpretation Table Consistency (Fix 57)** |
| | Aligned `GOCHAR_EFFECTS` text entries with corrected transit-favorable rules: Mercury 2/4 now favorable in narrative, Saturn 9th corrected to adverse interpretation, and Rahu/Ketu 10th favorable interpretations added. `config.py` |
| 2026-03-26 | **Session 11: Architecture Strict-Mirror Sync (Fix 58)** |
| | Updated architecture tables/formulas to match live code constants and gates: domain houses/negators/planets, transit evaluation inputs and behavior, KP cap details, MD/AD geometry range, and lagna-based transit scoring note. `SYSTEM_ARCHITECTURE.md` |
| 2026-03-26 | **Session 12: Transit/Nakshatra Integration Wiring + Architecture Sync (Fix 59)** |
| | Integrated previously dormant tables/signals into active runtime: `GOCHAR_SCORES` + `BAV_TRANSIT_MULTIPLIERS` in transit scoring, `TRANSIT_FRAME_WEIGHTS` and Nakshatra diagnostic signals in Classical Phase-1 multiplier composition, plus `VE_ENABLE_NAKSHATRA_SIGNALS` rollout flag. Synced strict-mirror docs accordingly. `prediction/transits.py` + `prediction/engine.py` + `analysis/nakshatra_analysis.py` + `SYSTEM_ARCHITECTURE.md` |
