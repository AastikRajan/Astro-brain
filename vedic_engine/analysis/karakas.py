"""
Jaimini Karaka Engine.
Computes Chara Karakas (variable significators) from planet degrees.

Algorithm (from astrology_system_analysis.md):
  Take the degree within sign (ignoring sign, only the degree 0-30°) for
  each of the 7 classical planets. Rank in DESCENDING order.
  1st = Atma Karaka (AK), 2nd = Amatya Karaka (AmK), etc.

  For Rahu, use (30 - degree_in_sign) because Rahu moves retrograde.

Karaka roles and life domains:
  AK  = Atma Karaka      → Soul, self, primary life direction, king
  AmK = Amatya Karaka    → Career, profession, ministers
  BK  = Bhratri Karaka   → Siblings, courage, communication
  MK  = Matri Karaka     → Mother, nourishment, homeland
  PK  = Putra Karaka     → Children, creativity, intelligence
  GK  = Gnati Karaka     → Enemies, obstacles, conflict, relatives
  DK  = Dara Karaka      → Spouse, marriage, partnerships
"""
from __future__ import annotations
from typing import Dict, List, Tuple
from vedic_engine.core.coordinates import degree_in_sign


KARAKA_ROLES = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
KARAKA_NAMES = [
    "Atma Karaka",
    "Amatya Karaka",
    "Bhratri Karaka",
    "Matri Karaka",
    "Putra Karaka",
    "Gnati Karaka",
    "Dara Karaka",
]
KARAKA_SIGNIFIES = [
    "Soul, self, primary life purpose, king of the chart",
    "Career, profession, ministers, how you earn",
    "Siblings, courage, communication, short journeys",
    "Mother, education, property, emotional nourishment",
    "Children, creativity, romance, intellect, speculation",
    "Enemies, obstacles, feuds, conflict, illness, transformation",
    "Spouse, marriage, business partnerships, legal matters",
]

PLANET_NAMES_7 = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]


def compute_chara_karakas(
        planet_lons: Dict[str, float],
        include_rahu: bool = False,
) -> List[Dict]:
    """
    Compute and rank Jaimini Chara Karakas.

    Returns list of 7 dicts (one per karaka role) in order AK → DK.
    Each dict: {role, role_name, planet, degree, signifies}
    """
    degrees: List[Tuple[str, float]] = []

    for pname in PLANET_NAMES_7:
        lon = planet_lons.get(pname)
        if lon is None:
            continue
        deg = degree_in_sign(lon)
        degrees.append((pname, deg))

    if include_rahu:
        rahu_lon = planet_lons.get("RAHU")
        if rahu_lon is not None:
            # Rahu retrograde: effective degree = 30 - degree_in_sign
            rahu_deg = 30.0 - degree_in_sign(rahu_lon)
            degrees.append(("RAHU", rahu_deg))

    # Sort DESCENDING by degree within sign
    degrees.sort(key=lambda x: x[1], reverse=True)

    karakas = []
    for i, (pname, deg) in enumerate(degrees[:7]):
        karakas.append({
            "rank": i + 1,
            "role": KARAKA_ROLES[i],
            "role_name": KARAKA_NAMES[i],
            "planet": pname,
            "degree": round(deg, 3),
            "signifies": KARAKA_SIGNIFIES[i],
        })

    return karakas


def get_atma_karaka(planet_lons: Dict[str, float]) -> str:
    """Quick accessor: return the Atma Karaka planet name."""
    karakas = compute_chara_karakas(planet_lons)
    return karakas[0]["planet"] if karakas else ""


def get_amatya_karaka(planet_lons: Dict[str, float]) -> str:
    """Quick accessor: return the Amatya Karaka (career) planet name."""
    karakas = compute_chara_karakas(planet_lons)
    return karakas[1]["planet"] if len(karakas) > 1 else ""


def analyze_karaka_relationships(
        karakas: List[Dict],
        planet_houses: Dict[str, int],
        shadbala_ratios: Dict[str, float],
) -> Dict:
    """
    Analyze key Jaimini relationships:
    - AK-AmK relationship (house distance) → career vs soul alignment
    - AK's house → primary life domain
    - AmK's strength → career prospects
    """
    if len(karakas) < 2:
        return {}

    ak = karakas[0]
    amk = karakas[1]

    ak_house = planet_houses.get(ak["planet"], 0)
    amk_house = planet_houses.get(amk["planet"], 0)

    # House relationship between AK and AmK
    if ak_house and amk_house:
        ak_amk_distance = ((amk_house - ak_house) % 12) + 1
    else:
        ak_amk_distance = 0

    ak_strength = shadbala_ratios.get(ak["planet"], 0.5)
    amk_strength = shadbala_ratios.get(amk["planet"], 0.5)

    # Interpret AK-AmK relationship
    relationship_interpretation = {
        2: "2-11 Dhana axis (AK-AmK): wealth through career, money and gains connected",
        6: "6-9 Dharma-Karma: career aligned with service and dharma (opposite: 6-9 tension)",
        10: "AK-AmK in 10-4 axis: career and home/family strongly linked",
        5: "5-10 axis: creativity drives career",
        9: "9-2 dharma-wealth link",
        1: "Same house: soul and career fully aligned",
        7: "7-1 axis: partnerships critical to career",
    }.get(ak_amk_distance, f"House {ak_amk_distance} apart")

    return {
        "atma_karaka": ak,
        "amatya_karaka": amk,
        "ak_house": ak_house,
        "amk_house": amk_house,
        "ak_amk_distance": ak_amk_distance,
        "ak_amk_relationship": relationship_interpretation,
        "ak_strength": ak_strength,
        "amk_strength": amk_strength,
        "career_note": (
            "Strong career potential" if amk_strength >= 1.0
            else "Career requires effort / Saturn-like discipline"
        ),
        "soul_note": (
            "Soul planet strong → clear life purpose" if ak_strength >= 1.0
            else "Soul planet weak → identity/purpose exploration needed"
        ),
        "all_karakas": karakas,
    }
