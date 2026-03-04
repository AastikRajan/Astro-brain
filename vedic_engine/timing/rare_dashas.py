"""
Rare Dasha Systems — Mandooka (Frog Leap) & Padanadhamsha (Arudha Navamsha).

Both are specialized Rashi Dashas from BPHS / Jaimini tradition.
Reference: BPHS Ch. 46-48, Jaimini Upadesha Sutras, K.N. Rao.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta


# ═══════════════════════════════════════════════════════════════
# COMMON HELPERS
# ═══════════════════════════════════════════════════════════════

_SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

_SIGN_LORD = {
    0: "MARS", 1: "VENUS", 2: "MERCURY", 3: "MOON",
    4: "SUN", 5: "MERCURY", 6: "VENUS", 7: "MARS",
    8: "JUPITER", 9: "SATURN", 10: "SATURN", 11: "JUPITER",
}

# Modality: 0=Cardinal, 1=Fixed, 2=Dual
_MODALITY = {
    0: 0, 1: 1, 2: 2, 3: 0, 4: 1, 5: 2,
    6: 0, 7: 1, 8: 2, 9: 0, 10: 1, 11: 2,
}

# Duration by modality
_MODALITY_YEARS = {0: 7, 1: 8, 2: 9}  # Cardinal=7, Fixed=8, Dual=9

# Odd/even sign (0-based)
def _is_odd_sign(sign: int) -> bool:
    return sign % 2 == 0  # Aries=0 is Odd, Taurus=1 is Even

def _sign_of(lon: float) -> int:
    return int(lon / 30.0) % 12

def _format_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


# ═══════════════════════════════════════════════════════════════
# 1. MANDOOKA DASHA (Frog Leap) — 96yr total
# ═══════════════════════════════════════════════════════════════
#
# Eligibility: 4+ planets (excluding Rahu/Ketu) in Kendras from ASC.
# Sequence: Jumps to every 4th sign → groups by modality (Cardinal→Fixed→Dual).
# Duration: Cardinal=7yr, Fixed=8yr, Dual=9yr  (total=4×7+4×8+4×9=96).
#
# Direct (odd ASC): Start from ASC, jump forward within modality, then next modality.
# Reverse (even ASC): Start from 7th house, jump backward within modality.

# Precomputed 12 starting-sign → full 12-sign sequence arrays
_MANDOOKA_DIRECT: Dict[int, List[int]] = {
    # Odd signs (ASC = starting sign, zodiacal jumps)
    0:  [0, 3, 6, 9,  1, 4, 7, 10,  2, 5, 8, 11],   # Aries
    2:  [2, 5, 8, 11,  3, 6, 9, 0,  4, 7, 10, 1],    # Gemini
    4:  [4, 7, 10, 1,  5, 8, 11, 2,  6, 9, 0, 3],    # Leo
    6:  [6, 9, 0, 3,  7, 10, 1, 4,  8, 11, 2, 5],    # Libra
    8:  [8, 11, 2, 5,  9, 0, 3, 6,  10, 1, 4, 7],    # Sagittarius
    10: [10, 1, 4, 7,  11, 2, 5, 8,  0, 3, 6, 9],    # Aquarius
}

_MANDOOKA_REVERSE: Dict[int, List[int]] = {
    # Even signs (start from 7th house, reverse jumps)
    1:  [7, 4, 1, 10,  6, 3, 0, 9,  5, 2, 11, 8],    # Taurus (start Scorpio)
    3:  [9, 6, 3, 0,  8, 5, 2, 11,  7, 4, 1, 10],    # Cancer (start Capricorn)
    5:  [11, 8, 5, 2,  10, 7, 4, 1,  9, 6, 3, 0],    # Virgo (start Pisces)
    7:  [1, 10, 7, 4,  0, 9, 6, 3,  11, 8, 5, 2],    # Scorpio (start Taurus)
    9:  [3, 0, 9, 6,  2, 11, 8, 5,  1, 10, 7, 4],    # Capricorn (start Cancer)
    11: [5, 2, 11, 8,  4, 1, 10, 7,  3, 0, 9, 6],    # Pisces (start Virgo)
}


def check_mandooka_eligible(
    planet_lons: Dict[str, float],
    asc_lon: float,
) -> Dict[str, Any]:
    """
    Check Mandooka Dasha eligibility: 4+ planets (excl. Rahu/Ketu) in Kendras.

    Args:
        planet_lons: planet→longitude (SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN)
        asc_lon: Ascendant longitude

    Returns:
        Dict with eligible flag, count, and planets in kendras.
    """
    asc_sign = _sign_of(asc_lon)
    kendras = {asc_sign, (asc_sign + 3) % 12, (asc_sign + 6) % 12, (asc_sign + 9) % 12}

    exclude = {"RAHU", "KETU"}
    in_kendra = []
    for planet, lon in planet_lons.items():
        if planet.upper() in exclude:
            continue
        if _sign_of(lon) in kendras:
            in_kendra.append(planet.upper())

    return {
        "eligible": len(in_kendra) >= 4,
        "planets_in_kendras": in_kendra,
        "count": len(in_kendra),
        "required": 4,
    }


def compute_mandooka_dasha(
    asc_lon: float,
    birth_dt: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Compute Mandooka (Frog Leap) Dasha sequence.

    Args:
        asc_lon: Ascendant longitude
        birth_dt: Birth datetime for period dating

    Returns:
        Dict with sequence of 12 sign periods.
    """
    asc_sign = _sign_of(asc_lon)
    is_odd = _is_odd_sign(asc_sign)

    if is_odd:
        sequence = _MANDOOKA_DIRECT.get(asc_sign, [])
        direction = "DIRECT"
        start_sign = asc_sign
    else:
        sequence = _MANDOOKA_REVERSE.get(asc_sign, [])
        direction = "REVERSE"
        start_sign = (asc_sign + 6) % 12

    # If sequence not in precomputed (shouldn't happen), generate dynamically
    if not sequence:
        sequence = _generate_mandooka_sequence(start_sign, direction == "DIRECT")

    periods = []
    cursor = birth_dt or datetime(2000, 1, 1)
    total_years = 0

    for sign in sequence:
        years = _MODALITY_YEARS[_MODALITY[sign]]
        end = cursor + timedelta(days=years * 365.25)
        periods.append({
            "sign": sign,
            "sign_name": _SIGN_NAMES[sign],
            "modality": ["CARDINAL", "FIXED", "DUAL"][_MODALITY[sign]],
            "years": years,
            "start": _format_date(cursor),
            "end": _format_date(end),
        })
        total_years += years
        cursor = end

    return {
        "dasha_type": "Mandooka Dasha (Frog Leap)",
        "direction": direction,
        "asc_sign": asc_sign,
        "start_sign": start_sign,
        "total_years": total_years,
        "periods": periods,
    }


def _generate_mandooka_sequence(start: int, direct: bool) -> List[int]:
    """Generate Mandooka sequence dynamically for any starting sign."""
    modality = _MODALITY[start]

    # Modality order: start with start's modality, then next two
    modality_order = [(modality + i) % 3 for i in range(3)]

    # Get signs of each modality
    modality_signs = {m: [s for s in range(12) if _MODALITY[s] == m] for m in range(3)}

    sequence = []
    for mod in modality_order:
        signs = modality_signs[mod]
        # Sort by every-4th-sign jump from appropriate starting point
        if direct:
            # Find the sign closest to start among this modality's signs
            idx = min(range(len(signs)), key=lambda i: (signs[i] - start) % 12)
            ordered = [signs[(idx + j) % len(signs)] for j in range(len(signs))]
        else:
            idx = min(range(len(signs)), key=lambda i: (start - signs[i]) % 12)
            ordered = [signs[(idx - j) % len(signs)] for j in range(len(signs))]
        sequence.extend(ordered)

    return sequence


# ═══════════════════════════════════════════════════════════════
# 2. PADANADHAMSHA DASHA (Arudha Navamsha Dasha)
# ═══════════════════════════════════════════════════════════════
#
# Starting sign = D-9 sign of the Arudha Lagna lord (Pada Nath).
# 6 distinct sequence patterns based on the starting sign's polarity + modality.
# Duration = distance from Dasha sign to its lord in D-9 (odd=forward, even=reverse).
# Override: lord in same sign = 12 years; lord in 7th = 10 years.

# 6 Precomputed sequence patterns
_PADANADHAMSHA_SEQUENCES: Dict[str, List[int]] = {
    # 1. Odd + Movable (Aries, Libra): Standard direct sequence
    "ODD_MOVABLE":  list(range(12)),  # 0,1,2,...,11

    # 2. Even + Movable (Cancer, Capricorn): Standard reverse sequence
    "EVEN_MOVABLE": list(range(11, -1, -1)),  # 11,10,9,...,0

    # 3. Odd + Fixed (Leo, Aquarius): Every 6th sign forward
    "ODD_FIXED_LEO":     [4, 9, 2, 7, 0, 5, 10, 3, 8, 1, 6, 11],
    "ODD_FIXED_AQU":     [10, 3, 8, 1, 6, 11, 4, 9, 2, 7, 0, 5],

    # 4. Even + Fixed (Taurus, Scorpio): Every 6th sign reverse
    "EVEN_FIXED_TAU":    [1, 8, 3, 10, 5, 0, 7, 2, 9, 4, 11, 6],
    "EVEN_FIXED_SCO":    [7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5, 0],

    # 5. Odd + Dual (Gemini, Sagittarius): Trinal jump forward (1,5,9)
    "ODD_DUAL_GEM":      [2, 6, 10, 3, 7, 11, 4, 8, 0, 5, 9, 1],
    "ODD_DUAL_SAG":      [8, 0, 4, 9, 1, 5, 10, 2, 6, 11, 3, 7],

    # 6. Even + Dual (Virgo, Pisces): Trinal jump reverse (1,5,9)
    "EVEN_DUAL_VIR":     [5, 1, 9, 4, 0, 8, 3, 11, 7, 2, 10, 6],
    "EVEN_DUAL_PIS":     [11, 7, 3, 10, 6, 2, 9, 5, 1, 8, 4, 0],
}


def _get_padanadhamsha_sequence(start_sign: int) -> List[int]:
    """Return the 12-sign sequence for the given Padanadhamsha starting sign."""
    mod = _MODALITY[start_sign]
    is_odd = _is_odd_sign(start_sign)

    if mod == 0:  # Movable
        if is_odd:  # Aries (0) or Libra (6)
            base = _PADANADHAMSHA_SEQUENCES["ODD_MOVABLE"]
            # Rotate so start_sign is first
            idx = base.index(start_sign) if start_sign in base else 0
            return base[idx:] + base[:idx]
        else:  # Cancer (3) or Capricorn (9)
            base = _PADANADHAMSHA_SEQUENCES["EVEN_MOVABLE"]
            idx = base.index(start_sign) if start_sign in base else 0
            return base[idx:] + base[:idx]

    elif mod == 1:  # Fixed
        if is_odd:  # Leo (4) or Aquarius (10)
            if start_sign == 4:
                return _PADANADHAMSHA_SEQUENCES["ODD_FIXED_LEO"]
            else:
                return _PADANADHAMSHA_SEQUENCES["ODD_FIXED_AQU"]
        else:  # Taurus (1) or Scorpio (7)
            if start_sign == 1:
                return _PADANADHAMSHA_SEQUENCES["EVEN_FIXED_TAU"]
            else:
                return _PADANADHAMSHA_SEQUENCES["EVEN_FIXED_SCO"]

    else:  # Dual
        if is_odd:  # Gemini (2) or Sagittarius (8)
            if start_sign == 2:
                return _PADANADHAMSHA_SEQUENCES["ODD_DUAL_GEM"]
            else:
                return _PADANADHAMSHA_SEQUENCES["ODD_DUAL_SAG"]
        else:  # Virgo (5) or Pisces (11)
            if start_sign == 5:
                return _PADANADHAMSHA_SEQUENCES["EVEN_DUAL_VIR"]
            else:
                return _PADANADHAMSHA_SEQUENCES["EVEN_DUAL_PIS"]

    # Fallback: direct sequence
    return [(start_sign + i) % 12 for i in range(12)]


def _padanadhamsha_duration(
    dasha_sign: int,
    lord_d9_sign: int,
) -> int:
    """
    Compute duration for one Padanadhamsha period.

    Rules:
        - If lord in same sign → 12 years
        - If lord in 7th from sign → 10 years
        - If sign is Odd → count forward to lord → years = distance
        - If sign is Even → count reverse to lord → years = distance
    """
    if lord_d9_sign == dasha_sign:
        return 12
    if (lord_d9_sign - dasha_sign) % 12 == 6:
        return 10

    if _is_odd_sign(dasha_sign):
        dist = (lord_d9_sign - dasha_sign) % 12
    else:
        dist = (dasha_sign - lord_d9_sign) % 12

    return max(1, dist)


def compute_padanadhamsha_dasha(
    arudha_lagna_lord: str,
    d9_positions: Dict[str, int],
    birth_dt: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Compute Padanadhamsha (Arudha Navamsha) Dasha.

    Args:
        arudha_lagna_lord: Planet name of Arudha Lagna lord (the Pada Nath)
        d9_positions: planet → D-9 sign index (0-11) for all planets
        birth_dt: Birth datetime

    Returns:
        Full dasha schedule with 12 periods.
    """
    # Starting sign = D-9 sign of the Pada Nath
    pada_nath = arudha_lagna_lord.upper()
    start_sign = d9_positions.get(pada_nath, 0)

    sequence = _get_padanadhamsha_sequence(start_sign)

    periods = []
    cursor = birth_dt or datetime(2000, 1, 1)
    total_years = 0

    for sign in sequence:
        sign_lord = _SIGN_LORD[sign]
        lord_d9_sign = d9_positions.get(sign_lord, sign)
        years = _padanadhamsha_duration(sign, lord_d9_sign)

        end = cursor + timedelta(days=years * 365.25)
        periods.append({
            "sign": sign,
            "sign_name": _SIGN_NAMES[sign],
            "lord": sign_lord,
            "lord_d9_sign": lord_d9_sign,
            "years": years,
            "start": _format_date(cursor),
            "end": _format_date(end),
        })
        total_years += years
        cursor = end

    return {
        "dasha_type": "Padanadhamsha Dasha (Arudha Navamsha)",
        "pada_nath": pada_nath,
        "start_sign": start_sign,
        "start_sign_name": _SIGN_NAMES[start_sign],
        "total_years": total_years,
        "periods": periods,
    }


# ═══════════════════════════════════════════════════════════════
# COMBINED ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def compute_all_rare_dashas(
    planet_lons: Dict[str, float],
    asc_lon: float,
    arudha_lagna_lord: Optional[str] = None,
    d9_positions: Optional[Dict[str, int]] = None,
    birth_dt: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Compute all rare dasha systems (Mandooka + Padanadhamsha).

    Returns dict with results keyed by dasha type.
    """
    results: Dict[str, Any] = {}

    # Mandooka
    elig = check_mandooka_eligible(planet_lons, asc_lon)
    results["mandooka_eligible"] = elig
    if elig["eligible"]:
        results["mandooka_dasha"] = compute_mandooka_dasha(asc_lon, birth_dt)
    else:
        results["mandooka_dasha"] = None

    # Padanadhamsha
    if arudha_lagna_lord and d9_positions:
        results["padanadhamsha_dasha"] = compute_padanadhamsha_dasha(
            arudha_lagna_lord, d9_positions, birth_dt
        )
    else:
        results["padanadhamsha_dasha"] = None

    return results
