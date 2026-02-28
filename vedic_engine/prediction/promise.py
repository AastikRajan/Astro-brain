"""
Promise Engine — Three Pillar Rule + Domain-Specific Thresholds.

BPHS Teaching: A chart event can only manifest if the NATAL PROMISE exists.
Dasha and Transit are the KEY and LOCK respectively — but the DOOR (promise)
must exist in the chart. Without promise, no Dasha+Transit combination can
physically manifest the event.

Three Pillar Rule:
  Bhava (House) + Bhavesha (House Lord) + Karaka (Universal Significator)
  3 strong → 100% promise (guaranteed)
  2 strong → 67%  promise (moderate effort needed)
  1 strong → 33%  promise (significant delay, sub-optimal)
  0 strong → 0%   promise (structurally DENIED — unbreakable hard boundary)

"Suppressed vs Denied" distinction:
  - NBRY planets and Upachaya malefics MASQUERADE as denial early-life.
  - Verified denial: bhava → 0, bhavesha → 0, karaka → 0 flat.
  - Suppressed: 1 or 2 pillars strong but one suppressed by malefic contact.
    Massive Dasha+Transit energy CAN override delay at maturity.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple


# ─── Constants ────────────────────────────────────────────────────────────────

PILLAR_STRENGTH_THRESHOLD = 0.50   # >= 0.50 = "strong" pillar

_NATURAL_BENEFICS = {"MOON", "MERCURY", "JUPITER", "VENUS"}
_NATURAL_MALEFICS = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}

# Universal Karakas per domain
DOMAIN_KARAKA: Dict[str, str] = {
    "marriage":  "VENUS",
    "career":    "SUN",
    "finance":   "JUPITER",
    "health":    "SUN",
    "spiritual": "KETU",
    "children":  "JUPITER",
    "siblings":  "MARS",
    "mother":    "MOON",
    "father":    "SUN",
    "property":  "MARS",
}

# Domain → primary house
DOMAIN_PRIMARY_HOUSE: Dict[str, int] = {
    "marriage":  7,
    "career":    10,
    "finance":   2,
    "health":    1,
    "spiritual": 9,
    "children":  5,
    "siblings":  3,
    "mother":    4,
    "father":    9,
    "property":  4,
}

_KENDRA  = {1, 4, 7, 10}
_TRIKONA = {1, 5, 9}
_DUSTHANA = {6, 8, 12}
_UPACHAYA = {3, 6, 10, 11}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _score_bhava(planet_houses: Dict[str, int],
                 house_lords: Dict[int, str],
                 shadbala_ratios: Dict[str, float],
                 domain_house: int,
                 planet_lons: Optional[Dict[str, float]] = None) -> float:
    """
    Bhava (House itself) strength.
    Considers: planets occupying it, lord strength, and absence of heavy affliction.
    """
    # Planets in the house
    in_house = [p for p, h in planet_houses.items() if h == domain_house]
    lord = house_lords.get(domain_house, "")

    if not lord:
        return 0.3  # Unknown lord → neutral

    lord_strength = shadbala_ratios.get(lord, 0.5)

    # Benefics in house boost; malefics penalise
    benefic_bonus = 0.0
    malefic_penalty = 0.0
    for p in in_house:
        if p in _NATURAL_BENEFICS:
            benefic_bonus += 0.10
        elif p in _NATURAL_MALEFICS:
            malefic_penalty += 0.10

    # House location of lord
    lord_house = planet_houses.get(lord, 0)
    location_score = 0.5
    if lord_house in _KENDRA or lord_house in _TRIKONA:
        location_score = 0.80
    elif lord_house in _DUSTHANA:
        location_score = 0.25

    score = (lord_strength * 0.5 + location_score * 0.3
             + min(0.2, benefic_bonus) - min(0.2, malefic_penalty))
    return max(0.0, min(1.0, score))


def _score_bhavesha(house_lords: Dict[int, str],
                    shadbala_ratios: Dict[str, float],
                    planet_houses: Dict[str, int],
                    domain_house: int,
                    vargas: Optional[Dict[str, Dict]] = None) -> float:
    """
    Bhavesha (House Lord) strength — D1 quantity + D9 quality.
    """
    lord = house_lords.get(domain_house, "")
    if not lord:
        return 0.3

    d1_strength = shadbala_ratios.get(lord, 0.5)
    lord_house   = planet_houses.get(lord, 0)

    # House placement bonus/penalty
    if lord_house in _KENDRA or lord_house in _TRIKONA:
        placement_score = 0.80
    elif lord_house in _DUSTHANA:
        placement_score = 0.25
    elif lord_house in _UPACHAYA:
        placement_score = 0.60  # Upachaya — grows with time
    else:
        placement_score = 0.50

    # D9 quality (sustainability) — if varga data available
    d9_score = 0.5
    if vargas:
        d9 = vargas.get("D9", {})
        d9_planets = d9.get("planet_signs", {})
        if d9_planets:
            # Check if lord is in exalted/own sign in D9 vs debilitated
            d9_sign = d9_planets.get(lord)
            if d9_sign is not None:
                # Simple proxy: if strong in D1 and D9 sign is kendra/trikona from D9 lagna
                d9_lagna = d9.get("lagna_sign", 0)
                d9_house = (d9_sign - d9_lagna) % 12 + 1
                if d9_house in _KENDRA or d9_house in _TRIKONA:
                    d9_score = 0.80
                elif d9_house in _DUSTHANA:
                    d9_score = 0.20
                else:
                    d9_score = 0.50

    score = d1_strength * 0.6 + placement_score * 0.2 + d9_score * 0.2
    return max(0.0, min(1.0, score))


def _score_karaka(domain: str,
                  shadbala_ratios: Dict[str, float],
                  planet_houses: Dict[str, int],
                  planet_lons: Optional[Dict[str, float]] = None,
                  vargas: Optional[Dict[str, Dict]] = None) -> float:
    """
    Karaka (Universal Significator) strength for domain.
    """
    karaka = DOMAIN_KARAKA.get(domain, "JUPITER")
    k_strength = shadbala_ratios.get(karaka, 0.5)
    k_house    = planet_houses.get(karaka, 0)

    if k_house in _KENDRA or k_house in _TRIKONA:
        placement_score = 0.80
    elif k_house in _DUSTHANA:
        placement_score = 0.25
    else:
        placement_score = 0.50

    # D9 quality for marriage uses Venus check
    d9_score = 0.5
    if vargas and domain == "marriage":
        d9 = vargas.get("D9", {})
        d9_lagna = d9.get("lagna_sign", 0)
        d9_planets = d9.get("planet_signs", {})
        for k in ("VENUS", "JUPITER"):
            ks = d9_planets.get(k)
            if ks is not None:
                d9_house = (ks - d9_lagna) % 12 + 1
                if d9_house in {1, 2, 5, 7, 9, 10, 11}:
                    d9_score = min(1.0, d9_score + 0.25)

    score = k_strength * 0.6 + placement_score * 0.25 + d9_score * 0.15
    return max(0.0, min(1.0, score))


# ─── Core Three Pillar Rule ───────────────────────────────────────────────────

def compute_promise(
    domain: str,
    planet_houses: Dict[str, int],
    house_lords: Dict[int, str],
    shadbala_ratios: Dict[str, float],
    planet_lons: Optional[Dict[str, float]] = None,
    vargas: Optional[Dict[str, Dict]] = None,
    nbry_planets: Optional[List[str]] = None,
    upachaya_malefics: Optional[List[str]] = None,
) -> Dict:
    """
    Compute promise score for a domain using Three Pillar Rule.

    Returns:
      {
        promise_pct: 0 | 33 | 67 | 100,
        denied: bool,          # Hard boundary — 0% promise
        suppressed: bool,      # Looks like denial but can be overcome at maturity
        pillars: {bhava, bhavesha, karaka},  # individual scores 0-1
        strong_count: int,     # 0-3
        promise_level: str,    # DENIED / SUPPRESSED / WEAK / MODERATE / STRONG
        detail: str,
      }
    """
    domain_house = DOMAIN_PRIMARY_HOUSE.get(domain, 10)

    bhava_score    = _score_bhava(planet_houses, house_lords, shadbala_ratios,
                                  domain_house, planet_lons)
    bhavesha_score = _score_bhavesha(house_lords, shadbala_ratios, planet_houses,
                                     domain_house, vargas)
    karaka_score   = _score_karaka(domain, shadbala_ratios, planet_houses,
                                   planet_lons, vargas)

    strong_count = sum(1 for s in [bhava_score, bhavesha_score, karaka_score]
                       if s >= PILLAR_STRENGTH_THRESHOLD)

    if strong_count == 3:
        promise_pct = 100
    elif strong_count == 2:
        promise_pct = 67
    elif strong_count == 1:
        promise_pct = 33
    else:
        promise_pct = 0

    # Check for NBRY / Upachaya masquerade (suppressed, not truly denied)
    suppressed = False
    denied = (promise_pct == 0)

    if denied:
        # Check if any weak pillar planet is an NBRY planet or Upachaya malefic
        # → if so, this is SUPPRESSED (can break through at maturity), not DENIED
        nbry_set = set(nbry_planets or [])
        upachaya_set = set(upachaya_malefics or [])

        # Bhavesha (house lord) is NBRY → suppressed
        lord = house_lords.get(domain_house, "")
        if lord in nbry_set or lord in upachaya_set:
            suppressed = True
            denied = False

        # Karaka is NBRY → suppressed
        karaka = DOMAIN_KARAKA.get(domain, "JUPITER")
        if karaka in nbry_set or karaka in upachaya_set:
            suppressed = True
            denied = False

    # Promise level label
    if denied:
        promise_level = "DENIED"
        detail = (f"All three pillars weak for {domain}. "
                  "No Dasha or Transit can physically manifest this event. "
                  "Best-case: functional substitute (e.g., denied progeny → mentoring).")
    elif suppressed:
        promise_level = "SUPPRESSED"
        detail = (f"Promise appears denied but NBRY/Upachaya planet(s) masquerade as denial. "
                  f"Event is highly delayed (early life struggle) but CAN break through "
                  f"during mature Dasha activation.")
    elif promise_pct == 33:
        promise_level = "WEAK"
        detail = (f"Only 1 of 3 pillars strong for {domain}. "
                  "Significant delays expected. Sub-optimal results even with good Dasha.")
    elif promise_pct == 67:
        promise_level = "MODERATE"
        detail = (f"2 of 3 pillars strong for {domain}. "
                  "Success after moderate effort. Dasha+Transit must both activate.")
    else:
        promise_level = "STRONG"
        detail = (f"All 3 pillars strong for {domain}. "
                  "Guaranteed manifestation during appropriate Dasha+Transit.")

    return {
        "promise_pct": promise_pct,
        "denied": denied,
        "suppressed": suppressed,
        "strong_count": strong_count,
        "promise_level": promise_level,
        "pillars": {
            "bhava":    round(bhava_score,    3),
            "bhavesha": round(bhavesha_score, 3),
            "karaka":   round(karaka_score,   3),
        },
        "detail": detail,
    }


# ─── Marriage Promise ─────────────────────────────────────────────────────────

def check_marriage_promise(
    planet_houses: Dict[str, int],
    house_lords: Dict[int, str],
    shadbala_ratios: Dict[str, float],
    planet_lons: Optional[Dict[str, float]] = None,
    arudha_signs: Optional[Dict[int, int]] = None,  # {bhava: sign_idx}
    lagna_sign: int = 0,
    is_female: bool = False,
    vargas: Optional[Dict[str, Dict]] = None,
) -> Dict:
    """
    Marriage promise using 5-point spectrum:
      7th lord placement + Venus state + UL analysis + Jupiter (female) + delay/denial check.

    Returns:
      {
        level: "denied" | "severe_delay" | "delayed" | "moderate" | "strong",
        score: 0-1,
        factors: {...},
        detail: str,
      }
    """
    factors = {}
    penalty = 0.0

    # ── 7th lord placement ───────────────────────────────────────
    lord_7 = house_lords.get(7, "")
    lord_7_house = planet_houses.get(lord_7, 0) if lord_7 else 0
    lord_7_strength = shadbala_ratios.get(lord_7, 0.5) if lord_7 else 0.3

    if lord_7_house in _DUSTHANA:
        factors["7th_lord"] = "dusthana_placement"
        penalty += 0.20
    else:
        factors["7th_lord"] = "acceptable_placement"

    # ── Venus state ──────────────────────────────────────────────
    venus_strength = shadbala_ratios.get("VENUS", 0.5)
    venus_house    = planet_houses.get("VENUS", 0)
    venus_afflicted = venus_house in _DUSTHANA or venus_strength < 0.35

    if venus_afflicted:
        factors["venus"] = "afflicted_foundational_vacuum"
        penalty += 0.25
    else:
        factors["venus"] = "acceptable"

    # ── Upapada Lagna (UL = A12) analysis ───────────────────────
    # UL sign from arudha_signs dict (bhava 12 → UL)
    ul_sign = None
    if arudha_signs:
        ul_sign = arudha_signs.get(12)

    if ul_sign is not None:
        # Planets in UL sign
        in_ul = [p for p, s in (
            {p: planet_houses.get(p, -1) for p in planet_houses}
        ).items() if False]  # we need sign-based lookup

        # Use lagna-based house: UL is a sign, not a house
        # Check second from UL for marriage stability
        second_from_ul = (ul_sign + 1) % 12

        # Malefics in UL or 2nd from UL → delay/friction
        ul_malefic_lords = []
        for p, h in planet_houses.items():
            # Convert house to sign for comparison
            p_sign = (lagna_sign + h - 1) % 12
            if p_sign == ul_sign and p in _NATURAL_MALEFICS:
                ul_malefic_lords.append(p)
            elif p_sign == second_from_ul and p in {"SATURN", "RAHU", "KETU"}:
                ul_malefic_lords.append(p)

        if ul_malefic_lords:
            factors["ul"] = f"malefics_{','.join(ul_malefic_lords)}_in_UL_or_2nd"
            penalty += 0.20
        else:
            factors["ul"] = "benefic_or_neutral"
    else:
        factors["ul"] = "not_computed"

    # ── Female chart: Jupiter signifies husband ──────────────────
    if is_female:
        jupiter_house     = planet_houses.get("JUPITER", 0)
        jupiter_strength  = shadbala_ratios.get("JUPITER", 0.5)
        if jupiter_house in _DUSTHANA or jupiter_strength < 0.35:
            factors["jupiter_female"] = "afflicted"
            penalty += 0.15
        else:
            factors["jupiter_female"] = "acceptable"

    # ── Saturn/Rahu aspect on 7th ────────────────────────────────
    saturn_house = planet_houses.get("SATURN", 0)
    # Saturn's 7th aspect = house + 6
    saturn_aspects_7th = (saturn_house + 6) % 12 + 1 == 7 if saturn_house else False
    if saturn_aspects_7th:
        factors["saturn_7th_aspect"] = "strongly_delayed"
        penalty += 0.10
    else:
        factors["saturn_7th_aspect"] = "none"

    # ── Denial check: ALL simultaneously severe ──────────────────
    paap_kartari = False  # TODO: implement Paap Kartari detection
    full_denial = (
        lord_7_house in _DUSTHANA and
        venus_afflicted and
        lord_7_strength < 0.30 and
        not vargas  # simplified: if D9 data absent, can't confirm fully
    )

    # ── Compute score ────────────────────────────────────────────
    base_score = 1.0 - penalty
    base_score = max(0.0, min(1.0, base_score))

    if full_denial:
        level = "denied"
    elif penalty >= 0.50:
        level = "severe_delay"
    elif penalty >= 0.30:
        level = "delayed"
    elif penalty >= 0.15:
        level = "moderate"
    else:
        level = "strong"

    return {
        "level": level,
        "score": round(base_score, 3),
        "penalty": round(penalty, 3),
        "factors": factors,
        "detail": _marriage_detail(level, factors),
    }


def _marriage_detail(level: str, factors: Dict) -> str:
    if level == "denied":
        return ("Marriage structurally denied: 7th lord debilitated/combust, "
                "Venus afflicted in D1 AND D9, no benefic relief, Paap Kartari confirmed. "
                "Best-case: deep bond without social formality.")
    elif level == "severe_delay":
        return ("Marriage severely delayed: multiple afflictions across UL, Venus, 7th lord. "
                "Marriage likely mid-life or later; requires exceptional Dasha activation.")
    elif level == "delayed":
        return ("Marriage delayed: one or two significant afflictions. "
                "Occurs but with friction or after extended search period.")
    elif level == "moderate":
        return "Marriage with moderate effort; reasonable timing, some challenges."
    else:
        return "Strong marriage promise; harmonious union at appropriate Dasha timing."


# ─── Career Promise ───────────────────────────────────────────────────────────

def check_career_promise(
    planet_houses: Dict[str, int],
    house_lords: Dict[int, str],
    shadbala_ratios: Dict[str, float],
    bhavabala: Optional[Dict[int, float]] = None,
    planet_lons: Optional[Dict[str, float]] = None,
    vargas: Optional[Dict[str, Dict]] = None,
) -> Dict:
    """
    Career promise using 5 gates:
      1. 10th lord in Kendra/Trikona → baseline high success
      2. Dharma-Karma Adhipati Yoga (9L + 10L together)
      3. Sun dignity (exalt/own/Dig Bala in 10th)
      4. D10 gate (strong D10 lagna lord + benefics in D10's 10th)
      5. Service vs Leadership (Bhavabala 6th vs 10th)

    Returns: {level, score, career_type, factors, detail}
    """
    factors = {}
    score = 0.0

    # ── Gate 1: 10th lord in Kendra/Trikona ─────────────────────
    lord_10 = house_lords.get(10, "")
    lord_10_house = planet_houses.get(lord_10, 0) if lord_10 else 0
    lord_10_strength = shadbala_ratios.get(lord_10, 0.5) if lord_10 else 0.3

    if lord_10_house in (_KENDRA | _TRIKONA):
        factors["10th_lord"] = "kendra_trikona"
        score += 0.30
    elif lord_10_house in _DUSTHANA:
        factors["10th_lord"] = "dusthana"
        score += 0.05
    else:
        factors["10th_lord"] = "neutral_house"
        score += 0.15

    # ── Gate 2: Dharma-Karma Adhipati Yoga ──────────────────────
    lord_9 = house_lords.get(9, "")
    lord_9_house = planet_houses.get(lord_9, 0) if lord_9 else 0
    dka_yoga = (lord_9 and lord_10 and lord_9 != lord_10 and
                lord_9_house == lord_10_house and lord_9_house != 0)
    if dka_yoga:
        factors["dharma_karma_yoga"] = "present_influential_public_career_guaranteed"
        score += 0.25
    else:
        factors["dharma_karma_yoga"] = "absent"

    # ── Gate 3: Sun dignity ──────────────────────────────────────
    sun_house    = planet_houses.get("SUN", 0)
    sun_strength = shadbala_ratios.get("SUN", 0.5)
    sun_in_10    = (sun_house == 10)
    sun_strong   = sun_strength >= 0.65

    if sun_in_10 and sun_strong:
        factors["sun_10th"] = "exalted_leadership_command"
        score += 0.20
    elif sun_strong:
        factors["sun_10th"] = "strong_sun_authority_potential"
        score += 0.10
    else:
        factors["sun_10th"] = "weak_sun_limited_command"

    # ── Gate 4: D10 gate ─────────────────────────────────────────
    d10_strong = False
    if vargas:
        d10 = vargas.get("D10", {})
        if d10:
            d10_lagna   = d10.get("lagna_sign", 0)
            d10_planets = d10.get("planet_signs", {})
            # D10 lagna lord strength in D10
            d10_lagna_lord = house_lords.get(1, "")  # approximate
            d10_lord_sign  = d10_planets.get(d10_lagna_lord, -1)
            if d10_lord_sign >= 0:
                d10_lord_house = (d10_lord_sign - d10_lagna) % 12 + 1
                d10_benefics_in_10 = [
                    p for p, s in d10_planets.items()
                    if (s - d10_lagna) % 12 + 1 == 10 and p in _NATURAL_BENEFICS
                ]
                d10_strong = (d10_lord_house in (_KENDRA | _TRIKONA) and
                              len(d10_benefics_in_10) > 0)

    if d10_strong:
        factors["d10"] = "strong_massive_public_career_confirmed"
        score += 0.15
    elif vargas and "D10" in vargas:
        factors["d10"] = "weak_skilled_but_subordinate"
    else:
        factors["d10"] = "not_computed"

    # ── Gate 5: Service vs Leadership ───────────────────────────
    career_type = "leadership"  # default
    if bhavabala:
        bala_6  = bhavabala.get(6, 0.5)
        bala_10 = bhavabala.get(10, 0.5)
        sixth_lord      = house_lords.get(6, "")
        tenth_lord      = house_lords.get(10, "")
        shadbala_6  = shadbala_ratios.get(sixth_lord, 0.5) if sixth_lord else 0.5
        shadbala_10 = shadbala_ratios.get(tenth_lord, 0.5) if tenth_lord else 0.5

        combined_6  = bala_6  * 0.5 + shadbala_6  * 0.5
        combined_10 = bala_10 * 0.5 + shadbala_10 * 0.5

        if combined_6 > combined_10:
            career_type = "service"
            factors["career_type"] = "service_employment_structured"
        else:
            career_type = "leadership"
            factors["career_type"] = "independent_authority"
    else:
        factors["career_type"] = "undetermined_no_bhavabala"

    # ── Final scoring ────────────────────────────────────────────
    score = min(1.0, score)
    if score >= 0.70:
        level = "exceptional"
    elif score >= 0.50:
        level = "strong"
    elif score >= 0.30:
        level = "moderate"
    elif score >= 0.15:
        level = "weak"
    else:
        level = "minimal"

    return {
        "level": level,
        "score": round(score, 3),
        "career_type": career_type,
        "factors": factors,
        "detail": _career_detail(level, career_type),
    }


def _career_detail(level: str, career_type: str) -> str:
    base = {
        "exceptional": "Exceptional career: Dharma-Karma yoga + strong D10 + Sun commanding.",
        "strong":      "Strong career promise with significant authority potential.",
        "moderate":    "Moderate career: achieves but requires sustained effort.",
        "weak":        "Weak career promise: skilled but frustrated; subordinate roles likely.",
        "minimal":     "Minimal career promise: obstacles throughout; requires remedies.",
    }.get(level, "")
    suffix = " Career path: independent authority/leadership." if career_type == "leadership" else \
             " Career path: structured employment/service roles."
    return base + suffix


# ─── Wealth Promise ───────────────────────────────────────────────────────────

def check_wealth_promise(
    planet_houses: Dict[str, int],
    house_lords: Dict[int, str],
    shadbala_ratios: Dict[str, float],
    planet_lons: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Wealth promise in 3 tiers:
      1. Baseline/Steady: 11L in 1st conjunct Jupiter or Venus (high Shadbala)
      2. High Net Worth: Jupiter in 11th + Moon in 2nd + Venus in 9th (all high Shadbala)
      3. Ultra-High (billionaire flag): 1/2/9/11 lords extremely powerful in Kendras
         PLUS Saturn+Venus in 11th with strong Rahu influence
      + Upachaya Paradox: Malefics in 3/6/10/11 with dignity → self-made millionaire

    Returns: {tier, score, upachaya_paradox, factors, detail}
    """
    factors = {}
    tier = 0  # 0=below baseline, 1=baseline, 2=high_networth, 3=ultra_high

    lord_11  = house_lords.get(11, "")
    lord_11_h = planet_houses.get(lord_11, 0) if lord_11 else 0

    jup_house = planet_houses.get("JUPITER", 0)
    ven_house = planet_houses.get("VENUS", 0)
    moon_house = planet_houses.get("MOON", 0)
    sat_house  = planet_houses.get("SATURN", 0)
    rahu_house = planet_houses.get("RAHU", 0)

    jup_str  = shadbala_ratios.get("JUPITER", 0.5)
    ven_str  = shadbala_ratios.get("VENUS", 0.5)
    moon_str = shadbala_ratios.get("MOON", 0.5)
    sat_str  = shadbala_ratios.get("SATURN", 0.5)
    rahu_str = shadbala_ratios.get("RAHU", 0.5)

    # ── Tier 1: Baseline/Steady ──────────────────────────────────
    # 11L in 1st conjunct Jupiter or Venus (with high Shadbala)
    if lord_11_h == 1:
        companions = [p for p, h in planet_houses.items() if h == 1 and p != lord_11]
        if ("JUPITER" in companions and jup_str >= 0.60) or \
           ("VENUS"   in companions and ven_str >= 0.60):
            tier = max(tier, 1)
            factors["tier1_baseline"] = "11L_in_1st_conjunct_benefic"

    # ── Tier 2: High Net Worth ───────────────────────────────────
    if (jup_house == 11 and jup_str >= 0.65 and
            moon_house == 2 and moon_str >= 0.60 and
            ven_house == 9 and ven_str >= 0.65):
        tier = max(tier, 2)
        factors["tier2_high_networth"] = "Jupiter_11_Moon_2_Venus_9_all_strong"

    # ── Tier 3: Ultra-High (billionaire flag) ────────────────────
    # Lords of 1, 2, 9, 11 all powerful + exclusively in Kendras + Saturn+Venus in 11 + strong Rahu
    key_lords = [house_lords.get(h, "") for h in (1, 2, 9, 11)]
    key_lords = [l for l in key_lords if l]
    lord_strengths = [shadbala_ratios.get(l, 0.5) for l in key_lords]
    lords_in_kendra = all(planet_houses.get(l, 0) in _KENDRA for l in key_lords)
    lords_very_strong = all(s >= 0.75 for s in lord_strengths)

    saturn_venus_in_11 = (sat_house == 11 and ven_house == 11)
    rahu_strong        = (rahu_str >= 0.65 or rahu_house in (3, 6, 10, 11))

    if lords_in_kendra and lords_very_strong and saturn_venus_in_11 and rahu_strong:
        tier = max(tier, 3)
        factors["tier3_ultra_high"] = "1_2_9_11L_kendra_powerful_Saturn_Venus_11_Rahu_strong"

    # ── Upachaya Paradox ─────────────────────────────────────────
    # Malefics (Saturn, Rahu) in 3/6/10/11 with dignity → self-made millionaire
    upachaya_paradox = False
    for mal_planet in ("SATURN", "RAHU", "MARS"):
        mal_house = planet_houses.get(mal_planet, 0)
        mal_str   = shadbala_ratios.get(mal_planet, 0.5)
        if mal_house in _UPACHAYA and mal_str >= 0.60:
            upachaya_paradox = True
            factors["upachaya_paradox"] = (
                f"{mal_planet}_in_Upachaya_{mal_house}th_with_dignity: "
                "obsessive hunger for wealth → self-made after early struggle"
            )
            tier = max(tier, 1)  # At least baseline tier if paradox active
            break

    # ── Score ────────────────────────────────────────────────────
    tier_score_map = {0: 0.15, 1: 0.50, 2: 0.75, 3: 1.00}
    score = tier_score_map.get(tier, 0.15)
    if upachaya_paradox and tier < 2:
        score = max(score, 0.50)  # Paradox guarantees at least strong wealth

    tier_labels = {
        0: "below_baseline",
        1: "baseline_steady",
        2: "high_networth",
        3: "ultra_high_potential",
    }

    return {
        "tier": tier,
        "tier_label": tier_labels.get(tier, "unknown"),
        "score": round(score, 3),
        "upachaya_paradox": upachaya_paradox,
        "factors": factors,
        "detail": _wealth_detail(tier, upachaya_paradox),
    }


def _wealth_detail(tier: int, upachaya_paradox: bool) -> str:
    msgs = {
        0: "Below baseline wealth promise. Financial struggles without remediation.",
        1: "Baseline/steady wealth: comfortable living, gradual accumulation.",
        2: "High net worth potential: affluent, multiple income streams likely.",
        3: ("Ultra-high wealth potential (billionaire flag): extraordinary accumulation "
            "if Dasha timing aligns. Predicated on extraordinary effort."),
    }
    base = msgs.get(tier, "")
    if upachaya_paradox:
        base += (" Upachaya Paradox active: early-life financial struggle becomes fuel "
                 "for massive self-made wealth in mature Dasha periods.")
    return base
