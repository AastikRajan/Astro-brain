# PHASE 2: Wire All Computed Systems Into Prediction Pipeline
# MASTER INSTRUCTION FOR VS CODE OPUS
# Date: March 3, 2026

---

## THE PROBLEM

We have 5+ fully computed systems that produce ZERO influence on prediction output:
1. `computed["yogas"]` (extended) — BYPASSED in favor of basic `detect_all_yogas()`
2. `computed["kota_chakra"]` — display only
3. `computed["sbc_grid"]` — display only
4. `computed["longevity"]` — display only
5. `computed["nadi_amsha"]` — display only

Additionally, these systems are computed but their influence is indirect or incomplete:
6. Avasthas (Baladi/Shayanadi/Deeptadi) — computed but don't modify Shadbala effective output
7. Upagrahas (Gulika/Mandi) — computed but not checked in transit triggers or affliction
8. Special Lagnas (Hora/Ghati/Varnada/Indu) — computed but not used for cross-validation
9. Sahams — computed but not monitored in transit triggers
10. Shodhya Pinda — computed but transit scoring still uses raw BAV
11. Vedha pairs — computed but not gating transits
12. Sudarshana Chakra — computed but not blended into transit score
13. Tajika Varshaphala — computed but not used as convergence validator
14. Kalachakra/Yogini/Narayana Dashas — computed but not used in multi-dasha convergence
15. Prastharashtakavarga — computed but Kaksha timing not extracted

**Phase 2 fixes all of this.** Read MEMORY_INDEX.md and RULEBOOK.md before starting.

---

## PHASE 2A: Fix the Yoga Pipeline (CRITICAL — Do First)

### Problem
`confidence.py` reads `static["yogas"]` (basic list from `detect_all_yogas()`).
`computed["yogas"]` (extended list with DKA, Dhana, Aristha, Nabhasa, grading, cancellations) is NEVER READ.
All the yoga work from Phase 1D is invisible to predictions.

### Fix
In `engine.py`, wherever `static["yogas"]` is set, REPLACE it with the extended yoga list:

```python
# OLD (somewhere in analyze_static or predict):
static["yogas"] = detect_all_yogas(...)

# NEW:
static["yogas"] = static["computed"]["yogas"]  # Use extended yogas with grading
```

OR better — merge them: keep the basic yogas AND add the extended ones, deduplicating by name:
```python
basic_yogas = detect_all_yogas(...)
extended_yogas = static["computed"]["yogas"]
# Merge: extended takes priority (has grading), basic fills gaps
merged = {y["name"]: y for y in basic_yogas}
merged.update({y["name"]: y for y in extended_yogas})
static["yogas"] = list(merged.values())
```

### Then update `score_yoga_activation()` in confidence.py
Currently this function scores yogas. It should now USE the grade field:

```python
def score_yoga_activation(yogas, domain, ...):
    domain_yogas = [y for y in yogas if y.get("domain") == domain or y.get("domain") == "general"]
    if not domain_yogas:
        return 0.0
    
    # Use grade scores from extended yogas
    grade_scores = {"S": 1.0, "A": 0.75, "B": 0.50, "C": 0.25}
    total = sum(grade_scores.get(y.get("grade", "C"), 0.25) for y in domain_yogas)
    # Normalize: cap at 1.0, scale by count
    return min(1.0, total / 3.0)  # 3 S-tier yogas = perfect score
```

This means DKA yoga in a career prediction now actually boosts career confidence. Aristha yoga in health actually lowers it. Dhana yoga in finance actually matters.

### Verify after this change
Run test chart. Compare yoga_activation scores before and after. They should now differ by domain.

---

## PHASE 2B: Wire Avasthas as Shadbala Modifier

### Problem
Avasthas are computed but Shadbala ratios are used raw. A planet with high Shadbala but "Mrita" (dead) Baladi Avastha should behave as effectively weak.

### Fix
Create function `apply_avastha_modifier(shadbala_ratios, avasthas)` in a utils or strength module:

```python
def apply_avastha_modifier(shadbala_ratios, baladi_avasthas):
    """Modify effective Shadbala by Baladi Avastha multiplier."""
    modified = {}
    for planet, ratio in shadbala_ratios.items():
        avastha = baladi_avasthas.get(planet, {})
        multiplier = avastha.get("multiplier", 1.0)
        # Don't let avastha completely zero out — floor at 0.15
        effective_multiplier = max(0.15, multiplier)
        modified[planet] = ratio * effective_multiplier
    return modified
```

Call this EARLY in the prediction pipeline — wherever `shadbala_ratios` is first used:
```python
# In engine.py, after computing shadbala_ratios:
shadbala_ratios = apply_avastha_modifier(shadbala_ratios, static["computed"]["baladi_avasthas"])
```

This makes a "Dead" planet effectively 15% of its Shadbala. A "Youth" planet keeps 100%. This cascades into Promise gate (lord strength), confidence scoring, and everywhere else Shadbala is read.

---

## PHASE 2C: Wire Vedha Into Transit Scoring

### Problem
Transit support score doesn't check if a favorable transit is obstructed by Vedha.

### Fix
In the transit evaluation function (wherever `transit_support` or `score_transit()` is computed):

```python
# After computing base transit score for a planet in a house:
if check_vedha(transit_planet, transit_house, other_planet_transit_houses):
    # Transit is obstructed — nullify its positive contribution
    transit_score_for_this_planet = 0.0
    # OR reduce by 80%: transit_score_for_this_planet *= 0.20
```

Use the Vedha function already implemented in Phase 1E. The key decision: full nullification (classical strict) or 80% reduction (pragmatic). 

**Recommendation:** Use 80% reduction. Classical Vedha is binary (blocked/not), but in practice some effect leaks through. A 0.20 multiplier is a good balance.

Also remember the EXCEPTIONS: Sun/Saturn and Moon/Mercury pairs don't Vedha each other.

---

## PHASE 2D: Wire Sudarshana Chakra Into Transit Score

### Problem
Transit evaluation only checks from Lagna reference frame. Sudarshana adds Moon and Sun reference frames.

### Fix
The Sudarshana evaluation function from Phase 1E returns a weighted composite score. Blend it into the existing transit score:

```python
# In transit scoring:
base_transit_score = ...  # existing computation (Lagna-based)
sudarshana_score = evaluate_sudarshana(transit_data, lagna_sign, moon_sign, sun_sign)

# Blend: 60% existing + 40% Sudarshana
# This preserves backward compatibility while adding the triple reference
transit_support = 0.60 * base_transit_score + 0.40 * sudarshana_score
```

Why 60/40? The existing transit scoring already includes BAV and double transit checks. Sudarshana adds the Moon/Sun reference frames which provide genuine new information, but shouldn't override the detailed existing computation.

---

## PHASE 2E: Wire Kota Chakra Into Health/Crisis Predictions

### Problem
Kota Chakra computes directional vector (inward=danger escalating, outward=retreating) but this doesn't affect health predictions.

### Fix
In the health domain prediction specifically:

```python
# Only for health/longevity domains:
if domain == "health":
    kota_status = static["computed"].get("kota_chakra", {})
    kota_direction = kota_status.get("direction", "neutral")
    
    if kota_direction == "inward":
        # Malefics moving toward inner fort — increase severity
        # Reduce confidence (= higher risk)
        health_confidence *= 0.85  # 15% penalty
    elif kota_direction == "outward":
        # Malefics retreating — crisis resolving
        health_confidence *= 1.10  # 10% boost (cap at ceiling)
```

Also add Kota status to the narrative output for health predictions: "Kota Chakra indicates [escalating/resolving] health conditions."

---

## PHASE 2F: Wire SBC Vedha Into Transit Triggers

### Problem
SBC grid is computed but Vedha piercing isn't checked against transits.

### Fix
After computing SBC Vedha (from Phase 1E), check if any transit planet pierces the natal Moon's nakshatra or the domain-relevant nakshatra:

```python
# In transit evaluation:
sbc_vedhas = check_sbc_vedha(transit_planet, transit_nakshatra, static["computed"]["sbc_grid"])

# Check if natal Moon's nakshatra is pierced
if natal_moon_nakshatra in sbc_vedhas:
    # SBC says this transit directly affects the native
    sbc_activation = True
    
# Use as a MODIFIER on transit strength:
if sbc_activation:
    transit_score *= 1.25  # Transit is 25% more potent when SBC confirms
```

This is a convergence signal: when standard transit analysis AND SBC Vedha both activate, the transit is more likely to produce a tangible event.

---

## PHASE 2G: Wire Multi-Dasha Convergence

### Problem
We compute Vimshottari, Yogini, Kalachakra, Narayana, and conditional dashas. But only Vimshottari feeds into the confidence pipeline. The rest are display only.

### Fix
Create function `compute_dasha_convergence(all_dashas, domain, prediction_date)`:

```python
def compute_dasha_convergence(static, domain, prediction_date):
    """Check if multiple dasha systems agree on the domain being active."""
    systems_checked = 0
    systems_favorable = 0
    
    # Vimshottari (already scored)
    vim_score = static.get("vimshottari_alignment", 0)
    systems_checked += 1
    if vim_score > 0.5: systems_favorable += 1
    
    # Yogini
    yogini = static["computed"].get("yogini_dasha", {})
    if yogini:
        systems_checked += 1
        yogini_planet = yogini.get("current_lord")
        if is_favorable_for_domain(yogini_planet, domain, static):
            systems_favorable += 1
    
    # Kalachakra
    kalachakra = static["computed"].get("kalachakra_dasha", {})
    if kalachakra:
        systems_checked += 1
        kala_sign = kalachakra.get("current_sign")
        if is_sign_favorable_for_domain(kala_sign, domain, static):
            systems_favorable += 1
    
    # Narayana
    narayana = static["computed"].get("narayana_dasha", {})
    if narayana:
        systems_checked += 1
        nar_sign = narayana.get("current_sign")
        if is_sign_favorable_for_domain(nar_sign, domain, static):
            systems_favorable += 1
    
    # Chara Dasha (Jaimini - already partially scored)
    chara_score = static.get("jaimini_alignment", 0)
    if chara_score is not None:
        systems_checked += 1
        if chara_score > 0.5: systems_favorable += 1
    
    # Convergence ratio
    if systems_checked == 0:
        return 0.5  # neutral
    
    convergence = systems_favorable / systems_checked
    return convergence
```

### Where to use this
Feed the convergence ratio into the Bayesian layer as a NEW evidence source:

```python
# In bayesian_layer.py, add a 5th evidence update:
dasha_convergence = compute_dasha_convergence(static, domain, date)
# Use 1.5 pseudo-observations (lighter weight than primary dasha)
alpha += dasha_convergence * 1.5
beta += (1 - dasha_convergence) * 1.5
```

This means when 4/5 dasha systems agree, confidence gets a genuine boost. When they disagree (2/5), it pulls toward neutral. Pure convergence detection.

---

## PHASE 2H: Wire Tajika Varshaphala as Convergence Validator

### Problem
Full Varshaphala system (1217 lines!) computed but contributes nothing to predictions.

### Fix
Create function `score_varshaphala_agreement(varshaphala_data, domain)`:

```python
def score_varshaphala_agreement(varshaphala, domain):
    """Does the solar return year chart agree with natal prediction?"""
    if not varshaphala:
        return 0.5  # neutral if unavailable
    
    score = 0.5  # start neutral
    
    # Check Muntha placement
    muntha_sign = varshaphala.get("muntha_sign")
    muntha_house = varshaphala.get("muntha_house")  # from Varsha Lagna
    if muntha_house in [1, 5, 9, 10, 11]:  # favorable houses
        score += 0.15
    elif muntha_house in [6, 8, 12]:  # unfavorable
        score -= 0.15
    
    # Check Year Lord strength
    year_lord_strength = varshaphala.get("year_lord_strength", 0.5)
    score += (year_lord_strength - 0.5) * 0.2  # scale to ±0.1
    
    # Check Tajika yogas relevant to domain
    tajika_yogas = varshaphala.get("tajika_yogas", [])
    for ty in tajika_yogas:
        if ty.get("type") == "ithasala" and ty.get("domain") == domain:
            score += 0.1  # applying aspect = event likely
        elif ty.get("type") == "ishrafa" and ty.get("domain") == domain:
            score -= 0.05  # separating = event fading
    
    return max(0.0, min(1.0, score))
```

### Wire into confidence pipeline
Add as a new component in the weighted sum:

```python
# In compute_confidence():
c_varsha = score_varshaphala_agreement(static["computed"].get("varshaphala"), domain)

# Add to weighted sum with weight ~0.08
# Redistribute from existing weights (take 0.03 from functional_alignment, 0.03 from kp, 0.02 from jaimini)
```

Or better — add to Bayesian layer as another evidence source with 1.0 pseudo-observations (light weight).

---

## PHASE 2I: Wire Upagrahas Into Affliction Scoring

### Problem
Gulika/Mandi positions computed but not checked for affliction.

### Fix
In the Promise gate or affliction analysis:

```python
# Check if domain-relevant houses have Gulika/Mandi:
gulika_long = static["computed"]["upagrahas"]["gulika"]
gulika_sign = int(gulika_long / 30)
gulika_house = (gulika_sign - lagna_sign) % 12 + 1

# If Gulika is in a domain-relevant house, add affliction penalty
domain_houses = get_domain_houses(domain)
if gulika_house in domain_houses:
    affliction_penalty += 0.10  # 10% affliction

# Also check transit: if current Saturn or Rahu transits natal Gulika position
gulika_transit_activated = is_planet_within_orb(current_saturn_long, gulika_long, orb=5.0)
if gulika_transit_activated:
    transit_affliction += 0.15  # Hidden issue surfacing
```

---

## PHASE 2J: Wire Special Lagnas as Domain Cross-Validators

### Problem  
Hora Lagna (wealth), Ghati Lagna (power), Indu Lagna (wealth) computed but unused.

### Fix
For domain-specific predictions, check the relevant Special Lagna:

```python
# In domain prediction:
if domain == "finance":
    # Check Hora Lagna and Indu Lagna
    hora_lagna_sign = int(static["computed"]["special_lagnas"]["hora_lagna"] / 30)
    indu_lagna_sign = int(static["computed"]["special_lagnas"]["indu_lagna"] / 30)
    
    # Is the finance prediction's key planet well-placed from Hora Lagna?
    # Check if 2nd/11th from Hora Lagna has benefics or strong planets
    hora_2nd = (hora_lagna_sign + 1) % 12
    hora_11th = (hora_lagna_sign + 10) % 12
    
    hora_support = count_benefics_in_signs([hora_2nd, hora_11th], planet_positions)
    if hora_support > 0:
        special_lagna_boost = 0.05 * hora_support  # up to +0.15
    
elif domain == "career":
    # Check Ghati Lagna (power/authority)
    ghati_sign = int(static["computed"]["special_lagnas"]["ghati_lagna"] / 30)
    # Similar check for 10th from Ghati Lagna
```

Add as a small modifier (±5-10%) on the final confidence score. Not a major component — a refinement signal.

---

## PHASE 2K: Wire Shodhya Pinda Into Advanced Transit Timing

### Problem
Transit scoring uses raw BAV. Shodhya Pinda (purified strength after reductions) is computed but unused.

### Fix
In the AV scoring function (`score_ashtakvarga`):

```python
# Currently: uses raw BAV bindus
# Upgrade: blend raw BAV with Shodhya Pinda for refined scoring

raw_bav_score = existing_computation  # keep as-is
pinda = static["computed"].get("shodhya_pinda", {})
pinda_value = pinda.get(transit_planet, 0)

# Normalize Pinda to 0-1 range (typical range is 0-300, varies by planet)
# Use planet-specific normalization
pinda_normalized = min(1.0, pinda_value / PINDA_MAX[transit_planet])

# Blend: 70% raw BAV (proven) + 30% Shodhya Pinda (refined)
av_score = 0.70 * raw_bav_score + 0.30 * pinda_normalized
```

---

## EXECUTION ORDER

1. **2A first** (yoga pipeline fix) — this is the biggest impact, all Phase 1D work becomes active
2. **2B** (avasthas) — cascading effect on all strength-based computations
3. **2C + 2D** (vedha + sudarshana) — transit accuracy improvement
4. **2G** (multi-dasha convergence) — THE convergence principle
5. **2H** (varshaphala) — annual validation
6. **2E + 2F** (kota + SBC) — domain-specific refinements
7. **2I + 2J** (upagrahas + special lagnas) — affliction and cross-validation
8. **2K** (shodhya pinda) — transit refinement

After EACH change: update memory, run test chart, verify EXIT:0 and reasonable confidence ranges.

---

## WEIGHT BUDGET

Adding new signals means redistributing weights. Here's the target:

**Confidence weighted sum (8 → 10 components):**

| Component | Current Best Weight | Target Weight | Change |
|-----------|-------------------|---------------|--------|
| dasha_alignment | 0.20 | 0.18 | -0.02 |
| transit_support (now includes Vedha+Sudarshana) | 0.35 | 0.32 | -0.03 |
| ashtakvarga_support (now includes Pinda) | 0.15 | 0.14 | -0.01 |
| yoga_activation (NOW USING EXTENDED+GRADED) | 0.12 | 0.12 | same |
| kp_confirmation | 0.10 | 0.09 | -0.01 |
| functional_alignment | 0.05 | 0.04 | -0.01 |
| house_lord_strength | 0.00 | 0.00 | same |
| jaimini_sub | 0.03 | 0.03 | same |
| **varshaphala_agreement** (NEW) | — | **0.05** | +0.05 |
| **special_lagna_support** (NEW) | — | **0.03** | +0.03 |

**Bayesian layer (4 → 6 evidence sources):**

| Source | Current Obs | Target Obs | Change |
|--------|------------|------------|--------|
| Prior (yoga+functional) | 4 | 4 | same |
| Dasha | 3 | 3 | same |
| Transit+BAV | 2 | 2 | same |
| KP | 0.2-2.0 | 0.2-2.0 | same |
| **Dasha convergence** (NEW) | — | **1.5** | +1.5 |
| **Varshaphala** (NEW) | — | **1.0** | +1.0 |

Total posterior weight: ~11.2 → ~13.7 pseudo-observations. Reasonable increase.

---

## AFTER PHASE 2

Run the test chart. Compare output to pre-Phase-2 output. Key things to check:
1. Yoga activation scores now DIFFER by domain (career vs finance vs health)
2. Transit scores are modified by Vedha and Sudarshana
3. Multi-dasha convergence appears in output
4. Health predictions show Kota Chakra influence
5. Overall confidence values are still in reasonable range (0.10-0.90)

Bring the before/after comparison to Claude for evaluation. 