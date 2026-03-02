# Deep Research Questions for Gemini Pro
## To Build a Computational Vedic Astrology Engine

**Context:** We are building a Python-based computational system that takes raw kundli data (planetary positions, degrees, nakshatras) and mathematically computes predictions. We need the EXACT formulas, rules, and logic - not interpretations. Think of it as reverse-engineering the algorithm that traditional astrologers use mentally.

---

## CATEGORY 1: SHADBALA CALCULATION FORMULAS (Priority: HIGH)

### Q1.1: Ochcha Bala (Exaltation Strength)
What is the exact mathematical formula for Ochcha Bala? I know each planet has an exaltation point (e.g., Sun exalts at 10° Aries = absolute 10°, Moon at 3° Taurus = absolute 33°). Is the formula:
```
Ochcha Bala = (180 - |planet_longitude - exaltation_longitude|) / 3
```
Result in Virupas (0-60 scale)? Please provide:
- The exact exaltation degree for each of the 7 planets (Sun through Saturn)
- The exact formula
- How debilitation point factors in (is it always 180° from exaltation?)

### Q1.2: Saptavargaja Bala
How is Saptavargaja Bala calculated? It involves checking a planet's dignity (own sign, mool trikona, exaltation, friendly, neutral, enemy, debilitation) across 7 divisional charts (D1, D2, D3, D7, D9, D12, D30). What are:
- The points assigned for each dignity level in each varga?
- Is it the same point scale across all 7 vargas or different?
- What are the exact rules for determining "mool trikona" sign and degree range for each planet?

### Q1.3: Dig Bala (Directional Strength)
The framework says Jupiter/Mercury are strongest in 1st house, Sun/Mars in 10th, Saturn in 7th, Moon/Venus in 4th. What is the exact formula?
- Is it based on the angular distance between the planet and its "dig bala point"?
- Formula: `Dig Bala = (180 - angular_distance_from_strongest_point) / 3` in Virupas?
- What happens when a planet is in the opposite house (weakest point)?

### Q1.4: Kala Bala Components
Kala Bala has 8-9 sub-components. For each, what is the exact calculation?
- **Nathonnatha Bala:** How is day/night birth factored? Which planets gain strength at day vs night? Formula?
- **Paksha Bala:** Based on Moon's phase (tithi). How exactly is the Shukla/Krishna paksha score calculated?
- **Tribhaga Bala:** Which planet rules which third of the day/night? How is 60 Virupas assigned?
- **Abda Bala (Year Lord):** How is the year lord determined? Formula for weekday of year start?
- **Masa Bala (Month Lord):** How is the month lord determined?
- **Vara Bala (Day Lord):** Born on Monday → Moon gets 45 Virupas. What do other planets get?
- **Hora Bala (Hour Lord):** How are planetary hours calculated? Which planet rules the birth hour?
- **Ayana Bala:** Formula involving planet's declination (kranti) and maximum declination (23°27')?
- **Yuddha Bala:** When two planets are within 1° longitude, how is the "winner" determined?

### Q1.5: Cheshta Bala (Motional Strength)
- How is Cheshta Bala calculated for each planet?
- Does retrograde motion give MORE or LESS cheshta bala?
- What is the exact formula relating planetary speed to Virupas?
- How is Sun's Cheshta Bala calculated (since Sun is never retrograde)?
- How is Moon's Cheshta Bala calculated (based on Paksha Bala)?

### Q1.6: Drik Bala (Aspectual Strength)
- How are benefic and malefic aspects quantified?
- Is there a formula: `Drik Bala = Sum(benefic_aspect_strengths) - Sum(malefic_aspect_strengths)`?
- How is the "strength" of an aspect calculated? Does it depend on the aspect angle (60°, 90°, 120°, 180°)?
- Natural benefics (Jupiter, Venus, well-placed Mercury, waxing Moon) vs Natural malefics (Saturn, Mars, Rahu, Ketu, Sun, waning Moon) - how is the classification done mathematically?

---

## CATEGORY 2: ASHTAKVARGA BINARY RULES (Priority: HIGH)

### Q2.1: Bhinna Ashtakvarga Contribution Rules
For each of the 7 planets (Sun through Saturn), there are 8 sources (7 planets + Ascendant) that give a benefic point (1) or not (0) based on the transit planet's position relative to the source. What are ALL these rules?

Example format needed:
```
SUN's Ashtakvarga:
- From SUN: Gives 1 in houses 1,2,4,7,8,9,10,11 from Sun's natal position
- From MOON: Gives 1 in houses 3,6,10,11 from Moon's natal position
- From MARS: Gives 1 in houses ...
... (for all 8 sources × 7 planets = 56 rule sets)
```

### Q2.2: Kaksha System within Ashtakvarga
Within each sign's ashtakvarga score, there are 8 equal divisions (Kaksha) of 3°45' each, each ruled by a planet in a specific order. What is:
- The fixed order of Kaksha lords (Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna?)
- How does a transiting planet's position within a Kaksha modify the ashtakvarga prediction?
- Is a transit in the Kaksha of a benefic contributor better than in a malefic contributor's Kaksha?

### Q2.3: Ashtakvarga Reduction (Trikona/Ekadhipati Shodhana)
What are the reduction rules applied to Ashtakvarga?
- Trikona Shodhana: How are points reduced in signs forming trines (1-5-9)?
- Ekadhipati Shodhana: When one planet lords two signs, how are the points redistributed?
- What is the reduced Sarvashtakvarga (Shodhya Pinda) and how is it calculated?

---

## CATEGORY 3: TRANSIT (GOCHAR) INTERPRETATION RULES (Priority: HIGH)

### Q3.1: Transit Results by House from Moon
When each planet transits each house FROM THE MOON SIGN, what are the results?
Provide the complete 9-planet × 12-house matrix:
```
Jupiter transiting 1st from Moon → [result]
Jupiter transiting 2nd from Moon → [result]
... (for all 9 planets × 12 houses = 108 combinations)
```
Which houses are considered "favorable" and which "unfavorable" for each planet's transit?

### Q3.2: Vedha (Obstruction) Rules
- Which transit positions block which other positions?
- Example: Jupiter in 2nd from Moon is blocked by a planet in 12th.
- Provide the complete Vedha pair table for all 9 planets.
- What are "Vipreet Vedha" exceptions (Sun-Saturn mutual exclusion)?

### Q3.3: Sade Sati Calculation
- Saturn transiting 12th, 1st, and 2nd from Moon sign = Sade Sati (7.5 years)
- What are the specific effects of each of the 3 phases?
- How does the Ashtakvarga score of Saturn in those signs modify the intensity?
- Is there a formula: `Sade Sati intensity = f(Saturn's BAV in sign, natal Saturn strength)`?
- What is "Dhaiya" (Kantaka Shani) - Saturn transiting 4th and 8th from Moon?

---

## CATEGORY 4: DASHA INTERPRETATION LOGIC (Priority: HIGH)

### Q4.1: Mahadasha-Antardasha Result Matrix
When planet A's Mahadasha runs with planet B's Antardasha, the result depends on:
1. A's house placement and lordship
2. B's house placement and lordship
3. A-B friendship/enmity (Panchda relationship)
4. A-B natural significations

Is there a systematic scoring formula like:
```
Result_score = f(A_shadbala, B_shadbala, A_houses, B_houses, A_B_friendship, yogas_involving_A_B)
```
Or is it purely qualitative? What are the traditional rules?

### Q4.2: Dasha Sandhi (Junction Period)
When one Mahadasha/Antardasha ends and another begins:
- How long is the transition/junction period?
- Is it the last 10% + first 10% of adjacent periods?
- What special effects occur during Sandhi?
- How does this affect prediction accuracy during transitions?

### Q4.3: Retrograde Planet's Dasha
Jupiter and Saturn are retrograde in our chart. When their dasha runs:
- Does retrograde give the results of the PREVIOUS house?
- Does it mean the planet acts like it's in the sign behind its actual position?
- How does retrograde affect antardasha calculations?
- What is the exact rule for retrograde interpretation in Parashari vs KP systems?

---

## CATEGORY 5: YOGA DETECTION RULES (Priority: MEDIUM)

### Q5.1: Complete Yoga Database
Provide the detection rules for at least the top 30 most important yogas:
1. Raj Yoga (multiple types)
2. Dhana Yoga (wealth)
3. Gajakesari Yoga
4. Chandra-Mangal Yoga
5. Budha-Aditya Yoga
6. Vipreet Raj Yoga
7. Pancha Mahapurusha Yogas (Ruchaka, Bhadra, Hamsa, Malavya, Shasha)
8. Neechabhanga Raj Yoga
9. Amala Yoga
10. Adhi Yoga
... etc.

For each, provide:
- EXACT detection criteria (which planet, which house, which relationship)
- Strength conditions (is the yoga stronger if planets are in certain dignity?)
- When does the yoga give results (which dasha activates it?)

### Q5.2: Yoga Cancellation Rules
When does a yoga get cancelled or weakened?
- Planet in yoga but combust (too close to Sun)?
- Planet in yoga but debilitated?
- Aspected by malefics?

---

## CATEGORY 6: DIVISIONAL CHART CALCULATION (Priority: MEDIUM)

### Q6.1: Navamsa (D9) Calculation Rules
- Confirm: For fire signs (Aries, Leo, Sag), navamsa starts from Aries
- For earth signs (Taurus, Virgo, Cap), starts from Capricorn
- For air signs (Gemini, Libra, Aquarius), starts from Libra
- For water signs (Cancer, Scorpio, Pisces), starts from Cancer
- Is this correct? Each 3°20' segment advances one sign from the start?

### Q6.2: Dashamsha (D10) for Career
- How to calculate D10 placement from a planet's degree?
- For odd signs: count from the same sign. For even signs: count from the 9th sign. Is this correct?
- What specific career indications come from D10 placements?

### Q6.3: Vimshopak Bala Calculation
- How to score a planet across all 16 divisional charts?
- Weightage table: D1=3.5, D2=1, D3=1, D4=0.5, D7=0.5, D9=3, D10=0.5, D12=0.5, D16=1, D20=0.5, D24=0.5, D27=0.5, D30=1, D40=0.5, D45=0.5, D60=4 (total=20)?
- Is the score: In own sign=full weight, exalted=full, friendly=3/4, neutral=1/2, enemy=1/4, debilitated=0?

---

## CATEGORY 7: REAL-TIME COMPUTATION NEEDS (Priority: HIGH)

### Q7.1: Ephemeris Data Source
To calculate current planetary positions (transits):
- What open-source ephemeris library can give sidereal (Lahiri ayanamsa) planetary positions?
- Swiss Ephemeris / PySwissEph - does it support Lahiri ayanamsa directly?
- What API or Python library can give me: "Where is Saturn on March 15, 2026 in sidereal zodiac?"

### Q7.2: Current Transit Data Needed
For the period Feb 2026 - Feb 2027:
- Saturn's transit sign and dates of any sign changes (sidereal Lahiri)
- Jupiter's transit sign and dates of any sign changes
- Rahu-Ketu axis position
- Mars's approximate monthly sign positions
- Any major retrograde periods for Jupiter, Saturn, Mercury, Venus

### Q7.3: Planetary Combustion Ranges
How close to the Sun must each planet be to be "combust" (asta)?
```
Moon: ? degrees
Mars: ? degrees
Mercury: ? degrees
Jupiter: ? degrees
Venus: ? degrees
Saturn: ? degrees
```

---

## CATEGORY 8: NAKSHATRA-SPECIFIC DATA (Priority: MEDIUM)

### Q8.1: Nakshatra Characteristics Table
For each of the 27 nakshatras, provide:
- Ruling planet
- Element (deva/manushya/rakshasa gana)
- Yoni (animal symbol)
- Favorable activities
- Unfavorable activities
- Body part association
- Deity

### Q8.2: Nakshatra Compatibility Matrix
- How is Nakshatra-based compatibility (marriage matching) scored?
- The 8 Kuta system: Varna (1), Vasya (2), Tara (3), Yoni (4), Graha Maitri (5), Gana (6), Bha Kuta (7), Nadi (8)
- What are the exact scoring rules for each of the 8 kutas?

---

## CATEGORY 9: SYSTEM INTEGRATION QUESTIONS (Priority: HIGH)

### Q9.1: Confidence Scoring
When multiple dasha systems (Vimshottari, Yogini, Chara) are checked for the same event:
- How do traditional astrologers weight the agreement/disagreement?
- Is there a standard priority: Vimshottari > Yogini > Chara?
- When they contradict, which one to trust for which type of event?

### Q9.2: Event Trigger Logic
An event (e.g., job change, marriage) needs:
1. Promise in D1 (static chart says it's possible)
2. Activation in Dasha (timing system says "now")
3. Trigger in Transit (current planetary position confirms)

What is the precise logic for determining WHICH month/week the event happens?
- Is it when the dasha lord's transit matches with the natal position?
- Is it when Jupiter/Saturn transit aspects the relevant house?
- What are the "double transit" rules (Jupiter + Saturn both influencing a house)?

### Q9.3: Quantifying Prediction Confidence
Can we create a numerical confidence score like:
```
confidence = (dasha_alignment × 0.3) + (transit_support × 0.25) +
             (ashtakvarga_score × 0.15) + (yoga_activation × 0.15) +
             (kp_sublord_confirmation × 0.15)
```
Has any scholar or researcher attempted to quantify this? What weightages would be appropriate?

---

## OUTPUT FORMAT REQUESTED
For each answer, please provide:
1. The EXACT formula or rule (not vague descriptions)
2. A worked example if possible
3. Any exceptions or edge cases
4. Source reference (which classical text this comes from: BPHS, Uttara Kalamrita, KP Reader, etc.)
