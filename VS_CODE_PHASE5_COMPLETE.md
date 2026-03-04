# PHASE 5: Final Completion — The Last 5-10%
# MASTER INSTRUCTION FOR VS CODE OPUS
# Research files are in new5/ folder (6 files)
# Execute ALL phases continuously — do NOT stop between files

---

## CONTEXT

You are completing the final 5-10% of a Vedic astrology prediction engine. Read MEMORY_INDEX.md and RULEBOOK.md first.

**Architecture rule (CRITICAL):** ALL new computations go into CORE as pure functions. NO weights, NO blending, NO prediction logic inside core. Store results in `static["computed"]`. Prediction wiring is separate.

**These files contain DENSE tabular data.** Your job is to READ each file thoroughly, find every table/formula/rule, and implement it. The gist below tells you WHAT to look for. The actual data is IN the files.

---

## FILE 1 (new5/ — Alternative & Annual Timing Systems)

**Read the ENTIRE file. Look for and implement:**

### Tithi Pravesh (Luni-Solar Annual Return) [NEW]
Create `vedic_engine/timing/tithi_pravesh.py`

The file contains the algorithm to find the exact moment when `(Transit_Moon - Transit_Sun)` equals `(Natal_Moon - Natal_Sun)` while Sun is in the natal sign. This is a different annual chart from Varshaphala.

Look for:
- The iterative time-solver algorithm (step-by-step)
- Year Lord rule: "IF Tithi Pravesh occurs on Weekday X, X is Year Lord"
- Interpretation rules for the Tithi Pravesh chart
- Any special yogas unique to Tithi Pravesh

Implement:
```python
def compute_tithi_pravesh(natal_sun_long, natal_moon_long, natal_tithi, year, ephemeris):
    """Find exact moment of tithi return for the given year"""
    # tithi = floor((moon_long - sun_long) / 12) + 1
    # search near solar return date for when transiting tithi == natal tithi
    ...
    return {"datetime": ..., "chart": ..., "year_lord": ..., "muntha_house": ...}
```

### Pancha Pakshi Shastra (Five Birds Biorhythm) [NEW]
Create `vedic_engine/timing/pancha_pakshi.py`

The file contains:
- **Bird Assignment Array**: based on lunar phase (Shukla/Krishna) × Nakshatra groupings → which of 5 birds (Vulture/Owl/Crow/Cock/Peacock)
- **Daily Activity Cycle**: each bird cycles through 5 activities (Rule/Eat/Walk/Sleep/Die)
- **Activity Index formula**: `activity = (minutes_since_sunrise_or_sunset) / 144` → maps to 0-4 index into activity array
- **Day and Night have DIFFERENT sequences** for Shukla vs Krishna paksha

EXTRACT the complete bird assignment table and activity sequence tables from the file.

Implement:
```python
def get_birth_bird(nakshatra_index, paksha):
    """Determine birth bird from nakshatra and lunar phase"""
    ...
    return {"bird": "Peacock", "bird_index": 4}

def get_current_activity(birth_bird, datetime, sunrise, sunset, paksha):
    """What activity is the birth bird performing right now?"""
    # minutes = (now - sunrise).minutes if daytime, (now - sunset).minutes if night
    # segment = minutes // 144  (gives 0-4)
    # lookup activity from sequence table for this bird + paksha + day/night
    ...
    return {"activity": "Rule", "is_favorable": True, "segment": 2}

def get_pakshi_compatibility(bird_a, activity_a, bird_b, activity_b):
    """Compare two people's bird activities for competition/compatibility"""
    ...
```

### Lal Kitab Rules [NEW]
Create `vedic_engine/analysis/lal_kitab.py`

The file contains:
- **Sleeping Planet rule**: "IF 7th house from a planet is EMPTY, planet = Dormant"
- **Karmic Debt (Rin) triggers**: 4 specific conditions (e.g., "Ketu in 4th = Matru Rin")
- **Progressive Varshphal**: "shift ALL planets exactly 1 house forward per year of age" — completely different from Tajika
- Possibly: planet-in-house predictions that differ from BPHS

EXTRACT all rules from the file. Implement:
```python
def detect_sleeping_planets(planet_houses):
    """A planet is sleeping if 7th house from it is empty"""
    ...
    return {"sleeping": ["VENUS", "JUPITER"], "awake": [...]}

def detect_karmic_debts(planet_houses, aspects):
    """Detect Lal Kitab Rin (karmic debts)"""
    # Look for: Ketu in 4th = Matru Rin, etc.
    ...
    return [{"type": "Matru_Rin", "trigger": "Ketu in H4", "domain": "mother"}]

def compute_lalkitab_varshphal(natal_planet_houses, age):
    """Shift all planets forward by age houses"""
    ...
    return {"planet_houses_progressed": {...}, "age": age}
```

---

## FILE 2 (new5/ — Advanced Prashna Framework)

**Read the ENTIRE file. Look for and implement:**

### Ashtamangala Prashna [NEW]
Create `vedic_engine/prashna/ashtamangala.py`

The file contains:
- **108-cell board mapping** (3 domains: Past/Present/Future)
- **Modulo-8 algorithm**: `pile_count % 8` executed 3 times for 3 piles
- **Remainder-to-planet table**: 8 rows linking remainders to planets/qualities
- **Ascending/Descending sequence evaluation** rules

Implement:
```python
def compute_ashtamangala(pile_left, pile_center, pile_right):
    """3-pile shell counting → Past/Present/Future vectors"""
    past = pile_left % 8 or 8
    present = pile_center % 8 or 8
    future = pile_right % 8 or 8
    # map each to planet/quality from the remainder table
    ...
    return {"past": ..., "present": ..., "future": ..., "overall": ...}
```

### Aksharachakra (Phonetic-to-Sign) [NEW]
The file contains a phoneme-to-sign mapping table (8 phonetic categories → zodiac signs).

Implement:
```python
AKSHARACHAKRA = {
    # Extract the COMPLETE mapping from the file
    # e.g., "ka": "Aries", "kha": "Aries", etc.
}

def get_prashna_sign_from_phoneme(first_syllable):
    """Map first syllable of question to zodiac sign"""
    ...
    return {"sign": "Aries", "sign_index": 0}
```

### Nimitta / Shakuna (Omen Decision Tree) [NEW]
The file contains:
- **Directional house activation**: 8 directions → zodiac houses
- **Shakuna (creature/event) significations**: 6+ omen types
- **Omen boolean overrides**: Sharirika/Drishya/Shakuna categories

Implement:
```python
def evaluate_nimitta(direction_faced, omens_observed):
    """Omen-based Prashna modifier"""
    ...
    return {"house_activated": 10, "omen_quality": "positive", "overrides": [...]}
```

### Prashna Timing Enhancement [NEW]
The file contains:
- **Fructification Timing**: `Planetary_Unit × Navamsas_traversed_by_Lagna_Lord`
- **Mute vs Speaking signs timing logic**
- **Trisphutam zone logic**: Srishti/Sthiti/Samhara sign blocks

Implement:
```python
def compute_prashna_fructification(lagna_lord, planet_timing_units, navamsas_traversed):
    """When will the queried event happen?"""
    ...
    return {"days": ..., "weeks": ..., "months": ..., "certainty": ...}
```

---

## FILE 3 (new5/ — Validation Data)

**Read the ENTIRE file. Look for and implement:**

### Benchmark Test Charts [NEW]
Create `vedic_engine/data/test_charts.py`

The file contains ~10 historical charts with exact birth data and known life events.

Extract ALL charts into a constant:
```python
BENCHMARK_CHARTS = [
    {
        "name": "...",
        "birth_date": "YYYY-MM-DD",
        "birth_time": "HH:MM:SS",
        "birth_place": "City, Country",
        "latitude": ..., "longitude": ...,
        "known_events": [
            {"event": "Marriage", "date": "YYYY-MM-DD", "dasha": "...", "transit": "..."},
            ...
        ]
    },
    ...
]
```

### BVB Marriage Parameters [NEW]
The file contains 5 verified marriage charts with the 8 BVB parameters (P1-P8).
Extract and store as test data.

### Validation Utilities [NEW]
Create `vedic_engine/data/validation.py`

Implement:
```python
def validate_engine_against_benchmarks(engine, charts=BENCHMARK_CHARTS):
    """Run engine on each benchmark chart, compare known events with predictions"""
    ...
    return {"charts_tested": N, "events_matched": M, "accuracy": M/total}
```

### Edge Case Handlers [VERIFY/NEW]
The file mentions:
- **Placidus high-latitude failsafe**: when `tan(lat) × tan(declination) > 1`, Placidus breaks
- **Eclipse/Syzygy detection**: `|Sun - Moon| ≈ 0° AND |Sun - Node| < 18°`
- **Ayanamsha boundary warning**: planet at 29°59'

Check if we have these. If not, add them to the appropriate existing modules.

---

## FILE 4 (new5/ — Lookup Tables)

**This is the MOST IMPORTANT file. It contains the raw data arrays we need.**

### Yoni Koota [NEW data]
The file contains:
- 27-row Nakshatra → Animal + Gender mapping
- 14×14 animal compatibility matrix (scores 0-4)

Create or update `vedic_engine/data/compatibility_tables.py`:
```python
NAKSHATRA_YONI = {
    "Ashwini": {"animal": "Horse", "gender": "Male"},
    # ... all 27
}

YONI_MATRIX = {
    # 14×14 grid — extract EVERY cell from the file
    ("Horse", "Horse"): 4,
    ("Horse", "Elephant"): 2,
    # ... all 196 combinations
}
```

### Vashya Koota [NEW data]
- 12 signs → 5 category mapping
- 5×5 compatibility matrix

```python
SIGN_VASHYA = {"Aries": "Chatushpad", "Taurus": "Chatushpad", ...}
VASHYA_MATRIX = {("Chatushpad", "Chatushpad"): 2, ...}  # 5×5
```

### Bhakoot Koota [NEW data]
- 12×12 Moon sign compatibility (0 or 7 points)
- ALL exception rules where normally bad distances become OK

```python
BHAKOOT_SCORES = {}  # 12×12 dict
BHAKOOT_EXCEPTIONS = [...]  # list of exception conditions
```

### Shashtiamsha D60 [NEW data — complete table]
The file contains TWO tables: one for odd signs, one for even signs. Each has 60 rows.
For even signs: reverse index (60→1) and invert benefic/malefic nature.

```python
D60_ODD = [
    {"index": 1, "name": "Ghora", "nature": "Malefic", "deity": "...", "effect": "..."},
    # ... all 60
]
D60_EVEN = [...]  # reversed and inverted from odd
```

### Bhrigu Sutras 108 [NEW data — complete]
9 planets × 12 houses = 108 predictions.
EXTRACT EVERY ROW from the file.

```python
BHRIGU_SUTRAS = {
    ("SUN", 1): "Leadership, government favor, strong constitution...",
    ("SUN", 2): "Wealth through authority, harsh speech...",
    # ... all 108
}
```

### 16 Tajika Yogas [NEW]
The file lists all 16 relational yogas used in Varshaphala.
We have Ithasala and Ishrafa. Extract the other 14.

```python
TAJIKA_YOGAS = [
    {"name": "Ithasala", "rule": "faster planet applying to slower within orb", "nature": "positive"},
    {"name": "Ishrafa", "rule": "faster planet separating from slower", "nature": "negative"},
    # ... all 16
]
```

### 50+ Tajika Sahams [NEW]
We have 19 natal Sahams. The file has 50+.
Formula: `Point_A + Point_B - Ascendant` (with day/night reversal and +30° correction).

```python
TAJIKA_SAHAMS = [
    {"name": "Saham of Fortune", "day": "ASC + Moon - Sun", "night": "ASC + Sun - Moon", "domain": "wealth"},
    # ... all 50+
]
```

### Nara Chakra (Nakshatra-Surgery) [NEW]
27 Nakshatras → forbidden surgery body zones.

```python
NAKSHATRA_SURGERY_MAP = {
    "Ashwini": "Head/Brain",
    "Bharani": "Head/Forehead",
    # ... all 27
}
```

Also look for:
- **Bhakoot Dosha exception handlers**: 6 cancellation conditions
- **Tajika aspect orbs (Deeptamshas)** and velocity hierarchy
- **Saham +30° correction rule**

---

## FILE 5 (new5/ — Rare Dasha Systems)

**Read the ENTIRE file. Look for and implement:**

Create `vedic_engine/timing/rare_dashas.py`

### The file contains computation for these dasha systems:

**1. Dwadashottari (112 years) [NEW]**
- Eligibility: extract from file
- 8 planets with year allocations (should total 112)
- Extract sequence and years

**2. Panchottari (105 years) [NEW]**
- 7 planets, total 105 years
- Extract eligibility + sequence + years

**3. Shatabdika (100 years) [NEW]**
- 7 planets, total 100 years
- Extract eligibility + sequence + years

**4. Chaturashiti Sama (84 years) [NEW]**
- 7 planets × 12 years each = 84
- Eligibility: "10th lord in 10th house" (verify from file)

**5. Mandooka Dasha (Frog Dasha) [NEW]**
- Non-sequential sign jumps — the "frog leap" pattern
- The file has **12 specific jumping arrays** based on Lagna sign
- This is the most complex one — extract ALL 12 arrays

**6. Shoola Dasha [VERIFY]**
- We may have basic version in jaimini_dashas.py
- File has: starts from evaluating Lagna vs 7th strength (Self), 3rd vs 9th (Father), 4th vs 10th (Mother)
- Verify we have this logic, add if missing

**7. Sudasa [VERIFY]**
- Forward/Reverse determined by Sree Lagna Odd/Even
- Saturn/Ketu override rules
- Verify completeness

**8. Drig Dasha [VERIFY]**
- Sequences based on Jaimini aspectual sightlines
- Verify completeness

For EACH new dasha, implement:
```python
def is_DASHA_eligible(chart):
    """Check if this conditional dasha applies"""
    ...

def compute_DASHA(moon_nakshatra, moon_longitude, birth_date):
    """Compute full dasha sequence"""
    ...
    return {"periods": [...], "total_years": N}
```

Also extract:
- **Sree Lagna derivation formula** (if we don't have it)
- **Dasha balance formula**: `(remaining_arc / 800) × planet_years`
- **Starting node**: `(distance from anchor nakshatra to natal moon) % N`

---

## FILE 6 (new5/ — Advanced Yogas)

**Read the ENTIRE file. Look for and implement:**

Update `vedic_engine/analysis/yogas.py` (or create `vedic_engine/analysis/yogas_extended.py`)

### The file contains ~25 NEW yogas with strict boolean logic:

**Solar Yogas:**
- Veshi: planet (not Moon/Rahu/Ketu) in 2nd from Sun
- Voshi: planet (not Moon/Rahu/Ketu) in 12th from Sun
- Ubhayachari: planets in both 2nd AND 12th from Sun

**Lunar Yogas:**
- Sunapha: planet (not Sun/Rahu/Ketu) in 2nd from Moon
- Anapha: planet (not Sun/Rahu/Ketu) in 12th from Moon
- Durudhara: planets in both 2nd AND 12th from Moon
- Kemadruma: NO planet in 2nd or 12th from Moon (AND no planet in Kendra from Lagna)
- Kemadruma Bhanga: cancellation conditions
- Chandra-Mangala: Moon conjunct Mars

**Wealth Yogas:**
- Parivartana types: Maha (1/2/4/5/7/9/10/11 lords exchange), Khala, Dainya (6/8/12 lords exchange)
- Amala: benefic in 10th from Moon or Lagna

**Special Yogas:**
- Budhaditya: Sun + Mercury conjunction — with EXACT orb filter from file: `6° ≤ |Sun - Mercury| ≤ 14°` (too close = combust, doesn't work)
- Bandhan: `count(planets in H_A) == count(planets in H_B)` on specific symmetric axes
- Parivrajya/ascetic variants with stellium rules
- Kakshya Vridhi/Hrasa (longevity bracket modifiers)

**Extract ALL yoga definitions as boolean functions.** The file describes them as "logic gates" — implement exactly as described.

For each:
```python
def detect_YOGA_NAME(planet_houses, planet_signs, aspects, ...):
    """[Description from file]"""
    # Extract exact boolean condition from file
    ...
    return {"present": True/False, "grade": "Major/Minor", "planets": [...], "prediction": "..."}
```

---

## AFTER ALL 6 FILES

1. Run complete test, verify EXIT:0
2. Generate content40 output file
3. Update MEMORY_INDEX.md with ALL new modules
4. Update CHANGELOG.md with Phase 5 entries
5. Wire new computed values into `static["computed"]` in engine.py

## PHASE 5 COMPLETION CHECKLIST

After ALL files, verify:
- [ ] Tithi Pravesh computation
- [ ] Pancha Pakshi (birth bird + activity cycle)
- [ ] Lal Kitab (sleeping planets + Rin + progressive varshphal)
- [ ] Ashtamangala Prashna (108-cell board + modulo-8)
- [ ] Aksharachakra phoneme-to-sign table
- [ ] Nimitta/Shakuna omen system
- [ ] Prashna fructification timing
- [ ] Benchmark test charts data
- [ ] BVB marriage validation data
- [ ] Yoni 14×14 matrix (COMPLETE)
- [ ] Vashya 5×5 matrix (COMPLETE)
- [ ] Bhakoot 12×12 with exceptions (COMPLETE)
- [ ] D60 Shashtiamsha full 60-row table (odd + even)
- [ ] Bhrigu Sutras all 108 entries
- [ ] All 16 Tajika Yogas
- [ ] 50+ Tajika Sahams
- [ ] Nara Chakra surgery mapping (27 rows)
- [ ] Dwadashottari Dasha
- [ ] Panchottari Dasha
- [ ] Shatabdika Dasha
- [ ] Chaturashiti Sama Dasha
- [ ] Mandooka Dasha (with 12 jumping arrays)
- [ ] ~25 new yogas (Solar, Lunar, Kemadruma, Parivartana, Budhaditya, Bandhan, etc.)
- [ ] Validation utility to test against benchmark charts
- [ ] EXIT:0
- [ ] Memory files updated