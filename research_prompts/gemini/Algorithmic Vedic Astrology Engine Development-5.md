# **Algorithmic Blueprint for an Advanced Vedic Astrology Prediction Engine: Horary, Kalachakra, Medical, and Conditional Dasha Systems**

The development of an algorithmic Vedic astrology engine targeting a prediction accuracy threshold exceeding ninety percent necessitates a rigorous, multi-layered computational architecture. Standard Vimshottari and Parashari principles, while foundational, are computationally insufficient for micro-level event timing and the resolution of highly specific temporal queries. To cross the advanced accuracy paradigm, the computational engine must integrate dynamic horary (Prashna) calculations, complex multi-tier non-linear Dasha systems (such as the Kalachakra mechanism and conditional planetary periods), and specialized medical symptomology matrices based on the anatomical zodiac. This comprehensive report details the programmatic logic, mathematical formulas, and deterministic rulesets required to map astronomical phenomena to actionable predictive outputs.

## **Branch A: Prashna (Horary Astrology) Algorithmic Logic**

Prashna Shastra represents the astrological science of generating predictive models based on the exact temporal and spatial moment a specific query is posed. Unlike natal astrology, which is static and relies on the birth epoch, Prashna is highly dynamic and extremely sensitive to micro-time variations.1 The predictive engine must implement dual processing pipelines: the Krishnamurti Paddhati (KP) Horary method for pinpoint binary (Yes/No) resolution, and the classical Prashna Marga indices for qualitative context.

### **Section A1: Prashna Chart Construction and Primary Significators**

The initialization of a Prashna chart fundamentally differs between the Classical and KP computational frameworks. For the Classical Prashna construction, the Prashna Lagna (Ascendant) is calculated using the exact geographic coordinates (latitude and longitude) of the astrologer or system server, combined with the precise timestamp of the query.2 This generates a real-time snapshot of the ecliptic. Conversely, the KP Prashna construction relies on a seed number provided by the querent, constrained between the integers 1 and 249\. This integer maps directly to one of the 249 stellar sub-divisions of the zodiac, instantly fixing the Ascendant degree regardless of the geographic location.3 The planetary positions are then calculated for the exact time of the query using the KP Ayanamsa and the Placidus house system.3

In the algorithmic execution of Prashna, identifying the correct anatomical house of the query is paramount. The querent is invariably assigned to the 1st house (Lagna), representing their physical self and personal agency.3 The quesited (the object of the query) varies strictly based on the ontological category of the question.

In the KP algorithm, the ultimate deterministic variable is the Sub-Lord of the Prashna Lagna (1st Cusp) or the specific house queried. A planet transitions into a significator state if it occupies a house, rules a house, or sits in the nakshatra (star) of a planet occupying or ruling that house.5 The algorithm must extract the Sub-Lord of the relevant cusp, identify the Star-Lord of this Sub-Lord, and evaluate the houses signified by this Star-Lord.6 If the Star-Lord signifies the positive house arrays relevant to the query, the event is promised; if it signifies detrimental houses, the event is denied.5

### **Section A2: Prashna Significators and House Connection Rules**

To compute probabilistic outcomes, the engine must execute boolean intersection checks against specific house arrays.3 The exact house connection rules for various event types dictate whether the algorithm returns a positive or negative flag.

| Query Type | Primary Cusp | Positive Array (YES) | Negative Array (NO) |
| :---- | :---- | :---- | :---- |
| **Marriage** | 7th | 2, 7, 11 | 1, 6, 10, 12 |
| **Job or Promotion** | 10th | 2, 6, 10, 11 | 1, 5, 9, 12 |
| **Health Recovery** | 6th | 1, 5, 11 | 6, 8, 12 |
| **Financial Gain** | 2nd | 2, 6, 11 | 5, 8, 12 |
| **Foreign Travel** | 9th | 3, 9, 12 | 2, 4, 11 |
| **Legal Victory** | 6th | 6, 11 | 7, 12 |

For computational execution regarding a Marriage query, the engine identifies the 7th Cusp Sub-Lord. If the Star-Lord of this Sub-Lord acts as a significator for houses 2, 7, or 11, the system computes a TRUE state for marriage. However, if it signifies houses 1, 6, 10, or 12, the system computes a FALSE state, indicating denial, separation, or divorce.8

### **Section A3: Ruling Planets in Prashna and Timing Algorithms**

Ruling Planets (RP) serve as the ultimate verification matrix in KP astrology. If the computational outcome of the Sub-Lord aligns with the Ruling Planets active at the moment of judgment, the probability of the event materializing approaches absolute certainty.4

The engine must extract the planetary lords active at the exact moment of computation to build the RP array. This array consists of the Ascendant Star Lord, the Ascendant Sign Lord, the Moon Star Lord, the Moon Sign Lord, and the Day Lord (where Sunday maps to the Sun, Monday to the Moon, and so forth).4

The primary confirmation rule requires that the significators of the target event geometrically intersect with the RP array. Specifically, if the 1st Cusp Sub-Lord and the Moon's Star-Lord are found within the operational RP array, the chart is deemed valid and the event is definitively promised.11 Event timing is subsequently derived by computing the Vimshottari Dasha sequence originating from the exact longitude of the Moon at the time of the Prashna.12

### **Section A4: Classical Prashna Indicators and Specialized Rules**

To complement the granular KP logic, the engine must overlay classical algorithms derived from the *Prashna Marga* and *Prashna Tantra*.

The Prashna Panchaka introduces a mathematical check for operational viability. The algorithm calculates the sum of the Tithi, Nakshatra, Weekday, and Ascendant Sign values, applying a modulo 9 operation.14

![][image1]

If the resulting remainder is 1 (Mrityu or Danger), 2 (Agni or Fire), 4 (Raja or Authority clash), 6 (Chora or Theft), or 8 (Roga or Disease), the timing is mathematically flawed and indicates severe operational obstacles.14

The Ithasala Yoga represents a vector-based aspectual rule. A positive outcome is generated if a faster-moving planetary body (representing the querent) is applying to an aspect with a slower-moving planetary body (representing the quesited) while remaining within their respective orbs of influence.15 Conversely, separating aspects, termed Easarapha, indicate historical events and yield a negative flag for future materialization.16 The Moon's applying aspect acts as the primary indicator; aspects the Moon will complete before leaving its current sign describe imminent future events, while separating aspects describe the context of the past.17

Specialized algorithmic triggers must be programmed for specific query archetypes. For queries regarding the return of a missing person or traveller, the engine checks the 2nd, 3rd, and 5th houses from the Prashna Lagna. If benefic planets occupy these vectors, or if the Moon remains un-afflicted in the 7th house, the system returns a status indicating a rapid and safe return.18 If malefic planets occupy the 7th or 8th house, the individual is flagged as being in confinement or facing restrictions.18 To ascertain if a missing person is deceased, the algorithm checks if the Lagna is a Prishthodaya sign heavily aspected by malefics, combined with an afflicted Mercury residing in the 6th house.18

For pregnancy confirmation queries, the *Prashna Marga* provides a precise formula. The timing of successful sexual union resulting in conception is computed by synthesizing the longitudes of the Lagna, Sun, Moon, and Gulika.21 The specific month of conception aligns with the transit of the Sun and Moon over the sum of their natal longitudes, while the year aligns with Jupiter transiting the sum of the longitudes of the Lagna, Moon, and Jupiter.21 Furthermore, surgical success is evaluated through the 8th house; an un-afflicted 8th house with beneficial aspects from Jupiter or Venus indicates a successful surgical intervention and recovery without chronic complications.22

## **Branch B: Kalachakra Dasha Computation and Prediction Rules**

Described by Maharishi Parashara as the supreme Dasha system (*Maanyaa sarvadashaasu yaa*), the Kalachakra Dasha requires the implementation of a highly complex non-linear sequence array based on Navamsa progression.23 It relies on a structural division of Nakshatras into Savya (Clockwise) and Apasavya (Counter-Clockwise) groups.24

### **Section B1: Complete Kalachakra Grid Construction**

The computational engine must map the exact Nakshatra Pada of the natal Moon to determine the sequence direction and extract the correct dimensional array.26 The Savya and Apasavya classifications are structurally mapped across six distinct groups.

| Classification | Nakshatra Grouping | Directional Flow |
| :---- | :---- | :---- |
| **Savya Group 1** | Aswini, Punarvasu, Hasta, Moola, P.Bhadra | Clockwise |
| **Savya Group 2** | Bharani, Pushya, Chitra, P.Ashadha, U.Bhadra | Clockwise |
| **Savya Group 3** | Krittika, Aslesha, Swati, U.Ashadha, Revati | Clockwise |
| **Apasavya Group 4** | Rohini, Magha, Visakha, Sravana | Counter-Clockwise |
| **Apasavya Group 5** | Mrigasira, P.Phalguni, Anuradha, Dhanishta | Counter-Clockwise |
| **Apasavya Group 6** | Ardra, U.Phalguni, Jyeshta, Satabhisha | Counter-Clockwise |
| 27 |  |  |

Unlike the Vimshottari system, the Kalachakra framework assigns unique temporal durations to each zodiacal sign rather than to the planets. The engine must strictly assign the following lifespans in years to the signs: Aries (7), Taurus (16), Gemini (9), Cancer (21), Leo (5), Virgo (9), Libra (16), Scorpio (7), Sagittarius (10), Capricorn (4), Aquarius (4), and Pisces (10).25

The operational sequence generated by the algorithm varies radically depending on the specific Pada (quarter) of the operational Nakshatra. The engine must query the following comprehensive arrays to determine the sign sequence, the maximum lifespan (Paramayus), and the specific Deha (Body) and Jeeva (Soul) signs.27

**Savya Chakra Arrays (Groups 1 and 3):**

* **Pada 1:** Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius. (Paramayus: 100\. Deha: Aries. Jeeva: Sagittarius).  
* **Pada 2:** Capricorn, Aquarius, Pisces, Scorpio, Libra, Virgo, Cancer, Leo, Gemini. (Paramayus: 85\. Deha: Taurus. Jeeva: Cancer).  
* **Pada 3:** Taurus, Aries, Pisces, Aquarius, Capricorn, Sagittarius, Aries, Taurus, Gemini. (Paramayus: 83\. Deha: Taurus. Jeeva: Gemini).  
* **Pada 4:** Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces. (Paramayus: 86\. Deha: Cancer. Jeeva: Pisces).  
  27

**Savya Chakra Arrays (Group 2):**

* **Pada 1:** Scorpio, Libra, Virgo, Cancer, Leo, Gemini, Taurus, Aries, Pisces. (Paramayus: 100\. Deha: Scorpio. Jeeva: Pisces).  
* **Pada 2:** Aquarius, Capricorn, Sagittarius, Aries, Taurus, Gemini, Cancer, Leo, Virgo. (Paramayus: 85\. Deha: Aquarius. Jeeva: Virgo).  
* **Pada 3:** Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces, Scorpio, Libra, Virgo. (Paramayus: 83\. Deha: Libra. Jeeva: Virgo).  
* **Pada 4:** Cancer, Leo, Gemini, Taurus, Aries, Pisces, Aquarius, Capricorn, Sagittarius. (Paramayus: 86\. Deha: Cancer. Jeeva: Sagittarius).  
  27

**Apasavya Chakra Arrays (Groups 4 and 6):**

* **Pada 1:** Sagittarius, Capricorn, Aquarius, Pisces, Aries, Taurus, Gemini, Leo, Cancer. (Paramayus: 86\. Deha: Sagittarius. Jeeva: Cancer).  
* **Pada 2:** Virgo, Libra, Scorpio, Pisces, Aquarius, Capricorn, Sagittarius, Scorpio, Libra. (Paramayus: 83\. Deha: Virgo. Jeeva: Libra).  
* **Pada 3:** Virgo, Leo, Cancer, Gemini, Taurus, Aries, Sagittarius, Capricorn, Aquarius. (Paramayus: 85\. Deha: Virgo. Jeeva: Aquarius).  
* **Pada 4:** Pisces, Aries, Taurus, Gemini, Leo, Cancer, Virgo, Libra, Scorpio. (Paramayus: 100\. Deha: Pisces. Jeeva: Scorpio).  
  27

**Apasavya Chakra Arrays (Group 5):**

* **Pada 1:** Pisces, Aquarius, Capricorn, Sagittarius, Scorpio, Libra, Virgo, Leo, Cancer. (Paramayus: 86\. Deha: Pisces. Jeeva: Cancer).  
* **Pada 2:** Gemini, Taurus, Aries, Sagittarius, Capricorn, Aquarius, Pisces, Aries, Taurus. (Paramayus: 83\. Deha: Gemini. Jeeva: Taurus).  
* **Pada 3:** Gemini, Leo, Cancer, Virgo, Libra, Scorpio, Pisces, Aquarius, Capricorn. (Paramayus: 85\. Deha: Gemini. Jeeva: Capricorn).  
* **Pada 4:** Sagittarius, Scorpio, Libra, Virgo, Leo, Cancer, Gemini, Taurus, Aries. (Paramayus: 100\. Deha: Sagittarius. Jeeva: Aries).  
  27

The sub-periods (Antardashas) within a primary Kalachakra Mahadasha are calculated proportionately based on the fixed sign durations. The mathematical formula governing this subdivision dictates that the duration of the Antardasha is equal to the product of the Mahadasha sign years and the Sub-Lord sign years, divided by the total Paramayus of the active Pada.27

### **Section B2: Kalachakra Prediction Rules and Critical Transitions**

The predictive efficacy of the Kalachakra system hinges on the accurate tagging of the Deha (Body) and Jeeva (Soul) signs for every computed chart. For Savya cycles, the sequence inherently begins with the Deha sign and terminates with the Jeeva sign.26 Conversely, for Apasavya cycles, the sequence begins with the Jeeva sign and terminates with the Deha sign.26

When the operational Kalachakra Dasha algorithm traverses the Deha sign, the native is subject to severe physical transformations, acute health crises, or bodily threats.29 When the sequence operates on the Jeeva sign, the native experiences profound psychological shifts, spiritual events, or threats to their overall cognitive vitality.29 Simultaneous affliction of both the Deha and Jeeva signs by transiting malefics serves as a highly reliable terminal indicator.

The sign progression within the Kalachakra does not always conform to standard zodiacal continuity. The engine must actively monitor for specific "leaps" or Gatis, which act as triggers for massive, non-linear life upheavals.29 The Manduki Gati, or Frog's Leap, involves a jump of two signs (e.g., from Virgo to Cancer), which algorithmically correlates to a sudden elevation or catastrophic drop in social status. The Simhavalokana Gati, or Lion's Leap, represents a trinal jump (e.g., from Pisces to Scorpio), triggering drastic, life-altering transformations, often related to extreme survival scenarios or the massive, sudden acquisition of wealth.29

## **Branch C: Medical and Health Astrology**

To synthesize accurate medical predictions, the engine requires a multidimensional array cross-referencing anatomical regions with planetary and sign-based afflictions. The integration of Ayurvedic pathology with astrological indicators allows the system to predict pathogenesis with extreme granularity.

### **Section C1: Anatomical Body Mapping Matrix**

The human body is mapped across a three-dimensional coordinate system comprising planets, signs, and houses.

| Anatomical System / Part | Governing Planet | Governing Zodiac Sign | Astrological House |
| :---- | :---- | :---- | :---- |
| **Brain, Head, Vitality** | Sun | Aries | 1st House |
| **Body Fluids, Chest, Breasts** | Moon | Cancer | 4th House |
| **Blood, Muscles, Marrow** | Mars | Scorpio / Aries | 6th / 8th House |
| **Lungs, Nerves, Speech** | Mercury | Gemini / Virgo | 3rd / 6th House |
| **Liver, Fat, Pancreas** | Jupiter | Sagittarius | 5th / 9th House |
| **Kidneys, Reproductive, Skin** | Venus | Taurus / Libra | 7th House |
| **Bones, Joints, Teeth** | Saturn | Capricorn / Aquarius | 10th / 11th House |
| **Toxins, Irregular Growth** | Rahu | N/A | 8th House |
| **Immunity, Undiagnosed Pain** | Ketu | N/A | 12th House |
| 22 |  |  |  |

### **Section C2: Disease Identification Algorithm**

The engine evaluates pathological potential through the Dusthana triangle, comprising the 6th house (acute disease and immune response), the 8th house (chronic conditions and surgical interventions), and the 12th house (hospitalization and terminal degradation).22

The intersection of specific malefic energies generates distinct disease profiles. Mars functions as the primary significator for inflammation, ulceration, and bleeding, whereas Saturn governs chronicity, bone degradation, and physiological blockages. An intersection of Mars and Saturn within the 6th or 8th house computes a statistically high probability for severe arthritis, complex fractures, or the necessity of surgical interventions.30

The engine must incorporate a specialized oncology algorithm to detect the probability of cancer, a disease defined by unnatural and toxic cellular replication. The algorithmic trigger for tumors requires a confluence of three factors: a severely afflicted Moon (disrupting lymphatic and fluid carriers), afflictions localized to the 6th, 8th, or 12th house, and the conjunction or mutual aspect of Rahu (representing toxins and irregular growth) or Ketu (representing hidden cellular degradation) with Saturn.33 For instance, the presence of the Moon, Saturn, and Rahu in the 6th house indicates a severe vulnerability to gastrointestinal or breast malignancies.33

Furthermore, psychiatric and autoimmune disorders are flagged when an afflicted Moon intersects with Mercury and Ketu. This specific array indicates mental health degradation, neurological misfiring, or autoimmune conditions where the origin of the disease remains obfuscated.30

### **Section C3: Timing of Health Events**

Health crises do not manifest randomly; they correlate strictly with operational Dashas and Transits (Gochara). The operational periods of the Mahadasha or Antardasha of the 6th lord, 8th lord, or planets occupying these houses serve as the primary flags for periods of severe medical vulnerability.31

The algorithm incorporates the 22nd Drekkana (Khara), a highly sensitive mathematical point representing the lord of the 8th house within the D-3 (Drekkana) divisional chart. When a transiting malefic such as Saturn or Rahu, or even the Lagna lord, crosses the exact degree span of the 22nd Drekkana, the system forecasts acute bodily discomfort, severe illness, or potential mortality.35 Additionally, the simultaneous transits of Saturn and Rahu over the natal Ascendant, the 6th house, or the Natal Moon serve as undeniable timing triggers for the physical materialization of previously dormant chronic diseases.6 The position of Gulika and Mandi further refines the timing, acting as micro-triggers for acute pain or infection.21

### **Section C4: Longevity Calculation (Ayurdaya)**

A robust prediction engine must synthesize three highly complex mathematical longevity models. The architectural choice of which model to prioritize depends entirely on identifying the strongest entity among the Sun, the Moon, and the Ascendant (Lagna).38

The Pindayu Method is applied computationally if the Sun possesses the highest relative strength.38 This model assigns a full exaltation base of years to each planet: Sun (19), Moon (25), Mars (15), Mercury (12), Jupiter (15), Venus (21), and Saturn (20). The algorithm calculates the Effective Arc of Longevity by subtracting the deepest exaltation point from the planet's longitude. If this value exceeds 180 degrees, the system reduces it by 180\. The gross years are then calculated by multiplying the Full Pindayu by the ratio of the Effective Arc to 360 degrees. Subsequent mathematical reductions, termed Haranas, are aggressively applied. These include Astangata (which halves the value due to combustion), Shatrukshetra (which reduces the value by one-third for enemy sign placement), Chakrapata (a reduction based on visible hemisphere placement), and Krurodaya (a reduction triggered by malefics rising in the ascendant).38

The Nisargayu Method is utilized if the Moon emerges as the strongest entity.38 While this model employs the exact same mathematical reductions (Haranas) as the Pindayu method, it alters the fundamental base years at exaltation to: Sun (20), Moon (1), Mars (2), Mercury (9), Jupiter (18), Venus (20), and Saturn (50).38

The Amsayu Method is triggered when the Lagna demonstrates superior strength.38 This method calculates longevity based strictly on Navamsa degrees. The base years are derived by taking the zodiacal longitude in arc minutes, dividing by 200, and applying a modulo 12 operation. Unlike the previous methods, Amsayu incorporates Bharanas (Increases), multiplying the base by 3 if the planet is exalted or retrograde, and by 2 if it is Vargottama. The standard reductions for Chakrapata, Astangata, and Shatrukshetra apply, but the Krurodaya reduction is systematically bypassed.38

If two or more of these core parameters possess equal strength, the engine averages the calculated lifespans to achieve synthesis.41 However, the algorithmic engine is programmed to recognize that standard Ayurdaya models are entirely overridden by Balarishta (infant mortality) yogas. If the natal Moon is positioned in the 6th, 8th, or 12th house, flanked or heavily aspected by cruel malefics without the mitigating intervention of benefics, the algorithm flags an exceptionally high probability of mortality within the first one to four years of life, thereby rendering long-term Ayurdaya calculations mathematically null.42

## **Branch D: Complete Conditional Dasha Systems**

While the Vimshottari Dasha serves as the universal baseline, conditional dashas must be dynamically triggered by the algorithm when specific mathematical prerequisites in the natal chart are satisfied. These dashas drastically refine the accuracy of predictions, narrowing the temporal window of probability for highly specific life events. The engine evaluates eligibility for all ten conditional systems simultaneously, running parallel predictive tracks.

### **1\. Shodashottari Dasha (116 Years)**

The Shodashottari Dasha is mathematically triggered if the birth occurs during the day in the Krishna Paksha (waning Moon phase) or at night in the Shukla Paksha (waxing Moon phase), provided that the Lagna rises in the Hora (half-sign division) of the Moon for Krishna births, or the Sun for Shukla births.44

The computation algorithm directs the system to count from Pushya Nakshatra to the Janma Nakshatra (natal Moon star), divide the result by 8, and use the remainder to determine the initiating Dasha. The operational sequence and duration run as follows: Sun (11 years), Mars (12 years), Jupiter (13 years), Saturn (14 years), Ketu (15 years), Moon (16 years), Mercury (17 years), and Venus (18 years). Rahu is structurally excluded from this system.45 Predictively, this Dasha specializes in evaluating deep physiological stamina, long-term health anomalies, and systemic, slow-building wealth accumulation over the native's lifetime.

### **2\. Dwadasottari Dasha (112 Years)**

Eligibility for the Dwadasottari Dasha is confirmed if the natal Lagna (Ascendant) falls within the Navamsa (D-9 divisional chart) of Venus, corresponding specifically to the signs of Taurus or Libra.46

To compute the sequence, the engine counts from the Janma Nakshatra to Revati, dividing the total by 8\. The remainder dictates the first operating planetary period. The sequence progresses through the Sun (7 years), Jupiter (9 years), Ketu (11 years), Mercury (13 years), Rahu (15 years), Mars (17 years), Saturn (19 years), and the Moon (21 years). Venus is purposefully excluded from this sequence.45 This Dasha is heavily utilized by the algorithm to analyze periods of luxury, marital fidelity, artistic expression, and profound material acquisitions, focusing heavily on outcomes derived from underlying Venusian attributes.

### **3\. Panchottari Dasha (105 Years)**

The Panchottari Dasha operates exclusively for charts where Cancer serves as the Ascendant in both the D-1 (Rasi) and the highly specific D-12 (Dwadasamsa) divisional charts.46

The algorithm instructs the engine to count from Anuradha to the Janma Nakshatra and divide the integer by 7\. The planetary sequence unfolds as the Sun (12 years), Mercury (13 years), Saturn (14 years), Mars (15 years), Venus (16 years), Moon (17 years), and Jupiter (18 years).47 Because it is tethered to the sign of Cancer, the engine utilizes this Dasha to evaluate emotional trauma, deep-seated psychological shifts, maternal inheritances, and significant fluctuations in real estate holdings.

### **4\. Shatabdika Dasha (100 Years)**

This Dasha becomes valid only when the natal Lagna is Vargottama, meaning it occupies the exact same zodiac sign in both the D-1 Rasi and the D-9 Navamsa charts.47

The computation requires counting from Revati to the Janma Nakshatra and dividing by 7\. The resulting sequence progresses through the Sun (5 years), Moon (5 years), Venus (10 years), Mercury (10 years), Jupiter (20 years), Mars (20 years), and Saturn (30 years).47 Because a Vargottama Lagna indicates unyielding foundational strength, this Dasha is ideal for charting monumental, sudden shifts in fortune, global fame, and the acquisition of sweeping public authority or legacy.

### **5\. Chaturaashiti Sama Dasha (84 Years)**

The Chaturaashiti Sama Dasha is triggered strictly when the Lord of the 10th House is posited precisely within the 10th House (Karmasthana), indicating a chart with extreme professional focus.46

The engine counts from Swati to the Janma Nakshatra and divides by 7\. Uniquely, all planets in this system are assigned equal durations of 12 years. The sequence follows a fixed order: Sun, Moon, Mars, Mercury, Jupiter, Venus, and Saturn.48 The algorithm relies exclusively on this Dasha for highly detailed career mapping, predicting professional zeniths, industry dominance, and unprecedented political ascension.

### **6\. Dwisaptati Sama Dasha (72 Years)**

Eligibility for the Dwisaptati Sama Dasha requires that the Lagna Lord occupies the 7th House, or conversely, that the 7th House Lord occupies the Lagna, establishing a profound mutual relationship between the self and the external world.46

Computation involves counting from Moola to the Janma Nakshatra and expunging multiples of 8\. The remainder determines the starting point. Each planetary Dasha lasts exactly 9 years, following the natural weekday chronological order: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, and Rahu. Ketu is omitted from the sequence as it governs the system overall.49 This Dasha is unparalleled for evaluating partnership dynamics, profound marriage timing, the dissolution or merger of business entities, and the manifestation of open rivalries.

### **7\. Shat Trimsa Sama Dasha (36 Years)**

This condensed Dasha is applicable if a native is born during the day while the Lagna resides in the Hora of the Sun, or born at night with the Lagna in the Hora of the Moon.46

The algorithm counts from Shravana to the Janma Nakshatra and divides by 8\.50 The sequence follows a progressively increasing timeline, escalating the karmic pressure over the 36-year cycle: Moon (1 year), Sun (2 years), Jupiter (3 years), Mars (4 years), Mercury (5 years), Saturn (6 years), Venus (7 years), and Rahu (8 years).50 The engine flags this Dasha to assess short-to-medium-term vitality, intense and rapid karmic burns, and sudden fluctuations in personal agency and concerted effort.

### **8\. Yogini Dasha (36 Years)**

The Yogini Dasha is universally applicable but heavily weighted towards Tantric and Karmic interpretations, offering a concentrated 36-year cycle.51 The underlying computation algorithm is rooted in eight feminine planetary deities mapped directly to the Nakshatras.

The sequence and specific planetary durations operate as follows: Mangala (Moon, 1 year), Pingala (Sun, 2 years), Dhanya (Jupiter, 3 years), Bhramari (Mars, 4 years), Bhadrika (Mercury, 5 years), Ulka (Saturn, 6 years), Siddha (Venus, 7 years), and Sankata (Rahu/Ketu, 8 years).51 The engine computes Antardashas (sub-periods) using a precise fractional rule where the sub-period equals the Mahadasha years multiplied by the Antardasha years, divided by 36\. For example, the Siddha-Sankata sub-period yields exactly 1.55 years.51 This sequence is highly sensitive for predicting profound spiritual awakenings, instances of karmic retribution, the emergence of hidden diseases, and sudden catastrophic or miraculous life events.

### **9\. Moola Dasha (Lagnadi Kendradi Dasha)**

The Moola Dasha is universally applicable and is utilized by the algorithm to evaluate the fundamental root karma of the native and its exact timing of manifestation.53

The computational starting point and subsequent sequence depend entirely on calculating the spatial strength of the Kendra (1st, 4th, 7th, 10th), Panaphara (2nd, 5th, 8th, 11th), and Apoklima (3rd, 6th, 9th, 12th) houses. The strongest entity among the Lagna, Sun, or Moon initiates the cycle. The Dashas then systematically follow the planets placed in the Kendras, followed by those in the Panapharas, and concluding with those in the Apoklimas.53 The duration math utilizes the standard Vimshottari period of the planet as a baseline, but applies dynamic modifications: the engine subtracts 1 year from the baseline; if the planet is Exalted, it adds 1 year; if Debilitated, it subtracts an additional 1 year. If the net calculation results in 0, the full baseline Vimshottari years are allocated, and negative values are treated as absolute.53 The predictive specialization of this Dasha allows the engine to trace generational curses, deep-seated psychological complexes, and the unavoidable fruition of past-life actions.

### **10\. Tara Dasha**

The Tara Dasha is a universally applicable system that acts as a highly refined, granular subset of the standard Vimshottari framework, relying heavily on Nakshatra positioning.55

While it utilizes the standard 120-year Vimshottari planetary durations, the periods are conceptually mapped to the nine *Taras* (Star categories) counted consecutively from the natal Moon's Nakshatra: Janma (Birth/Danger), Sampat (Wealth), Vipat (Loss), Kshema (Prosperity), Pratyak (Obstacles), Sadhana (Achievement), Naidhana (Death/Danger), Mitra (Friendship), and Parama Mitra (Great Friendship).14 Instead of generating predictions based on a planet's inherent benefic or malefic nature, the algorithm filters the planet's output strictly through its designated Tara state. A natural benefic planet operating in the *Vipat* or *Naidhana* Tara will produce destruction and loss, whereas a natural malefic operating in the *Sampat* or *Sadhana* Tara will yield fierce, unmitigated success. The engine relies heavily on this system for evaluating daily, micro-level transits and localizing exact event timing within larger planetary cycles.

#### **Works cited**

1. What Is Prashna Shastra? Complete Guide to Horary \- AstroSight, accessed on February 28, 2026, [https://astrosight.ai/prashna/what-is-prashna-shastra](https://astrosight.ai/prashna/what-is-prashna-shastra)  
2. How to Create a Prashna Chart: Step-by-Step Guide \- AstroSight.ai, accessed on February 28, 2026, [https://astrosight.ai/prashna/how-to-create-prashna-chart](https://astrosight.ai/prashna/how-to-create-prashna-chart)  
3. KP Reader Summaries | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/928846169/Kp-Reader-Summaries-2](https://www.scribd.com/document/928846169/Kp-Reader-Summaries-2)  
4. KP Prashna \- Final | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/779436632/Kp-Prashna-Final](https://www.scribd.com/document/779436632/Kp-Prashna-Final)  
5. KP Astrology – The Modern Science of Accurate Predictions, accessed on February 28, 2026, [https://anillkummar.com/kp-astrology-the-modern-science-of-accurate-predictions.html](https://anillkummar.com/kp-astrology-the-modern-science-of-accurate-predictions.html)  
6. KP Simple Rules | PDF | Astrological Sign \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/152895619/KP-Simple-Rules](https://www.scribd.com/document/152895619/KP-Simple-Rules)  
7. Download the Complete KP Astrology Formulas PDF – House Groupings by Astrologer Gautam Verma, accessed on February 28, 2026, [https://www.gautamcrystals.com/post/kp-astrology-combinations-pdf](https://www.gautamcrystals.com/post/kp-astrology-combinations-pdf)  
8. KP Rules Compiled | PDF | Horoscope | Marriage \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/271291393/KP-Rules-Compiled](https://www.scribd.com/document/271291393/KP-Rules-Compiled)  
9. KP Astrology House Grouping Guide | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/127714260/House-Grouping](https://www.scribd.com/document/127714260/House-Grouping)  
10. Chapter 2: Fundamental Principles \- KP Astrology \- AstroSage, accessed on February 28, 2026, [https://kpastrology.astrosage.com/kp-learning-home/tutorial/chapter-2-fundamental-principles](https://kpastrology.astrosage.com/kp-learning-home/tutorial/chapter-2-fundamental-principles)  
11. KP Astrology: Sub-Lord Analysis | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/936307144/KP-Material](https://www.scribd.com/document/936307144/KP-Material)  
12. Vimshottari Dasha: Get Free Predictions For Life \- AstroSage, accessed on February 28, 2026, [https://www.astrosage.com/free/vimshottari-dasha-prediction-life-report.asp](https://www.astrosage.com/free/vimshottari-dasha-prediction-life-report.asp)  
13. Free KP Horoscope | KP Chart, Cusps & Predictions | OnlineJyotish.com \- Online Jyotish, accessed on February 28, 2026, [https://www.onlinejyotish.com/free-astrology/kp-horoscope.php](https://www.onlinejyotish.com/free-astrology/kp-horoscope.php)  
14. Muhurta-Raman Eng \- Panchanga.lv, accessed on February 28, 2026, [http://www.panchanga.lv/wp-content/uploads/2020/06/Muhurta\_Raman.pdf](http://www.panchanga.lv/wp-content/uploads/2020/06/Muhurta_Raman.pdf)  
15. Ithasala Yoga in Prashna: Key to Horary Success \- AstroSight, accessed on February 28, 2026, [https://astrosight.ai/prashna/ithasala-yoga-in-prashna-astrology](https://astrosight.ai/prashna/ithasala-yoga-in-prashna-astrology)  
16. PRAS NA TANTRA ., accessed on February 28, 2026, [https://storage.yandexcloud.net/j108/library/pwnejyvl/Sri\_Neelakanta\_-\_Prasna\_Tantra.pdf](https://storage.yandexcloud.net/j108/library/pwnejyvl/Sri_Neelakanta_-_Prasna_Tantra.pdf)  
17. The Moon's Crucial Role in Prashna Astrology \- AstroSight, accessed on February 28, 2026, [https://astrosight.ai/prashna/role-of-moon-in-prashna](https://astrosight.ai/prashna/role-of-moon-in-prashna)  
18. Lost Person Prashna | PDF | Hindu Astrology | Divination \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/253329339/Lost-Person-Prashna](https://www.scribd.com/document/253329339/Lost-Person-Prashna)  
19. Prashna of Lost Person / Traveller | JYOTHISHI, accessed on February 28, 2026, [https://vijayalur.com/2014/09/22/prashna-of-lost-person-traveller-2/](https://vijayalur.com/2014/09/22/prashna-of-lost-person-traveller-2/)  
20. Missing Persons & Whereabouts in Prashna Shastra \- Astro Ankit, accessed on February 28, 2026, [https://astroankit.com/blogs/f/missing-persons-whereabouts-in-prashna-shastra](https://astroankit.com/blogs/f/missing-persons-whereabouts-in-prashna-shastra)  
21. Full text of "Prasna Marga \- Dr. BV Raman" \- Archive.org, accessed on February 28, 2026, [https://archive.org/stream/PrasnaMargaBVR/Prasna%20Marga%202\_djvu.txt](https://archive.org/stream/PrasnaMargaBVR/Prasna%20Marga%202_djvu.txt)  
22. Medical Astrology Question \- Reddit, accessed on February 28, 2026, [https://www.reddit.com/r/astrology/comments/1qsrbrn/medical\_astrology\_question/](https://www.reddit.com/r/astrology/comments/1qsrbrn/medical_astrology_question/)  
23. Kalachakra Dasa Demystified (Part1) \- Vedic Astrology Blog, accessed on February 28, 2026, [https://blog.indianastrologysoftware.com/kalachakra-dasa-demystified-part1/](https://blog.indianastrologysoftware.com/kalachakra-dasa-demystified-part1/)  
24. Kalachakra Dasa System of Prediction | PDF | Astrological Sign \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/138011691/Kalachakra-Dasa-System-of-Prediction](https://www.scribd.com/document/138011691/Kalachakra-Dasa-System-of-Prediction)  
25. Kalachakra Dasha System Explained: Classical Guide \- AstroSight, accessed on February 28, 2026, [https://astrosight.ai/transits/kalachakra-dasha-system-explained](https://astrosight.ai/transits/kalachakra-dasha-system-explained)  
26. Cycles of the Chakra \- Saravali, accessed on February 28, 2026, [https://saravali.github.io/astrology/kala\_cycle.html](https://saravali.github.io/astrology/kala_cycle.html)  
27. The Four Chakras \- Saravali, accessed on February 28, 2026, [https://saravali.github.io/astrology/kala\_chakras.html](https://saravali.github.io/astrology/kala_chakras.html)  
28. How To Calculate Dasha and Antardasha | PDF | Planets \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/443363105/How-to-Calculate-Dasha-and-Antardasha](https://www.scribd.com/document/443363105/How-to-Calculate-Dasha-and-Antardasha)  
29. Kalachakra Dasa Tutorial | PDF | Planets In Astrology | Divination \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/doc/48160412/Kalachakra-Dasa-Tutorial](https://www.scribd.com/doc/48160412/Kalachakra-Dasa-Tutorial)  
30. Medical Astrology Guide: Planets, Health & Remedies Explaine, accessed on February 28, 2026, [https://sitharsastrology.com/blog/complete-guide-to-disease-prediction-in-medical-astrology](https://sitharsastrology.com/blog/complete-guide-to-disease-prediction-in-medical-astrology)  
31. Medical Astrology and Important Combinations of Planets in Horoscope \- Astroshastra, accessed on February 28, 2026, [https://www.astroshastra.com/articles/medical.php](https://www.astroshastra.com/articles/medical.php)  
32. Astrology Planets \- Body parts and Diseases \- AstroMD \- Balu ..., accessed on February 28, 2026, [https://astromd.com/bodyparts.html](https://astromd.com/bodyparts.html)  
33. Cancer disease prediction using Medical Astrology, accessed on February 28, 2026, [https://sitharsastrology.com/blog/cancer-disease-prediction-using-medical-astrology](https://sitharsastrology.com/blog/cancer-disease-prediction-using-medical-astrology)  
34. Cancer | PDF | Planets In Astrology \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/presentation/985360019/Cancer](https://www.scribd.com/presentation/985360019/Cancer)  
35. Drekkana | JYOTHISHI, accessed on February 28, 2026, [https://vijayalur.com/2011/05/19/drekkana-dreshkana-decante/](https://vijayalur.com/2011/05/19/drekkana-dreshkana-decante/)  
36. 22nd Drekkana Lord and Its Play During Saturn Transit Randhra Bhava, accessed on February 28, 2026, [https://consultlunarastro.com/2025/08/02/22nd-drekkana-lord-and-its-play-during-saturn-transit-randhra-bhava/](https://consultlunarastro.com/2025/08/02/22nd-drekkana-lord-and-its-play-during-saturn-transit-randhra-bhava/)  
37. 35 DREKKANA (D3) IMPORTANCE IN MEDICAL ASTROLOGY Tirunaghari Udaya Kumar \- International Journal of Computational Research and Development, accessed on February 28, 2026, [https://ijcrd.dvpublication.com/uploads/66601fee47c5f\_211.pdf](https://ijcrd.dvpublication.com/uploads/66601fee47c5f_211.pdf)  
38. Pindayu, Nisargayu and Amsayu. Mathematical Models for Longevity… | by Varaha Mihira | Thoughts on Jyotish | Medium, accessed on February 28, 2026, [https://medium.com/thoughts-on-jyotish/pindayu-nisargayu-and-a%C5%84%C5%9Bayu-f2eb23c45611](https://medium.com/thoughts-on-jyotish/pindayu-nisargayu-and-a%C5%84%C5%9Bayu-f2eb23c45611)  
39. Longevity Analysis using Amsayu method | Sithars Astrology, accessed on February 28, 2026, [https://sitharsastrology.com/blog/longevity-analysis-using-amsayu-method](https://sitharsastrology.com/blog/longevity-analysis-using-amsayu-method)  
40. Amshayu: Longevity Calculation Method | PDF | Hindu Astrology | Planets \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/173404167/Amshayu-Main](https://www.scribd.com/document/173404167/Amshayu-Main)  
41. Pind Ayu | PDF | Hindu Astrology \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/439930329/pind-ayu](https://www.scribd.com/document/439930329/pind-ayu)  
42. Bhava Phalams \- Chapter 9-24 | PDF | Technical Factors Of Astrology \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/428421587/Bhava-Phalams-Chapter-9-24](https://www.scribd.com/document/428421587/Bhava-Phalams-Chapter-9-24)  
43. Understanding Balarishta in Vedic Astrology | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/109007088/Bala-Rishta](https://www.scribd.com/document/109007088/Bala-Rishta)  
44. shodasottari \- Parijaata, accessed on February 28, 2026, [https://parijaata.wordpress.com/tag/shodasottari/](https://parijaata.wordpress.com/tag/shodasottari/)  
45. Other Dashas | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/presentation/697114451/Other-Dashas](https://www.scribd.com/presentation/697114451/Other-Dashas)  
46. Conditional Dasa Systems \- The Art of Vedic Astrology, accessed on February 28, 2026, [https://www.theartofvedicastrology.com/?page\_id=436](https://www.theartofvedicastrology.com/?page_id=436)  
47. Panchottari Dasa & Shatabdika Dasa \- Tag-to-Adawal, accessed on February 28, 2026, [http://tagtoadawal.blogspot.com/2014/04/panchottari-dasa-shatabdika-dasa.html](http://tagtoadawal.blogspot.com/2014/04/panchottari-dasa-shatabdika-dasa.html)  
48. Parashari Dasha Systems \* BP Lama Jyotishavidya, accessed on February 28, 2026, [https://barbarapijan.com/bpa/VimshottariDasha/1Vimshottari\_dasha\_BPHS\_dashaSystems47.htm](https://barbarapijan.com/bpa/VimshottariDasha/1Vimshottari_dasha_BPHS_dashaSystems47.htm)  
49. Dvisaptati Sama Dasa \- Sanjay Rath, accessed on February 28, 2026, [https://srath.com/jyoti%E1%B9%A3a/dasa/dvisaptati-sama-dasa/](https://srath.com/jyoti%E1%B9%A3a/dasa/dvisaptati-sama-dasa/)  
50. In search of Maharishi Parashara's 42 Dasa systems | by Varaha Mihira | Thoughts on Jyotish | Medium, accessed on February 28, 2026, [https://medium.com/thoughts-on-jyotish/in-search-of-maharishi-parasharas-42-dasa-systems-56f7604b5138](https://medium.com/thoughts-on-jyotish/in-search-of-maharishi-parasharas-42-dasa-systems-56f7604b5138)  
51. Yogini Dasha Prediction Rules: Complete 36-Year Guide \- AstroSight, accessed on February 28, 2026, [https://astrosight.ai/transits/yogini-dasha-prediction-rules](https://astrosight.ai/transits/yogini-dasha-prediction-rules)  
52. Yogini Dasas- Govern the Different Phases of the Life \- Kali Tantra, accessed on February 28, 2026, [https://www.kalitantra.in/dasas.php](https://www.kalitantra.in/dasas.php)  
53. Mula dasa \- Mūla Daśā \- Sanjay Rath, accessed on February 28, 2026, [https://srath.com/jyoti%E1%B9%A3a/dasa/mula-dasa/](https://srath.com/jyoti%E1%B9%A3a/dasa/mula-dasa/)  
54. Jyotish BPHS Santhanam Vol.2 | PDF | Planets In Astrology \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/623154606/Jyotish-BPHS-Santhanam-Vol-2](https://www.scribd.com/document/623154606/Jyotish-BPHS-Santhanam-Vol-2)  
55. Tara Dasha System in Brihat Parashara Hora Shastra (BPHS) \- astrosutras.in, accessed on February 28, 2026, [https://astrosutras.in/index.php/2025/03/04/tara-dasha-system-in-brihat-parashara-hora-shastra-bphs/](https://astrosutras.in/index.php/2025/03/04/tara-dasha-system-in-brihat-parashara-hora-shastra-bphs/)  
56. How to predict life events using Dashas \- Farfaraway, accessed on February 28, 2026, [https://www.farfaraway.co/blog/how-to-read-dashas](https://www.farfaraway.co/blog/how-to-read-dashas)

[image1]: <data:image/png;base64,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>