# Decision Logic Architecture for a Computational Jyotisha Prediction Engine

## Sources and interpretive framing

This report synthesizes (a) classical-style rule statements on house/judgment, planetary conditions, and transits from entity["book","Phaladeepika","mantreswara jyotisha text"] by entity["people","Mantreswara","jyotisha author"] and entity["book","Saravali","kalyana varma jyotisha text"] by entity["people","Kalyana Varma","sanskrit astrologer"], especially on house assessment, yoga-fruition prerequisites, retrograde strength, and Ashtakavarga/transit logic. citeturn6view7turn6view2turn6view3turn15view5turn15view6turn15view0turn15view1

It also pulls timing logic from entity["book","Brihat Parashara Hora Shastra","parashara jyotisha text"] attributed to entity["people","Parashara","vedic sage jyotisha"]—as preserved in a full-text edition that explicitly states that (i) dasha effects depend on planet strength and (ii) retrograde reverses certain intra-dasha “order of manifestation” rules. citeturn12view1turn12view2turn12view3

For engineer-friendly prioritization heuristics (“what the practicing astrologer checks first”), this report uses the applied methodology of entity["people","B. V. Raman","indian astrologer 1912-1998"] in entity["book","How to Judge a Horoscope","b v raman astrology manual"], because it explicitly enumerates a checklist for judging any house and an explicit priority scheme “house → lord → karaka,” and it also ties “fructification” to dasha/bhukti contexts. citeturn34view0turn34view2turn34view1

For KP-style “promise gates” and day-level materialization, this report uses KP practitioner logic as shown in entity["book","Predictive Stellar Astrology","k s krishnamurti reader 3"] by entity["people","K. S. Krishnamurti","kp astrology founder"] (core “significators and sub-lords” decision logic), plus a worked KP-oriented case-study document (marriage promise + “transit must agree”) that explicitly states the marriage promise gate in terms of house significations (2-7-11). citeturn28view1turn28view3turn29view0turn29view1

Where the classical sources do **not** provide a single formal numeric threshold (common in practice), I translate “strong/weak, blemished/unblemished, destroyed/ensured” style rules into computational gating/scoring primitives. This is justified because both the classical and applied texts *explicitly* treat strength/blemish as a modulator of whether (and how fully) promised effects manifest. citeturn6view0turn6view2turn6view3turn34view0turn34view2

## Promise gating as a first-class module

**Question 1 — The “Promise” gate (Chart Promise vs Timing)**

**Classical/textual sources (if known).**  
A concrete “promise gate” pattern appears explicitly in house-assessment rules within entity["book","Phaladeepika","mantreswara jyotisha text"]: if the *lord of the house* is placed in the 8th, or “eclipsed by the Sun’s rays,” or debilitated, or inimical, and also lacks benefic association/aspect, then the house’s effects are described as “totally destroyed.” citeturn6view7 In applied practice, entity["book","How to Judge a Horoscope","b v raman astrology manual"] gives a generalized rule-checklist for a house (lord strength, house strength, yogas, navamsa/appropriate divisional charts) and insists these must be weighed before deducing results. citeturn34view0turn34view1

**Formal logic in plain English.**  
A computational “promise” gate is best modeled as: **(A) does the natal configuration contain sufficient potential for outcomes in this domain?** Only if yes, do dashas/transits become “timers/triggerers” rather than “manufacturers.” This matches (i) the classical “house effects can be destroyed” language when the lord is severely damaged and unsupported, and (ii) the applied house-judgment checklist approach. citeturn6view7turn34view0

Concretely, an astrologer judging “promise” typically checks whether *primary domain anchors* are viable:  
- the **house** itself (occupants/aspects; benefic vs malefic influences),  
- the **house lord** (placement, strength, afflictions, support),  
- the **domain karaka(s)**, and  
- the **relevant divisional chart** (e.g., Navamsa for marriage). citeturn34view0turn34view2turn44view0turn6view7

**Algorithmic formulation (gate + score).**  
A robust engineering translation is a **two-layer gate**: (1) hard denials (veto), then (2) soft promise score.

**Layer 1: Domain-denial veto (hard gate)**  
For a domain with primary house \(H\) and its lord \(L_H\):  
- Set `domain_promised = False` if **any** hard-denial rule triggers with sufficient severity. The most text-grounded denial clauses are:
  - **House-lord destruction rule:** if \(L_H\) is in the 8th *or* “eclipsed by Sun’s rays” (combust), *or* debilitated, *or* in inimical sign **and** is devoid of benefic association/aspect → “effects totally destroyed.” citeturn6view7turn6view3
  - **Yoga-fruition prerequisite:** if a domain-critical yoga exists but the yoga-forming planets (and lagna/moon framework) are “with blemish,” including **combustion**, then the yoga may not deliver its promised effects fully. (This converts to “don’t allow yoga to override a failed house-lord gate.”) citeturn6view2

In code terms, implement this as a boolean veto computed from your existing “planet condition” primitives: `{combust, debilitated, inimical, in_8th_from_reference, benefic_aspect_support}`.

**Layer 2: PromiseScore (soft gate)**  
If not vetoed, compute a continuous `PromiseScore ∈ [0,1]` and require it exceed a threshold before timing modules contribute large confidence:

\[
\text{PromiseScore}=\sigma\Big(\sum_i w_i\,f_i - \tau\Big)
\]

Where features \(f_i\) include:
- `HouseStrength(H)` (you already have Bhavabala and house cusp data), aligned with “strength of the house itself.” citeturn34view0  
- `LordStrength(L_H)` (Shadbala + Vimshopak Bala + Drik Bala + avastha penalties), aligned with “strength, aspects, conjunctions, and location of the lord.” citeturn34view0turn6view3  
- `KarakaStrength(domain)` (e.g., Venus for marriage), aligned with “house → lord → karaka.” citeturn34view2  
- `DivChartCoherence(domain)` (e.g., D9 confirms/weakens marriage promise), aligned with “consider Navamsa and other appropriate diagrams.” citeturn34view0turn44view0  
- `YogaSupport(domain)` with a **separate** “yoga viability” multiplier requiring “without blemish” (not combust etc.). citeturn6view2  

A practical thresholding strategy consistent with “weighing” language is:
- `domain_promised = PromiseScore ≥ 0.55` (tunable),  
- add a “grey zone” `0.45–0.55` where you produce “possible but constrained / delayed / requires strong timing alignment.” This mirrors applied texts’ emphasis on mixed indications and the need to weigh. citeturn34view0turn34view1

**Known disagreements between schools.**  
Parashari/classical-style house-lord destruction statements can read as **hard** (destroyed) when multiple afflictions stack and benefic support is absent. citeturn6view7 In contrast, applied authors often treat many indicators as **soft** (mitigatable by other strengths / karakas / divisional reinforcements) rather than absolute, emphasizing “weighing.” citeturn34view0turn33view2 KP-style practice often uses **explicit discrete promise gates** (e.g., marriage hinges on whether key cuspal significators connect to specific houses), which produces more veto-like behavior than broad Parashari weighting. citeturn29view0turn28view3

**Question 7 — Domain signification priority (primary vs secondary vs tertiary)**

**Classical/textual sources (if known).**  
An explicit priority order is given by entity["book","How to Judge a Horoscope","b v raman astrology manual"]: “First take the house, then the lord and finally the karaka,” adding that planets associating with/aspecting lord and karaka also matter and periods (dasha/bhukti) determine fructification. citeturn34view2 The same text also says to judge not only Rasi but also Navamsa and other appropriate divisional charts. citeturn34view0

**Formal logic in plain English.**  
For any domain \(D\):  
1) establish the condition of the **house(s)** that naturally rule \(D\),  
2) then evaluate the **house lord(s)**,  
3) then evaluate the **karaka(s)**,  
4) then corroborate/refine via **appropriate divisional charts** and yoga patterns. citeturn34view2turn34view0turn44view0

This ordering naturally supports a “promise gate”: if the house and its lord are catastrophically damaged, secondary indicators can add nuance but should not “force” the event. citeturn6view7turn34view2

**Algorithmic formulation (priority + compensation).**  
Implement a `DomainSpec` object with ordered indicator tiers:

- Tier A (primary): main house, its lord, primary karaka, primary divisional chart anchor  
- Tier B (secondary): supporting houses, secondary karakas, supporting divisional chart anchors  
- Tier C (tertiary): yogas, arudha/pada constructs, varga summaries, etc.  

Compute:
\[
\text{DomainScore} = \alpha\,S_A + \beta\,S_B + \gamma\,S_C
\]
with \(\alpha>\beta>\gamma\), *but* apply the veto from Q1 first. citeturn34view2turn6view7

A compensation rule consistent with “weighing” rather than absolutes:
- if Tier A is weak but not vetoed, allow Tier B/C to compensate partially (cap compensation, e.g., `S_B` can add at most +0.20 to the final score). This matches the practical “same house may show property but not education” nuance: karakas and sub-indicators resolve which sub-topic manifests within a house. citeturn32view0turn34view0

**Known disagreements between schools.**  
Some lineages heavily prioritize divisional charts (e.g., Navamsa for marriage) as a near co-primary promise-check, while others treat divisional charts as “fine-tuning that cannot override the birth chart field.” citeturn44view0turn34view0 KP, by design, often makes cuspal sub-lord signification the highest-priority promise determinant, which can override broad “rasi yoga” optimism. citeturn29view0turn28view3

## Contradiction resolution and veto power across systems

**Question 2 — Multi-system contradiction resolution**

**Classical/textual sources (if known).**  
A concrete contradiction-handling mechanism appears in:
- Ashtakavarga transit doctrine: more bindus → more auspicious transit results; fewer bindus → more inauspicious; and Saravali provides a discrete ladder (8 bindus → kingly; down to 0 bindus → “evils at all times”). citeturn15view5turn15view6  
- Yoga “doesn’t deliver unless unblemished”: yogas give promised effects only when lagna/moon and yoga-forming planets are strong and **not combust** (and not hemmed between malefics, etc.). citeturn6view2  
- House effect destruction conditions (lord eclipsed/combust etc + no benefic support). citeturn6view7  
- KP: a discrete marriage promise gate based on whether the 7th cusp sub-lord signifies 2-7-11; otherwise “marriage is not promised,” plus an explicit requirement that Dasa/Bhukti be governed by significators and that transits agree for the event to materialize. citeturn29view0turn29view1

**Formal logic in plain English.**  
Experienced astrologers usually resolve contradictions by separating the problem into two axes:

1) **Amplitude / promise**: how much of the domain is available in this lifetime (strong vs weak promise).  
2) **Timing / trigger**: when the promised potential becomes active (dasha windows + transits).  

Most contradictions come from confusing these axes—e.g., a very “good” dasha window may still not deliver if the promise/amplitude is capped by severe natal damage; conversely, a strong promise can remain dormant if timing is unhelpful. This decomposition is directly supported by (i) house-assessment “destroyed vs ensured” language and (ii) the KP rule that promise is checked first, then timing is checked via periods and transits. citeturn6view7turn29view0turn34view0

**Algorithmic formulation (decision function + veto list).**  
A rigorous computational resolver can be built as a **constrained evidence combiner**:

1) Compute `PromiseScore_D` from natal + divisional charts (Q1).  
2) Compute `TimingScore_D(t)` from active period lords (MD/AD/PD) and their connections to domain houses/karakas. citeturn34view2turn12view1turn43view0  
3) Compute `TransitScore_D(t)` from:
   - your gochara scoring,
   - Ashtakavarga bindu environment for the transiting planet/house (Saravali), citeturn15view5turn15view6
   - plus any “special transit rules” (your pipeline already has orbs/applying/separating).

Then combine:
\[
P(\text{event}_D\ \text{at time}\ t) = \text{PromiseScore}_D \times \sigma\big(a\,\text{TimingScore}_D(t)+b\,\text{TransitScore}_D(t)+c\big)
\]

This multiplicative form enforces the classical “promise gate”: timing can’t exceed the cap of promise. citeturn6view7turn29view0

**A practical veto set (event blockers).**  
Because classical and KP sources both contain “denial” language, implement a small set of *explicit blockers* that either set probability near zero or heavily cap it:

- **BPHS/Phaladeepika-style house destruction blocker:** if the primary house lord is combust/eclipsed or debilitated or inimical **and** unsupported by benefic aspect/association, treat the domain as “severely blocked” even if timing is good. citeturn6view7turn6view3  
- **Yoga viability blocker:** if the prediction depends on a yoga but yoga-forming planets are combust/blemished, cap the yoga contribution. citeturn6view2  
- **KP cuspal blocker (when doing KP mode):** if the relevant cusp sub-lord is a strong significator of “negating houses” for that domain (e.g., marriage not promised unless 7th cusp sub-lord signifies 2-7-11), treat as denial. citeturn29view0turn28view3  
- **Ashtakavarga low-bindu blocker (as a transit limiter):** very low bindu environments predict persistent adversity (down to “absence of bindus → evils at all times”), so cap transit optimism even if the dasha is supportive. citeturn15view6turn15view5

**Known disagreements between schools.**  
Many Parashari-style practitioners treat Ashtakavarga as a **modifier** (strongly shaping transit outcomes) rather than a sacred veto, whereas KP explicitly uses promise gates that behave like vetoes. citeturn15view5turn29view0 Schools also differ on whether a single afflicted karaka (e.g., Venus combust) “kills” marriage promise or just shifts the *quality* (delay, strain, nonstandard forms), with applied texts emphasizing weighting, and KP emphasizing house-signification logic. citeturn34view0turn28view1turn29view0

## From computed factors to a human prediction statement

**Question 3 — The exact pathway from calculated data to a prediction statement**

**Textual sources (if known).**  
No single classical verse enumerates an “end-to-end reasoning chain” in modern engineering terms, but the chain is reconstructible from:  
- house-judgment checklist (rasi + navamsa, lord strength, house strength, yogas) citeturn34view0  
- “house → lord → karaka” plus “when indications fructify in periods” logic citeturn34view2turn34view1  
- dasha effects depend on strength, and timing also requires considering the start/commencement and disposition during the dasha citeturn12view1turn12view3  
- transit quality shaped by Ashtakavarga bindus citeturn15view5turn15view6  

**Step-by-step classical-trained reasoning (computationally reproducible).**  
Take your example: **Rahu Mahadasha, Saturn Antardasha**, natal **10th lord in 11th**, Saturn transiting **10th from Moon**, Ashtakavarga score **35 in 10th** (strong), but **Vimshopak of Rahu = 40%** (weak).

A “mechanism-faithful” chain looks like this:

1) **Define the domain and its primary anchors.**  
Career/visibility/profession is anchored primarily in the **10th house**, its lord, supporting gains in **11th**, and (in many applied traditions) corroboration via the D10 and the Sun/Mercury/Jupiter significations depending on vocation. The “start with the house” principle is explicitly stated. citeturn34view2turn44view0

2) **Promise check (amplitude gate) for career.**  
- Natal 10th lord placed in 11th is read as a structural “career → gains/network/recognition” linkage (11th as gain/fulfillment). This is not a single-verse claim in the provided sources; computationally, it’s an inference anchored in the general method of judging the *house lord’s placement* as a primary “house promise” factor. citeturn34view0turn34view2  
- Then check whether the 10th house and 10th lord are **too damaged** (combust/debilitated/inimical unsupported, etc.) to allow career promise. The “house effects can be destroyed” rule provides the pattern for hard failure when the lord is badly damaged and unsupported. citeturn6view7  
If promise gate clears, you proceed; otherwise, you output “timing may show activity, but outcome caps at modest/strained.”

3) **Dasha frame (what themes are activated now).**  
From BPHS-style logic: “effects of the dashas of the grahas are in accordance with their strength.” citeturn12view1 So the first dasha computation is not “Rahu events,” but “Rahu’s *portfolio* (house ownership + occupancy + associations + aspects + dispositor agency) becomes dominant, scaled by Rahu’s strength.” This is consistent with applied descriptions that results of a bhava are realized in the dasha/bhukti of planets connected with that bhava. citeturn34view2turn34view1

4) **Sub-period modulation (Saturn as the constraint/structure filter).**  
Applied period logic: subperiods of planets associated with the house in the major period can produce that house’s results “par excellence,” while subperiods not connected produce limited effects. citeturn34view2  
So the astrologer asks: *In your natal + varga logic, do Rahu and Saturn connect to 10th/11th/career indicators?* If yes, career outcomes become plausible; if Saturn is a strong significator of obstacles (6/8/12 type linkages) the same window becomes “hard work, delay, responsibility” rather than “easy promotion.” This is also directly in KP logic: a planet signifying 7th can yield marriage/reunion if its sub-lord signifies 2 or 11, but separation if sub-lord signifies 12/6—illustrating **how sub-lord (micro-condition) flips the outcome sign**. citeturn28view1

5) **Now reconcile contradictions via “strength scaling.”**  
- Rahu Vimshopak 40% (weak): treat this as a reduction in the Rahu portfolio’s ability to deliver *cleanly* (more volatility, indirect routes, partial outcomes). This is structurally consistent with the texts’ repeated insistence that effects are “in accordance with strength” and that blemishes suppress promised yoga effects. citeturn12view1turn6view2  
- Saturn transit 10th from Moon + strong Ashtakavarga in 10th: treat as **timing reinforcement**. Saravali is explicit that transits in signs with more benefic dots yield auspicious results, while fewer yield inauspicious, and it gives a discrete scale for bindus. citeturn15view5turn15view6  
So the contradiction resolves as: *promise exists; timing is strong; delivery quality is constrained by Rahu weakness and Saturn’s nature (effort/delay) but the environment supports tangible outcome.*

6) **Intermediate conclusions (things a practitioner actually “decides”).**  
A computational engine should explicitly internalize these intermediate “latent variables”:
- `PromiseAmplitude` for career: **high/medium/low** (from natal 10th–11th linkage and lord strength checks). citeturn34view0  
- `DashaTheme`: Rahu-style outcomes (nonlinear growth, networks, foreign/tech/unconventional vectors depending on your Rahu modeling) **filtered** by Saturn subperiod (slow consolidation). The general idea that period lords distribute effects through time, with major/minor periods, is standard within Vimshottari explanations. citeturn44view0turn43view0  
- `TransitTrigger`: Saturn 10th from Moon supported by high bindus → “external structure supports career action now.” citeturn15view5turn15view6  
- `QualityPenalty`: Rahu low Vimshopak → “results are there, but not fully satisfying / delayed / require more effort.” This matches the strength-conditioned framework (not a single verse about Vimshopak specifically in the cited texts). citeturn12view1turn6view2

7) **Final statement synthesis (example output).**  
Given the above, the classical-style output is usually *not* “career will advance” as a binary, but a constrained narrative:  
- **Advance is likely**, but it will look like **Saturnian advancement** (slow, responsibility-heavy, requires endurance), and Rahu weakness implies **indirect, non-linear, or reputationally mixed** gains; still, strong 10th Ashtakavarga and supportive Saturn gochara increase the chance that effort converts to tangible status/role shift. citeturn12view1turn15view5turn34view2

**Known disagreements between schools.**  
Some traditions treat transits as secondary to dashas (dashas “suffice”), while KP explicitly requires transit agreement for materialization. citeturn44view0turn29view0 Others place much larger weight on Ashtakavarga for transit gating (Saravali’s discrete bindu ladder encourages that), whereas some modern schools treat it as one modifier among several. citeturn15view6turn34view0

## Retrograde correction rules across the pipeline

**Question 4 — Retrograde planet logic through the entire pipeline**

**Classical/textual sources (if known).**  
Retrograde (“vakri”) is explicitly tied to strength and timing in multiple sources:

- **Motional strength (Chesta Bala):** in entity["book","Phaladeepika","mantreswara jyotisha text"], the strength gained “by virtue of motions” is Chesta Bala, and a retrograde planet gets **60 shastyamsa** of such strength. citeturn6view1  
- **Retrograde can override debility/weak varga:** the same text states that even if a planet is debilitated or in debilitated navamsa, it is vested with full strength if retrograde and its rays are full/brilliant; and it also generalizes that the non-luminous planets are strong when retrograde. citeturn6view3  
- **Retrograde dasha sequencing:** BPHS states that dasha effects depend on strength and that the “timing within the dasha” tied to drekkana is reversed for retrograde planets, explicitly noting Rahu/Ketu (always retrograde) as always reversed. citeturn12view1turn12view2  
- **Retrograde transit mechanics:** Phaladeepika’s transit/vedha discussion states that when a planet is retrograde the aspect direction is “towards the right,” and it also states that when the planet causing vedha is retrograde, the effect is “two told.” citeturn6view4turn6view5  
- **School disagreement on retrograde in exaltation:** Saravali records a view that retrograde while in exaltation “produces no effect,” alongside statements that a benefic retrograde is strong and capable of conferring kingdom, while a malefic retrograde causes grief. citeturn15view0turn15view1  

**Formal logic in plain English.**  
Retrograde modifies *how much force* a planet has (strength), can modify *how its effects sequence within time* (reversal rules), and can modify *transit impact intensity* (amplification and different geometric behavior in certain transit frameworks). citeturn6view1turn12view2turn6view5

**Complete retrograde correction rule set for an engine (layer-by-layer).**  
Below is a “pipeline-complete” set that maps cleanly onto your existing modules.

**Retrograde Rule A — Strength layer (all downstream modules should use it).**  
- Set `ChestaBala` according to retrograde (e.g., 60 shastyamsa baseline mentioned). citeturn6view1  
- Apply a strength override: if `retrograde=True` and `rays_full=True`, treat the planet as “strong” even if in debility / debilitated navamsa (implementation: a multiplicative boost or a clamp to a minimum strength percentile). citeturn6view3  
**Downstream impact:** Shadbala/Vimshopak/Drik-based scoring, Argala weighting, yoga potency, and dasha output strength should all reference this unified final strength. citeturn6view1turn6view3

**Retrograde Rule B — Dasha temporal sequencing.**  
If you implement BPHS’s “effects of a graha in first/second/third drekkana appear at beginning/middle/end of dasha,” then:
- if that graha is retrograde, reverse the internal timing order. citeturn12view1turn12view2  
This can be engineered as: `subphase_timing = 1 - subphase_timing` for features tied to the planet’s drekkana placement.

**Retrograde Rule C — Transit intensity and repetition.**  
- Your applying/separating detection already encodes “approach vs departure”; retrograde naturally creates **multiple passes** over the same degree. Model this as repeated activation peaks (each pass receives an activation score). This is consistent with the idea that retrograde changes “effective direction”/behavior in transit frameworks and can amplify effects (“two told”). citeturn6view4turn6view5

**Retrograde Rule D — Transit aspect direction (when using vedha-like logic).**  
If you implement vedha or direction-sensitive aspects, follow the stated rule: retrograde aspect direction differs from direct. citeturn6view4

**Retrograde Rule E — Sign-based gochara (house-from-Moon) scoring.**  
Classical “Saturn in 12th from Moon” gochara rules are usually sign/house-based and do not *always* encode retrograde separately; however, Phaladeepika does encode **severity amplification** when retrograde in certain transit hit/vedha contexts. citeturn6view5  
Engineering translation: keep the sign/house category the same, but multiply the **magnitude** and **duration** of the transit score by a retrograde factor (e.g., `1.25–1.5`) and allow multiple peaks.

**Retrograde Rule F — Yoga participation.**  
Retrograde does not usually remove the structural presence of a yoga; instead, it modifies *potency through strength.* This is consistent with “retrograde planets are strong” and that yogas deliver only when planets are strong/unblemished. citeturn6view3turn6view2  
Engineering: `YogaPotency *= StrengthMultiplier(planet)`; if a school chooses the Saravali “retrograde exaltation gives no effect” view, this becomes a conditional override. citeturn15view0turn15view1

**Known disagreements between traditional schools.**  
The biggest explicit disagreement in the cited material is Saravali’s recorded view that retrograde in exaltation may produce no good effect. citeturn15view0 Many other strands instead treat retrograde as strengthening (Chesta Bala; “planets strong when retrograde”), which would increase effects rather than nullify them. citeturn6view1turn6view3turn15view1

## Combustion correction rules across the pipeline

**Question 5 — Combustion effects through the pipeline**

**Classical/textual sources (if known).**  
Combustion (astangata/asta) is treated in multiple layers:

- **Combustion degree-orbs (Sūrya Siddhānta tradition):** a compiled table gives combustion orbs for the non-luminaries—Mars 17°, Saturn 15°, Jupiter 11°, Venus 10° (direct) / 8° (retro), Mercury 14° (direct) / 12° (retro). citeturn42view0turn42view1  
- **Combustion as a severely negative avastha:** Phaladeepika explicitly labels a planet “Vikala (distressed) when combust,” and presents a graded scheme where Vikala is “100% bad,” with intermediate avasthas blending good/bad proportionately. citeturn6view0  
- **Combustion weakens even if otherwise dignified:** Phaladeepika states that a planet is treated as weak if its rays are eclipsed by proximity to the Sun “even though” it may be in exaltation/own/friendly sign or navamsa. citeturn6view3  
- **Yoga fruition constraint:** yogas give promised effects only when lagna/moon and yoga-forming planets are without blemish, including being “not combust.” citeturn6view2  
- **Combustion ~ debilitation behavior:** Phaladeepika states that in combustion a planet’s effect is similar to that in its sign of debilitation. citeturn30view3  
- **House-lord eclipse can destroy house results:** Phaladeepika says a house’s effects can be totally destroyed if the lord is “eclipsed by the Sun’s rays” and lacks benefic support (alongside other weakening clauses). citeturn6view7

**Formal logic in plain English.**  
Combustion does **not** usually erase the planet from the chart; it **suppresses** its capacity to deliver its significations cleanly, can make dignities behave as weakened, and can block yoga fruition or even destroy house outcomes when the house hinge is a combust lord without benefic support. citeturn6view3turn6view2turn6view7

**Complete combustion correction rule set for an engine (layer-by-layer).**

**Combustion Rule A — Determine combustion status with correct orb by planet and motion.**  
Use the combustion-orb table (direct vs retro for Mercury/Venus). citeturn42view0  
Compute:
\[
d = |\lambda_{\text{planet}}-\lambda_{\text{Sun}}| \ (\text{shortest arc})
\]
`combust = d ≤ orb_limit(planet, motion)`.

**Combustion Rule B — Optional latitude correction.**  
A technical note in the same combustion discussion says latitude can shift the onset by ~1–2 degrees (planet may be within longitude orb but still visible due to latitude). citeturn42view0  
If you already compute ecliptic latitude, implement:
- `effective_orb = orb_limit - k*|beta_planet - beta_sun|` (small k), or simply treat borderline cases as partially combust.

**Combustion Rule C — CombustionSeverity as continuous (supports “0–3° vs 3–8°” gradation).**  
Phaladeepika’s avastha doctrine explicitly supports graded effects (“auspicious decreasing proportionately… in intervening avasthas”) and labels combust as Vikala (100% bad), so a continuous severity model is text-consistent. citeturn6view0turn6view3  
Engineering formulation:
\[
\text{CombustionSeverity} = \text{clip}\Big(1 - \frac{d}{\text{orb_limit}}, 0, 1\Big)
\]
Then you can define bins like:
- `0–0.25` mild, `0.25–0.60` moderate, `0.60–1.0` severe, or the user’s preferred bins (0–3°, 3–8°, etc.) as planet-specific partitions of the orb.

**Combustion Rule D — Strength suppression applies even to dignified placements.**  
Because Phaladeepika explicitly says proximity to Sun can make a planet weak “even though” exalted/own/friendly, your strength module must apply the combustion penalty *after* dignity/varga scoring. citeturn6view3  
Engineering:
\[
\text{EffectiveStrength} = \text{BaseStrength}\times (1-\rho\cdot \text{CombustionSeverity})
\]
with \(\rho\) tuned per planet (Mercury/Venus often less catastrophic than Saturn/Jupiter in some schools; your engine can learn \(\rho\) from calibration).

**Combustion Rule E — Yogas: still “exist,” but may not deliver fully.**  
Phaladeepika’s yoga chapter is explicit: yogas produce promised effects only when lagna/moon and yoga-forming planets are “without blemish,” including “not combust.” citeturn6view2  
Engineering:  
- keep `YogaDetected=True` (structural),  
- set `YogaPotency *= (1 - CombustionSeverity)` for combust participants,  
- optionally apply an additional gate: if a “core planet” of the yoga is severely combust, cap `YogaPotency ≤ 0.3`.

This directly answers “Does it still participate in yogas it forms?”: computationally, yes as a structural pattern, but potency is reduced and may fail to deliver signature results. citeturn6view2turn6view3

**Combustion Rule F — House lordship still exists, but may fail to deliver.**  
The house-lord’s *lordship* is not erased, but Phaladeepika provides a case where if the lord is eclipsed by Sun’s rays (combust) and lacks benefic support, the house effects are “totally destroyed.” citeturn6view7  
Engineering:
- keep lordship in the signification graph,
- but set `LordPower(H) *= (1 - CombustionSeverity)` and allow the “house destroyed” hard gate when combined with other debilities and no benefic support. citeturn6view7turn6view3

**Combustion Rule G — Dasha lord combust: expect debility-like behavior.**  
Phaladeepika states combustion effects are similar to debilitation. citeturn30view3  
Engineering: treat combust dasha lord as “low delivery quality,” increasing obstacles/delays and decreasing clean gains, unless counter-supported by other strength factors.

**Concrete example: combust Jupiter in Sagittarius and Hamsa Yoga.**  
Phaladeepika defines Hamsa Yoga structurally (Jupiter in own/exalt sign in a kendra), but immediately warns that yogas deliver promised effects only when yoga-forming planets are strong and not combust. citeturn6view2turn6view3  
So your engine can encode: `HamsaYogaDetected=True`, `HamsaYogaPotency = BasePotency × (1 - CombustionSeverity(Jupiter))`. This directly models “valid but weakened.” citeturn6view2turn6view0

**Known disagreements between traditional schools.**  
Combustion orb definitions vary across traditions (the cited table represents a Sūrya Siddhānta-derived standard, but other traditions use different visibility/orb logic). citeturn42view1turn42view0 Also, some interpret a close-to-Sun planet as “purified” (spiritually) rather than merely weakened; the cited combustion discussion itself distinguishes an initially inauspicious approach phase vs a more auspicious “moving away” phase. citeturn37view1

## Dasha activation, subperiod modulation, and day-level narrowing

**Question 6 — The dasha activation mechanism**

**Classical/textual sources (if known).**  
Two complementary “mechanisms” appear in sources:

1) **Parashari/BPHS mechanism:** dasha effects are “in accordance with strength,” and assessment must keep in view the “commencement of a dasha,” including dispositions during the dasha. citeturn12view1turn12view3  
2) **Applied (Raman) mechanism:** results of a bhava are realized when the dasha/bhukti of a house lord (or relevant planet) comes; and subperiod logic refines which house’s results become prominent, with “par excellence” language for properly connected subperiods. citeturn34view1turn34view2  

KP adds a third, explicit mechanism: promise is checked first, then timing is checked via periods of significators, and **transits must agree** for materialization. citeturn29view0

**Formal logic in plain English.**  
A planet “gives results” in its dasha because its **natal portfolio** (lordships + placement + associations/aspects + karakatwa) becomes the dominant causal channel over that time, scaled by its strength and conditioned by the contemporaneous chart environment (including transits at commencement and during the period). citeturn12view1turn12view3turn34view2

**Algorithmic formulation.**  
Represent each planet as a “signification vector” over domains/houses:

\[
\mathbf{s}(P)=\text{HouseLordships}(P)+\text{OccupancyHouses}(P)+\text{AspectTargets}(P)+\text{KarakaTags}(P)
\]

Then define an activation function during time \(t\) (MD/AD/PD):

\[
\text{DashaActivation}_D(t)=\sum_{P\in\{MD,AD,PD\}} \omega_P \cdot \text{Strength}(P,t)\cdot \text{Relevance}(\mathbf{s}(P),D)
\]

- `Strength(P,t)` should incorporate natal strength and any “commencement/during dasha” placement conditioning (BPHS explicitly says to consider dispositions at birth and during the dasha). citeturn12view3turn12view0  
- weights \(\omega_P\) reflect hierarchy: MD > AD > PD (mirrors the “subperiods in major periods” treatment). citeturn34view2turn43view0

**Disagreements.**  
Some systems treat dashas as largely sufficient (transits optional), while KP explicitly requires transits to agree for event materialization; a modern overview text even states that Vedic astrology “does not require” transits to see planetary period effects, though transits can be added for fine-tuning. citeturn44view0turn29view0

**Question 8 — What changes in Antardasha vs Mahadasha**

**Textual sources (if known).**  
Raman explicitly encodes how subperiods modulate results: subperiods of planets associated with a house in the major periods of those connected with that house can produce results “par excellence,” while subperiods not associated produce limited results. citeturn34view2 KP similarly uses “conjoined period of significators” logic (event when periods of relevant significators run), implying an intersection principle. citeturn29view0turn29view2

**Formal logic in plain English.**  
Mahadasha establishes the **dominant causal channel** (broad themes); Antardasha selects a **sub-channel** that determines which part of those themes becomes concrete in that sub-window (and often whether it is constructive vs obstructive, depending on connections to supportive vs negating houses). citeturn34view2turn28view1

**Algorithmic modulation formula.**  
A clean computational translation is **intersection-with-weights**:

\[
\text{ActiveSignature}(t) = \omega_{MD}\,\mathbf{s}(MD) + \omega_{AD}\,\mathbf{s}(AD) + \omega_{PD}\,\mathbf{s}(PD)
\]

Then domain outcome polarity is determined by whether active signatures hit **support houses** vs **negation houses** (KP demonstrates this flip clearly: same core significator can yield marriage/reunion if sub-lord signifies 2 or 11, but separation if sub-lord signifies 6/12). citeturn28view1turn34view2

**Disagreements.**  
In Parashari practice, relationship quality (friend/enemy, dignity, yogas) is often used as the modulation layer; KP uses house signification via star/sub-lords as the primary modulation mechanism. citeturn34view0turn28view1

**Question 9 — How transits narrow the dasha window**

**Textual sources (if known).**  
KP provides the most explicit minimal condition set in the cited material: after promise is established, the event occurs in the conjoined periods of significators of the relevant houses, but “if the transit agrees then only the event will take place.” citeturn29view0turn29view1 Saravali also explicitly positions Ashtakavarga as a tool “to evaluate… day-to-day life due to planetary transits,” linking transits to daily results and giving bindu-based intensity ladders. citeturn15view5turn15view6

**Formal logic in plain English.**  
Use dashas to define a **window of eligibility**; use transits (especially those judged auspicious by Ashtakavarga bindus and other transit rules) to pick **specific sub-windows**; optionally use fast movers (Moon) and Panchanga criteria for day selection.

**Algorithmic “minimum alignment sets” (two modes).**

**Mode A: KP-minimal set (strongly explicit in sources).**  
Event day requires:
1) Promise gate satisfied (e.g., 7th cusp sub-lord signifies marriage houses). citeturn29view0  
2) Active period lords (DBA stack) are among significators of the relevant houses. citeturn29view0  
3) Transit agreement at that time (your engine already computes aspect triggers). citeturn29view0turn29view1  

**Mode B: Parashari + Ashtakavarga hybrid (closest match to cited classical-style components).**  
Event day requires:
1) Domain promised (house/lord/karaka viable). citeturn34view2turn6view7  
2) Dasha activation is strong (periods “in accordance with strength”). citeturn12view1turn34view2  
3) Transit environment supportive (high bindus / auspicious transit condition). citeturn15view5turn15view6  

**Engineering: daily scoring recipe.**  
Within an AD window, compute:
\[
\text{DailyEventScore}(t) = \text{PromiseScore}\times \text{DashaActivation}(t)\times \text{TransitScore}(t)\times \text{DayQuality}(t)
\]
where `DayQuality` can include your Panchanga scoring (you already compute it); the KP case-study also notes real-world precision limits (“dates vary by one or two days”), which argues for outputting short ranges or top-k days rather than a single day. citeturn29view1turn15view5

**Disagreements.**  
A major school disagreement is whether transits are strictly required for manifestation. KP says yes (in the cited source), while at least one modern Vedic overview states periods can be read without transits (transits optional for fine-tuning). citeturn29view0turn44view0

## Failure modes and the missing feedback layer

**Question 10 — Why predictions fail even when formulas are “correct”**

**Birth time error propagation.**  
**Textual sources.** Phaladeepika explicitly notes definitional ambiguity about “time of birth” (e.g., when the infant emerges/touches ground vs other criteria), which already implies systematic uncertainty in recorded birth time inputs. citeturn30view2 A modern Vedic overview also warns that unless birth time is highly accurate, the Ascendant cannot be relied upon in subtle harmonic/divisional charts beyond relatively coarse divisions, noting that a five-minute error can materially change Ascendant-derived readings in subtle subdivisions. citeturn44view0

**Mechanism + quantitative engineering estimate.**  
Astronomically, Earth’s rotation makes the sky turn 360° in 24 hours (15° per hour). citeturn41search1 That implies ~1° of rotation in ~4 minutes. Even though the *Ascendant’s zodiacal degree* is not exactly uniform with latitude/obliquity, this is the correct order of magnitude for why small time errors heavily move angles and house cusps. citeturn41search1turn41search0

For Vimshottari start balance, the Moon’s motion is also relevant: the Moon moves roughly 0.5° per hour (~13° per day) against the stars. citeturn45search0 Therefore, a 4–5 minute birth-time error can shift the Moon by roughly 2–2.5 arcminutes, which can meaningfully change nakshatra fraction (dasha balance) when the Moon is near a boundary (you already compute dasha balance as a proportion of the 13°20′ nakshatra span). citeturn43view0turn45search0

**Ayanamsa error (Lahiri vs KP variants) and dasha timing shifts.**  
**Textual sources.** The entity["company","Astrodienst AG","zollikon switzerland"] Swiss Ephemeris documentation gives an explicit Lahiri value and explicit Krishnamurti ayanamsa definitions (including one derived from Krishnamurti’s table), and it notes definitional uncertainty about Krishnamurti’s ayanamsa. citeturn39view0turn40view0

**Mechanism (what changes).**  
Ayanamsa shifts **every** sidereal longitude, so it can:
- change whether a planet falls into a different **nakshatra/pada** (changing dasha start lord or dasha balance fraction), citeturn43view0turn39view0  
- change KP **sub-lord boundaries** (very sensitive), because KP subdivides signs finely and uses the cusp sub-lord as a key promise/timing determinant. citeturn28view3turn40view0

Swiss Ephemeris gives (example epochs) a Lahiri value for J1900 and a Krishnamurti value for t0=1900 used in its “Krishnamurti table” ayanamsa definition. citeturn39view0turn40view0 The difference between such ayanamsas is on the order of arcminutes (a few to several), which is large enough to flip nakshatra/pada when bodies lie near boundaries and to shift KP sub-lords in many charts. citeturn40view0turn43view0

**Karma / “already used up” yogas.**  
**Textual sources.** Phaladeepika explicitly attributes certain outcomes (e.g., early child death) to “sinful actions” of parents or prior births even when nativity shows good longevity, and recommends remedial measures; this indicates a worldview where **chart indicators are not the only causal story**, which is one traditional explanation for “why a technically correct rule sometimes fails.” citeturn30view2

**Engineering translation.**  
“Used up yoga” is not codified as a standard numeric doctrine in the cited classical texts; the closest mechanistic translation consistent with sources is: yogas require both **structural presence** and **unblemished strength** and are mediated by time windows (dashas/transits). citeturn6view2turn34view2turn12view1 Your feedback layer can treat “non-manifestation” as evidence that either (i) promise was overestimated, (ii) timing triggers were misidentified, or (iii) birth-time/ayanamsa ambiguity moved key boundaries.

**Free will and mitigation.**  
**Textual sources.** BPHS dasha chapters (in the cited edition) prescribe remedial worship to obtain relief from evil effects during adverse subperiods, and Phaladeepika prescribes remedies to promote longevity, implying results can be mitigated. citeturn11view0turn30view2 The combustion discussion also recommends specific worship/mantra strategies to overcome combust effects. citeturn37view1

**Computational modeling recommendation.**  
Represent “free will / intervention” as *post-prediction control inputs* that can modify outcomes’ likelihood rather than negate the chart model. Meaning: keep your posterior probability but allow an “intervention factor” (e.g., behavior change, therapy, medical adherence) to update event likelihood downward/upward when the user reports it—consistent with “remedial measures” logic. citeturn11view0turn30view2turn37view1