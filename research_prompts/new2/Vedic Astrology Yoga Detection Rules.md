# **Computational Rules for Vedic Astrological Yoga Detection: A Technical Framework**

The development of a sophisticated computational Vedic astrology engine requires the rigorous translation of qualitative classical Sanskrit maxims into mathematically verifiable, boolean, and weighted programmatic logic. In the traditional system of Hindu astrology (Jyotish), a "Yoga" denotes a highly specific planetary configuration that predictably influences an individual's psychological patterns, material circumstances, health vectors, and overarching karmic trajectory. To programmatically identify these conditions without yielding erroneous false positives, a computational engine must deploy a multi-layered evaluation pipeline. This pipeline must be capable of detecting the base formation, assessing modifying constraints (such as planetary blemishes or combustion), calculating relative strength via Shadbala (six-fold strength) and positional dignity, and finally, processing strict cancellation (Bhanga) overrides.

This research report establishes the complete computational detection rules, strength grading architectures, and cancellation algorithms for the core astrological yoga categories required for a comprehensive programmatic engine. The ruleset is designed to bridge the gap between classical texts, such as the *Brihat Parashara Hora Shastra* and *Jataka Parijata*, and modern algorithmic implementation.

## **Foundational Computational Parameters and Architecture**

Before evaluating specific yogas, the computational engine must rigorously define the parameters of planetary association (Sambandha), structural domains (Bhavas), and the hierarchy of grading.

**Categorization of Astrological Houses (Bhavas):**

* **Kendra Houses (Angles/Vishnusthanas):** Houses 1, 4, 7, and 10\. These represent action, structural capacity, free will, and worldly manifestation.1  
* **Trikona Houses (Trines/Lakshmisthanas):** Houses 1, 5, and 9\. These represent fortune, divine purpose, intelligence, and accumulated past-life merit (Purva Punya).1 The 1st house serves as both a Kendra and a Trikona.3  
* **Trika / Dusthana Houses (Malefic/Hidden):** Houses 6, 8, and 12\. These represent obstacles, loss, disease, hidden karmic debts, and the dissolution of material assets.4  
* **Upachaya Houses (Growth):** Houses 3, 6, 10, and 11\. These represent areas of life that improve over time through effort and maturation.5

**Definition of Sambandha (Planetary Association):** A valid relationship between two planets in the computational engine requires the fulfillment of at least one of the following boolean conditions 1:

1. *Conjunction (Yuti):* Two or more planets occupying the same zodiacal sign (Rasi), or mathematically, their exact longitudes falling within a predefined orb (typically ![][image1]).  
2. *Mutual Aspect (Paraspara Drishti):* Planets positioned in mutually opposing 7th houses, or engaged via special planetary aspects (Mars projecting to the 4th/8th houses, Jupiter projecting to the 5th/9th houses, and Saturn projecting to the 3rd/10th houses).  
3. *Exchange (Parivartana):* Planet A resides in Planet B's ruled sign, and Planet B resides in Planet A's ruled sign, creating a closed energetic loop.

**Universal Grading Matrix:** The engine must grade every detected yoga into a defined tier to determine its manifestation probability and intensity 8:

* **Tier S (Apex/100% Manifestation):** Exact degree associations occurring in Kendra or Trikona houses, involving exalted, Moolatrikona, or Vargottama planets, entirely free from malefic influence.  
* **Tier A (Strong/75% Manifestation):** Association occurring in friendly signs, possessing high Shadbala scores, with minimal to no malefic affliction.  
* **Tier B (Moderate/50% Manifestation):** Base association present but lacking special dignity, possessing average Shadbala, or suffering from minor malefic aspects.  
* **Tier C (Weak/25% Manifestation):** Association occurring in Upachaya or neutral houses, weak Shadbala, or severely dampened by malefic interference.

## ---

**1\. Dharma-Karma Adhipati Yogas (DKA)**

The Dharma-Karma Adhipati (DKA) Yoga is universally considered the absolute apex of the Kendra-Trikona Raja Yogas. It represents the ultimate synthesis of destiny, fortune, and righteousness (the 9th house, Dharma) cooperating flawlessly with action, profession, and temporal authority (the 10th house, Karma).1

### **Computational Formation Rules**

Let ![][image2] be defined as the ruling planet of the 9th house, and ![][image3] be defined as the ruling planet of the 10th house. **Primary Condition:** A valid Sambandha (Conjunction, Mutual Aspect, or Parivartana Exchange) must exist between ![][image2] and ![][image3].6 **Positional Multiplier:** The yoga algorithm must apply a positive multiplier if this association occurs in the 1st, 2nd, 7th, 9th, or 10th houses, as these placements dramatically amplify the social prestige and executive efficiency granted by the yoga.10

### **Exhaustive Combinations by Ascendant (Lagna)**

The computational engine must dynamically map the exact ![][image2] and ![][image3] planets for all 12 astrological ascendants. Furthermore, the classical treatises note that certain lagnas suffer from an inherent "blemish" (Dosha) if either ![][image2] or ![][image3] simultaneously rules a malefic or problematic house, such as the 3rd, 6th, 8th, or 11th houses.11 The algorithm must apply a dampening multiplier to these specifically blemished configurations to accurately reflect their output.

| Lagna (Ascendant) | 9th Lord (L9​) | 10th Lord (L10​) | Computational Blemish Rule & Algorithmic Dampener |
| :---- | :---- | :---- | :---- |
| **Aries (Mesha)** | Jupiter | Saturn | Saturn simultaneously rules the 11th house. Apply moderate blemish dampener.11 |
| **Taurus (Vrishabha)** | Saturn | Saturn | Saturn rules both houses, becoming the absolute Yogakaraka. No blemish. S-Tier base.11 |
| **Gemini (Mithuna)** | Saturn | Jupiter | Saturn simultaneously rules the 8th house. Apply severe blemish dampener.11 |
| **Cancer (Karka)** | Jupiter | Mars | No blemish. Highly auspicious combination.11 |
| **Leo (Simha)** | Mars | Venus | Venus simultaneously rules the 3rd house. Apply mild blemish dampener.11 |
| **Virgo (Kanya)** | Venus | Mercury | No blemish. Excellent configuration.11 |
| **Libra (Tula)** | Mercury | Moon | No blemish. Highly favorable.11 |
| **Scorpio (Vrishchika)** | Moon | Sun | No blemish. The two luminaries combine, generating extreme visibility.10 |
| **Sagittarius (Dhanu)** | Sun | Mercury | No blemish.10 |
| **Capricorn (Makara)** | Mercury | Venus | Mercury simultaneously rules the 6th house. Apply mild blemish dampener.11 |
| **Aquarius (Kumbha)** | Venus | Mars | Mars simultaneously rules the 3rd house. Apply mild blemish dampener.11 |
| **Pisces (Meena)** | Mars | Jupiter | No blemish. Pure synergistic combination.11 |

### **Cancellation (Bhanga) Rules**

1. **Trika Nullification:** If either ![][image2] or ![][image3] is positioned in the 6th, 8th, or 12th house from the Ascendant, the DKA yoga is effectively nullified. The engine must drop the tier to C or zero, as the structural foundation of the yoga is cracked.1  
2. **Combustion Override:** If the dispositor (the ruler of the sign) where the DKA yoga is formed is heavily combusted by the Sun, or if the Lagna lord itself is combusted, the engine must flag the yoga as failing to fructify in physical reality.6  
3. **Navamsha Degradation:** To maintain an S-Tier or A-Tier rating, the planetary association must retain its dignity in the D9 (Navamsha) divisional chart. If the planets fall into debilitation in the D9 chart, their computational power is diminished.10  
* **Primary Domain Affected:** Career, Social Prestige, Executive Authority, and Life Purpose.  
* **Relative Strength Tiering:**  
  * **S-Tier:** Conjunction in the 9th or 10th house without any lagna-based blemishes, un-aspected by malefics.  
  * **A-Tier:** Mutual aspect across the 1st and 7th houses, or Parivartana exchange.  
  * **B-Tier:** Wide conjunction (beyond a ![][image4] orb) or presence in Upachaya houses.  
  * **C-Tier:** Formation occurring in severely blemished lagnas (e.g., Gemini) with only moderate Shadbala scores.

## ---

**2\. Complete Dhana Yogas (Wealth Formations)**

Dhana Yogas dictate the native's capacity to attract, accumulate, and safely retain financial resources over their lifetime. Computationally, wealth generation is evaluated as a mathematical matrix involving the primary houses of accumulation (2nd), speculative gain and intelligence (5th), cosmic fortune (9th), and liquid profit/fulfillment of desires (11th).13

### **Core Computational Formation Logic**

The foundational Dhana Yoga algorithm detects any combinatorial association (Conjunction, Mutual Aspect, or Parivartana Exchange) strictly between the lords of the wealth matrix: ![][image5].13

* **The Accumulation Vector (![][image6]):** This is the fundamental wealth circuit. It merges liquid gains and daily income (11th) directly with stored familial assets and bank balances (2nd). When these two lords associate, a steady, unbreakable income flow is generated.13  
* **The Fortune Vector (![][image7]):** This combination blends past-life merit (5th) with pure fortune and destiny (9th), frequently generating sudden windfalls, lottery luck, or massive returns on investments.13  
* **The Cross-Vectors:** The association of an accumulation lord (![][image8]) with a fortune lord (![][image9]). The computational engine should weight ![][image10] and ![][image11] higher than 11th house connections, due to the inherent purity of the 2nd house compared to the 11th house, which is also an Upachaya and can carry mild malefic traits.15

### **Lakshmi Yoga: The Apex Wealth Multiplier**

Lakshmi Yoga is a highly specific classical variant that guarantees aristocratic wealth, a luxurious lifestyle, physical attractiveness, and massive fortune in ventures. The engine must strictly query for this exact formation.16

**Algorithmic Condition:** IF (L9.Strength \== HIGH AND L9.Placement IN ) AND (Venus.Placement IN AND Venus.Sign IN \[Own, Exalted\]) THEN RETURN Lakshmi\_Yoga (Tier S).16 This yoga invokes the direct blessings of the Goddess of Wealth, providing substantial financial immunity.

### **Exhaustive List of Classical Wealth Yogas**

To be complete, the engine must parse for specific planet-based wealth yogas:

1. **Gajakesari Yoga (Wealth/Status Variant):** Jupiter placed in a Kendra (1st, 4th, 7th, 10th) from the Moon. This grants a lasting reputation, generosity, and financial protection throughout life. Yields an A-Tier financial safety net.18  
2. **Sunapha Yoga:** Any planet (excluding the Sun, Rahu, and Ketu) positioned in the 2nd house from the Moon. This mathematically indicates that the mind (Moon) is supported by resources, generating self-earned wealth, property accumulation, and financial intelligence.18  
3. **Saraswati Yoga:** Jupiter, Venus, and Mercury are all placed in Kendra houses, Trikona houses, or the 2nd house, and Jupiter possesses high strength. This generates massive wealth through intellectual pursuits, the arts, and knowledge.19  
4. **Amala Yoga:** A naturally benefic planet (Jupiter, Venus, or an unafflicted Mercury/Moon) occupying the 10th house from the Ascendant or the Moon. Grants spotless wealth and considerable fame.20  
5. **Chandra-Mangala Yoga:** The Moon and Mars occupying the same house. This specifically indicates earning money through aggressive commerce, real estate, or through the influence of women.19

### **Cancellation (Bhanga) Rules**

1. **12th House Drain Penalty:** If the lord of the 12th house (expenditure) associates with either the 2nd or 11th lords, the engine must apply a severe penalty. This configuration indicates that no matter how much wealth is generated, it will be continuously drained away.21  
2. **Jupiter Affliction:** Jupiter is the natural significator (Karaka) of wealth. If Jupiter is placed in the 2nd house but is strongly aspected by a hostile Mercury, classical rules dictate severe wealth destruction and deprivation.4  
3. **Dusthana Placement:** If the primary wealth lords (![][image5]) are located in the 6th, 8th, or 12th house without any counteracting benefic aspects, the Dhana yogas are nullified.4  
* **Primary Domain Affected:** Finance, Assets, Banking, Legacy, and Material Comforts.  
* **Relative Strength Tiering:**  
  * **S-Tier:** Lakshmi Yoga, ![][image6] Parivartana in a Kendra or Trikona house.  
  * **A-Tier:** ![][image7] conjunction, Sunapha Yoga formed by exalted benefics.  
  * **B-Tier:** Jupiter situated in the 2nd or 11th house, unaspected by any malefics.  
  * **C-Tier:** Wealth lords in mutual aspect but placed in neutral or Upachaya houses.

## ---

**3\. Complete Daridra Yogas (Poverty & Loss Formations)**

Daridra Yogas represent structural financial vulnerability, immense unpayable debt, and an inherent inability to retain resources. The computational engine must weigh these heavily against any detected Dhana Yogas to output an accurate net financial trajectory.22

### **Core Computational Formation Logic**

The primary algorithmic mechanism for Daridra Yoga involves the degradation of the 11th house (gains) and the 2nd house (savings) through their placement in Dusthanas (Trika houses: 6th, 8th, 12th) or through extreme malefic affliction.23

* **Rule 1 (11th Lord Affliction):** ![][image12]. The lord of gains falls into houses of debt, obstacles, or loss.23  
* **Rule 2 (2nd Lord Affliction):** ![][image13]. The lord of savings is destroyed.23  
* **Rule 3 (Jupiter Debilitation):** A debilitated Jupiter placed in the 6th, 8th, or 12th house.24  
* **Rule 4 (Poverty by Malefics):** The 2nd house is occupied by harsh malefics (Mars, Saturn, or the Sun), and is simultaneously aspected by a weak, waning Moon.4  
* **Rule 5 (Kemadruma Yoga):** The complete absence of planets (excluding the Sun, Rahu, and Ketu) in both the 2nd and 12th houses from the Moon. This indicates profound psychological isolation, lack of support, and structural poverty.25

### **Cancellation (Bhanga) Rules**

Daridra Yoga is highly sensitive to overrides. A computational engine that fails to implement Daridra Bhanga will consistently produce fatal false positives, predicting poverty where wealth actually exists.

1. **Viparita Override (Negative/Negative Reversal):** If the 11th lord is simultaneously the lord of a Dusthana (for example, in a Pisces Ascendant, Saturn rules both the 11th and the 12th houses) and is placed in a Dusthana, the Daridra Yoga is *entirely cancelled*. It mathematically converts into a Viparita Raja Yoga, indicating sudden massive gains through loss or crisis.26  
2. **Malefic Amplification Reversal:** If ![][image14] is situated in a Dusthana but is strongly conjoined with intense natural malefics (Saturn, Mars, Rahu), the classical logic dictates that a "negative planet in a negative house yields positive results." This reverses the poverty indication into an aggressive, albeit stressful, pursuit of material gain.26  
3. **Benefic Intervention:** If the afflicted ![][image14] or ![][image15] receives a strong, unblemished aspect from an exalted or strongly placed Jupiter or Venus, the Daridra Yoga is severely mitigated, acting merely as a financial hurdle rather than utter destitution.22  
* **Primary Domain Affected:** Finance, Debt, Personal Hardship, and Mental Peace.  
* **Relative Strength Tiering:**  
  * **S-Tier (Severe Poverty):** ![][image14] debilitated in the 8th house, completely unaspected by benefics.  
  * **A-Tier:** Kemadruma Yoga existing without any planetary cancellation.  
  * **B-Tier:** ![][image15] placed in the 12th house without a Viparita override.  
  * **C-Tier:** Malefics occupying the 11th house (often mitigated by age and maturity).

## ---

**4\. Complete Aristha Yogas & Aristhabhanga (Health Afflictions)**

Aristha Yogas identify critical biological vulnerabilities regarding longevity, physical health, and early-life survival. Classical astrology divides life threats into three distinct age brackets: Balarishta (infant mortality, ages 0 to 8), Madhyarishta (adolescent danger, ages 8 to 20), and Yogarishta (adult crises, ages 20 to 32).27

### **Balarishta Formation Rules (Infant Danger)**

The Moon, representing the mind and the physical body of the infant, is the central variable for early childhood vitality. The engine must scan for specific lunar afflictions intersecting with Dusthana placements.

1. **Rule 1 (Lunar Dusthana):** The Moon is placed in the 6th, 8th, or 12th house from the Lagna AND is simultaneously associated with or heavily aspected by strong malefics (Sun, Mars, Saturn, Rahu, Ketu).28  
2. **Rule 2 (Martian Affliction):** Mars is placed in the 1st (Lagna) or 8th house, and is closely conjoined with the Sun or Saturn, threatening the physical constitution.28  
3. **Rule 3 (Eclipse/Node Influence):** The Sun in its own house (Leo) or the Moon in its own house (Cancer) is heavily afflicted by a tight conjunction with Rahu or Ketu.28  
4. **Rule 4 (Papakartari Lagna):** The Moon is placed in the Ascendant, flanked by malefics in the 12th and 2nd houses (hemming it in), completely devoid of any benefic aspects.29  
5. **Rule 5 (Twilight/Sandhya Birth):** Birth occurs within 48 minutes (2 ghatis) before or after sunrise or sunset, paired with the Moon and malefics situated in Kendra houses.30

### **Additional Health Yogas**

* **Deha-kashta / Roga-grastha Yogas:** Detected when the Lagna lord is severely debilitated or placed in the 6th, 8th, or 12th house and aspected by the lords of the 6th or 8th. Indicates a life plagued by chronic illnesses and weak physical constitution.31

### **Aristhabhanga (Cancellation of Balarishta)**

A robust computational engine must process Aristhabhanga before finalizing health outputs. If these conditions are met, the danger is mathematically nullified, granting the native a standard, healthy lifespan.

* **Bhanga 1 (The Jupiterian Shield):** A strong, unafflicted Jupiter occupying the Lagna (1st house) is the ultimate shield; it universally cancels Balarishta, eradicating a host of malefic health yogas.32  
* **Bhanga 2 (Lagna Lord Strength):** The Lagna lord is positioned in a Kendra (1, 4, 7, 10), is aspected by strong benefics, and is completely free from any malefic conjunction or aspect.32  
* **Bhanga 3 (Lunar Dignity):** Even if placed poorly, if the Moon occupies a highly benefic Navamsha (D9) or is aspected by a powerful Jupiter in the D1 chart, the child is protected.32  
* **Bhanga 4 (Benefic Kendras):** Natural benefics (Mercury, Venus, Jupiter) occupying Kendra houses without any malefic aspects create a strong structural vitality that prevents early death.32  
* **Primary Domain Affected:** Health, Longevity, Physical Vitality, and Infancy.  
* **Relative Strength Tiering:**  
  * **S-Tier (Critical Danger):** Moon in the 8th house with Rahu, entirely devoid of Jupiter's aspect.  
  * **A-Tier:** Mars and Saturn conjunct tightly in the Lagna.  
  * **B-Tier:** Sun in Leo conjunct Ketu.  
  * **C-Tier (Fully Cancelled):** Base rule met, but completely overridden by a strong Jupiter in the Lagna.

## ---

**5\. Complete 32 Nabhasa Yogas (Geometric Patterns)**

Nabhasa Yogas form the underlying "skeletal" structure of a native's psychology and life pattern. Unlike most yogas that require Vimshottari Dasha activation, Nabhasa Yogas are celestial blueprints whose effects operate continuously throughout the native's entire life.33 There are precisely 32 Nabhasa Yogas, divided into four arrays: Akriti (Shape), Sankhya (Numerical), Ashraya (Positional), and Dala (Factional).34

Algorithmically, these are parsed purely through spatial planetary distribution arrays, specifically excluding the nodes (Rahu and Ketu).

### **I. Akriti Yogas (20 Geometric Shape-Based Formations)**

These yogas dictate specific angular or structural geometry across the 12 houses.34 The engine must map the occupied houses into an array and match them against the following patterns:

| Yoga Name | Computational Rule / Placement Pattern | Resulting Domain & Psychological Effect |
| :---- | :---- | :---- |
| **Gada** | All 7 planets occupy exactly two successive Kendras (e.g., 1 & 4, or 4 & 7). | Wealth focus, skilled in traditional knowledge, excellent communicator.36 |
| **Shakata** | All 7 planets confined exclusively to the 1st and 7th houses. | Fluctuating fortunes, heavy marital/public focus, unstable trajectory.36 |
| **Vihaga** | All 7 planets confined exclusively to the 4th and 10th houses. | Deep, internal conflict between career dominance and domestic life.36 |
| **Shringataka** | All 7 planets occupy only the Trikona houses (1, 5, 9). | Immense luck, divine grace, wisdom, natural authority.36 |
| **Hala** | All 7 planets in mutual trines excluding the Ascendant (2,6,10 or 3,7,11 or 4,8,12). | Hard labor, agricultural or service orientation, life of routine.38 |
| **Vajra** | Benefics exclusively in the 1st & 7th; Malefics exclusively in the 4th & 10th. | Happy early and late life, extreme valor, combative middle life.36 |
| **Yava** | Malefics exclusively in the 1st & 7th; Benefics exclusively in the 4th & 10th. | Deep struggles in personal life, strong career shielding, mental fortitude.36 |
| **Kamala** | All 7 planets distributed across all 4 Kendra houses (1, 4, 7, 10). | High public visibility, structural stability, lasting legacy.38 |
| **Vapi** | All planets strictly in Panaphara (2,5,8,11) or strictly in Apoklima (3,6,9,12). | Stealthy wealth accumulation, delayed success, late bloomer.38 |
| **Yupa** | All planets occupy the 1st, 2nd, 3rd, and 4th houses in an unbroken chain. | Deep spiritual focus, self-sacrifice, renunciation tendencies.38 |
| **Shara** | All planets occupy the 4th, 5th, 6th, and 7th houses in an unbroken chain. | Craftsmanship, conflict resolution, technical skills.38 |
| **Shakti** | All planets occupy the 7th, 8th, 9th, and 10th houses in an unbroken chain. | High resilience, dynamic leadership, dominant authority.37 |
| **Danda** | All planets occupy the 10th, 11th, 12th, and 1st houses in an unbroken chain. | Disciplined, somewhat reclusive, highly service-oriented.38 |
| **Nauka** | All planets in 7 continuous houses starting from the Ascendant (1 to 7). | Fluid lifestyle, dependency on others, shifting foundations.36 |
| **Koota** | All planets in 7 continuous houses starting from the 4th house (4 to 10). | Obscure wealth, highly complex domestic life, hidden enemies.38 |
| **Chatra** | All planets in 7 continuous houses starting from the 7th house (7 to 1). | Protection of dependents, public care, highly social.38 |
| **Chapa / Dhanushi** | All planets in 7 continuous houses starting from the 10th house (10 to 4). | Archery/military skills, strategic mindset, aggressive career.38 |
| **Ardha Chandra** | All planets in 7 continuous houses starting from any Panaphara or Apoklima house. | Highly charismatic, universally liked, physical beauty.35 |
| **Chakra** | Planets occupy 6 alternate houses starting from Ascendant (1,3,5,7,9,11). | Highly influential, vast network, immense wealth, kingly status.37 |
| **Samudra** | Planets occupy 6 alternate houses starting from the 2nd house (2,4,6,8,10,12). | Unpredictable emotional depths, immense hidden resources.38 |

### **II. Sankhya Yogas (7 Count-Based Formations)**

The engine must evaluate these *only* if no Akriti or Ashraya yoga is formed.33 The algorithm counts the total number of distinct Zodiac signs occupied by the 7 planets.

1. **Vallaki / Veena:** 7 planets in 7 distinct signs. (Cultured, artistic, balanced, widely talented).  
2. **Dama:** 7 planets in 6 distinct signs. (Wealthy, philanthropic, recognized).  
3. **Pasha:** 7 planets in 5 distinct signs. (Tethered to attachments, large family, bound by desire).  
4. **Kedara:** 7 planets in 4 distinct signs. (Agricultural wealth, steady, reliable growth).  
5. **Shoola:** 7 planets in 3 distinct signs. (Aggressive, prone to conflict, sharp-minded, combative).  
6. **Yuga:** 7 planets in 2 distinct signs. (Poor, unorthodox, extreme focus, highly skewed life).  
7. **Gola:** All 7 planets in 1 single sign. (Destitute, isolated, highly volatile, extreme concentration of energy).39

### **III. Ashraya Yogas (3 Modality Arrays)**

Triggered if all 7 planets occupy exclusively one specific astrological modality (Quadruplicity).34

1. **Rajju:** All planets in Movable (Chara) signs (Aries, Cancer, Libra, Capricorn). (Constant travel, ambitious, highly restless).  
2. **Musala:** All planets in Fixed (Sthira) signs (Taurus, Leo, Scorpio, Aquarius). (Stubborn, steady wealth, immovable nature, highly stable).  
3. **Nala:** All planets in Dual (Dwisvabhava) signs (Gemini, Virgo, Sagittarius, Pisces). (Highly intellectual, adaptable, fluctuating fortunes).

### **IV. Dala Yogas (2 Benefic/Malefic Groupings)**

In this calculation, the Moon is excluded.

1. **Mala (Garland):** Only natural benefics (Mercury, Venus, Jupiter) occupy 3 of the 4 Kendra houses. (Yields a luxurious life, universally beloved, joyful).7  
2. **Sarpa (Serpent):** Only natural malefics (Sun, Mars, Saturn) occupy 3 of the 4 Kendra houses. (Yields a cruel disposition, intense struggle, destructive tendencies).7  
* **Primary Domain Affected:** General Temperament, Core Psychological Framing, and Lifetime Blueprint.  
* **Relative Strength Tiering:** Nabhasa yogas do not undergo Dasha timing and represent a structural baseline. They are universally rated as Tier A for overall life influence.

## ---

**6\. Complete Raja Yogas (Royal Combinations)**

Raja Yogas transcend standard professional success, elevating the native to positions of profound executive power, international fame, and authoritative dominance. While DKA is the strongest variant, any non-blemished intersection of a Kendra lord and a Trikona lord yields a Raja Yoga.

### **Advanced Kendra-Trikona Computations**

The engine must iterate through the Vishnusthanas (Kendra) and Lakshmisthanas (Trikona) for all 12 lagnas.1

* **Aries:** K(Mars, Moon, Venus, Saturn) \+ T(Mars, Sun, Jupiter).  
* **Taurus:** K(Venus, Sun, Mars, Saturn) \+ T(Venus, Mercury, Saturn).  
* **Gemini:** K(Mercury, Venus, Jupiter) \+ T(Mercury, Venus, Saturn).  
* **Cancer:** K(Moon, Venus, Saturn, Mars) \+ T(Moon, Mars, Jupiter).  
* **Leo:** K(Sun, Mars, Saturn, Venus) \+ T(Sun, Jupiter, Mars).  
* **Virgo:** K(Mercury, Jupiter, Venus) \+ T(Mercury, Saturn, Venus).  
* **Libra:** K(Venus, Saturn, Mars, Moon) \+ T(Venus, Saturn, Mercury).  
* **Scorpio:** K(Mars, Saturn, Venus, Sun) \+ T(Mars, Jupiter, Moon).  
* **Sagittarius:** K(Jupiter, Mercury, Venus) \+ T(Jupiter, Mars, Sun).  
* **Capricorn:** K(Saturn, Mars, Venus) \+ T(Saturn, Venus, Mercury).  
* **Aquarius:** K(Saturn, Venus, Mars) \+ T(Saturn, Mercury, Venus).  
* **Pisces:** K(Jupiter, Mercury, Mars) \+ T(Jupiter, Moon, Mars).

**Yogakaraka Identification:** The engine must map specific Yogakaraka planets—a single planet that rules both a Kendra and a Trikona, acting as an autonomous, self-contained Raja Yoga generator 41:

* **Mars:** Yogakaraka for Cancer (rules 5th & 10th) and Leo (rules 4th & 9th).41  
* **Saturn:** Yogakaraka for Taurus (rules 9th & 10th) and Libra (rules 4th & 5th).41  
* **Venus:** Yogakaraka for Capricorn (rules 5th & 10th) and Aquarius (rules 4th & 9th).41

### **Special Raja Yogas**

1. **Akhanda Samrajya Yoga (The Unbroken Empire):**  
   * *Condition 1:* The Lagna must be fixed: Taurus, Leo, Scorpio, or Aquarius.42  
   * *Condition 2:* Jupiter must strictly rule the 5th or 11th house.42  
   * *Condition 3:* Jupiter must be strongly placed (not debilitated), and the lords of the 2nd, 9th, and 11th houses from the Moon must occupy Kendras from the Moon.43  
   * *Effect:* Uninterrupted executive power, massive empire building, and immunity from lesser negative yogas.42  
2. **Adhi Yoga:**  
   * *Condition:* Natural benefics (Jupiter, Venus, and Mercury) must exclusively occupy the 6th, 7th, and 8th houses counted from the Moon (Chandra-Lagna) or the Ascendant.44  
   * *Effect:* If powerfully placed, grants the status of a king; if moderately placed, a government minister; if weakly placed, a military commander. Highly supportive of mental fortitude and absolute victory over enemies.44  
3. **Sreenatha Yoga:**  
   * *Condition:* The 7th lord is exalted, and the lords of the 9th and 10th houses are associated with each other.3  
   * *Effect:* Grants immense fortune and royal status post-marriage.

### **Cancellation (Bhanga) Rules**

1. **Planetary War (Graha Yuddha):** If a Raja Yoga-forming planet is within 1 degree of another planet and computationally loses the positional planetary war, the yoga is destroyed.45  
2. **Extreme Debilitation:** Without a corresponding Neech Bhang Raj Yoga override, a debilitated Yoga-forming planet completely destroys the Raja Yoga.45  
3. **Dusthana Dispositor:** If the planet hosting the Raja Yoga is severely afflicted or placed in the 6th, 8th, or 12th house, the foundation crumbles, resulting in a "paper tiger" yoga (the appearance of power without actual substance).1  
* **Primary Domain Affected:** Power, Executive Authority, Mass Influence, and Politics.  
* **Relative Strength Tiering:**  
  * **S-Tier:** Akhanda Samrajya Yoga, or a Yogakaraka planet occupying its own Kendra/Trikona.  
  * **A-Tier:** Adhi Yoga formed by unafflicted, strong benefics.  
  * **B-Tier:** Standard Kendra-Trikona lord conjunction in a neutral house.  
  * **C-Tier:** Raja Yoga formed by a retrogressing or slightly combusted planet.

## ---

**7\. Pravrajya Yogas (Spiritual Renunciation)**

Pravrajya Yogas designate the capacity for severe spiritual intensity, monastic asceticism, and the renunciation of worldly and material attachments in pursuit of Moksha (ultimate liberation).

### **Core Computational Formation Logic**

The engine must detect a massive concentration of celestial energy overriding the general spread of the natal chart, forcing the native's psychology into a singularity of purpose.

* **The Stellium Rule:** Four or more powerful planets situated in a single sign or house.46  
* **Node Exclusion:** Rahu and Ketu do not inherently count toward the integer threshold of "four planets" for the base formation, but their inclusion in the house dramatically modifies and intensifies the ascetic flavor.48  
* **Dominant Ascetic Order:** The flavor of renunciation is dictated algorithmically by calculating the maximum Shadbala score among the conjunct planets. The strongest planet determines the path 49:  
  * *Sun strongest:* **Tapasvi** (Engages in severe penance and austere asceticism in remote locations).46  
  * *Moon strongest:* **Kapali** (Engages in seclusive meditation, deep study of scriptures).46  
  * *Mars strongest:* **Shakya** (Wears red robes, battles the temper, highly disciplined Buddhist-style monk).46  
  * *Mercury strongest:* **Dandi / Bhikshu** (Philosophical wandering mendicant carrying a staff, easily influenced by others' philosophies).49  
  * *Jupiter strongest:* **Yati / Hamsa** (Leader of a spiritual institution, possessing complete control over sensory organs).49  
  * *Venus strongest:* **Chakri** (Wandering seeker, mendicant).49  
  * *Saturn strongest:* **Digambar / Nirgrantha** (Extreme renunciation, naked asceticism, severe detachment).49

### **Ketu's Involvement Patterns**

Ketu is the ultimate Karaka (significator) of Moksha and detachment. However, the computational engine must be precise: Ketu in the 12th house alone does *not* mathematically trigger Pravrajya.50

* **Activation Condition:** To trigger a Ketu-based spiritual yoga, Ketu in the 12th house must be heavily aspected by the 5th lord, the 9th lord, or a strongly dignified Jupiter.50  
* **Conjunction Dynamics:** When Ketu joins a 4-planet conjunction (e.g., Sun \+ Moon \+ Mercury \+ Jupiter \+ Ketu), it acts as a black hole, annihilating ego-attachment and driving the native toward profound occult knowledge, strict isolation, and prophetic intuition.51 If Ketu possesses the highest degree in this conjunction, the native experiences intense spiritual confusion prior to realization.51

### **Cancellation (Bhanga) Rules**

1. **Combustion:** If the strongest planet in the Pravrajya cluster is combust by the Sun, the engine must downgrade the yoga. The native will not become an ascetic, but will merely harbor deep reverence for spirituality and worship ascetics.46  
2. **Yogabhrashta (Fallen Ascetic):** If the 4-planet conjunction occurs in the 8th house, there will be a severe break in the spiritual path. The native will initiate the path of renunciation but will experience a "fall from grace," abandoning the ascetic life.46  
* **Primary Domain Affected:** Spirituality, Monasticism, Occult Knowledge, and Inner Realization.  
* **Relative Strength Tiering:**  
  * **S-Tier:** 4+ planets in a Kendra or Trikona house, none combust, aspected heavily by Saturn, or Ketu in the 12th aspected by an exalted Jupiter.  
  * **A-Tier:** 4+ planets in a neutral house, strongly aspected by the 9th lord.  
  * **B-Tier:** 4+ planets where the strongest planet is slightly weakened by a malefic aspect.  
  * **C-Tier:** The strongest planet is combust (Yields profound reverence for spirituality, but no practical monastic practice).

#### **Works cited**

1. The "Royal Union" in Jyotish: A Technical Deep Dive into Kendra-Trikona Yoga \- Reddit, accessed on March 2, 2026, [https://www.reddit.com/r/Advancedastrology/comments/1pibedp/the\_royal\_union\_in\_jyotish\_a\_technical\_deep\_dive/](https://www.reddit.com/r/Advancedastrology/comments/1pibedp/the_royal_union_in_jyotish_a_technical_deep_dive/)  
2. Kendra Trikona Raj Yoga Blesses Sachin Tendulkar With Name, Fame & \- AstroSage, accessed on March 2, 2026, [https://www.astrosage.com/magazine/kendra-trikona-rajyoga.asp](https://www.astrosage.com/magazine/kendra-trikona-rajyoga.asp)  
3. Astrology Raja Yoga Combinations ABSTRACT \- Worldwidejournals.com, accessed on March 2, 2026, [https://www.worldwidejournals.com/international-journal-of-scientific-research-(IJSR)/recent\_issues\_pdf/2016/February/February\_2016\_1455963866\_\_123.pdf](https://www.worldwidejournals.com/international-journal-of-scientific-research-\(IJSR\)/recent_issues_pdf/2016/February/February_2016_1455963866__123.pdf)  
4. The Daridra Yoga: The Yogas for Penury\! | by Varaha Mihira | Thoughts on Jyotish | Medium, accessed on March 2, 2026, [https://medium.com/thoughts-on-jyotish/the-daridra-yoga-the-yogas-for-penury-d0716a472c42](https://medium.com/thoughts-on-jyotish/the-daridra-yoga-the-yogas-for-penury-d0716a472c42)  
5. Functional House-Lord Based Combinations | Sithars Astrology, accessed on March 2, 2026, [https://sitharsastrology.com/blog/functional-house-lord-based-combinations](https://sitharsastrology.com/blog/functional-house-lord-based-combinations)  
6. Dharma Karmadhipati yoga \- Wikipedia, accessed on March 2, 2026, [https://en.wikipedia.org/wiki/Dharma\_Karmadhipati\_yoga](https://en.wikipedia.org/wiki/Dharma_Karmadhipati_yoga)  
7. Yogas | PDF | Planets In Astrology | Esoteric Cosmology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/916826071/Yogas](https://www.scribd.com/document/916826071/Yogas)  
8. Teachings in Metaphysical Astrology: Evaluating Yogas, Types of Yogas, A Yoga Checklist, accessed on March 2, 2026, [https://www.learnastrologyfree.com/may03astro.htm](https://www.learnastrologyfree.com/may03astro.htm)  
9. Dharma Karmadhipati Yoga-The Best?? | by NAVEEN RANA \- Medium, accessed on March 2, 2026, [https://thevedichoroscope.medium.com/dharma-karmadhipati-yoga-the-best-fdcb8a1dcd66](https://thevedichoroscope.medium.com/dharma-karmadhipati-yoga-the-best-fdcb8a1dcd66)  
10. Dharma Karmadhipati Yoga in Astrology: Auspicious Yoga Formed \- GaneshaSpeaks, accessed on March 2, 2026, [https://www.ganeshaspeaks.com/learn-astrology/dharma-karmadhipati-yoga/](https://www.ganeshaspeaks.com/learn-astrology/dharma-karmadhipati-yoga/)  
11. Uttarakalamrta 1.4.3. Dharmakarmadhipatya Yoga | by Varaha Mihira | Thoughts on Jyotish, accessed on March 2, 2026, [https://medium.com/thoughts-on-jyotish/uttarakalamrta-1-4-3-dharmakarmadhipatya-yoga-827c7418739f](https://medium.com/thoughts-on-jyotish/uttarakalamrta-1-4-3-dharmakarmadhipatya-yoga-827c7418739f)  
12. Raj Yoga in Astrology: Types, Combinations & How to Identify in Your Kundli \- VAMA, accessed on March 2, 2026, [https://vama.app/blog/raj-yoga-in-astrology/](https://vama.app/blog/raj-yoga-in-astrology/)  
13. Dhan Yoga Combinations: Complete Wealth Guide \- AstroSight, accessed on March 2, 2026, [https://astrosight.ai/yogas/dhan-yoga-combinations-for-wealth](https://astrosight.ai/yogas/dhan-yoga-combinations-for-wealth)  
14. The Dhana Yogas: Thoughts on some wealth conferring combinations \- Medium, accessed on March 2, 2026, [https://medium.com/thoughts-on-jyotish/the-dhana-yogas-thoughts-on-some-wealth-conferring-combinations-b0f5f45021c5](https://medium.com/thoughts-on-jyotish/the-dhana-yogas-thoughts-on-some-wealth-conferring-combinations-b0f5f45021c5)  
15. Dhana Yogas: Combinations For Wealth I, accessed on March 2, 2026, [http://varahamihira.blogspot.com/2004/07/dhana-yogas-combinations-for-wealth-i.html](http://varahamihira.blogspot.com/2004/07/dhana-yogas-combinations-for-wealth-i.html)  
16. Wealth Yoga in Kundli: Keys to Prosperity \- AstroSight, accessed on March 2, 2026, [https://astrosight.ai/yogas/wealth-yoga-kundli-financial-abundance](https://astrosight.ai/yogas/wealth-yoga-kundli-financial-abundance)  
17. Laxmi Yoga: Auspicious Wealth Yoga \- Vedic Astrology, accessed on March 2, 2026, [https://www.indastro.com/learn-astrology/yoga-dasa/laxmi-yoga.html](https://www.indastro.com/learn-astrology/yoga-dasa/laxmi-yoga.html)  
18. 300 Astrology Yoga \- Astrotalk, accessed on March 2, 2026, [https://astrotalk.com/astrology-yoga](https://astrotalk.com/astrology-yoga)  
19. General Principles of Yoga Formation \- Learn Astrology Free, accessed on March 2, 2026, [https://www.learnastrologyfree.com/principlesofyogaformation.htm](https://www.learnastrologyfree.com/principlesofyogaformation.htm)  
20. Lakshmi yoga | PDF | Planets In Astrology | Esoteric Cosmology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/975479225/Lakshmi-yoga](https://www.scribd.com/document/975479225/Lakshmi-yoga)  
21. Dhana Yogas and Astrology Insights | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/465702451/Astrology-basic-3](https://www.scribd.com/document/465702451/Astrology-basic-3)  
22. Understanding Daridra Yoga in Vedic Astrology: Effects, Remedies, and \- Utsav, accessed on March 2, 2026, [https://utsavapp.in/gyan/daridra-yog-and-its-remedy/daridra-yog-and-its-remedy](https://utsavapp.in/gyan/daridra-yog-and-its-remedy/daridra-yog-and-its-remedy)  
23. What is Daridra Yoga? \- VedicFuture \- Medium, accessed on March 2, 2026, [https://vedicfuture.medium.com/what-is-daridra-yoga-22edbb8faee7](https://vedicfuture.medium.com/what-is-daridra-yoga-22edbb8faee7)  
24. Daridra Yoga (Effects & Influences) \- Vedic Astrology, accessed on March 2, 2026, [https://www.indastro.com/learn-astrology/yoga-dasa/daridra-yoga.html](https://www.indastro.com/learn-astrology/yoga-dasa/daridra-yoga.html)  
25. Yogas \- 300 Yogas | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/871026871/Yogas-300-Yogas](https://www.scribd.com/document/871026871/Yogas-300-Yogas)  
26. Daridra Yoga \- Astro Isha, accessed on March 2, 2026, [https://www.astroisha.com/yogas/269](https://www.astroisha.com/yogas/269)  
27. Balarishta \- Wikipedia, accessed on March 2, 2026, [https://en.wikipedia.org/wiki/Balarishta](https://en.wikipedia.org/wiki/Balarishta)  
28. Balarishta Dosha in Astrology, Effects, and Remedies \- Gokarna Puja, accessed on March 2, 2026, [https://gokarnapuja.com/balarishta-dosha-in-astrology-effects-and-remedies/](https://gokarnapuja.com/balarishta-dosha-in-astrology-effects-and-remedies/)  
29. Balarishta | PDF | Divination | Technical Factors Of Astrology \- Scribd, accessed on March 2, 2026, [https://fr.scribd.com/document/436957830/balarishta](https://fr.scribd.com/document/436957830/balarishta)  
30. Balarishta Analysis of a Child's Horoscope | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://fr.scribd.com/document/469806308/CS-Balarishta-9yrBoy](https://fr.scribd.com/document/469806308/CS-Balarishta-9yrBoy)  
31. BV Raman \* 300 Important Combinations \* 103-122 \* Deha Yoga for Physical Body \* BP Lama Jyotishavidya, accessed on March 2, 2026, [https://barbarapijan.com/bpa/Yoga/300ComBVRaman/300Raman\_103-117\_Deha.htm](https://barbarapijan.com/bpa/Yoga/300ComBVRaman/300Raman_103-117_Deha.htm)  
32. Balarishtabhanga yogas \- Jyotisha News | Daily Mirror, accessed on March 2, 2026, [https://www.dailymirror.lk/jyotisha-news/Balarishtabhanga-yogas/312-210062](https://www.dailymirror.lk/jyotisha-news/Balarishtabhanga-yogas/312-210062)  
33. Nabhasa yoga \- Wikipedia, accessed on March 2, 2026, [https://en.wikipedia.org/wiki/Nabhasa\_yoga](https://en.wikipedia.org/wiki/Nabhasa_yoga)  
34. Nabhash Yogas | PDF | Kama | Nature \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/288607/Nabhash-Yogas](https://www.scribd.com/document/288607/Nabhash-Yogas)  
35. Nabhasa Yogas | PDF | Planets In Astrology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/733157167/Nabhasa-Yogas](https://www.scribd.com/document/733157167/Nabhasa-Yogas)  
36. Nabhasa Yogas By G.K. Goel | Saptarishis Astrology, accessed on March 2, 2026, [https://saptarishisshop.com/nabhasa-yogas-by-g-k-goel/](https://saptarishisshop.com/nabhasa-yogas-by-g-k-goel/)  
37. Exploring Nābhāsa Yogas: 32 Planetary Patterns & Their Life Outcomes \- Pt. Pawan Kaushik \- Best Astrologer in Gurgaon | Consult Online, accessed on March 2, 2026, [https://www.pawankaushik.com/exploring-nabhasa-yogas-32-planetary-patterns-their-life-outcomes/](https://www.pawankaushik.com/exploring-nabhasa-yogas-32-planetary-patterns-their-life-outcomes/)  
38. Nabhasa Yogas \- Jyotish Vidya, accessed on March 2, 2026, [http://jyotishvidya.com/ch35.htm](http://jyotishvidya.com/ch35.htm)  
39. Nabhasa Yogas \- Smart Ganesha, accessed on March 2, 2026, [https://smartganesha.com/nabhasa-yogas/](https://smartganesha.com/nabhasa-yogas/)  
40. Nabhasa Yogas | PDF | Astrology | Esoteric Cosmology \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/202120426/Nabhasa-Yogas](https://www.scribd.com/document/202120426/Nabhasa-Yogas)  
41. Raj Yoga in Astrology: Complete Formation Guide \- AstroSight, accessed on March 2, 2026, [https://astrosight.ai/yogas/comprehensive-guide-to-understanding-raj-yoga-in-astrology](https://astrosight.ai/yogas/comprehensive-guide-to-understanding-raj-yoga-in-astrology)  
42. Akhanda Yoga: It's Meaning and Significance in Kundali \- Hindu Panchang, accessed on March 2, 2026, [https://www.mpanchang.com/articles/astrology/akhanda-yoga/](https://www.mpanchang.com/articles/astrology/akhanda-yoga/)  
43. The term "Raja yoga" is not defined in the texts dealing with Hindu Predictive astrology. All such planetary situations and combinations that indicate good fortune, wealth, comforts, exercise of ruling power and political influence gained either by way of inheritance or acquired through self-effort, are termed as Raja yogas. There are many varieties of Raja yogas but their formation generally involves the 9th, the 10th, the 2nd, the 11th house and the lagna (Ascendant), their house-lords and their exaltation signs and lords, which house-lords giving rise to Raja yogas invariably tend to enhance the affairs of the house they occupy, aspect and rule, In doing so they combine the influence of two types of houses, those governing personal initiatives and those that show good fortune. Therefore, Raja yogas are generally found in the horoscopes of leaders and famous people and reveal their birth to be out of the ordinary., accessed on March 2, 2026, [https://kasturiastrology.com/articles/Rajya%20Yog.php](https://kasturiastrology.com/articles/Rajya%20Yog.php)  
44. Adhi Yoga: Formation, Meaning, and Its Impact on Success & Growth \- Omega Astro, accessed on March 2, 2026, [https://omegaastro.com/adhi-yoga-formation-meaning-and-its-impact/](https://omegaastro.com/adhi-yoga-formation-meaning-and-its-impact/)  
45. Raj Yoga (Effects & Influences) \- Indastro, accessed on March 2, 2026, [https://www.indastro.com/learn-astrology/yoga-dasa/raj-yoga.html](https://www.indastro.com/learn-astrology/yoga-dasa/raj-yoga.html)  
46. Sannyasa yoga \- Wikipedia, accessed on March 2, 2026, [https://en.wikipedia.org/wiki/Sannyasa\_yoga](https://en.wikipedia.org/wiki/Sannyasa_yoga)  
47. Understanding Sanyasa Yoga in Astrology | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/733154107/Pravrajya-Yoga](https://www.scribd.com/document/733154107/Pravrajya-Yoga)  
48. Kala Sarpa: the astronomical rationale for â€œyogaâ \- NAVAMSA, accessed on March 2, 2026, [https://www.navamsa.com/?p=4018](https://www.navamsa.com/?p=4018)  
49. Pravrajya YOGA \!\!\! | Chiraan's Astrology \- WordPress.com, accessed on March 2, 2026, [https://chiraan.wordpress.com/2010/10/10/pravrajya-yoga/](https://chiraan.wordpress.com/2010/10/10/pravrajya-yoga/)  
50. Sannyas Yogas: Combinations for Spirituality, accessed on March 2, 2026, [https://www.lightonvedicastrology.com/blog/sannyas-yogas-combinations-for-spirituality](https://www.lightonvedicastrology.com/blog/sannyas-yogas-combinations-for-spirituality)  
51. Lal Kitab Crash Course \- Conjunction of 4 Planets | PDF \- Scribd, accessed on March 2, 2026, [https://www.scribd.com/document/869926393/Lal-Kitab-Crash-Course-Conjunction-of-4-Planets](https://www.scribd.com/document/869926393/Lal-Kitab-Crash-Course-Conjunction-of-4-Planets)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAXCAYAAABNq8wJAAABsUlEQVR4Xu2VTSsFURjHH6GUl4UFKeUiSjZiY3c3yndgIaEkG2VjwUYspCQLJRsbG0nuygdQSCkp9lKSpQ/A/++cy7nPnTPuzNyubs2vfjXneWaa85xXkZSUlErQCGt00IG5UdirE5YdeANnYIPKRWIVnsF2nQhgGu7DT2tTYfqHV3hqn2ttu8W22dk9+5xnQbVLgh3ehMcSPpIuHLEcvBB/AZ3wEQ44sQ04ZZ/5310nR4ZU2ws7yg6/wy6Vi8KJBBfANnPbKs4O8p9ZSTADI/BczKiXslzC8BWQgXdwMSDO9+dtexgOihnQSXhg40XUw2v4JGbTlQtfAeM2rgvggDF+pOKhjMF7OCEJd3kAcQvgd5HgCcAN9wxbVS4JFSvApQ8eijl/k2xg4iuA5/6L+AvQp08sWMCb/G6iOPgK6IcPUlxARsz7KyqeiGa4JGaJcalFwVcAWRdzqtQ5sSy8leQzH8iclH4T5wkrgGf+FexwYstiLrO4M1422OkguXld1uAHnIVb8LIwXR10i+k8l1TUJfoNL7E2MUvjL3nE/vv0anht66n2yeu/x3yWklL1fAEtgWHEkt1FIQAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAZCAYAAADe1WXtAAABDklEQVR4XmNgGAW0BrZAfBSIT6Lh3ciKyAXrgPg/ECugiVMELjNADOVAl6AEgAx8jS5ICeBhgBh6Gl2CEuDBADE0B12CElDJAPG6PboEuUABiM8B8UIGwpE0B4jXA/EuIJ6GJocCQF7/DMT56BJQEAnEzEDMB8RLGCAWCwHxFiBmRFKHAlYzQMJTCl0CCCyBeD+U3cOAGuYgtjcSHwWAXAkyFB2AXPEIiJ2gfJBPkA0FxQPIIqwAV/rMZYC4UgzKN2CAGAQCoCAABcVEKB8MxBkghhHCpjANUGDFAMnOPgwQS0NQpSkHzUCsiS5IKtAB4k0MkFQQBMTnUaXJA6xAPA+Iw4H4ABAbosiOgqEBAOMhNag2h1HWAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAZCAYAAAAiwE4nAAABKklEQVR4Xu2UvUoDURCFjxjBwi6FEFAUrIRA7OySzlqwtUpjIVgGO/EFQsgDiHXQVkFS2CmB9IH4BCl9AD3DbNi9Z5dAIjeF7Acf7M4s93D/Fij5b7TpZ4F3mW+iMKE/dEMbsbAwcy3swMOG2ojFATywK/Vo3NIveqKNGGzTR/hyVqUXhSad0SttFLAJvy6613ayrXZJn2gtbIfcwPfvVBsJz3SfHtM3+MAfwRdAix4mz/f0IW3lGcEDbWkVq11IrYcw0GZjY8xp0GnmPYeF2ZIqe/SdVqSugXbQ7MDNWRhoM7DAsTbIK/3WIvKBZwh/GIWBR0j/LIssupcaqAH6/mc0cOk9XJY+wgDjHOkp7dBBprcyu/CZZZf8Oult0Rf4ibZrU0/qJSWr8QvJTkarragIwwAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAXCAYAAAD6FjQuAAABDklEQVR4XmNgGAXDBagBMSO6IBIQB2IZIGZFlwACRSDuB+IDQJyMKgUBxkCcCMTngfg/EK8GYh4UFRCQDcSfgZgbiDmAuBSIOxgQloLENKFsGIhG4zM0APFJIC4A4h0MuC27A8T7kfggw58DsQOUD/Ixur4WND4cgBSCLMJmmSQDxNcZaOIgsctQNlE+gwF8llkwQAx2RxN/wgAJWhhYDsTaDJCgBVnEhySHAvBZlsOA3TJQ0ILESQYj07IQBjpaZs+A3TJQAqG6ZaBkDTK0Ek0cJLYJTYwogM8yEHjNAJGDARYGiGVJSGIEASzysWHkYAPlmZlAvApKfwBiKSR5qgNQAV0DxQZocqNgFJAPAExlRq/LLjIvAAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHQAAAAZCAYAAADg8AqjAAADsUlEQVR4Xu2Z34tNURTHv0JRSApRzDwgPyahiAeNvBAeJCUvpjwpJKWkKQ/kRV4Q4UGjPBAhPx5EoQgRSZSiJpHkRfkDWN9ZZ9+777r7nnvumbPPpM6nvnXv3mfuOnutddZe+wxQUVFRUVFRUQSrRc9EL40e+BcVzFQ023OKibXlxPuJQZpvF3rXReGG6K+o24zHZB/U5lY7EZGZUJv37ERERsK3eA81Os5ORIJ2LkHtzjNzMemFrvOonYhI2b4dggZ/2cGIrBR9Q7mOHSO6gPKTqGzfYgLU6Cs7EZE9UJsb7UREZoieQ0vgRDMXi5HwLdZDjdLJZUHH0iYXXBYuibjeshgJ3+IQtCRwfykLllsutExYbmmzzHJbum+7RW+gDUq7TfuM6Kroq+i1mesE7mV0LPeydnwWfRBdFL2Ddql5yZpE00U3RcdFZ0WTGqcz043sviUroOu0VWuK6CkyPuUsCX+gR4gQ20WjoUHYlIzNEj0RLXYXdQj3MjqWe1mIOaLZyWcGlNf+Fp2rXZEP/k6rgPaLDkCDdwX1ANwVHXEXdUgW3/IhIX3QYL5AY0CZUI+hyZgpoNegiwxl/irRo+Qzy9QnUU/yfR30b202ZSGtIWI23va+hzI2D+2S6BY0mCfQGHR3r3lI8y2hb7u871xnK58ysTMFlBkUuuFR0NK61k5An1Zmlg3IXNEuM2ZxnSYP9pPNHOGblWPed75ZuQ79XXaKvC8fdqu90CqShgtM6CXGftGC5LN72eHgHmj9w3vYCS3NaaT5dguafVtIQGkwdEbaC82gaXZCWAMtAWPNOB3O35tvxn3ofNqz508ukq/KOOcv9DzqexiD4XeoLrHouD5v3JL2EoMJwb93JXYJ1HmOy2gOyvJk7KEZt6T59geafZs7oMwsGmsn3riFzt2N8BPBJysULHISzb8fEvcxH5Zg91TS2XyCfTaIviPsXBcca8OKiehDeyzN96HO5zU+9AHX+dOMk6y+HUyu98kd0LxwIadRd/Bh0fj6dI1WTUCnMJiDqCdWKKCE4wN2sCCYnB/tYAKTtEhKDSiDOIjG/xqE9ssuNJe1vNDmZu/zQdGy+nQNlt0ddjAnPdDmj8lLm28R7uaZZHfs4DBhT8HmLPQW6wuKe1CG4EJt2WCn60MHsMW3jctwGBCdStTq3MoGq6h/gbEv4PlzG9Tm0sbpGuy+++zgMKAvrX+J3ap4rGnXjBUGm5pFdjAyPK8WmUBZYP/Q6ihSUVFRUVFR8Z/wDyyE/mwbUM7hAAAAAElFTkSuQmCC>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAE8AAAAZCAYAAABw43NsAAACSklEQVR4Xu2XzUtVQRjG3yAhIiVaJEbiXRX0tRCSNhG0SciVuJFAwVWLQnATbVoUIdLKRR8rIVAqBWnnQiwERUVsE+5aRBsXLvsD9Hmce+ve557bzDnec+DS/OAH+s545sw7M+8ZzSKRSOT/5TZch1viMrxS1a8VOGX186iYK4vwAJYk3orcNzeXp9qQF9/NDcjVa3VewH14RxvygonjgHlyEk5pUBg01y8rJfgNvreCNsIZc8nb1oYm0wVXNCjcguc1mIJ++BuOa0NecEAm75E2NJkFOKrBBOY1kAKOwblwoQqBhTXvGnECzpnb5T4+mOufBR7Zwmp3ycJrxBJ8ay7RTEQo03BNgx424KQGAwit3W3wlblrmtIHZyxgoX01Yhi+hhdhdzk2APfM/3AuxjNzE9q1+rvXv2R//t2EhX9AfLX7nLnEEI7B+rv5t/kIlhUmjnHf/P7UiAvaUOYr7IEj8CM8XY5zN4XWyKvwi7nVDoH92P+SNnio1O6kjcBnvpMY56DJI0wa8+JNHncdB1RYc3htuKsN5pLJ1eVuTMMqvKHBBJKOko/KhFmCSrVNR/CfgFmJHTt5jWrEY3NHM+na8Bz+0mAAT+BLDQo8ouyXFu5SXvSTavdlc/Mck3im5HWae5jPn+X+1fTCmxoMhC/ju4YMWYOXbgBLh753kqzbWjszJS8r1+Gnqt8fVP0ciu+oc2GLorDkdVjtF3MHXqvp0Xq8seQv81n4GbZrQ1YeWv1RKHKXNJsfVjuXys3hnsRpJBKJRCLpOAQBp5UQj/j2vAAAAABJRU5ErkJggg==>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAAAZCAYAAACSP2gVAAACS0lEQVR4Xu2Xz0sVURTHv5FFhFmbChLtIQSVEFYERYQQgm1zIUarolU/lxHuaiUhEm0qCMpFhUGEKARBGSEoUhARbaVNizZBf0B9D+eO3jm8N3NHZ9IH9wMfuHPunfvm3Lk/5gGRSCSyfjhFZ+m88a3fqEnIyuWg125FvKJ/ac3Em5FKcvkK7XSLrWhCKslFOvxlgxUwSjfboMc47bDBgpSeSyu00wVbUTIb6C0bNLymp22wAJXkcgba6VVbUSIyONeRP+330w82WIBKcpG3KlOy11aUyBGEJS4DeYW22YpASs+lRj/Tp8h/u3/oF/qCfoNO5zw20fN0CJp8KA/pGxvMoYbwXC7Tj/QJnUnVGGRKSuI3bIXjHN3oyjJ1xZ/09lKLbGRA5R77bZLnJ/obmuxuhBGai7woOekOuPJNutNrl+IlNIE9toKcoO+963teuQjb6BTq/0YjJIFBG8whKxchyaUP2jZZAT30PhrMcBlx6dQijX8gfaJ8p4+h67zoKSF7ynMbrIM89AQaPGwOWbkMYDmXw0gP0HHoF/gud52i0TfDNeiI+zeNQPcUQQbpkFcXgszIug/hcZZO2mAgWbnItpD8tgzMNN3hri/SOXhLWQrJfpLlseQGx3av3A/drLd6sRDGkD073kGnfCihuSy69gnt9C4dpifpI9qSalGQfdBltdddr3SAOpE9QN1YPhT+F73QWbQq5Ng86sqyzB5g9X8J1gp5qYvQFdIFPe5LQfaGO/QZSux0jZClfAG6Ki6ZukgkEomsV/4BgESJp0zG628AAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAZCAYAAACLtIazAAAB6klEQVR4Xu2XzysFURTHj1CULCyIktn4USQbykJkQ/EP2FopZG1jQVZWEtkqGyn/gCSLV0Q2VspCsrP0B/D9OjPMnHdf7817704W86lvb945M3Pfufecc+8TycnJ+c9MQQXozugyflOdaZHi8SJ55QL6ggJj98mC6Jib1uGLJ9EBOctZsQN9QNPW4QsGyAGzIoAeoRPJaGLbRIO8tw6PzEOf0IZ1+IIDMsg16/DIueiY3dbhCxZ+prUhmqqZ9YBAKq+NQ+gMeoMejC8tlfaAZmhIdJvrMj7a9xz2IsrVxhLUCDVBi6GtF7qBRqObUlKuB3RAE+E1985T6FaSwTDraL8ydidRbfRYB5iErsPrAegZGgm/z4k+yx+clqgHuCaWK3dsjVIcZMS+uO0JuIoc0NIgmpaz1iG6qkxdbuZx+qEVY7NwUjg5LJEg6fqBhxKukKWmIEvVxrroKnZaB5iB3kVnPQ7Tj+9jrZSCGcGDh6sHDIo+v2zsJHWQNPJl5TQePRCjHVoVrVPLruiE8SRj4fZk3+8SM4SZYkkdZLUwwAPRVCZbUOuf+xdXrdVKJkEysFdJ/mNw1V+faErWE2YNS8E2R9qPHPaqYVe1qcUOG4cTsR1+1osXSY4ZncrGjJ3KBP43HbbGnJycnG/9AXrKPo3BdAAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAZCAYAAABzVH1EAAACHUlEQVR4Xu2Wz0sXURTFj1QQURFFSQVmElGtChGECCECA1tEuIlAKFpEFG2EiHaFK1cRtXARtoygQHARYQoiFZEQ/QPfhdDCpX9AndN97+vM9fnj+50ZV/OBg2/eed47b+a++x2gpqamFS5RC9R3p8/Uucy6MjlMvcPanFJhPlB/qW43XyWPYDmHvVGE37Cgu71RIW9hOU97owgKuOwnK2YJlrc09sIC/vBGxShnqRu5Cgv4wBsVchSW8703ivAEVlYD3qiQfthGnnujXbqpRdjB2+yg/6HmqU9UI2+1xE5qAtZgNjvo92E5J6m5nONQWa3AWmGKm9SrMI41/Yu63lzROiqrr7CWv8954hTVRXXANns2jB/DfoOSqEZ1c8e8EZilToTxYNYogM6icg55gxykpsL4Cuz+1IzEeeolbFNr0NtIdQ4tvkFdzszpFT+j3lAfM/ORXuqOn0ygt6GcB7wB+8oYC+MLyG9E50r+kXCdQwFTvx8PYWci+0/Xwl/dwDRWE0QasHjrvv6A8qUenj6X5MWHp/jKEzesh/SN6gzX/wex3jdSI6wXO5BvBi+oe5lrMQm7kRE3H/HxUxptrjaOU+PUU+oirEmoWbTNLdihj0FSG4mkar8MBrC10t2QM9T+MD5J/aR2rdpN+qhDfrJN9sCqQjF7YGe0FGaou7DD+tp5QqWnRlAmX6jbsM8n5d4W1AzWa+M1NTXbzD8UfXOS5MTDOAAAAABJRU5ErkJggg==>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAAAZCAYAAACSP2gVAAACQklEQVR4Xu2XzesNURjHv/ISQjYoopuFvCWUIuknKYoNC5EVWcjrUlL+AclCFqywEUoSpZSXpMhLycrul5SFjfIH8P32zO2eeZqXc++dqd/U+dSnZs5z5tx5zjxnzlwgkUgkpg476Dv6wfki7NQRqnJZG/QbiUf0H+259i7SSi7fYIPO9oEO0kouGvC3b2yBq3SWbwy4S5f7xiFpPJd5sEE/+kDDTKMXfaPjMd3lG4eglVz2wgY94wMNosk5h/qyX03f+MYhaCUXPVWV5IQPNMhmxCWuiTxNF/hAJI3n0qNf6B3UP90b9D79QT+5WBkz6VF6GJZ8LDfpc99YQw/xuZyib+lt+joXcagk/9LzPpBxhE6nM+j+rE0vUVXDhn6nCr7CSt5/m9T5mf6BJbsEccTmogelnW5NdnyBLgr65XgIS2CpD5Bt9FV2vIp+p+uz8z2wa/VSrGM+fYri3yhDCRzyjTVU5SL6uexG/t430usoqXDNuAb1qLOWUtGOomrSctvnAxXonXLPNxagm36AkputoSqXgxjksgn5CdoK+wJfnJ3nKPtmOAub8aKLdtKfsPfLMKgii8YLOUCf+MZIqnL5hcFva2Ke0YXZ+XH6HsFS1oEGq3NL/4IAVYJ2Ga3lUbiG6up4CSv5WGJzmcz691lGr9BLdDu9BVsZY6HJCdfqZTpnEI5iBaonaB1Gn/xRmYBV0VgoqUnkd5qTYYcOMReWi1bISth2PzbavXzZaifrKlrKx2B/SU64WCKRSCSmKv8ByiCKCH4kxRsAAAAASUVORK5CYII=>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAAAZCAYAAACSP2gVAAACRUlEQVR4Xu2Xz0sVURTHj5hiUbYrCKq3SSIlpGjRIgo3BbnRhRT+A4KlazcucuUiQkLQRYtaaD9AIloIgiLSIrQgQsTdQwQXbYL+gPp+vTO9+w7z7tx5zoAD9wNfmHfOnfvme949984TCQQCgePDHegL9FVpxR5UElxerlnjmmIJ+gtVVLyMFOLlp5hJO3SihBTihRP+0sECeA6166DFG+iiDmYkdy+nxUy6qRM50wJN6KDiI9SngxkoxMsDMZM+0YkcYXHGJH3ZX4XWdTADhXjhr8oleVcncuSG+BlnIUehTp3wJHcvFeg79FrSf91Z6B20B22pXCPaoGHokRjzvsxDyzqYQkX8vfyBfkBvoW0xrZkIlyQHj+tExGOoFToB9UcxbqJcDdfjQQ74EFzy+t0kTd+g32LMnhc/fL0QPhN1AD37PyKBD2IGXtAJcBtai667oF2oJ/p8X8y9DStvcQb6LMnf0Qge1UM6mILLC4m9kBnr2gkrzkk1bAe2UtKJwtXEdnuoEw64pyzqYAIs+HvJ1o4xLi+DUu9lB3olZs9ynniN3hmeiqn4OZ0A96B9MftLFrgik+azGYA+6aAnLi9sJfu7p6X2/CxS3XbBno570KVb8Q0WXAk8ZeJezsoLca+OVahXBx34eqlG42POWtfcLrhZn7JiTcHivJSawUnoZC3txSVxF6hbmi++L1fEtNXl6HMuBaKpqtSfNCP2gBLBV4Cb0TXbbE6O/vfm8PTSy5aVLyvc56agBWhD5QKBQCBwXPkHN8iLDXxVNMQAAAAASUVORK5CYII=>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAH8AAAAZCAYAAAAYEPFUAAAEpklEQVR4Xu2Z36tVRRTHV6QQZVlGiWHmQ0gPCUoUROm9hGhoSlFBRXhfehD79RJBLz4YPWiJ+lCZD6JvYhCkiKKCiYVFEVSkIAUiRkggQn+ArY/rjGfuuntm7zlnX8nr/sAXPDP77nNmvmvWrBlFOjo6Ojo6phTfqq6o3lAtdX1TlRdUf6suq25zfUmWqL5T/eB0NH7oBmKu6l/Ve77DMVv1lGq67yigjXcE7lXN840Rs8S+a6bviFgg5uVbvqOOr8RWy3zXfqOxQvW9mDFVsCouqe7sff5C9WO/uxG3qM6qbu19flH1h+qua080AzPfFHsXc799fPdVVqnOiL2bIDss9uw6sd/hwXgC4H7fkeM3sZc2Thn/U9ZK2nwmb7PqnaiNMaMSHlE979r4POba6vhMLMuul7T5J8QCJHCf6pjqnOrJqD2A+anxJ+HL//GN1wki+LjYnoU5iAGvVj3R629KbvD7ZaLRH6hed211YNLTro20vVd1u2tvAr81ZX4Izrujtkd7baxwT278lcwQe1lp+msDMs0m1Wu9fw9LbvAEtzd/EAgYVmzM41JfZ6TImU/94jNyeJ5xenLjr+RZsZcVFwotwIp/0DcOQWrwTB5jZG8+IrZnkj43SHnBxvNhRXKyYMX7YCghZ34VL4k9/5HvEKsRqsafhEhmVYz4jkmGouRl3zgkmE/xGgq6AJ+ZMMbJCQeCiRvDQwVslX4AnFI9NL67iBLzydJfqn4Vqz08dQXvOOarflbtkfq0Sz978D6xHxHDUYRVUJI9Sp5tAiuQSayqusMEoxgmirZprj0HNcgF1RzVDum/97n4oQJKzD8tVhvl6iCy23npn0aSkPLZV971HT1elf5LSG27xCIvNp+q9RuxCSkxlGf9/YLXNqkPyvdVv4gVQER+FWHlMzExwfySoxEmhwocE/idvOOk2D1DKU3NZ3vE1DW+w8H7PhZ79oDrGwdG8sUP+A6xo8Rx1xbSjl/5wMSWmM/eVWdsCZjCqhjxHT1y5jdKk8oyscXiCVtIahHlaGI+J6C4ur9HNRp9DoTahkVaS6gmPUQ0kfOMa2/TfFIte2dpwZWD709dcnCX4Y3jhMP4Q9pn3I9JOhhS5gPtXLMGxiQdiDE58/k9ZBlfFFOn7XRtULTn86VV5/u3xVa9n8Q2zQe+I6TQNuD7U4P/RCYGOltVnA04sp0TOwlwoeIhrZPe/VUsARz/DcHEd6UCJSZnfshm4f4DUduwMAkAzzpJj/8qcfGTExPhadt8eFhsz+bmbdhtIGc+LBT7z4/PxYon/vMnLowoFnerLordFlbBajyjOihmBkZQfXv+VP0ldgFUBWb7OUdxMPq+oNTprG78QzEZ5sNy1dcycZBEecmtWZPBj4qZxipJgTGrfGPEHaoPxd4zKumta5FMPHZOJk3GPzBcM1ado4FIH6TgaRMMa2PwVMmpFdsUUv+nvnGSwfyUP0PhV2U4Vvn01cbkD0pRwZOArWfMNw7AqNjWcD3B/FRmnvKEIxdn79pLjgr4G4qsNlgp+cuYtmERUmAu9h03E6+ofhKrkg+5vqnK72Lj3eI7Ojo6OjpuWv4D0/Uo99xLNCoAAAAASUVORK5CYII=>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHgAAAAZCAYAAAD6zOotAAAEpklEQVR4Xu2Z3avmUxTHl1DMeMs05P1MJMrIS8KFRghxXIgbKRO5mBqG5EZK4oKkJGnISyMpEhcieSkJIW8hSpEnkQsl5Q9gfaxnOfss+7d/ez/P78w5pt+nvs151t7P89u/vfZea+09IiMjIyMjIyvKnapfVQ+rjglteyoXq95X/aU6PbR1cp7qA9XHQW+lndYgvOSJ0RjYT3W86lDVXqGtlgNUJ6sOjg0zsF7KY/bxHqHaN7Q52G9Xvac6OrQVeVls0haCfS3CpDPWLjap3lZdpdpbdZLqE9U+aaceiArvqo6afubfp1WL//ao40zVTtUXYmN+cXnzPxykela1WWy8OJDoxDvkotPhYr+1LTaU+FrsS6yitc4GKTsYx3yffH5TrD8TU8s9qpeCDUcw6RuDvcTdqldUt0q3g28SG3PKVrH+jwU7uIP5XjV84bdoHJh7VZ+K5c0Hpp+vUF2WdqrAXzDHWaqfVecktrPFntUCC+SpaFT+VF0UjRV41Mk5+COxtquDHVvuPZsd7A8njK0UTDwhbghKDsaRTFjLbs3xuZgz04hGiGeOjktstZQczA6n7YJgH8zBl0rjFxohRG6PxjnocjAFDKmG0Hqj6g6xapvdSAXawhmqb8We84fqBtWP0l389FFycI5DxPozhsiB0ugvJoLwvCU2DMSrYpXsUHQ5mKPDD2KOSPMn+Y2ipRVOGL6L0I7lzU20Ovhysf7UAhH/rSoHL4iFo2ekv8B6VPWC6iexXFoDzjgtGufgWrHn53bkJWIvThg9MmO/MrH1wfdfU50i9ix38vNixVYrLQ6mPqFvKc08LtbHq/xOCM/kmltiw5RrxEp38s/i1OZHiFO9UwEG+aX895ydinN4HyeoXlf9rrovtDm+g5lEJtRxBz+Y2PrAkWllyzOZp+qdE6h1MOd1nvNcbAjgE/cd89sJD+TB6Yp3zlW9M/2b/Pad2IoGJi1OZA5yyZZonAN2D5P/RGxQDhNbLHFc7mCq9xrWiUW1hWCHicxWjNY4mLz/jSzP85yjc5ByJtGYw1dlhJVEKIyVHbCbCdfkiRrYpV0DnYWuHAzXiTkZZzuez9IQTaHCwmMnREoO5kKIqtfhvSjA+uhzMFGRi4v0xm1B7Goy0pSD6UiBFblZbPemE+WcL3bWrK0ot8tSJBiCkoO5vpuIHcscikj6e+70Bcri3uqdAvTPFVWkgPQ7E7G+fZcfJQd7VHpILP8iog2h97Okn4NPig72CepTOkkOg8FhuZVfgsXA5BAR5q2oSw6G68Wiz06xopBdEC/nuVz5RexmKgfPeFLsmMLvfCiW/9ennZRdYhuEyJEDJ8R5dTl+0ZETxW+k+RxcC859RJbCyF2q/Zeae2FgfrZMxU5qoc/BwCJiJ1AcdZ0OqO53RWMC78li5ncIn6XL/dp0NQQr4mBediLLq19eejXwg/68EKa7dl4LRDrux3cX7uBBFxXVc9x5VKergeezeeGc25c7+yA6DHUFW4s7eLXmf7dAqCf8zprPj5XZ/484ZVHyR8yV4kLVV6r7pb7I/V+ySewsyEq+LbTtqbwh9r4Uja1F7sjIyMjI6vM31loh9bg9HnQAAAAASUVORK5CYII=>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAZCAYAAAAiwE4nAAAA+ElEQVR4XmNgGAXDDSQD8UksuAFJDU3ATSD+D8SM6BK0AiDLQJgugIcBYtledAlaAQUGiIX9aOI0A5VAfBeIDdElaAE4gHghAyQ4hdHkaALsgfg1EGegS2ABzAyQ7IItri2BeBm6IDaQzwCJPwt0CShYB8RyQKwFxLsZIJadQFHBwBAPxPOB+A6aOFZwmgFiISho0QFILARNbCIDpoUgIM6AXRwDgCwDBSk6kAXig0DMgiZOkYUgH4AsPIcuAQQ7gPgzuiADmRaqMCBKFnwYW74ky0JKAN0tnMwASWjoQIoBIk61wh/mA+Qgz4HKuaOJE5U9RsEowAkAU+NBbQpIaH4AAAAASUVORK5CYII=>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAZCAYAAADe1WXtAAAA+0lEQVR4XmNgGAW0BrZAfBSIT6Lh3ciKyAXrgPg/ECugiVMELjNADOVAl6AEgAx8jS5ICeBhgBh6Gl2CEuDBADE0B12CElDJAPG6PboEuUABiM8B8UIGwpG0HYinM0AcsBRNDgWAvP4ZiPPRJaAgEoiZgVgGiGWhYj5A/JwBEhdYwWoGSHhKoUsAgSUQ74ey44B4BRBzQfkTGfDEAciVIEPRASMQPwJiJ3QJIJBngKQUkOuxAlzpM5cB4koxdAkgaGKAWIgCxBkghhHCpjANSMCIAbs42UAXiFci8aOR2GQBPiC+yoAoxc4CsQ6KCjJABgNm8ICCcRQMJQAAFd43zN8UgIkAAAAASUVORK5CYII=>