# PHASE 6 LAYER 2: Research-Backed Prediction Wiring
# For VS Code. Read MEMORY_INDEX.md first. Research files are in new6/ folder.
# Read each research file for full context. The rules below are extracted summaries.

---

## CONTEXT

You already have `classical_modifiers.py` from Layer 1. The key-mapping fix is done (predict() now passes correct data to modifiers).

This Layer 2 does THREE things:
1. Rewrites `classical_modifiers.py` with RESEARCH-BACKED weights (not guesses)
2. Creates `domain_signal_weights.py` — the domain-to-signal mapping with exact priorities
3. Creates `prediction_overrides.py` — the 5 master override situations that bypass normal scoring

Read the research files in new6/ for full details. The rules below are the implementable extracts.

---

## FILE 1: Rewrite classical_modifiers.py

Replace the current file with this improved version that uses research-validated formulas:

### Planet Effectiveness Formula (from Research File 4)

This replaces the separate Shadbala/Vimshopak/BAV/Avastha modifiers with ONE combined formula:

```python
def compute_planet_effectiveness(planet_name, computed):
    """
    Research formula: E = Avastha_Coefficient × [0.45×(NetShadbala/MinRequired) + 0.35×(Vimshopak/20) + 0.20×(BAV/8)]
    Returns 0.0 to ~2.0 scale.
    """
    # Avastha coefficient (absolute multiplier)
    AVASTHA_COEFFICIENTS = {
        "deepta": 1.00, "swastha": 0.875, "mudita": 0.75,
        "normal": 0.50, "dina": 0.125, "dukhita": 0.25,
        "kshobhita": 0.125, "vriddha": 0.10, "mrita": 0.00,
    }
    
    avasthas = computed.get("avasthas", {})
    avastha_data = avasthas.get(planet_name, {})
    state = avastha_data.get("state", "normal").lower()
    avastha_coeff = AVASTHA_COEFFICIENTS.get(state, 0.50)
    
    if avastha_coeff == 0.0:
        return 0.0  # Dead planet = zero output
    
    # Shadbala ratio (Net = total minus Saptavargaja to avoid Vimshopak overlap)
    shadbala = computed.get("shadbala", {}).get(planet_name, {})
    ratio = shadbala.get("ratio", 1.0) if isinstance(shadbala, dict) else 1.0
    shadbala_component = min(ratio, 2.0)  # Cap at 2.0
    
    # Vimshopak (out of 20)
    vimshopak = computed.get("vimshopak", {}).get(planet_name, {})
    vim_score = vimshopak.get("score", 10) if isinstance(vimshopak, dict) else 10
    vimshopak_component = vim_score / 20.0
    
    # BAV score (out of 8, use the sign the planet occupies)
    bav_score = 4  # default neutral
    ashtakvarga = computed.get("ashtakvarga", {})
    bav_data = ashtakvarga.get("bav", {}).get(planet_name)
    if isinstance(bav_data, list):
        # Get planet's sign index
        planet_sign_idx = computed.get("planet_signs", {}).get(planet_name)
        if planet_sign_idx is not None and planet_sign_idx < len(bav_data):
            bav_score = bav_data[planet_sign_idx]
    bav_component = bav_score / 8.0
    
    # Combined formula
    raw_effectiveness = (0.45 * shadbala_component + 0.35 * vimshopak_component + 0.20 * bav_component)
    
    # Apply avastha as absolute multiplier
    return avastha_coeff * raw_effectiveness
```

### Bhava Effectiveness Formula (from Research File 4)

```python
def compute_bhava_effectiveness(house_num, lord_planet, computed):
    """
    Research formula: Realized_Output = Normalized_Bhava_Bala × log(Lord_Shadbala_Ratio)
    """
    import math
    
    bhavabala = computed.get("bhavabala", {})
    house_data = bhavabala.get(house_num, {})
    rupas = house_data.get("rupas", 7.0) if isinstance(house_data, dict) else 7.0
    
    # Normalize: 7.0 rupas = 1.0 (threshold), scale linearly
    normalized_bhava = rupas / 7.0
    
    # Lord's shadbala ratio
    lord_effectiveness = compute_planet_effectiveness(lord_planet, computed)
    
    # Combine: house environment × log of lord strength
    # log(1.0) = 0, log(2.0) = 0.69 — so we shift: log(ratio + 1) to keep positive
    lord_factor = math.log(lord_effectiveness + 1.0) / math.log(2.0)  # normalize log2
    
    return normalized_bhava * max(lord_factor, 0.1)  # floor at 0.1
```

### Domain Karaka Mapping (from Research File 1 — EXACT priorities)

```python
# Research-validated primary signals per domain with weights
DOMAIN_CONFIG = {
    "career": {
        "primary_house": 10,
        "secondary_houses": [1, 6],
        "karaka": "SUN",           # Natural karaka
        "house_lord_key": 10,       # 10th lord is PRIMARY (wt: 9)
        "kp_cusp": 10,             # KP sub-lord of 10th (wt: 10)
        "divisional": "D10",        # D10 chart (wt: 9.5)
        "yoga_tags": ["raja", "mahapurusha", "adhi", "bhadra", "ruchaka", "saraswati", "career", "power"],
        "yoga_boosts": {"dharma_karmadhipati": 0.35, "adhi": 0.25, "bhadra": 0.20, "ruchaka": 0.20, "saraswati": 0.20},
    },
    "finance": {
        "primary_house": 11,        # 11th lord is PRIMARY for income (wt: 10)
        "secondary_houses": [2, 5, 9],
        "karaka": "JUPITER",
        "house_lord_key": 11,
        "kp_cusp": 11,
        "divisional": "D2",
        "yoga_tags": ["dhana", "wealth", "lakshmi", "finance"],
        "yoga_boosts": {"maha_dhan": 0.40, "dhana": 0.30, "lakshmi": 0.25, "gajakesari": 0.15},
    },
    "marriage": {
        "primary_house": 7,
        "secondary_houses": [1, 2],
        "karaka": "VENUS",
        "house_lord_key": 7,
        "kp_cusp": 7,
        "divisional": "D9",         # D9 weight = equal to D1 (wt: 10)
        "yoga_tags": ["marriage", "kalatra", "vivaha", "parivartana"],
        "yoga_boosts": {"parivartana_7h": 0.25, "early_marriage": 0.20, "love_marriage": 0.15, "gajakesari": 0.10},
    },
    "health": {
        "primary_house": 1,         # Lagna lord is PRIMARY (wt: 10)
        "secondary_houses": [6, 8, 12],
        "karaka": "MOON",           # Moon for mental health
        "house_lord_key": 1,
        "kp_cusp": 1,
        "divisional": "D30",        # D30 for health (wt: 9)
        "yoga_tags": ["health", "longevity", "aristha", "balarishta", "medical"],
        "yoga_boosts": {"balarishta_bhanga": 0.40, "purna_ayush": 0.35, "arishta": -0.30, "vipreet_raja": 0.30},
    },
}
```

### Dasha Convergence (from Research File 2)

```python
# Dasha system weights per domain
DASHA_WEIGHTS = {
    "career":  {"vimshottari": 0.40, "chara": 0.25, "yogini": 0.15, "ashtottari": 0.10, "other": 0.10},
    "finance": {"vimshottari": 0.45, "ashtottari": 0.25, "chara": 0.15, "yogini": 0.10, "other": 0.05},
    "marriage": {"vimshottari": 0.40, "chara": 0.25, "yogini": 0.20, "ashtottari": 0.10, "other": 0.05},
    "health":  {"niryana_shoola": 0.40, "kalachakra": 0.20, "vimshottari": 0.20, "sudarshana": 0.15, "other": 0.05},
}

# Convergence confidence (from BVB study)
CONVERGENCE_TABLE = {
    # (agreeing / total) → confidence multiplier
    0.0: 0.05,   # 0% agree
    0.2: 0.10,   # 1/5 agree
    0.4: 0.325,  # 2/5 agree
    0.6: 0.725,  # 3/5 agree
    0.8: 0.965,  # 4/5 agree
    1.0: 0.999,  # 5/5 agree
}

def get_convergence_confidence(ratio):
    """Interpolate convergence confidence from research table."""
    if ratio <= 0.0: return 0.05
    if ratio >= 1.0: return 0.999
    # Linear interpolation between nearest points
    keys = sorted(CONVERGENCE_TABLE.keys())
    for i in range(len(keys) - 1):
        if keys[i] <= ratio <= keys[i+1]:
            low_k, high_k = keys[i], keys[i+1]
            low_v, high_v = CONVERGENCE_TABLE[low_k], CONVERGENCE_TABLE[high_k]
            t = (ratio - low_k) / (high_k - low_k)
            return low_v + t * (high_v - low_v)
    return 0.50
```

### Transit Weights (from Research File 3)

```python
# BAV score → transit multiplier (research-corrected)
BAV_TRANSIT_MULTIPLIERS = {
    0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0,  # BAV 0-3: destructive, zero good results
    4: 1.0,                             # BAV 4: neutral
    5: 1.5, 6: 1.5, 7: 1.5, 8: 1.5,   # BAV 5-8: highly auspicious
}

# Transit reference frame weights
TRANSIT_FRAME_WEIGHTS = {
    "lagna": 0.50,      # Objective/physical events
    "moon": 0.275,      # Subjective/emotional
    "dasha_lord": 0.20, # Vitality/authority
}

# Double transit: aspect counts as transit
# Required for MAJOR events only, not minor
```

### Master Override Checks (from Research File 6)

```python
def check_master_overrides(computed, domain):
    """
    5 override situations that bypass normal scoring.
    Returns (is_override, override_confidence, override_description) or (False, None, None).
    """
    
    # Override 1: Sade Sati + weak Moon BAV
    sade_sati = computed.get("sade_sati", {})
    if sade_sati.get("active", False):
        moon_bav_total = computed.get("ashtakvarga", {}).get("sav", [0]*12)
        # Check Moon sign SAV
        moon_sign_idx = computed.get("moon_sign_index")
        if moon_sign_idx is not None and isinstance(moon_bav_total, list):
            if moon_sign_idx < len(moon_bav_total) and moon_bav_total[moon_sign_idx] < 25:
                return (True, 0.95, "Sade Sati + Weak Moon SAV: Extreme stress period")
    
    # Override 2: Dasha Sandhi (transition between major periods)
    dasha_sandhi = computed.get("dasha_sandhi", False)
    if dasha_sandhi:
        return (True, 0.90, "Dasha Sandhi: High volatility, avoid major decisions")
    
    # Override 3: Transiting Saturn conjunct Rahu on Lagna or Moon
    # (check from transit data if available)
    
    # Override 4: Vipreet Raja Yoga active in current dasha
    active_dasha_lord = computed.get("active_dasha", {}).get("lord", "")
    yogas = computed.get("yogas", [])
    for yoga in yogas:
        if isinstance(yoga, dict):
            name = yoga.get("name", "").lower()
            planets = [p.upper() for p in yoga.get("planets", [])]
            if "vipreet" in name and active_dasha_lord.upper() in planets:
                return (True, 0.85, "Vipreet Raja Yoga active: Crisis followed by massive gain")
    
    # Override 5: Dasha lord Vimshopak >= 18
    vimshopak = computed.get("vimshopak", {}).get(active_dasha_lord, {})
    vim_score = vimshopak.get("score", 0) if isinstance(vimshopak, dict) else 0
    if vim_score >= 18:
        return (True, 0.90, "Dasha lord has exceptional Vimshopak: Guaranteed benefic results")
    
    return (False, None, None)
```

### Confidence Calibration Scale (from Research File 6)

```python
CONFIDENCE_LABELS = {
    (0.00, 0.08): "Highly Unlikely",
    (0.08, 0.15): "Event Latent / No Trigger",
    (0.15, 0.35): "Unlikely but Possible",
    (0.35, 0.58): "Average Results / High Friction",
    (0.58, 0.63): "Neutral Results",
    (0.63, 0.70): "Likely",
    (0.70, 0.78): "Moderate Success",
    (0.78, 0.88): "Highly Probable",
    (0.88, 1.00): "Will Definitely Happen",
}
```

---

## FILE 2: Create domain_signal_weights.py

```python
"""
Domain-specific signal weights from deep research.
Each domain has ranked primary/secondary signals with exact weights (1-10 scale).
Used by the prediction pipeline to determine which computed values matter most.
"""

DOMAIN_SIGNALS = {
    "career": {
        "primary": [
            ("kp_sublord_10", 10.0),
            ("d10_10th_lord_placement", 9.5),
            ("vimshottari_dasha_10th_connection", 9.0),
            ("d10_10th_house_lord", 8.5),
            ("double_transit_10_1", 8.0),
        ],
        "secondary": [
            ("vimshopak_10th_lord", 7.5),
            ("raja_mahapurusha_yogas", 7.0),
            ("avastha_10th_lord", 7.0),
            ("bav_10th_sign", 6.5),
            ("sun_karaka_strength", 6.0),
        ],
    },
    "finance": {
        "primary": [
            ("11th_lord_strength", 10.0),
            ("2nd_lord_strength", 9.5),
            ("sav_11_and_2", 9.0),
            ("dasha_dhana_yoga_activation", 8.5),
            ("d2_hora_dignity", 8.0),
        ],
        "secondary": [
            ("daridra_yogas", 7.5),
            ("8th_house_linkage", 7.0),
            ("jupiter_strength", 6.5),
            ("12th_house_prominence", 6.0),
            ("2nd_vs_11th_comparison", 5.0),
        ],
    },
    "marriage": {
        "primary": [
            ("bvb_md_ad_1_7_connection", 10.0),
            ("d9_7th_house_lord_dignity", 10.0),
            ("bvb_lagna_7th_lord_connection", 9.8),
            ("chara_dasha_dk_ul_connection", 9.6),
            ("upapada_lagna_condition", 9.0),
        ],
        "secondary": [
            ("d1_7th_lord_placement", 8.5),
            ("double_transit_7_1", 8.5),
            ("darakaraka_condition", 7.5),
            ("venus_karaka_condition", 7.0),
            ("manglik_dosha", 6.0),
        ],
    },
    "health": {
        "primary": [
            ("lagna_lord_strength", 10.0),
            ("dasha_6_8_12_activation", 9.5),
            ("d30_trimsamsha_affliction", 9.0),
            ("moon_dignity", 8.5),
            ("maraka_lord_dasha", 8.0),
        ],
        "secondary": [
            ("8th_house_prominence", 7.5),
            ("6th_house_prominence", 7.0),
            ("sade_sati_active", 6.0),
            ("malefic_transit_lagna_moon", 6.0),
            ("12th_house_prominence", 5.5),
        ],
    },
}
```

---

## FILE 3: Create prediction_overrides.py

Contains `check_master_overrides()` function from above. This gets called BEFORE normal scoring in predict(). If an override fires, it short-circuits the normal pipeline.

---

## WIRING INTO predict()

The flow in predict() should now be:

```python
# STEP 0: Check overrides FIRST
is_override, override_conf, override_desc = check_master_overrides(computed, domain)
if is_override:
    # Short-circuit: return override confidence directly
    confidence["override"] = True
    confidence["override_description"] = override_desc
    confidence["final"] = override_conf
    # Still compute rest for display, but final score is override_conf

# STEP 1: Promise Gate (existing — keep as is)

# STEP 2: Raw confidence from 8 components (existing — keep as is)

# STEP 3: Planet effectiveness modifier (NEW — replaces old separate modifiers)
domain_cfg = DOMAIN_CONFIG.get(domain, {})
karaka = domain_cfg.get("karaka", "SUN")
house_lord = domain_cfg.get("house_lord_key", 10)
lord_planet = house_lords.get(house_lord, karaka)

planet_eff = compute_planet_effectiveness(lord_planet, computed)
bhava_eff = compute_bhava_effectiveness(domain_cfg["primary_house"], lord_planet, computed)
domain_modifier = (0.60 * planet_eff + 0.40 * bhava_eff)

confidence["raw_adjusted"] = confidence["raw"] * max(domain_modifier, 0.10)

# STEP 4: Dasha convergence (NEW — replaces old 0.15× gate)
dasha_weights = DASHA_WEIGHTS.get(domain, {})
weighted_agreement = 0.0
for system, weight in dasha_weights.items():
    if system_supports_domain(system, domain):  # check if this dasha says yes
        weighted_agreement += weight
convergence_conf = get_convergence_confidence(weighted_agreement)
confidence["convergence"] = convergence_conf

# STEP 5: Dosha penalties (keep from Layer 1, only Manglik/KSY/Pitru)
dosha_mod = _dosha_modifier(computed, domain)
confidence["dosha_modifier"] = dosha_mod

# STEP 6: Bayesian + Fuzzy (existing — use raw_adjusted × convergence × dosha_mod)
adjusted_input = confidence["raw_adjusted"] * convergence_conf * dosha_mod

# STEP 7: Yoga activation boost
yoga_boost = compute_yoga_domain_boost(computed, domain)  # from research yoga boosts
confidence["yoga_boost"] = yoga_boost

# STEP 8: Final = adjusted_input × (1 + yoga_boost)
confidence["final"] = min(adjusted_input * (1.0 + yoga_boost), 0.999)
```

---

## YOGA BOOST FUNCTION

```python
def compute_yoga_domain_boost(computed, domain):
    """
    Research: First major yoga = big baseline boost, subsequent = diminishing returns (logarithmic).
    Returns a boost value: 0.0 (no yogas) to ~0.50 (exceptional yoga combinations).
    """
    import math
    
    cfg = DOMAIN_CONFIG.get(domain, {})
    yoga_boosts = cfg.get("yoga_boosts", {})
    yogas = computed.get("yogas", [])
    active_dasha_lord = computed.get("active_dasha", {}).get("lord", "").upper()
    
    activated_boosts = []
    
    for yoga in yogas:
        if isinstance(yoga, dict):
            name = yoga.get("name", "").lower().replace(" ", "_")
            planets = [p.upper() for p in yoga.get("planets", [])]
            
            # Check if yoga matches any known boost for this domain
            for boost_key, boost_val in yoga_boosts.items():
                if boost_key in name:
                    # Check if activated by dasha
                    if active_dasha_lord in planets:
                        activated_boosts.append(boost_val)
                    else:
                        activated_boosts.append(boost_val * 0.30)  # Dormant: 30% of full boost
    
    if not activated_boosts:
        return 0.0
    
    # Logarithmic diminishing returns
    activated_boosts.sort(reverse=True)
    total_boost = 0.0
    for i, boost in enumerate(activated_boosts):
        total_boost += boost / (1.0 + i * 0.5)  # Each subsequent yoga contributes less
    
    return min(total_boost, 0.50)  # Cap at 50% boost
```

---

## TEST

After implementation:
1. Run Nehru breakdown: print planet_effectiveness and bhava_effectiveness for each domain's karaka
2. Run full pipeline: generate content46
3. Compare: Career/Finance/Marriage/Health scores should now DIFFERENTIATE (not all identical)
4. Check that overrides fire when appropriate (Sade Sati, Dasha Sandhi, etc.)

## RULES
- Read new6/ research files for full context before implementing
- The DOMAIN_CONFIG, DASHA_WEIGHTS, CONVERGENCE_TABLE, BAV_TRANSIT_MULTIPLIERS are from verified research — implement exactly
- Planet effectiveness formula REPLACES the old separate shadbala/vimshopak/bhavabala/avastha modifiers
- Convergence table REPLACES the old consensus gate entirely
- Override checks happen BEFORE normal scoring
- Yoga boosts are ADDITIVE on top of the base score, not multiplicative
- Update MEMORY_INDEX.md and CHANGELOG.md after implementation