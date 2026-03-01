# **Computational Architecture of the Nakshatra Knowledge Base for Algorithmic Vedic Astrology**

The computational modeling of Vedic astrology requires a transition from qualitative, interpretive horoscopy into a deterministic, algorithmic framework based on strict astronomical geometries and mathematical array lookups. To engineer a robust astrological engine, the foundational celestial data must be codified into absolute sidereal longitudes, relational matrices, and exact orbital fractions. The zodiac, comprising 360 degrees of the ecliptic, is subdivided into 27 lunar mansions (Nakshatras), each spanning an exact longitudinal arc of 13 degrees and 20 minutes (800 arc-minutes). These are further fractionalized into 108 quarters (Padas) of 3 degrees and 20 minutes (200 arc-minutes), mapping directly to the Navamsa (D9) harmonic divisional chart.1

This report provides the exhaustive computational logic, hardcoded datasets, and Boolean evaluation rules necessary for a Nakshatra-based astrological engine. The architecture synthesizes classical frameworks from the Brihat Parashara Hora Shastra (BPHS), Muhurta Chintamani, and the Taittiriya Brahmana, integrating them with modern matrix-based compatibility indexing (Ashtakoota) and transit (Gochara) raycasting methodologies.4 Every logic gate and algorithm is explicitly defined to facilitate seamless integration into a programmatic backend.

## **SECTION 1: ALL 27 NAKSHATRA FULL DATA STRUCTURE**

The core database of the astrological engine relies on a 27-index array. Each index corresponds to a specific lunar mansion, bounded by absolute sidereal longitudes starting from 0°00'00" Aries. The attributes associated with each Nakshatra dictate the qualitative nature of planetary bodies occupying that space. When designing the primary object relational model, the astronomical star mappings anchor the abstract longitudinal zones to physical celestial coordinates, while the qualitative variables (Guna, Dosha, Tatwa, Nature) serve as weighted modifiers for predictive algorithms.7

### **Core Astronomical and Mythological Array**

| ID | Nakshatra | Absolute Sidereal Span | Ruling Lord | Presiding Deity | Symbol | Primary Astronomical Star(s) |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 1 | Ashwini | 0°00' \- 13°20' Aries | Ketu | Ashvins | Horse's head | β, γ Arietis 7 |
| 2 | Bharani | 13°20' \- 26°40' Aries | Venus | Yama | Yoni | 35, 39, 41 Arietis 7 |
| 3 | Krittika | 26°40' Aries \- 10°00' Taurus | Sun | Agni | Knife or spear | Pleiades 7 |
| 4 | Rohini | 10°00' \- 23°20' Taurus | Moon | Brahma | Chariot / Cart | Aldebaran 7 |
| 5 | Mrigashira | 23°20' Taurus \- 6°40' Gemini | Mars | Soma | Deer's head | λ, φ Orionis 7 |
| 6 | Ardra | 6°40' \- 20°00' Gemini | Rahu | Rudra | Teardrop | Betelgeuse 7 |
| 7 | Punarvasu | 20°00' Gemini \- 3°20' Cancer | Jupiter | Aditi | Bow and quiver | Castor, Pollux 7 |
| 8 | Pushya | 3°20' \- 16°40' Cancer | Saturn | Brihaspati | Cow's udder | γ, δ, θ Cancri 7 |
| 9 | Ashlesha | 16°40' \- 30°00' Cancer | Mercury | Nagas / Sarpas | Serpent | δ, ε, η, ρ, σ Hydrae 7 |
| 10 | Magha | 0°00' \- 13°20' Leo | Ketu | Pitrs | Royal Throne | Regulus 7 |
| 11 | Purva Phalguni | 13°20' \- 26°40' Leo | Venus | Bhaga | Hammock | δ, θ Leonis 7 |
| 12 | Uttara Phalguni | 26°40' Leo \- 10°00' Virgo | Sun | Aryaman | Four legs of bed | Denebola 7 |
| 13 | Hasta | 10°00' \- 23°20' Virgo | Moon | Savitri / Surya | Hand or fist | α, β, γ, δ, ε Corvi 7 |
| 14 | Chitra | 23°20' Virgo \- 6°40' Libra | Mars | Tvastar | Bright jewel | Spica 7 |
| 15 | Swati | 6°40' \- 20°00' Libra | Rahu | Vayu | Plant shoot / Coral | Arcturus 7 |
| 16 | Vishakha | 20°00' Libra \- 3°20' Scorpio | Jupiter | Indra and Agni | Triumphal arch | α, β, γ, ι Librae 7 |
| 17 | Anuradha | 3°20' \- 16°40' Scorpio | Saturn | Mitra | Lotus | β, δ, π Scorpionis 7 |
| 18 | Jyeshtha | 16°40' \- 30°00' Scorpio | Mercury | Indra | Earring / Amulet | α, σ, τ Scorpionis 7 |
| 19 | Mula | 0°00' \- 13°20' Sagittarius | Ketu | Nirrti | Tied roots | ε, ζ, η, θ, ι Scorpionis 7 |
| 20 | Purva Ashadha | 13°20' \- 26°40' Sagittarius | Venus | Apah | Fan / Basket | δ, ε Sagittarii 7 |
| 21 | Uttara Ashadha | 26°40' Sagittarius \- 10°00' Capricorn | Sun | Visvedevas | Elephant tusk | ζ, σ Sagittarii 7 |
| 22 | Shravana | 10°00' \- 23°20' Capricorn | Moon | Vishnu | Ear / Footprints | α, β, γ Aquilae 7 |
| 23 | Dhanishta | 23°20' Capricorn \- 6°40' Aquarius | Mars | Vasus | Drum or flute | α, β, γ, δ Delphini 7 |
| 24 | Shatabhisha | 6°40' \- 20°00' Aquarius | Rahu | Varuna | Empty circle | γ Aquarii 7 |
| 25 | Purva Bhadrapada | 20°00' Aquarius \- 3°20' Pisces | Jupiter | Ajaikapada | Two-faced man | α, β Pegasi 7 |
| 26 | Uttara Bhadrapada | 3°20' \- 16°40' Pisces | Saturn | Ahirbudhnya | Water snake | γ Pegasi, α Andromedae 7 |
| 27 | Revati | 16°40' \- 30°00' Pisces | Mercury | Pushan | Fish pair | ζ Piscium 7 |

### **Computational Attributational Data**

To build out the qualitative scoring mechanics—such as dosha imbalances in medical astrology or directional auspiciousness in horary (Prashna) queries—the engine must reference the secondary dimensional properties of each Nakshatra.8 The 14 biological Yonis represent instinctual behavior and physical drive, mapping to a 0-4 point scoring system in Ashtakoota matching.12

| ID | Nakshatra | Tatwa (Element) | Dosha | Guna | Nature | Purpose | Yoni (Animal) | Direction | Body Part Ruled |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 1 | Ashwini | Earth | Vata | Sattvic | Swift | Dharma | Horse | South | Knees, Top of feet 8 |
| 2 | Bharani | Earth | Pitta | Rajasic | Fierce | Artha | Elephant | West | Head, Bottom of feet 8 |
| 3 | Krittika | Earth | Kapha | Rajasic | Mixed | Kama | Sheep | North | Waist, Hips, Crown 8 |
| 4 | Rohini | Earth | Kapha | Rajasic | Fixed | Moksha | Serpent | East | Legs, Forehead, Ankles 8 |
| 5 | Mrigashira | Earth | Pitta | Tamasic | Soft | Moksha | Serpent | South | Eyes, Eyebrows 8 |
| 6 | Ardra | Water | Vata | Tamasic | Sharp | Kama | Dog | West | Hair, Back/Front of head 8 |
| 7 | Punarvasu | Water | Vata | Sattvic | Movable | Artha | Cat | North | Fingers, Nose 8 |
| 8 | Pushya | Water | Pitta | Tamasic | Swift | Dharma | Sheep | East | Mouth, Face, Joints 8 |
| 9 | Ashlesha | Water | Kapha | Sattvic | Sharp | Dharma | Cat | South | Nails, Knuckles, Ears 8 |
| 10 | Magha | Water | Kapha | Tamasic | Fierce | Artha | Rat | West | Nose, Lip, Chin 8 |
| 11 | Purva Phalguni | Water | Pitta | Rajasic | Fierce | Kama | Rat | North | Sexual organs, R-hand 8 |
| 12 | Uttara Phalguni | Fire | Vata | Rajasic | Fixed | Moksha | Cow | East | Sexual organs, L-hand 8 |
| 13 | Hasta | Fire | Vata | Rajasic | Swift | Moksha | Buffalo | South | Hands 8 |
| 14 | Chitra | Fire | Pitta | Tamasic | Soft | Kama | Tiger | West | Forehead, Neck 8 |
| 15 | Swati | Fire | Kapha | Tamasic | Movable | Artha | Buffalo | North | Teeth, Chest, Breathing 8 |
| 16 | Vishakha | Fire | Kapha | Sattvic | Mixed | Dharma | Tiger | East | Upper limbs, Breasts 8 |
| 17 | Anuradha | Fire | Pitta | Tamasic | Soft | Dharma | Hare / Deer | South | Astral fires, Stomach, Womb 8 |
| 18 | Jyeshtha | Air | Vata | Sattvic | Sharp | Artha | Hare / Deer | West | Tongue, Neck, R-side torso 8 |
| 19 | Mula | Air | Vata | Tamasic | Fierce | Kama | Dog | North | Feet, L-side torso, Back 8 |
| 20 | Purva Ashadha | Air | Pitta | Rajasic | Fierce | Moksha | Monkey | East | Both thighs 8 |
| 21 | Uttara Ashadha | Air | Kapha | Sattvic | Fixed | Moksha | Mongoose | South | Thighs, Waist 8 |
| 22 | Shravana | Air | Kapha | Rajasic | Movable | Artha | Monkey | West | Ears, Gait, Sex organs 8 |
| 23 | Dhanishta | Air | Pitta | Tamasic | Movable | Dharma | Lion | North | Back, Anus 8 |
| 24 | Shatabhisha | Air | Vata | Tamasic | Movable | Dharma | Horse | East | Chin, Jaw, R-thigh 8 |
| 25 | Purva Bhadrapada | Ether | Vata | Sattvic | Fierce | Artha | Lion | South | Ribs, L-thigh, Soles 8 |
| 26 | Uttara Bhadrapada | Ether | Pitta | Tamasic | Fixed | Kama | Cow | West | Sides of legs, Shins 8 |
| 27 | Revati | Ether | Kapha | Sattvic | Soft | Moksha | Elephant | North | Armpits, Abdomen, Groin 8 |

### **The 108 Pada Syllable Array**

A key sub-routine of the astrological engine involves phonemic mapping. The total 108 padas (quarters) each correlate to a specific Sanskrit seed syllable (Bija Akshara). This determines the Nama Nakshatra (Naming Star) for an individual, aligning verbal resonance with celestial vibration. The engine must map absolute longitudes directly to these syllables.2

| Nakshatra | Pada 1 (0°00' \- 3°20') | Pada 2 (3°20' \- 6°40') | Pada 3 (6°40' \- 10°00') | Pada 4 (10°00' \- 13°20') |
| :---- | :---- | :---- | :---- | :---- |
| Ashwini | Chu | Che | Cho | La |
| Bharani | Li | Lu | Le | Lo |
| Krittika | A | I | U | E |
| Rohini | O | Va | Vi | Vu |
| Mrigashira | Ve | Vo | Ka | Ki |
| Ardra | Ku | Gha | Ng | Chha |
| Punarvasu | Ke | Ko | Ha | Hi |
| Pushya | Hu | He | Ho | Da |
| Ashlesha | Di | Du | De | Do |
| Magha | Ma | Mi | Mu | Me |
| Purva Phalguni | Mo | Ta | Ti | Tu |
| Uttara Phalguni | Te | To | Pa | Pi |
| Hasta | Pu | Sha | Na | Tha |
| Chitra | Pe | Po | Ra | Ri |
| Swati | Ru | Re | Ro | Ta |
| Vishakha | Ti | Tu | Te | To |
| Anuradha | Na | Ni | Nu | Ne |
| Jyeshtha | No | Ya | Yi | Yu |
| Mula | Ye | Yo | Ba | Bi |
| Purva Ashadha | Bu | Dha | Bha | Dha |
| Uttara Ashadha | Be | Bo | Ja | Ji |
| Shravana | Ju | Je | Jo | Gha |
| Dhanishta | Ga | Gi | Gu | Ge |
| Shatabhisha | Go | Sa | Si | Su |
| Purva Bhadrapada | Se | So | Da | Di |
| Uttara Bhadrapada | Du | Tha | Jna | Da |
| Revati | De | Do | Cha | Chi |

*   
  1. IF \[Absolute\_Longitude \>= 0.00\] AND \[Absolute\_Longitude \< 3.3333\] THEN.13  
*   
  2. IF \[Absolute\_Longitude \>= 3.3333\] AND \[Absolute\_Longitude \< 6.6666\] THEN.13

### **Yoni Koota Compatibility Logic Matrix**

The 14 biological animal archetypes (Yonis) evaluate physical, sexual, and instinctual compatibility. The scoring output yields an integer between 0 and 4\. A score of 0 triggers a "Yoni Dosha," indicating severe biological hostility and instinctual friction, rooted in predator-prey dynamics.12

*   
  3. IF THEN AND.12  
*   
  4. IF THEN AND.12  
*   
  5. IF THEN AND.12  
*   
  6. IF THEN AND.12  
*   
  7. IF THEN AND.12

Definitive Relational Mapping Sets 12:

*   
  8. IF THEN,.  
*   
  9. IF THEN, \[Enemy \= Lion\].  
*   
  10. IF THEN, \[Enemy \= Monkey\].  
*   
  11. IF THEN \[Friendly \= Horse, Elephant\], \[Enemy \= Mongoose\].  
*   
  12. IF THEN \[Friendly \= Cat\],.  
*   
  13. IF THEN,.  
*   
  14. IF THEN, \[Enemy \= Cat\].  
*   
  15. IF THEN,.  
*   
  16. IF THEN, \[Enemy \= Horse\].  
*   
  17. IF THEN \[Friendly \= Lion\],.  
*   
  18. IF THEN,.  
*   
  19. IF THEN \[Friendly \= Horse, Elephant, Cat, Mongoose\],.  
*   
  20. IF THEN,.  
*   
  21. IF THEN, \[Enemy \= Elephant\].

## ---

**SECTION 2: TARABALA (BIRTH STAR COMPATIBILITY WITH TRANSIT STARS)**

In the algorithmic evaluation of daily planetary transits, the engine must not view transits in a vacuum. Instead, transits are filtered through a dynamic, relative compatibility index known as Tarabala (Star Strength).15 The distance from the natal Moon Nakshatra to the current transiting Moon Nakshatra creates a 9-fold harmonic resonance (Navatara). The system requires a modulo-9 geometric evaluation across the 27-star array to assign a dynamic multiplier to the transit's base strength.15

### **Tarabala Computational Algorithm**

*   
  22. IF THEN Execute.  
*   
  23. IF THEN Execute.  
*   
  24. IF THEN.  
*   
  25. IF \[Count \<= 0\] THEN \[Count \= Count \+ 27\].  
*   
  26. IF \[Count \> 0\] THEN.  
*   
  27. IF THEN.

### **Tara Categories and Transit Effect Multipliers**

The calculated Tara\_Value (1 through 9\) governs the categorical outcome of the transit.15 This score operates as a fractional multiplier on the base confidence score of the transit's predicted effect.

*   
  28. IF THEN AND \[Nature \= Negative/Neutral\] AND.15  
*   
  29. IF THEN AND \[Nature \= Positive\] AND.15  
*   
  30. IF THEN AND \[Nature \= Negative\] AND.15  
*   
  31. IF THEN \[Category \= "Kshema (Prosperity)"\] AND \[Nature \= Positive\] AND.15  
*   
  32. IF THEN \[Category \= "Pratyak (Obstacles)"\] AND \[Nature \= Negative\] AND.15  
*   
  33. IF THEN AND \[Nature \= Positive\] AND.15  
*   
  34. IF THEN AND \[Nature \= Highly Negative\] AND.15  
*   
  35. IF THEN \[Category \= "Mitra (Friend)"\] AND \[Nature \= Positive\] AND.15  
*   
  36. IF THEN \[Category \= "Ati-Mitra (Great Friend)"\] AND \[Nature \= Highly Positive\] AND.15

## ---

**SECTION 3: CHANDRABALA (LUNAR STRENGTH SCORE)**

While Tarabala operates on a 27-base index, Chandrabala evaluates the spatial relationship between the Natal Rashi (Moon Sign) and the Transit Rashi on a 12-base modulo.15 Because the Moon represents the psychological substrate and emotional capacity to endure karmic events, Chandrabala acts as the secondary confidence layer in Muhurta (electional timing) and transit evaluation.18

### **Chandrabala Computational Algorithm**

*   
  37. IF \[Action \= Compute\_Chandrabala\] THEN Execute.  
*   
  38. IF THEN Execute.  
*   
  39. IF THEN.  
*   
  40. IF \[Lunar\_Count \<= 0\] THEN \[Lunar\_Count \= Lunar\_Count \+ 12\].

### **Monthly Score and Quality Integration**

The resulting Lunar\_Count dictates the overarching psychological endurance and material success probability for the \~2.25 day transit of the Moon through that sign.15

*   
  41. IF \[Lunar\_Count in (1, 3, 6, 7, 10, 11)\] THEN AND.15  
*   
  42. IF \[Lunar\_Count \== 8\] THEN AND.18  
*   
  43. IF \[Lunar\_Count in (2, 12)\] THEN AND.17  
*   
  44. IF \[Lunar\_Count in (4, 5, 9)\] THEN AND.  
*   
  45. IF \[Lunar\_Count \== 8\] AND THEN AND (This traditional exception occurs because the Lord of the 8th matches the Lord of the 1st, or Lord of 8th is friendly, negating the Astama dosha effect).19

## ---

**SECTION 4: NAKSHATRA DASHA SYSTEM (TIMING CYCLES)**

Static astrological geometries lack temporal activation. The Dasha systems are algorithmic progressions that function as timing engines, rotating the natal chart's potentials into chronological reality.6 The primary Nakshatra Dasha is the Vimshottari system, mapping a 120-year cycle to human longevity based on an exact longitudinal fraction of the Moon's birth position.21 Alternative systems, such as the Dwisaptati Sama Dasa (72 years), are activated conditionally.22

### **Vimshottari Dasha Computational Logic**

The cycle operates via a hardcoded planetary array. The Moon's exact elapsed percentage within its birth Nakshatra dictates the starting balance of the corresponding planetary period.6

Master\_Dasha\_Array \=.6

*   
  46. IF THEN \[Nakshatra\_Arc\_Length \= 13.333333°\].  
*   
  47. IF THEN.  
*   
  48. IF THEN \[Fraction\_Elapsed \= Longitude\_in\_Current\_Nak / 13.333333\].  
*   
  49. IF THEN.  
*   
  50. IF THEN.  
*   
  51. IF THEN.  
*   
  52. IF THEN.6

To iterate through time, the engine simply steps through the Master\_Dasha\_Array index sequentially once the Balance\_of\_First\_Dasha\_at\_Birth duration is exhausted.

### **Conditional Dwisaptati Sama Dasa (72-Year Cycle)**

The BPHS specifies conditional timing systems. The engine must check the chart conditions to override the default Vimshottari progression if specific criteria are met.22

*   
  53. IF \[Lagna Lord is in 7th House\] OR \[7th Lord is in Lagna\] THEN.22  
*   
  54. IF THEN AND (Note: Ketu is excluded as it governs this Dasha).22  
*   
  55. IF THEN.  
*   
  56. IF THEN.  
*   
  57. IF THEN.22

## ---

**SECTION 5: PADA (QUARTER) SPECIFIC RULES**

The 108 Padas represent the deepest fractal layer of the Nakshatra engine, mapping the physical 30-degree signs (D1 Rashi) into the subconscious 3°20' increments of the Navamsa (D9) chart.1 Mathematical logic governs which Navamsa sign a specific degree falls into. Further, specific intersection degrees create monumental harmonic resonance, known as Vargottama and Pushkara.24

### **Navamsa Derivation Algorithm**

The engine derives the Navamsa sign based on the physical element (Tatwa) of the overarching Rashi.3

*   
  58. IF THEN.  
*   
  59. IF THEN.  
*   
  60. IF THEN.  
*   
  61. IF THEN.3  
*   
  62. IF THEN.

### **Vargottama Pada Logic**

A planet is Vargottama when its D1 (Rashi) sign matches its D9 (Navamsa) sign. The mathematical engine evaluates the planetary longitude relative to the base sign modality to trigger this strength multiplier.25

*   
  63. IF AND THEN \[Condition \= Vargottama\] AND.25  
*   
  64. IF AND THEN \[Condition \= Vargottama\] AND.25  
*   
  65. IF AND THEN \[Condition \= Vargottama\] AND.25

### **Pushkara Navamsa and Pushkara Bhaga**

Pushkara Navamsas are highly specific, deeply nourishing zones within the zodiac that act as massive structural multipliers for benefic results, often overriding debilitation. Pushkara Bhagas are exact degrees of supreme auspiciousness.24

Pushkara Navamsa Logic Arrays 24:

*   
  66. IF AND THEN AND \[Auspiciousness\_Multiplier \= 2.0\].  
*   
  67. IF AND THEN AND \[Auspiciousness\_Multiplier \= 2.0\].  
*   
  68. IF AND THEN AND \[Auspiciousness\_Multiplier \= 2.0\].  
*   
  69. IF AND THEN AND \[Auspiciousness\_Multiplier \= 2.0\].

Pushkara Bhaga Exact Degrees 24:

*   
  70. IF THEN AND \[Auspiciousness\_Multiplier \= 3.0\].  
*   
  71. IF THEN AND \[Auspiciousness\_Multiplier \= 3.0\].  
*   
  72. IF THEN AND \[Auspiciousness\_Multiplier \= 3.0\].  
*   
  73. IF THEN AND \[Auspiciousness\_Multiplier \= 3.0\].  
*   
  74. IF \[Nakshatra\_Lord in (Ketu, Mars, Mercury)\] THEN (Pushkara Bhagas do not occur in these constellations).24

## ---

**SECTION 6: NAKSHATRA-LEVEL TRANSIT EFFECTS**

When dynamic planets traverse the absolute longitudes of the 27 Nakshatras, specific karmic domains and psychological archetypes are activated. Based on classical texts including the Taittiriya Brahmana and Jyotish Pradeepika, the engine parses transits by injecting contextual themes corresponding to the presiding deity and cosmic motivation (Purushartha).4

### **The 27 Algorithmic Karmic Activations**

*   
  75. IF \[Planet transits Ashwini\] THEN AND.27  
*   
  76. IF THEN AND.27  
*   
  77. IF \[Planet transits Krittika\] THEN AND.27  
*   
  78. IF THEN AND.10  
*   
  79. IF \[Planet transits Mrigashira\] THEN AND.10  
*   
  80. IF \[Planet transits Ardra\] THEN AND.10  
*   
  81. IF \[Planet transits Punarvasu\] THEN AND.10  
*   
  82. IF \[Planet transits Pushya\] THEN AND.10  
*   
  83. IF \[Planet transits Ashlesha\] THEN AND.10  
*   
  84. IF \[Planet transits Magha\] THEN AND.10  
*   
  85. IF \[Planet transits Purva Phalguni\] THEN AND.27  
*   
  86. IF \[Planet transits Uttara Phalguni\] THEN AND.10  
*   
  87. IF \[Planet transits Hasta\] THEN AND.10  
*   
  88. IF \[Planet transits Chitra\] THEN AND.10  
*   
  89. IF THEN AND.10  
*   
  90. IF \[Planet transits Vishakha\] THEN AND.10  
*   
  91. IF \[Planet transits Anuradha\] THEN AND.10  
*   
  92. IF \[Planet transits Jyeshtha\] THEN AND.10  
*   
  93. IF \[Planet transits Mula\] THEN AND.10  
*   
  94. IF \[Planet transits Purva Ashadha\] THEN AND.10  
*   
  95. IF \[Planet transits Uttara Ashadha\] THEN AND.10  
*   
  96. IF THEN AND.10  
*   
  97. IF THEN AND.10  
*   
  98. IF THEN AND.10  
*   
  99. IF THEN AND.10  
*   
  100. IF THEN AND.10  
*   
  101. IF THEN AND.10

### **Universal vs. Chart-Dependent Applicability**

*   
  102. IF THEN AND.24  
*   
  103. IF THEN AND.15

## ---

**SECTION 7: SARVATOBHADRA CHAKRA (SBC)**

The Sarvatobhadra Chakra (SBC) operates as the master cryptographic matrix of Vedic predictive astrology. Meaning "auspicious from all directions," the SBC is an 81-square grid (9x9) computational array. It transcends basic longitudinal conjunctions by implementing a geometric raycasting mechanic called *Vedha* (Obstruction/Influence). By cross-referencing Nakshatras, vowels, consonants, weekdays, and lunar tithis, the SBC engine provides a high-resolution, day-by-day deterministic forecast of global and personal events.30

### **SBC Grid Matrix Construction Algorithm**

The array logic requires mapping 81 discrete objects onto specific (X,Y) coordinates within the matrix.30

*   
  104. IF \[Constructing Outer Perimeter\] THEN \[Map 28 Nakshatras (including Abhijit) into the 28 border squares, indexing clockwise from the top-right North-East corner\].  
*   
  105. IF THEN.  
*   
  106. IF THEN.  
*   
  107. IF \[Constructing Core Center\] THEN.

### **Planetary Vedha (Raycasting) Algorithm**

The predictive mechanic of the SBC dictates that a transiting planet "shoots" lines of influence (Vedha) across the matrix. The trajectory of this raycast is strictly dependent on the planet's celestial mechanics (direct, accelerated, or retrograde motion).30

*   
  108. IF THEN.31  
*   
  109. IF THEN.31  
*   
  110. IF THEN.31  
*   
  111. IF OR THEN (Luminaries and nodes maintain static multi-directional vectors).31

### **Evaluating SBC Vedha Impact Matrices**

When a planet's raycast intersects a critical node in a user's chart (such as their natal Moon Nakshatra, or the starting vowel of their name), a deterministic effect is logged.30

*   
  112. IF AND THEN AND.30  
*   
  113. IF AND THEN AND \[Effect \= Unfavorable / Obstruction Created\].30  
*   
  114. IF AND THEN.31  
*   
  115. IF AND \[Planet is Malefic\] THEN \[Krura Vedha Multiplier \= 2.0\] (Retrogradation intensely magnifies the effect).31  
*   
  116. IF THEN \[Vedha Multiplier \= 0.5\].31  
*   
  117. IF AND \[Krura Vedha\] Intersect simultaneously THEN.31

### **Integration with Ashtakvarga (SAV & BAV) Scores**

To output a final algorithmic confidence score for any specific day, the engine must merge the qualitative geometric raycasts of the SBC with the quantitative mathematical point system of Ashtakvarga. Sarvashtakvarga (SAV) measures the total strength of a sign (out of 56 points, typically averaging 28), while Bhinna Ashtakvarga (BAV) measures a specific planet's point contribution (0 to 8).34

*   
  118. IF AND THEN AND.34  
*   
  119. IF AND THEN (High SAV point density absorbs and mitigates the structural obstruction of the Malefic Vedha).  
*   
  120. IF AND THEN.34  
*   
  121. IF AND THEN AND.34  
*   
  122. IF THEN (Transit is robust and constructive).34  
*   
  123. IF THEN (Transit brings challenges or delays regardless of Vedha).34

#### **Works cited**

1. Pushkara Navamsha Zones of Good Fortune \* BP Lama Jyotishavidya, accessed on February 28, 2026, [https://barbarapijan.com/bpa/Varga/D9\_Pushkara\_Navamsha\_table.htm](https://barbarapijan.com/bpa/Varga/D9_Pushkara_Navamsha_table.htm)  
2. Importance of 108 \- Freedom Vidya, accessed on February 28, 2026, [https://shrifreedom.org/yoga/importance-of-108/](https://shrifreedom.org/yoga/importance-of-108/)  
3. Nakshatra Padas Explained: Quarter Divisions Guide \- AstroSight, accessed on February 28, 2026, [https://astrosight.ai/nakshatras/nakshatra-padas-explained](https://astrosight.ai/nakshatras/nakshatra-padas-explained)  
4. Wishes Granted through Each of the 27 Nakshatras or Lunar Mansions, accessed on February 28, 2026, [https://www.vedanet.com/27-nakshatras/](https://www.vedanet.com/27-nakshatras/)  
5. Understanding Nakshatras and Karma | PDF | Hindu Astrology \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/876982770/Rashi-Grahas-Nakshatras-Karma](https://www.scribd.com/document/876982770/Rashi-Grahas-Nakshatras-Karma)  
6. Dasha in Astrology: Complete Planetary Period Guide \- AstroSight, accessed on February 28, 2026, [https://astrosight.ai/transits/dasha-in-astrology](https://astrosight.ai/transits/dasha-in-astrology)  
7. List of Nakshatras \- Wikipedia, accessed on February 28, 2026, [https://en.wikipedia.org/wiki/List\_of\_Nakshatras](https://en.wikipedia.org/wiki/List_of_Nakshatras)  
8. Nakshatras and Body parts in astrology \- Astrolight08 \- WordPress.com, accessed on February 28, 2026, [https://astrolight08.wordpress.com/2018/08/22/nakshatras-and-part-of-body-in-astrology/](https://astrolight08.wordpress.com/2018/08/22/nakshatras-and-part-of-body-in-astrology/)  
9. 27 Nakshatras : Meaning, Traits & Role in Vedic Astrology, accessed on February 28, 2026, [https://www.vinaybajrangi.com/nakshatras.php](https://www.vinaybajrangi.com/nakshatras.php)  
10. 27 Nakshatras in Vedic Astrology: Meanings and Role \- RashiRatanBhagya.Com, accessed on February 28, 2026, [https://rashiratanbhagya.com/blog/post/27-nakshatras-vedic-astrology](https://rashiratanbhagya.com/blog/post/27-nakshatras-vedic-astrology)  
11. 27 Nakshatras Characteristics Table | PDF \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/doc/169858866/27-Nakshatras-Tables](https://www.scribd.com/doc/169858866/27-Nakshatras-Tables)  
12. Yoni Koota Compatibility Check: Complete Matching Guide, accessed on February 28, 2026, [https://astrosight.ai/nakshatras/yoni-koota-compatibility-check](https://astrosight.ai/nakshatras/yoni-koota-compatibility-check)  
13. Nakshatras and Sounds Corresponding to each Nakshatra \- World Yoga Forum, accessed on February 28, 2026, [https://worldyogaforum.com/nakshatras/sounds/](https://worldyogaforum.com/nakshatras/sounds/)  
14. Yoni Koota in Marriage Matching: Complete Scoring Guide, accessed on February 28, 2026, [https://astrosight.ai/nakshatras/yoni-koota-marriage-matching](https://astrosight.ai/nakshatras/yoni-koota-marriage-matching)  
15. How to Use Tarabala and Chandrabala to Find Your Auspicious Days \- Cosmic Insights, accessed on February 28, 2026, [https://blog.cosmicinsights.net/how-to-use-tarabala-and-chandrabala-to-find-your-auspicious-days/](https://blog.cosmicinsights.net/how-to-use-tarabala-and-chandrabala-to-find-your-auspicious-days/)  
16. The Nine Tarabala \- Vic DiCara's Astrology, accessed on February 28, 2026, [https://vicdicara.blog/2023/07/18/the-nine-tarabala/](https://vicdicara.blog/2023/07/18/the-nine-tarabala/)  
17. Tarabalam and Chandrabalam Explained | PDF | Esoteric Cosmology | Astronomy \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/531511518/166228602-Tarabalam-Chandrabalam](https://www.scribd.com/document/531511518/166228602-Tarabalam-Chandrabalam)  
18. Tarabala, Chandrabala & Panchaka | JYOTHISHI, accessed on February 28, 2026, [https://vijayalur.com/2011/10/02/tarabala-chandrabala-panchaka/](https://vijayalur.com/2011/10/02/tarabala-chandrabala-panchaka/)  
19. Determining Chandrabala and Tarabala | Centre for Traditional Education, accessed on February 28, 2026, [https://www.cteindia.org/determining-chandrabala-and-tarabala/](https://www.cteindia.org/determining-chandrabala-and-tarabala/)  
20. Transits and Nakshatra Dasa Progression \- Vedic Astrology, accessed on February 28, 2026, [https://www.vedicastrologer.org/articles/pp\_dasa\_transit.pdf](https://www.vedicastrologer.org/articles/pp_dasa_transit.pdf)  
21. Vimśottari Daśā \- Sanjay Rath, accessed on February 28, 2026, [https://srath.com/jyoti%E1%B9%A3a/dasa/vimsottari-dasa/](https://srath.com/jyoti%E1%B9%A3a/dasa/vimsottari-dasa/)  
22. Dvisaptati Sama Dasa \- Sanjay Rath, accessed on February 28, 2026, [https://srath.com/jyoti%E1%B9%A3a/dasa/dvisaptati-sama-dasa/](https://srath.com/jyoti%E1%B9%A3a/dasa/dvisaptati-sama-dasa/)  
23. Dasha (astrology) \- Wikipedia, accessed on February 28, 2026, [https://en.wikipedia.org/wiki/Dasha\_(astrology)](https://en.wikipedia.org/wiki/Dasha_\(astrology\))  
24. Pushkara Navamsha and Pushkara Bhaga | JYOTHISHI, accessed on February 28, 2026, [https://vijayalur.com/2013/07/26/pushkara-navamsha-and-pushkara-bhaga/](https://vijayalur.com/2013/07/26/pushkara-navamsha-and-pushkara-bhaga/)  
25. Research on Vargotamma, Numbers & Panchamahabhuta, accessed on February 28, 2026, [https://komilla.com/lib-vargotamma-numbers-panchamahabhuta.html](https://komilla.com/lib-vargotamma-numbers-panchamahabhuta.html)  
26. Pushkara \- Navamsha and Bhaga \- Komilla | Vedic Astrology, accessed on February 28, 2026, [https://komilla.com/lib-pushkara-part-two.html](https://komilla.com/lib-pushkara-part-two.html)  
27. The Nakshatras: The 27 Lunar Mansions That Shape Our Emotions and Destiny in Vedic Astrology \- Prakash Gem Merchant, accessed on February 28, 2026, [https://www.prakashgem.com/the-nakshatras-the-27-lunar-mansions-that-shape-our-emotions-and-destiny-in-vedic-astrology/](https://www.prakashgem.com/the-nakshatras-the-27-lunar-mansions-that-shape-our-emotions-and-destiny-in-vedic-astrology/)  
28. The 27 Nakshatras | PDF | Planets In Astrology \- Scribd, accessed on February 28, 2026, [https://www.scribd.com/document/867011974/The-27-Nakshatras](https://www.scribd.com/document/867011974/The-27-Nakshatras)  
29. Understanding All 27 Nakshatras Details in Vedic Astrology \- Astropatri, accessed on February 28, 2026, [https://astropatri.com/blog/understanding-all-27-nakshatras-details-in-vedic-astrology/](https://astropatri.com/blog/understanding-all-27-nakshatras-details-in-vedic-astrology/)  
30. Sarvatobhadra Chakra \- Learning Astrology, accessed on February 28, 2026, [http://astroveda.wikidot.com/sarvatobhadra-chakra](http://astroveda.wikidot.com/sarvatobhadra-chakra)  
31. The Construction methodology of Sarvatobhadra Chakra, accessed on February 28, 2026, [https://howisyourdaytoday.com/articles/Sarvatobhadrachakra/Sarvatobhadra-chakra-construction.htm](https://howisyourdaytoday.com/articles/Sarvatobhadrachakra/Sarvatobhadra-chakra-construction.htm)  
32. Sarvatobhadra Chakra \- Wikipedia, accessed on February 28, 2026, [https://en.wikipedia.org/wiki/Sarvatobhadra\_Chakra](https://en.wikipedia.org/wiki/Sarvatobhadra_Chakra)  
33. Vedhas \- Saravali, accessed on February 28, 2026, [https://saravali.github.io/astrology/sbc\_vedhas.html](https://saravali.github.io/astrology/sbc_vedhas.html)  
34. Using Ashtakvarga for transits : r/Nakshatras \- Reddit, accessed on February 28, 2026, [https://www.reddit.com/r/Nakshatras/comments/1od3vbc/using\_ashtakvarga\_for\_transits/](https://www.reddit.com/r/Nakshatras/comments/1od3vbc/using_ashtakvarga_for_transits/)