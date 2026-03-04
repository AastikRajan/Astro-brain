# **Computational Framework for Prashna (Horary) Astrology Engines**

The architectural development of a computational engine for Prashna, or Vedic horary astrology, requires the translation of qualitative, esoteric logic into deterministic, quantitative algorithms. Unlike natal astrology (Jataka), which processes the static chronological coordinates of an individual's birth to evaluate lifelong karmic patterns, Prashna functions as a dynamic, real-time diagnostic system.1 It calculates the celestial mechanics at the exact moment a query crystallizes in the mind, operating on the foundational principle of synchronicity.1 This axiom posits that the state of the macrocosm at a specific temporal locus acts as a mirror for the resolution of a localized human query, making the chart a "horoscope of the question itself".2

To build an expert-level computational Prashna engine, the software architecture must support highly specialized chart construction methodologies, unique rule sets derived from classical texts like the *Prashna Marga*, kinematic orbital logic from the Tajika system, specialized domain modules (such as legal, medical, and lost object retrieval), and precise chronological forecasting matrices. This report provides the exhaustive computational framework necessary to encode these systems into a functioning deterministic engine.

## **The Epistemological and Astrometric Foundation of Prashna**

The foundational trigger for any Prashna algorithm is the timestamp and geolocation of the query. The engine must capture the exact geographic coordinates, including latitude, longitude, and altitude, alongside the precise temporal marker of the query's vocalization or internal crystallization.1 Because the Moon and the Ascendant (Lagna) traverse the zodiac rapidly—the Ascendant changes degree approximately every four minutes—precision to the exact second is a critical requirement for computational accuracy.2

The computational engine must utilize high-precision astronomical ephemerides, such as the Swiss Ephemeris, to calculate planetary longitudes and orbital velocities.3 Unlike Western horary astrology, which typically employs the tropical zodiac based on the vernal equinox, Vedic Prashna relies strictly on the sidereal zodiac.1 This requires the application of a predefined Ayanamsa, which mathematically accounts for the longitudinal difference between the tropical and sidereal zodiacs caused by the precession of the equinoxes. The Lahiri, or Chitra Paksha, Ayanamsa is the standard application mandated by most classical interpretations of the *Prashna Marga*.1

While the baseline astronomical calculations for planetary placement mirror those of a natal chart, the variables of interpretation and the operational rule sets diverge significantly.2 A natal engine evaluates lifetime patterns using extensive, multi-decade time-lord systems such as the Vimshottari Dasha, which spans a 120-year cycle. It also relies heavily on Parashari principles of planetary strength, such as the Shadbala (six-fold strength) system. Conversely, a Prashna engine evaluates immediate, binary, or highly specific short-term outcomes.4

In terms of what is computed differently, a Prashna engine often sidelines the 120-year Vimshottari Dasha in favor of compressed systems like the Mudda Dasha, which reduces the entire 120-year sequence into a single 360-day cycle, making it applicable for imminent events.4 Furthermore, while standard Parashari planetary strengths are noted, Prashna relies heavily on the Tajika Panchavargeeya Bala (five-fold strength) system to determine which planet exerts dominant force in a short-term horary conflict.4 The engine must also instantiate unique variables completely absent from natal charting, including mathematically derived ascendants (Arudha), environmentally observed variables (Nimitta), and specific kinetic planetary combinations (Tajika Yogas) used exclusively to calculate event manifestation.4

## **Computational Implementation of Prashna Marga Rules**

The *Prashna Marga*, recognized as the definitive classical treatise on horary astrology in the Vedic tradition, introduces specific mathematical and observational mechanisms for deriving query significators.7 These rules are particularly vital when casting charts based on non-temporal data or when augmenting the standard temporal chart to gain deeper diagnostic insight.

### **The Arudha Lagna Computation**

The Arudha Lagna serves as a secondary, mathematically derived ascendant, acting as a diagnostic cross-reference to the Udaya Lagna, which is the astronomically rising sign on the eastern horizon.6 In the computational framework of Prashna, the Udaya Lagna represents the internal state of the querent, their hidden motivations, and the invisible mechanics of the query. The Arudha Lagna, conversely, represents the external, tangible manifestation of the issue and how it interacts with the physical world.6

The computational formula for determining the Arudha Lagna mathematically is defined by the spatial displacement of the Ascendant Lord.10 The engine must execute the following logic: First, it identifies the Udaya Lagna and assigns it a numerical index from 1 to 12 (e.g., Aries \= 1, Taurus \= 2). Second, it identifies the current zodiacal location of the Lagna Lord, which is the planet ruling the Ascendant sign. Third, the engine calculates the absolute distance in houses from the Udaya Lagna to the Lagna Lord. Finally, the engine projects that exact same distance forward from the position of the Lagna Lord to establish the Arudha Lagna.6

To encode this, the engine relies on modulo arithmetic. For example, if Aries is the Udaya Lagna (Index 1\) and its ruling planet, Mars, is currently positioned in Leo (Index 5), the engine computes a distance of five houses. Counting five houses forward from Leo, inclusive of Leo itself, lands the Arudha Lagna in Sagittarius (Index 9).6 The engine must then spawn two parallel processing threads: one evaluating the chart from the perspective of the Udaya Lagna, and the other evaluating the chart from the Arudha Lagna. If benefics occupy the houses relative to the Arudha, the external outcome is deemed favorable regardless of the internal stress indicated by the Udaya Lagna.

### **Number-Based Prashna Modalities**

In scenarios where a client cannot provide exact birth data, or when the exact temporal moment of the query is ambiguous, the engine must switch its architecture from a time-based generation model to a deterministic random generation model based on user input.3 This relies on the premise that the numerical value chosen by the querent carries the same synchronistic weight as the temporal timestamp.

The primary algorithmic model for this is the 1-108 system, often associated with the Kalidas method.12 The user is prompted to input an integer between 1 and 108\. The engine processes this integer to determine both the primary Ascendant (Lagna) and the harmonic D-9 divisional chart ascendant (Navamsa Lagna).12 This mathematical structure is highly specific because the zodiac is composed of 12 signs, and each sign is divided into 9 Navamsas, resulting in exactly 108 distinct sub-divisions of the sky.14

To encode the 1-108 system, the engine utilizes standard quotient and remainder logic. The inputted number is divided by 9\. The quotient, plus one, dictates the rising sign, while the remainder dictates the specific Navamsa.12 If a user inputs the number 107, the engine divides 107 by 9, resulting in a quotient of 11 and a remainder of 8\. The Rising Sign is calculated as 11 \+ 1, which equals 12, mapping to Pisces. The remainder of 8 dictates that the Ascendant falls in the 8th Navamsa of Pisces.12 This calculation instantly generates a highly specific mathematical anchor for the chart, entirely bypassing the need for chronological data.

An alternative numerical framework that the engine must support is the Krishnamurti Paddhati (KP) 1-249 system.3 Under the KP architecture, the zodiac is divided into 249 unequal segments based on the sub-lords of the Vimshottari Dasha system. The user inputs a "seed number" from 1 to 249, which the engine immediately maps to a predefined lookup table. This table correlates the integer to a specific Zodiac Sign, a specific Nakshatra (lunar mansion), and a specific Sub-Lord, fixing the Ascendant down to exact minutes and seconds of a degree.3 This method is highly favored in computational astrology because it reduces the margin of error significantly and guarantees a static, easily reproducible chart baseline.

### **Phonemic Analysis and the Aksharachakra**

A highly sophisticated Prashna engine must also feature an acoustic hashing module capable of deducing the nature of the query by mapping the phonetic structure of the querent's name or the first word spoken by the querent to specific astrological coordinates.17 This system is known in classical texts as the Avakahada Chakra or the Aksharachakra.

Sanskrit, and by extension many Indo-European languages, is a morphophonemic language where specific sounds represent discrete energetic frequencies. Classical Vedic texts associate specific vowels and consonants directly with the twelve signs of the zodiac and the twenty-seven Nakshatras.17 The engine requires a complex dictionary or lookup table that maps the leading phoneme, known as the Pranakshara or "life-breath letter," to a specific astrological sign.7

| Zodiac Sign | Phonetic Consonant Class | Representative Phonemes (Approximations) |
| :---- | :---- | :---- |
| Aries (Mesha) | Palatals & Vowels | A, L, Ch, Cha |
| Taurus (Vrishabha) | Semi-vowels | I, U, V, Va, Vi |
| Gemini (Mithuna) | Velars | K, Kh, G, Gh |
| Cancer (Karka) | Aspirates | H, Ha, Hi, Hu |
| Leo (Simha) | Dentals | M, Ma, Mi, Mu |
| Virgo (Kanya) | Labials | P, Ph, T, Th |
| Libra (Tula) | Sibilants | R, Ra, Ri, Ru |
| Scorpio (Vrischika) | Nasals | N, Na, Ni, Nu |
| Sagittarius (Dhanu) | Fricatives | Bh, Bha, Bhi |
| Capricorn (Makara) | Gutturals | J, Ja, Ji |
| Aquarius (Kumbha) | Cerebrals | S, Sa, Si, Su |
| Pisces (Meena) | Compound Consonants | D, Da, Di, Du |

*Table 1: Approximation of the Avakahada phonemic mapping matrix utilized for Name-based Prashna derivation.*

In a computational sequence, the software analyzes the first syllable of the query or the querent's name. If the query begins with a hard 'K' sound, the engine cross-references the phonemic matrix and assigns Gemini as the functional Ascendant for the query.17 This phonemic mapping allows the software to establish a chart even when the user is remote and numerical input is unavailable, utilizing the inherent vibration of the text string input by the user.

### **Object-Based Prashna and Nimitta**

The concept of Nimitta refers to exogenous variables—environmental omens or physical actions occurring at the exact moment of the query.7 While a purely backend server cannot observe the physical world, a comprehensive frontend user interface can prompt the astrologer or the user to input specific observations to weight the algorithmic outcomes.

The engine's Nimitta module processes several distinct categorical variables. The first is direction. The classical texts assign specific planetary rulers to the cardinal and ordinal directions. If the user indicates they are facing East, the engine registers an active solar and martial influence, augmenting the strength of the Sun and Mars in the computational matrix.7 The second variable is Sharirika Shastra, or the science of physical touch. The zodiac naturally maps to the human anatomy, with Aries representing the head and Pisces representing the feet. The engine prompts the user to input which body part they instinctively touched while formulating the question. If the user selects the chest, the engine automatically assigns Cancer (the sign governing the chest) as the Prashna Lagna.7 Finally, the engine can evaluate breathing patterns. Classical horary astrology heavily weights whether the querent's left nostril (Ida, lunar, cooling, benefic) or right nostril (Pingala, solar, heating, malefic) is dominant at the moment of the query. The user inputs their dominant breath, allowing the engine to mathematically weight the chart toward either benefic expansion or malefic restriction.7

## **The Tajika vs. Parashari Aspectual Engine**

Once the Prashna chart is successfully cast and the Ascendant is fixed via time, number, or phoneme, the engine enters the primary analysis phase. Standard Parashari astrology relies on sign-based aspects. In the Parashari system, a planet influences entire signs regardless of its specific degree within its own sign. For instance, Jupiter always aspects the 5th, 7th, and 9th signs from its current position. However, for horary predictions, the computational engine must override this baseline and switch its aspectual engine to the Tajika system, which is an Arabic-Persian derivative deeply embedded into Indian horary astrology.24

The Tajika system calculates planetary relationships based on orbital proximity, exact degrees, and relative planetary velocity.24 A Tajika aspect is only valid if the two planets involved are within a mathematically defined sphere of influence, known as their Deeptamsha, or orb.24

| Planet | Deeptamsha (Orb of Influence) |
| :---- | :---- |
| Sun | 15 Degrees |
| Moon | 12 Degrees |
| Jupiter | 9 Degrees |
| Saturn | 9 Degrees |
| Mars | 8 Degrees |
| Mercury | 7 Degrees |
| Venus | 7 Degrees |

Table 2: The Deeptamsha values for Tajika computational orbs.24

To calculate an aspect, the engine must find the semi-sum of the orbs of the two planets involved. For example, if the engine is evaluating a connection between the Moon and Venus, it calculates the Moon's orb (12) plus Venus's orb (7), which equals 19\. Divided by two, the functional orb for their interaction is 9.5 degrees. If the Moon and Venus are separated by an aspectual angle (such as a trine of 120 degrees) plus or minus 9.5 degrees, the engine registers a valid Tajika aspect.24

Furthermore, the nature of the aspect in the Tajika system differs from Parashari rules. The 5th and 9th house relationships (trines) are openly friendly and carry a 75 percent strength weight. The 3rd and 11th house relationships (sextiles) are secretly friendly, representing hidden assistance, carrying a 40 percent and 10 percent strength weight respectively. Conversely, the 4th and 10th house relationships (squares) are openly inimical and denote severe conflict, carrying a 75 percent malefic weight, while the 1st and 7th relationships (conjunction and opposition) denote intense, often hostile confrontations carrying a 100 percent strength weight.25

### **Ithasala and Ishrafa Logic Gates**

The core of the Tajika engine's ability to output a definitive "YES" or "NO" to any question relies on calculating the kinematic speeds of the planets to determine if an aspect is applying or separating. The engine must initialize the planets in a strict order of kinematic speed: the Moon is the fastest, followed by Mercury, Venus, the Sun, Mars, Jupiter, and finally Saturn.25

An **Ithasala Yoga** (Applying Aspect) forms when a faster-moving planet is placed at an earlier longitudinal degree than a slower-moving planet within an aspecting angle. Computationally, this indicates that the faster planet will mathematically "catch up" to the slower planet over time, eventually forming an exact geometric connection. In the context of a query, Ithasala translates directly to a "YES," signifying that the querent's desire and the object of their desire are moving toward a successful union.24 The algorithmic condition is defined as: If the speed of Planet 1 is greater than Planet 2, and the degree of Planet 1 is less than Planet 2, and the distance between them is within their combined orb, then Ithasala equals true. If the distance between the two planets is less than one single degree, the engine flags this as a "Complete Ithasala," indicating that the event is happening in the immediate, almost instantaneous present.25

Conversely, an **Ishrafa Yoga** (Separating Aspect) forms when the faster-moving planet has already passed the exact degree of the slower-moving planet. The mathematical opportunity for connection has elapsed. The engine interprets this as a "NO," indicating separation, failure, wastage, or an event that has already permanently concluded in the past.25 If the engine detects an Ishrafa Yoga between the significator of the querent and the significator of the goal, it halts execution on success probabilities and outputs a definitive failure notification.25

An edge case the engine must handle is the **Nakta Yoga**, or the translation of light. If the Lagna Lord (the querent) and the Karya Lord (the goal) are not in any recognized aspect with one another, the baseline output would be failure. However, if a faster-moving third planet, most commonly the Moon, is situated spatially between them and forms an Ithasala with both independent planets, it acts as a data bridge, transferring the light and energy from one to the other. The computational engine interprets a Nakta Yoga as a conditional success, outputting the qualitative string: "The goal will be accomplished, but only through the intervention of a third-party intermediary".27

## **Domain-Specific Prashna Algorithms**

Once the baseline chart is cast and the Tajika aspectual engine is initialized, the system enters the routing phase. It must assign specific planetary roles based on the exact category of the user's query. In all computational matrices, the Querent (the user asking the question) is represented by the 1st House Lord (Lagnesha) and the Moon, which acts as the cosmic messenger.3 The Quesited (the object, person, or goal sought) is represented by the Lord of the House directly governing that topic (Karyesha).28 The engine then routes the data through highly specific, domain-isolated subroutines.

### **The Lost Object Retrieval Algorithm**

Horary astrology is historically renowned for its highly deterministic spatial tracking capabilities regarding lost or stolen property.3 When a user submits a query regarding a missing item, the engine activates the Lost Object module, which isolates the evaluation to the 2nd House (representing movable possessions and valuables), the 4th House (representing the home and general storage), the 7th House (representing thieves or other people), and the 12th House (representing hidden, concealed, or lost environments).22

The engine's first task is to compute a Recovery Boolean to determine if the object is permanently gone or recoverable. The recovery probability is high if the Moon is strong, if benefic planets occupy the 2nd House, or if an Ithasala Yoga exists between the 1st Lord (the owner) and the 2nd Lord (the item).22 Angular placement is highly weighted; if the significator of the object is in an angular house (1st, 4th, 7th, 10th), the item is nearby and easily recoverable.22 Conversely, if the Ascendant falls in a malefic sign and is aspected by malefics, or if the 7th House is heavily afflicted by Mars or Rahu, the engine changes the boolean to false, outputting that the item has been permanently stolen or destroyed.31 If the significator is undergoing combustion by the Sun, the engine concludes the item is visually obscured and impossible to find in its current state.30

If recovery is deemed possible, the engine executes a Spatial Direction Matrix to output precise search locations. It evaluates the elemental nature of the zodiac signs occupied by the 2nd Lord, the 4th Lord, and the Moon to generate environmental clues.22

| Zodiac Element | Compass Direction | Environmental Output Clues |
| :---- | :---- | :---- |
| **Fire** (Aries, Leo, Sagittarius) | East | Warm places, near heating elements, stoves, fireplaces, electrical equipment, or areas with bright sunlight. |
| **Earth** (Taurus, Virgo, Capricorn) | South | Ground level, floors, gardens, basements, storage areas, or buried among practical everyday items. |
| **Air** (Gemini, Libra, Aquarius) | West | Elevated locations, high shelves, attics, upstairs rooms, near windows, or areas with significant airflow. |
| **Water** (Cancer, Scorpio, Pisces) | North | Near water sources, plumbing, bathrooms, kitchens, laundry areas, or damp environments. |

Table 3: The Spatial Direction Matrix utilized by the Lost Object module to output physical search locations.22

Furthermore, the engine evaluates planetary significators to provide object context. If Venus is the significator, the engine suggests looking near cosmetics, jewelry, or in the bedroom. If Mercury is the significator, it suggests looking near books, documents, or communication devices. If Saturn is involved, the engine outputs that the object is in a neglected, dark, or dusty location.22 If the significating planet is in retrograde motion, the engine applies a modifier suggesting the object is in a place the querent has already searched, or that it will be returned via an unexpected, convoluted path.30

### **The Medical Diagnostic Algorithm**

For queries regarding physical health, disease diagnosis, and survivability, the engine relies heavily on the axioms laid out in Chapters 13 through 15 of the *Prashna Marga*.7 The medical module forces the computational engine to pivot its structural focus toward the Dusthanas, or the houses of suffering. The engine evaluates the 6th House as the primary locus of acute pathogenesis and immediate illness, the 8th House as the governor of chronic, terminal, or systemic failures, and the 1st House as the metric of the patient's baseline vitality and immune response.34

To output a specific medical diagnosis, the engine executes an Anatomical Mapping Matrix. The twelve houses of the chart are directly correlated to the physical human body from head to toe.33

| House Assignment | Anatomical Zone Governed |
| :---- | :---- |
| 1st House | Head, Brain, Cranium |
| 2nd House | Face, Eyes, Throat, Oral Cavity |
| 3rd House | Shoulders, Arms, Nervous System |
| 4th House | Chest, Lungs, Heart |
| 5th House | Upper Stomach, Liver, Spleen |
| 6th House | Lower Stomach, Intestines, Kidneys |
| 7th House | Groin, Pelvic Region |
| 8th House | Reproductive Organs, Excretory System |
| 9th House | Thighs, Hips |
| 10th House | Knees, Joints |
| 11th House | Calves, Ankles |
| 12th House | Feet, Lymphatic System |

Table 4: The Anatomical Mapping Matrix for determining the locus of physical disease.33

The engine scans the entire house array to identify the house containing the most severe malefic afflictions—specifically looking for the presence of the 6th Lord, or the natural malefics Mars, Saturn, Rahu, and Ketu. The house sustaining the heaviest mathematical affliction is outputted as the primary anatomical zone of the disease.35 For instance, if Saturn and Rahu are conjunct in the 4th house, the engine outputs a high probability of severe pulmonary or cardiac distress.

Additionally, the engine evaluates the Tridosha (Ayurvedic humoral theory) by analyzing the element of the afflicted signs and planets. An afflicted Sun or Mars indicates Pitta (bile/inflammation) disorders; an afflicted Moon or Venus indicates Kapha (phlegm/water) disorders; and an afflicted Saturn or Mercury indicates Vata (wind/nervous) disorders.37 If the 1st Lord (vitality) is in an Ithasala Yoga with the 8th Lord (death) without any benefic intervention, the engine calculates a critically low survivability rate.39

### **The Legal and Litigation Algorithm**

Legal outcomes are structurally framed by the engine as a zero-sum, adversarial conflict between the 1st House, representing the querent, and the 7th House, representing the opponent or the opposing counsel.40 This binary conflict is mediated by the 6th House, which universally represents litigation, courts, and active enemies.40

The engine evaluates the relative Panchavargeeya Bala (strength) of the 1st Lord versus the 7th Lord. The algorithm's baseline logic dictates: IF (Strength(1st Lord) \> Strength(7th Lord)) AND (1st Lord occupies an Angular House), THEN Querent Wins.41 However, the 6th House introduces severe modifiers. If the 6th Lord is situated in any of the Kendra (angular) houses—1st, 4th, 7th, or 10th—and is aspected by a malefic planet, the engine flags the query for severe, prolonged trouble from enemies, indicating that the litigation will drag on detrimentally for the querent.40 An exchange of signs (Parivartana) between the 1st Lord and the 6th Lord creates a feedback loop in the engine's logic, outputting deep entanglement in the court system and high levels of personal stress.40

### **Travel and Pregnancy Algorithms**

For queries regarding the safety of travel or the return of a missing traveler, the engine assesses the 1st House (the traveler), the 4th House (the home base), and the 7th and 9th Houses (representing the journey itself).39 A safe return is computationally validated if benefic planets (Jupiter, Venus, Moon, Mercury) occupy the 2nd, 3rd, or 5th houses, or if the Lagna Lord forms an applying Ithasala aspect with a planet located in either the Lagna or the 10th house.39 Conversely, the engine outputs a "No Return" or "Severe Delay" flag if malefic planets occupy the 7th house, or if the chart features a Fixed sign ascending under malefic aspects, mathematically anchoring the traveler in their current distant location.39

In the case of pregnancy algorithms, the engine's focus isolates to the 5th House (children) and its Lord. Confirmation of a viable pregnancy is triggered if the Moon and the Lagna Lord are conjunct in the 5th house, or if they form an Ithasala Yoga while positioned in angular houses.25 Gender prediction relies on a simple binary sign check: male signs (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius) indicate a high probability of a male child, while female signs (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces) indicate a female child.25 The engine checks for severe medical complications or miscarriage risks if malefic planets, or retrograde planets, form an Ithasala with the Moon while the Ascendant is in a movable sign.25

## **Chronological Forecasting: Timing Matrices**

Perhaps the most computationally complex task for a Prashna engine is converting spatial, geometric degrees into accurate chronological timeframes.43 The engine must implement overlapping mathematical algorithms to establish when an expected event will actually manifest in the physical world.44

### **The Modality and House Matrix**

The primary timing algorithm calculates the exact number of degrees required for the faster, applying planet to perfect its aspect with the slower, receiving planet. The formula is: Degrees\_To\_Perfection \= Absolute\_Value(Planet\_A\_Degree \- Planet\_B\_Degree).44

However, a raw degree value is useless without a temporal multiplier. This multiplier is determined by cross-referencing the Modality (Quadruplicity) of the zodiac sign and the Angularity of the astrological house occupied by the primary significators.43

| Zodiac Sign Modality | Astrological House Type | Computational Time Unit | Relative Speed |
| :---- | :---- | :---- | :---- |
| **Cardinal** (Aries, Cancer, Libra, Capricorn) | **Angular** (1st, 4th, 7th, 10th) | Minutes, Hours, or Days | Fastest |
| **Mutable** (Gemini, Virgo, Sagittarius, Pisces) | **Succedent** (2nd, 5th, 8th, 11th) | Days, Weeks, or Months | Moderate |
| **Fixed** (Taurus, Leo, Scorpio, Aquarius) | **Cadent** (3rd, 6th, 9th, 12th) | Months or Years | Slowest |

Table 5: The Matrix for converting orbital degrees into chronological time units.43

Using this matrix, if the engine calculates that the Moon is exactly 5 degrees away from a perfect trine with Jupiter, it must determine what "5" means. If the Moon is situated in a Cardinal sign (representing swift action) and an Angular house (representing immediate manifestation), the engine outputs: "The event will occur in 5 days." If the Moon is in a Mutable sign and a Succedent house, the output shifts to "5 weeks." If the Moon is locked in a Fixed sign and buried in a Cadent house, the engine outputs the maximum timeframe: "5 years".43

### **The Navamsa Elapsed Algorithm**

An alternative timing method explicitly outlined in the *Prashna Marga* derives chronological data from the mathematical subdivisions of the Navamsa.29 First, the engine determines the specific Navamsa (the D-9 division, representing a 3 degree and 20 minute slice of the zodiac) currently occupied by the Lagna Lord. Second, it consults a hardcoded database of planetary time periods established by classical astrology: The Moon represents 48 minutes (a Muhurtha), Mars represents Days, Venus represents 14 Days (a Paksha), Jupiter represents 1 Month, Mercury represents 2 Months (a Ritu), the Sun represents 6 Months (an Ayana), and Saturn represents 1 Year.29

The engine then executes the formula: Time\_To\_Event \= Navamsas\_Traversed \* Planetary\_Period. For example, if Jupiter is the Lagna Lord and it has mathematically traversed 6 Navamsas into its current sign, the engine multiplies the integer 6 by Jupiter's designated time period (1 month). The engine outputs a predicted timeframe of 6 months for the event's culmination.29

### **Retrograde Modifiers and Mook (Mute) Signs**

The raw temporal outputs generated by the Modality Matrix or the Navamsa algorithm must pass through final modifier checks before being displayed to the user. If the primary applying planet is in retrograde motion, its kinematic behavior is reversed. The engine mathematically truncates or halves the calculated timeline, indicating that the event will happen with sudden, unexpected acceleration, often catching the querent off guard.44 Conversely, if the receiving planet is retrograde, the engine applies a delay multiplier, indicating the event will stall, require rework, or force a return to a past state before completion.30

Furthermore, the engine checks for the presence of Mook, or "mute," signs. In astrological classification, the water signs—Cancer, Scorpio, and Pisces—are categorized as mute, lacking a "voice".9 Computationally, when the primary significators fall into these mute signs, the engine adds a "Hidden Variable" or "Delay" flag to the output. This suggests to the user that the timing will take significantly longer than the raw mathematics imply due to uncommunicated factors, deliberate secrecy, or a fundamental lack of transparency surrounding the issue.

## **Ashta Mangala Prashna and Devaprasna**

The standard computational framework handles individual human queries efficiently, but the engine must possess the architecture to handle macro-level organizational queries and hyper-complex spiritual diagnostics. The *Ashta Mangala Prashna* and *Devaprasna* represent the apex of horary complexity, originating from the highly secretive traditions of Kerala, India.

### **Mathematical Divination via the 108-Square Board**

The Ashta Mangala system incorporates deep mathematical randomness and external physical divination into the chart-casting process.46 While traditional astrologers use a physical 108-square board representing the 108 Navamsas of the zodiac, and 108 sanctified cowrie shells, a software engine simulates this through modulo arithmetic and random number generation based on user input.14

The physical process involves the astrologer meditating and arbitrarily dividing the 108 cowrie shells into three distinct piles, representing the Past, Present, and Future.46 The engine mathematically simulates this sorting process using a modulo operator.

1. The user inputs the estimated number of shells in Pile 1 (Left). The engine computes: Remainder\_1 \= Pile\_1\_Count % 8\. If the remainder is exactly 0, the engine sets it to 8\.46  
2. The process is repeated for Pile 2 (Center) to calculate Remainder\_2.  
3. The process is repeated for Pile 3 (Right) to calculate Remainder\_3.

This sequence generates a discrete 3-digit numerical array (e.g., ), where no single digit can exceed the number 8\.48 The engine then parses this array using two distinct lookup tables. First, the numbers map to planets: 1=Sun, 2=Mars, 3=Jupiter, 4=Mercury, 5=Venus, 6=Saturn, 7=Moon, 8=Rahu.48 Second, the numbers undergo a boolean evaluation where Odd numbers equal Good (Benefic outcomes) and Even numbers equal Bad (Malefic outcomes).46 If the generated array is , the engine computationally interprets this sequence as a chronological trajectory from a highly malefic, restrictive past (8 \= Even/Rahu), transitioning into a benefic, expansive present (3 \= Odd/Jupiter), leading toward a highly successful, radiant future (1 \= Odd/Sun).48

The system also integrates the Tambula (Betel Leaf) Lagna. The querent presents a random number of betel leaves, which the engine accepts as the variable ![][image1].49 The engine processes this through a strict formula: Tambula\_Lagna \= (T \* 10 \+ 1\) % 7\.49 The resulting integer maps to the Vedic planetary week order (1=Sun, 2=Moon, 3=Mars, 4=Mercury, 5=Jupiter, 6=Venus, 0/7=Saturn). If ![][image2], the formula evaluates to ![][image3], yielding a remainder of 3\. The integer 3 maps to Mars. The engine locates the current zodiacal position of Mars in the chart, and that sign immediately overrides the temporal ascendant to become the fixed Tambula Lagna for the entire reading.49

### **Devaprasna: Organizational and Institutional Modifications**

When a Prashna is cast for an entire organization, a corporation, or specifically a deity and its temple structure (Devaprasna), the baseline semantic mapping of the astrological houses used for individual human queries must be completely overridden by the engine.48 The 1st House no longer represents a flesh-and-blood querent.

The software must dynamically swap its standard house dictionary for the Devaprasna institutional dictionary 48:

* **1st House:** The core corporate institution, the physical temple building, or the presiding deity/murti itself.  
* **2nd House:** Institutional wealth, temple treasures, bank accounts, liquid assets, and security guardians.  
* **3rd House:** Lower-level employees, servants, maintenance staff, and daily operational offerings (naivedya).  
* **4th House:** Real estate holdings, organizational buildings, surrounding lands, and corporate vehicles.  
* **6th House:** Institutional pollution, internal enemies, systemic corruption, and thieves.  
* **8th House:** Structural decay, severe existential threats, and the balance of overall good and evil matters.  
* **10th House:** Public reputation, administrative leadership, grand festivals, and overarching authority.

In standard human Prashna, the 6th and 8th houses evaluate individual illness or death. In Devaprasna, the engine places immense computational weight on these specific houses to detect systemic organizational decay, internal embezzlement, or external existential threats to the institution's survival.48 Divinatory rituals utilized during Devaprasna, such as the placement of a gold coin (Swarna Lagna) on a drawn Zodiac matrix by an uninitiated child, are mathematically encoded into the engine just as the Tambula Lagna is, assigning an overriding locational focal point that dictates the absolute truth of the institution's current health, superseding all standard astronomical ascendants.48

## **The Master Algorithmic Decision Tree**

To successfully construct and deploy this expert-level computational astrology engine, the software architecture must follow a strict, deterministic routing matrix. This pipeline ensures that every query—whether generated by time, numbers, phonemes, or physical omens—is processed through the correct domain logic and Tajika aspectual evaluation to yield a highly accurate, structured output.

**Phase 1: Initialization and Spatial-Temporal Processing**

1. The engine receives the Timestamp (in UTC) and the exact Geolocation (Latitude/Longitude).  
2. The engine applies the Lahiri Ayanamsa modifier to calculate precise sidereal planetary longitudes and orbital speeds.  
3. The engine casts the Udaya Lagna (Astronomical Ascendant) and generates the baseline 12-house geometric array.

**Phase 2: Prashna Vector Derivation and Override**

1. The engine calculates the Arudha Lagna via the spatial displacement modulo formula of the Lagna Lord.  
2. *Conditional Override:* If the user inputs a numerical seed (1-108 or KP 1-249), the engine bypasses the Udaya Lagna and recalculates the entire chart based on the mathematical integer mapping.  
3. *Conditional Override:* If the user provides phonetic input, the engine consults the Aksharachakra matrix, mapping the first phoneme to establish an alternate acoustic Ascendant.

**Phase 3: Role Assignment and Significator Identification**

1. The engine assigns the Querent\_Significator variable to the Lord of the 1st House and the Moon.  
2. The engine parses the user's intent to determine the Query Category (e.g., Medical \= 6th House, Legal \= 7th House, Lost Object \= 2nd/4th House).  
3. The engine assigns the Quesited\_Significator variable to the Lord of the respective category house.

**Phase 4: Tajika Boolean Evaluation (The YES / NO Gate)**

1. The engine calculates the kinematic speeds and applies the Deeptamsha (orbital radii) to the Querent\_Significator and Quesited\_Significator.  
2. The engine evaluates the aspectual status:  
   * IF Ithasala \== TRUE: The engine sets Outcome \= SUCCESS and proceeds to Phase 6 (Timing).  
   * IF Ishrafa \== TRUE: The engine sets Outcome \= FAILURE / PAST EVENT and halts execution, outputting a negative response to the user.  
   * IF Nakta \== TRUE: The engine sets Outcome \= SUCCESS\_VIA\_INTERMEDIARY and proceeds to Phase 6\.

**Phase 5: Domain-Specific Subroutine Execution**

* **If Query is "Lost Object":** The engine executes the Spatial Direction Matrix. It maps the elemental nature of the 2nd Lord to output a compass direction (e.g., Fire \= East) and environmental clues.  
* **If Query is "Medical":** The engine executes the Anatomical Mapping Matrix. It identifies the most mathematically afflicted house and outputs the corresponding anatomical zone (e.g., 4th House \= Chest/Lungs).  
* **If Mode is "Devaprasna":** The engine purges the standard personal house dictionary and loads the Institutional house dictionary, running deep diagnostic checks on the 6th (corruption) and 8th (decay) houses.

**Phase 6: Chronological Timing Calculation**

1. The engine calculates the absolute Delta\_Degrees between the applying and receiving significators.  
2. The engine identifies the Modality (Cardinal, Fixed, Mutable) and Angularity (Angle, Succedent, Cadent) of the primary moving planet.  
3. The engine cross-references the Time Matrix to extract the base temporal unit (Days, Months, Years).  
4. The engine applies modifying multipliers: halving the time if the planet is retrograde, or applying a delay flag if the significators occupy Mook (mute) water signs.

**Phase 7: Final Output Generation**

The engine aggregates the data from all parallel subroutines and logic gates to generate a structured JSON object or a human-readable professional report. The final output definitively answers the user's inquiry, formatted as:

{ "Outcome": "YES", "Timeframe": "5 Weeks", "Search\_Direction": "West", "Anatomical\_Risk": "None", "Confidence\_Score": 0.85 }.

By formalizing the heuristic and qualitative axioms of the *Prashna Marga* and *Tajika Neelakanthi* into strict computational logic gates, modulo arithmetic, and kinematic spatial-temporal rules, an astrology engine can successfully map the subjective, esoteric human query to an objective, measurable astronomical matrix. This framework effectively transitions horary astrology from an intuitive art form into a replicable, robust computational science.

#### **Works cited**

1. Prashna Kundali Basics: Complete Beginner's Guide \- AstroSight, accessed on March 3, 2026, [https://astrosight.ai/prashna/prashna-kundali-basics](https://astrosight.ai/prashna/prashna-kundali-basics)  
2. How to Create a Prashna Chart: Step-by-Step Guide \- AstroSight, accessed on March 3, 2026, [https://astrosight.ai/prashna/how-to-create-prashna-chart](https://astrosight.ai/prashna/how-to-create-prashna-chart)  
3. Prashna Kundli | Instant Answers with Horary Astrology | Online Jyotish, accessed on March 3, 2026, [https://www.onlinejyotish.com/horo/prashna-jyotish.php](https://www.onlinejyotish.com/horo/prashna-jyotish.php)  
4. Introduction to Varshapal / Tajik Astrology | JYOTHISHI, accessed on March 3, 2026, [https://vijayalur.com/2016/01/21/introduction-to-varshapal-tajik-astrology/](https://vijayalur.com/2016/01/21/introduction-to-varshapal-tajik-astrology/)  
5. Tajik Notes | PDF | Planets In Astrology | Horoscope \- Scribd, accessed on March 3, 2026, [https://www.scribd.com/document/927893631/Tajik-Notes](https://www.scribd.com/document/927893631/Tajik-Notes)  
6. Marriage Prashna | PDF | Occult | Astrology \- Scribd, accessed on March 3, 2026, [https://www.scribd.com/document/121822272/Marriage-Prashna](https://www.scribd.com/document/121822272/Marriage-Prashna)  
7. PRASNA MARGA \- WordPress.com, accessed on March 3, 2026, [https://astrofoxx.files.wordpress.com/2018/11/prasna-marga-1.pdf](https://astrofoxx.files.wordpress.com/2018/11/prasna-marga-1.pdf)  
8. Prasna Marga \- Wikipedia, accessed on March 3, 2026, [https://en.wikipedia.org/wiki/Prasna\_Marga](https://en.wikipedia.org/wiki/Prasna_Marga)  
9. MOOK PRASNA SERIES., accessed on March 3, 2026, [https://www.planet9.co/category/mook-prasna-series/](https://www.planet9.co/category/mook-prasna-series/)  
10. Arudha Lagna in Prashna Charts: Complete Guide \- AstroSight, accessed on March 3, 2026, [https://astrosight.ai/prashna/interpreting-arudha-lagna-prashna-chart](https://astrosight.ai/prashna/interpreting-arudha-lagna-prashna-chart)  
11. Praśna IV: Use of prasna arudha \- Varahamihira, accessed on March 3, 2026, [http://varahamihira.blogspot.com/2008/01/prana-iv-use-of-prasna-arudha.html](http://varahamihira.blogspot.com/2008/01/prana-iv-use-of-prasna-arudha.html)  
12. “108 – The Ultimate Vedic Number” – an article written by Vishal Aksh, accessed on March 3, 2026, [https://horoanalysis.wordpress.com/2018/06/08/108-the-ultimate-vedic-number-an-article-written-by-vishal-aksh/](https://horoanalysis.wordpress.com/2018/06/08/108-the-ultimate-vedic-number-an-article-written-by-vishal-aksh/)  
13. Features of Jagannatha Hora Software \- Vedic Astrology, accessed on March 3, 2026, [https://www.vedicastrologer.org/jh/features.htm](https://www.vedicastrologer.org/jh/features.htm)  
14. Navamsa (D-9) Chart | PDF | Astrological Sign \- Scribd, accessed on March 3, 2026, [https://www.scribd.com/document/895210023/Navamsa-D-9-Chart](https://www.scribd.com/document/895210023/Navamsa-D-9-Chart)  
15. Importance of 108 \- Freedom Vidya, accessed on March 3, 2026, [https://shrifreedom.org/yoga/importance-of-108/](https://shrifreedom.org/yoga/importance-of-108/)  
16. Prashna (Question based chart) \- Parashara's Light, accessed on March 3, 2026, [https://parasharaslight.com/parasharas-light/prashna-question-based-chart/](https://parasharaslight.com/parasharas-light/prashna-question-based-chart/)  
17. Zodiac Signs in Sanskrit Explained | PDF \- Scribd, accessed on March 3, 2026, [https://www.scribd.com/document/470526328/Horasara-of-Pthuyasas-Chapter-One-Divi-pdf](https://www.scribd.com/document/470526328/Horasara-of-Pthuyasas-Chapter-One-Divi-pdf)  
18. Prashna (Encyclopedia of Vedic Astrology) | Exotic India Art, accessed on March 3, 2026, [https://www.exoticindiaart.com/book/details/prashna-encyclopedia-of-vedic-astrology-idk728/](https://www.exoticindiaart.com/book/details/prashna-encyclopedia-of-vedic-astrology-idk728/)  
19. Phonemic Awareness Guidance \- Understanding the Science of Reading, accessed on March 3, 2026, [https://understandingreading.home.blog/wp-content/uploads/2021/11/phonemic-awareness-guidance.pdf](https://understandingreading.home.blog/wp-content/uploads/2021/11/phonemic-awareness-guidance.pdf)  
20. Vowels and consonants | Learn Sanskrit Online, accessed on March 3, 2026, [https://www.learnsanskrit.org/guide/devanagari/vowels-and-consonants/](https://www.learnsanskrit.org/guide/devanagari/vowels-and-consonants/)  
21. Ashtamangala Deva Prasna Specialized System of Prashna From Kerala 2 \- Vedic Astrologer Shyamasundara Dasa, accessed on March 3, 2026, [https://shyamasundaradasa.com/jyotish/resources/articles/adp/ashtamangala\_deva\_prasna\_2.html](https://shyamasundaradasa.com/jyotish/resources/articles/adp/ashtamangala_deva_prasna_2.html)  
22. Prashna Shastra for Lost Objects: Ancient Methods \- AstroSight, accessed on March 3, 2026, [https://astrosight.ai/prashna/prashna-shastra-lost-objects](https://astrosight.ai/prashna/prashna-shastra-lost-objects)  
23. Prashna Shastra | JYOTHISHI, accessed on March 3, 2026, [https://vijayalur.com/2011/08/11/prashna-shastra/](https://vijayalur.com/2011/08/11/prashna-shastra/)  
24. Ithasala Yoga in Prashna: Key to Horary Success \- AstroSight, accessed on March 3, 2026, [https://astrosight.ai/prashna/ithasala-yoga-in-prashna-astrology](https://astrosight.ai/prashna/ithasala-yoga-in-prashna-astrology)  
25. Tajika System of Prashna \- Astrology-Videos.com, accessed on March 3, 2026, [https://astrology-videos.com/CourseMaterials/TajikaSystemofPrashna.pdf](https://astrology-videos.com/CourseMaterials/TajikaSystemofPrashna.pdf)  
26. Tajik Yogas in Prasna Shastra \- Medium, accessed on March 3, 2026, [https://medium.com/prasna-jyotish/tajik-yogas-in-prasna-shastra-97e3afec652c](https://medium.com/prasna-jyotish/tajik-yogas-in-prasna-shastra-97e3afec652c)  
27. Encyclopedia of Vedic Astrology: Tajik Shastra and Annual Horoscopy: Tajika Yogas, Chapter IV, Part \- 4 \- Tag-to-Adawal, accessed on March 3, 2026, [http://tagtoadawal.blogspot.com/2013/01/encyclopedia-of-vedic-astrology-tajik\_6729.html](http://tagtoadawal.blogspot.com/2013/01/encyclopedia-of-vedic-astrology-tajik_6729.html)  
28. Prashna Kundali Analysis: Complete Interpretation Guide \- AstroSight, accessed on March 3, 2026, [https://astrosight.ai/prashna/prashna-kundali-analysis-guide](https://astrosight.ai/prashna/prashna-kundali-analysis-guide)  
29. Prasna Timing Methods: From Prasna Marga | by Varaha Mihira | Thoughts on Jyotish | Medium, accessed on March 3, 2026, [https://medium.com/thoughts-on-jyotish/prasna-timing-methods-from-prasna-marga-bf7923f22a4f](https://medium.com/thoughts-on-jyotish/prasna-timing-methods-from-prasna-marga-bf7923f22a4f)  
30. Prashna Kundali for Finding Lost Objects Guide \- AstroSight, accessed on March 3, 2026, [https://astrosight.ai/prashna/prashna-kundali-lost-objects](https://astrosight.ai/prashna/prashna-kundali-lost-objects)  
31. Prashna for lost articles | JYOTHISHI, accessed on March 3, 2026, [https://vijayalur.com/2014/11/13/prashna-for-lost-articles/](https://vijayalur.com/2014/11/13/prashna-for-lost-articles/)  
32. Rules to Find Lost Things Part \- 2 (Prashna Made Easy) by Vinayak Bhatt \- YouTube, accessed on March 3, 2026, [https://www.youtube.com/watch?v=J114TlrD1W4](https://www.youtube.com/watch?v=J114TlrD1W4)  
33. Full text of "Prasna Marga \- Dr. BV Raman" \- Archive.org, accessed on March 3, 2026, [https://archive.org/stream/PrasnaMargaBVR/Prasna%20Marga%201\_djvu.txt](https://archive.org/stream/PrasnaMargaBVR/Prasna%20Marga%201_djvu.txt)  
34. Medical Astrology – Important Planetary Combinations for Health in Horoscope, accessed on March 3, 2026, [https://www.astroshastra.com/articles/medical.php](https://www.astroshastra.com/articles/medical.php)  
35. How to Diagnose the health problem in Prashna | Saptarishis Astrology Magazine, accessed on March 3, 2026, [https://www.youtube.com/watch?v=ax\_D0EMs3hU](https://www.youtube.com/watch?v=ax_D0EMs3hU)  
36. Consideration of Disease Through Prashna Kundali: Planets Related To Diseases | PDF | Hindu Astrology \- Scribd, accessed on March 3, 2026, [https://it.scribd.com/document/373375390/Prashna-Astrology](https://it.scribd.com/document/373375390/Prashna-Astrology)  
37. MEDICAL ASTROLOGY .. \- Curofy, accessed on March 3, 2026, [https://media.curofy.com/pdfuploaduser/bwEPd8nWMcSLx95yC2M9HQ.pdf](https://media.curofy.com/pdfuploaduser/bwEPd8nWMcSLx95yC2M9HQ.pdf)  
38. Jyotish \- Advanced Medical Astrology \- Chatterjee | PDF | Poliomyelitis | Vaccines \- Scribd, accessed on March 3, 2026, [https://www.scribd.com/document/251301841/Jyotish-Advanced-Medical-Astrology-Chatterjee](https://www.scribd.com/document/251301841/Jyotish-Advanced-Medical-Astrology-Chatterjee)  
39. Prasna Notes | PDF | Superstitions | Occult \- Scribd, accessed on March 3, 2026, [https://www.scribd.com/document/253695125/Prasna-Notes](https://www.scribd.com/document/253695125/Prasna-Notes)  
40. astrological yoga's for troubles from court cases and litigation \- Sachin Malhotra, accessed on March 3, 2026, [https://astrologicalmusings.com/astrological-yogas-for-trouble-from-court-cases-and-litigation/](https://astrologicalmusings.com/astrological-yogas-for-trouble-from-court-cases-and-litigation/)  
41. Prashna Astrology for Property Dispute Resolution \- AstroSight, accessed on March 3, 2026, [https://astrosight.ai/prashna/prashna-for-property-disputes](https://astrosight.ai/prashna/prashna-for-property-disputes)  
42. Prashna of Lost Person / Traveller | JYOTHISHI, accessed on March 3, 2026, [https://vijayalur.com/2014/09/22/prashna-of-lost-person-traveller-2/](https://vijayalur.com/2014/09/22/prashna-of-lost-person-traveller-2/)  
43. Timing — Medieval Astrology Guide, accessed on March 3, 2026, [https://www.medievalastrologyguide.com/timing](https://www.medievalastrologyguide.com/timing)  
44. Establishing Time in Horary Astrology | PDF \- Scribd, accessed on March 3, 2026, [https://www.scribd.com/document/922213002/Establishing-Time-in-Horary-Astrology](https://www.scribd.com/document/922213002/Establishing-Time-in-Horary-Astrology)  
45. Prashna Shastra: Scientific Applications of Horary Astrology (Set of 2 Volumes), accessed on March 3, 2026, [https://www.exoticindiaart.com/book/details/prashna-shastra-scientific-applications-of-horary-astrology-set-of-2-volumes-nam115/](https://www.exoticindiaart.com/book/details/prashna-shastra-scientific-applications-of-horary-astrology-set-of-2-volumes-nam115/)  
46. Ashtamangala prasnam \- Wikipedia, accessed on March 3, 2026, [https://en.wikipedia.org/wiki/Ashtamangala\_prasnam](https://en.wikipedia.org/wiki/Ashtamangala_prasnam)  
47. Prashna Mangala Ashta | PDF | Hindu Astrology \- Scribd, accessed on March 3, 2026, [https://www.scribd.com/document/618349499/Prashna-mangala-ashta](https://www.scribd.com/document/618349499/Prashna-mangala-ashta)  
48. Ashtamangala Deva Prasna Specialized System of Prashna From ..., accessed on March 3, 2026, [https://shyamasundaradasa.com/jyotish/resources/articles/adp/ashtamangala\_deva\_prasna\_3.html](https://shyamasundaradasa.com/jyotish/resources/articles/adp/ashtamangala_deva_prasna_3.html)  
49. Ashtamangala Deva Prasna Specialized System of Prashna From ..., accessed on March 3, 2026, [https://shyamasundaradasa.com/jyotish/resources/articles/adp/ashtamangala\_deva\_prasna\_4.html](https://shyamasundaradasa.com/jyotish/resources/articles/adp/ashtamangala_deva_prasna_4.html)  
50. Ashtamangala Prasnam in Vedic Astrology | PDF \- Scribd, accessed on March 3, 2026, [https://www.scribd.com/document/294869382/Gopalakrishnasharma-blogspot-in-astrology-and-Your-Life](https://www.scribd.com/document/294869382/Gopalakrishnasharma-blogspot-in-astrology-and-Your-Life)  
51. Deva Prasna \- Guru Parampara, accessed on March 3, 2026, [https://www.astroguruparampara.com/services/deva-prasna](https://www.astroguruparampara.com/services/deva-prasna)  
52. How Do You Know The Will of Deity \- Explained by Rajarshi Nandy \#devaprasna \- YouTube, accessed on March 3, 2026, [https://www.youtube.com/watch?v=c9mAKRNMDHE](https://www.youtube.com/watch?v=c9mAKRNMDHE)  
53. ashtamangala deva prasna 3 \- Bhaktivedanta College, accessed on March 3, 2026, [https://www.bhaktivedantacollege.org/bvc\_site/resources\_services/articles/jyotish/adp/ashtamangala\_deva\_prasna\_3.html](https://www.bhaktivedantacollege.org/bvc_site/resources_services/articles/jyotish/adp/ashtamangala_deva_prasna_3.html)  
54. Deva Prashna \- Jyothisha kalalayam, accessed on March 3, 2026, [https://www.jyothishakalalayam.net/devaprashna.php](https://www.jyothishakalalayam.net/devaprashna.php)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAZCAYAAAABmx/yAAAAtklEQVR4XmNgGDnAEIi7SMBwcByItyILAEEPEN8BYgMksSQg/ozEZzgPxBpIfAEGiEEgDGLDgAIQn4VxhIHYFC4FAd5A/B+IQ9DEQbbvhHHsgZgPIQcGzQwQjcjOBAF3IF6NJoYCLjNANDKiSxACoAAAaSQJ8DBANO1FlyAEFBggGmehiRMElUD8BIgt0CXwAQUgPgfEC4GYA1UKP3BhgARMProENsDJAPETNgyKFjWE0lEw3AAAce8my0p3etcAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADEAAAAZCAYAAACYY8ZHAAABjUlEQVR4Xu2WPUsEMRCGR0QQv8VCLJQVxFotRG0Ez8IfYCdYWQgKNlpY+gGKrbXWithY6w+wsbESFMTGwkbwB+j7Jhc2N7t3LsLurZAHHridJJDsTOZWJBAIpDEOj+BJRqftssLphYOwSw+QO3gPW7zYIvyGB16sB17DCS9WBFPwEHbDVrgCv+CGP+kJzvoBsCt24pKKr4t9G0XRDs/gXvU3YSb4gp/dpD644B6qRPABXkkydVvqOW+Y/Rv4Aee9OA9BDTNwIB4zsJSYBWbDh+V2qmJFMAorEpc7y4oHeHUT0mAGOClS8TLQDy/F3s2GZc1S4iE69EAG5iTZzRq5LLUNpR4jcB++wReJ70ddeACWU1kZFru/Yz3gcDef2Sgz7kWnZpEtlRP0pW4WnXBNks2H7ZX7nFRxkwVeamYhqh3KTJvYC5fV32r7Quxmdbt3LXbIixn4+fEoduFfLnUebIvd7KqKu0OYcuLfuAukuWnXNJUx+Alv4Tl8l/gz5F/BKtkR25Z1VgKBQCCQDz/yKFHQDZVyQQAAAABJRU5ErkJggg==>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFcAAAAXCAYAAAB+kNMAAAADVklEQVR4Xu2Z34tNURTHl6Lkd4QIM15IKJTiSUmUxoNSHsSDPAjx4keTFxFJJEnkgZSixIMoCXMlIUVSvFDyqqT8AaxP++w7e9bd5+xzZ64z5nY/9e3O/p599j1n7XXW3veMSIcOHTokGaO6pZpkD7QRt1VnrVmCk6pR1iwLJ+5VzbcHlLGqmaqpUvwFE1SLVJPtgWGA6+S6LXNVz8UlUlmmqdYG7SOqxUE7yR3VA2uKm+mF2d8M+DLzwuz2F7wma/t+y+s9qmGL6pTql+qPatnAw3UI+gvVHHsgApN03ng/xI0f0++gXx3MndZUfqq6g/Y+cYPw6eExwwthpq9LPHuK2KrqtWZJ3qhqqnNSHFzgfg9aM0KXqs94NqChSLwBrFRdVY22B8SdcCJob8i8G4FHm0wNoUTYc8vApF2wZpP4BCgKLtkYzTID9xkmEpm8I2h7Vqh6rAmcHA4Qsks1PmgfEHfhftaZENqUlRDvN8xkgqqCSwmhT4qauHXEM076y5+HEsl9NiQnxfqpaok9EGG/uNkOB2ehiwUX8D9aM0FVwZ2tept95kHQmIQUn1SrrQkLxAWAIOWxR3VN3EJxxRxLBfeLNRNUFVyfVEV9KJdd1jSwg7okkawFspDVjxqZgu3LGdUTcTsEGKnB5X65ZtaQGDPEBb+I6eJi0W38On6BKhNcYMbp7xeDKVk7L7ivrZnBpGxUbTK6qLob8VFZWhFcsjG1GNOH78nd+7MX/Srx4HLSMePRjwERsNWKBdcvaA+Nn+J/ydyaapU1Da+kPw5RfGHvNj7slsaL9GUg3MZQVt4FbSDD6bPZ+CmqCi73wVPFmmMhYRgjRZhkUSaq7kn81xQFnQCFWY3HgNQaDxlg94z06xNXu5qhquD6hZwksLD1CrdfeSSDC2w38uoL/nvVZdUHcYP5n8Mh61WfVUfFZcR3KahFBQwluCye/oZDxcbz+3UL26/71syhVHC7xNVGFqcY28TtEg5JcTb4fnzyRAyGoQS3GW5KfA/un7gyHFZtt2YMZp3XasMNj+k8a/4DvokLpOWRDHwD1hKOS/N70pEKr1VPS3zj/1iaXydKsVTcO93B1MqRQo807mw8sySezS2D97JcQLvyTPIDuE7a+78w7cFfgGvHfjyFQ0UAAAAASUVORK5CYII=>