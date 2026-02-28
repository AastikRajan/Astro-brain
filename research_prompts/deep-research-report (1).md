# Arudha Padas, Jaimini Techniques, and Divisional Chart Computation Rules

## Textual basis and standardization choices

This report synthesizes “mechanics-first” rules primarily from (a) entity["book","Brihat Parashara Hora Shastra","sanskrit astrology text"] (BPHS) as translated/commented by entity["people","R. Santhanam","bphs translator"], (b) entity["book","Jaimini Sutras","sanskrit astrology text"] in the English translation/commentary by entity["people","B. Suryanarain Rao","astrology author 1955"], and (c) entity["book","Phaladeepika","mantreswara jyotish text"] by entity["people","Mantreswara","jyotish author"] for the *krūra/saumya* (inauspicious/auspicious) classification used in Shastiāṁśa (D60) quality judgment. citeturn13view0turn19view0turn7search7

A recurring practical issue in Jaimini/Arudha/Varga work is **lineage variance** (paramparā): some definitions and computational defaults (especially for Upapada interpretation and *non-core* vargas) differ across commentaries and modern schools. BPHS itself explicitly flags multiple interpretive views for the term “Upa Pada” in the relevant shloka, and modern authors also emphasize multiple valid Drekkana-reckoning frameworks beyond the most common Parāśarī D3. citeturn13view0turn34view0

Because your question asks for **exact algorithms**, the “standard” rule-set below follows BPHS for Arudha, most Shodasavarga computations, Vimsopaka weights, and the sign-based Rāśi dṛṣṭi rules; *where multiple systems exist*, they are presented explicitly and labeled. citeturn11view0turn35view0turn30view4turn10view2turn34view0

## Arudha Lagna and the full set of Arudha Padas

### What an Arudha represents vs the natal lagna

BPHS uses **Lagna Pada / Arudha Lagna** as a *second reference ascendant* for judging worldly manifestations (e.g., gains/expenses, fame/poverty, relational dynamics via the Pada of the 7th), which is precisely why Arudhas are commonly treated as “how something shows up in the world” rather than the underlying thing itself. citeturn12view3turn13view0  
A common interpretive gloss in modern Jaimini practice is: **natal lagna = the native’s intrinsic constitution / lived self**, while **Arudha Lagna = the social projection, reputation, or “visible identity” produced by that lagna** (i.e., the manifest “image”). citeturn0search9turn13view0

### Exact Arudha Lagna algorithm

BPHS gives the *Pada* (Arudha) computation as a **distance reflection** based on sign-count. citeturn11view0

To compute Arudha Lagna (AL = A1):

1) Identify the **lagna sign** (call it L).  
2) Identify the **lagna lord** and the sign it occupies (call that sign LL).  
3) Compute the **inclusive sign-distance** from L to LL:  
   - Distance \(d\) is the number of signs counted **including** both endpoints.  
   - In modular terms (Aries=1 … Pisces=12):  
     \(d = ((LL - L) \bmod 12) + 1\).  
   This “inclusive count” is exactly how BPHS illustrates distance (e.g., “moved away by 9 signs”). citeturn12view2turn11view0  
4) From LL, count forward **d** signs (again inclusive). The resulting sign is the *raw* Arudha Lagna candidate.

The user-phrasing “count from lagna lord’s position back to lagna” is equivalent as long as you keep the **reflection** idea straight: Arudha is defined so that **distance (L → LL) = distance (LL → AL)** in sign-count. BPHS states it in the forward-count form (from the lord), which is the standard computational implementation. citeturn11view0turn12view2

### Exception rules (the “1st/7th problem” and related cases)

BPHS gives three key exception conditions (often collapsed into the “same or 7th” rule in later teaching): citeturn11view0

- **Same-sign/house exception:** if the computed Arudha falls in the **same sign/house** as the source house, it is *not* allowed to remain there; it is shifted to the **10th from that house**. citeturn11view0  
- **Seventh-from exception:** if the computed Arudha falls in the **7th sign/house** from the source house, it is shifted to the **4th from the source house**. citeturn11view0  
- **Special 4th-from-lord placement rule:** if the **house lord is in the 4th from the house**, then the **lord’s own sign becomes the Pada** (i.e., the “raw reflection” is overridden). citeturn11view0

Why these matter for your specific “lord in 1st or 7th” prompt:  
- If the lagna lord is **in lagna (1st)**, the raw reflection returns AL = lagna itself, so the **same-sign exception** forces AL → 10th from lagna. citeturn11view0  
- If the lagna lord is **in the 7th**, the raw reflection often again returns to lagna, triggering the **same-sign exception** (implementation details depend on inclusive count, but BPHS’s exception is the practical rule). citeturn11view0

### A1–A12: formula for all twelve Arudha Padas

BPHS explicitly enumerates the 12 Bhava Padas and their conventional names. citeturn12view2turn11view0

The **computation formula is identical** for each house \(H_n\) (n=1…12):

- Let \(S_n\) be the sign of house \(n\).  
- Let \(L_n\) be the sign occupied by the **lord of \(S_n\)**.  
- Compute inclusive distance \(d_n = ((L_n - S_n) \bmod 12) + 1\). citeturn11view0  
- Raw Arudha \(A_n\) is the sign reached by counting \(d_n\) signs from \(L_n\) (inclusive). citeturn11view0turn12view2  
- Apply the **exceptions** (“same sign,” “7th sign,” and “lord in the 4th”) exactly as stated above. citeturn11view0

BPHS naming (A1–A12): citeturn12view2  
- **A1 (AL)**: Lagna Pada (Arudha of 1st)  
- **A2**: Dhana Pada (Arudha of 2nd)  
- **A3**: Vikrama/Bhratru Pada (Arudha of 3rd)  
- **A4**: Matru/Sukha Pada (Arudha of 4th)  
- **A5**: Mantra/Putra Pada (Arudha of 5th)  
- **A6**: Roga/Satru Pada (Arudha of 6th)  
- **A7**: Dara/Kalatra Pada (Arudha of 7th)  
- **A8**: Marana Pada (Arudha of 8th)  
- **A9**: Pitru Pada (Arudha of 9th)  
- **A10**: Karma Pada (Arudha of 10th)  
- **A11**: Labha Pada (Arudha of 11th)  
- **A12**: Vyaya Pada (Arudha of 12th)

## Upapada Lagna and marriage interpretation mechanics

### Exact computation

Mechanically, **Upapada Lagna (UL)** in most contemporary usage is simply **A12** (Arudha of the 12th house), computed using the same Bhava-Pada rules and exceptions as above. citeturn12view2turn11view0turn14search10

BPHS’s dedicated “Upa Pada” chapter states that Upa Pada is computed as an Arudha for the bhava connected with the lagna, and explicitly instructs the reader to keep the prior Arudha rules in mind when calculating it. citeturn13view0

### Important ambiguity you must standardize before interpreting

BPHS (as translated/commented in this edition) notes that there are “more than two views” on the specific shloka, with some commentarial traditions treating Upa Pada as connected to **12th** or **2nd** depending on odd/even lagna logic. citeturn13view0  

Operationally, you must **choose and stick to one convention** (and ensure your software matches it), because UL sign changes can radically alter interpretive outputs.

### What UL represents for marriage

A classical/parampara rationale (explicitly taught in modern Jaimini lineages and framed as consistent with Parāśara/Jaimini intent) is: the **12th house** shows the “debt”/resolution theme that manifests either as **marriage (bond)** or **renunciation**, and **Upapada** is the “Arudha” (manifestation) of that 12th-house principle—hence it is used as the core marriage-contract indicator. citeturn14search10turn13view0

BPHS’s Upapada chapter uses UL to judge happiness or deprivation regarding spouse and progeny, and places special analytical weight on the **2nd from UL** for marital sustenance/destruction themes. citeturn13view0

### Reading spouse nature and the state of marriage from UL

BPHS gives concrete interpretive rules (examples below are *mechanisms*, not exhaustive delineation): citeturn13view0

- **Benefics connected to UL** (conjunction/aspect) support spouse/progeny happiness; strong malefic connection can signify renunciation/spouse deprivation, mitigated by benefic aspect conditions as stated. citeturn13view0  
- The **2nd from UL** is treated as the “support” of the marriage; severe affliction/debilitation conditions there are described as leading toward spouse-loss indicators, while strong dignifications/aspects mitigate and can signify multiple marriages depending on specific sign conditions (e.g., BPHS mentions Gemini as 2nd from UL in the multi-wife context). citeturn13view0  

A practical synthesis consistent with these rules is to read UL as a “marital ascendant,” then examine:  
- UL sign + occupants (spouse archetype “presented”),  
- UL lord placement and strength (marriage stability vector),  
- 2nd from UL (continuity of bond),  
- 7th from UL (partner-facing dynamics),  
- D9 confirmation (BPHS explicitly assigns spouse analysis to Navamsha among the 16 divisions). citeturn26view0turn13view0

### Timing marriage with UL in practice

BPHS itself provides timing rules for marriage heavily from the 7th-house/venus/navamsha configurations, but “UL-first timing” is typically done via **Jaimini sign-based dashas** in later applied literature. citeturn16view4turn14search14  

A widely used applied workflow (as described in modern teaching on Jaimini Chara Dasha) is: mark **Darakaraka (DK)**, DK’s Navamsha sign, and **Upapada**, and look for marriage to occur in dashas/antardashas of signs materially linked to these factors (UL sign, UL lord’s sign, DK sign, DK Navamsha, and/or signs aspecting/connected by rashi drishti). citeturn14search14turn10view2  

Because dasha systems and their parameterization vary across schools, “timing” is the area most sensitive to your chosen convention; treat UL as the anchor **point**, but validate event windows via the dasha framework you actually use. citeturn14search14turn13view0

## Jaimini Rashi Drishti: exact rules and full sign table

### Core rule-set (as explicitly stated)

BPHS presents sign-based aspects (Rāśi dṛṣṭi) as a separate system from planetary aspects: the aspects are determined purely by **sign relationships**, and (for rashi-dṛṣṭi) longitudes are “ignorable,” with planets in a sign aspecting planets in aspected signs. citeturn10view2turn10view1  

The rules: citeturn10view2  
- **Movable (chara) signs** aspect **all fixed (sthira) signs**, **except** the fixed sign adjacent to them.  
- **Fixed signs** aspect **all movable signs**, **except** the movable sign adjacent to them.  
- **Dual/common (dvisvabhava) signs** aspect **the other dual signs**.

### Complete aspect table (derived directly from the rules)

Below, each sign lists the signs it aspects by Rāśi dṛṣṭi.

| Sign | Type | Aspects |
|---|---|---|
| Aries | Movable | Leo, Scorpio, Aquarius |
| Taurus | Fixed | Cancer, Libra, Capricorn |
| Gemini | Dual | Virgo, Sagittarius, Pisces |
| Cancer | Movable | Taurus, Scorpio, Aquarius |
| Leo | Fixed | Aries, Libra, Capricorn |
| Virgo | Dual | Gemini, Sagittarius, Pisces |
| Libra | Movable | Taurus, Leo, Aquarius |
| Scorpio | Fixed | Aries, Cancer, Capricorn |
| Sagittarius | Dual | Gemini, Virgo, Pisces |
| Capricorn | Movable | Taurus, Leo, Scorpio |
| Aquarius | Fixed | Aries, Cancer, Libra |
| Pisces | Dual | Gemini, Virgo, Sagittarius |

This table is a deterministic expansion of the BPHS rule statements and BPHS’s own Aries/Taurus/Gemini examples (e.g., Aries aspects Leo/Scorpio/Aquarius but not adjacent Taurus; Taurus aspects Cancer/Libra/Capricorn but not adjacent Aries; Gemini aspects the remaining dual signs). citeturn10view2

### How Jaimini rashi drishti differs from Parāśari graha drishti in prediction

BPHS distinguishes **sign-based** aspects from **planet-to-planet** aspects, and in its planetary-aspect chapter states the standard Parāśari graha-dṛṣṭi structure: all planets fully aspect the 7th, with **special aspects** for Saturn (3rd/10th), Jupiter (5th/9th), and Mars (4th/8th). citeturn17view0  

Mechanistically, this leads to different predictive emphasis:  
- **Parāśari drishti** is planet-centric (aspect strength can be evaluated and can vary with planetary context). citeturn17view0turn15view4  
- **Jaimini rashi drishti** is sign-centric and is used heavily to model *sign-to-sign relationships* (a natural fit for sign-based dashas and Arudha sign-references), because it defines a stable relational graph among rāśis independent of degree-orb considerations. citeturn10view2turn13view0  

## Chara Karakas: Atmakaraka, Amatyakaraka, and tie-handling

### Exact ranking rule for 7 vs 8 planets

BPHS gives the Chara Karaka ordering as “inconstant significators” ranked by **longitude within the sign** (i.e., degrees “devoid of rāśis”), with the highest becoming **Atmakaraka (AK)** and the next **Amatyakaraka (AmK)**, followed by the remaining karakas in descending order. citeturn18view4turn18view1  

It also explicitly documents two schools: one using **7 karakas** (Sun through Saturn) and another using **8 karakas** by adding Rahu. citeturn18view4turn19view0  

For an 8-karaka implementation including Rahu, BPHS requires: Rahu’s “degrees traversed” are counted **from the end of the sign** (because of Rahu’s reverse motion logic). citeturn18view1turn19view0

### Tie resolution when two planets have the “same degree” (and what “within 1′” implies)

A strict “exact” ranking uses full **degrees–minutes–seconds**. The Jaimini Sutra commentary explicitly says: if planets tie, resolve by checking who has greater minutes and seconds; only if they are equal in degrees, minutes, and seconds does a true merge occur. citeturn19view0  

When a true merge occurs (two or more planets exactly equal), the same commentary describes the operational fix: the tied planets are “merged” into one karaka, vacancies are supplied by Rahu “in reverse order,” and remaining gaps are filled by **Naisargika (permanent) karakas**. citeturn19view0  

BPHS’s parallel statement: if two planets have the same longitude, they become the same karaka, causing a deficit that is handled using constant significators for the relevant relation. citeturn18view4  

So, for “within 1′”:  
- **Textually precise**: 1′ is *not* itself a canonical “tie threshold”; tie is “same longitude” in the strict DMS sense, with minute/second tie-break. citeturn19view0turn18view4  
- **Practically**: if birth time (and thus ascendant/planet positions) is uncertain, near-ties can behave like ties in sensitivity analysis, but that is an applied-statistics caution rather than a sutra rule. citeturn19view0

### What AK signifies for life purpose and spiritual path

Two classical-style statements anchor modern “AK = life purpose/spiritual path” readings:

1) BPHS directly elevates AK as the principal significator: other karakas do not predominate over AK “just as the minister cannot go against the king.” citeturn18view0  
2) The Jaimini Sutra commentary links AK to outcomes framed as **bandha vs moksha** depending on benefic/malefic dispositions (exaltation/debility, benefic/malefic conjunction/aspect), explicitly using moksha language. citeturn19view0  

Mechanism-first reading method consistent with BPHS’s own “Karakamsa” usage:  
- Compute **Karakamsa** as the Navamsha sign occupied by AK (BPHS defines this and instructs yoga evaluation from it). citeturn12view3turn13view0  
- Read AK and its sign/house/aspects in D1, then read the Karakamsa as the “soul-axis ascendant” for themes of dharma, bondage, release, and the deep motivation structure implied by AK. citeturn13view0turn19view0  

## Shodasavarga mapping rules, Vimsopaka Bala weights, and Shastiāṁśa mechanics

### The sixteen classical divisional charts and what each is “for”

BPHS lists the 16 Vargas and then assigns their primary interpretive domains (e.g., spouse from Navamsha, power from Dashamsha, worship from Vimsamsa, learning from Chaturvimsamsa, etc.). citeturn32view0turn26view0  

This matters because “Dn charts beyond these 16” are often later extensions, and their standards are less uniform than the Shodashavarga set (which is explicitly standardized in BPHS). citeturn26view0turn34view0

### Exact mapping rules for the BPHS Shodasavarga set (D1–D60 subset of 16)

All degree ranges below are **within a sign** (0°00′00″ to 29°59′59″).

**D1 (Rāśi)**: unchanged sign. citeturn32view0  

**D2 (Horā)**: each sign split into two halves (0°–15°, 15°–30°). For **odd signs**: first half Sun, second half Moon; for **even signs**: reversed. BPHS includes a Horā-lord table by sign. citeturn32view0turn29view5  

**D3 (Drekkana / decanate, Parāśarī standard)**: each sign split into three 10° parts; the 3 drekkanas map to the **1st, 5th, and 9th signs from the sign** (table provided in BPHS). citeturn29view5turn20view0  

**D4 (Chaturthamsa / Turyāṁśa)**: each sign split into four 7°30′ parts; the 4 parts are ruled by the sign itself, then the **4th, 7th, and 10th** from it (BPHS gives a speculum table). citeturn32view0  

**D7 (Saptāṁśa)**: 7 equal parts of 4°17′8.57″. For **odd signs**, count from the sign itself; for **even signs**, count from the **7th sign** from it (BPHS provides the table and example Aries vs Taurus). citeturn32view0turn35view0  

**D9 (Navāṁśa)**: 9 equal parts of 3°20′. BPHS rule: for **movable signs**, start from the sign itself; for **fixed signs**, start from the **9th** from it; for **dual signs**, start from the **5th** from it (BPHS provides examples: Aries starts Aries; Taurus starts Capricorn; Gemini starts Libra). citeturn35view0  

**D10 (Daśāṁśa)**: 10 equal parts of 3°. BPHS rule: for **odd signs**, start from the sign itself; for **even signs**, start from the **9th** from it (table provided). citeturn35view0turn20view2  

**D12 (Dvādaśāṁśa)**: 12 equal parts of 2°30′; always counted successively from the sign itself (BPHS provides the table and Aries example). citeturn23view0turn35view0  

**D16 (Ṣoḍaśāṁśa / Kalāṁśa)**: 16 equal parts of 1°52′30″. Start sign depends on sign-type: Aries for movable, Leo for fixed, Sagittarius for dual; then distribute successively (BPHS provides a speculum). citeturn23view0turn20view3turn35view0  

**D20 (Viṁśāṁśa)**: 20 equal parts of 1°30′. Start sign depends on sign-type: Aries for movable; Sagittarius for fixed; Leo for dual/common (BPHS). citeturn23view0turn20view4  

**D24 (Chaturviṁśāṁśa / Siddhāṁśa)**: 24 equal parts of 1°15′. BPHS rule: start from **Leo** for odd signs and from **Cancer** for even signs (table referenced). citeturn23view0turn22view0  

**D27 (Saptaviṁśāṁśa / Bhāṁśa / Nakṣatrāṁśa)**: 27 equal parts of 1°6′40″, with a defined deity/lord sequence and a speculum table; BPHS states the distribution commences from Aries and other movable signs (with reverse deity order for even signs). citeturn23view0turn21view4  

**D30 (Triṁśāṁśa)**: **unequal** divisions. For odd signs, rulers are Mars/Saturn/Jupiter/Mercury/Venus ruling **5°, 5°, 8°, 7°, 5°** respectively; for even signs, the order and spans are reversed (BPHS provides the table). citeturn27view1turn27view2  

**D40 (Khavedāṁśa / Chatvāriṁśāṁśa)**: 40 equal parts of 45′. BPHS rule: distributed successively from **Aries** for odd signs and from **Libra** for even signs (speculum given). citeturn22view4  

**D45 (Akṣavedāṁśa)**: 45 equal parts of 40′. BPHS rule: start from Aries for movable, Leo for fixed, Sagittarius for dual; distribute successively (speculum referenced). citeturn31view0turn27view3  

**D60 (Ṣaṣṭiāṁśa / Shastiāṁśa)**: 60 equal parts of 30′ (half a degree). BPHS provides both the name sequence and the computation rule for the Shastiāṁśa “lord” (detailed below). citeturn31view0turn24view4  

### Drekkana variants: what’s “standard,” and what the alternates are used for

Within applied tradition, **Parāśarī D3** (the 1st/5th/9th mapping) is treated as the default when a text says “Drekkana” without qualification. citeturn33search0turn29view5turn34view0  

Modern Jaimini teaching emphasizes that there are **multiple** Drekkana-reckoning systems (Parāśarī, Jagannātha, Somanātha, and Parivṛtti-traya), and that Parāśara’s wording can be read as covering multiple “parivritti” interpretations. citeturn34view0turn33search0  

A widely cited Jagannātha-Drekkana computational style assigns drekkanas **continuously** across the zodiac such that (example) Aries’ three drekkanas (0–10, 10–20, 20–30) map to Aries, Taurus, Gemini, and Taurus’ map to Cancer, Leo, Virgo, etc. citeturn33search3turn33search0  

For **Somanātha Drekkana**, accessible sources in this sweep were clear about *use-case* (often cited for sexuality/drive analysis), but did not provide a complete, verifiable mapping table in the retrieved excerpts; several traditions place its computation in texts like “Upadesa Sutras” commentarial literature rather than BPHS proper. citeturn33search1turn33search20turn34view0  

### Vimsopaka Bala: exact weights by scheme

BPHS defines Vimsopaka as a **20-point** varga-strength framework and gives explicit weight sets for Shad-, Sapta-, Dasha-, and Shodasha-varga schemes. citeturn30view2turn30view4

#### Shadvarga (6 vargas)

Rāśi 6, Horā 2, Drekkana 4, Navāṁśa 5, Dvādaśāṁśa 2, Triṁśāṁśa 1 = 20 total. citeturn30view2turn30view4  

#### Saptavarga (7 vargas)

Rāśi 5, Horā 2, Drekkana 3, Saptāṁśa 2.5, Navāṁśa 4.5, Dvādaśāṁśa 2, Triṁśāṁśa 1 = 20 total. citeturn30view2turn30view4  

#### Dashavarga (10 vargas)

From BPHS’s tabulation: D1 3; D2 1.5; D3 1.5; D7 1.5; D9 1.5; D10 1.5; D12 1.5; D16 1.5; D30 1.5; D60 5 = 20 total. citeturn30view4  

#### Shodasavarga (16 vargas)

From BPHS’s tabulation:  
- D1 3.5  
- D2 1  
- D3 1  
- D4 0.5  
- D7 0.5  
- D9 3  
- D10 0.5  
- D12 0.5  
- D16 2  
- D20 0.5  
- D24 0.5  
- D27 0.5  
- D30 1  
- D40 0.5  
- D45 0.5  
- D60 4  
= 20 total. citeturn30view4  

#### About your “5-varga” request

In the BPHS framework accessed here, the “canonical” Vimsopaka weight schemes begin at **Shadvarga**, not Panchavarga. citeturn30view2turn30view4  
Some later authors may use reduced or customized varga sets (e.g., dropping D30 in some contexts), but an “official BPHS Panchavarga Vimsopaka table” is not presented in the retrieved BPHS passages; treat any 5-varga table as **nonstandard** unless your lineage specifies it explicitly. citeturn30view4turn34view0

### Shastiāṁśa (D60): exact computation and the 60-name list with quality/planet assignment

#### Exact computation rule (BPHS)

BPHS method to compute the **Shastiāṁśa lord / placement-sign**: ignore the rāśi portion, take degrees traversed within the sign, multiply by 2, divide by 12, add 1 to the remainder to get the target sign count; then count that many signs from the natal sign to locate the Shastiāṁśa sign; its sign lord is the ruling planet. citeturn31view0turn24view4  

BPHS also explicitly states: the **names** of the 60 Shastiāṁśas are listed in order for odd signs, and the order is reversed for even signs; benefic vs malefic Shastiāṁśa placement modifies outcomes accordingly. citeturn31view0turn24view4  

#### The 60 Shastiāṁśa names (BPHS order for odd signs)

BPHS gives the ordered list as:  
1 Ghorā, 2 Rakshasa, 3 Deva, 4 Kubera, 5 Yaksha, 6 Kinnara, 7 Bhrashta, 8 Kulaghna, 9 Garala, 10 Vahni, 11 Maya, 12 Purishaka, 13 Apampathi, 14 Marutwan, 15 Kala, 16 Sarpa, 17 Amrita, 18 Indu, 19 Mridu, 20 Komala, 21 Heramba, 22 Brahma, 23 Vishnu, 24 Maheswara, 25 Deva, 26 Ardra, 27 Kalinasa, 28 Kshiteesa, 29 Kamalakara, 30 Gulika, 31 Mrityu, 32 Kaala, 33 Davagni, 34 Ghorā, 35 Yama, 36 Kantaka, 37 Sudha, 38 Amrita, 39 Poornachandra, 40 Vishadagdha, 41 Kulanasa, 42 Vamsakshaya, 43 Utpata, 44 Kaala, 45 Saumya, 46 Komala, 47 Seetala, 48 Karala Damshtra, 49 Chandramukhi, 50 Praveena, 51 Kalapavaka, 52 Dandayudha, 53 Nirmala, 54 Saumya, 55 Kroora, 56 Atiseetala, 57 Amrita, 58 Payodhi, 59 Bhramana, 60 Chandrarekha (Indurekha). citeturn31view0turn6view0  

#### Quality (auspicious/inauspicious) classification

A classical krūra/saumya list is given (in the retrieved source) for **odd signs**: the krūra Shastiāṁśas are  
1, 2, 8, 9, 10, 11, 12, 15, 18, 30, 31, 32, 33, 34, 35, 39, 40, 42, 43, 44, 48, 51, 52, 59; the remaining are saumya (auspicious). For **even signs**, the classification reverses. citeturn7search7turn31view0  

#### Planet assignations: how to assign a graha to each Shastiāṁśa name

BPHS assigns the Shastiāṁśa’s ruling planet as the **sign lord of the Shastiāṁśa placement sign** produced by the computation rule above. citeturn31view0turn24view4  

If you want a **fixed reference table** for the 60 names, you must specify a “base sign.” A common convention is to list the 60 names against the 60 successive 30′ segments starting from **Aries** (i.e., as if the planet were in an odd sign with Aries as the sign reference), with rulership cycling by the sign-lord sequence; then in an actual chart, rotate/shift according to the planet’s natal sign and apply BPHS’s “reverse for even signs” rule for the name ordering. citeturn31view0turn24view4  

Because the D60 lord is computed by “counting from the natal sign” in BPHS’s example, the same Shastiāṁśa name does **not** have a single absolute planet-lord across all natal rāśis unless you explicitly normalize to a base sign for tabulation. citeturn31view0turn24view4