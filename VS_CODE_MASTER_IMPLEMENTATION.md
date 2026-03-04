# MASTER IMPLEMENTATION INSTRUCTION FOR VS CODE OPUS
# Phase 1: Core Completion Sprint
# Date: March 2, 2026

---

## HOW TO USE THIS DOCUMENT

This is your implementation roadmap. Follow it in ORDER (Phase 1A → 1B → 1C → 1D → 1E → 1F).

**Before starting:** 
1. Read `MEMORY_INDEX.md` to understand the system
2. The 6 research files are in a reference folder — read the RELEVANT research file before implementing each phase
3. After EVERY change: update the memory files per RULEBOOK.md

**Architecture rule:** In this phase you are ONLY building core computation functions. Do NOT modify the prediction pipeline, confidence scoring, or Bayesian layer. Just compute values and store them in the chart data dict so they're available for Phase 2.

**Code pattern:** For each new computation, create a function that:
- Takes the relevant inputs (longitudes, house positions, etc.)
- Returns a dict or value
- Gets called from `engine.py:analyze_static()` (or equivalent entry point)
- Stores result in `static["computed"][system_name]`

---

## PHASE 1A: Verify & Complete Shadbala
**Research file:** File 1 (Shadbala and Bhavabala)
**Priority:** CRITICAL — everything downstream depends on accurate Shadbala

### Task 1A.1: Audit existing Shadbala computation
Read the current Shadbala code. Compare each sub-component against File 1 formulas. Create a checklist:

| Sub-component | Formula from File 1 | Current code matches? | Fix needed? |
|---------------|---------------------|----------------------|-------------|
| Uchcha Bala | (Long - Debil_Long) / 3 using shortest arc | ? | ? |
| Saptavargaja Bala | Sum of dignity values across 7 vargas | ? | ? |
| Ojayugmarasyamsa Bala | +15 if parity matches in D1, +15 in D9 | ? | ? |
| Kendradi Bala | 60/30/15 for kendra/panapara/apoklima | ? | ? |
| Drekkana Bala | 15 if gender matches decanate | ? | ? |
| Dig Bala | (Long - Weakest_Point) / 3 | ? | ? |
| Nathonnatha Bala | Nocturnal: (Unnata/15)*60; Diurnal: (Nata/15)*60; Mercury=60 | ? | ? |
| Paksha Bala | Benefics: elongation/3; Malefics: 60-benefic; Moon: doubled | ? | ? |
| Tribhaga Bala | 60 to ruler of 1/3 of day/night; Jupiter always 60 | ? | ? |
| Abda/Masa/Vara/Hora | Matrix lookups from Ahargana | ? | ? |
| Ayana Bala | (23.45 ± Declination) / 46.9 * 60; Sun doubled | ? | ? |
| Yuddha Bala | Mass-transfer differential between victor/loser | ? | ? |
| Cheshta Bala | (True - Mean) / 2; Sun=Ayana, Moon=Paksha | ? | ? |
| Naisargika Bala | Fixed values: Sun=60 down to Saturn=8.57 | ? | ? |
| Drig Bala | 11-step piecewise with Mars/Jup/Sat overrides * 0.25 | ? | ? |

Report the checklist FIRST. Then fix any mismatches.

### Task 1A.2: Verify Shadbala minimum thresholds
Confirm these Rupa thresholds are correctly used:
- Sun: 6.5, Moon: 6.0, Mars: 5.0, Mercury: 7.0, Jupiter: 6.5, Venus: 5.5, Saturn: 5.0

### Task 1A.3: Add/verify Bhavabala
Check if Bhavabala is computed. If not, add:
- Bhavadhipati Bala = Lord's Shadbala contribution to the house
- Bhava Dig Bala = Biological sign taxonomy interpolation  
- Bhava Drishti Bala = Aspects on house cusp
- Store in `static["computed"]["bhavabala"]` as dict keyed by house number

### Task 1A.4: Add Ishta/Kashta verification
Verify Ishta Phala and Kashta Phala formulas match classical definitions. These should already exist — just verify they're correct per File 1.

**After completing 1A:** Update memory files. Report what was correct, what was fixed, what was added.

---

## PHASE 1B: Avasthas + Upagrahas + Special Lagnas + Sahams
**Research file:** File 2 (first half) + File 4 (second half)
**Priority:** HIGH — these are entirely new computation modules

### Task 1B.1: Implement Baladi Avasthas
Create function `compute_baladi_avasthas(planet_longitudes)`:
- Divide each sign into 6° segments (5 segments per 30° sign)
- ODD signs: [Bala, Kumara, Yuva, Vriddha, Mrita] = [0.25, 0.50, 1.00, 0.10, 0.00]
- EVEN signs: REVERSE order [Mrita, Vriddha, Yuva, Kumara, Bala]
- Exceptions from File 2:
  - Sun/Mars peak at Kumara (0.50 max multiplier for them? — verify against File 2)
  - Jupiter/Venus peak at Yuva (1.00)
  - Moon/Saturn peak at Vriddha (0.10 — this seems wrong, verify)
  - Mercury always 1.00
- Return dict: `{planet_name: {"avastha": name, "multiplier": float}}`
- Store in `static["computed"]["baladi_avasthas"]`

### Task 1B.2: Implement Shayanadi Avasthas  
Create function `compute_shayanadi_avasthas(planet_data)`:
- Formula from File 2: `(Planet_Nakshatra * Planet_Constant * Navamsa * Moon_Nakshatra * Ishta_Ghati * Ascendant_Sign) % 12`
- You'll need to define the Planet_Constant values (lookup in File 2 research)
- 12 states: Shayana(sleeping), Upavesha(sitting), Netrapani(eyes open), Prakasha(shining), Gamana(walking), Aagama(arriving), Sabha(in assembly), Agama(approaching), Bhojana(eating), Nrityalipsa(dancing), Kautuka(curious), Nidra(drowsy)
- Sub-state: `((Base^2 + Name_Syllable) % 12 + Planet_Additament) % 3`
- Store in `static["computed"]["shayanadi_avasthas"]`

### Task 1B.3: Implement Deeptadi Avasthas
Create function `compute_deeptadi_avasthas(planet_dignities, combustion_status)`:
- 9 states based on dignity: Deepta(exalted), Swastha(own), Pramudita(friend), Shanta(benefic varga), Dina(neutral), Dukhita(enemy), Vikala(combust), Khala(debilitated), Kopa(planetary war)
- Map each planet to its state and a multiplier
- Store in `static["computed"]["deeptadi_avasthas"]`

### Task 1B.4: Implement Upagrahas
Create function `compute_upagrahas(weekday, sunrise_time, sun_longitude)`:

**Gulika:** Ascendant degree at START of Saturn's 1/8th temporal fraction of day/night
**Mandi:** Ascendant degree at MIDPOINT of Saturn's 1/8th temporal fraction

Saturn's assigned hour varies by weekday. The planetary hour sequence for daytime starts from the weekday ruler:
- Sunday: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn → Saturn = 8th slot (but we use 7 slots for 7 planets, 8th is lordless)
- Actually: divide day into 8 parts. Each part ruled by a planet in weekday order. Saturn's part number depends on the weekday. Compute the start time of Saturn's part → find Ascendant at that moment = Gulika.

**Aprakash Grahas (from File 2):**
- Dhuma = Sun_Long + 133°20'
- Vyatipata = 360° - Dhuma
- Paridhi = Vyatipata + 180°
- Indrachapa = 360° - Paridhi  
- Upaketu = Indrachapa + 16°40'
All results mod 360°.

Store ALL in `static["computed"]["upagrahas"]` as dict with longitudes.

### Task 1B.5: Implement Special Lagnas
Create function `compute_special_lagnas(sun_long, moon_long, asc_long, sunrise_minutes, nakshatra_data)`:

From File 2 formulas:
- **Hora Lagna (HL):** Sun_Long + (Minutes_From_Sunrise * 15° / 60)
- **Ghati Lagna (GL):** Sun_Long + (Minutes_From_Sunrise * 360° / 24)  
  Wait — that's 15°/minute which equals 360°/24hours. Verify: GL should use a different rate. Check File 2 research for exact GL formula.
- **Varnada Lagna (VL):** Shift vector from Asc + HL counts, project forward for odd, backward for even
- **Pranapada:** Sun_Modality_Sign_Base + (Vighatis_from_Sunrise / 15)
- **Indu Lagna:** Count K signs from Moon, where K = (Kala of 9L from Lagna + Kala of 9L from Moon) % 12. Kala values: Sun=30, Moon=16, Mars=6, Mercury=8, Jupiter=10, Venus=12, Saturn=1
- **Sri Lagna (SL):** Asc_Long + (Fractional_Moon_Travel_in_Nakshatra * 360°)
- **Upapada:** Already implemented ✅ — just verify

Store ALL in `static["computed"]["special_lagnas"]` as dict with longitudes.

### Task 1B.6: Implement Sahams
Create function `compute_sahams(asc_long, planet_longs, house_cusps, is_daytime)`:

General formula: Day birth: ASC + Point_A - Point_B. Night birth: ASC + Point_B - Point_A.
If result < 0, add 360°.

Implement at minimum these (from File 2 and general Tajika rules):
```python
SAHAM_FORMULAS = {
    "punya": ("Moon", "Sun"),        # Fortune/Dharma
    "vidya": ("Sun", "Moon"),         # Education (reverse of Punya at night)
    "yasas": ("Jupiter", "Saturn"),   # Fame
    "mitra": ("Jupiter", "Mercury"),  # Friends
    "karma": ("Mars", "Saturn"),      # Career
    "roga": ("Saturn", "Mars"),       # Disease
    "mrityu": ("Moon", "Saturn"),     # Death
    "vivaha": ("Venus", "Saturn"),    # Marriage  
    "putra": ("Jupiter", "Moon"),     # Children
    "pitri": ("Saturn", "Sun"),       # Father
    "matri": ("Moon", "Venus"),       # Mother
    "paradesa": ("9th_cusp", "9th_lord"), # Foreign travel
}
```
Point_A and Point_B are planet longitudes. For house-based Sahams, use cusp longitude.

Store in `static["computed"]["sahams"]` as dict with longitudes.

**After completing 1B:** Update ALL memory files. This is a BIG addition — multiple new modules.

---

## PHASE 1C: Complete Ashtakavarga Reductions + Missing Dashas
**Research file:** File 5
**Priority:** HIGH — Shodhana reductions and missing dashas are major gaps

### Task 1C.1: Implement Trikona Shodhana
Create function `trikona_shodhana(bav_matrix)`:
For each planet's BAV (12 signs), process trine groups (1-5-9, 2-6-10, 3-7-11, 4-8-12):
- If ANY value in the trine == 0: skip this trine
- If all 3 values are EQUAL: set all to 0
- If UNEQUAL: subtract the minimum from all 3
- Return the reduced BAV matrix

### Task 1C.2: Implement Ekadhipatya Shodhana
Create function `ekadhipatya_shodhana(reduced_bav, sign_lords)`:
For each pair of signs owned by the same planet (e.g., Mars owns Aries+Scorpio):
- If either value == 0: skip
- If both signs EMPTY (no planets) AND values equal: both = 0
- If both signs EMPTY AND values unequal: both = min(values)
- If both signs OCCUPIED: skip
- If one OCCUPIED, one EMPTY:
  - If occupied_val >= empty_val: empty = 0
  - If occupied_val < empty_val: empty = empty - occupied

### Task 1C.3: Implement Shodhya Pinda
Create function `compute_shodhya_pinda(reduced_bav, rashi_gunakara, graha_gunakara)`:
- Rashi Pinda = Sum(reduced_sign_value × rashi_gunakara for each sign)
- Graha Pinda = Sum(reduced_value_of_occupied_signs × graha_gunakara)
- Shodhya Pinda = Rashi Pinda + Graha Pinda
- Rashi Gunakara values: Aries=7, Taurus=10, Gemini=8, Cancer=4, Leo=10, Virgo=6, Libra=7, Scorpio=8, Sag=9, Cap=5, Aqua=11, Pisces=12
- Graha Gunakara values: Sun=5, Moon=5, Mars=8, Mercury=5, Jupiter=10, Venus=7, Saturn=5

### Task 1C.4: Implement Prastharashtakavarga (PAV)
Create function `compute_prastharashtakavarga(natal_positions)`:
This is the full 8×12 matrix per planet showing WHICH contributor (Sun/Moon/Mars/Merc/Jup/Ven/Sat/Lagna) gave each bindu in each sign.
- Use the 7 standard BAV contribution tables (these are the classical rules for which positions contribute bindus)
- The research file says "Seven 8-row lookup tables" — implement these lookup tables
- Store as `static["computed"]["prastharashtakavarga"]` — dict keyed by planet, each value is 8×12 matrix

### Task 1C.5: Implement Yogini Dasha
Create function `compute_yogini_dasha(moon_nakshatra, birth_balance)`:
- Sequence start = (Moon_Nakshatra_Index + 3) % 8
- 8 periods: Mangala(1yr), Pingala(2yr), Dhanya(3yr), Bhramari(4yr), Bhadrika(5yr), Ulka(6yr), Siddha(7yr), Sankata(8yr)
- Total cycle = 36 years
- Compute current dasha/antardasha for any date
- Store alongside Vimshottari in `static["computed"]["yogini_dasha"]`

### Task 1C.6: Implement Kalachakra Dasha
Create function `compute_kalachakra_dasha(moon_nakshatra, moon_pada)`:
- Determine Savya (clockwise) vs Apsavya (counter-clockwise) from Nakshatra Pada array
- Sign-based period lengths: Aries=7, Taurus=16, Gemini=21, Cancer=9, Leo=5, Virgo=9, Libra=16, Scorpio=7, Sag=10, Cap=4, Aqua=4, Pisces=10
- Implement Gati (jump) rules:
  - Manduka Gati (Frog): Index ± 2 (skips a sign)
  - Markati Gati (Monkey): Index ± -1 (goes backward)  
  - Simhavalokana (Lion's glance): Index ± 5 or 9 (looks back)
- Total cycle = 144 years
- **NOTE:** This is the most complex dasha. If the research file details aren't sufficient for exact Gati trigger conditions, implement the basic Savya/Apsavya progression first and mark Gatis as TODO.

### Task 1C.7: Implement Narayana Dasha
Create function `compute_narayana_dasha(jaimini_data)`:
- Start sign = whichever has higher Jaimini strength: Lagna or 7th house sign
- Progression by modality: Movable=adjacent, Fixed=6th step, Dual=trinal block
- Duration = distance from sign to its lord - 1 (max 12 years)
- Direction from 9th house parity (odd=forward, even=backward)

### Task 1C.8: Implement Conditional Dasha Eligibility
Create function `check_conditional_dashas(chart_data)`:
Return a dict of which conditional dashas are eligible for this chart:

**Ashtottari (108yr):** Rahu in Kendra/Trikona from Lagna Lord AND ((daytime+Krishna) OR (nighttime+Shukla))
**Dwisaptati Sama (72yr):** Lagna Lord in 7th OR 7th Lord in Lagna
**Shat Trimsa Sama (36yr):** (Daytime + Sun Hora) OR (Nighttime + Moon Hora)

For eligible dashas, compute the full timeline.

**After completing 1C:** Update memory. This is another big batch.

---

## PHASE 1D: Complete Yoga Detection
**Research file:** File 6
**Priority:** HIGH — currently at ~40% yoga coverage

### Task 1D.1: Implement Sambandha evaluator
Create utility function `has_sambandha(planet_a, planet_b, chart_data)`:
Returns True if conjunction (within orb) OR mutual aspect OR parivartana (sign exchange).
This is used by ALL yoga detectors below.

### Task 1D.2: Implement Yoga Universal Grading
Create function `grade_yoga(yoga_planets, chart_data)`:
- S-Tier: Exact conjunction/aspect, in Kendra/Trikona, exalted/moolatrikona, no malefic influence
- A-Tier: Strong Shadbala, friendly sign, minimal malefic
- B-Tier: Moderate strength, minor malefic influence
- C-Tier: Upachaya placement, weak, afflicted
- Return grade as string + numeric score (S=1.0, A=0.75, B=0.5, C=0.25)

### Task 1D.3: Implement Dharma-Karma Adhipati Yoga
- Detect: Sambandha between 9th lord and 10th lord
- Boost: if in houses 1, 2, 7, 9, 10
- Dampen: if lords also rule 3, 6, 8, 11
- Nullify: if in 6, 8, 12 or heavily combust
- For each lagna, identify which specific planet pair forms this

### Task 1D.4: Implement Dhana + Daridra Yogas
**Dhana:** Sambandha between L2, L5, L9, L11 (various combinations)
- Lakshmi Yoga: L9 strong in Kendra/Trikona AND Venus in Kendra/Trikona in own/exalted sign
**Daridra:** L11 in dusthana OR L2 in dusthana OR Kemadruma (no planets 2/12 from Moon)
- Viparita override: if afflicted lord also rules a dusthana → cancels Daridra

### Task 1D.5: Implement Aristha Yogas (Health)
**Balarishta:** Moon in dusthana heavily afflicted OR Mars in 1/8 conjunct Sun/Saturn OR Luminaries conjunct nodes in own signs
**Bhanga (cancellation):** Jupiter in Lagna OR Lagna lord strong in Kendra

### Task 1D.6: Implement all 32 Nabhasa Yogas
Three groups:
**Akriti (20 shape patterns):** Implement as geometric checks on planet distribution across houses. Key ones:
- Gada: planets in 2 adjacent kendras
- Shakata: planets confined to 1 and 7
- Yupa: planets in continuous houses 1-4
- (implement all 20 from File 6)

**Sankhya (7 count patterns):** Count unique signs holding planets:
7 signs=Vallaki, 6=Dama, 5=Pasha, 4=Kedara, 3=Shoola, 2=Yuga, 1=Gola

**Ashraya/Dala (5 modality patterns):**
- Rajju: all in movable signs
- Musala: all in fixed signs
- Nala: all in dual signs
- Mala: only benefics in 3 kendras
- Sarpa: only malefics in 3 kendras

### Task 1D.7: Implement Raja Yogas
- Base: Sambandha between ANY kendra lord + ANY trikona lord
- Akhanda Samrajya: Fixed lagna + Jupiter rules 5/11 + Lords 2,9,11 in kendras from Moon
- Adhi Yoga: Benefics exclusively in 6,7,8 from Moon/Ascendant
- For each lagna, enumerate which planet combinations form Raja Yoga

### Task 1D.8: Implement Pravrajya Yogas
- 4+ planets in 1 sign
- Flavor from highest Shadbala planet (Sun=Tapasvi, Moon=Kapali, etc.)
- Ketu trigger: only if in 12th AND aspected by L5/L9/Jupiter
- Cancelled if strongest planet is combust

### Task 1D.9: Store all yogas in unified format
All detected yogas stored in `static["computed"]["yogas"]` as list of dicts:
```python
{
    "name": "Dharma-Karma Adhipati",
    "type": "raja",  # raja/dhana/daridra/aristha/nabhasa/pravrajya
    "planets": ["Jupiter", "Saturn"],
    "grade": "A",
    "score": 0.75,
    "domain": "career",  # career/finance/health/marriage/spiritual
    "active": True,
    "cancellation": None  # or reason string
}
```

**After completing 1D:** Update memory.

---

## PHASE 1E: Transit Systems
**Research file:** File 3
**Priority:** MEDIUM-HIGH — improves timing accuracy

### Task 1E.1: Implement Vedha pairs
Create function `check_vedha(transiting_planet, transit_house, other_planet_houses)`:
- Implement the complete Vedha pair matrix from File 3
- Exception: Sun/Saturn pair and Moon/Mercury pair are immune to mutual Vedha
- Return True if transit is obstructed (Vedha active)
- Add Vedha check to existing transit evaluation

### Task 1E.2: Implement Sudarshana Chakra evaluation  
Create function `evaluate_sudarshana(transit_data, lagna_sign, moon_sign, sun_sign)`:
- Compute transit house from Lagna reference frame
- Compute transit house from Moon reference frame
- Compute transit house from Sun reference frame
- Score each: +1/+3 for favorable, -1/-3 for malefic
- Weighted sum: Weight_L * Score_Lagna + Weight_M * Score_Moon + Weight_S * Score_Sun
- Suggested weights: Lagna=0.40, Moon=0.35, Sun=0.25

### Task 1E.3: Implement Sudarshana Dasha progression
Create function `compute_sudarshana_dasha(natal_lagna, age)`:
- Yearly: (Natal_Lagna_Sign + Age) % 12
- Monthly: (Annual_Lagna + Month) % 12
- Daily: (Monthly_Lagna + Block) % 12
- Store current Sudarshana Dasha sign for the prediction date

### Task 1E.4: Implement SBC grid construction
Create function `construct_sbc_grid(natal_data)`:
- Build the 9×9 (81-cell) matrix
- Map 28 Nakshatras on outer ring
- Map 12 Rasis, 30 Tithis centrally
- Map 7 weekdays
- Map consonants/vowels
- Store as `static["computed"]["sbc_grid"]`

### Task 1E.5: Implement SBC Vedha detection
Create function `check_sbc_vedha(transit_planet, transit_nakshatra, sbc_grid)`:
- Direct motion → cross-grid ray
- Fast motion → left diagonal ray
- Retrograde → right diagonal ray
- Sun/Nodes → 3-way ray
- Return list of nakshatras/signs/tithis that are "pierced"

### Task 1E.6: Implement Kota Chakra
Create function `compute_kota_chakra(moon_nakshatra)`:
- Build 4 concentric zones: Stambha (inner pillar), Durgantara (inner fort), Prakaara (wall), Bahya (outer)
- Distribute 28 nakshatras outward from Moon's natal nakshatra

Create function `evaluate_kota_transit(transit_planet, transit_nakshatra, kota_chakra)`:
- Direct on diagonals → INWARD movement
- Direct on cardinals → OUTWARD movement
- Retrograde → reverse direction
- Return {"zone": str, "direction": "inward"/"outward", "severity": float}

**After completing 1E:** Update memory.

---

## PHASE 1F: Functional Classification + KP + Longevity + Tajika
**Research file:** File 4 + File 3 (Tajika section)
**Priority:** MEDIUM — completes remaining gaps

### Task 1F.1: Verify/complete functional benefic-malefic tables
Create or verify `FUNCTIONAL_CLASSIFICATION` dict for ALL 12 lagnas from File 4.
Each lagna entry should have:
```python
{
    "yoga_karaka": [...],
    "functional_benefic": [...],
    "functional_malefic": [...],
    "neutral": [...],
    "maraka": [...],  # lords of 2nd and 7th
    "badhaka": ...,   # Cardinal=11th lord, Fixed=9th lord, Mutable=7th lord
}
```
Verify against what already exists. Fix any discrepancies.

### Task 1F.2: Verify/complete KP significator computation
- Verify sub-lord arc: `Arc = (Dasha_Years / 120) * 800 arc minutes`
- Verify 4-level hierarchy: Star of Occupants → Occupants → Star of Lord → Lord
- Verify house groupings match File 4:
  - Career: 10 primary + 2,6,11 favorable + 5,8,12 denial
  - Marriage: 7 primary + 2,11 favorable + 1,6,10,12 denial
  - Finance: 2 primary + 6,10,11 favorable + 5,8,12 denial
  - Health: 1 primary + 5,11 favorable + 6,8,12 denial
- Verify Ruling Planets: [Asc Star Lord, Asc Sign Lord, Moon Star Lord, Moon Sign Lord, Day Lord] minus retrogrades

### Task 1F.3: Implement Longevity methods (verify/expand existing)
We already have longevity guardrails. Verify the three methods:

**Pindayu:** Base = (Max_Years × Arc_from_Exaltation) / 180°. Apply reductions: Chakrapata, Astangata, Shatrukshetra, Krurodaya.
Planet max years: Sun=19, Moon=25, Mars=15, Mercury=12, Jupiter=15, Venus=21, Saturn=20

**Amsayu:** Base = (Planet_Minutes / 200) % 12. Multipliers: ×3 for retro/exalted/own; ×2 for own navamsha/drekkana/vargottama.

**Nisargayu:** Fixed constants: Saturn=50, Venus=20, Sun=20, Jupiter=18, Mercury=9, Mars=2, Moon=1. Apply Pindayu reductions.

**Three Pairs Band:** Evaluate [Lagna Lord/8th Lord], [Lagna/Hora Lagna], [Moon/Saturn] → modality of each pair → majority = band (Alpa/Madhya/Purna).

### Task 1F.4: Implement Tajika Varshaphala basics
Create function `compute_varshaphala(birth_data, year)`:
- Cast solar return chart (Sun returns to exact natal longitude)
- Compute Muntha: (Natal_Lagna_Sign + completed_years) % 12
- Compute Year Lord: max Panchavargiya Bala among candidates that aspect Varsha Lagna
- Compute Tajika aspects: Ithasala (applying), Ishrafa (separating) using speed+orb logic
- Store in `static["computed"]["varshaphala"]`

### Task 1F.5: Implement Nadi Amsha (basic)
Create function `compute_nadi_amsha(planet_longitudes)`:
- 1 Amsha = 0.2° (12 arc minutes)
- 150 Amshas per sign
- Cardinal signs: linear 1-150
- Fixed signs: reverse 150-1
- Dual signs: split 76-150 then 1-75
- Store the Nadi Amsha number for each planet
- This is primarily for birth time rectification (Phase 2 feature) but compute it now

**After completing 1F:** Update ALL memory files. Run test chart. Report full output.

---

## PHASE 1 COMPLETE CHECKLIST

When ALL phases are done, verify these exist in the chart data:

- [ ] Shadbala — all sub-components verified against classical formulas
- [ ] Bhavabala — computed for all 12 houses
- [ ] Baladi Avasthas — computed for all planets
- [ ] Shayanadi Avasthas — computed for all planets
- [ ] Deeptadi Avasthas — computed for all planets
- [ ] Upagrahas — Gulika, Mandi, Dhuma, Vyatipata, Paridhi, Indrachapa, Upaketu
- [ ] Special Lagnas — Hora, Ghati, Varnada, Pranapada, Indu, Sri (+ existing Upapada)
- [ ] Sahams — at least 12 major lots computed
- [ ] Trikona Shodhana — applied to all BAV
- [ ] Ekadhipatya Shodhana — applied to reduced BAV
- [ ] Shodhya Pinda — computed for all planets
- [ ] Prastharashtakavarga — 8×12 matrix for each planet
- [ ] Yogini Dasha — full timeline computed
- [ ] Kalachakra Dasha — basic timeline (Gatis may be TODO)
- [ ] Narayana Dasha — full timeline computed
- [ ] Conditional dasha eligibility — checked and eligible ones computed
- [ ] All Dharma-Karma Yogas detected
- [ ] All Dhana/Daridra Yogas detected
- [ ] All Aristha Yogas detected  
- [ ] All 32 Nabhasa Yogas detected
- [ ] All Raja Yogas detected
- [ ] Pravrajya Yogas detected
- [ ] Vedha pairs checked in transits
- [ ] Sudarshana Chakra evaluation
- [ ] Sudarshana Dasha progression
- [ ] SBC grid constructed
- [ ] SBC Vedha detection
- [ ] Kota Chakra constructed + transit direction
- [ ] Functional classification verified for all 12 lagnas
- [ ] KP significators verified
- [ ] Longevity methods verified/complete
- [ ] Tajika Varshaphala basics computed
- [ ] Nadi Amsha computed

This completes Phase 1. Phase 2 (wiring into prediction pipeline) comes next.