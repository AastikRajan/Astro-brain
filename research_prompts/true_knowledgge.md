# VEDIC ASTROLOGY ENGINE — COMPLETE CLASSICAL KNOWLEDGE BASE
## Technical Reference for AI Code Agent (Opus 4.6 in VS Code)

**PURPOSE:** This document contains every missing rule, gap, classical technique, and integration logic needed to upgrade the Vedic astrology prediction engine from ~40% to 90% accuracy. Each section is structured for direct code translation.

**HOW TO USE THIS DOCUMENT:**
- Each GAP has: WHAT'S MISSING → CLASSICAL RULE → IMPLEMENTATION LOGIC → WHERE TO ADD → PRIORITY
- Rules are stated as deterministic logic (if/then/else) ready for Python translation
- Data tables are given in array/dict format where possible
- Integration points reference the existing engine architecture

---

# SECTION 1: PARASHARI SYSTEM — MISSING YOGA RULES

## 1.1 NEECHA BHANGA (CANCELLATION OF DEBILITATION) — COMPLETE 8 CONDITIONS

**GAP:** Engine likely checks only 1-2 conditions. Classical texts describe 8 distinct cancellation conditions, each with different strength levels.

**SOURCE:** Phaladeepika Ch.7 Shloka 26+, BPHS, Jataka Parijata, Saravali

**ALL 8 CONDITIONS (implement as scored checklist):**

```python
NEECHA_BHANGA_CONDITIONS = {
    1: "Dispositor (lord of sign where planet is debilitated) is in Kendra from Lagna",
    2: "Dispositor is in Kendra from Moon",
    3: "Lord of planet's exaltation sign is in Kendra from Lagna",
    4: "Lord of planet's exaltation sign is in Kendra from Moon",
    5: "Debilitated planet is in Parivartana Yoga (exchange) with its dispositor",
    6: "Debilitated planet is conjunct an exalted planet in same sign",
    7: "Dispositor of debilitated planet aspects the debilitated planet",
    8: "Debilitated planet is exalted in Navamsha (D9)"
}
```

**SCORING LOGIC:**
```python
def score_neecha_bhanga(planet, chart):
    conditions_met = count_conditions(planet, chart)  # 0-8
    if conditions_met == 0:
        return 0.0  # No cancellation
    elif conditions_met == 1:
        return 0.3  # Partial cancellation — reduces damage but no Raja Yoga
    elif conditions_met == 2:
        return 0.6  # Strong cancellation — can produce Raja Yoga
    elif conditions_met >= 3:
        return 0.9  # Very strong — Neecha Bhanga RAJA Yoga confirmed
    
    # CRITICAL MODIFIER: Closer to exact debilitation degree = STRONGER cancellation
    # (per Devakeralam: "the more a debilitated planet is close to its highest 
    #  debilitation degree, the more powerful would be its neecha bhanga")
    debilitation_proximity = 1.0 - abs(planet.degree - DEEP_DEBILITATION[planet.name]) / 30.0
    score *= (0.7 + 0.3 * debilitation_proximity)
    
    # EXCEPTION (Devakeralam): For CANCER ASCENDANT, Neecha Bhanga Raja Yoga 
    # does NOT function — it obstructs prosperity instead
    if chart.lagna == "Cancer":
        score *= 0.3  # Severely diminished
    
    return score
```

**ACTIVATION TIMING:**
- Neecha Bhanga remains DORMANT until Dasha/Bhukti of the debilitated planet OR its dispositor
- Also activates at planet's MATURITY AGE (see Section 8.10)
- Must check D9 and D10 for confirmation — if planet is strong in D9/D10, cancellation is confirmed

**WHERE TO ADD:** `analysis/yoga_identifier.py` — add `check_neecha_bhanga()` function, feed score into Promise gate and yoga_activation confidence component

**PRIORITY:** HIGH — This single fix can flip predictions for any chart with debilitated planets

---

## 1.2 VIPARITA RAJA YOGA — COMPLETE RULES WITH CANCELLATION

**GAP:** Engine may detect basic VRY but miss cancellation conditions and strength gradation.

**SOURCE:** BPHS, Phaladeepika, Uttara Kalamrita

**THREE TYPES:**
```python
VIPARITA_RAJA_YOGAS = {
    "Harsha": {"lord": 6, "placed_in": [6, 8, 12], "effect": "Victory over enemies, good health"},
    "Sarala": {"lord": 8, "placed_in": [6, 8, 12], "effect": "Longevity, sudden gains, occult knowledge"},
    "Vimala": {"lord": 12, "placed_in": [6, 8, 12], "effect": "Spiritual growth, foreign gains, liberation"}
}
```

**FORMATION RULES:**
1. Lord of 6th, 8th, or 12th house is placed in another dusthana (6th, 8th, or 12th)
2. Two dusthana lords in mutual aspect also qualifies
3. Two dusthana lords in conjunction in a dusthana house = strongest form

**CANCELLATION CONDITIONS (CRITICAL — often missed):**
```python
def is_vry_cancelled(dusthana_lord, chart):
    # VRY is CANCELLED if:
    # 1. Lord of Trikona (1,5,9) is ALSO the dusthana lord (dual ownership)
    if dusthana_lord.also_lords_trikona(chart):
        return True
    # 2. Any dusthana lord involved in Parivartana Yoga
    if dusthana_lord.in_parivartana():
        return True  
    # 3. Lords of 10th or Trikona houses are PRESENT in the dusthana 
    #    where VRY is forming
    if trikona_or_10th_lord_in_same_dusthana(dusthana_lord, chart):
        return True
    # 4. VRY planet is aspected by lords of 2nd, 5th, or 9th houses
    #    (benefic association dilutes the "evil cancelling evil" mechanism)
    if aspected_by_lords_of([2, 5, 9], dusthana_lord, chart):
        return True  # Debated — some reduce rather than cancel
    return False
```

**RESULTS PATTERN:** VRY gives results AFTER suffering/crisis first, then sudden reversal. Timing = Dasha of the VRY-forming planet.

**WHERE TO ADD:** `analysis/yoga_identifier.py` — enhance VRY detection with cancellation checks

**PRIORITY:** MEDIUM

---

## 1.3 PANCHA MAHAPURUSHA YOGA — CANCELLATION RULES

**GAP:** Engine detects formation but likely misses cancellation conditions.

**FIVE YOGAS:**
```python
PANCHA_MAHAPURUSHA = {
    "Ruchaka":  {"planet": "Mars",    "condition": "own/exalted sign in Kendra"},
    "Bhadra":   {"planet": "Mercury", "condition": "own/exalted sign in Kendra"},
    "Hamsa":    {"planet": "Jupiter", "condition": "own/exalted sign in Kendra"},
    "Malavya":  {"planet": "Venus",   "condition": "own/exalted sign in Kendra"},
    "Shasha":   {"planet": "Saturn",  "condition": "own/exalted sign in Kendra"}
}
```

**CANCELLATION CONDITIONS:**
1. Planet is COMBUST (within combustion orb of Sun) → Yoga cancelled
2. Planet is in Planetary War (Graha Yuddha) and LOSES → Yoga severely weakened
3. Planet is RETROGRADE → Debated: some say strengthens, classical view = erratic results
4. Planet is aspected by its ENEMY → Yoga weakened proportionally
5. Planet is in 6th, 8th from Moon sign → Yoga gives delayed/reduced results
6. Planet has low Shadbala (below minimum threshold) → Yoga exists on paper but won't deliver

**STRENGTH GRADATION:**
```python
def grade_mahapurusha(planet, chart):
    base = 1.0
    if planet.is_combust: base *= 0.1  # Nearly cancelled
    if planet.lost_graha_yuddha: base *= 0.3
    if planet.is_retrograde: base *= 0.8  # Mild reduction
    if planet.aspected_by_enemy: base *= 0.6
    if planet.shadbala_ratio < 1.0: base *= planet.shadbala_ratio
    # Exalted in Kendra > Own sign in Kendra
    if planet.is_exalted: base *= 1.2
    return min(base, 1.0)
```

**WHERE TO ADD:** `analysis/yoga_identifier.py` — add cancellation checks to existing Mahapurusha detection

**PRIORITY:** MEDIUM

---

## 1.4 YOGA KARAKAS — FUNCTIONAL BENEFIC/MALEFIC COMPLETE RULES

**GAP:** Verify engine implements ALL the nuanced rules from BPHS Ch.34

**SOURCE:** BPHS Chapter 34 (Yoga Karakas), Uttara Kalamrita

**COMPLETE RULES PER LAGNA (CRITICAL TABLE):**

```python
YOGA_KARAKA_RULES = {
    # For each Lagna: yogakaraka planets, functional malefics, maraka planets
    "Aries": {
        "yogakaraka": ["Sun"],  # Lords 5th(Leo)
        "strong_benefic": ["Jupiter"],  # Lords 9th + 12th, but 9th Trikona dominant
        "functional_malefic": ["Mercury", "Saturn"],  # Mercury: 3rd+6th, Saturn: 10th+11th
        "maraka": ["Venus"],  # 2nd + 7th lord = double maraka
        "notes": "Saturn owns Kendra(10th) + Trishadi(11th) = malefic despite Kendra ownership"
    },
    "Taurus": {
        "yogakaraka": ["Saturn"],  # Lords 9th(Capricorn) + 10th(Aquarius) = Dharma-Karma Adhipati
        "strong_benefic": ["Mercury"],
        "functional_malefic": ["Jupiter", "Venus"],  # Jupiter: 8th+11th, Venus: 1st+6th
        "maraka": ["Mars"],  # 7th + 12th
        "notes": "Jupiter is MOST malefic for Taurus — 8th+11th both bad houses"
    },
    "Gemini": {
        "yogakaraka": ["Venus"],  # 5th + 12th, but 5th Trikona dominant
        "strong_benefic": ["Saturn"],  # 8th+9th, but 9th dominant
        "functional_malefic": ["Mars"],  # 6th+11th
        "maraka": ["Jupiter"],  # 7th + 10th
        "notes": "Saturn despite 8th lordship gives good results due to 9th"
    },
    "Cancer": {
        "yogakaraka": ["Mars"],  # Lords 5th(Scorpio) + 10th(Aries) = Dharma-Karma Adhipati
        "strong_benefic": ["Jupiter"],  # 6th+9th, 9th dominant
        "functional_malefic": ["Venus", "Mercury"],  # Venus: 4th+11th, Mercury: 3rd+12th
        "maraka": ["Saturn"],  # 7th + 8th = worst planet for Cancer
        "notes": "Mars is THE Yogakaraka — 5th+10th Trikona+Kendra"
    },
    "Leo": {
        "yogakaraka": ["Mars"],  # Lords 4th+9th = Kendra+Trikona
        "strong_benefic": ["Sun", "Jupiter"],
        "functional_malefic": ["Mercury"],  # 2nd+11th
        "maraka": ["Saturn"],  # 6th + 7th
        "notes": "Mars gives excellent results for Leo lagna"
    },
    "Virgo": {
        "yogakaraka": ["Venus"],  # 2nd+9th, 9th Trikona dominant
        "strong_benefic": ["Mercury"],
        "functional_malefic": ["Mars", "Moon"],  # Mars: 3rd+8th, Moon: 11th
        "maraka": ["Jupiter"],  # 4th+7th, 7th maraka aspect
        "notes": "Jupiter is both Kendra lord AND maraka"
    },
    "Libra": {
        "yogakaraka": ["Saturn"],  # Lords 4th(Capricorn) + 5th(Aquarius) = Kendra+Trikona
        "strong_benefic": ["Mercury", "Venus"],
        "functional_malefic": ["Jupiter"],  # 3rd+6th
        "maraka": ["Mars"],  # 2nd + 7th = double maraka
        "notes": "Saturn is THE Yogakaraka — 4th+5th"
    },
    "Scorpio": {
        "yogakaraka": ["Jupiter"],  # Lords 2nd+5th, 5th Trikona dominant
        "strong_benefic": ["Moon", "Sun"],
        "functional_malefic": ["Mercury", "Venus"],  # Mercury: 8th+11th, Venus: 7th+12th
        "maraka": ["Venus"],  # 7th + 12th
        "notes": "Moon lords 9th = strong benefic"
    },
    "Sagittarius": {
        "yogakaraka": ["Sun"],  # Lords 9th (Leo)
        "strong_benefic": ["Mars"],  # 5th+12th, 5th dominant
        "functional_malefic": ["Venus"],  # 6th+11th
        "maraka": ["Mercury"],  # 7th + 10th
        "notes": "Mars despite 12th lordship is benefic due to 5th Trikona"
    },
    "Capricorn": {
        "yogakaraka": ["Venus"],  # Lords 5th(Taurus) + 10th(Libra) = Trikona+Kendra
        "strong_benefic": ["Mercury", "Saturn"],
        "functional_malefic": ["Mars", "Jupiter"],  # Mars: 4th+11th, Jupiter: 3rd+12th
        "maraka": ["Moon"],  # 7th lord
        "notes": "Venus is THE Yogakaraka — 5th+10th"
    },
    "Aquarius": {
        "yogakaraka": ["Venus"],  # Lords 4th(Taurus) + 9th(Libra) = Kendra+Trikona
        "strong_benefic": ["Saturn"],
        "functional_malefic": ["Jupiter", "Moon"],  # Jupiter: 2nd+11th, Moon: 6th
        "maraka": ["Sun"],  # 7th lord
        "notes": "Venus is THE Yogakaraka — 4th+9th"
    },
    "Pisces": {
        "yogakaraka": ["Mars"],  # Lords 2nd+9th, 9th Trikona dominant
        "strong_benefic": ["Moon", "Jupiter"],
        "functional_malefic": ["Saturn", "Venus", "Sun", "Mercury"],
        "maraka": ["Mercury"],  # 4th+7th, 7th maraka
        "notes": "Mars and Moon are the primary benefics"
    }
}
```

**KEY BPHS RULES (Ch.34) — often partially implemented:**
1. Benefics owning Kendras LOSE benefic power (Kendradhipati Dosha)
2. Malefics owning Kendras LOSE malefic power
3. Trikona lords are ALWAYS auspicious
4. Lords of 3rd, 6th, 11th (Trishadi) give EVIL effects
5. 8th lord's effects depend on association
6. 12th lord's effects depend on association
7. When a planet owns BOTH a Kendra and Trikona = Yogakaraka (most auspicious)
8. **ASCENDING ORDER RULE:** Among each group, significance increases: e.g., among Trikonas, 9th > 5th > 1st
9. 8th lord is NOT auspicious because it's 12th from 9th house (Bhagya)
10. If 8th lord ALSO owns 3rd, 7th, or 11th = specifically HARMFUL

**WHERE TO ADD:** `analysis/functional_benefics.py` — verify complete implementation, add missing lagna-specific rules

**PRIORITY:** HIGH — This is the foundation of the entire prediction system

---

## 1.5 SPECIAL ASPECTS (DRISHTI) — PARTIAL ASPECT PERCENTAGES

**GAP:** Engine may implement special aspects as binary. Classical texts give graduated percentages.

**SOURCE:** BPHS, Saravali

```python
# Standard 7th aspect = 100% for all planets
# Special aspects with classical percentages:

ASPECT_STRENGTHS = {
    "Mars": {
        4: 0.75,   # 4th house aspect = 3/4 strength
        7: 1.00,   # 7th house = full
        8: 1.00,   # 8th house = full (special)
    },
    "Jupiter": {
        5: 1.00,   # 5th house = full (special)
        7: 1.00,   # 7th house = full
        9: 1.00,   # 9th house = full (special)
    },
    "Saturn": {
        3: 1.00,   # 3rd house = full (special)
        7: 1.00,   # 7th house = full
        10: 1.00,  # 10th house = full (special)
    },
    # ALL planets also have partial aspects:
    "all_planets": {
        3: 0.25,   # 3rd/11th = 1/4 strength
        4: 0.50,   # 4th/10th = 1/2 strength  
        5: 0.75,   # 5th/9th = 3/4 strength
        7: 1.00,   # 7th = full
        8: 0.75,   # 8th = 3/4 strength
        9: 0.50,   # 9th = 1/2 strength (except Jupiter = full)
        10: 0.25,  # 10th = 1/4 strength (except Saturn = full)
    }
}
```

**INTEGRATION:** These partial aspects should feed into Drig Bala (Shadbala component) AND into yoga detection and transit analysis. Currently the engine likely uses binary aspects.

**WHERE TO ADD:** `core/aspects.py` or equivalent — replace binary aspect with graduated strength

**PRIORITY:** MEDIUM-HIGH — Affects every aspect-based calculation in the engine

---

## 1.6 RAJA YOGA COMPLETE LIST — MISSING CATEGORIES

**GAP:** Engine has 50+ yogas. Classical texts describe 300+. Key missing categories:

### A. DHARMA-KARMADHIPATI YOGA (Most Important Raja Yoga)
```python
# Lord of 9th and Lord of 10th in conjunction, mutual aspect, or exchange
# This is THE premier Raja Yoga — stronger than any other single combination
def check_dharma_karma_yoga(chart):
    lord_9 = chart.house_lord(9)
    lord_10 = chart.house_lord(10)
    if lord_9.conjunct(lord_10) or lord_9.mutual_aspect(lord_10) or lord_9.exchange(lord_10):
        strength = min(lord_9.shadbala_ratio, lord_10.shadbala_ratio)
        return {"present": True, "strength": strength, "type": "Dharma-Karmadhipati"}
```

### B. DARIDRA YOGAS (Poverty Yogas — often completely missing)
```python
DARIDRA_YOGAS = [
    "Lord of 11th in 6th, 8th, or 12th house",
    "Lord of 11th conjunct malefic without benefic aspect",
    "Lord of 2nd in 6th, 8th, or 12th without benefic aspect",  
    "All benefics in 6th, 8th, 12th houses",
    "Lord of 9th in 6th and lord of 6th in 9th (exchange)",
    "Jupiter combust + lord of 2nd debilitated",
    "Moon in Kendra aspected only by malefics (Kemdruma Yoga)",
]
```

### C. ARISTHA YOGAS (Suffering/Affliction Yogas)
```python
ARISTHA_YOGAS = [
    "Lord of 8th in Lagna aspected by malefic",
    "Lord of Lagna in 8th aspected by malefic",
    "Malefics in 6th, 8th, 12th without benefic aspect",
    "Lagna lord weak + Moon weak + no benefic in Kendra",
    "All planets in 4th and 10th houses (Sarpa Yoga)",
]
```

### D. DHANA YOGAS (Wealth — Complete Set)
```python
DHANA_YOGA_RULES = [
    # Primary Dhana Yogas
    "Lord of 2nd + Lord of 11th in conjunction/aspect/exchange",
    "Lord of 5th + Lord of 9th connected (Lakshmi Yoga variant)",
    "Lord of 1st + Lord of 2nd + Lord of 11th all connected",
    "Jupiter in 2nd or 11th in own/exalted sign",
    # Specific named Dhana Yogas
    "Lakshmi Yoga: Lord of 9th in own/exalted sign in Kendra/Trikona + strong Lagna lord",
    "Kubera Yoga: Lord of 2nd exalted + Jupiter in 11th",
    "Chandra-Mangal Yoga: Moon + Mars conjunction → wealth through self-effort",
    "Guru-Mangal Yoga: Jupiter + Mars conjunction → wealth through knowledge",
]
```

### E. PRAVRAJYA YOGAS (Renunciation/Spiritual Yogas)
```python
PRAVRAJYA_YOGAS = [
    "4+ planets in one house including lord of 10th",
    "Moon in Drekkana of Saturn aspected by Saturn",
    "Lord of Lagna + Moon both in Navamsha of Saturn aspected by Saturn",
    "Saturn alone in 10th aspecting Lagna lord + all benefics in 6,8,12",
]
```

### F. NABHASA YOGAS (32 Pattern-Based Yogas from BPHS Ch.35)
```python
# Based on distribution of planets across houses
NABHASA_YOGAS = {
    # Akriti (Shape) Yogas - 20 types
    "Rajju": "All planets in movable signs → wandering, earning abroad",
    "Musala": "All planets in fixed signs → honor, wealth, firmness",
    "Nala": "All planets in dual signs → uneven physique, accumulating money",
    "Mala": "All benefics in 3 consecutive Kendras → ever happy, conveyances",
    "Sarpa": "All malefics in 3 consecutive Kendras → crooked, cruel, poor",
    "Gada": "All planets in 2 consecutive Kendras → efforts for wealth",
    "Shakata": "All planets in 1st and 7th houses → poverty, disease",
    "Shringataka": "All planets in Trikonas → happiness, some comforts",
    "Hala": "All planets in 2nd, 6th, 10th (or 3,7,11 or 4,8,12)",
    "Vajra": "All benefics in 1st+7th, malefics in 4th+10th → happy beginning/end",
    "Yava": "All benefics in 4th+10th, malefics in 1st+7th → happy middle period",
    "Kamala": "All planets in Kendras → very wealthy, virtuous, famous, long-lived",
    "Vaapi": "All planets in Panapharas (2,5,8,11) or Apoklimas (3,6,9,12) → moderate",
    # Sankhya (Number) Yogas - 7 types
    "Vallaki/Veena": "All 7 planets in 7 consecutive signs → musical talent, happy",
    "Dama": "All 7 in 6 consecutive signs → liberal, generous",
    "Pasha": "All 7 in 5 consecutive signs → imprisonment or servitude possible",
    "Kedara": "All 7 in 4 consecutive signs → agriculture, honest living",
    "Shoola": "All 7 in 3 consecutive signs → sharp, brave, poor, warlike",
    "Yuga": "All 7 in 2 consecutive signs → heretic, poor, without learning",
    "Gola": "All 7 in 1 sign → poor, dirty, ignorant, wandering",
    # Dala (Branch) Yogas
    "Maala": "Benefics in 3 Kendras → comforts, conveyances",
    "Sarpa_dala": "Malefics in 3 Kendras → suffering, cruelty",
}
```

**WHERE TO ADD:** `analysis/yoga_identifier.py` — add missing yoga categories. Feed all detected yogas into `yoga_activation` confidence component with strength grading.

**PRIORITY:** HIGH — The 50→300+ yoga expansion is one of the highest-ROI changes

---

# SECTION 2: SHADBALA — COMPLETE COMPUTATION & INTEGRATION

## 2.1 MINIMUM SHADBALA REQUIREMENTS (BPHS 27.32-33)

```python
# Minimum Shadbala in Virupas for each planet to be considered "strong"
SHADBALA_MINIMUM = {
    "Sun": 390,
    "Moon": 360,
    "Mars": 300,
    "Mercury": 420,
    "Jupiter": 390,
    "Venus": 330,
    "Saturn": 300
}

# Alternative (Phaladeepika) in Rupas (divide Virupas by 60):
SHADBALA_MIN_RUPAS = {
    "Sun": 6.5, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
    "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0
}
```

## 2.2 ISHTA PHALA AND KASHTA PHALA — DASHA QUALITY PREDICTOR

**GAP:** Engine likely computes Shadbala total but doesn't derive Ishta/Kashta Phala for dasha quality scoring.

**SOURCE:** BPHS, Phaladeepika

```python
def compute_ishta_kashta(planet):
    """
    Ishta Phala = sqrt(Uccha_Bala * Chesta_Bala)
    Kashta Phala = sqrt((60 - Uccha_Bala) * (60 - Chesta_Bala))
    
    For Sun and Moon (no Chesta Bala):
    - Sun: Chesta Bala = compute from (Sun_longitude + 90). If > 180, subtract from 360.
      Then convert to Virupas (divide by 3).
    - Moon: Similar computation using Moon's distance from Sun
    
    Ishta Phala ranges 0-60. Higher = planet gives good results EASILY in its dasha
    Kashta Phala ranges 0-60. Higher = planet gives results through STRUGGLE/obstacles
    
    KEY INSIGHT: If Ishta > Kashta → planet's dasha favourable
                 If Kashta > Ishta → planet's dasha brings challenges
    """
    uccha_bala = planet.sthana_bala.uccha_bala  # 0-60 Virupas
    chesta_bala = planet.chesta_bala  # 0-60 Virupas
    
    ishta = math.sqrt(uccha_bala * chesta_bala)
    kashta = math.sqrt((60 - uccha_bala) * (60 - chesta_bala))
    
    return ishta, kashta
```

**INTEGRATION INTO DASHA QUALITY:**
```python
def dasha_quality_score(planet):
    ishta, kashta = compute_ishta_kashta(planet)
    # Normalize to 0-1 scale
    quality = ishta / (ishta + kashta) if (ishta + kashta) > 0 else 0.5
    
    # Combine with other factors for total dasha quality:
    shadbala_factor = planet.shadbala_ratio / max(SHADBALA_MIN_RUPAS.values())
    functional_role = 1.0 if planet.is_yogakaraka else (0.7 if planet.is_benefic else 0.4)
    d9_dignity = planet.navamsha_dignity_score()  # 0-1
    retrograde_mod = 0.85 if planet.is_retrograde else 1.0
    
    total_quality = (
        quality * 0.30 +           # Ishta/Kashta ratio
        shadbala_factor * 0.25 +   # Overall strength
        functional_role * 0.20 +   # Functional nature for lagna
        d9_dignity * 0.15 +        # D9 confirmation
        retrograde_mod * 0.10      # Retrograde adjustment
    )
    return total_quality  # 0-1 scale: >0.7 = good dasha, <0.4 = difficult dasha
```

**WHERE TO ADD:** `strength/shadbala.py` — add Ishta/Kashta computation. Create new `timing/dasha_quality.py` — use this to transform binary dasha activation into graded quality score.

**PRIORITY:** HIGH — Directly fixes the "dasha as binary switch" problem

---

## 2.3 BHAVABALA (HOUSE STRENGTH) — COMPLETE COMPONENTS

**SOURCE:** BPHS Ch.27

```python
BHAVABALA_COMPONENTS = {
    "Bhavadhipathi_Bala": "Strength of the house lord (from Shadbala)",
    "Bhava_Dig_Bala": "Directional strength of the house itself",
    "Bhava_Drishti_Bala": "Aspectual strength (benefic aspects add, malefic subtract)",
    "Bhava_Ashtakavarga": "SAV score for the sign containing the house cusp",
    "Rising_Nature": {
        # Day birth: Sheershodaya (head-rising) signs strong
        # Night birth: Prishtodaya (back-rising) signs strong
        "Sheershodaya": ["Gemini", "Leo", "Virgo", "Libra", "Scorpio", "Aquarius"],
        "Prishtodaya": ["Aries", "Taurus", "Cancer", "Sagittarius", "Capricorn"],
        "Ubhayodaya": ["Pisces"],  # Strong at twilight
        # Award 15 Virupas (1/4 of 60) if sign matches birth time
    }
}
```

**INTEGRATION:** Bhavabala should feed DIRECTLY into the Promise gate's "Bhava strength" pillar. Currently, the engine may compute Bhavabala but not connect it to domain-specific Promise scoring.

**WHERE TO ADD:** `strength/bhavabala.py` — verify all components. `prediction/confidence.py` — wire Bhavabala into Promise gate.

**PRIORITY:** HIGH

---

# SECTION 3: ASHTAKAVARGA — DEEP IMPLEMENTATION

## 3.1 DOMAIN-SPECIFIC BAV (Bhinna Ashtakavarga)

**GAP:** Engine shows SAV = constant 1.00 across all domains. Must use PLANET-SPECIFIC BAV for each domain.

```python
DOMAIN_BAV_MAPPING = {
    "Career": {
        "primary": [
            ("Sun", 10),    # Sun's BAV in 10th house sign
            ("Saturn", 10), # Saturn's BAV in 10th house sign  
            ("Mercury", 10),# Mercury's BAV for business
        ],
        "secondary": [
            ("Jupiter", 9), # Jupiter's BAV in 9th (luck/dharma)
            ("Mars", 3),    # Mars's BAV in 3rd (courage/initiative)
        ],
        "formula": "weighted_avg(primary*0.7, secondary*0.3) / 8.0"
    },
    "Finance": {
        "primary": [
            ("Jupiter", 2),  # Jupiter's BAV in 2nd house sign
            ("Jupiter", 11), # Jupiter's BAV in 11th house sign
        ],
        "secondary": [
            ("Venus", 2),   # Venus's BAV in 2nd
            ("Saturn", 11), # Saturn's BAV in 11th
        ],
        "formula": "weighted_avg(primary*0.7, secondary*0.3) / 8.0"
    },
    "Marriage": {
        "primary": [
            ("Venus", 7),   # Venus's BAV in 7th house sign
            ("Jupiter", 7), # Jupiter's BAV in 7th (for females traditionally)
        ],
        "secondary": [
            ("Moon", 7),    # Moon's BAV in 7th
            ("Venus", 4),   # Venus's BAV in 4th (sukha/comfort)
        ],
        "formula": "weighted_avg(primary*0.7, secondary*0.3) / 8.0"
    },
    "Health": {
        "primary": [
            ("Sun", 1),     # Sun's BAV in Lagna sign (vitality)
            ("Moon", 1),    # Moon's BAV in Lagna sign (constitution)
        ],
        "secondary": [
            ("Mars", 8),    # Mars's BAV in 8th (longevity)
            ("Saturn", 8),  # Saturn's BAV in 8th
        ],
        "formula": "weighted_avg(primary*0.7, secondary*0.3) / 8.0"
    }
}
```

**BAV TRANSIT SCORING:**
```python
# When a planet transits a sign, check its BAV score in that sign:
# 0-1 bindus: Very bad transit — expect obstacles
# 2-3 bindus: Bad transit — delays, difficulties  
# 4 bindus: Average — mixed results (4 is the neutral threshold)
# 5-6 bindus: Good transit — favorable results
# 7-8 bindus: Excellent transit — maximum positive results

def bav_transit_quality(planet, transit_sign, bav_table):
    bindus = bav_table[planet][transit_sign]
    if bindus <= 1: return -1.0
    elif bindus <= 3: return -0.5
    elif bindus == 4: return 0.0
    elif bindus <= 6: return 0.5
    else: return 1.0
```

**WHERE TO ADD:** Replace constant AV score in `prediction/confidence.py` with domain-specific BAV lookup. Add BAV transit scoring to `timing/transit_analyzer.py`.

**PRIORITY:** CRITICAL — This is the #1 bug fix (AV always showing 1.00)

---

## 3.2 TRIKONA SHODHANA (Triangular Reduction)

**GAP:** Engine computes raw BAV/SAV but doesn't apply classical reductions.

**SOURCE:** BPHS Ch.69

**ALGORITHM:**
```python
def trikona_shodhana(bav_table):
    """
    Step 1: Group the 12 signs into 4 Trikona groups:
    - Fire: Aries(1), Leo(5), Sagittarius(9)
    - Earth: Taurus(2), Virgo(6), Capricorn(10)
    - Air: Gemini(3), Libra(7), Aquarius(11)
    - Water: Cancer(4), Scorpio(8), Pisces(12)
    
    Step 2: For each Trikona group of 3 signs:
    - If any sign has 0 bindus → NO reduction for this group
    - If two signs have same value and third is 0 → make both 0
    - If all three have values → subtract the MINIMUM from all three
    - Keep the remainders
    """
    trikona_groups = [
        [0, 4, 8],   # Ar, Le, Sg (indices)
        [1, 5, 9],   # Ta, Vi, Cp
        [2, 6, 10],  # Ge, Li, Aq
        [3, 7, 11],  # Cn, Sc, Pi
    ]
    
    reduced = bav_table.copy()
    for group in trikona_groups:
        values = [reduced[i] for i in group]
        if 0 in values:
            # If any is 0, no reduction
            # BUT: if two have values and one is 0 → make the others 0 too
            if values.count(0) == 1:
                continue  # No reduction when one is 0
            elif values.count(0) == 2:
                # Make the non-zero one also 0
                for i in group:
                    reduced[i] = 0
            # If all 0, nothing to do
        else:
            min_val = min(values)
            for i in group:
                reduced[i] -= min_val
    
    return reduced
```

## 3.3 EKADHIPATYA SHODHANA (Single-Lord Reduction)

**SOURCE:** BPHS Ch.70

```python
def ekadhipatya_shodhana(reduced_bav, chart):
    """
    Applied AFTER Trikona Shodhana. Deals with dual-ownership planets.
    Sun and Moon own one sign each → NO reduction for Cancer/Leo.
    
    For Mars (Ar/Sc), Mercury (Ge/Vi), Jupiter (Sg/Pi), Venus (Ta/Li), Saturn (Cp/Aq):
    
    Rules (for each pair of signs owned by same planet):
    1. Both signs unoccupied by any planet + same value → both become 0
    2. Both signs unoccupied + different values → both get the SMALLER value
    3. Both signs occupied → NO reduction
    4. One occupied, one not:
       a. Occupied has SMALLER value → reduce unoccupied to 0
       b. Occupied has LARGER value → reduce unoccupied to 0, keep occupied
       c. Equal values → reduce unoccupied to 0
    5. One sign has 0 → no reduction needed
    """
    dual_lords = {
        "Mars": [0, 7],      # Aries, Scorpio
        "Mercury": [2, 5],   # Gemini, Virgo
        "Jupiter": [8, 11],  # Sagittarius, Pisces
        "Venus": [1, 6],     # Taurus, Libra
        "Saturn": [9, 10],   # Capricorn, Aquarius
    }
    
    result = reduced_bav.copy()
    for planet, (sign_a, sign_b) in dual_lords.items():
        val_a, val_b = result[sign_a], result[sign_b]
        if val_a == 0 or val_b == 0:
            continue  # No reduction if either is 0
        
        occupied_a = chart.has_planet_in_sign(sign_a)
        occupied_b = chart.has_planet_in_sign(sign_b)
        
        if occupied_a and occupied_b:
            continue  # Both occupied → no reduction
        elif not occupied_a and not occupied_b:
            if val_a == val_b:
                result[sign_a] = 0
                result[sign_b] = 0
            else:
                smaller = min(val_a, val_b)
                result[sign_a] = smaller
                result[sign_b] = smaller
        else:
            # One occupied, one not
            if occupied_a:
                result[sign_b] = 0  # Reduce unoccupied to 0
            else:
                result[sign_a] = 0
    
    return result
```

## 3.4 KAKSHA (Sub-Division) TRANSIT TIMING

**GAP:** Engine doesn't use Kaksha system for precise transit timing within a sign.

**SOURCE:** BPHS, Classical Ashtakavarga texts

```python
# Each 30° sign is divided into 8 Kakshas of 3°45' each
# Each Kaksha is ruled by a planet in this fixed order:
KAKSHA_LORDS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Lagna"]
# Kaksha 1: 0°00' - 3°45', Kaksha 2: 3°45' - 7°30', etc.

def kaksha_of_degree(degree_in_sign):
    """Returns 0-7 kaksha index for a given degree within a sign"""
    return int(degree_in_sign / 3.75)

def kaksha_transit_quality(transiting_planet, degree_in_sign, bav_prastara):
    """
    In Prastharashtakavarga (8x12 matrix), each planet has a row 
    showing whether it contributes a bindu (1) or rekha (0) in each sign.
    
    When a planet transits through a specific Kaksha:
    - If the Kaksha lord contributed a bindu → good results during that 3°45' transit
    - If the Kaksha lord contributed a rekha → bad results during that 3°45' transit
    
    This gives DAILY-LEVEL precision from the Ashtakavarga system.
    """
    kaksha_idx = kaksha_of_degree(degree_in_sign)
    kaksha_lord = KAKSHA_LORDS[kaksha_idx]
    # Look up in Prastharashtakavarga: did kaksha_lord contribute a bindu?
    return bav_prastara[transiting_planet][kaksha_lord]  # 1 = good, 0 = bad
```

**WHERE TO ADD:** Create new `analysis/ashtakavarga_deep.py` with all reduction methods and Kaksha system. Wire into transit timing.

**PRIORITY:** CRITICAL for domain-specific AV fix, HIGH for Kaksha timing

---

# SECTION 4: JAIMINI SYSTEM — COMPLETE INTEGRATION RULES

## 4.1 CURRENT STATE: DISPLAY-ONLY → MUST FEED SCORING PIPELINE

**GAP:** Chara Dasha, Rashi Drishti, Karakamsha, Arudha Padas all compute but DON'T feed the confidence scoring pipeline. They are display-only.

**FIX:** Create Jaimini confidence sub-score that feeds into the main weighted sum.

```python
def jaimini_confidence_score(chart, domain, current_date):
    """
    Synthesize Jaimini signals into a 0-1 confidence score per domain.
    This feeds as an ADDITIONAL component into the main confidence pipeline.
    """
    score = 0.0
    
    # 1. Chara Dasha alignment (0.30 weight)
    chara_dasha_sign = chart.current_chara_dasha(current_date)
    relevant_houses = DOMAIN_HOUSES[domain]  # e.g., Career: [10, 7, 4, 1]
    if chara_dasha_sign in [chart.house_sign(h) for h in relevant_houses]:
        score += 0.30
    
    # 2. Karakamsha relevance (0.25 weight)
    karakamsha = chart.karakamsha_sign
    karakamsha_planets = chart.planets_in_sign_d9(karakamsha)
    domain_karakas = DOMAIN_JAIMINI_KARAKAS[domain]
    for planet in karakamsha_planets:
        if planet.name in domain_karakas:
            score += 0.25
            break
    
    # 3. Arudha Pada relevance (0.25 weight)
    domain_arudha = DOMAIN_ARUDHA[domain]  # e.g., Career: "A10", Finance: "A2"+"A11"
    arudha_sign = chart.arudha_pada(domain_arudha)
    if chara_dasha_sign == arudha_sign or chart.jaimini_aspects(chara_dasha_sign, arudha_sign):
        score += 0.25
    
    # 4. Rashi Drishti on relevant houses (0.20 weight)
    benefic_drishti = count_benefic_rashi_drishti(chart, relevant_houses)
    score += 0.20 * min(benefic_drishti / 3.0, 1.0)
    
    return score

# Jaimini-specific domain mappings:
DOMAIN_JAIMINI_KARAKAS = {
    "Career": ["AmK", "AK"],    # Amatya Karaka = career significator
    "Finance": ["AK", "DK"],     # Atma Karaka for overall destiny
    "Marriage": ["DK", "UL"],    # Dara Karaka + Upapada
    "Health": ["AK"],            # Atma Karaka = self/body
}

DOMAIN_ARUDHA = {
    "Career": "A10",
    "Finance": ["A2", "A11"],
    "Marriage": "UL",  # Upapada Lagna (A12)
    "Health": "AL",    # Arudha Lagna (A1)
}
```

## 4.2 UPAPADA LAGNA — COMPLETE MARRIAGE PREDICTION RULES

**SOURCE:** BPHS Upapadadhyaya, Jaimini Sutras

```python
UPAPADA_MARRIAGE_RULES = {
    "spouse_nature": {
        "benefic_conjunct_UL": "Well-behaved, pleasant spouse",
        "malefic_conjunct_UL": "Harsh, demanding spouse",
        "Jupiter_on_UL": "Wise, knowledgeable, law-abiding spouse",
        "Venus_on_UL": "Beautiful, artistic, romantic spouse",
        "Saturn_on_UL": "Older or mature spouse, delays in marriage",
        "Mars_on_UL": "Dynamic, confident but aggressive spouse",
        "Rahu_on_UL": "Unconventional spouse, possible inter-caste/foreign",
        "Ketu_on_UL": "Extremely problematic — delays, spiritual but detached",
    },
    "marriage_stability": {
        "2nd_from_UL": "Sustains marriage. Benefics = stable. Malefics (esp Mars/Rahu) = separation risk",
        "UL_lord_exalted": "Spouse from noble/wealthy family",
        "UL_lord_debilitated": "Spouse from humble background",
        "AL_UL_relationship": {
            "kendra": "Harmonious marriage perception",
            "trikona": "Supportive marriage",
            "6_8": "Tension, mismatch in self-image vs marriage",
            "2_12": "Lack of understanding, sacrifice required",
        }
    },
    "marriage_timing": {
        "chara_dasha_of_UL_sign": "Marriage likely during this period",
        "chara_dasha_of_7th_from_UL": "Also marriage timing",
        "transit_Jupiter_over_UL": "Triggers marriage if dasha supports",
    },
    "opposition_to_marriage": {
        "Sun_7th_from_UL": "Father opposes marriage",
        "Mars_7th_from_UL": "Brothers oppose",
        "Moon_7th_from_UL": "Mother opposes",
        "Saturn_7th_from_UL": "Elders/society opposes",
    }
}
```

## 4.3 RASHI DRISHTI (SIGN ASPECTS) — COMPLETE PATTERN

```python
# Jaimini Rashi Drishti: Signs aspect other signs in FIXED patterns
# Movable signs (Ar,Cn,Li,Cp) aspect: Fixed signs EXCEPT the one next to them
# Fixed signs (Ta,Le,Sc,Aq) aspect: Movable signs EXCEPT the one before them  
# Dual signs (Ge,Vi,Sg,Pi) aspect: Each other (all dual signs aspect all dual signs)

RASHI_DRISHTI = {
    # Movable → Fixed (excluding adjacent)
    "Aries":   ["Leo", "Scorpio", "Aquarius"],      # Not Taurus (adjacent)
    "Cancer":  ["Taurus", "Scorpio", "Aquarius"],    # Not Leo (adjacent)
    "Libra":   ["Taurus", "Leo", "Aquarius"],        # Not Scorpio (adjacent)
    "Capricorn": ["Taurus", "Leo", "Scorpio"],       # Not Aquarius (adjacent)
    # Fixed → Movable (excluding preceding)
    "Taurus":  ["Cancer", "Libra", "Capricorn"],     # Not Aries (preceding)
    "Leo":     ["Aries", "Libra", "Capricorn"],      # Not Cancer (preceding)
    "Scorpio": ["Aries", "Cancer", "Capricorn"],     # Not Libra (preceding)
    "Aquarius":["Aries", "Cancer", "Libra"],         # Not Capricorn (preceding)
    # Dual → Dual (all mutual)
    "Gemini":  ["Virgo", "Sagittarius", "Pisces"],
    "Virgo":   ["Gemini", "Sagittarius", "Pisces"],
    "Sagittarius": ["Gemini", "Virgo", "Pisces"],
    "Pisces":  ["Gemini", "Virgo", "Sagittarius"],
}
```

**WHERE TO ADD:** `analysis/rashi_drishti.py` — verify correct implementation, then wire into Jaimini confidence sub-score

**PRIORITY:** HIGH — Jaimini integration is the #3 architectural gap

---

# SECTION 5: TRANSIT SYSTEMS — MISSING TECHNIQUES

## 5.1 DOUBLE TRANSIT THEORY (Jupiter + Saturn)

**GAP:** Engine doesn't implement the critical Double Transit rule.

**SOURCE:** BPHS, widely used in modern practice

```python
def check_double_transit(house_number, chart, transit_date):
    """
    RULE: For any major life event to manifest, BOTH Jupiter AND Saturn 
    must aspect or transit the relevant house simultaneously.
    
    This is one of the most reliable timing techniques in Vedic astrology.
    Jupiter's transit cycle: ~12 years (1 year per sign)
    Saturn's transit cycle: ~29.5 years (~2.5 years per sign)
    When both influence the same house = event trigger window
    """
    house_sign = chart.house_sign(house_number)
    
    jupiter_pos = get_transit_position("Jupiter", transit_date)
    saturn_pos = get_transit_position("Saturn", transit_date)
    
    # Check if Jupiter aspects or occupies the house sign
    jupiter_influences = jupiter_pos == house_sign or \
                         house_sign in get_aspect_signs("Jupiter", jupiter_pos)
    
    # Check if Saturn aspects or occupies the house sign
    saturn_influences = saturn_pos == house_sign or \
                        house_sign in get_aspect_signs("Saturn", saturn_pos)
    
    return jupiter_influences and saturn_influences

# Domain application:
DOUBLE_TRANSIT_HOUSES = {
    "Marriage": [7, 1],      # 7th house (spouse) or 1st house (self)
    "Career_Change": [10, 6],# 10th (karma) or 6th (service) 
    "Finance": [2, 11],      # 2nd (wealth) or 11th (gains)
    "Children": [5, 9],      # 5th (putra) or 9th (bhagya)
    "Education": [4, 5],     # 4th (vidya) or 5th (learning)
    "Health_Crisis": [1, 8], # 1st (body) or 8th (chronic illness)
}
```

**WHERE TO ADD:** `timing/transit_analyzer.py` — add as highest-priority transit check. An event CANNOT manifest without double transit support (use as hard gate similar to Promise gate).

**PRIORITY:** CRITICAL — This alone can dramatically improve timing accuracy

---

## 5.2 SUDARSHANA CHAKRA (Triple Reference Frame)

**GAP:** Engine only uses Gochar (transit from Moon). Must add Lagna and Sun reference frames.

**SOURCE:** BPHS, Sudarshana Chakra Dasha chapter

```python
def sudarshana_transit_score(house, chart, transit_date):
    """
    Analyze transits from THREE reference points simultaneously:
    1. From Lagna (body, physical events)
    2. From Moon (mind, emotional events)  
    3. From Sun (soul, career/authority events)
    
    Composite score: 0.40*lagna + 0.40*moon + 0.20*sun
    
    When all three frames agree = very strong signal
    When they disagree = mixed results, weakened prediction
    """
    lagna_sign = chart.lagna_sign
    moon_sign = chart.moon_sign
    sun_sign = chart.sun_sign
    
    # Count benefic transits through/aspecting the house from each reference
    lagna_score = transit_quality_from_reference(house, lagna_sign, transit_date)
    moon_score = transit_quality_from_reference(house, moon_sign, transit_date)
    sun_score = transit_quality_from_reference(house, sun_sign, transit_date)
    
    composite = 0.40 * lagna_score + 0.40 * moon_score + 0.20 * sun_score
    
    # Convergence bonus: if all three agree on direction
    if all_same_direction(lagna_score, moon_score, sun_score):
        composite *= 1.15  # 15% convergence bonus
    
    return composite
```

**WHERE TO ADD:** `timing/sudarshana.py` (new module). Feed into `transit_support` component of confidence pipeline.

**PRIORITY:** HIGH — Adds genuinely independent transit evidence

---

## 5.3 SARVATOBHADRA CHAKRA — NAKSHATRA-BASED TRANSIT

**GAP:** Completely missing. Independent transit system using 28 nakshatras.

**SOURCE:** BPHS, Mansagari, Saravali

**CORE CONCEPT:**
```python
# 9x9 grid = 81 boxes containing:
# - 28 Nakshatras (including Abhijit) on outer ring
# - 12 Rasis on inner ring
# - 7 Weekdays + 5 Tithis in center
# - Vowels and Consonants in middle rings

# THREE TYPES OF VEDHA (piercing/influence):
SBC_VEDHA_TYPES = {
    "across": "Horizontal/vertical opposite in the grid — effective when planet is in NORMAL motion",
    "fore": "Diagonal clockwise — effective when planet is moving FAST",
    "hind": "Diagonal anti-clockwise — effective when planet is RETROGRADE",
}

# VEDHA EFFECTS BY PLANET:
SBC_VEDHA_EFFECTS = {
    "Sun": "grief, problems with authority",
    "Moon": "mixed good/bad happenings (natural benefic but changeable)",
    "Mars": "loss of wealth, accidents, aggression",
    "Mercury": "sharpening of intellect, communication gains",
    "Jupiter": "many good happenings, gains, wisdom",
    "Venus": "fear from enemies, but luxury/comfort (mixed)",
    "Saturn": "pain, ailments, delays, chronic issues",
    "Rahu": "obstructions, confusion, unconventional events",
    "Ketu": "obstructions, spiritual events, losses",
}

# SEVERITY SCALE:
# 1 vedha from malefic = conflict/misunderstanding
# 2 vedhas = loss of wealth
# 3 vedhas = defeat/failure/illness  
# 4 vedhas = death or death-like experience

def sbc_vedha_score(natal_nakshatra, transit_date):
    """
    Check how many benefic vs malefic planets cause vedha 
    on the native's Janma Nakshatra on a given date.
    
    Returns: float (-1.0 to +1.0)
    Positive = benefic vedhas dominate
    Negative = malefic vedhas dominate
    """
    benefic_vedhas = 0
    malefic_vedhas = 0
    
    for planet in ALL_PLANETS:
        transit_nak = get_nakshatra(planet, transit_date)
        vedha_type = get_vedha_type(transit_nak, natal_nakshatra, SBC_GRID)
        if vedha_type:
            if planet in BENEFICS:
                benefic_vedhas += vedha_type.strength
            else:
                malefic_vedhas += vedha_type.strength
    
    total = benefic_vedhas + malefic_vedhas
    if total == 0:
        return 0.0
    return (benefic_vedhas - malefic_vedhas) / total
```

**WHERE TO ADD:** Create `timing/sarvatobhadra.py`. Feed SBC score as independent cross-validator of Gochar transit prediction.

**PRIORITY:** HIGH — Completely independent transit assessment system

---

## 5.4 BHRIGU BINDU ACTIVATION

**GAP:** Already computed (214.62° in sample output) but NOT USED in timing.

**SOURCE:** Bhrigu Nandi Nadi, modern practice

```python
def bhrigu_bindu_transit_check(bb_degree, transit_date):
    """
    Bhrigu Bindu = midpoint of Rahu and Jupiter in natal chart.
    
    When transiting Jupiter, Saturn, or Rahu crosses this exact degree:
    - Events related to the HOUSE containing the Bhrigu Bindu get triggered
    - Jupiter transit = positive events
    - Saturn transit = karmic/structural events
    - Rahu transit = sudden/unexpected events
    
    Orb: ±1° for exact trigger, ±5° for influence window
    """
    bb_sign = int(bb_degree / 30)
    bb_house = chart.sign_to_house(bb_sign)
    
    for planet in ["Jupiter", "Saturn", "Rahu"]:
        transit_degree = get_longitude(planet, transit_date)
        orb = abs(transit_degree - bb_degree) % 360
        if orb > 180: orb = 360 - orb
        
        if orb <= 1.0:
            return {"triggered": True, "planet": planet, "house": bb_house, "strength": 1.0}
        elif orb <= 5.0:
            return {"triggered": True, "planet": planet, "house": bb_house, 
                    "strength": 1.0 - (orb / 5.0)}
    
    return {"triggered": False}
```

**WHERE TO ADD:** `timing/transit_analyzer.py` — add as trigger check. Zero computational cost, high predictive value.

**PRIORITY:** HIGH — Already computed, just needs wiring

---

# SECTION 6: MISSING CLASSICAL TECHNIQUES

## 6.1 MRITYU BHAGA (DEATH DEGREES) — COMPLETE TABLE

**SOURCE:** Jataka Parijata Ch.1 Verse 57, Sarvartha Chintamani, Phala Deepika

```python
# Mrityu Bhaga degrees per planet per sign (Jataka Parijata / Sarvartha Chintamani)
# Format: MRITYU_BHAGA[planet_index][sign_index] = degree
# Signs: 0=Ar, 1=Ta, 2=Ge, 3=Cn, 4=Le, 5=Vi, 6=Li, 7=Sc, 8=Sg, 9=Cp, 10=Aq, 11=Pi

MRITYU_BHAGA = {
    "Sun":     [20, 9, 12, 6, 8, 24, 16, 17, 22, 2, 3, 23],
    "Moon":    [26, 12, 13, 25, 24, 11, 26, 14, 13, 25, 5, 12],
    "Mars":    [19, 28, 25, 23, 29, 28, 14, 21, 2, 15, 11, 6],
    "Mercury": [15, 14, 13, 12, 8, 18, 20, 10, 21, 22, 7, 5],
    "Jupiter": [19, 29, 12, 27, 6, 4, 13, 10, 17, 11, 15, 28],
    "Venus":   [28, 15, 11, 17, 10, 13, 4, 6, 27, 12, 29, 19],
    "Saturn":  [10, 4, 7, 9, 12, 16, 3, 18, 28, 14, 13, 15],
    "Rahu":    [14, 13, 12, 11, 24, 23, 22, 21, 10, 20, 18, 8],
    "Ketu":    [8, 18, 20, 10, 21, 22, 23, 24, 11, 12, 13, 14],
    "Lagna":   [1, 9, 22, 22, 25, 2, 4, 23, 18, 20, 24, 10],
}

def is_in_mrityu_bhaga(planet_name, planet_degree, sign_index):
    """
    Check if a planet is within its Mrityu Bhaga degree.
    Convention: MB occupies 1° range, i.e., degree-1 to degree.
    (Per PVR Narasimha Rao: 17-18° recommended interpretation)
    
    A planet in MB:
    - Loses ability to deliver good results for its significations
    - Affects the house it occupies, houses it rules, and natural karakatvas
    - Malefic association intensifies negative effects
    - Jupiter's aspect provides SIGNIFICANT relief
    - Results manifest during Dasha of the sign containing MB planet
    """
    mb_degree = MRITYU_BHAGA[planet_name][sign_index]
    degree_in_sign = planet_degree % 30
    return abs(degree_in_sign - mb_degree) < 1.0

def mrityu_bhaga_modifier(planet, chart):
    """Returns a penalty multiplier (0.2 to 1.0) for planets in Mrityu Bhaga"""
    if not is_in_mrityu_bhaga(planet.name, planet.longitude, planet.sign_index):
        return 1.0  # No penalty
    
    # Base penalty
    penalty = 0.3  # Planet at 30% effectiveness
    
    # Jupiter's aspect provides relief
    if planet.aspected_by("Jupiter", chart):
        penalty = 0.6  # Significant relief
    
    # Benefic conjunction helps
    if planet.conjunct_benefic(chart):
        penalty = min(penalty + 0.2, 0.8)
    
    # Malefic conjunction worsens
    if planet.conjunct_malefic(chart):
        penalty = max(penalty - 0.2, 0.1)
    
    return penalty
```

**WHERE TO ADD:** `analysis/special_degrees.py` (new module). Apply modifier to Promise gate and planet strength calculations.

**PRIORITY:** MEDIUM — Low computation cost, adds a meaningful refinement layer

---

## 6.2 GANDANTA — WATER-TO-FIRE JUNCTIONS

**SOURCE:** BPHS, classical texts

```python
# Gandanta occurs at the junctions between Water and Fire signs:
# Cancer(30°) → Leo(0°)          = degrees 119°-121° absolute
# Scorpio(30°) → Sagittarius(0°)  = degrees 239°-241° absolute
# Pisces(30°) → Aries(0°)         = degrees 359°-1° absolute

GANDANTA_ZONES = [
    (119.0, 121.0),  # Cancer-Leo junction
    (239.0, 241.0),  # Scorpio-Sagittarius junction
    (359.0, 1.0),    # Pisces-Aries junction (wraps around)
]

# Each zone is approximately 3°20' (one Nakshatra pada) wide:
# Last pada of Ashlesha / First pada of Magha
# Last pada of Jyeshtha / First pada of Moola
# Last pada of Revati / First pada of Ashwini

GANDANTA_NAKSHATRAS = {
    "Ashlesha_4": "Most dangerous Gandanta — emotional/psychic crisis",
    "Magha_1": "Ancestral karma activation",
    "Jyeshtha_4": "Power struggles, transformation",  
    "Moola_1": "Root destruction then rebuilding — MOST severe Gandanta",
    "Revati_4": "Endings, dissolution, spiritual completion",
    "Ashwini_1": "New beginnings from crisis, rebirth energy",
}

def gandanta_severity(planet_longitude):
    """Returns 0.0 (not in Gandanta) to 1.0 (exact junction)"""
    for zone_start, zone_end in GANDANTA_ZONES:
        if zone_start < zone_end:
            if zone_start <= planet_longitude <= zone_end:
                center = (zone_start + zone_end) / 2
                return 1.0 - abs(planet_longitude - center) / 1.0
        else:  # Wraps around 360°
            if planet_longitude >= zone_start or planet_longitude <= zone_end:
                if planet_longitude >= zone_start:
                    dist = planet_longitude - zone_start
                else:
                    dist = planet_longitude + (360 - zone_start)
                return 1.0 - abs(dist - 1.0) / 1.0
    return 0.0
```

**WHERE TO ADD:** `analysis/special_degrees.py`. Apply as modifier to planet strength and Promise gate.

**PRIORITY:** MEDIUM

---

## 6.3 COMBUSTION — PER-PLANET ORBS

**GAP:** Engine likely uses single combustion threshold. Classical texts give different orbs per planet.

**SOURCE:** Surya Siddhanta, BPHS

```python
COMBUSTION_ORBS = {
    # Planet: (direct_orb, retrograde_orb) in degrees
    "Moon":    (12, 12),    # Always same (Moon doesn't retrograde)
    "Mars":    (17, 17),    
    "Mercury": (14, 12),    # Tighter orb when retrograde
    "Jupiter": (11, 11),    
    "Venus":   (10, 8),     # Tighter when retrograde  
    "Saturn":  (15, 15),    
}

def combustion_strength(planet, sun_longitude):
    """
    Returns 0.0 (fully combust) to 1.0 (not combust).
    Graduated — not binary.
    """
    if planet.name in ["Sun", "Rahu", "Ketu"]:
        return 1.0  # Sun can't be combust, nodes don't apply
    
    orb_direct, orb_retro = COMBUSTION_ORBS[planet.name]
    orb = orb_retro if planet.is_retrograde else orb_direct
    
    angular_distance = abs(planet.longitude - sun_longitude) % 360
    if angular_distance > 180:
        angular_distance = 360 - angular_distance
    
    if angular_distance >= orb:
        return 1.0  # Not combust
    elif angular_distance <= 1.0:
        return 0.05  # Nearly fully combust (war-level proximity)
    else:
        return angular_distance / orb  # Linear degradation

# KEY RULE: Combust planet's dasha period gives reduced/delayed results
# but the planet DOES still give results — just with difficulty
# EXCEPTION: Mercury combust within 3° does NOT suffer much 
# (considered "nourished" by Sun due to natural proximity)
```

**WHERE TO ADD:** `core/planets.py` or `strength/` — replace binary combustion with graduated function

**PRIORITY:** MEDIUM-HIGH

---

## 6.4 PUSHKARA NAVAMSHA AND PUSHKARA BHAGA

```python
# Pushkara Navamshas — specific Navamsha divisions considered extremely auspicious
# A planet in Pushkara Navamsha gains strength equivalent to exaltation
PUSHKARA_NAVAMSHA = {
    # Sign: [navamsha_number (1-9) that are Pushkara]
    "Aries":       [2, 5, 7],   # Taurus, Leo, Libra navamshas
    "Taurus":      [1, 3, 6],
    "Gemini":      [2, 5, 7],
    "Cancer":      [1, 3, 6],
    "Leo":         [2, 5, 7],
    "Virgo":       [1, 3, 6],
    "Libra":       [2, 5, 7],
    "Scorpio":     [1, 3, 6],
    "Sagittarius": [2, 5, 7],
    "Capricorn":   [1, 3, 6],
    "Aquarius":    [2, 5, 7],
    "Pisces":      [1, 3, 6],
}

# Pushkara Bhaga — specific DEGREES within each sign that are auspicious
PUSHKARA_BHAGA = {
    "Aries": [21], "Taurus": [14], "Gemini": [18], "Cancer": [8],
    "Leo": [19], "Virgo": [9], "Libra": [24], "Scorpio": [11],
    "Sagittarius": [23], "Capricorn": [14], "Aquarius": [19], "Pisces": [9],
}

# Vargottama — planet in same sign in D1 and D9
# Engine already detects this. Effect: +20% strength modifier
VARGOTTAMA_BONUS = 0.20  # Add to planet's dignity score
```

**WHERE TO ADD:** `analysis/special_degrees.py` — add checks, feed into dignity scoring

**PRIORITY:** LOW-MEDIUM

---

## 6.5 PLANET MATURITY AGES

**GAP:** Engine likely doesn't use planet maturity ages for timing.

**SOURCE:** Classical texts (multiple sources agree)

```python
PLANET_MATURITY_AGE = {
    "Jupiter": 16,
    "Sun": 22,
    "Moon": 24,
    "Venus": 25,
    "Mars": 28,
    "Mercury": 32,
    "Saturn": 36,
    "Rahu": 42,
    "Ketu": 48,
}

# RULE: A planet gives its FULL results only after its maturity age.
# Before maturity: results are partial, delayed, or experienced differently.
# At/after maturity: planet's full significations manifest.
# 
# INTEGRATION: When predicting events, if native's age < planet's maturity age,
# reduce the confidence of predictions involving that planet.

def maturity_modifier(planet_name, native_age):
    maturity = PLANET_MATURITY_AGE[planet_name]
    if native_age >= maturity:
        return 1.0  # Full results
    elif native_age >= maturity - 3:
        return 0.7  # Approaching maturity — partial results beginning
    else:
        return 0.4  # Well below maturity — significantly reduced results
```

**WHERE TO ADD:** `timing/dasha_quality.py` — apply as modifier to dasha predictions

**PRIORITY:** MEDIUM — Simple lookup but surprisingly effective for timing

---

# SECTION 7: KP SYSTEM REFINEMENTS

## 7.1 KP HOUSE GROUPINGS PER LIFE EVENT

**GAP:** KP sub-lord analysis needs clear domain-specific house groupings.

**SOURCE:** KP Reader series by K.S. Krishnamurti

```python
KP_HOUSE_GROUPS = {
    "Marriage": {
        "favorable": [2, 7, 11],    # 2nd(family), 7th(spouse), 11th(fulfillment)
        "negating":  [1, 6, 10, 12], # 12th from favorable houses
        "sublord_check": "7th_cusp_sublord",
    },
    "Career_Promotion": {
        "favorable": [2, 6, 10, 11],
        "negating":  [1, 5, 8, 12],
        "sublord_check": "10th_cusp_sublord",
    },
    "Wealth_Gain": {
        "favorable": [2, 6, 10, 11],
        "negating":  [5, 8, 12],
        "sublord_check": "2nd_cusp_sublord",
    },
    "Foreign_Travel": {
        "favorable": [3, 9, 12],
        "negating":  [4],  # 4th = homeland
        "sublord_check": "12th_cusp_sublord",
    },
    "Children": {
        "favorable": [2, 5, 11],
        "negating":  [1, 4, 10],
        "sublord_check": "5th_cusp_sublord",
    },
    "Health_Issues": {
        "indicating": [1, 6, 8, 12],  # Illness signified by these
        "recovery":   [1, 5, 11],      # Recovery signified by these
        "sublord_check": "1st_cusp_sublord",
    },
    "Education": {
        "favorable": [4, 9, 11],
        "negating":  [3, 8, 12],
        "sublord_check": "4th_cusp_sublord",
    }
}

# KP DENIAL CONDITION:
# If the sub-lord of the relevant cusp signifies MORE negating houses 
# than favorable houses → event is DENIED in the native's life.
def kp_event_promise(cusp_sublord, event_type, chart):
    favorable = KP_HOUSE_GROUPS[event_type]["favorable"]
    negating = KP_HOUSE_GROUPS[event_type]["negating"]
    
    sublord_signifies = kp_signification_chain(cusp_sublord, chart)
    # Count how many favorable vs negating houses the sublord signifies
    fav_count = len(set(sublord_signifies) & set(favorable))
    neg_count = len(set(sublord_signifies) & set(negating))
    
    if neg_count > fav_count:
        return {"promised": False, "reason": f"Sub-lord of cusp signifies more negating houses"}
    return {"promised": True, "strength": fav_count / (fav_count + neg_count)}
```

## 7.2 KP REQUIRES PLACIDUS CUSPS

**GAP:** KP analysis uses Whole Sign house numbers but should use Placidus cusps.

**FIX:** When computing KP significators, use Placidus cuspal degrees, not Whole Sign boundaries. This is fundamental to KP methodology.

```python
# In KP system, a planet's house is determined by which Placidus cusp boundaries it falls within.
# NOT by its sign. A planet at 29° Aries could be in the 2nd Placidus house even if 
# Aries = 1st house in Whole Sign.

def kp_house_of_planet(planet_longitude, placidus_cusps):
    """Determine house by Placidus cusps for KP analysis"""
    for i in range(12):
        cusp_start = placidus_cusps[i]
        cusp_end = placidus_cusps[(i + 1) % 12]
        if cusp_start < cusp_end:
            if cusp_start <= planet_longitude < cusp_end:
                return i + 1
        else:  # Wraps around 360°
            if planet_longitude >= cusp_start or planet_longitude < cusp_end:
                return i + 1
    return 1  # Fallback
```

**WHERE TO ADD:** `analysis/kp_analysis.py` — add Placidus cusp integration

**PRIORITY:** HIGH — Fundamental KP accuracy issue

---

# SECTION 8: PREDICTION METHODOLOGY — DOMAIN RULES

## 8.1 CAREER PREDICTION — COMPLETE FACTOR LIST

```python
CAREER_FACTORS = {
    "natal_promise": {
        "10th_house": "Condition and strength of 10th house",
        "10th_lord": "Placement, strength, dignity of 10th lord",
        "Sun": "Natural karaka for authority, government, leadership",
        "Saturn": "Natural karaka for profession, discipline, service",
        "Mercury": "Natural karaka for business, communication, trade",
        "D10_analysis": "Dashamsha chart — confirms career direction and quality",
        "A10": "Arudha of 10th house — public perception of career",
        "AmK_in_D1_D10": "Jaimini Amatya Karaka placement",
        "Karakamsha_10th": "Planets in 10th from Karakamsha",
    },
    "timing": {
        "Dasha_of_10th_lord": "Career events during 10th lord's dasha",
        "Dasha_of_planet_in_10th": "Events during dasha of planet occupying 10th",
        "Double_transit_on_10th": "Jupiter AND Saturn both influencing 10th house",
        "Saturn_transit_10th": "Major career restructuring every ~7 years",
        "Jupiter_transit_10th": "Career expansion/promotion opportunity",
    },
    "KP": {
        "10th_cusp_sublord": "If signifies 2,6,10,11 → career growth",
        "6th_cusp_sublord": "Service/employment analysis",
    }
}
```

## 8.2 MARRIAGE PREDICTION — COMPLETE FACTOR LIST

```python
MARRIAGE_FACTORS = {
    "natal_promise": {
        "7th_house": "Condition and occupants",
        "7th_lord": "Placement and dignity",
        "Venus": "Natural marriage karaka (male charts)",
        "Jupiter": "Natural marriage karaka (female charts traditionally)",
        "D9_analysis": "Navamsha — PRIMARY chart for marriage quality",
        "D9_7th_house": "7th of Navamsha = spouse personality",
        "UL": "Upapada Lagna — marriage perception and stability",
        "DK": "Darakaraka — soul-level marriage significator",
        "A7": "Darapada — short-term relationships vs A12 (UL) for marriage",
        "2nd_from_UL": "Sustenance of marriage",
        "Manglik_check": "Mars in 1,4,7,8,12 from Lagna/Moon/Venus",
    },
    "denial_conditions": [
        "7th lord combust + Venus combust + no benefic in 7th",
        "7th house hemmed by malefics (Papakartari) + weak 7th lord",
        "Saturn + Rahu in 7th without Jupiter aspect",
        "KP: 7th cusp sublord signifies 6,12 more than 2,7,11",
        "All malefics in 1,7 axis without benefic intervention",
    ],
    "timing": {
        "Dasha_of_7th_lord_or_Venus": "Primary marriage dasha",
        "Double_transit_on_7th_or_1st": "Jupiter+Saturn influence required",
        "Chara_dasha_of_UL_sign": "Jaimini marriage timing",
        "Age_of_Venus_maturity": "25 years — marriage possibility increases",
    }
}
```

## 8.3 FINANCE PREDICTION — COMPLETE FACTOR LIST

```python
FINANCE_FACTORS = {
    "natal_promise": {
        "2nd_house": "Accumulated wealth, family wealth",
        "11th_house": "Gains, income, fulfillment of desires",
        "2nd_lord_11th_lord": "Connection between them = Dhana Yoga",
        "Jupiter": "Natural karaka for wealth and expansion",
        "D2_Hora": "Hora chart — wealth potential (Sun Hora vs Moon Hora)",
        "Dhana_Yogas": "Count and strength of all wealth combinations",
        "A2_A11": "Arudha Padas for wealth perception",
    },
    "timing": {
        "Dasha_of_2nd_or_11th_lord": "Wealth accumulation periods",
        "Double_transit_on_2_or_11": "Jupiter+Saturn = wealth event trigger",
        "Jupiter_transit_2nd": "Expansion of wealth",
        "Saturn_transit_11th": "Structured/delayed but substantial gains",
    }
}
```

## 8.4 HEALTH PREDICTION — COMPLETE FACTOR LIST

```python
HEALTH_FACTORS = {
    "natal_promise": {
        "Lagna": "Constitution, vitality, physical body",
        "Lagna_lord": "Overall health controller",
        "6th_house": "Diseases, immunity, recovery ability",
        "8th_house": "Chronic illness, longevity, surgeries",
        "Sun": "Vitality, heart, bones, father's health",
        "Moon": "Mental health, fluids, mother's health",
        "D30_Trimsamsha": "Chart specifically for health/misfortunes",
        "Balarishta": "Infant mortality yoga checks (age 0-12)",
        "22nd_Drekkana_lord": "Potential health crisis trigger",
        "Mrityu_Bhaga": "Death-inflicting degrees — planets here cause health issues",
        "Gandanta_planets": "Planets at water-fire junctions",
    },
    "longevity_methods": {
        "Pindayu": "Based on planetary longitudes — already implemented",
        "Nisargayu": "Based on natural planetary periods",
        "Amsayu": "Based on Navamsha positions",
        "Alpa_Madhya_Purna": {
            "Alpa_Ayu": "Short life: 0-32 years",
            "Madhya_Ayu": "Medium life: 32-64 years",
            "Purna_Ayu": "Full life: 64-100 years",
            # Determined by: Lagna lord, 8th lord, and Moon
            # All three in movable/fixed/dual signs → specific band
        }
    },
    "medical_astrology_body_mapping": {
        "Sun": "Heart, right eye, bones, head, stomach, constitution",
        "Moon": "Mind, left eye, blood, breast, kidneys, uterus, fluids",
        "Mars": "Blood, muscles, marrow, energy, surgery, accidents, burns",
        "Mercury": "Nerves, skin, speech, intellect, respiratory, intestines",
        "Jupiter": "Liver, fat, diabetes, tumors, ears, brain",
        "Venus": "Reproductive system, face, eyes, kidneys, throat",
        "Saturn": "Bones, teeth, joints, chronic diseases, aging, depression",
        "Rahu": "Rare/hard-to-diagnose diseases, poisons, addictions, anxiety",
        "Ketu": "Mysterious ailments, viruses, spiritual/psychosomatic issues",
    },
    "GUARDRAIL": "NEVER display specific longevity numbers without disclaimer. Use Alpa/Madhya/Purna bands only. Gate numerical display behind explicit config flag."
}
```

---

# SECTION 9: SYNTHESIS & CONVERGENCE — RESOLVING CONFLICTS

## 9.1 EVIDENCE HIERARCHY (Classical Priority)

```python
EVIDENCE_HIERARCHY = {
    1: "NATAL PROMISE (D1 + D9)",  # If natal chart denies, nothing can override
    2: "DIVISIONAL CHART CONFIRMATION",  # D9 overrides D1 for marriage quality
    3: "DASHA ACTIVATION",  # Which dasha lord + period is running
    4: "DOUBLE TRANSIT",  # Jupiter + Saturn both must support
    5: "ASHTAKAVARGA TRANSIT",  # BAV transit quality
    6: "GOCHAR + SUDARSHANA",  # Transit from Lagna/Moon/Sun
    7: "KP SUB-LORD",  # Validates or denies at granular level
    8: "JAIMINI CHARA DASHA",  # Independent timing confirmation
    9: "SARVATOBHADRA CHAKRA",  # Nakshatra-level transit cross-validation
}

# RULE: An event can ONLY manifest if:
# 1. Natal promise exists (Level 1 — hard gate)
# 2. Dasha supports (Level 3 — required)
# 3. Double transit supports (Level 4 — required for major events)
# 4. At least 2 more lower-level systems agree (Levels 5-9)
```

## 9.2 PARASHARI VS JAIMINI DISAGREEMENT RESOLUTION

```python
def resolve_parashari_jaimini(parashari_score, jaimini_score, domain):
    """
    When Parashari and Jaimini predictions disagree:
    
    Classical guidance:
    - Parashari is PRIMARY for event prediction (will it happen?)
    - Jaimini is PRIMARY for narrative/perception (how is it experienced?)
    - For TIMING: if Vimshottari and Chara Dasha both point to same window → very strong
    - For MARRIAGE specifically: Jaimini (UL, DK) gets EQUAL weight to Parashari (7th house)
    
    Resolution:
    - Agreement = multiply confidence by 1.2 (convergence bonus)
    - Mild disagreement = use weighted average (Parashari 60%, Jaimini 40%)
    - Strong disagreement = cap confidence at 0.5 and flag uncertainty
    """
    agreement = 1.0 - abs(parashari_score - jaimini_score)
    
    if agreement > 0.7:  # Both systems agree
        combined = max(parashari_score, jaimini_score) * 1.15
    elif agreement > 0.4:  # Mild disagreement
        if domain == "Marriage":
            combined = parashari_score * 0.50 + jaimini_score * 0.50
        else:
            combined = parashari_score * 0.60 + jaimini_score * 0.40
    else:  # Strong disagreement
        combined = min(parashari_score * 0.60 + jaimini_score * 0.40, 0.50)
    
    return min(combined, 1.0)
```

## 9.3 FIXING THE DOUBLE-COUNTING BUG

**GAP:** `dasha_alignment` and `yoga_activation` both use the dasha planet, treated as independent in Bayesian layer.

**FIX:**
```python
# In bayesian_layer.py, make dasha and yoga share pseudo-observations:
# Instead of:
#   dasha_update: 3 pseudo-observations (independent)
#   yoga_update: 2 pseudo-observations (independent)
# 
# Use:
#   dasha_yoga_combined: 3 pseudo-observations total
#   - If dasha planet is ALSO the yoga planet, use SAME 3 observations (not 3+2)
#   - If different planets, keep separate but reduce yoga to 1 pseudo-observation

def compute_bayesian_update(dasha_planet, yoga_planets, ...):
    overlap = dasha_planet in yoga_planets
    if overlap:
        # Combined update: 3 pseudo-obs for both signals
        combined_strength = max(dasha_strength, yoga_strength)
        update_observations = 3
    else:
        # Separate: 3 for dasha, 1 for yoga (reduced from 2)
        dasha_obs = 3
        yoga_obs = 1  # Was 2, reduced to avoid inflation
```

**ALSO FIX:** `house_lord_strength` appearing in BOTH Promise pillars AND confidence.py:
```python
# Remove house_lord_strength from confidence.py weighted sum
# It's already captured in the Promise gate's Bhavesha pillar
# Redistribute its 7% weight to other components
```

**WHERE TO ADD:** `prediction/bayesian_layer.py` and `prediction/confidence.py`

**PRIORITY:** CRITICAL — Directly inflates confidence scores

---

# SECTION 10: ARCHITECTURAL IMPROVEMENTS

## 10.1 PREDICTION TIME WINDOW SEMANTICS

**GAP:** Confidence score has no defined time window.

**FIX:**
```python
# Every prediction must specify:
PREDICTION_SCHEMA = {
    "domain": "Career|Finance|Marriage|Health",
    "event_type": "promotion|job_change|wealth_gain|marriage|illness|...",
    "time_window": {
        "type": "dasha_period|transit_window|specific_date_range",
        "start": "date",
        "end": "date",
        "broad_envelope": "AD period dates",
        "trigger_peaks": ["list of transit peak dates within envelope"],
    },
    "confidence": {
        "promise_score": 0.0-1.0,      # Will this EVER happen?
        "timing_score": 0.0-1.0,       # Is the timing window correct?
        "combined_score": 0.0-1.0,     # Product of promise × timing
        "credible_interval": [low, high],
    },
    "supporting_evidence": {
        "parashari": {...},
        "jaimini": {...},
        "kp": {...},
        "transit": {...},
    }
}
```

## 10.2 MONTE CARLO BIRTH TIME SENSITIVITY

```python
def birth_time_sensitivity(chart_params, prediction_func, minutes_range=5, steps=11):
    """
    Run prediction with birth time ± 5 minutes in 1-minute increments.
    If prediction is STABLE across all runs → high confidence
    If prediction FLIPS → flag "birth time sensitive" and reduce confidence
    """
    results = []
    for delta_minutes in range(-minutes_range, minutes_range + 1):
        modified_params = chart_params.copy()
        modified_params['birth_time'] += timedelta(minutes=delta_minutes)
        result = prediction_func(modified_params)
        results.append(result['confidence'])
    
    stability = 1.0 - np.std(results) / max(np.mean(results), 0.01)
    
    return {
        "mean_confidence": np.mean(results),
        "stability": stability,
        "birth_time_sensitive": stability < 0.7,
        "confidence_modifier": stability  # Multiply final confidence by this
    }
```

**WHERE TO ADD:** `prediction/engine.py` — wrap main prediction in sensitivity analysis

**PRIORITY:** MEDIUM — Cheap uncertainty quantification

---

# SECTION 11: QUICK-REFERENCE DATA TABLES

## 11.1 EXALTATION / DEBILITATION / MOOLATRIKONA

```python
PLANETARY_DIGNITY = {
    # Planet: (exaltation_sign, exact_degree, debilitation_sign, exact_degree, moolatrikona_sign, mt_degrees)
    "Sun":     ("Aries", 10, "Libra", 10, "Leo", "0-20"),
    "Moon":    ("Taurus", 3, "Scorpio", 3, "Taurus", "3-30"),
    "Mars":    ("Capricorn", 28, "Cancer", 28, "Aries", "0-12"),
    "Mercury": ("Virgo", 15, "Pisces", 15, "Virgo", "15-20"),
    "Jupiter": ("Cancer", 5, "Capricorn", 5, "Sagittarius", "0-10"),
    "Venus":   ("Pisces", 27, "Virgo", 27, "Libra", "0-15"),
    "Saturn":  ("Libra", 20, "Aries", 20, "Aquarius", "0-20"),
    "Rahu":    ("Taurus", None, "Scorpio", None, "Aquarius", None),  # Debated
    "Ketu":    ("Scorpio", None, "Taurus", None, "Leo", None),  # Debated
}
```

## 11.2 DIGBALA (DIRECTIONAL STRENGTH)

```python
DIGBALA = {
    # Planet: house_of_maximum_strength
    "Jupiter": 1,   # East (Lagna) — wise in presence
    "Mercury": 1,   # East (Lagna) — intelligent in presence
    "Sun": 10,      # North (10th) — authority at zenith
    "Mars": 10,     # North (10th) — warrior at zenith
    "Saturn": 7,    # West (7th) — discipline in partnerships
    "Moon": 4,      # South (4th) — nourishing at home
    "Venus": 4,     # South (4th) — comfort at home
}
# Planet in opposite house (7th from Digbala house) has ZERO directional strength
```

## 11.3 NATURAL FRIENDSHIP TABLE

```python
NATURAL_FRIENDSHIPS = {
    "Sun":     {"friends": ["Moon","Mars","Jupiter"], "enemies": ["Venus","Saturn"], "neutral": ["Mercury"]},
    "Moon":    {"friends": ["Sun","Mercury"], "enemies": [], "neutral": ["Mars","Jupiter","Venus","Saturn"]},
    "Mars":    {"friends": ["Sun","Moon","Jupiter"], "enemies": ["Mercury"], "neutral": ["Venus","Saturn"]},
    "Mercury": {"friends": ["Sun","Venus"], "enemies": ["Moon"], "neutral": ["Mars","Jupiter","Saturn"]},
    "Jupiter": {"friends": ["Sun","Moon","Mars"], "enemies": ["Mercury","Venus"], "neutral": ["Saturn"]},
    "Venus":   {"friends": ["Mercury","Saturn"], "enemies": ["Sun","Moon"], "neutral": ["Mars","Jupiter"]},
    "Saturn":  {"friends": ["Mercury","Venus"], "enemies": ["Sun","Moon","Mars"], "neutral": ["Jupiter"]},
}
# Rahu acts like Saturn, Ketu acts like Mars for friendship purposes
```

---

# END OF KNOWLEDGE BASE

## IMPLEMENTATION PRIORITY SUMMARY:

| # | FIX | Impact | Effort |
|---|-----|--------|--------|
| 1 | Domain-specific BAV (fix AV=1.00 bug) | CRITICAL | 2 days |
| 2 | Double Transit hard gate | CRITICAL | 4 hours |
| 3 | Fix double-counting in Bayesian layer | CRITICAL | 2 hours |
| 4 | Jaimini → scoring pipeline integration | HIGH | 1 day |
| 5 | Dasha quality scoring (Ishta/Kashta) | HIGH | 1 day |
| 6 | Sudarshana Chakra (triple transit) | HIGH | 2 days |
| 7 | Complete Neecha Bhanga (8 conditions) | HIGH | 4 hours |
| 8 | Bhrigu Bindu transit activation | HIGH | 2 hours |
| 9 | Yoga expansion (50→300+) | HIGH | 3-5 days |
| 10 | Sarvatobhadra Chakra transit | HIGH | 3 days |
| 11 | KP Placidus cusp fix | HIGH | 4 hours |
| 12 | Per-planet combustion orbs | MEDIUM | 2 hours |
| 13 | Mrityu Bhaga table + modifier | MEDIUM | 3 hours |
| 14 | Gandanta severity scoring | MEDIUM | 2 hours |
| 15 | Planet maturity ages | MEDIUM | 1 hour |
| 16 | Complete Yoga Karaka table verification | HIGH | 2 hours |
| 17 | Prediction time window semantics | MEDIUM | 1 day |
| 18 | Monte Carlo birth time sensitivity | MEDIUM | 4 hours |
| 19 | Pushkara Navamsha/Bhaga | LOW | 2 hours |
| 20 | Nabhasa Yogas (32 pattern yogas) | MEDIUM | 1 day |
