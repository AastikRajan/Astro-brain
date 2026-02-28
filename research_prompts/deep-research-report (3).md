# Timing Precision and Sensitive-Point Techniques in Jyotisha and KP

## Tajika Varshaphala computations: solar return, Munthā, and Varṣeśa

### Solar return chart computation and the “tropical vs sidereal” fork  
In the annual-horoscope framework called Varshaphala (Tajika annual horoscopy), the anchor moment is the **solar return / varṣa-praveśa**: the instant when the Sun’s longitude in the target year becomes equal to the Sun’s longitude at birth. citeturn42view1turn4view1

A key practical point is **which zodiac** defines “same longitude”:

- **Sidereal / nirayana practice (common in many Indian Tajika lineages and modern Jyotisha software)**: Some Tajika teaching notes explicitly gloss solar return as Sun’s return to its **natal sidereal position**. citeturn26view1turn42view1  
- **Tropical practice (standard in Western solar returns, also argued as historically closer to Perso-Arabic antecedents)**: Western solar return descriptions frequently specify the Sun’s return to the natal **tropical** longitude. citeturn0search8turn4view1

Mechanically, this is not a philosophical triviality: using a sidereal zodiac typically shifts the return moment by **minutes** relative to a tropical return, which can visibly change the annual Ascendant and house cusps—hence “timing precision” is central to the technique. citeturn42view1turn4view1

### A workable “exact” algorithm (precision-first, implementation-oriented)  
Classical-style manuals often define the target (Sun returns to natal longitude) and then give computational procedures via ephemerides and corrections rather than modern numerical root-finding. A representative stepwise procedure (matching the classical intent) is:

1. **Fix the zodiac mode** (sidereal or tropical) and compute the natal Sun longitude in that same framework. citeturn4view1turn26view1turn0search8  
2. **Get a first-guess return time near the birthday**. One traditional computational route uses the mean solar-year excess over 52 weeks (≈ 1 day 6h 9m 10s) as a “dhruvāṅka” constant and scales it by completed years to estimate the weekday/time of return near the birthday week. citeturn42view1turn42view0  
3. **Refine by ephemeris**: consult the ephemeris around that estimated date/time and adjust until the **Sun’s longitude “tallies” with the natal Sun longitude**, because that exact equality defines varṣa-praveśa. citeturn42view0turn42view1  
4. **Cast the annual chart** for the return moment (varṣa-praveśa) and then proceed with Tajika judgment (Munthā, Varṣeśa, yogas, daśā, etc.). citeturn42view1turn31view0

This is “exact” in the mathematical sense that the defining condition is a root condition (Δλ☉ = 0) and the procedure iterates/adjusts until the equality holds. The cited tradition emphasizes the equality criterion itself (“Sun’s longitude must tally with the birth longitude”), even if the numerical method is presented via ephemeris tables rather than explicit Newton steps. citeturn42view0turn42view1

### Munthā: computation, annual motion, and finer subdivision  
Tajika uses **Munthā (profected Ascendant)** as a central moving point for annual topics. In a major Tajika compendium, entity["book","Hayanaratna: The Jewel of Annual Astrology","tajika annual astrology 2020"], Munthā is defined as the Ascendant “rotated” one sign per year, computed by dividing elapsed years by 12, taking the remainder, and counting that many signs from the natal Ascendant to locate the Munthā for that year. citeturn27view0

Two “precision upgrades” are explicitly described in that same source tradition:

- **Monthly Munthā increment**: divide a house’s degrees by 12 to get a monthly increment (for month-by-month results). citeturn27view0  
- **Daily Munthā increment**: divide the monthly motion by the days in the relevant month segment to get a daily increment (for day-level timing). citeturn27view0

This matters because Munthā is not only a sign/house token; it can be treated as a **moving degree** for finer timing when the tradition allows it. citeturn27view0

### Varṣeśa (Varsha lord): the five candidates and the selection rule  
The Varṣeśa selection is not “pick the annual Lagna lord and stop.” The classical Tajika rule-set (as preserved in Hayanaratna’s survey of authorities) enumerates **five candidates (pañcādhikārin)**:

1. **Ruler of the Munthā (inthihā/munthā lord)**  
2. **Ruler of the annual Ascendant**  
3. **Triplicity ruler of the annual Ascendant**  
4. **Day/night ruler**: ruler of the sign occupied by the Sun (if the revolution is by day) or by the Moon (if by night)  
5. **Ruler of the natal Ascendant** citeturn31view0

The primary decision rule is also explicit: among the five, **the one that is strong and aspects the annual Ascendant** becomes Varṣeśa; a planet strong but **not** aspecting the annual Ascendant is rejected as Varṣeśa under that rule. citeturn31view0

Tie-breaking logic is likewise given: if multiple candidates aspect the Ascendant, use **greater aspect strength**, then **greater planetary strength**, then “more claims” by dignity schemes; and if no candidate aspects, different sub-traditions propose fallbacks (e.g., annual lagna lord, munthā lord, etc.) with an attempt to resolve by comparative strength. citeturn31view0

## The sixteen Tajika yogas and how they function as a timing logic

### Names and aspect orbs (the “mechanical substrate”)  
The Tajika “sixteen configurations” (ṣoḍaśayoga) are listed explicitly (ikkavāla through duruḥpha), and the **orbs of light** used to judge whether configurations form are also specified: Sun 15°, Moon 12°, Mars 8°, Venus/Mercury 7°, Jupiter/Saturn 9° (with some traditions also giving Rahu 12°). citeturn32view0

### Compact operational definitions (one-line mechanics, tradition-consistent)  
The table below gives “what must be true” for each yoga to exist, in the operational language of the tradition (aspects within orb, faster/slower, giving/taking light, etc.). citeturn33view0turn33view1turn34view0turn34view2turn34view3turn35view0turn36view0turn37view0turn37view1turn37view2turn37view3turn37view4turn37view5turn37view6turn37view7

| Tajika yoga | Minimal mechanical definition (how it forms) |
|---|---|
| Ikkavāla | All planets concentrated in **angles/succedents** (one classical definition); treated as strong for dominion/happiness. |
| Induvāra | All planets concentrated in **cadent** houses (classically “not praised”). |
| Itthaśāla | An applying configuration: within orb, the faster planet is behind in longitude and approaches the slower (mutthaśila). |
| Īsarāpha | A separating configuration: faster planet has passed ahead of the slower by about a degree (classically evil, with noted benefic exceptions). |
| Nakta | No direct aspect between significators; an intervening **faster** planet transfers light from the one behind to the other. |
| Yamayā | No mutual aspect between significators; a **slower third** planet collects light from the faster and gives to the slower. |
| Maṇaū | Mars/Saturn (malefic) interferes by taking/robbing light via inimical aspect, defeating an otherwise helpful configuration. |
| Kambūla | A success configuration built from an itthaśāla between significators plus the Moon forming itthaśāla with one or both; graded by dignities into many subtypes. |
| Gairikambūla | Moon traverses a sign not aspected by the significators, then enters a planet’s sign/exaltation such that a joining/configuration is formed: treated as kambūla-like if in proper dignity. |
| Khallāsara | Moon cannot configure with either significator (no mutthaśila/joining), thereby destroying the matter sought despite a base itthaśāla. |
| Radda | An itthaśāla involving a debilitated condition: retrograde, combust/approaching rays, set, in 6/8/12, overcome by malefic, etc., destroying pleasant results. |
| Duḥphālikuttha | A slower planet with dignity forms a configuration with a swifter planet lacking dignity; declared beneficent for accomplishment. |
| Dutthotthadabīra | Weak significators configure, but one/both receive help via configuration with another strong planet(s), accomplishing through assistance. |
| Tambīra | No configuration between significators; one strong significator at end of sign gives light to a strong planet in the next sign within orb—highly beneficial. |
| Kuttha | A “strength certificate”: a planet strong by dignity, angularity, benefic contacts, free of malefic affliction, direct/risen, etc., granting results fully. |
| Duruḥpha | A “weakness/affliction certificate”: set/retrograde/malefic contacts, in 6/8/12, etc.; also includes special cautions for Moon conditions. |

The practical reason these matter for timing is that they encode a **causal chain**: applying vs separating, light transfer/collection, and malefic interruption are all formal ways of saying “promise, mediation, delay, denial, or destruction.” citeturn33view1turn34view2turn35view0turn37view2turn37view7

## Tithi Pravesha: computation, cadence, and difference from Varshaphala

### What a Tithi Pravesha chart is (annual, but phase-locked)  
Tithi Pravesha is explicitly framed as an **annual** horoscopy keyed not only to the Sun’s yearly cycle but to the **Sun–Moon angular displacement** (tithi) at birth: the “annual birth moment” is when the Sun is in its natal sign and the Moon–Sun displacement angle matches birth (same tithi and same fraction remaining). citeturn26view1turn26view0

This differs from a “pure” Varshaphala solar return where the defining condition is “Sun returns to natal longitude” (in the chosen zodiac). citeturn42view1turn4view1

### Exact computation procedure (manual, reproducible)  
A practical “do it by hand” algorithm (as taught in a detailed worked example) is:

1. In the natal chart, record:  
   - the Sun’s **sign** at birth,  
   - the running **tithi** at birth, and  
   - the **fraction of the tithi remaining** at birth. citeturn26view0turn26view1  
2. In the target year, find the window when the Sun returns to the **natal Sun sign**. citeturn26view0turn26view1  
3. Inside that window, locate when the same **tithi** recurs; compute tithi start/end times from a panchanga. citeturn26view0turn26view1  
4. Convert the natal “fraction remaining” into minutes/hours from the **end** of the tithi and count backward to get the **exact return moment** when the remaining fraction matches birth. citeturn26view0turn26view1  
5. Cast the chart for that exact moment using the **birthplace longitude/latitude** (explicitly stated as independent of where the native is currently living in the cited method). citeturn26view0turn26view1

### Use-case logic and “monthly vs annual”  
The canonical definition above is annual (because it is anchored to the Sun coming back to its natal sign once per year). citeturn26view1turn26view0  
However, some modern authors discuss “monthly and daily iterations” of praveśa concepts as a further subdivision approach (annual → monthly → daily), analogous in spirit to the way some Tajika sources also discuss monthly/daily revolutions. citeturn23search10turn27view0

## Gochara Vedha: complete obstruction table, explicit exceptions, and how “Viparīta Vedha” appears in practice

### The classical-style Vedha table (from Moon as reference)  
A standard presentation (as given in entity["book","Gochar Phaladeepika","transit astrology | U. S. Pulippani"]) lists, for each planet, (a) the **benefic transit places** (counted from natal Moon) and (b) the corresponding **Vedha (obstruction) places** that can block those benefic results. citeturn43search9turn6view0

**Complete table (benefic places → vedha places)**: citeturn43search9turn6view0  

- **Sun**: 3, 6, 10, 11 → 9, 12, 4, 5  
- **Moon**: 1, 3, 6, 7, 10, 11 → 5, 9, 12, 2, 4, 8  
- **Mars**: 3, 6, 11 → 12, 9, 5  
- **Mercury**: 2, 4, 6, 8, 10, 11 → 5, 3, 9, 1, 8, 12  
- **Jupiter**: 2, 5, 7, 9, 11 → 12, 4, 3, 10, 8  
- **Venus**: 1, 2, 3, 4, 5, 8, 9, 11, 12 → 8, 7, 1, 10, 9, 5, 11, 3, 6  
- **Saturn**: 3, 6, 11 → 12, 9, 5  

### Exceptions “beyond the standard ones” (explicitly stated)  
The same Vedha presentation contains **named non-obstruction exceptions**, i.e., planet-pairs where the usual vedha blocking is not applied. The cited Gochar Phaladeepika table explicitly states at least the following: **no Vedha by Saturn to Sun**, **no Vedha by Mercury for Moon**, **no Vedha to Mercury by Moon**, and **no Vedha by Sun to Venus** (and also **no Vedha by Sun to Saturn** in the same table tradition). citeturn43search9turn6view0

### Do benefics weaken the Vedha effect?  
In the stripped-down vedha rule as taught in gochara manuals, the obstruction is triggered by “a planet” being in the vedha place, with the classical exceptions specifying **which planet does not count** (e.g., “other than the Sun” / “other than Mercury” style clauses in worked gochara descriptions). citeturn44view0

So the baseline classical-style operational reading is: **Vedha is positional and categorical, not inherently “benefic vs malefic dependent,”** except where the exception list explicitly names a planet that does not obstruct. citeturn44view0turn43search9

That said, ancillary classical principles quoted in gochara teaching literature also state that benefic and malefic influences can **neutralize** each other under specific interaction conditions (e.g., “strong planet yielding good results” afflicted by an evil-causing planet, or malefic aspected by benefic → effects neutralized), which is one textual route by which later practitioners justify “severity weighting.” citeturn44view0

### Where “Viparīta Vedha” shows up mechanically  
Even without using the label, the gochara rules repeatedly describe obstruction of **good** effects (benefic transit blocked by a planet in vedha place) and obstruction of **ill** effects (bad transit mitigated when the “blocking” placement is present). For example, the same teaching format says the ill effects of a transit can be obstructed when another planet occupies a specified place “other than X,” mirroring the viparīta idea. citeturn44view0

## Tarabala and Chandrabala: exact formula, repeating cycle, and Muhurta integration

### Tarabala (Navatara chakra): the exact cycle and auspicious/inauspicious classes  
Tarabala is based on the transit Moon’s **nakshatra distance** from the natal Moon’s nakshatra (Janma Nakshatra). The 27 nakshatras are partitioned into **three cycles** of nine (1–9, 10–18, 19–27), and the same nine Tara categories repeat across all 27. citeturn50view0turn48view0

A precise computation rule (index-based):

- Label natal nakshatra as N (1–27) and transit nakshatra as T (1–27).  
- Compute forward count: **k = ((T − N + 27) mod 27) + 1** (so k is 1–27 counting inclusively from natal to transit).  
- Tara category index is **r = ((k − 1) mod 9) + 1**, mapping:  
  1 Janma, 2 Sampat, 3 Vipat, 4 Kshema, 5 Pratyari/Pratyak, 6 Sadhana/Sadhaka, 7 Naidhana, 8 Mitra, 9 Parama/Adhi-Mitra. citeturn50view0turn48view0

Auspiciousness classification is also consistently summarized:

- **Benefic / auspicious**: Sampat, Kshema, Sadhana, Mitra, Parama/Adhi-Mitra. citeturn50view0turn48view0  
- **Malefic / inauspicious**: Vipat, Pratyari, Naidhana. citeturn50view0turn48view0  
- **Janma** is often treated as neutral-to-mixed (many practical guides tag it “not good” for muhurta selection). citeturn50view0turn48view0

### Chandrabala: strong vs weak transit placements relative to natal Moon sign  
Chandrabala is framed as a **rāśi-distance** rule: count from the natal Moon sign (Janma Rāśi) to the transit Moon sign. If the count is in an allowed set, Chandrabala is present (favorable). citeturn51search1turn51search2turn51search3

Two closely related rule-sets appear in practice-oriented sources:

- **Set A (includes 7)**: favorable counts = **1, 3, 6, 7, 10, 11**; avoid **8th** (Aṣṭama Candra). citeturn51search1turn51search2  
- **Set B (excludes 7)**: favorable counts = **1, 3, 6, 10, 11** (again, avoid 8). citeturn51search3  

If you need a single operational rule in Muhurta screening, Set A is explicitly given in multiple muhūrta-checklist style writeups, and the “avoid 8th” warning is consistent across them. citeturn51search1turn51search2turn51search3

### How Tarabala and Chandrabala are combined in Muhurta practice  
Practical electional checklists treat Tarabala as a **baseline filter** (“Tarabalam is a basic step”), then apply Chandrabala as an additional strength check on the event day/time; if either is adverse, many sources advise discarding the muhurta or using remedial/exception handling, and they also emphasize that other strength factors and the muhurta chart itself can override some defects. citeturn48view0turn51search1turn51search2

## KP Sub-Sub Lord: computation logic, signification rules, and “final trigger” conditions

### What KP means by star, sub, and sub-sub in a timing workflow  
In KP practice, a point (especially a **cusp**) is classified by **sign lord**, **constellation (nakshatra) lord**, and **sub lord**; the sub level is treated as especially decisive for specificity. citeturn53view1turn53view3

A key structural fact emphasized in KP manuals is that the nakshatra subdivisions produce around **249 subs** in practical tables (rather than a purely idealized 243) because some sub divisions cross sign boundaries; and practitioners may **further subdivide** those subs for finer research-grade work. citeturn16view1turn16view0

### Signification rules (what a planet “promises”)  
A core interpretive rule is:

- Identify **which star (constellation)** a planet occupies, find the **lord of that constellation**, then read (a) the house where that constellation lord sits (occupancy) and (b) the houses it owns (lordship); these are the results delivered during the period of the planet occupying that constellation. citeturn53view3

A second key rule is that sub-level discrimination changes the output even when the constellation theme remains the same: a text example states that if the constellation indicates a topic (e.g., married life), then **transit through favorable vs unfavorable subs** changes whether the experience is pleasure or displeasure, even though the constellation indication is unchanged. citeturn53view1

### How to compute a Sub-Sub Lord (SSub) in a strictly algorithmic way  
KP’s sub system is based on Vimshottari proportional division of the 13°20′ nakshatra arc; the cited manuals describe the existence of sub divisions at scale (the 249-sub practical table) and explicitly note that further subdivision is a legitimate extension for research students. citeturn16view1turn16view0

A reconstruction consistent with that framework (inference, but mechanically forced by the sub-division premise) is:

1. Determine the point’s nakshatra and its **sub lord** by locating the degree segment inside the nakshatra’s Vimshottari-proportional sub arc. citeturn16view1turn53view3  
2. Take the sub lord’s sub arc and subdivide it again by the **same Vimshottari proportions** (a second-order subdivision).  
3. The planet ruling the resulting second-order segment is the **sub-sub lord (SSub)**. citeturn16view1turn16view0  

This step is not always spelled out in a single “one-line formula” in the cited pages, but it is the standard mathematical extension implied by (a) the 249-sub framework and (b) explicit encouragement to further subdivide for finer discrimination. citeturn16view1turn16view0

### When SSub becomes the “final timing trigger” (promise vs delivery vs activation)  
KP texts repeatedly separate **(i) promise/deny** logic at cusps from **(ii) timing/triggering** via periods and transits:

- Promise/deny is illustrated by statements like: *if the sub lord of a cusp is a significator of certain houses, then the event outcome follows* (with many concrete examples for how cusp sub-lords signify results). citeturn53view0turn53view2  
- Fine sequencing is illustrated by a transit-through-subs example (a legal case progressing through successive sub segments), showing how **sub-level transits** can time stages of manifestation. citeturn53view1  

Putting those together, the strict rule-set that many KP practitioners operationalize is:

1. **Event must be promised**: relevant cusp sub-lords must signify the event houses (and avoid strong denial houses for that matter). citeturn53view0turn53view2  
2. **Period must support**: the running period lords (down to sub/sub-sub levels in the period scheme) must be significators of the event houses; KP manuals explicitly treat period subdivisions as meaningful (daśā subdivided into bhukti, then antara/sub-subperiods, etc.). citeturn16view2turn16view3  
3. **Transit must activate**: transits through relevant subs (and, by extension, sub-subs for finer precision) act as the operational “trigger,” consistent with the worked transit sequencing example. citeturn53view1turn16view1  

Under that logic, **SSub is “final” only after promise is established at the cusp-sub level**; otherwise, SSub refinement is irrelevant because there is nothing to deliver. citeturn53view0turn53view1

## Special points and sensitive degrees: Māṇḍī, upagrahas, Yogi/Avayogi, Sarpa/Pakshi drekkana, and Bhrigu Bindu

### Māṇḍī vs Gulika: exact computations and conceptual distinction  
A standard computational teaching document defines **Gulika** via dividing day/night into eight equal parts and taking Saturn’s portion; it then states that Gulika’s longitude is the **ascending degree at the start of Gulika’s portion**. citeturn46view0

The same document distinguishes **Māṇḍī (Mandi)** by using a **32-part division** of day or night and provides a weekday-dependent lookup:

- Divide the relevant half (day if birth before sunset, night if after sunset) into **32 equal parts**.  
- Māṇḍī rises (i.e., take the Ascendant at that moment) at these part numbers (Sun→Sat):  
  - **Day**: 26, 22, 18, 14, 10, 6, 2  
  - **Night**: 10, 6, 2, 30, 26, 22, 18 citeturn46view0

It explicitly interprets this as: Māṇḍī rises in the **middle portion of Saturn’s part** each day—thereby giving a clear conceptual distinction: Gulika is tied to the Saturn-ruled segment boundary in the 8-part scheme, while Māṇḍī is placed at a different, more “mid-segment” timing in the 32-part refinement. citeturn46view0

### The five “Aprakāśa” upagrahas from Sun longitude (formulas + meaning)  
A widely circulated computational note defines the five non-luminous points **Dhuma, Vyatipāta, Pariveṣa/Paridhi, Indracāpa (Chāpa), Upaketu**, stating they are calculated from the Sun’s longitude and are “malefic by nature” and afflictive. citeturn46view0

Formulas (all longitudes mod 360°):

- **Dhuma** = Sun + 133°20′  
- **Vyatipāta (Pāta)** = 360° − Dhuma  
- **Pariveṣa/Paridhi** = 180° + Pāta  
- **Indracāpa (Chāpa/Kodanda)** = 360° − Paridhi  
- **Upaketu** = Chāpa + 16°40′ citeturn46view0

### Yogi, Avayogi, and Duplicate Yogi: exact calculation and identification  
A detailed instructional write-up gives an explicit computational scheme:

1. **Yogi point** = Sun longitude + Moon longitude + **93°20′** (constant), reduced mod 360°. citeturn47view0  
2. **Avayogi point** = Yogi point + **6 signs 6°40′** (i.e., +186°40′), reduced mod 360°. citeturn47view0  
3. Identification rules:  
   - **Yogi planet** = lord of the nakshatra containing the Yogi point. citeturn47view0  
   - **Duplicate Yogi** = ruler of the sign containing the Yogi point. citeturn47view0  
   - **Avayogi planet** = lord of the nakshatra containing the Avayogi point. citeturn47view0  
4. A noted shortcut: once Yogi planet is known, Avayogi can be found by counting **6 inclusively in Vimshottari sequence** from the Yogi planet. citeturn47view0

### Sarpa and Pakshi drekkana: complete placement table and health/danger interpretations  
A full “nature of drekkana” table assigns each 10° drekkana (I, II, III within each sign) to categories including **Sarpa** and **Pakshi**, among others. citeturn20view0

To make it operational for “which drekkana positions”:

- Drekkana I = 0°00′–10°00′ of a sign  
- Drekkana II = 10°00′–20°00′  
- Drekkana III = 20°00′–30°00′ citeturn52view0turn20view0

**Where Sarpa appears in the complete table** (including mixed labels where given):  
- Taurus II (Sarpa/Chatuspada)  
- Cancer II (Sarpa), Cancer III (Sarpa)  
- Scorpio I (Sarpa), Scorpio II (Sarpa/Pasha)  
- Pisces III (Sarpa) citeturn20view0

**Where Pakshi appears in the complete table** (including mixed labels where given):  
- Gemini II (Ayudha/Pakshi)  
- Leo I (Ayudha/Pakshi/Chatuspada)  
- Virgo I, II, III (Pakshi)  
- Libra I, II (Pakshi)  
- Sagittarius I (Pakshi)  
- Capricorn I (Pakshi/Chatuspada) citeturn20view0

For health/danger result framing, one drekkana-focused writeup (citing classical tradition such as Phaladīpikā) states that among certain named drekkanas (including Sarpa/Pāśa/Nigala), births under these can correlate with adverse character/poverty themes and that if the **rising drekkana** is Nigala, Pāśa, or Sarpa and is associated with malefics, it indicates **short life**; it also explicitly links drekkana analysis to illness/recovery and the 22nd drekkana to death indications. citeturn52view0  
Separately, a student-notes style drekkana document states that “Pakshi drekkana” is unstable/communicative and warns that certain key lords placed there can indicate unnatural death (a modern-compiled but widely circulated rule in the drekkana-anatomy tradition). citeturn18search1turn19search2

### Bhrigu Bindu: exact computation and transit use claims  
Bhrigu Bindu is commonly defined in practitioner literature as the **midpoint on the Rahu–Moon axis**, computed by taking the difference between Moon and Rahu longitudes and halving it (then placing the midpoint accordingly). citeturn18search8turn18search18

A precise midpoint computation (zodiac-safe) is:

- Let λR = Rahu longitude, λM = Moon longitude (both mod 360°).  
- Compute forward distance d = (λM − λR) mod 360°.  
- Midpoint longitude λBB = (λR + d/2) mod 360°. citeturn18search8turn18search18

Use in transit timing is described (in modern predictive practice) as treating Bhrigu Bindu as a **sensitive degree** such that transits over it (or aspects to it) correlate with “eventful” periods; some sources further ascribe planet-specific flavors (e.g., benefics vs malefics) to those contacts. citeturn18search15turn18search8