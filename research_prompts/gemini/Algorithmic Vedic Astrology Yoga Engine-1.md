# **Algorithmic Architecture and Computational Framework of Classical Vedic Yogas**

The translation of classical Vedic astrological principles into a deterministic, high-fidelity algorithmic prediction engine requires an exceptionally rigorous structural framework. To achieve the targeted prediction accuracy exceeding ninety percent, the computational architecture must transcend rudimentary planetary placements and systematically evaluate multi-dimensional planetary state conditions, topological house mappings, cancellation vectors, and complex temporal activation triggers. This comprehensive analysis exhaustively codifies the classical library of planetary combinations (yogas) and their modifier rules extracted from foundational treatises, including the Brihat Parashara Hora Shastra, Brihat Jataka, Saravali, Phaladeepika, Sarvartha Chintamani, Jataka Parijata, Uttara Kalamrita, Mansagari, and Jataka Bharanam. The following schema provides the robust logic and algorithmic definitions required for programmatic implementation.

## **SECTION 1: COMPLETE YOGA CATALOG**

The algorithmic detection of astrological yogas necessitates precise, boolean evaluation of planetary coordinates, lordship arrays, mutual aspects, dignity matrices, and house (bhava) occupancies. The computational engine must instantiate a matrix representing the twelve discrete houses and a vector array for the nine grahas (planets), continuously scanning for the specific geometric and dignitary intersections defined in the classical literature.

The table below structures the exhaustive catalog of classical yogas into the required computational logic format. This dictates the exact conditions for true/false validation within the engine's decision tree, mapping each yoga to its classical source, its resultant domain (including strength tiers such as Raja, Dhana, or Dosha), its specific cancellation (bhanga) conditions, and the requisite Dasha period for its fructification.

| NAME | CONDITION | SOURCE | DOMAIN | BHANGA\_CONDITION | FRUCTIFICATION\_DASHA |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Gaja-Kesari Yoga | Jupiter in Kendra (1, 4, 7, 10\) from the Moon, or conjunct the Moon.1 | Phaladeepika / General | Raja/Fame Tier: Wealth, illustrious fame, scholarly intellect, lasting reputation.2 | Jupiter combust, debilitated, or severely afflicted by Saturn or Rahu without benefic relief.3 | Jupiter or Moon Mahadasha/Antardasha (MD/AD).5 |
| Budha-Aditya (Nipuna) Yoga | Sun and Mercury conjunct in the same house without Mercury being combust.1 | Jataka Parijata / General | Raja/Intellect Tier: Brilliance in speech, logic, administrative skills, high reputation.2 | Mercury mathematically combust strictly within 12° (if retrograde) or 14° (direct) of the Sun.4 | Sun or Mercury MD/AD.5 |
| Dharma-Karmadhipati Raja Yoga | Mutual aspect, conjunction, or exchange of signs between the 9th lord and 10th lord.4 | BPHS / Saravali | Raja Tier: High status, career success, accumulation of wealth, ruling power.4 | The 10th lord occupying the 6th house from the 10th (i.e., the 3rd house from Lagna).6 | MD of the 9th lord or 10th lord; AD of the participating planet.6 |
| Hamsa (Panchamahapurusha) | Jupiter in Kendra (1, 4, 7, 10\) from Lagna AND in its own sign (Sagittarius/Pisces) or exalted (Cancer).7 | BPHS 77:1-2 | Mahapurusha Tier: Leadership, religious authority, extreme fortune, expansion.9 | Jupiter debilitated in Navamsa (D9) or defeated in Graha Yuddha (planetary war).10 | Jupiter MD/AD.11 |
| Malavya (Panchamahapurusha) | Venus in Kendra (1, 4, 7, 10\) AND in its own sign (Taurus/Libra) or exalted (Pisces).8 | BPHS / Phaladeepika | Mahapurusha Tier: Material comfort, beauty, diplomacy, arts, grace.9 | Venus mathematically combust or tightly conjunct the nodes (Rahu/Ketu).13 | Venus MD (20-year span).14 |
| Ruchaka (Panchamahapurusha) | Mars in Kendra (1, 4, 7, 10\) AND in its own sign (Aries/Scorpio) or exalted (Capricorn).7 | BPHS / Phaladeepika | Mahapurusha Tier: Courage, competitive dominance, military or police power.9 | Mars located in Bhava Sandhi (house cusps) or defeated in Graha Yuddha.15 | Mars MD (7-year span).17 |
| Bhadra (Panchamahapurusha) | Mercury in Kendra (1, 4, 7, 10\) AND in its own sign (Gemini/Virgo) or exalted (Virgo).8 | BPHS / Phaladeepika | Mahapurusha Tier: Exceptional intelligence, communication, commerce, wealth.9 | Mercury combust or heavily afflicted by natural malefics without relief.13 | Mercury MD (17-year span).17 |
| Sasa (Panchamahapurusha) | Saturn in Kendra (1, 4, 7, 10\) AND in its own sign (Capricorn/Aquarius) or exalted (Libra).7 | BPHS / Phaladeepika | Mahapurusha Tier: Political power, endurance, maintenance of social order, duty.7 | Saturn combust or closely aspected by its enemy, Mars.13 | Saturn MD (19-year span).17 |
| Amala (Amala-Kirti) Yoga | A natural benefic (Jupiter, Venus, unblemished Mercury or Moon) occupying the 10th house from Lagna.1 | Jataka Bharanam | Fame Tier: Lasting fame, philanthropy, reverence by rulers, spotless reputation.1 | A malefic planet aspecting or occupying the 10th house.1 | Dasha of the benefic planet in the 10th house.1 |
| Kemadruma Yoga | Absence of any planets (excluding Sun, Rahu, Ketu) in the 2nd and 12th houses from the Moon.1 | BPHS / Phaladeepika | Dosha Tier: Poverty, mental anguish, loss of wealth, severe humiliation.9 | Planets present in Kendra from Lagna or Moon; or Jupiter aspecting the Moon.1 | Moon MD; intensified during adverse transits. |
| Kahala Yoga | Lords of the 4th and 9th houses positioned in mutual Kendras, while the Lagna lord is exceptionally strong.1 | Jataka Bharanam | Raja Tier: Courage, aggressive leadership, military command, land ownership.1 | Lagna lord weak or placed in a Dusthana (6, 8, or 12th house).1 | MD of the 4th or 9th lord. |
| Viparita Sarala Raja Yoga | Lord of the 8th house placed exclusively in the 6th, 8th, or 12th house.1 | Phaladeepika 6/65 | Raja Tier: Longevity, prosperity, victory over enemies, massive success from crisis.1 | Benefic conjunction or aspect directly onto the 8th lord.19 | MD of the 8th lord.19 |
| Lakshmi Yoga | Lagna lord strong AND the 9th lord occupying a Kendra identical to its own or exalted sign.1 | Sarvartha Chintamani | Dhana/Raja Tier: Immense wealth, vast lands, virtue, illustrious royal reputation.1 | 9th lord combust, debilitated, or defeated in planetary war.13 | 9th lord MD or AD. |
| Saraswati Yoga | Jupiter, Venus, and Mercury occupying Kendras, Trikonas, or the 2nd house with high residential strength.2 | Jataka Parijata | Intellect Tier: Supreme learning, literary talent, eloquence, artistic mastery.2 | Any of the three participating planets combust or strictly debilitated.13 | MD of Mercury, Jupiter, or Venus. |
| Maha-Parivartana Yoga | Mutual exchange (Parivartana) between the Lagna lord and the lord of the 2nd, 4th, 5th, 7th, 9th, 10th, or 11th house.1 | Phaladeepika | Raja/Dhana Tier: Massive wealth, high status, physical enjoyments, mutual support.1 | One of the exchanged planets is retrograde and occupying its exaltation sign (acts debilitated).19 | MD of either exchanging planet.2 |
| Adhi Yoga | Benefic planets (Jupiter, Venus, Mercury) exclusively occupying the 6th, 7th, and 8th houses from the Moon.2 | Saravali | Raja Tier: Calm mind, royal lifestyle, lasting fame, executive leadership.2 | Presence of malefic planets interfering in the 6th, 7th, or 8th from the Moon.20 | MD of the benefics occupying those specific houses. |
| Voshi Yoga | A planet (excluding the Moon) occupying the 12th house from the Sun.1 | Mansagari | Character Tier: Eloquence, physical strength, renown, scientific pursuits (if benefic).1 | If formed by a malefic, yields poor intelligence, untruthfulness, and cruel nature.1 | Dasha of the planet in the 12th from the Sun. |
| Veshi Yoga | A planet (excluding the Moon) occupying the 2nd house from the Sun.1 | Jataka Bharanam | Character Tier: Wealth, capability to defeat opponents, powerful eloquence.1 | Malefic in the 2nd from the Sun causes physical and speech defects.1 | Dasha of the planet in the 2nd from the Sun. |
| Sunapha Yoga | A planet (excluding the Sun) occupying the 2nd house from the Moon.1 | Saravali | Dhana Tier: King-like status, self-earned fortune, virtuous and contented nature.1 | Malefic occupying the 2nd house from the Moon causes severe financial drain.1 | Dasha of the planet in the 2nd from the Moon. |
| Anapha Yoga | A planet (excluding the Sun) occupying the 12th house from the Moon.1 | Saravali | Character Tier: Health, affability, renowned reputation, material possessions.1 | Malefic occupancy creates adverse career effects and loss of reputation.1 | Dasha of the planet in the 12th from the Moon. |
| Buddhmaturya Yoga | The 5th house lord is a natural benefic, is aspected by a benefic, or is placed in a benefic sign.1 | Sarvartha Chintamani | Intellect Tier: Great intelligence, highly moral character, academic success.1 | The 5th lord conjunct Rahu/Ketu or aspected by Saturn/Mars.13 | 5th lord MD. |
| Ubhayachari Yoga | Planets (excluding the Moon) occupying both the 2nd and 12th houses from the Sun.1 | Sarvartha Chintamani | Raja Tier: King-like strong physique, capability for great responsibility, balanced outlook.1 | Malefics in both positions severely corrupt the results, causing intense struggle.1 | MDs of the planets flanking the Sun. |
| Mangal-Budha Yoga | Mars and Mercury conjunct in the exact same house.1 | General Classical | Career Tier: Skill in medicine, metalcraft, architecture, or fine arts; eloquent but average wealth.1 | Conjunction occurs in a Dusthana (6, 8, 12\) or either planet is combust.13 | Mars or Mercury MD. |
| Dattaputra Yoga | The 5th house lord is weak and completely disconnected from the lords of the Lagna and 7th house.1 | Phaladeepika 12/8 | Progeny Tier: Denotes the adoption of a child due to lack of biological progeny.1 | Jupiter (Karaka for children) exceptionally strong and aspecting the 5th house.1 | 5th lord MD or Jupiter MD. |
| Matrudirgayur Yoga | The lord of the Navamsha (D9) sign holding the 4th lord is strong and placed in a Kendra from Lagna or Moon.1 | Sarvartha Chintamani | Health Tier: Guarantees a remarkably long life span for the native's mother.1 | Affliction to the Moon (Karaka for mother) by Saturn or Rahu.1 | 4th lord MD. |
| Sarira Sukhya Yoga | The Lagna lord, Jupiter, or Venus is placed strongly in a Kendra.1 | Sarvartha Chintamani | Health/Raja Tier: Extreme longevity, physical comfort, wealth, and political alignment.1 | The planet in Kendra is debilitated or defeated in planetary war.13 | Lagna lord, Jupiter, or Venus MD. |
| Purnayu Yoga | The 6th or 12th lord is placed in the 6th, 12th, 8th, or Lagna house, alongside strong 1st, 5th, and 8th lords.1 | Jataka Parijata | Health Tier: Maximum life span extending up to or beyond 100 years.1 | Lagna lord severely afflicted by Maraka (death-inflicting) planets.1 | N/A (Operates throughout life). |
| Akhanda Samrajya Yoga | The 11th, 9th, or 2nd lord in Kendra from the Moon, while Jupiter is the lord of the 2nd, 5th, or 11th house.1 | Jyotisharnava Navanitam | Raja/Dhana Tier: Vast, unbroken empire, tremendous executive control, and generational wealth.1 | Jupiter debilitated in Capricorn or combust the Sun.13 | Jupiter MD or the participating Kendra lord's MD. |
| Uttamadi Yoga | The Moon is positioned in an Apoklima house (3, 6, 9, 12\) counted from the Sun.1 | Saravali | Dhana Tier: Plenteous wealth, profound learning, and widespread fame.1 | The Moon is debilitated in Scorpio or strictly conjunct Ketu.1 | Moon MD. |

## **SECTION 2: COMPLETE YOGA BHANGA (CANCELLATION) RULES**

The predictive accuracy of an astrological engine depends entirely on its computational capacity to process Yoga Bhanga—the nullification, mitigation, or total inversion of a promised outcome. Classical texts outline rigorous mathematical and topological conditions under which planetary strengths are canceled or profound weaknesses are miraculously reversed. The algorithm must process these rules as dynamic weighting modifiers applied to the baseline score of any detected yoga.

### **Neecha Bhanga Raja Yoga (Cancellation of Debilitation)**

Neecha Bhanga Raja Yoga represents an alchemical transformation within the chart, turning a planet's profound weakness (debilitation) into an overwhelming asset. Algorithmically, this functions as an inverted multiplier. The *Phaladeepika* (Chapter 7, Slokas 26-30) establishes eight precise computational conditions for this cancellation. For a full Raja Yoga to manifest—where the liability becomes a spectacular advantage—the computational engine must verify that at least two of these eight conditions evaluate to true.

The algorithmic engine must check the following eight vectors for any debilitated planet:

First, it must identify the lord of the sign in which the planet is debilitated and verify if this dispositor is located in a Kendra (houses 1, 4, 7, or 10\) relative to the Lagna. Second, it must run the identical check for this dispositor relative to the Moon's position. Third, the system must identify the planet that rules the sign where the debilitated planet would theoretically be exalted, verifying if this exaltation lord is situated in a Kendra from the Lagna. Fourth, it checks if this exaltation lord is in a Kendra from the Moon. Fifth, the algorithm identifies the specific planet that achieves exaltation in the sign where the target planet is currently debilitated, checking if this secondary planet occupies a Kendra from the Lagna. Sixth, it checks if this secondary planet occupies a Kendra from the Moon. Seventh, the engine evaluates the spatial relationship between the lord of the debilitation sign and the lord of the exaltation sign, returning true if they occupy mutual Kendras to each other. Finally, the eighth condition checks if the debilitated planet is receiving a direct aspect from the lord of the sign it currently occupies.

Additional enhancer logic must be programmed to check the Navamsa (D9) divisional chart; if the debilitated planet occupies its exact sign of exaltation within the Navamsa matrix, the debilitation is immediately canceled. The temporal output of this algorithm must generate a "delayed success" timeline. Classical rules dictate the dictum "First the nīcha, then the bhanga," meaning the native must initially experience the failure, humiliation, or liability associated with the debilitated planet before the cancellation protocol activates to yield power and prosperity.

### **Graha Yuddha (Planetary War) Cancellation Rules**

When two true planets—strictly excluding the luminaries (Sun and Moon) and the nodes (Rahu and Ketu)—are conjunct within a tight longitudinal orb of one degree, a Graha Yuddha (planetary war) occurs. The defeated planet suffers a catastrophic loss of dignity, stripping it of its ability to confer any positive yoga results. If a yoga-forming planet loses a Graha Yuddha, all yogas dependent on that planet are heavily diminished, and the victorious planet absorbs its operational strength.

The algorithmic determination of the victor requires multi-dimensional coordinate evaluation. According to the foundational *Brihat Parashara Hora Shastra*, the base rule declares the planet with the lower longitudinal degree as the winner. However, the *Uttara Kalamrita* provides an advanced, three-dimensional override: if the longitudes are highly exact (matching up to minutes of arc), the algorithm must reference latitudinal coordinates. The planet with the higher northern declination (latitude) is declared the victor.

Furthermore, the *Uttara Kalamrita* introduces categorical severity algorithms dividing the combatant planets into *Paura* (Mercury, Jupiter, Saturn) and *Yayi* (Mars, Venus). The engine must apply varying cancellation weights based on these classes. A war between two *Paura* planets triggers the absolute most severe cancellation of associated yogas. A war between a *Paura* and a *Yayi* is moderately severe, while a war between two *Yayi* planets is considered mathematically mild, resulting in only partial cancellation of the defeated planet's yogas.

### **Combustion (Asta) Cancellation Rules**

Combustion acts as a primary nullification vector for Raja Yogas and Dhana Yogas. When a planet's longitude approaches the Sun's longitude, its rays are physically eclipsed, rendering it mathematically impotent. The proximity thresholds for combustion vary by planet, but general algorithmic implementation requires testing if the absolute distance between the Sun and the target planet falls within a 12° to 14° orb.

An explicit computational exception applies to the retrograde inner planets (Mercury and Venus). Because they are geographically closer to Earth during retrogression and positioned between the Earth and the Sun, their combustion effects are mitigated. The algorithm must reduce the combustion penalty for a retrograde Venus or Mercury. If any planet forming a major Raja Yoga is found to be combust, the yoga's output score must be reduced to near zero, rendering the results negligible, unless specific mitigating factors—such as an exceptionally high Ashtakavarga bindu count for that planet—are present to offset the eclipse.

### **Retrograde (Vakri) Enhancement and Cancellation**

The evaluation of retrograde planets (Vakri grahas) introduces complex, paradoxical conditional logic into the engine. According to the *Phaladeepika*, a retrograde planet accumulates exceptional strength (Cheshtabala), rendering its output equivalent to an exalted state, even if it is geographically positioned in a debilitated or inimical sign.

However, the *Uttara Kalamrita* posits a polar logic array that the algorithm must strictly follow. If a planet is retrograde while simultaneously occupying its sign of exaltation, its output acts as though it is deeply debilitated, reducing its associated yogas to zero effect. Conversely, if a planet is debilitated and retrograde simultaneously, the double-negative logic evaluates it as though it is exalted. This requires the engine to map an explicit boolean gate: IF state \== retrograde AND position \== debilitated THEN effective\_status \= exalted. Furthermore, retrograde planets inherently delay the fructification of their yogas, requiring the timeline engine to push the predicted manifestation dates later into the native's Dasha period.

## **SECTION 3: YOGA FRUCTIFICATION RULES**

The structural existence of a yoga in a static natal chart represents mere potential energy. To achieve predictive accuracy, the algorithmic engine must compute precise temporal triggers to forecast exactly when these combinations materialize into tangible life events. This requires the synchronization of Dasha periods, transit overlays, and chronological age mapping.

### **Dasha and Antardasha Activation Requirements**

The Vimshottari Dasha system, operating on a maximal human life cycle of 120 lunar years, dictates the macro-periods of yoga manifestation. The algorithm calculates this by determining the exact longitudinal displacement of the Moon within its natal Nakshatra at the time of birth, yielding the proportional starting point of the sequence. For a primary yoga to fructify, the Mahadasha (MD) lord currently running must be a participating planet in the yoga. The Antardasha (AD), or sub-period, determines the exact fractional window of manifestation.

According to stringent astrological parameters, the spatial relationship between the MD and AD lords in the natal chart is critical for activation. If the algorithm detects that the MD and AD lords are positioned in a 1-7 axis (mutual aspect) from each other in the birth chart, the period yields maximal output for the yoga's promise. Conversely, if the MD and AD lords are locked in a 2-12 or 6-8 axis (Shadashtaka), the energy is severely obstructed, and the yoga will fail to manifest smoothly. A foundational Parashari rule also dictates that if the MD and AD lords are the identical planet (e.g., the first sub-period of Jupiter within the major period of Jupiter), the results remain strictly neutral. The yoga will not spike during this initial phase; fructification explicitly requires the AD of a cooperating but distinct planetary agent.

### **Transits and the Double Transit Rule**

Transits (Gochara) function as the final validation gate for an event within the engine. While Dashas provide the background potential, transits act as the immediate catalyst. The most critical algorithmic filter required here is the "Double Transit" rule, which tracks the simultaneous orbital movements of Saturn (the Karaka of physical manifestation and karma) and Jupiter (the Jeeva Karaka of blessings and intention).

The engine must calculate the forward-looking aspects of both slow-moving planets and identify the intersection sets of their aspect matrices. When both Saturn and Jupiter simultaneously transit over or aspect a specific natal house, its lord, or a yoga-forming coordinate, that house becomes fully "activated." For instance, if a natal Dhana Yoga exists in the 2nd house, the exact timing of wealth manifestation occurs during the precise months when transit Jupiter and transit Saturn jointly aspect the 2nd house or its lord. The algorithm must not rely on transits alone; if the Double Transit activates a house but the underlying Dasha does not support the event, the manifestation will be minor or psychological rather than a major life event.

### **Age Theory and Manduka Gati Sequences**

According to Jaimini principles and classical longevity distributions, specific houses govern distinct chronological blocks of the native's life. The algorithm must map a natural lifespan of 108 years, dividing it into 12 distinct segments of 9 years each. The sequence of chronological house activation does not follow the standard zodiacal order but rather the non-linear path of *Manduka Gati* (the frog's leap).

The computational sequence of house activation is programmed as follows: 4th house \-\> 2nd house \-\> 8th house \-\> 10th house \-\> 12th house \-\> 6th house \-\> 5th house \-\> 11th house \-\> 1st house \-\> 7th house \-\> 9th house \-\> 3rd house. Consequently, the engine must map the yogas found in the natal chart to specific human age thresholds based on their house placement. Yogas occurring in the 4th, 2nd, 8th, and 10th houses govern "Early Life" (ages 0 to 36). Yogas occupying the 12th, 6th, 5th, and 11th houses govern "Middle Life" (ages 36 to 72). Yogas situated in the 1st, 7th, 9th, and 3rd houses govern "Late Life" (ages 72 to 108). For example, a Raja Yoga positioned in the 4th house will algorithmically project massive success during early adulthood, whereas the exact same yoga in the 9th house delays its ultimate fruition until old age.

Further computational granularity is achieved by assessing the sign modalities of the yoga's location within that 9-year block. Sirsodaya signs (Gemini, Leo, Virgo, Libra, Scorpio, Aquarius) force the yoga to fructify in the early third (first 3 years) of the designated 9-year period. Pristodaya signs (Taurus, Cancer, Sagittarius, Capricorn) force manifestation in the late third (final 3 years), while Ubhayodaya signs (Pisces) yield results squarely in the middle 3-year segment.

## **SECTION 4: NABHASA YOGAS (COMPLETE SET)**

The 32 Nabhasa Yogas form the topological and structural backbone of Vedic chart analysis. These yogas are evaluated completely independent of planetary lordships, specific dignities, or Dasha periods. They rely entirely on the continuous geometric distribution of the seven visible planets across the 12 celestial houses. Because they represent the overarching pattern of the native's life, the engine must implement spatial pattern recognition arrays to detect these 32 formations before processing any other logic. They are categorized into four distinct computational classes.

### **Ashraya Yogas (Sign-Based)**

These three yogas depend purely on the modality of the signs occupied by the planets. The algorithm must use modulo arithmetic to group the zodiac signs into Movable, Fixed, and Dual arrays.

1. The **Rajju Yoga** is triggered when all seven planets occupy solely Movable (Chara) signs (Aries, Cancer, Libra, Capricorn). This pattern outputs a highly ambitious, adaptable, and intellectually mobile native who frequently travels but lacks stability.  
2. The **Musala Yoga** is triggered when all seven planets occupy solely Fixed (Sthira) signs (Taurus, Leo, Scorpio, Aquarius). This outputs a stable, obstinate nature focused on accumulation and resolute determination.  
3. The **Nala Yoga** is triggered when all seven planets occupy solely Dual (Dvisvabhava) signs (Gemini, Virgo, Sagittarius, Pisces). This outputs a pedantic, multi-tasking individual prone to exploring options but occasionally losing opportunities due to over-analysis.

### **Dala Yogas (House-Based)**

These two yogas evaluate the disposition of natural benefics versus natural malefics specifically within the angular houses (Kendras: 1, 4, 7, 10).

4\. The **Maala (Srik) Yoga** is produced if three of the angular houses are occupied exclusively by benefic planets, outputting constant enjoyment, luxury, and fine clothing.

5\. The **Bhujanga (Sarpa) Yoga** is produced if three of the angular houses are occupied exclusively by malefic planets, outputting a life fraught with continuous struggle, hostility, and restriction.

### **Akriti Yogas (Shape-Based)**

These twenty yogas demand stringent pattern-matching algorithms, evaluating specific permutations of angular, succedent, and cadent house occupancies to identify celestial geometry.

6\. **Gada Yoga**: All planets confined exclusively to two successive angles (houses 1-4, 4-7, 7-10, or 10-1).

7\. **Sakata Yoga**: All planets restricted entirely to the 1st and 7th houses, causing severe fluctuations in fortune.

8\. **Vihanga (Pakshi) Yoga**: All planets restricted entirely to the 4th and 10th houses, yielding a wandering nature.

9\. **Sringataka Yoga**: All planets restricted to the primary trines (1st, 5th, 9th houses), outputting happiness and martial prowess.

10\. **Hala Yoga**: All planets restricted to mutual trines originating from non-angles (houses 2-6-10, or 3-7-11, or 4-8-12), denoting agricultural or labor-intensive wealth.

11\. **Vajra Yoga**: All natural benefics placed in the 1st and 7th houses, with all natural malefics confined to the 4th and 10th houses.

12\. **Yava Yoga**: The inverse of Vajra. All malefics in the 1st and 7th houses, with all benefics confined to the 4th and 10th houses.

13\. **Kamala Yoga**: All seven planets distributed across all four angular houses (1, 4, 7, 10), yielding extreme prominence and purity.

14\. **Vapi Yoga**: All planets distributed exclusively in cadent houses (3,6,9,12) OR exclusively in succedent houses (2,5,8,11), indicating hidden wealth or indirect power.

15\. **Yupa Yoga**: All planets occupying four consecutive houses starting precisely from the Lagna (houses 1, 2, 3, 4).

16\. **Sara Yoga**: All planets occupying four consecutive houses starting precisely from the 4th house (houses 4, 5, 6, 7).

17\. **Shakti Yoga**: All planets occupying four consecutive houses starting precisely from the 7th house (houses 7, 8, 9, 10).

18\. **Danda Yoga**: All planets occupying four consecutive houses starting precisely from the 10th house (houses 10, 11, 12, 1).

19\. **Nauka Yoga**: All planets occupying the first seven consecutive houses (1 through 7), representing a boat-like shape.

20\. **Koota Yoga**: All planets occupying seven consecutive houses starting from the 4th house (4 through 10).

21\. **Chatra Yoga**: All planets occupying seven consecutive houses starting from the 7th house (7 through 1).

22\. **Chapa Yoga**: All planets occupying seven consecutive houses starting from the 10th house (10 through 4).

23\. **Ardha Chandra Yoga**: All planets occupying seven contiguous houses starting from any succedent or cadent house (a non-Kendra starting point).

24\. **Chakra Yoga**: All planets occupying six alternative signs commencing from the Lagna (houses 1, 3, 5, 7, 9, 11), generating immense imperial power.

25\. **Samudra Yoga**: All planets occupying six alternative signs commencing from the 2nd house (houses 2, 4, 6, 8, 10, 12), yielding oceanic wealth and stability.

### **Sankhya Yogas (Count-Based)**

These seven yogas calculate the unique number of distinct zodiac signs occupied by the seven planets. The algorithm must enforce a strict precedence rule: if any Akriti Yoga is successfully detected, the Sankhya Yogas are bypassed and nullified to prevent contradictory outputs.

26\. **Gola Yoga**: All planets restricted to exactly 1 single sign. Indicates destitution and social isolation.

27\. **Yuga Yoga**: All planets restricted to exactly 2 signs. Indicates heresy and poverty.

28\. **Soola Yoga**: All planets restricted to exactly 3 signs. Indicates a sharp, violent, or piercing nature.

29\. **Kedara Yoga**: All planets restricted to exactly 4 signs. Indicates agricultural wealth and truthfulness.

30\. **Paasa Yoga**: All planets restricted to exactly 5 signs. Indicates a large family and skill in wealth acquisition, though prone to entanglement.

31\. **Daamini Yoga**: All planets restricted to exactly 6 signs. Indicates a charitable, helpful disposition with numerous cattle/assets.

32\. **Veena Yoga**: All planets distributed across exactly 7 separate signs. Indicates a highly cultured, musical, and harmonious life.

## **SECTION 5: COMPOUND YOGA INTERACTIONS**

To achieve the targeted predictive accuracy, the algorithmic engine must account for multiplier effects when isolated yogas overlap. Astrological combinations do not scale linearly; the co-presence of multiple favorable combinations results in exponential output enhancements, while conflicting yogas require complex resolution logic to determine the net vector of the native's life.

### **Panchamahapurusha and Raja Yoga Symbiosis**

The five Mahapurusha yogas (Ruchaka, Bhadra, Hamsa, Malavya, Sasa) grant highly specialized personality characteristics and professional dominance based on the exalted or own-sign placement of the five non-luminary planets in Kendras. However, when these yogas geographically intersect with standard Raja Yogas (such as the conjunction of Kendra and Trikona lords), the result is algorithmically magnified.

Classical texts indicate that the presence of a strong Jupiter or Venus forming a Mahapurusha yoga within a Kendra contributes up to 60% of the maximum required strength to manifest an overarching Raja Yoga. If a native has a Dharma-Karmadhipati Raja Yoga (9th and 10th lords interacting), and one of those lords simultaneously forms a Mahapurusha Yoga, the computational logic must assign a massive heavy-weighting factor to the career output. The Mahapurusha planet acts as an indestructible foundation, ensuring that the Raja Yoga does not collapse under the pressure of hostile transits.

### **Dhana Yoga Stacking and Wealth Thresholds**

Dhana Yogas dictate financial accumulation by mapping the relationships between specific wealth-generating houses: the 1st (self), 2nd (accumulated bank balance), 5th (speculative intelligence and investments), 9th (fortune and luck), and 11th (liquid income and networking gains). The engine must evaluate the number of concurrent Dhana Yogas to determine the ultimate financial output tier.

The base threshold for financial stability is triggered by a single connection between the 2nd and 11th lords, such as a mutual aspect. This establishes a continuous flow between earning and accumulating. However, algorithmic multipliers are activated when the 5th and 9th lords are integrated into this 2nd/11th axis. The maximum yield—representing extreme, unparalleled wealth—is achieved when a Parivartana (exchange of signs) occurs between the 2nd and 11th lords, coupled with the direct influence of a strong Lagna lord.

When the system detects three or more distinct Dhana Yogas coexisting—especially if supported by the placement of the natural wealth significators (Jupiter and the Sun) in high dignity—the native radically exceeds normal prosperity thresholds, indicating multi-millionaire or billionaire potential. Conversely, the algorithm must enforce a strict cancellation trigger: if Saturn occupies the 2nd house, severely aspects the 2nd lord, or associates with the 2nd lord from the Lagna or Moon, this acts as a hard mathematical ceiling on the Dhana Yoga output. Regardless of the stacking density of the wealth combinations, this specific Saturnian influence restricts fluid accumulation, forcing the native into a state of continuous financial resistance or debt.

#### **Works cited**

1. Astrological Yogas in Brief | PDF | Religion & Spirituality \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/doc/145045075/Astrological-Yogas-in-Brief](https://www.scribd.com/doc/145045075/Astrological-Yogas-in-Brief)  
2. 20 most-cited classical Yogas (planetary combinations) in Jyotisha Shastra (Vedic Astrology, accessed on February 28, 2026, [https://www.youtube.com/watch?v=PXYaQnUQ8Tk](https://www.youtube.com/watch?v=PXYaQnUQ8Tk)  
3. The Dhana Yogas: Thoughts on some wealth conferring combinations | by Varaha Mihira, accessed on February 28, 2026, [https://medium.com/thoughts-on-jyotish/the-dhana-yogas-thoughts-on-some-wealth-conferring-combinations-b0f5f45021c5](https://medium.com/thoughts-on-jyotish/the-dhana-yogas-thoughts-on-some-wealth-conferring-combinations-b0f5f45021c5)  
4. How does a retrograde planet effect yogas in birth chart \[closed\] \- Hinduism Stack Exchange, accessed on February 28, 2026, [https://hinduism.stackexchange.com/questions/62837/how-does-a-retrograde-planet-effect-yogas-in-birth-chart](https://hinduism.stackexchange.com/questions/62837/how-does-a-retrograde-planet-effect-yogas-in-birth-chart)  
5. Vedic Astrology: Vimshottari Dasha Guide | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/595134912/dasa-a](https://www.scribd.com/document/595134912/dasa-a)  
6. Raja yoga (Hindu astrology) \- Wikipedia, accessed on February 28, 2026, [https://en.wikipedia.org/wiki/Raja\_yoga\_(Hindu\_astrology)](https://en.wikipedia.org/wiki/Raja_yoga_\(Hindu_astrology\))  
7. Panchamahapurusha Yoga comments examples \* BP Lama Jyotishavidya, accessed on February 28, 2026, [https://barbarapijan.com/bpa/Yoga/Panchmahapurusha\_yoga.htm](https://barbarapijan.com/bpa/Yoga/Panchmahapurusha_yoga.htm)  
8. Pancha Mahapurusha Yoga | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/doc/295015146/Pancha-Mahapurusha-Yoga](https://www.scribd.com/doc/295015146/Pancha-Mahapurusha-Yoga)  
9. Yogas in Vedic Astrology | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/253561698/Yogas-in-Vedic-Astrology](https://www.scribd.com/document/253561698/Yogas-in-Vedic-Astrology)  
10. Graha-yuddha or planetary war \- Indian Astrology Secrets \- Quora, accessed on February 28, 2026, [https://indianastrologysecrets.quora.com/Graha-yuddha-or-planetary-war](https://indianastrologysecrets.quora.com/Graha-yuddha-or-planetary-war)  
11. Panch Mahapurusha Rajyoga in Astrology|Kundli, accessed on February 28, 2026, [https://www.varanasiastro.com/panch-mahapurusha-rajyoga.html](https://www.varanasiastro.com/panch-mahapurusha-rajyoga.html)  
12. Pancha Mahapurusha Yogas \- Cosmic Insights, accessed on February 28, 2026, [https://blog.cosmicinsights.net/pancha-mahapurusha-yogas/](https://blog.cosmicinsights.net/pancha-mahapurusha-yogas/)  
13. Vedic Astrology 36, accessed on February 28, 2026, [https://www.eastrovedica.com/html/vedic\_astrology36.htm](https://www.eastrovedica.com/html/vedic_astrology36.htm)  
14. Dhan Yoga Combinations: Complete Wealth Guide \- AstroSight, accessed on February 28, 2026, [https://astrosight.ai/yogas/dhan-yoga-combinations-for-wealth](https://astrosight.ai/yogas/dhan-yoga-combinations-for-wealth)  
15. Uttarakalamrta 1.4.2. The Grahas that diminish the Shubha Yoga ..., accessed on February 28, 2026, [https://medium.com/thoughts-on-jyotish/uttarakalamrta-1-4-2-the-grahas-that-diminish-the-shubha-yoga-mentioned-in-verse-1-4-1-fe19702a3e4f](https://medium.com/thoughts-on-jyotish/uttarakalamrta-1-4-2-the-grahas-that-diminish-the-shubha-yoga-mentioned-in-verse-1-4-1-fe19702a3e4f)  
16. Planetary War | PDF | Horoscope | Planets \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/365154191/Planetary-War](https://www.scribd.com/document/365154191/Planetary-War)  
17. Vimsottari \- Flowjoule, accessed on February 28, 2026, [http://www.flowjoule.com/vimsottari.html](http://www.flowjoule.com/vimsottari.html)  
18. 500 Yogas | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/doc/66490571/500-yogas](https://www.scribd.com/doc/66490571/500-yogas)  
19. How does a retro debilated planet works when in parivartan yoga? : r/Nakshatras \- Reddit, accessed on February 28, 2026, [https://www.reddit.com/r/Nakshatras/comments/1oovqda/how\_does\_a\_retro\_debilated\_planet\_works\_when\_in/](https://www.reddit.com/r/Nakshatras/comments/1oovqda/how_does_a_retro_debilated_planet_works_when_in/)  
20. GREAT Raj Yogas \- Nikhil Astro World, accessed on February 28, 2026, [https://nikhilastroworld.com/2020/11/19/great-raj-yogas/](https://nikhilastroworld.com/2020/11/19/great-raj-yogas/)  
21. Favourable Yogas \- Lakshana, accessed on February 28, 2026, [https://lakshana.home.blog/1001-yogas/](https://lakshana.home.blog/1001-yogas/)