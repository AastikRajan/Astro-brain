"""
Ashtakoota (8-Kuta) Marriage Compatibility Engine.

Computes the classical 8-kuta scoring (total 36 points) from:
  1. Varna Kuta   (1 pt)  — psychological type / varna rank
  2. Vashya Kuta  (2 pt)  — mutual attraction / control group
  3. Tara Kuta    (3 pt)  — lunar mansion count compatibility
  4. Yoni Kuta    (4 pt)  — animal symbol affinity
  5. Graha Maitri (5 pt)  — lord of Moon-sign friendship
  6. Gana Kuta    (6 pt)  — divine/human/demonic gana match
  7. Bhakoot Kuta (7 pt)  — Moon sign position (2-12, 6-8 dosha)
  8. Nadi Kuta    (8 pt)  — nadi energy mismatch check

Traditional minimum: 18 / 36 for compatibility.
Sources: BPHS, Ashtakoota texts, DrikPanchang classical tables.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

from vedic_engine.data.nakshatra_db import (
    get_nakshatra_index, get_nakshatra_by_index, yoni_score,
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. VARNA KUTA (1 point)
# Signs → Varna rank (higher = better/more evolved)
# Brahmin=3, Kshatriya=2, Vaishya=1, Shudra=0
# ─────────────────────────────────────────────────────────────────────────────
_SIGN_VARNA: Dict[int, Tuple[str, int]] = {
    3:  ("Brahmin", 3),   # Cancer
    7:  ("Brahmin", 3),   # Scorpio
    11: ("Brahmin", 3),   # Pisces
    0:  ("Kshatriya", 2), # Aries
    4:  ("Kshatriya", 2), # Leo
    8:  ("Kshatriya", 2), # Sagittarius
    1:  ("Vaishya", 1),   # Taurus
    5:  ("Vaishya", 1),   # Virgo
    9:  ("Vaishya", 1),   # Capricorn
    2:  ("Shudra", 0),    # Gemini
    6:  ("Shudra", 0),    # Libra
    10: ("Shudra", 0),    # Aquarius
}

def _varna_kuta(bride_moon_sign: int, groom_moon_sign: int) -> Tuple[float, str]:
    """Varna Kuta: 1 if groom's varna ≥ bride's varna, else 0."""
    b_varna, b_rank = _SIGN_VARNA.get(bride_moon_sign % 12, ("Shudra", 0))
    g_varna, g_rank = _SIGN_VARNA.get(groom_moon_sign % 12, ("Shudra", 0))
    score = 1.0 if g_rank >= b_rank else 0.0
    return score, f"Bride={b_varna}({b_rank}) Groom={g_varna}({g_rank})"


# ─────────────────────────────────────────────────────────────────────────────
# 2. VASHYA KUTA (2 points)
# Signs → Vashya class
# Classes: Chatushpada / Manav / Jalachara / Vanachara / Keeta
# ─────────────────────────────────────────────────────────────────────────────
# For Sagittarius (8): 0-15° = Manav, 15-30° = Chatushpada
# For Capricorn (9): 0-15° = Chatushpada, 15-30° = Jalachara
# We simplify to whole-sign for compatibility (traditional simplification).
_SIGN_VASHYA: Dict[int, str] = {
    0: "Chatushpada",  # Aries
    1: "Chatushpada",  # Taurus
    2: "Manav",        # Gemini
    3: "Jalachara",    # Cancer
    4: "Vanachara",    # Leo
    5: "Manav",        # Virgo
    6: "Manav",        # Libra
    7: "Keeta",        # Scorpio
    8: "Manav",        # Sagittarius (simplified: Manav)
    9: "Chatushpada",  # Capricorn (simplified: Chatushpada)
    10:"Jalachara",    # Aquarius
    11:"Jalachara",    # Pisces
}

# Compatibility pairs: same=2, partial=1, else=0
_VASHYA_PARTIAL: List[Tuple[str, str]] = [
    ("Chatushpada", "Manav"),
    ("Chatushpada", "Jalachara"),
    ("Manav", "Jalachara"),
    ("Vanachara", "Chatushpada"),
    ("Keeta", "Jalachara"),
]

def _vashya_kuta(bride_moon_sign: int, groom_moon_sign: int) -> Tuple[float, str]:
    """Vashya Kuta: 2=same class, 1=partial, 0=incompatible."""
    bv = _SIGN_VASHYA.get(bride_moon_sign % 12, "Manav")
    gv = _SIGN_VASHYA.get(groom_moon_sign % 12, "Manav")
    if bv == gv:
        score = 2.0
    elif frozenset({bv, gv}) in [frozenset({a, b}) for a, b in _VASHYA_PARTIAL]:
        score = 1.0
    else:
        score = 0.0
    return score, f"Bride={bv} Groom={gv}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. TARA KUTA (3 points)
# Count from bride's nakshatra to groom's, divide by 9, take remainder.
# Remainders 3, 5, 7 = malefic (Kala Tara). Others = benefic.
# Score: both benefic=3, one malefic=1.5, both malefic=0.
# ─────────────────────────────────────────────────────────────────────────────
_MALEFIC_TARA = {3, 5, 7}  # Vipat, Pratyak, Nidhana

_TARA_NAMES = {
    1: "Janma", 2: "Sampat", 3: "Vipat", 4: "Kshema",
    5: "Pratyari", 6: "Sadhana", 7: "Nidhana", 8: "Mitra", 0: "Ati Mitra",
}

def _tara_kuta(bride_nak: int, groom_nak: int) -> Tuple[float, str]:
    """Tara Kuta scoring based on nakshatra count."""
    diff_bg = ((groom_nak - bride_nak) % 27)
    diff_gb = ((bride_nak - groom_nak) % 27)
    rem_bg = (diff_bg % 9)
    rem_gb = (diff_gb % 9)
    tara_bg = _TARA_NAMES.get(rem_bg, "Ati Mitra")
    tara_gb = _TARA_NAMES.get(rem_gb, "Ati Mitra")
    mal_bg = rem_bg in _MALEFIC_TARA
    mal_gb = rem_gb in _MALEFIC_TARA
    if not mal_bg and not mal_gb:
        score = 3.0
    elif mal_bg and mal_gb:
        score = 0.0
    else:
        score = 1.5
    detail = f"Bride→Groom={tara_bg}({'bad' if mal_bg else 'good'}) Groom→Bride={tara_gb}({'bad' if mal_gb else 'good'})"
    return score, detail


# ─────────────────────────────────────────────────────────────────────────────
# 4. YONI KUTA (4 points) — delegated to nakshatra_db
# ─────────────────────────────────────────────────────────────────────────────
def _yoni_kuta(bride_nak: int, groom_nak: int) -> Tuple[float, str]:
    """Yoni Kuta: 4=same, 3=friendly, 2=neutral, 1=inimical, 0=hostile."""
    b_nak = get_nakshatra_by_index(bride_nak)
    g_nak = get_nakshatra_by_index(groom_nak)
    score = float(yoni_score(b_nak.yoni_animal, g_nak.yoni_animal))
    detail = f"Bride={b_nak.yoni_animal}({b_nak.yoni_gender}) Groom={g_nak.yoni_animal}({g_nak.yoni_gender}) → {int(score)}/4"
    return score, detail


# ─────────────────────────────────────────────────────────────────────────────
# 5. GRAHA MAITRI KUTA (5 points)
# Compare lords of bride's and groom's Moon signs.
# Lords: natural friendship table (classical BPHS).
# ─────────────────────────────────────────────────────────────────────────────
# Sign → lord (planet name)
_SIGN_LORD: Dict[int, str] = {
    0: "MARS", 1: "VENUS", 2: "MERCURY", 3: "MOON", 4: "SUN", 5: "MERCURY",
    6: "VENUS", 7: "MARS", 8: "JUPITER", 9: "SATURN", 10: "SATURN", 11: "JUPITER",
}

# Natural friendships (BPHS)
_NAT_FRIENDS: Dict[str, List[str]] = {
    "SUN":     ["MOON", "MARS", "JUPITER"],
    "MOON":    ["SUN", "MARS", "JUPITER"],
    "MARS":    ["SUN", "MOON", "JUPITER"],
    "MERCURY": ["SUN", "VENUS", "SATURN"],
    "JUPITER": ["SUN", "MOON", "MARS"],
    "VENUS":   ["MERCURY", "SATURN"],
    "SATURN":  ["MERCURY", "VENUS"],
}
_NAT_ENEMIES: Dict[str, List[str]] = {
    "SUN":     ["VENUS", "SATURN"],
    "MOON":    [],
    "MARS":    ["MERCURY"],
    "MERCURY": ["MOON"],
    "JUPITER": ["MERCURY", "VENUS"],
    "VENUS":   ["SUN"],
    "SATURN":  ["SUN", "MOON", "MARS"],
}


def _planetary_relation(planet_a: str, planet_b: str) -> str:
    """Return 'friend', 'neutral', or 'enemy' from A's perspective toward B."""
    friends = _NAT_FRIENDS.get(planet_a, [])
    enemies = _NAT_ENEMIES.get(planet_a, [])
    if planet_b in friends:
        return "friend"
    elif planet_b in enemies:
        return "enemy"
    return "neutral"


def _graha_maitri(bride_moon_sign: int, groom_moon_sign: int) -> Tuple[float, str]:
    """
    Graha Maitri Kuta (5 points).
    Scoring:
      Mutual friends                      = 5
      One friend, one neutral             = 4
      Both neutral                        = 3
      One friend, one enemy               = 2
      One neutral, one enemy              = 1
      Mutual enemies                      = 0
    """
    b_lord = _SIGN_LORD.get(bride_moon_sign % 12, "MOON")
    g_lord = _SIGN_LORD.get(groom_moon_sign % 12, "MOON")
    if b_lord == g_lord:
        return 5.0, f"Same lord: {b_lord} — mutual friends"
    b_view = _planetary_relation(b_lord, g_lord)
    g_view = _planetary_relation(g_lord, b_lord)
    views = frozenset({b_view, g_view})
    if b_view == "friend" and g_view == "friend":
        score = 5.0
    elif "friend" in views and "neutral" in views:
        score = 4.0
    elif b_view == "neutral" and g_view == "neutral":
        score = 3.0
    elif "friend" in views and "enemy" in views:
        score = 2.0
    elif "neutral" in views and "enemy" in views:
        score = 1.0
    else:  # both enemy
        score = 0.0
    detail = f"Bride lord={b_lord}({b_view}) Groom lord={g_lord}({g_view})"
    return score, detail


# ─────────────────────────────────────────────────────────────────────────────
# 6. GANA KUTA (6 points)
# Gana: Deva, Manushya (Manav), Rakshasa
# scoring matrix (bride_gana × groom_gana):
# Deva×Deva=6, Deva×Manushya=6, Manushya×Deva=6, Manushya×Manushya=6
# Rakshasa×Rakshasa=6
# Deva×Rakshasa=1 (or Rakshasa×Deva=1)
# Manushya×Rakshasa=0 (or vice versa)
# ─────────────────────────────────────────────────────────────────────────────
_GANA_SCORE: Dict[Tuple[str, str], float] = {
    ("Deva", "Deva"):         6.0,
    ("Deva", "Manushya"):     6.0,
    ("Manushya", "Deva"):     6.0,
    ("Manushya", "Manushya"): 6.0,
    ("Rakshasa", "Rakshasa"): 6.0,
    ("Deva", "Rakshasa"):     1.0,
    ("Rakshasa", "Deva"):     1.0,
    ("Manushya", "Rakshasa"): 0.0,
    ("Rakshasa", "Manushya"): 0.0,
}

def _gana_kuta(bride_nak: int, groom_nak: int) -> Tuple[float, str]:
    """Gana Kuta (6 points)."""
    b_gana = get_nakshatra_by_index(bride_nak).gana
    g_gana = get_nakshatra_by_index(groom_nak).gana
    score = _GANA_SCORE.get((b_gana, g_gana), 0.0)
    return score, f"Bride={b_gana} Groom={g_gana}"


# ─────────────────────────────────────────────────────────────────────────────
# 7. BHAKOOT KUTA (7 points)
# Dosha if Moon signs are 2-12 or 6-8 from each other.
# Full 7 points if no dosha.
# ─────────────────────────────────────────────────────────────────────────────
def _bhakoot_kuta(bride_moon_sign: int, groom_moon_sign: int) -> Tuple[float, str]:
    """Bhakoot (Rashi) Kuta: 7 points if no dosha, 0 if 2/12 or 6/8 axis."""
    b = bride_moon_sign % 12
    g = groom_moon_sign % 12
    b_to_g = ((g - b) % 12) + 1
    g_to_b = ((b - g) % 12) + 1
    # Dosha: relationship is 2/12 (one is 2nd, other is 12th)
    # or 6/8 (one is 6th, other is 8th)
    dosha = False
    reason = "No dosha"
    if {b_to_g, g_to_b} == {2, 12}:
        dosha = True
        reason = "2-12 dosha (financial/emotional incompatibility)"
    elif {b_to_g, g_to_b} == {6, 8}:
        dosha = True
        reason = "6-8 dosha (health/longevity concern)"
    score = 0.0 if dosha else 7.0
    return score, reason


# ─────────────────────────────────────────────────────────────────────────────
# 8. NADI KUTA (8 points)
# Same nadi = Nadi Dosha (0 points).
# Different nadi = 8 points.
# Classical cancellation: same nadi but different Moon signs → dosha cancelled.
# ─────────────────────────────────────────────────────────────────────────────
def _nadi_kuta(
    bride_nak: int, groom_nak: int,
    bride_moon_sign: int, groom_moon_sign: int,
) -> Tuple[float, str]:
    """Nadi Kuta: 8 if different nadi, 0 if same, with cancellation check."""
    b_nadi = get_nakshatra_by_index(bride_nak).nadi
    g_nadi = get_nakshatra_by_index(groom_nak).nadi
    if b_nadi != g_nadi:
        return 8.0, f"Different Nadi ({b_nadi} vs {g_nadi}) — excellent"
    # Same nadi — check cancellation: different Moon signs
    if bride_moon_sign % 12 != groom_moon_sign % 12:
        return 8.0, f"Nadi Dosha ({b_nadi}) — CANCELLED by different Moon signs"
    return 0.0, f"Nadi Dosha ({b_nadi}) — Same nadi, same Moon sign — serious concern"


# ─────────────────────────────────────────────────────────────────────────────
# Main scorer
# ─────────────────────────────────────────────────────────────────────────────
def ashtakoota_score(
    bride_moon_longitude: float,
    groom_moon_longitude: float,
) -> Dict:
    """
    Compute full Ashtakoota (8-Kuta) compatibility score.

    Args:
        bride_moon_longitude: Bride's natal Moon sidereal longitude (0-360°)
        groom_moon_longitude: Groom's natal Moon sidereal longitude (0-360°)

    Returns:
        Dict with individual kuta scores, total, compatibility assessment,
        any doshas detected, and plain-language detail for each kuta.
    """
    b_sign = int(bride_moon_longitude // 30) % 12
    g_sign = int(groom_moon_longitude // 30) % 12
    b_nak = get_nakshatra_index(bride_moon_longitude)
    g_nak = get_nakshatra_index(groom_moon_longitude)
    b_nak_obj = get_nakshatra_by_index(b_nak)
    g_nak_obj = get_nakshatra_by_index(g_nak)

    v1, d1 = _varna_kuta(b_sign, g_sign)
    v2, d2 = _vashya_kuta(b_sign, g_sign)
    v3, d3 = _tara_kuta(b_nak, g_nak)
    v4, d4 = _yoni_kuta(b_nak, g_nak)
    v5, d5 = _graha_maitri(b_sign, g_sign)
    v6, d6 = _gana_kuta(b_nak, g_nak)
    v7, d7 = _bhakoot_kuta(b_sign, g_sign)
    v8, d8 = _nadi_kuta(b_nak, g_nak, b_sign, g_sign)

    total = v1 + v2 + v3 + v4 + v5 + v6 + v7 + v8
    max_score = 36.0
    pct = round(total / max_score * 100, 1)

    # Doshas
    doshas = []
    if v7 == 0:
        doshas.append("Bhakoot Dosha")
    if v8 == 0:
        doshas.append("Nadi Dosha")

    # Compatibility assessment
    if total >= 28:
        grade = "Excellent"
    elif total >= 24:
        grade = "Very Good"
    elif total >= 18:
        grade = "Good (acceptable)"
    elif total >= 12:
        grade = "Below Average (remedies advised)"
    else:
        grade = "Incompatible (not recommended)"

    return {
        "bride_nakshatra": b_nak_obj.name,
        "groom_nakshatra": g_nak_obj.name,
        "bride_moon_sign": b_sign,
        "groom_moon_sign": g_sign,
        "kutas": {
            "varna":       {"score": v1, "max": 1, "detail": d1},
            "vashya":      {"score": v2, "max": 2, "detail": d2},
            "tara":        {"score": v3, "max": 3, "detail": d3},
            "yoni":        {"score": v4, "max": 4, "detail": d4},
            "graha_maitri":{"score": v5, "max": 5, "detail": d5},
            "gana":        {"score": v6, "max": 6, "detail": d6},
            "bhakoot":     {"score": v7, "max": 7, "detail": d7},
            "nadi":        {"score": v8, "max": 8, "detail": d8},
        },
        "total": total,
        "max": max_score,
        "percentage": pct,
        "grade": grade,
        "doshas": doshas,
        "minimum_required": 18,
        "is_compatible": total >= 18,
    }
