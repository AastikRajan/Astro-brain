# Jaimini Rashi Drishti (Sign Aspects)

Jaimini’s sign-aspect rules are whole-sign in nature.  **Movable (Chara) signs** (Aries, Cancer, Libra, Capricorn) each aspect *all* fixed signs except the one adjacent to them, and **Fixed (Sthira) signs** (Taurus, Leo, Scorpio, Aquarius) each aspect *all* movable signs except the one previous to them【22†L8548-L8555】.  **Common/Dual (Dwi‑swabhava) signs** (Gemini, Virgo, Sagittarius, Pisces) mutually aspect each other (each dual sign aspects the other three dual signs)【22†L8548-L8555】.  In practice, every planet in a sign casts that sign’s Jaimini drishti. For example, a planet in Aries will Rashi-aspect Leo, Scorpio, and Aquarius (but *not* adjacent Taurus)【22†L8548-L8555】【16†L300-L307】.  Crucially, Jaimini aspects are *mutual*: if sign A aspects sign B, then a planet in B is also considered as being aspected by A【22†L8548-L8555】.  In summary (using sign names for clarity):
- **Aries** (cardinal) → aspects **Leo, Scorpio, Aquarius** (fixed)【16†L300-L307】.  
- **Taurus** (fixed) → aspects **Cancer, Libra, Capricorn** (cardinal)【16†L309-L316】.  
- **Gemini** (dual) ↔ **Virgo, Sagittarius, Pisces** (all dual)【16†L318-L323】.  
- **Cancer** (cardinal) → aspects **Taurus, Scorpio, Aquarius**【16†L300-L307】.  
- **Leo** (fixed) → aspects **Aries, Libra, Capricorn**【16†L309-L316】.  
- **Virgo** (dual) ↔ **Gemini, Sagittarius, Pisces**【16†L318-L323】.  
- **Libra** (cardinal) → aspects **Taurus, Leo, Aquarius**【16†L300-L307】.  
- **Scorpio** (fixed) → aspects **Aries, Cancer, Capricorn**【16†L309-L316】.  
- **Sagittarius** (dual) ↔ **Gemini, Virgo, Pisces**【16†L318-L323】.  
- **Capricorn** (cardinal) → aspects **Taurus, Leo, Scorpio**【16†L300-L307】.  
- **Aquarius** (fixed) → aspects **Aries, Cancer, Libra**【16†L309-L316】.  
- **Pisces** (dual) ↔ **Gemini, Virgo, Sagittarius**【16†L318-L323】.  

Each planet in a sign therefore “throws” that sign’s aspects to the target signs【22†L8548-L8555】.  These sign-aspects are treated as full-strength: in Shadbala they contribute a fixed 60 points (full aspect) to each target sign【22†L8548-L8555】【25†L83-L91】.  In other words, Jaimini drishti are not distance-dependent; if a planet’s sign aspects another sign, it counts fully (100%) as an aspect.  

When **Graha (planetary) drishti** and **Rashi drishti** both apply to the same house or chart point, both are generally counted simultaneously. Traditional sources state that Rashi-aspects are *permanent sign aspects* (a static background), while Graha-aspects modulate the planet’s desires and effects【32†L119-L123】【30†L31-L34】.  In practice, one typically adds their influences: Rashi drishti provides a general connection, and Graha drishti provides additional force or nuance.  Commentators note that Graha drishti often produces more immediate or concrete effects than Rashi drishti【30†L31-L34】【32†L119-L123】.  There is no formal hierarchy that “cancels” one by the other; both are applied, with Graha drishti usually viewed as more potent if a conflict arises【32†L119-L123】【30†L31-L34】.

**Argala vs. Rashi Drishti:**  In Jaimini astrology, *argala* is a special kind of blocking aspect created only by planets (“drashta”), not by empty-sign aspects【33†L119-L125】.  Thus a mere Rashi drishti (a sign-based aspect) does *not* itself create argala nor cancel it.  Only a planet occupying the 2nd, 4th or 11th house from the aspected chart point (per sutra) creates argala【33†L119-L125】. In short, Rashi-aspect alone is not an argala condition.

**Chara Dasha House Activation:**  In Chara Dasha (sign-based Vimshottari), when a particular sign’s period is active, that sign *and* all the houses/signs it aspects become “activated.”  In chart terms: if sign *S* (with house number *h* relative to Ascendant) is in dasha, then house *h* and the houses of S’s Jaimini-aspected signs are activated.  For example, during Aries dasha (Aries=1st house), houses **1, 5, 8, 11** (Aries itself and Leo, Scorpio, Aquarius) are emphasized【16†L300-L307】.  In general, 
```
activated_houses(S) = { house_of(S) } ∪ { house_of(T) for each sign T that S aspects }.
```  
This follows directly from the above aspect table【16†L300-L307】【22†L8548-L8555】.

**Rahu/Ketu:**  Modern practice generally treats the lunar nodes as “planets” for the sake of Jaimini drishti.  Brihat Parashara (BPHS) describes the rule in terms of “a planet in a sign”【22†L8548-L8555】, and classical commentaries include Rahu and Ketu among the grahas.  Thus nodes *do* cast sign aspects under Jaimini’s rule just like other planets.  (Some traditionalists debate this, but the BPHS framework is to include them as typical grahas for drishti.)

# 27 Nakshatra Attributes

The 27 lunar nakshatras have the following attributes:

| # | Nakshatra     | Deity              | Symbol              | Span (Sidereal °)     | Lord (Vimshottari) | Gana      | Varna       | Yoni (Animal⟋Gender)      | Nadi     | Body Part        | Guna    | Category     |
|---|---------------|--------------------|---------------------|-----------------------|-------------------|-----------|-------------|----------------------------|----------|------------------|---------|--------------|
| 1 | Ashvini       | Ashwini Kumars     | Horse’s head        | 0° Aries – 13°20′     | Ketu              | Deva      | Kshatriya   | Horse (male)               | Aadi     | Head              | Rajasic (R) | Kṣipra (Swift)   |
| 2 | Bharani       | Yama               | Yoni (womb)         | 13°20′ – 26°40′ Aries | Venus             | Rakshasa  | Shudra      | Elephant (female)         | Madhya   | Private parts     | Tamasic (T) | Ugra (Violent)   |
| 3 | Krittika      | Agni               | Razor/knife         | 26°40′ Aries – 10° Taurus | Sun           | Deva      | Vaishya     | Sheep (male)              | Antya    | Face, eyes        | Sattvic (S) | Mishra (Mixed)   |
| 4 | Rohini        | Prajapati/Brahma   | Chariot            | 10° – 23°20′ Taurus   | Moon              | Manushya  | Vaishya     | Serpent (male)            | Antya    | Tongue            | Rajasic (R) | Dhruva (Stable)  |
| 5 | Mrigashira    | Soma (Moon)        | Deer’s head        | 23°20′ Taurus – 6°40′ Gemini | Mars         | Rakshasa  | Shudra      | Female deer (female)      | Madhya   | Neck, throat      | Tamasic (T) | Mridu (Gentle)   |
| 6 | Ardra         | Rudra              | Teardrop/tree      | 6°40′ – 20° Gemini    | Rahu              | Rakshasa  | Shudra      | Female goat (female)      | Antya    | Eye             | Tamasic (T) | Tikshna (Sharp) |
| 7 | Punarvasu     | Aditi              | Bow and quiver     | 20° Gemini – 3°20′ Cancer | Jupiter       | Deva      | Kshatriya   | Cat (female)             | Aadi     | Hands             | Sattvic (S) | Chara (Movable)  |
| 8 | Pushya        | Brihaspati         | Cow’s udder        | 3°20′ – 16°40′ Cancer | Saturn            | Deva      | Kshatriya   | Buffalo (male)           | Madhya   | Chest, breasts    | Sattvic (S) | Kṣipra (Swift)   |
| 9 | Ashlesha      | Naga (Serpent)     | Coiled serpent     | 16°40′ – 30° Cancer   | Mercury           | Rakshasa  | Shudra      | Cat (male)               | Antya    | Stomach           | Tamasic (T) | Tikshna (Sharp) |
| 10| Magha         | Pitris             | Throne room        | 0° – 13°20′ Leo       | Ketu              | Rakshasa  | Kshatriya   | Female lion (female)     | Aadi     | Heart             | Tamasic (T) | Ugra (Violent)   |
| 11| Purva Phalguni| Bhaga              | Front legs bed     | 13°20′ – 26°40′ Leo   | Venus             | Manushya  | Vaishya     | Female elephant (female) | Madhya   | Thighs            | Tamasic (T) | Ugra (Violent)   |
| 12| Uttara Phalguni| Aryaman           | Back legs bed      | 26°40′ Leo – 10° Virgo | Sun              | Deva      | Kshatriya   | Horse (female)           | Madhya   | Finger           | Sattvic (S) | Sthira (Fixed)   |
| 13| Hasta         | Savitar            | Hand               | 10° – 23°20′ Virgo    | Moon              | Manushya  | Vaishya     | Buffalo (female)         | Aadi     | Palm             | Sattvic (S) | Kṣipra (Swift)   |
| 14| Chitra        | Tvashtar           | Bright jewel/art   | 23°20′ Virgo – 6°40′ Libra | Mars         | Rakshasa  | Kshatriya   | Female cat (female)     | Madhya   | Heart            | Sattvic (S) | Mridu (Gentle)   |
| 15| Swati         | Vayu               | Young plant       | 6°40′ – 20° Libra     | Rahu              | Manushya  | Vaishya     | Buffalo (male)           | Aadi     | Skin            | Tamasic (T) | Chara (Movable)  |
| 16| Vishakha      | Indra-Agni         | Triumphal arch    | 20° Libra – 3°20′ Scorpio | Jupiter      | Rakshasa  | Vaishya     | Tiger (male)            | Antya    | Rectum           | Tamasic (T) | Mishra (Mixed)   |
| 17| Anuradha      | Mitra              | Lotus              | 3°20′ – 16°40′ Scorpio | Saturn         | Deva      | Vaishya     | Deer (female)            | Madhya   | Heart            | Sattvic (S) | Mridu (Gentle)   |
| 18| Jyeshtha      | Indra              | Circular amulet    | 16°40′ – 30° Scorpio  | Mercury           | Manushya  | Kshatriya   | Female elephant (female) | Antya    | Lower back       | Tamasic (T) | Tikshna (Sharp) |
| 19| Moola         | Nirriti            | Tied bunch        | 0° – 13°20′ Sagittarius | Ketu           | Deva      | Shudra      | Male dog (male)         | Antya    | Genitals         | Tamasic (T) | Tikshna (Sharp) |
| 20| Purva Ashadha | Apah               | Front legs of bed | 13°20′ – 26°40′ Sagittarius | Venus        | Rakshasa  | Vaishya     | Female dog (female)    | Madhya   | Reproductive organs | Tamasic (T) | Ugra (Violent)   |
| 21| Uttara Ashadha| Vishvadevas        | Back legs of bed  | 26°40′ Sagittarius – 10° Capricorn | Sun       | Deva      | Kshatriya   | Female elephant (male) | Antya    | Hips            | Sattvic (S) | Sthira (Fixed)   |
| 22| Shravana      | Vishnu             | Ear                | 10° – 23°20′ Capricorn | Moon          | Deva      | Kshatriya   | Monkey (male)           | Antya    | Ears            | Rajasic (R) | Chara (Movable)  |
| 23| Dhanishta     | Eight Vasus        | Drum               | 23°20′ Capricorn – 6°40′ Aquarius | Mars       | Deva      | Kshatriya   | Lion (male)            | Antya    | Knees           | Rajasic (R) | Chara (Movable)  |
| 24| Shatabhisha   | Varuna             | Empty circle      | 6°40′ – 20° Aquarius  | Rahu             | Manushya  | Vaishya     | Horse (male)           | Aadi     | Skin (all over)  | Rajasic (R) | Chara (Movable)  |
| 25| Purva Bhadra. | Ajaikapad (Varaha)| Stage bed         | 20° – 3°20′ Pisces    | Jupiter          | Rakshasa  | Kshatriya   | Elephant (male)         | Madhya   | Thighs          | Rajasic (R) | Ugra (Violent)   |
| 26| Uttara Bhadra | Ahirbudhnya        | Stage bed         | 3°20′ – 16°40′ Pisces | Saturn           | Deva      | Kshatriya   | Female elephant (female) | Antya   | Feet            | Sattvic (S) | Sthira (Fixed)   |
| 27| Revati        | Pushan             | Fish              | 16°40′ – 30° Pisces   | Mercury          | Manushya  | Vaishya     | Frog (male)            | Antya    | Feet            | Sattvic (S) | Mridu (Gentle)   |

*(Sources: classical Hora texts, Drik Panchang, etc.)*

# Ashtakoota Compatibility Rules (Marriage Kutas)

In Vedic marriage matching, eight *Kutas* (ashta-koota) are scored (total 36).  A **minimum score** of 18 is traditionally required for a “compatible” match (with some remedial exceptions for certain Doshas)【45†L23-L27】. The details of each Kuta are:

- **Varna Kuta (1 point):**  Compares social/psychological type.  The four varnas rank Brahmin > Kshatriya > Vaishya > Shudra【45†L33-L37】.  Compatibility score is 1 if the groom’s varna is equal or higher (better) than the bride’s; if the bride’s varna is higher than the groom’s, score 0【41†L375-L383】.  (Caste labels are symbolic; e.g. Cancer/Scorpio/Pisces = “Brahmin” type, Aries/Leo/Sagittarius = “Kshatriya”, etc【47†L198-L206】.) 

- **Vashya Kuta (2 points):**  Assesses mutual attraction/control.  The 12 zodiac signs are grouped into five *vāśya* classes【45†L90-L99】:  **Chatushpada (Quadruped):** Aries, Taurus, 15–30° Sagittarius, 0–15° Capricorn; **Manav (Human):** Gemini, Virgo, Libra, 0–15° Sagittarius; **Jalachara (Aquatic):** Cancer, 15–30° Capricorn, Aquarius, Pisces; **Vanachara (Wandering/Leo):** Leo; **Keeta (Insect):** Scorpio【45†L90-L99】.  If both partners’ Moon signs fall in the same group, award 2 points (ideal).  Other pairings get partial points: for example, Table [45†L106-L114] shows Chatushpada–Manav (1 point), Chatushpada–Jalachara (1), etc., and 0 where groups are mutually incompatible.  (See [45†L109-L118] for a full ready-reckoner.)  

- **Tara Kuta (3 points):**  Based on lunar mansion count.  Count from bride’s nakshatra to groom’s and divide by 9; record the remainder (1–9).  Likewise count from groom’s to bride’s, mod9【47†L262-L270】.  The remainders correspond to one of nine *tara* categories: 1 – Janma; 2 – Sampat; 3 – Vipat; 4 – Kshema; 5 – Pratyak (Pratyari); 6 – Sadhana; 7 – Nidhana (Vadha); 8 – Mitra; 9 – Ati Mitra【47†L272-L280】.  Remainders 3, 5, or 7 are considered malefic (Kala Tara) and the result is unfavorable【47†L262-L270】.  Remainders 1,2,4,6,8,9 are benefic.  Scoring: if *both* counts are benefic, full 3 points; if one is benefic and one is malefic, 1.5 points; if both are malefic, 0 points【47†L282-L290】.  

- **Yoni Kuta (4 points):**  Each nakshatra has an animal *yoni* (symbol) – e.g. Ashvini/Shatabhisha = Horse, Bharani/Revati = Elephant, Pushya/Krittika = Sheep, etc.  Compatibility is classified as: same yoni (union of identical animals), friendly, neutral, inimical.  Scoring is: same = 4, friendly = 3, neutral = 2, inimical = 1, hostile = 0【48†L31-L34】.  (Full tables of yoni and animosity are found in classical sources.)  

- **Graha Maitri Kuta (5 points):**  Measures planetary affinity: compare the lord of bride’s Moon sign vs lord of groom’s Moon sign.  Each planet has natural friends, enemies, and neutrals.  For example (from classical tables): 

  - *Sun* – Friends: **Moon, Mars, Jupiter**; Enemies: **Venus, Saturn**; Neutral: **Mercury**【54†L87-L89】.  
  - *Moon* – Friends: **Sun, Mars, Jupiter**; Enemies: – (none listed) ; Neutral: **Mercury, Venus, Saturn**【54†L89-L90】.  
  - *Mars* – Friends: **Sun, Moon, Jupiter**; Enemy: **Mercury**; Neutral: **Venus, Saturn**【54†L90-L92】.  
  - *Jupiter* – Friends: **Sun, Moon, Mars**; Enemies: **Mercury, Venus**; Neutral: **Saturn**【54†L91-L92】.  
  - *Mercury* – Friends: **Sun, Saturn, Venus**; Enemy: **Moon**; Neutral: **Mars, Jupiter**【54†L91-L93】.  
  - *Venus* – Friends: **Mercury, Saturn**; Enemy: **Sun**; Neutral: **Mars, Jupiter**【54†L92-L94】.  
  - *Saturn* – Friends: **Mercury, Venus**; Enemies: **Sun, Moon, Mars**; Neutral: **Jupiter**【54†L92-L94】.  

  The exact scoring can vary, but typically 5 points are allotted if the two lords are mutual friends; 4 if one is neutral, 2 if one is enemy, etc.  (Roughly: mutual friends = 5, one friend & one neutral ≈4, one friend & one enemy ≈2, both neutral ≈2, one neutral & one enemy ≈1, both enemy = 0.)  

- **Gana Kuta (6 points):**  Classifies nakshatras into three *ganas*: Deva (divine), Manushya (human), Rakshasa (demonic).  Scoring is as follows【56†L241-L249】: Deva–Deva, Deva–Manushya, Manushya–Deva and Manushya–Manushya all yield 6 points; Rakshasa–Rakshasa yields 6 points.  A Deva–Rakshasa or Rakshasa–Deva pairing gives only 1 point, and Manushya–Rakshasa or vice versa gives 0 points【56†L241-L249】.  (Table excerpt: Deva×Deva=6; Deva×Manav=6; Manav×Manav=6; Rakshasa×Rakshasa=6; Deva×Rakshasa=1; Rakshasa×Manav=0, etc.) 

- **Bhakoot (Rāśi) Kuta (7 points):**  Compares Moon sign position (emotional compatibility).  The highly inauspicious separations are 2–12 and 6–8 houses apart (i.e. Moon in one chart is 2nd/12th or 6th/8th from the other’s)【56†L258-L266】.  In many traditions, any such malefic Bhakoota yields 0 points; if neither partner’s Moon falls in those axes, the match earns the full 7 points【56†L258-L266】.  (In effect, only the 2/12 and 6/8 separations are treated as “dosha.”)  

- **Nadi Kuta (8 points):**  Each nakshatra is Aadi, Madhya or Antya Nadi【59†L125-L134】.  If both partners have the *same* Nadi, it is a Nadi dosha (score 0); if different, score 8.  **Exception:** Classical texts rule that if partners have the same Nadi but *different* Moon signs (i.e. different rāśis), the Nadi dosha is effectively cancelled【59†L210-L218】.  

The **traditional cutoff** is 18 points or higher (out of 36) for a marriage to be deemed compatible. Some authorities allow exceptions: e.g. Nadi Dosha can be ignored if cancelled by differing Moon signs【59†L210-L218】, or remedied by other astrological factors or rituals. (But as a rule, same Nadi is usually considered a fatal flaw unless one applies classical cancellations【59†L210-L218】.)  

**Sources:** Brihat Parāśara (BPHS) rules for sign aspects【22†L8548-L8555】; classical Nakshatra tables (DrikPanchang, Varāha Mihira, etc.); Ashtakoota texts and compatibility guides【45†L33-L37】【54†L87-L94】【56†L241-L249】【59†L210-L218】. Each result above is anchored by these traditional sources.