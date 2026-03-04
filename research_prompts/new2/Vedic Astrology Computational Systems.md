# **Computational Frameworks for Advanced Vedic Astrology: Transits, Chakras, and Solar Returns**

The development of a sophisticated computational Vedic astrology engine necessitates the translation of ancient cosmological rules into discrete mathematical algorithms, Boolean logic matrices, and topological data structures. Advanced predictive frameworks—such as Gochara (transits), Sudarshana Chakra, Sarvatobhadra Chakra, Kota Chakra, and Tajika (Varshaphala)—operate on multidimensional layers of planetary geometries, temporal progressions, and relational strengths. The following comprehensive architectural blueprint provides the necessary algorithmic logic for programming these systems, codifying the rules of planetary obstruction, fractal time progression, spatial grid mapping, and solar return evaluation.

## **Part A: Gochara Vedha (Transit Obstruction) Matrices**

In Vedic transit theory, planetary effects are calculated relative to the natal Moon. However, the manifestation of a favorable transit is subject to binary obstruction logic known as *Vedha* (piercing or blocking). Conversely, a negative transit can be neutralized by *Vipareeta Vedha* (reverse obstruction).1 For a computational engine, this requires simultaneous array monitoring of the natal Moon's relative houses. The engine must query the location of the transiting planet and cross-reference a specific paired house for simultaneous occupation by an obstructing entity.

### **The Complete 12-House Vedha Pair Tables**

To program this comprehensively for all 12 houses, the engine must evaluate both forward obstruction (Vedha) and reverse obstruction (Vipareeta Vedha). When a transiting planet occupies a specific benefic house (![][image1]), the engine checks the corresponding paired Vedha house (![][image2]). If a planetary entity occupies ![][image2], the positive output is negated.1 By the law of inversion, if a planet transits an inauspicious house (![][image2]), it generates negative results, but if another planet simultaneously occupies its paired ![][image1] position, the adverse effects are mathematically canceled (Vipareeta Vedha).2 Houses lacking a defined pair execute their absolute values without interference.

The following matrices provide the complete array mappings for all 12 houses for the seven classical planets, enabling exhaustive if/else conditional logic.2

#### **1\. The Sun (Surya)**

The Sun yields auspicious results in houses 3, 6, 10, and 11 from the natal Moon.4

| Transit House | Nature of Result | Matched House to Check for Obstruction (Vedha / Vipareeta Vedha) |
| :---- | :---- | :---- |
| **1** | Inauspicious (-) | No paired cancellation (Absolute) |
| **2** | Inauspicious (-) | No paired cancellation (Absolute) |
| **3** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 9** |
| **4** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 10** |
| **5** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 11** |
| **6** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 12** |
| **7** | Inauspicious (-) | No paired cancellation (Absolute) |
| **8** | Inauspicious (-) | No paired cancellation (Absolute) |
| **9** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 3** |
| **10** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 4** |
| **11** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 5** |
| **12** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 6** |

#### **2\. The Moon (Chandra)**

The Moon yields auspicious results in houses 1, 3, 6, 7, 10, and 11\.3

| Transit House | Nature of Result | Matched House to Check for Obstruction (Vedha / Vipareeta Vedha) |
| :---- | :---- | :---- |
| **1** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 5** |
| **2** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 7** |
| **3** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 9** |
| **4** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 10** |
| **5** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 1** |
| **6** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 12** |
| **7** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 2** |
| **8** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 11** |
| **9** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 3** |
| **10** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 4** |
| **11** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 8** |
| **12** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 6** |

#### **3\. Mars (Mangala)**

Mars functions similarly to the Sun and Saturn, favoring upachaya houses 3, 6, and 11\.3

| Transit House | Nature of Result | Matched House to Check for Obstruction (Vedha / Vipareeta Vedha) |
| :---- | :---- | :---- |
| **1** | Inauspicious (-) | No paired cancellation (Absolute) |
| **2** | Inauspicious (-) | No paired cancellation (Absolute) |
| **3** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 12** |
| **4** | Inauspicious (-) | No paired cancellation (Absolute) |
| **5** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 11** |
| **6** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 9** |
| **7** | Inauspicious (-) | No paired cancellation (Absolute) |
| **8** | Inauspicious (-) | No paired cancellation (Absolute) |
| **9** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 6** |
| **10** | Inauspicious (-) | No paired cancellation (Absolute) |
| **11** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 5** |
| **12** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 3** |

#### **4\. Mercury (Budha)**

Mercury presents the most complex transit geometry, yielding auspicious results in 2, 4, 6, 8, 10, and 11\.3

| Transit House | Nature of Result | Matched House to Check for Obstruction (Vedha / Vipareeta Vedha) |
| :---- | :---- | :---- |
| **1** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 8** |
| **2** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 5** |
| **3** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 4** |
| **4** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 3** |
| **5** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 2** |
| **6** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 9** |
| **7** | Inauspicious (-) | No paired cancellation (Absolute) |
| **8** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 1** |
| **9** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 6** |
| **10** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 8** |
| **11** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 12** |
| **12** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 11** |

#### **5\. Jupiter (Guru)**

Jupiter's transit beneficence aligns with 2, 5, 7, 9, and 11\.3

| Transit House | Nature of Result | Matched House to Check for Obstruction (Vedha / Vipareeta Vedha) |
| :---- | :---- | :---- |
| **1** | Inauspicious (-) | No paired cancellation (Absolute) |
| **2** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 12** |
| **3** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 7** |
| **4** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 5** |
| **5** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 4** |
| **6** | Inauspicious (-) | No paired cancellation (Absolute) |
| **7** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 3** |
| **8** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 11** |
| **9** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 10** |
| **10** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 9** |
| **11** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 8** |
| **12** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 2** |

#### **6\. Venus (Shukra)**

Venus provides overwhelmingly positive transits, yielding auspicious results in 1, 2, 3, 4, 5, 8, 9, 11, and 12\.3

| Transit House | Nature of Result | Matched House to Check for Obstruction (Vedha / Vipareeta Vedha) |
| :---- | :---- | :---- |
| **1** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 8** |
| **2** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 7** |
| **3** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 1** |
| **4** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 10** |
| **5** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 9** |
| **6** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 11** |
| **7** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 2** |
| **8** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 5** |
| **9** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 11** |
| **10** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 4** |
| **11** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 6** |
| **12** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 3** |

#### **7\. Saturn (Shani)**

Saturn perfectly mimics Mars in its transit logic, proving auspicious in houses 3, 6, and 11\.3 Note that the lunar nodes (Rahu and Ketu) follow this identical structural matrix for transits.6

| Transit House | Nature of Result | Matched House to Check for Obstruction (Vedha / Vipareeta Vedha) |
| :---- | :---- | :---- |
| **1** | Inauspicious (-) | No paired cancellation (Absolute) |
| **2** | Inauspicious (-) | No paired cancellation (Absolute) |
| **3** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 12** |
| **4** | Inauspicious (-) | No paired cancellation (Absolute) |
| **5** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 11** |
| **6** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 9** |
| **7** | Inauspicious (-) | No paired cancellation (Absolute) |
| **8** | Inauspicious (-) | No paired cancellation (Absolute) |
| **9** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 6** |
| **10** | Inauspicious (-) | No paired cancellation (Absolute) |
| **11** | Auspicious (+) | Blocked (Vedha) if any planet is in **House 5** |
| **12** | Inauspicious (-) | Canceled (Vipareeta Vedha) if any planet is in **House 3** |

### **Exception Logic for the Computational Engine**

The computational logic must implement specific exemption protocols overriding the Boolean checks established above. The paternal and filial relationships in Vedic astrology dictate that certain celestial bodies do not possess the energetic capacity to obstruct one another, requiring a hard-coded bypass.5

1. **The Solar-Saturnian By-pass:** The Sun does not cause Vedha or Vipareeta Vedha to Saturn, and Saturn does not cause Vedha to the Sun.1 If the engine detects the Sun in an auspicious house 3, and flags a check on house 9, the presence of Saturn in house 9 must return False for obstruction, allowing the Sun's beneficence to compute at full amplitude.5  
2. **The Lunar-Mercurial By-pass:** The Moon and Mercury share an identical exemption. The Moon does not obstruct Mercury, and Mercury does not obstruct the Moon.1

These exceptions ensure the algorithms do not generate false negatives during the parsing of complex planetary alignments.

## **Part B: Sudarshana Chakra — Complete Method**

The Sudarshana Chakra relies on a multi-dimensional, non-linear coordinate system. It transcends the static natal chart by evaluating time and transit impacts concurrently from three distinct cosmological pivots: the Ascendant (Janma Lagna \- body), the Moon (Chandra Lagna \- mind), and the Sun (Surya Lagna \- soul).9

### **1\. Construction of the Reference Frames**

To construct this computationally, the engine generates three concentric circular arrays, each containing 12 indices representing the zodiacal signs (Rasis).11

* **Inner Frame (Array 1):** The natal Ascendant (Janma Lagna) is locked at index 0 (House 1). All subsequent houses increment logically.  
* **Middle Frame (Array 2):** The natal Moon sign is locked at index 0 (House 1).  
* **Outer Frame (Array 3):** The natal Sun sign is locked at index 0 (House 1).11

When parsing a specific life domain—such as career (10th house)—the engine extracts a composite vector intersecting the 10th sign from the Ascendant, the 10th sign from the Moon, and the 10th sign from the Sun.11 The alignment or affliction of this vector defines the baseline karmic constraint.

### **2\. Year-by-Year Progression Rules (Sudarshana Dasha)**

The Sudarshana Dasha introduces a dynamic temporal framework operating on a continuous modulo-12 arithmetic loop.12 Each house assumes the role of a temporary Ascendant (Progressed Lagna) for specific fractal divisions of time.13

* **Macro-Progression (Mahadasha \- Yearly):** The progressed Ascendant shifts by one sign per year. Progressed\_Annual\_Lagna \= (Natal\_Lagna \+ Current\_Age\_in\_Completed\_Years) % 12\.12 Year 1 (Age 0-1) sets the 1st House as Lagna. Year 2 sets the 2nd House as Lagna. After 12 years, the cycle resets.13  
* **Micro-Progression (Antardasha \- Monthly):** The year is subdivided into 12 periods of roughly 30 days (based on 30 degrees of solar motion).12 Progressed\_Monthly\_Lagna \= (Progressed\_Annual\_Lagna \+ Month\_Index) % 12\.14  
* **Nano-Progression (Pratyantardasha \- Daily):** The month is subdivided into 12 periods of 2.5 days (60 hours).12 Progressed\_Daily\_Lagna \= (Progressed\_Monthly\_Lagna \+ Block\_Index) % 12\.12

### **3\. Overlaying Frames for Transit Analysis**

The engine dynamically rotates the base chart to align with the Progressed Lagna for a given temporal query.13 If a native is in their 5th year, the 5th house acts as the 1st house. Transit logic is then evaluated relative to this temporary anchor.13

### **4\. Scoring and Evaluation Method**

The engine utilizes specific scalar weights to evaluate the nature of planets occupying or transiting critical houses relative to the Progressed Lagna.

* **Auspicious Coordinates (+1 to \+3):** Natural benefics (Jupiter, Venus, well-associated Mercury, strong Moon) transiting the Kendras (1, 4, 7, 10), Trikonas (5, 9), or the 8th house generate positive values.11  
* **Malefic Utilities (+1 to \+3):** Natural malefics (Mars, Saturn, Sun) transiting the Upachaya houses (3, 6, 11\) yield highly positive results, indicating triumph over adversity.11  
* **Inauspicious Coordinates (-1 to \-3):** Malefics transiting Kendras or Trikonas, or houses occupied solely by lunar nodes (Rahu/Ketu), flag severe distress.11

### **5\. Combined Assessment Computation**

Because the Sudarshana framework requires analysis from three distinct anchor points, the algorithm calculates three independent sub-scores for any given transit epoch.15

Final\_Transit\_Score \= Weight\_L \* Score(Lagna) \+ Weight\_M \* Score(Moon) \+ Weight\_S \* Score(Sun)

What does it mean functionally when a transit is favorable from the Lagna but unfavorable from the Moon and Sun? The Lagna correlates to physical manifestation, the Moon to psycho-emotional perception, and the Sun to soul-level authority or vitality.11 If the engine returns a positive score for the Lagna vector but negative scores for the Lunar and Solar vectors, the prediction engine outputs a scenario where the native physically accomplishes a task (e.g., obtains a new job), but the experience is characterized by intense psychological anxiety (Moon) and a lack of true fulfillment or recognition from authority figures (Sun).15 Maximum kinetic realization of an event only occurs when all three vectors align affirmatively.

## **Part C: Sarvatobhadra Chakra (SBC) — Complete Grid Construction**

The Sarvatobhadra Chakra (SBC) is the most granular topological matrix in Vedic astrology, utilized for pinpointing daily transit vulnerabilities, horary analysis, and financial market fluctuations.16 It fuses 81 distinct spatial, temporal, and phonetic variables into an integrated map.

### **1\. The Exact 9x9 Grid Layout**

The engine initializes a two-dimensional array, SBC, comprising 81 discrete indices ranging from to. The structure consists of an outer boundary and concentric interior rings spiraling toward a single central node.17

### **2\. Mapping the 28 Nakshatras**

The outer perimeter of the array (32 cells) houses the 28 Nakshatras (including the intercalary Abhijit Nakshatra) and 4 principal corner vowels.17

* **East Edge (to):** Krittika, Rohini, Mrigashira, Ardra, Punarvasu, Pushya, Ashlesha.18  
* **South Edge (to):** Magha, Purva Phalguni, Uttara Phalguni, Hasta, Chitra, Swati, Vishakha.18  
* **West Edge (to):** Anuradha, Jyestha, Moola, Purvashadha, Uttarashadha, Abhijit, Shravana.18  
* **North Edge (to):** Dhanishta, Shatabhisha, Purvabhadrapada, Uttarabhadrapada, Revati, Ashwini, Bharani.18

### **3\. Mapping the 12 Signs (Rasis)**

The third concentric ring inward maps the 12 zodiacal signs, distributed three per side, aligning with the elemental cardinalities of the grid.17

* **East Ring Cells:** Taurus, Gemini, Cancer.18  
* **South Ring Cells:** Leo, Virgo, Libra.18  
* **West Ring Cells:** Scorpio, Sagittarius, Capricorn.18  
* **North Ring Cells:** Aquarius, Pisces, Aries.18

### **4\. Mapping the Tithis (Lunar Days)**

The fourth concentric ring handles the temporal classification of the lunar days, known as Tithis. These 30 lunar phases are grouped into five overarching categories and placed centrally.17

* **Nanda** (1st, 6th, 11th, 16th, 21st, 26th Tithi)  
* **Bhadra** (2nd, 7th, 12th, 17th, 22nd, 27th Tithi)  
* **Jaya** (3rd, 8th, 13th, 18th, 23rd, 28th Tithi).20  
* **Rikta** (4th, 9th, 14th, 19th, 24th, 29th Tithi).20  
* **Poorna** (5th, 10th, 15th, 20th, 25th, 30th Tithi).20

### **5\. Mapping the Weekdays (Vara)**

The absolute focal center of the grid—index \`\` (the 81st cell)—and its immediate adjacent cells house the assignment of the seven weekdays.17 Mars and the Sun co-rule Tuesday/Sunday; Mercury and the Moon co-rule Wednesday/Monday.

### **6\. Mapping Vowels and Consonants (Aksharas)**

The phonetic architecture allows the algorithm to map transits against a native's spoken name or a corporate entity's title.

* **Vowels (Swaras):** The 16 Sanskrit vowels are mapped primarily to the four absolute corners of the matrix (, , , ) and specific interior diagonal cells.17  
* **Consonants (Varnas):** The second concentric ring (just inside the Nakshatras) houses 20 primary consonants.17 Some consonants share cells due to linguistic substitutions; the algorithm treats pairs like 'b' and 'v', or 's' and 'sh' as occupying the same coordinate value.20

### **7\. VEDHA (Piercing) on the SBC Grid**

In the SBC environment, *Vedha* is a topological concept equivalent to an optical ray-cast. When a transiting planet occupies a Nakshatra on the grid's perimeter, it projects a vector (ray) across the matrix.17 Any celestial, phonetic, or temporal variable intersecting this vector is defined as "pierced".17

### **8\. Plotting Transits and Computing Vectors**

The engine establishes the vector trajectory based on a planetary entity's inherent kinetics 17:

* **Direct Motion (Normal Speed):** The planet casts a **Front-Vedha** (Opposite Vedha), tracing a straight vertical or horizontal line entirely across the grid to the diametrically opposed cell.17  
* **Accelerated Motion (Atichara):** Fast-moving planets cast a **Left-Vedha**, tracing a diagonal vector to the left relative to their current position.17  
* **Retrograde Motion (Vakra):** Retrograde planets cast a **Right-Vedha** (Backward Vedha), tracing a diagonal vector to the right.17  
* **Nodes and Luminaries:** The Sun, Rahu, and Ketu possess fixed vectors, casting rays simultaneously to the Front, Left, and Right.17

### **9\. Complete Rules for Piercing Execution**

When the engine executes a ray-cast over the SBC array, it extracts a list of all pierced indices. If a malefic planet casts a Left-Vedha that intersects a native's Nakshatra, the Rasi of their natal moon, the consonant matching the first letter of their name, and the Tithi of their birth, the system calculates a compounding negative score.17

**Phonetic Rule Constraint:** If the ray intersects a primary vowel, its phonetic counterpart (e.g., 'a' and 'aa', or 'i' and 'ee') is immediately flagged as pierced.20 If a benefic planet (like Jupiter) casts a ray intersecting the exact same variables, the native is insulated from harm, resulting in profound material or spiritual accumulation.17 A favorable Vedha crossing the path of an adverse Vedha mathematically nullifies the negative impact.17

## **Part D: Kota Chakra (Fortress Matrix)**

The Kota Chakra operates as a specialized topological matrix designed to compute physical survival, vulnerability to profound illness, and professional/martial crises. It algorithms conceptualize the 28-Nakshatra zodiac as a fortified citadel.24

### **1\. Constructing the Kota Chakra from a Natal Chart**

The algorithmic construction requires an ordered array of 28 elements (the 27 traditional Nakshatras plus Abhijit). The origin point (Index 1\) is dynamically assigned to the native's *Janma Nakshatra* (the natal star occupied by the Moon). This initial Nakshatra is plotted at the North-East coordinate of the fortress geometry.26

### **2\. The Concentric Structure**

The array wraps in a squared spiral, depositing specific Nakshatras into four distinct arrays representing defensive perimeters based on their distance from the Janma Nakshatra.26

1. **Stambha (Inner Pillar / Heart):** The innermost array containing Nakshatras at positions 4, 11, 18, and 25 relative to the Janma Nakshatra. This constitutes the absolute core of the entity.26  
2. **Durgantara / Madhya (Inner-Middle):** The adjacent array holding Nakshatras at positions 3, 5, 10, 12, 17, 19, 24, and 26\.26  
3. **Prakaara (Boundary Wall):** The outer defensive array holding Nakshatras at 2, 6, 9, 13, 16, 20, 23, and 27\.26  
4. **Bahya (Exterior):** The peripheral array holding Nakshatras at 1, 7, 8, 14, 15, 21, 22, and 28\. Transits here represent ambient environmental pressures outside the native's immediate vulnerability zone.26

### **3\. Inward and Outward Movement Vectors**

The danger threshold in the Kota Chakra is entirely dependent on planetary vectors—specifically, whether a transiting body is moving *into* or *out* of the Stambha.27 The geometric mapping dictates these paths.

* **Entry Path (Inward Movement):** The diagonals. Nakshatras positioned on the North-East, South-East, South-West, and North-West axes are plotted as incoming trajectories. A direct planet transiting these stars moves INWARD, increasing proximity to the core.24  
* **Exit Path (Outward Movement):** The cardinal cross. Nakshatras positioned on the East, South, West, and North axes are plotted as outgoing trajectories. A direct planet transiting these stars moves OUTWARD, decreasing danger.24  
* **The Retrograde Reversal:** A critical computational rule states that planetary retrogression reverses the vector. A retrograde planet transiting an "Exit Path" Nakshatra acts mathematically as an "Entry Path," moving inward.26 Because Rahu and Ketu are perpetually retrograde, their cardinal transits are computed as incursions.26

### **4\. Scoring Rules for Crisis Severity**

The engine calculates risk via positional intersections and planetary designations.

**Key Designations:**

* **Kota Swami (Lord of the Fort):** The planetary ruler of the native's natal Moon sign.24  
* **Kota Paala (Guard of the Fort):** The planetary ruler of the specific Pada (quarter) of the Janma Nakshatra.24

**Severity Logic:**

1. **Durga Bhanga (Fort Destruction) Yoga:** A maximum severity score is generated when transiting malefics (Saturn, Mars, Rahu, Ketu, Sun) occupy the Entry Paths (moving inward) while transiting benefics occupy the Exit Paths (fleeing the fort). This alignment indicates collapse, physical danger, or professional ruin.26  
2. **Stambha Invasion:** If a malefic successfully transits into the Stambha indices, the crisis severity compounds exponentially.25  
3. **Lord Vulnerability:** If the Kota Swami (Lord) or Kota Paala (Guard) are afflicted or transiting outward while malefics transit inward, the defense logic fails.27 Optimum defense occurs when the Kota Swami occupies the inner Stambha/Madhya and the Kota Paala patrols the Bahya (Exterior).27

## **Part E: Tajika / Varshaphala (Solar Return Annual Prediction)**

Tajika astrology—the primary framework for the *Varshaphala* (fruits of the year)—fuses Persian-Arabic geometric principles with Vedic systems. It demands precise astronomical ephemeris processing to cast solar returns and relies heavily on intersecting orbs and mathematically derived sensitive points.30

### **1\. Casting the Varshaphala Chart**

The annual chart is calculated exclusively for the precise astronomical moment the transiting Sun aligns exactly with the native's natal Sun in Degrees, Minutes, and Seconds.31 Because the sidereal solar year is 365.25 days, the timestamp of the return drifts annually. The computational engine must ping high-precision ephemerides to lock this timestamp and construct a new planetary map valid for one year.31

### **2\. The 5 Tajika Aspects and Orb Calculations**

Tajika aspects diverge from standard Parashari sightlines, utilizing a geometric array akin to Western astrology but modulated by specific planetary *Deeptamshas* (orbs of influence).30

**The Five Aspect Topologies:**

1. **Mitra (Very Friendly):** 5/9 axis (Trine, 120°).35  
2. **Gupta Mitra (Secretly Friendly):** 3/11 axis (Sextile, 60°).35  
3. **Shatru (Open Inimical):** 1/7 axis (Opposition, 180°).35  
4. **Gupta Shatru (Secretly Inimical):** 4/10 axis (Square, 90°).35  
5. **Sama (Neutral/No Aspect):** 2/12 and 6/8 axes.37

**Orb Calculations (Deeptamshas):** For an aspect to functionally operate as a Yoga, the exact distance between the planets must fall within an acceptable intersection of their respective orbs. The assigned planetary orbs are: Sun ![][image3], Moon ![][image4], Jupiter ![][image5], Saturn ![][image5], Mars ![][image6], Mercury ![][image7], Venus ![][image7].30 The engine calculates the operational limit using the formula: Orb\_Threshold \= (Orb(Planet\_A) \+ Orb(Planet\_B)) / 2\.38 An aspect is only valid if |Longitude\_A \- Longitude\_B| \<= Orb\_Threshold.

### **3\. The 16 Tajika Yogas**

The engine must evaluate the Varshaphala chart against 16 dynamic relational states (Yogas). These are primarily assessed between the *Lagnesha* (Ascendant Lord) and the *Karyesha* (Lord of the house representing the query/event).35 The computational definitions are as follows:

1. **Ithasala (Applying) Yoga:** Speed(Planet\_A) \> Speed(Planet\_B) AND Longitude(Planet\_A) \< Longitude(Planet\_B) AND Aspect \== TRUE AND Orb\_Distance \<= Orb\_Threshold. Denotes direct success and completion of objectives.35  
2. **Ishrafa (Separating) Yoga:** Speed(Planet\_A) \> Speed(Planet\_B) AND Longitude(Planet\_A) \> Longitude(Planet\_B) \+ 1\_degree. Indicates a past event, separating energy, or missed opportunity.40  
3. **Nakta Yoga:** Lagnesha and Karyesha share no aspect (Sama). A third planet, positioned longitudinally between them, is faster than both. It receives applying aspects from both, transferring the light. Indicates success through a quick intermediary.35  
4. **Yamaya Yoga:** Identical to Nakta, but the intermediary planet is *slower* than the two primary significators. Success through an intermediary, but fraught with delay.40  
5. **Manau / Manaoo Yoga:** An established Ithasala Yoga is simultaneously afflicted by an applying, inimical aspect from a powerful malefic (Mars or Saturn). The malefic "cancels" the success, denoting sudden failure or ruin.42  
6. **Kamboola Yoga:** An established Ithasala Yoga where the Moon is simultaneously forming its own Ithasala with either of the principal planets. Magnifies the event's success profoundly.41  
7. **Gairi-Kamboola Yoga:** The Moon acts as a proxy for an otherwise weak applying aspect between the primary lords.33  
8. **Ikabala Yoga:** A systemic state where all planets reside in Kendras (1, 4, 7, 10\) or Panaparas (2, 5, 8, 11). Denotes robust health, status, and general prosperity for the year.43  
9. **Induvara Yoga:** A systemic state where all planets are relegated to Apoklimas (3, 6, 9, 12). Indicates severe structural weakness, failure, and misfortune.38  
10. **Khallasara Yoga:** Lagnesha and Karyesha form no aspects with any planets and are entirely devoid of course and strength.33  
11. **Rudda Yoga:** An Ithasala (applying aspect) where the faster planet is structurally obstructed by a retrograde or debilitated planet before perfection.41  
12. **Duhphali-Kuttha Yoga:** Frustration of an applying aspect due to the slower planet being severely debilitated or heavily afflicted.41  
13. **Dutthottha-Davira Yoga:** Dual planetary applications creating highly contradictory, confusing outputs.33  
14. **Tambira Yoga:** Evaluates the perfection of an applying aspect at the extreme late degrees of a sign boundary, indicating eleventh-hour results.33  
15. **Kuttha Yoga:** An Ithasala constrained entirely within angular houses (Kendras), fortifying the structural integrity of the event.33  
16. **Durapha Yoga:** An Ithasala where both planets are deeply afflicted by debilitation or placement in Dusthanas (6, 8, 12), ensuring the event leads to destruction.33

### **4\. Muntha Calculation and Progression**

The Muntha acts as the progressed Ascendant of the year, providing the contextual focal point for the native's energies. The algorithmic determination is: Muntha\_Sign\_Index \= (Natal\_Lagna\_Sign\_Index \+ Age\_in\_completed\_years) % 12\.33 *(If the modulo returns 0, the Muntha defaults to 12, representing Pisces).*

### **5\. The Muntha Lord's Role**

The planetary ruler of the Muntha\_Sign becomes the **Muntha Lord**. The algorithm evaluates this entity's dignity in the Varshaphala chart. If the Muntha Lord occupies favorable houses (1, 2, 3, 5, 9, 10, 11), the engine predicts immense fortune, health, and expansion.33 If relegated to inauspicious houses (4, 6, 7, 8, 12\) or afflicted by malefics, the engine flags the year for extreme distress, illness, or financial loss.33

### **6\. Sahams in Tajika**

Sahams are dynamically calculated mathematical sensitive points (conceptually identical to Arabic Parts) representing specific life domains.30 While natal Arabic parts remain static, Tajika Sahams recalculate based on the geometry of the annual solar return chart.45

The universal algorithm is: Saham\_Arc \= Point\_A\_Longitude \- Point\_B\_Longitude \+ Ascendant\_Longitude.38 **Condition:** If the Ascendant's longitude does not fall sequentially between Point B and Point A, an offset of ![][image8] (1 Sign) must be appended to the calculation.38

**Key implementations:**

* **Punya Saham (Fortune/Luck):** Daytime Return \= Moon \- Sun \+ Asc; Nighttime Return \= Sun \- Moon \+ Asc.30 It dictates the baseline luck for the year.36  
* **Vivaha Saham (Marriage):** Venus \- Saturn \+ Asc (Static for day/night).30  
* **Karma Saham (Success):** Mars \- Mercury \+ Asc.38

### **7\. Year Lord (Varsheshvara) Determination**

The Year Lord is the ultimate planetary authority presiding over the Varshaphala chart.33 The engine deduces the Varsheshvara via a multi-stage filtering process against five "Office Bearers" (Pancha Adhikaris) 33:

1. **Muntha Lord:** Ruler of the calculated Muntha.33  
2. **Janma Lagna Lord:** Ruler of the natal Ascendant.33  
3. **Varsha Lagna Lord:** Ruler of the annual return Ascendant.33  
4. **Tri-Rashi Pati:** A specialized planetary ruler dependent on the sign of the Varsha Lagna and the diurnal/nocturnal state of the chart.33  
5. **Dina/Ratri Pati:** Ruler of the Sun sign (if daytime return) or Moon sign (if nighttime return).33

The engine evaluates these five candidates using the **Panchavargiya Bala**, a robust 5-tier point system computing Kshetra (Sign), Uchcha (Exaltation), Hudda, Drekkana, and Navamsha strengths to generate an absolute numerical score (Max 30).30

**Final Selection Logic:** The candidate with the highest Panchavargiya Bala score is designated the Year Lord, *provided* it casts a valid Tajika aspect upon the Varsha Lagna.33 If the strongest candidate lacks this aspect, the algorithm selects the next highest scoring candidate that meets the visual criteria.33

#### **Works cited**

1. Rashi Gochar Vedha (Transit based Planetary Obstruction) | ASHTAKVARGA JYOTI, accessed on March 2, 2026, [https://ashtakvargajyoti.wordpress.com/2015/01/30/rashi-gochar-vedha-transit-based-planetary-obstruction/](https://ashtakvargajyoti.wordpress.com/2015/01/30/rashi-gochar-vedha-transit-based-planetary-obstruction/)  
2. Understanding Vedha in Astrology | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/791154858/Transits-Graha-Vedha-Vipr-Vedha](https://www.scribd.com/document/791154858/Transits-Graha-Vedha-Vipr-Vedha)  
3. Planetary Transits (Gochaara) \- Concept & Significance | PDF | Astrological Sign | Zodiac \- Scribd, accessed on March 2, 2026, [https://es.scribd.com/doc/71784738/Planetary-Transits-Gochaara-Concept-Significance](https://es.scribd.com/doc/71784738/Planetary-Transits-Gochaara-Concept-Significance)  
4. Rasi Gochara Vedha \- Learning Astrology \- Wikidot, accessed on March 2, 2026, [http://astroveda.wikidot.com/rasi-gochara-vedha](http://astroveda.wikidot.com/rasi-gochara-vedha)  
5. Special Predictive Notes With Reference to Transit (Gochar) \- Tag-to-Adawal, accessed on March 2, 2026, [http://tagtoadawal.blogspot.com/2011/03/special-predictive-notes-with-reference.html](http://tagtoadawal.blogspot.com/2011/03/special-predictive-notes-with-reference.html)  
6. Transit Influences by Dr. P. S. Sastri \- Saptarishis Astrology, accessed on March 2, 2026, [https://saptarishisastrology.com/transit-influences-by-dr-p-s-sastri/](https://saptarishisastrology.com/transit-influences-by-dr-p-s-sastri/)  
7. Understanding Gochara in Astrology | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/doc/71784738/Planetary-Transits-Gochaara-Concept-Significance](https://www.scribd.com/doc/71784738/Planetary-Transits-Gochaara-Concept-Significance)  
8. GOCARA- RESULTS OF TRANSITS FROM THE MOON \- Vedic-Astrology.net, accessed on March 2, 2026, [https://www.vedic-astrology.net/FreeClasses/Gocara.pdf](https://www.vedic-astrology.net/FreeClasses/Gocara.pdf)  
9. The Sudarshan Chakra--Ultimate Predictive tool. \#astrology \#vastu \#hinsub \- YouTube, accessed on March 2, 2026, [https://www.youtube.com/watch?v=8J93entomCI](https://www.youtube.com/watch?v=8J93entomCI)  
10. Secrets of Sudarshana Chakra Dasa: Part 2 | by Varaha Mihira | Thoughts on Jyotish, accessed on March 2, 2026, [https://medium.com/thoughts-on-jyotish/secrets-of-sudarshana-chakra-dasa-part-2-84214579b0d7](https://medium.com/thoughts-on-jyotish/secrets-of-sudarshana-chakra-dasa-part-2-84214579b0d7)  
11. Sudarsana Chakra Dasa \- Learning Astrology \- Wikidot, accessed on March 2, 2026, [http://astroveda.wikidot.com/sudarsana-chakra-dasa](http://astroveda.wikidot.com/sudarsana-chakra-dasa)  
12. Sudarshan Chakra Dasa \- A New Approach Calculation And Applicability By Sanjeev Ranjan Mishra | Saptarishis Astrology, accessed on March 2, 2026, [https://saptarishisshop.com/sudarshan-chakra-dasa-a-new-approach-calculation-and-applicability-by-sanjeev-ranjan-mishra/](https://saptarishisshop.com/sudarshan-chakra-dasa-a-new-approach-calculation-and-applicability-by-sanjeev-ranjan-mishra/)  
13. Sudarshan Chakra Part 2: Predicting Time Using the 12-Year Dasha Cycle \- Reddit, accessed on March 2, 2026, [https://www.reddit.com/r/Advancedastrology/comments/1lu4uhs/sudarshan\_chakra\_part\_2\_predicting\_time\_using\_the/](https://www.reddit.com/r/Advancedastrology/comments/1lu4uhs/sudarshan_chakra_part_2_predicting_time_using_the/)  
14. Secrets of Sudarshana Chakra Dasa | PDF | Hindu Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/464171531/Secrets-of-Sudarshana-Chakra-Dasa](https://www.scribd.com/document/464171531/Secrets-of-Sudarshana-Chakra-Dasa)  
15. Secrets of Sudarshana Chakra Dasa: Part 3: The Tripod of Life | by Varaha Mihira \- Medium, accessed on March 2, 2026, [https://medium.com/thoughts-on-jyotish/secrets-of-sudarshana-chakra-dasa-part-3-the-tripod-of-life-28b4f097538e](https://medium.com/thoughts-on-jyotish/secrets-of-sudarshana-chakra-dasa-part-3-the-tripod-of-life-28b4f097538e)  
16. Introduction of Sarvatobhadra Chakra | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/847025144/Introduction-of-Sarvatobhadra-Chakra](https://www.scribd.com/document/847025144/Introduction-of-Sarvatobhadra-Chakra)  
17. The Construction methodology of Sarvatobhadra Chakra, accessed on March 2, 2026, [https://howisyourdaytoday.com/articles/Sarvatobhadrachakra/Sarvatobhadra-chakra-construction.htm](https://howisyourdaytoday.com/articles/Sarvatobhadrachakra/Sarvatobhadra-chakra-construction.htm)  
18. Sarvatobhadra Chakra \- Wikipedia, accessed on March 2, 2026, [https://en.wikipedia.org/wiki/Sarvatobhadra\_Chakra](https://en.wikipedia.org/wiki/Sarvatobhadra_Chakra)  
19. Understanding Sarvatobhadra Chakra | PDF | Religion & Spirituality \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/doc/145866881/Sarvatobhadra](https://www.scribd.com/doc/145866881/Sarvatobhadra)  
20. Sarvatobhadra Chakra \- Learning Astrology \- Wikidot, accessed on March 2, 2026, [http://astroveda.wikidot.com/sarvatobhadra-chakra](http://astroveda.wikidot.com/sarvatobhadra-chakra)  
21. Sarvato Bhadra Chakra Explained | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/517568399/Varaha-Mihira-s-Sarvato-Bhadra](https://www.scribd.com/document/517568399/Varaha-Mihira-s-Sarvato-Bhadra)  
22. Sarvatobhadra Chakra. This chart contains 9\*9 \= 81 boxes… | by Varaha Mihira \- Medium, accessed on March 2, 2026, [https://srivarahamihira.medium.com/sarvatobhadra-chakra-8d3ecc2ba9ca](https://srivarahamihira.medium.com/sarvatobhadra-chakra-8d3ecc2ba9ca)  
23. Sarvatobhadra Cakra | Saptarishis Astrology, accessed on March 2, 2026, [https://saptarishisshop.com/sarvatobhadra-cakra/](https://saptarishisshop.com/sarvatobhadra-cakra/)  
24. Kota Chakra \- Jyothishi | PDF | Hindu Astrology | Astronomy \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/516731732/Kota-Chakra-Jyothishi](https://www.scribd.com/document/516731732/Kota-Chakra-Jyothishi)  
25. Kota Chakra | The Art of Vedic Astrology, accessed on March 2, 2026, [https://www.theartofvedicastrology.com/?page\_id=389](https://www.theartofvedicastrology.com/?page_id=389)  
26. Kota Chakra | JYOTHISHI, accessed on March 2, 2026, [https://vijayalur.com/2011/06/02/kota-chakra/](https://vijayalur.com/2011/06/02/kota-chakra/)  
27. Kota Chakraand Professional Setbackby MImran BW | PDF | Philosophy | History \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/doc/123553048/KotaChakraandProfessionalSetbackbyMImranBW](https://www.scribd.com/doc/123553048/KotaChakraandProfessionalSetbackbyMImranBW)  
28. Kota Chakra Lesson 1 | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/891799433/Kota-Chakra-Lesson-1](https://www.scribd.com/document/891799433/Kota-Chakra-Lesson-1)  
29. KOTA CHAKRA | sreenivasdesabhatla \- WordPress.com, accessed on March 2, 2026, [https://sreenivasdesabhatla.wordpress.com/2017/09/06/kota-chakra/](https://sreenivasdesabhatla.wordpress.com/2017/09/06/kota-chakra/)  
30. Varshphal Tajik Astrology Basics: Complete Guide \- AstroSight, accessed on March 2, 2026, [https://astrosight.ai/transits/varshphal-tajik-astrology-basics](https://astrosight.ai/transits/varshphal-tajik-astrology-basics)  
31. Varshphal Annual Horoscope: Complete Analysis Guide \- AstroSight, accessed on March 2, 2026, [https://astrosight.ai/transits/varshphal-annual-horoscope-analysis](https://astrosight.ai/transits/varshphal-annual-horoscope-analysis)  
32. How to Read Your Varshaphal (Solar Return) \- Cosmic Insights, accessed on March 2, 2026, [https://blog.cosmicinsights.net/how-to-read-your-varshaphal-solar-return/](https://blog.cosmicinsights.net/how-to-read-your-varshaphal-solar-return/)  
33. Introduction to Varshapal / Tajik Astrology | JYOTHISHI, accessed on March 2, 2026, [https://vijayalur.com/2016/01/21/introduction-to-varshapal-tajik-astrology/](https://vijayalur.com/2016/01/21/introduction-to-varshapal-tajik-astrology/)  
34. Tajika Astrology: Key Concepts and Methods | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/presentation/682193103/1-Tajika-Astrology-Class](https://www.scribd.com/presentation/682193103/1-Tajika-Astrology-Class)  
35. Varshaphala Deck | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/865166174/Varshaphala-Deck](https://www.scribd.com/document/865166174/Varshaphala-Deck)  
36. A Brief Note On Varshaphala And Sahams By Anjaneyulu Marella | Saptarishis Astrology, accessed on March 2, 2026, [https://saptarishisshop.com/a-brief-note-on-varshaphala-and-sahams-by-anjaneyulu-marella/](https://saptarishisshop.com/a-brief-note-on-varshaphala-and-sahams-by-anjaneyulu-marella/)  
37. which taijika yogas are important – Varshaphala – Solar Returns \- Astrology-Videos.com, accessed on March 2, 2026, [https://astrology-videos.com/forum/varshaphala/which-taijika-yogas-are-important](https://astrology-videos.com/forum/varshaphala/which-taijika-yogas-are-important)  
38. ANNUAL HOROSCOPE (Varshaphala or Tajak) Effective Predictive Techniques BY MS Mehta \- WordPress.com, accessed on March 2, 2026, [https://astrofoxx.files.wordpress.com/2018/11/jyotish\_annual-horoscope\_varshaphala\_m-s-mehta.pdf](https://astrofoxx.files.wordpress.com/2018/11/jyotish_annual-horoscope_varshaphala_m-s-mehta.pdf)  
39. Tajik Yogas in Prasna Shastra \- Medium, accessed on March 2, 2026, [https://medium.com/prasna-jyotish/tajik-yogas-in-prasna-shastra-97e3afec652c](https://medium.com/prasna-jyotish/tajik-yogas-in-prasna-shastra-97e3afec652c)  
40. Nakta Yoga Explained: Light Transfer in Astrology \- AstroSight, accessed on March 2, 2026, [https://astrosight.ai/yogas/nakta-yoga-explained](https://astrosight.ai/yogas/nakta-yoga-explained)  
41. A Textbook of Varshaphala EN \- K.S. CHARAK\_Page\_001\_Image\_0001\_1.png, accessed on March 2, 2026, [https://storage.yandexcloud.net/j108/library/l2nnkwz1/K.S.\_Charak\_-\_A\_Textbook\_of\_Varshaphala.pdf](https://storage.yandexcloud.net/j108/library/l2nnkwz1/K.S._Charak_-_A_Textbook_of_Varshaphala.pdf)  
42. Encyclopedia of Vedic Astrology: Tajik Shastra and Annual Horoscopy: Tajika Yogas, Chapter IV, Part \- Tag-to-Adawal, accessed on March 2, 2026, [http://tagtoadawal.blogspot.com/2013/01/encyclopedia-of-vedic-astrology-tajik\_9928.html](http://tagtoadawal.blogspot.com/2013/01/encyclopedia-of-vedic-astrology-tajik_9928.html)  
43. 5 \- Tajika Astrology Class Tajika Yogas | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/682193090/5-Tajika-astrology-Class-Tajika-Yogas](https://www.scribd.com/document/682193090/5-Tajika-astrology-Class-Tajika-Yogas)  
44. Encyclopedia of Vedic Astrology: Tajik Shastra and Annual Horoscopy:Tajika Yogas, Chapter IV, Part \- 2 \- Tag-to-Adawal, accessed on March 2, 2026, [http://tagtoadawal.blogspot.com/2013/01/encyclopedia-of-vedic-astrology-tajika\_22.html](http://tagtoadawal.blogspot.com/2013/01/encyclopedia-of-vedic-astrology-tajika_22.html)  
45. Varshaphal and Muntha | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/513676134/Varshaphal-and-Muntha](https://www.scribd.com/document/513676134/Varshaphal-and-Muntha)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD4AAAAZCAYAAABpaJ3KAAACm0lEQVR4Xu2XzatNYRSHl0KSKIpc4TBQYuBrcCe6SIhSyFQpA0mUTGSidAfuTdIlH8VFEYnCiMgISRgoUkRSBob+AH5P692d17r73Khz1Nn2U7/ae6199t7r6333MaupqfmfWCk9kZ4HbU3+eyW+I8lXCW5LP6VGsBfg+xGNVeCNeXATokNMNPe9io4qQGDfozGx1tx/KDq6nUk2ekUJmDbfEB3dDgER+P7oMJ95EnLTPEGVgooS+GiqXJs3zCt62coXtus2crWfIm2T9ma2TjNWOmv+Lusz+1vzd/9raHPmt6zNgaTwsNjmO6TeYOskC8wTfVKanNnvSxuz8z+G2Y0VzcEX9+9p0iPzKvwrGDWCbxsERXBlNMx9JCeHamOfI42Ths3HZJ70UJqarjuV7MvNK3VFWiGtkb6ka2Cz9M78XmhL5htjHjD37Ul+GJDmm391Tk82rn1tPobrpE/JXgoBtNq/i9U+LmwnpJfZ+XtpsfRYupXZeTmSQfDnzRMAS6WPxUXim7QvHfPycdskcD6wcnaa3/euNVuf321Px1fN7/sbs23kqo0uSOOliyW+Z9JMfiw+WHNh4+EETiU/S0PmFcvbMgZKEhgVIGFPzZPEolVUL2e3+TMjB6WF6bjPWhewbfAAHgQN86yTFIJh/iOMxtfs/IXUn46XSEczXxmMCS2dQ5V5brETUQgK1FF4cVZ0Oof2LuaOf25z0zEvdNh8ASQhdEJBkSASwnWn03UwS1qdjgvYWeK4ESh21odd5iOVj98i6UZ23hZoPSpAAHsy+zHpgXRGumM+r8Bemy9YzOuwNRPGlnRJumY+bhE6bFOwLTNP9HFrzjj/Kc6Zj82gNCPZuw5amblv9XFVWdhqD0irgr2mpqY1vwAvVJWVF9VsiwAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADQAAAAZCAYAAAB+Sg0DAAACPUlEQVR4Xu2Wz4tOURjHvzIkjR+lyEzyUqz9A1JSGDYmyk5SslA2NspCRJKNpCZFrExNo4ydLGYzIWFhpZSNslA2/gC+n55zeu973HkX5k7dqfupb/ec89x73+c853me+0odHR1Nst9asN4Vmkz2lzW2a8nWap5bf6xesZ7BdqRcbDOfFU6vKw1mvYZvtpXg8M9yMXFIYV8xjCoc/lgaEles3+Vim6E22NCl0qBIMzY6U6y3Gk6ADQ0T96wIeooTeKr6hjCt5WkIm6zv1kVrtTWuaExLhnSjPurSDdgsG6LOmoYmdCCNCSafjiVDbQw7AWzL0RA2azAr2Nixvvn/wVmcrqOnsJUN4Y61W/EPY6v1SIPveG3dT+NT1kgav7IuW3utD+qfDt85UnvKWmXdtLYkG/MLimdIzV+KQCwKjiz2/cndr2wIZxWRnbM2WrusN8k2Zs2mdTiocIo5gcmpe09xL/QUqZ2fIf23pfFx61saw1fVlMcO/dvFEJFeaz2usWWHMxTzvjTebt1SP9KczlX1o8om2Axz4FptAAQsz3da7ys2MuhGZY4tB6IxsuPUAXCSnFp2PKdLhmi/tTak+UkNZgUplBvCCetHxUYwc22VddcY2fFcG+cqtjOKKAM/TM1wfZCuQNrw/F3FvWyOTQIb50SuK1L5i6LWSEeCeFiRxo3D/7uHivRcU1nHaYqfxvFCUQNAmj9R3H9akWLnFfX1ydqT7rttzVsTaU5DoPk8s44q3sk7Ojo6Our5C34fgXbs4oMgAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAXCAYAAAD6FjQuAAABJElEQVR4XmNgGAXDBagBMSO6IBCIATEzmpgIEHMg8RWBuB+IDwBxMpI4HBgDcSIQnwfi/0C8Goh5UFRAwAkGiDwy9mNAOAxkqSaUDQPRaHyGBiA+CcQFQLyDgTjLPgPxMlRpBnEGTH0taHw4ACkEWYTPMnd0QSRAlM9ggFLLQGA5EGsDMSsDxCI+VGkEIMayUCB+zgAJyiMM2BMSUYAYy54CsRAQCwLxSiAuYYD4gmRAyDKQBcgG8zJAfLgJSYxoQMgyYQbMfAZLnSQDfJaJMkAMnY0mThPLQKUKKG91IInBgnEvkhjRAJ9loDxUzoCa+gwYIA6IRxIjCHIYMIshGEbOVx5AfAeIpwPxIyD+wIBaLlIdgIKuC4jjgFgGTW4UjALyAQDmbELsdFWysgAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAXCAYAAAD6FjQuAAABKUlEQVR4XmNgGAXDBagBMSO6IBLQBGJRIGZGlwACRSDuB+IDQJyMKgUBxkCcCMTngfg/EK8GYh4UFRCwB4jnMUAs6QLiz0C8GIj5oPIcDBCHIINoND5DAxCfBOICIN7BgN0yFiBewYAwGOTzJgaI48qhYuIMmPpa0PhwAFIIsgibZQYMEIOfIIlxQcVAPgQBonwGA/gsk2eAGHwNTRwkBsIwsByItYGYlQFiESwkMAA+y7ABBQaIRfvRxIkCpFqWwwAJwnh0CWIAKZaBEgvIV9zoEsQCYi3LhmJs+YxoQKxldxgQmR6UJayR5IgGhCwzAuLTaGIWQHwETYwoQMiyg0B8jAFSeoDwdCC+CsRbkRURAqBUBcsv6NgdqgaWqbHhZqiaUTAKhggAABTsQes8/uhlAAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAXCAYAAADtNKTnAAAA7ElEQVR4XmNgGAWEACsQKwGxEBAzosmB+M5AfBKI10H5KIAPiFcAcSoQMwOxNhAfBWIjJDWTgZgDiT8NiFWR+AxdQPwfiFmQxJyAeBkSPweJDeO7IwuADABhZMCLJobXJSDbsRnCAxUTgPKzgLgNygaFWToDUriAGPgMMUATxwmwGSIFFSPakGwg/syA8DMoqqczkGgICIC8tYQBkg6SGCD+Rg4TsoAYA8QQjESFC2xigGgAJToYCIGKEw1OMEAMAdkOAiCvbAFiB5gCYgAoeV9jgAQmCF8H4gAUFUQCkO2g5N8OxNxocqNgIAAAx70p9PGajD4AAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAXCAYAAADtNKTnAAAA/UlEQVR4XmNgGAWEAAcQKwOxEBAzosmB+M5AfBKI10H5KIAPiFcAsTqUzwvE7UCcDVfBwDCZAWIJDEwDYlUkPkM8EB9GFgACViC+hMTPQWLD+O7IAieAeDuyABS8RmITdMlWIP4PxILIgkDwAImdBcRtUDYozNIZ0MJFFogPMkAM+gzEoQwQr4DCiiSgxgAxBIYnokoTBiAbZwKxIxAbMyAMArmOaAAKwHI0MW0GiEEKaOI4wRMgtkAXBIKzQGyILogL4DIEFK3y6IK4AMg7/eiCDBCXYCRvXIAbiJuB+BEQzwPiPUD8AYjFkRURC+KAuAuIS4FYBU1uFNAbAABguinVSt7naQAAAABJRU5ErkJggg==>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAXCAYAAADtNKTnAAAAvElEQVR4XmNgGAW4gAsQp6MLogFGIHYG4pNAvA7KRwELgfg/DrwLiIWAeDIQc8A0AME0IFZF4jNsZcDUDMM+UDU5UBoGQHx3ZIGNQCyMLAAErEC8AolP0CUgAS5kAQaIC/SQ+FlA3AZlg7wHCkOMcEEG84F4BrogqeAuEJuiC5IC4oG4El2QFACy/QEQG6KJkwRA0QaKVh10CVLAXgaIIeLoEqSAEwxUMOQ0A8QQ9IRHEnAA4mZ0wVEwQAAAf3ok2Q15r40AAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAXCAYAAAD6FjQuAAABdUlEQVR4Xu2UvytGYRTHj1DycxQxKIssUsrG5h+wKQMGYRKDMskgJRkNZqEMMipMdlZKUgaL8gfw/XbOcZ97uuXqZVD3W5/ee85z7jnd857niFT67+oAnaA1HgQxpgc0xgOoD+yCKzCbP1INg1vQZvYUeAGLoM6DzH4HLaAJrIItyYrSN2DPLubK6UA0OYMpftkJuAdDHmT2ZWIznu+Nm13Ulc1gyxn4AGOJb89802Z3mT3/FaGi786eS30Z+7wmWcvYzlPwCEbMNyqaeMJs17Noa12HYFC0tSzUnpwV6kg0MdviWjJfLMbW0v9jbYi29AEshLNfL+bqBdeSn7Q/K0ZxWJjkxuxJs2suNgeWg48jzyRsKeXFYzEOSOlizaLBJL0jTJp+GceaNqc2FX38n0uLLzwF34r5OTSuV9HL7moQjZlJfN+qH5yDC7AjuhXeJFtfLt6ZfXBsv4zpzkWUVL3ortsW3RpctEXixV830lVWqVJt+gTLWFFJCaQISQAAAABJRU5ErkJggg==>