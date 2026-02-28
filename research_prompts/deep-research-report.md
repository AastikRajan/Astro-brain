# Missing Dasha Systems and Natal Yoga Rules

## Scope, notation, and source discipline

This report focuses on the *mechanics* (how to compute periods) for the requested dasha systems and the *formation rules* (how to test conditions) for the requested natal yogas. It uses primary-text translations where they explicitly specify procedures (especially for: Chara Dasha as a sign-dasha in entity["book","Brihat Parashara Hora Shastra","r santhanam english tr"]; Sudarshana Chakra; Ashtottari; and Kalachakra), plus a sutra-based translation for the “odd/ even counting + exceptions” rule (entity["book","Jaimini Sutras","b suryanarain rao tr"]), and a worked “ruleset” style treatment of Narayana Dasha (entity["book","Narayana Dasa","sanjay rath pdf"]). citeturn14view1turn18view1turn21view1turn30view2turn25view1

Two cautions are necessary up front.

First, **many of these systems exist in multiple lineages / implementations** (and sometimes the *same name* is used for slightly different rule sets). Where the classical translation gives an explicit rule, that is treated as the anchor; where the tradition is known to diverge, I label the divergence as an “implementation fork” instead of presenting a single blended rule as if it were unique. citeturn14view1turn30view3turn25view4

Second, **“strength / scoring” language is often post-classical**. For Sudarshana triple convergence and strength scoring of parivartana/vipareeta yogas, the classical texts mostly provide *formation* conditions and qualitative results; numeric scoring is therefore presented as an explicit, reproducible *analytic overlay* rather than as a claimed classical formula. citeturn18view1turn37search21turn36view0

## Jaimini Chara Dasha

### What “Chara Dasha” means here

In entity["book","Brihat Parashara Hora Shastra","r santhanam english tr"], “Chara Dasha of the signs” is defined as a rashi-based dasha where the **duration in years of each sign** is computed by counting from the sign to the sign occupied by its lord, with a distinctive **pada parity rule** that changes the counting direction for groups of signs. citeturn14view1turn13view1turn14view2

Separately, the sutra tradition (as translated in entity["book","Jaimini Sutras","b suryanarain rao tr"]) provides a general rule: **odd signs count forward; even signs count backward**, followed by an explicit “not always” exception statement that *names* Taurus, Scorpio, Aquarius, and Leo as exceptions to the simple odd/even direction rule. citeturn30view2turn30view3

These two sources line up conceptually (direction depends on a parity classification), but they encode parity differently (BPHS uses “padas” in trines-of-sign groups; Jaimini uses odd/even signs with named exceptions). Because your question explicitly asks about **exception conditions**, the algorithm below is written as a “core + selectable exception layer.”

### Step-by-step algorithm from BPHS (core rule set)

**Inputs**
- Rasi positions of the lords of each sign (including special handling for Scorpio and Aquarius).
- Exaltation/debilitation status of planets in each sign (for ±1 year adjustment).
- Ascendant sign and the sign in the 9th from Ascendant (to decide the *order* of the dashas). citeturn14view1turn14view2turn13view1

**Step A: Determine counting direction for *duration* via “pada”**
BPHS states: “every three signs from Aries etc. have four Padas,” and:
- For **odd Padas (1, 3)**: count **forward** from the sign to the sign occupied by its lord.
- For **even Padas (2, 4)**: count **reverse**. citeturn14view1

Operationally, you must be able to map each sign to “odd-pada vs even-pada” as used in this scheme (software implementations usually encode this mapping directly because it is a fixed classification). citeturn14view1turn13view1

**Step B: Handle dual-lord signs**
BPHS explicitly makes:
- Scorpio dual-lorded by Mars and Ketu,
- Aquarius dual-lorded by Saturn and Rahu. citeturn13view1turn14view1turn14view2

For Scorpio/Aquarius, BPHS then gives a multistep tie-breaking and “stronger sign” rule to decide which lord (and hence which destination sign) is used for the count:
- If both lords are in their own signs → **12 years**.
- Otherwise: count from the sign to the sign occupied by its lord.
- If lords occupy different signs: count up to the **stronger** sign.
- “Stronger sign” is decided by (in order): a sign containing any planet is stronger than empty; more planets wins; if equal, sign-type strength (dual > fixed > movable); if still equal, “bigger number” sign. citeturn13view1turn14view2

**Step C: Apply exaltation/debilitation year adjustment**
BPHS says:
- If one sign is occupied by a planet in exaltation, count up to that sign (in the Scorpio/Aquarius dual-lord decision logic),
- Then **+1 year** for a sign with an exalted planet,
- **−1 year** for a sign with a debilitated planet. citeturn13view1turn14view2

**Step D: Determine *sequence order* of mahadashas from Ascendant**
BPHS gives the ordering switch:
- If the sign in the **9th from Ascendant** is in an **odd pada**, count the dasha order “from the sign in the Ascendant onwards.”
- If that 9th sign is in an **even pada**, the order is **reverse**. citeturn14view2

BPHS also illustrates that after the 12-sign run completes, the sequence repeats from the start sign. citeturn14view2

### Exception overlay from Jaimini Sutras (odd/even + named reversals)

The sutra translation states:
- “In all odd signs the counting must be in the right direction” and
- “In even signs the counting must be in the reverse order,”
- then adds “In some places or signs this does not apply,” and the commentary explicitly says:
  - even fixed signs **Taurus and Scorpio** count forward (not reverse),
  - odd fixed signs **Aquarius and Leo** count backward (not forward). citeturn30view2turn30view3

If you choose to implement a **“sutra-override mode”** for duration counting, apply these sign-specific reversals after deciding direction by odd/even.

### Pseudo-code

```pseudo
# Sign indices: 1..12 (Aries..Pisces); wrap with mod12.
# chart.lord_sign[s] gives sign index where lord of sign s is placed (for Scorpio/Aquarius may return 2 lords)
# chart.planets_in_sign[s] gives list of planets in sign s and their dignity (exalt/debil/normal)

function chara_dasha_schedule(chart, mode):
    start_sign = chart.asc_sign

    # Determine dasha ORDER direction from BPHS rule using 9th-house pada parity:
    ninth_sign = sign_from(start_sign, +8)  # 9th from asc
    order_dir = (is_odd_pada(ninth_sign) ? +1 : -1)  # BPHS 46.167

    # Build the ordered sign sequence of 12 dashas:
    seq = []
    s = start_sign
    for i in 1..12:
        seq.append(s)
        s = sign_from(s, order_dir)

    # Compute durations sign-by-sign:
    durations_years = dict()
    for s in seq:
        durations_years[s] = chara_dasha_years_for_sign(chart, s, mode)

    # Convert to timeline by accumulating from birth time:
    return accumulate(seq, durations_years, chart.birth_datetime)

function chara_dasha_years_for_sign(chart, s, mode):
    # Determine direction for COUNTING (duration):
    if mode.uses_bphs_pada_rule:
        count_dir = (is_odd_pada(s) ? +1 : -1)  # BPHS 46.155-156
    else:
        # sutra baseline
        count_dir = (is_odd_sign(s) ? +1 : -1)  # JS 1.1.25-26

        # sutra exceptions (JS 1.1.27 commentary):
        if s in {Taurus, Scorpio}: count_dir = +1
        if s in {Leo, Aquarius}:   count_dir = -1

    # Identify controlling "lord destination" sign for the count:
    if s == Scorpio or s == Aquarius:
        dest = choose_stronger_dual_lord_destination(chart, s)  # BPHS 46.157-166
    else:
        dest = chart.lord_sign[s]

    # Count number of signs from s to dest in count_dir, inclusive of dest, exclusive/inclusive per implementation.
    # BPHS describes "reckoned from the Rashi up to the house in which its lord is posited";
    # Many implementations set years = number_counted (with own-sign as 12 in some variants).
    years = count_signs(s, dest, count_dir)

    # Apply exalt/debil adjustment:
    if sign_has_exalted_planet(chart, s): years += 1
    if sign_has_debilitated_planet(chart, s): years -= 1

    # Guardrails:
    years = clamp(years, 1, 12)

    return years
```

This pseudo-code corresponds to the explicit BPHS “pada” method for Chara Dasha (including dual-lord rules for Scorpio/Aquarius and ±1 year dignity adjustments) plus an optional sutra-based direction override layer. citeturn14view1turn14view2turn30view2turn30view3

## Sudarshana Chakra

### The three-wheel structure and when the method applies

BPHS defines Sudarshana Chakra as **three concentric circles**, each divided into 12 houses:
- inner circle: houses from the **Ascendant** with planets placed,
- middle circle: houses from the **Moon sign** with planets,
- outer circle: houses from the **Sun sign** with planets;
so “there will be 3 rāśhis in each Bhava” of the chakra. citeturn16view1

BPHS also gives a **use-condition**: declare results according to Sudarshana Chakra only when the **Sun and Moon are in separate signs different from the Ascendant sign**; if two of the three (Ascendant/Sun/Moon) share the same sign, judge from the birth chart instead. citeturn18view0turn18view1

### The “dasha-like” timing: year, month, day

BPHS then provides a deterministic timing scheme:
- Each of the 12 houses gets a **one-year** “Dasha period” in a repeating 12-year cycle: Year 1 → House 1 acts as Ascendant-of-year; Year 2 → House 2 acts as Ascendant-of-year; …; Year 12 → House 12 acts as Ascendant-of-year. citeturn18view1
- Within each year, each house gets an **Antardasha of one month** (12 months covering 12 houses, each taking the role of month-ascendant in turn). citeturn18view1
- Each house also gets a **Pratyantar** of 2½ days and a **Vidasha** of 12½ ghatikas, using the same “house becomes ascendant” logic at finer granularity. citeturn18view1turn18view2
- BPHS notes the system uses **solar months** for these computations. citeturn18view2

### “Agreement of all three wheels” as a computational object

Given the architecture, any time-slice activates:
- a **house index** (e.g., House 10 for that year/month/day slice),
- and within that house index you have **three concurrent rāśis**: one from the Lagna wheel, one from the Moon wheel, one from the Sun wheel. citeturn16view1turn18view1

So “all three wheels agree” cannot mean “all three produce the same rāśi” (because that would force Sun/Moon/Lagna sign identity, which BPHS says invalidates Sudarshana use). Instead, the operational definition that matches the classical setup is:

**Triple agreement = the active house’s indication is consistent across all three wheels**, when you independently evaluate that house’s condition in each circle (occupancy/aspects/benefic-malefic majority and lordship fallback). citeturn16view2turn18view1turn18view2

### A reproducible scoring formula for triple convergence

BPHS gives the qualitative evaluation rules:
- A house advances if occupied/aspected by its lord or by benefics; harmed if occupied/aspected by malefics; if both act, majority (or stronger planets if tied) decides; if no planet aspects/occupies, judge by the house lord. citeturn16view2turn16view1
- Additional rule-of-thumb placements at dasha start: benefics in certain relative houses produce favorable effects; Rahu/Ketu alone in a house is harmful; malefics in 3/6/11 from the active ascendant can be favorable (a standard upachaya logic embedded into this Sudarshana method). citeturn18view2

A scoring overlay consistent with those instructions:

Let `wheel ∈ {Lagna, Moon, Sun}`.

1. For the active time-slice (year-house, month-house, etc.), compute a wheel-specific **house score**:
   - `+1` if the house is occupied or aspected by benefic(s),
   - `−1` if occupied or aspected by malefic(s),
   - If both: use majority; if tied: break by relative planet strength (BPHS says stronger decides in ties). citeturn16view2turn18view2

2. Define **triple convergence** at that time slice as:
   - `TC = 1` if all three wheel scores have the same sign (all ≥0, or all ≤0) *and* at least two are non-zero (i.e., not “all neutral by lord fallback”),
   - else `TC = 0`.

3. Define a numeric **triple convergence score**:
   - `Score = wY*(|S_L|+|S_M|+|S_S|) + wTC*TC`
   - default weights: `wY=1`, `wTC=2` for year-level analysis; for month-level, use `wY=0.5`. (These weights are not classical; they’re an explicit analytic choice.)

Mechanically, this gives you a sortable list of “high agreement” years/months that directly corresponds to BPHS’s stated evaluation logic, without claiming a classical numeric formula. citeturn18view1turn16view2turn18view2

## Ashtottari Dasha (108-year cycle)

### Applicability trigger vs Vimshottari

BPHS states Ashtottari is to be known when **Rahu is not in Lagna and is not in any other Kendra or Trikona from the Lagna lord** (the text’s phrasing is compact; implementations typically evaluate Rahu’s placement relative to Lagna and the Lagna lord’s kendra/trikona axis). citeturn32view1

BPHS also explicitly links suitability to lunar fortnight/time conditions: it notes applicability for births “at day in Krishna Paksha or at night in Shukla Paksha.” citeturn20view1

### Planet sequence and years per planet

BPHS gives the eight dasha lords (excluding Ketu) in order:
**Sun → Moon → Mars → Mercury → Saturn → Jupiter → Rahu → Venus**. citeturn32view1turn32view3

It then gives the durations (years):
- Sun 6
- Moon 15
- Mars 8
- Mercury 17
- Saturn 10
- Jupiter 19
- Rahu 12
- Venus 21  
Total = 108 years. citeturn32view3turn32view2

### “Nakshatra trigger condition” and how to map nakshatra → starting dasha lord

BPHS defines the nakshatra grouping by a repeating **4–3–4–3–4–3–4–3** partition starting from Ardra for Sun (with Abhijit treated specially as an intercalary segment between Uttarashada and Shravan). citeturn32view1turn32view3turn32view2

The table in BPHS shows the functional sequence (example reconstruction aligned to the table ordering):
- Sun: Ardra, Punarvasu, Pushyami, Ashlesha
- Moon: Magha, Purva Phalguni, Uttara Phalguni
- Mars: Hasta, Chitra, Swati, Vishakha
- Mercury: Anuradha, Jyeshtha, Moola
- Saturn: Purva Ashadha, Uttara Ashadha (+Abhijit handling), Shravan, Dhanishta
- Jupiter: Shatabhisha, Purva Bhadrapada, Uttara Bhadrapada
- Rahu: Revati, Ashwini, Bharani, Krittika
- Venus: Rohini, Mrigashira, Ardra (loop closes) citeturn32view3turn32view2

### Balance at birth: explicit formula

BPHS states the expired portion is computed like Vimshottari using:
- `Expired = Bhayat × (DashaPortion_of_JanmaNakshatra) / Bhabhog`
- Balance = (full dasha length) − expired. citeturn32view2

It also gives special handling for Uttarashada/Abhijit/Shravan in defining Bhabhog/Bhayat for those segments. citeturn32view2turn32view3

### Pseudo-code

```pseudo
function is_ashtottari_applicable(chart):
    # BPHS condition summarized: Rahu not in Lagna; and not in kendra/trikona from Lagna-lord
    L = chart.asc_house
    rahu_house = house_of(chart.rahu)
    lagna_lord_house = house_of(lord_of(chart.asc_sign))
    if rahu_house == L: return false
    if is_kendra_or_trikona_from(rahu_house, lagna_lord_house): return false
    return true

function ashtottari_starting_lord(janma_nakshatra_segment):
    # Use BPHS table mapping; handle Abhijit interpolation per BPHS notes
    return lookup_ashtottari_lord(janma_nakshatra_segment)

function ashtottari_balance_at_birth(chart):
    lord = ashtottari_starting_lord(chart.janma_nakshatra_segment)
    full_years = ASHTOTTARI_YEARS[lord]
    portion_years = dasha_portion_years_of_this_nakshatra(lord)  # 1/4 malefic, 1/3 benefic
    expired = chart.bhayat * portion_years / chart.bhabhog
    balance = full_years - expired
    return (lord, balance)
```

The sequence and durations, the 1/4 vs 1/3 nakshatra-portion rule, and the Bhayat/Bhabhog formula are explicitly stated in BPHS. citeturn32view1turn32view2turn32view3

## Kalachakra Dasha

### Core idea: Moon’s nakshatra pada selects a “pada program”

BPHS frames Kalachakra Dasha as a system where you prepare two charts, **Savya** and **Apsavya**, each of 12 apartments, and then incorporate nakshatras and their padas in defined ways; the Deha (body) and Jeeva (life) signs for the Moon’s nakshatra pada determine the dasha lord sequence. citeturn19view1turn19view2turn21view1

### Savya vs Apsavya construction (direction rule)

BPHS instructs:
- **Savya**: from the 2nd apartment place signs **Aries onward**,
- **Apsavya**: from the 2nd apartment place signs **from Scorpio onward in reverse order** (Scorpio, Libra, Virgo, …). citeturn19view1turn19view3

This is the concrete “forward/backward” rule you asked for: savya is Aries-forward; apsavya is Scorpio-reverse for the chart layout itself. citeturn19view1turn19view3

### Period lengths: fixed dasha years per sign

BPHS gives the base year values (via the sign lords’ years) and then a direct sign table. The planet-year list is:
Sun 5, Moon 21, Mars 7, Mercury 9, Jupiter 10, Venus 16, Saturn 4. citeturn21view1

The resulting sign-year table shown in BPHS is:
- Aries 7
- Taurus 16
- Gemini 9
- Cancer 21
- Leo 5
- Virgo 9
- Libra 16
- Scorpio 7
- Sagittarius 10
- Capricorn 4
- Aquarius 4
- Pisces 10 citeturn21view1turn21view2

### Exact “pada-to-dasha-sequence” programs

BPHS provides explicit sequences for the four padas of Ashwini (Savya prototype) and Rohini (Apsavya prototype), and then states other nakshatras reuse these programs. citeturn19view2turn19view3turn21view0

I’ll present this as **program tables** that you can implement.

#### Savya program (as exemplified by Ashwini)

For the **1st pada of Ashwini**, BPHS states:
- Deha = Aries, Jeeva = Sagittarius,
- Dasha lords are the lords of the **nine signs Aries → Sagittarius** in order. citeturn19view2

So the rashi sequence is:
`Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius`

For the **2nd pada of Ashwini**, BPHS states:
- Deha = Capricorn, Jeeva = Gemini,
- Dasha lords are the lords of the nine signs **Capricorn → Gemini**. citeturn19view2

So the rashi sequence is:
`Capricorn, Aquarius, Pisces, Aries, Taurus, Gemini` plus the intermediate 9-sign chain explicitly implied by “from Capricorn to Gemini” (i.e., `Capricorn, Aquarius, Pisces, Aries, Taurus, Gemini` is only 6; the full 9 is `Capricorn, Aquarius, Pisces, Aries, Taurus, Gemini` plus preceding? In practice, implement as the zodiacal run from Deha to Jeeva inclusive, length 9 as BPHS states). citeturn19view2turn21view1

For the **3rd pada of the 10 nakshatras beginning Ashwini**, BPHS gives a *nonlinear* rashi list explicitly:
`Taurus, Aries, Pisces, Aquarius, Capricorn, Sagittarius, Aries, Taurus, Gemini` (and then the corresponding planetary lords in order). citeturn19view2

For the **4th pada** (10 nakshatras beginning Ashwini), BPHS states:
- Deha = Cancer, Jeeva = Pisces,
- Dasha lords are lords of the nine signs **Cancer → Pisces**. citeturn19view2

So the rashi sequence is:
`Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces` citeturn19view2

BPHS then states that multiple other nakshatras’ padas in Savya chakra “should be reckoned in the same manner as the padas of Ashwini” (explicitly listing several). citeturn19view2

#### Apsavya program (as exemplified by Rohini)

BPHS instructs that Apsavya chakra is laid out starting Scorpio backward, and then states Deha/Jeeva and dasha lord sequences for Rohini padas; additionally it says Deha/Jeeva for Rohini, Makha, Vishakha, and Sravana follow the Rohini scheme. citeturn19view3

The text then provides explicit Deha/Jeeva and lord-sequences for Rohini padas (1–4), analogous to the Ashwini presentation. citeturn19view3turn21view0

### Implementation note

Because BPHS sometimes expresses sequences as “lords of the nine signs from X to Y” (which requires you to know the intended traversal direction and fixed length 9), and sometimes lists signs explicitly (as in the 3rd pada Savya case), a robust implementation should:
- treat “explicit rashi list” as authoritative when present,
- otherwise generate the 9-sign run by stepping zodiacally from Deha to Jeeva until 9 signs are collected (and validate against expected sign-year totals). citeturn19view2turn21view1

## Narayana Dasha and Yogini Dasha sub-periods

### Narayana Dasha

#### Starting sign (Arambha Rasi)

entity["book","Narayana Dasa","sanjay rath pdf"] states the Narayana dasha begins from the **stronger of the Ascendant and the 7th house** (rule attributed to entity["people","Sanjay Rath","jyotish author"]’s sutra discussion), rejecting gender-based deviations as “not within the rule.” citeturn25view1

#### Dasha duration per sign (years)

The same source gives:
- If the sign is **Vimsapada (odd-footed)**, count **zodiacally** from the sign to the sign occupied by its lord;
- If **Samapada (even-footed)**, count **reverse**;
- “The count is from the sign to that occupied by its lord and is reduced by one.” citeturn23view1

It also imports BPHS-style tie-breaking and dignity adjustments in worked examples (±1 year for exaltation/debility within the first cycle), and uses the “second cycle is 12 − first cycle” idea where longevity exceeds the first 12-sign run. citeturn25view0turn23view2

#### Dasha sequence (order of signs)

The same text gives a classical Jaimini-sutra-driven sequence logic:
- If starting sign is **movable**, the dasa is “regular” (sequential). citeturn25view2  
- If starting sign is **fixed**, the next dasa is the sign in the **6th** and so on. citeturn25view2  
- If starting sign is **dual**, follow the trines (5th/9th) then 10th and its trines, repeating until all signs are covered. citeturn25view3  

It also states a direction switch rule (attributed back to BPHS 46.167): whether succession is zodiacal or reverse depends on the **9th house sign** being Vimsapada vs Samapada. citeturn25view3turn14view2

#### Antardasha sub-periods

The text gives a clear “equal division” rule:
- divide the dasa period into **12 equal antardashas** of the 12 signs (each = 1/12 of mahadasha),
- direction depends on whether the dasa sign (or its lord) is in an odd vs even sign; the notes emphasize this is about odd/even, not Vimsapada/Samapada classification. citeturn23view3

It also provides exceptions:
- If Saturn is in the starting sign, succession becomes regular and the “9th-house basis” is not used in the same way; antardasha direction becomes zodiacal. citeturn25view4
- If Ketu is in the dasa sign, movement is “Vipareetam” (opposite), reversing indicated direction for dasa/antardasa. citeturn25view4

### Yogini Dasha sub-periods

BPHS gives the Yogini mahadasha scheme: eight Yoginis, their lord-planets, and their year-lengths summing to 36 years. citeturn6view2

For **antardasha math**, classical sources often don’t spell an explicit fractional formula the way Vimshottari does; the dominant computational convention (used in many teaching documents) is proportional division over the 36-year cycle:
- `AD_years = (MD_years × sub_yogini_years) / 36`
Equivalently, under a 360-day year convention:
- `AD_days = MD_years × sub_yogini_years × 10` (because 360/36 = 10). citeturn10search2turn6view2

That formula is **proportional**, not fixed; all eight antardashas occur within each mahadasha in Yogini order starting from the mahadasha yogini (a standard proportional-dasha recursion). citeturn10search2turn6view2

## Missing natal yoga rules

### Neecha Bhanga Raja Yoga

entity["book","Mantreswara's Phaladeepika","v subrahmanya sastri tr"] gives a clear five-fold classical list of Neechabhanga Raja Yoga mechanisms, and also provides verse-style statements that match those mechanisms (e.g., “debil planet aspected by lord of the debility sign” cancels debility; “debil planet in kendra from Lagna or Moon” cancels, etc.). citeturn36view0

The five conditions (Phaladeepika summary list) are:

- The lord of the debility sign **or** the planet exalted in that sign is in a **kendra** from Lagna or Moon. citeturn36view0  
- The lord of the debility sign and the lord of the exaltation sign of the debilitated planet are **mutually in kendras**. citeturn36view0  
- The debilitated planet is **aspected by the lord** of the sign it occupies (its debility sign). citeturn36view0  
- The lord of the debility sign **or** the lord of the exaltation sign is in a **kendra** from Lagna or Moon (Phaladeepika lists this as a distinct enumerated item, functionally overlapping the first; lineages treat (1) and (4) as two presentations of “dispositor/exaltation-lord kendra” logic). citeturn36view0  
- The debilitated planet itself is in a **kendra** from Lagna or Moon. citeturn36view0  

**Strength boost / stacking:** Phaladeepika’s text is qualitative (“powerful king of kings,” “wealthy emperor,” etc.) and does not present a numeric “boost.” The mechanism-first way to treat stacking is: multiple independent cancellation routes increase confidence that the debilitated planet’s *functional capacity* is restored; but whether this rises to “raja yoga” depends on the planet’s house lordship context and wider yoga network (a standard interpretive constraint, stated in many traditions but not as a numeric factor in these verses). citeturn36view0

### Vipareeta Raja Yoga

A key methodological issue: in the sources retrieved here, the “Vipareeta Raja Yoga” label is primarily given in modern explanatory literature rather than as a verbatim classical verse under that exact heading; modern sources consistently define it as **dusthana lords (6th/8th/12th) placed in other dusthanas**, producing rise after adversity, with three named variants: Harsha, Sarala, Vimala. citeturn37search0turn37search3turn37search6

Mechanism-first formation test (modern consensus definition):
- Harsha: 6th lord connected to (placed in) 6/8/12 (variant definitions differ by author).
- Sarala: 8th lord connected to 6/8/12.
- Vimala: 12th lord connected to 6/8/12.
Power increases when the dusthana-lords are *strong by dignity* and when the producing dusthana is not simultaneously afflicted by major benefic-lord “cancellation clauses” (some modern authors warn of such cancellations). citeturn37search0turn37search20turn37search6

**When powerful vs weak (mechanistic criteria consistent with the definition):**
- Powerful: dusthana lord strong (own/exaltation, strong shadbala, unafflicted), and the dusthana placement is “clean” (not simultaneously binding key kendras/trikonas into dusthana damage), and the yoga times in dasha (because dusthana transformations are timing-sensitive). citeturn37search0turn37search20turn37search3  
- Weak: dusthana lord debilitated *without cancellation*, heavily combust/afflicted, or the “dusthana-to-dusthana” condition exists but is overwhelmed by simultaneous daridra/arishta configurations (modern commentators explicitly debate how fully the “sting” disappears). citeturn37search6turn37search35  

Because these are not retrieved as direct classical verses in the current source set, the above is presented as a consistent computational definition rather than as a text-critical reconstruction of a specific classical passage. citeturn37search0turn37search6

### Parivartana Yoga

A strong classical anchor exists here: the Phaladeepika “Yoga chapter” provides an explicit definition and classification.

Phaladeepika defines Parivartana as mutual exchange of houses/signs between two bhava lords and states there are 66 such interchanges, then classifies:
- **Dainya**: exchanges involving lords of 6/8/12 (counted as 30).
- **Khala/Kahala**: those involving the 3rd lord (counted as 8).
- **Maha**: the remainder (i.e., exchanges not falling into the above). citeturn37search21turn37search17

BPHS also explicitly treats **exchange between an angular lord and a trinal lord** as yoga-producing (royal/fame-producing), which is the conceptual core behind why Maha-type exchanges (when involving auspicious houses) are ranked stronger. citeturn35view3

**Strength scoring (analytic overlay consistent with classical classification):**
- Base class score: Maha = +2, Kahala/Khala = +1, Dainya = −1 (because Dainya is explicitly “dainya” = difficulty/weakening in the classification). citeturn37search21turn37search4  
- Add dignity score per exchanging planet: exaltation/own/friend +1; debility/enemy −1 (classical texts discuss dignity effects broadly; specific numeric scoring is a modern overlay). citeturn34view4turn36view0  
- Add house-functional score: if exchange connects a trinal lord with a kendra lord, add +1 (BPHS explicitly states such relationships cause yoga). citeturn35view3  

**Prediction differences by type (mechanism-first):**
- Maha: tends to consolidate and elevate the portfolios of both houses (status + resources).
- Dainya: tends to “import” dusthana themes (debts, disease, loss, obstacles) into the partner house, even if the dusthana lord itself gains leverage.
- Kahala/Khala: tends to mix resilience, struggle, initiative, and “effort-based” results (3rd house themes) into the partner house’s outcomes. citeturn37search21turn37search4  

### Kartari Yoga

One clear computational definition across modern/classical-derivative sources is:

- **Papakartari**: a bhava (or a planet) is “hemmed in” when the **2nd and 12th from it** are both occupied by natural malefics.
- **Shubhakartari**: similarly, hemmed by benefics. citeturn37search30turn37search11turn37search26

BPHS (in a later discussion) also uses a specific “Kartari yoga” phrasing in an example gloss (direct malefic planets in 12th and retrograde malefic in 2nd), which is consistent with the same 12th/2nd hemming geometry (the retrograde detail is an interpretive add-on in that example’s framing). citeturn34view3

**Does it apply to signs or houses?** Operationally, it applies to the **house positions** (2nd/12th relative to the target house), but because houses are anchored to signs in whole-sign frameworks, most implementations compute it as “adjacent signs/houses around the target.” The invariant geometric object is “one behind and one ahead” of the target. citeturn37search30turn37search26

**How it modifies results:** Mechanically, it acts like a constraint (papakartari) or support (shubhakartari) layer on the target house/planet’s ability to deliver its significations, often interpreted as pressure vs protection. citeturn37search30turn37search11turn37search26

### Kesari Yoga variants

BPHS provides a stricter variant called **Gaja-Kesari Yoga**:
- Jupiter in an **angle (kendra)** from Ascendant *or* from Moon,
- and Jupiter is conjunct or aspected by a benefic,
- while avoiding debilitation, combustion, and inimical sign. citeturn34view4

The same BPHS passage also discusses variant traditions:
- a common variant: Jupiter in kendra from Moon (often called Kesari),
- additional variant: Moon aspected by Mercury/Venus/Jupiter with the aspecting planet free from debility/combustion (attributed to another text tradition in the commentary). citeturn34view4

So, **“Jupiter aspecting Moon”** can count in some variants (as an “aspect-based Kesari” definition), but the BPHS verse quoted above makes *kendra placement* the primary geometry and requires benefic support plus lack of affliction. citeturn34view4

### Dhana yogas

#### What the classical texts in-hand explicitly provide

Both BPHS and Saravali give a concrete “Dhana Yoga” rule in the lunar-yoga context:

If benefics occupy upachayas (3/6/10/11) from the Moon, wealth results scale with how many benefics participate (3 → great; 2 → moderate; 1 → little). citeturn34view5turn36view1turn34view7

BPHS also explicitly notes that an **exchange between the lords of the 11th and 2nd** is “a very powerful Dhana yoga.” citeturn34view5

More broadly, BPHS states that exchange or strong linkage between an **angular lord and a trinal lord** is yoga-producing (kingship/fame), which is a core mechanism behind “high-power wealth” yogas when the 2nd/11th also participate. citeturn35view3

#### The unresolved “32 dhana yogas” request

Within the sources retrieved in this session, I did not find an explicit canonical enumerated list titled “32 Dhana Yogas” across BPHS + Phaladeepika + Saravali that I can quote or reproduce verbatim without overreach. I did find (separately) that Saravali explicitly enumerates **32 Nabhasa yogas**, not 32 dhana yogas. citeturn36view1

So, what can be stated reliably from the in-hand primary translations is:
- at least one named “Dhana Yoga” rule (benefics in upachayas from Moon) appears in both BPHS and Saravali, and
- at least one “power Dhana yoga” exchange (2nd ↔ 11th lords) is explicitly flagged in BPHS. citeturn34view5turn36view1

If you want the exact “32 Dhana Yogas” list you referenced, the next mechanically correct step would be to anchor it to the exact chapter/verse locus in a classical translation that enumerates them as a set (because “32” is often attached to other yoga corpora like Nabhasa). With the current retrieved primary passages, I can’t honestly claim to have that exact 32-item classical list fully in hand. citeturn36view1turn34view5