"""
Planetary Avasthas (States of Existence) — Three Classical Systems.

Implements per-planet state and strength modifier for:
  1. Baladi Avasthas   — age/maturation state from sign position (5 states)
  2. Shayanadi Avasthas— subconscious activity state (12 states, complex formula)
  3. Deeptadi Avasthas — dignity-based illumination state (9 states)

Research source:
  "Vedic Astrology Computational Rules.md" (File 2) — Part A
  BPHS Ch. 45 / Phaladeepika / Sarvartha Chintamani

All functions follow the ARCHITECTURE RULE:
  Core computation only — returns dicts; does NOT modify prediction pipeline.
  Caller stores results in static["computed"]["avasthas"].

ADDED 2026-03-02: Phase 1B — new module.
"""
from __future__ import annotations
import math
from datetime import datetime
from typing import Dict, List, Optional

from vedic_engine.core.coordinates import normalize, nakshatra_of


# ─── Constants ────────────────────────────────────────────────────────────────

# 5 × 6° segments per sign; ODD sign sequence → EVEN sign reverses
_BALADI_STATES = ["Bala", "Kumara", "Yuva", "Vriddha", "Mrita"]

# Base multipliers (Research File 2, Table 1)
_BALADI_BASE_MULTIPLIER: Dict[str, float] = {
    "Bala":    0.25,   # Infant: 25%
    "Kumara":  0.50,   # Adolescent: 50%
    "Yuva":    1.00,   # Youth/Prime: 100%
    "Vriddha": 0.10,   # Old Age: 10%  (override for Moon/Saturn → effective 1.0)
    "Mrita":   0.00,   # Dead: 0%
}

# Odd sign indices (0-based): Aries=0, Gemini=2, Leo=4, Libra=6, Sag=8, Aquarius=10
_ODD_SIGNS = {0, 2, 4, 6, 8, 10}

# Planetary constants for Shayanadi formula (Research File 2):
# P index: Sun=1,Moon=2,Mars=3,Mercury=4,Jupiter=5,Venus=6,Saturn=7,Rahu=8,Ketu=9
_SHAYANADI_P_INDEX: Dict[str, int] = {
    "SUN": 1, "MOON": 2, "MARS": 3, "MERCURY": 4,
    "JUPITER": 5, "VENUS": 6, "SATURN": 7, "RAHU": 8, "KETU": 9,
}

# Planetary additament (D_p) for Shayanadi sub-state (Research File 2):
_SHAYANADI_ADDITAMENT: Dict[str, int] = {
    "SUN": 5, "MOON": 2, "MARS": 2, "MERCURY": 3,
    "JUPITER": 5, "VENUS": 3, "SATURN": 3, "RAHU": 4, "KETU": 4,
}

# 12 Shayanadi states by index (1=Shayana … 12=Nidra)
_SHAYANADI_STATES: List[str] = [
    "",             # placeholder (index 0 unused)
    "Shayana",      # 1 – resting/sleeping
    "Upavesana",    # 2 – sitting/observing
    "Netrapani",    # 3 – hand on eye, peering; very auspicious for benefics
    "Prakasana",    # 4 – shining/illuminating
    "Gamana",       # 5 – moving/wandering
    "Agamana",      # 6 – returning/approaching (outward)
    "Sabha",        # 7 – in assembly/court
    "Agama",        # 8 – steadily advancing/impending
    "Bhojana",      # 9 – eating/consuming  [dangerous for malefics]
    "Nrityalipsa",  # 10 – desire to dance; chaotic
    "Kautuka",      # 11 – eager/curious; wealth-giving
    "Nidra",        # 12 – dormant/asleep
]

# Sub-state multiplier by (S_p % 3) output:
# 0 → Vicheshta (Nil/0%), 1 → Drishti (Medium/50%), 2 → Cheshta (Full/100%)
_SHAYANADI_SUB_LABEL = {0: "Vicheshta", 1: "Drishti", 2: "Cheshta"}
_SHAYANADI_SUB_MULTIPLIER = {0: 0.0, 1: 0.5, 2: 1.0}

# Deeptadi: dignity conditions → state label and quality multiplier
_DEEPTADI_MAP = [
    # (condition_key, label, multiplier)
    # Research: Kopa = combust = 0.00 (severe negative, eclipsed ability)
    # Vikala = malefic conjunction = 0.05 (near-zero, crippled)
    # Khala = great enemy/debilitated = 0.00 (subtractive, wicked)
    # Dukhita = enemy sign = 0.0625 (severely distressed, barely functional)
    ("kopa",      "Kopa",      0.00),    # combust — eclipsed, 0% delivery
    ("vikala",    "Vikala",    0.05),    # malefic conjunction — crippled
    ("khala",     "Khala",     0.00),    # great enemy / debilitated — wicked/nil
    ("dukhita",   "Dukhita",   0.0625),  # enemy sign — miserable
    ("dina",      "Dina",      0.125),   # neutral sign — distressed
    ("shanta",    "Shanta",    0.25),    # friend's sign — peaceful
    ("pramudita", "Pramudita", 0.375),   # great friend's sign — delighted
    ("swastha",   "Swastha",   0.625),   # own / moolatrikona — comfortable
    ("deepta",    "Deepta",    1.0),     # exalted — blazing/radiant
]

# Combustion orbs per planet (degrees from Sun, sidereal)
_COMBUSTION_ORBS: Dict[str, float] = {
    "MOON": 12.0, "MARS": 17.0, "MERCURY": 14.0, "JUPITER": 11.0,
    "VENUS": 10.0, "SATURN": 15.0,
}

# Dignity enum import (resolves at call time to avoid circular import)
_DIGNITY_CACHE = {}
def _get_dignity_order():
    if not _DIGNITY_CACHE:
        from vedic_engine.config import Dignity
        _DIGNITY_CACHE["mod"] = Dignity
    return _DIGNITY_CACHE["mod"]


# ─── 1. Baladi Avasthas ───────────────────────────────────────────────────────

def compute_baladi_avasthas(
    planet_lons: Dict[str, float],
) -> Dict[str, Dict]:
    """
    Compute Baladi Avasthas for all planets in planet_lons.

    Algorithm (Research File 2, BPHS Ch.45):
      sign_degree = planet_longitude % 30  → position within sign (0–30°)
      segment     = floor(sign_degree / 6) → 0–4 (five 6° segments)
      ODD signs:  [Bala, Kumara, Yuva, Vriddha, Mrita] (ascending)
      EVEN signs: [Mrita, Vriddha, Yuva, Kumara, Bala] (reversed)

    Planet overrides (classical BPHS exceptions):
      Sun, Mars     → always peak at Bala (return 1.00 when in Bala state)
      Jupiter,Venus → follow standard (peak 1.00 at Yuva)
      Moon, Saturn  → treated as peak at Vriddha (return 1.00 in Vriddha)
      Mercury       → immune to Baladi; always 1.00

    Returns dict: {planet_name: {"avastha": str, "multiplier": float}}
    ADDED 2026-03-02: Phase 1B.
    """
    result = {}
    for planet, lon in planet_lons.items():
        sign_idx   = int(lon / 30) % 12
        deg_in_sign = lon % 30
        segment    = min(int(deg_in_sign / 6), 4)  # 0–4

        # EVEN signs reverse the order
        if sign_idx not in _ODD_SIGNS:
            segment = 4 - segment

        avastha   = _BALADI_STATES[segment]
        base_mult = _BALADI_BASE_MULTIPLIER[avastha]

        # Apply planet-specific overrides
        p = planet.upper()
        if p == "MERCURY":
            multiplier = 1.0
        elif p in ("SUN", "MARS"):
            # Peak at Bala; standard otherwise
            multiplier = 1.0 if avastha == "Bala" else base_mult
        elif p in ("MOON", "SATURN"):
            # Peak (effective 1.0) at Vriddha; others standard
            multiplier = 1.0 if avastha == "Vriddha" else base_mult
        else:
            multiplier = base_mult

        result[planet] = {
            "avastha":    avastha,
            "multiplier": round(multiplier, 4),
            "sign_idx":   sign_idx,
            "segment":    segment,
            "is_odd_sign": sign_idx in _ODD_SIGNS,
        }
    return result


# ─── 2. Shayanadi Avasthas ────────────────────────────────────────────────────

def compute_shayanadi_avasthas(
    planet_lons: Dict[str, float],
    moon_lon: float,
    lagna_sign: int,               # 0-11 (Aries=0)
    birth_dt: datetime,
    sunrise_hour: float = 6.0,
    name_syllable_anka: int = 1,   # Anka of first syllable (default=1 when unknown)
) -> Dict[str, Dict]:
    """
    Compute Shayanadi (12-state activity) Avasthas for all planets.

    Base-state formula (Research File 2, Sayana-etc-Avastha algorithm):
      N_p  = planet nakshatra (1–27, Ashwini=1)
      P_p  = planet constant index (Sun=1..Saturn=7..Ketu=9)
      NA_p = planet Navamsha within sign (1–9)
      N_m  = Moon nakshatra (1–27)
      IG   = Ishta Ghati (integer Ghatis elapsed since sunrise; 1 Ghati=24 min)
      L    = Lagna sign (Aries=1..Pisces=12)

      Base index I_p = (N_p × P_p × NA_p × N_m × IG × L) % 12
      If I_p == 0 → default to 12 (Nidra)

    Sub-state (intensity):
      Raw      = (I_p^2 + Anka) % 12 [if 0 → 12]
      S_p      = (Raw + D_p) % 3
      sub_intensity from {0: Vicheshta/nil, 1: Drishti/50%, 2: Cheshta/100%}

    ADDED 2026-03-02: Phase 1B.
    """
    # Ghati calculation
    birth_hour = birth_dt.hour + birth_dt.minute / 60.0 + birth_dt.second / 3600.0
    elapsed_min = (birth_hour - sunrise_hour) * 60.0
    if elapsed_min < 0:
        elapsed_min += 24 * 60   # handle pre-sunrise births: use previous day count
    ishta_ghati = max(1, int(elapsed_min / 24))  # 1 ghati = 24 minutes

    moon_nak_idx = int(moon_lon / (360 / 27)) % 27   # 0-based
    N_m = moon_nak_idx + 1                             # 1-27
    L   = lagna_sign + 1                               # 1-12

    result = {}
    for planet, lon in planet_lons.items():
        p = planet.upper()
        P_p  = _SHAYANADI_P_INDEX.get(p, 1)
        D_p  = _SHAYANADI_ADDITAMENT.get(p, 1)

        N_p  = (int(lon / (360 / 27)) % 27) + 1         # nakshatra 1-27
        deg_in_sign = lon % 30
        NA_p = int(deg_in_sign / (30 / 9)) + 1          # navamsha 1-9 within sign
        NA_p = min(NA_p, 9)

        IG   = ishta_ghati

        product = N_p * P_p * NA_p * N_m * IG * L
        I_p  = product % 12
        if I_p == 0:
            I_p = 12

        # Sub-state
        raw_sq = (I_p ** 2 + name_syllable_anka) % 12
        if raw_sq == 0:
            raw_sq = 12
        S_p = (raw_sq + D_p) % 3

        avastha    = _SHAYANADI_STATES[I_p]
        sub_label  = _SHAYANADI_SUB_LABEL[S_p]
        sub_mult   = _SHAYANADI_SUB_MULTIPLIER[S_p]

        result[planet] = {
            "avastha":         avastha,
            "base_index":      I_p,
            "sub_state":       sub_label,
            "sub_multiplier":  sub_mult,
            "ishta_ghati":     IG,
        }
    return result


# ─── 3. Deeptadi Avasthas ────────────────────────────────────────────────────

def compute_deeptadi_avasthas(
    planet_dignities: Dict[str, str],        # {planet: dignity_key str like "EXALTED"}
    planet_lons: Dict[str, float],
    sun_lon: float,
    malefic_conjunction_planets: Optional[Dict[str, List[str]]] = None,
    retrograde_planets: Optional[Dict[str, bool]] = None,
) -> Dict[str, Dict]:
    """
    Compute Deeptadi (9-state dignity-based) Avasthas for all planets.

    Hierarchy (Research File 2, Part A.3):
      Kopa      : combust (within Sun orb) — overrides ALL including exaltation
      Vikala    : conjunct natural malefic (Mars/Saturn/Rahu/Ketu) within 5°
      Khala     : placed in great enemy / debilitation sign
      Dukhita   : placed in enemy sign
      Dina      : placed in neutral sign
      Shanta    : placed in friend sign
      Pramudita : placed in great friend sign
      Swastha   : own or moolatrikona sign
      Deepta    : exalted sign

    Combination rules (Research: BPHS/Phaladeepika):
      - Combustion (Kopa) + Exaltation (Deepta) → Kopa wins (0.00)
      - Retrograde + Debilitation (Khala) → classical double-negative → Deepta (1.00)
      - Mrita (Baladi) + Retrograde → Baladi handled separately; Mrita=0.00 wins

    multiplier → used as quality coefficient for dasha/prediction layers.
    ADDED 2026-03-02: Phase 1B.
    """
    _DIGNITY_TO_DEEPTADI = {
        "EXALTED":      "deepta",
        "MOOLATRIKONA": "swastha",
        "OWN":          "swastha",
        "GREAT_FRIEND": "pramudita",
        "FRIEND":       "shanta",
        "NEUTRAL":      "dina",
        "ENEMY":        "dukhita",
        "GREAT_ENEMY":  "khala",
        "DEBILITATED":  "khala",
    }

    _STATE_TO_LABEL_MULT = {k: (label, mult) for k, label, mult in _DEEPTADI_MAP}

    NATURAL_MALEFICS = {"MARS", "SATURN", "RAHU", "KETU"}
    VIKALA_ORB = 5.0   # degrees

    result = {}
    for planet, lon in planet_lons.items():
        p = planet.upper()
        if p == "SUN":
            continue   # Sun cannot be combust itself

        # ── Check Kopa (combustion) ──
        orb = _COMBUSTION_ORBS.get(p, 0.0)
        if orb > 0:
            arc = abs((lon - sun_lon + 180) % 360 - 180)
            if arc <= orb:
                label, mult = _STATE_TO_LABEL_MULT["kopa"]
                pct = round((1.0 - arc / orb) * 100, 1)
                result[planet] = {
                    "avastha": label,
                    "condition": "kopa",
                    "multiplier": mult,
                    "combust_pct": pct,
                }
                continue

        # ── Check Vikala (malefic conjunction) ──
        if malefic_conjunction_planets:
            conj_mal = malefic_conjunction_planets.get(p, [])
            if conj_mal:
                label, mult = _STATE_TO_LABEL_MULT["vikala"]
                result[planet] = {
                    "avastha": label,
                    "condition": "vikala",
                    "multiplier": mult,
                    "conjunct_malefics": conj_mal,
                }
                continue

        # ── Spatial dignity state ──
        dignity_key = (planet_dignities.get(planet)
                       or planet_dignities.get(p, "NEUTRAL"))
        condition   = _DIGNITY_TO_DEEPTADI.get(dignity_key, "dina")

        # Combination rule: Retrograde + Debilitated/Great-Enemy → Deepta (exalted)
        # Classical double-negative logic (Uttara Kalamrita): retro planet in
        # debilitation acts as if exalted. BUT Kopa (combustion) still overrides.
        is_retro = (retrograde_planets or {}).get(p, False)
        if is_retro and condition == "khala":
            condition = "deepta"  # double-negative inversion

        label, mult = _STATE_TO_LABEL_MULT.get(condition, ("Dina", 0.125))

        result[planet] = {
            "avastha":   label,
            "condition": condition,
            "multiplier": mult,
            "dignity":   dignity_key,
            "retro_inversion": (is_retro and dignity_key in ("DEBILITATED", "GREAT_ENEMY")),
        }

    # Sun gets Deepta / Swastha / Dina based on its own dignity
    sun_dig = planet_dignities.get("SUN") or planet_dignities.get("sun", "NEUTRAL")
    sun_cond = _DIGNITY_TO_DEEPTADI.get(sun_dig, "dina")
    sun_label, sun_mult = _STATE_TO_LABEL_MULT.get(sun_cond, ("Dina", 0.125))
    result["SUN"] = {
        "avastha": sun_label, "condition": sun_cond,
        "multiplier": sun_mult, "dignity": sun_dig,
    }

    return result


# ─── Master entry point ───────────────────────────────────────────────────────

def compute_all_avasthas(
    planet_lons: Dict[str, float],
    planet_dignities: Dict[str, str],
    moon_lon: float,
    sun_lon: float,
    lagna_sign: int,
    birth_dt: datetime,
    sunrise_hour: float = 6.0,
    combustion_data: Optional[Dict[str, float]] = None,
    malefic_conjunctions: Optional[Dict[str, List[str]]] = None,
    retrograde_planets: Optional[Dict[str, bool]] = None,
) -> Dict[str, Dict]:
    """
    Compute all three Avastha systems and return combined result.

    Returns:
        {
            "baladi":   {planet: {avastha, multiplier, ...}},
            "shayanadi":{planet: {avastha, base_index, sub_state, ...}},
            "deeptadi": {planet: {avastha, condition, multiplier, ...}},
        }

    Store in: static["computed"]["avasthas"]
    ADDED 2026-03-02: Phase 1B.
    """
    # Filter to 9 classical planets for Baladi/Shayanadi (include Rahu/Ketu)
    baladi   = compute_baladi_avasthas(planet_lons)
    shayanadi = compute_shayanadi_avasthas(
        planet_lons, moon_lon, lagna_sign, birth_dt, sunrise_hour
    )
    deeptadi = compute_deeptadi_avasthas(
        planet_dignities, planet_lons, sun_lon,
        malefic_conjunction_planets=malefic_conjunctions,
        retrograde_planets=retrograde_planets,
    )

    return {
        "baladi":    baladi,
        "shayanadi": shayanadi,
        "deeptadi":  deeptadi,
    }
