"""
Career Checklist — 5-Step Algorithmic Decision Tree.

Implements the K.N. Rao / Sanjay Rath methodology for career synthesis:
  Step 1 : D1 foundation — 10th from Asc+Moon+Sun, 6-10-11 nexus, negative modifiers
  Step 2 : Jaimini — AK-AmK geometric relationship → soul alignment
  Step 3 : D10 microscope — D1 10th lord placement within the Dasamsa
  Step 4 : D3 karmic roots — past-life skills via 10th house of Drekkana
  Step 5 : Dasha + Transit synchronisation — timing activation check

All rules come from: Deep Dive into Jyotish Logic.md (sections "Human Decision Tree")
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional


# ── Constants ────────────────────────────────────────────────────────────────
KENDRA_HOUSES  = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}

SIGN_LORDS = {
    0: "MARS",    1: "VENUS",   2: "MERCURY", 3: "MOON",
    4: "SUN",     5: "MERCURY", 6: "VENUS",   7: "MARS",
    8: "JUPITER", 9: "SATURN",  10: "SATURN", 11: "JUPITER",
}

MOVABLE_SIGNS = {0, 3, 6, 9}   # Aries, Cancer, Libra, Capricorn
FIXED_SIGNS   = {1, 4, 7, 10}  # Taurus, Leo, Scorpio, Aquarius
DUAL_SIGNS    = {2, 5, 8, 11}  # Gemini, Virgo, Sagittarius, Pisces


def _house_of(planet_sign: int, reference_sign: int) -> int:
    """1-based house of planet_sign from reference_sign."""
    return ((planet_sign - reference_sign) % 12) + 1


def _trine_relation(sign_a: int, sign_b: int) -> bool:
    """True if sign_a and sign_b are in 1/5/9 relationship."""
    diff = (sign_b - sign_a) % 12
    return diff in (0, 4, 8)


def _dusthana_relation(sign_a: int, sign_b: int) -> bool:
    """True if sign_a and sign_b are in 6/8 relationship."""
    diff = (sign_b - sign_a) % 12
    return diff in (5, 7)   # 6th or 8th


# ── Step 1: D1 Foundation ────────────────────────────────────────────────────
def _step1_d1_foundation(
    lagna_sign: int,
    moon_sign: int,
    sun_sign: int,
    planet_signs: Dict[str, int],   # planet name → sign index (D1)
    planet_houses: Dict[str, int],  # planet name → house num from lagna
) -> Dict[str, Any]:
    """
    Analyse the D1 Rasi chart for career foundations.
    Returns dict with: 10th house from each anchor, 6-10-11 nexus,
    10th lord dignity flags.
    """
    tenth_from_lagna = (lagna_sign + 9) % 12
    tenth_from_moon  = (moon_sign  + 9) % 12
    tenth_from_sun   = (sun_sign   + 9) % 12

    tenth_lord_lagna = SIGN_LORDS[tenth_from_lagna]
    tenth_lord_moon  = SIGN_LORDS[tenth_from_moon]
    tenth_lord_sun   = SIGN_LORDS[tenth_from_sun]

    # Determine strongest 10th lord (by house quality: kendra > trikona > else)
    def _house_quality(lord: str) -> int:
        h = planet_houses.get(lord, 0)
        if h in KENDRA_HOUSES:
            return 3
        if h in TRIKONA_HOUSES:
            return 2
        if h in DUSTHANA_HOUSES:
            return 0
        return 1

    scores = {
        "lagna": (_house_quality(tenth_lord_lagna), tenth_lord_lagna),
        "moon":  (_house_quality(tenth_lord_moon),  tenth_lord_moon),
        "sun":   (_house_quality(tenth_lord_sun),   tenth_lord_sun),
    }
    primary_ref = max(scores, key=lambda k: scores[k][0])
    primary_tenth_lord = scores[primary_ref][1]

    # 6-10-11 nexus scan: look for houses 6/10/11 being connected through
    # planets occupying them or lords linking them.
    h6_lord  = SIGN_LORDS[(lagna_sign + 5) % 12]
    h10_lord = SIGN_LORDS[tenth_from_lagna]
    h11_lord = SIGN_LORDS[(lagna_sign + 10) % 12]

    house_of_6th_lord  = planet_houses.get(h6_lord, 0)
    house_of_10th_lord = planet_houses.get(h10_lord, 0)
    house_of_11th_lord = planet_houses.get(h11_lord, 0)

    nexus_houses = {house_of_6th_lord, house_of_10th_lord, house_of_11th_lord}
    nexus_active = nexus_houses.issuperset({6, 10, 11}) or (
        # At least two of the three lords are in {6,10,11}
        len(nexus_houses & {6, 10, 11}) >= 2
    )

    # Negative modifiers
    tenth_lord_house = planet_houses.get(primary_tenth_lord, 0)
    neg_modifiers = []
    if tenth_lord_house == 8:
        neg_modifiers.append("10th lord in 8th house → sudden career breaks")
    if tenth_lord_house == 12:
        neg_modifiers.append("10th lord in 12th house → career abroad / dissolution")
    if tenth_lord_house == 6:
        neg_modifiers.append("10th lord in 6th house → service/conflict environment")

    # 10th lord combust or debilitated flags are checked by caller via Shadbala data

    return {
        "tenth_lord_primary": primary_tenth_lord,
        "primary_reference": primary_ref,
        "tenth_lord_house": tenth_lord_house,
        "nexus_6_10_11_active": nexus_active,
        "negative_modifiers": neg_modifiers,
        "d1_career_score": (
            1.0 if tenth_lord_house in KENDRA_HOUSES else
            0.75 if tenth_lord_house in TRIKONA_HOUSES else
            0.3  if tenth_lord_house in DUSTHANA_HOUSES else 0.5
        ) + (0.2 if nexus_active else 0.0) - (0.1 * len(neg_modifiers)),
    }


# ── Step 2: Jaimini Variables ────────────────────────────────────────────────
def _step2_jaimini(
    ak_sign: int,    # Atmakaraka sign
    amk_sign: int,   # Amatyakaraka sign
    amk_planet: str,
) -> Dict[str, Any]:
    """
    Evaluate AK–AmK geometric relationship for soul alignment.

    Trine (1/5/9)    → soul_aligned_career  (high intrinsic success)
    6/8 relationship → career_struggle_against_self
    Other            → neutral
    """
    if _trine_relation(ak_sign, amk_sign):
        alignment = "soul_aligned_career"
        alignment_note = (
            f"AK and AmK ({amk_planet}) are in mutual trine → "
            "Career is perfectly aligned with soul purpose. "
            "High intrinsic success and satisfaction guaranteed."
        )
        alignment_score = 1.0
    elif _dusthana_relation(ak_sign, amk_sign):
        alignment = "career_struggle_against_self"
        alignment_note = (
            f"AK and AmK ({amk_planet}) are in 6/8 relationship → "
            "Career will feel like a constant inner conflict. "
            "Success possible but always accompanied by friction, "
            "self-doubt, or ill health during professional phases."
        )
        alignment_score = 0.3
    else:
        alignment = "neutral_alignment"
        alignment_note = (
            f"AmK ({amk_planet}): Neither trine nor 6/8 to AK. "
            "Moderate soul-career alignment — depends on transits and Dasha."
        )
        alignment_score = 0.6

    return {
        "amk_planet": amk_planet,
        "ak_amk_alignment": alignment,
        "alignment_note": alignment_note,
        "jaimini_score": alignment_score,
    }


# ── Step 3: D10 Microscope ───────────────────────────────────────────────────
def _step3_d10(
    d1_tenth_lord: str,
    d10_planet_houses: Dict[str, int],   # houses from D10 Ascendant
) -> Dict[str, Any]:
    """
    Locate D1 10th lord within the D10 chart.

    Kendra (1/4/7/10)  → great heights
    Trikona (1/5/9)    → sustained success
    Dusthana (6/8/12)  → severe setbacks regardless of D1
    """
    house_in_d10 = d10_planet_houses.get(d1_tenth_lord, 0)

    if house_in_d10 in KENDRA_HOUSES:
        sustainability = "great_heights"
        d10_note = (
            f"{d1_tenth_lord} in D10 {house_in_d10}th (Kendra) → "
            "Maximum career sustainability and public recognition."
        )
        d10_score = 1.0
    elif house_in_d10 in TRIKONA_HOUSES:
        sustainability = "sustained_success"
        d10_note = (
            f"{d1_tenth_lord} in D10 {house_in_d10}th (Trikona) → "
            "Dharmic career upliftment; long-term success via virtuous work."
        )
        d10_score = 0.85
    elif house_in_d10 in DUSTHANA_HOUSES:
        sustainability = "severe_setback_risk"
        d10_note = (
            f"CRITICAL: {d1_tenth_lord} in D10 {house_in_d10}th (Dusthana) → "
            "Career will face severe, unavoidable setbacks regardless of D1 beauty. "
            "Hidden enemies, sudden reversals, or professional disgrace is indicated."
        )
        d10_score = 0.1
    else:
        sustainability = "moderate"
        d10_note = (
            f"{d1_tenth_lord} in D10 {house_in_d10}th → "
            "Average career sustainability; needs strong Dasha support."
        )
        d10_score = 0.5

    return {
        "d1_tenth_lord_in_d10_house": house_in_d10,
        "career_sustainability": sustainability,
        "d10_note": d10_note,
        "d10_score": d10_score,
    }


# ── Step 4: D3 Karmic Roots ──────────────────────────────────────────────────
def _step4_d3_karmic(
    d3_tenth_house_planets: List[str],   # planets in 10th house of D3
    d3_tenth_lord: Optional[str] = None,
    d3_tenth_lord_house: int = 0,
) -> Dict[str, Any]:
    """
    10th house of D3 (Drekkana) → karmic/past-life skills driving career.
    """
    karmic_skills: List[str] = []
    _skill_map = {
        "SUN":     "leadership, authority, government service (past-life royalty or administration)",
        "MOON":    "nurturing, arts, healing, public engagement (past-life service or creative role)",
        "MARS":    "engineering, military, surgery, sports (past-life warrior or craftsman)",
        "MERCURY": "communication, trade, writing, mathematics (past-life merchant or scholar)",
        "JUPITER": "teaching, law, finance, counsel (past-life Guru or judge)",
        "VENUS":   "aesthetics, luxury trade, diplomacy (past-life artist or diplomat)",
        "SATURN":  "discipline, structure, labour, research (past-life ascetic or scientist)",
        "RAHU":    "technology, foreign connections, unconventional fields (karmic accumulation)",
        "KETU":    "spirituality, occult, medicine, liberation (karmic completion cycle)",
    }
    for p in d3_tenth_house_planets:
        if p.upper() in _skill_map:
            karmic_skills.append(_skill_map[p.upper()])

    d3_lord_quality = "unknown"
    if d3_tenth_lord:
        if d3_tenth_lord_house in KENDRA_HOUSES | TRIKONA_HOUSES:
            d3_lord_quality = "strong_karmic_support"
        elif d3_tenth_lord_house in DUSTHANA_HOUSES:
            d3_lord_quality = "karmic_obstruction"
        else:
            d3_lord_quality = "moderate_karmic_skill"

    return {
        "d3_tenth_house_planets": d3_tenth_house_planets,
        "karmic_skills_activated": karmic_skills,
        "d3_tenth_lord_quality": d3_lord_quality,
        "d3_note": (
            "Past-life skills and karmic career drives via D3 10th: "
            + (", ".join(karmic_skills) if karmic_skills else "None identified; neutral karmic slate.")
        ),
    }


# ── Step 5: Dasha + Transit Synchronisation ──────────────────────────────────
def _step5_dasha_transit(
    md_lord: str,
    ad_lord: str,
    d1_tenth_lord: str,
    d1_eleventh_lord: str,
    amk_planet: str,
    tenth_house_occupants: List[str],   # planets in D1 10th house
    saturn_transit_house: int,          # Saturn's current house from lagna
    jupiter_transit_house: int,         # Jupiter's current house from lagna
    d1_tenth_lord_house: int,           # natal house of 10th lord
) -> Dict[str, Any]:
    """
    Step 5: Career Dasha Activation + Double Transit check.

    Dasha activation: MD or AD lord is 10th lord / 11th lord / AmK /
                      or an occupant of the 10th house.
    Double transit  : Saturn AND Jupiter both transit 10th house,
                      or 10th lord's natal house.
    """
    career_planets = {d1_tenth_lord, d1_eleventh_lord, amk_planet} | set(tenth_house_occupants)

    md_active = md_lord in career_planets
    ad_active = ad_lord  in career_planets

    dasha_active = md_active or ad_active
    dasha_note_parts = []
    if md_active:
        dasha_note_parts.append(f"MD lord {md_lord} = career significator")
    if ad_active:
        dasha_note_parts.append(f"AD lord {ad_lord} = career significator")
    if not dasha_active:
        dasha_note_parts.append("Current MD/AD lord has NO direct career connection — muted period")

    # Double transit: both Saturn AND Jupiter activating 10th house or 10th lord's natal house
    target_houses = {10, d1_tenth_lord_house} if d1_tenth_lord_house else {10}
    sat_hits  = saturn_transit_house  in target_houses
    jup_hits  = jupiter_transit_house in target_houses
    double_transit = sat_hits and jup_hits

    transit_note = ""
    if double_transit:
        transit_note = (
            f"DOUBLE TRANSIT CONFIRMED: Saturn (H{saturn_transit_house}) "
            f"AND Jupiter (H{jupiter_transit_house}) are both activating "
            "the career axis. Major promotions, job changes, or status "
            "elevation events are highly imminent."
        )
    elif sat_hits:
        transit_note = f"Saturn alone activates career axis (H{saturn_transit_house}). Karmic career pressure — results via struggle."
    elif jup_hits:
        transit_note = f"Jupiter alone blesses career axis (H{jupiter_transit_house}). Opportunity available but needs Saturn's executor."
    else:
        transit_note = "Neither Saturn nor Jupiter is activating the career axis. Career transit support is absent."

    return {
        "md_lord": md_lord,
        "ad_lord": ad_lord,
        "dasha_active": dasha_active,
        "dasha_notes": dasha_note_parts,
        "double_transit_active": double_transit,
        "saturn_transit_house": saturn_transit_house,
        "jupiter_transit_house": jupiter_transit_house,
        "transit_note": transit_note,
        "timing_score": (
            1.0 if (dasha_active and double_transit) else
            0.7 if (dasha_active or double_transit) else
            0.2
        ),
    }


# ── Master Function ───────────────────────────────────────────────────────────
def compute_career_checklist(
    lagna_sign: int,
    moon_sign: int,
    sun_sign: int,
    planet_signs: Dict[str, int],           # P → sign idx (D1)
    planet_houses: Dict[str, int],          # P → house num from lagna (D1)
    ak_sign: int,
    amk_sign: int,
    amk_planet: str,
    d10_planet_houses: Dict[str, int],
    d3_tenth_house_planets: List[str],
    d3_tenth_lord: Optional[str],
    d3_tenth_lord_house: int,
    md_lord: str,
    ad_lord: str,
    tenth_house_occupants: List[str],
    saturn_transit_house: int,
    jupiter_transit_house: int,
) -> Dict[str, Any]:
    """
    Execute the full 5-step career checklist and return a synthesised report.

    Returns:
        career_direction    : qualitative assessment from D1
        soul_alignment      : AK–AmK relationship type
        d10_sustainability  : career sustainability via D10
        karmic_skills       : past-life professional drivers via D3
        current_dasha_active: bool — is timing window open?
        double_transit_active: bool — major event imminent?
        career_score        : weighted composite 0–1
        notes               : list of key narrative findings
    """
    tenth_from_lagna = (lagna_sign + 9) % 12
    d1_tenth_lord    = SIGN_LORDS[tenth_from_lagna]
    d1_eleventh_lord = SIGN_LORDS[(lagna_sign + 10) % 12]
    d1_tenth_lord_house = planet_houses.get(d1_tenth_lord, 0)

    s1 = _step1_d1_foundation(lagna_sign, moon_sign, sun_sign, planet_signs, planet_houses)
    s2 = _step2_jaimini(ak_sign, amk_sign, amk_planet)
    s3 = _step3_d10(d1_tenth_lord, d10_planet_houses)
    s4 = _step4_d3_karmic(d3_tenth_house_planets, d3_tenth_lord, d3_tenth_lord_house)
    s5 = _step5_dasha_transit(
        md_lord, ad_lord,
        d1_tenth_lord, d1_eleventh_lord, amk_planet,
        tenth_house_occupants,
        saturn_transit_house, jupiter_transit_house,
        d1_tenth_lord_house,
    )

    # Composite weighted score (Step weights: D1=25%, Jaimini=20%, D10=25%, D3=10%, Timing=20%)
    career_score = (
        0.25 * max(0.0, min(1.0, s1["d1_career_score"])) +
        0.20 * s2["jaimini_score"] +
        0.25 * s3["d10_score"] +
        0.10 * (1.0 if s4["d3_tenth_house_planets"] else 0.5) +
        0.20 * s5["timing_score"]
    )

    notes = []
    if s1["nexus_6_10_11_active"]:
        notes.append("6-10-11 nexus ACTIVE → potential for immense corporate/professional success")
    notes.extend(s1["negative_modifiers"])
    notes.append(s2["alignment_note"])
    notes.append(s3["d10_note"])
    notes.append(s4["d3_note"])
    notes.append(s5["transit_note"])

    career_direction: str
    if career_score >= 0.8:
        career_direction = "exceptional_career_promise"
    elif career_score >= 0.6:
        career_direction = "strong_career_promise"
    elif career_score >= 0.4:
        career_direction = "moderate_career_prospects"
    else:
        career_direction = "weak_career_structurally_challenged"

    return {
        "career_direction": career_direction,
        "career_score": round(career_score, 3),
        "soul_alignment": s2["ak_amk_alignment"],
        "d10_sustainability": s3["career_sustainability"],
        "karmic_skills": s4["karmic_skills_activated"],
        "current_dasha_active": s5["dasha_active"],
        "double_transit_active": s5["double_transit_active"],
        "d1_tenth_lord": d1_tenth_lord,
        "amk_planet": amk_planet,
        "step1_d1": s1,
        "step2_jaimini": s2,
        "step3_d10": s3,
        "step4_d3": s4,
        "step5_timing": s5,
        "notes": notes,
    }
