"""
Marriage Synthesis — 4-Pillar Conflict Resolution Matrix.

Implements the classical multi-indicator marriage analysis methodology:
  Pillar 1 : Venus       — natural capacity for love / attraction
  Pillar 2 : 7th Lord    — physical logistics, daily marital environment
  Pillar 3 : Dara Karaka — soul/karmic connection with partner
  Pillar 4 : Upapada Lagna (UL) — institutional longevity, social sustenance

Three Hierarchical Override Rules:
  Rule 1 : 2nd from UL overrides 7th lord for marriage LONGEVITY
  Rule 2 : D9 (Navamsa) overrides D1 for POST-MARITAL dynamics
  Rule 3 : Final synthesis → pattern label (High_Compatibility_High_Friction etc.)

Second Marriage detection:
  9th house → nature/timing of new partner
  2nd house → longevity/stability of second union

Source: Deep Dive into Jyotish Logic.md (section "Synthesising Marriage Karakas")
"""
from __future__ import annotations
from typing import Dict, Any, Optional

KENDRA_HOUSES   = {1, 4, 7, 10}
TRIKONA_HOUSES  = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}

SIGN_LORDS = {
    0: "MARS",    1: "VENUS",   2: "MERCURY", 3: "MOON",
    4: "SUN",     5: "MERCURY", 6: "VENUS",   7: "MARS",
    8: "JUPITER", 9: "SATURN",  10: "SATURN", 11: "JUPITER",
}

NATURAL_BENEFICS = {"JUPITER", "VENUS", "MERCURY", "MOON"}
NATURAL_MALEFICS = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}


def _score_from_house(house_num: int) -> float:
    """Convert house placement to 0–1 strength score."""
    if house_num in KENDRA_HOUSES:
        return 0.9
    if house_num in TRIKONA_HOUSES:
        return 0.85
    if house_num in DUSTHANA_HOUSES:
        return 0.15
    if house_num in {2, 11}:
        return 0.65
    return 0.5


def _house_of(planet_sign: int, reference_sign: int) -> int:
    """1-based house of planet_sign counted from reference_sign."""
    return ((planet_sign - reference_sign) % 12) + 1


# ── Pillar Scorers ────────────────────────────────────────────────────────────

def _score_venus(venus_house_d1: int, venus_sign_d9: Optional[int], benefic_aspects: int) -> float:
    """Score Venus pillar: D1 house + D9 dignity + benefic aspects."""
    base = _score_from_house(venus_house_d1)
    d9_bonus = 0.1 if venus_sign_d9 is not None and venus_sign_d9 in {1, 2} else 0.0  # own/exalted
    asp_bonus = min(0.1, benefic_aspects * 0.05)
    return min(1.0, base + d9_bonus + asp_bonus)


def _score_seventh_lord(seventh_lord_house_d1: int, seventh_lord_combust: bool,
                         seventh_lord_retrograde: bool) -> float:
    """Score 7th lord pillar: house + combustion/retrogression modifiers."""
    base = _score_from_house(seventh_lord_house_d1)
    if seventh_lord_combust:
        base *= 0.6
    if seventh_lord_retrograde:
        base *= 0.85   # retrograde = delayed/unusual, not destroyed
    return max(0.0, min(1.0, base))


def _score_dk(dk_house_d1: int, dk_and_venus_same_sign: bool) -> float:
    """Score Dara Karaka pillar: D1 house + proximity to Venus."""
    base = _score_from_house(dk_house_d1)
    bonus = 0.1 if dk_and_venus_same_sign else 0.0
    return min(1.0, base + bonus)


def _score_ul(ul_sign: int, lagna_sign: int, planet_houses: Dict[str, int],
               planet_signs: Dict[str, int]) -> Dict[str, Any]:
    """
    Score Upapada Lagna (UL) and the critical 2nd house from UL.

    The 2nd from UL is the PRIMARY longevity indicator (Rule 1).
    """
    ul_house_from_lagna = _house_of(ul_sign, lagna_sign)
    second_from_ul_sign = (ul_sign + 1) % 12
    second_from_ul_lord = SIGN_LORDS[second_from_ul_sign]
    second_from_ul_lord_house = planet_houses.get(second_from_ul_lord, 0)

    # Check if Rahu/Saturn/Ketu afflict the 2nd from UL sign
    afflictors = []
    for p, s in planet_signs.items():
        if s == second_from_ul_sign and p.upper() in {"RAHU", "SATURN", "KETU", "MARS"}:
            afflictors.append(p)

    longevity_score = _score_from_house(second_from_ul_lord_house)
    if afflictors:
        longevity_score *= 0.5  # severe affliction

    ul_score = _score_from_house(ul_house_from_lagna)

    return {
        "ul_house_from_lagna": ul_house_from_lagna,
        "ul_score": ul_score,
        "second_from_ul_lord": second_from_ul_lord,
        "second_from_ul_lord_house": second_from_ul_lord_house,
        "second_from_ul_afflictors": afflictors,
        "longevity_score": round(longevity_score, 3),
        "longevity_note": (
            "Marriage SURVIVES long-term (2nd from UL strong)" if longevity_score >= 0.6
            else "Marriage longevity THREATENED (2nd from UL afflicted)"
        ),
    }


# ── Rule Evaluators ───────────────────────────────────────────────────────────

def _apply_rule1_override(
    seventh_lord_score: float,
    ul_longevity_score: float,
    seventh_lord_house: int,
) -> Dict[str, Any]:
    """
    Rule 1: 2nd from UL OVERRIDES 7th lord for marriage survival.

    Even if 7th lord is exalted (great initial attraction), if 2nd from UL
    is devastated, the marriage will terminate.
    """
    if ul_longevity_score >= 0.6:
        if seventh_lord_score < 0.4:
            conflict_type = "SURVIVES_DESPITE_FRICTION"
            conflict_note = (
                "7th lord weak (physical friction, daily difficulties) BUT 2nd from UL "
                "is strong → Marriage SURVIVES. Expect logistical challenges but no dissolution."
            )
        else:
            conflict_type = "STRONG_BOTH"
            conflict_note = "Strong 7th lord AND strong 2nd from UL → Ideal marital environment."
        longevity_verdict = "SUSTAINED"
    else:
        if seventh_lord_score >= 0.7:
            conflict_type = "PASSION_WITHOUT_LONGEVITY"
            conflict_note = (
                "7th lord strong (intense initial attraction, passionate courtship) BUT "
                "2nd from UL devastated → Couple WILL separate once passion fades. "
                "Legal/social termination is near-inevitable."
            )
        else:
            conflict_type = "DIFFICULT_BOTH"
            conflict_note = (
                "Both 7th lord AND 2nd from UL are weak → Marriage timeline is restricted; "
                "either delayed, cancelled, or severely short-lived."
            )
        longevity_verdict = "AT_RISK"

    return {
        "conflict_type": conflict_type,
        "conflict_note": conflict_note,
        "longevity_verdict": longevity_verdict,
    }


def _apply_rule2_d9_override(
    d1_seventh_lord_house: int,
    d9_seventh_lord_house: int,
) -> Dict[str, Any]:
    """
    Rule 2: D9 overrides D1 for POST-MARITAL dynamics.

    Difficult D1 courtship + strong D9 = improves dramatically after wedding.
    """
    d1_strong = d1_seventh_lord_house in (KENDRA_HOUSES | TRIKONA_HOUSES)
    d9_strong = d9_seventh_lord_house in (KENDRA_HOUSES | TRIKONA_HOUSES)

    if not d1_strong and d9_strong:
        pattern = "courtship_difficult_married_life_harmonious"
        note = (
            "D1 7th lord weak (difficult courtship, delayed marriage) BUT D9 7th lord strong → "
            "Relationship will DRAMATICALLY IMPROVE after the marriage ceremony. "
            "The wedding ceremony itself is the pivotal turning point."
        )
    elif d1_strong and not d9_strong:
        pattern = "courtship_exciting_married_life_stressful"
        note = (
            "D1 7th lord strong (exciting courtship) BUT D9 7th lord weak → "
            "Relationship quality DETERIORATES post-marriage. "
            "Compatibility deepens but satisfaction erodes over time."
        )
    elif d1_strong and d9_strong:
        pattern = "excellent_courtship_and_marriage"
        note = "Both D1 and D9 support marriage → Consistently high-quality relationship."
    else:
        pattern = "challenging_courtship_and_marriage"
        note = "Both D1 and D9 weakly placed → Persistent marital difficulties."

    return {
        "d9_override_pattern": pattern,
        "d9_override_note": note,
        "d9_seventh_lord_house": d9_seventh_lord_house,
    }


def _synthesise_pattern(
    venus_score: float,
    seventh_lord_score: float,
    dk_score: float,
    ul_score: float,
    longevity_verdict: str,
) -> str:
    """
    Rule 3: Generate the final synthesis output label.

    Example from research:
      Venus+DK strong, 7th lord weak, UL good → "High_Compatibility_High_Friction"
    """
    compatibility = (venus_score + dk_score) / 2.0
    logistics     = seventh_lord_score
    longevity     = ul_score

    high_compat = compatibility >= 0.65
    low_compat  = compatibility < 0.4
    good_logistics = logistics >= 0.6
    poor_logistics = logistics < 0.35

    if high_compat and good_logistics and longevity_verdict == "SUSTAINED":
        return "High_Compatibility_High_Harmony"
    if high_compat and poor_logistics:
        return "High_Compatibility_High_Friction"
    if not high_compat and good_logistics:
        return "Low_Compatibility_Logistically_Stable"
    if low_compat and poor_logistics and longevity_verdict == "AT_RISK":
        return "Difficult_Marriage_Dissolution_Likely"
    if high_compat and longevity_verdict == "AT_RISK":
        return "Deep_Love_Short_Duration"
    return "Mixed_Marriage_Quality"


# ── Second Marriage ───────────────────────────────────────────────────────────
def analyse_second_marriage(
    lagna_sign: int,
    planet_houses: Dict[str, int],
    planet_signs: Dict[str, int],
) -> Dict[str, Any]:
    """
    Second marriage analysis:
      9th house → nature and timing of new partner (Bhavat Bhavam: 3rd from 7th)
      2nd house → longevity of the second union (8th from 7th = death of first marriage)
    """
    ninth_sign  = (lagna_sign + 8) % 12
    second_sign = (lagna_sign + 1) % 12

    ninth_lord  = SIGN_LORDS[ninth_sign]
    second_lord = SIGN_LORDS[second_sign]

    ninth_lord_house  = planet_houses.get(ninth_lord, 0)
    second_lord_house = planet_houses.get(second_lord, 0)

    ninth_occupants  = [p for p, s in planet_signs.items() if s == ninth_sign]
    second_occupants = [p for p, s in planet_signs.items() if s == second_sign]

    partner_nature: str
    if ninth_occupants:
        partner_nature = f"New partner flavoured by {', '.join(ninth_occupants)} (9th house planets)"
    else:
        partner_nature = f"New partner flavoured by {ninth_lord} (9th lord, H{ninth_lord_house})"

    second_union_score = _score_from_house(second_lord_house)
    second_union_quality = (
        "stable_and_enduring"    if second_union_score >= 0.7 else
        "moderate_duration"      if second_union_score >= 0.5 else
        "fragile_short_lived"
    )

    return {
        "ninth_house_partner_nature": partner_nature,
        "ninth_lord": ninth_lord,
        "ninth_lord_house": ninth_lord_house,
        "ninth_occupants": ninth_occupants,
        "second_lord": second_lord,
        "second_lord_house": second_lord_house,
        "second_occupants": second_occupants,
        "second_union_longevity_score": round(second_union_score, 3),
        "second_union_quality": second_union_quality,
        "analysis": (
            f"Second marriage: Partner characteristics from 9th house ({partner_nature}). "
            f"Second union longevity via 2nd house: {second_union_quality}."
        ),
    }


# ── Master Function ───────────────────────────────────────────────────────────
def compute_marriage_synthesis(
    lagna_sign: int,
    moon_sign: int,
    venus_house_d1: int,
    venus_sign_d9: Optional[int],
    venus_benefic_aspects: int,         # count of benefic planets aspecting Venus
    seventh_lord: str,
    seventh_lord_house_d1: int,
    seventh_lord_house_d9: int,
    seventh_lord_combust: bool,
    seventh_lord_retrograde: bool,
    dk_planet: str,
    dk_house_d1: int,
    dk_sign: int,
    venus_sign: int,                    # D1 sign index of Venus
    ul_sign: int,                       # sign index of Upapada Lagna
    planet_houses: Dict[str, int],      # all planets → house (D1, from lagna)
    planet_signs: Dict[str, int],       # all planets → sign index (D1)
    query_type: str = "first",          # "first" | "second"
) -> Dict[str, Any]:
    """
    Synthesise all four marriage pillars and apply hierarchical conflict rules.

    Returns:
        synthesis_pattern       : e.g. "High_Compatibility_High_Friction"
        longevity_verdict       : "SUSTAINED" | "AT_RISK"
        d9_dynamics_pattern     : post-marital quality descriptor
        love_score              : Venus + DK composite 0–1
        logistics_score         : 7th lord 0–1
        longevity_score         : 2nd from UL 0–1
        conflict_resolution     : dict with conflict_type, conflict_note
        second_marriage         : dict (when query_type="second")
        notes                   : list of key narrative findings
    """
    # Pillar scores
    venus_score  = _score_venus(venus_house_d1, venus_sign_d9, venus_benefic_aspects)
    seventh_score = _score_seventh_lord(seventh_lord_house_d1, seventh_lord_combust, seventh_lord_retrograde)
    dk_score     = _score_dk(dk_house_d1, dk_sign == venus_sign)
    ul_data      = _score_ul(ul_sign, lagna_sign, planet_houses, planet_signs)

    # Rule 1: longevity override
    rule1 = _apply_rule1_override(seventh_score, ul_data["longevity_score"], seventh_lord_house_d1)

    # Rule 2: D9 post-marital dynamics
    rule2 = _apply_rule2_d9_override(seventh_lord_house_d1, seventh_lord_house_d9)

    # Rule 3: final synthesis pattern
    pattern = _synthesise_pattern(
        venus_score, seventh_score, dk_score,
        ul_data["ul_score"], rule1["longevity_verdict"],
    )

    # Overall marriage score
    marriage_score = (
        0.25 * venus_score +
        0.20 * seventh_score +
        0.25 * dk_score +
        0.30 * ul_data["longevity_score"]
    )

    notes = [
        f"Venus score: {venus_score:.2f} — love/attraction capacity",
        f"7th lord ({seventh_lord}) score: {seventh_score:.2f} — marital logistics",
        f"Dara Karaka ({dk_planet}) score: {dk_score:.2f} — soul connection",
        ul_data["longevity_note"],
        rule1["conflict_note"],
        rule2["d9_override_note"],
    ]

    result: Dict[str, Any] = {
        "synthesis_pattern": pattern,
        "marriage_score": round(marriage_score, 3),
        "longevity_verdict": rule1["longevity_verdict"],
        "d9_dynamics_pattern": rule2["d9_override_pattern"],
        "love_score": round((venus_score + dk_score) / 2, 3),
        "logistics_score": round(seventh_score, 3),
        "longevity_score": round(ul_data["longevity_score"], 3),
        "conflict_resolution": rule1,
        "ul_analysis": ul_data,
        "d9_override": rule2,
        "pillar_scores": {
            "venus": round(venus_score, 3),
            "seventh_lord": round(seventh_score, 3),
            "dara_karaka": round(dk_score, 3),
            "upapada_lagna": round(ul_data["ul_score"], 3),
        },
        "notes": notes,
    }

    if query_type == "second":
        result["second_marriage"] = analyse_second_marriage(
            lagna_sign, planet_houses, planet_signs
        )

    return result
