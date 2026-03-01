# **Algorithmic Implementation of Advanced Jaimini Astrological Systems: A Comprehensive Computational Framework**

The translation of classical Vedic astrological principles into a deterministic computational engine requires a rigid formalization of abstract aphorisms. While Parashari astrology relies heavily on spatial geometry, orbital angular momentum, and planetary lordship, the Jaimini system operates on an entirely distinct mathematical architecture. Jaimini utilizes a state-based matrix where zodiacal signs act as independent functional entities, significators mutate based on exact longitudinal arrays, and time is measured in sign-based periods rather than stellar fractions. To achieve a holistic algorithmic engine, the remaining eighty percent of the Jaimini framework must be systematically encoded. This entails the integration of static and dynamic significators, sign-based aspectual matrices, complex multi-variable Dasha (timing) systems, specialized divisional chart mapping, and unique planetary yogas. The following architectural documentation provides the exhaustive computational logic required to implement these advanced Jaimini modules.

## **SECTION 1: STHIRA KARAKAS (FIXED SIGNIFICATORS)**

Within the Jaimini engine, significators (Karakas) are the primary variables through which the algorithm interprets human relationships and physical realities. A robust computational model must differentiate between the three distinct Karaka classes: Naisargika (Natural), Chara (Variable), and Sthira (Fixed). The failure of most modern astrological software stems from conflating these three arrays or utilizing them in the wrong predictive modules.

The Naisargika Karakas represent the foundational architecture of the universe, presided over by the creator archetype, Brahma. They encompass all nine planetary bodies, including the nodes Rahu and Ketu, and signify the general, impersonal existence of matters and entities in the cosmos.1 Conversely, the Chara Karakas, governed by the sustainer archetype, Vishnu, are dynamically assigned based on the descending order of planetary longitudes within any given sign. They map the functional roles that various souls play in the native's socio-economic and spiritual sustenance.1 The Chara Karaka array utilizes eight planets (including Rahu but strictly excluding Ketu, as Ketu represents liberation and the dissolution of worldly sustenance).1

The Sthira Karakas, presided over by the destroyer archetype, Shiva, govern the physical bodies of specific relatives, their health susceptibilities, and their ultimate destruction or death.1 Because the shadowy nodes (Rahu and Ketu) possess no physical mass, they cannot experience physical decay or death; therefore, the algorithmic array for Sthira Karakas must strictly exclude the nodes, utilizing only the seven visible planets.2

The exact assignment of Sthira Karakas for each relative is mathematically fixed, requiring the engine to evaluate specific planetary strengths to break ties between dual candidates. The computational engine must deploy the following static assignments for Sthira Karakas:

| Astrological Entity | Sthira Karaka Assignment | Algorithmic Evaluation Criteria |
| :---- | :---- | :---- |
| Father | Stronger of Sun or Venus | Evaluate Shadbala or longitudinal advancement to resolve tie. |
| Mother | Stronger of Moon or Mars | Evaluate Shadbala or longitudinal advancement to resolve tie. |
| Younger Siblings / Brother-in-Law | Mars | Fixed constant assignment. |
| Maternal Relatives / Uncles | Mercury | Fixed constant assignment. |
| Paternal Grandfather / Husband / Sons | Jupiter | Fixed constant assignment. |
| Wife / Parents-in-Law / Maternal Grandfather | Venus | Fixed constant assignment. |
| Elder Siblings / Native's Longevity (Ayush) | Saturn | Fixed constant assignment. |

The computational engine must possess a strict routing protocol to determine which Karaka array to invoke during specific predictive tasks. The application of these arrays is mutually exclusive based on the nature of the inquiry.

SUTRA 1 — Plain English: Fixed significators denote the destruction of the body, while variable significators denote sustenance and interactions. — Computational IF/THEN rule: IF the predictive module invoked is an Ayur Dasha (e.g., Shoola Dasha, Niryana Shoola Dasha) calculating health, severe disease, or physical death, THEN assign the Sthira Karaka array to represent the specific relative. IF the predictive module is a Phalita Dasha (e.g., Chara Dasha, Narayana Dasha) calculating career, wealth, or marriage, THEN assign the Chara Karaka array. — Example application: When the engine is tasked with timing the exact period of the mother's demise, it must evaluate the Shoola Dasha affecting the stronger of the Moon or Mars (the Sthira Karaka), rather than evaluating the Matrukaraka (the Chara Karaka).

When a direct contradiction arises in the code base between a Sthira Karaka and a Chara Karaka within a longevity module, the Sthira Karaka must act as the absolute override, dictating the physical outcome.1

## **SECTION 2: JAIMINI ASPECT COMPUTATION**

The implementation of aspects in the Jaimini system represents a fundamental departure from the Parashari model. The engine must decouple the concept of aspect from planetary geometry and reorient it toward sign-based environmental linkages.

### **Complete Rules for Rashi Drishti (Sign Aspects)**

In the Parashari system, planets cast aspects based on spatial angles (e.g., opposition or trine). In the Jaimini system, the zodiacal signs themselves hold a permanent, structural aspectual relationship with one another, known as Rashi Drishti (Sign Sight). This aspect represents a permanent cognitive and environmental linkage (Gyana Shakti) that does not fluctuate with time or planetary transits.4 Furthermore, Rashi Drishti is absolute; unlike Parashari aspects which can possess fractional strengths based on angular distance, a Rashi Drishti is always calculated at one hundred percent strength.5

The base logic requires categorizing the twelve signs into three arrays: Movable (Cardinal), Fixed, and Dual (Mutable). The engine must then apply a specific vector of interaction between these arrays.

SUTRA 1.1.2 — Plain English: Zodiacal signs aspect the signs fronting them, and the planets residing within those signs transmit the exact same aspect. — Computational IF/THEN rule: IF a sign is Movable, THEN it aspects all Fixed signs EXCEPT the Fixed sign immediately adjacent to it. IF a sign is Fixed, THEN it aspects all Movable signs EXCEPT the Movable sign immediately adjacent to it. IF a sign is Dual, THEN it aspects the other three Dual signs. — Example application: An entity located in Aries (Movable) will cast a full aspect on Leo, Scorpio, and Aquarius, but the engine must explicitly exclude Taurus (the adjacent Fixed sign) from the aspect array.

| Sign Quality | Origin Sign | Signs Receiving Rashi Drishti (Target Array) | Excluded Adjacent Sign |
| :---- | :---- | :---- | :---- |
| Movable | Aries | Leo, Scorpio, Aquarius | Taurus |
| Movable | Cancer | Scorpio, Aquarius, Taurus | Leo |
| Movable | Libra | Aquarius, Taurus, Leo | Scorpio |
| Movable | Capricorn | Taurus, Leo, Scorpio | Aquarius |
| Fixed | Taurus | Cancer, Libra, Capricorn | Aries |
| Fixed | Leo | Libra, Capricorn, Aries | Cancer |
| Fixed | Scorpio | Capricorn, Aries, Cancer | Libra |
| Fixed | Aquarius | Aries, Cancer, Libra | Capricorn |
| Dual | Gemini | Virgo, Sagittarius, Pisces | None |
| Dual | Virgo | Sagittarius, Pisces, Gemini | None |
| Dual | Sagittarius | Pisces, Gemini, Virgo | None |
| Dual | Pisces | Gemini, Virgo, Sagittarius | None |

The computational implication of this rule is that the sign itself is the transmitter. Therefore, any planetary body, calculated mathematical point (such as Arudha Padas), or invisible Upagraha (such as Gulika) that resides within the origin sign inherits the sign's aspectual vector. The engine must propagate the properties of the resident planet across the entire target array.5 If a planet sits in a sign, and that sign aspects another sign via Rashi Drishti, the planet effectively aspects that target sign and all planets within it.

### **Graha Drishti in Jaimini**

While Rashi Drishti maps the permanent environmental data, Graha Drishti (Planetary Aspect) in Jaimini maps the projection of a planet's active desire (Iccha Shakti).4 The Jaimini system acknowledges the special Parashari aspects of the outer planets: Mars aspects the 4th and 8th houses from its position; Jupiter aspects the 5th and 9th houses; Saturn aspects the 3rd and 10th houses.8 However, the computational deployment of these aspects differs critically from Parashari rules.

In standard Parashari implementation, if Mars aspects a planet, the relationship is a one-way vector unless the target planet also has an aspect intersecting Mars. In Jaimini, the special Graha Drishti remains strictly unilateral, but with one major algorithmic exception regarding the dispositor.

SUTRA 2 — Plain English: A unilateral planetary aspect becomes a bilateral energy exchange if the aspecting planet occupies the domicile of the aspected planet. — Computational IF/THEN rule: IF Planet A aspects Planet B via a special Graha Drishti vector (4, 8, 5, 9, 3, or 10\) AND Planet A is physically located in a zodiacal sign ruled by Planet B, THEN force a bidirectional feedback loop where Planet B exerts an equal reciprocal influence on Planet A. — Example application: If Saturn is placed in Cancer, it casts a 10th house Graha Drishti onto the Moon located in Aries. Because Saturn occupies Cancer (the sign ruled by the Moon), the algorithmic engine must register the Moon as simultaneously aspecting and influencing Saturn, despite the Moon lacking a geometric aspect back to Cancer.8

### **Argala and Virodha Argala Computation**

The concept of Argala constitutes the mathematical linchpin of the Jaimini system. Argala translates to an intervention, a celestial bolt, or an obstruction that forces a specific destined outcome by either locking or unlocking the energy of a house or planet.9 It quantifies the invisible network of support and sabotage that operates independently of geometric aspects. The engine must compute the primary Argalas, the obstructing Virodha Argalas, and resolve the mathematical conflicts between them.

Primary Argala establishes the immediate support vectors for any reference point in the chart. These support vectors provide the tangible resources, emotional foundation, and fulfillment necessary for the reference point to manifest its potential.

SUTRA 1.1.5 — Plain English: Planets situated in the fourth, second, and eleventh positions from the reference point create a supportive intervention known as Argala. — Computational IF/THEN rule: IF planetary entities are detected in House \+ 1 (2nd house), House \+ 3 (4th house), or House \+ 10 (11th house) from a target reference point, THEN initialize a Primary Argala support array for that reference point. — Example application: If evaluating the Ascendant, planets located in the 2nd house generate an Argala that provides the financial and verbal resources necessary for the native's worldly success.11

However, this support is subject to immediate cosmic counterforces known as Virodha Argala (obstruction). The engine must map specific houses as dedicated antagonists to the primary support houses. The 12th house obstructs the 2nd house; the 10th house obstructs the 4th house; and the 3rd house obstructs the 11th house.10

SUTRA 1.1.7 — Plain English: Planets occupying the tenth, twelfth, and third houses from the reference point cause obstruction to the respective primary Argalas, potentially destroying the support. — Computational IF/THEN rule: IF the target reference has an active Argala, THEN evaluate the corresponding Virodha Argala house. IF Count(Planets in Virodha House) \> Count(Planets in Argala House) OR (Count(Planets in Virodha House) \== Count(Planets in Argala House) AND Overall\_Dignity\_Score(Virodha Planets) \> Overall\_Dignity\_Score(Argala Planets)), THEN nullify the Primary Argala support array. — Example application: The engine detects Jupiter in the 4th house providing strong Argala to the Lagna. However, it detects Saturn and Mars in the 10th house. Because two planets outnumber one, the Virodha Argala from the 10th house completely breaks the support offered by Jupiter in the 4th house.

The algorithm must also process Secondary and Tertiary Argalas. Secondary Argala operates on a subtler, longer-term frequency, generated by planets in the 5th house and obstructed by planets in the 9th house.10 Tertiary Argala introduces a highly specific exception state known as Vipareeta Argala. If three or more natural malefics are located simultaneously in the 3rd house from the reference point, they generate a massive, unobstructable surge of positive intervention, locking in success through aggressive, competitive means.10 The engine must flag this as an unblockable support vector.

Finally, the computation of Argala requires a specific coordinate reversal when dealing with the spiritual node, Ketu.

SUTRA 1.1.10 — Plain English: The entire mathematical calculation of Argala must be reversed for the sign occupied by Ketu, reflecting its counter-material nature. — Computational IF/THEN rule: IF the reference point for the Argala calculation \== Ketu, THEN reassign the primary Argala array to the 12th, 10th, and 3rd houses, AND reassign the Virodha Argala (obstruction) array to the 2nd, 4th, and 11th houses. — Example application: When evaluating the spiritual liberation potential of Ketu, planets in the 12th house from Ketu provide the supportive Argala, while planets in the 2nd house from Ketu obstruct the spiritual path.13

## **SECTION 3: ALL JAIMINI DASHA SYSTEMS**

The Jaimini engine replaces the static, Moon-centric Vimshottari Dasha with dynamic, sign-based Rashi Dashas. The engine must implement specific algorithms to handle the sequence, duration, and triggering events for eight un-implemented Dasha systems.

### **Niryana Shoola Dasha (Trishoola Dasha)**

This is an Ayur Dasha, utilized exclusively for timing the physical death of the native or their relatives. The computational sequence is highly deterministic and relies on fixed nine-year intervals.

1. **Eligibility and Starting Condition**: The engine must evaluate the exact longitudinal degrees, planetary occupancy, and dignities of the Janma Lagna (Ascendant) and the 7th house. The Dasha always commences from the mathematically stronger of these two signs.14  
2. **Sequence Generation**: The engine must evaluate the polarity of the commencing sign. IF the commencing sign is an odd sign (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius), THEN the Dasha sequence progresses directly (zodiacally). IF the commencing sign is an even sign (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces), THEN the sequence progresses in reverse (anti-zodiacally).14  
3. **Duration Algorithm**: Unlike other Jaimini systems, Niryana Shoola Dasha does not calculate duration based on lord placement. The duration is a hard-coded constant: each sign governs exactly 9 years.16  
4. **Lord Identification**: The engine must identify the Rudra (the planet signifying destruction). Calculate the strength of the 8th lord from the Lagna versus the 8th lord from the 7th house. The stronger of the two is the Prani Rudra. The weaker is the Aprani Rudra, which only becomes active if heavily aspected by malefics.15  
5. **Results Interpretation**: The engine flags the specific periods of mortality by identifying the Trishoola (trident) signs. The Trishoola signs are the 1st, 5th, and 9th signs from the sign occupied by the active Rudra planet. When the Maha Dasha or Antar Dasha aligns with these Trishoola signs, a critical mortality warning is generated.15

### **Navamsha Dasha**

The Navamsha Dasha operates as both a Phalita (general results) and Ayur Dasha. Its unique feature is that the entire mathematical computation occurs exclusively within the spatial coordinates of the D-9 Navamsha chart, isolated from the D-1 Rashi chart.

1. **Eligibility and Starting Condition**: Calculate the Chara Karakas specifically utilizing the longitudes within the D-9 chart. The Dasha commences from the sign occupying the Navamsha Lagna.18  
2. **Sequence Generation**: IF the Navamsha Lagna is an odd sign, the Dasha progression is direct. IF the Navamsha Lagna is an even sign, the sequence is reverse. Note: Certain sub-routines (following Dr. Suresh Chandra Mishra) demand that for even ascendants, the Dasha starts from the *Adarsha Rashi* (the other sign ruled by the same planet), but the primary algorithmic implementation defaults to direct/reverse from the Lagna.18  
3. **Duration Algorithm**: The engine computes the shortest spatial distance from the Dasha sign to the sign occupied by its lord within the D-9 chart. IF counting forward, subtract 1 from the total count. IF counting backward, subtract 1\. IF the lord occupies the Dasha sign itself, assign a full 12 years. IF the lord is exalted in the D-9, add 1 year; IF debilitated, subtract 1 year.  
4. **Results Interpretation**: The engine evaluates the activation of the D-9 Chara Karakas during the Dasha periods to predict highly localized internal changes, spiritual shifts, and marital events.

### **Shoola Dasha**

Distinct from Niryana Shoola, the standard Shoola Dasha is utilized to determine broader periods of severe suffering, health crises, and the eventual physical demise.

1. **Eligibility and Starting Condition**: The engine sets the absolute maximum lifespan variable (Purna Ayus) to 108 years, corresponding to 12 signs multiplied by 9 years.20 The Dasha begins from the stronger of the Lagna or the 7th house.20  
2. **Sequence Generation**: A critical algorithmic deviation from Niryana Shoola is required here. The Shoola Dasha sequence is *always* regular and direct (zodiacal), regardless of whether the commencing sign is odd or even. The algorithm does not reverse.20  
3. **Lord Identification**: The engine identifies the primary Rudra by comparing the strength of the 2nd house lord against the 8th house lord. The stronger of these two takes the mantle of the Rudra.20  
4. **Results Interpretation**: The sign containing the Rudra, along with its trinal signs (the 5th and 9th from it), constitute the active Trishoola. The algorithm flags these specific 9-year blocks as periods of extreme physical vulnerability and potential death.16

### **Brahma Dasha**

The Brahma Dasha is a highly specialized, rarely invoked Dasha used for timing critical karmic shifts, ultimate longevity parameters, and the point of spiritual liberation for advanced souls.

1. **Identify Brahma**: The engine first evaluates the Lagna and the 7th house, selecting the stronger of the two. From this stronger sign, it identifies the lords of the 6th, 8th, and 12th houses. The algorithm evaluates the strength of these three lords. The strongest among them becomes the Brahma planet. The engine must enforce a strict exception handling rule: Saturn, Rahu, and Ketu are permanently disqualified from becoming the Brahma planet.21  
2. **Identify Maheshwara**: The engine calculates the 8th house from the sign occupied by the Atmakaraka (AK). The lord of this 8th house is designated as Maheshwara.21  
3. **Sequence Generation**: The Dasha commences from the sign physically occupied by the Brahma planet. The progression sequence follows the standard Sthira Dasha rules.21  
4. **Duration Algorithm**: The durations are calculated by counting the distance from the Dasha sign to its lord, identical to the Chara Dasha duration math.

### **Sree Lagna Dasha (Sudasa)**

The Sree Lagna Dasha, also known as Sudasa, is a highly specific Phalita Dasha dedicated exclusively to timing the acquisition of immense wealth, financial prosperity, and material comforts (Lakshmi Sthana).

1. **Calculate Sree Lagna (SL)**: The engine must execute a precise floating-point calculation. Determine the exact degree of the Moon. Calculate the elapsed fraction of the Moon's current ![][image1] Nakshatra span. Multiply this fractional value by the full ![][image2] of the zodiac to obtain the elapsed proportional arc. Add this elapsed arc to the exact longitudinal degree of the Janma Lagna. The resulting point on the ecliptic is the Sree Lagna.22  
2. **Sequence Generation**: The Dasha strictly commences from the sign of the Sree Lagna. The progression leaps categorically rather than sequentially: it evaluates all Kendras (1st, 4th, 7th, 10th from SL), followed by the Panapharas (2nd, 5th, 8th, 11th from SL), and finally the Apoklimas (3rd, 6th, 9th, 12th from SL).22  
3. **Duration Algorithm**: The engine evaluates the "footing" of the Dasha sign. IF the Dasha sign is odd-footed (Aries, Taurus, Gemini, Libra, Scorpio, Sagittarius), THEN count forward from the sign to its lord. IF the Dasha sign is even-footed, count backward. Subtract 1 from the total count to yield the duration in years.22 The first Dasha period must be fractionally adjusted based on the remaining degrees of the Sree Lagna within its sign.22

### **Drig Dasha**

The Drig Dasha is utilized to time spiritual evolution, periods of deep renunciation, and the exact manifestation windows of Argala-based Raja Yogas.

1. **Starting Condition**: The Dasha rigidly commences from the 9th house from the Lagna.24  
2. **Sequence Generation (Trikuta Padakrama)**: The sequence follows a complex triad of aspects based on Rashi Drishti. The first cluster includes the 9th house and the three specific signs it aspects. The second cluster includes the 10th house and its three aspected signs. The final cluster includes the 11th house and its three aspected signs.25  
3. **Duration Algorithm**: Drig Dasha does not use variable lord-based counting. It assigns durations based on the fixed Sthira Dasha years: Movable signs receive 7 years, Fixed signs receive 8 years, and Dual signs receive 9 years.26

### **Trikona Dasha**

The Trikona Dasha is a Phalita Dasha utilized to confirm highly auspicious life events, particularly the timing of marriage and childbirth.

1. **Starting Condition**: The engine evaluates the mathematical strengths of the 1st, 5th, and 9th houses from the Lagna. The Dasha commences from the strongest of these three trinal points.27  
2. **Sequence Generation**: IF the commencing sign is an odd sign, the Dasha signs run sequentially forward (zodiacally). IF the commencing sign is an even sign, they run sequentially backward (anti-zodiacally).27  
3. **Duration Algorithm**: Durations are calculated using the standard Chara Dasha formula (counting from the sign to its lord).

## **SECTION 4: KARAKAMSHA CHART**

The Karakamsha acts as the most critical pivot for evaluating the destiny of the soul, functioning as a structural bridge between the physical reality of the D-1 chart and the internal spiritual scaffolding of the D-9 Navamsha chart. The computational engine must differentiate precisely between the terms Karakamsha and Svamsha to avoid compounding predictive errors.

### **Casting Karakamsha vs. Svamsha**

* **Svamsha**: This is the exact zodiacal sign occupied by the Atmakaraka (AK) within the D-9 Navamsha chart itself. Analyzing the Svamsha reveals the native's inner spiritual path, their inherent, hidden talents, and their microscopic physical constitution.28  
* **Karakamsha Lagna**: To construct the Karakamsha, the algorithm must extract the Navamsha sign of the AK and map it back onto the spatial grid of the D-1 Rashi chart. The D-1 chart is then dynamically rotated such that this specific sign becomes the new 1st house (Ascendant).28 The Karakamsha framework determines how the soul's deepest desires manifest objectively in the material world, heavily influencing career trajectory, public status, and visible spirituality.

### **House Interpretation Algorithm from Karakamsha Lagna**

The algorithm must process the rotated Karakamsha chart by evaluating planetary placements and Rashi Drishti aspects against the new house array.

SUTRA 3 — Plain English: Interpretations derived from the Karakamsha establish the immutable parameters of the native's material and spiritual destiny. — Computational IF/THEN rule: IF an astrological event is assessed for core karmic validity, THEN evaluate the specific house relative to the Karakamsha Lagna as the primary definitive filter.

* **1st House (Karakamsha itself)**: IF occupied or aspected by strong benefics, the engine flags a trajectory of royal association, high administrative power, or noble lineage.31  
* **2nd House**: IF occupied by Ketu or powerful benefics, the algorithm indicates immense spiritual capacity, saintliness, and non-attachment to material wealth.31  
* **3rd House**: IF occupied by malefics, the output indicates immense physical courage and absolute success in complex undertakings. IF occupied by benefics, the output flags passivity or defeat.31  
* **4th House**: Defines the emotional and physical real estate. IF Ketu occupies the 4th (or 12th) house from Karakamsha, the engine must flag a definitive Moksha Yoga (spiritual liberation).32  
* **5th House**: Evaluates Dharma Parayana (obedience to universal law). IF Jupiter or the 5th lord interacts here, the engine indicates the acquisition of highly specialized, traditional intelligence.31  
* **6th House**: IF heavily afflicted by malefics, the engine flags chronic diseases and heavy karmic debts requiring resolution.31  
* **7th House**: Crucial for evaluating the reality of marriage. IF benefics occupy this house, it assures a pure heart and a joyful union. IF Venus is strong here, marital bliss is heavily fortified.31  
* **8th House**: IF occupied by planets, it indicates the acquisition of occult knowledge, but simultaneous exposure to sudden troubles, physical weakness, or defeat in warfare.31  
* **9th House**: Indicates deep piety, fortune, and adherence to the teachings of the Guru.31  
* **10th House**: Represents the pillar of the family and objective career. IF the 10th house is vacant, the algorithm must select the Lord of the 10th from the Karakamsha to dictate the exact profession.31  
* **11th House**: Denotes gains, bravery, and execution capability. IF a strong Mars is present, the engine triggers a Raja Yoga condition for military or executive success.31  
* **12th House**: The domain of the Ishta Devata. The strongest planet occupying the 12th house (or aspecting it via Rashi Drishti if vacant) indicates the specific deity guiding the soul toward ultimate liberation. IF Ketu is placed here, it indicates definitive spiritual emancipation in the current incarnation.32

## **SECTION 5: JAIMINI YOGAS (NON-PARASHARI)**

Jaimini Yogas operate through a fundamentally different mechanism than Parashari Yogas. They completely ignore house lordships and geometric planetary aspects, relying instead on Rashi Drishti and specific spatial combinations between the Chara Karakas.

### **Atmakaraka (AK) and Amatyakaraka (AmK) Combinations**

The Atmakaraka represents the sovereign soul, while the Amatyakaraka represents the "minister"—the intellectual, financial, and professional executor of the soul's desires.35

SUTRA 4 — Plain English: The seamless association of the sovereign soul with its minister creates a Raja Yoga of the highest material order. — Computational IF/THEN rule: IF the Atmakaraka and Amatyakaraka are physically conjunct in the same sign OR aspect each other via mutual Rashi Drishti, THEN a primary Jaimini Raja Yoga is formed. The engine must output a guarantee of significant career elevation, status, and social power during the activation of their respective Dashas.35

### **Unique Algorithmic Raja Yogas**

* **AK and Darakaraka (DK)**: IF the AK and DK conjoin or aspect each other via Rashi Drishti, the engine generates a powerful Raja Yoga conferring wealth and success that specifically manifests through, or immediately following, marriage or major business partnerships.37  
* **AK and Putrakaraka (PK)**: IF the AK and PK interact, the engine flags a trajectory of massive public following, intellectual brilliance, and status derived primarily from creative outputs, students, or devoted followers.37  
* **Moon and Venus Synergy**: A highly specific Jaimini rule requires the engine to track the Moon and Venus. IF the Moon and Venus conjoin or aspect each other via Rashi Drishti, OR IF Venus is placed precisely in the Karakamsha Lagna, the algorithm triggers an intense Raja Yoga ensuring the acquisition of extreme luxury, vehicles, and comforts.37

### **AK in Navamsha Signs (Svamsha Implications)**

The zodiacal sign placement of the AK in the Navamsha (the Svamsha) directly encodes the specific karmic struggles and physical realities the native will endure. The computational engine must map the AK's D-9 sign to the following fixed outcomes:

| Svamsha Sign (D-9) | Algorithmic Output / Life Path Indication |
| :---- | :---- |
| Aries | Susceptibility to bites from rodents or cats; highly aggressive baseline. |
| Taurus | Wealth derived from, or physical trouble caused by, quadrupeds. |
| Gemini | Dermatological sensitivities, allergies, and severe weight fluctuations. |
| Cancer | Vulnerability to dangers from water or aquatic environments. |
| Leo | Encounters with wild beasts, risk of public humiliation, or dominant nature. |
| Virgo | Issues related to fire, gastrointestinal heat, and severe digestive distress. |
| Libra | Excellence in trade and commerce, coupled with potential falls from physical heights. |
| Scorpio | Deprivation of mother's milk in infancy or severe aquatic dangers. |
| Sagittarius | Vulnerability to falls from conveyances, animals, or high altitudes. |
| Capricorn | Hazards from aquatic creatures, birds, or complex, enduring psychic trauma. |
| Aquarius | A life defined by service to others; philanthropic but laborious and exhausted. |
| Pisces | The pinnacle of spiritual liberation (Moksha) and the establishment of philanthropic institutions. |

## **SECTION 6: PADA ASPECTS AND THEIR EFFECTS**

The Arudha Padas represent the concept of *Maya*—the perceived manifestation, illusion, and tangible external reality of a house's internal, abstract indications. The algorithm computes the Arudha by counting the distance from a house to its lord, and projecting that same distance forward from the lord.

### **Arudha Lagna (AL) and Upapada Lagna (UL) Dynamics**

The AL (Arudha of the 1st house) represents the public image and perceived status of the native. The UL (Arudha of the 12th house) represents the perceived reality of the marriage, the spouse, and intimate bed comforts.28

* **Planets Aspecting AL**: The engine evaluates planets aspecting the AL via Rashi Drishti. Benefic planets aspecting the AL sustain and aggressively elevate the native's public reputation. Malefics aspecting the AL damage the public image through scandal and controversy.38  
* **Rahu and Ketu on AL**: SUTRA 5 — Plain English: The nodes impacting the perceived image or its direct opposite cause digestive destruction and fiery distress. — Computational IF/THEN rule: IF Rahu or Ketu is placed precisely in the AL OR in the 7th house from the AL, THEN flag the native for severe, chronic stomach disorders, a high risk of accidents involving fire, and deeply rooted marital distress.39  
* **AL and UL Relationship Algorithm**: To compute the sustainability of a marriage, the engine measures the spatial distance between the AL and the UL. IF the AL and UL are positioned in Kendras (1st, 4th, 7th, 10th) or Trikonas (1st, 5th, 9th) relative to one another, the algorithm predicts a sustainable, publically supported marriage. IF the AL and UL are positioned in a 6/8 or 2/12 axis relative to one another, the engine must output a prediction of fundamental, irreconcilable friction between the native's public trajectory and their private marital harmony, often leading to separation.28

### **Rajya Pada (A10) Analysis**

The A10 (Arudha of the 10th house) indicates how the native's career, authority, and professional actions are perceived by the wider public and power structures.40

* **Benefic Influence**: Benefics conjoining or aspecting A10 ensure an untarnished professional reputation, social grace, and steady promotions without conflict.  
* **Malefic Influence**: Malefics influencing the A10 indicate that power is gained and maintained through aggressive, controversial, dictatorial, or manipulative means.

### **Contraargala on Arudha Padas**

The complex mathematical concept of Argala applies robustly to the evaluation of Padas. For example, if the A10 has a strong benefic in the 2nd house from it, that planet provides massive resources (Argala) for career growth. However, the engine must constantly check the opposing coordinate. If a powerful malefic sits in the 12th house from the A10 (creating Virodha Argala), it acts as a severe Contraargala. This dynamically drains the resources and completely blocks the manifestation of the career leap until the obstruction is mathematically resolved through a planetary transit or a shift in the Dasha period.38

## **SECTION 7: NAVAMSHA ANALYSIS DEPTH (JAIMINI METHOD)**

In traditional Parashari astrology, the Navamsha (D-9) is heavily weighted as a supplementary chart specifically for marriage and the later half of life. In the Jaimini algorithm, the Navamsha is elevated to the absolute microscopic map of the soul's strength and destiny, possessing veto power over the D-1 chart.

### **Vargottama in the Jaimini Context**

A planet achieves Vargottama status when it occupies the exact same zodiacal sign in both the D-1 Rashi chart and the D-9 Navamsha chart. In the Parashari system, this equates roughly to the strength of an exalted planet. In the Jaimini algorithmic system, a Vargottama planet achieves a state of supreme, unalterable deterministic power.

SUTRA 6 — Plain English: A Vargottama planet enforces its assigned Chara Karaka mandate without fail, crushing all opposing geometric afflictions. — Computational IF/THEN rule: IF a planet mathematically qualifies as Vargottama AND acts as the Amatyakaraka (career significator), THEN the engine must guarantee a highly successful professional trajectory, explicitly overriding and ignoring standard D-1 afflictions such as debilitation or malefic conjunctions.41 The Vargottama status permanently locks the planet's agenda into the native's destiny matrix.

### **Pushkara Navamsha Activation**

Pushkara Navamshas are 24 highly specific Navamsha divisions (two per zodiacal sign, all ruled by natural benefics) that possess extreme, almost magical regenerative and healing capacities.42

The algorithmic integration of Pushkara Navamshas requires a tracking subroutine during Dasha generation. IF the active Jaimini Dasha running belongs to a sign that contains a planet placed in a Pushkara Navamsha, OR IF the exact degree of the Dasha sign's cusp falls into a Pushkara Navamsha zone, the engine must flag the entire temporal period as yielding extraordinary nourishment, exponential growth, and rapid recovery. This calculation explicitly overrides general malefic transits occurring during that time, forcing a positive output.42

## **SECTION 8: TIMING OF EVENTS — JAIMINI SPECIFIC RULES**

The predictive accuracy of the Jaimini engine relies on the mathematical convergence of Rashi Dashas, the longitudinal progression of Chara Karakas, and the spatial positioning of Arudha Padas.

### **The "3 Concurrent Confirmations" Rule**

To output a high-confidence prediction for any major life event, the algorithmic engine must find mathematical verification across three completely independent timing vectors.44 If only one or two vectors confirm the event, the probability output drops significantly.

1. **Vimshottari Dasha Vector**: Analyzes the Nakshatra-based timing to confirm the native's mental readiness and general environmental phasing.  
2. **Jaimini Rashi Dasha Vector**: Analyzes the Chara, Trikona, or Narayana Dasha to map the exact situational, circumstantial, and physical shift in the material world.  
3. **Transit (Gochar) Vector**: Tracks the real-time movement of heavy planets (Saturn and Jupiter) making exact aspects onto specific Jaimini focal points (such as Padas or Karakas).

### **Timing Marriage (UL \+ Chara Dasha)**

SUTRA 7 — Plain English: The physical event of marriage occurs when the time period simultaneously activates the spouse indicator and the house of bed comforts. — Computational IF/THEN rule: IF the active Chara Dasha sign contains the Darakaraka (DK) OR contains the Upapada Lagna (UL) OR aspects them via Rashi Drishti, AND real-time Transit Jupiter or Saturn aspects the UL or its Lord via Graha Drishti, THEN output a high-confidence probability for the occurrence of marriage.46

### **Timing Career Peaks (A10 \+ Chara Dasha)**

SUTRA 8 — Plain English: A rapid professional rise mathematically correlates with the activation of the executive minister and the public image of action. — Computational IF/THEN rule: IF the active Chara Dasha sign corresponds to the 10th house from the Lagna, OR contains the Amatyakaraka (AmK), OR strongly aspects the A10 (Rajya Pada) via Rashi Drishti without Virodha Argala obstruction, THEN forecast a significant, highly visible career event, promotion, or elevation in status.40

### **Timing Death (Shoola Dasha)**

SUTRA 9 — Plain English: The definitive physical end of the body arrives during the overlapping periods of the destructive trident. — Computational IF/THEN rule: IF the native is currently within the Shoola Maha Dasha of a Trishoola sign (specifically the 1st, 5th, or 9th sign from the location of the active Rudra planet), AND the running Shoola Antar Dasha corresponds exactly to the 6th, 7th, 8th, or 12th sign computed from the Dasha sign or the Arudha Lagna, THEN flag the temporal window as a highly critical period for mortality.16 The exact timeline of death within this window is further localized and confirmed by evaluating the precise Dasha of the Sthira Karakas within this matrix.1

#### **Works cited**

1. Karakas Significators \- Learning Astrology \- Wikidot, accessed on February 28, 2026, [http://astroveda.wikidot.com/karakas-significators](http://astroveda.wikidot.com/karakas-significators)  
2. The Karakas I \- Varahamihira, accessed on February 28, 2026, [http://varahamihira.blogspot.com/2005/02/karakas-i.html](http://varahamihira.blogspot.com/2005/02/karakas-i.html)  
3. Jaimini Astrology: Understanding Karakas | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/215062336/THE-SIGNIFICANCE-OF-KARAKAS-IN-JAIMINI-ASTROLOGY](https://www.scribd.com/document/215062336/THE-SIGNIFICANCE-OF-KARAKAS-IN-JAIMINI-ASTROLOGY)  
4. Introduction to Vedic Astrology | Panchanga.lv, accessed on February 28, 2026, [http://www.panchanga.lv/wp-content/uploads/2020/06/Introduction-to-Vedic-Astrology-Sanjay-Rath.pdf](http://www.panchanga.lv/wp-content/uploads/2020/06/Introduction-to-Vedic-Astrology-Sanjay-Rath.pdf)  
5. Drsti Bheda: Rashi, Graha and Bhava \- Shubham Alock, accessed on February 28, 2026, [https://shubhamalock.com/drsti-bheda/](https://shubhamalock.com/drsti-bheda/)  
6. Rules \- For Planet Aspects | PDF | Planets In Astrology | Divination \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/86352252/Rules-For-Planet-aspects](https://www.scribd.com/document/86352252/Rules-For-Planet-aspects)  
7. Some Important Jamini Concepts to Know \- The Art of Vedic Astrology, accessed on February 28, 2026, [https://www.theartofvedicastrology.com/?page\_id=553](https://www.theartofvedicastrology.com/?page_id=553)  
8. Understanding Graha Drishti in Vedic Astrology | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/461799361/1-5048830860715884681](https://www.scribd.com/document/461799361/1-5048830860715884681)  
9. Understanding Argala in Jaimini Astrology | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/253520288/Argala-the-Linchpin](https://www.scribd.com/document/253520288/Argala-the-Linchpin)  
10. Argala: The Planetary Mechanism for Quantifying Chart Strength : r/Nakshatras \- Reddit, accessed on February 28, 2026, [https://www.reddit.com/r/Nakshatras/comments/1o6hpgy/argala\_the\_planetary\_mechanism\_for\_quantifying/](https://www.reddit.com/r/Nakshatras/comments/1o6hpgy/argala_the_planetary_mechanism_for_quantifying/)  
11. Argala in Jaimini Upadesa Sutras \- Asheville Vedic Astrology \- WordPress.com, accessed on February 28, 2026, [https://ashevillevedicastrology.wordpress.com/2014/11/10/argala-in-jaimini-upadesa-sutras/](https://ashevillevedicastrology.wordpress.com/2014/11/10/argala-in-jaimini-upadesa-sutras/)  
12. Argala: Planetary Intervention \- Argalā \- Sanjay Rath, accessed on February 28, 2026, [https://srath.com/jyoti%E1%B9%A3a/amateur/argala-planetary-intervention/](https://srath.com/jyoti%E1%B9%A3a/amateur/argala-planetary-intervention/)  
13. Jaimini Astrology: Key Concepts and Techniques | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/394130426/A-BRIEF-INTRODUCTION-TO-JAIMINI-ASTROLOGY-NOTES-FOR-STUDENTS-pdf](https://www.scribd.com/document/394130426/A-BRIEF-INTRODUCTION-TO-JAIMINI-ASTROLOGY-NOTES-FOR-STUDENTS-pdf)  
14. Niryana Shoola Dasa | PDF | Astrology | Ancient Astronomy \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/6001426/Niryana-Shoola-Dasa](https://www.scribd.com/document/6001426/Niryana-Shoola-Dasa)  
15. Niryana Sula Dasa By Iranganti Rangacharya \- Saptarishis Astrology, accessed on February 28, 2026, [https://saptarishisshop.com/niryana-sula-dasa-by-iranganti-rangacharya/](https://saptarishisshop.com/niryana-sula-dasa-by-iranganti-rangacharya/)  
16. Shoola Dasha for Longevity: Classical Analysis Guide \- AstroSight, accessed on February 28, 2026, [https://astrosight.ai/transits/shoola-dasha-longevity](https://astrosight.ai/transits/shoola-dasha-longevity)  
17. Niryana Shoola Dasa Explained | PDF | Occult | Divination \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/232352637/%D0%A0%D0%B0%D0%BC%D0%B0%D0%BD-Niryana-Shoola-Dasa](https://www.scribd.com/document/232352637/%D0%A0%D0%B0%D0%BC%D0%B0%D0%BD-Niryana-Shoola-Dasa)  
18. Jaimini Navamsha Dasha Salient Features and Calculation | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/516137043/Jaimini-Navamsha-Dasha-Salient-Features-and-Calculation](https://www.scribd.com/document/516137043/Jaimini-Navamsha-Dasha-Salient-Features-and-Calculation)  
19. NAVAMSA DASA: PART \-6 \- Shubham Alock Singh, accessed on February 28, 2026, [https://shubhamalock.wordpress.com/2016/10/21/navamsa-dasa-part-6/](https://shubhamalock.wordpress.com/2016/10/21/navamsa-dasa-part-6/)  
20. Shula Dasha \- Sanjay Rath, accessed on February 28, 2026, [https://srath.com/jyoti%E1%B9%A3a/dasa/shula-dasha/](https://srath.com/jyoti%E1%B9%A3a/dasa/shula-dasha/)  
21. Sthira dasha in jaimini astrology brahma maheshwara & rudra | DOCX \- Slideshare, accessed on February 28, 2026, [https://www.slideshare.net/slideshow/sthira-dasha-in-jaimini-astrology-brahma-maheshwara-rudra/34620981](https://www.slideshare.net/slideshow/sthira-dasha-in-jaimini-astrology-brahma-maheshwara-rudra/34620981)  
22. Sree Lagna Stands For Lakshmi | PDF | Hindu Astrology \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/doc/12807366/Sree-Lagna-Stands-for-Lakshmi](https://www.scribd.com/doc/12807366/Sree-Lagna-Stands-for-Lakshmi)  
23. Sudasha | Parijaata, accessed on February 28, 2026, [https://parijaata.wordpress.com/tag/sudasha/](https://parijaata.wordpress.com/tag/sudasha/)  
24. Understanding Drig Dasa in Jaimini Astrology | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/169415126/Drig-Dasa](https://www.scribd.com/document/169415126/Drig-Dasa)  
25. Jaimini Dashas Drig & Char Paryaya | PDF | Planets In Astrology | Superstitions \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/516137041/Jaimini-Dashas-Drig-Char-Paryaya](https://www.scribd.com/document/516137041/Jaimini-Dashas-Drig-Char-Paryaya)  
26. Understanding Drigdasa in Astrology | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/doc/128917374/drik-am](https://www.scribd.com/doc/128917374/drik-am)  
27. Trikona Dasa – A Critical Review By Iranganti Rangacharya | Saptarishis Astrology, accessed on February 28, 2026, [https://saptarishisshop.com/trikona-dasa-a-critical-review-by-iranganti-rangacharya/](https://saptarishisshop.com/trikona-dasa-a-critical-review-by-iranganti-rangacharya/)  
28. Jaimini Astrology and Marriage \- Sachin Malhotra, accessed on February 28, 2026, [https://astrologicalmusings.com/jaimini-astrology-and-marriage/](https://astrologicalmusings.com/jaimini-astrology-and-marriage/)  
29. Swamsa Bhava: Jaimini Karakamsa: Atmakaraka Navamsa \- Shubham Alock, accessed on February 28, 2026, [https://shubhamalock.com/swamsa-bhava/](https://shubhamalock.com/swamsa-bhava/)  
30. The Structure Of Jaimini Astrology By Gary Gomes, accessed on February 28, 2026, [https://saptarishisshop.com/the-structure-of-jaimini-astrology-by-gary-gomes/](https://saptarishisshop.com/the-structure-of-jaimini-astrology-by-gary-gomes/)  
31. Atmakaraka & Karakamsa \- Sanjay Rath, accessed on February 28, 2026, [https://srath.com/jyoti%E1%B9%A3a/scholar/atmakaraka-karakamsa/comment-page-1/](https://srath.com/jyoti%E1%B9%A3a/scholar/atmakaraka-karakamsa/comment-page-1/)  
32. Karakamsa | PDF | Planets In Astrology \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/doc/51021250/karakamsa](https://www.scribd.com/doc/51021250/karakamsa)  
33. Jaimini Astrology: Understanding Karakas | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/340012974/Jamini](https://www.scribd.com/document/340012974/Jamini)  
34. Profession in Jamini System \- astro giva, accessed on February 28, 2026, [https://astrogiva.com/profession-in-jamini-system/](https://astrogiva.com/profession-in-jamini-system/)  
35. Amatyakaraka in Jaimini Astrology: Significations and Interpretations from Jaimini Upadesha Sutras \- astrosutras.in, accessed on February 28, 2026, [https://astrosutras.in/index.php/2025/02/27/amatyakaraka-in-jaimini-astrology-significations-and-interpretations-from-jaimini-upadesha-sutras/](https://astrosutras.in/index.php/2025/02/27/amatyakaraka-in-jaimini-astrology-significations-and-interpretations-from-jaimini-upadesha-sutras/)  
36. How will parivartan yoga between Atmakarak and Amatyakarak manifest? \- Reddit, accessed on February 28, 2026, [https://www.reddit.com/r/Nakshatras/comments/1lu3e2u/how\_will\_parivartan\_yoga\_between\_atmakarak\_and/](https://www.reddit.com/r/Nakshatras/comments/1lu3e2u/how_will_parivartan_yoga_between_atmakarak_and/)  
37. Jamini Raj Yoga in Vedic Astrology (Jamini Lesson 5\) \- YouTube, accessed on February 28, 2026, [https://www.youtube.com/watch?v=7IEsxiax7II](https://www.youtube.com/watch?v=7IEsxiax7II)  
38. Understanding Arudha Lagna in Astrology | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/310031340/Planets-in-Signs-and-Houses-Arudha-Lagna-by-Sh-Sanjay-Rath](https://www.scribd.com/document/310031340/Planets-in-Signs-and-Houses-Arudha-Lagna-by-Sh-Sanjay-Rath)  
39. Arudha Pada | PDF | Planets In Astrology \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/490087/Arudha-Pada](https://www.scribd.com/document/490087/Arudha-Pada)  
40. Jaimini Chara Dasha for Career: A Timing Guide \- AstroSight, accessed on February 28, 2026, [https://astrosight.ai/transits/jaimini-chara-dasha-career-insights](https://astrosight.ai/transits/jaimini-chara-dasha-career-insights)  
41. Simple and easy way to understand D-9 (Navamsha Chart) | JYOTHISHI, accessed on February 28, 2026, [https://vijayalur.com/2013/12/21/simple-and-easy-way-to-decipher-d-9-navamsha-chart/](https://vijayalur.com/2013/12/21/simple-and-easy-way-to-decipher-d-9-navamsha-chart/)  
42. Pushkara \- Navamsha and Bhaga \- Komilla | Vedic Astrology, accessed on February 28, 2026, [https://komilla.com/lib-pushkara-part-two.html](https://komilla.com/lib-pushkara-part-two.html)  
43. Pushkara Navamsha and Pushkara Bhaga | JYOTHISHI, accessed on February 28, 2026, [https://vijayalur.com/2013/07/26/pushkara-navamsha-and-pushkara-bhaga/](https://vijayalur.com/2013/07/26/pushkara-navamsha-and-pushkara-bhaga/)  
44. Jaimini Astrology KNRao | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/455383652/JaiminiAstrologyKNRao](https://www.scribd.com/document/455383652/JaiminiAstrologyKNRao)  
45. A Simple Approach to Demystify Timing of Events in Vedic Astrology \- Medium, accessed on February 28, 2026, [https://medium.com/@ranjanpal9/a-simple-approach-to-demystify-timing-of-events-in-vedic-astrology-974f1af92671](https://medium.com/@ranjanpal9/a-simple-approach-to-demystify-timing-of-events-in-vedic-astrology-974f1af92671)  
46. Timing Of Marriage By Transits And Jaimini Astrology By Gautam Dave, accessed on February 28, 2026, [https://saptarishisshop.com/timing-of-marriage-by-transits-and-jaimini-astrology-by-gautam-dave/](https://saptarishisshop.com/timing-of-marriage-by-transits-and-jaimini-astrology-by-gautam-dave/)  
47. Niryana Shoola Dasa \- Learning Astrology \- Wikidot, accessed on February 28, 2026, [http://astroveda.wikidot.com/niryana-shoola-dasa](http://astroveda.wikidot.com/niryana-shoola-dasa)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAXCAYAAACmnHcKAAACc0lEQVR4Xu2Wz4tPURjG34mR0GyE/EqamixJbDQRihoJaVKzmp2wmAULUaY0jWQjSRQlKZGFnQULRZKYYmWa1aQslJQ/wDxP73n7vvf9nnPnJqPU/dRT977vuefc55z3nHtFWloWiqUx8L9yHnoJrYwJzwDUE4OJXmg1tApaFHKEHV+C3kAXQs7gc2ugfmhFyHms3QbRcT3LoEeihipsh0ahKeg39ES6B2FnV6FBUaProafQK2hjasP43nRteEPMn4SGRctjCHoHzaZr3+40dANaLtr2HHTFtdkP/Uq5CuOinY5BzyVvZhf0DdrpYgdFzV9L93yGM+m5nuJkK/TJ5cgW0T4+uBjbzYhWgMGX5vgGV4RminBQGsmZOSr68H3pzAYH5Yuwbsl8K0NjbH8HWuzi7Jdxlg55m+4jjHELkI+SKTFPnRmW2TGpbjaWBge46WIPoT2i9b5POiVIzoq2n5DqnuQqMG5jfk33EcZZXuQLtMPluqgzEzkiuuwnpHxYNIUv7l8+3hs0fTldL/GJHE3MjEC3oB/Qs5D7E3hS8cVfuFidGZZqI5qYMezE4YbeFnJNOSS6urtD/J+bITwISgPPB/cSV2NzTEi5T5o5E4Ml6sxw9sele3/YwDFeR5/oB88f42ulc8J9l7wZHgDHY7BEnRk7Pg+4GNuUZrEET8UHooYMmuBxbfD4z/XJmH+uljoz70U787O5KcXih7CE7bO7on8TJvbtP4hDoqvj34GGcwa7YB3aDEfZSnBGT0HT0D3odcrb700T7KOZ02fXjnAFWA2PodvQT2hdpcVf4DA0CV0UNbKQ8A+D41C8bmlpackzB+4ZkZv10Le9AAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAXCAYAAACMLIalAAACJklEQVR4Xu2Vz4uOURTHj1CT/Cib2TBGIQsLKWUjypTCf6DYWEzIlFhImSglkWxmoSyskJJkJRshSZlYWFGTjcVslD+A7+c957zvfe6888xrMSvvp7697zn33PPce8597mM2ZMjyskEaldbWA30gZo/5nH5slPZJI/VAMC29ky5L66qxDiT/Yr3B49JP6Yy0IoOCvdIHaX/YB6UL3VGzY+Zz2RxkrvVhk+9q/E+OVnaH++YTc1dU4Yn0TdqdQeaL/yqNhb1dmjWPzeq+iZiERVyXToZN3N3ecIe+3Xku/ZEOFD4m4jtR+H5LnwqbBx6RtoVNYubc6kY4bGzePP/AldoqXbJeq2jjU2nOvF1AFXkgVVmMcfOYs4v4J8PebN72ldIh6WH4W3lsniTPBbBLfDPSS+mc9MP8fCWHI6ZeFHnwP6j8A3HNvJXfpdPVGCUmMecsz16esZ1hL7WotiovCeV9Ld2QVoePB5GYtpbgnzNv87IuCrJd78OeCLt+c3Kx/HIvtS2qntvKKel85eONIRGthF1h14nLRe0o/peMh5+XaSDWmE9A5V2RrchKAfajwoYpa76lxNzrjjpU/aO0pfK3QiLepBJuafwc/oRDTvJklfkC7ljv7BFTbgTIxQVafx1a4fJ7Ib2Sbpvf7r9s4TeJB/Ot+mzeRmKeNSI85op5Lo4Fm33biPgHuMguSjfNb/FNzeEGXILE0Rbm9SNztcUMGfL/8hc5enac5JENrAAAAABJRU5ErkJggg==>