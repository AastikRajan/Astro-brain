# VEDIC ENGINE — ARCHITECTURE MAPPING ADDENDUM
## Maps Knowledge Base Items → Actual Code Paths & Functions

**PURPOSE:** This addendum bridges the knowledge base (vedic_engine_knowledge_base.md) with the actual engine architecture discovered by Opus 4.6's pipeline trace. Every fix in the knowledge base now has an exact file path, function name, and insertion point.

**Use this alongside vedic_engine_knowledge_base.md for code changes.**

---

## ACTUAL ENGINE DIRECTORY STRUCTURE

```
vedic_engine/
├── data/
│   ├── loader.py          # load_sample_chart(), build_chart_swe(), parse JSON
│   └── models.py          # BirthInfo, PlanetPosition dataclasses
├── core/                   # Chart math, aspects, house calculations
├── strength/              # Shadbala, Ashtakavarga, Vimshopaka, Bhavabala
├── analysis/              # 20+ modules: yogas, karakas, KP, Jaimini, remedies, etc.
├── timing/                # Dasha systems, transit_analyzer
├── prediction/
│   ├── engine.py          # MASTER ORCHESTRATOR: analyze_static(), analyze_dynamic(), predict()
│   ├── confidence.py      # 7-component weighted sum (25%+20%+15%+13%+12%+8%+7%)
│   ├── bayesian_layer.py  # Beta-conjugate posterior with pseudo-counts
│   ├── fuzzy_confidence.py# scikit-fuzzy inference (falls back to weighted sum)
│   ├── calibration.py     # 25-point hand-tuned isotonic curve
│   ├── promise.py         # Three-Pillar Promise gate (Bhava+Bhavesha+Karaka)
│   └── transits.py        # get_transit_positions() — SWE tier-1
├── ai/
│   └── gpt_reasoner.py    # GPT-4o-mini for 4 structured decision points
main.py                    # Entry point: CLI args, print_domain_report(), output formatting
```

---

## PIPELINE FLOW (4 Stages)

```
main.py CLI
  → loader.py: load_sample_chart() OR build_chart_swe()
    → engine.py: analyze_static(chart)
      → [20+ analysis modules compute natal chart]
    → engine.py: analyze_dynamic(static_data, target_date)
      → [transits, dashas, timing windows]
    → engine.py: predict(static_data, dynamic_data)
      → [per-domain scoring: Career, Finance, Marriage, Health]
      → confidence.py → bayesian_layer.py → fuzzy_confidence.py → calibration.py
      → promise.py (hard gate)
    → main.py: print_domain_report(predictions)
```

---

## EXACT CODE MAPPING: Knowledge Base Item → File & Function

### CRITICAL FIXES (Priority 1-3)

| KB Item | Fix | Exact File | Function/Location | What To Change |
|---------|-----|-----------|-------------------|----------------|
| **§3.1 Domain-specific BAV** | Fix AV=1.00 bug | `prediction/confidence.py` | The `ashtakavarga` component (15% weight) | Currently returns constant 1.00. Replace with domain-specific BAV lookup using `static_data['ashtakavarga']['bhinna']` tables. Map each domain to specific planet BAV + house sign per §3.1 DOMAIN_BAV_MAPPING |
| **§5.1 Double Transit** | Add Jupiter+Saturn hard gate | `prediction/engine.py` | Inside `predict()`, after Promise gate | Add new check: `check_double_transit(domain_houses, static_data, dynamic_data['transit_positions'])`. If fails, cap timing_score at 0.3 |
| **§9.3 Double-counting** | Fix Bayesian inflation | `prediction/bayesian_layer.py` | `compute_bayesian_confidence()` | Merge dasha_alignment + yoga_activation into single timing group with 3 pseudo-obs total (not 3+2). Remove house_lord_strength from both confidence.py AND bayesian update |

### HIGH PRIORITY FIXES (Priority 4-11)

| KB Item | Fix | Exact File | What To Change |
|---------|-----|-----------|----------------|
| **§4.1 Jaimini→Pipeline** | Wire Jaimini into scoring | `prediction/engine.py` → `predict()` | Currently: Jaimini data computed in `analyze_static()` under keys like `chara_karakas`, `arudha_padas`, `rashi_drishti`, `karakamsha`. Add new function `jaimini_confidence_score()` per §4.1, feed result as 8th component into `confidence.py` weighted sum (steal weight from existing components or add at ~10%) |
| **§2.2 Dasha Quality** | Ishta/Kashta Phala | `strength/shadbala.py` (new function) + `prediction/engine.py` | Shadbala values come from JSON input OR SWE-enhanced recomputation. Add `compute_ishta_kashta()` to shadbala module. Create `timing/dasha_quality.py` that combines Ishta/Kashta + functional role + D9 dignity + retrograde status into single quality score. Replace binary dasha activation with graded quality |
| **§5.2 Sudarshana Chakra** | Triple transit reference | `prediction/transits.py` (extend) | `get_transit_positions()` already uses SWE for live positions. Add `sudarshana_transit_score()` that evaluates transits from Lagna, Moon, AND Sun. Feed into `transit_support` component of confidence.py |
| **§1.1 Neecha Bhanga** | Complete 8 conditions | `analysis/` (yoga module) | Whichever module handles yoga detection. Add `check_neecha_bhanga()` with all 8 conditions + Cancer lagna exception + proximity-to-deep-debilitation modifier. Feed score into yoga_activation |
| **§5.4 Bhrigu Bindu** | Transit activation | `prediction/engine.py` → `analyze_dynamic()` | Bhrigu Bindu already computed in `analyze_static()` (seen as 214.62° in sample output). In `analyze_dynamic()`, add transit check: when Jupiter/Saturn/Rahu crosses BB degree (±5° orb), flag activation with house identification |
| **§1.6 Yoga Expansion** | 50→300+ yogas | `analysis/` (yoga module) | Add missing yoga categories per §1.6: Dharma-Karmadhipati, Daridra, Aristha, complete Dhana set, Pravrajya, all 32 Nabhasa yogas. Each yoga needs: detection logic, strength gradation, domain mapping |
| **§5.3 Sarvatobhadra** | Nakshatra transit system | New file: `timing/sarvatobhadra.py` | Completely new module. Build 9×9 grid, implement Vedha detection (across/fore/hind), score against Janma Nakshatra. Feed as independent cross-validator into transit_support |
| **§7.2 KP Placidus** | Fix house system inconsistency | `analysis/` (KP module) | KP analysis currently uses Whole Sign house numbers. Switch to Placidus cusps for KP signification chain. `build_chart_swe()` in loader.py can compute Placidus cusps via SWE — wire those through to KP module |

### MEDIUM PRIORITY FIXES

| KB Item | Fix | Exact File | What To Change |
|---------|-----|-----------|----------------|
| **§6.3 Combustion** | Per-planet orbs | `core/` (planet module) | Replace single combustion threshold with §6.3 COMBUSTION_ORBS table. Use graduated strength (not binary). Affects: Pancha Mahapurusha cancellation, yoga strength, dasha quality |
| **§6.1 Mrityu Bhaga** | Complete degree table | New: `analysis/special_degrees.py` | Add MRITYU_BHAGA lookup table per §6.1. Apply `mrityu_bhaga_modifier()` (0.2-1.0 penalty) to planet strength calculations and Promise gate |
| **§6.2 Gandanta** | Water-fire junction scoring | New: `analysis/special_degrees.py` | Add `gandanta_severity()` per §6.2. Apply to planets within 1° of Cancer-Leo, Scorpio-Sagittarius, Pisces-Aries junctions |
| **§6.5 Maturity Ages** | Planet maturity timing | `timing/dasha_quality.py` (new) | Add PLANET_MATURITY_AGE table per §6.5. Apply `maturity_modifier()` to reduce confidence for predictions involving planets below maturity age |
| **§10.2 Monte Carlo** | Birth time sensitivity | `prediction/engine.py` | Wrap `predict()` in sensitivity loop: run ±5 min in 1-min steps. If predictions flip, flag "birth_time_sensitive" and multiply confidence by stability factor |

---

## DATA FLOW NOTES FOR OPUS 4.6

### Where Birth Data Lives
- **Default path:** `loader.py` → `load_sample_chart()` → hardcoded JSON dict with planet longitudes from AstroSage export
- **SWE path:** `loader.py` → `build_chart_swe()` → computes ALL positions from birth date/time/place using pyswisseph. **This exists but isn't the default.**
- **User JSON path:** `python main.py chart.json` → reads external JSON file

### Where Transit Data Lives
- `prediction/transits.py` → `get_transit_positions(date)` → SWE tier-1 (pyswisseph `calc_ut`) → astropy fallback → ephem fallback → hardcoded positions
- Transit positions are LIVE and REAL when SWE is installed

### Where Shadbala Lives
- `strength/shadbala.py` — computes from planet positions
- SWE-enhanced: uses real sunrise/sunset, solar declination, Mesha Sankranti for accurate Kala Bala
- Values in the sample chart come from JSON input, but engine RECOMPUTES with SWE enhancement

### Where Ashtakavarga Lives
- `strength/` (ashtakavarga module) — computes BAV tables from planet sign positions
- Currently: CORRECTLY computes BAV/SAV from natal positions
- BUG: confidence.py returns constant 1.00 for AV component across all domains (not using domain-specific BAV)

### Where Confidence Scoring Lives
- `prediction/confidence.py` — 7-component weighted sum:
  ```
  dasha_alignment: 25%
  transit_support: 20%
  ashtakavarga: 15%  ← BUG: always 1.00
  yoga_activation: 13%
  kp_sublord: 12%
  functional_role: 8%
  house_lord_strength: 7%  ← DOUBLE-COUNTED with Promise
  ```
- `prediction/bayesian_layer.py` — Beta posterior with:
  - Prior: natal yoga + functional role + house lord strength
  - Likelihood: dasha(3 obs) + transit+AV(2 obs) + KP(2 obs, binary)
- `prediction/fuzzy_confidence.py` — scikit-fuzzy or weighted-sum fallback
- `prediction/promise.py` — Three-pillar hard gate (Bhava + Bhavesha + Karaka)
- `prediction/calibration.py` — 25-point isotonic curve (hand-authored)

### Where the 4 GPT Decision Points Fire
- `ai/gpt_reasoner.py` — called during `predict()` for:
  1. Yoga fructification in current dasha
  2. Dasha conflict resolution
  3. KP ambiguity resolution
  4. Adaptive weight tuning
- Model: gpt-4o-mini, JSON mode, max_tokens 200-350
- Session-cached by MD5 hash
- Falls back silently if no API key

### Where Jaimini Data Lives (Computed but Not Used in Scoring)
- `analyze_static()` computes:
  - `chara_karakas` — AK, AmK, BK, MK, PK, GK, DK assignments
  - `arudha_padas` — AL, UL, A7, A10
  - `rashi_drishti` — Jaimini sign aspects
  - `karakamsha` — AK's D9 sign analysis
  - Chara Dasha periods
  - Sthira Karakas, Svamsha
- `predict()` uses a `jaimini_subscore` key but it's lightweight — just checks if Chara Dasha sign relates to domain houses
- **NEEDED:** Full integration per §4.1 with UL for marriage, A10 for career, Karakamsha planet analysis

---

## WHAT OPUS 4.6 SHOULD DO FIRST (Recommended Order)

### Phase 1: Foundation Fixes (do first, everything else builds on these)
1. **Fix AV=1.00 bug** — `confidence.py`: replace constant with domain-specific BAV lookup
2. **Fix double-counting** — `bayesian_layer.py`: merge dasha+yoga groups, remove house_lord_strength overlap
3. **Add Double Transit gate** — `engine.py predict()`: Jupiter+Saturn check as required condition

### Phase 2: Enhance Existing Systems
4. **Dasha quality scoring** — new `timing/dasha_quality.py` + modify engine.py
5. **Wire Jaimini into pipeline** — modify `engine.py predict()` and `confidence.py`
6. **Per-planet combustion** — modify combustion check in `core/`
7. **Complete Neecha Bhanga** — enhance yoga detection module

### Phase 3: Add New Systems
8. **Sudarshana Chakra** — new module in `timing/`
9. **Bhrigu Bindu activation** — wire existing computation to transit check in `analyze_dynamic()`
10. **Mrityu Bhaga + Gandanta** — new `analysis/special_degrees.py`
11. **Sarvatobhadra Chakra** — new `timing/sarvatobhadra.py`
12. **Yoga expansion** — bulk additions to yoga detection module

### Phase 4: Architecture
13. **Prediction time windows** — modify prediction schema in `engine.py`
14. **KP Placidus fix** — modify KP analysis module
15. **Monte Carlo sensitivity** — wrapper in `engine.py`
16. **Medical guardrails** — modify `main.py` print functions

---

## SAMPLE INTEGRATION PATTERNS

### Pattern: Adding a New Confidence Component
```python
# In confidence.py, the weighted sum currently has 7 components totaling 100%.
# To add Jaimini sub-score (§4.1):
# Option A: Reduce existing weights and add 8th component
# Option B: Replace house_lord_strength (7%, already double-counted) with Jaimini

# Recommended: Option B — kills two bugs with one fix
# BEFORE: house_lord_strength: 7%
# AFTER:  jaimini_subscore: 7%  (or 10% by stealing from others)
```

### Pattern: Adding a New Hard Gate
```python
# In engine.py predict(), Promise gate already exists as hard floor.
# Double Transit check goes AFTER Promise, BEFORE confidence scoring:
# 
# promise = compute_promise(domain, static_data)
# if promise == 0.0:
#     return {"confidence": 0.0, "status": "DENIED"}
# 
# double_transit = check_double_transit(domain, static_data, dynamic_data)
# if not double_transit:
#     timing_cap = 0.30  # Major events can't manifest without DT
# else:
#     timing_cap = 1.00
#
# confidence = compute_confidence(...) * timing_cap
```

### Pattern: Using Existing Jaimini Data
```python
# In engine.py predict(), Jaimini data is already available:
# static_data['chara_karakas']  → dict with AK, AmK, etc.
# static_data['arudha_padas']   → dict with AL, UL, A7, A10, etc.
# static_data['karakamsha']     → sign + planets analysis
# dynamic_data['chara_dasha']   → current Chara Dasha sign
#
# Just need to SCORE these and feed into confidence pipeline
```

---

## KEY WARNINGS FOR OPUS 4.6

1. **DON'T break the SWE fallback chain.** Transit positions have a 4-tier fallback: pyswisseph → astropy → ephem → hardcoded. Any new module that needs transit data should call `get_transit_positions()` from transits.py, not compute independently.

2. **DON'T modify the Promise gate semantics.** The three-pillar gate (Bhava + Bhavesha + Karaka) is architecturally sound. ADD gates alongside it (like Double Transit), don't replace.

3. **RESPECT the JSON input path.** The sample chart comes from a hardcoded JSON dict. Any new computation that needs data not in the JSON (like Placidus cusps) should use `build_chart_swe()` conditionally — check if SWE is available first.

4. **KEEP the scikit-fuzzy fallback.** `fuzzy_confidence.py` falls back to weighted sum if scikit-fuzzy isn't installed. Any new fuzzy rules must have a non-fuzzy fallback.

5. **THE `is_daytime` AND `paksha` ARE HARDCODED.** Several conditional dasha systems depend on these. Fixing them requires SWE sunrise computation — which `build_chart_swe()` already has. Wire it through to the conditional dasha eligibility checks.

6. **Ashtakavarga is CORRECTLY COMPUTED** — the data exists in `static_data['ashtakavarga']`. The bug is only in `confidence.py` not USING the per-planet BAV for domain scoring.

7. **GPT reasoner is sandboxed.** Its 4 decision points feed math, not narrative. Don't expand its role without careful thought — it adds API latency and cost per prediction.