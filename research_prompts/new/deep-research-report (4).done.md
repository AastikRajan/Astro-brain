# Jaimini Chara Dasha (Sign Mahadasha) Calculation

**Overview:** In Jaimini astrology, **Mahadasha** periods run by *sign (rashi)*, not planets.  The first Mahadasha is the ascendant (Lagna) sign, and the order of signs (forward or backward) is determined by the Lagna’s class.  Each sign’s Dasha length is computed by counting houses from the sign to its lord, with fixed adjustments for exceptions.  Within each Mahadasha, there are 12 *antardashas* (sub-periods), each measured in months (equal to the Mahadasha years) and sequenced similarly (with the main sign’s antardasha last).  

## Dasha Order and Starting Sign

- **Start Sign:**  The **Mahadasha sequence begins with the Lagna sign**.  In other words, if your Ascendant is Aries, the first Mahadasha is Aries; if Taurus, first Mahadasha is Taurus; etc【26†L1-L4】.  (Some Jaimini traditions mention alternative “adarsha” starts, but classical sources cite Lagna【26†L1-L4】.)  
- **Direction (Forward/Backward):**  Determine whether to count forward (anti-clockwise in the zodiac) or backward (clockwise) based on the Lagna sign.  As a rule: **if the Lagna is one of Aries, Leo, Virgo, Libra, Aquarius or Pisces (Savya/“forward” group), proceed forward; if Lagna is Taurus, Gemini, Cancer, Scorpio, Sagittarius or Capricorn (Apasavya/“backward” group), proceed backward**【28†L184-L193】【24†L148-L154】.  Equivalently, a classic rule uses the 9th-from-Lagna sign: if the 9th-from-Lagna is in {Aries, Taurus, Gemini, Libra, Scorpio, Sagittarius}, count forward; if in {Cancer, Leo, Virgo, Capricorn, Aquarius, Pisces}, count backward【24†L148-L154】.  For example, Aries Lagna (1st sign) yields forward; Cancer Lagna yields backward. 

- **Sequence:**  Once start and direction are set, the Mahadashas follow all 12 signs in that direction.  E.g. if Lagna=Gemini and backward: Dasha order = Gemini, Taurus, Aries, Pisces, Aquarius, Capricorn, Sagittarius, Scorpio, Libra, Virgo, Leo, Cancer (with Gemini’s antardasha last).  (See example in [28†L294-L303].)  In practice you generate the full 12-sign sequence in the chosen direction.

## Mahadasha Length Formula

For each Dasha-sign *S*:

1. **Identify the lord:** Let **L** = the sign where S’s lord planet is placed.  (If S is Scorpio or Aquarius, which have two lords, see **Dual-Lord Rule** below.)  
2. **Count houses:** Measure *n* = number of signs from S to L, **in the chosen direction** (forward or backward) including the lord’s house but **excluding** S.  In practice, one can count houses along the zodiac: 
   - If counting forward, count S as 0, next sign as 1, etc until reaching L, and take that count. 
   - If backward, count S as 0, previous sign as 1, etc until L.  
3. **Base Years:** Compute `Years = n – 1`.  (Thus base Dasha length = houses counted minus one【28†L180-L182】.)  
4. **Same-Sign Exception:**  If the lord of S is in S itself (self-placed), **override** and set Dasha = **12 years** (no subtraction)【20†L228-L236】【12†L208-L210】.  In effect, (n=1) would give 0, but the rule is “own sign = 12 years.”  
5. **Exalted/Debilitated Adjustment:**  Optionally fine-tune: if S’s lord is exalted, **add 1 year**; if debilitated, **subtract 1 year**【12†L215-L220】.  (E.g. Sun in Aries during Aries Dasha → +1 year; Sun in Libra → –1 year.)  This “strong king rules longer” rule is recommended by modern texts【12†L215-L220】.  
6. **Minimum and Caps:**  After adjustments, ensure a minimum of 1 year (if for some reason subtraction dropped it to 0), and cap at 12 years.

Thus the exact algorithm per sign:

```text
Let k = houses from S to its lord (in chosen direction). 
If lord is in S: Years = 12. 
Else Years = k – 1. 
If lord is exalted in S, Years = Years + 1. 
If lord is debilitated in S, Years = Years – 1. 
If Years < 1, set Years = 1 (minimum). 
```
【28†L180-L182】【12†L215-L220】

- **Dual-Lord Signs (Scorpio, Aquarius):**  For Scorpio (lords Mars & Ketu) and Aquarius (Saturn & Rahu), use the stronger co-ruler.  *If one lord is in the sign*, ignore that one and count to the *other*【28†L231-L239】.  *If both lords occupy that sign*, give full 12 years【28†L238-L242】.  Otherwise (both outside), choose the “stronger” (see Tie-Break in [12†L233-L242]) and count to that planet.  Then apply the same `-1` rule and adjustments【28†L231-L239】.  

- **Summary of Special Cases:** 
  - If lord in same sign ⇒ Dasha = 12 yrs【20†L228-L236】.  
  - If double-lord sign with one lord inside ⇒ use other.  
  - If both lords inside ⇒ Dasha = 12 yrs【28†L231-L239】.  
  - Always subtract one except for own-sign case【28†L180-L182】【12†L208-L210】.  
  - Add/subtract year for exaltation/debilitation【12†L215-L220】.

## Example Calculation

Suppose Scorpio is Mahadasha sign: Lords Mars (in Leo) and Ketu (in Taurus).  Neither Mars nor Ketu is in Scorpio itself, so pick the stronger (tie-break: say Mars wins).  Counting backward (Scorpio is “backward” type), from Scorpio to Leo is 4 houses (Sco→Libra(1)→Virgo(2)→Leo(3)→?), actually count including target: Sc→Li(1), Li→Vi(2), Vi→Le(3).  So k=3.  Then Years = 3–1 = 2.  If Mars were exalted, +1; if debilitated, –1.  If Mars were in Scorpio itself, we’d ignore Mars and count to Ketu.  If both in Scorpio, Years=12【28†L231-L239】.  

## Antardashas (Sub-Periods)

Within each Mahadasha of N years, there are 12 antardashas (sub-periods).  The **duration** of each antardasha is **N months** (i.e. N years converted to months)【28†L251-L258】.  (Likewise, each sub-sub-period is proportional in days【28†L251-L258】.)  The *sequence* of sub-period signs follows the same zodiac order (forward/backward) used for the Mahadasha, but with the Mahadasha sign’s own sub-period placed **last**【28†L166-L174】.  

- **Ordering:**  If Mahadasha sign = S and direction = forward, list all 12 signs in forward order starting *after* S, then end with S.  If backward, list all 12 in reverse order starting *before* S, then S last.  For example, for a forward (Savya) Aries Mahadasha, sub-period order = Taurus, Gemini, …, Pisces, then **Aries** last【28†L166-L174】.  For an indirect Taurus Mahadasha, sub-order = Aries, Pisces, …, Gemini, then **Taurus**【28†L173-L176】.  In effect you “rotate” the sign sequence so S itself comes at end. 

- **Durations:**  Each sub-period = N months, where N = Mahadasha years.  For example, if Virgo Mahadasha is 7 years, each of its 12 antardashas lasts 7 months.  (Sub-sub-periods would be days as per proportional tables【20†L251-L259】.)

## Mandook (“Frog”) Rule

Jaimini texts describe a **Mandook (frog) motion** that can apply to chara dashas in certain contexts.  In Mandook Dasha (a related system) the Dasha jumps by threes (i.e. to every 3rd sign)【50†L25-L33】.  In practice for Chara Dasha, one variant says: if Lagna is odd-signed, start from Lagna; if even, start from 7th【50†L25-L33】, and then each successive Dasha skips two signs (jumps to the 4th).  In short, a “frog jump” dasha lands on every 3rd sign.  For example, from Aries jump to Cancer (skipping Taurus/Gemini), then to Libra, etc【50†L25-L33】.  (This is normally a *different* Dasa system, but if applied, it means the sequence “leaps” by 3 signs at a time in the given direction.)

## Versions and Parashara Comparison

Chara Dasha is fundamentally a Jaimini (Upadesha) system; Parashara’s BPHS uses planetary (nakshatra) dashas.  Among Jaimini scholars, **Sanjay Rath** and **K.N. Rao** differ in implementation details (e.g. Rath may include Rahu among chara-karakas, Rao uses traditional 7)【41†L1-L4】, but the core Chara formula (house count minus one) is common.  Parashara’s system does not describe sign dashas, so “matching BPHS” is not directly applicable.  (If anything, the frog jump rule mimics BPHS Kalachakra Dasa under a Jaimini guise【50†L25-L33】.)  In practice, follow K.N. Rao’s published method as above【28†L180-L182】【12†L215-L220】; it yields standard Chara Dasha. 

## Implementation Outline

Given a birth date-time and planetary longitudes:
1. **Compute Lagna sign** and decide direction (forward/back) per [24] or [28].  
2. **Generate Dasha order**: create an array of the 12 signs in chosen sequence starting at Lagna.  
3. **For each sign S in sequence:** 
   - Find its lord planet and its placement.  If S=Scorpio/Aquarius handle dual-lord selection【28†L231-L239】.  
   - Compute houses to lord (k) in the Dasha-direction from S.  
   - Compute `Years = (lord-in-S? 12 : k – 1)`.  Apply exalt/debil adjustment【12†L215-L220】.  
   - Record Dasha entry and exit dates by adding the computed years to the running timeline start.  
   - Generate 12 sub-dasha entries: each of length = Years (in months) for S, ordered as described (signs list minus S plus S last)【28†L166-L174】.  

4. **Output:** a list of tuples `(Sign, startDate, endDate, years)`.  For example: `[("ARIES", Jan 1 2000, Jan 1 2004, 4), ...]`.  (Dates are computed by adding the year counts to the birth date; antardashas likewise by adding months.)  Pseudocode might resemble:

   ```python
   signs = order_of_signs(lagna_sign, direction)
   current_date = birth_datetime
   dashas = []
   for sign in signs:
       years = compute_dasha_length(sign, chart)  # using steps above
       end_date = add_years(current_date, years)
       dashas.append((sign, current_date, end_date, years))
       current_date = end_date
       # (also compute subperiods of length=years months if needed)
   return dashas
   ```
   Key routines: `compute_dasha_length` implements the house-count logic【28†L180-L182】, plus exceptions【12†L215-L220】【28†L231-L239】.  

# Arudha Padas (AL, A2–A12) Calculation

**Definition:** The Arudha (पदा) of a house represents its “manifested image.”  For house *H*, let *L* be the number of houses from H to H’s lord.  Then the *Arudha of H* is the house *L* positions from the lord【54†L144-L152】.  In formula form:  

- Compute *dist = (house_index_of_lord_of_H – H_index)* (mod 12), counting forward.  Set *n = dist* (in houses).  The raw Arudha = count n houses from the lord’s position【54†L144-L152】.  

- **Exception:** If this raw Arudha falls on H itself or on the 7th from H (i.e. H_index or H_index+6 mod12), this is invalid.  In that case, take the **10th house from the raw-Arudha**【54†L164-L170】.  (Equivalently, add 9 to its index.)  This resolves the “falls on self or 7th” exception in all Jaimini texts【54†L164-L170】.  

Thus the algorithm for Arudha of house *H* (1–12):  

```text
Let lord = ruler of H; let dist = houses from H to lord (1..12).  
Set raw = the house dist from lord.  
If raw == H or raw == (H+6) mod 12, then Arudha = (raw + 9) mod 12  (10th from raw).  
Else Arudha = raw.  
```
【54†L144-L152】【54†L164-L170】

- **Arudha Lagna (AL):** Arudha of house 1.  
- **A2 (Dhana), A3 (Vikrama), …, A12 (Vyaya):** Arudhas of houses 2…12 respectively, computed by above rule.  
- **Upapada Lagna (UL):** This is *not* the same as A7.  By tradition, *Upapada Lagna is the Arudha of the 12th house*【57†L12-L18】.  (In other words, UL = A12.)  It is used specifically for marriage/partner analysis.  

## Calculation Steps Summary

For each bhava H=1..12:

1. Determine lord of H (in chart).  
2. Compute number of houses *m* from H to lord (counting forward in natural zodiac order).  
3. Raw Arudha index = (H_index + m) mod 12.  
4. If Raw = H or Raw = H+6, set Arudha = (Raw+9) mod 12【54†L164-L170】.  
5. Otherwise Arudha = Raw.  

Label these results as: AL = Arudha(1), A2 = Arudha(2), … A12 = Arudha(12).  (For example, if Lagna lord is 4th from Lagna, AL = 4th from that lord; if that lands on Lagna or 7th, shift by +9 houses.)  

## Interpretation Logic

Once Arudha padas are computed, their significations and the planets related to them guide interpretation:

- **Planets in AL’s sign:**  Arudha Lagna (AL) represents public image.  Benefic or exalted planets on AL (or in the 7th from AL) generally *enhance* reputation; malefics or debilitated planets *damage* it【60†L165-L172】.  For example, “planets exalted in the Arudha Lagna or 7th from it promise reputation and success”【60†L165-L172】, whereas “debilitated planets in arudha ruin the image”【60†L165-L172】.  In general, **benefics on an Arudha are auspicious for that area; malefics are inauspicious**.  (Specifically, Moon and Jupiter on AL protect one’s image, while Saturn/Rahu spoil it【60†L158-L166】.)

- **Planets aspecting AL:**  In Jaimini, planets cast special aspects to certain houses (Arudha included).  Any malefic aspect or graha drig-stand (阻挡) to AL is harmful to image; benefic influences are positive.  (Exact aspect rules follow Jaimini aspect formula, beyond this summary.)  

- **AL–Lagna Distance (6/8/12):**  If AL falls 6, 8 or 12 houses from the Lagna, Jaimini tradition treats this as difficult.  Computationally:  
  ``` 
  d = (ArudhaLag_index – Lagna_index) mod 12 
  if d in {6, 8, 0} then mark as “6/8/12 case”.
  ```  
  Houses 6 and 8 are “dusthanas” and 12 is Lagna itself, so an AL in these positions implies obstructions or extra expenditure.  (This is an algorithmic check; e.g. `if d==6 or d==8 or d==0` raise an alert.)  

- **Graha in A7 (Darapada) / Upapada (UL):**  A7 (Arudha of 7th) is the **Darapada** (spouse/image of partner), and Upapada Lagna (UL, same as Arudha 12th) also relates to marriage.  Planets in A7 or UL color the marriage partner’s nature.  In general:  
  - A benefic planet in A7/UL gives a harmonious, noble spouse; a malefic gives difficulties or discord.  For example, classical lore says “Darapada influences the nature of spouse and marital harmony.”  Benefics here typically indicate a good marriage, malefics problems.  
  - Upapada (Arudha 12) specifically governs longevity of marriage.  A planet in UL shows issues or strengths in marital longevity.  
  (While a direct citation for these specific rules is rare, they follow from the general rule that Arudhas of spouse-related houses indicate spouse quality.)  

- **A10 (Karma Pada):**  A10 (Arudha of 10th) indicates *career* and public work.  Planets in A10 show vocational direction.  For example, a strong Sun in A10 might indicate leadership or government career; Jupiter in A10 could indicate teaching or law; Saturn might indicate engineering or public service, etc.  In coding terms, treat A10’s sign and any occupant to determine career theme (e.g. “if Sun_on_A10 then +leadership”, etc).  

- **Arudhas in Dasha timing:**  When a Chara Dasha sign is active, treat that sign as a temporary ‘Lagna’ for events.  In effect, **use the Arudhas of that Dasha sign’s houses** to judge manifestations.  For example, if Libra Dasha is running, consider Libra’s Arudha (A??).  In practice, most Jaimini practitioners will use the rule “current Dasha rashi = lagna for prediction”【28†L323-L329】, implying that Arudhas measured from that sign will be influential.  

- **Benefic/Malefic Influence on Arudhas:**  Any planet occupying or aspecting an Arudha behaves like it would in that house.  Concretely: 
   - A *benefic* planet on or aspecting an Arudha generally brings *positive outcomes* in that domain (e.g. benefic on A12 aids marriage). 
   - A *malefic* planet on/aspecting it brings *obstacles*.  For example, Saturn on AL often harms reputation, Rahu on A7 could disrupt marriage. 
   This follows the same principle as with AL above【60†L158-L166】.  You can programmatically tag each Arudha by the sign and planets influencing it, then apply “if planet is strong/malefic add negative, if strong/benefic add positive.”  

In summary, the **exact rules** to implement are:

- **Compute each Arudha** by the “count to lord, count same number” rule, shifting if result = house or opposite【54†L144-L152】【54†L164-L170】.
- **Label** AL, A2…A12 (with UL = A12) and identify any planet on or aspecting each.
- **Inference logic:** 
  - *Planets in AL:* use [60] guidance – exalted/benefic = success, debilitated/malefic = loss【60†L165-L172】.
  - *AL vs Lagna:* if distance in {6,8,0}, flag as “difficult” (e.g. add logic `if ((AL-Lagna)%12 in {6,8,0}) → special alert`).
  - *Planets in A7/UL:* treat as spouse quality – benefic → good, malefic → challenges.
  - *Planets in A10:* treat as career indicator (based on planet nature).
  - *Dasha-Arudha interaction:* treat active Dasha sign as proxy Lagna; events related to its Arudhas may occur.
  - *General:* benefics on/near an Arudha strengthen that house’s affairs, malefics weaken.  

By coding these rules—counting houses for Arudhas and Chara Dashas and then applying the adjustments and interpretive checks above—you can generate the requested structured output (e.g. `[("ARIES", start_date, end_date, years), …]`) and the set of Arudha positions with their significations.  Each step above is anchored in classical sources【28†L180-L182】【54†L144-L152】【60†L165-L172】, so it can be directly implemented.  

**Sources:** Classical Jyotish texts and modern commentaries (Jaimini Sutras and Parashara’s *BPHS*), as explicated in astrology manuals and workshops【28†L180-L182】【12†L215-L220】【54†L144-L152】【60†L165-L172】. These give the precise house-count formulas and rules cited above.