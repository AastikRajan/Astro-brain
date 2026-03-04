"""
Nadi Amsha computation (Phase 1F).

Nadi Amsha divides each sign into 150 equal parts of 0.2° (12 arc-minutes) each.
Primarily used for birth-time rectification (Phase 2), but computed now.

Rules (BPHS / Nadi texts):
  Cardinal (Movable) signs     → Amshas run 1 → 150 (direct / ascending order)
  Fixed signs                  → Amshas run 150 → 1 (reverse / descending)
  Dual (Mutable) signs         → Split: first half 76→150, second half 1→75
                                  (rising from 6 o'clock, meeting at top)

Amsha 1° resolution = 0.2° per amsha, so each sign of 30° = 150 amshas.

The amsha number encodes a specific Nadi leaf / pulse-point used in rectification.

Usage::
    from vedic_engine.analysis.nadi_amsha import compute_nadi_amsha
    result = compute_nadi_amsha({"SUN": 90.5, "MOON": 45.2, ...}, lagna_lon=15.3)
"""
from __future__ import annotations
from typing import Dict, Optional

# ── Sign helpers ──────────────────────────────────────────────────────────────

_SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Modalities (sign index 0-11)
_MOVABLE = frozenset({0, 3, 6, 9})    # Aries, Cancer, Libra, Capricorn
_FIXED   = frozenset({1, 4, 7, 10})   # Taurus, Leo, Scorpio, Aquarius
_DUAL    = frozenset({2, 5, 8, 11})   # Gemini, Virgo, Sagittarius, Pisces

_AMSHA_SIZE_DEG = 0.2          # degrees per Nadi Amsha
_AMSHAS_PER_SIGN = 150         # = 30° / 0.2°

# ── Core computation ──────────────────────────────────────────────────────────

def _sign_modality(sign_idx: int) -> str:
    if sign_idx in _MOVABLE: return "cardinal"
    if sign_idx in _FIXED:   return "fixed"
    return "dual"


def longitude_to_nadi_amsha(lon: float) -> Dict:
    """
    Compute Nadi Amsha for a single ecliptic longitude (0–360°).

    Returns:
        sign_idx:      0-based sign index
        sign_name:     sign name string
        modality:      "cardinal" | "fixed" | "dual"
        deg_in_sign:   degrees within sign (0–30°)
        raw_position:  linear amsha 1–150 within sign (before direction reversal)
        nadi_amsha:    final Nadi Amsha number (1–150, with direction applied)
        direction:     "ascending" | "descending" | "ascending_split"
    """
    lon = lon % 360.0
    sign_idx     = int(lon / 30.0) % 12
    deg_in_sign  = lon % 30.0
    sign_name    = _SIGN_NAMES[sign_idx]
    modality     = _sign_modality(sign_idx)

    # Linear position within sign: 0 to 149
    raw_pos_0 = deg_in_sign / _AMSHA_SIZE_DEG   # float 0.0–149.999
    raw_amsha  = int(raw_pos_0) + 1              # 1–150
    raw_amsha  = min(raw_amsha, _AMSHAS_PER_SIGN)

    if modality == "cardinal":
        # Ascending: 1 → 150
        nadi_amsha = raw_amsha
        direction  = "ascending"

    elif modality == "fixed":
        # Descending: 150 → 1
        nadi_amsha = _AMSHAS_PER_SIGN - raw_amsha + 1
        direction  = "descending"

    else:  # dual
        # First half (1–75): Amshas rise from 76 → 150
        # Second half (76–150): Amshas fall from 1 → 75
        if raw_amsha <= 75:
            nadi_amsha = 75 + raw_amsha          # maps 1→76, 75→150
        else:
            nadi_amsha = raw_amsha - 75           # maps 76→1, 150→75
        direction = "ascending_split"

    return {
        "sign_idx":       sign_idx,
        "sign_name":      sign_name,
        "modality":       modality,
        "deg_in_sign":    round(deg_in_sign, 4),
        "raw_amsha":      raw_amsha,
        "nadi_amsha":     nadi_amsha,
        "direction":      direction,
    }


# ── Batch computation ─────────────────────────────────────────────────────────

def compute_nadi_amsha(
    planet_lons: Dict[str, float],
    lagna_lon: Optional[float] = None,
) -> Dict[str, Dict]:
    """
    Compute Nadi Amsha for all planets and optionally the Lagna.

    Args:
        planet_lons: dict mapping planet name → ecliptic longitude (0–360°)
        lagna_lon:   Lagna (Ascendant) longitude; included if provided

    Returns:
        dict mapping body name → nadi_amsha_detail dict
        Each detail: {sign_idx, sign_name, modality, deg_in_sign,
                       raw_amsha, nadi_amsha, direction}
    """
    result: Dict[str, Dict] = {}
    for planet, lon in planet_lons.items():
        if not isinstance(lon, (int, float)):
            continue
        result[planet] = longitude_to_nadi_amsha(float(lon))

    if lagna_lon is not None:
        result["LAGNA"] = longitude_to_nadi_amsha(float(lagna_lon))

    return result
