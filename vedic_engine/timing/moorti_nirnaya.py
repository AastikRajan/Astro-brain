"""
Moorti Nirnaya and Paya helpers.

This module centralizes the classical Gold/Silver/Copper/Iron transit quality
mapping so transit analysis can reuse one authoritative implementation.
"""
from __future__ import annotations

from typing import Dict, Tuple


# House from Moon -> (Paya metal, descriptive interpretation)
_PAYA_MAP: Dict[int, Tuple[str, str]] = {
    1: ("Gold", "Very Auspicious - transit carries hidden blessings"),
    6: ("Gold", "Very Auspicious - transit carries hidden blessings"),
    11: ("Gold", "Very Auspicious - transit carries hidden blessings"),
    2: ("Silver", "Auspicious - some hardship with silver lining"),
    5: ("Silver", "Auspicious - some hardship with silver lining"),
    9: ("Silver", "Auspicious - some hardship with silver lining"),
    3: ("Copper", "Average - mixed results, effort required"),
    7: ("Copper", "Average - mixed results, effort required"),
    10: ("Copper", "Average - mixed results, effort required"),
    4: ("Iron", "Difficult - intensified pressure, patience key"),
    8: ("Iron", "Difficult - intensified pressure, patience key"),
    12: ("Iron", "Difficult - intensified pressure, patience key"),
}

_MOORTI_MULTIPLIER = {
    "Gold": 1.00,
    "Silver": 0.75,
    "Copper": 0.50,
    "Iron": 0.25,
}


def compute_paya(house_from_moon: int) -> dict:
    """Return Paya/Moorti classification for a house number from Moon."""
    try:
        house = int(house_from_moon)
    except Exception:
        house = -1

    metal, desc = _PAYA_MAP.get(house, ("Iron", "Unknown"))
    moorti_multiplier = _MOORTI_MULTIPLIER.get(metal, 0.25)

    return {
        "house_from_moon": house,
        "metal": metal,
        "description": desc,
        "moorti": metal,
        "moorti_multiplier": moorti_multiplier,
        "source": "Classical Moorti/Paya mapping",
    }


def compute_moorti_from_signs(transit_sign: int, natal_moon_sign: int) -> dict:
    """Return Paya/Moorti using transit sign and natal Moon sign indices (0-11)."""
    house_from_moon = ((int(transit_sign) - int(natal_moon_sign)) % 12) + 1
    return compute_paya(house_from_moon)


__all__ = ["compute_paya", "compute_moorti_from_signs"]
