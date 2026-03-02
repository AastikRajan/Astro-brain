# Vedic Astrology: Computational System Analysis
## What I Understand, What's Computable, and What Needs Research

---

## PART 1: THE SYSTEM ARCHITECTURE (What I've Reverse-Engineered)

### 1.1 The Coordinate System
The entire system is built on a **360-degree circle** with two overlapping grids:
- **Grid A - Signs (Rashi):** 12 divisions of 30° each (Aries=0-30, Taurus=30-60, ... Pisces=330-360)
- **Grid B - Nakshatras:** 27 divisions of 13°20' each (Ashwini=0-13°20', Bharani=13°20'-26°40', ...)
- **Grid C - Padas:** Each Nakshatra has 4 padas of 3°20' each (108 total padas = 9 Navamsa per sign)

Every planet's position is a single number (0-360°) that maps onto ALL three grids simultaneously. This is the foundational data structure.

**VERIFIED MATH FROM OUR DATA:**
- Moon at 24°14'18" of Aries = absolute position ~24.238°
- Bharani nakshatra spans 13°20' to 26°40' (13.333° to 26.667°)
- Moon is in Bharani, Pada 4 (last quarter: 23°20' to 26°40') ✓ MATCHES

### 1.2 The Ownership Model (Who Controls What)
Each sign has exactly ONE lord (owner planet):
```
Aries=Mars, Taurus=Venus, Gemini=Mercury, Cancer=Moon,
Leo=Sun, Virgo=Mercury, Libra=Venus, Scorpio=Mars,
Sagittarius=Jupiter, Capricorn=Saturn, Aquarius=Saturn, Pisces=Jupiter
```
Each nakshatra also has a lord (in the Vimshottari sequence):
```
Ketu(1,10,19), Venus(2,11,20), Sun(3,12,21), Moon(4,13,22),
Mars(5,14,23), Rahu(6,15,24), Jupiter(7,16,25), Saturn(8,17,26), Mercury(9,18,27)
```
This creates a **dual-ownership matrix**: every degree of the zodiac is simultaneously ruled by a sign lord AND a nakshatra lord. The interaction between these two owners is a key computational variable.

### 1.3 The House System (Bhava)
Houses are counted FROM the Ascendant sign. Our Lagna = Gemini, so:
```
H1=Gemini, H2=Cancer, H3=Leo, H4=Virgo, H5=Libra, H6=Scorpio,
H7=Sagittarius, H8=Capricorn, H9=Aquarius, H10=Pisces, H11=Aries, H12=Taurus
```
Each house has a "lord" = the planet that owns the sign falling in that house.
This creates the **House-Lord mapping** which is critical:
```
H1-lord=Mercury, H2-lord=Moon, H3-lord=Sun, H4-lord=Mercury,
H5-lord=Venus, H6-lord=Mars, H7-lord=Jupiter, H8-lord=Saturn,
H9-lord=Saturn, H10-lord=Jupiter, H11-lord=Mars, H12-lord=Venus
```

**IMPORTANT FINDING:** Mercury rules BOTH H1 and H4. Jupiter rules BOTH H7 and H10. Mars rules BOTH H6 and H11. Venus rules BOTH H5 and H12. Saturn rules BOTH H8 and H9. These dual-lordship connections create inter-house dependencies.

### 1.4 Planetary Dignity System (Strength by Position)
Planets have varying strength depending on which sign they're in:
- **Exaltation (Uchcha):** Maximum strength. Each planet has ONE sign of exaltation.
- **Own Sign (Swakshetra):** Strong. Planet in the sign it owns.
- **Friendly Sign:** Moderate strength.
- **Neutral Sign:** Average.
- **Enemy Sign:** Weak.
- **Debilitation (Neecha):** Minimum strength. Opposite of exaltation.

**FROM OUR DATA - Planet Dignity Status:**
| Planet | Sign | Dignity Assessment |
|--------|------|-------------------|
| Jupiter[R] | Cancer | **EXALTED** (Cancer is Jupiter's exaltation) |
| Saturn[R] | Gemini | **Friendly** (Mercury is friend of Saturn) |
| Moon | Aries | Mars is neutral to Moon → **Neutral** |
| Sun | Sagittarius | Jupiter is friend of Sun → **Friendly** |
| Mercury | Sagittarius | Jupiter is enemy of Mercury → **Enemy sign** |
| Mars | Libra | Venus is neutral to Mars → **Neutral** (but Mars debilitates in Cancer, not here) |
| Venus | Libra | **Own Sign** (Venus owns Libra) |
| Rahu | Taurus | Venus-owned sign. Rahu exalts in Taurus by some traditions → **Strong** |
| Ketu | Scorpio | Mars-owned sign. Ketu is comfortable here → **Strong** |

### 1.5 The Aspect System
Planets cast aspects (drishti) on other planets/houses. Standard aspects:
- **All planets:** Aspect the 7th house from themselves (opposite)
- **Mars special:** Also aspects 4th and 8th from itself
- **Jupiter special:** Also aspects 5th and 9th from itself
- **Saturn special:** Also aspects 3rd and 10th from itself

**COMPUTED ASPECTS FOR OUR CHART (from planet's house position):**
| Planet | In House | Standard (7th) | Special Aspects |
|--------|----------|----------------|-----------------|
| Saturn[R] | H1 | H7 | H3 (3rd), H10 (10th) |
| Jupiter[R] | H2 | H8 | H6 (5th), H10 (9th) |
| Sun | H7 | H1 | - |
| Mercury | H7 | H1 | - |
| Mars | H5 | H11 | H8 (4th), H12 (8th) |
| Venus | H5 | H11 | - |
| Moon | H11 | H5 | - |

**KEY INSIGHT:** H10 (career) receives aspects from BOTH Saturn (10th aspect) AND Jupiter (9th aspect). This is significant - the two biggest planets both influence career.

---

## PART 2: THE QUANTITATIVE ENGINES (Computable Math)

### 2.1 Shadbala - Six-Fold Strength (WE HAVE COMPLETE DATA)
This is a **scoring system with 6 sub-scores** that sum to a total. Each sub-score has its own calculation:

**Component Breakdown (from our data):**
```
Total Shadbala = Sthana Bala + Dig Bala + Kala Bala + Cheshta Bala + Naisargika Bala + Drik Bala
```

| Component | Sun | Moon | Mars | Mercury | Jupiter | Venus | Saturn |
|-----------|-----|------|------|---------|---------|-------|--------|
| Sthana (Position) | 226.85 | 199.58 | 160.93 | 164.09 | 213.05 | 147.21 | 145.17 |
| Dig (Direction) | 24.17 | 12.06 | 9.24 | 2.65 | 50.57 | 50.43 | 7.96 |
| Kala (Time) | 37.21 | 196.68 | 89.14 | 191.27 | 181.89 | 98.13 | 48.11 |
| Cheshta (Motion) | 1.85 | 47.89 | 17.36 | 25.65 | 43.16 | 42.85 | 58.77 |
| Naisargika (Natural) | 60.00 | 51.42 | 17.16 | 25.74 | 34.26 | 42.84 | 8.58 |
| Drik (Aspect) | 9.30 | -3.61 | 15.74 | 4.13 | -10.26 | 16.83 | -24.56 |
| **TOTAL** | **359.38** | **504.03** | **309.56** | **413.53** | **512.66** | **398.30** | **244.04** |
| **Rupas** | **5.99** | **8.40** | **5.16** | **6.89** | **8.54** | **6.64** | **4.07** |
| **Min Req** | **5.00** | **6.00** | **5.00** | **7.00** | **6.50** | **5.50** | **5.00** |
| **Ratio** | **1.20** | **1.40** | **1.03** | **0.98** | **1.31** | **1.21** | **0.81** |

**CRITICAL FLAGS:**
- Mercury: Ratio 0.98 → BELOW MINIMUM. Lagna lord is underperforming.
- Saturn: Ratio 0.81 → SIGNIFICANTLY BELOW MINIMUM. Weakest planet.
- Drik Bala: Saturn has -24.56 (heavily aspected by malefics)

**WHAT I DON'T KNOW:** The exact formulas for calculating each sub-component. I have the RESULTS but not the PROCESS. To build a Python engine, I need:
- How is Ochcha Bala calculated from planet's degree vs exaltation degree?
- How is Saptavargaja Bala derived from divisional chart placements?
- What are the exact Dig Bala formulas for each planet-house combination?
- How are Kala Bala sub-components (Nathonnatha, Paksha, etc.) calculated?

### 2.2 Bhavabala - House Strength (WE HAVE COMPLETE DATA)
```
Total Bhavabala = Bhavadhipati Bala + Bhavdig Bala + Bhavdrishti Bala
```
- Bhavadhipati Bala = Shadbala of the house lord (directly linked!)
- Bhavdig Bala = Positional strength based on house number (fixed values?)
- Bhavdrishti Bala = Net aspect influence (benefic - malefic) on the house

**KEY INSIGHT:** House strength is DEPENDENT on planetary strength. H7 is strongest because Jupiter (its lord) has the highest Shadbala.

### 2.3 Ashtakvarga - Transit Effectiveness Score (WE HAVE COMPLETE DATA)
This is a **binary matrix** system:
- 7 planets each produce an 8×12 binary grid (contributions from 7 planets + ascendant across 12 signs)
- Each cell = 0 or 1 (benefic point or not)
- Sum across 8 contributors = that planet's ashtakvarga for that sign (0-8 scale)
- Sarvashtakvarga = sum of all 7 planets' scores for each sign (0-56 scale)

**FROM OUR DATA - Sarvashtakvarga:**
```
Aries=33, Taurus=28, Gemini=30, Cancer=25, Leo=33, Virgo=30,
Libra=30, Scorpio=27, Sagittarius=22, Capricorn=22, Aquarius=32, Pisces=25
```
Average = 337/12 = 28.08. Signs above average = favorable for transits.

**USAGE RULE:** When a planet transits a sign:
- If that sign has HIGH points in that planet's individual ashtakvarga → good results
- If LOW points → difficult results
- The Sarvashtakvarga gives an OVERALL favorability of the sign

**WHAT I NEED:** The exact rules for which planet contributes 1 vs 0 in each cell. There are traditional rules (e.g., "Sun gives a benefic point to itself in signs 1,2,4,7,8,9,10,11 from itself").

### 2.4 Vimshottari Dasha - Timing Engine (WE HAVE COMPLETE DATA)
**THE MATH I'VE VERIFIED:**

Starting Dasha Calculation:
```
Moon's Nakshatra = Bharani (nakshatra #2)
Bharani Lord = Venus
Therefore starting Mahadasha = Venus

Venus dasha total = 20 years
Moon's position in Bharani = 24°14'18" - 13°20'00" = 10°54'18" traversed
Remaining = 26°40'00" - 24°14'18" = 2°25'42"
Balance fraction = 2°25'42" / 13°20'00" = 2.4283° / 13.3333° = 0.18213
Balance = 20 × 0.18213 = 3.6425 years = 3Y 7M 21D ✓ MATCHES DATA
```

Antardasha Calculation:
```
Within any Mahadasha of duration D_major:
Antardasha of planet X = (D_x / 120) × D_major

Example: Mars Mahadasha (7 years)
Mars-Mercury antardasha = (17/120) × 7 = 0.9917 years ≈ 11 months 28 days
```

Pratyantardasha Calculation:
```
Within any Antardasha of duration D_antar:
Pratyantardasha of planet X = (D_x / 120) × D_antar
```

**THIS IS FULLY COMPUTABLE.** Given Moon's position, I can calculate the entire dasha timeline from birth to death. The JSON data confirms this.

### 2.5 Yogini Dasha (WE HAVE COMPLETE DATA)
**THE MATH:**
```
Starting Yogini = (Moon's Nakshatra number + 3) mod 8
Bharani = nakshatra #2
(2 + 3) mod 8 = 5 mod 8 = 5 → Bhadrika (Mercury)

Wait - but the data shows starting yogini period involves different ones.
Need to verify: the formula might be (N+3)/8 where N is the nakshatra number,
and the remainder maps to the yogini. Need to check if remainder 0 = Mangala or Sankata.
```

**UNCLEAR:** The exact starting yogini formula. The framework text mentions `(N+3)/8 remainder` but doesn't specify the mapping of remainder to yogini. Need research.

### 2.6 KP System (WE HAVE COMPLETE DATA)
The KP system adds a SUB-division layer on top of nakshatras:

Each nakshatra (13°20') is divided into 9 unequal sub-divisions, proportional to the Vimshottari dasha periods:
```
Ketu sub = (7/120) × 13°20' = 0°46'40"
Venus sub = (20/120) × 13°20' = 2°13'20"
Sun sub = (6/120) × 13°20' = 0°40'
Moon sub = (10/120) × 13°20' = 1°06'40"
Mars sub = (7/120) × 13°20' = 0°46'40"
Rahu sub = (18/120) × 13°20' = 2°00'
Jupiter sub = (16/120) × 13°20' = 1°46'40"
Saturn sub = (19/120) × 13°20' = 2°06'40"
Mercury sub = (17/120) × 13°20' = 1°53'20"
```
The starting sub within each nakshatra follows the same cyclic order starting from the nakshatra lord.

**THIS IS FULLY COMPUTABLE** from a planet's degree. The JSON has Rashi Lord, Nak Lord, Sub Lord, and Sub-Sub Lord for each planet and cusp.

### 2.7 The Signification Chain (KP's Core Logic)
```
Planet → occupies a HOUSE → lords certain HOUSES
Star Lord → occupies a HOUSE → lords certain HOUSES
Sub Lord → occupies a HOUSE → lords certain HOUSES

Final signification = Union of all these house numbers

If a planet signifies houses 2,6,10,11 → POSITIVE for finance/career
If a planet signifies houses 5,8,12 → NEGATIVE (losses)
If mixed → the Sub Lord decides the direction
```

**FROM OUR DATA - Planet → House Signification (KP):**
```
Sun: 3,5,6          → Mixed (5=speculation good, 6=obstacles, 3=effort)
Moon: 2,4,5,11,12   → Mixed (2,11=gains, 12=losses, 4=property, 5=creativity)
Mars: 4,6,11        → Positive tendency (6=service, 11=gains, 4=property)
Mercury: 1,4,5,6,12 → Mixed (1=self, 4,5=good, 6=health issues, 12=losses)
Jupiter: 1,2,4,6,7,10 → Strongly positive (1,2,10=career, 7=partnerships)
Venus: 4,5,11,12    → Mixed (5,11=gains/creativity, 12=expenses)
Saturn: 4,6,8,9,11,12 → Mixed-negative (8=obstacles, 9=luck issues, but 11=gains)
Rahu: 2,11          → Strongly positive (2=wealth, 11=gains)
Ketu: 5,8,9,12      → Mixed-negative (5=intelligence, but 8,12=losses)
```

### 2.8 Jaimini Chara Karakas (NEED TO COMPUTE)
Based on descending degree within sign (ignoring sign, just the degree):
```
Sun: 00°33' in Sagittarius → degree within sign = 0.558°
Moon: 24°14' in Aries → degree = 24.238°
Mars: 15°47' in Libra → degree = 15.781°
Mercury: 17°43' in Sagittarius → degree = 17.717°
Jupiter: 23°58' in Cancer → degree = 23.963°
Venus: 16°45' in Libra → degree = 16.754°
Saturn: 01°46' in Gemini → degree = 1.772°

Descending order of degrees:
1. Moon: 24.238° → ATMA KARAKA (Soul significator)
2. Jupiter: 23.963° → AMATYA KARAKA (Career significator)
3. Mercury: 17.717° → BHRATRI KARAKA (Siblings)
4. Venus: 16.754° → MATRI KARAKA (Mother)
5. Mars: 15.781° → PUTRA KARAKA (Children)
6. Saturn: 1.772° → GNATI KARAKA (Obstacles)
7. Sun: 0.558° → DARA KARAKA (Spouse)
```

**KEY FINDING:** Moon is the Atma Karaka (soul planet). Jupiter is the Amatya Karaka (career). Moon-Jupiter are in a 2-11 relationship (Jupiter in H2, Moon in H11) which creates a financial/wealth axis for career. This is a 2-11 Dhana connection between AK and AmK.

---

## PART 3: DATA INVENTORY - WHAT WE HAVE vs WHAT WE NEED

### HAVE (in JSON):
| Data Type | Status | Completeness |
|-----------|--------|-------------|
| Birth details | ✅ Complete | Date, time, place, coordinates |
| D1 Rashi chart positions | ✅ Complete | All 9 planets + outer planets |
| House placement | ✅ Computable | From Lagna + planetary positions |
| Vimshottari Dasha tables | ✅ Complete | All levels down to Pratyantardasha |
| Yogini Dasha tables | ✅ Complete | All periods with sub-periods |
| Chara Dasha tables | ✅ Complete | Major and sub-periods |
| Shadbala (all components) | ✅ Complete | All 6 strengths + totals + ratios |
| Bhavabala (all components) | ✅ Complete | All 3 components + totals |
| Sarvashtakvarga | ✅ Complete | 12 totals |
| Prastharashtakvarga | ✅ Partial | Sun's individual grid available |
| KP Cuspal positions | ✅ Complete | All 12 cusps with Rashi/Nak/Sub/SS |
| KP Planetary positions | ✅ Complete | All planets with Rashi/Nak/Sub/SS |
| KP House significations | ✅ Complete | Both per-planet and per-house |
| Friendship tables | ✅ Complete | Naisargika, Tatkalika, Panchda (3 tables) |
| Lucky/unlucky metadata | ✅ Complete | Numbers, days, planets, etc. |
| Chart images | ✅ References | 25 image filenames referenced |

### MISSING (not in JSON but needed for full computation):
| Data Type | Why Needed | Can We Compute It? |
|-----------|-----------|-------------------|
| Navamsa (D9) chart | Confirms planet's TRUE dignity. Framework says it's the 2nd most important chart | YES - from degree. Each 3°20' maps to a specific navamsa sign |
| Other divisional charts (D2-D60) | Specific life domains | YES - each has a formula from degree |
| Vimshopak Bala | Cumulative divisional strength score | YES - if we compute all 16 divisional placements |
| Planetary aspects (degrees) | Exact aspect strengths, not just presence | PARTIALLY - we know the rules but need exact strength formulas |
| Bhava Chalit positions | Where planets ACTUALLY function (house vs sign) | YES - from Lagna degree and planet degrees |
| Current transit positions | WHERE planets are NOW (2026) | NEED EXTERNAL DATA (ephemeris) |
| Yoga formations | Specific combinations (Raj Yoga, Gajakesari, etc.) | YES - from planet positions, but need the RULES database |
| Nakshatra-level compatibility data | Detailed nakshatra effects | NEED RESEARCH on 27 nakshatra characteristics |

---

## PART 4: COMPUTABLE FORMULAS I CAN ALREADY IMPLEMENT IN PYTHON

### 4.1 Navamsa (D9) Calculator
```python
def get_navamsa_sign(planet_degree):
    """Each 3°20' = one navamsa pada.
    Navamsa starts from Aries for fire signs, Cancer for earth,
    Libra for air, Capricorn for water signs."""
    sign_index = int(planet_degree / 30)  # 0-11
    degree_in_sign = planet_degree % 30
    pada = int(degree_in_sign / (10/3))  # 0-8 (9 divisions)

    # Starting navamsa depends on sign element
    element = sign_index % 4  # 0=fire, 1=earth, 2=air, 3=water
    start_signs = [0, 3, 6, 9]  # Aries, Cancer, Libra, Capricorn

    navamsa_sign = (start_signs[element] + pada) % 12
    return navamsa_sign
```

### 4.2 Dasha Timeline Calculator
```python
def calculate_dasha_balance(moon_degree):
    """Calculate remaining dasha at birth from Moon's position."""
    nakshatra_span = 13 + 20/60  # 13.333 degrees
    nakshatra_index = int(moon_degree / nakshatra_span)  # 0-26

    lords_sequence = ['KET','VEN','SUN','MON','MAR','RAH','JUP','SAT','MER']
    durations = [7, 20, 6, 10, 7, 18, 16, 19, 17]

    lord_index = nakshatra_index % 9
    position_in_nakshatra = moon_degree % nakshatra_span
    remaining_fraction = 1 - (position_in_nakshatra / nakshatra_span)
    balance_years = durations[lord_index] * remaining_fraction

    return lords_sequence[lord_index], balance_years
```

### 4.3 KP Sub-Lord Calculator
```python
def get_sub_lord(degree):
    """Get the sub-lord for any given zodiacal degree."""
    lords = ['KET','VEN','SUN','MON','MAR','RAH','JUP','SAT','MER']
    durations = [7, 20, 6, 10, 7, 18, 16, 19, 17]
    total = 120

    nakshatra_span = 13 + 20/60
    nak_index = int(degree / nakshatra_span)
    nak_lord_index = nak_index % 9

    degree_in_nak = degree % nakshatra_span

    # Sub-divisions proportional to dasha durations
    # Starting from nakshatra lord's position in sequence
    sub_start = nak_lord_index
    accumulated = 0

    for i in range(9):
        idx = (sub_start + i) % 9
        sub_span = (durations[idx] / total) * nakshatra_span
        accumulated += sub_span
        if degree_in_nak < accumulated:
            return lords[idx]

    return lords[(sub_start + 8) % 9]
```

### 4.4 Ashtakvarga Transit Score Lookup
```python
# Already have the data, just need lookup
sarvashtakvarga = {
    'Aries': 33, 'Taurus': 28, 'Gemini': 30, 'Cancer': 25,
    'Leo': 33, 'Virgo': 30, 'Libra': 30, 'Scorpio': 27,
    'Sagittarius': 22, 'Capricorn': 22, 'Aquarius': 32, 'Pisces': 25
}
# Average = 28.08. Above = favorable sign for transits.
```

---

## PART 5: THE INTERPRETATION ENGINE (What Converts Numbers to Meaning)

This is the HARDEST part. The numbers above are "features" in ML terms. The interpretation requires RULES that map feature combinations to outcomes. These rules are where the deep research is needed.

### 5.1 Dasha Interpretation Rules
When Mars Mahadasha + Mercury Antardasha is active:
- Mars's house results get PRIMARY activation (Mars lords H6, H11; sits in H5)
- Mercury's house results get SECONDARY activation (Mercury lords H1, H4; sits in H7)
- The INTERACTION between Mars and Mercury matters:
  - In Naisargika friendship: Mars considers Mercury an ENEMY
  - In Tatkalika friendship: Need to check (based on relative position in chart)
  - In Panchda (composite): Mars-Mercury = NEUTRAL

**THE QUESTION:** How does this friendship/enmity affect the INTENSITY and DIRECTION of results? Is there a scoring formula? Or is it qualitative?

### 5.2 Transit Rules
When transit Jupiter enters sign X:
- Check Jupiter's individual ashtakvarga for sign X
- Check Sarvashtakvarga for sign X
- Check which HOUSE sign X is from natal Moon (for Gochar rules)
- Check if Jupiter aspects any natal planets while in sign X

**VEDHA RULE (Obstruction):** Certain transit positions are "blocked" by another planet's transit in a specific counter-position. These pairs are fixed rules.

**THE QUESTION:** What are all the Vedha pairs? What are the "Vipreet Vedha" exceptions?

### 5.3 Yoga Detection Rules
Specific planet combinations = specific outcomes:
- **Gajakesari Yoga:** Jupiter in kendra (1,4,7,10) from Moon → We have Jupiter in H2 from Lagna but what house from Moon? Moon in H11 (Aries), Jupiter in H2 (Cancer). Cancer is 4th from Aries → Jupiter is in 4th from Moon = **GAJAKESARI YOGA EXISTS** ← This is a prosperity yoga!
- **Chandra-Mangal Yoga:** Moon-Mars conjunction or mutual aspect → Moon in H11, Mars in H5. They are in 7th from each other = mutual aspect! **CHANDRA-MANGAL YOGA EXISTS** ← wealth yoga!
- **Budha-Aditya Yoga:** Sun-Mercury in same sign → Both in Sagittarius → **EXISTS** ← intelligence yoga!

**THE QUESTION:** What is the complete list of major yogas and their detection rules (which I can code)?

---

## PART 6: THE PREDICTION PIPELINE (How Everything Connects)

```
STEP 1: STATIC ANALYSIS (birth chart - one-time)
├── Planet positions → House placements
├── House lordships → Inter-house dependencies
├── Shadbala → Planet capability scores
├── Bhavabala → House capability scores
├── Ashtakvarga → Transit readiness per sign
├── KP significations → Event possibility mapping
├── Jaimini Karakas → Soul-level purpose indicators
├── Yoga detection → Special combination flags
└── Navamsa analysis → Hidden strength/weakness

STEP 2: DYNAMIC ANALYSIS (time-dependent)
├── Current Dasha period → Which planets are "ON"
├── Current Yogini period → Cross-verification signal
├── Current Chara Dasha → Which signs are "ON"
├── Current transits → Where planets are NOW
├── Transit Ashtakvarga scores → How effective are current transits
└── Dasha-Transit interaction → When both align = EVENT

STEP 3: DOMAIN-SPECIFIC QUERIES
├── Career → Check H10 lord, KP 10th cusp sub-lord, D10, AmK
├── Finance → Check H2, H11, Dhana yogas, Jupiter strength
├── Health → Check H1, H6, H8 lords, Mars/Saturn afflictions
├── Relationships → Check H7, DK, Venus, D9
└── Education → Check H4, H5, D24, Mercury strength

STEP 4: CONFIDENCE SCORING
├── If Vimshottari + Yogini agree → HIGH confidence
├── If KP sub-lord confirms → VERY HIGH confidence
├── If Ashtakvarga transit score supports → CONFIRMED
└── If multiple systems contradict → LOW confidence, flag uncertainty
```

---

## PART 7: WHAT I CAN BUILD RIGHT NOW vs WHAT NEEDS RESEARCH

### CAN BUILD NOW:
1. ✅ Navamsa (D9) calculator from degrees
2. ✅ All 16 divisional chart calculators
3. ✅ Dasha timeline engine (any level of depth)
4. ✅ KP sub-lord chain calculator
5. ✅ Jaimini Chara Karaka identifier
6. ✅ House-planet-lordship mapper
7. ✅ Ashtakvarga transit score lookup
8. ✅ Aspect calculator (who aspects whom)
9. ✅ Basic yoga detector (for known yoga rules)
10. ✅ Dasha period finder (what period is active on any given date)

### NEEDS RESEARCH FIRST:
1. ❓ Complete Shadbala calculation formulas (all sub-components)
2. ❓ Complete list of Yoga definitions (there are 100+ named yogas)
3. ❓ Transit interpretation rules (Gochar phal for each planet in each house from Moon)
4. ❓ Vedha (obstruction) rules and exceptions
5. ❓ Dasha interpretation rules (what happens when planet A's dasha runs and planet B's sub-dasha runs, based on their relationship)
6. ❓ KP "ruling planets" methodology (for event timing precision)
7. ❓ Ashtakvarga Kaksha-based predictions (within each sign, which planet's kaksha is the transit planet in?)
8. ❓ Bhinna Ashtakvarga individual planet contribution rules (the 8 binary rules per planet)
9. ❓ Sade Sati calculation and effects by phase
10. ❓ Dasha Sandhi (junction) effects when one period transitions to another
11. ❓ Planetary combustion rules (when planets are too close to Sun)
12. ❓ Retrograde planet interpretation (Jupiter and Saturn are both retrograde in our chart)
13. ❓ Nakshatra-specific qualities and their effect on planet behavior
14. ❓ Paya (Gold/Silver/Copper/Iron) system calculation and interpretation
15. ❓ How to calculate actual transit dates for planets (ephemeris data source)
