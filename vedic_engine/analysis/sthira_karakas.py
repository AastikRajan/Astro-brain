"""
Sthira Karaka (Fixed Significator) Engine — Jaimini System.

Sthira Karakas are fixed planetary significators used EXCLUSIVELY in
Ayur (longevity) Dasha systems (Shoola Dasha, Niryana Shoola Dasha).

CRITICAL ROUTING RULE:
  - Ayur Dasha  (Shoola, Niryana Shoola) → use Sthira Karaka
  - Phalita Dasha (Chara, Narayana)       → use Chara Karaka
  - Sthira OVERRIDES Chara in all longevity/mortality modules.

S1  — Father:          stronger of SUN  vs VENUS  (Shadbala-based)
S2  — Mother:          stronger of MOON vs MARS   (Shadbala-based)
S3  — Younger sibling/brother-in-law:    MARS     (fixed constant)
S4  — Maternal uncle/relatives:          MERCURY  (fixed constant)
S5  — Paternal grandfather/husband/sons: JUPITER  (fixed constant)
S6  — Wife/parents-in-law/mat. gfather:  VENUS    (fixed constant)
S7  — Elder sibling / native longevity:  SATURN   (fixed constant)

Nodes (Rahu, Ketu) are excluded — no physical body → no physical death marker.

Source: Jaimini Upadesa Sutras; K.N. Rao commentary on Sthira Karakas.
"""
from __future__ import annotations
from typing import Dict, Optional


# ─── Sthira Karaka roles ──────────────────────────────────────────────────────

STHIRA_KARAKA_ROLES = {
    "father":              "stronger_of(SUN, VENUS)",
    "mother":              "stronger_of(MOON, MARS)",
    "younger_sibling":     "MARS",
    "maternal_uncle":      "MERCURY",
    "paternal_grandfather_husband_sons": "JUPITER",
    "wife_parents_in_law": "VENUS",
    "elder_sibling_longevity": "SATURN",
}

# Human-readable descriptions
STHIRA_KARAKA_DESCRIPTIONS = {
    "father":              "Father, paternal figures",
    "mother":              "Mother, maternal nourishment",
    "younger_sibling":     "Younger siblings, brother-in-law",
    "maternal_uncle":      "Maternal relatives, uncles",
    "paternal_grandfather_husband_sons": "Paternal grandfather, husband, sons",
    "wife_parents_in_law": "Wife/husband, parents-in-law, maternal grandfather",
    "elder_sibling_longevity": "Elder siblings, native's own longevity/health",
}

# Usage context
STHIRA_KARAKA_USAGE = (
    "Use ONLY in Ayur Dasha systems (Shoola, Niryana Shoola). "
    "For Phalita Dashas (Chara, Narayana) use Chara Karakas instead. "
    "In longevity/mortality modules, Sthira Karaka absolutely overrides Chara Karaka."
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _pick_stronger(
    planet_a: str,
    planet_b: str,
    shadbala: Optional[Dict[str, float]],
    planet_lons: Optional[Dict[str, float]],
) -> str:
    """
    Return the stronger of two planets using Shadbala ratios.
    Fallback: closer to 30° within sign (higher degree = stronger per Jaimini).
    If still tied: first argument wins.
    """
    if shadbala:
        sa = shadbala.get(planet_a, 0.5)
        sb = shadbala.get(planet_b, 0.5)
        if sa > sb:
            return planet_a
        if sb > sa:
            return planet_b
        # Equal Shadbala — fall through to longitude
    # Longitude fallback: higher degree within sign = stronger
    if planet_lons:
        la = planet_lons.get(planet_a, 0.0) % 30.0
        lb = planet_lons.get(planet_b, 0.0) % 30.0
        if la >= lb:
            return planet_a
        return planet_b
    return planet_a  # default


# ─── Main computation ─────────────────────────────────────────────────────────

def compute_sthira_karakas(
    shadbala_ratios: Optional[Dict[str, float]] = None,
    planet_lons: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Compute all 7 Sthira Karakas.

    Parameters
    ----------
    shadbala_ratios : {planet_name: ratio} — Shadbala strength ratios
    planet_lons     : {planet_name: sidereal longitude} — fallback for ties

    Returns
    -------
    dict with keys:
        karakas     : {role: planet_name}
        details     : list of {role, planet, description, notes}
        usage_note  : str (dasha routing guidance)
        rudra_candidates : dict (relevant for Shoola computations)
    """
    karakas: Dict[str, str] = {}

    # Variable (strength-dependent) Karakas
    karakas["father"] = _pick_stronger("SUN", "VENUS", shadbala_ratios, planet_lons)
    karakas["mother"] = _pick_stronger("MOON", "MARS", shadbala_ratios, planet_lons)

    # Fixed Karakas
    karakas["younger_sibling"]     = "MARS"
    karakas["maternal_uncle"]      = "MERCURY"
    karakas["paternal_grandfather_husband_sons"] = "JUPITER"
    karakas["wife_parents_in_law"] = "VENUS"
    karakas["elder_sibling_longevity"] = "SATURN"

    details = []
    for role, planet in karakas.items():
        is_variable = role in ("father", "mother")
        details.append({
            "role":        role,
            "planet":      planet,
            "description": STHIRA_KARAKA_DESCRIPTIONS[role],
            "type":        "variable (Shadbala-based)" if is_variable else "fixed constant",
        })

    # Rudra candidates (8th-house significators for death timing in Shoola)
    # Sthira Karaka for longevity = Saturn; for native's death = 8th lord context
    rudra_candidates_note = (
        "Rudra (death marker) for Shoola Dasha = stronger of 2nd lord vs 8th lord. "
        "Saturn (Sthira elder-sibling/longevity karaka) governs lifespan. "
        "Evaluate 8th house Prani Rudra for Niryana Shoola."
    )

    return {
        "karakas":         karakas,
        "details":         details,
        "usage_note":      STHIRA_KARAKA_USAGE,
        "rudra_note":      rudra_candidates_note,
        "father_planet":   karakas["father"],
        "mother_planet":   karakas["mother"],
        "longevity_planet": "SATURN",
    }


def get_sthira_karaka_for_role(
    role: str,
    shadbala_ratios: Optional[Dict[str, float]] = None,
    planet_lons: Optional[Dict[str, float]] = None,
) -> str:
    """
    Quick accessor: return the Sthira Karaka planet for a specific relative.

    role: 'father' | 'mother' | 'younger_sibling' | 'maternal_uncle' |
          'paternal_grandfather_husband_sons' | 'wife_parents_in_law' |
          'elder_sibling_longevity'
    """
    result = compute_sthira_karakas(shadbala_ratios, planet_lons)
    return result["karakas"].get(role, "SATURN")


def sthira_karaka_routing(dasha_type: str) -> str:
    """
    Returns 'sthira' or 'chara' based on the dasha system type.

    dasha_type: 'shoola' | 'niryana_shoola' → 'sthira'
                'chara'  | 'narayana' | 'trikona' → 'chara'
    """
    _AYUR_DASHAS = {"shoola", "niryana_shoola", "sthira"}
    return "sthira" if dasha_type.lower() in _AYUR_DASHAS else "chara"
