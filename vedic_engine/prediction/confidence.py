"""
Prediction Confidence Scoring.

Multi-system agreement formula:
  confidence = (dasha_alignment × 0.30) + (transit_support × 0.25)
             + (ashtakvarga_score × 0.15) + (yoga_activation × 0.15)
             + (kp_sublord_confirmation × 0.15)

Each component is normalised to 0-1 before weighting.
"""
from __future__ import annotations
from typing import Dict, List, Optional


# ─── Weight constants (module-level reference; actual weights are adaptive per gate) ──
W_DASHA        = 0.25   # Vimshottari dasha lord alignment
W_TRANSIT      = 0.20   # Transit support (Gochar + BAV bindus)
W_ASHTAKVARGA  = 0.15   # Natal SAV/BAV strength of domain signs
W_YOGA         = 0.13   # Active yoga relevance
W_KP           = 0.12   # KP sub-lord confirmation
W_FUNCTIONAL   = 0.08   # Functional benefic/malefic role of dasha lord
W_HOUSE_LORD   = 0.00   # REMOVED (§9.3): already in Promise gate → zero weight


def _clamp(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


# ─── Individual component scorers ────────────────────────────────

def score_dasha_alignment(
    dasha_planet: str,
    antardasha_planet: str,
    domain: str,
    planet_domain_map: Dict[str, List[str]],
    shadbala_ratios: Dict[str, float],
) -> float:
    """
    Dasha planet alignment with queried domain.
    - 0.60 if Maha-dasha planet signifies the domain
    - 0.40 bonus if Antar-dasha planet also signifies it
    - Weighted by shadbala ratio (0.5 – 1.5 range normalised)
    """
    score = 0.0
    md_domains = planet_domain_map.get(dasha_planet, [])
    ad_domains = planet_domain_map.get(antardasha_planet, [])

    if domain in md_domains:
        score += 0.6
    if domain in ad_domains:
        score += 0.4

    # Modulate by strength of dasha-lord
    md_ratio = shadbala_ratios.get(dasha_planet, 1.0)
    strength_mod = _clamp(md_ratio / 1.5)          # 1.5× minimum is strong
    score = score * (0.5 + 0.5 * strength_mod)     # 50-100% of raw score

    return _clamp(score)


def score_transit_support(
    transit_scores: Dict[str, Dict],
    domain_planets: List[str],
) -> float:
    """
    Average net_score of domain-relevant transiting planets.
    """
    relevant = [transit_scores[p]["net_score"]
                for p in domain_planets if p in transit_scores]
    if not relevant:
        return 0.3     # neutral when no data
    return _clamp(sum(relevant) / len(relevant))


# ── Karaka-BAV mappings per domain (classical Sthira Karakas) ──────────────
# Each entry: list of (planet_name, sign_offset_from_planet)
# sign_offset_from_planet: 0 = planet's own sign, N = Nth sign from planet
# Special: ("HOUSE_LORD", house_number) → use the lord of that house's BAV at that sign
DOMAIN_KARAKA_BAV_MAP: Dict[str, list] = {
    "career":  [("SATURN", 10), ("SUN", 10)],         # Saturn BAV@10th-from-Saturn, Sun BAV@10th-from-Sun
    "finance": [("JUPITER", 0), ("HOUSE_LORD", 2)],    # Jupiter BAV@self, 2nd-lord BAV@self
    "marriage":[("VENUS", 7)],                          # Venus BAV@7th-from-Venus
    "health":  [("SUN", 1), ("SATURN", 8)],             # Sun BAV@Lagna, Saturn BAV@8th-from-Saturn
}


def _tiered_bav(values: list, signs: list) -> float:
    """Tiered BAV scoring — shared by SAV and individual planet BAVs."""
    picked = [values[s] for s in signs if 0 <= s < len(values)]
    if not picked:
        return 0.3
    avg = sum(picked) / len(picked)
    if avg <= 2.0:
        return 0.0
    elif avg <= 3.0:
        return 0.05 + (avg - 2.0) * 0.10
    elif avg <= 4.0:
        return 0.15 + (avg - 3.0) * 0.25
    elif avg <= 5.0:
        return 0.40 + (avg - 4.0) * 0.20
    else:
        return min(1.0, 0.60 + (avg - 5.0) / 3.0 * 0.40)


def score_ashtakvarga(
    sarva_av: Optional[List[int]],
    relevant_signs: List[int],
    dasha_planet_bav: Optional[List[int]] = None,
    karaka_bav_data: Optional[Dict] = None,
    domain: str = "career",
) -> float:
    """
    Three-signal Ashtakavarga blend (classical karaka-specific BAV).

    Architecture:
      40% SAV — collective strength of relevant signs
      35% Karaka BAV — domain-specific sthira karaka's own BAV
      25% Dasha BAV — current dasha lord's own BAV in those signs

    Uses TIERED thresholds per research (not linear):
      0-3 bindus  → malefic / disastrous zone      → 0.0–0.15
      4 bindus    → neutral equilibrium              → 0.40
      5-8 bindus  → exponentially positive           → 0.55–1.0
    """
    if not sarva_av or not relevant_signs:
        return 0.3

    # ── Signal 1: SAV (40%) ──
    sav_score = _tiered_bav(sarva_av, relevant_signs)

    # ── Signal 2: Karaka BAV (35%) ──
    karaka_score = 0.3   # neutral fallback
    if karaka_bav_data and isinstance(karaka_bav_data, dict):
        bhinna = karaka_bav_data.get("bhinna", {})
        planet_signs_map = karaka_bav_data.get("planet_signs", {})
        house_lords_map  = karaka_bav_data.get("house_lords", {})
        mappings = DOMAIN_KARAKA_BAV_MAP.get(domain.lower(), [])
        karaka_scores = []
        for planet_key, offset in mappings:
            if planet_key == "HOUSE_LORD":
                # offset here is the house number; get its lord
                lord = house_lords_map.get(offset, house_lords_map.get(str(offset)))
                if not lord:
                    continue
                bav_row = bhinna.get(lord)
                if bav_row and isinstance(bav_row, (list, tuple)) and len(bav_row) >= 12:
                    # Evaluate at lord's own sign
                    lord_sign = planet_signs_map.get(lord, 0)
                    target_sign = lord_sign  # BAV at the lord's own position
                    karaka_scores.append(_tiered_bav(bav_row, [target_sign]))
            else:
                bav_row = bhinna.get(planet_key)
                if bav_row and isinstance(bav_row, (list, tuple)) and len(bav_row) >= 12:
                    # Target sign = planet's natal sign + offset (1-indexed → 0-indexed)
                    planet_sign = planet_signs_map.get(planet_key, 0)
                    if offset == 0:
                        target_sign = planet_sign
                    else:
                        target_sign = (planet_sign + offset - 1) % 12
                    karaka_scores.append(_tiered_bav(bav_row, [target_sign]))
        if karaka_scores:
            karaka_score = sum(karaka_scores) / len(karaka_scores)

    # ── Signal 3: Dasha BAV (25%) ──
    dasha_score = 0.3    # neutral fallback
    if dasha_planet_bav:
        dasha_score = _tiered_bav(dasha_planet_bav, relevant_signs)

    # ── Three-signal blend ──
    blended = 0.40 * sav_score + 0.35 * karaka_score + 0.25 * dasha_score
    return _clamp(blended)


def score_yoga_activation(
    active_yogas: List[Dict],
    domain: str,
) -> float:
    """
    Quality and domain relevance of currently active yogas.
    - Raja Yogas → career, authority
    - Dhana Yogas → finance
    - Gajakesari → career, wealth
    - Amala → reputation, career
    - etc.
    """
    domain_yoga_map = {
        "career":   ["Raja Yoga", "Gajakesari Yoga", "Amala Yoga", "Pancha Mahapurusha",
                     "Budha-Aditya Yoga", "Adhi Yoga"],
        "finance":  ["Dhana Yoga", "Gajakesari Yoga", "Chandra-Mangal Yoga",
                     "Lakshmi Yoga", "Kubera Yoga"],
        "marriage": ["Kalathra Yoga", "Malavya Yoga", "Venus strong", "7L Dhana"],
        "health":   ["Viparita Raja Yoga", "Neechabhanga"],
        "spiritual":["Viparita Raja Yoga", "Hamsa Yoga", "Neechabhanga"],
    }
    relevant_names = domain_yoga_map.get(domain.lower(), [])
    if not active_yogas:
        return 0.1

    matches = 0
    for yoga in active_yogas:
        # Handle both dict and dataclass/namedtuple
        if isinstance(yoga, dict):
            name = yoga.get("name", "")
        else:
            name = getattr(yoga, "name", str(yoga))
        if any(r.lower() in name.lower() for r in relevant_names):
            matches += 1

    # More matches = stronger; cap at 5
    score = min(matches, 5) / 5.0
    # Baseline: having any yogas at all is positive
    score = max(score, 0.1 * min(len(active_yogas), 5) / 5.0)
    return _clamp(score)


def score_kp_sublord(
    kp_significations: Dict[str, List[int]],
    domain_houses: List[int],
    dasha_planet: str,
    antardasha_planet: str,
    negator_houses: Optional[List[int]] = None,
) -> float:
    """
    KP system confirmation: check if dasha/antardasha planet's KP
    significations include domain-relevant houses.
    Negator house significations reduce the score.
    """
    neg_set = set(negator_houses) if negator_houses else set()

    def sig_overlap(planet: str) -> float:
        sigs = set(kp_significations.get(planet, []))
        domain_set = set(domain_houses)
        if not domain_set:
            return 0.0
        overlap = len(sigs & domain_set)
        neg_overlap = len(sigs & neg_set)
        raw = _clamp(overlap / len(domain_set))
        # Negator penalty: each negator house signified reduces score by 0.15
        penalty = min(raw, neg_overlap * 0.15)
        return _clamp(raw - penalty)

    md_score = sig_overlap(dasha_planet)
    ad_score = sig_overlap(antardasha_planet)
    # Weighted: dasha more important
    combined = 0.60 * md_score + 0.40 * ad_score
    return _clamp(combined)


def score_functional_alignment(
    dasha_planet: str,
    antardasha_planet: str,
    functional_analysis: Dict,
    domain: Optional[str] = None,
    planet_houses: Optional[Dict[str, int]] = None,
) -> float:
    """
    Score how functionally aligned the dasha lords are for the chart's lagna.

    Yogakaraka = 1.0, functional benefic = 0.6-0.8, neutral = 0.4,
    functional malefic = 0.15, badhaka = 0.05 (unless spiritual domain), maraka = 0.15.

    If dasha lord = badhaka for this lagna, it will obstruct material results
    but potentially activate spiritual results.
    """
    if not functional_analysis:
        return 0.4   # neutral default when not computed

    from vedic_engine.analysis.functional import score_planet_functional
    md_house = (planet_houses or {}).get(dasha_planet)
    ad_house = (planet_houses or {}).get(antardasha_planet)
    md_score = score_planet_functional(dasha_planet, functional_analysis,
                                       planet_house=md_house, domain=domain)
    ad_score = score_planet_functional(antardasha_planet, functional_analysis,
                                       planet_house=ad_house, domain=domain)

    # Map -1..+1 to 0..1
    md_norm = (md_score + 1.0) / 2.0
    ad_norm = (ad_score + 1.0) / 2.0

    combined = 0.65 * md_norm + 0.35 * ad_norm
    return _clamp(combined)


def score_house_lord_strength(
    domain: str,
    domain_houses: List[int],
    house_lords: Dict[int, str],
    shadbala_ratios: Dict[str, float],
    vargas: Optional[Dict[str, Dict]] = None,
    planet_houses: Optional[Dict[str, int]] = None,
) -> float:
    """
    Strength of the primary house lord(s) for the domain.

    For example:
      career   → 10th lord (and 1st lord)
      marriage → 7th lord
      finance  → 2nd and 11th lords
      health   → 1st and 6th lords

    Scoring:
    • Base score = Shadbala ratio normalised by 1.5× minimum
    • Trik placement penalty: lord in H6/H8/H12 → ×0.60
    • Kendra/Trikona boost: lord in H1/4/5/7/9/10 → ×1.15 (capped at 1.0)
    • D9 (Navamsa) dignity for marriage: own/exalt in D9 → +0.12
    • D10 (Dashamsa) dignity for career : own/exalt in D10 → +0.12
    """
    # Primary house per domain (the most important single house)
    PRIMARY_HOUSE: Dict[str, int] = {
        "career":   10,
        "finance":  11,
        "marriage": 7,
        "health":   1,
        "children": 5,
        "property": 4,
        "spiritual": 9,
        "travel":   9,
    }
    primary = PRIMARY_HOUSE.get(domain.lower())
    check_houses = [primary] if primary else domain_houses[:2]

    # Import dignity helpers here (avoid circular at module level)
    try:
        from vedic_engine.config import (
            OWN_SIGNS, MOOLATRIKONA, EXALTATION_DEGREES, DEBILITATION_DEGREES, Sign, Planet
        )
        from vedic_engine.core.coordinates import sign_of as _sign_of

        def _is_good_sign(planet_name: str, sign_idx: int) -> bool:
            """Own, Moolatrikona, or Exalted in given sign."""
            try:
                p = Planet[planet_name]
            except KeyError:
                return False
            own_list = [s.value for s in OWN_SIGNS.get(p, [])]
            moola = MOOLATRIKONA.get(p)
            exalt_sign = _sign_of(EXALTATION_DEGREES.get(p, -999.0))
            return (sign_idx in own_list or
                    (moola and moola[0].value == sign_idx) or
                    sign_idx == exalt_sign)

        has_dignity_check = True
    except Exception:
        has_dignity_check = False
        def _is_good_sign(planet_name: str, sign_idx: int) -> bool:
            return False

    TRIK = frozenset({6, 8, 12})
    GOOD_H = frozenset({1, 4, 5, 7, 9, 10})

    scores = []
    for h in check_houses:
        lord = house_lords.get(h)
        if not lord:
            continue
        ratio = shadbala_ratios.get(lord, 0.5)
        # Shadbala: ratio >= 1.0 = meeting minimum, >= 1.5 = strong
        lord_score = _clamp(ratio / 1.5)

        # Natal placement modifier
        if planet_houses:
            natal_house = planet_houses.get(lord, 0)
            if natal_house in TRIK:
                lord_score *= 0.60           # debilitated placement
            elif natal_house in GOOD_H:
                lord_score = min(1.0, lord_score * 1.15)

        # D9 bonus for marriage / D10 bonus for career with actual dignity check
        if vargas and lord in vargas and has_dignity_check:
            lord_vargas = vargas[lord]
            if domain.lower() == "marriage" and 9 in lord_vargas:
                d9_sign = lord_vargas[9]
                if _is_good_sign(lord, d9_sign):
                    lord_score = min(1.0, lord_score + 0.12)
            elif domain.lower() == "career" and 10 in lord_vargas:
                d10_sign = lord_vargas[10]
                if _is_good_sign(lord, d10_sign):
                    lord_score = min(1.0, lord_score + 0.12)

        scores.append(lord_score)

    if not scores:
        return 0.4
    return _clamp(sum(scores) / len(scores))


def score_jaimini_sub(
    jaimini_data: Optional[Dict],
    domain: str,
) -> float:
    """
    Jaimini system confidence sub-score for the queried domain.

    Sub-score structure (ad.md §4.1):
      Chara Dasha alignment      : 30%
      Karakamsha dignity/strength: 25%
      Arudha Pada concordance    : 25%
      Rashi Drishti confirmation : 20%

    Each sub-component is normalised to 0–1 from the pre-computed Jaimini
    analysis modules (jaimini_dashas, karakamsha, arudha_padas, rashi_drishti).

    Args:
        jaimini_data : Dict from Jaimini analysis with keys:
          chara_alignment     : float 0-1 — current Chara lord signifies domain
          karakamsha_score    : float 0-1 — Karakamsha planet/sign strength
          arudha_alignment    : float 0-1 — Arudha Pada concordance for domain
          rashi_drishti_score : float 0-1 — Rashi Drishti to relevant houses
        domain : str — not used directly (Jaimini analysis is pre-filtered)

    Returns:
        float in [0, 1] — Jaimini sub-score; 0.3 (neutral) if no data available
    """
    if not jaimini_data:
        return 0.3   # neutral when Jaimini analysis not performed

    chara   = _clamp(float(jaimini_data.get("chara_alignment",     0.30)))
    kara    = _clamp(float(jaimini_data.get("karakamsha_score",    0.30)))
    arudha  = _clamp(float(jaimini_data.get("arudha_alignment",    0.30)))
    rashi_d = _clamp(float(jaimini_data.get("rashi_drishti_score", 0.30)))

    score = 0.30 * chara + 0.25 * kara + 0.25 * arudha + 0.20 * rashi_d
    return _clamp(score)


# ─── Main Aggregator ─────────────────────────────────────────────

def compute_confidence(
    dasha_planet: str,
    antardasha_planet: str,
    domain: str,
    planet_domain_map: Dict[str, List[str]],
    shadbala_ratios: Dict[str, float],
    transit_scores: Dict[str, Dict],
    domain_planets: List[str],
    sarva_av: Optional[List[int]],
    relevant_signs: List[int],
    active_yogas: List[Dict],
    kp_significations: Dict[str, List[int]],
    domain_houses: List[int],
    dasha_planet_bav: Optional[List[int]] = None,
    # ── NEW parameters ─────────────────────────────────────────
    functional_analysis: Optional[Dict] = None,
    house_lords: Optional[Dict[int, str]] = None,
    vargas: Optional[Dict[str, Dict]] = None,
    planet_houses: Optional[Dict[str, int]] = None,
    negator_houses: Optional[List[int]] = None,
    gpt_adjustments: Optional[Dict] = None,
    jaimini_data: Optional[Dict] = None,     # Jaimini sub-score inputs (ad.md §4.1)
    karaka_bav_data: Optional[Dict] = None,  # bhinna + planet_signs + house_lords for karaka BAV
    # ── Promise Gate 0 (Three Pillar Rule result) ───────────
    promise_result: Optional[Dict] = None,
    # ── MD/AD Geometric check ─────────────────────────
    dasha_house: int = 0,              # Natal house of Maha-dasha lord
    antardasha_house: int = 0,         # Natal house of Antar-dasha lord
    # ── Dasha lord dignity flags ──────────────────────────
    dasha_lord_combust: bool = False,   # MD lord combust → burned domains
    dasha_lord_retrograde: bool = False,  # MD lord retrograde → erratic/delayed
) -> Dict:
    """
    Multi-system confidence score using CONDITIONAL GATE LOGIC.

    Architecture (per KP + Research Brief):
      Gate 0 — Three Pillar Promise (Bhava+Bhavesha+Karaka)
               → if DENIED: hard cap 0.05, return DENIED (unbreakable)
               → if SUPPRESSED: cap 0.45 (delayed but possible at maturity)
      Gate 1 — KP Promise (natal sub-lord signifies domain houses)
               → if fails: cap confidence at 0.20, return VERY LOW
      Gate 2 — Dasha confirmation window
               → if fails: cap confidence at 0.35
      Gate 3 — Transit is 100% dominant once Gates 0+1+2 pass
               → transit weight escalates to 0.50 in timing mode
      MD/AD Geometry: AD in 6/8/12 from MD → friction; in kendra/trikona → boost
      Intensity = yoga_strength × dasha_lord_dignities × active_BAV

    GPT adjustments (optional): {adjusted_kp_score, yoga_multiplier, dominant_system}
    to allow AI-reasoned corrections to feed back into math pipeline.
    """
    # ─── GATE 0: Three Pillar Promise Check (HARD BOUNDARY) ───────────────────
    promise_denied     = False
    promise_suppressed = False
    promise_pct        = 100  # default: assume strong promise if not provided

    if promise_result:
        promise_denied     = promise_result.get("denied", False)
        promise_suppressed = promise_result.get("suppressed", False)
        promise_pct        = promise_result.get("promise_pct", 100)

        if promise_denied:
            # Hard boundary: no Dasha+Transit can overcome structural denial
            return {
                "domain": domain,
                "overall": 0.05,
                "level": "DENIED",
                "gate_status": "PROMISE_DENIED_THREE_PILLAR",
                "promise_pct": 0,
                "promise_detail": promise_result.get("detail", ""),
                "components": {},
                "weights_used": {},
                "best_case": "Functional substitute only (e.g., mentoring vs. own children).",
            }

    # --- Component scores ---
    c_dasha    = score_dasha_alignment(dasha_planet, antardasha_planet, domain,
                                       planet_domain_map, shadbala_ratios)
    c_transit  = score_transit_support(transit_scores, domain_planets)
    c_av       = score_ashtakvarga(sarva_av, relevant_signs, dasha_planet_bav,
                                    karaka_bav_data=karaka_bav_data, domain=domain)
    c_yoga     = score_yoga_activation(active_yogas, domain)
    c_kp       = score_kp_sublord(kp_significations, domain_houses,
                                  dasha_planet, antardasha_planet,
                                  negator_houses=negator_houses)
    c_func     = score_functional_alignment(dasha_planet, antardasha_planet,
                                            functional_analysis or {},
                                            domain=domain,
                                            planet_houses=planet_houses)
    c_hlord    = score_house_lord_strength(domain, domain_houses,
                                           house_lords or {}, shadbala_ratios, vargas,
                                           planet_houses=planet_houses)

    # Allow GPT-reasoned adjustments to override specific components
    if gpt_adjustments:
        if "adjusted_kp_score" in gpt_adjustments:
            c_kp = _clamp(float(gpt_adjustments["adjusted_kp_score"]))
        if "yoga_multiplier" in gpt_adjustments:
            c_yoga = _clamp(c_yoga * float(gpt_adjustments["yoga_multiplier"]))
        if "dasha_weight_boost" in gpt_adjustments:
            c_dasha = _clamp(c_dasha * float(gpt_adjustments["dasha_weight_boost"]))

    # ── MD/AD Geometric Relationship Check ───────────────────────────────────
    # AD lord in Dusthana (6/8/12) from MD lord → Shadashtaka/Dwirdwadasha friction
    # AD lord in Kendra (1/4/7/10) or Trikona (5/9) from MD lord → boost
    md_ad_geometry = "neutral"
    if dasha_house > 0 and antardasha_house > 0:
        ad_from_md = (antardasha_house - dasha_house) % 12 + 1
        if ad_from_md in (6, 8, 12):
            c_dasha = _clamp(c_dasha * 0.55)   # strong friction: enmity, health, obstacles
            md_ad_geometry = f"friction_shadashtaka_AD_{ad_from_md}th_from_MD"
        elif ad_from_md in (1, 4, 7, 10, 5, 9):
            c_dasha = _clamp(c_dasha * 1.25)   # Kendra/Trikona: fruitful, overrides MD negativity
            md_ad_geometry = f"boost_kendra_trikona_AD_{ad_from_md}th_from_MD"

    # ── Dasha Lord Dignity Modifiers ─────────────────────────────────────────
    # Combustion → domains of dasha lord: drastically reduced, hidden, conflicted
    if dasha_lord_combust:
        c_dasha = _clamp(c_dasha * 0.50)   # "burned" — half effectiveness

    # Retrograde → erratic, internalized, repeated efforts; delayed but eventual
    if dasha_lord_retrograde:
        # Retrograde benefic → eventually massive but delayed
        c_dasha = _clamp(c_dasha * 0.75)   # 25% reduction due to delay/erratic nature

    # ── Promise ceiling for suppressed charts ────────────────────────────────
    # Suppressed promise: reduce all scores proportional to promise_pct
    if promise_suppressed:
        promise_ceiling = 0.45  # highly suppressed charts capped at moderate
    elif promise_pct <= 33:
        promise_ceiling = 0.40  # weak promise → moderate cap
    elif promise_pct <= 67:
        promise_ceiling = 0.70  # moderate promise → high possible but not very high
    else:
        promise_ceiling = 1.00  # full promise → uncapped

    # ── GATE 1: KP Promise check ──────────────────────────────
    # If natal sub-lord does not signify domain houses, the chart has NO PROMISE.
    # Even strong transits cannot overcome lack of promise.
    PROMISE_THRESHOLD = 0.18
    promise_failed = c_kp < PROMISE_THRESHOLD

    # ── GATE 2: Dasha confirmation ────────────────────────────
    DASHA_THRESHOLD = 0.25
    dasha_confirmed = c_dasha >= DASHA_THRESHOLD

    # ── Adaptive weights based on gate passage ────────────────
    # Jaimini sub-score (8th component — ad.md §4.1)
    c_jaimini = score_jaimini_sub(jaimini_data, domain)

    # NOTE: w_hlord set to 0.00 in ALL states — house lord strength is already
    # fully evaluated inside the Promise gate (Gate 0: Three Pillar Rule) via
    # _score_bhavesha() + _score_bhava().  Including it again in the weighted
    # sum was architectural double-counting (audit §9.3).  Former w_hlord
    # weight redistributed: +50% → transit, +50% → AV.
    if promise_failed:
        # Gate 1 failed: use minimal weights, promise not in chart
        w_dasha, w_transit, w_av, w_yoga, w_kp, w_func, w_hlord, w_jaimini = (
            0.20, 0.16, 0.11, 0.08, 0.30, 0.10, 0.00, 0.05
        )
    elif not dasha_confirmed:
        # Gate 1 passed but dasha not confirming: standard weights
        w_dasha, w_transit, w_av, w_yoga, w_kp, w_func, w_hlord, w_jaimini = (
            0.30, 0.185, 0.135, 0.12, 0.14, 0.07, 0.00, 0.05
        )
    else:
        # Both gates passed: transit becomes dominant for precise timing
        # This is the "activation" state — transit weight escalates
        w_dasha, w_transit, w_av, w_yoga, w_kp, w_func, w_hlord, w_jaimini = (
            0.20, 0.35, 0.15, 0.12, 0.10, 0.05, 0.00, 0.03
        )

    overall = (w_dasha   * c_dasha   +
               w_transit * c_transit +
               w_av      * c_av      +
               w_yoga    * c_yoga    +
               w_kp      * c_kp     +
               w_func    * c_func   +
               w_hlord   * c_hlord  +
               w_jaimini * c_jaimini)

    # ── Gate caps ─────────────────────────────────────────────
    if promise_failed:
        overall = min(overall, 0.22)    # Chart has no KP promise → cap at Very Low
    elif not dasha_confirmed:
        overall = min(overall, 0.38)    # Dasha not active → cap at Low

    # Apply promise-ceiling from Three Pillar Rule (Gate 0)
    overall = min(overall, promise_ceiling)

    level = ("VERY HIGH" if overall >= 0.75 else
             "HIGH"      if overall >= 0.60 else
             "MODERATE"  if overall >= 0.40 else
             "LOW"       if overall >= 0.25 else "VERY LOW")

    gate_status = ("BOTH_GATES_PASSED" if (not promise_failed and dasha_confirmed) else
                   "DASHA_NOT_CONFIRMED" if (not promise_failed) else
                   "PROMISE_FAILED")

    return {
        "domain": domain,
        "overall": round(overall, 3),
        "level": level,
        "gate_status": gate_status,
        "promise_pct": promise_pct,
        "promise_level": promise_result.get("promise_level", "UNKNOWN") if promise_result else "UNKNOWN",
        "md_ad_geometry": md_ad_geometry,
        "dasha_lord_combust": dasha_lord_combust,
        "dasha_lord_retrograde": dasha_lord_retrograde,
        "components": {
            "dasha_alignment":      round(c_dasha,   3),
            "transit_support":      round(c_transit, 3),
            "ashtakvarga_support":  round(c_av,      3),
            "yoga_activation":      round(c_yoga,    3),
            "kp_confirmation":      round(c_kp,      3),
            "functional_alignment": round(c_func,    3),
            "house_lord_strength":  round(c_hlord,   3),
            "jaimini_sub":          round(c_jaimini, 3),
        },
        "weights_used": {
            "dasha":     round(w_dasha,   3),
            "transit":   round(w_transit, 3),
            "ashtakvarga": round(w_av,    3),
            "yoga":      round(w_yoga,    3),
            "kp":        round(w_kp,      3),
            "functional":round(w_func,    3),
            "house_lord":round(w_hlord,   3),
            "jaimini":   round(w_jaimini, 3),
        },
    }


def multi_system_agreement(
    vimshottari_active: str,
    yogini_active: str,
    domain: str,
    planet_domain_map: Dict[str, List[str]],
    chara_dasha_lord: Optional[str] = None,
    chara_supports_domain: Optional[bool] = None,
    transit_supports_domain: Optional[bool] = None,
) -> Dict:
    """
    Triple-Lock Convergence Engine (Logic Integration Manifest §3.8).

    Fuses Vimshottari, Yogini, and Chara Dasha (+ optional Transit support)
    into a formal convergence lock with three confidence tiers:

      Level 3 (all 3 dasha systems converge):   boost +0.15  (85-95% confidence zone)
      Level 2 (any 2 of 3 dasha systems agree): boost +0.08  (50-70% confidence zone)
      Level 1 (only 1 or no agreement):         boost +0.00  (<40% base reliability)

    Transit is an optional 4th factor — if it also supports the domain when
    Level 3 is already active, an additional micro-boost of +0.03 is added.

    Classical justification:
      Vimshottari = Nakshatra-lord time cycle (primary predictive dasha)
      Yogini      = 8-fold Shakti-based dasha (corroborating cycle)
      Chara Dasha = Jaimini sign-based dasha (3rd perpendicular view)
      When all three independently point to the same domain/event,
      the probability of manifestation is highest.

    Args:
        vimshottari_active      : Current Vimshottari Maha-dasha lord (e.g. "JUPITER")
        yogini_active           : Current Yogini Maha-dasha lord
        domain                  : Domain being tested (e.g. "career", "marriage")
        planet_domain_map       : {planet → [domain1, domain2, ...]} lookup
        chara_dasha_lord        : Current Jaimini Chara Dasha sign/lord (optional)
        chara_supports_domain   : Whether Chara Dasha lord's significations cover
                                  the domain (pre-computed — pass True/False/None)
        transit_supports_domain : Whether current transit configuration supports
                                  the domain (pre-computed — pass True/False/None)

    Returns:
        Dict with lock_level, confidence_boost, lock_details
    """
    vim_domains  = set(planet_domain_map.get(vimshottari_active, []))
    yog_domains  = set(planet_domain_map.get(yogini_active, []))

    vim_supports  = domain in vim_domains
    yog_supports  = domain in yog_domains
    same_planet   = (vimshottari_active == yogini_active)

    # Chara Dasha — use provided flag or fall back to domain map lookup
    char_supports: bool
    if chara_supports_domain is not None:
        char_supports = chara_supports_domain
    elif chara_dasha_lord is not None:
        char_domains  = set(planet_domain_map.get(chara_dasha_lord, []))
        char_supports = domain in char_domains
    else:
        char_supports = False   # No Chara data → conservatively exclude

    # Score each lock: count how many of the 3 primary systems support the domain
    # (Yogini gets an extra point if it's the same lord as Vimshottari)
    supports = [vim_supports, yog_supports, char_supports]
    n_agree  = sum(supports)

    # Special case: if same lord in both Vimshottari + Yogini, treat both as
    # strong agreement (weight = 1.5 systems)
    if same_planet and vim_supports and yog_supports:
        n_agree = max(n_agree, 2)   # at least Level 2

    # Convergence level determination
    if n_agree >= 3:
        lock_level = 3
        boost      = 0.15
        tier_label = "LEVEL_3 (85-95%): All 3 dasha systems converge"
    elif n_agree == 2:
        lock_level = 2
        boost      = 0.08
        tier_label = "LEVEL_2 (50-70%): 2 of 3 dasha systems agree"
    else:
        lock_level = 1
        boost      = 0.00
        tier_label = "LEVEL_1 (<40%): No sufficient multi-system agreement"

    # Transit micro-boost: only applies when Level 3 already confirmed
    transit_micro_boost = 0.0
    if lock_level == 3 and transit_supports_domain is True:
        transit_micro_boost = 0.03
        boost += transit_micro_boost
        tier_label += " + Transit confirms (micro-boost +0.03)"

    return {
        "vimshottari_dasha_lord":   vimshottari_active,
        "yogini_dasha_lord":        yogini_active,
        "chara_dasha_lord":         chara_dasha_lord,
        "vimshottari_supports":     vim_supports,
        "yogini_supports":          yog_supports,
        "chara_supports":           char_supports,
        "transit_supports":         transit_supports_domain,
        "same_lord_vim_yog":        same_planet,
        "systems_agree_count":      n_agree,
        "lock_level":               lock_level,
        "tier_label":               tier_label,
        "confidence_boost":         round(boost, 3),
        "transit_micro_boost":      transit_micro_boost,
        # Legacy keys (backwards compatibility)
        "both_support_domain":      vim_supports and yog_supports,
        "same_lord":                same_planet,    }