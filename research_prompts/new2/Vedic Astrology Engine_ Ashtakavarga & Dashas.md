# **Computational Architecture for Advanced Vedic Astrology: Ashtakavarga Reductions and Conditional Dasha Systems**

The translation of classical Vedic astrological principles into a deterministic computational engine requires a rigorous mathematical formalization of ancient heuristic frameworks. The algorithmic translation of treatises such as the Brihat Parashara Hora Shastra (BPHS) demands highly complex, conditional, and multi-layered processing to determine planetary strength and time life events accurately. This comprehensive architectural blueprint provides an exhaustive specification for implementing the complete Ashtakavarga reduction pipeline, alongside the nuanced computational rules for six critical Dasha systems. The ensuing analysis formalizes the geometric, mathematical, and astronomical rules required to build a high-fidelity, computationally exact Jyotish engine.

## **Part A: Complete Ashtakavarga Reduction and Advanced Usage**

The Ashtakavarga system functions as a multi-dimensional matrix that quantifies planetary support across the zodiac. The initial raw computation yields the Bhinna Ashtakavarga (BAV) for the seven classical physical planets and the aggregate Sarvashtakavarga (SAV). However, these raw scores contain inherent redundancies due to the elemental symmetries of the zodiac and the dual planetary lordships governing the signs. To distill this raw data into the true, operative strength of a planet, the computational engine must execute two sequential reduction algorithms: Trikona Shodhana (Triangular Reduction) and Ekadhipatya Shodhana (Dual Lordship Reduction). These reductions are the strict prerequisite for computing the Shodhya Pinda (Corrected Aggregate), which serves as the ultimate metric for transit forecasting.

### **Trikona Shodhana (Triangular Reduction) Algorithm**

The Trikona Shodhana algorithm is designed to eliminate geometric redundancies within the elemental trines of the astrological chart. The underlying astrological theory postulates that signs located 120 degrees apart share a harmonious elemental resonance, and energy distributed evenly across them constitutes a baseline state that must be subtracted to find the true, exceptional strength of a planet.1

The twelve zodiac signs are partitioned into four distinct groups of three mutually trinal signs, categorized by their elemental nature:

1. **Fire (Agni) Trine:** Aries (1), Leo (5), Sagittarius (9).1  
2. **Earth (Prithvi) Trine:** Taurus (2), Virgo (6), Capricorn (10).1  
3. **Air (Vayu) Trine:** Gemini (3), Libra (7), Aquarius (11).1  
4. **Water (Jala) Trine:** Cancer (4), Scorpio (8), Pisces (12).1

#### **Algorithmic Rules for Trikona Reduction**

For each of the four trinal groups in a planet's Bhinna Ashtakavarga, the computational engine must evaluate the integer values of bindus (benefic points) residing in the three constituent signs. The algorithm applies the following mutually exclusive rules to each trine independently:

1. **The Zero Condition:** If any single sign within the three-sign trinal group contains exactly zero bindus, the algorithm terminates for that specific trine. No reduction is performed, and the original values of all three signs are retained in the array.1  
2. **The Equality Condition:** If all three signs within the trinal group contain an identical, non-zero number of bindus, the mathematical redundancy is considered absolute. The algorithm must reduce the bindu values of all three signs to zero.1  
3. **The Unequal Condition:** If the three signs contain varying, non-zero numbers of bindus, the engine must identify the absolute minimum value among the three integers. This minimum baseline value is then subtracted from the current value of all three signs. Consequently, the sign that originally held the minimum value will be reduced to zero, while the others will retain the mathematical difference.1

#### **Step-by-Step Computational Walkthrough**

To ensure exact implementation, consider a raw Bhinna Ashtakavarga integer array for the planet Mars across the 12 signs (index 1 to 12):

* Aries (1) \= 4 bindus  
* Taurus (2) \= 5 bindus  
* Gemini (3) \= 3 bindus  
* Cancer (4) \= 4 bindus  
* Leo (5) \= 2 bindus  
* Virgo (6) \= 4 bindus  
* Libra (7) \= 4 bindus  
* Scorpio (8) \= 2 bindus  
* Sagittarius (9) \= 0 bindus  
* Capricorn (10) \= 3 bindus  
* Aquarius (11) \= 5 bindus  
* Pisces (12) \= 1 bindu

**Execution of the Algorithm:**

* **Evaluating the Fire Trine (Aries, Leo, Sagittarius):** The engine retrieves the values (4, 2, 0). Because the value for Sagittarius is exactly 0, the Zero Condition is triggered. The engine bypasses reduction. *Resulting array values: Aries=4, Leo=2, Sagittarius=0.*  
* **Evaluating the Earth Trine (Taurus, Virgo, Capricorn):** The engine retrieves the values (5, 4, 3). All values are non-zero and unequal, triggering the Unequal Condition. The minimum value is 3\. The engine subtracts 3 from all constituents. *Resulting array values: Taurus (5-3)=2, Virgo (4-3)=1, Capricorn (3-3)=0.*  
* **Evaluating the Air Trine (Gemini, Libra, Aquarius):** The engine retrieves the values (3, 4, 5). All values are non-zero and unequal. The minimum value is 3\. The engine subtracts 3 from all constituents. *Resulting array values: Gemini (3-3)=0, Libra (4-3)=1, Aquarius (5-3)=2.*  
* **Evaluating the Water Trine (Cancer, Scorpio, Pisces):** The engine retrieves the values (4, 2, 1). All values are non-zero and unequal. The minimum value is 1\. The engine subtracts 1 from all constituents. *Resulting array values: Cancer (4-1)=3, Scorpio (2-1)=1, Pisces (1-1)=0.*

The post-Trikona Shodhana array is structurally modified and passed immediately into the Ekadhipatya Shodhana function.

### **Ekadhipatya Shodhana (Dual Lordship Reduction) Algorithm**

The Ekadhipatya Shodhana algorithm is processed sequentially after the Trikona reduction is completed. This mathematical operation addresses the redundancy of a single planetary entity projecting its influence across two separate zodiacal signs.3 Because the Sun and the Moon only govern one sign each (Leo and Cancer, respectively), these two signs are completely excluded from the Ekadhipatya reduction. Their post-Trikona values remain permanently untouched by this second algorithm.2

The algorithm pairs the remaining ten signs based on their shared planetary lordship:

* Mars dictates Aries & Scorpio.2  
* Venus dictates Taurus & Libra.2  
* Mercury dictates Gemini & Virgo.2  
* Jupiter dictates Sagittarius & Pisces.2  
* Saturn dictates Capricorn & Aquarius.2

#### **Algorithmic Rules for Dual Lordship Reduction**

For each of the five planetary pairs, the computational engine must evaluate two specific variables: the scalar integer of bindus remaining after Trikona Shodhana, and a Boolean flag indicating the physical presence of any natal planet (excluding the lunar nodes, Rahu and Ketu) occupying those signs in the birth chart.3

The engine applies the following exhaustive logical conditions:

1. **Rule 1 (Both Empty, Equal Values):** If neither sign contains a physical planet, and their post-Trikona bindu values are exactly equal, the engine reduces both values to zero.3  
2. **Rule 2 (Both Empty, Unequal Values):** If neither sign contains a physical planet, and their bindu values are unequal, the engine isolates the smaller number and sets the value of both signs to match this smaller integer.3  
3. **Rule 3 (Both Occupied):** If both signs in the pair contain at least one physical planet, the engine performs no reduction. Both values remain unchanged.3  
4. **Rule 4 (One Occupied, One Empty, Occupied ![][image1] Empty):** If one sign is occupied by a planet and the other is empty, and the occupied sign possesses an equal or greater number of bindus compared to the empty sign, the engine reduces the empty sign's value to zero. The occupied sign's value is kept unchanged.3  
5. **Rule 5 (One Occupied, One Empty, Occupied ![][image2] Empty):** If one sign is occupied and the other is empty, and the occupied sign has strictly fewer bindus than the empty sign, the engine must subtract the occupied sign's value from the empty sign's value. The new value of the empty sign becomes the remainder of this subtraction, while the occupied sign remains unchanged.3  
6. **Rule 6 (The Zero Condition):** If either sign in the paired relationship has been reduced to zero by the previous Trikona Shodhana, the Ekadhipatya algorithm is aborted for this specific pair. No reduction is performed on either sign.3

#### **Step-by-Step Computational Walkthrough**

Continuing from the output array of the previous Trikona example, the post-Trikona values are: Aries=4, Taurus=2, Gemini=0, Cancer=3, Leo=2, Virgo=1, Libra=1, Scorpio=1, Sagittarius=0, Capricorn=0, Aquarius=2, Pisces=0.

Assume the astrological engine identifies the following natal planetary placements: The Moon is in Aries, the Sun is in Virgo, and Venus is in Libra. All other signs are devoid of planets.

**Execution of the Algorithm:**

* **Cancer & Leo:** Excluded from the algorithm. Values remain Cancer=3, Leo=2.  
* **Mars Pair (Aries & Scorpio):** Aries has 4 bindus and is Occupied (by the Moon). Scorpio has 1 bindu and is Empty. The condition is "One Occupied, One Empty, Occupied \> Empty." Rule 4 applies. The engine reduces the empty sign (Scorpio) to 0\. *Result: Aries=4, Scorpio=0.*  
* **Venus Pair (Taurus & Libra):** Taurus has 2 bindus and is Empty. Libra has 1 bindu and is Occupied (by Venus). The condition is "One Occupied, One Empty, Occupied \< Empty." Rule 5 applies. The engine subtracts the occupied value (1) from the empty value (2). The new value for Taurus is ![][image3]. *Result: Taurus=1, Libra=1.*  
* **Mercury Pair (Gemini & Virgo):** Gemini has 0 bindus and is Empty. Virgo has 1 bindu and is Occupied. Because one of the signs (Gemini) is already at zero, Rule 6 applies. The engine bypasses reduction. *Result: Gemini=0, Virgo=1.*  
* **Jupiter Pair (Sagittarius & Pisces):** Both signs have 0 bindus. Rule 6 applies. *Result: Sagittarius=0, Pisces=0.*  
* **Saturn Pair (Capricorn & Aquarius):** Capricorn has 0 bindus and Aquarius has 2\. Because Capricorn is 0, Rule 6 applies. *Result: Capricorn=0, Aquarius=2.*

This final array matrix represents the fully reduced Bhinna Ashtakavarga, ready to be utilized in the calculation of the Shodhya Pinda.

### **Shodhya Pinda Computation**

The Shodhya Pinda (Purified Aggregate) serves as the ultimate scalar metric of a planet's static and dynamic capacity to deliver results during its Dasha and transit periods. It is mathematically defined as the sum of two separate vector dot products: the Rashi Pinda (Sign Aggregate) and the Graha Pinda (Planetary Aggregate).6

#### **Mathematical Formulation**

The Shodhya Pinda (![][image4]) for a specific planet's Ashtakavarga is defined as:

![][image5]  
Where ![][image6] (Rashi Pinda) is the summation of the products obtained by multiplying the fully reduced bindu value of each sign by its corresponding fixed sign multiplier, and ![][image7] (Graha Pinda) is the summation of the products obtained by multiplying the reduced bindus of only those signs that are physically occupied by planets by the fixed planetary multipliers.7

#### **Multiplier Constants**

The astrological engine must store two constant arrays of multipliers.

**Rashi Gunakara (Sign Multipliers):**

* Aries: 7  
* Taurus: 10  
* Gemini: 8  
* Cancer: 4  
* Leo: 10  
* Virgo: 5  
* Libra: 7  
* Scorpio: 8  
* Sagittarius: 9  
* Capricorn: 5  
* Aquarius: 11  
* Pisces: 12 6

**Graha Gunakara (Planet Multipliers):**

* Sun: 5  
* Moon: 5  
* Mars: 8  
* Mercury: 5  
* Jupiter: 10  
* Venus: 7  
* Saturn: 5 6

#### **Algorithmic Computation**

1. **Rashi Pinda (![][image6]) Loop:** The engine initiates a loop from index 1 to 12 (representing the zodiac signs). For each index, it retrieves the fully reduced bindu value from the Ekadhipatya Shodhana output. It multiplies this integer by the corresponding Rashi Gunakara constant. The 12 resulting products are aggregated to form the total Rashi Pinda.7  
   ![][image8]  
2. **Graha Pinda (![][image7]) Loop:** The engine initiates a loop iterating through the seven physical planets. For each planet, it identifies the exact zodiac sign it occupies in the natal chart. It retrieves the fully reduced bindu value for that specific occupied sign from the current planet's Ashtakavarga chart. It multiplies that bindu value by the occupying planet's Graha Gunakara constant. If multiple planets occupy the same sign, the bindu value of that sign is multiplied by each respective planet's multiplier separately, and the results are added together to form the total Graha Pinda.7  
   ![][image9]  
3. **Final Shodhya Pinda:** The engine adds the computed ![][image6] and ![][image7] integers together. This final composite integer is then utilized in advanced transit forecasting. For instance, multiplying the Shodhya Pinda by 7 and dividing the product by 27 yields a remainder that maps to a specific Nakshatra; transits of malefic planets over this computed star sequence are mathematically proven to correlate with critical life challenges or mortality.6

### **Prastharashtakavarga: The 8-Row Kakshya Matrix**

While the Bhinna Ashtakavarga provides the aggregate sum of benefic bindus per sign, it lacks the temporal granularity required for micro-forecasting. The Prastharashtakavarga (PAV) system solves this by unpacking the precise spatial geometry of *which* specific planetary contributor granted *which* bindu in the final sum. This allows the computational engine to pinpoint transit timing down to fractions of a sign based on the concept of Kakshyas.10

A Kakshya is an exact one-eighth division of a 30-degree zodiac sign, meaning each Kakshya spans exactly 3 degrees and 45 minutes of arc.10 The rulership of these eight Kakshyas strictly follows the descending order of planetary orbital velocity from the geocentric perspective: Saturn rules the first Kakshya (0° to 3°45'), followed sequentially by Jupiter, Mars, the Sun, Venus, Mercury, the Moon, and finally the Ascendant (Lagna) ruling the eighth Kakshya (26°15' to 30°00').10 When a transiting planet enters a sign, it traverses these eight Kakshyas in order. If the lord of the current Kakshya contributed a bindu in the PAV matrix, the transit yields demonstrably positive results specifically during the time it takes to transit those 3°45'.11

#### **The Complete 7x8 Contribution Matrix**

To generate the complete 337-bindu network, the engine must establish a three-dimensional matrix for each planet's PAV. The following tables define the exact houses (calculated relative to the contributor's natal position) where a bindu of value '1' is injected. The engine iterates through the natal positions of all 8 contributors, projecting 1s into the respective relative indices of the planet's PAV matrix.14

**1\. Sun's Prastharashtakavarga (Total: 48 Bindus)** 14

| Contributor | Houses from Contributor's Natal Position Receiving a Bindu | Total |
| :---- | :---- | :---- |
| **Sun** | 1, 2, 4, 7, 8, 9, 10, 11 | 8 |
| **Moon** | 3, 6, 10, 11 | 4 |
| **Mars** | 1, 2, 4, 7, 8, 9, 10, 11 | 8 |
| **Mercury** | 3, 5, 6, 9, 10, 11, 12 | 7 |
| **Jupiter** | 5, 6, 9, 11 | 4 |
| **Venus** | 6, 7, 12 | 3 |
| **Saturn** | 1, 2, 4, 7, 8, 9, 10, 11 | 8 |
| **Lagna** | 3, 4, 6, 10, 11, 12 | 6 |

**2\. Moon's Prastharashtakavarga (Total: 49 Bindus)** 14

| Contributor | Houses from Contributor's Natal Position Receiving a Bindu | Total |
| :---- | :---- | :---- |
| **Sun** | 3, 6, 7, 8, 10, 11 | 6 |
| **Moon** | 1, 3, 6, 7, 10, 11 | 6 |
| **Mars** | 2, 3, 5, 6, 9, 10, 11 | 7 |
| **Mercury** | 1, 3, 4, 5, 7, 8, 10, 11 | 8 |
| **Jupiter** | 1, 4, 7, 8, 10, 11, 12 | 7 |
| **Venus** | 3, 4, 5, 7, 9, 10, 11 | 7 |
| **Saturn** | 3, 5, 6, 11 | 4 |
| **Lagna** | 3, 6, 10, 11 | 4 |

**3\. Mars' Prastharashtakavarga (Total: 39 Bindus)** 14

| Contributor | Houses from Contributor's Natal Position Receiving a Bindu | Total |
| :---- | :---- | :---- |
| **Sun** | 3, 5, 6, 10, 11 | 5 |
| **Moon** | 3, 6, 11 | 3 |
| **Mars** | 1, 2, 4, 7, 8, 10, 11 | 7 |
| **Mercury** | 3, 5, 6, 11 | 4 |
| **Jupiter** | 6, 10, 11, 12 | 4 |
| **Venus** | 6, 8, 11, 12 | 4 |
| **Saturn** | 1, 4, 7, 8, 9, 10, 11 | 7 |
| **Lagna** | 1, 3, 6, 10, 11 | 5 |

**4\. Mercury's Prastharashtakavarga (Total: 54 Bindus)** 14

| Contributor | Houses from Contributor's Natal Position Receiving a Bindu | Total |
| :---- | :---- | :---- |
| **Sun** | 5, 6, 9, 11, 12 | 5 |
| **Moon** | 2, 4, 6, 8, 10, 11 | 6 |
| **Mars** | 1, 2, 4, 7, 8, 9, 10, 11 | 8 |
| **Mercury** | 1, 3, 5, 6, 9, 10, 11, 12 | 8 |
| **Jupiter** | 6, 8, 11, 12 | 4 |
| **Venus** | 1, 2, 3, 4, 5, 8, 9, 11 | 8 |
| **Saturn** | 1, 2, 4, 7, 8, 9, 10, 11 | 8 |
| **Lagna** | 1, 2, 4, 6, 8, 10, 11 | 7 |

**5\. Jupiter's Prastharashtakavarga (Total: 56 Bindus)** 14

| Contributor | Houses from Contributor's Natal Position Receiving a Bindu | Total |
| :---- | :---- | :---- |
| **Sun** | 1, 2, 3, 4, 7, 8, 9, 10, 11 | 9 |
| **Moon** | 2, 5, 7, 9, 11 | 5 |
| **Mars** | 1, 2, 4, 7, 8, 10, 11 | 7 |
| **Mercury** | 1, 2, 4, 5, 6, 9, 10, 11 | 8 |
| **Jupiter** | 1, 2, 3, 4, 7, 8, 10, 11 | 8 |
| **Venus** | 2, 5, 6, 9, 10, 11 | 6 |
| **Saturn** | 3, 5, 6, 12 | 4 |
| **Lagna** | 1, 2, 4, 5, 6, 7, 9, 10, 11 | 9 |

**6\. Venus's Prastharashtakavarga (Total: 52 Bindus)** 14

| Contributor | Houses from Contributor's Natal Position Receiving a Bindu | Total |
| :---- | :---- | :---- |
| **Sun** | 8, 11, 12 | 3 |
| **Moon** | 1, 2, 3, 4, 5, 8, 9, 11, 12 | 9 |
| **Mars** | 3, 5, 6, 9, 11, 12 | 6 |
| **Mercury** | 3, 5, 6, 9, 11 | 5 |
| **Jupiter** | 5, 8, 9, 10, 11 | 5 |
| **Venus** | 1, 2, 3, 4, 5, 8, 9, 10, 11 | 9 |
| **Saturn** | 3, 4, 5, 8, 9, 10, 11 | 7 |
| **Lagna** | 1, 2, 3, 4, 5, 8, 9, 11 | 8 |

**7\. Saturn's Prastharashtakavarga (Total: 39 Bindus)** 14

| Contributor | Houses from Contributor's Natal Position Receiving a Bindu | Total |
| :---- | :---- | :---- |
| **Sun** | 1, 2, 4, 7, 8, 10, 11 | 7 |
| **Moon** | 3, 6, 11 | 3 |
| **Mars** | 3, 5, 6, 10, 11, 12 | 6 |
| **Mercury** | 6, 8, 9, 10, 11, 12 | 6 |
| **Jupiter** | 5, 6, 11, 12 | 4 |
| **Venus** | 6, 11, 12 | 3 |
| **Saturn** | 3, 5, 6, 11 | 4 |
| **Lagna** | 1, 3, 4, 6, 10, 11 | 6 |

## ---

**Part B: Missing Dasha Systems \- Complete Computation Rules**

While the 120-year Vimshottari Dasha serves as the foundational timing mechanism in Vedic astrology, classical literature mandates the implementation of specific conditional and structural Dasha systems to resolve complex chart timing when precise mathematical conditions are met. An advanced computational engine must be programmed to dynamically assess birth parameters to trigger the appropriate predictive framework automatically.

### **1\. Yogini Dasha (36-Year Cycle)**

Yogini Dasha operates on a highly compressed, rapid 36-year repeating cycle. It represents the manifestation of specific feminine planetary deities (Yoginis) and is considered uniquely potent for diagnosing health patterns, sudden karmic shifts, and micro-timing events within the framework of the Kali Yuga.19

* **Eligibility Conditions:** The Yogini Dasha is universally applicable and should be rendered in tandem with the Vimshottari Dasha. It is particularly effective for confirming major life transitions and assessing periods of high volatility or sudden fortune.19  
* **Sequence and Durations:** The sequence consists of eight periods, expanding incrementally in duration from 1 to 8 years.  
  1. Mangala (Ruled by Moon) – 1 Year  
  2. Pingala (Ruled by Sun) – 2 Years  
  3. Dhanya (Ruled by Jupiter) – 3 Years  
  4. Bhramari (Ruled by Mars) – 4 Years  
  5. Bhadrika (Ruled by Mercury) – 5 Years  
  6. Ulka (Ruled by Saturn) – 6 Years  
  7. Siddha (Ruled by Venus) – 7 Years  
  8. Sankata (Ruled by Rahu) – 8 Years 19  
* **Starting Point Calculation:** The engine computes the operative Yogini at the moment of birth based on the Moon's natal Nakshatra index (an integer from 1 to 27, where Ashwini \= 1). The formula is determined as follows:  
  ![][image10]  
  If the modulo operation yields a remainder of 0, it is computationally treated as 8, triggering the Sankata Dasha.22 The exact mathematical balance of the Dasha remaining at birth is interpolated proportionally based on the un-traversed longitudinal degrees of the Moon within that specific 13°20' Nakshatra span, exactly mirroring the proportion method utilized in Vimshottari.22  
* **Sub-Periods (Antardashas):** The internal sub-divisions are calculated proportionally. The algorithm follows the formula:  
  ![][image11]  
  The internal sequence always initiates with the ruler of the overarching Mahadasha and proceeds circularly through the standard sequence.19

### **2\. Kalachakra Dasha (The Wheel of Time)**

Declared by Sage Parashara as the most sovereign of all Dasha systems, the Kalachakra Dasha is an incredibly intricate framework relying heavily on spiral time mathematics. Unlike Vimshottari which maps to the 27 Nakshatras, Kalachakra derives its flow from the 108 Nakshatra Padas (quarters), explicitly linking it to the Navamsa (D-9) harmonic chart.25 It defines a maximum theoretical longevity cycle of 144 years.25

* **Eligibility Conditions:** The system is universally applicable but is exceptionally sensitive to precision. Because the calculations pivot on the Moon's exact fractional placement within a 3°20' Pada, any slight deviation in birth time or Ayanamsa renders the output invalid.27  
* **Structural Mechanics (Savya and Apasavya):** The core algorithmic pathway rests on identifying the directional spin of the "Wheel" based on the exact Nakshatra Pada occupied by the Moon. The 27 Nakshatras are divided into specific Savya (Clockwise/Zodiacal) and Apasavya (Counter-Clockwise/Anti-Zodiacal) groupings.  
  * **Savya Groups:** Includes Aswini, Krittika, Punarvasu, Aslesha, Hasta, Swati, Moola, Uttarashadha, Purvabhadra, Revati (Group 1\) and Bharani, Pushyami, Chitra, Purvashadha, Uttarabhadra (Group 2). If the Moon is in Pada 1, 2, 3, or 4 of these stars, the sequence generally moves forward through the zodiac.28  
  * **Apasavya Groups:** Includes Rohini, Mrigasira, Ardra, Magha, Purvaphalguni, Uttaraphalguni, Visakha, Anuradha, Jyeshta, Sravana, Dhanishtha, Satabhisha. The progression here generally moves backward through the zodiac.28  
* **Sequence and Durations:** Kalachakra is a *Sign-based* dasha, not a planet-based one. However, the duration of each sign's period depends exclusively on its planetary lord:  
  * Aries & Scorpio (Mars): 7 Years  
  * Taurus & Libra (Venus): 16 Years  
  * Gemini & Virgo (Mercury): 9 Years  
  * Cancer (Moon): 21 Years  
  * Leo (Sun): 5 Years  
  * Sagittarius & Pisces (Jupiter): 10 Years  
  * Capricorn & Aquarius (Saturn): 4 Years 25  
* **Starting Point Calculation:** The starting Dasha corresponds to the Navamsa sign mapped to the specific Nakshatra Pada. For example, in a Savya progression, Pada 1 initiates the sequence from Aries, Pada 2 from Capricorn, Pada 3 from Taurus, and Pada 4 from Cancer. The sequence then flows through 9 distinct sign periods, representing the span of life. The exact mathematical balance of the first period is formulated based on the longitudinal fraction of the specific 3°20' Pada left to be traversed.25  
* **Gati (Jump) Algorithms:** The most critical computational feature of Kalachakra is its defiance of standard zodiacal sequences through violent systemic jumps, known as Gatis. These topological leaps indicate massive paradigm shifts, crises, or ascensions in the native's life.31 The engine must codify these index manipulations precisely:  
  1. **Manduka Gati (Frog's Leap):** A jump that skips one entire adjacent sign. Mathematically, ![][image12]. Examples include transitioning directly from Virgo to Cancer, or from Leo to Gemini. Classically, this leap indicates sudden distress, aggressive locational shifts, conflict with authority, or the contraction of illness.26  
  2. **Markati Gati (Monkey's Leap):** A temporary reversal of the wheel's forward or backward momentum. Mathematically, ![][image13]. For instance, moving from Cancer backward to Leo during a sequence that is otherwise moving forward (Savya). This creates immediate, localized disruptions, financial recalculations, or temporary losses before restoring the original trajectory.26  
  3. **Simhavalokana Gati (Lion's Leap):** A massive trinal (5th or 9th house) leap across the wheel. Mathematically, ![][image14] or ![][image15]. Examples include jumping from Pisces directly to Scorpio, or Sagittarius to Aries. This signals severe transformation, paradigm destruction, animal attacks, fatal injury, or complete systemic collapse followed by a total rebuild.26

### **3\. Narayana Dasha (Jaimini Sign-Based Progression)**

Narayana Dasha is the most versatile Rasi-based (sign-based) Dasha within the Jaimini paradigm. While Vimshottari maps the internal, psychological, and reactive states of the mind (governed by the Moon), Narayana Dasha maps the external, deterministic environmental shifts, physical socio-economic circumstances, and status.35

* **Eligibility Conditions:** Universally applicable in all charts. It provides an environmental macro-context and must operate in parallel with a Nakshatra-based dasha.36  
* **Starting Point (Arambha Rasi):** The sequence initiates from either the Ascendant (Lagna) or the 7th house, but the choice is governed by strict Jaimini strength algorithms.38 The computational engine must iterate through the following conditional rules to determine the stronger sign, breaking the loop immediately when a tie is resolved:  
  1. The sign containing a greater absolute number of physical planets is declared stronger.39  
  2. If the planet count is tied, the sign aspected by Jupiter, Mercury, or its own lord (strictly using Jaimini Rasi Drishti/Sign Aspects, not planetary aspects) is declared stronger.39  
  3. If still tied, the sign harboring an exalted planet is declared stronger.39  
  4. If still tied, the engine applies the natural strength hierarchy: Dual signs ![][image16] Fixed signs ![][image16] Movable signs.39  
  5. If still tied, the engine evaluates the odd/even lord placement logic: For an even sign, if its lord is placed in an odd sign, it gains strength; for an odd sign, if its lord is placed in an even sign, it gains strength.39  
  6. If still tied, the sign that yields a higher calculated Dasa duration (explained below) is deemed stronger and serves as the starting point.39  
* **Sign Sequence Progression:** Once the starting sign is determined, the pathway depends entirely on the modality of that initiating sign:  
  * **Movable Sign:** The sequence progresses regularly to adjacent signs (e.g., 1, 2, 3, 4...).40  
  * **Fixed Sign:** The sequence progresses by jumping to every 6th sign (e.g., 1, 6, 11, 4...).40  
  * **Dual Sign:** The sequence progresses by trines, exhausting one trinal group before moving to the next. It follows the 1-5-9 (Dharma) pattern, then jumps to the 10-2-6 (Artha) pattern, then 7-11-3 (Kama), and finishes with 4-8-12 (Moksha).40  
* **Direction of Motion:** The engine determines whether the progression moves forward or backward by evaluating the 9th house from the initiating sign. If the 9th house is an "Odd-Footed" sign (Aries, Taurus, Gemini, Libra, Scorpio, Sagittarius), the progression moves forward (Zodiacally). If the 9th house is an "Even-Footed" sign (Cancer, Leo, Virgo, Capricorn, Aquarius, Pisces), the progression moves backward (Anti-Zodiacally).36  
* **Special Exceptions (Saturn and Ketu):**  
  * If Saturn physically occupies the initiating sign, the mathematical modality rules are overridden. The progression is forcibly set to regular, Zodiacal motion (ignoring Movable/Fixed/Dual jumps and odd/even-footed directional rules).40  
  * If Ketu physically occupies the initiating sign, it generates a "Vipareetam" (opposite) effect. The mathematically derived direction of motion is explicitly reversed (forward becomes backward, backward becomes forward), though the jump sequence remains intact.40  
* **Period Durations:** The duration for any sign's Dasha is computed by counting the distance from the Dasha sign itself to the sign occupied by its lord. If the calculation mandates counting forward, the engine counts the distance and subtracts 1\. If counting backward, the engine similarly counts the distance and subtracts 1\. If the lord occupies its own sign, the duration is maximized at 12 years. If the lord is exalted, the engine adds 1 year to the total; if debilitated, it subtracts 1 year. The absolute maximum bound for any single sign is 12 years.38 For signs with dual lordships, namely Scorpio (Mars/Ketu) and Aquarius (Saturn/Rahu), the engine must apply the standard Jaimini strength rules to determine the dominant lord before counting the distance.39

### **4\. Ashtottari Dasha (108-Year Conditional Cycle)**

Ashtottari Dasha is a Nakshatra-based timing mechanism encompassing exactly 108 years, utilizing only eight planetary lords. Notably, the South Node, Ketu, is excluded entirely from the sequence, assigning dominant significance to Rahu.46

* **Eligibility Conditions:** The engine must utilize conditional logic to flag Ashtottari Dasha as the primary predictive tool when specific celestial parameters align 46:  
  1. **Rahu Placement:** Rahu must be positioned in a Kendra (1st, 4th, 7th, 10th) or Trikona (5th, 9th) relative to the Lagna Lord (the ruling planet of the Ascendant, not counted from the Ascendant itself). Crucially, Rahu must not occupy the physical Ascendant.48  
  2. **Luni-Solar Phase Check:** The birth must occur during the daytime in the Krishna Paksha (the waning phase of the moon) OR during the nighttime in the Shukla Paksha (the waxing phase of the moon).48  
  3. If the Ascendant falls within a Nakshatra ruled by Rahu (Ardra, Swati, or Shatabhisha), the Ashtottari system becomes exceedingly dominant and predictive.51  
* **Sequence and Durations:** The mathematical division of the 108 years is distributed unevenly among the eight operating planets:  
  1. Sun: 6 Years  
  2. Moon: 15 Years  
  3. Mars: 8 Years  
  4. Mercury: 17 Years  
  5. Saturn: 10 Years  
  6. Jupiter: 19 Years  
  7. Rahu: 12 Years  
  8. Venus: 21 Years 46  
* **Starting Point Calculation:** The algorithmic mapping begins from specific Nakshatras depending on Rahu's placement. It initiates from Ardra if Rahu is placed in a Kendra, or from Krittika if Rahu is placed in a Trikona. The 27 Nakshatras are distributed sequentially to the 8 planets in block clusters. The Sun assumes rulership over the first block of four Nakshatras, the Moon the next three, Mars four, Mercury three, Saturn four, Jupiter three, Rahu four, and Venus the final three.29 The Dasha operating at the exact moment of birth is determined by the block into which the natal Moon's Nakshatra falls, with the exact time balance calculated via proportional longitudinal traversal.29

### **5\. Dwisaptati Sama Dasha (72-Year Conditional Cycle)**

Dwisaptati Sama Dasha is a highly specialized, 72-year cycle utilized to decode profound matters of psychological desire, partnership, and ultimate renunciation (Moksha). It operates under the conceptual and spiritual governance of Ketu, which represents liberation and the dissolution of worldly ties.48

* **Eligibility Conditions:** The computational engine must trigger this Dasha exclusively when a strict physical exchange occurs along the 1st/7th axis. It activates when the Lagna Lord is physically situated in the 7th house, OR when the 7th Lord is physically situated in the Lagna. It is not triggered by mutual aspect or mutual reception, only by direct physical tenancy.48  
* **Sequence and Durations:** Because Ketu governs the spiritual essence of this system, it is mathematically removed from the sequential array. The remaining 8 planetary entities (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu) each rule exactly 9 years of the cycle. This strict numerical symmetry totals 72 years (8 planets × 9 years).52  
* **Starting Point Calculation:** The computational seed for initiating this Dasha is Moola (Nakshatra index 19), the star inherently associated with Ketu and profound root transformation. The engine must calculate the integer count of Nakshatras starting from Moola up to the Janma Nakshatra (natal Moon position). It then applies a modulo operator: ![][image17]. If the remainder resolves to 0, it is computationally treated as 8\. The resulting integer maps directly to the planet array index to determine the starting Dasha: 1=Sun, 2=Moon, 3=Mars, 4=Mercury, 5=Jupiter, 6=Venus, 7=Saturn, 8=Rahu. As with all Nakshatra dashas, the exact balance remaining is proportional to the Moon's passage through the birth star.29

### **6\. Shat Trimsa Sama Dasha (36-Year Conditional Cycle)**

Not to be confused with the Yogini Dasha, the Shat Trimsa Sama Dasha is another highly specialized 36-year cycle. It is deeply tied to the daily solar and lunar rhythms and is utilized for evaluating fundamental vitality and the flow of daily karma.

* **Eligibility Conditions:** The computational engine must implement a strict astronomical check against planetary hours (Horas). This specific Dasha is activated only if the individual is born during the daytime and the Lagna is mathematically positioned in the Sun's Hora, OR if the individual is born during the nighttime and the Lagna is positioned in the Moon's Hora.48  
* **Sequence and Durations:** The planetary timeline compresses into a fast-moving, 36-year repeating loop characterized by steadily escalating durations. Ketu is omitted from the sequence:  
  1. Moon: 1 Year  
  2. Sun: 2 Years  
  3. Jupiter: 3 Years  
  4. Mars: 4 Years  
  5. Mercury: 5 Years  
  6. Saturn: 6 Years  
  7. Venus: 7 Years  
  8. Rahu: 8 Years 53  
* **Starting Point Calculation:** The mathematical origin seed for this sequence is the Nakshatra Shravana. The engine calculates the integer distance from Shravana to the Janma Nakshatra and computes the remainder via a modulo 8 operation. This remainder determines the initial Dasha lord based on the sequential index provided above. The fractional remainder of the Dasha at birth is calculated based on the proportional degrees of the birth Nakshatra yet to be traversed by the Moon.53

#### **Works cited**

1. Trokon & Ekadhipatya Sodhana | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/667380355/Trokon-Ekadhipatya-Sodhana](https://www.scribd.com/document/667380355/Trokon-Ekadhipatya-Sodhana)  
2. Group \- 7 Trikona and Ekadhipatya Sodhana \- Reduction | PDF | Planets In Astrology, accessed on March 2, 2026, [https://www.scribd.com/document/966469668/Group-7-Trikona-and-Ekadhipatya-Sodhana-Reduction](https://www.scribd.com/document/966469668/Group-7-Trikona-and-Ekadhipatya-Sodhana-Reduction)  
3. EKADHIPATYA SHODHAN IN ASHTAKVARGA \- AstrologerRAMAN.com, accessed on March 2, 2026, [https://www.astrologerraman.com/post/ekadhipatya-shodhan-in-ashtakvarga](https://www.astrologerraman.com/post/ekadhipatya-shodhan-in-ashtakvarga)  
4. Shodhana Techniques in Astrology | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/920168718/AV-TS-ES-MS](https://www.scribd.com/document/920168718/AV-TS-ES-MS)  
5. Ekadhipatya Shod \- Jyotish Vidya, accessed on March 2, 2026, [http://jyotishvidya.com/ch68.htm](http://jyotishvidya.com/ch68.htm)  
6. Advance Predictive Techniques of \- 'ASHTAKVARGA, accessed on March 2, 2026, [http://103.203.175.90:81/fdScript/RootOfEBooks/E%20Book%20collection%20-%202025%20-%20C/RARE%20BOOKS/M\_S\_Mehta\_and\_Rajesh\_Dadwal\_Advanced\_Predictive\_Techniques\_of\_Ashtakvarga.pdf](http://103.203.175.90:81/fdScript/RootOfEBooks/E%20Book%20collection%20-%202025%20-%20C/RARE%20BOOKS/M_S_Mehta_and_Rajesh_Dadwal_Advanced_Predictive_Techniques_of_Ashtakvarga.pdf)  
7. Group \- 9 Shodaya Shodya Pinda and Applications | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/966469677/Group-9-Shodaya-Shodya-Pinda-and-Applications](https://www.scribd.com/document/966469677/Group-9-Shodaya-Shodya-Pinda-and-Applications)  
8. Reference Manual of Vedic Astrology | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/187606379/118466924-Reference-Manual-of-Vedic-Astrology](https://www.scribd.com/document/187606379/118466924-Reference-Manual-of-Vedic-Astrology)  
9. Timing With Sodhya Pindas \- Learning Astrology \- Wikidot, accessed on March 2, 2026, [http://astroveda.wikidot.com/timing-with-sodhya-pindas](http://astroveda.wikidot.com/timing-with-sodhya-pindas)  
10. Ashtaka Varga | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/doc/283296965/Ashtaka-Varga](https://www.scribd.com/doc/283296965/Ashtaka-Varga)  
11. Prastharashtakvarga (or Bhinnashtakavarga) \- planetsoulgalaxy.in, accessed on March 2, 2026, [https://planetsoulgalaxy.in/prastharashtakvarga-or-bhinnashtakavarga/](https://planetsoulgalaxy.in/prastharashtakvarga-or-bhinnashtakavarga/)  
12. Understanding the Ashtakavarga System | PDF | Esoteric Cosmology | Technical Factors Of Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/15787607/Lesson-01](https://www.scribd.com/document/15787607/Lesson-01)  
13. Ashtakavarga: Astrology Chart Insights | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/119705392/UNDERSTANDING-ASHTAKAVARGA-IN-ASTROLOGY](https://www.scribd.com/document/119705392/UNDERSTANDING-ASHTAKAVARGA-IN-ASTROLOGY)  
14. Asthavarga Table For Planets | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/892069105/Asthavarga-Table-for-Planets](https://www.scribd.com/document/892069105/Asthavarga-Table-for-Planets)  
15. LESSON 1 \- Krushna's Ashtakavarga System, accessed on March 2, 2026, [https://kascorner.com/wp-content/uploads/2020/05/LESSON-No.1\_Intro-Ashtakvarga-System-Copy.pdf](https://kascorner.com/wp-content/uploads/2020/05/LESSON-No.1_Intro-Ashtakvarga-System-Copy.pdf)  
16. Ashtakavarga Charts: BAV, SAV, PAV Insights | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/920166982/Av-Charts-Bav-Sav-Topic-2-1](https://www.scribd.com/document/920166982/Av-Charts-Bav-Sav-Topic-2-1)  
17. Ashtakvarga System | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/975723888/Ashtakvarga-System](https://www.scribd.com/document/975723888/Ashtakvarga-System)  
18. ASHTAKVARGA CONCEPT AND APPLICATION GUIDE & EDITOR K.N. RAO M.S. MEHTA I.F.S. fRetd.) \- WordPress.com, accessed on March 2, 2026, [https://astrofoxx.files.wordpress.com/2018/11/jyotish\_ashtakavarga\_m-s-mehta.pdf](https://astrofoxx.files.wordpress.com/2018/11/jyotish_ashtakavarga_m-s-mehta.pdf)  
19. Yogini Dasha Prediction Rules: Complete 36-Year Guide \- AstroSight, accessed on March 2, 2026, [https://astrosight.ai/transits/yogini-dasha-prediction-rules](https://astrosight.ai/transits/yogini-dasha-prediction-rules)  
20. Yogini Dasas- Govern the Different Phases of the Life \- Kali Tantra, accessed on March 2, 2026, [https://www.kalitantra.in/dasas.php](https://www.kalitantra.in/dasas.php)  
21. Dasha Calculator and Predictions \- AstroSage, accessed on March 2, 2026, [https://www.astrosage.com/free/dasha-calculator.asp](https://www.astrosage.com/free/dasha-calculator.asp)  
22. Introduction to Yogini Dasha in Astrology | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/395709371/Yogini-Dasha](https://www.scribd.com/document/395709371/Yogini-Dasha)  
23. An Introduction To The Yogini Dasha | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/doc/299912030/An-Introduction-to-the-Yogini-Dasha](https://www.scribd.com/doc/299912030/An-Introduction-to-the-Yogini-Dasha)  
24. Yogini Dasha \- Amar Deep Sharma (engineer), accessed on March 2, 2026, [https://astroamardeep.weebly.com/yogini-dasha.html](https://astroamardeep.weebly.com/yogini-dasha.html)  
25. Kalachakra Dasha System Explained: Classical Guide \- AstroSight, accessed on March 2, 2026, [https://astrosight.ai/transits/kalachakra-dasha-system-explained](https://astrosight.ai/transits/kalachakra-dasha-system-explained)  
26. Kalachakra Dasa \- Learning Astrology \- Wikidot, accessed on March 2, 2026, [http://astroveda.wikidot.com/kalachakra-dasa](http://astroveda.wikidot.com/kalachakra-dasa)  
27. Kalachakra Dasa: An Overview | PDF | Planets In Astrology | Divination \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/35289442/Basics](https://www.scribd.com/document/35289442/Basics)  
28. Kalachakra Dasa Tutorial \- Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/804014825/kalachakra-dasa-tutorial](https://www.scribd.com/document/804014825/kalachakra-dasa-tutorial)  
29. Parashari Dasha Systems \* BP Lama Jyotishavidya, accessed on March 2, 2026, [https://barbarapijan.com/bpa/VimshottariDasha/1Vimshottari\_dasha\_BPHS\_dashaSystems47.htm](https://barbarapijan.com/bpa/VimshottariDasha/1Vimshottari_dasha_BPHS_dashaSystems47.htm)  
30. Kalachakra Dasa | PDF | Cosmología Esotérica | Signo Astrológico \- Scribd, accessed on March 2, 2026, [https://es.scribd.com/document/379056761/Kalachakra-Dasa](https://es.scribd.com/document/379056761/Kalachakra-Dasa)  
31. Kaala Chakra Dasa System Explained | PDF | Astrological Sign \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/doc/121822600/Kalachakra-Dasa-System](https://www.scribd.com/doc/121822600/Kalachakra-Dasa-System)  
32. Kalachakra Dasa Tutorial | PDF | Planets In Astrology | Divination \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/doc/48160412/Kalachakra-Dasa-Tutorial](https://www.scribd.com/doc/48160412/Kalachakra-Dasa-Tutorial)  
33. Kalchakra Dasa Tutorial | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/63345077/Kalchakra-Dasa-Tutorial](https://www.scribd.com/document/63345077/Kalchakra-Dasa-Tutorial)  
34. Kaal Chakra\#3 | PDF | Planets In Astrology | Superstitions \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/255089647/Kaal-Chakra-3](https://www.scribd.com/document/255089647/Kaal-Chakra-3)  
35. Narayana Dasa II: Cues to Interpretation I, accessed on March 2, 2026, [http://varahamihira.blogspot.com/2005/02/narayana-dasa-ii-cues-to.html](http://varahamihira.blogspot.com/2005/02/narayana-dasa-ii-cues-to.html)  
36. Narayana Dasa, accessed on March 2, 2026, [http://docs.rohinaa.com/narayandasa.pdf](http://docs.rohinaa.com/narayandasa.pdf)  
37. Use of Narayana Dasha \- Know Your Planets (Astrology) \- Quora, accessed on March 2, 2026, [https://knowyourplanets.quora.com/Use-of-Narayana-Dasha](https://knowyourplanets.quora.com/Use-of-Narayana-Dasha)  
38. Narayan Dasa Ex \- Rao | PDF | Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/255156929/Narayan-Dasa-Ex-rao](https://www.scribd.com/document/255156929/Narayan-Dasa-Ex-rao)  
39. Narayana Dasa I: Basics, accessed on March 2, 2026, [http://varahamihira.blogspot.com/2004/11/narayana-dasa-i-basics.html](http://varahamihira.blogspot.com/2004/11/narayana-dasa-i-basics.html)  
40. Narayana Dasa by Sanjay Rath.pdf \- Science of Light, accessed on March 2, 2026, [https://scienceoflight.net/wp-content/uploads/extra/Narayana%20Dasa%20by%20Sanjay%20Rath.pdf](https://scienceoflight.net/wp-content/uploads/extra/Narayana%20Dasa%20by%20Sanjay%20Rath.pdf)  
41. Chara Dasa (Raghava Bhatta \- Nrisimha Suri method) \- Jaimini Sutramritam, accessed on March 2, 2026, [http://sutramritam.blogspot.com/2009/08/chara-dasa-raghava-bhatta-nrisimha-suri.html](http://sutramritam.blogspot.com/2009/08/chara-dasa-raghava-bhatta-nrisimha-suri.html)  
42. Lessons On Vedic Astrology P.V.R. Narasimha Rao Compiled by The Students of Sri Jagannath Center-Boston, accessed on March 2, 2026, [https://www.vedicastrologer.org/classes/book1-for-CD.pdf](https://www.vedicastrologer.org/classes/book1-for-CD.pdf)  
43. Narayana Dasa \- Parijaata, accessed on March 2, 2026, [https://parijaata.wordpress.com/2011/12/12/263/](https://parijaata.wordpress.com/2011/12/12/263/)  
44. Narayana Dasa, accessed on March 2, 2026, [https://storage.yandexcloud.net/j108/library/6fhh7uus/Sanjay\_Rath\_-\_Narayana\_Dasa.pdf](https://storage.yandexcloud.net/j108/library/6fhh7uus/Sanjay_Rath_-_Narayana_Dasa.pdf)  
45. What Is The Correct Procedure For Computing Jaimini's Chara Dasa? By U.K. Jha, India, accessed on March 2, 2026, [https://saptarishisshop.com/what-is-the-correct-procedure-for-computing-jaiminis-chara-dasa-by-uk-jha/](https://saptarishisshop.com/what-is-the-correct-procedure-for-computing-jaiminis-chara-dasa-by-uk-jha/)  
46. Ashtottari Dasha System in Brihat Parashara Hora Shastra (BPHS – astrosutras.in, accessed on March 2, 2026, [https://astrosutras.in/index.php/2025/03/04/ashtottari-dasha-system-in-brihat-parashara-hora-shastra-bphs/](https://astrosutras.in/index.php/2025/03/04/ashtottari-dasha-system-in-brihat-parashara-hora-shastra-bphs/)  
47. Dashas—the time periods in Vedic astrology, accessed on March 2, 2026, [https://www.indastro.com/learn-astrology/mahadasha.html](https://www.indastro.com/learn-astrology/mahadasha.html)  
48. Applicability of Vimsottari Dasa \- Parijaata \- WordPress.com, accessed on March 2, 2026, [https://parijaata.wordpress.com/2013/03/26/applicability-of-vimsottari-dasa/](https://parijaata.wordpress.com/2013/03/26/applicability-of-vimsottari-dasa/)  
49. Complete Guide to All Types of Dashas in Vedic Astrology, accessed on March 2, 2026, [https://astrokaya.com/all-types-of-dashas-complete-guide.html](https://astrokaya.com/all-types-of-dashas-complete-guide.html)  
50. In search of Maharishi Parashara's 42 Dasa systems | by Varaha Mihira | Thoughts on Jyotish | Medium, accessed on March 2, 2026, [https://medium.com/thoughts-on-jyotish/in-search-of-maharishi-parasharas-42-dasa-systems-56f7604b5138](https://medium.com/thoughts-on-jyotish/in-search-of-maharishi-parasharas-42-dasa-systems-56f7604b5138)  
51. The Secret Dasha Not Meant for Everyone – Ashtottari Mahadasha \- Astro Blogs, accessed on March 2, 2026, [https://thehealingastroblogs.com/the-secret-dasha-not-meant-for-everyone-ashtottari-mahadasha/](https://thehealingastroblogs.com/the-secret-dasha-not-meant-for-everyone-ashtottari-mahadasha/)  
52. Dvisaptati Sama Dasa \- Sanjay Rath, accessed on March 2, 2026, [https://srath.com/jyoti%E1%B9%A3a/dasa/dvisaptati-sama-dasa/](https://srath.com/jyoti%E1%B9%A3a/dasa/dvisaptati-sama-dasa/)  
53. Dasas of Grahas \- Jyotish Vidya, accessed on March 2, 2026, [https://www.jyotishvidya.com/ch46.htm](https://www.jyotishvidya.com/ch46.htm)  
54. Dwisaptati Samadasha | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/doc/169417249/Dwisaptati-Samadasha](https://www.scribd.com/doc/169417249/Dwisaptati-Samadasha)  
55. Conditional Dasa Systems \- The Art of Vedic Astrology, accessed on March 2, 2026, [https://www.theartofvedicastrology.com/?page\_id=436](https://www.theartofvedicastrology.com/?page_id=436)  
56. Vedic Astrology Dasa Systems Guide | PDF | Art \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/doc/247258381/Dasa-Selection](https://www.scribd.com/doc/247258381/Dasa-Selection)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAYCAYAAAAlBadpAAAAqklEQVR4XmNgGAVkgTggvgvE6kDMiCZHFBAC4vtAvJGBTAN4gbiYAWKAMQOZhoAAyKBCIN4BxLZockSDVCC+DsQOQMyMKkU84ADiZCDeD8S6aHIEAcwbW4BYBU0OJ6hlgMSCNgMJAQiKOpDGZQwQjQSBOBC3AfEcIFZFk8MLQBpfAvEMdAlCAJQsQZqHGAAlAJCzicFiQMwK0QYB1UD8n0j8GYjDIdqGJAAAgCgc64wSJyYAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAYCAYAAAAlBadpAAAAg0lEQVR4XmNgGAXDGMQDsSG6ID4gDsRPgXgZEDOiyeEFbUD8CIhV0SVwgX4gfgnEM9Al8AGQ6XMYIJrl0eRwgmog/swA8RvJQJEBYaM0mhxJAORckH9JcjoyAGmCBRrRoYwNgMIBFF3zGCgwqBaI7wOxOroEsYAXiG8BsR+6xCggAgAA1bERttNWvuIAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAE8AAAAXCAYAAABK6RIcAAABdElEQVR4Xu2XPS8FQRSGjyARub4jEgm1QqGREAWdAp0fIVerkSg0Gp1GoVBL/AEJjUKiVpCoRKNQ+gG8b8bGuSeX3SlmNhvnSZ5iz8zcu/veuztnRRzHcf4v43AFjtiBGpiAs7ZYI0O2ULABn+Aw7IdX8BPuwB41LyV9En64c/gs4ftPOmbkZRMewDcJ57LeOfzDLdxVx5PwBr7AZVVPySA8hRewLfWHdw3v4L6UhMdBOqpq8981fkBupqT+8AoY2p/hfUiYMKBqxQXcq1ouGhVeN7YlLDqyAxlodHgteAkf4JwZy0FseHvwOMJDOM2FFYgO71HCLpNrp7XEhpeSyuGxVeFut2gHfoEXuVXRJdgblpXSyPD4l9a76xhcU8e5aFR4vD3Z582YOnucM1PLQWx4fCPimqryTarqI6k0PHbTfMbphypv31cJAeYmNryUlIbHwW6+w1U1LzUMy54DXdCTMsH+1p4HZRfCbsRxHMdxnOR8AS3qZXgHOTN1AAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAZCAYAAADAHFVeAAABh0lEQVR4Xu2UvytGYRiGH0kpMihE5GSQMhpsLMpCGfwHDIpYLLKxSAaTXRZlU0osyoAURdilDBblD+C+v+cc3nM7p/N9xXauuvr6nud9zvv7NSv5Z+rgOJyEjXGsCQ5+t/gjhuExfIDX8BnOwj24ErfhALbhVY5ncM180LlMwC37mQ1hwSK8gVEQJ2PwAy5JnDVT8BNuSK5CNzyHvZoA/fAANkucnfCDoxInbMvcoybIrnkyiw7zWSgX5jXhSiR0medeNEE4cibbNQHaYI8GwZvlD5CzZe5EE2TZPJl4BOdTLdJwNmzH2Snc+1fzbzZIrkIL3Ld0h3TVsgs6zfNc/hCuDDviKa6XXCbseMe8gB88TKcrLJifxGnzPU1sDRvVQp95Z5cS5xJyRvfmJ7VqIvNLmEeyfyHcfB6OdYkXwrvCwix49+7ggMSTaxJJvJCkUA8B/2/COYkTvias0UteyC0cgk/w3fy+ncb/+eSEzNjv08pDUjUj8S9fdb70nA33QmdaUlJSO1+Q0lXopvwKqgAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAApCAYAAACIn3XTAAADMklEQVR4Xu3cz+tlYxwH8EcoC2pYEEUzGwtRpEQWdkPJjj/AbhYyi8lCNoryIxJFslMaSoqNnZqFkhgbzWimmY2UhY3yB/C8O+fw3Oee+/3eM98731KvV737dj7n+d7z6a4+Pfe5txQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+L97qeb3mnM1X9Y8WXN0vPdpzfczeXG8f7X0z0terrm2WROb+jvWLtqx9PBVzd81F2p+rbm+5vWa68Y1N5T1npIzNdeMawAAtvJZzUPN9V1lGERaJ2Zqz4/1qynPzPA4uW2s3dnUYq6/v8b6rmXYymvf1NUv1fzW1SJrTzbX+f/0Og12AAD7yqDRyxDXyppXutoDNT91tV26v6wPYZHaW11trr/LZbv+Pu8Le3ikzPcUj9c819VuL8P67La1Unu4qwEAbJTh4VRfbEw7Qnd39Qw6D3a1XXqn5ueu9kwZdqza3alN/aW2TX9LBrY8+/2+OMrAdmtXywD3R1dL730NAGBPObuW4WbKfau313a6MiC9V/NLU+u9VvPmPsmZr71k1+yLmqdqXqj5sebtlRWDTf0db2p72XZgy45YnpNds219V/Nxc52BLu93fw4PAGBfGSByJi07SEkrO10ZnnJ+bMph6HfN0sPcmbSD9rftwPZu2fxx6CZZ/3T5r69bVm8DAOzv2e76aFkfSjIMZSg6bH0fH9Wc7WqxtL97y7BrN+VMd53MmRvYHi3DQJb66Zp7mnvT+bUbmxoAwCI5CJ8hpJUdrR+a6+l8WD52XCK7dO3HrHO5+d/V6/Lc/vxaBrNvutqV9tfadoftibI+sMWRMtT7j0rzzdB+txIAYJHHyvo3RM/X3NFcT+e2Dvt3w/Lc/luf6WMarr4e/+6iv20Htsj5s5y/a+V6bpDLN1SXvDYAwJochs+5qos1n5RhN6g9//VGWd0RO8gu1hLtM9vdvg/LMDC9WoafFGnXHaS/JUNVBsNvy/ADw/npkz/L8J590C4qq33ZZQMAOKAlAxsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABckX8AGQOv20YwADQAAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAZCAYAAAAmNZ4aAAABiElEQVR4Xu2TsStFcRTHv0JJL0kh6pWBzSBSVmWTQb1MUjbFZJORScoqmwmr2CgDyShlMhiUwaL8AZzvO7/j/d65v6v3ShncT32He76/87vnnHsuUPDfWBDd5ehKNCFqtcMRPaIjZHNMB6K579M/8CD69EHhBBof9EZgC+qPuni/6FR0Iep1Xh0fSL+4Ao2veSNwDPW7vQHNocc7knRAD5x7Q9iAeuwsxRvSBZNdqLfiDYNj5IE9b0DHRW/SGwF6Tz4InQAbeUZ+bnUkTB6LYi2iadGraDWKxwwgv2DbjS5vGG3QDXwULUI3cVl0LXoXjdSOZpiCXr4UxfjZZqE7sx/FMzD5BfXJ5AaazM5TWMH3onHoFlN9ovboXC788KyaBcTYUnGcKfgCFncI7bJpLqEvYAcxvJDxIRc3OCH6M95oFCZz1B77TVL/J7GCO73RCOySybfegMapUng+Ew3X7Gqx9JuCS2AXm7hI89GZzRDbDiqHuM+j+K1/DW4zO9wRrTuvoKDgb/kCKI9hVXrq6UEAAAAASUVORK5CYII=>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAaCAYAAACgoey0AAABqElEQVR4Xu2VvytGURjHH6GEZFIGRcmvLDYlm0wMymAyGCQ/NouMNikki5RsymJRUjYG2Qgl6h2UwaL8AXy/nnNux3PPfb1vGaT7qU/v+57vec9z7rnn3CuS80eohwNwFHYE7W2wOfj9a1TDMfjhfHKfvvg57HXfPe3wMsMLuAErk94GBnPwBS6YjKyKTmAdVpiM1MB90UJNJusS/e+eaf9iEb7DYRs4uuEdnLSBg8VYdAdWmYyw8LNt5BWw6KsNAhrhMeyzgaNfdOAZGzj8rUvgJjoUvRpeVRa+X2yZyZbowLGN1yqaXYWN3Ei82m2JL5HHF87iTHRw3mvLlGiNb6txI9kzLQeOYW9VA7yHbxKZkF/7VFAmfhwrd3pn0C8hddMd3KUnkj6XPWEnB881x1ixQTGyCteJHq1peA0LcFbiKzMuOgY/S6Yg8cIef0yWbODwx4zye8lwp7Kwfdp45kXzIRs4+CjlBl2zwU/wXE6Ibvdd0z4IT+EjrA0y0iL6AjkSndiy+13sSEbhw58D3MID+CB6FPjSGAn6eTYlvYOpnWBOTs4/5BNg7mSetZODjQAAAABJRU5ErkJggg==>

[image8]: <data:image/png;base64,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>

[image9]: <data:image/png;base64,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>

[image10]: <data:image/png;base64,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>

[image11]: <data:image/png;base64,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>

[image12]: <data:image/png;base64,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>

[image13]: <data:image/png;base64,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>

[image14]: <data:image/png;base64,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>

[image15]: <data:image/png;base64,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>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAYCAYAAAAlBadpAAAAiklEQVR4XmNgGAVDDPgBsRu6ICmAGYj3A/F1IOZAkyMKgAxwYIAYkArE3CiyJABGIDYG4rtAXIgmRzQAGbARiGuBmBdNjmgAcok2ED8CYnc0OYIApJEkF4BsA2m4z0CkBhAAhbotEO9ggAQWURodGCBxTVI0weL3IhBHoUoRBp0MEI1kpaxRQCQAACJzEL4WC5BMAAAAAElFTkSuQmCC>

[image17]: <data:image/png;base64,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>