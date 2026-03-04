"""
Advanced Jyotish Techniques  (Phase 4, File 6 – analysis).

Implements NEW pure functions from research:
  – Bhrigu Sutras 9×12 interpretive matrix (lookup)
  – Nadi Amsa / Pada Nadhamsha (150-part division, equal model)
  – Chaturthamsha D4 construction + property timing rules
  – Drekkana 3 variants (Parashari, Parivritta, Somnath)
  – Ashtamsha D8 construction + interpretation rules
  – Jataka Tatva extended Neechabhanga (3 extra conditions)
  – Saptha Shalaka Chakra Vedha grid
  – Phala Jyotish event prediction rules

Architecture rule: ALL pure functions. No weights, no blending, no prediction logic.
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Any, Optional

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_LORDS = {
    "Aries": "MARS", "Taurus": "VENUS", "Gemini": "MERCURY",
    "Cancer": "MOON", "Leo": "SUN", "Virgo": "MERCURY",
    "Libra": "VENUS", "Scorpio": "MARS", "Sagittarius": "JUPITER",
    "Capricorn": "SATURN", "Aquarius": "SATURN", "Pisces": "JUPITER",
}

ODD_SIGNS = frozenset([0, 2, 4, 6, 8, 10])  # indices: Aries, Gemini, Leo, ...
DUSTHANA = frozenset([6, 8, 12])
KENDRA = frozenset([1, 4, 7, 10])
UPACHAYA = frozenset([3, 6, 10, 11])

EXALT_SIGNS = {
    "SUN": 0, "MOON": 1, "MARS": 9, "MERCURY": 5,
    "JUPITER": 3, "VENUS": 11, "SATURN": 6,
}
DEBIL_SIGNS = {
    "SUN": 6, "MOON": 7, "MARS": 3, "MERCURY": 11,
    "JUPITER": 9, "VENUS": 5, "SATURN": 0,
}

# 28 Nakshatras including Abhijit (placed between Uttara Ashadha and Shravana)
NAKSHATRA_28 = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Abhijit", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]


# ════════════════════════════════════════════════════════════════════════════
# 1. BHRIGU SUTRAS – 9×12 INTERPRETIVE MATRIX
# ════════════════════════════════════════════════════════════════════════════

# Condensed 1-line summaries per planet-house combination
BHRIGU_SUTRAS: Dict[str, Dict[int, str]] = {
    "SUN": {
        1: "Sparse hair, temperamental, ego-driven, eye afflictions",
        2: "Speech defects, loss of early wealth, government penal actions",
        3: "Courageous, loss of older siblings, dominant intellect",
        4: "Deprived of ancestral land, heart/chest vulnerabilities, restless mind",
        5: "Loss of first child, highly intellectual, stomach issues, easily angered",
        6: "Destroyer of enemies, immense immune resilience, high status",
        7: "Severe friction in marriage, delayed union, travel-oriented spouse",
        8: "Eye disease, sudden falls, fewer children, short longevity if afflicted",
        9: "Loss of father early, spiritual but unorthodox, conflict with preceptors",
        10: "Supreme success, political power, commanding personality",
        11: "Limitless wealth, influential network, longevity, vehicle acquisition",
        12: "Migratory, massive financial drains, eye issues, solitary nature",
    },
    "MOON": {
        1: "Handsome, romantic, rapid emotional fluctuations",
        2: "Soft-spoken, wealthy, fluctuating finances, attractive face",
        3: "Fond of art/music, protective of siblings, communicative",
        4: "Deep maternal happiness, conveyances, agricultural gains",
        5: "Female progeny predominant, highly creative, speculative success",
        6: "Somatic illness, gastric issues, susceptible to subtle adversaries",
        7: "Passionate, attractive spouse, foreign travels, jealous nature",
        8: "Hidden chronic diseases, psychological fears, aquatic dangers",
        9: "Highly devoted, prosperous, foreign residence, charitable",
        10: "Public-facing career, fluctuating fame, wealth through women",
        11: "High fame, steady influx of resources, long life, good friends",
        12: "Secretive, high expenses on luxuries, sleep disturbances",
    },
    "MARS": {
        1: "Scars on head/face, highly aggressive, martial inclination",
        2: "Harsh speech, sudden wealth via land, severe familial disputes",
        3: "Extreme physical courage, loss of younger brothers, athletic",
        4: "Domestic strife, loss of maternal property, chest wounds",
        5: "Aggressive children, surgical interventions, sharp intellect",
        6: "Crushes enemies ruthlessly, debt-free, prone to cuts/burns",
        7: "Kuja Dosha marital friction, assertive spouse, violent temper",
        8: "Eye/urinary disease, rheumatic pain, fatal accidents, short life",
        9: "Disagreement with father, dogmatic, aggressive faith",
        10: "Commanding position, uniform career, mechanical skills, successful",
        11: "Large gains via real estate, leadership, elder sibling friction",
        12: "High expenditure, hidden enemies, limb injuries, weapon wounds",
    },
    "MERCURY": {
        1: "Analytical, articulate, youthful appearance, highly adaptable",
        2: "Persuasive speaker, financial acumen, mathematical talent",
        3: "Literary talent, frequent short journeys, logical siblings",
        4: "Clever hands, academic success, multiple conveyances, happy",
        5: "Scholarly, advisor role, multiple children, deep learning",
        6: "Nervous disorders, strategic victory over rivals, analytical",
        7: "Intellectual spouse, early marriage, successful partnerships",
        8: "Long life, inheritance, neurological sensitivities, occult learning",
        9: "Philosophical, scientific mind, publisher, highly educated",
        10: "Career in commerce/writing, rapid promotions, famous",
        11: "Multifaceted income, expansive social network, financial brilliance",
        12: "Expenditures on education, mental restlessness, nervous anxiety",
    },
    "JUPITER": {
        1: "Magnanimous, heavy physique, divine protection, deeply moral",
        2: "Vast wealth accumulation, eloquent speaker, family leader",
        3: "Cautious courage, philosophical siblings, respected by peers",
        4: "Immense domestic peace, large properties, ethical mother",
        5: "Brilliant progeny, deep wisdom, ministerial capability, famous",
        6: "Lethargy, subdues enemies via diplomacy, liver/sugar issues",
        7: "Virtuous spouse, expansion of public relations, stable marriage",
        8: "Long life, peaceful end, deep occult knowledge, secretive wealth",
        9: "Supreme luck, religious authority, pilgrimages, highly devoted",
        10: "Honorable profession, judiciary/teaching, immense respect",
        11: "Massive wealth, total fulfillment of desires, charitable",
        12: "Expenditures on charity, moksha, spiritual liberation, peaceful",
    },
    "VENUS": {
        1: "Charismatic, fond of luxury, artistic, physically attractive",
        2: "Attractive face, sudden wealth, poetic speech, food lover",
        3: "Affectionate to siblings, creative hobbies, success in arts",
        4: "Beautiful homes, luxury vehicles, profound contentment, sensual",
        5: "Romantic, artistic children, massive speculative success",
        6: "Reproductive/kidney issues, subtle enemies, overcomes via charm",
        7: "Sensual, highly sexed, loss of spouse if severely afflicted",
        8: "Wealth through marriage, peaceful death, reproductive ailments",
        9: "Fortunate, artistic inclinations, long travels, aesthetic",
        10: "Career in arts/women's goods, comfortable status, easy life",
        11: "Gains through females/arts, extreme luxury, immense popularity",
        12: "Bed comforts, high expenses on sensual pleasures, foreign lands",
    },
    "SATURN": {
        1: "Melancholic, slow to act, long-limbed, persistent, gloomy",
        2: "Restricted wealth, harsh speech, dental/facial issues, separated from family",
        3: "Serious mindset, loss of siblings, manual trades",
        4: "Detachment from mother, dilapidated homes, depressive thoughts",
        5: "Delayed progeny, slow learner, rigid beliefs, chronic stomach",
        6: "Supreme conqueror of enemies, chronic slow-healing diseases, fearless",
        7: "Older/serious spouse, delayed marriage, legal friction, cold/stable",
        8: "Extreme longevity, slow death, deep occult, hidden diseases",
        9: "Orthodox, philosophical, delayed fortune, atheist early",
        10: "Heavy labor, slow but certain rise to power",
        11: "Slow but permanent wealth, older friends, massive late-life gains",
        12: "Isolation, imprisonment risk, long-term hospitalization, severe losses",
    },
    "RAHU": {
        1: "Unconventional, eccentric, ailments, deeply manipulative",
        2: "Manipulative speech, foreign wealth, familial disconnect",
        3: "Extraordinary bravery, technological skills",
        4: "Foreign residence, turbulent domestic life, maternal distress, phobias",
        5: "Unusual children, extreme speculative risks, deceptive intellect",
        6: "Immune to black magic, absolute victor in litigation, mysterious diseases",
        7: "Foreign/unorthodox spouse, partnership deceit",
        8: "Phobias, poison/venom risks, sudden occult insights, hidden wealth",
        9: "Rebellion against tradition, unorthodox gurus, extreme foreign travel",
        10: "Sudden career rise and fall, political manipulation, visible",
        11: "Massive sudden gains, material fulfillment, corrupt friends",
        12: "Asylum, deep foreign settlement, sleep paralysis, hidden addictions",
    },
    "KETU": {
        1: "Spiritual, highly internalized, physically weak, detached",
        2: "Stammering, loss of inherited wealth, peculiar eating habits",
        3: "Mental courage, spiritual siblings, lacks physical drive",
        4: "Complete detachment from property, sudden loss of home",
        5: "Karmic children, hyper-focused intellect, mantra siddhi, stomach pain",
        6: "Unidentifiable diseases, ignores enemies, highly intuitive",
        7: "Detached spouse, spiritual partnerships, marital void, sudden breaks",
        8: "Chronic piles/fistula, extreme intuitive flashes, sudden fatal events",
        9: "Complete asceticism, extreme pilgrimages, highly orthodox faith",
        10: "Complete disinterest in status, sudden career shifts, spiritual work",
        11: "Denies typical material gains, spiritual network, unexpected small gains",
        12: "Final liberation (Moksha), monastic life, wandering, extreme isolation",
    },
}


def lookup_bhrigu_sutra(planet: str, house: int) -> Dict[str, Any]:
    """Look up the Bhrigu Sutra aphorism for a planet in a given house (1-12)."""
    planet_data = BHRIGU_SUTRAS.get(planet, {})
    description = planet_data.get(house, "No data available")
    return {
        "planet": planet,
        "house": house,
        "bhrigu_sutra": description,
    }


def lookup_bhrigu_all_planets(planet_houses: Dict[str, int]) -> List[Dict[str, Any]]:
    """Get Bhrigu Sutra readings for all planets based on their house positions."""
    results: List[Dict[str, Any]] = []
    for planet, house in sorted(planet_houses.items()):
        if house < 1 or house > 12:
            continue
        results.append(lookup_bhrigu_sutra(planet, house))
    return results


# ════════════════════════════════════════════════════════════════════════════
# 2. NADI AMSA / PADA NADHAMSHA (150-Part Division)
# ════════════════════════════════════════════════════════════════════════════

def compute_nadi_amsa(longitude: float) -> Dict[str, Any]:
    """
    Equal Division Model (Savodya Kaal):
    Each Rasi (30°) divided into 150 equal parts.
    1 Nadi Amsa = 30° / 150 = 0.2° = 12 arc-minutes.
    In temporal terms: ~48 seconds of clock time per Nadi Amsa.

    Returns the Nadi Amsa number (1-150) within the sign,
    plus the absolute Nadi Amsa (1-1800) across the zodiac.
    """
    lon = longitude % 360.0
    sign_idx = int(lon / 30) % 12
    degree_in_sign = lon % 30.0

    # Nadi Amsa within sign: 1-indexed
    nadi_in_sign = int(degree_in_sign / 0.2) + 1
    if nadi_in_sign > 150:
        nadi_in_sign = 150

    # Absolute Nadi Amsa: 1-1800
    nadi_absolute = sign_idx * 150 + nadi_in_sign

    return {
        "longitude": round(lon, 6),
        "sign": SIGN_NAMES[sign_idx],
        "degree_in_sign": round(degree_in_sign, 6),
        "nadi_amsa_in_sign": nadi_in_sign,
        "nadi_amsa_absolute": nadi_absolute,
        "arc_per_nadi": "0° 12'",
        "time_per_nadi": "~48 seconds",
    }


# ════════════════════════════════════════════════════════════════════════════
# 3. CHATURTHAMSHA (D4) – PROPERTY DIVISION
# ════════════════════════════════════════════════════════════════════════════

def compute_chaturthamsha(longitude: float) -> Dict[str, Any]:
    """
    D4 (Turyamsa): each sign divided into 4 equal 7.5° sectors.
    0°-7.5°   → same sign
    7.5°-15°  → 4th sign from it
    15°-22.5° → 7th sign from it
    22.5°-30° → 10th sign from it
    """
    lon = longitude % 360.0
    sign_idx = int(lon / 30) % 12
    degree_in_sign = lon % 30.0

    if degree_in_sign < 7.5:
        d4_idx = sign_idx
        sector = 1
    elif degree_in_sign < 15.0:
        d4_idx = (sign_idx + 3) % 12
        sector = 2
    elif degree_in_sign < 22.5:
        d4_idx = (sign_idx + 6) % 12
        sector = 3
    else:
        d4_idx = (sign_idx + 9) % 12
        sector = 4

    return {
        "longitude": round(lon, 4),
        "d1_sign": SIGN_NAMES[sign_idx],
        "degree_in_sign": round(degree_in_sign, 4),
        "d4_sector": sector,
        "d4_sign": SIGN_NAMES[d4_idx],
        "d4_sign_lord": SIGN_LORDS[SIGN_NAMES[d4_idx]],
    }


def analyze_d4_property(
    d4_lagna_lord_house: int,
    d4_fourth_lord_house: int,
    d4_first_lord_sign: str = "",
    d4_second_lord_sign: str = "",
    d4_fourth_lord_sign: str = "",
    d4_eighth_lord_sign: str = "",
    planets_in_d4_fourth: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    D4 property timing and acquisition analysis.

    Rules:
    - Acquisition: Dasha of D4 Lagna Lord, D4 4th Lord, or planets in D4 4th house
    - Mars → raw land/foundations. Venus → luxury homes. Saturn → inherited/agricultural.
    - Self-acquired: link between 1st+2nd+4th lords in D4
    - Inherited: link between 8th+4th lords (especially via Saturn/9th house)
    - Loss: 4th lord in D4 Dusthana (6/8/12)
    """
    if planets_in_d4_fourth is None:
        planets_in_d4_fourth = []

    # Property nature based on activating planet
    property_nature: List[str] = []
    if "MARS" in planets_in_d4_fourth:
        property_nature.append("Raw land, structural foundations")
    if "VENUS" in planets_in_d4_fourth:
        property_nature.append("Luxury/aesthetic property")
    if "SATURN" in planets_in_d4_fourth:
        property_nature.append("Inherited/agricultural land, slow construction")
    if "JUPITER" in planets_in_d4_fourth:
        property_nature.append("Temple/educational property, expansion trigger")

    # Self-acquired vs Inherited
    # Simplified: check if first+fourth lords are related (same sign as proxy)
    self_acquired = (d4_first_lord_sign == d4_fourth_lord_sign and d4_first_lord_sign != "")
    inherited = (d4_eighth_lord_sign == d4_fourth_lord_sign and d4_eighth_lord_sign != "")

    acquisition = "Self-Acquired" if self_acquired else ("Inherited" if inherited else "Mixed/Undetermined")

    # Loss indicator
    fourth_lord_in_dusthana = d4_fourth_lord_house in DUSTHANA
    loss_risk = fourth_lord_in_dusthana

    return {
        "d4_lagna_lord_house": d4_lagna_lord_house,
        "d4_fourth_lord_house": d4_fourth_lord_house,
        "planets_in_d4_fourth": planets_in_d4_fourth,
        "property_nature": property_nature,
        "acquisition_type": acquisition,
        "loss_risk": loss_risk,
        "loss_note": "4th lord in Dusthana → forced sale/eviction risk" if loss_risk else "No immediate loss indicators",
    }


# ════════════════════════════════════════════════════════════════════════════
# 4. DREKKANA VARIANTS (3 Calculation Methods)
# ════════════════════════════════════════════════════════════════════════════

def compute_parashari_drekkana(longitude: float) -> Dict[str, Any]:
    """
    Standard Parashari Drekkana (D3):
    0°-10°  → same sign (Sage Narada / Atma)
    10°-20° → 5th sign from it (Sage Agastya / Mind)
    20°-30° → 9th sign from it (Sage Durvasa / Senses)
    """
    lon = longitude % 360.0
    sign_idx = int(lon / 30) % 12
    degree_in_sign = lon % 30.0

    if degree_in_sign < 10:
        d3_idx = sign_idx
        decan = 1
        ruler = "Narada"
        dimension = "Atma (Spiritual)"
    elif degree_in_sign < 20:
        d3_idx = (sign_idx + 4) % 12
        decan = 2
        ruler = "Agastya"
        dimension = "Manas (Psychological)"
    else:
        d3_idx = (sign_idx + 8) % 12
        decan = 3
        ruler = "Durvasa"
        dimension = "Senses (Physical)"

    return {
        "method": "Parashari",
        "d1_sign": SIGN_NAMES[sign_idx],
        "degree_in_sign": round(degree_in_sign, 4),
        "decanate": decan,
        "d3_sign": SIGN_NAMES[d3_idx],
        "d3_lord": SIGN_LORDS[SIGN_NAMES[d3_idx]],
        "sage_ruler": ruler,
        "dimension": dimension,
    }


def compute_parivritta_drekkana(longitude: float) -> Dict[str, Any]:
    """
    Parivritta Drekkana: continuous cyclical progression.
    Each 10° maps to a sequential sign starting from Aries, cycling through
    the entire zodiac. 36 decanates across 360°.
    """
    lon = longitude % 360.0
    # Each decanate = 10°, total 36 decanates
    decan_absolute = int(lon / 10)  # 0-35
    decan_in_sign = (decan_absolute % 3) + 1
    sign_idx = int(lon / 30) % 12

    # Parivritta: sequential from Aries
    parivritta_sign_idx = decan_absolute % 12

    return {
        "method": "Parivritta",
        "d1_sign": SIGN_NAMES[sign_idx],
        "degree_in_sign": round(lon % 30.0, 4),
        "decanate": decan_in_sign,
        "decanate_absolute": decan_absolute + 1,
        "d3_sign": SIGN_NAMES[parivritta_sign_idx],
        "d3_lord": SIGN_LORDS[SIGN_NAMES[parivritta_sign_idx]],
        "note": "Used for psychological analysis and Prashna thief identification",
    }


def compute_somnath_drekkana(longitude: float) -> Dict[str, Any]:
    """
    Somnath (Jagannath) Drekkana: niche calculation with reversed
    progression for even signs.
    Odd signs: same as Parashari (1→ same, 2→ 5th, 3→ 9th)
    Even signs: reversed (1→ 9th, 2→ 5th, 3→ same)
    Focus: inner vitality, sexual energy, karmic libido.
    """
    lon = longitude % 360.0
    sign_idx = int(lon / 30) % 12
    degree_in_sign = lon % 30.0
    is_odd = sign_idx in ODD_SIGNS

    if degree_in_sign < 10:
        decan = 1
        if is_odd:
            d3_idx = sign_idx
        else:
            d3_idx = (sign_idx + 8) % 12
    elif degree_in_sign < 20:
        decan = 2
        d3_idx = (sign_idx + 4) % 12  # same for both
    else:
        decan = 3
        if is_odd:
            d3_idx = (sign_idx + 8) % 12
        else:
            d3_idx = sign_idx

    return {
        "method": "Somnath (Jagannath)",
        "d1_sign": SIGN_NAMES[sign_idx],
        "degree_in_sign": round(degree_in_sign, 4),
        "decanate": decan,
        "d3_sign": SIGN_NAMES[d3_idx],
        "d3_lord": SIGN_LORDS[SIGN_NAMES[d3_idx]],
        "sign_parity": "Odd" if is_odd else "Even",
        "note": "Focus on inner vitality, sexual energy, karmic libido",
    }


# ════════════════════════════════════════════════════════════════════════════
# 5. ASHTAMSHA (D8) CONSTRUCTION
# ════════════════════════════════════════════════════════════════════════════

def compute_ashtamsha(longitude: float) -> Dict[str, Any]:
    """
    D8: each sign divided into 8 equal 3.75° segments.
    Segment n (0-based) maps to sign_idx + n for odd signs (forward),
    or sign_idx + (7-n) for even signs (backward).
    Standard: Aries starts at Aries, segment progresses.
    """
    lon = longitude % 360.0
    sign_idx = int(lon / 30) % 12
    degree_in_sign = lon % 30.0
    segment = min(int(degree_in_sign / 3.75), 7)  # 0-7

    # D8 sign: offset from natal sign
    d8_idx = (sign_idx + segment) % 12

    return {
        "longitude": round(lon, 4),
        "d1_sign": SIGN_NAMES[sign_idx],
        "degree_in_sign": round(degree_in_sign, 4),
        "d8_segment": segment + 1,
        "d8_sign": SIGN_NAMES[d8_idx],
        "d8_lord": SIGN_LORDS[SIGN_NAMES[d8_idx]],
    }


def analyze_d8_health(
    d8_lagna_lord_house: int,
    d8_eighth_lord_house: int,
    khara_lord_d8_house: int = 0,
    mars_in_d8: int = 0,
    ketu_in_d8: int = 0,
    saturn_d8_sign: str = "",
    saturn_debilitated_d8: bool = False,
) -> Dict[str, Any]:
    """
    D8 health interpretation rules:
    - Khara (22nd Drekkana lord) in D8 dusthana → chronic incurable disease
    - Mars/Ketu in D8 1st/8th → sudden physical trauma
    - Saturn debilitated in D8 → terminal parameters
    - 8th house of D8 = absolute terminal point
    """
    findings: List[Dict[str, str]] = []

    if khara_lord_d8_house in DUSTHANA:
        findings.append({
            "type": "CHRONIC_DISEASE",
            "detail": f"22nd Drekkana lord in D8 H{khara_lord_d8_house} (Dusthana) → chronic incurable disease",
        })

    if mars_in_d8 in (1, 8):
        findings.append({
            "type": "SURGICAL_TRAUMA",
            "detail": f"Mars in D8 H{mars_in_d8} → sudden physical trauma when activated by Pratyantardasha",
        })

    if ketu_in_d8 in (1, 8):
        findings.append({
            "type": "SUDDEN_INJURY",
            "detail": f"Ketu in D8 H{ketu_in_d8} → sudden unexplained injury/pain",
        })

    if saturn_debilitated_d8:
        findings.append({
            "type": "TERMINAL_PARAMETER",
            "detail": "Saturn (Ayushkaraka) debilitated in D8 → terminal parameters indicated",
        })

    if d8_eighth_lord_house in DUSTHANA:
        findings.append({
            "type": "LONGEVITY_THREAT",
            "detail": f"D8 8th lord in H{d8_eighth_lord_house} (Dusthana) → longevity under stress",
        })

    severity = "HIGH" if len(findings) >= 3 else ("MODERATE" if findings else "LOW")

    return {
        "d8_lagna_lord_house": d8_lagna_lord_house,
        "d8_eighth_lord_house": d8_eighth_lord_house,
        "findings": findings,
        "findings_count": len(findings),
        "severity": severity,
    }


# ════════════════════════════════════════════════════════════════════════════
# 6. JATAKA TATVA – EXTENDED NEECHABHANGA CONDITIONS
# ════════════════════════════════════════════════════════════════════════════

def check_neechabhanga_extended(
    planet: str,
    planet_house: int,
    planet_d1_sign_idx: int,
    planet_d9_sign_idx: int = -1,
    planet_d60_sign_idx: int = -1,
    other_debilitated: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """
    Jataka Tatva additional Neechabhanga conditions beyond standard 8:
    1. Upachaya Override: debilitated planet in Upachaya (3,6,10,11) →
       material success, psychological struggles remain
    2. Navamsha/Shashtiamsha Exaltation: debilitated D1 but exalted D9/D60 →
       absolute cancellation, supreme status in later life
    3. Mutual Aspect of Debilitation: two debilitated planets in mutual aspect (7th) →
       both lose debilitation, function as yogakarakas
    """
    if other_debilitated is None:
        other_debilitated = {}

    debil_sign = DEBIL_SIGNS.get(planet, -1)
    exalt_sign = EXALT_SIGNS.get(planet, -1)
    is_debilitated = (planet_d1_sign_idx == debil_sign)

    if not is_debilitated:
        return {
            "planet": planet,
            "is_debilitated": False,
            "cancellations": [],
            "note": "Planet is not debilitated – no Neechabhanga applicable",
        }

    cancellations: List[Dict[str, str]] = []

    # Condition 1: Upachaya Override
    if planet_house in UPACHAYA:
        cancellations.append({
            "type": "UPACHAYA_OVERRIDE",
            "detail": f"Debilitated {planet} in Upachaya H{planet_house} → material success guaranteed, psychological struggles remain",
            "quality": "MATERIAL",
        })

    # Condition 2: Navamsha or Shashtiamsha exaltation
    if planet_d9_sign_idx == exalt_sign:
        cancellations.append({
            "type": "NAVAMSHA_EXALTATION",
            "detail": f"Debilitated in D1 but exalted in D9 ({SIGN_NAMES[exalt_sign]}) → absolute cancellation, late-life supremacy",
            "quality": "ABSOLUTE",
        })
    if planet_d60_sign_idx == exalt_sign:
        cancellations.append({
            "type": "D60_EXALTATION",
            "detail": f"Debilitated in D1 but exalted in D60 ({SIGN_NAMES[exalt_sign]}) → absolute cancellation",
            "quality": "ABSOLUTE",
        })

    # Condition 3: Mutual aspect of debilitation
    for other_planet, other_sign_idx in other_debilitated.items():
        if other_planet == planet:
            continue
        # Check if in mutual 7th aspect
        if (planet_d1_sign_idx + 6) % 12 == other_sign_idx:
            cancellations.append({
                "type": "MUTUAL_DEBILITATION_ASPECT",
                "detail": f"Mutual 7th aspect with debilitated {other_planet} → both become yogakarakas",
                "quality": "RAJA_YOGA",
            })

    return {
        "planet": planet,
        "is_debilitated": True,
        "d1_sign": SIGN_NAMES[planet_d1_sign_idx],
        "house": planet_house,
        "cancellations": cancellations,
        "cancelled": len(cancellations) > 0,
        "note": f"{len(cancellations)} Jataka Tatva cancellation(s) found" if cancellations else "No extended cancellation conditions met",
    }


# ════════════════════════════════════════════════════════════════════════════
# 7. SAPTHA SHALAKA CHAKRA – VEDHA GRID
# ════════════════════════════════════════════════════════════════════════════

# Vedha pairs: nakshatras on same line cause Vedha to each other
# Using 28-nakshatra system (including Abhijit at position 21)
# Pairs from the 7×4 perimeter grid, starting Krittika NE clockwise
SAPTHA_VEDHA_PAIRS: List[Tuple[str, str]] = [
    ("Krittika", "Shravana"),
    ("Rohini", "Dhanishtha"),
    ("Mrigashira", "Shatabhisha"),
    ("Ardra", "Purva Bhadrapada"),
    ("Punarvasu", "Uttara Bhadrapada"),
    ("Pushya", "Revati"),
    ("Ashlesha", "Ashwini"),
    ("Magha", "Bharani"),
    ("Purva Phalguni", "Mula"),
    ("Uttara Phalguni", "Purva Ashadha"),
    ("Hasta", "Uttara Ashadha"),
    ("Chitra", "Abhijit"),
    ("Swati", "Anuradha"),
    ("Vishakha", "Jyeshtha"),
]

# Build lookup dict for fast Vedha check
_VEDHA_LOOKUP: Dict[str, str] = {}
for a, b in SAPTHA_VEDHA_PAIRS:
    _VEDHA_LOOKUP[a] = b
    _VEDHA_LOOKUP[b] = a

# Dangerous nakshatra positions from Janma (1-indexed)
FATAL_NAK_POSITIONS = frozenset([1, 3, 5, 7, 10, 19, 23])


def check_saptha_shalaka_vedha(
    janma_nakshatra: str,
    transit_sun_nakshatra: str = "",
    transit_malefic_nakshatras: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Saptha Shalaka Chakra evaluation:
    1. Check if Sun transits a Vedha star to Janma Nakshatra → danger to life
    2. Check if malefics (Saturn/Mars/Rahu/Ketu) transit 1st/3rd/5th/7th/10th/19th/23rd
       nakshatra from Janma
    """
    if transit_malefic_nakshatras is None:
        transit_malefic_nakshatras = {}

    findings: List[Dict[str, str]] = []

    # Sun Vedha check
    vedha_star = _VEDHA_LOOKUP.get(janma_nakshatra, "")
    if transit_sun_nakshatra and transit_sun_nakshatra == vedha_star:
        findings.append({
            "type": "SUN_VEDHA",
            "detail": f"Sun transiting {transit_sun_nakshatra} (Vedha to {janma_nakshatra}) → severe danger/anxiety",
        })

    # Malefic transit on fatal positions
    if janma_nakshatra in NAKSHATRA_28:
        janma_idx = NAKSHATRA_28.index(janma_nakshatra)
        for malefic, mal_nak in transit_malefic_nakshatras.items():
            if mal_nak in NAKSHATRA_28:
                mal_idx = NAKSHATRA_28.index(mal_nak)
                distance = ((mal_idx - janma_idx) % 28) + 1
                if distance in FATAL_NAK_POSITIONS:
                    findings.append({
                        "type": "FATAL_TRANSIT",
                        "detail": f"{malefic} transiting {mal_nak} ({distance}th from {janma_nakshatra}) → fatalistic results",
                    })

    return {
        "janma_nakshatra": janma_nakshatra,
        "vedha_star": vedha_star,
        "findings": findings,
        "danger_level": "HIGH" if len(findings) >= 2 else ("MODERATE" if findings else "LOW"),
    }


# ════════════════════════════════════════════════════════════════════════════
# 8. PHALA JYOTISH – EVENT PREDICTION RULES
# ════════════════════════════════════════════════════════════════════════════

def check_theft_litigation(
    sixth_lord_house: int,
    eighth_lord_house: int,
    twelfth_lord_house: int,
    sixth_lord_aspects_twelfth: bool = False,
    rahu_house: int = 0,
) -> Dict[str, Any]:
    """
    Theft/Litigation algorithm from Phala Jyotish:
    - 6th lord in Dusthana or 8th lord heavily aspecting 6th → legal disputes
    - If 6th lord connects to 12th house → imprisonment follows litigation
    - Rahu in 12th aspected by 6th lord → long-term incarceration
    """
    risk_factors: List[str] = []

    if sixth_lord_house in DUSTHANA:
        risk_factors.append(f"6th lord in H{sixth_lord_house} (Dusthana) → active legal/theft triggers")
    if eighth_lord_house == 6:
        risk_factors.append("8th lord in 6th house → sudden legal crisis, betrayal")

    imprisonment_risk = False
    if sixth_lord_house == 12 or sixth_lord_aspects_twelfth:
        risk_factors.append("6th lord connected to 12th house → litigation leads to imprisonment")
        imprisonment_risk = True
    if rahu_house == 12:
        risk_factors.append("Rahu in 12th house → long-term incarceration signature")
        imprisonment_risk = True

    return {
        "litigation_risk": len(risk_factors) > 0,
        "imprisonment_risk": imprisonment_risk,
        "risk_factors": risk_factors,
    }


def check_travel_relocation(
    third_lord_house: int,
    ninth_lord_house: int,
    twelfth_lord_house: int,
    ninth_twelfth_parivartana: bool = False,
    rahu_house: int = 0,
) -> Dict[str, Any]:
    """
    Travel/Relocation from Phala Jyotish:
    - 9th-12th Parivartana → confirmed permanent foreign relocation
    - Rahu activating 12th → foreign settlement
    - 3rd lord active → short journeys; 9th → long journeys; 12th → foreign
    """
    indicators: List[str] = []

    if ninth_twelfth_parivartana:
        indicators.append("9th-12th lord Parivartana → permanent foreign relocation confirmed")

    if rahu_house == 12:
        indicators.append("Rahu in 12th house → foreign settlement signature")
    elif rahu_house == 9:
        indicators.append("Rahu in 9th → long-distance foreign travel")

    if twelfth_lord_house == 9 or ninth_lord_house == 12:
        indicators.append("9th/12th lord exchange → strong foreign connection")

    travel_type = "FOREIGN_SETTLEMENT" if ninth_twelfth_parivartana else \
                  ("LONG_TRAVEL" if ninth_lord_house == 12 or rahu_house in (9, 12) else "SHORT_TRAVEL")

    return {
        "travel_type": travel_type,
        "indicators": indicators,
        "foreign_settlement": ninth_twelfth_parivartana or (rahu_house == 12),
    }


def check_competition_success(
    fifth_lord_house: int,
    sixth_lord_house: int,
    malefics_in_sixth: Optional[List[str]] = None,
    benefics_in_sixth: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Competition/Exam Success from Phala Jyotish:
    - Malefics in 6th → aggressive edge to defeat competitors
    - Benefics in 6th → complacency (harmful for competition)
    - Success requires simultaneous 5th (intellect) + 6th (competition) activation
    """
    if malefics_in_sixth is None:
        malefics_in_sixth = []
    if benefics_in_sixth is None:
        benefics_in_sixth = []

    factors: List[str] = []
    competitive_edge = False

    if malefics_in_sixth:
        factors.append(f"Natural malefics in 6th ({', '.join(malefics_in_sixth)}) → aggressive competitive edge")
        competitive_edge = True
    if benefics_in_sixth:
        factors.append(f"Benefics in 6th ({', '.join(benefics_in_sixth)}) → complacency risk, less competitive drive")

    # Dual activation check
    fifth_active = fifth_lord_house in KENDRA or fifth_lord_house in {1, 5, 9}
    sixth_active = sixth_lord_house in UPACHAYA
    dual_activation = fifth_active and sixth_active

    if dual_activation:
        factors.append("5th + 6th house lords activated → exam/competition success indicated")

    success_probability = "HIGH" if competitive_edge and dual_activation else \
                          ("MODERATE" if competitive_edge or dual_activation else "LOW")

    return {
        "competitive_edge": competitive_edge,
        "dual_activation": dual_activation,
        "success_probability": success_probability,
        "factors": factors,
    }


# ════════════════════════════════════════════════════════════════════════════
# 9. JATAKA TATVA – UNIQUE ARISHTA (MORTALITY) YOGAS
# ════════════════════════════════════════════════════════════════════════════

def check_jataka_tatva_arishta(
    moon_house: int,
    moon_hemmed_by_malefics: bool = False,
    twilight_birth: bool = False,
    lunar_hora: bool = False,
    gandantha_malefics: bool = False,
) -> Dict[str, Any]:
    """
    Jataka Tatva unique Arishta (mortality) yogas:
    1. Instant Mortality: Moon in Papakartari in 4th/7th/8th house
    2. Twilight Fatalism: birth at twilight in lunar Hora with
       malefics in Gandantha degrees → uncancelable death yoga
    """
    yogas: List[Dict[str, str]] = []

    # Instant Mortality
    if moon_hemmed_by_malefics and moon_house in (4, 7, 8):
        yogas.append({
            "yoga": "Instant Mortality (Papakartari)",
            "detail": f"Moon hemmed by malefics in H{moon_house} → immediate infant mortality (overrides standard benefic aspects)",
            "severity": "FATAL",
        })

    # Twilight Fatalism
    if twilight_birth and lunar_hora and gandantha_malefics:
        yogas.append({
            "yoga": "Twilight Fatalism",
            "detail": "Birth at twilight in lunar Hora with Gandantha malefics → absolute uncancelable death yoga",
            "severity": "FATAL",
        })

    return {
        "arishta_yogas": yogas,
        "fatal_count": len(yogas),
        "any_fatal": len(yogas) > 0,
    }
