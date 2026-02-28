"""
Vimshopak Bala Engine.
Evaluates planet strength across divisional charts with weighted scoring.
Max score = 20 (sum of all weights).

Research Brief (Jyotish Logic Architecture):
  Shadvarga scheme (6-chart, classical Parashara):
    D1=6, D9=5, D3=4, D2=2, D12=2, D30=1  (total = 20)
  Shodashavarga scheme (16-chart, detailed) via VIMSHOPAK_WEIGHTS config.

  Degradation scale (0-20 proportional):
    Own/Moolatrikona  = 20/20 = full weight (1.000)
    Great Friend      = 18/20 → multiplier 0.900
    Friend            = 15/20 → multiplier 0.750
    Neutral           = 10/20 → multiplier 0.500
    Enemy             =  7/20 → multiplier 0.350
    Great Enemy       =  5/20 → multiplier 0.250
    Debilitated       =  0/20 → multiplier 0.000

  Score interpretation tiers:
    15–20  → HIGH:     deep contentment, frictionless excellence
    10–15  → AVERAGE:  mixed results; oscillates with transits
    < 10   → LOW:      results manifest (Shadbala) but bring frustration, no joy

  Shadbala vs Vimshopak distinction:
    Shadbala = QUANTITY/FORCE of events
    Vimshopaka = QUALITY/CONTENTMENT of experience

  Domain targeting: high score benefits Karakatwa domains + lordship domains.
"""
from __future__ import annotations
from typing import Dict, List, Optional

from vedic_engine.config import (
    Planet, Dignity, VIMSHOPAK_WEIGHTS, VIMSHOPAK_MAX
)
from vedic_engine.core.divisional import get_varga, VARGA_FUNCTIONS
from vedic_engine.strength.shadbala import _get_dignity, _P

# ─── Corrected degradation multipliers per Research Brief ────────────────
# Great Friend=18/20, Friend=15/20, Neutral=10/20, Enemy=7/20, Great Enemy=5/20
DIGNITY_MULTIPLIERS = {
    Dignity.EXALTED:       1.000,
    Dignity.MOOLATRIKONA:  1.000,
    Dignity.OWN:           1.000,
    Dignity.GREAT_FRIEND:  0.900,   # 18/20
    Dignity.FRIEND:        0.750,   # 15/20
    Dignity.NEUTRAL:       0.500,   # 10/20
    Dignity.ENEMY:         0.350,   #  7/20
    Dignity.GREAT_ENEMY:   0.250,   #  5/20
    Dignity.DEBILITATED:   0.000,   #  0/20
}

# ─── Shadvarga weights (6-chart classical scheme) ─────────────────────────
# D1=6, D9=5, D3=4, D2=2, D12=2, D30=1
_SHADVARGA_WEIGHTS: Dict[int, float] = {
    1: 6.0,    # Rasi
    2: 2.0,    # Hora
    3: 4.0,    # Drekkana
    9: 5.0,    # Navamsa
    12: 2.0,   # Dwadasamsa
    30: 1.0,   # Trimsamsa
}
_SHADVARGA_MAX = 20.0  # same 20-point scale

# ─── Score interpretation tiers ──────────────────────────────────────────
def interpret_vimshopak_score(score: float, max_score: float = 20.0) -> Dict:
    """
    Research Brief quality tier interpretation.

    HIGH (15-20):    Deep contentment; frictionless; domain excellence guaranteed
    AVERAGE (10-15): Mixed results; oscillation; transit-dependent
    LOW (< 10):      Results manifest (Shadbala active) but bring deep frustration;
                     success without happiness; high Shadbala + low Vimshopak =
                     'acquires job but extremely stressed, no recognition'

    Critically: Karakatwa (living significations) destroyed before Lordship.
    """
    pct = score / max_score * 100

    if score >= 15.0:
        return {
            "tier": "HIGH",
            "pct": round(pct, 1),
            "quality": "Exceptional contentment and excellency in domain",
            "detail": (f"Score {score:.1f}/20. Deep qualitative fulfillment during Dasha. "
                       "Karakatwa (natural significations) deliver joy; Lordship domains excel."),
        }
    elif score >= 10.0:
        return {
            "tier": "AVERAGE",
            "pct": round(pct, 1),
            "quality": "Mixed; oscillation with transits",
            "detail": (f"Score {score:.1f}/20. Mediocre quality experience. Success alternates "
                       "with dissatisfaction. Highly transit-dependent in Antardasha periods."),
        }
    else:
        return {
            "tier": "LOW",
            "pct": round(pct, 1),
            "quality": "Force without joy (Shadbala may be high)",
            "detail": (f"Score {score:.1f}/20. CRITICAL: Planet has force (check Shadbala) but "
                       "events arrive without subjective happiness. Job acquired = high stress. "
                       "Marriage acquired = emotional emptiness. Karakatwa significations burned."),
        }


def compute_vimshopak(planet: str, natal_longitude: float) -> Dict:
    """
    Compute Vimshopak Bala for one planet (Shodashavarga scheme).
    Returns score (0-20) and per-varga breakdown with quality interpretation.
    """
    p = _P.get(planet)
    if p is None:
        return {"planet": planet, "score": 0.0, "breakdown": {}}

    total = 0.0
    breakdown = {}

    for d, weight in VIMSHOPAK_WEIGHTS.items():
        if d not in VARGA_FUNCTIONS:
            continue
        varga_sign = get_varga(natal_longitude, d)
        # Get dignity in that varga sign
        varga_lon = varga_sign * 30.0  # center of the sign
        dignity = _get_dignity(planet, varga_lon)
        mult = DIGNITY_MULTIPLIERS.get(dignity, 0.5)
        contribution = weight * mult
        total += contribution
        breakdown[f"D{d}"] = {
            "sign": varga_sign,
            "dignity": dignity.value,
            "weight": weight,
            "contribution": round(contribution, 3),
        }

    interpretation = interpret_vimshopak_score(total, VIMSHOPAK_MAX)
    return {
        "planet": planet,
        "score": round(total, 3),
        "max_possible": VIMSHOPAK_MAX,
        "percentage": round(total / VIMSHOPAK_MAX * 100, 1),
        "tier": interpretation["tier"],
        "quality": interpretation["quality"],
        "interpretation": interpretation,
        "breakdown": breakdown,
    }


def compute_shadvarga_vimshopak(planet: str, natal_longitude: float) -> Dict:
    """
    Compute Vimshopak Bala using classical Shadvarga scheme (6 charts).
    Research Brief: D1=6, D9=5, D3=4, D2=2, D12=2, D30=1 → total 20 pts.

    This is the simpler classical 6-chart scheme as opposed to Shodashavarga.
    Provides cleaner signal for Karakatwa + Lordship quality assessment.
    """
    p = _P.get(planet)
    if p is None:
        return {"planet": planet, "shadvarga_score": 0.0, "breakdown": {}}

    total = 0.0
    breakdown = {}

    for d, weight in _SHADVARGA_WEIGHTS.items():
        if d not in VARGA_FUNCTIONS:
            continue
        varga_sign = get_varga(natal_longitude, d)
        varga_lon  = varga_sign * 30.0
        dignity    = _get_dignity(planet, varga_lon)
        mult       = DIGNITY_MULTIPLIERS.get(dignity, 0.5)
        contribution = weight * mult
        total += contribution
        breakdown[f"D{d}"] = {
            "sign": varga_sign,
            "dignity": dignity.value,
            "weight": weight,
            "contribution": round(contribution, 3),
        }

    interpretation = interpret_vimshopak_score(total, _SHADVARGA_MAX)
    return {
        "planet": planet,
        "shadvarga_score": round(total, 3),
        "shadvarga_max": _SHADVARGA_MAX,
        "shadvarga_pct": round(total / _SHADVARGA_MAX * 100, 1),
        "tier": interpretation["tier"],
        "quality": interpretation["quality"],
        "interpretation": interpretation,
        "breakdown": breakdown,
    }


def compute_all_vimshopak(planet_longitudes: Dict[str, float]) -> Dict[str, Dict]:
    """Compute Vimshopak (Shodashavarga) for all available planets."""
    return {p: compute_vimshopak(p, lon) for p, lon in planet_longitudes.items() if p in _P}


def compute_all_shadvarga(planet_longitudes: Dict[str, float]) -> Dict[str, Dict]:
    """Compute Shadvarga Vimshopak for all available planets."""
    return {p: compute_shadvarga_vimshopak(p, lon) for p, lon in planet_longitudes.items() if p in _P}


# ─── Natural Karakatwa domains per planet (Research Brief) ────────────────
_PLANET_KARAKATWA: Dict[str, List[str]] = {
    "SUN":     ["soul", "father", "authority", "government", "career_status", "health_vitality"],
    "MOON":    ["mind", "mother", "emotions", "public", "food", "liquid"],
    "MARS":    ["siblings", "courage", "competition", "land", "engineering", "surgery"],
    "MERCURY": ["intellect", "communication", "trade", "siblings", "education", "writing"],
    "JUPITER": ["wisdom", "children", "teachers", "husband_male", "wealth", "dharma"],
    "VENUS":   ["marriage", "romance", "vehicles", "luxury", "arts", "wife_female"],
    "SATURN":  ["longevity", "karma", "service", "poverty", "delay", "discipline"],
    "RAHU":    ["foreign", "illusion", "unconventional", "technology", "sudden_gain"],
    "KETU":    ["spirituality", "liberation", "past_karma", "occult", "detachment"],
}


def get_karakatwa_quality(
    planet: str,
    vimshopak_score: float,
    max_score: float = 20.0,
) -> Dict:
    """
    Research Brief: High Vimshopak score guarantees excellence specifically in
    the planet's Karakatwa (natural significations) and house lordship domains.

    Returns domain-specific interpretation:
    - HIGH (>=15): exceptional quality in all natural significations
    - AVERAGE (10-15): mixed; some domains good, others frustrated
    - LOW (<10): events manifest (Shadbala-driven) but without joy
    """
    tier = interpret_vimshopak_score(vimshopak_score, max_score)
    karakatwa = _PLANET_KARAKATWA.get(planet.upper(), [])

    if tier["tier"] == "HIGH":
        status = {d: "excellent_quality" for d in karakatwa}
        note   = "Guaranteed frictionless quality in all natural and lordship domains."
    elif tier["tier"] == "AVERAGE":
        status = {d: "mixed_quality" for d in karakatwa}
        note   = "Transit-dependent; some domains thrive in favorable sub-periods."
    else:
        status = {d: "force_without_joy" for d in karakatwa}
        note   = ("Events in these domains WILL occur (if Shadbala is strong) "
                  "but native will feel deep dissatisfaction. Stress, clashes, "
                  "lack of recognition across all natural significations.")

    return {
        "planet": planet,
        "tier": tier["tier"],
        "karakatwa_domains": karakatwa,
        "domain_status": status,
        "note": note,
    }
