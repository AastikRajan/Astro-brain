"""
Panchadha Maitri (5-Fold Compound Friendship) — Vedic Engine
=============================================================
Combines:
  1. Naisargika Maitri (permanent/natural friendship from BPHS)
  2. Tatkalika Maitri  (temporary friendship based on current sign positions)

The compound Panchadha score ranges from -2 to +2:
  Naisargika  Tatkalika  Panchadha          Score
  Friend (+1)  Friend (+1) Adhi Mitra        +2
  Friend (+1)  Enemy  (-1) Sama (Neutral)     0
  Neutral  (0) Friend (+1) Mitra              +1
  Neutral  (0) Enemy  (-1) Shatru             -1
  Enemy   (-1) Friend (+1) Sama (Neutral)      0
  Enemy   (-1) Enemy  (-1) Adhi Shatru        -2

Panchadha labels:
  +2 → Adhi Mitra  (Great Friend)
  +1 → Mitra       (Friend)
   0 → Sama        (Neutral)
  -1 → Shatru      (Enemy)
  -2 → Adhi Shatru (Great Enemy)

This maps directly to Dignity enum used in Saptavargaja Bala:
  +2 → Dignity.GREAT_FRIEND  (22.5 virupas)
  +1 → Dignity.FRIEND        (15.0 virupas)
   0 → Dignity.NEUTRAL       (7.5  virupas)
  -1 → Dignity.ENEMY         (3.75 virupas)
  -2 → Dignity.GREAT_ENEMY   (1.875 virupas)

CRITICAL: Rahu/Ketu friendships use the corrected Moolatrikona-based derivation
(overriding the Santhanam translation error used by most software):
  Rahu  Moolatrikona = Gemini
        Friends  = Moon, Venus, Saturn
        Neutral  = Mercury (rules Gemini → neutralises)
        Enemies  = Sun, Mars, Jupiter

  Ketu  Moolatrikona = Sagittarius
        Friends  = Sun, Moon, Mars
        Neutral  = Jupiter (rules Sagittarius → neutralises)
        Enemies  = Mercury, Venus, Saturn
"""

from __future__ import annotations

from typing import Dict, FrozenSet, Set, Tuple

# ---------------------------------------------------------------------------
# NAISARGIKA MAITRI — permanent/natural relationships (BPHS, corrected)
# ---------------------------------------------------------------------------

# Represented as string planet names to keep this module self-contained
# and avoid circular imports with config.py enums.

_NAISARGIKA_FRIENDS: Dict[str, FrozenSet[str]] = {
    "SUN":     frozenset({"MOON", "MARS", "JUPITER"}),
    "MOON":    frozenset({"SUN", "MERCURY"}),
    "MARS":    frozenset({"SUN", "MOON", "JUPITER"}),
    "MERCURY": frozenset({"SUN", "VENUS"}),
    "JUPITER": frozenset({"SUN", "MOON", "MARS"}),
    "VENUS":   frozenset({"MERCURY", "SATURN"}),
    "SATURN":  frozenset({"MERCURY", "VENUS"}),
    # Corrected Rahu/Ketu (Moolatrikona-based, overrides Santhanam error):
    "RAHU":    frozenset({"MOON", "VENUS", "SATURN"}),
    "KETU":    frozenset({"SUN", "MOON", "MARS"}),
}

_NAISARGIKA_ENEMIES: Dict[str, FrozenSet[str]] = {
    "SUN":     frozenset({"VENUS", "SATURN"}),
    "MOON":    frozenset(),                           # Moon has no natural enemies
    "MARS":    frozenset({"MERCURY"}),
    "MERCURY": frozenset({"MOON"}),
    "JUPITER": frozenset({"MERCURY", "VENUS"}),
    "VENUS":   frozenset({"SUN", "MOON"}),
    "SATURN":  frozenset({"SUN", "MOON", "MARS"}),
    # Corrected Rahu/Ketu:
    "RAHU":    frozenset({"SUN", "MARS", "JUPITER"}),
    "KETU":    frozenset({"MERCURY", "VENUS", "SATURN"}),
}
# Neutrals = all planets not in friends/enemies (excluding self)


def naisargika_relation(planet_a: str, planet_b: str) -> int:
    """
    Return Naisargika relationship of planet_a toward planet_b.

    Returns:
        +1  if planet_b is a natural Friend of planet_a
         0  if planet_b is Neutral to planet_a
        -1  if planet_b is a natural Enemy of planet_a
    """
    a = planet_a.upper()
    b = planet_b.upper()
    if b in _NAISARGIKA_FRIENDS.get(a, frozenset()):
        return 1
    if b in _NAISARGIKA_ENEMIES.get(a, frozenset()):
        return -1
    return 0


# ---------------------------------------------------------------------------
# TATKALIKA MAITRI — temporary relationship based on current sign positions
# ---------------------------------------------------------------------------
# From planet P, count forward: houses {2,3,4,10,11,12} → FRIEND (+1)
# All other positions (same sign=1, 5,6,7,8,9) → ENEMY (-1)
# The relationship is bidirectional: abs difference in {2,3,4,10,11,12} → friend.

_TATKALIKA_FRIEND_DISTANCES: FrozenSet[int] = frozenset({2, 3, 4, 10, 11, 12})


def tatkalika_relation(sign_a: int, sign_b: int) -> int:
    """
    Return Tatkalika (temporary) relationship of the planet in sign_a
    toward the planet in sign_b.

    sign_a, sign_b: 0-based zodiac sign indices (0=Aries … 11=Pisces)

    Returns:
        +1  Friend
        -1  Enemy
    """
    # Forward distance from A to B (1-based count, as in classical houses)
    fwd = ((sign_b - sign_a) % 12) + 1   # ranges 1-12
    if fwd in _TATKALIKA_FRIEND_DISTANCES:
        return 1
    return -1


# ---------------------------------------------------------------------------
# PANCHADHA MAITRI — 5-fold compound
# ---------------------------------------------------------------------------

def panchadha_score(
    planet_a: str,
    sign_a: int,
    planet_b: str,
    sign_b: int,
) -> int:
    """
    Compound Panchadha score of planet_a (in sign_a) toward planet_b (in sign_b).

    Returns integer score: -2 (Adhi Shatru) … +2 (Adhi Mitra)
    """
    n = naisargika_relation(planet_a, planet_b)   # -1, 0, +1
    t = tatkalika_relation(sign_a, sign_b)        # -1 or +1

    raw = n + t   # -2, -1, 0, +1, +2
    return raw

    # Explicit Panchadha table (per classical rules):
    # n=+1, t=+1 → +2  Adhi Mitra
    # n=+1, t=-1 →  0  Sama
    # n= 0, t=+1 → +1  Mitra
    # n= 0, t=-1 → -1  Shatru
    # n=-1, t=+1 →  0  Sama
    # n=-1, t=-1 → -2  Adhi Shatru
    # This matches n+t exactly.


_PANCHADHA_LABELS: Dict[int, str] = {
    2: "Adhi Mitra",    # Great Friend
    1: "Mitra",         # Friend
    0: "Sama",          # Neutral
   -1: "Shatru",        # Enemy
   -2: "Adhi Shatru",   # Great Enemy
}


def panchadha_label(score: int) -> str:
    """Return the classical Panchadha label for a compound score."""
    return _PANCHADHA_LABELS.get(score, "Unknown")


def compute_all_panchadha(
    planet_signs: Dict[str, int],
) -> Dict[str, Dict[str, int]]:
    """
    Compute the full Panchadha Maitri relationship matrix for all given planets.

    Args:
        planet_signs: dict of {planet_name: sign_index (0-11)}

    Returns:
        Nested dict: {planet_a: {planet_b: panchadha_score, ...}, ...}
        Note: the relationship is NOT necessarily symmetric.
    """
    planets = list(planet_signs.keys())
    result: Dict[str, Dict[str, int]] = {}
    for pa in planets:
        result[pa] = {}
        sa = planet_signs[pa]
        for pb in planets:
            if pa == pb:
                continue
            sb = planet_signs[pb]
            result[pa][pb] = panchadha_score(pa, sa, pb, sb)
    return result


# ---------------------------------------------------------------------------
# DIGNITY MAPPING — for use in Saptavargaja Bala
# ---------------------------------------------------------------------------
# Imports Dignity only at call-time to avoid circular dependency concerns.

def panchadha_to_dignity(score: int):
    """
    Convert a Panchadha compound score to a Dignity enum value.

    Used by Saptavargaja Bala to properly classify a planet's relationship
    with the sign lord using the 5-fold compound system.

    Returns a Dignity enum member from vedic_engine.config.
    """
    from vedic_engine.config import Dignity
    mapping = {
        2: Dignity.GREAT_FRIEND,
        1: Dignity.FRIEND,
        0: Dignity.NEUTRAL,
       -1: Dignity.ENEMY,
       -2: Dignity.GREAT_ENEMY,
    }
    return mapping.get(score, Dignity.NEUTRAL)


def get_panchadha_dignity(
    planet: str,
    planet_sign: int,
    sign_lord: str,
    sign_lord_sign: int,
):
    """
    Get the Dignity of `planet` relative to `sign_lord` using Panchadha Maitri.

    This replaces the Naisargika-only friendship lookup in Saptavargaja Bala
    with the full 5-fold compound method.

    Args:
        planet:          planet name (e.g. "SUN")
        planet_sign:     sign index of planet (0-11) for Tatkalika computation
        sign_lord:       name of the sign's ruling planet
        sign_lord_sign:  sign index of the sign lord (0-11)

    Returns:
        Dignity enum member
    """
    score = panchadha_score(planet, planet_sign, sign_lord, sign_lord_sign)
    return panchadha_to_dignity(score)


# ---------------------------------------------------------------------------
# CONVENIENCE — summary report
# ---------------------------------------------------------------------------

def panchadha_summary(planet_signs: Dict[str, int]) -> Dict[str, Dict[str, str]]:
    """
    Return the full Panchadha matrix with human-readable labels.

    Returns:
        {planet_a: {planet_b: "Adhi Mitra"|"Mitra"|"Sama"|"Shatru"|"Adhi Shatru"}}
    """
    matrix = compute_all_panchadha(planet_signs)
    return {
        pa: {pb: panchadha_label(score) for pb, score in pb_dict.items()}
        for pa, pb_dict in matrix.items()
    }
