# **Computational Architecture of Classical Vedic Astrology: Algorithms for Dignity, KP, Nadi Amsha, and Ayurdaya**

The development of a computational Vedic astrology engine requires translating thousands of years of esoteric heuristic principles into deterministic mathematical algorithms. The system must synthesize classical Parashari principles, the highly precise Krishnamurti Paddhati (KP) system, micro-zodiacal divisions (Nadi Amsha and Tattva), and the complex mathematical models of Ayurdaya (longevity). This report details the core computational rules required to complete the classical knowledge base, providing the definitive algorithms, edge cases, and architectural logic for functional dignity, sub-arc significations, destiny profiling, and lifespan calculation.

## **Part A: Functional Dignity and Obstruction Matrix (All 12 Lagnas)**

The computational evaluation of a planetary body’s functional dignity is paramount for accurate dasha (planetary period) and transit forecasting. In classical Vedic astrology, a planet's natural benefic or malefic status is algorithmically overridden by the specific houses it rules relative to the Ascendant (Lagna).1 The engine must assign weighted values to planets based on their functional disposition before calculating their net effects.

The fundamental algorithmic logic for determining functional dignity relies on the following structural heuristics:

1. **Trinal Lords (1st, 5th, 9th Houses):** These are always programmed as functional benefics. They represent high-energy, auspicious vectors and positive karmic momentum. The 9th house is the most auspicious trine, followed by the 5th, and then the 1st.1  
2. **Trishadaya Lords (3rd, 6th, 11th Houses):** These are always programmed as functional malefics. They represent stress, illness, competition, and excessive material desire. The 11th house is the most malefic of the Trishadaya group, followed by the 6th, and then the 3rd.2  
3. **Kendradhipati Dosha:** Natural benefics (Jupiter, Venus, unassociated Mercury, and the waxing Moon) that own angular houses (4th, 7th, 10th) lose their inherent beneficence. In the computational model, they become functionally neutral or malefic, depending on their secondary house lordship.3  
4. **Dependent/Neutral Lords (2nd, 8th, 12th Houses):** These planets are functionally neutral and give results based on their other house lordship or their planetary conjunctions.2 The 8th house lordship is mathematically the most severely detrimental of the three because it is the 12th house (loss) from the 9th house (fortune and dharma).5  
5. **Yoga Karaka:** This is a single planet that simultaneously rules an angular house (Kendra: 1, 4, 7, 10\) and a trinal house (Kona: 1, 5, 9). When this condition is met, the engine elevates this planet to the status of supreme benefic for that specific Lagna, granting it the highest positive weight in the matrix.2  
6. **Maraka (Death-Inflicting Planets):** The lords of the 2nd and 7th houses are programmed as Marakas. The logic derives from the principle of negation: the 8th house represents longevity, and the 12th house from any house negates it. Thus, the 12th from the 8th is the 7th house. The 3rd house is the secondary house of longevity (being the 8th from the 8th), and the 12th from the 3rd is the 2nd house.5  
7. **Badhaka (Obstructor Planets):** The Badhaka represents unseen obstacles and is calculated via a modulo logic based on the sign's modality (Quadruplicity).7  
   * For **Cardinal (Chara) Signs** (Aries, Cancer, Libra, Capricorn): The 11th House Lord is the Badhaka.7  
   * For **Fixed (Sthira) Signs** (Taurus, Leo, Scorpio, Aquarius): The 9th House Lord is the Badhaka.7  
   * For **Mutable/Dual (Dvisvabhava) Signs** (Gemini, Virgo, Sagittarius, Pisces): The 7th House Lord is the Badhaka.7

### **Comprehensive Dignity Array by Ascendant**

The computational engine must utilize the following predefined matrices for the twelve Ascendants to assign appropriate functional weights.2

#### **1\. Aries (Mesha) Ascendant**

* **Modality:** Cardinal  
* **Yoga Karaka:** None. While Mars and Jupiter are highly auspicious, they do not rule a Kendra and Kona simultaneously.8  
* **Functional Benefics:** Mars, Sun, and Jupiter. Mars rules the 1st (trine) and 8th (dusthana), but its Moolatrikona sign (Aries) falls in the 1st house, making it predominantly benefic.3 The Sun rules the 5th (trine). Jupiter rules the 9th (trine) and 12th (neutral).3  
* **Functional Malefics:** Mercury, Saturn, Rahu, and Ketu. Mercury rules the 3rd and 6th houses (both Trishadaya). Saturn rules the 10th and 11th, becoming malefic primarily due to its 11th house Trishadaya lordship.3  
* **Neutral:** Venus (rules 2nd and 7th) and Moon (rules 4th).3  
* **Maraka:** Venus (Lord of 2nd and 7th).3  
* **Badhaka:** Saturn (Lord of the 11th house for a Cardinal sign).7

#### **2\. Taurus (Vrishabha) Ascendant**

* **Modality:** Fixed  
* **Yoga Karaka:** Saturn. It rules the 9th (Kona) and 10th (Kendra) houses simultaneously, operating as the highest benefic.3  
* **Functional Benefics:** Saturn, Sun (rules the 4th), and Mercury (rules the 2nd and 5th).2  
* **Functional Malefics:** Jupiter (rules 8th and 11th), Venus, Moon, and Mars. Venus is a complex edge case; it rules the 1st and 6th houses. Because Venus lacks overlapping positive significations with the 6th house, its functional nature becomes slightly tainted, making it a conditional malefic or neutral rather than a pure benefic despite being the Lagna lord.4  
* **Neutral:** None explicitly, though Venus is debated as neutral.2  
* **Maraka:** Mercury (2nd) and Mars (7th).3  
* **Badhaka:** Saturn (Lord of the 9th house for a Fixed sign).7 Note that Saturn is both the Yoga Karaka and the Badhaka, creating a complex dual algorithm where it causes obstacles but ultimately delivers success.

#### **3\. Gemini (Mithuna) Ascendant**

* **Modality:** Mutable  
* **Yoga Karaka:** None.2  
* **Functional Benefics:** Venus (rules 5th and 12th).2  
* **Functional Malefics:** Mars (rules 6th and 11th), Jupiter (rules 7th and 10th \- suffers severe Kendradhipati dosha), and Sun (rules 3rd).2  
* **Neutral:** Moon (rules 2nd), Mercury (rules 1st and 4th), and Saturn (rules 8th and 9th).2  
* **Maraka:** Moon (2nd) and Jupiter (7th).2  
* **Badhaka:** Jupiter (Lord of the 7th house for a Mutable sign).7

#### **4\. Cancer (Karka) Ascendant**

* **Modality:** Cardinal  
* **Yoga Karaka:** Mars. It rules the 5th (Kona) and 10th (Kendra) houses, operating as a supreme benefic.2  
* **Functional Benefics:** Mars, Moon (rules 1st), and Jupiter. Jupiter rules the 9th and 6th, but its Moolatrikona sign (Sagittarius) falls in the 6th house, pulling its center of gravity toward some malefic results if unafflicted, though it remains a primary benefic.2  
* **Functional Malefics:** Mercury (rules 3rd and 12th), Venus (rules 4th and 11th), and Saturn (rules 7th and 8th).2  
* **Neutral:** Sun (rules 2nd).2  
* **Maraka:** Sun (2nd) and Saturn (7th). Saturn is a particularly strong Maraka due to its simultaneous 8th house lordship.2  
* **Badhaka:** Venus (Lord of the 11th house for a Cardinal sign).7

#### **5\. Leo (Simha) Ascendant**

* **Modality:** Fixed  
* **Yoga Karaka:** Mars. It rules the 4th (Kendra) and 9th (Kona) houses.2  
* **Functional Benefics:** Mars, Sun (rules 1st), and Jupiter (rules 5th and 8th).2  
* **Functional Malefics:** Mercury (rules 2nd and 11th), Venus (rules 3rd and 10th), and Saturn (rules 6th and 7th).2  
* **Neutral:** Moon (rules 12th). Because the Sun and Moon are friends, the Moon acts neutrally or beneficially depending on its phase.2  
* **Maraka:** Mercury (2nd) and Saturn (7th).8  
* **Badhaka:** Mars (Lord of the 9th house for a Fixed sign).7 Like Taurus, the Yoga Karaka is also the Badhaka.

#### **6\. Virgo (Kanya) Ascendant**

* **Modality:** Mutable  
* **Yoga Karaka:** None.2  
* **Functional Benefics:** Venus (rules 2nd and 9th).2  
* **Functional Malefics:** Mars (rules 3rd and 8th), Jupiter (rules 4th and 7th \- suffers Kendradhipati dosha), and Moon (rules 11th).2  
* **Neutral:** Mercury (rules 1st and 10th), Saturn (rules 5th and 6th), and Sun (rules 12th).2  
* **Maraka:** Venus (2nd) and Jupiter (7th).2  
* **Badhaka:** Jupiter (Lord of the 7th house for a Mutable sign).7

#### **7\. Libra (Tula) Ascendant**

* **Modality:** Cardinal  
* **Yoga Karaka:** Saturn. It rules the 4th (Kendra) and 5th (Kona) houses.2  
* **Functional Benefics:** Saturn, Mercury (rules 9th and 12th), and Venus (rules 1st and 8th).2  
* **Functional Malefics:** Mars (rules 2nd and 7th), Jupiter (rules 3rd and 6th), and Sun (rules 11th).2  
* **Neutral:** Moon (rules 10th).2  
* **Maraka:** Mars (Lord of 2nd and 7th).2  
* **Badhaka:** Sun (Lord of the 11th house for a Cardinal sign).7

#### **8\. Scorpio (Vrishchika) Ascendant**

* **Modality:** Fixed  
* **Yoga Karaka:** None.2  
* **Functional Benefics:** Moon (rules 9th), Jupiter (rules 2nd and 5th), and Sun (rules 10th).2  
* **Functional Malefics:** Mercury (rules 8th and 11th), Venus (rules 7th and 12th), and Saturn (rules 3rd and 4th).2  
* **Neutral:** Mars (rules 1st and 6th). Mars shares overlapping karakatwas (significations) with the 6th house (competitiveness, injury, litigation). Thus, while it acts favorably for the 1st house, it strongly activates 6th house themes, creating a complex, mixed vector rather than pure beneficence.4  
* **Maraka:** Jupiter (2nd) and Venus (7th).2  
* **Badhaka:** Moon (Lord of the 9th house for a Fixed sign).7

#### **9\. Sagittarius (Dhanu) Ascendant**

* **Modality:** Mutable  
* **Yoga Karaka:** None.2  
* **Functional Benefics:** Mars (rules 5th and 12th) and Sun (rules 9th).2  
* **Functional Malefics:** Venus (rules 6th and 11th), Saturn (rules 2nd and 3rd), and Mercury (rules 7th and 10th \- suffers Kendradhipati dosha).2  
* **Neutral:** Jupiter (rules 1st and 4th) and Moon (rules 8th).2  
* **Maraka:** Saturn (2nd) and Mercury (7th).2  
* **Badhaka:** Mercury (Lord of the 7th house for a Mutable sign).7

#### **10\. Capricorn (Makara) Ascendant**

* **Modality:** Cardinal  
* **Yoga Karaka:** Venus. It rules the 5th (Kona) and 10th (Kendra) houses.2  
* **Functional Benefics:** Venus, Mercury (rules 6th and 9th), and Saturn (rules 1st and 2nd).2  
* **Functional Malefics:** Mars (rules 4th and 11th), Jupiter (rules 3rd and 12th), and Moon (rules 7th).2  
* **Neutral:** Sun (rules 8th).2  
* **Maraka:** Saturn (2nd) and Moon (7th).2  
* **Badhaka:** Mars (Lord of the 11th house for a Cardinal sign).7

#### **11\. Aquarius (Kumbha) Ascendant**

* **Modality:** Fixed  
* **Yoga Karaka:** Venus. It rules the 4th (Kendra) and 9th (Kona) houses.2  
* **Functional Benefics:** Venus, Saturn (rules 1st and 12th), and Sun (rules 7th).2  
* **Functional Malefics:** Mars (rules 3rd and 10th), Jupiter (rules 2nd and 11th), and Moon (rules 6th).2  
* **Neutral:** Mercury (rules 5th and 8th).2  
* **Maraka:** Jupiter (2nd) and Sun (7th).2  
* **Badhaka:** Venus (Lord of the 9th house for a Fixed sign).7

#### **12\. Pisces (Meena) Ascendant**

* **Modality:** Mutable  
* **Yoga Karaka:** None.2  
* **Functional Benefics:** Moon (rules 5th) and Mars (rules 2nd and 9th).2  
* **Functional Malefics:** Venus (rules 3rd and 8th), Saturn (rules 11th and 12th), Sun (rules 6th), and Mercury (rules 4th and 7th \- suffers Kendradhipati dosha).2  
* **Neutral:** Jupiter (rules 1st and 10th).2  
* **Maraka:** Mars (2nd) and Mercury (7th).2  
* **Badhaka:** Mercury (Lord of the 7th house for a Mutable sign).7

## ---

**Part B: Krishnamurti Paddhati (KP) Engine Mechanics**

The Krishnamurti Paddhati (KP) system demands an exceedingly precise computational framework, abandoning sign-based boundaries in favor of specific cuspal coordinates calculated via the Placidus house system.11 The KP engine relies heavily on the division of Nakshatras (lunar mansions) into smaller fractions governed by "Sub-Lords" and "Sub-Sub-Lords."

### **1\. Sub-Lord Computation Algorithm**

A Nakshatra spans exactly ![][image1] (or 800 arc minutes).12 The KP system divides this arc into nine unequal segments based on the Vimshottari Dasha system's planetary period proportions.11 The total Vimshottari cycle is 120 years.

The arc span ![][image2] of a Sub-Lord is computed as:

![][image3]  
Where ![][image4] is the Dasha years assigned to the planet.12

| Planet | Vimshottari Years | Proportion of Nakshatra | Sub-Lord Arc Span |
| :---- | :---- | :---- | :---- |
| **Ketu** | 7 | 7 / 120 | ![][image5] |
| **Venus** | 20 | 20 / 120 | ![][image6] |
| **Sun** | 6 | 6 / 120 | ![][image7] |
| **Moon** | 10 | 10 / 120 | ![][image8] |
| **Mars** | 7 | 7 / 120 | ![][image5] |
| **Rahu** | 18 | 18 / 120 | ![][image9] |
| **Jupiter** | 16 | 16 / 120 | ![][image10] |
| **Saturn** | 19 | 19 / 120 | ![][image11] |
| **Mercury** | 17 | 17 / 120 | ![][image12] |

The sequence of Sub-Lords within a given Nakshatra always begins with the planet that rules the Nakshatra (the Star-Lord) and proceeds in the standard Vimshottari sequence.14 To locate the Sub-Lord of any Placidus house cusp, the engine calculates the exact degree, identifies the governing Nakshatra, and iteratively subtracts the Sub-Lord arcs from the start of the Nakshatra until the specific degree is isolated.

### **2\. The 4-Level Significator Chain and Hierarchy**

KP astrology identifies planetary agents (significators) for any given house through a strict, four-tier hierarchy.12 Level 1 is computationally the most powerful determinant.

* **Level 1 (Type A):** Planets situated in the Nakshatra (Star) of the occupants of the house.  
* **Level 2 (Type B):** Planets physically occupying the house.  
* **Level 3 (Type C):** Planets situated in the Nakshatra (Star) of the owner (lord) of the house.  
* **Level 4 (Type D):** The owner (lord) of the house.15

Simultaneously, the engine must evaluate the condition of each planet through its own internal hierarchy: **Planet ![][image13] Star-Lord ![][image13] Sub-Lord ![][image13] Sub-Sub-Lord**.11 The underlying KP philosophy programs the **Planet** as the *source* or *resource*, while its **Star-Lord** dictates the *result* or *eventual manifestation*. The **Sub-Lord** acts as the final judge, determining the quality, magnitude, or denial of that result. The **Sub-Sub-Lord** provides microscopic precision for event timing.11 For example, if a planet signifies houses 4 and 11, but its Star-Lord signifies 2 and 7, the result is marriage (2, 7\) supported by domestic stability (4, 11).15

### **3\. House Groupings (Event Vectors)**

A computational engine must group specific houses to evaluate life events. An event is promised if the Sub-Lord of the primary house signifies the favorable group. It is denied if it exclusively signifies the detrimental houses (which are usually the 12th from the favorable houses, representing negation or loss).12

| Life Event | Primary House | Favorable House Group (Fructification) | Detrimental / Denial Houses |
| :---- | :---- | :---- | :---- |
| **Marriage** | 7th | 2, 7, 11 | 1, 6, 10, 12 12 |
| **Career / New Job** | 10th | 2, 6, 10, 11 | 5, 8, 12 16 |
| **Finance / Gain** | 2nd | 2, 6, 10, 11 | 5, 8, 12 16 |
| **Health / Recovery** | 1st/11th | 1, 5, 11 | 6, 8, 12 (illness/sickness) 16 |
| **Children (Childbirth)** | 5th | 2, 5, 11 | 1, 4, 10, 12 16 |
| **Foreign Travel** | 12th | 3, 9, 12 | 2, 8, 11 16 |

### **4\. KP Ruling Planets (RP) Timing Method**

To pinpoint the exact timing of an event out of several promised windows, the system utilizes the Ruling Planets (RP) present at the moment of judgment (horary/prashna) or at birth.12 The engine must capture the astronomical state at the exact moment of inquiry.

The five Ruling Planets, listed in order of computational weight (strongest to weakest), are:

1. **Ascendant Star Lord** (Lord of the Nakshatra rising on the Eastern horizon).  
2. **Ascendant Sign Lord**.  
3. **Moon Star Lord** (Lord of the Nakshatra occupied by the Moon).  
4. **Moon Sign Lord**.  
5. **Day Lord** (Ruler of the Hindu day, calculated from sunrise to sunrise).12

*Algorithmic Filter:* Any Ruling Planet that is retrograde, or is situated in the Nakshatra or Sub of a retrograde planet, is considered obstructed and must be discarded from the array.12 Rahu and Ketu act as agents for the planets whose signs they occupy or with whom they conjoin, inheriting their RP status.12

**Confirmation of Timing:** The engine evaluates the Vimshottari Dasha, Bhukti, Antara, and Sookshma (DBAS). The event will occur when the DBAS lords are prominent among the Ruling Planets. Furthermore, precision timing is triggered when the Sun, Moon, or Ascendant transits the exact degrees of the zodiac ruled by the selected fruitful significators (Sign, Star, and Sub). The Sun transit pinpoints the month, the Moon transit pinpoints the day, and the Ascendant transit pinpoints the hour and minute.12

### **5\. Denial Conditions**

The engine computes denial when the Sub-Lord of the primary house exclusively signifies the detrimental houses.12 For example, if evaluating marriage, the primary house is the 7th. If the 7th cuspal Sub-Lord is placed in a Nakshatra whose lord strongly signifies the denial houses (1, 6, 10\) and has no connection to the favorable houses (2, 7, 11), the event will not occur in the native's lifetime.12 If the Sub-Lord signifies a mix of favorable and detrimental houses, the engine predicts partial success, delays, or multiple outcomes depending on the running Dasha.12

## ---

**Part C: Nadi Amsha and Tattva Harmonics (High-Resolution Sub-Divisions)**

For ultra-precise birth time rectification (BTR) and micro-destiny profiling, the classical engine incorporates Nadi Amshas and the Tattva system. These mechanisms fractionate the zodiac into microscopic arcs, requiring birth time accuracy down to seconds.

### **1\. Nadi Amsha Computation**

The *Chandra Kala Nadi* (also known as *Deva Keralam*) splits each 30-degree zodiacal sign into 150 divisions.19 These divisions are formed by merging the boundaries of all sixteen Shodasa Vargas (divisional charts).20

### **2\. The Arc of a Nadi Amsha**

Assuming the equal division metric standardized for computational models, the arc of a single Nadi Amsha is:

![][image14]  
21

In terms of time (assuming a mean ascension of 2 hours per sign), one Nadi Amsha corresponds to approximately 48 seconds of birth time.19 Across the 12 signs of the zodiac, there are 1800 Nadi Amshas (![][image15]).

### **3\. The 1800 Nadi Amsha Naming Convention**

A definitive array of 150 unique names is mapped to the zodiac. The mapping algorithm is highly dependent on the modality (quadruplicity) of the sign 20:

* **Moveable/Cardinal (Chara) Signs** (Aries, Cancer, Libra, Capricorn): The Nadi Amshas run in direct sequence from 1 to 150\. (![][image16] to ![][image17] is Vasudha).20  
* **Fixed (Sthira) Signs** (Taurus, Leo, Scorpio, Aquarius): The sequence is strictly reversed, running from 150 to 1\. (![][image16] to ![][image17] is Parameswari, ![][image18] to ![][image19] is Vasudha).20  
* **Dual/Mutable (Dvisvabhava) Signs** (Gemini, Virgo, Sagittarius, Pisces): The sequence begins precisely in the middle. The first 75 divisions (from ![][image16] to ![][image20]) map to names 76 through 150\. The next 75 divisions (from ![][image20] to ![][image19]) map to names 1 through 75\.20

**Partial Array of Nadi Amsha Names (1-59 and 75-109):** To build the internal database, the engine maps the following sequence (compiled from the *Deva Keralam* texts) 20:

1. Vasudha, 2\. Vaishnavi, 3\. Brahmi, 4\. Kalakoota, 5\. Sankari, 6\. Sudhakarasama, 7\. Saumya, 8\. Suraa, 9\. Maaya, 29\. Kalushaa, 30\. Kamalaa, 31\. Kanthaa, 32\. Kaalaa, 33\. Karikaraa, 34\. Kshamaa, 35\. Durdharaa, 36\. Dhurbhagaa, 37\. Viswa, 38\. Visirnaa, 39\. Vihwala, 40\. Anilaa, 41\. Bhima, 42\. Sukhaprada, 43\. Snigdha, 44\. Sodaraa, 45\. Surasundari, 46\. Amrutaprasini, 47\. Kaala (Karalaa), 48\. KamadrukkaraVeerini, 49\. Gahwaraa, 50\. Kundini, 51\. Kanthaa, 52\. Vishakhya (Vishaa), 53\. Vishanaasini, 54\. Nirmada, 55\. Seethala, 56\. Nimnaa, 57\. Preeta, 58\. Priyavivardhani, 59\. Maanaghna... 75\. Trailokyamohanakari, 76\. Mahaamaari, 79\. Suprabhaa, 80\. Sobhaa, 81\. Sobhana, 82\. Sivadaa, 83\. Siva, 84\. Balaa, 85\. Jwalaa, 86\. Gadaa, 87\. Gaadaa, 88\. Nootanaa, 89\. Sumanoharaa, 90\. Somavalli, 91\. Somalatha, 92\. Mangala, 93\. Mudrika, 94\. Sudha, 95\. Melaa, 96\. Apavargaa, 97\. Pasyathaa, 98\. Navaneetha, 99\. Nisachari, 100\. Nirvrithi, 101\. Nirgathaa, 102\. Saaraa, 103\. Samagaa, 104\. Samadaa, 105\. Samaa, 106\. Viswambharaa, 107\. Kumari, 108\. Kokila, 109\. Kunjarakrithi.20

### **4\. Prediction vs. Rectification**

Nadi Amshas are primarily utilized to define the fundamental DNA of the nativity. While divisional charts (Vargas) refine specific areas of life, the Nadi Amsha dictates the overarching pattern of fate, including precise occupational archetypes, spiritual trajectory, and inherent fortune. It acts as the ultimate filter for Birth Time Rectification (BTR); if the life events do not match the classical definitions of the ascending Nadi Amsha, the chart time is computationally invalid.19 Once rectified, it is used for prediction by defining the baseline potential that planetary dashas will activate.22

### **5\. The Tattva (Five Elements) System**

The Tattva system operates as a secondary micro-timing algorithm, identifying the dominant cosmic element at the moment of birth. The five elements (Pancha Mahabhutas) are Akasha (Space/Ether), Vayu (Air), Tejas/Agni (Fire), Apas/Jala (Water), and Prithvi (Earth).27

Within each sign's subdivision, the elements cycle in specific mathematical intervals. A common computational model allocates 180 minutes (3 hours) to a full cycle of five elements, distributed unequally:

* **Prithvi:** 6 minutes  
* **Apas:** 12 minutes  
* **Tejas:** 18 minutes  
* **Vayu:** 24 minutes  
* **Akasha:** 30 minutes (Totaling 90 minutes for Aroha/Ascending sequence, and reversing for Avaroha/Descending sequence).29

**Computation Method (Antartattva):** Elements operate fractally. To find the duration of a sub-element (Antartattva) within a primary Tattva, the engine uses proportional division.

For example, the duration of the Prithvi Antartattva within the primary Prithvi Tattva:

![][image21]  
The Apas Antartattva within Prithvi:

![][image22]  
.31 This provides the computational engine with sub-minute resolution for mapping elemental dominance at birth.

## ---

**Part D: Ayurdaya (Longevity Computation)**

Vedic astrology incorporates deeply complex mathematical models to assess the duration of life. No single formula is considered absolute; instead, a multi-model approach is computationally required. The engine selects the primary mathematical model based on the strongest entity among the Sun, Moon, and Lagna. If the Sun is strongest, **Pindayu** is utilized; if the Moon is strongest, **Nisargayu** is triggered; and if the Lagna is strongest, **Amsayu** is applied.32

### **1\. Pindayu Method (Sun Dominant)**

This algorithm calculates longevity based on the distance of planets from their point of deepest exaltation.32

* **Maximum Potential Years:** Sun (19), Moon (25), Mars (15), Mercury (12), Jupiter (15), Venus (21), Saturn (20).32 Total maximum contribution is 127 years.  
* **Base Calculation:** A planet provides its full years if precisely at deep exaltation. If at deep debilitation, it yields exactly half. For intermediate positions, the years are calculated proportionally based on the arc distance.  
  ![][image23]  
  (If the arc distance exceeds ![][image24], it is subtracted from ![][image25] before applying the proportion).32

**Haranas (Reductions):** The engine must apply reductions sequentially:

1. **Chakrapata Harana (Visible Half Reduction):** Planets positioned in the visible hemisphere (Houses 7 through 12\) suffer deductions. Malefics lose: 100% (12th H), 50% (11th H), 33.3% (10th H), 25% (9th H), 20% (8th H), 16.6% (7th H). Benefics lose exactly half of these fractions.32  
2. **Astangata Harana (Combustion):** If a planet is combust (too close to the Sun), its contribution is reduced by 50%. Venus and Saturn are exempt from this algorithmic penalty.32  
3. **Shatrukshetra Harana (Inimical Sign):** If positioned in an enemy's sign, a planet loses 33.3% (1/3) of its remaining years. Mars and any retrograde planets are exempt.32  
4. **Krurodaya Harana:** If a malefic planet resides in the 1st House, a specific mathematical penalty is applied based on the Lagna's exact longitude.32

To sum and interpret, the engine adds the adjusted contributions of all seven planets plus the Lagna (which contributes based on its Navamsha strength, up to 12 years) to output the final Pindayu lifespan.32

### **2\. Amsayu Method (Lagna Dominant)**

Amsayu abandons the exaltation metric and relies heavily on the Navamsha (D-9) division.32

* **Base Formula:** The longitude of the planet (in arc minutes) is divided by 200\. The result modulo 12 yields the base years contributed by the planet. Each Navamsha traversed from Aries equates to one year, up to a maximum of 12 years per planet.32  
* **Bharanas (Enhancements):** A multiplier is applied before reductions. If a planet is retrograde, exalted, or in its own sign (Rasi), its contribution is multiplied by 3\. If it occupies its own Navamsha, Drekkana, or is Vargottama, it is multiplied by 2\. If both conditions apply, only the x3 multiplier executes.32  
* **Reductions:** Shatrukshetra, Astangata, and Chakrapata Haranas apply precisely as they do in Pindayu. Krurodaya Harana is bypassed.32

### **3\. Naisargika Ayurdaya (Moon Dominant)**

This method assigns fixed natural years to each planet, independent of their exaltation.32

* **Fixed Constants:** Moon (1 year), Mars (2 years), Mercury (9 years), Jupiter (18 years), Sun (20 years), Venus (20 years), Saturn (50 years).32 Total potential is 120 years.  
* **Adjustments:** The engine processes the identical Haranas (reductions) utilized in the Pindayu method to scale these fixed years down based on chart afflictions.32

### **4\. The Three Longevity Bands and Method of Pairs**

Beyond the raw mathematical outputs, Vedic astrology categorizes life into three broad bands. A computational engine verifies the output against these bands to ensure algorithmic sanity.32

* **Alpayu (Short Life):** 0 to 32 years (sometimes calculated as 0 to 36).39  
* **Madhyayu (Medium Life):** 32 to 64 years (sometimes calculated as 36 to 72).39  
* **Purnayu (Long Life):** 64 to 96+ years (sometimes calculated up to 108 or 120).39

**The "Three Pairs" Logic Matrix:** The Jaimini "Method of Three Pairs" is the standard algorithm for determining the correct longevity band. The engine evaluates the modalities (Moveable, Fixed, Dual) of three specific pairs of entities 41:

1. Lagna Lord & 8th House Lord  
2. Lagna & Hora Lagna  
3. Moon & Saturn

The computational logic evaluates the intersecting modalities to output a band:

| Pair Modality 1 | Pair Modality 2 | Resulting Longevity Band |
| :---- | :---- | :---- |
| Moveable | Moveable | Long Life (Purnayu) 41 |
| Fixed | Dual | Long Life (Purnayu) 41 |
| Moveable | Fixed | Medium Life (Madhyayu) 41 |
| Dual | Dual | Medium Life (Madhyayu) 41 |
| Moveable | Dual | Short Life (Alpayu) 41 |
| Fixed | Fixed | Short Life (Alpayu) 41 |

The engine counts the outputs of the three pairs. If two or more pairs yield the same result (e.g., two pairs output "Long Life"), that becomes the final longevity band. If all three yield different results, the result dictated by the Lagna and Hora Lagna pair overrides the others.41

### **5\. Execution of Death: Maraka and Badhaka Mechanics**

Longevity mathematics provide the maximum timeline, but the specific timing of physical dematerialization (death or extreme physical danger) requires evaluating dashas and transits.44

* **Maraka & Badhaka Identification:** The engine identifies the lords of the 2nd and 7th houses as Marakas, and the 11th, 9th, or 7th lord as Badhaka (depending on the sign modality).3  
* **Dasha Triggers:** Death manifests during the Vimshottari Dasha/Bhukti of a Maraka planet or a Badhaka planet, or planets occupying their houses.7  
* **Chidra Grahas (Vulnerability Nodes):** The computational engine must isolate the lord of the 22nd Drekkana (Kharesha) and the lord of the 64th Navamsha from the Moon. These planets are "Chidra Grahas" (planets of vulnerability) and act as silent executioners.44  
* **Transit Confirmation:** The physical event is algorithmically confirmed when malefic transiting planets (Saturn, Mars, Rahu, Ketu) cross over the exact degrees of the Maraka lord, the Badhaka lord, the Ascendant, or the 64th Navamsha.7 A convergence of a Maraka Dasha with a transit over the 22nd Drekkana signals critical systemic failure and potential death.44

#### **Works cited**

1. Compilation of Functional Malefics & Benefics and Ascendant-Wise Yogakaraks \- Reddit, accessed on March 2, 2026, [https://www.reddit.com/r/Advancedastrology/comments/1r0gspv/compilation\_of\_functional\_malefics\_benefics\_and/](https://www.reddit.com/r/Advancedastrology/comments/1r0gspv/compilation_of_functional_malefics_benefics_and/)  
2. Functional Nature \- Learning Astrology \- Wikidot, accessed on March 2, 2026, [http://astroveda.wikidot.com/functional-nature](http://astroveda.wikidot.com/functional-nature)  
3. Benefic & Malefic Planets in Kundli (With Calculator by Ascendant) \- Astropatri, accessed on March 2, 2026, [https://astropatri.com/kundli/planets/](https://astropatri.com/kundli/planets/)  
4. Benefics/ Malefics | The Art of Vedic Astrology, accessed on March 2, 2026, [https://www.theartofvedicastrology.com/?page\_id=372](https://www.theartofvedicastrology.com/?page_id=372)  
5. Functional Nature of planets based on their ownership \- Karmic Rhythms | Dr. Satya Prakash Choudhary | Yoga Vedanta Buddhism Tantra Jyotish, accessed on March 2, 2026, [https://karmicrhythms.com/functional-nature-of-planets-based-on-their-ownership/](https://karmicrhythms.com/functional-nature-of-planets-based-on-their-ownership/)  
6. Compilation of Functional Malefics & Benefics and Ascendant-Wise Yogakaraks \- Reddit, accessed on March 2, 2026, [https://www.reddit.com/r/Nakshatras/comments/1qp20zo/compilation\_of\_functional\_malefics\_benefics\_and/](https://www.reddit.com/r/Nakshatras/comments/1qp20zo/compilation_of_functional_malefics_benefics_and/)  
7. Life Span And Unnatural Death P.M. Gopalachari \- Saptarishis Astrology, accessed on March 2, 2026, [https://saptarishisshop.com/life-span-and-unnatural-death-pm-gopalachari/](https://saptarishisshop.com/life-span-and-unnatural-death-pm-gopalachari/)  
8. Yogakaraka and Maraka For All Lagnas | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/412334650/Yogakaraka-and-maraka-for-all-lagnas-docx](https://www.scribd.com/document/412334650/Yogakaraka-and-maraka-for-all-lagnas-docx)  
9. Functional Benefics and Malefics for All Ascendants | Learn Jyotish, accessed on March 2, 2026, [https://www.vedicplanet.com/jyotish/learn-jyotish/functional-benefics-and-malefics-for-all-ascendants/](https://www.vedicplanet.com/jyotish/learn-jyotish/functional-benefics-and-malefics-for-all-ascendants/)  
10. Behavior of Benefic and Malefic Planets | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/193541703/Natural-Functional-Behavior-of-Planets](https://www.scribd.com/document/193541703/Natural-Functional-Behavior-of-Planets)  
11. KP Astrology vs Vedic Astrology, accessed on March 2, 2026, [https://www.learnastrologyonline.in/blog/kp-astrology-vs-vedic-astrology](https://www.learnastrologyonline.in/blog/kp-astrology-vs-vedic-astrology)  
12. Chapter 2: Fundamental Principles \- KP Astrology, accessed on March 2, 2026, [https://kpastrology.astrosage.com/kp-learning-home/tutorial/chapter-2-fundamental-principles](https://kpastrology.astrosage.com/kp-learning-home/tutorial/chapter-2-fundamental-principles)  
13. KP Astrology \- Sub Lord Table, accessed on March 2, 2026, [https://aryanastrologyresearchcentre.com/2021/08/kp-astrology-sub-lord-table/](https://aryanastrologyresearchcentre.com/2021/08/kp-astrology-sub-lord-table/)  
14. Vimshottari Dasha Sub Lords Explained | PDF | Art \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/793431465/df](https://www.scribd.com/document/793431465/df)  
15. KP Astrology: Sub-Lord Analysis | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/936307144/KP-Material](https://www.scribd.com/document/936307144/KP-Material)  
16. New PDF of KP \- Astrology House Groupings (Formulas) \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/866199340/New-PDF-of-KP-Astrology-House-Groupings-formulas](https://www.scribd.com/document/866199340/New-PDF-of-KP-Astrology-House-Groupings-formulas)  
17. K.P. Astrology: Sub Lords Explained | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/doc/210313549/KP-Astrology-Rules](https://www.scribd.com/doc/210313549/KP-Astrology-Rules)  
18. KP Astrology: Event Timing Guide | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/doc/309294230/new-Learning-KP-Astrology](https://www.scribd.com/doc/309294230/new-Learning-KP-Astrology)  
19. Roots of Naadi Astrology: \- WordPress.com, accessed on March 2, 2026, [https://astrofoxx.files.wordpress.com/2018/11/roots-of-nadi-astrology.pdf](https://astrofoxx.files.wordpress.com/2018/11/roots-of-nadi-astrology.pdf)  
20. A ready reckoner for names and Rasis of Nadi Amsas \- International Journal of Jyotish Research, accessed on March 2, 2026, [https://www.jyotishajournal.com/pdf/2025/vol10issue2/PartB/10-2-3-179.pdf](https://www.jyotishajournal.com/pdf/2025/vol10issue2/PartB/10-2-3-179.pdf)  
21. Nadi Astrology \- Indian Astrology \- Vedic Astrology, accessed on March 2, 2026, [https://kascorner.com/nadi-astrology/](https://kascorner.com/nadi-astrology/)  
22. Jeeva and Sharira in Vedic Astrology | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/475769895/jeeva-and-sharira-graha](https://www.scribd.com/document/475769895/jeeva-and-sharira-graha)  
23. Nadiamsha: Understanding Nadi Concepts | PDF | Shiva | Kali \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/850992565/Nadiamsha-Description-of-each](https://www.scribd.com/document/850992565/Nadiamsha-Description-of-each)  
24. deva keralam \- (chandra kala nadi), accessed on March 2, 2026, [https://ia801405.us.archive.org/6/items/in.ernet.dli.2015.489052/2015.489052.Deva-Keralam.pdf](https://ia801405.us.archive.org/6/items/in.ernet.dli.2015.489052/2015.489052.Deva-Keralam.pdf)  
25. Nadi Amsha Chart Preparation Guide | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/doc/141621608/NadiAmsaChart](https://www.scribd.com/doc/141621608/NadiAmsaChart)  
26. Mystery About Number and Longitude of Each Nadi Explained by Jagdish Raj Ratra, India, accessed on March 2, 2026, [https://saptarishisastrology.com/mystery-about-number-and-longitude-of-each-nadi-explained-by-jagdish-raj-ratra/](https://saptarishisastrology.com/mystery-about-number-and-longitude-of-each-nadi-explained-by-jagdish-raj-ratra/)  
27. Using Tattvas in Vedic Astrology by Vidhan Pandya \- YouTube, accessed on March 2, 2026, [https://www.youtube.com/watch?v=gmul2ub9Mvw](https://www.youtube.com/watch?v=gmul2ub9Mvw)  
28. The Pancha Tattwa: The Five Elements \- The Yogi Press, accessed on March 2, 2026, [https://www.yogi.press/home/article/the-pancha-tattwa-the-five-elements](https://www.yogi.press/home/article/the-pancha-tattwa-the-five-elements)  
29. The five elements in which you are born tell a lot about you. \- Astrovibes, accessed on March 2, 2026, [https://astrovibes.co.in/blogs/the-five-elements-in-which-you-are-born-tell-a-lot-about-you](https://astrovibes.co.in/blogs/the-five-elements-in-which-you-are-born-tell-a-lot-about-you)  
30. Understanding Panch Tatva in the Body | PDF | Human Body | Atmosphere Of Earth \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/doc/314434321/Panch-Tatva](https://www.scribd.com/doc/314434321/Panch-Tatva)  
31. Tatwa \- Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/220895732/Tatwa](https://www.scribd.com/document/220895732/Tatwa)  
32. Pindayu, Nisargayu and Amsayu. Mathematical Models for ... \- Medium, accessed on March 2, 2026, [https://medium.com/thoughts-on-jyotish/pindayu-nisargayu-and-a%C5%84%C5%9Bayu-f2eb23c45611](https://medium.com/thoughts-on-jyotish/pindayu-nisargayu-and-a%C5%84%C5%9Bayu-f2eb23c45611)  
33. Longevity Analysis using Amsayu method | Sithars Astrology, accessed on March 2, 2026, [https://sitharsastrology.com/blog/longevity-analysis-using-amsayu-method](https://sitharsastrology.com/blog/longevity-analysis-using-amsayu-method)  
34. Longevity \- Dr. Anuradha Rai \- Dubai based Astrologer, Numerologist, Vaastu Consultant & Vedic Life Coach, accessed on March 2, 2026, [https://dranuradharai.com/2018/01/25/longevity/](https://dranuradharai.com/2018/01/25/longevity/)  
35. I just wrote code to calculate the life span according to pindayurdaya method. \- Reddit, accessed on March 2, 2026, [https://www.reddit.com/r/hinduism/comments/uz1zrx/i\_just\_wrote\_code\_to\_calculate\_the\_life\_span/](https://www.reddit.com/r/hinduism/comments/uz1zrx/i_just_wrote_code_to_calculate_the_life_span/)  
36. Pindayu Chakra Path Analysis | PDF | Solar System | Esoteric Cosmology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/514677374/LONGEVITY-Notes](https://www.scribd.com/document/514677374/LONGEVITY-Notes)  
37. Amshayu: Longevity Calculation Method | PDF | Hindu Astrology | Planets \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/173404167/Amshayu-Main](https://www.scribd.com/document/173404167/Amshayu-Main)  
38. Thoughts on the Mathematical Ayur models and their usage in the Dasas such as Moola and Naisargika… \- Medium, accessed on March 2, 2026, [https://medium.com/thoughts-on-jyotish/thoughts-on-the-mathematical-ayur-models-and-their-usage-in-the-dasas-such-as-moola-and-naisargika-517dee1396ae](https://medium.com/thoughts-on-jyotish/thoughts-on-the-mathematical-ayur-models-and-their-usage-in-the-dasas-such-as-moola-and-naisargika-517dee1396ae)  
39. Longevity in Astrology | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/doc/155246602/Longevity-in-Astrology](https://www.scribd.com/doc/155246602/Longevity-in-Astrology)  
40. Ayur Jyotish Sketches In Astrological Longevity By Robert A. Koch, accessed on March 2, 2026, [https://saptarishisshop.com/ayur-jyotish-sketches-in-astrological-longevity-by-robert-a-koch/](https://saptarishisshop.com/ayur-jyotish-sketches-in-astrological-longevity-by-robert-a-koch/)  
41. Looking Back: An Update \- Vedic Astrology, accessed on March 2, 2026, [https://www.vedicastrologer.org/articles/vedic\_astro\_textbook.pdf](https://www.vedicastrologer.org/articles/vedic_astro_textbook.pdf)  
42. Astrology of Longevity Indicators | PDF \- Scribd, accessed on March 2, 2026, [https://pt.scribd.com/document/535059544/LONGIVITY-EXPLAINED](https://pt.scribd.com/document/535059544/LONGIVITY-EXPLAINED)  
43. Jaimini Jathaka Sara Sangraha | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/863539521/Jaimini-Jathaka-Sara-Sangraha](https://www.scribd.com/document/863539521/Jaimini-Jathaka-Sara-Sangraha)  
44. Death Rebirth mahasamadhi time \* BP Lama Jyotishavidya, accessed on March 2, 2026, [https://barbarapijan.com/bpa/Death/1Death\_main.htm](https://barbarapijan.com/bpa/Death/1Death_main.htm)  
45. Navamsha Lord in The Timing Death \- Astrology \- Scribd, accessed on March 2, 2026, [https://fr.scribd.com/document/250016147/Navamsha-Lord-in-the-Timing-Death](https://fr.scribd.com/document/250016147/Navamsha-Lord-in-the-Timing-Death)  
46. Change, Transformation, Endings, Death : r/Nakshatras \- Reddit, accessed on March 2, 2026, [https://www.reddit.com/r/Nakshatras/comments/1n68yl3/change\_transformation\_endings\_death/](https://www.reddit.com/r/Nakshatras/comments/1n68yl3/change_transformation_endings_death/)  
47. The 64th Navamsa | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/409898753/The-64th-Navamsa-docx](https://www.scribd.com/document/409898753/The-64th-Navamsa-docx)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAXCAYAAACmnHcKAAACc0lEQVR4Xu2Wz4tPURjG34mR0GyE/EqamixJbDQRihoJaVKzmp2wmAULUaY0jWQjSRQlKZGFnQULRZKYYmWa1aQslJQ/wDxP73n7vvf9nnPnJqPU/dRT977vuefc55z3nHtFWloWiqUx8L9yHnoJrYwJzwDUE4OJXmg1tApaFHKEHV+C3kAXQs7gc2ugfmhFyHms3QbRcT3LoEeihipsh0ahKeg39ES6B2FnV6FBUaProafQK2hjasP43nRteEPMn4SGRctjCHoHzaZr3+40dANaLtr2HHTFtdkP/Uq5CuOinY5BzyVvZhf0DdrpYgdFzV9L93yGM+m5nuJkK/TJ5cgW0T4+uBjbzYhWgMGX5vgGV4RminBQGsmZOSr68H3pzAYH5Yuwbsl8K0NjbH8HWuzi7Jdxlg55m+4jjHELkI+SKTFPnRmW2TGpbjaWBge46WIPoT2i9b5POiVIzoq2n5DqnuQqMG5jfk33EcZZXuQLtMPluqgzEzkiuuwnpHxYNIUv7l8+3hs0fTldL/GJHE3MjEC3oB/Qs5D7E3hS8cVfuFidGZZqI5qYMezE4YbeFnJNOSS6urtD/J+bITwISgPPB/cSV2NzTEi5T5o5E4Ml6sxw9sele3/YwDFeR5/oB88f42ulc8J9l7wZHgDHY7BEnRk7Pg+4GNuUZrEET8UHooYMmuBxbfD4z/XJmH+uljoz70U787O5KcXih7CE7bO7on8TJvbtP4hDoqvj34GGcwa7YB3aDEfZSnBGT0HT0D3odcrb700T7KOZ02fXjnAFWA2PodvQT2hdpcVf4DA0CV0UNbKQ8A+D41C8bmlpackzB+4ZkZv10Le9AAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACMAAAAZCAYAAAC7OJeSAAABsklEQVR4Xu2VzysFURTHj6Is/IoiisaO8gfYKSnKStgSC0mKnWzZSCSJhULK4pWiZKVkJUlsLKQoCxtZ+gP4fjvnzryZp1fP1BW9b316994zb+bMud97RqSof6RysGG/v65h8AEqkgHfKgGfRkMi5l1t4E00mY5EzKv6wDWYF02mJx72q1MwbTCZ3njYn1pBv42ZBJNhUt5VCpZAmc07wStYD6/wqEMwlzWncR9tPe3xrgaDUkCVX8AWWDbY8Lh2BCrDq36uEdFq5xV7yoLkvj3nrModCOKhglUHzkWtkFd7osl8J/rlHXQl1nn8afZxcACawapoNTN2TT1YtDGrwsPQIupJPjPnM8Oq3IP2ZMC0IrnHmzfZt/EZ2AGzoBtcgE2LcUuGbLwGbm1M0YthM62VqN07sjNlo0vGWWaWm5qwNT68ydb4YlegUXQ7tkGNxZ4kMi+fE0smjXgyeEPXh9zbM1EmwES4RZeiCVLZWx2AE1Bl81R6kOgTcSxaZSoAMzbmaXwGA2AM3IhuG73Farpello06K5BQzo5/9H0o6J+oqFZgUnRSnGrp9wfiirqz+sLpWxRZpRT1GYAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,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>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAZCAYAAABzVH1EAAACUElEQVR4Xu2WzatNURjGH6GkfETIR7lKMjBAlIlEyhUTZSgDEUWMZWCAiZTESPmaoETdgaGhkI8BAykikYEy8Qfw/HrX6qy929d1bkftk/2rp7PWu9ZZH+9617u21NHRMRHzrGcN2lJ2MseKNrSs2tweRqxf1qequcI363Dd2DamKTaCmlhvHbCm1BvayBPFRjbV7Het8zVbqzmn2MjJwjZdsZHZha31zLceWd+tbdYR63WlxxBxRnEqnM57a3e1eXgghNjIT0VY/S1zrD2qhuW/gDWtrBubmKHYCBe/X3ZZ2+vGAbNWEfITwkPIRngA+2GW9cCaWW8YIKT+i9biekMdTuOW4jSaOq9W3J1X1kFrqiIZjCpOg3DMMCmeW5X6/VCMzXt12rpkvbQ2pL6f1fuaoP5WEUaIkGVt+6yv1iLFF8m4jCgWeVUxYR1edbLZB/UexqfWBUWS4L8ZksTHok7iOKGY46xiDmwZxtyRyjjmeCozD3XYa31J5UbwXH7VS20sOyUY+HFRJ1WzkTeqXnROh81lnltLijoL35/KOI20T/pfY71TPMBsbGHqAw8VDhgIc1UdjAVz9PyWFx1HEG7AfwgrwiODZ/MXxHJFyOIkLnN5UiXY+72744IXTykmPWqtS/Z71gLFogCvEvOkc74M8C5hCXj+snrhyX3Bxths9oZ6ob3U2prK+VSvKO7rpMlZg0Vft+4XbYTWzdQHCFdC8I610xpT/AcIH04xwx1g8SQBWKEY67Z1LdngRapvLmyT4k/HPlQcUqTRjo7/hd99H3AdgZSTdwAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAAAXCAYAAACcTMh5AAADiElEQVR4Xu2Xy6vNURTHl1DKIylvda+UyCWRYnQnQqEMDJTBLQyEjEhi5JGSkoEBhSTvDIgyoJQUXRlQShlIysBE+QNYH2uv7j7rt8/vnHu63dHvU6vzW2u/v/t5RBoaGnpnotqsGGzonmdqf2NwjJjcwS8yRW2J2KxOCGkOcdLJR/7IYrWLaq/U9rYmFaG+A1KuC0hfL9Ze5IvajxgMHFHbGIMJ2qTu0ir+qLZfrP01ap8zv8IMtXtqu8QyLFR7pLY1z6RsS/G5Yttnt9otsfJAh5anb4c87aDjT9Ueqk0LadT/W+165n9TW+cZxFbfnsyPbBDLcyjE6e9PsfEC4/0ureMlnbKb1bYkn8lC8Ao0QOZcXYR4oTY7+YvUXqe4Q/4/akPJR9goxJng5xwTazcKSL0HxVaybx0mIhdjptqwWl/yIz45JQHxz0rreFlhjNdhJ10VE5B8A2qPk18BEdgOERq/mb4ZZOm8+ar2K32PZgWyCtgSl6Qq4GWxtiZlsalqh9Mv7JQ2qyHxRm2TVAVkNTFeBMmhH+TNjxImYH7m008mrgIF38agWJyOwIfkR2L8rtoKsZWDeL69I4iBaCUBP0m5rZzT0r5unxx2RBTweIqRluPxOcln1Z1Kv8B44kr+Dx2vE9BXF9+lQVEuzlwnGCBbFEoCelsP1K6lX1ZNLhhnYom1MjLpJQF9J0UByUN8MPm3s7R5avczv4VOArponQTMBajDzzcXIwpIurfll5qXuSGdJ4od4JPTi4DFM66O8Rbwjtj2daKA3p/YlsefhHjOKrEV6IyLgBzUdQJySQBXeBwUuIDdsEzsEKfzblfEbjduPRexTkDvT2RI7NDP6x4QK8Ntz9nGOcbNWifg6hDvijoBuSSg3cEeL5E6mF0Xp2S+UtzP6SSg36LtjHKIw+WDHwX0S6Q/xLsCceKLnrOGCnnJgzecPy2AS2Y4xLoFUdhS8RJ5KVUBp6dY3RaOIBhl8i28VGy88QnEcy222TUXpFq4T+xx6e86OsMs5u8ioByP0l5oJ6Bvp3yy+sUma0cW60RJQOpkvHkMWASMt2dWiv2dOS/2IudvVPwDjc9zgnTykZ9yvVDacvmgFoi19VztvVh/Ot3Ajl8eufkWdt6J9X+f2HhOSHW8o2a72jkZeYSW4LA/KralB0PaWMONelKsPdodS5gMxstCYLwNDQ0NDQ3jyz93RPz/UnHsCAAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAAAXCAYAAACcTMh5AAADoUlEQVR4Xu2Xy+tNURTHl1CSV+SVx++KlFAipZRfmVCYGShFYSCMxEC/mUcekUwkZSAJiSLKQPopQqIQRZSkDEyUP4D1uXsvZ5999jn33OvH6Hzq2737cfZee+3X2iINDQ29M1w1Mc5sqM9d1a84c4gY2SGdZJRqrrhZHRaVGVZnuqQbnaM6rRpUbc8XFZikmh1nBoxXTVWNiQs871Vf40xxNq4SZ2MV1Fsh6VX8WrVTnB+Wqt4F6QLjVFdVm8RVmKG6oVoX1bmkWixu6+xTfVPdV83ydTBogf9vbI7SK1W7VR/ErZ4z+eI2GMwAxvo0bdAX34UD4PttQRob74mzcYo4G6mDjSHUoz3GC4z3i+THSznfrlGt9WkmC4cX2COucmgcjqDjyT5NnYdZcZut4r4759Op1XI4Sp9VPVPtknIHXhBnMBMCtHld9VG1xOdNUD1X9fk0YKNNpvFTXD/hbqHeEcmPlxUWOpqddF6cA6m3SHXLpwvQCdshho4v+v9PfXpjVtyGPDuH6qxAA2eXOfC2uLL+II965G3xaewIVwPtpWw86fPYfsBqYrw4JMTat0mDO5I/BphEJq4AH9J5DPmP/X8b1OqsuE3oQLiiWihuxnEe2yVFlQOZ/QOSrRC28k3VZ9Vyn3dI8m3zHxu/S95G2138Au2Spv8Qy2frA30f9L/AeKyNHGyPKgdiUBnMBnVY/t1S5cCYa1IcNOdwHeymtp3BKorbAnN0v09fDsqmibMhSScHhqsrhkOXcmaqW+o4kHZZVZ/EnZm9wAKgH1tJnRyYPOOq6NWBJyRtSF3qONDgYuACOybp0CkF9bCRaCK0ccgdOEKqHcjNF7NedVzyB263dONA6BdX/0lcUAIhBzbGcLNWOdBu+a6ocuDLKI8Y7a3kV8Ky4H9dqhy4Q7U3ymNg1Gc7dwIbiQFDG+f7Xy6flAPtEmlF+bV4I8WIntVFgxhisJUIB8L4qaV6FKTrUubA0T4fcbwYbK06K/CBZCGL0ZIs5MGRjDcOiAnXaL8nLFYK6RN3u9rtZa8VnmmcLYjBv1K98HW6ocyBQD4vgxB7VVRdWNjICya0cVCcjS1fhyOL8cYhCUF5L9HEH3j+YDSdEpH/kPwWsCA1JQu262ABa6zwrJ0nLojFjlPiXiXYY0+7FExIlY3xec1riPFyXNDPgNS/oErZoDoqbgvEZ8T/hjhvv7gJ5fUxM1/81+BQxkv78ZZvaGhoaGj49/wGv4ft1XFK+a0AAAAASUVORK5CYII=>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAAAXCAYAAACcTMh5AAADTUlEQVR4Xu2Xz6tNURTHl1BvIEn5FfWelAglI7M3pDAzUAYKAyEjkpSBHym9kuEzk/xKBoqZgULolQGllJGUgYnyB7A+1l7ad519z9n3hlLnU6t71j57r/M966z944r09PSMz3y1pbGxp57Haj9i4x9iYYdfZEJtndhXnRfuObRzn370j6xVu6r2VO3Q4K0ixDsq5Vhdej6ofY6NYn23i41tg/j0K1XxW7UjYrG2qb3P/AaL1e6q7RPrsFrtgdquvJOyO7WvEJs++9Vuio0HBG1M1w59hoHwR2r31RZl7bV6qL6Doe2LWF9AIz4ac4hPO/GB+J9kMD73ib9DbWfy+VgkvMFxsc55dknEE7VlyV+j9iy1O/T/rnYg+SQ2TwRcDH7OabHnxgTW6FmiNqc2+buHaaRSco2XxDTmEJ/2PD7jiO8wk66LJZB+m9UeJr8BD2A6RHiJG+malyytNx/VvqbrUSqQKmBKXJNmAmv07JXBamA8cWayNtgqpnE6+VQT8UlIDjqIny8lzI5VmU98PlwDBr6KjWLtL9L1m+RHYvsdtU1iiy7J8+kdOSH20qUE1ui5IIOxp8S0UF053s7HgjNicZgtOd6+PPlU3fn0C7xPjP0LhLcJ9uriupRAxsUv1wUvfixdxwTW6mF9y2FqcT++JIkiFpWLRp9JMYG+bEwn/1Z2b6XavcwfoEuwJ60rgXkFtcEXJXlePaMmsKQBuhLoz+hKYHGNa6NW8DDxoybwttj0df77BC6QdsEswMAWXhLvCaxhg9gijni3WbHdjV2PF6zVE2FDQeOwBPKhgJ21LYFsOiPTJpgFGN4lPxI3kTa8SoaZv3yNnsh6MY0xgVNiY9gkgM2nlEDfRKZCexU8OJ7oJ8QCnky+P5gKyWFRnwtttfiUirtwjZ4SaKTCco3TYhonk++JjgdiNhnij8WMNAfzwPxQ6uep/FwEjONQOg7DElijpwQaX8qgRhJOLD+OkFzix0qlCIg/NlvE/s5cETuRf5PmH2h8DqHcpx/9GTcOfnDNLX+pGj0lzolpPCw29rmUNb4Wi08/4p+Vuvit7FG7LHbojGuEw2J/Smy6MD3+JjV6SqCR5KExnhcdlgTi04/4PT09PT09/5afTZj9dRCpy/UAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAAAXCAYAAACcTMh5AAADdklEQVR4Xu2YzYtPYRTHv0LJOzVe04xIYchLitVshEJZWCgLeVkoshpJrLykNIWFjWKykLcsvJVCWCgaWVCkLCYpCxvlD+B8neeYc8+9v/v7zTUzWdxPffvNOfftOd/nee7z3AFqamqqM1o0PSZrWueh6FdMDhFjm8SFjBMtgPbqqHAsslA0KSaF+aJzoueivdlDGSaKVommxAMBtmMttF2RT6KvMRnoFq2PyQTr5b2LRvE70X7o89nODy7OMVl0Q7QDesJc0R3RZnfONNEW0X3RN2jPb3THCRu0OOR2hnie6IWoK8VLoY1d+fcMhdPzh+iKi/tFa+wEaBv2uDiyDnrOwZBnvayB9RLW+wXZen2Nm1LMzqLhOfgAnuzdpRFPRG0pXiJ6LDovOopiA2dCR5bnVIh7kJ9230W9LmY7DkBHsk0ddoQ3Y6qoT9Se4ghH1QMUG8j4NLL1coSxXoMz6RK0Rp7XKbqb4hw/odMhwodfjUnoTYoMbGUE8rqXIXc75Y2LKR7jchNEh9Iv2Y4GoyHBZ2xA3kCOJtZLQzwXoOeyBoMdMNvFbCc7LgcvfBWTKC6WNDKQXIdOS44cmsfpYtAQXseGeNjTzI9P8fsUl3ES2Xt7mOf7ijMiGmizh8c8lp+RYo66E+mXsJ44kv/AKVdmIKdXpMzAMqygaKD1/qIU82/qluhy+uWo8YbxnVjEagx0epGBNtqjgfYa60rxNXdsluimizM0M5CKDJeBK6A9bs+1Rc3eib3ITrEiOAN4Lqli4GBr+u8MtPbE51r+Xsh7lkNHoDEiBtp7qZGBn2MS1Q3kC7jMQCuqzMCi9pBd0Jc+72HiQsFrjkDfbXyP2fu2kYHsxEFTZuDbmER1Azn9igy0omyFq2KgdUIj8Tqaw8WHcTTQFpGOkG8JrnpxR2/FcicfqWog4aIUO+UpdJHwcTSQXz3MlU3hCA3jNX4Kc6FivXELxO1afGbL9CB/cTt0cxn3deRfDOTo82aRftEzF9t08vvADqj521yuGUUG8p6s1+dIH7TeyiyDfs6che7I+RnlP6A55DnNbUp4xSnZDG5wP0I3xrznbuS/MedAjX4kegNtT7MV2LDFw8umsPEaWu8+aL3H0OI/DMrYKjqDgU3ocMJNNjsrfql4uKIeFx2GfloNJewM1ss2sN6ampqampqR5Te7e/gpkyP6pgAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAAAXCAYAAACcTMh5AAADd0lEQVR4Xu2Xy6tPURTHl1CSkPIK3d9NKaE8Jma3DFCYGSgDeQzuQEYmUgYeiW7JTCaShGRAzAhF6EYhpAwkZWCi/AGsz9173bvPOq99f90MdD717fdb+6yzztprP84+Ih0dHf0zXbXAN3bk80D1xzdOETNb7EpmqVZKGNVp7pphPkulOuig6oLqiepg8VKBOaqNqnn+QkJbPp9V332jBN/NEu5tgvj4Vc3id6phCbHI82Nil5iruqnaI8FhmeqOaofzuaZaJ2HpHFX9UD1UrYg+JLQ6/jf2Ohvfp6qhaK+RkOyGcY+8fIDZd8C1kRO+QJ7Y5J1CfNqJD8T/JsX4XCf+NtX2aDNYFLzEYQnOaXUpBMVZGG186HjKPgn3XYr2YgkzK+W0s0ekvOx+qq4kdk4+81WjqoFxD5HlEmZKOohnVL8TG4hPexqf+4hvsJIuSyggfmtVd6NdggewHDx04mr8/zLauycuj0GbFSRnBuL73LXdju1GTj7kkc4GBo44DFDKetUXmZjxzCbiU5CUixLi0wfjvoStyiA+A1eCGymQJ+3svWhvmbg8RlpAuCFhWbI/UjyWizFDgi+JpDDStM+Odk4+p6QYu6d6I2F2pVg7+xcckxCH1ZJi7Yuizaw7GX+B/vjYYzByTQmzvOpgNPBh+udA0lUFtNFfJfn5sL+lsLS47jvJM4nFzGV22Wz3BbRtYyja15NrS1S3ErtAW8KoDjZdrjNSObQVkOXWbz5tBeSZtsybCli5xzXRb8LnpTqRJv7LAtq+VJcwG7Bnp+qcFDfcHGzJ1xWQTvWTD/BC4ZhRV0CeAbbf1hWQQZw0TQmzAadwqPwgxUP0puR/ExS8qoDWKXvDTSYfg/3zvZQL2JNwDy8J4OVTVUB7ifRcexY82J/orbMcmA0OwcNSPD/1VM8Suw1eAr4Ij6R4VsvNx0NxGAxmsTEk4ZkD0bZC+wMxLxni98WIlG/mgemh1L4O+Exj/0Msi7eq19EnB2afP9h+VT1O7Jx8qmD5vZDi2Y2CE8sGneIS38/UUck/TVTCJxqfMxSGE/kvKS5TlhSJVMkOt7lsVX1SHZEQd7+UvzHb8qnjhIQBOiThXlYHsTyvJMTHj/jHJS9+I7tUZyUsU79HTDUcsumg/1JJ6TefQQmxWdL+vGiwJRAfP+J3dHR0dHT8W/4CrHcA3ztH570AAAAASUVORK5CYII=>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAAAXCAYAAACcTMh5AAADWElEQVR4Xu2Yy6tOYRTGH6GUSyj3wTkiuRwSKUYmQqEMDJSBwkDIiCRGLikpDAwoZOCegVsplImiIwNKKQNJGZgofwDrsfbqrG/td1++7fhM9q+eTu/ae7/vu573+h2gpaWlOSNFk2OwpT6PRb9icJgYXVFOMkY0BzqqI8KzyFzR+BgUZovOil6IdnY+SsJ29kDbTsHnK6H9inwUfY3BwAHRmhjMYJusOzWL34l2Q9tfJvrgyjkmiG6JtkJfmCW6J9rg3pkk2ih6KPoGHfl17jlhhxaE2LZQ9rDjj0R3RePCMy7PH6IrrvxZtMJegPZhhytHVkHf2RfizJc5MF/CfL+gM1+f4/qszMGi4TnYAF/27tKIZ6IpWXmh6KnonOgw0gZOQ96IE6HsOQStJxrIfuyFzmRbOhwIb8ZE0aCoLytHbHBSBrJ8Ep35coYxX4Mr6RI0R743ILqflXP8hC6HCBu/FoPQSlIGdjMDOQu4JM4jb+AFaP2jXGysaH/2l2xBwWzIeClai7yBnE3Ml4Z42A++67cSDsAMV2Y/OXA5+OGrGITG2ZFIkYHkpmgRdObQPBqVgmbQtJSB76H1l3EcxXXb4HBFRANt9fCZx+JTszJn3bHsL2E+cSb/gR0vM/B7DKLcwDowQS5RkjKQdVN3RJezv5w13jDuiSmWY2jQUwayrZSBfIfx1Vn5uns2XXTblTuoMjA1E/7GQNvfzIxoIJ9bu3ao2TdXUXxaG1wBNjhNDOw6p14beAO6fI1ooPUntmvxByHuWQKdgUZPDORGXWbgpxhEcwPnQzdxdt50EXq68dQzE8sMTPWHbIdu+r7uAeg3PO25t3Ef48laZuDSEK9FmYFvYxDNDbTvimQzxcqeKgPtFC0Sv6M5PHxYjgbaIdIf4rXgqRdv9NxrWCFv8pGmBkZoCpdUPESeI28gf/UwVraEIzSM3/glPA+ab7wC8boW26zNGeQ/7oNeLuO9jvxrA205+XtgP/RGsNnFqkgZyDqZr4+RQWi+jVkM/TlzGnoj588o/wOaU57L3C8LEw3oltSS80nNhF5dnojeQPtTdQIbdnh42RI2XkPz3QXN9whq/sOgjE2iUxi6hP5veKIeFR2EHjLDCQeD+XLCMN+WlpaWlpbe8huATu8WZ1kQEQAAAABJRU5ErkJggg==>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAAAXCAYAAACcTMh5AAADs0lEQVR4Xu2Xy6tPURTHl1DyTnmne6WUPPJIMboloVAGBsrg5jFQZEQSI49Et2SgpLhJ8sqAKANCUXRRCCmDm5SBifIHsD537+W3zzrnd37n/rru6Hzq2++39tnnnL2++3lEampq2mekaoovrKnOA9UfXzhEjG4RFzJGNU9Cr45w1wyrM1OKHzpXdVb1VLUreynDeNVy1SR/wUE7Vkl4p+eL6rsvdBxQrfWFEXLh2UWj+L1qj4T3085PSZxjouqGapuECrNVd1QbXZ2rqsUSpg4N+6F6pJoT69CgBfG/sd3F1H2m6orxQgmNXfavRoB3/FJdTuJ+1UqrIGH07Uxiz2oJdfa5cnKh7eQL5PtNsvlynXvXqzbEmM7C8By8gMqpuxiBOVNjTB0ST+mWcN+FGE+XMLJSTri4R/LT7qeqN4lpx14JI9lGOR2RmjFZ1afqiLGHUXVfig0kPinZfBlh5Gswky5KMJB6i1R3Y5zjt4Tp4OHlV+L/lzHe2rg8AGVmSJURSN0Xrux2LDfOx3hUUjZOtT/+Au0oHA0R3rFO8gYymsgXQ1LOSahLDgYdwFJl0E46Lgc3YpAnTfZejNc0Lg+QGgjXJUxLRg7mMV0MDKEuDUmhpykfG+MPMS7juGSfnUI56xUzwht4OJZxLcXKp8WYUXcs/gL5+JE8AFOuzECmVzPoDeow/KtgCXkDrffnx9g65ZbqUvxl1KSGsSYWsUIanV5koI12b6AtY10xvpZcm6G6mcQZWhmImsGiy3V6qgqtDFwqocftvbap2ZrYK9kpVgQzgLrQjoGFa1wZ7Rp4RoobUkYVA609/r1WzlLSjCUSRqAxLAbautTMwK++UNmkOi2tR4PHpnwzAy2pMgOL2gPdEhZ9nmFio+CeQxLWNtYxW2+bGUgnDpoyA9+6Mg6VHyV7iE57vQwMLzLQkrIdrh0DrROaifswh82nyEDbRDpdeSXY9fyJ3pLlwGxwCGZ3S89PnarnSdwKNiXfKY8lbBJp7A2cEMvKprAHw7gnncJsVOTrj0Ac1/w7K9Mj+Zs7JOyudq6zrxUOt6x/iF5/p3oT61SB0ZeaBf2qJ0ls0yk9B3ZKMH9LUtaKIgN5JvmmZdAn1U8ThfCJxucMxnAi5zMqnaZMcT8tTHbYrgoH3M8SDsY8d4fkvzFnSTD6oeq1hPZUXXNt80hlU9h4JSHf3RLyPSLF3/aDYrPqlDQOof8TDtl0lv9SSWFtPao6KOHTaiihM8iXNpBvTU1NTU3N8PIX1iMAacqRBvAAAAAASUVORK5CYII=>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAAAXCAYAAACcTMh5AAADoElEQVR4Xu2Xy6tPURTHl1CSd3mF7hUpr0IpBtwyoVAGBkoZYCCMxECMPPLoClMyMBAS5VWKuAZCSqFIUZIyUFL+ANbnrrP7rbPO+f1+597fZXQ+9e3evfb+7b3X2q91RGpqagbPcNWkaKypzn3Vn2gcIka2KZcySjVHbFWHhbrIXNXYaFRmq86q+lQ78lX98JtxwcbkpgYbjBezj4kVGR9V36JRzI/VqumxIkC7FVK+i9+qdonFYZnqvSsXwKFrqi1iDWaobqrWuzYTVRtUd1XfxVZ+rasHJjQ/2LaG8l6x33pdEes/wYRxIC0QfTDmHsk7wG+3uzJ+PFAtVk1R7c/aPHJtgHb0h7+Av18l76/3cV1WZrEIeIHklJ8cgWDgyVl5geqh6pzqoJQHsGy3HAvlGMAPYoH3XBKbcLLT5w3VJ9WSzDZB9UrVlZWBvme5MvwWG8cfQdodl7y/7DAfaE7SBTEfabdIdTsrF2AQjkOEgS9Ho1gnZQGsugMJRivuiPXf42znM9u2rLxZ8ruBxXsh1oa6RG9m4/gBuwl/CYgn9e8X857krwHmzcIV4IcMHsH+LBqleQDhqmqh2IoTvHjfVQkgq88uTzuEo3xL9UW1PLMdlXzf/E/gf6jWOHva8fyFdHrinZvsHH1g7CPZX8Cf1EcOjkerADKhSKsAtoNJcL8+EeuDoxqdiVyXotOkMFVIL3U6GSxe7AtSoHuyMvdyYprYHEppF0AU6TSAP1UrxVZ3k9gun+cbZbAD2FWfVbtDXVXYAMw17aR2ARywT/87gNwxpCce+uJeagYPw1PVSamYj4m1Oy22232whjyAI6R1AHn5Ip0EkOCxaB7GoL9o9/SItXkeK5pAynEqGsVe1lYBTK/8gGgVwNfRKJ0F8JdYzuWJAdyp2teo7gfHaMNxbgd5JDmg363piuDxKQtgekS6g70S76SY0XPU6JCJRDoJIL8jSY42BKNd2e/INGa7HfhYGilLolsaKQ+BxN+YEJOupTkMmF4p/rhLLLmMeR10EkACQJqSSFeIT2Ipx12avip4WJpBKsPi8CnJ/Yf6VG+ksbMYD39jSkJSjr+Dhs8fJs2gOMNR80fAJ6pR7fI6D59sF8U+CQkmj8fSXAv7ziaJZR5nxFId5lP27Z1oNT/kE2R4KeYv1wXjHJLqD1RTNqpOiB2BeEcMJaQUhzOtCnUJ8rwDYgvK18fMfHXHEFD8pf945Gtqampqav49fwHote7s3I4ZPgAAAABJRU5ErkJggg==>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAXCAYAAADpwXTaAAAAbklEQVR4XmNgGAWjgGpAEIjnoguSCziAeCG6ICVAFIi90QUpAbuAWBZdkFzACsR1QGwLxIzIEu5A7EsGzgHiLUBsxkAhMATicwwQF1IEWIC4i4EKBoGAKRAroguSAwQYIOFEFcAMxNrogqNgEAAAJuELtdtcUzIAAAAASUVORK5CYII=>

[image14]: <data:image/png;base64,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>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAAAXCAYAAACoNQllAAACq0lEQVR4Xu2XvWsVQRTFr6ggJn4T0iSdiEELRSwkRSSIFkkgRTorK8WkSCeioAgiSDpTRAVtFf8BwUgIEkhQEhJBQRTExsIyf0Byzrs7633X3dldv4v5wWGZO/P2zp6ZvbNPJJFIJP4/DkFbfBB0+wDYDe3yQdAJ9UF7fMc/omiOgf1Qv0TmegK6AK1AG9Az0Qe0sM04+63Goa1mXC80Dw1k7SPQAnQ8H/F3GIauQ19F53muvbvFEPRedJG3Q89Fx14St0FuQkvQpOigugZxrN9pU1mfZRB67GJ/mheiC3NVyg3iQnKBA13QLPQZOmXiOcGEmEFVcDKcmIW/9aYVsVN0JWPEXpUiaEyZQWGh95rY0Szmn6HFrxq0TfTmflyI04AYN6D7Pmg4C73xwQpiBq2L9u0wMdZZxhZNLKeOQZehT6I3WZX2FQ839wYRxln8q2A9eJJdLTSHdaUpMYOKGBMdf9t3kDoGTUM9oq5PQfegjmxMlUHHfLAEGkQFaM5b025CE4PCM65Bh11fi5hBxB+DLNBM/jpr/y6DSNhJXNFR+fEwqEsTg96JnnqluWIG8Sg/4GKEySnCYhczqOg7KsZH6BW0z3c0oI5BYTFO+g5PzKCHool4FFqsQXztigwKRdqeFlWw3lCc/FP5eZPqGHRX2k8t5jpt2jkxg16KJrLFM7xitj58g5ZNm3Dn8cSoC3eOLcjMydPNF+46xAzi/MdFP24t/HZ64GItYgaxqs+4GIs1k98yMf7Wm8GtO+diZdCYIR+U8tOtiphBzMWawx0UxBxfRE3KmZDvr4qXvTH/LnyAHmVXGlG09Xnq8BP+muj3BBOWFj7DReiMDxo6oCs+WALz+meh7OL7viC+BQPZmMaMQHdEt+ZB12c5L7oivDb9+k0kEolEoppNenyuplp+hxsAAAAASUVORK5CYII=>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAXCAYAAADtNKTnAAAA1ElEQVR4XmNgGAWEAAcQKwOxEBAzosmB+M5AfBKI10H5KIAPiFcAcQQDRFIaiNcCsTeSmskMEEtgYBoQqyLxGXKA+D8DqumaQLwHiQ9SgwxAfHdkgc9AfBNZAApABsNsJ+gSkOITyAJQABIXg7KzgLgNygaFWToDkst5GPAbYo8uiA0QMgTF37gAVQxhYcBviAG6IC6AzxAFdEFc4DIQP0ETA0UnyBCiQQ8DpgZ5IL6GJkYQ6ALxIyDuYoCk1A9AzIqigkjgC8TtQJwBxOJocqOA3gAAXGMqULYH4TsAAAAASUVORK5CYII=>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACkAAAAXCAYAAACWEGYrAAAB1UlEQVR4Xu2WzSsFURjGX6GEJIVEKEWKkpWyk7KQnWQnVoqslD0LJRtZ2Imdko1SlJJCpGyUUlays1H+AJ7nvnN07jsfZlY+ml/96s57Zs59zsyc916RnP9PHSy1xd9ELfyAK3aAVMAO0VWUmDEyAU/gDuwqHgrRKdFzOLrhoETfrR74Agf8Yg3cg5OiEzfDAzjqnTMUjDlaRBfjMw23RO/CPqwuHi5wCrdFw7XCd9HzmcGxDme84wLzoif6IbhSTlgfHPMcS585voGH8FiiQ5aJ3gw/0LLody+Jfj8f9RFs884pwNU82qLoxbvB5zR30sGAUSG5KM7JR+moFA3ODMNw3Ix/wQuvbVG0fhl8LocLsEp0lXxkccSF5HWc88HUN4L6iOhm4dMoghMlhXy1xRTEhYyiHd7BM9gg+q6GNtN3IWlWsoR0+2HKDvj8ZEhuIM6/aQcs3HFJIZ9sMQVpQs6JvkqhRxtHUki+L1lJE5KLZ192sLE3ecch7iW87fnrw5CLpp6GpJD98NYWwYXoJoqFHd6+e22irYJNPStJIc/hFVwL5C8U2xwbOBt5Ir3wWfRC/tK8ifbGLLiNZmX/I66ZRxn5ZyKKMbgKZ2GjGcvJyflLfAIByHC4ho3ruAAAAABJRU5ErkJggg==>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAXCAYAAACmnHcKAAACkElEQVR4Xu2WzauNURTGl0Ty/ZHkhlIGBgwoA0luKOregc9/wEiIkSTKQCZmZkgx8VFGQhm4RRJFBhQp6iZloKT8ATy/1l6dfbZ93nuO7h2o91dP9917v2ft/ey99nqvWUvLVDGr7PhfOS2NSUvKAVgsbZEWlAMFjA9ZfVcIfE56Lp0pxmpMk45YPdZ0aZm0QppRjM2W7pgb6mJE+iDNN//RI+m3dNh8smBUeiitMp/8pHTROhPx7vb0HDQZYvMeSHeluVk/cY5K+80NIZ5ZfLBT+mWVTXhq/uNgqfRYGpc2p76N0ntpU2oDgb5Ju1ObBbGTOZdSf41T5ptWmlkrvc7aAXMFnAhm/oKAaGHWty71kS7wLrXLhdHHGAxyMmQBJ4/Z0gx9X7N2wP0gveCNVVIMcMii8iNjh+l7mdoE72UGBTelYfPU2CGtzMYCTB83j1UzwyKJuSHrg/Hs+aN1Z0kjB8wDXkjtz6k9kZl+YPGR1jUz3EHuYsTeZ35f1mfvzMyeGyEwE7w1z194ZZNjhlO5bZ5mUDMDc6yTMehF93D/cNG5bHklI10oFPmdoDgMYoYF37LuuDUzjB8yr5bLrWMqLwATwm5xnE25yARPpBvSGhvMDMWEysd9DF2R7kmrrWPomXnJzplnbor07wvyNKoXLDK/zE1g5FPZ2YMw3kvH0nssulapLksnys6S+EiVlYeAV9PzXvNJ+BtQysu+QYi7WaZZLzMj1sdco+b5yMmESLcv1gnKrrF7fBuCg9J1q3yF+6SXGdIsz5CAk+GD3kh53KHv0rb0TpTL++nvD+laGvsXuPjlfJFmZMoe6af5v0+xsVvT+KTAh/CsuRkuf16VpoJd0vmk4e6hlpaWlow/BWKcAIkI+wMAAAAASUVORK5CYII=>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAXCAYAAAD6FjQuAAABdUlEQVR4Xu2UvytGYRTHj1DycxQxKIssUsrG5h+wKQMGYRKDMskgJRkNZqEMMipMdlZKUgaL8gfw/XbOcZ97uuXqZVD3W5/ee85z7jnd857niFT67+oAnaA1HgQxpgc0xgOoD+yCKzCbP1INg1vQZvYUeAGLoM6DzH4HLaAJrIItyYrSN2DPLubK6UA0OYMpftkJuAdDHmT2ZWIznu+Nm13Ulc1gyxn4AGOJb89802Z3mT3/FaGi786eS30Z+7wmWcvYzlPwCEbMNyqaeMJs17Noa12HYFC0tSzUnpwV6kg0MdviWjJfLMbW0v9jbYi29AEshLNfL+bqBdeSn7Q/K0ZxWJjkxuxJs2suNgeWg48jzyRsKeXFYzEOSOlizaLBJL0jTJp+GceaNqc2FX38n0uLLzwF34r5OTSuV9HL7moQjZlJfN+qH5yDC7AjuhXeJFtfLt6ZfXBsv4zpzkWUVL3ortsW3RpctEXixV830lVWqVJt+gTLWFFJCaQISQAAAABJRU5ErkJggg==>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAXCAYAAAD6FjQuAAABJElEQVR4XmNgGAXDBagBMSO6IBCIATEzmpgIEHMg8RWBuB+IDwBxMpI4HBgDcSIQnwfi/0C8Goh5UFRAwAkGiDwy9mNAOAxkqSaUDQPRaHyGBiA+CcQFQLyDgTjLPgPxMlRpBnEGTH0taHw4ACkEWYTPMnd0QSRAlM9ggFLLQGA5EGsDMSsDxCI+VGkEIMayUCB+zgAJyiMM2BMSUYAYy54CsRAQCwLxSiAuYYD4gmRAyDKQBcgG8zJAfLgJSYxoQMgyYQbMfAZLnSQDfJaJMkAMnY0mThPLQKUKKG91IInBgnEvkhjRAJ9loDxUzoCa+gwYIA6IRxIjCHIYMIshGEbOVx5AfAeIpwPxIyD+wIBaLlIdgIKuC4jjgFgGTW4UjALyAQDmbELsdFWysgAAAABJRU5ErkJggg==>

[image21]: <data:image/png;base64,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>

[image22]: <data:image/png;base64,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>

[image23]: <data:image/png;base64,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>

[image24]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAXCAYAAACMLIalAAAB1UlEQVR4Xu2VzSsFURjGX0nJ14Ik5eOurJWUou4tysJdEDsLkYWiWLCQ8pFspGQnOyvKlrKwQxKlLChZSVlY+gN4njnn3DlzzJ25V7mreepX877vmTnPnDnzHpFEiUqjDlDmJi01gV5Q4RYs1YMeUOkWtNbANVgBtU7NUxeYBA/gG5yAmsAIpVnwAsp1PApeQV1uhEgWfIgyTo3r2Izhy27oa6MhJ/a0Dm7BAjiX/KbuwbCTYzxhxZfgyYppYkv8MXzunl/2xBcIm88TCzSUz9Q76HNyDeAYVIm6hyu9Exgh0gk+QVqKWCmjOFOckCtqqxss6uuUqDFzuWowP6PjVpARtQ36wZHOhyrO1Laoh5MrUStkmxzUNdcUPw/zh06+IMWZqga74hu7Ae1WPc4Un1u04kxNidpXzWBffHNZXS+5qRZwKqr/GLG/8E/ihGOi+lKUKfevK0hRpgbAspOj2EA54byophtmKqXzYffH6i+mqC8woq85+YFVo9LgToL7r2BFmeLn47HQ5uS5UhegUcfs8PwBbLFlsIFGHV2/xOU2m9aFm9eI3fsZnIlqD2/g0apTNLkqyui0qDFsH/8qtoVNUaYykv9QXhI1hp/OnJWJEiUy+gH5zWlFy8r7pAAAAABJRU5ErkJggg==>

[image25]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAXCAYAAACMLIalAAACJklEQVR4Xu2Vz4uOURTHj1CT/Cib2TBGIQsLKWUjypTCf6DYWEzIlFhImSglkWxmoSyskJJkJRshSZlYWFGTjcVslD+A7+c957zvfe6888xrMSvvp7697zn33PPce8597mM2ZMjyskEaldbWA30gZo/5nH5slPZJI/VAMC29ky5L66qxDiT/Yr3B49JP6Yy0IoOCvdIHaX/YB6UL3VGzY+Zz2RxkrvVhk+9q/E+OVnaH++YTc1dU4Yn0TdqdQeaL/yqNhb1dmjWPzeq+iZiERVyXToZN3N3ecIe+3Xku/ZEOFD4m4jtR+H5LnwqbBx6RtoVNYubc6kY4bGzePP/AldoqXbJeq2jjU2nOvF1AFXkgVVmMcfOYs4v4J8PebN72ldIh6WH4W3lsniTPBbBLfDPSS+mc9MP8fCWHI6ZeFHnwP6j8A3HNvJXfpdPVGCUmMecsz16esZ1hL7WotiovCeV9Ld2QVoePB5GYtpbgnzNv87IuCrJd78OeCLt+c3Kx/HIvtS2qntvKKel85eONIRGthF1h14nLRe0o/peMh5+XaSDWmE9A5V2RrchKAfajwoYpa76lxNzrjjpU/aO0pfK3QiLepBJuafwc/oRDTvJklfkC7ljv7BFTbgTIxQVafx1a4fJ7Ib2Sbpvf7r9s4TeJB/Ot+mzeRmKeNSI85op5Lo4Fm33biPgHuMguSjfNb/FNzeEGXILE0Rbm9SNztcUMGfL/8hc5enac5JENrAAAAABJRU5ErkJggg==>