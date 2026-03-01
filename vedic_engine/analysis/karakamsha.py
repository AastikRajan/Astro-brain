"""
Karakamsha Chart Engine — Jaimini System.

KEY DEFINITIONS:
  Svamsha      = Sign occupied by the Atmakaraka (AK) in the D-9 Navamsha chart.
                 Reveals: inner spiritual path, hidden talents, physical constitution.
  Karakamsha   = AK's Navamsha sign mapped back onto the D-1 Rashi chart,
                 rotated to become the 1st house.
                 Reveals: soul's destiny in the material world (career, status, spirituality).

DIFFERENCE:
  Svamsha  → D-9 chart analysis (internal/spiritual)
  Karakamsha → D-1 chart analysis (external/material destiny)

JAIMINI YOGAS (Section 5):
  Uses Rashi Drishti (sign aspects) — NOT geometric/Parashari aspects.
  Completely ignores house lordships.
  Based on conjunctions and Rashi Drishti between Chara Karakas.

Sources: Jaimini Upadesa Sutras; BPHS (Parashara); K.N. Rao Jaimini commentary.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple


SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Rashi Drishti (sign aspect) lookup — 0-based sign → frozenset of aspected signs
_RASHI_DRISHTI: Dict[int, frozenset] = {
    0:  frozenset({4, 7, 10}),   # Aries → Leo, Scorpio, Aquarius
    3:  frozenset({7, 10, 1}),   # Cancer → Scorpio, Aquarius, Taurus
    6:  frozenset({10, 1, 4}),   # Libra → Aquarius, Taurus, Leo
    9:  frozenset({1, 4, 7}),    # Capricorn → Taurus, Leo, Scorpio
    1:  frozenset({3, 6, 9}),    # Taurus → Cancer, Libra, Capricorn
    4:  frozenset({6, 9, 0}),    # Leo → Libra, Capricorn, Aries
    7:  frozenset({9, 0, 3}),    # Scorpio → Capricorn, Aries, Cancer
    10: frozenset({0, 3, 6}),    # Aquarius → Aries, Cancer, Libra
    2:  frozenset({5, 8, 11}),   # Gemini → Virgo, Sagittarius, Pisces
    5:  frozenset({8, 11, 2}),   # Virgo → Sagittarius, Pisces, Gemini
    8:  frozenset({11, 2, 5}),   # Sagittarius → Pisces, Gemini, Virgo
    11: frozenset({2, 5, 8}),    # Pisces → Gemini, Virgo, Sagittarius
}


def _has_rashi_drishti(sign_a: int, sign_b: int) -> bool:
    """True if sign_a aspects sign_b via Rashi Drishti (mutual)."""
    return sign_b in _RASHI_DRISHTI.get(sign_a, frozenset()) or \
           sign_a in _RASHI_DRISHTI.get(sign_b, frozenset())


def _planets_in_sign(sign: int, planet_signs: Dict[str, int]) -> List[str]:
    return [p for p, s in planet_signs.items() if s == sign]


# ─── AK in Navamsha Signs (Svamsha implications) ─────────────────────────────

SVAMSHA_INDICATIONS: Dict[int, str] = {
    0:  "Susceptibility to rodent/cat bites; highly aggressive baseline (Aries)",
    1:  "Wealth from quadrupeds; physical trouble from animals (Taurus)",
    2:  "Dermatological sensitivities, allergies, severe weight fluctuations (Gemini)",
    3:  "Vulnerability to water/aquatic dangers (Cancer)",
    4:  "Encounters with wild beasts, risk of public humiliation, dominant nature (Leo)",
    5:  "Fire hazards, gastrointestinal heat, severe digestive distress (Virgo)",
    6:  "Excellence in trade/commerce; risk of falls from heights (Libra)",
    7:  "Deprivation of mother's milk in infancy or severe aquatic dangers (Scorpio)",
    8:  "Vulnerability to falls from conveyances, animals, or high altitudes (Sagittarius)",
    9:  "Hazards from aquatic creatures, birds; enduring psychic trauma (Capricorn)",
    10: "Life of service to others; philanthropic but exhausted (Aquarius)",
    11: "Pinnacle of spiritual liberation (Moksha); philanthropic institutions (Pisces)",
}


# ─── Karakamsha House Interpretations ────────────────────────────────────────

KARAKAMSHA_HOUSE_MEANINGS: Dict[int, Dict] = {
    1:  {"name": "1st (Karakamsha itself)",
         "benefic": "Royal association, high administrative power, noble lineage.",
         "malefic": "Ego struggles, power conflicts.",
         "ketu": "Spiritual detachment from external identity."},
    2:  {"name": "2nd",
         "ketu": "Immense spiritual capacity, saintliness, non-attachment to wealth.",
         "benefic": "Eloquent speech, accumulated wealth through virtuous means.",
         "malefic": "Speech problems, financial hoarding."},
    3:  {"name": "3rd",
         "malefic": "Immense physical courage and success in complex undertakings (positive).",
         "benefic": "Passivity or defeat; loss of initiative (negative in 3rd)."},
    4:  {"name": "4th",
         "ketu": "Definitive Moksha Yoga — liberation from material cycle.",
         "benefic": "Real estate, vehicle luxuries, emotional contentment.",
         "malefic": "Domestic turbulence, property disputes."},
    5:  {"name": "5th",
         "jupiter": "Specialized traditional intelligence, Dharma Parayana.",
         "benefic": "Creative brilliance, intelligent children, speculation success.",
         "malefic": "Childlessness risk, speculative losses."},
    6:  {"name": "6th",
         "malefic": "Chronic diseases, heavy karmic debts requiring resolution.",
         "benefic": "Service industry success, legal profession."},
    7:  {"name": "7th",
         "benefic": "Pure heart, joyful union, successful partnerships.",
         "venus": "Marital bliss heavily fortified.",
         "malefic": "Marital tension, problematic partnerships."},
    8:  {"name": "8th",
         "any":    "Occult knowledge acquisition; simultaneous sudden troubles, physical weakness.",
         "notes":  "Research, hidden sciences; health vulnerabilities."},
    9:  {"name": "9th",
         "benefic": "Deep piety, fortune, Guru's teachings, long-distance travel.",
         "malefic": "Father difficulties, fortune delays."},
    10: {"name": "10th",
         "vacant": "Lord of 10th from Karakamsha dictates exact profession.",
         "benefic": "Career pillar of the family; executive authority.",
         "malefic": "Career controversy; power through force."},
    11: {"name": "11th",
         "mars":    "Raja Yoga for military or executive success.",
         "benefic": "Abundant gains, wide networks, bravery in execution.",
         "malefic": "Earned through opposition, enemies converted to allies."},
    12: {"name": "12th (Ishta Devata domain)",
         "ketu":    "Definitive spiritual emancipation in current incarnation.",
         "benefic": "Foreign residence; spiritual liberation through devotion.",
         "notes":   "Strongest planet here or aspecting via RD = Ishta Devata."},
}


# ─── Karakamsha Computation ───────────────────────────────────────────────────

def compute_svamsha(ak_d9_sign: int) -> Dict:
    """
    Svamsha = AK's sign in the D-9 Navamsha chart.

    Returns dict with sign, name, and life indication.
    """
    return {
        "sign_idx":   ak_d9_sign,
        "sign_name":  SIGN_NAMES[ak_d9_sign],
        "indication": SVAMSHA_INDICATIONS.get(ak_d9_sign, ""),
        "domain":     "Inner spiritual path, hidden talents, physical constitution (D-9 analysis)",
    }


def compute_karakamsha_lagna(ak_d9_sign: int) -> int:
    """
    Karakamsha Lagna = AK's D-9 sign mapped back to D-1.
    The D-1 chart is rotated so this sign becomes the 1st house.

    Returns: 0-based sign index that IS the Karakamsha Lagna.
    """
    # The sign itself becomes the KL — the rotation is conceptual; the sign is the house 1
    return ak_d9_sign


def analyze_karakamsha(
    ak_d9_sign: int,
    planet_signs: Dict[str, int],    # D-1 planet signs (0-based)
    lagna_sign: int,
    planet_lons: Optional[Dict[str, float]] = None,
    shadbala_ratios: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Full Karakamsha chart analysis.

    The Karakamsha chart rotates D-1 so that AK's D-9 sign = House 1.

    Parameters
    ----------
    ak_d9_sign    : 0-based sign of AK in D-9
    planet_signs  : D-1 planet placements {planet: sign_idx}
    lagna_sign    : D-1 Ascendant sign (0-based)
    planet_lons   : D-1 longitudes for extra dignity checks
    shadbala_ratios : Shadbala strength ratios

    Returns
    -------
    dict with Karakamsha houses, planetary placements, interpretations
    """
    kl = compute_karakamsha_lagna(ak_d9_sign)  # 0-based sign = KL house 1

    # Build house-to-sign and sign-to-house mapping from Karakamsha Lagna
    kl_house_signs: Dict[int, int] = {}   # house 1-12 → sign 0-11
    kl_sign_houses: Dict[int, int] = {}   # sign 0-11 → house 1-12
    for h in range(1, 13):
        s = (kl + h - 1) % 12
        kl_house_signs[h] = s
        kl_sign_houses[s] = h

    # Place planets into Karakamsha houses
    planet_kl_houses: Dict[str, int] = {}
    for planet, psign in planet_signs.items():
        h = kl_sign_houses.get(psign, 0)
        if h:
            planet_kl_houses[planet] = h

    # Rashi Drishti aspects INTO each Karakamsha house's sign
    kl_rashi_drishti: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
    for h in range(1, 13):
        target_sign = kl_house_signs[h]
        for planet, psign in planet_signs.items():
            if psign != target_sign and _has_rashi_drishti(psign, target_sign):
                kl_rashi_drishti[h].append(planet)

    _NAT_BEN = {"JUPITER", "VENUS", "MERCURY", "MOON"}
    _NAT_MAL = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}

    # Interpret each house
    house_analyses: List[Dict] = []
    for h in range(1, 13):
        occupants = [p for p, hh in planet_kl_houses.items() if hh == h]
        aspecting  = kl_rashi_drishti[h]
        all_influences = occupants + aspecting

        benefics_present = [p for p in all_influences if p in _NAT_BEN]
        malefics_present = [p for p in all_influences if p in _NAT_MAL]
        ketu_present     = "KETU" in all_influences
        jupiter_present  = "JUPITER" in all_influences
        venus_present    = "VENUS"   in all_influences
        mars_present     = "MARS"    in all_influences
        vacant           = not occupants

        meaning = KARAKAMSHA_HOUSE_MEANINGS.get(h, {})
        notes_list = []

        if ketu_present and h in (4, 12, 2):
            notes_list.append(meaning.get("ketu", ""))
        if benefics_present and "benefic" in meaning:
            notes_list.append(meaning.get("benefic", ""))
        if malefics_present and "malefic" in meaning:
            notes_list.append(meaning.get("malefic", ""))
        if jupiter_present and "jupiter" in meaning:
            notes_list.append(meaning.get("jupiter", ""))
        if venus_present and h == 7 and "venus" in meaning:
            notes_list.append(meaning.get("venus", ""))
        if mars_present and h == 11 and "mars" in meaning:
            notes_list.append(meaning.get("mars", ""))
        if vacant and h == 10 and "vacant" in meaning:
            notes_list.append(meaning.get("vacant", ""))
        if "any" in meaning and occupants:
            notes_list.append(meaning.get("any", ""))
        if "notes" in meaning:
            notes_list.append(meaning.get("notes", ""))

        notes = "; ".join(n for n in notes_list if n)

        house_analyses.append({
            "house":          h,
            "sign":           kl_house_signs[h],
            "sign_name":      SIGN_NAMES[kl_house_signs[h]],
            "occupants":      occupants,
            "rashi_drishti":  aspecting,
            "benefics":       benefics_present,
            "malefics":       malefics_present,
            "ketu":           ketu_present,
            "vacant":         vacant,
            "interpretation": notes or meaning.get("name", f"House {h}"),
        })

    # 10th house lord fallback (if 10th is vacant → lord dictates profession)
    _SIGN_LORD = {
        0:"MARS",1:"VENUS",2:"MERCURY",3:"MOON",4:"SUN",5:"MERCURY",
        6:"VENUS",7:"MARS",8:"JUPITER",9:"SATURN",10:"SATURN",11:"JUPITER"
    }
    tenth_sign = kl_house_signs[10]
    tenth_lord = _SIGN_LORD[tenth_sign]
    tenth_vacant = not any(p for p, hh in planet_kl_houses.items() if hh == 10)

    # Ishta Devata (strongest planet in 12th or aspecting 12th via RD)
    twelfth_sign = kl_house_signs[12]
    in_12th = [p for p, hh in planet_kl_houses.items() if hh == 12]
    aspecting_12th = kl_rashi_drishti[12]
    ishta_candidates = in_12th if in_12th else aspecting_12th
    ishta_devata = None
    if ishta_candidates and shadbala_ratios:
        ishta_devata = max(ishta_candidates, key=lambda p: shadbala_ratios.get(p, 0.0))
    elif ishta_candidates:
        ishta_devata = ishta_candidates[0]

    # Moksha yoga check (Ketu in 4th or 12th from KL)
    moksha_yoga = (
        "KETU" in [p for p, hh in planet_kl_houses.items() if hh in (4, 12)]
    )

    return {
        "karakamsha_lagna":   kl,
        "karakamsha_sign":    SIGN_NAMES[kl],
        "house_analyses":     house_analyses,
        "planet_kl_houses":   planet_kl_houses,
        "rashi_drishti_map":  kl_rashi_drishti,
        "tenth_lord":         tenth_lord,
        "tenth_vacant":       tenth_vacant,
        "profession_indicator": tenth_lord if tenth_vacant else None,
        "ishta_devata":       ishta_devata,
        "moksha_yoga":        moksha_yoga,
        "domain":             "Soul's material destiny: career, public status, visible spirituality",
    }


# ─── Jaimini Raja Yogas ───────────────────────────────────────────────────────

def compute_jaimini_yogas(
    karakas_list: List[Dict],           # from compute_chara_karakas()
    planet_signs: Dict[str, int],       # D-1 sign placements
    ak_d9_sign: int,                    # AK's D-9 sign (for Karakamsha context)
    planet_d9_signs: Optional[Dict[str, int]] = None,  # D-9 placements
    planet_lons: Optional[Dict[str, float]] = None,
) -> List[Dict]:
    """
    Compute Jaimini-specific Raja Yogas and special combinations.

    These operate ONLY through:
      1. Physical conjunction (same sign in D-1)
      2. Mutual Rashi Drishti (sign aspects)

    Ignores: house lordships, geometric Parashari aspects.

    Returns list of yoga dicts: {name, planets, mechanism, strength, meaning}
    """
    if not karakas_list:
        return []

    # Build role → planet quick lookup
    role_to_planet: Dict[str, str] = {}
    for k in karakas_list:
        role = k.get("role", "")
        planet = k.get("planet", "")
        if role and planet:
            role_to_planet[role] = planet

    ak  = role_to_planet.get("AK", "")
    amk = role_to_planet.get("AmK", "")
    bk  = role_to_planet.get("BK", "")
    mk  = role_to_planet.get("MK", "")
    pk  = role_to_planet.get("PK", "")
    gk  = role_to_planet.get("GK", "")
    dk  = role_to_planet.get("DK", "")

    yogas: List[Dict] = []

    def _conjunct_or_aspect(p1: str, p2: str) -> Tuple[bool, str]:
        """Returns (is_formed, mechanism)."""
        if not p1 or not p2 or p1 == p2:
            return False, ""
        s1 = planet_signs.get(p1, -1)
        s2 = planet_signs.get(p2, -1)
        if s1 < 0 or s2 < 0:
            return False, ""
        if s1 == s2:
            return True, "conjunction (same sign)"
        if _has_rashi_drishti(s1, s2):
            return True, "mutual Rashi Drishti"
        return False, ""

    # ── 1. AK + AmK: Primary Raja Yoga ──────────────────────────────────────
    formed, mech = _conjunct_or_aspect(ak, amk)
    if formed:
        yogas.append({
            "name":     "AK-AmK Raja Yoga (Primary)",
            "planets":  [ak, amk],
            "roles":    ["AK", "AmK"],
            "mechanism": mech,
            "strength": "very high",
            "meaning":  (
                "Highest Jaimini Raja Yoga. Soul and career minister aligned. "
                "Guarantees significant career elevation, status, and social power "
                "during their Dasha periods. Soul's desires execute through career."
            ),
        })

    # ── 2. AK + DK: Wealth through Partnership/Marriage ─────────────────────
    formed, mech = _conjunct_or_aspect(ak, dk)
    if formed:
        yogas.append({
            "name":     "AK-DK Raja Yoga (Wealth through Partnership)",
            "planets":  [ak, dk],
            "roles":    ["AK", "DK"],
            "mechanism": mech,
            "strength": "high",
            "meaning":  (
                "Wealth and success manifesting through or following marriage / "
                "major business partnerships. Soul's destiny intertwined with partnerships."
            ),
        })

    # ── 3. AK + PK: Mass Following / Creative Brilliance ────────────────────
    formed, mech = _conjunct_or_aspect(ak, pk)
    if formed:
        yogas.append({
            "name":     "AK-PK Raja Yoga (Mass Following)",
            "planets":  [ak, pk],
            "roles":    ["AK", "PK"],
            "mechanism": mech,
            "strength": "high",
            "meaning":  (
                "Massive public following, intellectual brilliance, status from creative "
                "outputs, students, or devoted followers. Soul expressed through creativity."
            ),
        })

    # ── 4. Moon + Venus: Luxury Raja Yoga ───────────────────────────────────
    moon_sign = planet_signs.get("MOON", -1)
    venus_sign = planet_signs.get("VENUS", -1)
    kl_sign = ak_d9_sign  # Karakamsha Lagna sign

    moon_venus_formed = False
    moon_venus_mech = ""
    if moon_sign >= 0 and venus_sign >= 0:
        if moon_sign == venus_sign:
            moon_venus_formed = True
            moon_venus_mech = "Moon-Venus conjunction (same sign)"
        elif _has_rashi_drishti(moon_sign, venus_sign):
            moon_venus_formed = True
            moon_venus_mech = "Moon-Venus mutual Rashi Drishti"

    # Venus in Karakamsha Lagna also triggers this yoga
    venus_in_kl = (venus_sign == kl_sign)
    if moon_venus_formed or venus_in_kl:
        mech_parts = []
        if moon_venus_formed:
            mech_parts.append(moon_venus_mech)
        if venus_in_kl:
            mech_parts.append("Venus in Karakamsha Lagna")
        yogas.append({
            "name":     "Moon-Venus Luxury Raja Yoga",
            "planets":  ["MOON", "VENUS"],
            "roles":    ["luminary", "luxury"],
            "mechanism": "; ".join(mech_parts),
            "strength": "high",
            "meaning":  (
                "Intense Jaimini Raja Yoga ensuring acquisition of extreme luxury, "
                "vehicles, and comforts. Aesthetic sensitivity and artistic refinement."
            ),
        })

    # ── 5. AK + AmK + DK: Triple Alliance ───────────────────────────────────
    # AK conjunct/aspect AmK AND AmK conjunct/aspect DK (or all three in mutual aspect)
    ak_amk, m1 = _conjunct_or_aspect(ak, amk)
    amk_dk, m2 = _conjunct_or_aspect(amk, dk)
    if ak_amk and amk_dk:
        yogas.append({
            "name":     "Triple Karaka Alliance (AK-AmK-DK)",
            "planets":  [ak, amk, dk],
            "roles":    ["AK", "AmK", "DK"],
            "mechanism": f"Chain: {m1} + {m2}",
            "strength": "extraordinary",
            "meaning":  (
                "Soul, career minister, and spouse indicator all aligned. "
                "Extremely rare. Career success through partnership routes with "
                "deep soul purpose. Multiple area simultaneous elevation."
            ),
        })

    # ── 6. AmK strength (Vargottama override) ───────────────────────────────
    if planet_d9_signs and amk:
        amk_d1_sign = planet_signs.get(amk, -1)
        amk_d9_sign = planet_d9_signs.get(amk, -1)
        if amk_d1_sign >= 0 and amk_d1_sign == amk_d9_sign:
            yogas.append({
                "name":     "AmK Vargottama Override",
                "planets":  [amk],
                "roles":    ["AmK"],
                "mechanism": "Vargottama (same sign in D-1 and D-9)",
                "strength": "absolute",
                "meaning":  (
                    "Amatyakaraka is Vargottama — career significator in supreme power. "
                    "Guarantees highly successful professional trajectory, OVERRIDING "
                    "all D-1 afflictions (debilitation, malefic conjunctions). "
                    "Career mandate permanently locked into destiny matrix."
                ),
            })

    # ── 7. AK in Svamsha sign implications ──────────────────────────────────
    # Already captured in svamsha analysis — add cross-reference note
    if ak and planet_d9_signs:
        ak_nav_sign = planet_d9_signs.get(ak, -1)
        if ak_nav_sign >= 0:
            indication = SVAMSHA_INDICATIONS.get(ak_nav_sign, "")
            yogas.append({
                "name":     f"AK Svamsha ({SIGN_NAMES[ak_nav_sign]})",
                "planets":  [ak],
                "roles":    ["AK"],
                "mechanism": f"AK in {SIGN_NAMES[ak_nav_sign]} Navamsha (Svamsha)",
                "strength": "permanent karmic imprint",
                "meaning":  indication or f"Soul's karmic path via {SIGN_NAMES[ak_nav_sign]}",
            })

    return yogas


# ─── Trikona Timing Rule (Section 8) ─────────────────────────────────────────

def check_marriage_timing(
    active_chara_dasha_sign: int,
    ul_sign: Optional[int],
    dk_planet: Optional[str],
    planet_signs: Dict[str, int],
) -> Dict:
    """
    Jaimini marriage timing rule (SUTRA 7).
    IF active Chara Dasha sign:
      a) Contains Darakaraka (DK), OR
      b) Contains Upapada Lagna (UL), OR
      c) Aspects UL via Rashi Drishti
    THEN: high-confidence marriage window.

    Returns: {flag: bool, reasons: list, confidence: str}
    """
    reasons = []
    flag = False

    ds = active_chara_dasha_sign

    # a) DK planet in dasha sign
    if dk_planet and planet_signs.get(dk_planet, -1) == ds:
        flag = True
        reasons.append(f"{dk_planet} (DK) in active Chara Dasha sign")

    # b) UL in dasha sign
    if ul_sign is not None and ul_sign == ds:
        flag = True
        reasons.append("Upapada Lagna (UL) in active Chara Dasha sign")

    # c) Dasha sign aspects UL via Rashi Drishti
    if ul_sign is not None and ul_sign != ds and _has_rashi_drishti(ds, ul_sign):
        flag = True
        reasons.append(f"Dasha sign {SIGN_NAMES[ds]} aspects UL ({SIGN_NAMES[ul_sign]}) via Rashi Drishti")

    return {
        "marriage_flag":   flag,
        "reasons":          reasons,
        "confidence":       "HIGH" if len(reasons) >= 2 else ("MODERATE" if flag else "LOW"),
        "note":             "Requires additional confirmation: Transit Jupiter/Saturn on UL or UL lord.",
    }


def check_career_timing(
    active_chara_dasha_sign: int,
    lagna_sign: int,
    amk_planet: Optional[str],
    a10_sign: Optional[int],
    planet_signs: Dict[str, int],
) -> Dict:
    """
    Jaimini career peak timing rule (SUTRA 8).
    IF active Chara Dasha sign:
      a) Is 10th house from Lagna, OR
      b) Contains Amatyakaraka (AmK), OR
      c) Aspects A10 (Rajya Pada) via Rashi Drishti without Virodha obstruction
    THEN: significant career event.

    Returns: {flag: bool, reasons: list, confidence: str}
    """
    reasons = []
    flag = False
    ds = active_chara_dasha_sign

    # a) 10th house from Lagna
    tenth_from_lagna = (lagna_sign + 9) % 12
    if ds == tenth_from_lagna:
        flag = True
        reasons.append(f"Dasha sign is 10th house ({SIGN_NAMES[ds]}) from Lagna")

    # b) AmK planet in dasha sign
    if amk_planet and planet_signs.get(amk_planet, -1) == ds:
        flag = True
        reasons.append(f"{amk_planet} (AmK) in active Chara Dasha sign")

    # c) Dasha sign aspects A10 via Rashi Drishti
    if a10_sign is not None and ds != a10_sign and _has_rashi_drishti(ds, a10_sign):
        flag = True
        reasons.append(f"Dasha sign aspects A10 ({SIGN_NAMES[a10_sign]}) via Rashi Drishti")

    return {
        "career_flag":  flag,
        "reasons":       reasons,
        "confidence":    "HIGH" if len(reasons) >= 2 else ("MODERATE" if flag else "LOW"),
        "note":          "Maximum confidence with 3 confirmations: Vimshottari + Jaimini + Transit.",
    }


# ─── AL/UL Relationship Analysis (Section 6) ─────────────────────────────────

def analyze_al_ul_relationship(
    al_sign: int,
    ul_sign: int,
    planet_signs: Dict[str, int],
) -> Dict:
    """
    Evaluate the sustainability of marriage from AL-UL spatial dynamics.

    Rules:
      Kendra/Trikona relationship → sustainable, publically supported marriage.
      6/8 or 2/12 axis → irreconcilable friction, separation risk.
      Rahu/Ketu on AL or 7th from AL → digestive disorders, fire accidents, marital distress.
    """
    # Distance from AL to UL (forward)
    dist = ((ul_sign - al_sign) % 12) + 1  # 1 = same sign, 7 = 7th, etc.

    _KENDRA    = {1, 4, 7, 10}
    _TRIKONA   = {1, 5, 9}
    _DUSHTHANA_PAIRS = {(6, 8), (8, 6), (2, 12), (12, 2)}

    # Reverse distance
    dist_ul_al = ((al_sign - ul_sign) % 12) + 1

    in_kendra    = dist in _KENDRA
    in_trikona   = dist in _TRIKONA
    is_68_212    = ((dist in {6, 8, 2, 12}) or (dist_ul_al in {6, 8, 2, 12}))

    if in_kendra or in_trikona:
        relationship = "SUSTAINABLE"
        marriage_note = "Sustainable, publically supported marriage. Kendra/Trikona alignment."
    elif is_68_212:
        relationship = "FRICTION"
        marriage_note = ("Fundamental irreconcilable friction between public trajectory and "
                         "private marital harmony. Separation risk indicated.")
    else:
        relationship = "NEUTRAL"
        marriage_note = "Moderate marriage sustainability; other factors determine quality."

    # Rahu/Ketu on AL or 7th from AL
    seventh_from_al = (al_sign + 6) % 12
    rahu_sign  = planet_signs.get("RAHU", -1)
    ketu_sign  = planet_signs.get("KETU", -1)

    node_on_al = (rahu_sign == al_sign or ketu_sign == al_sign)
    node_on_7th = (rahu_sign == seventh_from_al or ketu_sign == seventh_from_al)
    node_affliction = node_on_al or node_on_7th

    # A10 analysis via planets aspecting A10
    result = {
        "al_sign":          al_sign,
        "al_sign_name":     SIGN_NAMES[al_sign],
        "ul_sign":          ul_sign,
        "ul_sign_name":     SIGN_NAMES[ul_sign],
        "al_to_ul_distance": dist,
        "relationship":     relationship,
        "marriage_note":    marriage_note,
        "in_kendra":        in_kendra,
        "in_trikona":       in_trikona,
        "is_6_8_or_2_12":   is_68_212,
        "node_affliction":  node_affliction,
        "node_on_al":       node_on_al,
        "node_on_7th_from_al": node_on_7th,
    }

    if node_affliction:
        result["node_affliction_note"] = (
            "RAHU/KETU on AL or 7th from AL: severe chronic stomach disorders, "
            "high fire/accident risk, and deeply rooted marital distress flagged (SUTRA 5)."
        )

    return result
