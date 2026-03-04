# PHASE 3: New Timing Systems & Cross-Tradition Integration
# MASTER INSTRUCTION FOR VS CODE OPUS
# Execute ALL phases continuously — do NOT stop between sub-phases
# Only stop if you encounter an ambiguity that requires human clarification

---

## SETUP

- Research files are in the `new3/` folder
- Read MEMORY_INDEX.md before starting
- Follow RULEBOOK.md for every change
- After EVERY sub-phase: run test chart, verify EXIT:0, update memory files
- Architecture rule: ALL new computations go into CORE as pure functions. They compute and return classical results. NO weights, NO blending, NO prediction logic inside core functions. The prediction layer wiring happens separately at the end.

---

## EXECUTION ORDER

Read ONE research file at a time. Implement everything from that file. Then move to next file. Do not read all files at once.

---

## PHASE 3A: Nadi Timing Systems
**Read:** `new3/` file about Nadi system (the one covering BCP, BNN, Patel formulas, Saturn transit activation)
**Where to add:** Create new file `vedic_engine/timing/nadi_timing.py` OR add to existing timing module

### 3A.1: Bhrigu Chakra Paddathi (BCP)
```python
def compute_bcp_active_house(age_years):
    """Maps current age to the active house via 12-year cycle."""
    return ((age_years - 1) % 12) + 1
```
- Call from engine.py with the native's current age
- Store result in `static["computed"]["bcp_active_house"]`
- Also store which planets occupy that house: `static["computed"]["bcp_active_planets"]`
- This tells us: "At age 25, house 1 is activated. Whatever planets are in house 1 will deliver results this year."

### 3A.2: Nadi Saturn Transit Activation
```python
def check_nadi_saturn_activation(saturn_transit_longitude, natal_planet_longitudes, orb=3.0):
    """When transit Saturn conjuncts any natal planet within orb, that planet's karakatwa activates."""
    activated = []
    for planet, natal_long in natal_planet_longitudes.items():
        distance = abs(saturn_transit_longitude - natal_long) % 360
        if distance > 180:
            distance = 360 - distance
        if distance <= orb:
            activated.append(planet)
    return activated
```
- Call from engine.py during transit evaluation
- Store in `static["computed"]["nadi_saturn_activated_planets"]`
- This is MORE specific than generic Sade Sati — it tells us WHICH planet Saturn is activating right now

### 3A.3: Patel Marriage Timing Formulas
```python
def compute_patel_marriage_dates(asc_longitude_degrees, birth_date):
    """Two Nadi formulas that compute candidate marriage dates."""
    candidates = []
    for n in range(5):  # check first 5 cycles
        days_formula_1 = (asc_longitude_degrees * 324) + (n * 10800)
        days_formula_2 = (asc_longitude_degrees * 216) + (n * 10800)
        candidates.append({
            "formula": "patel_324",
            "days_from_birth": days_formula_1,
            "date": birth_date + timedelta(days=int(days_formula_1))
        })
        candidates.append({
            "formula": "patel_216",
            "days_from_birth": days_formula_2,
            "date": birth_date + timedelta(days=int(days_formula_2))
        })
    return candidates
```
- Use the Navamsha Ascendant longitude (D9 ASC), not D1
- Store in `static["computed"]["patel_marriage_candidates"]`
- These are candidate dates — the prediction layer will later check if any fall within the current dasha/transit window

### 3A.4: BNN Graph Connectivity (Nadi Sign-Based)
```python
def compute_bnn_graph(planet_signs):
    """Compute Bhrigu Nandi Nadi sign-based connectivity graph.
    No Lagna needed — purely sign-to-sign relationships."""
    edges = []
    planets = list(planet_signs.keys())
    for i, p1 in enumerate(planets):
        for p2 in planets[i+1:]:
            sign_distance = (planet_signs[p2] - planet_signs[p1]) % 12
            if sign_distance in [0]:  # conjunction (same sign)
                edges.append({"p1": p1, "p2": p2, "type": "conjunction", "weight": 1.0})
            elif sign_distance in [4, 8]:  # trine (5th/9th = indices 4,8)
                edges.append({"p1": p1, "p2": p2, "type": "trine", "weight": 1.0})
            elif sign_distance in [6]:  # opposition (7th = index 6)
                edges.append({"p1": p1, "p2": p2, "type": "opposition", "weight": 0.5})
            elif sign_distance in [1, 11]:  # adjacent (2nd/12th)
                edges.append({"p1": p1, "p2": p2, "type": "adjacent", "weight": 0.75})
    return edges
```
- Store in `static["computed"]["bnn_graph"]`
- Also compute: for each planet, count its total edge weight = its "connectivity score"

### 3A.5: Spouse Profession Algorithm
```python
def compute_spouse_career_sign(venus_sign_index):
    """Nadi rule: spouse career determined by 10th house from Venus."""
    return (venus_sign_index + 9) % 12  # 10th from Venus
```
- Store in `static["computed"]["spouse_career_sign"]`
- Check which planets occupy this sign — they indicate spouse's career nature

### 3A.6: BNN Retrograde Dual-Sign Rule
```python
def compute_bnn_retrograde_influence(planet, planet_sign, is_retrograde):
    """Retrograde planets influence both current sign and previous sign."""
    if is_retrograde:
        return [planet_sign, (planet_sign - 1) % 12]
    return [planet_sign]
```
- Apply this in the BNN graph computation — retrograde planets get edges from BOTH signs

**After 3A: Run test, verify EXIT:0, update memory. Then continue immediately to 3B.**

---

## PHASE 3B: Hellenistic Timing Systems
**Read:** `new3/` file about cross-tradition techniques (Western, Hellenistic, Chinese)
**Where to add:** Create new file `vedic_engine/timing/hellenistic.py`

### 3B.1: Annual Profections + Time Lord
```python
def compute_annual_profection(natal_asc_sign_index, age_years):
    """Each year activates the next sign from Ascendant. Lord of that sign = Time Lord."""
    active_sign = (natal_asc_sign_index + age_years) % 12
    return {
        "active_sign": active_sign,
        "time_lord": SIGN_LORDS[active_sign],  # use existing sign lords table
        "age": age_years
    }
```
- Store in `static["computed"]["annual_profection"]`
- This is essentially the same as Sudarshana yearly progression — but extract the Time Lord explicitly
- The Time Lord is the most important planet for the entire year

### 3B.2: Hellenistic Sect (Day/Night Functional Override)
```python
def compute_sect_dignity(is_daytime):
    """Day charts: Sun/Jupiter/Saturn are sect-favored. Night charts: Moon/Venus/Mars are sect-favored."""
    if is_daytime:
        return {
            "sect_benefics": ["SUN", "JUPITER", "SATURN"],
            "sect_malefics": ["MOON", "VENUS", "MARS"],
            "sect_light": "SUN",
            "sect_benefic_of_sect": "JUPITER",
            "sect_malefic_of_sect": "SATURN"  # least malefic malefic for day
        }
    else:
        return {
            "sect_benefics": ["MOON", "VENUS", "MARS"],
            "sect_malefics": ["SUN", "JUPITER", "SATURN"],
            "sect_light": "MOON",
            "sect_benefic_of_sect": "VENUS",
            "sect_malefic_of_sect": "MARS"  # least malefic malefic for night
        }
```
- Store in `static["computed"]["hellenistic_sect"]`
- This does NOT replace the Vedic functional classification — it's stored separately as an additional perspective
- Mercury is ALWAYS neutral in sect — it joins the sect of whichever planet it's closest to

### 3B.3: Zodiacal Releasing (ZR)
This is the most complex item. Implement step by step:

```python
def compute_lot_of_spirit(asc_long, sun_long, moon_long, is_daytime):
    """Lot of Spirit = ASC + Sun - Moon (day) or ASC + Moon - Sun (night)."""
    if is_daytime:
        lot = (asc_long + sun_long - moon_long) % 360
    else:
        lot = (asc_long + moon_long - sun_long) % 360
    return lot

def compute_lot_of_fortune(asc_long, sun_long, moon_long, is_daytime):
    """Lot of Fortune = ASC + Moon - Sun (day) or ASC + Sun - Moon (night)."""
    # Reverse of Spirit
    if is_daytime:
        lot = (asc_long + moon_long - sun_long) % 360
    else:
        lot = (asc_long + sun_long - moon_long) % 360
    return lot

# Sign ruler period lengths (in years) for ZR:
ZR_PERIODS = {
    "SUN": 19, "MOON": 25, "MERCURY": 20, "VENUS": 8,
    "MARS": 15, "JUPITER": 12, "SATURN": 27
}
# Note: some sources use Saturn=30. Check the research file for which values it specifies.

def compute_zodiacal_releasing(lot_longitude, birth_date, target_date):
    """Compute ZR periods from a Lot (Spirit for career, Fortune for health/body).
    Steps through signs from the Lot's sign, each sign lasting ZR_PERIODS[sign_lord] years."""
    start_sign = int(lot_longitude / 30)
    periods = []
    current_date = birth_date
    current_sign = start_sign
    
    while current_date < target_date:
        lord = SIGN_LORDS[current_sign]
        duration_years = ZR_PERIODS.get(lord, 12)
        end_date = current_date + timedelta(days=int(duration_years * 365.25))
        periods.append({
            "sign": current_sign,
            "lord": lord,
            "start": current_date,
            "end": end_date,
            "duration_years": duration_years
        })
        current_date = end_date
        current_sign = (current_sign + 1) % 12  # advance to next sign
    
    # Find which period the target_date falls in
    current_period = None
    for p in periods:
        if p["start"] <= target_date < p["end"]:
            current_period = p
            break
    
    return {
        "lot_longitude": lot_longitude,
        "lot_sign": start_sign,
        "periods": periods,
        "current_period": current_period
    }
```
- Compute ZR from BOTH Lot of Spirit (career/action) and Lot of Fortune (health/body)
- Store in `static["computed"]["zodiacal_releasing_spirit"]` and `static["computed"]["zodiacal_releasing_fortune"]`
- "Loosing of the Bond" detection: when ZR transitions from an angular sign (1,4,7,10 from lot) to a cadent sign (3,6,9,12 from lot) → flag as "narrative fracture" period
- Peak eminence: when ZR is in angular signs from the lot AND the lord is well-dignified → flag

### 3B.4: Secondary Progressions
```python
def compute_secondary_progressions(birth_date, birth_time, target_date, latitude, longitude):
    """1 day after birth = 1 year of life.
    Compute planetary positions for birth + N days, where N = age in years."""
    age_years = (target_date - birth_date).days / 365.25
    progressed_date = birth_date + timedelta(days=age_years)  # 1 day = 1 year
    
    # Use SWE to compute planetary positions at progressed_date
    progressed_positions = compute_planet_positions(progressed_date, birth_time, latitude, longitude)
    
    return {
        "progressed_date": progressed_date,
        "positions": progressed_positions,
        "progressed_moon_sign": int(progressed_positions["MOON"] / 30),
        "progressed_sun_sign": int(progressed_positions["SUN"] / 30),
    }
```
- Store in `static["computed"]["secondary_progressions"]`
- Key signals to extract:
  - Progressed Moon sign = emotional theme of current ~2.5 year period
  - Progressed Moon conjunct natal planet = emotional activation
  - Progressed Sun sign change = major identity shift (happens every ~30 years)
- This requires an SWE call for the progressed date — use the same Swiss Ephemeris functions already in the codebase

### 3B.5: Western Midpoints (Cosmobiology)
```python
def compute_midpoints(planet_longitudes):
    """Compute all pairwise midpoints between planets."""
    midpoints = {}
    planets = list(planet_longitudes.keys())
    for i, p1 in enumerate(planets):
        for p2 in planets[i+1:]:
            long1 = planet_longitudes[p1]
            long2 = planet_longitudes[p2]
            # Shorter arc midpoint
            diff = (long2 - long1) % 360
            if diff > 180:
                mid = (long1 + (diff - 360) / 2) % 360
            else:
                mid = (long1 + diff / 2) % 360
            midpoints[f"{p1}/{p2}"] = mid
    return midpoints
```
- Store in `static["computed"]["midpoints"]`
- These are hidden sensitive points — similar to Sahams but from Western tradition
- When a transit planet hits a midpoint, the two natal planets' combined theme activates

**After 3B: Run test, verify EXIT:0, update memory. Then continue immediately to 3C.**

---

## PHASE 3C: Prashna (Horary) Module
**Read:** `new3/` file about Prashna/horary astrology
**Where to add:** Create new file `vedic_engine/prashna/prashna.py`

### 3C.1: Prashna Chart Casting
```python
def cast_prashna_chart(question_datetime, question_location_lat, question_location_lon):
    """Cast a chart for the exact moment a question is asked.
    Uses the same SWE computation as natal charts."""
    # Reuse existing chart computation with question_datetime as birth_datetime
    prashna_chart = compute_chart(question_datetime, question_location_lat, question_location_lon)
    return prashna_chart
```
- This reuses the existing natal chart computation engine — same SWE calls, same house computation
- The Prashna chart IS a regular chart, just cast for the question moment instead of birth

### 3C.2: Prashna Timing Modality Matrix
```python
PRASHNA_TIMING = {
    # (sign_modality, house_type) → time unit
    ("cardinal", "angular"): "days",
    ("cardinal", "succedent"): "weeks",
    ("cardinal", "cadent"): "months",
    ("mutable", "angular"): "weeks",
    ("mutable", "succedent"): "months",
    ("mutable", "cadent"): "months",
    ("fixed", "angular"): "months",
    ("fixed", "succedent"): "years",
    ("fixed", "cadent"): "years",
}

def estimate_prashna_timing(significator_sign_modality, significator_house_type):
    """Estimate how long until the queried event manifests."""
    return PRASHNA_TIMING.get((significator_sign_modality, significator_house_type), "months")
```

### 3C.3: Prashna YES/NO Decision Tree
```python
def evaluate_prashna_question(prashna_chart, question_house):
    """Core Prashna evaluation: will the queried event happen?
    question_house = which house governs the question topic
    (7th for marriage, 10th for career, 2nd for money, etc.)"""
    
    house_lord = get_house_lord(prashna_chart, question_house)
    lagna_lord = get_house_lord(prashna_chart, 1)
    moon = prashna_chart["planets"]["MOON"]
    
    result = {
        "question_house": question_house,
        "house_lord": house_lord,
        "signals_yes": [],
        "signals_no": [],
    }
    
    # Signal 1: House lord placement
    lord_house = get_planet_house(prashna_chart, house_lord)
    if lord_house in [1, 4, 5, 7, 9, 10, 11]:
        result["signals_yes"].append("house_lord_well_placed")
    elif lord_house in [6, 8, 12]:
        result["signals_no"].append("house_lord_in_dusthana")
    
    # Signal 2: Moon's condition
    moon_house = get_planet_house(prashna_chart, "MOON")
    if moon_house in [1, 4, 7, 10]:  # Moon in kendra
        result["signals_yes"].append("moon_in_kendra")
    
    # Signal 3: Lagna lord and house lord relationship
    if has_sambandha(lagna_lord, house_lord, prashna_chart):
        result["signals_yes"].append("lagna_lord_connected_to_house_lord")
    
    # Signal 4: Benefics in question house
    benefics_in_house = count_benefics_in_house(prashna_chart, question_house)
    if benefics_in_house > 0:
        result["signals_yes"].append("benefics_in_question_house")
    
    # Signal 5: Malefics in question house
    malefics_in_house = count_malefics_in_house(prashna_chart, question_house)
    if malefics_in_house > 0:
        result["signals_no"].append("malefics_in_question_house")
    
    # Verdict
    yes_count = len(result["signals_yes"])
    no_count = len(result["signals_no"])
    result["verdict"] = "YES" if yes_count > no_count else "NO" if no_count > yes_count else "UNCERTAIN"
    result["confidence"] = abs(yes_count - no_count) / max(yes_count + no_count, 1)
    
    return result
```

### 3C.4: Lost Object Direction
```python
ELEMENT_DIRECTION = {
    "fire": "East",    # Aries, Leo, Sagittarius
    "earth": "South",  # Taurus, Virgo, Capricorn
    "air": "West",     # Gemini, Libra, Aquarius
    "water": "North",  # Cancer, Scorpio, Pisces
}

def find_lost_object_direction(prashna_chart):
    """Determine direction of lost object from 2nd lord's sign element."""
    second_lord = get_house_lord(prashna_chart, 2)
    lord_sign = get_planet_sign(prashna_chart, second_lord)
    element = get_sign_element(lord_sign)
    return ELEMENT_DIRECTION.get(element, "Unknown")
```

### 3C.5: Medical Prashna
```python
HOUSE_BODY_PARTS = {
    1: "Head/Brain", 2: "Face/Mouth/Eyes", 3: "Throat/Neck/Shoulders",
    4: "Chest/Heart/Lungs", 5: "Upper Abdomen/Stomach", 6: "Lower Abdomen/Intestines",
    7: "Pelvis/Kidneys", 8: "Reproductive/Excretory", 9: "Hips/Thighs",
    10: "Knees/Joints", 11: "Calves/Ankles", 12: "Feet/Lymphatic"
}

def diagnose_medical_prashna(prashna_chart):
    """Find the most afflicted house = most likely disease location."""
    affliction_scores = {}
    for house in range(1, 13):
        score = count_malefics_in_house(prashna_chart, house)
        # Add weight for malefic aspects on the house
        score += count_malefic_aspects_on_house(prashna_chart, house) * 0.5
        affliction_scores[house] = score
    
    most_afflicted = max(affliction_scores, key=affliction_scores.get)
    return {
        "afflicted_house": most_afflicted,
        "body_region": HOUSE_BODY_PARTS[most_afflicted],
        "severity": affliction_scores[most_afflicted]
    }
```

### 3C.6: Number-Based Prashna (Kalidas Method)
```python
def compute_number_prashna(user_number):
    """Convert a user-provided number (1-108) into a Prashna chart reference.
    Quotient = rising sign, Remainder = Navamsha."""
    if user_number < 1 or user_number > 108:
        return None
    quotient = ((user_number - 1) // 9)  # 0-11 = sign index
    remainder = ((user_number - 1) % 9) + 1  # 1-9 = navamsha
    return {
        "rising_sign": quotient,
        "navamsha": remainder,
        "input_number": user_number
    }
```

### 3C.7: Devaprasna (Institutional/Entity Prashna)
```python
DEVAPRASNA_HOUSES = {
    1: "Institution itself / Overall health",
    2: "Treasury / Financial reserves",
    3: "Communication / PR / Internal messaging",
    4: "Infrastructure / Physical assets",
    5: "Innovation / Future projects / Education",
    6: "Systemic corruption / Internal conflicts / Legal issues",
    7: "Partnerships / Public relations / Competitors",
    8: "Existential threats / Hidden liabilities / Transformation",
    9: "Leadership philosophy / Governance / Ethics",
    10: "Reputation / Public standing / Authority",
    11: "Revenue streams / Allies / Network",
    12: "Hidden enemies / Losses / Dissolution",
}

def evaluate_devaprasna(prashna_chart):
    """Evaluate an institutional Prashna — reinterpret houses for organizations."""
    # Same evaluation as personal Prashna but with institutional house meanings
    results = {}
    for house, meaning in DEVAPRASNA_HOUSES.items():
        strength = compute_house_strength(prashna_chart, house)
        results[house] = {
            "meaning": meaning,
            "strength": strength,
            "planets": get_planets_in_house(prashna_chart, house),
            "status": "strong" if strength > 0.6 else "weak" if strength < 0.3 else "moderate"
        }
    return results
```

**After 3C: Run test, verify EXIT:0, update memory. Then continue immediately to 3D.**

---

## PHASE 3D: Mundane Basics
**Read:** `new3/` file about mundane astrology (national charts, eclipses, ingress)
**Where to add:** Create new file `vedic_engine/mundane/mundane.py`

### 3D.1: Ingress Chart Validity Rule
```python
def compute_ingress_validity(ingress_chart_asc_sign_modality):
    """How many ingress charts needed per year based on ASC modality."""
    if ingress_chart_asc_sign_modality == "fixed":
        return {"charts_per_year": 1, "validity": "full_year"}
    elif ingress_chart_asc_sign_modality == "mutable":
        return {"charts_per_year": 2, "validity": "6_months"}
    else:  # cardinal
        return {"charts_per_year": 4, "validity": "3_months"}
```

### 3D.2: Eclipse Duration Effect
```python
def compute_eclipse_effect_duration(eclipse_type, obscuration_hours):
    """Classical rule: Solar eclipse hours = years of effect. Lunar = months."""
    if eclipse_type == "solar":
        return {"effect_years": obscuration_hours, "type": "solar"}
    else:
        return {"effect_months": obscuration_hours, "type": "lunar"}
```

### 3D.3: Jupiter-Saturn Great Conjunction Cycle
```python
def compute_great_conjunction_phase(year):
    """Track the Jupiter-Saturn 20-year cycle and 200-year elemental shift."""
    # Last conjunction: Dec 21, 2020 at 0°29' Aquarius (Air sign)
    # Previous element: Earth (1802-2020)
    # Current element: Air (2020-2219)
    years_since_2020 = year - 2020
    cycle_position = years_since_2020 % 20  # position within 20-year cycle
    
    return {
        "current_element": "air",  # 2020-2219
        "years_into_cycle": cycle_position,
        "next_conjunction_year": 2020 + ((cycle_position // 20) + 1) * 20,
        "cycle_phase": "early" if cycle_position < 7 else "middle" if cycle_position < 14 else "late"
    }
```

### 3D.4: Gann Price-to-Degree Conversion
```python
def gann_price_to_degree(price):
    """Convert a financial price to zodiacal degree (Gann method)."""
    import math
    degree = ((math.sqrt(price) * 180 - 225) / 360 % 1) * 360
    return degree

def gann_degree_to_sign(degree):
    """Convert degree to zodiac sign and position."""
    sign_index = int(degree / 30)
    sign_degree = degree % 30
    return {"sign_index": sign_index, "degree_in_sign": sign_degree}
```

**After 3D: Run test, verify EXIT:0, update memory. Then continue to 3E.**

---

## PHASE 3E: Scientific Correlation Hooks
**Read:** `new3/` file about scientific correlations (lunar, solar, geomagnetic)
**Where to add:** Create new file `vedic_engine/science/correlations.py`

These are HOOKS — we compute the values and store them. They don't affect predictions yet. Future phases will wire them in.

### 3E.1: Lunar Phase Health Modifier
```python
def compute_lunar_phase_health_modifier(moon_sun_elongation, prediction_date):
    """Scientific: sleep disruption and cardiovascular risk increase 3-5 days around full moon.
    Full moon = elongation ~180°. Returns a risk modifier."""
    # Full moon zone: elongation between 165° and 195°
    if 165 <= moon_sun_elongation <= 195:
        days_from_exact_full = abs(180 - moon_sun_elongation) / 12  # rough day estimate
        if days_from_exact_full <= 5:
            return {"modifier": 1.05, "reason": "full_moon_zone", "days_from_full": days_from_exact_full}
    return {"modifier": 1.00, "reason": "normal_lunar_phase"}
```

### 3E.2: Birth Month Baseline Risk
```python
BIRTH_MONTH_RISK = {
    # Based on epidemiological meta-analyses
    1: {"schizophrenia": 1.05, "ms": 0.95},  # January
    2: {"schizophrenia": 1.05, "ms": 0.97},
    3: {"schizophrenia": 1.03, "ms": 1.00},
    4: {"schizophrenia": 1.00, "ms": 1.05},
    5: {"schizophrenia": 0.98, "ms": 1.08},  # May = MS peak
    6: {"schizophrenia": 0.95, "ms": 1.05},
    7: {"schizophrenia": 0.95, "ms": 1.00},
    8: {"schizophrenia": 0.97, "ms": 0.97},
    9: {"schizophrenia": 0.98, "ms": 0.95},
    10: {"schizophrenia": 1.00, "ms": 0.93},
    11: {"schizophrenia": 1.02, "ms": 0.90},
    12: {"schizophrenia": 1.04, "ms": 0.92},
}

def get_birth_month_risk(birth_month):
    """Return epidemiological risk modifiers based on birth month."""
    return BIRTH_MONTH_RISK.get(birth_month, {"schizophrenia": 1.00, "ms": 1.00})
```

### 3E.3: Chronotherapy Hora Validation Hook
```python
def compute_hora_chronotherapy_alignment(birth_hora_lord, current_hora_lord):
    """Hook for future research: does planetary hour at birth/treatment time
    correlate with treatment efficacy?
    Stores the hora lords for later statistical analysis."""
    return {
        "birth_hora_lord": birth_hora_lord,
        "current_hora_lord": current_hora_lord,
        "same_lord": birth_hora_lord == current_hora_lord
    }
```

**After 3E: Run test, verify EXIT:0, update memory.**

---

## PHASE 3F: Wire New Systems Into Prediction Layer

Now wire the Phase 3 core computations into the prediction pipeline. Remember: core functions stay pure. Only the prediction layer reads their outputs.

### 3F.1: Add BCP + Profections + ZR to Multi-Dasha Convergence
In the dasha convergence computation (Phase 2G), add three new signals:

```python
# BCP check: is the BCP-active house a domain-relevant house?
bcp_house = static["computed"].get("bcp_active_house")
if bcp_house and bcp_house in domain_houses:
    systems_checked += 1
    systems_favorable += 1
elif bcp_house:
    systems_checked += 1

# Profection check: is the Time Lord a domain-relevant planet?
profection = static["computed"].get("annual_profection", {})
time_lord = profection.get("time_lord")
if time_lord and time_lord in domain_planets:
    systems_checked += 1
    systems_favorable += 1
elif time_lord:
    systems_checked += 1

# ZR check: is the current ZR period in an angular sign from the lot?
zr = static["computed"].get("zodiacal_releasing_spirit", {})
current_zr = zr.get("current_period", {})
if current_zr:
    zr_sign = current_zr.get("sign")
    lot_sign = zr.get("lot_sign")
    if zr_sign is not None and lot_sign is not None:
        distance = (zr_sign - lot_sign) % 12
        systems_checked += 1
        if distance in [0, 3, 6, 9]:  # angular from lot = peak activity
            systems_favorable += 1
```

This takes the convergence check from ~5 systems to ~8 systems. More voices voting.

### 3F.2: Add Nadi Saturn Activation to Transit Evaluation
In the transit scoring section:

```python
# Check Nadi Saturn activation
nadi_saturn = static["computed"].get("nadi_saturn_activated_planets", [])
for activated_planet in nadi_saturn:
    # Saturn is currently activating this planet's karakatwa
    # If this planet is a domain karaka, boost transit significance
    if activated_planet in domain_karakas:
        transit_modifier += 0.10  # Saturn activation = strong manifestation signal
```

### 3F.3: Add Hellenistic Sect as Functional Classification Modifier
In the functional alignment scoring:

```python
# Sect bonus: if a planet is sect-favored, its benefic effects are stronger
sect_data = static["computed"].get("hellenistic_sect", {})
sect_benefics = sect_data.get("sect_benefics", [])
# For domain-relevant planets that are also sect-favored: small bonus
for planet in domain_relevant_planets:
    if planet in sect_benefics:
        functional_score += 0.05
```

**After 3F: Run test, generate content38, report full before/after comparison across all 4 domains.**

---

## COMPLETION CHECKLIST

After ALL phases, verify these exist:

- [ ] BCP active house computed and stored
- [ ] Nadi Saturn activation checked
- [ ] Patel marriage candidates computed
- [ ] BNN graph built
- [ ] Spouse career sign computed
- [ ] Annual Profections + Time Lord computed
- [ ] Hellenistic Sect computed
- [ ] Zodiacal Releasing from Spirit + Fortune computed
- [ ] Secondary Progressions computed
- [ ] Western midpoints computed
- [ ] Prashna module exists with: chart casting, YES/NO tree, timing, lost object, medical, number-based, devaprasna
- [ ] Mundane basics: ingress validity, eclipse duration, Great Conjunction, Gann conversion
- [ ] Scientific hooks: lunar health, birth month risk, chronotherapy
- [ ] BCP + Profections + ZR wired into convergence
- [ ] Nadi Saturn wired into transit
- [ ] Sect wired into functional scoring
- [ ] Test chart runs EXIT:0
- [ ] All memory files updated
- [ ] CHANGELOG.md updated with all Phase 3 entries