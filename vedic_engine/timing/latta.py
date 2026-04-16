"""
Latta (planetary kick) star helpers.

This module mirrors the reference Latta constants and cyclic-star counting
algorithm used in the local pyjhora reference implementation.
"""
from __future__ import annotations

from typing import Dict, Tuple

from vedic_engine.config import NAKSHATRA_NAMES
from vedic_engine.core.coordinates import nakshatra_of


# Reference order: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu.
# Tuple format: (nth star distance, direction) where direction is +1/-1.
LATTA_STARS_OF_PLANETS: Dict[str, Tuple[int, int]] = {
    "SUN": (12, 1),
    "MOON": (22, -1),
    "MARS": (3, 1),
    "MERCURY": (7, -1),
    "JUPITER": (6, 1),
    "VENUS": (5, -1),
    "SATURN": (8, 1),
    "RAHU": (9, -1),
    "KETU": (9, -1),
}

PLANET_ORDER = (
    "SUN",
    "MOON",
    "MARS",
    "MERCURY",
    "JUPITER",
    "VENUS",
    "SATURN",
    "RAHU",
    "KETU",
)

# 28-star sequence with Abhijit inserted between Uttarashadha and Shravana.
NAKSHATRA_NAMES_28 = [*NAKSHATRA_NAMES[:21], "Abhijit", *NAKSHATRA_NAMES[21:]]


def _cyclic_count_of_stars_with_abhijit(
    from_star: int,
    count: int,
    direction: int = 1,
    star_count: int = 28,
) -> int:
    """Reference-equivalent cyclic counting over 27 or 28 stars (1-indexed)."""
    return ((int(from_star) - 1 + (int(count) - 1) * int(direction)) % int(star_count)) + 1


def _normalize_star_27(star_number: int) -> int:
    """Normalize to 1..27 (source stars are classical 27-nakshatra indices)."""
    return ((int(star_number) - 1) % 27) + 1


def compute_latta_star(
    planet: str,
    source_star: int,
    include_abhijit: bool = True,
) -> dict:
    """
    Compute Latta star for one planet.

    Notes:
      - source_star uses the standard 27-nakshatra numbering (1..27).
      - when include_abhijit=True, the target Latta star is computed on a 28-star
        cycle with Abhijit inserted at position 22.
    """
    p = str(planet).upper()
    if p not in LATTA_STARS_OF_PLANETS:
        return {
            "planet": p,
            "available": False,
            "reason": "unsupported_planet",
        }

    source_star_27 = _normalize_star_27(source_star)
    star_count = 28 if include_abhijit else 27
    count, direction = LATTA_STARS_OF_PLANETS[p]

    latta_star = _cyclic_count_of_stars_with_abhijit(
        source_star_27,
        count,
        direction,
        star_count,
    )

    latta_name_list = NAKSHATRA_NAMES_28 if include_abhijit else NAKSHATRA_NAMES

    return {
        "planet": p,
        "available": True,
        "source_star": source_star_27,
        "source_star_name": NAKSHATRA_NAMES[source_star_27 - 1],
        "latta_star": latta_star,
        "latta_star_name": latta_name_list[latta_star - 1],
        "distance": count,
        "direction": direction,
        "direction_label": "forward" if direction > 0 else "backward",
        "include_abhijit": bool(include_abhijit),
        "star_count": star_count,
        "source": "pyjhora const.latta_stars_of_planets + cyclic_count_of_stars_with_abhijit",
    }


def compute_latta_from_nakshatra_map(
    planet_stars: Dict[str, int],
    include_abhijit: bool = True,
) -> Dict[str, dict]:
    """Compute Latta stars from {planet: source_star_1_to_27} input."""
    out: Dict[str, dict] = {}
    for planet in PLANET_ORDER:
        if planet not in planet_stars:
            continue
        out[planet] = compute_latta_star(
            planet=planet,
            source_star=int(planet_stars[planet]),
            include_abhijit=include_abhijit,
        )
    return out


def compute_latta_from_longitudes(
    planet_longitudes: Dict[str, float],
    include_abhijit: bool = True,
) -> Dict[str, dict]:
    """Compute Latta stars from {planet: sidereal_longitude_degrees} input."""
    planet_stars: Dict[str, int] = {}
    for planet in PLANET_ORDER:
        if planet not in planet_longitudes:
            continue
        lon = planet_longitudes[planet]
        if not isinstance(lon, (int, float)):
            continue
        planet_stars[planet] = nakshatra_of(float(lon)) + 1
    return compute_latta_from_nakshatra_map(planet_stars, include_abhijit=include_abhijit)


__all__ = [
    "LATTA_STARS_OF_PLANETS",
    "PLANET_ORDER",
    "NAKSHATRA_NAMES_28",
    "compute_latta_star",
    "compute_latta_from_nakshatra_map",
    "compute_latta_from_longitudes",
]