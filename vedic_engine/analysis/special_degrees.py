"""
Special Degree Analysis — Mrityu Bhaga, Gandanta, Pushkara Bhaga.

Three classical techniques that modify planet strength at specific ecliptic
degrees, independent of sign dignity:

  Mrityu Bhaga:  "Death Degree" — a planet at its MB becomes destructive
                  to its own significations. Penalty: 0.2–0.7 multiplier.

  Gandanta:      Water-to-Fire sign junctions — karmic crisis zone.
                  Lagna or Moon in Gandanta = deep karmic imprinting.
                  Penalty: 0.3–0.9 multiplier scaling to junction.

  Pushkara Bhaga: Specific auspicious single degrees within each sign.
                  Bonus: +0.15 additive to dignity score.

Sources: Jataka Parijata (Ch.1 v.57), Sarvartha Chintamani,
         Phaladeepika, BPHS classical texts.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

# ─── Mrityu Bhaga ─────────────────────────────────────────────────────────────
# Classical degree per planet per sign that acts as a "death degree" for that
# planet's significations.
# Format: MRITYU_BHAGA[planet_name][sign_index_0_to_11] = degree (integer)
# Source: Jataka Parijata Ch.1 v.57 / Sarvartha Chintamani tabulation.

MRITYU_BHAGA: Dict[str, List[int]] = {
    # Sign:     Ar  Ta  Ge  Cn  Le  Vi  Li  Sc  Sg  Cp  Aq  Pi
    "SUN":     [20,  9, 12,  6,  8, 24, 16, 17, 22,  2,  3, 23],
    "MOON":    [26, 12, 13, 25, 24, 11, 26, 14, 13, 25,  5, 12],
    "MARS":    [19, 28, 25, 23, 29, 28, 14, 21,  2, 15, 11,  6],
    "MERCURY": [15, 14, 13, 12,  8, 18, 20, 10, 21, 22,  7,  5],
    "JUPITER": [19, 29, 12, 27,  6,  4, 13, 10, 17, 11, 15, 28],
    "VENUS":   [28, 15, 11, 17, 10, 13,  4,  6, 27, 12, 29, 19],
    "SATURN":  [10,  4,  7,  9, 12, 16,  3, 18, 28, 14, 13, 15],
    "RAHU":    [14, 13, 12, 11, 24, 23, 22, 21, 10, 20, 18,  8],
    "KETU":    [ 8, 18, 20, 10, 21, 22, 23, 24, 11, 12, 13, 14],
    "LAGNA":   [ 1,  9, 22, 22, 25,  2,  4, 23, 18, 20, 24, 10],
}

# Tolerance: 1° on either side of the MB degree triggers the effect.
MRITYU_BHAGA_ORB = 1.0  # degrees


def is_mrityu_bhaga(planet: str, longitude: float) -> bool:
    """
    Return True if the planet is within the Mrityu Bhaga orb for its sign.
    
    Args:
        planet    : Planet name (uppercase) — must be key in MRITYU_BHAGA
        longitude : Absolute sidereal longitude (0–360°)
    """
    mb_table = MRITYU_BHAGA.get(planet.upper())
    if mb_table is None:
        return False
    sign_idx = int(longitude / 30) % 12
    deg_in_sign = longitude % 30
    mb_deg = mb_table[sign_idx]
    return abs(deg_in_sign - mb_deg) <= MRITYU_BHAGA_ORB


def mrityu_bhaga_modifier(
    planet: str,
    longitude: float,
    aspected_by_jupiter: bool = False,
    conjunct_benefic: bool = False,
    conjunct_malefic: bool = False,
) -> Dict:
    """
    Compute the Mrityu Bhaga strength multiplier for a planet.

    Classical rules (Jataka Parijata / Sarvartha Chintamani):
    - Base penalty: planet operates at ~30% strength
    - Jupiter's aspect provides SIGNIFICANT relief (up to 60%)
    - Benefic conjunction adds partial repair
    - Malefic conjunction intensifies damage

    Returns:
        dict with:
          in_mrityu_bhaga : bool
          multiplier      : float (0.1 – 1.0)
          notes           : str
    """
    if not is_mrityu_bhaga(planet, longitude):
        return {
            "in_mrityu_bhaga": False,
            "multiplier": 1.0,
            "notes": "",
        }

    sign_idx = int(longitude / 30) % 12
    deg_in_sign = longitude % 30
    mb_deg = MRITYU_BHAGA[planet.upper()][sign_idx]
    proximity = 1.0 - abs(deg_in_sign - mb_deg) / MRITYU_BHAGA_ORB  # 0–1

    # Base penalty: closer to exact MB = more damaged
    multiplier = 0.30 + (1.0 - proximity) * 0.20  # 0.30 to 0.50

    # Jupiter aspect provides powerful relief
    if aspected_by_jupiter:
        multiplier += 0.30  # Significant relief

    # Benefic conjunction helps
    if conjunct_benefic:
        multiplier += 0.15

    # Malefic conjunction worsens
    if conjunct_malefic:
        multiplier -= 0.15

    multiplier = round(max(0.10, min(0.90, multiplier)), 3)

    notes_parts = [
        f"{planet} at {deg_in_sign:.1f}° in sign {sign_idx} touches "
        f"Mrityu Bhaga ({mb_deg}°) — significations suppressed."
    ]
    if aspected_by_jupiter:
        notes_parts.append("Jupiter aspect provides relief.")
    if conjunct_benefic:
        notes_parts.append("Benefic conjunction partially repairs.")
    if conjunct_malefic:
        notes_parts.append("Malefic conjunction intensifies damage.")

    return {
        "in_mrityu_bhaga": True,
        "mb_degree": mb_deg,
        "sign_index": sign_idx,
        "proximity": round(proximity, 3),
        "multiplier": multiplier,
        "notes": " ".join(notes_parts),
    }


def compute_all_mrityu_bhaga(
    planet_longitudes: Dict[str, float],
    aspected_by_jupiter: Optional[Dict[str, bool]] = None,
    conjunct_benefic: Optional[Dict[str, bool]] = None,
    conjunct_malefic: Optional[Dict[str, bool]] = None,
) -> Dict[str, Dict]:
    """
    Compute Mrityu Bhaga status for all planets in a chart.

    Args:
        planet_longitudes   : {planet_upper: longitude}
        aspected_by_jupiter : {planet: bool} — optional
        conjunct_benefic    : {planet: bool} — optional
        conjunct_malefic    : {planet: bool} — optional

    Returns:
        {planet: mrityu_bhaga_modifier_result}
    """
    results = {}
    for planet, lon in planet_longitudes.items():
        p = planet.upper()
        if p not in MRITYU_BHAGA:
            continue
        results[p] = mrityu_bhaga_modifier(
            p, lon,
            aspected_by_jupiter=(aspected_by_jupiter or {}).get(p, False),
            conjunct_benefic=(conjunct_benefic or {}).get(p, False),
            conjunct_malefic=(conjunct_malefic or {}).get(p, False),
        )
    return results


# ─── Gandanta ─────────────────────────────────────────────────────────────────
# Gandanta = the junction between Water signs (Cancer, Scorpio, Pisces) and
# the subsequent Fire signs (Leo, Sagittarius, Aries). The last ~3°20' of the
# Water sign and first ~3°20' of the Fire sign form the Gandanta zone.
# Each zone spans approximately one Nakshatra pada.
#
# The three zones (absolute sidereal longitudes):
#   Cancer→Leo:          last 3°20' of Cancer = 116°40'–120°
#                        first 3°20' of Leo    = 120°–123°20'
#   Scorpio→Sagittarius: last 3°20' of Scorpio  = 236°40'–240°
#                        first 3°20' of Sagitt.  = 240°–243°20'
#   Pisces→Aries:        last 3°20' of Pisces   = 356°40'–360°
#                        first 3°20' of Aries    = 0°–3°20'
#
# Nakshatra labels (most commonly cited):
#   Water-side: Ashlesha-4, Jyeshtha-4, Revati-4  (dissolution/crisis)
#   Fire-side:  Magha-1,    Moola-1,    Ashwini-1  (rebirth energy)

GANDANTA_ZONES: List[Tuple[float, float, str]] = [
    # (zone_start, zone_end, label)  All in absolute degrees
    (116.667, 123.333, "Ashlesha-Magha Gandanta"),       # Cancer-Leo
    (236.667, 243.333, "Jyeshtha-Moola Gandanta"),       # Scorpio-Sagittarius
    # Pisces-Aries wraps around 360°: two sub-intervals
    (356.667, 360.0,   "Revati-Ashwini Gandanta (end)"), # Pisces side
    (0.0,     3.333,   "Revati-Ashwini Gandanta (start)"), # Aries side
]

# Centre of each Gandanta zone (exact junction = maximum severity)
GANDANTA_CENTRES: Dict[str, float] = {
    "Ashlesha-Magha":   120.0,  # Cancer-Leo cusp
    "Jyeshtha-Moola":   240.0,  # Scorpio-Sagittarius cusp
    "Revati-Ashwini":   0.0,    # Pisces-Aries cusp (= 360°)
}

GANDANTA_NAKSHATRA_NOTES: Dict[str, str] = {
    "Ashlesha-Magha":  "Emotional/psychological turmoil; ancestral karma activates",
    "Jyeshtha-Moola":  "Root-level transformation; most severe Gandanta",
    "Revati-Ashwini":  "Endings transitioning to new beginnings; dissolution then rebirth",
}


def gandanta_severity(longitude: float) -> Dict:
    """
    Compute Gandanta severity for a given absolute sidereal longitude.

    Returns:
        in_gandanta   : bool
        severity      : float (0.0 = not in zone, 1.0 = exact junction)
        zone_label    : str
        nakshatra_note: str
        multiplier    : float (1.0 = no effect, 0.3 = exact junction)
    """
    for (z_start, z_end, label) in GANDANTA_ZONES:
        if z_start <= z_end:
            in_zone = (z_start <= longitude <= z_end)
        else:
            in_zone = (longitude >= z_start or longitude <= z_end)

        if not in_zone:
            continue

        # Find nearest zone centre
        if "end" in label:
            centre = 360.0
            dist = abs(longitude - centre)
        elif "start" in label:
            centre = 0.0
            dist = abs(longitude - centre)
        else:
            centre = (z_start + z_end) / 2.0
            dist = abs(longitude - centre)

        half_width = (z_end - z_start) / 2.0 if z_start <= z_end else 3.333
        severity = 1.0 - min(dist / half_width, 1.0)  # 1.0 = exact centre

        # Multiplier: from 1.0 (edge of zone) to 0.30 (exact junction)
        multiplier = 1.0 - (0.70 * severity)
        multiplier = round(max(0.30, multiplier), 3)

        # Resolve nakshatra label
        if "Ashlesha" in label or "Magha" in label:
            nak_key = "Ashlesha-Magha"
        elif "Jyeshtha" in label or "Moola" in label:
            nak_key = "Jyeshtha-Moola"
        else:
            nak_key = "Revati-Ashwini"

        return {
            "in_gandanta":    True,
            "severity":       round(severity, 3),
            "zone_label":     label,
            "nakshatra_key":  nak_key,
            "nakshatra_note": GANDANTA_NAKSHATRA_NOTES[nak_key],
            "multiplier":     multiplier,
        }

    return {
        "in_gandanta":    False,
        "severity":       0.0,
        "zone_label":     "",
        "nakshatra_key":  "",
        "nakshatra_note": "",
        "multiplier":     1.0,
    }


def compute_all_gandanta(planet_longitudes: Dict[str, float]) -> Dict[str, Dict]:
    """
    Compute Gandanta status for all planets + Lagna.

    Args:
        planet_longitudes: {name: absolute_longitude}

    Returns:
        {name: gandanta_severity_result}
    """
    return {name: gandanta_severity(lon) for name, lon in planet_longitudes.items()}


# ─── Pushkara Bhaga ───────────────────────────────────────────────────────────
# Highly auspicious single degrees within each sign.
# A planet hitting its Pushkara Bhaga degree gains strength equivalent to
# exaltation at that precise point.
# Source: Pushkara Bhaga list from Sarvartha Chintamani / BPHS commentary.

PUSHKARA_BHAGA: Dict[str, int] = {
    # Sign name → single degree (floor) within which the Pushkara point lies
    "Aries":       21,
    "Taurus":      14,
    "Gemini":      18,
    "Cancer":       8,
    "Leo":         19,
    "Virgo":        9,
    "Libra":       24,
    "Scorpio":     11,
    "Sagittarius": 23,
    "Capricorn":   14,
    "Aquarius":    19,
    "Pisces":       9,
}

_SIGN_NAMES_12 = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

PUSHKARA_BHAGA_ORB = 0.5  # degrees on either side counts as Pushkara Bhaga
PUSHKARA_BHAGA_BONUS = 0.15  # additive bonus to dignity score


def pushkara_bhaga_check(longitude: float) -> Dict:
    """
    Check if a longitude falls on a Pushkara Bhaga point.

    Returns:
        in_pushkara_bhaga : bool
        bonus             : float (0.0 or PUSHKARA_BHAGA_BONUS=0.15)
        sign              : str
        pb_degree         : int
    """
    sign_idx = int(longitude / 30) % 12
    sign_name = _SIGN_NAMES_12[sign_idx]
    deg_in_sign = longitude % 30
    pb_deg = PUSHKARA_BHAGA.get(sign_name, -999)
    in_pb = abs(deg_in_sign - pb_deg) <= PUSHKARA_BHAGA_ORB

    return {
        "in_pushkara_bhaga": in_pb,
        "bonus": PUSHKARA_BHAGA_BONUS if in_pb else 0.0,
        "sign": sign_name,
        "pb_degree": pb_deg,
        "degree_in_sign": round(deg_in_sign, 3),
    }


def compute_all_special_degrees(
    planet_longitudes: Dict[str, float],
    aspected_by_jupiter: Optional[Dict[str, bool]] = None,
    conjunct_benefic: Optional[Dict[str, bool]] = None,
    conjunct_malefic: Optional[Dict[str, bool]] = None,
) -> Dict:
    """
    Master function: compute Mrityu Bhaga, Gandanta, and Pushkara Bhaga
    for all listed longitudes simultaneously.

    Args:
        planet_longitudes   : {name: longitude} — planets + Lagna
        aspected_by_jupiter : optional {name: bool} for MB relief check
        conjunct_benefic    : optional {name: bool}
        conjunct_malefic    : optional {name: bool}

    Returns:
        {
          "mrityu_bhaga"   : {name: mb_result},
          "gandanta"       : {name: gand_result},
          "pushkara_bhaga" : {name: pb_result},
          "summary"        : human-readable list of notable conditions
        }
    """
    mb_results   = compute_all_mrityu_bhaga(
        planet_longitudes, aspected_by_jupiter, conjunct_benefic, conjunct_malefic
    )
    gand_results = compute_all_gandanta(planet_longitudes)
    pb_results   = {n: pushkara_bhaga_check(lon) for n, lon in planet_longitudes.items()}

    summary: List[str] = []
    for name in planet_longitudes:
        mb = mb_results.get(name, {})
        gd = gand_results.get(name, {})
        pb = pb_results.get(name, {})
        if mb.get("in_mrityu_bhaga"):
            summary.append(f"{name}: Mrityu Bhaga at {mb['mb_degree']}° (mult {mb['multiplier']})")
        if gd.get("in_gandanta"):
            summary.append(f"{name}: Gandanta — {gd['zone_label']} (severity {gd['severity']:.2f})")
        if pb.get("in_pushkara_bhaga"):
            summary.append(f"{name}: Pushkara Bhaga at {pb['pb_degree']}° (+0.15 bonus)")

    return {
        "mrityu_bhaga":   mb_results,
        "gandanta":       gand_results,
        "pushkara_bhaga": pb_results,
        "summary":        summary,
    }
