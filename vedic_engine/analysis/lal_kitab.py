"""
Lal Kitab — Red Book Remedial Astrology.

Core concepts implemented:
  1. Sleeping (Dormant) Planets: planet whose 7th house is empty
  2. Karmic Debts (Rin): Pitru, Swa, Matru, Stree Rin detection
  3. Progressive Varshkundli: each planet shifts 1 house forward per year

Reference: Lal Kitab (Pandit Roop Chand Joshi, 1939-1952 editions).
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional


# ── Rin Definitions ────────────────────────────────────────────
# Karmic debts detected by specific planetary placements.
RIN_DEFINITIONS = {
    "PITRU_RIN": {
        "name": "Pitru Rin (Ancestral Debt)",
        "description": "9th sector afflicted or Jupiter afflicted — debt to father / ancestors",
        "conditions": [
            "9th_house_afflicted",
            "jupiter_afflicted",
        ],
    },
    "SWA_RIN": {
        "name": "Swa Rin (Self Debt)",
        "description": "Venus placed in 5th house — debt from own past karmas",
        "conditions": [
            "venus_in_5th",
        ],
    },
    "MATRU_RIN": {
        "name": "Matru Rin (Maternal Debt)",
        "description": "Ketu placed in 4th house — debt to mother",
        "conditions": [
            "ketu_in_4th",
        ],
    },
    "STREE_RIN": {
        "name": "Stree Rin (Spouse Debt)",
        "description": "Sun, Rahu, or Ketu in 2nd house — debt to wife/women",
        "conditions": [
            "sun_in_2nd",
            "rahu_in_2nd",
            "ketu_in_2nd",
        ],
    },
}

# Malefic planets for affliction checks
NATURAL_MALEFICS = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}


def detect_sleeping_planets(planet_houses: Dict[str, int]) -> Dict[str, Any]:
    """
    Detect sleeping (dormant) planets per Lal Kitab.

    A planet is 'sleeping' if the 7th house from it is empty
    (no planet occupies that house).

    Args:
        planet_houses: dict mapping planet name → house (1-12)
            e.g. {"SUN": 1, "MOON": 4, "MARS": 7, ...}

    Returns:
        Dict with list of sleeping planets and their details.
    """
    # Build occupancy map: house → list of planets
    house_occupants: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
    for planet, house in planet_houses.items():
        h = ((house - 1) % 12) + 1
        house_occupants[h].append(planet)

    sleeping = []
    active = []
    for planet, house in planet_houses.items():
        h = ((house - 1) % 12) + 1
        seventh_from = ((h - 1 + 6) % 12) + 1  # 7th house from planet's position
        if not house_occupants[seventh_from]:
            sleeping.append({
                "planet": planet,
                "house": h,
                "seventh_house": seventh_from,
                "status": "SLEEPING",
                "effect": f"{planet} is dormant — its significations are weakened; remedies needed to activate",
            })
        else:
            active.append({
                "planet": planet,
                "house": h,
                "seventh_house": seventh_from,
                "status": "ACTIVE",
                "awakened_by": house_occupants[seventh_from],
            })

    return {
        "sleeping_planets": sleeping,
        "active_planets": active,
        "sleeping_count": len(sleeping),
        "active_count": len(active),
    }


def detect_karmic_debts(
    planet_houses: Dict[str, int],
    aspecting_planets: Optional[Dict[int, List[str]]] = None,
) -> Dict[str, Any]:
    """
    Detect Lal Kitab Karmic Debts (Rin).

    Conditions:
      - Pitru Rin: 9th house has malefic(s) / Jupiter afflicted by malefic aspect
      - Swa Rin: Venus in 5th house
      - Matru Rin: Ketu in 4th house
      - Stree Rin: Sun/Rahu/Ketu in 2nd house

    Args:
        planet_houses: planet → house (1-12)
        aspecting_planets: house → list of planets aspecting that house (optional,
            for affliction checks)

    Returns:
        Dict with detected debts and remedial notes.
    """
    detected_rins: List[Dict[str, Any]] = []

    # Helper: planets in a given house
    def planets_in(h: int) -> List[str]:
        return [p for p, ph in planet_houses.items() if ((ph - 1) % 12) + 1 == h]

    # Helper: house has malefic
    def house_has_malefic(h: int) -> bool:
        return any(p in NATURAL_MALEFICS for p in planets_in(h))

    # 1. Pitru Rin: 9th house afflicted or Jupiter afflicted
    ninth_afflicted = house_has_malefic(9)
    jupiter_house = planet_houses.get("JUPITER", planet_houses.get("JU", None))
    jupiter_afflicted = False
    if jupiter_house is not None and aspecting_planets:
        jh = ((jupiter_house - 1) % 12) + 1
        aspectors = aspecting_planets.get(jh, [])
        jupiter_afflicted = any(p in NATURAL_MALEFICS for p in aspectors)

    if ninth_afflicted or jupiter_afflicted:
        detected_rins.append({
            "rin": "PITRU_RIN",
            **RIN_DEFINITIONS["PITRU_RIN"],
            "triggered_by": {
                "ninth_afflicted": ninth_afflicted,
                "jupiter_afflicted": jupiter_afflicted,
            },
            "remedy": "Serve father/elders, donate to old age homes, water offerings to ancestors",
        })

    # 2. Swa Rin: Venus in 5th
    venus_house = planet_houses.get("VENUS", planet_houses.get("VE", None))
    if venus_house is not None and ((venus_house - 1) % 12) + 1 == 5:
        detected_rins.append({
            "rin": "SWA_RIN",
            **RIN_DEFINITIONS["SWA_RIN"],
            "triggered_by": {"venus_in_5th": True},
            "remedy": "Charitable acts for women/children, donate sweets on Fridays",
        })

    # 3. Matru Rin: Ketu in 4th
    ketu_house = planet_houses.get("KETU", planet_houses.get("KE", None))
    if ketu_house is not None and ((ketu_house - 1) % 12) + 1 == 4:
        detected_rins.append({
            "rin": "MATRU_RIN",
            **RIN_DEFINITIONS["MATRU_RIN"],
            "triggered_by": {"ketu_in_4th": True},
            "remedy": "Serve mother, donate milk/white items on Mondays",
        })

    # 4. Stree Rin: Sun/Rahu/Ketu in 2nd
    stree_triggers = {}
    for pname in ["SUN", "SU", "RAHU", "RA", "KETU", "KE"]:
        ph = planet_houses.get(pname, None)
        if ph is not None and ((ph - 1) % 12) + 1 == 2:
            canonical = pname[:2].upper()
            if canonical == "SU":
                canonical = "SUN"
            elif canonical == "RA":
                canonical = "RAHU"
            elif canonical == "KE":
                canonical = "KETU"
            stree_triggers[f"{canonical.lower()}_in_2nd"] = True

    if stree_triggers:
        detected_rins.append({
            "rin": "STREE_RIN",
            **RIN_DEFINITIONS["STREE_RIN"],
            "triggered_by": stree_triggers,
            "remedy": "Respect wife/women, donate to women's charities, avoid harshness",
        })

    return {
        "detected_rins": detected_rins,
        "rin_count": len(detected_rins),
        "has_karmic_debt": len(detected_rins) > 0,
        "rin_names": [r["rin"] for r in detected_rins],
    }


def compute_lalkitab_varshphal(
    natal_planet_houses: Dict[str, int],
    age: int,
) -> Dict[str, Any]:
    """
    Lal Kitab Progressive Varshkundli (Annual Chart).

    Each planet shifts 1 house forward per year of age.
    New_house = ((natal_house - 1 + age) % 12) + 1

    Args:
        natal_planet_houses: planet → natal house (1-12)
        age: completed years of age

    Returns:
        Dict with original and progressed house positions.
    """
    progressed: Dict[str, Dict[str, Any]] = {}

    for planet, natal_house in natal_planet_houses.items():
        nh = ((natal_house - 1) % 12) + 1
        new_house = ((nh - 1 + age) % 12) + 1
        houses_moved = age % 12

        progressed[planet] = {
            "natal_house": nh,
            "progressed_house": new_house,
            "houses_moved": houses_moved,
            "same_as_natal": (new_house == nh),
        }

    return {
        "age": age,
        "natal_positions": {p: ((h - 1) % 12) + 1 for p, h in natal_planet_houses.items()},
        "progressed_positions": {p: v["progressed_house"] for p, v in progressed.items()},
        "progression_details": progressed,
        "cycle_complete": (age % 12 == 0),
        "note": f"At age {age}, each planet has advanced {age % 12} houses from natal position",
    }


def compute_all_lalkitab(
    planet_houses: Dict[str, int],
    age: int = 0,
    aspecting_planets: Optional[Dict[int, List[str]]] = None,
) -> Dict[str, Any]:
    """
    Comprehensive Lal Kitab analysis: sleeping planets, karmic debts, annual chart.

    Args:
        planet_houses: planet → house (1-12)
        age: completed years (for progressive varshkundli)
        aspecting_planets: house → aspecting planets (optional)

    Returns:
        Combined analysis dict.
    """
    sleeping = detect_sleeping_planets(planet_houses)
    debts = detect_karmic_debts(planet_houses, aspecting_planets)
    annual = compute_lalkitab_varshphal(planet_houses, age) if age > 0 else None

    return {
        "sleeping_analysis": sleeping,
        "karmic_debts": debts,
        "annual_chart": annual,
        "summary": {
            "sleeping_count": sleeping["sleeping_count"],
            "rin_count": debts["rin_count"],
            "has_debt": debts["has_karmic_debt"],
            "notable": (
                sleeping["sleeping_count"] >= 3 or debts["rin_count"] >= 2
            ),
        },
    }
