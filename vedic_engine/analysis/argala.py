"""
Argala (Intervention) Analysis Engine.

Argala = the ability of a planet in certain houses to "intervene" and modify
the results of a reference point (lagna, dasha lord, specific house cusp).

Classical BPHS rule (Ch. 38):
  Houses 2, 4, 5, 11 from any reference point → Argala (positive intervention)
  Houses 12, 10, 9, 3 from any reference point → Virodha Argala (obstructs)

Virodha (obstruction) cancels Argala if:
  - House 12 has more benefic count than house 2 → Argala of H2 cancelled
  - House 10 has more benefic count than house 4 → Argala of H4 cancelled
  - House 9  has more benefic count than house 5 → Argala of H5 cancelled
  - House 3  has a planet stronger than H11      → Argala of H11 cancelled

Special rule: Benefics in Argala houses → positive Argala (wealth, support)
              Malefics in Argala houses → Paapa (negative) Argala (obstacles)
              Malefics in Virodha houses → they ALSO obstruct (double block)

Ketu Exception (Jaimini — File 4 spec):
  Ketu reverses ALL directions in Argala computation.
  Ketu in Argala house (2nd,4th,11th,5th) → flips to Virodha role (obstruction).
  Ketu in Virodha house (12th,10th,3rd,9th) → flips to Argala role (support).
  This reflects Ketu's nature as a south node (inward/reverse vector).

Integration into confidence:
  - Strong positive Argala from Jupiter/Venus on dasha lord → confidence boost
  - Paapa Argala from Saturn/Rahu on domain ruler → confidence penalty
  - Net argala strength becomes a modifier on the domain prediction
"""
from __future__ import annotations
import os
from typing import Dict, List, Optional, Tuple

from vedic_engine.config import Planet, NATURAL_BENEFICS, NATURAL_MALEFICS


# ─── Constants ────────────────────────────────────────────────────────────────

ARGALA_HOUSES   = [2, 4, 5, 11]   # from reference point
VIRODHA_HOUSES  = [12, 10, 9, 3]  # corresponding obstruction houses

# Which virodha house obstructs which argala house
ARGALA_VIRODHA_PAIRS = {2: 12, 4: 10, 5: 9, 11: 3}

NATURAL_BENEFIC_NAMES  = {"JUPITER", "VENUS", "MERCURY", "MOON"}
NATURAL_MALEFIC_NAMES  = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}

# Argala modifier weights  (net_argala → confidence adjustment)
ARGALA_BENEFIC_WT  = 0.08   # per strong benefic argala
ARGALA_PAAPA_WT    = 0.06   # per malefic argala (negative)

# Classical house weights: 2/4/11 primary full, 5 secondary half, 7 special half.
ARGALA_HOUSE_WEIGHTS = {
    2: 1.0,
    4: 1.0,
    11: 1.0,
    5: 0.5,
    7: 0.5,
}

# Node reversal mode:
# - "ketu"  : backward-compatible legacy behavior
# - "both"  : apply reverse-direction treatment to both nodes
_ARGALA_NODE_REVERSE_MODE = os.getenv("VE_ARGALA_NODE_REVERSE_MODE", "ketu").strip().lower()
if _ARGALA_NODE_REVERSE_MODE not in {"ketu", "both"}:
    _ARGALA_NODE_REVERSE_MODE = "ketu"


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _house_from(ref_house: int, offset: int) -> int:
    """Return the house that is `offset` houses away from ref_house (1-indexed)."""
    return (ref_house - 1 + offset - 1) % 12 + 1


def _planets_in_house(house: int, planet_houses: Dict[str, int]) -> List[str]:
    return [p for p, h in planet_houses.items() if h == house]


def _is_benefic(planet: str) -> bool:
    return planet in NATURAL_BENEFIC_NAMES


def _apply_node_reversal(
    a_planets: List[str],
    v_planets: List[str],
) -> Tuple[List[str], List[str]]:
    """
    Reverse-direction node rule for Argala.

    In "ketu" mode: only Ketu reverses direction.
    In "both" mode: Ketu and Rahu reverse direction.

    This is applied PER argala pair, after house lookups.
    """
    reverse_nodes = {"KETU"}
    if _ARGALA_NODE_REVERSE_MODE == "both":
        reverse_nodes.add("RAHU")

    new_a = [p for p in a_planets if p not in reverse_nodes]
    new_v = [p for p in v_planets if p not in reverse_nodes]

    for node in reverse_nodes:
        if node in a_planets:
            new_v.append(node)
        if node in v_planets:
            new_a.append(node)

    return new_a, new_v


def _is_malefic(planet: str) -> bool:
    return planet in NATURAL_MALEFIC_NAMES


def _shadbala_count(planets: List[str], shadbala: Dict[str, float]) -> float:
    """Sum of shadbala ratios for a list of planets (proxy for strength count)."""
    return sum(shadbala.get(p, 1.0) for p in planets)


# ─── Core computation ─────────────────────────────────────────────────────────

def compute_argala(
    reference_house: int,
    planet_houses: Dict[str, int],
    shadbala_ratios: Optional[Dict[str, float]] = None,
    label: str = "reference",
) -> Dict:
    """
    Compute Argala and Virodha Argala on a reference house from all planets.

    Parameters
    ----------
    reference_house : int 1-12
    planet_houses   : {planet_name: house_number}
    shadbala_ratios : {planet_name: ratio} — used for strength-weighted cancellation
    label           : human-readable label for the reference point

    Returns
    -------
    dict with:
        argala         : list of active argala contributions
        virodha        : list of active virodha contributions
        net_strength   : float [-1, +1] — positive = net helpful
        verdict        : str
        confidence_mod : float — confidence adjustment to apply
    """
    if shadbala_ratios is None:
        shadbala_ratios = {}

    argala_active   = []
    virodha_active  = []
    unobstructable_count = 0

    # ── VIPARITA ARGALA check ─────────────────────────────────────
    # 3+ malefics in 3rd house from reference = totally unblockable worldly success
    third_house = _house_from(reference_house, 3)
    malefics_in_3rd = [p for p in _planets_in_house(third_house, planet_houses)
                       if _is_malefic(p)]
    viparita_argala_active = len(malefics_in_3rd) >= 3

    # ── Argala pairs: Primary + Secondary + Special ───────────────
    # Primary:   2→12, 4→10, 11→3
    # Secondary: 5→9    (also secondary: 8→6, but 8 is rarely used)
    # Special:   7→1    (7th argala obstructed ONLY by 1st)
    argala_pairs = [
        (2, 12, "primary"),
        (4, 10, "primary"),
        (11, 3, "primary"),
        (5,  9, "secondary"),
        (7,  1, "special"),    # 7th-house argala, blocked ONLY by 1st
    ]

    for argala_offset, virodha_offset, argala_type in argala_pairs:
        a_house = _house_from(reference_house, argala_offset)
        v_house = _house_from(reference_house, virodha_offset)

        a_planets = _planets_in_house(a_house, planet_houses)
        v_planets = _planets_in_house(v_house, planet_houses)

        # Reverse-direction node rule (Ketu-only by default, both nodes in strict mode).
        a_planets, v_planets = _apply_node_reversal(a_planets, v_planets)

        pair_weight = ARGALA_HOUSE_WEIGHTS.get(argala_offset, 1.0)

        # Pure obstruction: empty Argala house but occupied virodha house.
        if not a_planets and v_planets:
            virodha_active.append({
                "house": v_house,
                "offset": virodha_offset,
                "planets": v_planets,
                "obstructs_argala_house": a_house,
                "pure_obstruction": True,
            })
            argala_active.append({
                "argala_house": a_house,
                "argala_offset": argala_offset,
                "argala_type": argala_type,
                "house_weight": pair_weight,
                "planets": [],
                "benefics": [],
                "malefics": [],
                "virodha_house": v_house,
                "virodha_planets": v_planets,
                "cancelled": True,
                "unobstructable": False,
                "pure_virodha": True,
                "viparita_argala_override": False,
                "net_type": "PURE_VIRODHA",
                "contribution": round(-ARGALA_PAAPA_WT * pair_weight * min(len(v_planets), 2), 4),
            })
            continue

        if not a_planets:
            continue  # no argala from this house

        # Classify argala
        a_benefics = [p for p in a_planets if _is_benefic(p)]
        a_malefics = [p for p in a_planets if _is_malefic(p)]

        # ── Resolution hierarchy (per classical rules) ──────────
        # Priority 1: QUANTITY — more planets in house wins
        # Priority 2: DIGNITY — own-sign/exalt planet outweighs debilitated
        # Priority 3: BENEFIC ASPECT — benefic in virodha tips equal balance
        # Priority 4: BANDANA YOGA — perfectly equal = paralysis (net 0)

        a_count   = len(a_planets)
        v_count   = len(v_planets)
        a_strength = _shadbala_count(a_planets, shadbala_ratios)
        v_strength = _shadbala_count(v_planets, shadbala_ratios)

        # Benefic in virodha house acts as aspect bonus (tipping factor)
        v_benefics = [p for p in v_planets if _is_benefic(p)]
        v_has_benefic_aspect = bool(v_benefics)

        # Special case: 3+ planets in Argala house is unobstructable.
        unobstructable = a_count >= 3

        # Special case: Viparita Argala overrides all obstruction for primary houses.
        if viparita_argala_active and argala_type == "primary":
            cancelled = False  # unblockable
        elif unobstructable:
            cancelled = False
        elif a_count > v_count:
            # Priority 1: Quantity wins for argala
            cancelled = False
        elif v_count > a_count:
            # Priority 1: Quantity wins for virodha
            cancelled = True
        elif a_strength > v_strength * 1.05:
            # Priority 2: Dignity — argala side stronger
            cancelled = False
        elif v_strength > a_strength * 1.05:
            # Priority 2: Dignity — virodha side stronger
            cancelled = True
        elif v_has_benefic_aspect:
            # Priority 3: Benefic Jupiter/Venus in virodha tips balance toward blocking
            cancelled = True
        else:
            # Priority 4: Bandana Yoga (deadlock) = net zero (cancelled for safety)
            cancelled = True   # "paralysis/confinement" — report as cancelled

        argala_entry = {
            "argala_house":   a_house,
            "argala_offset":  argala_offset,
            "argala_type":    argala_type,
            "house_weight":   pair_weight,
            "planets":        a_planets,
            "benefics":       a_benefics,
            "malefics":       a_malefics,
            "virodha_house":  v_house,
            "virodha_planets":v_planets,
            "cancelled":      cancelled,
            "unobstructable": unobstructable,
            "pure_virodha":   False,
            "viparita_argala_override": viparita_argala_active and argala_type == "primary",
            "net_type":       None,
            "contribution":   0.0,
        }

        if cancelled:
            argala_entry["net_type"] = "CANCELLED"
            argala_entry["contribution"] = 0.0
        elif a_benefics:
            # Positive Argala
            count = len(a_benefics)
            strength_avg = _shadbala_count(a_benefics, shadbala_ratios) / max(count, 1)
            argala_entry["net_type"] = "POSITIVE"
            argala_entry["contribution"] = (
                ARGALA_BENEFIC_WT
                * pair_weight
                * count
                * min(strength_avg, 1.5)
                / 1.5
            )
        elif a_malefics:
            # Paapa Argala
            count = len(a_malefics)
            argala_entry["net_type"] = "PAAPA"
            argala_entry["contribution"] = -ARGALA_PAAPA_WT * pair_weight * count

        if unobstructable:
            unobstructable_count += 1

        argala_active.append(argala_entry)

        if v_planets:
            virodha_active.append({
                "house":                 v_house,
                "offset":                virodha_offset,
                "planets":               v_planets,
                "obstructs_argala_house":a_house,
            })

    # Net strength
    net = sum(e["contribution"] for e in argala_active)
    net = max(-1.0, min(1.0, net))

    positive_count = sum(1 for e in argala_active if e["net_type"] == "POSITIVE")
    paapa_count    = sum(1 for e in argala_active if e["net_type"] == "PAAPA")
    cancelled_count= sum(1 for e in argala_active if e["net_type"] == "CANCELLED")

    if net >= 0.12:
        verdict = "STRONG POSITIVE ARGALA"
    elif net >= 0.04:
        verdict = "MILD POSITIVE ARGALA"
    elif net <= -0.10:
        verdict = "STRONG PAAPA ARGALA"
    elif net <= -0.03:
        verdict = "MILD PAAPA ARGALA"
    else:
        verdict = "NEUTRAL / BALANCED"

    return {
        "reference": label,
        "reference_house": reference_house,
        "viparita_argala": viparita_argala_active,
        "node_reverse_mode": _ARGALA_NODE_REVERSE_MODE,
        "argala_list": argala_active,
        "virodha_list": virodha_active,
        "positive_count": positive_count,
        "paapa_count": paapa_count,
        "cancelled_count": cancelled_count,
        "unobstructable_count": unobstructable_count,
        "net_strength": round(net, 4),
        "verdict": verdict,
        "confidence_mod": round(net * 0.5, 4),  # halved for conservative blending
    }


def compute_all_argala(
    planet_houses: Dict[str, int],
    lagna_house: int = 1,
    dasha_lord_house: Optional[int] = None,
    antardasha_lord_house: Optional[int] = None,
    shadbala_ratios: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Compute Argala on multiple reference points:
    - Lagna (house 1)
    - Active dasha lord's house
    - Moon's house

    Returns combined dict with all reference point analyses.
    """
    results = {}
    moon_house = planet_houses.get("MOON", 1)

    results["lagna"] = compute_argala(
        lagna_house, planet_houses, shadbala_ratios, "Lagna"
    )
    results["moon"] = compute_argala(
        moon_house, planet_houses, shadbala_ratios, "Moon"
    )
    if dasha_lord_house:
        results["dasha_lord"] = compute_argala(
            dasha_lord_house, planet_houses, shadbala_ratios, "Dasha Lord"
        )
    if antardasha_lord_house:
        results["antardasha_lord"] = compute_argala(
            antardasha_lord_house, planet_houses, shadbala_ratios, "Antardasha Lord"
        )

    # Combined net (average of key reference points)
    nets = [v["net_strength"] for v in results.values()]
    combined = sum(nets) / max(len(nets), 1)

    results["combined_net"] = round(combined, 4)
    results["combined_confidence_mod"] = round(combined * 0.5, 4)

    return results
