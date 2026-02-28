"""
Dispositor Chain Analysis.

In Vedic astrology every planet is "disposited" by the lord of the sign it
occupies.  Tracing the chain from a planet through its successive dispositors
reveals whose strength ultimately controls that planet's ability to deliver
results — critical for accurate dasha prediction.

Core concepts
─────────────
• Dispositor    : Lord of the sign a planet occupies.
• Final Disp.   : A planet in its own sign (Moolatrikona counts too) — the chain
                  terminates here ("Atmakaraka of the chain").
• Strong chain  : Every link is well-placed (kendra/trikona, dignified).
• Weak chain    : One or more links in trik houses (6/8/12) or debilitated.
• Mutual disp.  : Two planets each rule the other's sign (Parivartana) — 
                  usually resolved as co-lords; both are strong.

API
───
    from vedic_engine.analysis.dispositor import (
        compute_dispositor_chain, analyze_dasha_lord_dispositor, compute_all_chains
    )
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

from vedic_engine.config import (
    Planet, Sign, SIGN_LORDS, OWN_SIGNS, MOOLATRIKONA,
    EXALTATION_DEGREES, DEBILITATION_DEGREES,
)
from vedic_engine.core.coordinates import sign_of

# ─── Constants ────────────────────────────────────────────────────────────────

TRIK_HOUSES = frozenset({6, 8, 12})
KENDRA_HOUSES = frozenset({1, 4, 7, 10})
TRIKONA_HOUSES = frozenset({1, 5, 9})
GOOD_HOUSES = KENDRA_HOUSES | TRIKONA_HOUSES  # 1,4,5,7,9,10

# Rahu/Ketu have sign-based dispositors (they don't own signs)
RAHU_KETU = frozenset({"RAHU", "KETU"})

_STR_TO_PLANET = {p.name: p for p in Planet}
_PLANET_TO_STR = {p: p.name for p in Planet}


# ─── Dignity helpers ──────────────────────────────────────────────────────────

def _is_own_or_moola(planet_name: str, sign_idx: int) -> bool:
    """True if the planet is in its own sign or Moolatrikona sign."""
    p = _STR_TO_PLANET.get(planet_name)
    if p is None:
        return False
    if sign_idx in [s.value for s in OWN_SIGNS.get(p, [])]:
        return True
    moola = MOOLATRIKONA.get(p)
    if moola and moola[0].value == sign_idx:
        return True
    return False


def _is_exalted(planet_name: str, sign_idx: int) -> bool:
    p = _STR_TO_PLANET.get(planet_name)
    if p is None:
        return False
    return sign_idx == sign_of(EXALTATION_DEGREES.get(p, -999))


def _is_debilitated(planet_name: str, sign_idx: int) -> bool:
    p = _STR_TO_PLANET.get(planet_name)
    if p is None:
        return False
    return sign_idx == sign_of(DEBILITATION_DEGREES.get(p, -999))


def _get_sign_lord(sign_idx: int) -> Optional[str]:
    """Return planet name that owns the sign."""
    try:
        lord_planet = SIGN_LORDS.get(Sign(sign_idx))
        return lord_planet.name if lord_planet else None
    except (ValueError, AttributeError):
        return None


def _planet_sign(planet_name: str, planet_signs: Dict[str, int]) -> Optional[int]:
    """Return sign index (0-11) of the planet; None if not in map."""
    return planet_signs.get(planet_name)


# ─── Dignity level for scoring ───────────────────────────────────────────────

def _dignity_score(planet_name: str, sign_idx: int) -> float:
    """
    Returns a dignity score in 0-1 range.
    Exalted/Own/Moola → high, Debilitated → low.
    """
    if _is_exalted(planet_name, sign_idx):
        return 1.0
    if _is_own_or_moola(planet_name, sign_idx):
        return 0.85
    if _is_debilitated(planet_name, sign_idx):
        return 0.1
    return 0.5   # neutral


def _placement_score(house_num: int) -> float:
    """Score 0-1 based on house placement of the dispositor."""
    if house_num in KENDRA_HOUSES:
        return 1.0
    if house_num in TRIKONA_HOUSES:
        return 0.9
    if house_num in frozenset({2, 11}):
        return 0.7
    if house_num == 3:
        return 0.45
    if house_num == 6:
        return 0.35
    if house_num == 8:
        return 0.25
    if house_num == 12:
        return 0.30
    return 0.5   # 4, 5 already covered above; fallback


# ─── Chain builder ────────────────────────────────────────────────────────────

def compute_dispositor_chain(
        planet_name: str,
        planet_signs: Dict[str, int],
        planet_houses: Dict[str, int],
        shadbala_ratios: Optional[Dict[str, float]] = None,
        max_depth: int = 6,
) -> List[Dict]:
    """
    Trace the dispositor chain starting from `planet_name`.

    Returns a list of dicts (one per link), from the starting planet
    to the final dispositor:
        {
          "planet":   "VENUS",
          "sign":     5,          # sign index (0-11)
          "sign_name":"Virgo",
          "house":    4,          # natal house
          "is_own_sign": False,
          "is_exalted":  False,
          "is_debilitated": False,
          "is_final_disp": False, # True = chain ends here
          "dignity_score": 0.5,
          "placement_score": 1.0,
          "link_score": 0.75,     # combined strength of this link
          "shadbala_ratio": 1.1,  # from shadbala if provided
        }

    Chain terminates when:
        1. Planet is in its own sign      (final dispositor found)
        2. We encounter a repeated planet  (mutual dispositor cycle)
        3. max_depth is reached
    """
    if shadbala_ratios is None:
        shadbala_ratios = {}

    sign_names = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]

    chain: List[Dict] = []
    visited: List[str] = []
    current = planet_name

    for _ in range(max_depth):
        if current in visited:
            # Cycle detected — mark last node as mutual dispositor
            if chain:
                chain[-1]["is_mutual_dispositor"] = True
                chain[-1]["is_final_disp"] = True
            break
        visited.append(current)

        sign_idx = _planet_sign(current, planet_signs)
        if sign_idx is None:
            break
        house_num = planet_houses.get(current, 0)
        own   = _is_own_or_moola(current, sign_idx)
        exalt = _is_exalted(current, sign_idx)
        debi  = _is_debilitated(current, sign_idx)
        d_score = _dignity_score(current, sign_idx)
        p_score = _placement_score(house_num)
        sb  = shadbala_ratios.get(current, 0.5)
        sb_norm = min(1.0, sb / 1.5)           # 1.5× minimum = strong
        link_score = round((d_score * 0.35 + p_score * 0.35 + sb_norm * 0.30), 3)

        node = {
            "planet":           current,
            "sign":             sign_idx,
            "sign_name":        sign_names[sign_idx] if 0 <= sign_idx < 12 else "?",
            "house":            house_num,
            "is_own_sign":      own,
            "is_exalted":       exalt,
            "is_debilitated":   debi,
            "is_mutual_dispositor": False,
            "is_final_disp":    own or exalt,   # terminates here
            "dignity_score":    round(d_score, 3),
            "placement_score":  round(p_score, 3),
            "link_score":       link_score,
            "shadbala_ratio":   round(sb, 3),
        }
        chain.append(node)

        if own or exalt:
            break   # chain resolved at this planet

        # Follow to dispositor
        disp = _get_sign_lord(sign_idx)
        if disp is None or disp in RAHU_KETU:
            break
        current = disp

    return chain


def compute_all_chains(
        planet_signs: Dict[str, int],
        planet_houses: Dict[str, int],
        shadbala_ratios: Optional[Dict[str, float]] = None,
) -> Dict[str, List[Dict]]:
    """Compute dispositor chain for every planet (7 + Rahu/Ketu)."""
    all_planets = list(planet_signs.keys())
    return {
        p: compute_dispositor_chain(p, planet_signs, planet_houses, shadbala_ratios)
        for p in all_planets
    }


# ─── Dasha lord dispositor analysis ─────────────────────────────────────────

def analyze_dasha_lord_dispositor(
        dasha_planet: str,
        antardasha_planet: str,
        planet_signs: Dict[str, int],
        planet_houses: Dict[str, int],
        shadbala_ratios: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    High-level analysis of the dispositor chains for the active dasha lords.

    Returns:
        {
            "mahadasha_chain": [...],
            "antardasha_chain": [...],
            "mahadasha_final_dispositor": "VENUS",
            "antardasha_final_dispositor": "MERCURY",
            "mahadasha_chain_strength": 0.72,
            "antardasha_chain_strength": 0.55,
            "combined_strength": 0.64,
            "chain_verdict": "STRONG",         # STRONG / MODERATE / WEAK / BROKEN
            "interpretation": "..."
        }
    """
    if shadbala_ratios is None:
        shadbala_ratios = {}

    md_chain = compute_dispositor_chain(
        dasha_planet, planet_signs, planet_houses, shadbala_ratios)
    ad_chain = compute_dispositor_chain(
        antardasha_planet, planet_signs, planet_houses, shadbala_ratios)

    def _chain_strength(chain: List[Dict]) -> float:
        if not chain:
            return 0.3
        # Final dispositor's link_score is most important, average the rest
        final = chain[-1]["link_score"]
        if len(chain) == 1:
            return final
        midlinks = [c["link_score"] for c in chain[:-1]]
        mid_avg = sum(midlinks) / len(midlinks)
        # Chain strength: 60% final dispositor, 40% path average
        # But penalise each step (longer chain = more dilution)
        depth_penalty = max(0.0, 1.0 - 0.05 * (len(chain) - 1))
        return round(min(1.0, (0.60 * final + 0.40 * mid_avg) * depth_penalty), 3)

    def _final_disp_name(chain: List[Dict]) -> str:
        if not chain:
            return "UNKNOWN"
        return chain[-1]["planet"]

    def _has_trik_link(chain: List[Dict]) -> bool:
        return any(c["house"] in TRIK_HOUSES for c in chain[1:])   # skip root planet itself

    md_strength  = _chain_strength(md_chain)
    ad_strength  = _chain_strength(ad_chain)
    combined     = round(0.65 * md_strength + 0.35 * ad_strength, 3)

    verdict = (
        "STRONG"   if combined >= 0.70 else
        "MODERATE" if combined >= 0.50 else
        "WEAK"     if combined >= 0.30 else
        "BROKEN"
    )

    # Interpretation text
    md_final = _final_disp_name(md_chain)
    ad_final = _final_disp_name(ad_chain)
    trik_warn = ""
    if _has_trik_link(md_chain):
        trik_warn += f" {dasha_planet}'s chain passes through a trik house — results suppressed."
    if _has_trik_link(ad_chain):
        trik_warn += f" {antardasha_planet}'s chain passes through a trik house."

    interp = (
        f"Mahadasha {dasha_planet} is ultimately controlled by {md_final} "
        f"(chain strength {md_strength:.0%}). "
        f"Antardasha {antardasha_planet} resolves to {ad_final} "
        f"(chain strength {ad_strength:.0%}). "
        f"Combined dispositor strength: {combined:.0%} -> {verdict}."
        + trik_warn
    )

    return {
        "mahadasha_chain":              md_chain,
        "antardasha_chain":             ad_chain,
        "mahadasha_final_dispositor":   md_final,
        "antardasha_final_dispositor":  ad_final,
        "mahadasha_chain_strength":     md_strength,
        "antardasha_chain_strength":    ad_strength,
        "combined_strength":            combined,
        "chain_verdict":                verdict,
        "interpretation":               interp,
    }


# ─── NetworkX graph analysis ─────────────────────────────────────────────────

def compute_dispositor_graph(
        planet_signs: Dict[str, int],
        shadbala_ratios: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Build a directed dispositor graph using NetworkX and derive:
      - Mutual receptions (planet A owns sign of B, B owns sign of A)
      - Dispositor cycles (longer loops)
      - Final dispositors (planets with no outgoing edge = self-disposited)
      - Most-disposited planet (highest in-degree = controls most planets)
      - Isolated planets (lords of empty signs, not dispositing anyone)

    Nodes = planets.  Edge A → B = "A is disposited by B" (A sits in B's sign).

    Returns:
        {
          "mutual_receptions": List[Tuple[str, str]],
          "cycles": List[List[str]],        # included mutual receptions
          "final_dispositors": List[str],   # self-disposited (most powerful)
          "most_controlled_by": str,        # planet controlling most others
          "in_degree": Dict[str, int],
          "graph_summary": str,
        }
    """
    try:
        import networkx as nx
    except ImportError:
        return {"error": "networkx not installed"}

    if shadbala_ratios is None:
        shadbala_ratios = {}

    planets = list(planet_signs.keys())

    # Build dispositor mapping: planet → lord of its sign
    G = nx.DiGraph()
    G.add_nodes_from(planets)

    for pname in planets:
        sign_idx = planet_signs.get(pname)
        if sign_idx is None:
            continue
        lord = _get_sign_lord(sign_idx)
        if lord and lord != pname and lord in planet_signs:
            # Edge: pname is controlled by lord
            strength = shadbala_ratios.get(lord, 1.0)
            G.add_edge(pname, lord, weight=round(strength, 3))

    # ── Mutual receptions ──────────────────────────────────────────────────────
    mutual = []
    for a, b in list(G.edges()):
        if G.has_edge(b, a) and (b, a) not in [(x[1], x[0]) for x in mutual]:
            mutual.append((a, b))

    # ── All cycles (including mutual receptions) ───────────────────────────────
    try:
        raw_cycles = list(nx.simple_cycles(G))
        cycles = [c for c in raw_cycles if len(c) >= 2]
    except Exception:
        cycles = [[list(m) for m in mutual]]

    # ── Final dispositors (self-disposited: out-degree=0 in G, meaning no lord exists
    #    in the chart, OR planet is in its own sign) ───────────────────────────
    final_dispositors = [
        p for p in planets
        if G.out_degree(p) == 0 or _is_own_or_moola(p, planet_signs.get(p, -1))
    ]

    # ── Most-disposited (highest in-degree: most other planets feed into this one) ──
    in_degrees = dict(G.in_degree())
    most_controlled_by = max(in_degrees, key=lambda p: in_degrees[p]) if in_degrees else "NONE"

    # ── Summary text ────────────────────────────────────────────────────────────
    lines = []
    if final_dispositors:
        lines.append(f"Final dispositor(s): {', '.join(final_dispositors)} "
                     f"(self-ruled — highest independent authority in chart).")
    if mutual:
        pairs = [f"{a}↔{b}" for a, b in mutual]
        lines.append(f"Mutual receptions: {', '.join(pairs)} "
                     f"(these planets exchange power freely).")
    if cycles and any(len(c) > 2 for c in cycles):
        long_cycles = [c for c in cycles if len(c) > 2]
        lines.append(f"Dispositor cycles (length>2): "
                     f"{'; '.join(['→'.join(c) for c in long_cycles[:3]])}")
    if most_controlled_by and in_degrees.get(most_controlled_by, 0) > 1:
        lines.append(f"Most controlling planet: {most_controlled_by} "
                     f"(disposits {in_degrees[most_controlled_by]} others).")

    return {
        "mutual_receptions": mutual,
        "cycles": cycles,
        "final_dispositors": final_dispositors,
        "most_controlled_by": most_controlled_by,
        "in_degree": in_degrees,
        "graph_summary": " ".join(lines) if lines else "No special graph structures detected.",
    }
