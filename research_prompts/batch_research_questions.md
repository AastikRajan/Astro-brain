# Vedic Astrology Engine — Batch Research Questions for GPT Research
# Context: Python Vedic astrology prediction engine
# Purpose: Fill gaps in astrology logic, formulas, and data tables
# Give to: GPT Research / Gemini Deep Research (one batch at a time)
# Related project files: vedic_engine/ directory (see architecture below)

## ENGINE CONTEXT (for the AI researcher)
This engine already implements:
- Natal positions (sidereal, Lahiri ayanamsa), house cusps (Whole Sign)
- Shadbala (6 strengths), Ashtakavarga (Bhinna + Sarva), Vimshopak Bala, Drik Bala, Bhavabala
- Vimshottari dasha (3 levels), Yogini dasha, KP sub-lords
- Divisional charts D1–D60, yogas (~30 types), Panchanga (5 limbs)
- Argala/Virodha analysis, transit Gochar scoring, Vedha obstruction
- Transit-to-natal longitude aspects (weighted orb, applying/separating)
- Secondary progressions, solar arc directions, solar term crossings
- Fuzzy inference (24 rules), Bayesian posterior, 8-layer blended confidence
- Chara Karakas (partial), functional analysis (yogakaraka, badhaka, maraka)

---

## BATCH 1 — Missing Dasha Systems

1. **Jaimini Chara Dasha**: What is the step-by-step algorithm to compute Chara Dasha periods? How are sign periods assigned (fixed vs variable based on Rahu/retrograde rules)? What are the exception conditions? Give pseudo-code.

2. **Sudarshana Chakra**: Explain the three-wheel system (Lagna dasha + Sun dasha + Moon dasha running simultaneously). How do you identify years/months when all 3 wheels agree? What is the scoring formula for triple convergence?

3. **Ashtottari Dasha** (108-year cycle): What is the nakshatra trigger condition? Give the planet sequence, years per planet, and the rule for which charts use Ashtottari vs Vimshottari. Provide formulas.

4. **Kalachakra Dasha**: Based on nakshatra pada of Moon. Give the exact pada-to-dasha-sequence table, forward/backward motion rules ("savya/apsavya"), and period lengths for each sign.

5. **Narayana Dasha**: Sign-based dasha from Lagna. Explain how to compute Narayana Dasha periods per sign (odd/even lagna rules), and how to determine antardasha sub-periods.

6. **Yogini Dasha sub-periods**: What are the exact Antardasha period lengths within each of the 8 Yogini periods? Give the formula (proportional or fixed)?

---

## BATCH 2 — Missing Yoga Rules (Natal Chart)

7. **Neecha Bhanga Raja Yoga (NBRY)**: List ALL classical conditions for debilitation cancellation (at least 5 conditions from BPHS and Phaladeepika). For each condition, what is the exact rule, and what strength boost does it confer? Can multiple NBRY conditions stack?

8. **Vipareeta Raja Yoga**: Lords of 6th, 8th, 12th — exact conditions for VRY formation. When is it truly powerful vs weak? What distinguishes a real VRY from a simple dusthana lord exchange?

9. **Parivartana Yoga (Mutual Sign Exchange)**: Three types — Maha (kendras), Dainya (with dusthana), Kahala. Exact rules for each type, how to score their strength, and what predictions differ.

10. **Kartari Yoga (Papakartari & Shubhakartari)**: Exact rule for planets being hemmed — which planets must be in adjacent houses? Does it apply to signs or houses? How does it modify a planet's results?

11. **Kesari Yoga variants**: Are there additional conditions beyond Jupiter in kendra from Moon? What about Jupiter aspecting Moon — does that count? What house positions strengthen it most?

12. **The 32 Dhana Yogas (wealth combinations)** from classical texts (BPHS, Phaladeepika, Saravali): Give the full list with house lords and conditions. Which are the most powerful?

---

## BATCH 3 — Arudha Padas & Jaimini System

13. **Arudha Lagna (AL) computation**: Exact algorithm — count from lagna lord's position back to lagna; handle special exceptions (when lord is in 1st or 7th from lagna). What does AL represent vs natal lagna?

14. **Pada calculations for all 12 houses (A1–A12)**: Give the formula for each Arudha Pada. What are the exception rules (when result falls in same house or 7th from it)?

15. **Upapada Lagna (UL)**: Exact computation (Arudha of 12th house). What does it represent for marriage? How do you read UL for timing of marriage and spouse nature?

16. **Jaimini Aspects (Rashi Drishti)**: Exact rules — movable signs aspect fixed signs (except adjacent), etc. Give the complete table. How does Jaimini aspect differ from Parashari drishti in prediction?

17. **Atmakaraka and Amatyakaraka** (Chara Karakas): Exact rule for degree-based ranking of 8 planets. What happens when two planets have same degree (within 1')? How does AK determine life purpose and spiritual path?

---

## BATCH 4 — Vargas (Divisional Charts) — Missing Rules

18. **Shodasavarga (all 16 divisional charts)**: For each varga D1 through D60 — give the exact mapping formula. Specifically: D3 (Drekkana — 3 systems: Parashari, Jagannatha, Somnatha — which is standard?), D10 (Dashamsha — two systems), D16 (Shodashamsha), D20, D24, D27, D30 (Trimshamsha — two systems).

19. **Vimshopak Bala weights**: What are the exact weights for the 5-varga set (Panchamsa), 7-varga (Saptavarga), 10-varga (Dashavarga), and 16-varga (Shodasavarga) schemes? Give the complete weight table per varga per scheme.

20. **Shastiamsha (D60) meanings**: Give the complete list of all 60 shastiamsha names, their planet assignations, and their quality (auspicious/inauspicious). What is the exact computation rule?

---

## BATCH 5 — Shadbala & Strength — Missing Details

21. **Exact Combustion Orbs per Planet**: What is the exact degree of combustion for each planet (Sun center to planet center)? Do these change when planet is retrograde (traditionally ½ the normal orb)? Give the complete table including different values for mean orb vs exact (Spashta) orb.

22. **Cheshta Bala exact formula**: How is motional strength computed for each planet? What are the 7 states of planetary motion (Vakra, Anuvakra, Vikala, Manda, Mandatara, Sama, Chara, Atichara)? What Shashtiamsha points does each state get?

23. **Kala Bala complete formula**: Give all components — Nathonnatha Bala (day/night strength), Paksha Bala (lunar phase), Tribhaga Bala (3-part day/night), Varsha/Masa/Vara/Hora Bala (year/month/weekday/hour lords), Ayana Bala, Yuddha Bala. Formulas for each.

24. **Ishta Phala and Kashta Phala**: Formula using Uchcha Bala and Cheshta Bala to compute benefic (Ishta) and malefic (Kashta) potential. How is this different from total Shadbala?

25. **Residential Strength (Bhavadhipati Bala in Bhavabala)**: What exactly are the 3 components and their weights? Are there any correction factors for the lord being in a dusthana?

---

## BATCH 6 — Ashtakavarga — Missing Reduction Steps

26. **Trikona Shodhana (Triangular Reduction)**: Exact step-by-step algorithm for reducing Prastara Ashtakavarga to Bhinna Ashtakavarga using trikona reduction. Give a worked numerical example.

27. **Ekadhipatya Shodhana (Single-lordship Reduction)**: The second reduction step — exact algorithm, which planets/signs trigger it, how to apply it. Give a worked example.

28. **Sarvashtakavarga transit scoring**: When a transiting planet passes through a sign, how exactly do the bindu counts translate to a prediction score? What are the threshold values (e.g., ≥30 = excellent, ≤20 = weak)? Give the complete threshold table.

29. **Ashtakavarga Kakshya (sub-house divisions)**: Each sign divided into 8 kakshyas of 3°45'. How does kakshya lord determination affect transit quality? Give exact computation.

---

## BATCH 7 — Timing Precision — Missing Techniques

30. **Tajika (Varshaphala / Annual Horoscope)**: Exact algorithm — solar return chart computation (tropical or sidereal?). How is Muntha computed and moved? How is Varsha lord (Varshesha) determined? What are the 16 Tajika yogas?

31. **Tithi Pravesha Chart**: How to compute. What is its use — monthly or annual? How does it differ from Varshaphala?

32. **Gochara Vedha — Complete Table**: Give the COMPLETE classical Vedha obstruction table (which house obstructs which house, for each planet). Are there exceptions beyond the standard ones? Do benefics have a weakened Vedha effect?

33. **Tarabala (Transit Nakshatra from Natal)**: The 9 categories — Janma, Sampat, Vipat, Kshema, Pratyak, Sadhana, Naidhana, Mitra, Parama Mitra. Exact formula and repeating cycle for nakshatras 1–27. Which are auspicious vs inauspicious?

34. **Chandrabala (Transit Moon strength)**: Exact rules for which houses transit Moon is strong/weak relative to natal Moon. How is Chandrabala combined with Tarabala in Muhurta practice?

35. **KP Sub-Sub Lord (SSub) determination**: In KP system, sub-lord determines event occurrence/denial. What is the exact rule for determining if SSub is the final timing trigger? What are the signification rules for SSub?

---

## BATCH 8 — Special Points & Sensitive Degrees

36. **Maandi (Mandi) computation**: Different from Gulika — exact formula for Mandi longitude based on weekday + time of day. What does Mandi represent in prediction?

37. **Upagrahas (all 5 sub-planets)**: Dhuma, Vyatipata, Parivesha, Indrachapa, Upaketu — exact computation formulas for each from Sun's longitude. What do they signify?

38. **Sensitive points — Yogi, Avayogi, Duplicate Yogi**: Formulas using Sun + Moon + Nakshatra lord longitude. What do they indicate in natal chart and transits?

39. **Sarpa Drekkana and Pakshi Drekkana**: Which drekkana positions of planets indicate specific results for health/danger? Give the complete table.

40. **Bhrigu Bindu (Bhrigu Point)**: Midpoint of Rahu and Moon. Exact computation. What is its use in transit timing? What happens when a planet transits over Bhrigu Bindu?

---

## BATCH 9 — Prediction Accuracy & Rule Weighting

41. **Classical testimony weighting**: In traditional Jyotisha, when multiple factors agree or disagree, what is the explicit hierarchy/priority? Is there any classical text that gives numerical weights?

42. **The "3 of 5 must agree" rule**: Is there a classical or modern systematic rule about how many independent timing systems must confirm an event? What are the independent systems considered?

43. **Dasha lord in natal chart — strength thresholds**: What Shadbala minimum (in Rupas) is needed for a dasha to give strong results? What is the exact classical minimum required table per planet?

44. **Functional malefic transit rules**: When a functional malefic transits the 1st, 4th, 7th, 8th house — how is this scored differently from a natural malefic? Do functional benefics in transit override?

45. **Timing events using Navamsha (D9) activation**: How does a planet entering its natal Navamsha position in transit "activate" that planet's period? Give the exact computation rule.

---

## HOW TO USE THESE BATCHES
- Give **Batch 1–3** first (highest value — missing dasha systems + yoga rules)
- Then **Batch 4–6** (varga mapping formulas + strength components)
- Then **Batch 7–9** (timing precision + special points)
- For each answer received, paste it back and reference which question number it answers
- Request format: classical source + plain English rule + numerical/algorithmic formulation + school disagreements
