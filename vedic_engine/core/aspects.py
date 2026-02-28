"""
Aspect (Drishti) calculation engine.
Implements BPHS piecewise aspect strengths for all 7 classical planets.

From deep-research-report.md:
  All planets: full aspect on 7th house (60 shashtiamsas)
  Mars special: 4th (45) and 8th (45)
  Jupiter special: 5th (30) and 9th (30)
  Saturn special: 3rd (15) and 10th (15)

Drik Bala = Σ(benefic aspect strengths) - Σ(malefic aspect strengths)
  on the aspected planet/point.
"""
from __future__ import annotations
from typing import Dict, List, Tuple

from vedic_engine.config import (
    Planet, SPECIAL_ASPECTS, ASPECT_STRENGTHS,
    NATURAL_BENEFICS, NATURAL_MALEFICS
)

PLANET_NAMES_7 = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]


def houses_aspected(aspector_house: int, planet: Planet) -> Dict[int, float]:
    """
    Returns {house_number: strength} for all houses aspected by this planet.
    aspector_house: 1-12, the house the planet occupies.
    """
    aspects = {}
    # Standard 7th house full aspect
    target_7 = (aspector_house + 6 - 1) % 12 + 1
    aspects[target_7] = ASPECT_STRENGTHS[7]

    # Special aspects
    for house_offset in SPECIAL_ASPECTS.get(planet, []):
        t = (aspector_house + house_offset - 1 - 1) % 12 + 1
        aspects[t] = ASPECT_STRENGTHS[house_offset]

    return aspects


def planet_aspects_planet(
        aspector: str, aspector_house: int,
        aspected: str, aspected_house: int,
        planet_enum: Planet
) -> float:
    """
    Returns the aspect strength (shashtiamsas) of `aspector` on `aspected`,
    or 0 if no aspect exists.
    """
    aspected_aspects = houses_aspected(aspector_house, planet_enum)
    return aspected_aspects.get(aspected_house, 0.0)


def compute_drik_bala(
        target_planet: str,
        target_house: int,
        planet_houses: Dict[str, int],
        moon_waxing: bool = True,
) -> float:
    """
    Compute Drik Bala (aspectual strength) for a target planet.

    Formula (BPHS):
      Drik Bala = Σ(aspect_strength × ½) for benefic aspectors
                − Σ(aspect_strength × ½) for malefic aspectors

    Moon is treated as benefic when waxing, malefic when waning.
    Mercury is benefic unless with malefics (simplified: treat as benefic here).
    """
    total = 0.0
    for pname, p_house in planet_houses.items():
        if pname == target_planet:
            continue
        p_enum = _get_planet_enum(pname)
        if p_enum is None:
            continue
        strength = planet_aspects_planet(pname, p_house, target_planet, target_house, p_enum)
        if strength == 0:
            continue
        # Scale: aspect strength is in 0-60 scale, Drik Bala uses ¼ of full
        scaled = strength / 4.0
        if _is_benefic(p_enum, moon_waxing):
            total += scaled
        else:
            total -= scaled
    return total


def compute_all_drik_bala(
        planet_houses: Dict[str, int],
        moon_waxing: bool = True,
) -> Dict[str, float]:
    """Compute Drik Bala for all 7 classical planets."""
    results = {}
    for pname in PLANET_NAMES_7:
        if pname not in planet_houses:
            continue
        results[pname] = compute_drik_bala(
            pname, planet_houses[pname], planet_houses, moon_waxing
        )
    return results


def get_aspect_map(planet_houses: Dict[str, int]) -> Dict[Tuple[str, str], float]:
    """
    Returns a matrix of {(aspector, aspected): strength_shashtiamsas}
    for all planet pairs where an aspect exists.
    """
    result = {}
    for pname, p_house in planet_houses.items():
        p_enum = _get_planet_enum(pname)
        if p_enum is None:
            continue
        aspected = houses_aspected(p_house, p_enum)
        for target_pname, target_house in planet_houses.items():
            if target_pname == pname:
                continue
            s = aspected.get(target_house, 0)
            if s > 0:
                result[(pname, target_pname)] = s
    return result


def _is_benefic(planet: Planet, moon_waxing: bool = True) -> bool:
    if planet == Planet.MOON:
        return moon_waxing
    return planet in NATURAL_BENEFICS


def _get_planet_enum(name: str):
    mapping = {
        "SUN": Planet.SUN, "MOON": Planet.MOON, "MARS": Planet.MARS,
        "MERCURY": Planet.MERCURY, "JUPITER": Planet.JUPITER,
        "VENUS": Planet.VENUS, "SATURN": Planet.SATURN,
    }
    return mapping.get(name.upper())
