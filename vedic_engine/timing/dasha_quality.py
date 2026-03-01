"""
Dasha Quality Scoring — Ishta/Kashta Phala + Planet Maturity Ages.

Two distinct classical techniques for assessing HOW a dasha period will
manifest, as opposed to WHETHER it will (which is done by Promise gates):

══ 1. ISHTA PHALA / KASHTA PHALA (BPHS / Phaladeepika) ══════════════════
  The two "poles" of a planet's dasha delivery:

    Ishta Phala  = √(Uccha_Bala × Chesta_Bala)  — ease and grace of delivery
    Kashta Phala = √((60−Uccha_Bala) × (60−Chesta_Bala)) — toil and effort needed

  Both range 0–60 Shashtiamsas (Virupas).
    Ishta > Kashta → dasha delivers good results EASILY (grace)
    Kashta > Ishta → dasha delivers results through STRUGGLE / obstacles
    Balanced (≈ equal) → mixed dasha with peaks and valleys

  INTEGRATION: The Ishta/Kashta ratio transforms raw dasha confidence from
  a binary switch ("dasha is active") to a quality-weighted score.

══ 2. PLANET MATURITY AGES (classical / widely consistent across texts) ════
  A planet gives its FULL results only after its maturity age.
  Before maturity: results are partial, immature, or experienced symbolically.
  At/after age of maturity: full significations manifest in concrete life events.

  Applied: when predicting, if native's age < maturity age of the dasha planet,
  reduce the dasha confidence by the maturity_modifier factor.

Sources: BPHS Ch.35 (Ishta/Kashta), Phaladeepika, Jataka Parijata,
         Uttara Kalamrita (maturity ages), Devakeralam.
"""
from __future__ import annotations
import math
from typing import Dict, Optional

# ─── Ishta / Kashta constants ─────────────────────────────────────────────────

# Minimum Shadbala (in Rupas = Virupas/60) for each planet — used to normalise
# the Shadbala ratio to an approximate Uccha/Chesta pair when raw Bala values
# are not available.
_SHADBALA_MIN_RUPAS: Dict[str, float] = {
    "SUN":     6.5,
    "MOON":    6.0,
    "MARS":    5.0,
    "MERCURY": 7.0,
    "JUPITER": 6.5,
    "VENUS":   5.5,
    "SATURN":  5.0,
}

# ─── Planet Maturity Ages ─────────────────────────────────────────────────────

PLANET_MATURITY_AGE: Dict[str, int] = {
    "JUPITER": 16,
    "SUN":     22,
    "MOON":    24,
    "VENUS":   25,
    "MARS":    28,
    "MERCURY": 32,
    "SATURN":  36,
    "RAHU":    42,
    "KETU":    48,
}


# ─── Ishta / Kashta Phala ─────────────────────────────────────────────────────

def compute_ishta_kashta(
    planet: str,
    uccha_bala_virupas: Optional[float] = None,
    chesta_bala_virupas: Optional[float] = None,
    shadbala_ratio: Optional[float] = None,
) -> Dict:
    """
    Compute Ishta Phala and Kashta Phala for a planet.

    Formula (BPHS / Phaladeepika):
        Ishta  = √(Uccha_Bala × Chesta_Bala)
        Kashta = √((60 − Uccha_Bala) × (60 − Chesta_Bala))

    Both values range 0–60 Shashtiamsas.

    If raw Uccha/Chesta Bala are not provided, a proportional approximation
    is computed from the planet's Shadbala ratio using the minimum requirement
    as baseline:
        approx_bala ≈ shadbala_ratio × min_rupas × 60 / 2
        (half the total Shadbala is attributed to position, half to motion)

    Args:
        planet                : Planet name UPPERCASE
        uccha_bala_virupas    : Uccha (position/exaltation) Bala in Virupas (0–60)
        chesta_bala_virupas   : Chesta (motional) Bala in Virupas (0–60)
        shadbala_ratio        : Shadbala ratio (actual/minimum) — used if raw values absent

    Returns:
        Dict with ishta, kashta, quality (ratio), quality_label, notes
    """
    p = planet.upper()

    # ── Derive Uccha and Chesta from ratio if raw values not given ────────
    if uccha_bala_virupas is None or chesta_bala_virupas is None:
        ratio = shadbala_ratio if shadbala_ratio is not None else 0.8
        min_r = _SHADBALA_MIN_RUPAS.get(p, 6.0)
        # Approximate: treat half shadbala as uccha-type, half as chesta-type
        estimated_bala = ratio * min_r * 60.0 / 2.0  # in Virupas proxy
        uccha  = max(0.0, min(60.0, estimated_bala * 0.55))  # slight positional bias
        chesta = max(0.0, min(60.0, estimated_bala * 0.45))  # motional component
    else:
        uccha  = max(0.0, min(60.0, float(uccha_bala_virupas)))
        chesta = max(0.0, min(60.0, float(chesta_bala_virupas)))

    # ── Ishta and Kashta formulas ─────────────────────────────────────────
    ishta  = math.sqrt(uccha * chesta)
    kashta = math.sqrt((60.0 - uccha) * (60.0 - chesta))

    # ── Quality ratio: Ishta/(Ishta+Kashta) → 0.0 to 1.0 ────────────────
    total = ishta + kashta
    quality_ratio = ishta / total if total > 0 else 0.5

    # ── Quality label ─────────────────────────────────────────────────────
    if quality_ratio >= 0.70:
        quality_label = "GRACEFUL"
        note = "Dasha delivers results easily — natural flow, minimal obstacles."
    elif quality_ratio >= 0.55:
        quality_label = "FAVOURABLE"
        note = "Results come with modest effort. Positive overall dasha tone."
    elif quality_ratio >= 0.45:
        quality_label = "MIXED"
        note = "Balanced Ishta/Kashta. Peaks of gain alternating with effort periods."
    elif quality_ratio >= 0.30:
        quality_label = "LABOURED"
        note = "Kashta dominates. Results arrive only through sustained effort and delay."
    else:
        quality_label = "ARDUOUS"
        note = "Strongly Kashta-dominant. This dasha requires significant sacrifice to yield results."

    return {
        "planet":         p,
        "uccha_bala":     round(uccha, 2),
        "chesta_bala":    round(chesta, 2),
        "ishta_phala":    round(ishta, 2),
        "kashta_phala":   round(kashta, 2),
        "quality_ratio":  round(quality_ratio, 3),
        "quality_label":  quality_label,
        "notes":          note,
    }


# ─── Planet Maturity Age Modifier ─────────────────────────────────────────────

def maturity_modifier(planet: str, native_age: float) -> Dict:
    """
    Compute the maturity-age modifier for a planet's dasha predictions.

    Classical rule: A planet gives FULL results only after its maturity age.
    Three tiers:
      - Well below maturity (≥ 3 years short):  40% effectiveness
      - Approaching maturity (within 3 years):   70% effectiveness
      - At or past maturity:                    100% effectiveness

    Args:
        planet     : Planet name UPPERCASE
        native_age : Current age of the native in years (float)

    Returns:
        Dict with maturity_age, modifier, tier, notes
    """
    p = planet.upper()
    maturity_age = PLANET_MATURITY_AGE.get(p)
    if maturity_age is None:
        return {
            "planet":       p,
            "maturity_age": None,
            "modifier":     1.0,
            "tier":         "N/A",
            "notes":        f"{p} has no classical maturity age defined.",
        }

    years_short = maturity_age - native_age

    if years_short <= 0:
        modifier = 1.0
        tier = "MATURE"
        note = f"{p} has passed its maturity age ({maturity_age}). Full results expected."
    elif years_short <= 3:
        modifier = 0.70
        tier = "APPROACHING"
        note = (
            f"{p} matures at age {maturity_age} (native is {native_age:.1f}). "
            f"Partial results — matures in ~{years_short:.0f} year(s)."
        )
    else:
        modifier = 0.40
        tier = "IMMATURE"
        note = (
            f"{p} matures at age {maturity_age} (native is {native_age:.1f}, "
            f"{years_short:.0f} years short). Results symbolic or delayed."
        )

    return {
        "planet":       p,
        "maturity_age": maturity_age,
        "native_age":   round(native_age, 1),
        "years_short":  round(max(years_short, 0), 1),
        "modifier":     modifier,
        "tier":         tier,
        "notes":        note,
    }


# ─── Composite Dasha Quality Score ────────────────────────────────────────────

def dasha_quality_score(
    planet: str,
    native_age: float,
    shadbala_ratio: float = 1.0,
    is_yogakaraka: bool = False,
    is_functional_benefic: bool = False,
    is_retrograde: bool = False,
    d9_dignity: Optional[float] = None,
    uccha_bala_virupas: Optional[float] = None,
    chesta_bala_virupas: Optional[float] = None,
) -> Dict:
    """
    Composite dasha quality score (0–1) combining all classical factors.

    Component weights:
      Ishta/Kashta quality ratio  : 30%
      Shadbala sufficiency        : 25%
      Functional role for Lagna   : 20%
      D9 dignity confirmation     : 15%
      Retrograde modifier         : 10%

    The maturity modifier is applied as a FINAL GATE multiplier (not additive):
    even a strong dasha will be moderated if the native hasn't reached the
    planet's maturity age.

    Returns:
        Dict with total_score, quality_label, component_scores, notes
    """
    p = planet.upper()

    # ── Ishta/Kashta (30%) ─────────────────────────────────────────────────
    ik = compute_ishta_kashta(p, uccha_bala_virupas, chesta_bala_virupas, shadbala_ratio)
    c_ishta = ik["quality_ratio"]

    # ── Shadbala sufficiency (25%) ─────────────────────────────────────────
    c_shadbala = min(shadbala_ratio, 2.0) / 2.0   # normalise to 0–1 (2.0 = max practical)

    # ── Functional role for Lagna (20%) ────────────────────────────────────
    if is_yogakaraka:
        c_functional = 1.0
    elif is_functional_benefic:
        c_functional = 0.70
    else:
        c_functional = 0.40

    # ── D9 dignity (15%) ───────────────────────────────────────────────────
    c_d9 = d9_dignity if d9_dignity is not None else 0.5  # neutral if unknown

    # ── Retrograde modifier (10%) ──────────────────────────────────────────
    c_retro = 0.85 if is_retrograde else 1.0

    # ── Weighted composite ─────────────────────────────────────────────────
    total = (
        0.30 * c_ishta     +
        0.25 * c_shadbala  +
        0.20 * c_functional +
        0.15 * c_d9        +
        0.10 * c_retro
    )
    total = round(max(0.0, min(1.0, total)), 3)

    # ── Maturity gate ──────────────────────────────────────────────────────
    mat = maturity_modifier(p, native_age)
    final = round(total * mat["modifier"], 3)

    # ── Label ──────────────────────────────────────────────────────────────
    if final >= 0.70:
        label = "EXCELLENT DASHA"
    elif final >= 0.55:
        label = "GOOD DASHA"
    elif final >= 0.40:
        label = "MIXED DASHA"
    elif final >= 0.25:
        label = "DIFFICULT DASHA"
    else:
        label = "VERY DIFFICULT DASHA"

    return {
        "planet":           p,
        "dasha_quality":    final,
        "quality_label":    label,
        "maturity_tier":    mat["tier"],
        "maturity_modifier": mat["modifier"],
        "component_scores": {
            "ishta_kashta":  round(c_ishta, 3),
            "shadbala":      round(c_shadbala, 3),
            "functional":    round(c_functional, 3),
            "d9_dignity":    round(c_d9, 3),
            "retrograde":    round(c_retro, 3),
            "raw_composite": total,
        },
        "ishta_kashta_detail": ik,
        "maturity_detail":     mat,
    }


def dasha_quality_for_all_planets(
    planet_data: Dict[str, Dict],
    native_age: float,
) -> Dict[str, Dict]:
    """
    Compute dasha quality for multiple planets at once.

    Args:
        planet_data: {planet: {shadbala_ratio, is_yogakaraka, is_functional_benefic,
                               is_retrograde, d9_dignity}} — all fields optional
        native_age : Current age of the native

    Returns:
        {planet: dasha_quality_score_result}
    """
    results = {}
    for planet, data in planet_data.items():
        results[planet.upper()] = dasha_quality_score(
            planet        = planet,
            native_age    = native_age,
            shadbala_ratio       = data.get("shadbala_ratio", 1.0),
            is_yogakaraka        = data.get("is_yogakaraka", False),
            is_functional_benefic= data.get("is_functional_benefic", False),
            is_retrograde        = data.get("is_retrograde", False),
            d9_dignity           = data.get("d9_dignity"),
        )
    return results
