"""
Badhaka (Obstruction) Calculator — Friction Coefficient Engine.

Implements Parashari Badhaka Sthana logic as a probabilistic friction
coefficient, NOT a hard boolean deny function.

Badhaka house by ascendant modality:
  Movable (Aries/Cancer/Libra/Capricorn) : 11th house
  Fixed   (Taurus/Leo/Scorpio/Aquarius)  : 9th house
  Dual    (Gemini/Virgo/Sagittarius/Pisces): 7th house

Friction thresholds:
  High friction (40–50% reduction): Badhakesh is natural malefic
                                    AND in a dusthana (6/8/12)
  Moderate      (25–35%)          : Badhakesh is natural malefic
                                    but in a neutral house
  Low friction  (10–20% reduction): Badhakesh is functional benefic
                                    OR in kendra/trikona

Sanskrit etymology: "badh" = obstruction / harassment / delay — not denial.

Source: Deep Dive into Jyotish Logic.md (section "Badhaka Thresholds")
"""
from __future__ import annotations
from typing import Dict, Any, Optional

# ── Ascendant modality → Badhaka house ───────────────────────────────────────
# Sign indices 0-11: Aries=0, Taurus=1, ... Pisces=11
MOVABLE_SIGNS = {0, 3, 6, 9}   # Aries, Cancer, Libra, Capricorn
FIXED_SIGNS   = {1, 4, 7, 10}  # Taurus, Leo, Scorpio, Aquarius
DUAL_SIGNS    = {2, 5, 8, 11}  # Gemini, Virgo, Sagittarius, Pisces

BADHAKA_HOUSE = {
    "movable": 11,
    "fixed":    9,
    "dual":     7,
}

SIGN_LORDS = {
    0: "MARS",    1: "VENUS",   2: "MERCURY", 3: "MOON",
    4: "SUN",     5: "MERCURY", 6: "VENUS",   7: "MARS",
    8: "JUPITER", 9: "SATURN",  10: "SATURN", 11: "JUPITER",
}

NATURAL_MALEFICS = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}
NATURAL_BENEFICS = {"JUPITER", "VENUS", "MERCURY", "MOON"}

KENDRA_HOUSES   = {1, 4, 7, 10}
TRIKONA_HOUSES  = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}


def _modality_of(sign_idx: int) -> str:
    """Return 'movable', 'fixed', or 'dual' for a sign index."""
    if sign_idx in MOVABLE_SIGNS:
        return "movable"
    if sign_idx in FIXED_SIGNS:
        return "fixed"
    return "dual"


def get_badhaka_house(lagna_sign: int) -> Dict[str, Any]:
    """
    Determine the Badhaka Sthana (obstruction house) for a given ascendant.

    Returns:
        lagna_sign       : 0-11
        lagna_modality   : movable | fixed | dual
        badhaka_house    : 1-based house number
        badhaka_sign     : 0-11 sign index of the Badhaka house cusp
        badhakesh        : planet name that lords the Badhaka house
    """
    modality = _modality_of(lagna_sign)
    bh       = BADHAKA_HOUSE[modality]
    bh_sign  = (lagna_sign + bh - 1) % 12
    badhakesh = SIGN_LORDS[bh_sign]

    return {
        "lagna_sign": lagna_sign,
        "lagna_modality": modality,
        "badhaka_house": bh,
        "badhaka_sign": bh_sign,
        "badhakesh": badhakesh,
    }


def compute_badhaka_friction(
    lagna_sign: int,
    badhakesh_house: int,               # natal house of Badhakesh from lagna
    badhakesh_is_functional_benefic: bool = False,
    badhakesh_shadbala_ratio: float = 1.0,  # actual/required; < 1.0 = weak
    current_dasha_lord: Optional[str] = None,
    badhakesh: Optional[str] = None,    # planet name for comparison
    event_domain: str = "general",
) -> Dict[str, Any]:
    """
    Compute the Badhaka friction coefficient for a given prediction query.

    The friction coefficient reduces event probability — it does NOT deny events.

    High friction   (40–50%): malefic Badhakesh in dusthana → extreme delays + pain
    Moderate        (25–35%): malefic Badhakesh in neutral house
    Low friction    (10–20%): benefic/dignified Badhakesh → karmic learning delay

    Returns:
        friction_pct          : percentage REDUCTION to apply (0–50)
        friction_label        : "high" | "moderate" | "low" | "none"
        badhaka_active        : True if current Dasha lord IS the Badhakesh
        friction_multiplier   : (1.0 − friction_pct/100) to multiply into confidence
        note                  : human-readable narrative
    """
    bh_info   = get_badhaka_house(lagna_sign)
    badhakesh = badhakesh or bh_info["badhakesh"]

    is_natural_malefic = badhakesh.upper() in NATURAL_MALEFICS
    in_dusthana        = badhakesh_house in DUSTHANA_HOUSES
    in_kendra_trikona  = badhakesh_house in (KENDRA_HOUSES | TRIKONA_HOUSES)

    # ── Determine friction tier ──────────────────────────────────────
    if is_natural_malefic and in_dusthana and badhakesh_shadbala_ratio < 1.0:
        friction_pct = 50.0
        friction_label = "high"
        note = (
            f"EXTREME FRICTION: {badhakesh} (natural malefic) is placed in H{badhakesh_house} "
            f"(Dusthana) and has insufficient Shadbala (ratio {badhakesh_shadbala_ratio:.2f}). "
            f"For domain '{event_domain}': expect 40–50% probability reduction. "
            "Manifestation will occur with agonising delays, severe hurdles, "
            "or a deeply compromised form of the promised result."
        )
    elif is_natural_malefic and in_dusthana:
        friction_pct = 45.0
        friction_label = "high"
        note = (
            f"HIGH FRICTION: {badhakesh} (natural malefic) in H{badhakesh_house} (Dusthana). "
            f"Domain '{event_domain}' faces major obstructions. ~45% probability dampening."
        )
    elif is_natural_malefic and not in_kendra_trikona:
        # Upachaya houses (3, 6, 10, 11): growth through struggle → reduced long-term severity
        in_upachaya = badhakesh_house in {3, 6, 10, 11}
        if in_upachaya:
            friction_pct = 22.0
            friction_label = "moderate_reducing"
            note = (
                f"MODERATE (REDUCING): {badhakesh} (natural malefic) in Upachaya H{badhakesh_house}. "
                f"Domain '{event_domain}' faces initial struggle that diminishes over time — "
                "Upachaya forces native to develop skills that ultimately defeat the obstruction."
            )
        else:
            friction_pct = 30.0
            friction_label = "moderate"
            note = (
                f"MODERATE FRICTION: {badhakesh} (natural malefic) in neutral H{badhakesh_house}. "
                f"Domain '{event_domain}' faces meaningful delays. ~30% dampening."
            )
    elif is_natural_malefic and in_kendra_trikona:
        friction_pct = 20.0
        friction_label = "moderate_low"
        note = (
            f"MILD-MODERATE FRICTION: {badhakesh} (malefic) is well-placed in H{badhakesh_house} "
            f"(Kendra/Trikona). Obstructions are present but surmountable. ~20% dampening."
        )
    elif badhakesh_is_functional_benefic and in_kendra_trikona:
        friction_pct = 10.0
        friction_label = "low"
        note = (
            f"LOW FRICTION: {badhakesh} (functional benefic) is dignified in H{badhakesh_house}. "
            f"The 'obstruction' for domain '{event_domain}' is a karmic learning curve. "
            "The promised event will be delivered fully once the native aligns with the lesson. "
            "~10% probability dampening only."
        )
    else:
        friction_pct = 15.0
        friction_label = "low"
        note = (
            f"LOW FRICTION: {badhakesh} in H{badhakesh_house}. "
            f"Minor delays for domain '{event_domain}'. ~15% dampening."
        )

    # ── Check if current Dasha lord IS the Badhakesh ─────────────────
    badhaka_active = (
        current_dasha_lord is not None and
        current_dasha_lord.upper() == badhakesh.upper()
    )
    if badhaka_active:
        note += (
            f" ⚠ DASHA ACTIVE: {badhakesh} Mahadasha/Antardasha is currently running → "
            "the Badhaka friction is NOW OPERATIONAL. Delays/obstructions are manifest, "
            "not merely potential. Events promised by this period will require extraordinary "
            "effort and patience."
        )

    # ── Domain-specific modulation ────────────────────────────────────
    # Spiritual domains: Badhaka paradoxically ELEVATES inner growth.
    # Health domains: Badhaka is EXTREME — worse than Maraka for illness.
    _domain_lower = event_domain.lower()
    if _domain_lower in ("spiritual", "dharma", "moksha"):
        # Badhaka period spectacularly benefits spiritual growth
        friction_pct = max(0.0, friction_pct - 25.0)  # reduce friction heavily
        if friction_pct <= 5.0:
            friction_pct = -10.0  # net POSITIVE effect for spiritual domains
            friction_label = "spiritual_boost"
            note += (
                " SPIRITUAL DOMAIN: Badhaka period dissolves ego and accelerates "
                "inner growth — paradoxical net positive for spiritual pursues."
            )
    elif _domain_lower in ("health", "medical", "longevity"):
        # Badhaka governs unseen obstacles, misdiagnoses, sudden trauma
        friction_pct = min(60.0, friction_pct * 1.35)  # amplify by 35%, cap at 60%
        friction_label = "extreme_health" if friction_pct > 40 else friction_label
        note += (
            " HEALTH DOMAIN: Badhaka governs severe medical misdiagnoses, "
            "sudden physical trauma, and hard-to-cure diseases. "
            "Combined Maraka+Badhaka dasha can prove fatal if longevity expired."
        )

    friction_multiplier = round(1.0 - friction_pct / 100.0, 3)

    return {
        "lagna_sign": lagna_sign,
        "badhaka_house": bh_info["badhaka_house"],
        "badhakesh": badhakesh,
        "badhakesh_house": badhakesh_house,
        "is_natural_malefic": is_natural_malefic,
        "badhakesh_is_functional_benefic": badhakesh_is_functional_benefic,
        "in_dusthana": in_dusthana,
        "friction_pct": friction_pct,
        "friction_label": friction_label,
        "friction_multiplier": friction_multiplier,
        "badhaka_active_in_dasha": badhaka_active,
        "current_dasha_lord": current_dasha_lord,
        "event_domain": event_domain,
        "note": note,
    }


def apply_badhaka_to_confidence(
    confidence: float,
    friction_multiplier: float,
    badhaka_active_in_dasha: bool,
) -> float:
    """
    Apply the Badhaka friction multiplier to a raw confidence score.

    If Badhaka Dasha is active, the friction is doubled for the timing window.
    """
    if badhaka_active_in_dasha:
        # Amplify the penalty while Badhakesh runs as Dasha lord
        effective_friction = 1.0 - (1.0 - friction_multiplier) * 1.5
        effective_friction = max(0.2, effective_friction)   # never reduce below 20% chance
    else:
        effective_friction = friction_multiplier

    return max(0.0, min(1.0, confidence * effective_friction))
