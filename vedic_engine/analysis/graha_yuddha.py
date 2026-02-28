"""
Graha Yuddha (Planetary War).

When two visible planets (Mars, Mercury, Jupiter, Venus, Saturn) occupy
the same ecliptic longitude within 1°, they enter a war.

Rules (BPHS / Phaladeepika):
  - Planet with HIGHER natural strength (Naisargika Bala) wins.
  - Winner's strength is enhanced; loser suffers significant weakness.
  - Sun and Moon never fight; Rahu/Ketu never fight.
  - A planet in war with a benefic and losing → acts as a malefic.

Strength penalty applied to loser's Shadbala ratio:
  - Exact conjunction → 50% penalty
  - 1° apart → no penalty (boundary)
  - Linear interpolation in between.

Reference: BPHS Ch. 3 (Graha Yuddha Adhyaya)
"""
from __future__ import annotations
from typing import Dict, List, Tuple

from vedic_engine.config import Planet, NAISARGIKA_BALA
from vedic_engine.core.coordinates import angular_distance

# Only these planets can go to war (not Sun/Moon/Rahu/Ketu)
WAR_PLANETS = ["MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]

# Natural strength hierarchy (same as Naisargika Bala) for winner determination
_NAT_STRENGTH: Dict[str, float] = {
    "SUN": 60.0, "MOON": 51.43, "VENUS": 42.86, "JUPITER": 34.29,
    "MERCURY": 25.71, "MARS": 17.14, "SATURN": 8.57,
}

WAR_ORB_DEG = 1.0   # degrees within which a war is declared


def detect_planetary_wars(planet_lons: Dict[str, float]) -> List[Dict]:
    """
    Identify all active planetary wars in a chart.

    For each pair of war-eligible planets within WAR_ORB_DEG, determine:
      - winner  (higher Naisargika order)
      - loser   (weaker by Naisargika order)
      - strength_penalty to loser (0.0 – 0.5 fraction of Shadbala)

    Returns list of dicts, one per war pair.
    """
    candidates = [p for p in WAR_PLANETS if p in planet_lons]
    wars = []
    for i, p1 in enumerate(candidates):
        for p2 in candidates[i + 1:]:
            sep = angular_distance(planet_lons[p1], planet_lons[p2])
            if sep > WAR_ORB_DEG:
                continue

            s1 = _NAT_STRENGTH.get(p1, 0.0)
            s2 = _NAT_STRENGTH.get(p2, 0.0)
            winner, loser = (p1, p2) if s1 >= s2 else (p2, p1)

            # Penalty scales from 0 (at 1°) to 0.50 (exact conjunction)
            penalty = (WAR_ORB_DEG - sep) / WAR_ORB_DEG * 0.50

            wars.append({
                "p1":              p1,
                "p2":              p2,
                "separation_deg":  round(sep, 4),
                "winner":          winner,
                "loser":           loser,
                "strength_penalty": round(penalty, 3),
                "description":     (
                    f"{p1} and {p2} in planetary war (sep={sep:.2f}°). "
                    f"{winner} wins; {loser} weakened by "
                    f"{penalty:.0%}."
                ),
            })
    return wars


def apply_war_penalties(
        shadbala_ratios: Dict[str, float],
        wars: List[Dict],
) -> Dict[str, float]:
    """
    Return adjusted Shadbala ratios after applying war penalties.

    Loser's ratio is reduced by penalty fraction.
    Winner's ratio receives a 5% boost (capped at 2.0).
    """
    adjusted = {k: v for k, v in shadbala_ratios.items()}
    for war in wars:
        loser  = war["loser"]
        winner = war["winner"]
        penalty = war["strength_penalty"]
        if loser  in adjusted:
            adjusted[loser]  = round(adjusted[loser]  * (1.0 - penalty), 3)
        if winner in adjusted:
            adjusted[winner] = round(min(adjusted[winner] * 1.05, 2.0), 3)
    return adjusted


def war_summary(wars: List[Dict]) -> str:
    """Human-readable summary of active wars."""
    if not wars:
        return "No planetary wars."
    return "; ".join(w["description"] for w in wars)
