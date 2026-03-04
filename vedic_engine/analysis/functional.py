"""
Functional Benefic / Malefic Classification  (Lagna-specific roles).

In Vedic astrology every planet's benefic or malefic nature shifts
depending on which houses it *lords* for a given Lagna.  Natural
beneficence (Jupiter = good) is over-ridden by functional role.

Key rules (BPHS Ch. 34 / Phaladeepika Ch. 2):
  TRIKONA lords (1, 5, 9)  → functional benefics
  KENDRA lords  (1, 4, 7, 10) → neutral-to-benefic (powerful when combined)
  TRIK lords    (6, 8, 12) → functional malefics
  Planet owning BOTH kendra + trikona → YOGAKARAKA (strongest benefic)
  Planet owning trikona + trik → mixed; trikona still outweighs trik
  H2 / H7 lords → MARAKA (death / obstruction indicators)

Badhaka (obstructor) lord per lagna type:
  Movable  (Aries, Cancer, Libra, Capricorn)  -> H11 lord
  Fixed    (Taurus, Leo, Scorpio, Aquarius)   -> H9 lord
  Dual     (Gemini, Virgo, Sagittarius, Pisces) -> H7 lord

Usage:
    from vedic_engine.analysis.functional import compute_functional_analysis
    fa = compute_functional_analysis(lagna_sign=2)   # Gemini=2
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

from vedic_engine.config import (
    Planet, Sign, SIGN_LORDS, OWN_SIGNS, SignQuality, SIGN_QUALITIES,
)

_ALL_PLANETS = [
    Planet.SUN, Planet.MOON, Planet.MARS, Planet.MERCURY,
    Planet.JUPITER, Planet.VENUS, Planet.SATURN,
]

# Natural benefics subject to Kendradhipati Dosha (BPHS / Phaladeepika):
# When these planets own ONLY pure kendra houses (4, 7, 10 — NOT house 1
# which is simultaneously a trikona), they lose their benefic nature.
NATURAL_BENEFICS = frozenset({Planet.JUPITER, Planet.VENUS, Planet.MERCURY})

# House categories
TRIKONA_HOUSES = frozenset({1, 5, 9})
KENDRA_HOUSES  = frozenset({1, 4, 7, 10})
TRIK_HOUSES    = frozenset({6, 8, 12})
UPACHAYA       = frozenset({3, 6, 10, 11})
MARAKA_HOUSES  = frozenset({2, 7})


# ─── House lord lookup ────────────────────────────────────────────

def get_house_lord(house_num: int, lagna_sign: int) -> Optional[Planet]:
    """Return the planet that lords the nth house (1-based) for a lagna."""
    sign_idx = (lagna_sign + house_num - 1) % 12
    return SIGN_LORDS.get(Sign(sign_idx))


def get_house_lords_all(lagna_sign: int) -> Dict[int, Planet]:
    """Return {house_num: Planet} for all 12 houses."""
    return {h: lord for h in range(1, 13)
            if (lord := get_house_lord(h, lagna_sign))}


def get_owned_houses(planet: Planet, lagna_sign: int) -> List[int]:
    """House numbers (1-12) owned by a planet for given lagna."""
    owned = OWN_SIGNS.get(planet, [])
    result = []
    for sign in owned:
        sign_val = sign.value if isinstance(sign, Sign) else int(sign)
        h = (sign_val - lagna_sign) % 12 + 1
        result.append(h)
    return result


# ─── Classification ───────────────────────────────────────────────

def _house_quality(house: int) -> str:
    if house in TRIKONA_HOUSES: return "trikona"
    if house in KENDRA_HOUSES:  return "kendra"
    if house in TRIK_HOUSES:    return "trik"
    if house in UPACHAYA:       return "upachaya"
    return "neutral"


def classify_planet(planet: Planet, lagna_sign: int) -> Dict:
    """
    Classify a planet's functional role for a lagna.

    Returns:
        planet:        planet name string
        houses:        list of owned house numbers
        role:          'yogakaraka' | 'functional_benefic' | 'functional_malefic' | 'neutral'
        owns_trikona:  bool
        owns_kendra:   bool
        owns_trik:     bool
        score:         float  (-1.0 to +2.0)
    """
    houses    = get_owned_houses(planet, lagna_sign)
    qualities = [_house_quality(h) for h in houses]

    owns_trikona = "trikona" in qualities
    owns_kendra  = "kendra"  in qualities
    owns_trik    = "trik"    in qualities

    # Build score
    score = 0.0
    if owns_trikona:
        score += 1.0
    if owns_kendra and not owns_trikona:
        score += 0.5          # kendra-only is supportive
    if owns_kendra and owns_trikona:
        score += 0.5          # yogakaraka bonus
    if owns_trik:
        score -= 0.8
    if owns_trikona and owns_trik:
        score += 0.3          # trikona partially offsets trik lordship

    # Clamp
    score = max(-1.0, min(2.0, score))

    # Kendradhipati Dosha: natural benefics owning kendra but NOT trikona
    # lose their benefic nature and become functional malefics.
    # Classical cases: Jupiter for Gemini/Virgo (rules H7+H10 / H4+H7);
    #                  Mercury for Sagittarius/Pisces (rules H7+H10 / H4+H7).
    # Exception: H1 is both kendra AND trikona → owns_trikona=True → no dosha.
    if planet in NATURAL_BENEFICS and owns_kendra and not owns_trikona:
        score = min(score, -0.8)  # force into functional_malefic territory

    if owns_kendra and owns_trikona:
        role = "yogakaraka"
    elif score > 0.5:
        role = "functional_benefic"
    elif score < -0.3:
        role = "functional_malefic"
    else:
        role = "neutral"

    return {
        "planet":       planet.name,
        "houses":       houses,
        "role":         role,
        "owns_trikona": owns_trikona,
        "owns_kendra":  owns_kendra,
        "owns_trik":    owns_trik,
        "score":        round(score, 2),
    }


# ─── Special designations ─────────────────────────────────────────

def get_badhaka_planet(lagna_sign: int) -> Optional[Planet]:
    """
    Badhaka (obstructor) planet:
      Movable lagna → H11 lord
      Fixed lagna   → H9 lord
      Dual lagna    → H7 lord
    """
    lagna_s = Sign(lagna_sign)
    quality = SIGN_QUALITIES.get(lagna_s)
    if   quality == SignQuality.MOVABLE: badhaka_h = 11
    elif quality == SignQuality.FIXED:   badhaka_h = 9
    else:                                badhaka_h = 7   # DUAL
    return get_house_lord(badhaka_h, lagna_sign)


def get_maraka_planets(lagna_sign: int) -> List[Planet]:
    """Maraka lords (H2, H7) who can inflict death/major setbacks in dashas."""
    marakas = []
    for h in [2, 7]:
        lord = get_house_lord(h, lagna_sign)
        if lord and lord not in marakas:
            marakas.append(lord)
    return marakas


def get_yogakaraka_planets(lagna_sign: int) -> List[Planet]:
    """Planets that own BOTH a kendra and a trikona house → most potent benefics."""
    return [p for p in _ALL_PLANETS
            if classify_planet(p, lagna_sign)["role"] == "yogakaraka"]


# ─── Main API ─────────────────────────────────────────────────────

def compute_functional_analysis(lagna_sign: int) -> Dict:
    """
    Complete functional analysis for a lagna sign (0-based, Aries=0).

    Returns:
        lagna_sign:         int
        lagna_name:         str
        classifications:    {planet_name: classification_dict}
        yogakarakas:        [planet_name, ...]
        functional_benefics:[planet_name, ...]  (includes yogakarakas)
        functional_malefics:[planet_name, ...]
        neutral:            [planet_name, ...]
        badhaka:            planet_name or None
        badhaka_house:      int (the badhaka house number)
        marakas:            [planet_name, ...]
        house_lords:        {house_num: planet_name}
    """
    from vedic_engine.config import Sign as _Sign
    sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                  "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

    classifications: Dict[str, Dict] = {}
    for planet in _ALL_PLANETS:
        classifications[planet.name] = classify_planet(planet, lagna_sign)

    yogakarakas   = [p for p, c in classifications.items() if c["role"] == "yogakaraka"]
    func_benefics = [p for p, c in classifications.items()
                     if c["role"] in ("functional_benefic", "yogakaraka")]
    func_malefics = [p for p, c in classifications.items() if c["role"] == "functional_malefic"]
    neutrals      = [p for p, c in classifications.items() if c["role"] == "neutral"]

    badhaka_planet = get_badhaka_planet(lagna_sign)
    marakas        = get_maraka_planets(lagna_sign)

    # Determine badhaka house number
    lagna_s = _Sign(lagna_sign)
    quality = SIGN_QUALITIES.get(lagna_s)
    badhaka_house = 11 if quality == SignQuality.MOVABLE \
                    else (9 if quality == SignQuality.FIXED else 7)

    hl_raw = get_house_lords_all(lagna_sign)
    house_lords_str = {h: p.name for h, p in hl_raw.items()}

    return {
        "lagna_sign":          lagna_sign,
        "lagna_name":          sign_names[lagna_sign % 12],
        "classifications":     classifications,
        "yogakarakas":         yogakarakas,
        "functional_benefics": func_benefics,
        "functional_malefics": func_malefics,
        "neutral":             neutrals,
        "badhaka":             badhaka_planet.name if badhaka_planet else None,
        "badhaka_house":       badhaka_house,
        "marakas":             [m.name for m in marakas],
        "house_lords":         house_lords_str,
    }


def score_planet_functional(
    planet_name: str,
    functional_analysis: Dict,
    planet_house: Optional[int] = None,
    domain: Optional[str] = None,
) -> float:
    """
    Return a normalized functional score for a planet: -1.0 to +1.0.
    Yogakaraka → 1.0, func_benefic → 0.5-0.9, neutral → 0.0,
    func_malefic → -0.5, badhaka → -0.7, maraka → -0.3.

    Badhaka dual-role rules (per research):
    - Badhaka + Yogakaraka simultaneously → delivers yoga but with delays.
      Net effect: moderate positive (not full 1.0 but not negative either).
    - Badhaka in Upachaya house (3,6,10,11) → reduced long-term severity.
    - Domain sensitivity: Badhaka primarily suppresses material/external domains
      (career, finance, marriage). For spiritual/internal domains → hyper-activates.
    """
    cls  = functional_analysis.get("classifications", {}).get(planet_name, {})
    role = cls.get("role", "neutral")
    score = cls.get("score", 0.0)

    if role == "yogakaraka":
        base = 1.0
    elif role == "functional_benefic":
        base = min(0.9, 0.5 + score * 0.2)
    elif role == "functional_malefic":
        base = max(-0.7, score * 0.5)
    else:
        base = 0.0

    is_badhaka = (planet_name == functional_analysis.get("badhaka"))
    is_maraka  = (planet_name in functional_analysis.get("marakas", []))
    is_yogakaraka = (planet_name in functional_analysis.get("yogakarakas", []))

    if is_badhaka:
        if is_yogakaraka:
            # Dual role: Badhaka + Yogakaraka → delivers yoga but with obstacles/delays
            # Net: moderate positive (don't subtract full badhaka penalty)
            base = max(base * 0.55, 0.15)
        else:
            # Standard badhaka penalty
            MATERIAL_DOMAINS = {"career", "finance", "marriage", "property",
                                 "finance_active", "finance_invest", "children"}
            SPIRITUAL_DOMAINS = {"spiritual", "travel"}

            if domain and domain in SPIRITUAL_DOMAINS:
                # Badhaka hyper-activates spiritual domains
                base += 0.25
            elif domain and domain in MATERIAL_DOMAINS:
                # Stronger penalty for material domains
                base -= 0.35
            else:
                # Generic badhaka penalty
                base -= 0.30

            # Upachaya placement (3,6,10,11): reduced long-term severity
            if planet_house and planet_house in UPACHAYA:
                base += 0.12   # native develops skills to overcome obstruction

    if is_maraka:
        base -= 0.20

    return max(-1.0, min(1.0, base))
