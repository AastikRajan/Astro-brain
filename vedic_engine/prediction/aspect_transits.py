"""
Transit-to-Natal Longitude Aspect Analysis.

Implements the research-formalised continuous orb weight function from
deep-research-report1.md:

    w(Δ) = max(0,  1 - Δorb / max_orb)

where Δorb = |separation - aspect_angle|.

Key differences from the existing gochar (house-from-Moon) layer:
  • Uses actual sidereal LONGITUDE differences, not house counts.
  • Covers all major aspect angles: 0°, 60°, 90°, 120°, 180°.
  • Detects APPLYING vs SEPARATING (applying = transit approaching exact, stronger).
  • Produces a normalised net activation score per domain.

This is the "Western-meets-Vedic" longitude aspect layer wired on top of
the existing Vedic gochar system.
"""
from __future__ import annotations
from typing import Dict, List, Tuple


# ─── Aspect definitions ────────────────────────────────────────────────────────

MAJOR_ASPECTS: Dict[int, str] = {
    0:   "Conjunction",
    60:  "Sextile",
    90:  "Square",
    120: "Trine",
    180: "Opposition",
}

# Benefic(+1) or Malefic(−1) tendency of the aspect angle itself
ASPECT_POLARITY: Dict[int, int] = {
    0:   0,    # conjunction – evaluated via planet nature
    60:  1,
    90:  -1,
    120: 1,
    180: -1,
}

# Orb radius per transiting planet (degrees) — traditional table
ORB_TABLE: Dict[str, float] = {
    "SUN":     8.0,
    "MOON":    8.0,
    "MARS":    7.0,
    "JUPITER": 7.0,
    "SATURN":  7.0,
    "VENUS":   6.0,
    "MERCURY": 6.0,
    "RAHU":    5.0,
    "KETU":    5.0,
}

# Natural benefics → conjunction treated as benefic
NATURAL_BENEFIC = {"JUPITER", "VENUS", "MERCURY", "MOON"}
NATURAL_MALEFIC = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}

# Mean motion deg/day — used to decide applying vs separating
MEAN_SPEED: Dict[str, float] = {
    "SUN":     0.9856,
    "MOON":    13.1764,
    "MARS":    0.5240,
    "MERCURY": 1.3833,
    "JUPITER": 0.0831,
    "VENUS":   1.2022,
    "SATURN":  0.0335,
    "RAHU":    -0.0529,
    "KETU":    -0.0529,
}


# ─── Geometry helpers ──────────────────────────────────────────────────────────

def _separation(lon_a: float, lon_b: float) -> float:
    """Minimal arc (0–180) between two ecliptic longitudes."""
    raw = abs(lon_a - lon_b) % 360.0
    return raw if raw <= 180.0 else 360.0 - raw


def _is_applying(
    transit_lon: float,
    natal_lon: float,
    transit_speed: float,
    aspect_angle: float,
) -> bool:
    """
    True when the transit planet is GETTING CLOSER to the exact aspect.
    Simulate position 2 hours ahead and compare orb.
    """
    step = transit_speed * (2.0 / 24.0)          # 2-hour step in degrees
    next_lon = (transit_lon + step) % 360.0
    curr_orb = abs(_separation(transit_lon, natal_lon) - aspect_angle)
    next_orb = abs(_separation(next_lon,    natal_lon) - aspect_angle)
    return next_orb < curr_orb


# ─── Main computation ──────────────────────────────────────────────────────────

def compute_transit_aspects(
    transit_positions: Dict[str, float],
    natal_positions:   Dict[str, float],
    transit_speeds:    Dict[str, float] | None = None,
) -> Dict[str, dict]:
    """
    Compute all transit-to-natal major aspects with continuous orb weighting.

    Parameters
    ----------
    transit_positions : {planet: sidereal_longitude}  — current transits
    natal_positions   : {planet: sidereal_longitude}  — natal chart
    transit_speeds    : optional {planet: deg_per_day} — for applying/separating

    Returns
    -------
    {
      "SATURN": {
          "aspects": [
              {natal_planet, aspect, aspect_angle, orb, strength, applying, nature}, …
          ],
          "benefic_score": float,
          "malefic_score": float,
          "net_aspect_score": float,   # benefic − malefic  (can be negative)
      },
      …
    }
    """
    speeds = transit_speeds or {}
    results: Dict[str, dict] = {}

    for t_planet, t_lon in transit_positions.items():
        max_orb   = ORB_TABLE.get(t_planet, 6.0)
        t_speed   = speeds.get(t_planet, MEAN_SPEED.get(t_planet, 1.0))
        is_benefic_planet = t_planet in NATURAL_BENEFIC

        aspects_found: List[dict] = []
        total_benefic = 0.0
        total_malefic = 0.0

        for n_planet, n_lon in natal_positions.items():
            sep = _separation(t_lon, n_lon)

            for asp_angle, asp_name in MAJOR_ASPECTS.items():
                orb_diff = abs(sep - asp_angle)
                if orb_diff > max_orb:
                    continue

                # Continuous weight function (research formula)
                strength = 1.0 - orb_diff / max_orb

                # Applying aspects are 15% stronger (classical rule)
                applying = _is_applying(t_lon, n_lon, t_speed, asp_angle)
                if applying:
                    strength = min(1.0, strength * 1.15)

                # Conjunction nature depends on transit planet
                polarity = ASPECT_POLARITY[asp_angle]
                if asp_angle == 0:
                    polarity = 1 if is_benefic_planet else -1

                nature = "benefic" if polarity > 0 else "malefic"
                aspects_found.append({
                    "natal_planet":  n_planet,
                    "aspect":        asp_name,
                    "aspect_angle":  asp_angle,
                    "orb":           round(orb_diff, 2),
                    "strength":      round(strength, 3),
                    "applying":      applying,
                    "nature":        nature,
                })
                if polarity > 0:
                    total_benefic += strength
                else:
                    total_malefic += strength

        # Sort closest (smallest orb) first
        aspects_found.sort(key=lambda x: x["orb"])

        results[t_planet] = {
            "aspects":          aspects_found,
            "benefic_score":    round(total_benefic, 3),
            "malefic_score":    round(total_malefic, 3),
            "net_aspect_score": round(total_benefic - total_malefic, 3),
        }

    return results


def compute_natal_activation_score(
    transit_aspects: Dict[str, dict],
    domain_natal_planets: List[str],
) -> float:
    """
    Summarize how much transiting planets are activating domain-relevant
    natal planets via longitude aspects.

    Returns a score in [0.0, 1.0], where 0.5 = neutral.
    """
    total_benefic = 0.0
    total_malefic = 0.0

    for planet_result in transit_aspects.values():
        for asp in planet_result.get("aspects", []):
            if asp["natal_planet"] not in domain_natal_planets:
                continue
            if asp["nature"] == "benefic":
                total_benefic += asp["strength"]
            else:
                total_malefic += asp["strength"]

    raw_net = total_benefic - total_malefic
    # Sigmoid-like normalization: raw ±6 maps to score ≈ 0–1, 0 → 0.5
    score = 0.5 + raw_net / (2.0 * max(1.0, abs(raw_net) + 1.0))
    return round(max(0.0, min(1.0, score)), 3)


def top_transit_aspects(
    transit_aspects: Dict[str, dict],
    top_n: int = 6,
) -> List[dict]:
    """
    Flatten and return the top N strongest transit-to-natal aspects across
    all transiting planets, sorted by strength descending.
    """
    all_aspects = []
    for t_planet, data in transit_aspects.items():
        for asp in data.get("aspects", []):
            all_aspects.append({**asp, "transit_planet": t_planet})
    all_aspects.sort(key=lambda x: x["strength"], reverse=True)
    return all_aspects[:top_n]
