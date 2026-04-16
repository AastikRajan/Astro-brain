# **Architectural Blueprint and Implementation Specification for a Production-Grade Vedic Prediction Engine**

## **1\. Executive Summary for Engineers**

The current state of the computational prediction engine demonstrates robust foundational coverage of standard Parashari and Jaimini Dasha systems, Tajika Varshaphala core mechanics, and basic transit mapping. However, the system architecture presently exhibits a significant bottleneck defined as a diagnostic dead-end: advanced timing metrics, annual modifications, and specific divisional strengths are computed but are not mathematically propagated into a unified, domain-specific confidence score. Consequently, the engine identifies isolated astrological configurations but lacks the deterministic arbitration required to finalize a weighted predictive output.

To transition the system from a diagnostic calculator to an autonomous deterministic predictive engine, the implementation must explicitly integrate the exact astronomical triggers for the Pravesha family, encompassing Yoga Pravesha, Nakshatra Pravesha, and Dasha Pravesha. Furthermore, the architecture requires the completion of the Tajika annual module with native Tripataki Chakra and Harsha Bala logic, alongside the implementation of a rigorous Shodashavarga weighted fusion algorithm based on classical Vimshopaka principles. Most critically, the architecture demands a mathematical arbitration layer operating as a hybrid Bayesian and deterministic gating system. This system scales the base natal promise by dynamic temporal multipliers derived from Dashas and Transits, subsequently filtering the output through strict contradiction-handling and uncertainty routines. The following specification provides the precise algorithms, mathematical weights, and integration pipelines required to code these missing features directly into the core engine.

## **2\. Canonical Implementation Targets**

| Feature | Status in Current Engine | Classical Importance | Predictive Importance | Implementation Difficulty | Best Role in Engine | Recommended Priority |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Yoga Pravesha | Missing | High (Timing) | Secondary | High (Root-finding) | Confirmer | Priority 1 |
| Nakshatra Pravesha | Missing | High (Timing) | Primary (Monthly) | High (Root-finding) | Primary Trigger | Priority 1 |
| Dasha Pravesha | Weak Integration | Critical | High (Context) | Medium (Timestamp parsing) | Modifier / Veto | Priority 1 |
| Tripataki Chakra | Missing | High (Tajika) | Medium | Low (Modulo math) | Modifier | Priority 2 |
| Harsha Bala | Bridge-only | Critical (Tajika) | High (Annual) | Low (Static rules) | Modifier | Priority 2 |
| Shodasha Varga Fusion | Underweighted | Absolute Core | Absolute Critical | High (Dignity matrix) | Primary Multiplier | Priority 3 |
| Confidence Arbitration | Diagnostic only | Modern necessity | Absolute Critical | Very High (Architecture) | Final Output Gate | Priority 4 |

## **3\. Deep Research by Feature**

### **Yoga Pravesha and Nakshatra Pravesha**

The Pravesha systems represent the precise astronomical epoch when a specific soli-lunar geometric relationship exactly replicates its original natal state. Unlike generic solar returns, these charts rely on the dynamic relationship between the luminaries, offering high-fidelity timing signals. Nakshatra Pravesha, frequently referred to as the lunar return, defines the exact epoch when the Sun is transiting its natal tropical sign, and the Moon simultaneously returns to its exact natal sidereal longitude, measured down to the minute and second of arc.1 This chart is cast annually or monthly and serves to pinpoint the psychological and emotional fructification of karmas promised by the broader Dasha system.2 Yoga Pravesha operates on a similar computational foundation but defines the epoch when the exact sum of the longitudes of the Sun and Moon, which forms the basis for the Naisargika Yoga, returns to its exact natal degree.4

The classical tradition often fractures on the precise definition of an astrological year, with many medieval texts relying exclusively on sidereal solar returns. However, robust computational reconstruction by modern scholars strongly mandates a mixed zodiacal approach to achieve consistent results in divisional charts. In this framework, the Tropical Zodiac must be utilized for defining the anchor month and season, while the Sidereal Zodiac is strictly reserved for the spatial measurement of the Moon's longitude.5 The computational flow for determining the Nakshatra Pravesha requires extracting the natal Tropical Sun sign and the natal Sidereal Moon longitude.6 The algorithm must then identify the approximate thirty-day window during the target year when the transiting Sun enters the natal Tropical sign. Within this temporal boundary, a root-finding algorithm, such as a binary search or a Newton-Raphson iteration interfacing with the Swiss Ephemeris, must execute to find the exact Unix timestamp where the transiting sidereal Moon longitude perfectly matches the natal longitude. Once this epoch is isolated, a complete planetary chart is cast utilizing the native's current geographic coordinates.6 These charts function optimally as secondary confirmers or primary timing triggers within the engine. If a Mahadasha promises career elevation, the specific month containing a Nakshatra Pravesha chart where the Dasha lord occupies the Lagna or the tenth house acts as the definitive temporal trigger for manifestation.

### **Dasha Pravesha (Commencement Charts)**

Dasha Pravesha involves casting a distinct horoscope for the precise astronomical microsecond that a Mahadasha, Antardasha, or Pratyantardasha initiates.7 The timing of events in predictive astrology often experiences slight shifts because the natal chart merely outlines the static promise, while the Dasha Pravesha chart defines the dynamic environmental friction modifying that promise.7 The computation requires calculating the precise proportional balance of the natal Nakshatra occupied by the Moon at birth to establish the exact duration of the first opening Dasha.9 From this initialization point, the exact planetary period lengths are sequentially added to determine the subsequent transition epochs.9 These durations must be processed as highly precise ephemeris days, utilizing the standard tropical year length of 365.2425 days for the Vimshottari system.

Once the exact Julian Date or Unix Timestamp of the Dasha transition is identified, the engine casts a new chart for that moment.7 The rule hierarchy for Dasha Pravesha does not permit the chart to generate novel karmic promises; rather, it strictly serves as a modifier or veto layer over the existing natal promise.7 The primary evaluation metric is the geometric relationship between the natal Lagna and the newly generated Dasha Pravesha Lagna. If the Pravesha Lagna falls in a trinal or kendra relationship to the natal Lagna, the Dasha operates with minimal resistance and high environmental support.7 Conversely, if the Pravesha Lagna falls in a Dusthana position relative to the natal ascendant, the period will demand immense sacrifice and generate high friction, regardless of the Dasha lord's natal dignity.7 Furthermore, if the ruling Dasha lord is found to be debilitated in its own Pravesha chart, the engine must flag this as a critical edge case indicating an initial severe downfall or humiliation preceding any promised rise, acting as an override modifier to the domain confidence.7

### **Tripataki Chakra**

The Tripataki Chakra is a specialized Tajika charting mechanism deployed specifically for annual horoscopy to evaluate beneficial or malefic obstruction, known as Vedha, cast upon the Moon or the Ascendant.10 Geometrically, it is constructed by drawing three parallel vertical lines intersected by three parallel horizontal lines, creating twelve intersection points, or flags, mapped to the twelve zodiac signs.10 The progression logic is fundamentally dependent on the native's age. The computational algorithm first determines the current running year by taking the completed years of life and adding one.10 Planetary progression indices are then calculated using modular arithmetic. The Moon's progression index is defined as the current running year modulo nine, falling back to nine if the remainder is zero.10 The progression index for the Sun, Mercury, Jupiter, Venus, and Saturn is calculated using modulo four.10 Mars, Rahu, and Ketu utilize a modulo six operation.10

The mapping coordinates begin with the central upper flag, designated as point 'a', which is assigned the sign of the annual Ascendant (Varsha Lagna).12 The remaining signs are distributed in an anti-clockwise direction to the other eleven points.13 Planets are then positioned on this grid by counting forward from their natal signs by their respective calculated indices.10 A critical edge case dictates that the lunar nodes, Rahu and Ketu, are always calculated using mean retrograde motion, meaning their placement must be determined by counting backwards from their natal positions.10 Once all planets are placed, the algorithm analyzes specific pre-defined Vedha lines. For instance, the central point 'a' receives direct Vedha from the intersection points 'd', 'g', and 'j'.12 Within the modern prediction engine, the Tripataki Chakra should be inserted exclusively into the annual module flow. It acts as an additive modifier rather than a primary timing signal. A malefic Vedha upon the Moon from Saturn or Rahu subtracts from the annual emotional or health confidence score, while a benefic Vedha from Jupiter or Venus adds positive reinforcement.12

### **Harsha Bala Native Path**

Harsha Bala is a fundamental twenty-point quantitative measure defining a planet's functional efficacy and situational happiness within the Tajika annual chart framework.14 It determines whether a planet possesses the required strength to manifest its promised Sahams and Mudda Dasha results during the solar year. The algorithm measures four specific conditions, each contributing five points to the total score, allowing for a maximum possible score of twenty.14

The exact computation flow requires parsing the Varshaphala chart through four sub-routines. The first is Sthana Bala, granting five points if specific planets occupy designated houses: the Sun in the ninth, the Moon in the third, Mars in the sixth, Mercury in the first, Jupiter in the eleventh, Venus in the fifth, and Saturn in the twelfth.14 The second routine, Uccha-Swakshetri Bala, assesses dignity, awarding five points if the planet occupies its sign of exaltation, its Moolatrikona sign, or its own domicile.14 The third routine evaluates Stri-Purusha Bala, analyzing gender alignment. The Sun, Mars, and Jupiter are classified as male, while the Moon, Mercury, Venus, and Saturn are classified as female.14 Similarly, the houses themselves possess inherent genders, with houses four, five, six, ten, eleven, and twelve being male, and the remainder female.14 If a planet's gender matches the gender of its occupied house, five points are awarded. The final routine is Dina-Ratri Bala, which depends on the diurnal or nocturnal nature of the solar return epoch. If the Varsha Pravesha occurs during the day, all male planets receive five points; if at night, all female planets receive the points.14 Within the engine architecture, Harsha Bala must operate as an annual diagnostic modifier. A planet scoring fifteen or higher functions as a high-confidence multiplier for domains it rules during its active Mudda Dasha, whereas a score of zero acts as a severe dampener, restricting the planet's ability to produce material results.12

### **Full Shodasha-Style Weighted Varga Fusion**

The Vimshopaka Bala system represents the pinnacle of classical Parashari mathematical aggregation, designed to calculate a planet's absolute capability to deliver results across sixteen precise life domains, weighted to a rigid twenty-point scale.18 A standard limitation in simplistic prediction engines is the over-reliance on the D1 (Rashi) chart, ignoring the fact that classical sources mandate specific weights for divisional charts to extract an accurate dignity profile.

The algorithmic implementation of full Shodashavarga fusion requires applying static multiplier weights to each of the sixteen charts. As defined by Parashara, the distribution of these twenty points is exceptionally specific: the D1 carries a weight of 3.5, the D9 carries 3.0, and crucially, the D60 (Shastiamsa) commands the highest individual weight of 4.0.18 The remaining points are distributed among the D2, D3, D4, D7, D10, D12, D16, D20, D24, D27, D30, D40, and D45.18 For each chart, a baseline dignity score is generated using the Panchadha Maitri compound friendship rules, translating qualitative states into numerical values: Own or Exalted signs yield 20 points, Extreme Friend yields 18, Friend yields 15, Neutral yields 10, Enemy yields 7, and Extreme Enemy yields 5\.18 The partial score for each chart is calculated by multiplying the Varga weight by the dignity score and dividing by twenty.18

However, a raw Vimshopaka sum is inherently flawed for domain-specific predictions, as it causes signal bleeding. To implement a coder-ready fusion algorithm that avoids double-counting, the engine must isolate specific arrays of vargas mapped to the queried domain. For instance, if the engine is parsing a career-related confidence score, the fusion algorithm must not sum all sixteen charts. Instead, it must isolate the D1 (physical reality), D9 (latent potential), D10 (career specific), and D60 (karmic root), mathematically normalizing their localized Vimshopaka outputs into a unified career multiplier.23 By mapping the D7 exclusively to progeny queries and the D24 strictly to education queries 23, the engine establishes a defensible classical foundation that natively modifies the final domain confidence score without inflating the values across unrelated queries. Contradictions between the D1 and higher vargas are handled by the heavier mathematical weight of the D60 and D9; a debilitated planet in the D1 that is exalted in the D9 and D60 will output a net-positive multiplier, effectively coding the concept of Neecha Bhanga natively into the matrix.

## **4\. Classical Rule Extraction**

This section provides the normalized rule engine specifications required to encode the classical logic into deterministic computational flows.

**Rule Set 1: Dasha Pravesha Gating Logic**

* **IF** the predictive query relies on Dasha or Antardasha timing triggers  
* **THEN** compute Dasha\_Pravesha\_Chart for the exact start epoch of the period.  
* **IF** Pravesha\_Lagna is 6, 8, or 12 signs away from Natal\_Lagna  
* **THEN** set Dasha\_Friction\_Multiplier \= 0.7 AND set Event\_Delay\_Flag \= True.  
* **ELSE IF** Pravesha\_Lagna is 1, 5, or 9 signs away from Natal\_Lagna  
* **THEN** set Dasha\_Friction\_Multiplier \= 1.3.  
* **EXCEPTION RULE:** **IF** Dasha\_Lord is Debilitated in the Dasha\_Pravesha\_Chart  
* **THEN** append diagnostic string: "Manifestation preceded by initial struggle or reversal."

**Rule Set 2: Harsha Bala Native Computation**

* **FOR EACH** Planet IN:  
  * Initialize harsha\_score \= 0\.  
  * **IF** Planet Sthana matches target (Sun=9, Moon=3, Mars=6, Merc=1, Jup=11, Ven=5, Sat=12) **THEN** harsha\_score \+= 5\.  
  * **IF** Planet Dignity IN \[Exalted, Moolatrikona, Own\] **THEN** harsha\_score \+= 5\.  
  * **IF** Planet\_Gender matches House\_Gender **THEN** harsha\_score \+= 5\.  
  * **IF** Varsha\_Pravesha is Daytime AND Planet\_Gender \== Male **THEN** harsha\_score \+= 5\.  
  * **ELSE IF** Varsha\_Pravesha is Nighttime AND Planet\_Gender \== Female **THEN** harsha\_score \+= 5\.  
  * **RETURN** harsha\_score.

**Rule Set 3: Tripataki Vedha Coordinate Mapping**

* **DEFINE** Current\_Year \= Age\_in\_completed\_years \+ 1\.  
* **SET** Moon\_Position \= (Natal\_Moon\_Sign \+ (Current\_Year MOD 9)) MOD 12\. (If MOD \== 0, use divisor).  
* **SET** Sun\_Merc\_Jup\_Ven\_Sat\_Position \= (Natal\_Sign \+ (Current\_Year MOD 4)) MOD 12\.  
* **SET** Mars\_Position \= (Natal\_Sign \+ (Current\_Year MOD 6)) MOD 12\.  
* **SET** Rahu\_Ketu\_Position \= (Natal\_Sign \- (Current\_Year MOD 6)) MOD 12 (Reverse mathematical count).  
* **CONFLICT RULE:** **IF** any planet maps to coordinates connected by predefined Tripataki Vedha geometry to the Moon\_Position  
* **THEN** apply Vedha modifier to annual emotional stability score based on natural malefic/benefic status.

## **5\. Pseudocode / Algorithm Design**

The following Python-like pseudocode is optimized for translation by the Codex agent, favoring deterministic flow and pure functions over complex state objects.

Python

from typing import Dict, List, Tuple  
import ephemeris\_core  \# Abstract backend interface to Swiss Ephemeris

\# \--- 1\. NAKSHATRA PRAVESHA ROOT-FINDING ALGORITHM \---  
def find\_nakshatra\_pravesha\_epoch(natal\_chart: Dict, target\_year: int) \-\> float:  
    """  
    Executes a binary search to find the precise Unix timestamp for the annual   
    Nakshatra return utilizing a mixed Tropical/Sidereal logic paradigm.  
    """  
    natal\_trop\_sun\_sign \= natal\_chart\['sun\_tropical\_sign'\]  
    natal\_sid\_moon\_long \= natal\_chart\['moon\_sidereal\_longitude'\]  
      
    \# Isolate the \~30 day window where the transiting Sun occupies the natal tropical sign  
    start\_time, end\_time \= ephemeris\_core.get\_sun\_transit\_window(target\_year, natal\_trop\_sun\_sign)  
      
    \# Binary search to find the exact moment of sidereal lunar return  
    tolerance \= 0.00001 \# Degree tolerance for high-precision epoch  
      
    while (end\_time \- start\_time) \> 1.0: \# Isolate down to 1 second  
        mid\_time \= (start\_time \+ end\_time) / 2.0  
        mid\_moon\_long \= ephemeris\_core.get\_sidereal\_moon\_longitude(mid\_time)  
          
        \# Helper function accounts for 360 degree wrapping  
        if is\_moon\_approaching\_target(mid\_moon\_long, natal\_sid\_moon\_long):  
            start\_time \= mid\_time  
        else:  
            end\_time \= mid\_time  
              
    return start\_time \# Return Unix timestamp for Pravesha chart casting

\# \--- 2\. HARSHA BALA COMPUTATION \---  
def calculate\_harsha\_bala(planet: str, varsha\_chart: Dict) \-\> int:  
    """  
    Computes the 20-point Tajika Harsha Bala score natively.  
    """  
    score \= 0  
    sthana\_map \= {"Sun": 9, "Moon": 3, "Mars": 6, "Mercury": 1, "Jupiter": 11, "Venus": 5, "Saturn": 12}  
    male\_planets \=  
    female\_planets \=  
    male\_houses \=   
      
    \# 1\. Sthana Bala (+5)  
    if varsha\_chart\['house\_positions'\]\[planet\] \== sthana\_map.get(planet):  
        score \+= 5  
          
    \# 2\. Uccha-Swakshetri Bala (+5)  
    if varsha\_chart\['dignity\_states'\]\[planet\] in \["Exalted", "Moolatrikona", "Own"\]:  
        score \+= 5  
          
    \# 3\. Stri-Purusha Bala (+5)  
    p\_house \= varsha\_chart\['house\_positions'\]\[planet\]  
    p\_gender \= "Male" if planet in male\_planets else "Female"  
    h\_gender \= "Male" if p\_house in male\_houses else "Female"  
      
    if p\_gender \== h\_gender:  
        score \+= 5  
          
    \# 4\. Dina-Ratri Bala (+5)  
    is\_daytime\_return \= varsha\_chart\['is\_daytime\_pravesha'\]  
    if is\_daytime\_return and p\_gender \== "Male":  
        score \+= 5  
    elif not is\_daytime\_return and p\_gender \== "Female":  
        score \+= 5  
          
    return score

\# \--- 3\. DOMAIN-ISOLATED SHODASHA VARGA FUSION \---  
def calculate\_domain\_varga\_multiplier(planet: str, domain: str, varga\_matrices: Dict) \-\> float:  
    """  
    Normalizes specific Varga strengths into a unified domain multiplier.  
    Prevents signal bleeding by isolating relevant divisional charts.  
    """  
    \# Classical BPHS Weights normalized for isolated domains  
    varga\_weights \= {  
        "D1": 3.5, "D9": 3.0, "D10": 0.5, "D60": 4.0,   
        "D7": 0.5, "D4": 0.5, "D16": 2.0, "D24": 0.5  
    }  
      
    dignity\_scores \= {  
        "Exalted": 20, "Own": 20, "Extreme\_Friend": 18, "Friend": 15,   
        "Neutral": 10, "Enemy": 7, "Extreme\_Enemy": 5  
    }  
      
    \# Map specific queries to isolated chart matrices  
    domain\_mapping \= {  
        "Career":,  
        "Marriage":,  
        "Assets":,  
        "Progeny":  
    }  
      
    target\_vargas \= domain\_mapping.get(domain,)  
      
    total\_weight \= sum(\[varga\_weights\[v\] for v in target\_vargas\])  
    weighted\_score\_sum \= 0.0  
      
    for varga in target\_vargas:  
        dignity \= varga\_matrices\[varga\]\['panchadha\_maitri\_states'\]\[planet\]  
        swavishwa \= dignity\_scores\[dignity\]  
        weight \= varga\_weights\[varga\]  
          
        weighted\_score\_sum \+= (weight \* swavishwa) / 20.0  
          
    \# Normalize back to a functional multiplier scale (e.g., 0.5x to 1.5x)  
    normalized\_base \= weighted\_score\_sum / total\_weight  
    return 0.5 \+ (normalized\_base / 20.0) \# Outputs between 0.5 and 1.5

## **6\. Integration Architecture**

To establish a production-grade environment, the integration of these features must adhere to strict modular isolation, segregating heavy astronomical computations from the final arbitration logic.

* **core/astronomy.py**: This module will encapsulate the ephemeris root-finding algorithms (e.g., find\_nakshatra\_pravesha\_epoch). Because natal planetary longitudes are immutable, the output timestamps should be heavily cached via a Redis layer to prevent redundant ephemeris polling.  
* **timing/pravesha.py**: Ingests the precise Unix timestamps generated by the astronomy core, instantiates the chart objects for those epochs, and executes the normalized rule extractions (such as the 6/8/12 Lagna relationship parsing for Dasha Pravesha).  
* **varga/shodasha.py**: Contains the complex dignity matrices and executes the calculate\_domain\_varga\_multiplier logic. It returns strictly typed JSON payloads mapping planets to their domain-specific isolated scores.  
* **annual/tajika.py**: Computes the Tripataki modulo logic and Harsha Bala natively. This module must be injected *after* the natal promise is fully established, functioning purely as a contextual override layer for specific year-based queries.  
* **confidence/arbitration.py**: The definitive integration node. It accepts the JSON payloads from all sub-modules and applies the mathematical gating logic detailed in Section 7 to output the final confidence array.

**Dependency Execution Order:**

1. Generate base Natal matrix \-\> 2\. Compute Shodashavarga Multipliers \-\> 3\. Identify Active Dasha & execute Dasha Pravesha parsing \-\> 4\. Calculate Annual Tajika Modifiers \-\> 5\. Route payload to Arbitration Engine.

## **7\. Weighting and Arbitration Proposal**

The arbitration architecture is the most critical component of the engine. Its primary directive is to prevent algorithmic confidence inflation—a scenario where multiple active diagnostic flags artificially inflate the probability of an event occurring simultaneously. The engine must utilize a mathematically bounded, hybrid Bayesian and deterministic gating equation.

**Variable Definitions:**

* $P\_{natal} \\in $: The core natal promise for a specific domain (e.g., Career).  
* ![][image1]: The domain-isolated Vimshopaka fusion multiplier.  
* ![][image2]: The Dasha gating factor, mathematically modified by the Dasha Pravesha logic.  
* ![][image3]: The Transit trigger matrix derived from Gochar and Kakshya data.  
* ![][image4]: The additive annual modifier derived from Harsha Bala and Tripataki.

**Arbitration Logic and Deterministic Gating Order:**

1. **Varga Scaling (Establishing Absolute Potential):**  
   The engine first scales the base probability by the deep karmic reality of the divisional charts.  
   ![][image5]  
   *Veto Rule:* The engine establishes a strict **Floor of Futility**. If ![][image6], the natal promise is deemed too weak. Consequently, all active Dashas and Transits are flagged as *diagnostic only*. They may indicate psychological desires, but the engine will veto any prediction of material manifestation.  
2. **Dasha Gating (The Authorization Protocol):**  
   The running Dasha functions as an authorization gate rather than an additive bonus.  
   * If the Dasha Lord is totally unconnected to the queried domain: ![][image7].  
   * If connected and the Dasha Pravesha Lagna is highly favorable (1/5/9): ![][image8].  
   * If connected but Dasha Pravesha Lagna is highly frictional (6/8/12): ![][image9].  
     ![][image10]  
3. **Transit Trigger (The Delivery Mechanism):** Adhering to the classical Rule of Double Prediction, transit support is mandatory for an event to finalize.25  
   * If the primary domain trigger (e.g., Jupiter transiting the 5th for progeny) is highly active: ![][image11].  
   * If severe malefic transit obstruction exists (e.g., Saturn transiting the 8th from the domain lord): ![][image12] (Acting as a secondary veto capability).  
     ![][image13]  
4. **Annual Modification (The Micro-Context):**  
   If the temporal query falls within a specific solar year, the Tajika matrix is applied as a direct additive modifier to nudge the final score.  
   ![][image14]  
5. **Final Confidence Caps and Abstention Logic:**  
   * The engine must apply a strict upper bound: ![][image15]. Capping at 0.95 mathematically accounts for free will and unknown edge-case exceptions.  
   * **Contradiction Handling:** If ![][image16] is exceptionally high (\>0.8) but ![][image17] is severely low (\<0.5), the mathematical variance is too broad to output a definitive prediction. The engine must trigger an ABSTAIN flag. The final confidence is artificially reduced to 0.5, and the system appends a deterministic string explaining the exact contradiction (e.g., "The natal promise for this domain is excellent, but the current Saturn transit actively vetoes immediate manifestation. Action is delayed.").

## **8\. Unit Tests and Validation Checklist**

**1\. Nakshatra and Dasha Pravesha Validation:**

* *Test Case 1 (Precision Tracking):* Input a known, verified natal chart. Validate that the root-finding algorithm outputs a Unix timestamp where the Moon's computed sidereal longitude is within 0.0001 degrees of the natal position.  
* *Test Case 2 (Boundary Handling):* Ensure the Nakshatra Pravesha algorithm safely handles Adhika Masa (leap months), verifying it does not erroneously select the Pravesha epoch from the previous or subsequent lunar month.  
* *Test Case 3 (Dasha Fraction Arithmetic):* Validate that the sum of all computed Dasha Pravesha fractional balances equals exactly 120 tropical years, down to the microsecond, ensuring zero drift in the timeline.

**2\. Harsha Bala Validation:**

* *Test Case 4 (Maximum Threshold):* Construct a mock Varshaphala chart featuring the Sun in the 9th house, in its Exaltation sign, in a Male house, during a Daytime return. Validate that the output perfectly equals 20\.  
* *Test Case 5 (Minimum Threshold):* Construct a chart with Venus in the 8th house, Debilitated, in a Male house, during a Daytime return. Validate that the output equals 0\.

**3\. Tripataki Chakra Validation:**

* *Test Case 6 (Modulo Wrapping):* Input a native age of 45\. Validate that the Moon index computes to 1 ((45+1) % 9). Validate that the Mars index computes to 4 ((45+1) % 6).  
* *Test Case 7 (Retrograde Node Routing):* Input a native age of 33\. Ensure the algorithm routes Rahu and Ketu in the reverse numerical direction along the 3x3 grid compared to Mars.

**4\. Varga Fusion and Arbitration Tests:**

* *Test Case 8 (D60 Weight Verification):* Ensure that altering a planet's dignity specifically in the D60 from "Enemy" to "Own" shifts the unified Vimshopaka score by exactly 2.6 points ((4 \* 20)/20 \- (4 \* 7)/20).  
* *Test Case 9 (Veto Logic Execution):* Input ![][image18], but forcefully set ![][image7]. Ensure the final confidence output drops below 0.3, successfully validating the multiplicative Dasha gate architecture.

## **9\. Source Map with Reliability Ranking**

| Source Reference | Type | Relevance | Reliability | Exact Feature Supported |
| :---- | :---- | :---- | :---- | :---- |
| 1 | Modern Implementation (PVR Rao) | High | Very High | Tropical/Sidereal mixed matrix for Nakshatra/Tithi Pravesha root-finding |
| 14 | Classical Commentary (Tajika) | High | Very High | Harsha Bala 4-factor exact logic, gender mappings, and 20-point rules |
| 10 | Modern Interpretation | Medium | High | Tripataki Chakra Modulo (9, 4, 6\) mathematics and reverse node tracking |
| 12 | Technical Guide | High | High | Tripataki 12-flag spatial mapping and internal Vedha intersection lines |
| 18 | Primary Text (BPHS Chapter 27\) | Critical | Absolute | Shodashavarga exactly weighted 20-point scale; D60 dominance validation |
| 7 | Modern Implementation | High | High | Dasha Pravesha chart generation protocol and Lagna 1/5/9 vs 6/8/12 rules |
| 25 | Modern Astrological Engineering | High | High | Rule of Double Prediction parameters and Dasha multiplicative gating logic |

## **10\. Final Implementation Brief for Codex**

**To the Autonomous Coding Agent (Codex):**

You are instructed to systematically implement the missing modules for a production-grade Vedic prediction engine based on the parameters outlined in this specification.

1. **What to Build First:** Initiate the build with the mathematical calculation layers situated in core/astronomy.py. Focus specifically on the implementation of the binary search root-finding algorithms required for Nakshatra\_Pravesha and the timestamp generation logic for Dasha\_Pravesha. You must safely assume that ephemeris\_core will actively provide accurate, geocentric planetary longitudes.  
2. **What NOT to Touch:** Under no circumstances should you refactor the existing transit matrix, the BAV multipliers, or the core Vimshottari period length generators. Leave these systems intact unless you are explicitly passing their output data into the newly constructed arbitration layer.  
3. **Safe Assumptions:**  
   * You are permitted to assume standard Brihat Parashara Hora Shastra (BPHS) principles for planetary friendships (Panchadha Maitri) when drafting the underlying arrays for Vimshopaka Bala calculations.  
   * You may safely assume the Swiss Ephemeris wrapper is already properly configured to handle Delta-T shifts and Ayanamsa corrections internally.  
4. **Risky Assumptions and Strict Constraints:**  
   * **DO NOT** hallucinate or dynamically generate the Varga weights. You must use *exactly* the float values provided in Section 5\. The D60 value MUST strictly equal 4.0.  
   * **DO NOT** attempt to smooth over the Zodiac conflict regarding Pravesha charts. You must rigorously implement the Tropical Sun \+ Sidereal Moon logic precisely as defined in Section 3.1.  
   * **Node Direction:** When writing the modulo logic for Tripataki, you must ensure the step iteration for Rahu and Ketu is distinctly negative (retrograde) compared to the standard planetary loops.  
5. **Configuration Flags:**  
   * Initialize a system feature flag for USE\_TROPICAL\_MONTH\_FOR\_PRAVESHA. Default this flag to True based on the modern computational reconstructions provided by PVR Narasimha Rao, but construct the architecture to allow toggling to False (pure sidereal) to ensure backwards compatibility testing.  
   * Ensure the Arbitration logic outlined in Section 7 is implemented as an entirely isolated class or pipeline step. This ensures that the individual weights (![][image19], ![][image20]) can be calibrated seamlessly by machine learning routines in future updates. The final output of the arbitration engine must return a strictly typed JSON object containing the specific keys: base\_probability, dasha\_multiplier, transit\_gate, annual\_modifier, and final\_confidence.

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJMAAAAZCAYAAAA1zhyrAAAFg0lEQVR4Xu2Z/ctlUxTHl1DylpcQpech71FeIi8/jB/EaEZRSCkaSjLCDyihHqQkkrfyEs2EEnlJyUvEhCIhKUWURNKUpvwBrE9rL3ed9Zxzzzl37n3Gned8anXv2XufdffZ+7v3WmdfkYGBgYGBgYGBRk5Wu0ztolyxk3KM2LO+pnZjqqtwqtrHal8Ue13toNggsbuM2rqtNhDT3rmwcIjaOWLj1JW6tvvmgp4ggF1yYQO7qe2aC5U90vWj0iImZ7PaG2p/q52X6pzD1F5R+0ft61S3mqgT00axsdurXN+m9pfUCyWCH8Yz2jYxf304TW2D2jdiPl6V5X1sggWQ+/CrLBdjZzF9pnaLmKOrUp2zpHa7WJuXq1Wrijox/aT2UbhmVb+odm4oq6NOTGfL8olsY0ksSjCH78r2iYlFcWylhdFZTPy4O+WmDNsu6l+ntlVtTbV6bmA7/1Zs5T1YjBVNTnBCaDeOLKZDxcbt+lAGF6h9JxZymsBPpwnqCP6Yy75ioq9tdBITMfMOsdXAoNCRDANF/X1iIW6xUjsf7K/2ktqFUp8jdCWL6UyxccsTQvm4tAF2OjHx0IvlO4OS86HH1NaKrTBWGsKbN1gIhObtTWwhi4kBrhMT7ShnATaBn1vVbpBRmLlG2nOtJiYVE2+n9NP7sL7SwugkJnadPct3HP0c6oBQwMMR4qifxxB3vNpZuXBC+oqpLm1w8POH2hPlmlyLex7/r0U/JhXT72p3lmt2cHbULOhWMR2s9km4ZlfiYZyl8J1jA+ryK+M8MG5C+zJNMUEeT4TEfQupvAuTiIldOwuHuX5Lqjt5q5gIcZ+Ga97qopieC98JcbFunmAg8vlYNt5UuzBtMWVuFrtvXK7VxCRiqgNB/6B2YihrFdMzUs2BuIEH2UftJqm+olKe86l5YZp5XhbTGqkXkyfml6Zyhx3pWbV3pHpQ7OIcO3EN9BUTv8vv04+4Q7oO4jO1ioldaTFcc8aEk6+kekZC8k15nBS2QPIpEkh2NDrDTuYdOFztfbEt9Eix3ICBZzJOFzubuVjtfBkNOD6fFovbnj+wUgF//Bb+toj56woDmxfHpGQxeT+zYBnLHCpIrp0D1T5Ue0GqbTzMxSMFfoPjixwSM21iOkntynDtL1UPSDXUEeboG310xoqJgeUmdiEHIfAgOOfIwGGyt0o1+b5E7IyGwzkGDY6QURvenngo50uxU3QO1li1v4n1gU7yFwTcq/Z9+Q7+as1g488HiHvw1wd21fW5cAKymICxic/K2D0pVfEsiI3t0eWaZ79flucr5LC0i8JnEVHG+IyjTUy/iPk5oFwjTuYvLzIW+tWprFZMOMJhNBcAB3Axh+JcJrfdLNUVwg8zwMD91PF2GA/s+PQdBgivKD+Df9+lGAwEhC8+8efwPfrrCqLl+dg18iR2pU5MvqPydxMC2qb2ZqWF/R6iy7sL+dqPas+Xz6fEdubIKWp/iv1dUgeTnOfJLYaqTWJ9iBsFQmIO8c04c6B7d6h3asU0TZjot9X2K9dryyevm3HXQyAuWEBIj4Rrh2MJBg4WZRQ6Phfz5+Rdsg+Xi/25nQf9odBmHHViAiblLrHQT5u82pvwEMZ9G6X5PsaUf+5nAfNE+KMPTX+nzVxMDCq7DEpfp3ZtKefadzBCC/kNyZ5PWBRNhFyNM6EzxMLdYiknZOAP8Mc2jr+FUraSNIlp1hDqxh2AzpqZiwnYHv2tMIaO98S21XvUrijfryt1OTF1CBH4e1jtAxkdppJ8449QgD/C3CZpXsWzZEeJiZeZ43LhCrIiYpoWR4lt5UBy3+dtbSXZEWIih5o0x5sWcyMmwiFhzPOgLWLx+/8IYvI8azUQk/u5ENPAwMDAwMAU+BctA0eCIpUGjgAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJAAAAAZCAYAAADe+aeoAAAE/ElEQVR4Xu2Z6+ulUxTHv0IJMSiijEsot2KklBhJLrk0MbxRNF5IzRQvmCKviBeaEnIthqIGKbkUhZkpQqJQRKQmJSlN+QNYn9azf2eddZ7nOdf5HXPO86nV7/zW3mc/z177u/deex+po6Ojo6NjITnY7FSz682OCP4DzA4J/y8b55m9I4/LBalsETle3tenzJ5IZbUgkLPN/jD71+wns71mD1dld5mtWam9fCCgl7Kz4jizi+WTbxKOyY4JOUM+VuPAonCpXDB1bNEIArpSLpq6AK2Vl2HLTJ2ANpv9Y3ZY9f99Zn9ruJAOkguO9qaN7SazZ+VtvGl2eH9xI+wuH5ida3as2b3yNk6MlTSCgDbIVx0aaOo4Df+SnUtGnYCIyc7wP7P5VbPLgq+OQ82eMdth9q2mE9CX8q0VMYwjIISRxcJkeE79OmgV0Cnyl/8oFyQI1OPZuR9xoNmNZnvMHquMmcsef1ao10YWEEs+sWNrj1xl9r18OxmFLzSdgAqIZ1QBseWW524M/m2VL/apUUCoDLWhuptTWQYBxQftb7xm9qlcSJOSBXSRPNgIJoKfmF6R/E3MQ0BsX6xaf5ldHvyIhXfhb/TVCuhpDVZeNEgoH1L/aXJSsoBKsLOAqIefw8cozENATbxv9oPZmcHXKKBv5C9OhxcVAsEAzYJxBVQb9Br+TwJiRWLCxZNco4B4aYwTwTSwFb5h9nkuGIMj5e9yWy6YEjo+qxV2kQXEGJIXvpULNIKA6uBERnYfjVNDEyx9r2TnmPxqdn52Tgkd/1mDfYm2daV2O4ssoM3yvO2oXKAJBVQYpQ6w9K3PzjHgIo0bz3EvwYZxv0bPRYaRBUR/6wRUkutRDx3zFtA69V/hcMseT5CNAtouf/GYMEW4XKL841wgP+btlp9qHpCvPtyBwLXy4CIGjs3xlvVq+dUBZdyXcB8CtMdzLpGfCvhegfa+Uq+9uvdpgmAS1FkIMwuI/hIfRBphG+aEExP3m9Q8wdoExHvfIT92D6NNQNz30E7mEw1eQ3BaZRIUGgWE8si4d6j+lMKyRsfq7n9+kw8sENi7q8+lzQLBKYNHwMs2d7TZi5WPHOwF+XeBbYztrEB7JY+hPVaqcaDd67JzArKAgJWXQSvQF063cbDwEUe2iDraBHShvGzYPR20CYgJSDunBx9j/p18fMvd2C6zr81OXqnVIqDCe/LGyRU+lN+Mch1/mtmTGrwQYxWJ2wKfT6g+8/tZzIWiEOBO9bbF8h3U/vtKDR+Assqco/7VbdI8iZ8NmFmsDk237cOoExCD8Lz8EIFo9pq93VfD4b13Jh+DUmIRLZ6KaR+R/hl8mfz9YnFrfUTeToljvEjMFuMNQwXECrFWPRXeIF8hmqDBsvqskSfQ5YG8QFmNmHlxu+GkRT069rp6OQKDGoXGbKHDQN3c3qQ/PPLsXRoM2LZQp406AQHxe1AeO+rMYrvMtA7gPmaogMaFZXV99ZnZxyCQt9wjH/wyywkoD39UPvg/qnc7u0E9kSIKtrBCEQkCO0m9o31pj5xt2quHSWgS0L6GeL+bnavIzAXEDPtM3ug18hyKwJKosTIhIvbiW+QzvuQ2pR7Gkl9g27s1/M/vSNvV22poj2eV9l6u/KvNvATEM2/PzlVk5gJaVuYhIE65JVecF52AZgQC4kdltuxlCCj5Z8kTl6G/HR0dHR2Lz38oK0HFjzeC/AAAAABJRU5ErkJggg==>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJMAAAAZCAYAAAA1zhyrAAAFIklEQVR4Xu2Z26scRRCHS1QQjXdMiERzxAskedEEJb54QMS7qKhPii+CBGIQwRdJIJCghqCoiCiKihfECz54BU1UBEVFEYygCPoiER8EX/wDtL7tqWxtnZ7Zmd2THbL2B8XZqZnt7en6dXV1H5FCoVAoFAqFRrar3aB2arwxhxyndoXaPWqfhnsDLlB7WG1vS7skfa1QcVV0VKxQW6d2crzRgcskiXUazlM7MTobOCk6lFXh+kK1j4JvwCdq36gd5Xyo71+13c7Hj/wqqaHCkCims9Q+V1usrjeofal20aEn2nGspBh8HW+MgQx5vdp7an9KaiP2sQmejxazbq2YflG7NPgeUPtH7erg58WiSv/vxEA9IikAnsvVXpS0TLTlNplMTOvV9qk9LimO04rprtHbA7JiOkXSi3oW1L5Xe0tSqvY8Ea6PdMi8zF7eiyWc61vVrlU73T3XRAwUASATeRhH/D7TN/GY2h6ZTEwe+tZVTLm4R7Ji2ixLB40ljqyEqj0sgxRe88LFai+onR9vdMQH6hhJwSMgHvO/Hvx1fKx2phxhYspBY3RgIfjnCYK1NTonxAeKEiAnJsD/Y3QGqJPISvyFPsT0tto1MlzmHh29PaC1mFjiaOT4eGOOeF/ttOickC5iYgPTBIUzQjf6ENPfkrb9R0tajSgD2PF7WouJH2eZq+McGc6cPuDlfO1Bf2501+Mg4Mu5I10uMbEU+qwEfYgpHmVcJ0kPNztfKzFZoUh2yoFSeeGV8cYM4SX8Npv+xIK3CQL+g6TjkDqjvbjDrWO5xMTO+ezg60NMEcaaNtilGq3ExAvxxVh8GzTSNCB9QH+6bAzYwS5G5xT4QLH1z4nJCvAPgt+wceWZOptkJ91VTHeo/S6j40Pf4juNFRNZiS+QlRZGbw2gxqA4s7MmBo7ijPWUwnKb2hcyFCKHnE+qnSCpXVs66Qg7KQaP013aebX6ayBqli8yIfeo3/gtdp7siLimP+zE6M8G6XaGQ/bZFJ0TEgP1lyzN7PQ7LhW847g+E8RcZtoiaXzG0SQm4nKLpNrIoHw4IKOZn2WONu50vrFiMlFYsHIws5511yh5Qe0ZSWs9A3Z79ZlzmzXVc2SO36rP90k6kjhYPYdgEJ1tRxngl6rPCOb5ysd5GMvrU5JmOpBl6I9dt4Wd3GfROSExUH7iGEwefs+XBwRop7vOkRPT2spP0MfRJCbGkXvEy2CMo0hZ3varneF8WTGhShqss7h8IACE4CETxWqfDjBDDf5lg2AMPuMDE5bnbhn2gfMWQDAMgA8IB4yxP21ByAj8FUmiRdSTkAvUlWo/S8q8iIGlI7b/ndTXZTEOmC1z9Jux/aO6jrBq8Jvx+5hfqjiY5f3PdT54ToYHuV9JWm0iWTF1gcGg8dXOZ1kkHnLR6W/dNWLxaRIhWYa7X+0nd4/dBO0SpDckCQbWSmrTgmKbAd+frjDwO2XpoJNZOLxtQ05MwIwnO/O3yz9a2xIn+nLBuCIW+r5D8jv3qcXEwN9bfWbG8aOLMpqBDARimWejpJlC0En3wIywdZnaCaGRdUilzGgL5E0yPA9iprDMUi9Qb9gMBM5n4syfFXViOpwwsT6MzhkytZhYZkh5T0sq3oDA+gxkUHy/LOlZljQKUq5N5e9Wz8Brau/IUFzUbPybA3uz8gGC4bdYVmmH/jwo6Tcecs/Nmj7EtKuyvphaTIU8sxYTGZjda58UMR0mrM5igOcdX9zHXWahUCgUCvPKfxIaP9mVYLYOAAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,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>

[image5]: <data:image/png;base64,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>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAG8AAAAZCAYAAAA/vnC8AAAEP0lEQVR4Xu2Y26tPWxTHhw6l45aj45qDHHKScnnAg2tCuZRcUkR5OnWUlBeJyK1cEpLIZcslEqIUwubBLSEUESkpyYvyBxzjY6zpN3/DWr/L3r8te1uf+rbXHnOuudZvjjHHHHOJ5OTk5OTk/JqMVt1S3cvQSVWHb71z2qr6q/5QtXJt5eDesaoeviGhszcov0kFz8FJ/6t6OjsDYn/m7L8izNF8scnspTqjmlbUI52OqkuqIaquqhVic3o17pTYvHyfVO6LdSY6PGGgshHQwvFz8I/Y5P4Z2dJYqurtbJ/FxmsT2bzjVkuFWY/OH70xIQzW2jc0c/5TPVeN9A0pTFW98EaxeTnijRHdVHfF+s2J7NsS27+RjX70rwpWGwOx+jyhjUhpKTBBa1XnVSOKmzJZKTa5HuaGmiELUuYFsYUxMbKzGrmXv4EGOW+cfD9QgDzPyw30Dc0M0t1R1QfVANdWjvaq05LtvKyMVYqLYveSegOMP14KKZX3/TtqTwWn8QI4MUAupjJikL8ie3OE1cUq2yQNiGwp7zxULcw398V7KE57KIV9kCKxZKFI2XpHdVbVT+zHBaUVL7Vgllgaqgaqu+2qob4hA0rsetVrqXDTL0EtnYdjtohVqj6QqOxjZw4Te3+q01RYbUTBet/QhFBeT/LGMlAs7Vd18Q0pdFddVi2W2gRgLZ1HkcQKSzvTeTi2UYewdf3u2r5CpcTDf+SexipPfZkSjFK988YyjBE7Xy2Xxq8+gjvLeaS6Shgutori40GYdxbRJ9XCqC1UqpmFTMi9lXBFLLUuUR1LbCzzR6rZqsmqN4mdc0140Zuq94kd4sqV+2eKvTR994qlVWCF8qPowz3XEnu1cP9gsd+6w7VVCpPsgydU4nFa43czP57rUnwsgL5iQQmLVG+l+NAf0mZmVuThlRwDeFE2fMCJB5Prqaq5yfVxMSdRHrPUSTewU4qPIXGkcj/3hFy/IbERpfFmTfTtjv5vCFSZu1QHkutqIG37IO8j9o5xxcjvpF88PvPxRCxw2O/QDdVjMQcCY/CpMiYcJwbFRr4IhFwdi7xeCpY1/erF8jGrgmj24Lin0f9cL0uuieC4WOHge1tsL5gS2V9J8eGXCCQSawXfJl+KVaFxkVAKPm+xOph8vqwwH3EKhI1icxL22viQnqbQD9aK3UuwMz4fEMhmjaaT2A9mgnkoXwtCZHh4Wfa1AC+Eo4G0EBcrOCktLTBucDhRT8qspFiphnaqBapVvqEEM1SbxVJg6j7USNiWCA7mhPdrNORjoiBwTsyRPOhBZGdfOaXaI4VVM11sRbPa+4hFVbiGw2L9A3WqCWLph+cS2WvEAoXU0tI+0TU5RBipkIg4JMWHdlbRvqRtq1hfNm1KdfquE0ubdWLpCWeGayAA6Mv9J6TwRYEVigNx/DyxPaIuacvJycnJycnJyflZ+QJYqfOC5L/pSAAAAABJRU5ErkJggg==>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGYAAAAZCAYAAADDq1t2AAADf0lEQVR4Xu2Y2+tMURTHl1CSXEPkkksiFEqRRJJLLlF4UbxJ/RQPPPDiQTx4ESIUP+LBJW8URZGESKGIiKQ8KCl/AOsz6+zfrNlzzm9mJDN+sz/1rTlrX86ZtfZe+yKSSCQSPZ6+qomqNaqBzt5L1c89J/4ROH666qvql+qt6ofqQFa2XTW4q3Z7gz+GqiZJ44OVdgtUg+KCPJaJBeNcXKCMEytDCZHVquuqkareqs2qi1KZXYp4I1aPrHRLzKcMeAJdxTqxWbJbrEEedPA+NrYhY1QPVNOcDaf+VG11tjxo2+Geh6vuqD6p5jt7iQliTqdCdxCUI7GxDbkm+ZkD/3yLjRE7xNr65WBGZnvobKXZcUos2ht9QQ68eENsbEOeS35giuye9WJ1/JpEOsT22NnkRGYkkon6KFprcWzs9HpgsNPuoDeGKM/yxh7G4QZVKyvUCsyAuKAbqEtqfKma6gvCS/p44x9ASryqehQXNABbR75lS1zQYvzNwLwW23RV7ciKXgLs0J5EOllRo5KbqguxsUE+qGbHxhajyGeNBmas6rNqbVwARS/x1FMH2JEsio0NMEx1XHJGT4vxSvL9Uc/iHyBl+l3YENVi9yydYp35PblnhFj53bhA7FB0X+yAtU9stoSFb5VYkHAyowKnB1aIbdEpu6Tqn9npj/csVC0RaxeI+8v7niL4D+x86lWtxZtbEHwSp38G5lP3THrnv8b9cY5htnj2qs54wxyxPHdZ8k+tdMJH5J1fPoo5DNg87Mx+hz4DTPEwC/jIkO64ljib2fiTfBhtgXRGWgvE/TGzmgX/laPDqMiOn/zOiqUA235nA9YUv9nA9ww2glPFDbFO3qluq16ovqsmq46pppSrlmAkMHIC/B6d/eZ+za813sGwTcrpMbSZp/rSVcO28WFWcACL+2v2OsRs4OzHoRzn4tiZFTXsG59J5Yk+HDBjFS4DjGjuw0IUWZAY0UXwgjBbOMWy8Icpy4vC7GEm+LTDzot6y1VXpLw1ZSfmA0hKCKOPunF/PjU2C9LxHrFBmevUZjBXyh9zWiwYrAu7xJyKoxlVBJkgHhJzKhd4S61Z6X4uBB9n+xwbnE/gxkt1f6yJcY5PiM0wdhVHVSvF8iS30ixqzCSCw8Fpk+qelNeOUA9x7gmQ/rihDbDz6ZTyhWrc3/nMnkgkEolEIvF/8xuUhM7+AIW9ygAAAABJRU5ErkJggg==>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGYAAAAZCAYAAADDq1t2AAADRUlEQVR4Xu2Yy+tNURTHl1CSt1DyiCSvAUqRRJJHHlGYKEMp6mdgwsRADEy8IpRXGXgMUYRiIEQKRUQkZaCk/AGsz11n/866+557/c7vFte9+1Pfunftfda5d6+91157iyQSiUTb0181WbVWNcTZ+6gGuO+JvwQDP1P1VfVL9Vb1Q7U/a9uuGtbdOwFTVINj4x8YoVqoGho3FLFcLBjn4gZlglgb6nSGq9aorks+gVdU9WjMG7EsRFa6JfY8E56JX8N6sZfsFnugCBy8j40dyAzVHdUR1R4pF5hxqh3u+yjVXdUn1QJnrzBJzDkdGkFQDsfGDoeAlAnMTrH+fjuYldkeOltldZxS/VRt8g0FEJiNsbHDKRuYDWL9fQE1JrM9djY5kRmJZKI8ZQNTBJMdHwe88XlmnO2NbcahkiqTFZoNzCDVNdVL1TTfgFPUzxt7ASnxqupR3FACSkd+y9a4oYVpNjCvxYqumoosBKYIKrQnkU5W9ajmpupibCzJB9Wc2NjCNBOY8arPqnVxAzQKTKAnfeCbanFsLMFI1XEpmD0tTG8DQ8r0VRhnoyXuu5wXczzdGx2jxdrvxQ1ih6IHqr6qvWKrJVQbq8WCxCAzKxj0wEqxEp22S6qBmR1/vGeRaqnYc4HYX9HvqQf/gcqnpypz5dQoMKR3/mvsj3MMq8XDeeiMN8wVy3OXpfpOLIATXlx0fvkoNmBA8dCVfQ4+A5SBYRXwI0O641ribGZjj+OH8SyQzkhrgdgfK6sVaBQYtgLa9kV29hRfbDD2TDaCU8MNMSfvVLdVL1Tfxe6Bjqmm5l0rMBO4PwvweWz2mfs1v9f4AYZtkqfH8Mx81ZfuHlbGh1XBASz29y/3IVYVkyP8By8qrAC/8ZlUn+jDATNW3W2AGc19WIgiGxIzuh68IKwWTrFs/GHJ8qKwelgJPu1QedGPGXZF8tKUSswH8KnkdT19Y38+NSYc8ySP8GmxYLAv7BIbVAaaHEuQCeJBsUHlAm+ZPVa5nwvBZ7B9jg2DT+AmSq0/9sRmS/y2hBVGVXFUtUosT3IrzabGSiI4LOvNqvuS7x2hH+LcEyD9bXHfX4kVJuFCNfZ3IbMnEolEIpFI/N/8BtOgwO5e52s+AAAAAElFTkSuQmCC>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGYAAAAZCAYAAADDq1t2AAADkUlEQVR4Xu2Y26tNURSHh1CSuyJyyCWXUC4pHiSSSy55wIviTQrxwIsXRSgpIUJxiAecvJEURRJyKRQRkZQHJeUPYHzGnnvNPfZaZ+8dOcfZ86tf7T3mZa015hxzjjlFEolEosvTUzVGtULVL7J3U/WK/if+ETh+suqL6qfqjeq7am+pbJNqQLl2c4M/BqnGSuOTlfq0oz39tMsiscE46wuUkWJlKCGyXHVVNVTVXbVOdUEqV5ciLqkmlH73VR1QbZaCAVolFiU7xJaxPBiUd97YhIxQ3VNNimw49YdqQ2QrgrYx+PuFaqKzy2gxp9/yBQ4G5bA3NiFtkr9y4J+v3uggwm54o1g7tokyjNZJsdFeExfkwINXe2MT8kzyB6bIHsP+TJ2Bzv5RNSs2HBeruCU2JtqlaK99KGavlQjcFasXgoFlrGpvCqM8zRd0IQ42qFqrQq2B6eMLHOMl6wMdqSw2QmEPX9AgLIlXVA98QQP0F3uX9b6gk/GnA3NKNV81U7K+iKKWuFLRQ4AM7ZHTiYoalVxXnffGBnmvmu6NnYwin9UzMEzgV9H/rZKdGQ9F9sKHxNRTB8gs5nljAwxWHZOCfL4T8VLy/VHP5o/zZ3uj8lRsUpZpFesszsljhoiV3/YFYukdIcgBa5dYtISNb5nYIOHkT2JODywRS9Epu6jqXbLTH8+Zq1og1i7g+8t7nyL4BtLUelVr8+YWBJ/45Z+J+Tj6T3TwrXF/RQPDhIzbygyx0OI0WpUZiJ1IeYm888sHMYcBycO20u/QZ4AQD1HAS4bljuuIMyUbH3larC2wnMUzyPfHh3QUfCtHh2HOjp/2Rf/ZCrDtjmz4K8+XRMweb4RrYp28Vd1UPVd9U41THRXLJGKYCcycAL+Hl35zvxbvNRUhqmyUbHkMbZhFn8s1LI0PUTFFqvvr6H2IaCDd5VBOJkcUT62oYe/4RDXH2fEV9bn6oj13kURqLsxo7sNCyrhSbEYXwbknRAuHJjb+ELI4PEQPkRAvO2Re1FusuixZakomFg8gYR1mH3V9f/HS2FGwHO8UczTLbCPwvfiZ9kz+vwan1PAypH8MBvvCdjGn8mBmFQ9nEPeLOfW1aqE1+30/FwYfZ7OUBYLzGbhRUt0fe6Jf4xNiEXZf7HC0VGyPIjRbxCKJwWlTrVXdkWzvCPUQ554Ayx83tAEyn1bJLlR9f+dK9kQikUgkEon/m18HndECxQjDwgAAAABJRU5ErkJggg==>

[image10]: <data:image/png;base64,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>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGkAAAAZCAYAAAAyoAD7AAADe0lEQVR4Xu2Yz6uNQRjHH6GEECEixwJJyo+I1S0UC8XCjqwkyc9iIRsllEiSSBGS/MiCsiB2hBRJkaIslIWS8gfwfM4zzznzzj3vvee9t+493PnUt3Nm5j3zzpln5pnnGZFMJpPJZDqLuaoTqpNtarn9LFPCGLE5rcIo1VTVRNWwpK3OU9UrKTauUf1RHY3qxqk+qxZFdRljqeqC6q3YvN0tNpfCnN5SzQvlBarnoY62Bp9UK+MK5ZDqt2pdUv9SzOKZIkdUD1T7pJqRNqt+qmpR3S6xPvisM0G1qtFs1FRvxF40ttgkZ5NypgjzVcVIB6S7x1ob6q55xQrVpEazgatjF7GbYnCHDetmWlLVSJxf28Kns1esDwxYCi/goVpSn+mdqkZK2SO2QbrShhRcHS8anTb8B4wQW7lpxNqTiHzbpa9G2qm6ovqlupi0tYSXYM0yZqtGppUDyHcp+nDGsyEqDyZ9NZLDvLIwnqhmJm0N/CXsplZwLp1RTUkbBpBHqsVRmfEQtnYC/TUSzBfrgzC8JYTcPJAGDQ45ErlSJ8F4OiWgqWqk1WLhe4z3gbpBI52zi2rFpjpkw/ekmSuRJZ8Wy67fq3arnknTwCRj58QiF/p1F4qhl4lN7mGxfm6ET4fFghtj59LG+ci7iERZYZQZzxyx8ZAExr/vCf4n429Xk+1nbdGbkRZKMc90Y8QXBLSXHjk+2T4JrXiouhSVt4gZlMMOf0rHJGjuW2eE51jpX8L3/WKh/7fwHIbAmJ6TMdmeI2CIy6GOfA43e14sAADyPMbj5cGmJyOxML+qHov9L6DMnPl/B56jD86lOsNDRZlSN8LEMsEx7Jz0ruqU6kdU5uoJQzh8pw7cYDHbpTmG6aEOQ2Cg+DzcJN3HMxgwT+ncuRw8y1WxMNsXFV6GIIjrJK6V3on9xq+JKsOKf6GaFtX5qo9XArCSXkdljLA1KmMg35EkbR+itvFi/ZJ53xYzBMwS65NxgAcx8Xj+VfA+eJ6D0s+7UXwl2TBwljBJXVLcMQ4T7ztlidi5wWSylQHX5xEaZxMGZJfg/z+K3XrARmm6Bq6kcLc7xM4sxkO/sF5Kbo+HGmxRAgO2JdsUmLB4xzhs7etiz+LaCEYoe37FZaTf8t5U3Zem0TgTSezQnVAHGIJ34V7ph/EcE3vH8ei5TCaTyWQymaHJX5+lwMlYRLIdAAAAAElFTkSuQmCC>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGkAAAAZCAYAAAAyoAD7AAADhUlEQVR4Xu2Yz6tNURTHl1BCiJDf14AJCkWMXkmRHzGgFBlJBn6k3kSGQokkiRQhyY8MKANiRkhMFClKUgaG/gDW56293H32Ofe+83q59+XtT317Z69z3j777rXX2utskUwmk8lkhhYLVSdVp2pqpf1bpoIxqlWqyemNATBTtSQ1PlO9Vo2IbGtVv1XHItsE1WfV0siWMZibH6odoT1L9U218e8T9diu+qVal974pFqd2I6IPbw+sb9STU9sGZH9quNSXOgfVE+jdh3eigVHwUmTVGtig9JQvVPdU40v3pJzSTtjC5kFvTixM1dMOCmwDltVG8SyVcFJ5M8psUEs1fFSoimGVcKKyRRhnnBGmmHcPi2xVzFXbNthKyk5qQoiiM4biT1Tjc9X6iQWNPaexF4FaXGODMBJpDo6H5ve+A8Ypdoj5Yq1nah829Gfk/qbcJyzKVzXdhIdk+5aMV81OjV2EKqouOpkPFuidqcZjJPYz0hzTi0nUSjQMdFUBfvSWamXZ/8Vj1XLojbjeRG1O81gnPRErGBwajkJz9JxWjQ43slQgvF0s6Ahqquc5IVDI7E7HhDtlPbZ90+sCqKoUbzVB1/R96X5rURpeUbsxOK96oDquTQdzAfeedU4sX49heLoFWKTe1Ssn5vhr8NiIY0Rudxjf+RdVKK3Q5vxLBAbzyKpX+ryOxl/XU21f2uJ/34q5ZjrYhMdw0lCaeIjiKC20ecv80mo4pHqctTeJebQS2L7FI7YGa7ZdGeH51jpX8L1YbEf9D08hyNwpn+TMdn8QMARV4KN7znS7AWxAgD4zmM83u4GvPu0lKP5jdgHrcPC/CqW4lodG1U6aWQwtlL6YiY2XTFEDg6OYdA/ozabI45wuPYN0x0Ws1eaY+AsC5gMHBTvh9ukPJ5uwdEaR0FUj5TUZIm4wCKzXFMdlPKi8m0knf92UVcJK/6lakZk81XvUeCQ3lhJDk7YHbVxkEdkrxRX3ESxfllNd8QcAfPE+mQc4EVMPJ5uwpg3i2WQfcm9joFXD4VrVgmT1CPFiHGYeI+U5WL7BpNJyAOpzys0VhAOJErI/x/FTj2AysdTA8cspFsmgD2L8dAv8J3hzhvWEKIUBhfFigFgwuKIcQjtG2LPktooRmh7+D8Mz8At1QNpOo098WrQ3WADHMG7SK/0w3g41OQdJ6LnMplMJpPJZIYnfwAPjseg0xXbMwAAAABJRU5ErkJggg==>

[image13]: <data:image/png;base64,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>

[image14]: <data:image/png;base64,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>

[image15]: <data:image/png;base64,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>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAZCAYAAABzVH1EAAACQElEQVR4Xu2Wz0tVURDHv5KBizAqJDLK2gjWxoQgN9VCUtCFUrkRXLhwk9DGjZsghBZWi5CQBEXBIBG0VVAg6qJfhAoGuTHaBC7aBP0B+f025/jOO7zHe1c0bnQ/8IU5M/e8d+fMzL0XyMjISEIz9Zb6WEQvqJ7dq/8BdMO/qdrIf4yapb5E/tTyCZZIVRwgrbBYRRxII7rRH7HTcRcWr4wDaUNV0I2qKjGKTVO/4kAauQZLZCAOIDc79XEgjSgBtZUS8hymrsKSeBn4U8sp6j01T52nTgYqNPj7QRf1PXaW4DT1mGqMAx5VQdUYjgMHSDuSz5weNOPUiTjg0SD/7RlQ9TV7SbiCElVUNZRIObyBtV8fNeN8eresUzepG9Q35z9DDcJmbYXadn6harQE6zvUBnUI9vK97PyqnDpG/6E9i85fECVRTpk1Lw+crYQmnN1G3Xb2c9gNV8NO/IjzP0H+o32NOhestafT2WOwOWhC/tfEB2o0WP+hBpZArLnwogL8hF23BPuU8fMVoyQ+B2vZeqkKtfBQEFNlXlEj1PXAvwVre89X6lKw3jNHqePIfa7cgj22C7WlTk9z4Akf7WqXsK30e73B2qPf9clr0NVWRQc9CZuBvQBLSvOyGvgvwnr8KXKn2QGrtLqgDtZmsh+5uGzNkkf7L8BaUQlqxu7BDq0B+/CZpHZR+Seps4Ffp/vMxR7C3j8a9Newa+/DWmsKNrRKTHY/cryD/YYOSPuFKqdkdAjd1DJsX0ZGxv/GDgSIdYZi5zjoAAAAAElFTkSuQmCC>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADcAAAAZCAYAAACVfbYAAAACUElEQVR4Xu2Xv2uUQRCGJ6ggKhpUIorIRYgoWIhgSCpBLMRCFNJFAnYWERtBxFJF0UgIFoZ0WgliIygIKhaKBsEUQiAQO8EiZf6A+D7OLrff3ndwHnLehe+BF3Znbz9mZ2Z/nFlFRcX/4JB0V7rfooZ9Wm/wTpqX+hLbaWlNupXYtkvL0rHE1vUsSaOZ7Ya0Kp3J7F+kPZmta+mXTmW2mvRNei5tKw7ZTNbvakakXZmNkiRrZC+Fsp3MbD0HGWO/1TL7uoCSZHFb8oH1AAujLJsxKG3KjR1kUdqc9Fv2hwOExZG9Mth309JAPtBB3iTtv/KHo5/F5YdJhDuOu65baNkfssZhQtZqxaE/EdopvbD6XUdpPDR/4XyXrkgfrR4YLv1H0lbz78ZSj3NeSw/Mv33Hiqf2Pul8GHsrHTV/HR2UPgV7mT9NiU4+s+aHyStpLulfNA/ErHnds4Dx0MaZ/eF3XCE/QnvMfA6OEQC4asXHwYS0O7QXpCHpkvkCXsYfWaM/BTaYl2Ez5ffaT/O7MYVMEZiUKWkl6fPEI4sRFhPn1Kxxj5Op6EP6SromHUn6Zf60BaXwWdqb2IjkE2t8yVCGX5M+TpANiHN4HcEF6VdoA+M7pOPSbfPMbDTPMlmL5VfmT9tQNkQcbpp//KQVMxQhwmQLcJJ9gRMnrHEOYzzQyfZh8zLk+3DA6u9eqogMnwv9Mn/ahuhxYDw2PyTgshUzFCHKT81/SzniFH32Yj7nnvRBOhv61833Eu/Y91Z3miDx74UDCcr8qaioqPj3/AbHG3NS9pfk+wAAAABJRU5ErkJggg==>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGAAAAAZCAYAAADOtSsxAAADXElEQVR4Xu2Yz6tNURTHl1Dy+0eI/HgmSvJroJh4LwMSA4qRMqUoBkoyITORhJQBzwQlChkY6KUIKRNFSnlJGSgTfwDr89bZ96633j3v3Oc+7+q+/alv756199lvn7XWXnufI5LJZDKZjLFZ9VL1pkR3VTNqvccX01WrVLNiQxPMV61TTY4NZeDo36rFwT6nsH8I9k5mqeq5qru4Xi2WpBtqPco5rPol5je4XFxPqPUo4a2Yo6fEBjE7qhykQzgv9ryeraqb0tg/nu9ivkwsUPWp1jpbQ/iHP6KxIAVgUmzoUHhWMt5DOcJ+Ntg9rBj6XAr2o6pnqnnBXoOocqOPXCK1sYzGAyQZz3uvxE6pLmOvNA7AEdU31aZgr5EiR8cI/5BsWBkbOpSF0jgAgP19NDp2SnkAyvw7AA2UHwKRYPfeInbjMmf/3ziuOjcCnR64q5yqAHyORsdGGRoA9k024tIALFK9Uj1QrRCbQFLVhjMSGLuZI9kS1W1VV7CPFa0EADgt+hPjPrGNuTQAZD3ZP9zm0ipkwUWxE0EVvHOQDFNjwxjRagAoQ1/FTk0c6R+LrTzuZY8Ywi2xxn9Z49dL9cQTPEA7N/x06IgBSJvwk2BvBo61VBmqzRDIfgYejoOq3WJOpDxMFHtDPOD68PJCPabM8BLDsiPz56ruq15LvaxhPyQWdMb6WdiB7B/upBHhLdWXzSoxnyrwybtg4whJYuxxtjWq/e4a8GW/u+4SG4v9oSHcUJVxLKHZYhMjEMDySjVtppjTOCsDm5A/0pI11931LtUXd+1XB6eMk+66HZD90Sc4sE8Gl9F+Mf/5oEZ/nihsg15i+U6BMSouOw8O9/sETkplC+f74xm/eflIxDMwE/Rj+WCRLV3uul1sU31UnRJbvdT1+CWgVywp/QsqvqDvBdULseec5tr/mm6pbyJk/COplw0mSOlIMCn6A5OO9Y9gU+uBlcU+BGzAPEC7NuAI5YXVz99mP0hSgnvE7qPMjgo4GielSVB6yPIesQy5WrQD5YWVxCpbLlZ302qgLwH5JBagVLq2q46Jbdb85gSRcVD3/LcRPixRKq6IOZEN+KnqhuqMWHB6xZzN8mQpXpP6UiQzGO+OaofqodgYjMVvxslkMplMJpMZXf4AKrXDeZ/4v24AAAAASUVORK5CYII=>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADcAAAAZCAYAAACVfbYAAAACf0lEQVR4Xu2Xy6tPURTHl3LL4xLKFSWXgZGBR14ZMBCKAWVgpFAyYyAyuzKRlK4yUXQVeRWl7uB6FKHIa2CkmCkDQ38A34+1V3uf7Wb2y/npfOtTe+91zv6dtfdaa++fWadOnf6lVoun4nXinphfPlBpwPKzQet1TdwXP8TWyhZaJO6In+J9ZWu1Xopj5h++v7KFRsQJ82duNU3t1l2xwPzDRysbmi3WiJ3iu9jcNLdXU8UpMcXcORytdcTcfsY8JIcb1hZrg+WPnSyfLoodYrn4aL4QfSN2ZUZq49yXwobOmVdJQhJ734TkkHhe9Nk1HECE4Ug2/T4msE0rxlotQvJF0adqhnMbxZXCRkiGrS902Zo5RKXEgVnipPnuhSbLx1aLXRsu+pxxOPGuGEMUE8bLheB4IB+Pm+844cpOb0/2xeKheb4+E9/S+EqxVnwWu8U2sTfZWMyDYl1qc6kgHRBz8VvLzOf7a+7zMi+ySyE+DCfOFmOIH6/Ptz3igLguHqSxpZaf4aCPY4WIeJPaXBZIh6/m34BtU7JtsbwI6K04b76QzDWYxnmHG9MfmmfuQEl80ELLOThd3KieA65qZVFhB9gNxPvYqL7kKDuOaB9NbUQ6PCn6IebCFvokVpgvVMwVR1LPhRPjYk7qcx4ibjtlVNS7jmMXin6IxYtF4HIRc7+yPFdEUc9FmLDSfAjn4KE0Tj92eJd5SPFvY0myc5auSu1Sj81zbq64bTkXL1mOFsKW+QjXmK9n+mC56lI8QhNiTJw2DyPaUX3JUfKoFg4/EjfNHSIkEcVpTFwV+8znO2zNat5qzRTrU5sdiQL0X4hjiIs5IuQo95069bt+AU/whOLds9iOAAAAAElFTkSuQmCC>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADQAAAAZCAYAAAB+Sg0DAAACbUlEQVR4Xu2WzYuPURTHj4ZMDfLWNAlFUkih1OxIInnJgq2FlSIsLNUsJhubSdNgNRINpZRioUiSIqVYKCIWyk7KH8D307nXc39nnqZ+fhbP6PnWt557zr3nOW/3xaxFi0ZhnrhWPCjuLORzxP5i3Hjg8Cbxm/hLfC/+EEfFAfGEuPjP7IZjj3kQk1EhrBafm+tnBQ6bV+WcebvVAd3HKGwi1phn/lFUBGwRx6KwaaAaV8Wf4tGgiyCgI1HYNEyYV+dUVMxWvDYPiOz/FyAYODcqusQC8Z31tsc2mu/jZVHRDXJAdeBUexl4uWNGJ76Kx6KwCxDIY/O78K8xU0AZOMmcmZylwjjTS3ax/ykKu8U1c2c3REXCoPjE6p29IY6Ly8UHVgVMhnlRrBf7xO/i9aQD6G6bn7AjhZyL+7O4ULxp09c8Nbd3Julqn2DbzHufHywKOnDS/Ehnb5StgDPPxJVpzCm5NX0fMHcsg8sYJzJIznFxnfi2kNOyF9M3ibpT6LC3P31zgJX2anHfvFIfxIfiG/PM8lMCJdsZBEaAO9I49j4J4O2X8UpcUYwvmM/hf1NJFlv2i1UV322d9vgu7dUCZ3ivkSF4SFzaMaMCJxrZy0aHzbObgaM5mzxky/bgP/PFIfMTLa8jEKqSk0LX5G1A9Ut7tHdtu/UCTsCcTU6/F+J5cbv5C53qUVlaea+4K80lu5vT92nzVwqgGiQG0FKMSSjEZu4G7JEw7J1Nsn8CnL0rXhH3mV/QbHD2FhuYDX4r6e5Z9YLnrmENXUBFliT5Jas6gg5gDesBVcMec7BHUNhblfQtWrRoMR2/AcQQd1P58idcAAAAAElFTkSuQmCC>