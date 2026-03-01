"""
Divisional Chart (Varga) Interpretation Layer.

Implements classical rules from addditonal.md:
  D9  (Navāmśa)   – vargottama, Pushkara Navamsa, inner strength / marriage
  D10 (Daśāmśa)   – career analysis (lagna lord, Upachaya, 10th house)
  D7  (Saptāmśa)  – children / progeny (5th house count, benefics)
  D4  (Caturthāmśa)– property / assets (4th house, inheritance via 9th)
  D60 (Ṣaṣṭyāmśa)– karmic / fine-tuning (śubha vs krūra 1/60th portions)

All functions take pre-computed divisional sign indices (0-11) from
vedic_engine.core.divisional and natal chart data.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

SIGN_NAMES = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
]

PLANET_OWN_SIGNS: Dict[str, List[int]] = {
    "SUN":     [4],
    "MOON":    [3],
    "MARS":    [0, 7],
    "MERCURY": [2, 5],
    "JUPITER": [8, 11],
    "VENUS":   [1, 6],
    "SATURN":  [9, 10],
    "RAHU":    [],   # no own sign in standard system
    "KETU":    [],
}

EXALT_SIGNS: Dict[str, int] = {
    "SUN": 0, "MOON": 1, "MARS": 9, "MERCURY": 5,
    "JUPITER": 3, "VENUS": 11, "SATURN": 6,
}

DEBI_SIGNS: Dict[str, int] = {
    "SUN": 6, "MOON": 7, "MARS": 3, "MERCURY": 11,
    "JUPITER": 9, "VENUS": 5, "SATURN": 0,
}

BENEFICS = {"MOON", "MERCURY", "JUPITER", "VENUS"}
MALEFICS = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}


def _dignity(planet: str, sign: int) -> str:
    if sign in PLANET_OWN_SIGNS.get(planet, []):
        return "own"
    if EXALT_SIGNS.get(planet) == sign:
        return "exalted"
    if DEBI_SIGNS.get(planet) == sign:
        return "debilitated"
    return "neutral"


# ─── D9 Navāmśa Analysis ─────────────────────────────────────────────────────

# Pushkara Navamsa positions: (nakshatra_index, pada) based on BPHS tabulation
# Each entry = (d1_sign, navamsa_segment) where planet gains Pushkara blessing.
# 24 total Pushkara points (2 per sign), benefic nakshatras:
# Aries: Bharani-pada3 (20°-23°20'), Krittika-pada1 (26°40'-30°)
# Taurus: Rohini-pada2 (43°20'-46°40'), Mrigashira-pada1 (56°40'-60°)
# ... etc. Stored as (d1_sign_0idx, segment_0idx_within_sign_navamsa_0to8)
PUSHKARA_NAVAMSA: List[Tuple[int, int]] = [
    (0, 5), (0, 8),   # Aries:       segments 6 & 9 (0-indexed: 5 & 8)
    (1, 1), (1, 4),   # Taurus:      segments 2 & 5
    (2, 3), (2, 6),   # Gemini:      segments 4 & 7
    (3, 0), (3, 3),   # Cancer:      segments 1 & 4
    (4, 2), (4, 5),   # Leo:         segments 3 & 6
    (5, 1), (5, 7),   # Virgo:       segments 2 & 8
    (6, 0), (6, 4),   # Libra:       segments 1 & 5
    (7, 2), (7, 6),   # Scorpio:     segments 3 & 7
    (8, 1), (8, 5),   # Sagittarius: segments 2 & 6
    (9, 0), (9, 4),   # Capricorn:   segments 1 & 5
    (10, 2), (10, 7), # Aquarius:    segments 3 & 8
    (11, 3), (11, 6), # Pisces:      segments 4 & 7
]


def is_vargottama(d1_sign: int, d9_sign: int) -> bool:
    """Planet in same sign in D1 and D9 → vargottama (maximum strength)."""
    return d1_sign == d9_sign


def is_pushkara_navamsa(d1_lon: float) -> bool:
    """
    Check if a longitude falls in a Pushkara Navamsa position.
    d1_lon: absolute sidereal longitude 0-360.
    """
    from vedic_engine.core.coordinates import sign_of, degree_in_sign
    s = sign_of(d1_lon)
    d = degree_in_sign(d1_lon)
    seg = int(d / (30.0 / 9))   # which of 9 navamsa segments (0-8)
    return (s, seg) in PUSHKARA_NAVAMSA


def analyze_d9(
    planet_d1_lons: Dict[str, float],
    planet_d9_signs: Dict[str, int],
    d9_lagna: int,
) -> Dict:
    """
    Full D9 analysis for all planets.
    Returns vargottama list, pushkara list, D9 dignities, and marriage indications.
    """
    vargottama: List[str] = []
    pushkara: List[str] = []
    d9_dignities: Dict[str, str] = {}
    marriage_indications: List[str] = []

    from vedic_engine.core.coordinates import sign_of
    for planet, lon in planet_d1_lons.items():
        d1_sign = sign_of(lon)
        d9_sign = planet_d9_signs.get(planet)
        if d9_sign is None:
            continue

        if is_vargottama(d1_sign, d9_sign):
            vargottama.append(planet)

        if is_pushkara_navamsa(lon):
            pushkara.append(planet)

        dig = _dignity(planet, d9_sign)
        d9_dignities[planet] = dig

    # Marriage indicators: Venus (general), Jupiter (husband in female chart)
    for karaka in ["VENUS", "JUPITER", "MOON"]:
        d9_dig = d9_dignities.get(karaka, "neutral")
        if d9_dig in ("own", "exalted"):
            marriage_indications.append(f"{karaka} strong in D9 ({SIGN_NAMES[planet_d9_signs.get(karaka,0)]}) → favors marriage")
        elif d9_dig == "debilitated":
            marriage_indications.append(f"{karaka} debilitated in D9 → challenges in marriage/relationships")

    return {
        "vargottama":          vargottama,
        "pushkara":            pushkara,
        "d9_dignities":        d9_dignities,
        "d9_lagna_sign":       SIGN_NAMES[d9_lagna],
        "marriage_indications": marriage_indications,
    }


# ─── D10 Daśāmśa Analysis (Career) ───────────────────────────────────────────

# Upachaya houses in D10 (growth houses for career): 3, 6, 10, 11
UPACHAYA = {3, 6, 10, 11}


def analyze_d10(
    planet_d10_signs: Dict[str, int],
    d10_lagna: int,
    planet_d1_lons: Dict[str, float],
) -> Dict:
    """
    D10 career analysis per addditonal.md rules.
    - D10 lagna lord strong → stable career
    - Sun/Saturn/Mercury in own sign or Kendra → good profession
    - Saturn in Upachaya → steady success
    - 9th lord in D10 9th house → fortune/mentors
    - Planets in 6/8/12 from D10 lagna → obstacles
    """
    from vedic_engine.core.coordinates import sign_of

    d10_lagna_lord = _sign_lord(d10_lagna)
    lagna_lord_sign = planet_d10_signs.get(d10_lagna_lord, -1)
    lagna_lord_house = ((lagna_lord_sign - d10_lagna) % 12) + 1 if lagna_lord_sign >= 0 else None

    favorable: List[str] = []
    challenges: List[str] = []

    # Lagna lord strength
    if lagna_lord_house in (1, 4, 7, 10):
        favorable.append(f"D10 lagna lord {d10_lagna_lord} in Kendra (H{lagna_lord_house}) → stable career")
    elif lagna_lord_sign is not None and lagna_lord_sign in PLANET_OWN_SIGNS.get(d10_lagna_lord, []):
        favorable.append(f"D10 lagna lord {d10_lagna_lord} in own sign → stable career")
    elif lagna_lord_house in (6, 8, 12):
        challenges.append(f"D10 lagna lord {d10_lagna_lord} in dusthana (H{lagna_lord_house}) → career setbacks")

    # Key career planets
    for planet in ["SUN", "SATURN", "MERCURY"]:
        if planet not in planet_d10_signs:
            continue
        psign = planet_d10_signs[planet]
        house = ((psign - d10_lagna) % 12) + 1
        dig = _dignity(planet, psign)
        if dig in ("own", "exalted"):
            favorable.append(f"{planet} in {dig} sign in D10 → strong professional results")
        if planet == "SUN" and dig == "exalted":
            favorable.append("Sun exalted in D10 → leadership in career")
        if planet == "SATURN" and house in UPACHAYA:
            favorable.append(f"Saturn in Upachaya (H{house}) of D10 → steady, long-term professional success")
        if house in (6, 8, 12):
            challenges.append(f"{planet} in H{house} of D10 → obstacles to profession")

    # 10th house content
    tenth_planets = [p for p, s in planet_d10_signs.items()
                     if ((s - d10_lagna) % 12) + 1 == 10]
    tenth_summary = f"D10 10th house: {', '.join(tenth_planets) if tenth_planets else 'empty'}"

    return {
        "d10_lagna":      SIGN_NAMES[d10_lagna],
        "lagna_lord":     d10_lagna_lord,
        "favorable":      favorable,
        "challenges":     challenges,
        "tenth_house":    tenth_summary,
    }


# ─── D7 Saptāmśa Analysis (Children) ─────────────────────────────────────────

def analyze_d7(
    planet_d7_signs: Dict[str, int],
    d7_lagna: int,
) -> Dict:
    """
    D7 progeny analysis.
    - 5th house: benefics → easy conception; malefics → delays
    - Count of non-combust planets in 5th → estimated children number
    - 1st house affliction → constitutional fertility issues
    - 7th house affliction → spouse carries fertility karma
    """
    results: Dict = {}
    indications: List[str] = []

    def planets_in_house(house: int) -> List[str]:
        return [p for p, s in planet_d7_signs.items()
                if ((s - d7_lagna) % 12) + 1 == house]

    fifth_planets  = planets_in_house(5)
    first_planets  = planets_in_house(1)
    seventh_planets = planets_in_house(7)
    ninth_planets  = planets_in_house(9)

    # Fifth house analysis
    benefics_5th = [p for p in fifth_planets if p in BENEFICS]
    malefics_5th = [p for p in fifth_planets if p in MALEFICS]

    estimated_children = len([p for p in fifth_planets if p not in {"RAHU","KETU","SATURN"}])

    if benefics_5th:
        indications.append(f"Benefics in D7-5th ({', '.join(benefics_5th)}) → easy conception, healthy children")
    if malefics_5th:
        indications.append(f"Malefics in D7-5th ({', '.join(malefics_5th)}) → delays or challenges with children")

    # Jupiter check (natural karaka for children)
    if "JUPITER" in fifth_planets:
        indications.append("Jupiter in D7-5th → strong progeny blessing")

    if malefics_5th and not benefics_5th:
        indications.append("D7-5th dominated by malefics → significant progeny challenges indicated")

    if any(p in MALEFICS for p in first_planets):
        indications.append("Malefics in D7-1st → constitutional fertility considerations")

    if any(p in MALEFICS for p in seventh_planets):
        indications.append("Malefics in D7-7th → spouse's fertility karma a factor")

    if ninth_planets:
        indications.append(f"D7-9th house planets ({', '.join(ninth_planets)}) → lineage / grandchildren karma")

    return {
        "d7_lagna":          SIGN_NAMES[d7_lagna],
        "fifth_house":       fifth_planets,
        "estimated_children": estimated_children,
        "indications":       indications,
    }


# ─── D4 Chaturthāmśa Analysis (Property) ─────────────────────────────────────

def analyze_d4(
    planet_d4_signs: Dict[str, int],
    d4_lagna: int,
) -> Dict:
    """
    D4 property/assets analysis.
    - 1st house: overall happiness and wealth constitution
    - 4th house: actual real estate / property
    - 9th house: inherited wealth / patrimonial luck
    - 11th house: gains from assets (rental income)
    """
    indications: List[str] = []

    def planets_in_house(house: int) -> List[str]:
        return [p for p, s in planet_d4_signs.items()
                if ((s - d4_lagna) % 12) + 1 == house]

    fourth_planets  = planets_in_house(4)
    ninth_planets   = planets_in_house(9)
    eleventh_planets = planets_in_house(11)
    first_planets   = planets_in_house(1)

    # 4th house: property acquisition
    if any(p in BENEFICS for p in fourth_planets):
        indications.append(f"Benefics in D4-4th ({', '.join(fourth_planets)}) → property acquisition favored")
    if any(p in MALEFICS for p in fourth_planets):
        indications.append(f"Malefics in D4-4th ({', '.join([p for p in fourth_planets if p in MALEFICS])}) → property delays or disputes")
    if "SATURN" in fourth_planets:
        indications.append("Saturn in D4-4th → delayed but eventual property gain; old/stone structures")

    # 9th house: inheritance
    if ninth_planets:
        indications.append(f"D4-9th occupied ({', '.join(ninth_planets)}) → inherited wealth / ancestral property karma")

    # 11th house: income from assets
    if any(p in BENEFICS for p in eleventh_planets):
        indications.append(f"Benefics in D4-11th ({', '.join([p for p in eleventh_planets if p in BENEFICS])}) → income from property/assets")

    # D4 lagna lord placement
    d4_lagna_lord = _sign_lord(d4_lagna)
    lord_sign = planet_d4_signs.get(d4_lagna_lord, -1)
    lord_house = ((lord_sign - d4_lagna) % 12) + 1 if lord_sign >= 0 else None
    if lord_house in (1, 4, 11):
        indications.append(f"D4 lagna lord {d4_lagna_lord} in H{lord_house} → good property dharma/acquisition")
    elif lord_house in (6, 8, 12):
        indications.append(f"D4 lagna lord {d4_lagna_lord} in dusthana → challenges with property/assets")

    return {
        "d4_lagna":     SIGN_NAMES[d4_lagna],
        "fourth_house": fourth_planets,
        "ninth_house":  ninth_planets,
        "eleventh_house": eleventh_planets,
        "indications":  indications,
    }


# ─── D60 Ṣaṣṭyāmśa Analysis (Karmic fine-tuning) ────────────────────────────

# Shashtyamsha segments: which are krura (inauspicious) in ODD signs (0-indexed 1-60)
# In EVEN signs, the good/bad are REVERSED.
# Segments 1-60; inauspicious in odd signs: 1,2,8-12,15-16,30-35,39-44,48,51-52,59
_D60_KRURA_ODD = {
    1,2,8,9,10,11,12,15,16,30,31,32,33,34,35,39,40,41,42,43,44,48,51,52,59
}


def d60_segment(lon: float) -> int:
    """Return which 1/60th segment (1-60) the longitude falls in for its sign."""
    from vedic_engine.core.coordinates import degree_in_sign
    d = degree_in_sign(lon)
    seg = int(d / 0.5) + 1   # 0.5° each segment, 60 per sign
    return min(seg, 60)


def is_d60_shubha(lon: float, sign_idx: int) -> bool:
    """
    Returns True if the longitude falls in a śubha (auspicious) Shashtyamsha.
    Odd signs: krura = _D60_KRURA_ODD; even signs: krura is the complement.
    """
    seg = d60_segment(lon)
    is_odd_sign = (sign_idx % 2 == 0)   # sign_idx 0=Aries(odd), 1=Taurus(even)
    if is_odd_sign:
        return seg not in _D60_KRURA_ODD
    else:
        # Even sign: reverse — originally krura become shubha
        return seg in _D60_KRURA_ODD


def analyze_d60(planet_d1_lons: Dict[str, float]) -> Dict:
    """
    Compute D60 status for every planet.
    Returns: {planet: {"segment": int, "status": "shubha"/"krura", "effect": str}}
    """
    from vedic_engine.core.coordinates import sign_of
    results: Dict[str, Dict] = {}
    for planet, lon in planet_d1_lons.items():
        si = sign_of(lon)
        seg = d60_segment(lon)
        shubha = is_d60_shubha(lon, si)
        results[planet] = {
            "segment": seg,
            "status":  "shubha" if shubha else "krura",
            "effect":  "Fine karma → results better than D1 alone suggests" if shubha
                       else "Krura karma → results may be worse than D1 alone suggests",
        }
    return results


# ─── Master Varga Report ─────────────────────────────────────────────────────

def _sign_lord(sign_idx: int) -> str:
    """Return primary lord of a sign (0-11)."""
    lords = ["MARS","VENUS","MERCURY","MOON","SUN","MERCURY",
             "VENUS","MARS","JUPITER","SATURN","SATURN","JUPITER"]
    return lords[sign_idx]


import math as _math_varga

# ─── D1/D9 Fructification Synthesis (Logic Integration Manifest §3.1) ────────
#
# When a planet makes promises in D1, the D9 acts as a final arbiter of
# whether those promises will actually manifest in real life.
#
# Formula:
#   FCS(p) = P_D1(p) × log(1 + M_D9(p))
#
# Where:
#   P_D1(p) = planet's D1 promise score (passed in, 0.0 – 1.0 range)
#   M_D9(p) = D9 dignity multiplier:
#               Debilitated  → 0.2   (strong D9 veto: barely any fructification)
#               Enemy sign   → 0.6   (weakened delivery)
#               Neutral      → 1.0   (neutral: log(2) ≈ 0.693 of D1 promise)
#               Own sign     → 1.4   (strong delivery)
#               Exaltation   → 1.8   (full + bonus delivery)
#               Vargottama   → 2.0   (maximum — D1 and D9 in exact same sign)
#
# Maximum FCS when M_D9=2.0: P_D1 × log(3) ≈ 1.099 × P_D1 (log can exceed 1)
# So results are NOT capped at 1.0; they can signal "over-delivery".

_D9_MULTIPLIER: Dict[str, float] = {
    "debilitated":  0.2,
    "enemy":        0.6,
    "neutral":      1.0,
    "own":          1.4,
    "exalted":      1.8,
    "vargottama":   2.0,
}

# Enemy signs: the sign 7 away from own sign (BPHS natural enmity)
_ENEMY_SIGNS: Dict[str, List[int]] = {
    "SUN":     [6, 10],    # Libra (7th), Aquarius (great enemy Saturn owns)
    "MOON":    [9, 10],    # Capricorn, Aquarius
    "MARS":    [3, 9],     # Cancer (debil), Capricorn (partial)
    "MERCURY": [8, 11],    # Sagittarius (Jupiter=enemy), Pisces
    "JUPITER": [2, 5],     # Gemini, Virgo (Mercury owns; Mercury=enemy)
    "VENUS":   [0, 7],     # Aries (enemy Sun), Scorpio (enemy Mars)
    "SATURN":  [0, 3, 4],  # Aries (enemy Mars), Cancer (Moon), Leo (Sun)
}


def d9_dignity_multiplier(planet: str, d9_sign: int, d1_sign: int) -> Tuple[str, float]:
    """
    Determine the D9 dignity category and its M_D9 fructification multiplier.

    Args:
        planet    : Planet name (uppercase)
        d9_sign   : Planet's sign in D9 chart (0-indexed)
        d1_sign   : Planet's sign in D1 chart (0-indexed) — for vargottama check

    Returns:
        (dignity_label, M_D9_float)
    """
    # Vargottama (highest) — check first
    if d1_sign == d9_sign:
        return ("vargottama", _D9_MULTIPLIER["vargottama"])

    # Exaltation
    if EXALT_SIGNS.get(planet) == d9_sign:
        return ("exalted", _D9_MULTIPLIER["exalted"])

    # Debilitation
    if DEBI_SIGNS.get(planet) == d9_sign:
        return ("debilitated", _D9_MULTIPLIER["debilitated"])

    # Own sign
    if d9_sign in PLANET_OWN_SIGNS.get(planet, []):
        return ("own", _D9_MULTIPLIER["own"])

    # Enemy sign
    if d9_sign in _ENEMY_SIGNS.get(planet, []):
        return ("enemy", _D9_MULTIPLIER["enemy"])

    # Default: neutral
    return ("neutral", _D9_MULTIPLIER["neutral"])


def d1_d9_fructification_score(
    planet: str,
    d1_promise: float,
    d9_sign: int,
    d1_sign: int,
) -> Dict:
    """
    Compute the D1/D9 Fructification Composite Score (FCS) for one planet.

    FCS(p) = P_D1(p) × log(1 + M_D9(p))

    The log smoothing prevents an exalted D9 from simply doubling the D1 result.
    Instead it provides a bounded but generous boost: exalted → log(2.8) ≈ 1.03,
    vargottama → log(3) ≈ 1.099 multiplier on the D1 promise.

    A debilitated D9 planet has M_D9=0.2: FCS = P_D1 × log(1.2) ≈ 0.18 × P_D1
    → only ~18% of the D1 promise fructifies. Harsh veto.

    Args:
        planet     : Planet name (uppercase)
        d1_promise : Natal D1 strength/promise score (typically 0.0 – 1.0)
        d9_sign    : D9 sign index (0–11)
        d1_sign    : D1 sign index (0–11) for vargottama detection

    Returns:
        Dict with fcs, d9_dignity, m_d9, commentary
    """
    d9_dignity, m_d9 = d9_dignity_multiplier(planet, d9_sign, d1_sign)
    fcs = d1_promise * _math_varga.log(1.0 + m_d9)

    # Interpretation tier
    if fcs >= d1_promise * 0.90:
        tier = "excellent"
        note = "D9 strongly validates D1 promise — high probability of manifestation."
    elif fcs >= d1_promise * 0.60:
        tier = "good"
        note = "D9 reasonably supports D1 promise — moderate to good manifestation expected."
    elif fcs >= d1_promise * 0.30:
        tier = "weak"
        note = "D9 only partially supports D1 promise — delayed or diluted manifestation."
    else:
        tier = "suppressed"
        note = "D9 heavily debilitates D1 promise — results largely withheld or denied."

    return {
        "planet":       planet,
        "d1_promise":   round(d1_promise, 4),
        "d9_dignity":   d9_dignity,
        "m_d9":         m_d9,
        "fcs":          round(fcs, 4),
        "fcs_tier":     tier,
        "commentary":   note,
    }


def compute_all_fcs(
    planet_d1_lons:   Dict[str, float],
    planet_d9_signs:  Dict[str, int],
    planet_d1_strengths: Optional[Dict[str, float]] = None,
) -> Dict[str, Dict]:
    """
    Compute D1/D9 Fructification Scores for all planets.

    If planet_d1_strengths is not provided, uses a uniform promise of 0.5
    (equal-weight baseline).  Pass actual Shadbala ratios or yoga scores
    as d1_strengths for precise results.

    Returns a dict: {planet: fcs_result_dict}
    """
    from vedic_engine.core.coordinates import sign_of
    results = {}
    for planet, lon in planet_d1_lons.items():
        d1_sign = sign_of(lon)
        d9_sign = planet_d9_signs.get(planet)
        if d9_sign is None:
            continue
        d1_promise = (planet_d1_strengths or {}).get(planet, 0.5)
        results[planet] = d1_d9_fructification_score(planet, d1_promise, d9_sign, d1_sign)
    return results


def compute_varga_report(
    planet_d1_lons:  Dict[str, float],   # absolute sidereal longitudes
    planet_d9_signs: Dict[str, int],
    planet_d10_signs: Dict[str, int],
    planet_d7_signs: Dict[str, int],
    planet_d4_signs: Dict[str, int],
    d9_lagna:  int,
    d10_lagna: int,
    d7_lagna:  int,
    d4_lagna:  int,
    planet_d1_strengths: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Full divisional chart report combining D9/D10/D7/D4/D60 analyses,
    plus D1/D9 Fructification Composite Scores (FCS) for all planets.

    Args:
        planet_d1_strengths: Optional Shadbala ratios / yoga scores (0-1) per planet.
                             If omitted, uniform 0.5 baseline is used for FCS.
    """
    d9  = analyze_d9(planet_d1_lons, planet_d9_signs,  d9_lagna)
    d10 = analyze_d10(planet_d10_signs, d10_lagna, planet_d1_lons)
    d7  = analyze_d7(planet_d7_signs, d7_lagna)
    d4  = analyze_d4(planet_d4_signs, d4_lagna)
    d60 = analyze_d60(planet_d1_lons)

    # D1/D9 Fructification Composite Scores
    fcs = compute_all_fcs(planet_d1_lons, planet_d9_signs, planet_d1_strengths)

    # D60 shubha/krura count
    shubha_count = sum(1 for v in d60.values() if v["status"] == "shubha")
    krura_count  = len(d60) - shubha_count

    return {
        "d9":          d9,
        "d10":         d10,
        "d7":          d7,
        "d4":          d4,
        "d60":         d60,
        "d60_summary": f"{shubha_count} planets in shubha D60, {krura_count} in krura D60",
        "vargottama":  d9["vargottama"],
        "pushkara":    d9["pushkara"],
        "fcs":         fcs,   # D1/D9 fructification synthesis per planet
    }
