"""
Longevity Methods: Pindayu, Amsayu, Nisargayu + Three Pairs Band (Phase 1F).

Three classical ayu (longevity) computations from Jataka Parijata / BPHS:

  Pindayu   — Arc-based method from exaltation longitude with dignity reductions
  Amsayu    — Navamsha-based method; accumulates sub-year units from chart arc
  Nisargayu — Fixed-constant method (natural years per planet)

Three Pairs Band determines overall life span bracket:
  Alpa  (short)  ← movable modality majority
  Madhya (medium) ← fixed modality majority
  Purna  (long)  ← dual modality majority

Usage::
    from vedic_engine.analysis.longevity import compute_longevity
    result = compute_longevity(
        planet_lons={"SUN": 90.5, ...},
        lagna_sign=2,
        hora_lagna_sign=4,
        retrogrades={"SATURN": True, ...},
        planet_signs={"SUN": 3, ...},
        planet_dignities={"SUN": "EXALTED", ...},
    )
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

# ── Constants ─────────────────────────────────────────────────────────────────

# Maximum Pindayu years per planet (classical)
PINDAYU_MAX_YEARS: Dict[str, float] = {
    "SUN":     19.0,
    "MOON":    25.0,
    "MARS":    15.0,
    "MERCURY": 12.0,
    "JUPITER": 15.0,
    "VENUS":   21.0,
    "SATURN":  20.0,
}

# Nisargayu fixed natural years per planet
NISARGAYU_YEARS: Dict[str, float] = {
    "SATURN":  50.0,
    "VENUS":   20.0,
    "SUN":     20.0,
    "JUPITER": 18.0,
    "MERCURY":  9.0,
    "MARS":     2.0,
    "MOON":     1.0,
}

# Exaltation longitude (tropical-reference degrees 0-360) for each planet
EXALTATION_LON: Dict[str, float] = {
    "SUN":      10.0,   # 10° Aries
    "MOON":     33.0,   # 3° Taurus
    "MARS":    298.0,   # 28° Capricorn
    "MERCURY": 165.0,   # 15° Virgo
    "JUPITER":  95.0,   # 5° Cancer
    "VENUS":   357.0,   # 27° Pisces
    "SATURN":  200.0,   # 20° Libra
}

# Enemy signs per planet (sign indices 0-11 where planet is debilitated/enemy sign)
# Debilitation signs (7th from exaltation)
DEBILITATION_SIGN: Dict[str, int] = {
    "SUN":     6,   # Libra
    "MOON":    9,   # Scorpio  (actually Scorpio per some texts; using 9)
    "MARS":    3,   # Cancer
    "MERCURY": 11,  # Pisces
    "JUPITER":  9,  # Capricorn
    "VENUS":    5,  # Virgo
    "SATURN":   0,  # Aries
}

# Natural malefics for lagna ascendant Krurodaya check
_NATURAL_MALEFICS = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}

# Sign modality for Three Pairs Band
_MOVABLE = {0, 3, 6, 9}    # Aries, Cancer, Libra, Capricorn
_FIXED   = {1, 4, 7, 10}   # Taurus, Leo, Scorpio, Aquarius
_DUAL    = {2, 5, 8, 11}   # Gemini, Virgo, Sagittarius, Pisces

SIGN_LORDS_MAP = {
    0: "MARS",    1: "VENUS",   2: "MERCURY", 3: "MOON",
    4: "SUN",     5: "MERCURY", 6: "VENUS",   7: "MARS",
    8: "JUPITER", 9: "SATURN", 10: "SATURN", 11: "JUPITER",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sign_modality(sign_idx: int) -> str:
    if sign_idx in _MOVABLE: return "movable"
    if sign_idx in _FIXED:   return "fixed"
    return "dual"


def _pindayu_reductions(
    planet: str,
    planet_lon: float,
    sun_lon: float,
    is_retrograde: bool,
    planet_sign: int,
    planet_dignity: str,
    lagna_sign: int,
) -> float:
    """
    Compute cumulative Pindayu reduction factor (0.0 − 1.0 subtracted from base).

    Classical reductions:
      Chakrapata  — combust (within orb of Sun): 1/3 reduction
      Astangata   — retrograde: 1/3 reduction  (but retrograde often INCREASES Amsayu)
      Shatrukshetra — in enemy/debilitation sign: 1/4 reduction
      Krurodaya   — malefic planet on ascendant: 1/6 reduction (lagna-wide)
    """
    reduction = 0.0

    # Combustion orbs
    _COMBUST_ORBS = {
        "MOON": 12.0, "MARS": 17.0, "MERCURY": 14.0,
        "JUPITER": 11.0, "VENUS": 10.0, "SATURN": 15.0,
    }
    if planet not in ("SUN", "RAHU", "KETU"):
        orb = _COMBUST_ORBS.get(planet, 12.0)
        diff = abs((planet_lon - sun_lon + 180) % 360 - 180)
        if diff <= orb:
            reduction += 1 / 3

    # Retrograde
    if is_retrograde:
        reduction += 1 / 3

    # Enemy / debilitation sign
    if planet_sign == DEBILITATION_SIGN.get(planet, -1):
        reduction += 1 / 4
    elif planet_dignity in ("ENEMY", "GREAT_ENEMY", "DEBILITATED"):
        reduction += 1 / 6

    # Krurodaya — malefic rising at lagna ascendant (applied equally to all planets)
    lagna_lord = SIGN_LORDS_MAP.get(lagna_sign, "")
    if lagna_lord in _NATURAL_MALEFICS:
        reduction += 1 / 6

    return min(reduction, 0.75)   # cap at 75% total reduction


# ── Pindayu ───────────────────────────────────────────────────────────────────

def compute_pindayu(
    planet_lons: Dict[str, float],
    sun_lon: float,
    lagna_sign: int,
    planet_signs: Dict[str, int],
    planet_dignities: Dict[str, str],
    retrogrades: Dict[str, bool],
) -> Dict:
    """
    Pindayu: arc-from-exaltation method.

    For each planet p:
      arc_years = PINDAYU_MAX[p] × ((lon_p - exalt_lon_p) % 360) / 180
      reduced = arc_years × (1 − reduction_factor)

    Total Pindayu = sum of reduced years for all 7 planets.
    """
    planet_details: Dict[str, Dict] = {}
    total = 0.0

    for planet, max_yrs in PINDAYU_MAX_YEARS.items():
        lon = planet_lons.get(planet)
        if lon is None:
            continue
        exalt_lon = EXALTATION_LON.get(planet, 0.0)
        arc = (lon - exalt_lon) % 360.0
        base_yrs = max_yrs * arc / 180.0

        reduction = _pindayu_reductions(
            planet=planet,
            planet_lon=lon,
            sun_lon=sun_lon,
            is_retrograde=bool(retrogrades.get(planet, False)),
            planet_sign=planet_signs.get(planet, 0),
            planet_dignity=planet_dignities.get(planet, "NEUTRAL"),
            lagna_sign=lagna_sign,
        )
        reduced_yrs = base_yrs * (1.0 - reduction)
        planet_details[planet] = {
            "arc_deg":       round(arc, 2),
            "base_years":    round(base_yrs, 3),
            "reduction":     round(reduction, 3),
            "reduced_years": round(reduced_yrs, 3),
        }
        total += reduced_yrs

    return {
        "method":          "Pindayu",
        "planet_details":  planet_details,
        "total_years":     round(total, 2),
        "interpretation":  _band_label(total),
    }


# ── Amsayu ────────────────────────────────────────────────────────────────────

def compute_amsayu(
    planet_lons: Dict[str, float],
    lagna_lon: float,
    planet_signs: Dict[str, int],
    planet_dignities: Dict[str, str],
    retrogrades: Dict[str, bool],
) -> Dict:
    """
    Amsayu: navamsha-arc method.

    For each planet p (incl. Lagna):
      arc_minutes = lon_p × 60   (total arc-minutes from 0° Aries)
      base_years  = (arc_minutes / 200) % 12
      multiplier  = ×3 if retrograde or exalted or own sign
                    ×2 if own-navamsha or vargottama
    Total Amsayu = Σ multiplied_years / normalization_factor
    """
    planet_details: Dict[str, Dict] = {}
    total = 0.0

    all_lons = dict(planet_lons)
    all_lons["LAGNA"] = lagna_lon

    for planet, lon in all_lons.items():
        if planet in ("RAHU", "KETU"):
            continue
        arc_min = lon * 60.0
        base = (arc_min / 200.0) % 12.0

        dignity = planet_dignities.get(planet, "NEUTRAL")
        is_retro = bool(retrogrades.get(planet, False))
        p_sign = planet_signs.get(planet, int(lon % 360 / 30) % 12)

        # Navamsha sign (D9): each sign = 30° / 9 = 3.33° per navamsha
        nav_sign = int((lon % 30) / (30.0 / 9)) % 12

        # Vargottama: D1 sign == D9 sign
        d1_sign = int(lon % 360 / 30) % 12
        is_vargottama = (d1_sign == nav_sign)

        multiplier = 1.0
        if is_retro or dignity in ("EXALTED",):
            multiplier = 3.0
        elif planet in SIGN_LORDS_MAP.values() and p_sign in [
            i for i, v in SIGN_LORDS_MAP.items() if v == planet
        ]:
            multiplier = 3.0   # own sign
        elif is_vargottama:
            multiplier = 2.0

        contrib = base * multiplier
        planet_details[planet] = {
            "arc_minutes":  round(arc_min, 1),
            "base_years":   round(base, 4),
            "multiplier":   multiplier,
            "contribution": round(contrib, 4),
            "vargottama":   is_vargottama,
        }
        total += contrib

    # Normalize: maximum possible total with 9 planets × 12 × 3 = 324 → scale to ~120 year life range
    normalized = min(total / 2.7, 120.0)

    return {
        "method":          "Amsayu",
        "planet_details":  planet_details,
        "raw_total":       round(total, 3),
        "total_years":     round(normalized, 2),
        "interpretation":  _band_label(normalized),
    }


# ── Nisargayu ─────────────────────────────────────────────────────────────────

def compute_nisargayu(
    planet_lons: Dict[str, float],
    sun_lon: float,
    lagna_sign: int,
    planet_signs: Dict[str, int],
    planet_dignities: Dict[str, str],
    retrogrades: Dict[str, bool],
) -> Dict:
    """
    Nisargayu: fixed natural-year method.

    Base for each planet = NISARGAYU_YEARS[planet].
    Apply same Pindayu-style reductions (Chakrapata, Astangata, Shatrukshetra, Krurodaya).
    Total Nisargayu = sum of reduced years.
    """
    planet_details: Dict[str, Dict] = {}
    total = 0.0

    for planet, base_yrs in NISARGAYU_YEARS.items():
        lon = planet_lons.get(planet)
        if lon is None:
            continue
        reduction = _pindayu_reductions(
            planet=planet,
            planet_lon=lon,
            sun_lon=sun_lon,
            is_retrograde=bool(retrogrades.get(planet, False)),
            planet_sign=planet_signs.get(planet, 0),
            planet_dignity=planet_dignities.get(planet, "NEUTRAL"),
            lagna_sign=lagna_sign,
        )
        reduced_yrs = base_yrs * (1.0 - reduction)
        planet_details[planet] = {
            "base_years":    base_yrs,
            "reduction":     round(reduction, 3),
            "reduced_years": round(reduced_yrs, 3),
        }
        total += reduced_yrs

    return {
        "method":         "Nisargayu",
        "planet_details": planet_details,
        "total_years":    round(total, 2),
        "interpretation": _band_label(total),
    }


# ── Three Pairs Band ──────────────────────────────────────────────────────────

def compute_three_pairs_band(
    lagna_sign: int,
    hora_lagna_sign: Optional[int],
    moon_sign: int,
    saturn_sign: int,
    planet_signs: Dict[str, int],
) -> Dict:
    """
    Determine life-span band from Three Pairs (tridosha).

    Pairs evaluated:
      [1] Lagna Lord sign  vs 8th Lord sign  → modality of their signs
      [2] Lagna sign       vs Hora Lagna sign → modality
      [3] Moon sign        vs Saturn sign     → modality

    Majority modality → band:
      Movable majority → Alpa  (short life: ~33 years theoretical)
      Fixed   majority → Purna (long life:  ~100 years)
      Dual    majority → Madhya (medium:    ~66 years)
    """
    lagna_lord = SIGN_LORDS_MAP.get(lagna_sign, "MARS")
    eighth_lord = SIGN_LORDS_MAP.get((lagna_sign + 7) % 12, "SATURN")

    lagna_lord_sign = planet_signs.get(lagna_lord, lagna_sign)
    eighth_lord_sign = planet_signs.get(eighth_lord, (lagna_sign + 7) % 12)

    pair1_mod = _sign_modality(lagna_lord_sign)     # vs 8th lord
    pair2_mod = _sign_modality(lagna_sign)           # Lagna itself
    if hora_lagna_sign is not None:
        pair2_mod2 = _sign_modality(hora_lagna_sign)
        # Use majority of the two for pair2
        if pair2_mod == pair2_mod2:
            # Same → confirm
            pass
        else:
            # Mixed → use lagna_sign
            pair2_mod = pair2_mod
    pair3_mod = _sign_modality(moon_sign)            # vs Saturn
    pair3_mod2 = _sign_modality(saturn_sign)

    modalities = [pair1_mod, pair2_mod, pair3_mod]
    modality_counts = {m: modalities.count(m) for m in ("movable", "fixed", "dual")}
    dominant = max(modality_counts, key=lambda k: modality_counts[k])

    band_map = {
        "movable": ("Alpa",   "Short life span (~32 years theoretical)"),
        "fixed":   ("Purna",  "Long life span (~100 years theoretical)"),
        "dual":    ("Madhya", "Medium life span (~66 years theoretical)"),
    }
    band_name, band_desc = band_map[dominant]

    return {
        "pair1": {"lagna_lord": lagna_lord, "eighth_lord": eighth_lord,
                  "modality": pair1_mod},
        "pair2": {"entity": "Lagna vs Hora Lagna", "modality": pair2_mod},
        "pair3": {"entity": "Moon vs Saturn",
                  "moon_modality": pair3_mod, "saturn_modality": pair3_mod2,
                  "modality": pair3_mod},
        "modality_counts":  modality_counts,
        "dominant_modality": dominant,
        "band":              band_name,
        "description":       band_desc,
    }


# ── Band label helper ─────────────────────────────────────────────────────────

def _band_label(years: float) -> str:
    if years < 36:
        return f"Alpa (short) — {years:.1f} years"
    if years < 72:
        return f"Madhya (medium) — {years:.1f} years"
    return f"Purna (long) — {years:.1f} years"


# ── Main API ──────────────────────────────────────────────────────────────────

def compute_longevity(
    planet_lons: Dict[str, float],
    lagna_sign: int,
    lagna_lon: float = 0.0,
    hora_lagna_sign: Optional[int] = None,
    retrogrades: Optional[Dict[str, bool]] = None,
    planet_signs: Optional[Dict[str, int]] = None,
    planet_dignities: Optional[Dict[str, str]] = None,
) -> Dict:
    """
    Compute all three longevity methods + Three Pairs Band.

    Returns:
        pindayu:      Pindayu result dict
        amsayu:       Amsayu result dict
        nisargayu:    Nisargayu result dict
        three_pairs:  Three Pairs Band dict
        consensus:    Average of three methods in years
        consensus_band: Band label for consensus
    """
    retrogrades    = retrogrades    or {}
    planet_signs   = planet_signs   or {p: int(lon % 360 / 30) % 12
                                         for p, lon in planet_lons.items()}
    planet_dignities = planet_dignities or {}

    sun_lon  = planet_lons.get("SUN", 0.0)
    moon_lon = planet_lons.get("MOON", 90.0)
    sat_sign = planet_signs.get("SATURN", 9)
    moon_sign = planet_signs.get("MOON", int(moon_lon % 360 / 30) % 12)

    pindayu   = compute_pindayu(planet_lons, sun_lon, lagna_sign,
                                planet_signs, planet_dignities, retrogrades)
    amsayu    = compute_amsayu(planet_lons, lagna_lon, planet_signs,
                               planet_dignities, retrogrades)
    nisargayu = compute_nisargayu(planet_lons, sun_lon, lagna_sign,
                                  planet_signs, planet_dignities, retrogrades)

    three_pairs = compute_three_pairs_band(
        lagna_sign=lagna_sign,
        hora_lagna_sign=hora_lagna_sign,
        moon_sign=moon_sign,
        saturn_sign=sat_sign,
        planet_signs=planet_signs,
    )

    p_yrs = pindayu["total_years"]
    a_yrs = amsayu["total_years"]
    n_yrs = nisargayu["total_years"]
    consensus = (p_yrs + a_yrs + n_yrs) / 3.0

    return {
        "pindayu":       pindayu,
        "amsayu":        amsayu,
        "nisargayu":     nisargayu,
        "three_pairs":   three_pairs,
        "consensus_years": round(consensus, 2),
        "consensus_band":  _band_label(consensus),
    }
