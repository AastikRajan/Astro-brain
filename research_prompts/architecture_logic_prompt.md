# Vedic Astrology Engine — Architecture & Decision Logic Research Prompt
# Context: Python Vedic astrology prediction engine
# Purpose: Understand HOW calculated data becomes a prediction — the missing reasoning layer
# Give to: GPT o1-pro / Claude / Gemini Advanced (single full prompt, do not split)
# Related project files: vedic_engine/ directory (see context section below)

## ENGINE CONTEXT (for the AI researcher)
This engine already computes:
- Natal positions (sidereal, Lahiri), house cusps (Whole Sign), retrogrades, combustion flags
- Shadbala (6 components), Ashtakavarga (Bhinna + Sarva + reductions), Vimshopak Bala, Drik Bala, Bhavabala
- Vimshottari dasha (Maha + Antar + Pratyantar), Yogini dasha, KP sub-lords + sub-sub lords
- Divisional charts D1–D60, 30+ yoga types, Panchanga (5 limbs: tithi/vara/nakshatra/yoga/karana)
- Argala/Virodha on Lagna + Moon + dasha lords, transit Gochar (house from Moon) scoring
- Vedha obstruction table, Tarabala + Chandrabala, Sade Sati detection
- Transit-to-natal longitude aspects with weighted continuous orb + applying/separating detection
- Dasha lord transit tracker (Gochar score, natal activation, double transit)
- Secondary progressions (day-for-year), solar arc directions, solar term crossings
- Ingress calendar (next sign changes for outer planets)
- Fuzzy inference (24 rules, 3 inputs), Bayesian posterior (Beta conjugate), 8-layer blended confidence per domain
- Chara Karakas (partial), functional malefic/benefic/yogakaraka/badhaka/maraka analysis
- Dispositor chain analysis for dasha lords

Current output: a blended confidence percentage per domain (career/finance/marriage/health) + prediction text.

**The problem**: The engine scores correctly but the REASONING LAYER that connects all computed data to a meaningful prediction is unclear. The following 10 questions target exactly that gap.

---

## THE 10 ARCHITECTURE QUESTIONS

---

### QUESTION 1 — The "Promise" Gate (Chart Promise vs Timing)

Classical Jyotisha says an event can only happen if the natal chart "promises" it. Otherwise no dasha or transit can force it. How does a practicing astrologer formally determine whether a chart has a "promise" for a specific domain (marriage, wealth, etc.)? What are the exact conditions checked — is it the strength of the house, the lord, the karaka, the relevant yogas, all of them together? Is there a formal threshold or priority sequence? How should a computational engine implement this as a gate/filter BEFORE computing timing confidence?

---

### QUESTION 2 — Multi-System Contradiction Resolution

When different systems give contradictory signals — for example: Vimshottari dasha is excellent for marriage, but Ashtakavarga bindus in the 7th house are very low, the 7th lord is combust, Jupiter (karaka for marriage) is transiting 6th from Moon, and the Navamsha shows a debilitated 7th lord — how does an experienced astrologer weigh and resolve this? Is there a formal priority hierarchy (e.g., natal strength > dasha > transit)? Or is it pattern-matching experience? Can this be formalized as a decision tree or scoring function? Which factors have VETO POWER (i.e., a single factor that alone can block an event regardless of other positive signals)?

---

### QUESTION 3 — The Exact Pathway from Calculated Data to a Prediction Statement

Take a specific example: a chart has RAHU Mahadasha, SATURN Antardasha, natal 10th lord in 11th house, Saturn transiting 10th from Moon (Gochar), Ashtakavarga score 35 in 10th house (strong), but Vimshopak of RAHU is 40% (weak). Walk me through EXACTLY how a classical-trained astrologer would process these contradictory signals step-by-step and arrive at a final prediction statement ("career will advance / stall / struggle") — and what intermediate conclusions they form at each step. I want to understand the actual REASONING CHAIN, not just the data.

---

### QUESTION 4 — Retrograde Planet Logic Through the Entire Pipeline

Retrograde planets are flagged in the natal chart and sometimes in transit. But what exactly changes in every downstream calculation when a planet is retrograde? Specifically:
- Does its Gochar house-from-Moon scoring change (does Saturn retrograde in H12 behave differently from direct Saturn in H12)?
- Does its Argala strength change?
- Does its dasha quality change (is a retrograde Mahadasha lord generally weaker or stronger, and why)?
- Does its yoga participation change (a retrograde planet in a Raja Yoga — is the yoga weaker)?
- Does it give results earlier, later, or in reverse?
Give the complete set of "retrograde correction rules" that apply to every layer a computational engine should implement.

---

### QUESTION 5 — Combustion Effects Through the Pipeline

When a planet is combust (within Sun's orb), it is considered weakened. But what exact downstream effects does combustion produce:
- Does it still participate in yogas it forms?
- Does its house lordship still function?
- Does it still receive and give transits?
- Does it still function as a dasha lord?
- A combust Jupiter in Sagittarius (own sign) — is it still a valid Hamsa Yoga?
- A combust 7th lord — does the 7th house completely fail?
- What is the graduated scale (is combustion 0–3° different from 3–8°)?
Give the complete rule set with source references.

---

### QUESTION 6 — The Dasha Activation Mechanism

Why does a planet "give results" during its dasha period? What is the Vedic theoretical mechanism:
- Is it that the planet's natal strength (wherever it sits and whatever it lords) gets activated?
- Does the planet's transit position during the dasha period matter more than its natal position?
- When the Antardasha lord and Mahadasha lord are in mutual aspect or the same sign natally — how does this change the dasha results?
- Is there an explicit "activation check" — e.g., does the dasha lord need a transit trigger to actually manifest results, or does the dasha period itself guarantee results?
What is the interaction between natal promise, dasha activation, and transit trigger in producing a real-world event?

---

### QUESTION 7 — Domain Signification: Primary vs Secondary vs Tertiary Indicators

For each life domain, there are multiple relevant planets, houses, and karakas. For marriage: Venus (karaka), 7th house, 7th lord, 2nd house (family), 11th house (fulfillment), 5th house (romance), Navamsha 7th, Upapada Lagna, Darakaraka. When computing a marriage prediction:
- What is the exact formal PRIORITY ORDER for testing these indicators?
- Does failure of the primary indicator (Venus combust) automatically make it negative regardless of others?
- Or does a strong Upapada or strong 7th lord compensate?
- What is the formal weighting/compensation rule across primary/secondary/tertiary indicators?
Give this structure for: marriage, career, finance, and health.

---

### QUESTION 8 — What Actually Changes in Antardasha vs Mahadasha?

A Mahadasha runs for years (6–20 years). A prediction can't be "RAHU dasha = Rahu events for 18 years." The Antardasha must modulate the prediction. What is the exact classical rule for how the Antardasha lord modifies the Mahadasha lord's results? Is it:
- The intersection of both lords' significations?
- Does the relationship between MD lord and AD lord (friend/enemy/neutral, their houses, their mutual aspect) determine whether the sub-period is productive or obstructive?
- How do you compute the "combined signification" of MD + AD as a unit?
Give the complete modulation formula including what changes further at Pratyantara level.

---

### QUESTION 9 — How Transit Timing Narrows the Dasha Window to a Specific Day

Even within an Antardasha (which can be months to weeks), the actual event happens on specific days. What is the classical mechanism for narrowing from Antardasha → Pratyantara → specific day/week? Specifically:
- Does the Pratyantara lord need to be simultaneously (a) a significator of the event house, (b) in transit activating the dasha lord's natal position, AND (c) receiving aspect from Jupiter or the relevant karaka in transit?
- Or is it sufficient for just one of these to be true?
- What is the minimum set of SIMULTANEOUS CONDITIONS that classical texts say must align for an event to actually occur on a specific day?
- How does Moon's transit (which changes sign every 2.5 days) serve as the final trigger?

---

### QUESTION 10 — The Missing Feedback Layer: Why Predictions Fail and How to Model Uncertainty

In computational astrology, what are the most common reasons a technically correct prediction (all formulas applied correctly) still fails? Specifically:
(a) **Birth time error propagation**: how many minutes of error cause how much positional shift in fast-moving cusps, dashas, and progressions? What is the sensitivity formula?
(b) **Ayanamsa error**: if Lahiri vs Krishnamurti ayanamsa differs by ~6', how much does that shift dasha start times and transit house positions?
(c) **"Karma exhausted" concept**: do classical texts say certain yogas in the chart are already "used up" by the time of analysis and won't repeat?
(d) **Free will and choices**: do classical texts acknowledge that the person's actions can override chart indicators, and if so how should a computational confidence system model this uncertainty?
(e) **What is the theoretical maximum accuracy** of any Vedic prediction system and why (given irreducible birth time uncertainty)?

---

## REQUIRED ANSWER FORMAT
For each question provide:
1. Classical Sanskrit source/text that addresses it (BPHS chapter, Phaladeepika, Saravali, Jataka Parijata, etc.)
2. The formal logic/rule in plain English
3. A concrete numerical or algorithmic formulation where possible (pseudocode, formula, decision tree)
4. Any known disagreements between traditional schools (Parashari vs Jaimini vs KP)
5. A suggested implementation approach for a Python engine

The goal is to convert classical astrological reasoning into explicit, implementable code modules.
Read [](file:///c%3A/Users/aasti/Downloads/New%20folder%20%283%29/vedic_engine)

Searched for regex `def compute_|def detect_|def analyze_|def get_|def calculate_` (`**/vedic_engine/**/*.py`), 60 results

Searched for regex `arudha|upapada|jaimini.*aspect|rashi_drishti|jaimini.*dasha|chara_dasha|kalachakra|ashtottari|shodasottari|nadi|pranapada` (`**/vedic_engine/**/*.py`), no results

Searched for regex `nakshatra_data|NAKSHATRA_QUALITIES|gana|yoni|nadi_koota|kuta_score|marriage_compat` (`**/vedic_engine/**/*.py`), no results

Good comprehensive picture now. Let me do a final check on a few more gaps:  

Searched for regex `gochar_results|gochar_matrix|transit_result.*house|house.*transit.*moon|jupiter.*1st.*moon` (`**/vedic_engine/**/*.py`), 9 results

Searched for regex `openai|gpt|llm|ai_interpret|narrative|explanation.*str` (`**/vedic_engine/**/*.py`), 3 results

Now I have the full picture. Let me give you the complete system audit and then the GPT Deep Research prompts.

---

## Full System Audit

### ✅ What's Already Built (Computation Layer)

| Module | What it does |
|---|---|
| Shadbala | All 6 components + Abda/Masa Bala + 8-state Cheshta |
| Bhavabala | 3-component house strength |
| Ashtakvarga | Bhinna, Sarva, Kaksha, Trikona+Ekadhipatya Shodhana, Pinda |
| Vimshopak | 16 divisional chart strength scoring |
| All Divisionals | D1–D60 calculators (divisional.py) |
| Vimshottari | 3-level dasha, active period, Sandhi detection |
| Yogini Dasha | Full periods + active |
| KP System | Sub-lords, ruling planets |
| 30+ Yogas | Raj, Dhana, Pancha Mahapurusha, Neechabhanga, Vipreet, Gajakesari, etc. with cancellation |
| Jaimini Karakas | AK→DK + AK-AmK relationship analysis |
| Argala | Intervention plugging |
| Dispositor Chains | Chained lord analysis |
| Transits | Ashtakvarga-weighted, Vedha, Sade Sati + Paya |
| Dasha-Transit | Dasha lord transit, double-transit (Jup+Sat), ingress calendar |
| Varshaphala | Tajika solar return, Muntha, Varshesha, Itthasala/Isarapa |
| Special Points | Gulika, Mandi, 5 Upagrahas, Hora/Ghati/Indu Lagna, Yogi/Avayogi, Bhrigu Bindu |
| Panchanga | Tithi, Vara, Nakshatra, Yoga, Karana + Vishti flag |
| Confidence | Bayesian + Fuzzy layers → final score |
| Retrograde | Dasha-lord retrograde flag, Cheshta 8-state |
| Dasha Sandhi | Junction period detection with phase |
| Graha Yuddha | Planetary war (within 1°) |
| Transit Aspects | Applying/separating with orb weighting |

---
