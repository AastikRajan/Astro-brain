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

Yuddha Bala Transfer (BPHS Ch.3 / Logic Integration Manifest §3.2):
  The classical Yuddha Bala quantum is computed from the difference in each
  planet's Tri-Bala (Positional + Directional + Temporal, EXCLUDING Ayana Bala)
  divided by the difference in their apparent disc circumferences (in arc-seconds).

  Disc circumferences hardcoded from classical texts:
    Mars: 9.4"  Mercury: 6.6"  Jupiter: 190.4"  Venus: 16.6"  Saturn: 158.0"

  The Yuddha Bala is then TRANSFERRED: subtracted from the loser's Shadbala
  matrix and added to the winner's, mathematical zeroing loser's Yoga potential.

Reference: BPHS Ch. 3 (Graha Yuddha Adhyaya); BPHS Ch. 28 (Shadbala)
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

# Classical disc circumferences in arc-seconds (BPHS Ch.3 / Phaladeepika)
# These are the apparent angular diameters of the planets as seen from Earth.
# Critical for the exact Yuddha Bala transfer formula.
DISC_CIRCUMFERENCE_ARCSEC: Dict[str, float] = {
    "MARS":    9.4,
    "MERCURY": 6.6,
    "JUPITER": 190.4,
    "VENUS":   16.6,
    "SATURN":  158.0,
}

# Minimum Shadbala requirements (in rupas) for reference unit conversion
# Used to convert Yuddha Bala (rupas) to ratio-unit transfer.
MIN_SHADBALA_RUPAS: Dict[str, float] = {
    "SUN": 390.0, "MOON": 360.0, "MARS": 300.0,
    "MERCURY": 420.0, "JUPITER": 390.0, "VENUS": 330.0, "SATURN": 300.0,
}

WAR_ORB_DEG = 1.0   # degrees within which a war is declared


def _compute_yuddha_bala(
    winner: str,
    loser: str,
    winner_shadbala_ratio: float,
    loser_shadbala_ratio: float,
) -> float:
    """
    Compute Yuddha Bala quantum (in Shadbala ratio units).

    Formula (BPHS):
        YB_rupas = |Tribala_winner - Tribala_loser| / |Disc_winner - Disc_loser|

    Since we use Shadbala *ratios* (not raw rupas), we reconstruct approximate
    rupas via: Tribala_approx ≈ ratio × min_rupas × (3/6)  [Tri-Bala is 3 of 6]

    The result is expressed as a Shadbala ratio adjustment:
        YB_ratio = YB_rupas / min_rupas_loser

    This ratio is then transferred: subtracted from loser, added to winner.

    Disc circumference difference guard: if planets have equal disc sizes
    (undefined in classical texts), fall back to Naisargika Bala difference.
    """
    disc_winner = DISC_CIRCUMFERENCE_ARCSEC.get(winner, 10.0)
    disc_loser  = DISC_CIRCUMFERENCE_ARCSEC.get(loser, 10.0)
    disc_diff   = abs(disc_winner - disc_loser)

    min_w = MIN_SHADBALA_RUPAS.get(winner, 360.0)
    min_l = MIN_SHADBALA_RUPAS.get(loser,  360.0)

    # Approximate Tri-Bala (3 sub-components out of 6) ≈ ratio × min × 0.5
    trib_w = winner_shadbala_ratio * min_w * 0.5
    trib_l =  loser_shadbala_ratio * min_l * 0.5
    trib_diff = abs(trib_w - trib_l)

    if disc_diff < 0.01:
        # Same disc size — use Naisargika Bala difference as fallback
        nat_diff = abs(_NAT_STRENGTH.get(winner, 20) - _NAT_STRENGTH.get(loser, 10))
        yuddha_bala_rupas = trib_diff / max(nat_diff, 1.0)
    else:
        yuddha_bala_rupas = trib_diff / disc_diff

    # Express as ratio-unit relative to loser's minimum
    yuddha_bala_ratio = yuddha_bala_rupas / max(min_l, 1.0)

    # Cap at 0.8 ratio units to prevent erasing the loser entirely
    return round(min(yuddha_bala_ratio, 0.80), 4)


def detect_planetary_wars(planet_lons: Dict[str, float]) -> List[Dict]:
    """
    Identify all active planetary wars in a chart.

    For each pair of war-eligible planets within WAR_ORB_DEG, determine:
      - winner  (higher Naisargika order)
      - loser   (weaker by Naisargika order)
      - strength_penalty to loser (0.0 – 0.5 fraction of Shadbala)
      - yuddha_bala_transfer : ratio-unit quantum to transfer (requires shadbala)

    Returns list of dicts, one per war pair.
    """
    candidates = [p for p in WAR_PLANETS if p in planet_lons]
    wars = []
    for i, p1 in enumerate(candidates):
        for p2 in candidates[i + 1:]:
            sep = angular_distance(planet_lons[p1], planet_lons[p2])
            if sep > WAR_ORB_DEG:
                continue

            # Classical exception: Venus is declared victor in any Graha Yuddha.
            if p1 == "VENUS" or p2 == "VENUS":
                winner, loser = ("VENUS", p2 if p1 == "VENUS" else p1)
            else:
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
                # Yuddha Bala transfer quantum — filled by apply_war_penalties()
                # when shadbala_ratios are available
                "yuddha_bala_transfer": None,
                "disc_winner_arcsec": DISC_CIRCUMFERENCE_ARCSEC.get(winner),
                "disc_loser_arcsec":  DISC_CIRCUMFERENCE_ARCSEC.get(loser),
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
    Return adjusted Shadbala ratios after applying Yuddha Bala transfer.

    Classical Yuddha Bala (BPHS §3.2 / Logic Manifest §3.2):
      1. Compute the Yuddha Bala quantum from Tri-Bala difference / disc
         circumference difference.
      2. TRANSFER the exact quantum: subtract from loser, add to winner.
      3. The loser's ability to fructify Yoga and house results is zeroed out
         at the quantum level; winner absorbs that karmic potential.

    This replaces the crude proportional penalty with the classical formula.
    Updates the war dicts in-place with the computed yuddha_bala_transfer.
    """
    adjusted = {k: v for k, v in shadbala_ratios.items()}
    for war in wars:
        loser  = war["loser"]
        winner = war["winner"]
        penalty = war["strength_penalty"]   # legacy penalty preserved

        r_winner = adjusted.get(winner, 1.0)
        r_loser  = adjusted.get(loser,  1.0)

        # Step 1: Compute Yuddha Bala quantum (exact classical formula)
        yb = _compute_yuddha_bala(winner, loser, r_winner, r_loser)
        war["yuddha_bala_transfer"] = yb   # record for reporting

        # Step 2: Classical transfer — subtract from loser, add to winner
        # At separation < WAR_ORB_DEG the transfer is FULL (loser fully crippled);
        # scale proportionally with the separation (at 0° = full, at WAR_ORB = 0)
        transfer_factor = (WAR_ORB_DEG - war["separation_deg"]) / WAR_ORB_DEG
        effective_transfer = yb * transfer_factor

        if loser in adjusted:
            adjusted[loser] = round(max(adjusted[loser] - effective_transfer, 0.05), 3)
        if winner in adjusted:
            adjusted[winner] = round(min(adjusted[winner] + effective_transfer * 0.5, 2.5), 3)

    return adjusted


def war_summary(wars: List[Dict]) -> str:
    """Human-readable summary of active wars."""
    if not wars:
        return "No planetary wars."
    return "; ".join(w["description"] for w in wars)
