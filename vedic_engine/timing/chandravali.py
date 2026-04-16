"""
Chandravali (daily Moon transit effect) helpers.

This module centralizes Moon-from-Moon daily favorability logic used in transit
evaluation. It preserves the existing engine scoring profile and also exposes a
pyjhora-aligned muhurta profile.
"""
from __future__ import annotations

from typing import Dict, FrozenSet


# Existing engine transit profile (kept behavior-compatible).
CHANDRAVALI_TRANSIT_GOOD_HOUSES: FrozenSet[int] = frozenset({1, 3, 6, 7, 10, 11})

# pyjhora drik.chandrabalam profile (good houses list there is 1,3,6,7,10).
CHANDRAVALI_MUHURTA_GOOD_HOUSES: FrozenSet[int] = frozenset({1, 3, 6, 7, 10})


def _house_from_natal_moon(natal_moon_sign: int, transit_moon_sign: int) -> int:
    """Return 1-12 house count from natal Moon sign to transit Moon sign."""
    return ((int(transit_moon_sign) - int(natal_moon_sign)) % 12) + 1


def compute_chandravali(
    natal_moon_sign: int,
    transit_moon_sign: int,
    profile: str = "transit",
) -> Dict:
    """
    Compute Chandravali/Chandrabala quality for transit Moon.

    Profiles:
      - transit: preserves existing engine behavior
      - muhurta: pyjhora-style day filter profile
    """
    profile_norm = str(profile).strip().lower()
    house_from_moon = _house_from_natal_moon(natal_moon_sign, transit_moon_sign)

    if profile_norm == "muhurta":
        good_houses = CHANDRAVALI_MUHURTA_GOOD_HOUSES
        is_good = house_from_moon in good_houses
        score = 1.0 if is_good else 0.0
        source = "pyjhora drik.chandrabalam house filter"
    else:
        good_houses = CHANDRAVALI_TRANSIT_GOOD_HOUSES
        is_good = house_from_moon in good_houses
        score = 0.75 if is_good else 0.25
        source = "existing transit Chandrabala profile"

    return {
        "house_from_natal_moon": house_from_moon,
        "is_good": is_good,
        "score": score,
        "profile": profile_norm,
        "source": source,
    }


__all__ = [
    "CHANDRAVALI_TRANSIT_GOOD_HOUSES",
    "CHANDRAVALI_MUHURTA_GOOD_HOUSES",
    "compute_chandravali",
]