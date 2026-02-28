# ATCH 5 and ATCH 6 Missing Details in Shadbala and Ashtakavarga

## Measurement conventions and where these formulas “live” in the classical stack

Classical *Shadbala* computations are expressed in **Shashtiamsa/Virupas** units (i.e., “60ths”), where **1 Rūpa = 60 Shashtiamsas (Virupas)**. citeturn16view2 The practical consequence is that many “divide by 3” rules are doing a hidden normalization: e.g., a 180° arc (half-zodiac) mapped into a 60-point scale gives 180/3 = 60. citeturn13view0turn29view0

For the “missing details” you flagged, the most load-bearing primary sources are the heliacal visibility/combustion thresholds in entity["book","Sūrya Siddhānta","sanskrit astronomy text"], and the Shadbala + Ishta/Kashta + Ashtakavarga shodhana procedures in entity["book","Brihat Parashara Hora Shastra","santhanam english translation"]. citeturn12view0turn21view0turn22view0 For modern computational “worked-out” clarity on Kala Bala and related computations (including explicit Ayana Bala and Yuddha Bala formulas), a widely used modern manual is entity["book","Graha and Bhava Balas","b v raman 1996"] by entity["people","B. V. Raman","indian astrologer 1912-1998"]. citeturn15view0turn28view0turn29view0

## Exact combustion orbs per planet

### What “combustion orb” is measuring in the Surya Siddhanta frame

In entity["book","Sūrya Siddhānta","sanskrit astronomy text"], the relevant idea is *heliacal invisibility/visibility* relative to the Sun: bodies “with little light” become invisible when the computed “Kalāṃśa” is less than the body’s own Kalāṃśa; they reappear when it is greater. citeturn12view0 In modern astrological shorthand, this often gets treated as a **Sun–planet center-to-center angular separation threshold** (a fixed “orb”), although the text’s own phrasing is in “degrees of time” tied to heliacal rise/set geometry. citeturn12view0

### The complete Surya Siddhanta table (mean/standard Kalāṃśa thresholds)

The following values are stated explicitly (Ch. IX for the five “starry” planets, plus Ch. X for the Moon). citeturn12view0

| Body (geocentric) | Standard “combustion / heliacal invisibility” threshold (Kalāṃśa) | Retrograde adjustment stated in the text? | Notes |
|---|---:|---|---|
| Moon | 12° | No retrograde state | Moon’s heliacal visibility rule is given separately; she becomes visible/invisible by 12°. citeturn12view0 |
| Mars | 17° | No | Given as one of the standard Kalāṃśas. citeturn12view0 |
| Jupiter | 11° | No | Given as one of the standard Kalāṃśas. citeturn12view0 |
| Saturn | 15° | No | Given as one of the standard Kalāṃśas. citeturn12view0 |
| Venus | 10° (direct) / 8° (retrograde) | Yes (explicit, not “half”) | The text explicitly links the 8° case to retrograde motion and “greatness of its disc,” and the 10° case to direct motion (disc smaller). citeturn12view0 |
| Mercury | 14° (direct/“moving quick”) / 12° (retrograde) | Yes (explicit, not “half”) | Mercury is 12° in retrograde, 14° in quick/direct motion. citeturn12view0 |

### Does retrograde make it “½ the orb”?

Not in this primary table. The explicit retrograde adjustments in entity["book","Sūrya Siddhānta","sanskrit astronomy text"] are **specific** to Mercury and Venus (14→12; 10→8), and are **not** a simple “½ orb” rule. citeturn12view0

If your course notes assert a “retrograde = half orb” convention, that appears to be a *later pedagogical simplification* (or a cross-system import) rather than what this particular classical astronomical source states. The clean takeaway for “exact table work” is: **use the explicit Surya Siddhanta values unless your lineage/textbook specifies an alternate pramāṇa**. citeturn12view0

### Mean orb vs exact (Spashta) orb

There are two distinct layers that often get conflated:

1. **The canonical threshold numbers** (the Kalāṃśas above) are “standard/mean” constants in the text. citeturn12view0  
2. The **exact time and effective separation for visibility** depends on observational geometry (including latitude effects). A practical statement of this “exactness” issue is that planetary latitude away from the ecliptic can require the Sun to be “a bit closer or farther,” shifting the effective range by about **1–2 degrees at most**. citeturn4view0

So, a defensible “mean vs exact” table representation is:

- **Mean (Sāma) orb**: the fixed Surya Siddhanta Kalāṃśa values above. citeturn12view0  
- **Exact (Spashta) orb**: *mean value plus a small geometric correction*, typically on the order of ~±1–2° depending on latitude/visibility geometry, rather than a second fixed canonical number per planet. citeturn4view0

## Cheshta Bala exact formula and the motion-state table

### Two different (but related) “Cheshta” implementations you must not mix up

In the Parāśarī Shadbala pipeline, “Cheshta Bala” exists in two complementary forms:

- A **continuous** computation based on a “Cheshta Kendra” (linked to mean/true positions and the Sīghrocca/apogee). citeturn13view0  
- A **discrete** computation using **eight motion states** (often read directly from an ephemeris as “vakra, manda, etc.”) with fixed Shashtiamsa allocations. citeturn13view0  

These are best treated as two lenses on the same underlying idea: “how dynamically potent is the planet’s apparent motion at this time?”

### Cheshta Bala formula by planet class

**Sun and Moon (special rules):**

- The Sun’s Cheshta Bala is taken to **correspond to its Ayana Bala**. citeturn13view0  
- The Moon’s Cheshta Bala is taken as **its Paksha Bala**. citeturn13view0  

**Mars through Saturn (the continuous ‘Cheshta Kendra’ computation):**

A compact restatement of the steps given is: citeturn13view0

1. Let **L̄** = mean longitude of the planet, and **L** = true longitude of the planet.  
2. Compute the midpoint longitude: **Lmid = (L̄ + L) / 2**.  
3. Compute the angular separation from the **Sīghrocca** (apogee) to Lmid; the remainder (normalized to within 0–180°) is the **Cheshta Kendra**. citeturn13view0  
4. Convert the Cheshta Kendra to degrees and compute:  
   **Cheshta Bala (Virupas) = Cheshta Kendra / 3**. citeturn13view0  

This produces a 0–60 scale naturally, since the maximum normalized kendra is 180°. citeturn13view0

### The “7 states” issue: the standard list is eight

Your prompt says “7 states” but lists eight names. The standard Parāśarī list here is explicitly **eight** motions: Vakra, Anuvakra, Vikala, Manda, Mandatara, Sama, Chara, Atichara. citeturn13view0

### The eight motion states and their Shashtiamsa allocations

For Mars through Saturn, the stated allocation is: citeturn13view0

| Motion state | Description gloss (as given) | Cheshta points (Virupas) |
|---|---|---:|
| Vakra | retrograde motion | 60 |
| Anuvakra | entering the previous sign in retrograde | 30 |
| Vikala | stationary / devoid of motion | 15 |
| Manda | somewhat slower than usual | 30 |
| Mandatara | slower than the previous-mentioned | 15 |
| Sama | somewhat increasing vs manda | 7.5 |
| Chara | faster than sama | 45 |
| Atichara | entering next sign in accelerated motion | 30 |

This table is exactly the kind of thing software and teaching notes often scramble (especially swapping labels or using alternative point sets), so anchoring it to the cited canonical list matters for “exact formula” work. citeturn13view0

## Kala Bala complete formula

### Component list (what “complete” typically includes)

A standard modern exposition (explicitly listing the components you asked for) states that Kala Bala consists of **Nathonnatha**, **Paksha**, **Tribhaga**, **Abda (Varsha)**, **Masa**, **Vara**, **Hora**, **Ayana**, and **Yuddha Bala**. citeturn15view0

### Nathonnatha Bala (Divaratri / day-night strength)

One classical stepwise method is: citeturn13view0

- Compute **Unnata** = the difference between midnight and apparent birth time.  
- Compute **Nata = 30 ghatis − Unnata**.  
- **Moon, Mars, Saturn**: get **Nathonnatha Bala = 2 × Nata (in ghatis)**, expressed on the 0–60 scale. citeturn13view0  
- **Sun, Jupiter, Venus**: get **Unnatha Bala = 60 − Nathonnatha Bala**. citeturn13view0  
- **Mercury**: always gets the full **60 Virupas** irrespective of day/night. citeturn13view0  

A fully explicit variant (same idea, but algebraically expressed and tied to local apparent time) appears in entity["book","Graha and Bhava Balas","b v raman 1996"], including the “if the birth-time-in-degrees exceeds 180°, subtract from 360°” normalization so the result stays in the 0–180° half-cycle. citeturn15view0

### Paksha Bala (lunar phase / elongation-based strength)

The basic computation is:

1. Compute the Sun–Moon longitudinal difference; if it exceeds 180° (6 signs), take its complement to 180° (or equivalently to 360° depending on the convention) so you work with a 0–180° arc. citeturn13view0turn29view0  
2. Convert to degrees and divide by 3: **Paksha Bala = (normalized elongation) / 3** for benefics; malefics get the complement to 60. citeturn13view0turn29view0  
3. A commonly stated detail is that **the Moon’s Paksha Bala is doubled** in this computation. citeturn29view0  

### Tribhaga Bala (three-part day/night strength)

The day (sunrise→sunset) and night (sunset→sunrise) are each divided into three equal parts; the planet assigned to the part containing birth gets **60**. citeturn13view0turn29view0

Assignments:

- **Day**: 1st third Mercury, 2nd third Sun, 3rd third Saturn. citeturn13view0turn29view0  
- **Night**: 1st third Moon, 2nd third Venus, 3rd third Mars. citeturn13view0turn29view0  
- **Jupiter**: gets 60 at all times. citeturn13view0turn29view0  

### Varsha/Masa/Vara/Hora Bala (lords of year, month, weekday, hour)

A classical allocation rule is:

- **Varsha (Abda) lord**: 15 Virupas  
- **Masa lord**: 30 Virupas  
- **Vara (weekday) lord**: 45 Virupas  
- **Hora lord**: 60 Virupas citeturn13view0  

The computational question is how to find the **lords**. A detailed algorithm is:

- Compute **Ahargana** (days from an epoch). citeturn29view0  
- Treat the astrological year as **360 days** and month as **30 days** (explicitly not solar/lunar months for this purpose). citeturn29view0  
- **Year lord (Abdadhipathi)**: divide Ahargana by 360; take the quotient (years elapsed), multiply by 3, add 1, divide by 7, and count the remainder from Sunday to get the weekday of year commencement; the planet ruling that weekday is the year lord. citeturn29view0  
- **Month lord (Masadhipathi)**: divide Ahargana by 30; take the quotient (months elapsed), multiply by 2, add 1, divide by 7, and count the remainder from Sunday to get the weekday of month commencement; its weekday ruler is the month lord. citeturn29view0  
- **Weekday lord (Varadhipathi)** is simply the planet ruling the weekday of birth (also verifiable by Ahargana mod 7). citeturn29view0  
- **Hora lord**: the first hora of the day is ruled by the weekday lord; count hours from sunrise to birth to identify the hora sequence and its planetary ruler. citeturn16view3  

### Ayana Bala (declination / Kranti-based seasonal strength)

An explicit computational formula (attributed there to entity["people","Keshava Daivajna","indian astrologer"]) is: citeturn28view0

\[
\text{Ayana Bala}=\frac{24^\circ \pm \text{Kranti}}{48}\times 60
\]

Where “±” depends on whether the planet’s declination (Kranti) is additive or subtractive for that planet:

- For **Sun, Mars, Jupiter, Venus**: **north declination additive**, south subtractive. citeturn28view0  
- For **Saturn, Moon**: **south declination additive**, north subtractive. citeturn28view0  
- For **Mercury**: **both north and south are additive**. citeturn28view0  
- The Sun’s Ayana Bala is stated to be **doubled**. citeturn28view0  

### Yuddha Bala (planetary war) as a Kala Bala component

A standard Kala Bala treatment computes Yuddha Bala when two planets are at war:

- Two planets are in Yuddha when they are in conjunction and their separation is **< 1°**. citeturn28view0  
- All planets except Sun and Moon may enter into war; the victorious planet is stated as the one with **less longitude**. citeturn28view0  
- Compute an aggregate **(Sthana Bala + Dig Bala + Kala Bala up to Hora Bala)** for each combatant, take the difference, and divide by the difference of their apparent disc diameters (Bimba Parimāṇas) to obtain **Yuddha Bala**. citeturn28view0  
- Add that Yuddha Bala to the victor’s Kala Bala total and subtract it from the vanquished planet’s Kala Bala total. citeturn28view0  

This is the “complete formula” version you asked for, because it specifies: (i) detection threshold, (ii) winner rule, (iii) which Bala subtotal to use, and (iv) how it’s applied back into Kala Bala. citeturn28view0

## Ishta Phala and Kashta Phala from Uchcha and Cheshta

### The BPHS formula chain (Uchcha Rasmi + Cheshta Rasmi → Ishta/Kashta)

In entity["book","Brihat Parashara Hora Shastra","santhanam english translation"], the Ishta/Kashta logic is presented as “benefic and evil tendencies” to judge good/bad outcomes in planetary periods. citeturn13view0

The method uses “rays” (Rasmis), not the full sixfold Shadbala:

1. **Uchcha Rasmis (exaltation rays):** computed from the planet’s position relative to its debilitation point with a 0–180° normalization, then scaled. citeturn13view0  
2. **Cheshta Rasmis:** computed from Cheshta Kendra in an analogous way (Sun and Moon have special Cheshta Kendra rules stated there). citeturn13view0  
3. **Subha Rasmis (auspicious rays):** the average of Uchcha Rasmis and Cheshta Rasmis. citeturn13view0  
4. **Ishta Phala:** subtract 1 from each of Uchcha Rasmi and Cheshta Rasmi, multiply each by 10, add them, take half. citeturn13view0  
5. **Kashta Phala:** **Kashta = 60 − Ishta**. citeturn13view0  

### How this differs from total Shadbala

Ishta/Kashta here is a **benefic-vs-malefic tendency estimator** built from a narrow slice of factors (exaltation-related and motion-related “rays”). citeturn13view0

By contrast, **total Shadbala** is an aggregate strength measure from six sources (positional, directional, temporal, motional, natural, aspectual), and is used more broadly to determine whether a planet is strong enough to deliver its promised results at all. citeturn13view0turn16view2

So a planet can be:
- **High Shadbala but low Ishta**: powerful, but tends to deliver more challenging/malefic results in its periods.
- **Lower Shadbala but higher Ishta**: more benefic in tendency, but may lack delivery power unless supported.

That distinction is exactly why classical workflows often look at both “capacity” (Shadbala) and “valence” (Ishta/Kashta) rather than treating them as redundant metrics. citeturn13view0turn16view2

## Residential strength in Bhavabala (Bhavadhipati Bala) and its components

### What the “three components” usually are

A standard definition of **total Bhava Bala** is the sum of three components: citeturn16view0turn16view2

1. **Bhavadhipati Bala** (strength of the house lord)  
2. **Bhava Digbala** (directional strength of the house)  
3. **Bhava Drigbala** (aspect strength on the house)

These are simply **added** (i.e., weights of 1.0 each in the most literal reading). citeturn16view0turn16view2

### Bhavadhipati Bala “formula”

Bhavadhipati Bala is defined here very plainly: the **Shadbala Pinda of the lord of the bhava** is taken as that bhava’s Bhavadhipati Bala. citeturn16view2

So, computationally, the “residential strength of the lord” is not a separate mini-formula with independent weights; it is **the already-computed Shadbala total of that planet**, slotted into the Bhava Bala sum. citeturn16view2

### Are there dusthana correction factors?

In the explicit computational definitions above, there is **no special correction factor stated** like “if the lord is in a dusthana, multiply by X.” citeturn16view2

However, two important caveats apply:

- Dusthana placement often **reduces Shadbala indirectly** because it correlates with weakened dignities, afflictions, adverse aspects, etc., which are already captured in Shadbala components. citeturn16view2turn13view0  
- A separate set of **Bhava Bala adjustments** exists in Parāśarī instructions: e.g., bhavas occupied by Jupiter or Mercury get an addition of **1 Rūpa**, while those occupied by Saturn, Mars, and Sun suffer a **1 Rūpa reduction**, and there are further conditional additions tied to rasi types and day/twilight/night birth contexts. citeturn13view0  

Those are “house corrections,” not “dusthana-lord multipliers,” but they function as explicit correction terms in Bhava Bala computation. citeturn13view0

## Ashtakavarga reductions: Trikona Shodhana and Ekadhipatya Shodhana

### What is being reduced

In the reduction chapters, the procedure operates on the **count of Rekhas (benefic lines)** per sign after constructing the planet’s Ashtakavarga chart; it is those sign-wise totals that are rectified by Trikona and Ekadhipatya Shodhana. citeturn21view0turn22view0

### Trikona Shodhana: exact step-by-step algorithm with a worked example

The text defines the trines as the four sign-triads: (Aries–Leo–Sagittarius), (Taurus–Virgo–Capricorn), (Gemini–Libra–Aquarius), (Cancer–Scorpio–Pisces). citeturn21view0

A precise algorithm consistent with the worked demonstration is:

1. For each triad, let the three bindu totals be (a, b, c).  
2. If **any** of (a, b, c) is **0**, **no Trikona Shodhana is done** for that triad. citeturn21view0turn22view0  
3. Otherwise, let **m = min(a, b, c)** and replace the triad by **(a−m, b−m, c−m)**. citeturn22view0  
4. Special case: if all three numbers are equal, this rule reduces them all to zero (explicitly stated as well). citeturn21view0turn22view0  

**Worked numerical example (directly from the demonstration):**

In the Sun’s example, the triad (Capricorn, Taurus, Virgo) has **5, 3, 2** rekhas respectively; m = 2. Subtracting yields:

- Capricorn: 5 − 2 = 3  
- Taurus: 3 − 2 = 1  
- Virgo: 2 − 2 = 0 citeturn22view0  

The same reduction is then shown for the other triads (Aquarius–Gemini–Libra; Pisces–Cancer–Scorpio; Aries–Leo–Sagittarius). citeturn22view0

### Ekadhipatya Shodhana: triggers, exact algorithm, worked example

**Trigger condition and scope:**

- Ekadhipatya Shodhana is done **after** Trikona Shodhana. citeturn22view0  
- It applies when **both** signs owned by a planet (i.e., a dual-sign lord) have **non-zero** numbers after Trikona Shodhana; it is not done if one is numberless. citeturn22view0turn17view0  
- Practically, it concerns the dual sign lords: Mars (Aries/Scorpio), Venus (Taurus/Libra), Mercury (Gemini/Virgo), Jupiter (Sagittarius/Pisces), Saturn (Capricorn/Aquarius). Sun and Moon own only one sign each and are left unchanged in this step. citeturn22view0turn17view0  

**Operational rules (mechanism-first form):**

Let the two owned signs have Trikona-corrected totals **A** and **B** (both > 0), and note whether each sign is occupied by any planet.

- **If both signs are occupied by planets:** do nothing. citeturn22view0turn17view0  
- **If one sign is occupied and the other is empty:** the empty sign is reduced (often to zero), while the occupied sign is kept unchanged; in the mixed-size case the reduction is performed by subtracting the occupied sign’s smaller value from the other’s larger value. citeturn22view0turn17view0  
- **If both signs are empty:** the procedure reduces the pair so that redundancy is removed; a worked illustration in the text shows subtracting the smaller from both (making one zero and the other the difference). citeturn20view1turn22view0  

**Worked numerical example (explicit in-text style):**

- Aries (occupied) has 1 and Scorpio (empty) has 3: subtract 1 from 3 → Scorpio becomes 2, Aries stays 1. citeturn20view1turn22view0  
- Sagittarius (empty) has 1 and Pisces (empty) has 2: subtract 1 from both → Sagittarius becomes 0 and Pisces becomes 1. citeturn20view1  

**Important note on “exactness”:**
Some paraphrases of rule (1) in secondary write-ups phrase the “both empty, unequal” case as “make both equal to the smaller number.” citeturn17view0 The worked illustration in the BPHS text flow, however, demonstrates a *difference-preserving* reduction (one becomes zero; the other becomes the difference). citeturn20view1 If you are implementing this in software or audit-checking a program, that discrepancy is exactly the kind of “missing reduction step” bug that changes Shodhya Pinda downstream.

## Sarvashtakavarga transit scoring and Kakshya

### How bindus become a usable “transit score” in practice

A highly operational (and explicitly taught) usage pattern is:

- Use **planet’s own BAV bindus for a sign** to judge whether the planet’s transit through that sign tends to manifest *good vs hard* outcomes. citeturn26view0  
- Use **Sarvashtakavarga (SAV) bindus in the sign/house** as the “environmental support” layer, with an average around **28 bindus per sign** derived from a total of **337 bindus** (with a noted debate about optionally adding Lagna’s 49 to make 386). citeturn25view0turn26view0  

### Threshold tables requested

**Planet BAV threshold table (0–8 scale):**

- **5–8 bindus:** very auspicious  
- **4 bindus:** mixed  
- **0–3 bindus:** not good / difficult citeturn26view0  

A concise “rule form” is also given: planets with **more than 5 bindus** in their ashtakavargas give good results. citeturn25view1

**SAV threshold table (house/sign support layer):**

A widely used operational scale is:

- **Below 25:** weak zone / adverse  
- **25–30:** average / mixed  
- **31+ (or 30+ in many thumb-rules):** favorable / strong citeturn23search28turn23search7turn25view1  

A more “engineering” way the same sources justify these thresholds is: since 337/12 ≈ 28, **28** is “average strength,” below it is weaker support, above it is stronger support. citeturn25view0turn23search28

A key rule statement tying this directly to transit interpretation is: strong planets may fail to deliver favorable results if transiting a house with **less than ~28 bindus**, and conversely weakened planets may not give as bad results if associated with **more than ~28 bindus**; additionally, bhavas with **less than 25** are treated as weak. citeturn25view1

### Ashtakavarga Kakshya (3°45′ sub-divisions): exact computation and how it changes transit quality

In the Kakshya method (explicitly treated as a distinct interpretive chapter in one teaching tradition), **each 30° sign is divided into 8 equal parts of 3°45′**, and the kakshya lords are assigned in the following fixed order: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna. citeturn26view0

**Exact kakshya mapping within any sign:**

| Kakshya segment | Degree span within sign | Kakshya lord |
|---|---|---|
| 1 | 0°00′–3°45′ | Saturn |
| 2 | 3°45′–7°30′ | Jupiter |
| 3 | 7°30′–11°15′ | Mars |
| 4 | 11°15′–15°00′ | Sun |
| 5 | 15°00′–18°45′ | Venus |
| 6 | 18°45′–22°30′ | Mercury |
| 7 | 22°30′–26°15′ | Moon |
| 8 | 26°15′–30°00′ | Lagna citeturn26view0 |

**How to use it (exact computation pipeline):**

1. Take the transiting planet’s longitude, identify its sign, then compute its intra-sign degree (0°–30°). citeturn26view0  
2. Map that intra-sign degree to the kakshya segment above, giving the **kakshya lord**. citeturn26view0  
3. Consult the **Prastara (contribution) Ashtakavarga** of the transiting planet for that sign to see whether the kakshya lord contributed a bindu in that sign. citeturn26view0  
4. If the kakshya lord **contributed a bindu**, the transit through that kakshya is taken as **good**; if that kakshya is **binduless**, the transit is taken as **harmful/difficult**. citeturn26view0  
5. A second-order refinement is stated: if the transiting planet and kakshya lord are friends, results improve; if enemies, results worsen. citeturn26view0  

This gives you a very literal “micro-timing” lever: a planet can be in the same sign for weeks/months, but its kakshya transitions subdivide that sign into discrete windows whose quality depends on bindu support from specific contributing lords. citeturn26view0