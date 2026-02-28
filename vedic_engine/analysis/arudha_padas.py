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
