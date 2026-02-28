"""
Jaimini Rashi Drishti (Sign Aspects).

Rules (BPHS / Jaimini):
  - Movable (Chara) signs aspect all Fixed signs EXCEPT the adjacent one.
  - Fixed (Sthira) signs aspect all Movable signs EXCEPT the preceding one.
  - Dual (Dwi-swabhava) signs mutually aspect each other (all 4 dual signs).

Sign indices (0-based):
  Aries=0  Taurus=1  Gemini=2  Cancer=3  Leo=4     Virgo=5
  Libra=6  Scorpio=7 Sagittarius=8  Capricorn=9  Aquarius=10 Pisces=11

Sign categories:
  Movable  (Chara)    : 0(Aries) 3(Cancer) 6(Libra)  9(Capricorn)
  Fixed    (Sthira)   : 1(Taurus) 4(Leo) 7(Scorpio) 10(Aquarius)
  Dual     (Dwiswabhava): 2(Gemini) 5(Virgo) 8(Sagittarius) 11(Pisces)

Aspect table (classical examples):
  Aries    (movable) → Leo, Scorpio, Aquarius         (not Taurus, adjacent)
  Cancer   (movable) → Taurus, Scorpio, Aquarius      (not Leo, adjacent)
  Libra    (movable) → Taurus, Leo, Aquarius          (not Scorpio, adjacent)
  Capricorn(movable) → Taurus, Leo, Scorpio           (not Aquarius, adjacent)

  Taurus   (fixed)   → Cancer, Libra, Capricorn       (not Aries, preceding)
  Leo      (fixed)   → Aries, Libra, Capricorn        (not Cancer, preceding)
  Scorpio  (fixed)   → Aries, Cancer, Capricorn       (not Libra, preceding)
  Aquarius (fixed)   → Aries, Cancer, Libra           (not Scorpio, preceding)

  Gemini    (dual) ↔ Virgo, Sagittarius, Pisces
  Virgo     (dual) ↔ Gemini, Sagittarius, Pisces
  Sagittarius(dual)↔ Gemini, Virgo, Pisces
  Pisces    (dual) ↔ Gemini, Virgo, Sagittarius

Rashi drishti are MUTUAL: if A aspects B, then B aspects A.
Aspects are full-strength (100%) — not distance dependent.
"""
from __future__ import annotations
from typing import Dict, FrozenSet, List, Set, Tuple


SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Categories
MOVABLE  = frozenset({0, 3, 6, 9})   # Aries, Cancer, Libra, Capricorn
FIXED    = frozenset({1, 4, 7, 10})  # Taurus, Leo, Scorpio, Aquarius
DUAL     = frozenset({2, 5, 8, 11})  # Gemini, Virgo, Sagittarius, Pisces

_ALL_FIXED    = {1, 4, 7, 10}
_ALL_MOVABLE  = {0, 3, 6, 9}
_ALL_DUAL     = {2, 5, 8, 11}

def _sign_category(s: int) -> str:
    if s in MOVABLE: return "movable"
    if s in FIXED:   return "fixed"
    return "dual"


def _build_aspect_table() -> Dict[int, FrozenSet[int]]:
    """
    Build the complete Jaimini Rashi Drishti aspect table.
    Returns: {sign_idx: frozenset of sign indices it aspects}
    """
    table: Dict[int, Set[int]] = {i: set() for i in range(12)}

    # ── Movable signs → all Fixed signs EXCEPT the one adjacent (next) to them ──
    # Adjacent fixed sign to a movable sign = the next sign (movable+1 mod 12)
    for m in _ALL_MOVABLE:
        adjacent_fixed = (m + 1) % 12   # e.g. Aries(0)+1 = Taurus(1)
        for f in _ALL_FIXED:
            if f != adjacent_fixed:
                table[m].add(f)
                table[f].add(m)   # mutual

    # ── Fixed signs → all Movable signs EXCEPT the preceding one ──
    # Preceding movable sign for a fixed sign = (fixed - 1) mod 12
    # (This is already handled by the mutual aspect above from movable→fixed;
    #  the mutual adds everything correctly.)
    # But let's verify the "not preceding" exclusion is correct:
    # Taurus(1) preceding movable = Aries(0). Aries IS adjacent to Taurus (Aries+1=Taurus).
    # So Taurus does NOT aspect Aries ✓. Already handled above.

    # ── Dual signs → mutually aspect all other Dual signs ──
    dual_list = [2, 5, 8, 11]
    for i, a in enumerate(dual_list):
        for b in dual_list[i+1:]:
            table[a].add(b)
            table[b].add(a)

    return {s: frozenset(aspects) for s, aspects in table.items()}


# Pre-computed table: sign → frozenset of aspected signs
RASHI_ASPECTS: Dict[int, FrozenSet[int]] = _build_aspect_table()


def get_sign_category(sign_idx: int) -> str:
    """Return 'movable', 'fixed', or 'dual' for a sign index (0-11)."""
    return _sign_category(sign_idx % 12)


def signs_aspected_by(sign_idx: int) -> FrozenSet[int]:
    """
    Return frozenset of sign indices that `sign_idx` aspects (Jaimini Rashi Drishti).
    Since aspects are mutual, this is the same as signs that aspect sign_idx.
    """
    return RASHI_ASPECTS.get(sign_idx % 12, frozenset())


def does_sign_aspect(source_sign: int, target_sign: int) -> bool:
    """
    Return True if source_sign casts Jaimini Rashi Drishti on target_sign.
    Mutual: does_sign_aspect(A, B) == does_sign_aspect(B, A).
    """
    src = source_sign % 12
    tgt = target_sign % 12
    if src == tgt:
        return False
    return tgt in RASHI_ASPECTS.get(src, frozenset())


def get_aspecting_signs(target_sign: int) -> FrozenSet[int]:
    """
    Return all signs that throw Rashi Drishti on target_sign.
    (Same as signs_aspected_by due to mutual nature.)
    """
    return RASHI_ASPECTS.get(target_sign % 12, frozenset())


def planets_with_rashi_drishti(
    planet_positions: Dict[str, int],  # {planet_name: sign_idx}
    target_sign: int,
) -> List[str]:
    """
    Return list of planets whose sign casts Jaimini Rashi Drishti on target_sign.
    planet_positions: dict mapping planet name to sign index (0-11).
    """
    tgt = target_sign % 12
    aspecting = RASHI_ASPECTS.get(tgt, frozenset())
    result = []
    for pname, psign in planet_positions.items():
        if (psign % 12) in aspecting:
            result.append(pname)
    return result


def activated_houses_in_dasha(
    dasha_sign: int,
    lagna_sign: int,
) -> List[int]:
    """
    During Chara Dasha of `dasha_sign`, this returns the list of 1-based
    house numbers that are activated (i.e. the dasha sign and all signs
    it Rashi-aspects, relative to lagna).

    activated = {house_of(dasha_sign)} ∪ {house_of(T) for T in aspects(dasha_sign)}
    """
    activated_signs = {dasha_sign % 12} | set(RASHI_ASPECTS.get(dasha_sign % 12, frozenset()))
    houses = sorted([((s - lagna_sign) % 12) + 1 for s in activated_signs])
    return houses


def rashi_drishti_summary(planet_positions: Dict[str, int]) -> Dict[int, List[str]]:
    """
    For each sign (0-11), return the list of planets casting Rashi Drishti on it.
    Useful for comprehensive chart analysis.
    """
    result: Dict[int, List[str]] = {i: [] for i in range(12)}
    for tgt in range(12):
        aspecting_signs = RASHI_ASPECTS.get(tgt, frozenset())
        for pname, psign in planet_positions.items():
            if (psign % 12) in aspecting_signs:
                if pname not in result[tgt]:
                    result[tgt].append(pname)
    return result
