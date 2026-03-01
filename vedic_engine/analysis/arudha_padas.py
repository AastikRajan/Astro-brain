"""
Arudha Padas (AL, A2–A12) Engine.

Computes the "manifested image" of each bhava (house) using Jaimini's rule:
  - For house H, find its lord L.
  - Count n = houses from H to its lord's position (inclusive).
  - Raw Arudha = count n houses from the lord's position.
  - Exception: if Raw == H itself or Raw == (H+6) mod 12 (the 7th from H),
    take the 10th from raw (i.e. add 9 houses).

Standard Arudha labels:
  AL = A1  = Arudha Lagna   (image of self / public persona)
  A2       = Dhana Pada     (image of wealth)
  A3       = Vikrama Pada   (image of valour / siblings)
  A4       = Matri Pada     (image of home / mother)
  A5       = Putra Pada     (image of children / creativity)
  A6       = Shatru Pada    (image of enemies / diseases)
  A7  = DK = Dara Pada      (image of spouse / partnerships)
  A8       = Mrityu Pada    (image of obstacles / transformation)
  A9       = Bhagya Pada    (image of fortune / dharma)
  A10      = Karma Pada     (image of career / action)
  A11      = Labha Pada     (image of gains / income)
  A12 = UL = Upapada Lagna  (image of marriage / bed pleasures → marriage longevity)

Sources: Jaimini Sutras, BPHS, K.N. Rao commentary.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple


SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Sign lord (0-based)
_SIGN_LORD: Dict[int, str] = {
    0: "MARS", 1: "VENUS", 2: "MERCURY", 3: "MOON", 4: "SUN", 5: "MERCURY",
    6: "VENUS", 7: "MARS", 8: "JUPITER", 9: "SATURN", 10: "SATURN", 11: "JUPITER",
}

ARUDHA_LABELS: Dict[int, Tuple[str, str]] = {
    1:  ("AL",  "Arudha Lagna — public image, self"),
    2:  ("A2",  "Dhana Pada — image of wealth"),
    3:  ("A3",  "Vikrama Pada — image of courage, siblings"),
    4:  ("A4",  "Matri Pada — image of home, mother"),
    5:  ("A5",  "Putra Pada — image of children, creativity"),
    6:  ("A6",  "Shatru Pada — image of enemies, disease"),
    7:  ("A7",  "Dara Pada (Darapada) — image of spouse"),
    8:  ("A8",  "Mrityu Pada — image of obstacles, transformation"),
    9:  ("A9",  "Bhagya Pada — image of fortune, dharma"),
    10: ("A10", "Karma Pada — image of career, action"),
    11: ("A11", "Labha Pada — image of gains, income"),
    12: ("UL",  "Upapada Lagna (A12) — marriage, marital longevity"),
}

# Natural benefics/malefics for interpretation
_NATURAL_BENEFICS  = {"MOON", "MERCURY", "JUPITER", "VENUS"}
_NATURAL_MALEFICS  = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}


def compute_arudha(
    bhava: int,
    lagna_sign: int,
    planet_signs: Dict[str, int],
) -> int:
    """
    Compute the Arudha Pada index (0-based sign) for a given bhava (1-based).

    Args:
        bhava: House number 1-12
        lagna_sign: 0-based Ascendant sign
        planet_signs: {planet_name: sign_idx (0-based)}

    Returns:
        0-based sign index of the Arudha for the given bhava.
    """
    # Sign of the bhava (0-based)
    h_sign = (lagna_sign + bhava - 1) % 12

    # Lord of this sign
    lord = _SIGN_LORD.get(h_sign, "MARS")
    lord_sign = planet_signs.get(lord, h_sign)

    # Distance from H's sign to lord's sign (forward, 1-based)
    n = ((lord_sign - h_sign) % 12) + 1   # 1=same sign, 2=next sign, …

    # Raw Arudha = count same n from lord's sign
    raw_arudha = (lord_sign + n - 1) % 12

    # Exception: if raw falls on H's sign or the 7th from H's sign
    seventh_from_h = (h_sign + 6) % 12
    if raw_arudha == h_sign or raw_arudha == seventh_from_h:
        # Take 10th from raw Arudha (add 9 houses)
        raw_arudha = (raw_arudha + 9) % 12

    return raw_arudha


def compute_all_arudhas(
    lagna_sign: int,
    planet_signs: Dict[str, int],
) -> Dict[int, Dict]:
    """
    Compute all 12 Arudha Padas.

    Returns:
        Dict keyed by bhava number (1-12), each value is:
        {
            "bhava": int,
            "label": str,    # "AL", "A2"…"A12" / "UL"
            "meaning": str,
            "arudha_sign": int,        # 0-based sign index
            "arudha_sign_name": str,
        }
    """
    result = {}
    for bhava in range(1, 13):
        arudha_sign = compute_arudha(bhava, lagna_sign, planet_signs)
        label, meaning = ARUDHA_LABELS[bhava]
        result[bhava] = {
            "bhava": bhava,
            "label": label,
            "meaning": meaning,
            "arudha_sign": arudha_sign,
            "arudha_sign_name": SIGN_NAMES[arudha_sign],
        }
    return result


def analyze_arudha_influences(
    arudhas: Dict[int, Dict],
    planet_signs: Dict[str, int],
    lagna_sign: int,
) -> Dict[int, Dict]:
    """
    Analyze planetary influences on each Arudha Pada.

    For each Arudha, returns:
      - planets conjunct the Arudha sign
      - AL vs Lagna distance check (6/8/12 rule)
      - benefic/malefic assessment
      - brief interpretation
    """
    # Invert planet_signs for quick sign→[planets] lookup
    sign_to_planets: Dict[int, List[str]] = {}
    for pname, psign in planet_signs.items():
        sign_to_planets.setdefault(psign, []).append(pname)

    analyses = {}
    al_sign = arudhas[1]["arudha_sign"]
    lagna_distance = ((al_sign - lagna_sign) % 12)  # 0 = same as lagna; 6 = 7th etc

    for bhava, adata in arudhas.items():
        asign = adata["arudha_sign"]
        planets_in = sign_to_planets.get(asign, [])

        benefic_count = sum(1 for p in planets_in if p in _NATURAL_BENEFICS)
        malefic_count = sum(1 for p in planets_in if p in _NATURAL_MALEFICS)

        # Overall influence
        if benefic_count > malefic_count:
            influence = "benefic"
        elif malefic_count > benefic_count:
            influence = "malefic"
        elif not planets_in:
            influence = "neutral"
        else:
            influence = "mixed"

        # Core interpretation
        if bhava == 1:  # AL
            if influence == "benefic":
                note = "Good public image, reputation supported by benefic influence."
            elif influence == "malefic":
                note = "Public image challenged; malefic planets damage social standing."
            else:
                note = "Neutral public image — unoccupied or mixed Arudha Lagna."
            # Check AL distance from Lagna
            if lagna_distance in (0, 6, 8):
                note += " [Note: AL in dusthana (6/8/12) from Lagna — challenges to self-expression.]"
        elif bhava == 7:  # A7 (Darapada)
            if influence == "benefic":
                note = "Marriage/partnerships supported; harmonious spouse indicated."
            elif influence == "malefic":
                note = "Challenges in partnerships; discord or delays in marriage."
            else:
                note = "Neutral marital indications."
        elif bhava == 10:  # A10 (Karma Pada)
            career_planet = planets_in[0] if planets_in else None
            career_map = {
                "SUN": "leadership, government, authority",
                "MOON": "service, public care, emotions",
                "MARS": "engineering, military, physical work",
                "MERCURY": "writing, communication, trade",
                "JUPITER": "teaching, law, finance",
                "VENUS": "arts, luxury, beauty industry",
                "SATURN": "discipline, public service, infrastructure",
                "RAHU": "unconventional career, technology, foreign",
                "KETU": "spiritual/research career",
            }
            career_theme = career_map.get(career_planet, "general professional pursuits") if career_planet else "general career"
            note = f"Career focus: {career_theme}."
        elif bhava == 12:  # UL (A12 = Upapada)
            if influence == "benefic":
                note = "Marriage longevity supported; peaceful home life."
            elif influence == "malefic":
                note = "Challenges to marriage longevity; may indicate multiple unions."
            else:
                note = "Neutral marital longevity indications."
        else:
            label = adata["label"]
            if influence == "benefic":
                note = f"{label} strengthened by benefic planets — positive manifestation."
            elif influence == "malefic":
                note = f"{label} weakened by malefic planets — obstacles in this domain."
            else:
                note = f"{label} — no direct planetary influence on this Arudha."

        analyses[bhava] = {
            **adata,
            "planets_conjunct": planets_in,
            "benefic_influence": benefic_count,
            "malefic_influence": malefic_count,
            "overall_influence": influence,
            "note": note,
        }

    return analyses


def arudha_summary(
    lagna_sign: int,
    planet_signs: Dict[str, int],
) -> Dict:
    """
    Full Arudha Padas summary with interpretations.

    Returns dict with:
      - "arudhas": {bhava: {label, sign_name, planets_conjunct, note, ...}}
      - "al_sign": Arudha Lagna sign name
      - "ul_sign": Upapada Lagna sign name
      - "a7_sign": Darapada sign name
    """
    arudhas = compute_all_arudhas(lagna_sign, planet_signs)
    analyses = analyze_arudha_influences(arudhas, planet_signs, lagna_sign)

    return {
        "al_sign": arudhas[1]["arudha_sign_name"],
        "ul_sign": arudhas[12]["arudha_sign_name"],
        "a7_sign": arudhas[7]["arudha_sign_name"],
        "a10_sign": arudhas[10]["arudha_sign_name"],
        "arudhas": analyses,
    }


# ─── Rashi Drishti lookup for extended Arudha analysis ───────────────────────

_RASHI_DRISHTI: Dict[int, frozenset] = {
    0:frozenset({4,7,10}),3:frozenset({7,10,1}),6:frozenset({10,1,4}),9:frozenset({1,4,7}),
    1:frozenset({3,6,9}),4:frozenset({6,9,0}),7:frozenset({9,0,3}),10:frozenset({0,3,6}),
    2:frozenset({5,8,11}),5:frozenset({8,11,2}),8:frozenset({11,2,5}),11:frozenset({2,5,8}),
}

def _has_rashidrishti(s1: int, s2: int) -> bool:
    return s2 in _RASHI_DRISHTI.get(s1, frozenset()) or s1 in _RASHI_DRISHTI.get(s2, frozenset())


def compute_arudha_extended_analysis(
    lagna_sign: int,
    planet_signs: Dict[str, int],
) -> Dict:
    """
    Extended Jaimini Arudha Pada analysis (File 4 Sections 6 + 8).

    Adds to the base arudha_summary:
      1. AL-UL axis sustainability (Kendra/Trikona vs 6/8 or 2/12)
      2. Rahu/Ketu on AL or 7th from AL → health/marital warning (SUTRA 5)
      3. A10 influencing planets (occupants + Rashi Drishti aspirants)
      4. A10 reputation analysis (benefic=clean; malefic=controversial)
      5. Marriage probability summary from AL-UL
    """
    arudhas = compute_all_arudhas(lagna_sign, planet_signs)
    al_sign  = arudhas[1]["arudha_sign"]
    ul_sign  = arudhas[12]["arudha_sign"]
    a10_sign = arudhas[10]["arudha_sign"]

    # ── 1. AL-UL Axis Analysis ────────────────────────────────────────────────
    dist_al_ul = ((ul_sign - al_sign) % 12) + 1  # 1-based (1=same, 7=opposite)
    dist_ul_al = ((al_sign - ul_sign) % 12) + 1

    _KENDRA   = {1, 4, 7, 10}
    _TRIKONA  = {1, 5, 9}
    _TROUBLES = {6, 8, 2, 12}

    in_kendra   = dist_al_ul in _KENDRA
    in_trikona  = dist_al_ul in _TRIKONA
    is_troubled = dist_al_ul in _TROUBLES or dist_ul_al in _TROUBLES

    if in_kendra or in_trikona:
        al_ul_verdict = "SUSTAINABLE"
        al_ul_note    = (f"AL ({SIGN_NAMES[al_sign]}) and UL ({SIGN_NAMES[ul_sign]}) in "
                         f"Kendra/Trikona relationship ({dist_al_ul}th from AL). "
                         "Sustainable, publically supported marriage.")
    elif is_troubled:
        al_ul_verdict = "FRICTION"
        al_ul_note    = (f"AL and UL in 6/8 or 2/12 axis ({dist_al_ul}th from AL). "
                         "Fundamental friction between public trajectory and private marital harmony. "
                         "Separation risk possible.")
    else:
        al_ul_verdict = "NEUTRAL"
        al_ul_note    = f"AL-UL distance {dist_al_ul}: moderate sustainability, other factors determine."

    # ── 2. Rahu/Ketu on AL or 7th from AL (SUTRA 5) ──────────────────────────
    seventh_from_al = (al_sign + 6) % 12
    rahu_sign = planet_signs.get("RAHU", -1)
    ketu_sign = planet_signs.get("KETU", -1)

    node_on_al  = (rahu_sign == al_sign or ketu_sign == al_sign)
    node_on_7th = (rahu_sign == seventh_from_al or ketu_sign == seventh_from_al)
    node_flag   = node_on_al or node_on_7th
    node_note   = ""
    if node_flag:
        loc = []
        if node_on_al:  loc.append("on AL")
        if node_on_7th: loc.append("on 7th from AL")
        node_note = (f"SUTRA 5: Rahu/Ketu {', '.join(loc)} → "
                     "severe chronic stomach disorders, high fire/accident risk, "
                     "deeply rooted marital distress.")

    # ── 3. A10 Aspecting Planets (Rujay Pada analysis) ───────────────────────
    a10_occupants  = [p for p, s in planet_signs.items() if s == a10_sign]
    a10_aspecting  = [p for p, s in planet_signs.items() if s != a10_sign and _has_rashidrishti(s, a10_sign)]
    a10_influences = a10_occupants + a10_aspecting

    a10_benefics = [p for p in a10_influences if p in _NATURAL_BENEFICS]
    a10_malefics = [p for p in a10_influences if p in _NATURAL_MALEFICS]

    if a10_benefics and not a10_malefics:
        a10_reputation = "CLEAN — Untarnished professional reputation, steady promotions."
    elif a10_malefics and not a10_benefics:
        a10_reputation = "CONTROVERSIAL — Power through aggressive, dictatorial, or manipulative means."
    elif a10_benefics and a10_malefics:
        a10_reputation = "MIXED — Career success with occasional controversy; complex public image."
    else:
        a10_reputation = "NEUTRAL — Career uninfluenced by strong planetary signature on A10."

    # ── 4. Contraargala check on A10 (2nd from A10 vs 12th from A10) ─────────
    second_from_a10 = (a10_sign + 1) % 12    # 2nd from A10 = Argala support
    twelfth_from_a10 = (a10_sign + 11) % 12  # 12th from A10 = Virodha Argala

    a10_argala_planets  = [p for p, s in planet_signs.items() if s == second_from_a10]
    a10_virodha_planets = [p for p, s in planet_signs.items() if s == twelfth_from_a10]

    a10_argala_active = bool(a10_argala_planets) and len(a10_argala_planets) >= len(a10_virodha_planets)
    a10_contraargala  = bool(a10_virodha_planets) and len(a10_virodha_planets) > len(a10_argala_planets)

    contraargala_note = ""
    if a10_contraargala:
        contraargala_note = (f"Contraargala on A10: {a10_virodha_planets} in 12th from A10 blocks career "
                             f"against {a10_argala_planets or 'empty'} in 2nd. Career leap obstructed until "
                             "resolved by Dasha shift or transit.")
    elif a10_argala_active:
        contraargala_note = (f"Argala on A10: {a10_argala_planets} in 2nd from A10 provide career resources. "
                             "No blocking Contraargala — manifestation supported.")

    return {
        "al_sign":         SIGN_NAMES[al_sign],
        "ul_sign":         SIGN_NAMES[ul_sign],
        "a10_sign":        SIGN_NAMES[a10_sign],
        "al_ul_distance":  dist_al_ul,
        "al_ul_verdict":   al_ul_verdict,
        "al_ul_note":      al_ul_note,
        "node_affliction": node_flag,
        "node_note":       node_note,
        "a10_occupants":   a10_occupants,
        "a10_aspecting":   a10_aspecting,
        "a10_benefics":    a10_benefics,
        "a10_malefics":    a10_malefics,
        "a10_reputation":  a10_reputation,
        "a10_argala":      a10_argala_planets,
        "a10_virodha":     a10_virodha_planets,
        "a10_argala_active":    a10_argala_active,
        "a10_contraargala":     a10_contraargala,
        "contraargala_note":    contraargala_note,
    }
