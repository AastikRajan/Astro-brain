"""
Phase 3A — Nadi Jyotish Timing System.

Implements six Nadi-specific computational modules:
  1. BCP (Biometric Chronological Progression) — active house and planets
  2. Nadi Saturn Activation — natal planet karakatwa trigger by transit Saturn
  3. Patel Marriage Dates — D9-ASC-based day-count formulas
  4. BNN (Biometric Nodal Network) Graph — weighted edge set of planet relations
  5. BNN Connectivity Scores — per-planet hub-strength in the BNN
  6. Spouse Career Sign — Venus-based 7th-harmonic projection

Architecture Note: ALL functions here are pure computation.
No prediction weights, no blending, no domain logic.
Those belong exclusively in prediction/engine.py (Phase 3F).

References: Nadi Jyotish Computational Analysis Framework.md
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple


# ─── Sign name lookup ────────────────────────────────────────────────────────

SIGN_NAMES: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Nadi karakatwa table — which planet signifies which life domain
# (used to label BNN nodes and explain Saturn-activation results)
NADI_KARAKATWA: Dict[str, List[str]] = {
    "SUN":      ["father", "authority", "ego", "soul"],
    "MOON":     ["mother", "mind", "emotions", "home"],
    "MARS":     ["siblings", "energy", "conflict", "property"],
    "MERCURY":  ["intelligence", "communication", "trade"],
    "JUPITER":  ["wisdom", "children", "husband_for_female", "dharma"],
    "VENUS":    ["wife_for_male", "wealth", "luxury", "relationships"],
    "SATURN":   ["profession", "karma", "longevity", "servants"],
    "RAHU":     ["foreign", "obsession", "technology", "outcaste"],
    "KETU":     ["spirituality", "liberation", "past_karma", "accidents"],
}

# BNN graph edge-weight rules (from research: trine=1.0, adjacent=0.75, opposition=0.5)
_BNN_TRINE_DIST    = {4, 8}      # 5th and 9th sign distances
_BNN_OPPOSITION_DIST = {6}       # 7th sign distance (opposition)
_BNN_ADJACENT_DIST = {1, 11}     # 2nd and 12th sign distances

# Planets included in BNN graph
_BNN_PLANETS = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU"]


# ─── 1. BCP (Biometric Chronological Progression) ────────────────────────────

def compute_bcp_active_house(age_years: int) -> int:
    """
    Return the BCP-active house number (1–12) for a given age.

    Formula from Nadi Jyotish: age cycles through 12 houses, starting at H1 for age 1.
        active_house = ((age_years - 1) % 12) + 1
    At age 0 or negative → treated as age 1 (house 1).

    Returns:
        int in [1, 12]
    """
    if age_years < 1:
        age_years = 1
    return ((age_years - 1) % 12) + 1


def compute_bcp_active_planets(active_house: int,
                                planet_houses: Dict[str, int]) -> List[str]:
    """
    Return the list of planets residing in the BCP-active natal house.

    Args:
        active_house:   House number (1–12) from compute_bcp_active_house().
        planet_houses:  {planet_name: house_num} from chart_raw.

    Returns:
        List of planet name strings (may be empty).
    """
    return [p for p, h in planet_houses.items() if h == active_house]


# ─── 2. Nadi Saturn Activation ───────────────────────────────────────────────

def check_nadi_saturn_activation(
    saturn_lon: float,
    natal_planet_lons: Dict[str, float],
    orb: float = 3.0,
) -> List[Dict[str, Any]]:
    """
    Detect which natal planets are activated by Nadi Saturn activation logic.

    A natal planet P is "Nadi-activated" when transit Saturn is within `orb`
    degrees of P's natal longitude (conjunction), triggering P's karakatwa
    (significations) into the native's life narrative.

    This is NOT Sade-Sati (Moon-sign transit). It is a precise degree-level
    conjunction-activation that fires the natal planet's specific significations.

    Args:
        saturn_lon:         Current (transit) longitude of Saturn in degrees [0, 360).
        natal_planet_lons:  {planet_name: natal_longitude} from chart_raw.
        orb:                Degrees of orb for conjunction (default 3.0°).

    Returns:
        List of dicts: [{
            "planet": str,
            "natal_lon": float,
            "saturn_lon": float,
            "separation": float,   # degrees, always positive
            "karakatwa": list,     # significations triggered
        }]
    """
    activated: List[Dict[str, Any]] = []
    for planet, natal_lon in natal_planet_lons.items():
        if planet == "SATURN":   # Saturn doesn't activate itself this way
            continue
        raw_sep = abs(saturn_lon - natal_lon) % 360.0
        sep = raw_sep if raw_sep <= 180.0 else 360.0 - raw_sep
        if sep <= orb:
            activated.append({
                "planet":      planet,
                "natal_lon":   round(natal_lon, 4),
                "saturn_lon":  round(saturn_lon, 4),
                "separation":  round(sep, 4),
                "karakatwa":   NADI_KARAKATWA.get(planet, []),
            })
    # Sort by proximity (closest first)
    activated.sort(key=lambda x: x["separation"])
    return activated


# ─── 3. Patel Marriage Date Formulas ─────────────────────────────────────────

def _days_to_date(birth_date: date, days: float) -> Optional[date]:
    """Convert a day-offset from birth_date to a calendar date, or None if invalid."""
    try:
        return birth_date + timedelta(days=int(round(days)))
    except (OverflowError, ValueError):
        return None


def compute_patel_marriage_dates(
    navamsha_asc_lon: float,
    birth_date: date,
    cycles: int = 3,
) -> List[Dict[str, Any]]:
    """
    Compute Patel marriage candidate dates using D9 (Navamsha) ASC longitude.

    Two formulas from Patel (research-documented):
      Formula A (primary cycle):   days = (navamsha_asc_lon × 324) + (n × 10800)
      Formula B (secondary cycle): days = (navamsha_asc_lon × 216) + (n × 10800)

    For each formula, cycles n = 0, 1, 2, ..., `cycles`-1 are generated.
    The base navamsha_asc_lon is the D9 ascendant in degrees [0, 360).

    Args:
        navamsha_asc_lon:   Navamsha ASC longitude in degrees (D9 chart).
        birth_date:         Native's date of birth.
        cycles:             Number of cycles to generate per formula (default 3).

    Returns:
        List of dicts: [{
            "formula": "A" or "B",
            "cycle": int (n),
            "days_from_birth": float,
            "candidate_date": date or None,
            "candidate_year": int or None,
        }]
    """
    results: List[Dict[str, Any]] = []
    # Clamp lon to [0, 360)
    lon = navamsha_asc_lon % 360.0

    for n in range(cycles):
        for formula_label, multiplier in [("A", 324.0), ("B", 216.0)]:
            days = (lon * multiplier) + (n * 10800.0)
            cand_date = _days_to_date(birth_date, days)
            results.append({
                "formula":         formula_label,
                "cycle":           n,
                "days_from_birth": round(days, 2),
                "candidate_date":  cand_date,
                "candidate_year":  cand_date.year if cand_date else None,
            })

    # Sort by candidate date ascending
    results.sort(key=lambda x: x["days_from_birth"])
    return results


# ─── 4. BNN (Biometric Nodal Network) Graph ──────────────────────────────────

def _bnn_edge_weight(dist: int) -> float:
    """
    Return the BNN edge weight based on sign distance.

    Distances are always 0–6 (after taking min(d, 12-d)):
      0   → same sign (conjunction) = 1.0
      4,8 → trine = 1.0
      6   → opposition = 0.5
      1,11→ adjacent = 0.75
      else → no edge (0.0)
    """
    d = dist % 12
    d = min(d, 12 - d)  # 0–6 range
    if d == 0:
        return 1.0          # conjunction
    if d in (4,):           # trine (120°, also 240° = same weight)
        return 1.0
    if d == 6:              # opposition
        return 0.5
    if d in (1,):           # adjacent (30°/330°)
        return 0.75
    return 0.0              # no significant Nadi relationship


def compute_bnn_graph(
    planet_signs: Dict[str, int],
    retrogrades:  Dict[str, bool],
) -> List[Dict[str, Any]]:
    """
    Build the BNN (Biometric Nodal Network) weighted edge list.

    Rules from Nadi Jyotish research:
      • For each pair of planets (P1, P2), compute sign distance.
      • Edge weight: trine (4/8) = 1.0, conjunction (0) = 1.0,
        opposition (6) = 0.5, adjacent (1/11) = 0.75, else = no edge.
      • Retrograde rule: a retrograde planet also acts from (sign - 1) % 12,
        so we create an additional "retrograde" edge from that secondary sign.

    Args:
        planet_signs:  {planet_name: sign_idx}  0-indexed (0=Aries…11=Pisces)
        retrogrades:   {planet_name: bool}

    Returns:
        List of edge dicts: [{
            "planet1": str,
            "planet2": str,
            "weight": float,
            "p1_sign": int,
            "p2_sign": int,
            "p1_retrograde_shadow": bool,  # True if edge via retrograde shadow sign
            "p2_retrograde_shadow": bool,
        }]
    """
    planets = [p for p in _BNN_PLANETS if p in planet_signs]
    edges: List[Dict[str, Any]] = []

    for i in range(len(planets)):
        p1 = planets[i]
        s1_main = planet_signs[p1] % 12
        p1_retro = retrogrades.get(p1, False)
        p1_signs = [s1_main] if not p1_retro else [s1_main, (s1_main - 1) % 12]

        for j in range(i + 1, len(planets)):
            p2 = planets[j]
            s2_main = planet_signs[p2] % 12
            p2_retro = retrogrades.get(p2, False)
            p2_signs = [s2_main] if not p2_retro else [s2_main, (s2_main - 1) % 12]

            # Try all combinations of primary/shadow signs
            for idx1, s1 in enumerate(p1_signs):
                for idx2, s2 in enumerate(p2_signs):
                    dist = (s2 - s1) % 12
                    w = _bnn_edge_weight(dist)
                    if w > 0.0:
                        edges.append({
                            "planet1":               p1,
                            "planet2":               p2,
                            "weight":                w,
                            "p1_sign":               s1,
                            "p2_sign":               s2,
                            "p1_retrograde_shadow":  (idx1 == 1),
                            "p2_retrograde_shadow":  (idx2 == 1),
                            "distance":              dist,
                        })
                        break  # take the highest-weight edge for this pair
                else:
                    continue
                break

    return edges


# ─── 5. BNN Connectivity Scores ──────────────────────────────────────────────

def compute_bnn_connectivity_scores(
    bnn_graph: List[Dict[str, Any]],
    planet_signs: Dict[str, int],
) -> Dict[str, float]:
    """
    Compute weighted hub-centrality for each planet in the BNN graph.

    Score for planet P = sum of weights of all edges touching P,
    then normalized to [0.0, 1.0] relative to the maximum score.

    Args:
        bnn_graph:     Output of compute_bnn_graph().
        planet_signs:  {planet_name: sign_idx} — used to initialise zero scores.

    Returns:
        {planet_name: connectivity_score}  — float in [0.0, 1.0]
    """
    scores: Dict[str, float] = {p: 0.0 for p in planet_signs}
    for edge in bnn_graph:
        p1, p2, w = edge["planet1"], edge["planet2"], edge["weight"]
        scores[p1] = scores.get(p1, 0.0) + w
        scores[p2] = scores.get(p2, 0.0) + w

    max_score = max(scores.values(), default=1.0)
    if max_score == 0.0:
        return scores
    return {p: round(v / max_score, 4) for p, v in scores.items()}


# ─── 6. Spouse Career Sign ───────────────────────────────────────────────────

def compute_spouse_career_sign(venus_sign_idx: int) -> int:
    """
    Compute the spouse's probable career (professional) sign using the
    Nadi formula: 10th from the 7th from Venus → (Venus sign + 9) % 12.

    The 7th from Venus = indicator of spouse's nature.
    The 10th from that = spouse's career sign.
    Combined: (venus_sign + 6 + 3) % 12 = (venus_sign + 9) % 12.

    Args:
        venus_sign_idx: Venus's natal sign index (0=Aries … 11=Pisces)

    Returns:
        Sign index (0–11) of the spouse's career sign.
    """
    return (venus_sign_idx + 9) % 12


# ─── Convenience: compute all Nadi signals from static chart data ─────────────

def compute_all_nadi_signals(
    planet_signs:      Dict[str, int],
    planet_houses:     Dict[str, int],
    planet_lons:       Dict[str, float],
    retrogrades:       Dict[str, bool],
    navamsha_asc_lon:  float,
    birth_date:        date,
    age_years:         int,
    transit_saturn_lon: Optional[float] = None,
    patel_cycles:      int = 2,
    saturn_orb:        float = 3.0,
) -> Dict[str, Any]:
    """
    Convenience wrapper — compute all Nadi signals and return as one dict.

    Designed to be called from analyze_static() / analyze_dynamic() in engine.py.
    All individual functions fail-safe; errors stored under "errors" key.

    Returns:
        {
          "bcp_active_house":             int,
          "bcp_active_planets":           list[str],
          "nadi_saturn_activated":        list[dict],  # empty if no transit_saturn_lon
          "patel_marriage_candidates":    list[dict],
          "bnn_graph":                    list[dict],
          "bnn_connectivity_scores":      dict[str,float],
          "spouse_career_sign":           int,
          "spouse_career_sign_name":      str,
          "errors":                       list[str],
        }
    """
    out: Dict[str, Any] = {"errors": []}

    # 1. BCP
    try:
        bcp_house = compute_bcp_active_house(age_years)
        out["bcp_active_house"]   = bcp_house
        out["bcp_active_planets"] = compute_bcp_active_planets(bcp_house, planet_houses)
    except Exception as e:
        out["bcp_active_house"]   = 1
        out["bcp_active_planets"] = []
        out["errors"].append(f"BCP: {e}")

    # 2. Nadi Saturn activation
    try:
        if transit_saturn_lon is not None:
            out["nadi_saturn_activated"] = check_nadi_saturn_activation(
                transit_saturn_lon, planet_lons, orb=saturn_orb
            )
        else:
            out["nadi_saturn_activated"] = []
    except Exception as e:
        out["nadi_saturn_activated"] = []
        out["errors"].append(f"NadiSaturn: {e}")

    # 3. Patel marriage dates
    try:
        out["patel_marriage_candidates"] = compute_patel_marriage_dates(
            navamsha_asc_lon, birth_date, cycles=patel_cycles
        )
    except Exception as e:
        out["patel_marriage_candidates"] = []
        out["errors"].append(f"Patel: {e}")

    # 4. BNN graph
    try:
        bnn_g = compute_bnn_graph(planet_signs, retrogrades)
        out["bnn_graph"] = bnn_g
    except Exception as e:
        bnn_g = []
        out["bnn_graph"] = []
        out["errors"].append(f"BNN: {e}")

    # 5. BNN connectivity scores
    try:
        out["bnn_connectivity_scores"] = compute_bnn_connectivity_scores(bnn_g, planet_signs)
    except Exception as e:
        out["bnn_connectivity_scores"] = {}
        out["errors"].append(f"BNN scores: {e}")

    # 6. Spouse career sign
    try:
        venus_sign = planet_signs.get("VENUS", 0)
        scs = compute_spouse_career_sign(venus_sign)
        out["spouse_career_sign"]      = scs
        out["spouse_career_sign_name"] = SIGN_NAMES[scs]
    except Exception as e:
        out["spouse_career_sign"]      = 0
        out["spouse_career_sign_name"] = "Aries"
        out["errors"].append(f"SpouseCareer: {e}")

    return out
