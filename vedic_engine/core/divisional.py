"""
Divisional (Varga) Chart Calculators.
Each function takes an absolute sidereal longitude (0-360°) and returns
a sign index (0-11) for that planet in the specified divisional chart.

All formulas verified against deep-research-report.md + classical BPHS.

KEY WARNING from research doc:
  Navamsa (D9): Earth signs START from Capricorn, Water signs from Cancer.
  NOT the other way round (common implementation bug).
"""
from __future__ import annotations
from vedic_engine.core.coordinates import normalize, sign_of, degree_in_sign
from vedic_engine.config import Sign, SIGN_ELEMENTS, Element


# ─── Internal helpers ──────────────────────────────────────────────

def _navamsa_start(sign_idx: int) -> int:
    """
    Starting navamsa sign for each rashi based on element (BPHS rule).
    Fire  → Aries  (0)
    Earth → Capricorn (9)   ← Research doc warns: common bug maps this to Cancer
    Air   → Libra  (6)
    Water → Cancer (3)
    """
    el = SIGN_ELEMENTS[Sign(sign_idx)]
    return {
        Element.FIRE: 0,   # Aries
        Element.EARTH: 9,  # Capricorn
        Element.AIR: 6,    # Libra
        Element.WATER: 3,  # Cancer
    }[el]

def _generic_division(lon: float, n: int, start_rule: str = "same") -> int:
    """
    Generic D-n calculator.
    lon       : absolute sidereal longitude
    n         : division number
    start_rule: "same"     → start from same sign (odd signs rule)
                "9th"      → start from 9th sign (even signs rule, D10)
                "navamsa"  → element-based start (D9)
    """
    s = sign_of(lon)
    d = degree_in_sign(lon)
    span = 30.0 / n
    segment = int(d / span)   # 0-indexed which division we're in

    if start_rule == "same":
        return (s + segment) % 12
    elif start_rule == "9th":
        start = (s + 8) % 12  # 9th sign = +8
        return (start + segment) % 12
    elif start_rule == "navamsa":
        start = _navamsa_start(s)
        return (start + segment) % 12
    else:
        return (s + segment) % 12


# ─── Individual Varga Functions ────────────────────────────────────

def D1(lon: float) -> int:
    """Rashi (natal) chart. Trivially the sign itself."""
    return sign_of(lon)


def D2(lon: float) -> int:
    """
    Hora chart – 2 divisions of 15° each.
    Odd signs: 1st hora → Leo (4), 2nd hora → Cancer (3)
    Even signs: 1st hora → Cancer (3), 2nd hora → Leo (4)
    """
    s = sign_of(lon)
    d = degree_in_sign(lon)
    hora = 0 if d < 15 else 1
    if s % 2 == 0:  # Odd signs (Aries=0 is odd-numbered=1st)
        return [4, 3][hora]   # Leo, Cancer
    else:           # Even signs
        return [3, 4][hora]   # Cancer, Leo


def D3(lon: float) -> int:
    """Drekkana – 3 divisions of 10° each. Same element starts."""
    s = sign_of(lon)
    d = degree_in_sign(lon)
    dec = int(d / 10)         # 0,1,2
    starts = [s, (s + 4) % 12, (s + 8) % 12]  # 1st, 5th, 9th
    return starts[dec]


def D4(lon: float) -> int:
    """Chaturthamsa – 4 divisions of 7°30' each."""
    s = sign_of(lon)
    d = degree_in_sign(lon)
    seg = int(d / 7.5)
    if s % 4 == 0:   # Movable signs
        return (s + seg) % 12
    elif s % 4 == 1:  # Fixed signs
        return (s + 3 + seg) % 12
    elif s % 4 == 2:  # Dual/mutable
        return (s + 6 + seg) % 12
    else:
        return (s + 9 + seg) % 12


def D7(lon: float) -> int:
    """Saptamsha – 7 divisions of 4°17'8\".  Odd/even rule."""
    s = sign_of(lon)
    d = degree_in_sign(lon)
    span = 30.0 / 7
    seg = int(d / span)
    if s % 2 == 0:   # Odd sign
        return (s + seg) % 12
    else:            # Even sign: start from 7th
        return (s + 6 + seg) % 12


def D9(lon: float) -> int:
    """
    Navamsa – 9 divisions of 3°20' each.
    Start sign depends on ELEMENT of the rashi (BPHS rule).
    THIS IS THE CORRECTED VERSION – Earth → Capricorn, Water → Cancer.
    """
    return _generic_division(lon, 9, start_rule="navamsa")


def D10(lon: float) -> int:
    """
    Dashamsha – 10 divisions of 3° each.
    Odd signs: start from same sign.
    Even signs: start from 9th sign.
    """
    s = sign_of(lon)
    d = degree_in_sign(lon)
    seg = int(d / 3)
    if s % 2 == 0:   # Odd
        return (s + seg) % 12
    else:            # Even: 9th
        return (s + 8 + seg) % 12


def D12(lon: float) -> int:
    """Dwadashamsha – 12 divisions of 2°30'. Start from same sign."""
    return _generic_division(lon, 12, start_rule="same")


def D16(lon: float) -> int:
    """Shodashamsha – 16 divisions of 1°52'30\".
    Movable → Aries(0), Fixed → Leo(4), Dual → Sagittarius(8)."""
    s = sign_of(lon)
    d = degree_in_sign(lon)
    span = 30.0 / 16
    seg = int(d / span)
    qual_start = {0: 0, 1: 4, 2: 8}  # movable=0,fixed=1,dual=2
    from vedic_engine.config import SIGN_QUALITIES, SignQuality
    q = SIGN_QUALITIES[Sign(s)]
    q_idx = {SignQuality.MOVABLE: 0, SignQuality.FIXED: 1, SignQuality.DUAL: 2}[q]
    return (qual_start[q_idx] + seg) % 12


def D20(lon: float) -> int:
    """Vimsamsha – 20 divisions of 1°30'.
    Movable → Aries, Fixed → Sagittarius, Dual → Leo."""
    from vedic_engine.config import SIGN_QUALITIES, SignQuality
    s = sign_of(lon)
    d = degree_in_sign(lon)
    span = 30.0 / 20
    seg = int(d / span)
    q = SIGN_QUALITIES[Sign(s)]
    start = {SignQuality.MOVABLE: 0, SignQuality.FIXED: 8, SignQuality.DUAL: 4}[q]
    return (start + seg) % 12


def D24(lon: float) -> int:
    """Chaturvimsamsha – 24 divisions of 1°15'.
    Odd → Leo(4), Even → Cancer(3)."""
    s = sign_of(lon)
    d = degree_in_sign(lon)
    span = 30.0 / 24
    seg = int(d / span)
    start = 4 if s % 2 == 0 else 3  # odd=Leo, even=Cancer
    return (start + seg) % 12


def D27(lon: float) -> int:
    """Nakshatramsha – 27 divisions of 1°6'40\".  Element-based like D9."""
    s = sign_of(lon)
    d = degree_in_sign(lon)
    span = 30.0 / 27
    seg = int(d / span)
    el = SIGN_ELEMENTS[Sign(s)]
    start = {Element.FIRE: 0, Element.EARTH: 3, Element.AIR: 6, Element.WATER: 9}[el]
    return (start + seg) % 12


def D30(lon: float) -> int:
    """
    Trimsamsha – 30 divisions of 1° each.
    Different planet-owned degrees for odd vs even signs (BPHS table).
    Odd signs: Mars(5°) Venus(5°) Mercury(8°) Jupiter(7°) Saturn(5°)
    Even signs: Saturn(5°) Mercury(7°) Jupiter(8°) Venus(5°) Mars(5°)
    Returns sign index of the trims lord's sign (first own sign used).
    """
    s = sign_of(lon)
    d = degree_in_sign(lon)

    # Each entry: (lord_sign_0indexed, span_degrees)
    if s % 2 == 0:  # Odd signs (Aries, Gemini, Leo …)
        pieces = [
            (0, 5),   # Mars → Aries
            (6, 5),   # Venus → Libra (first own)
            (2, 8),   # Mercury → Gemini
            (8, 7),   # Jupiter → Sagittarius
            (9, 5),   # Saturn → Capricorn
        ]
    else:           # Even signs (Taurus, Cancer, Virgo …)
        pieces = [
            (9, 5),   # Saturn → Capricorn
            (2, 7),   # Mercury → Gemini
            (8, 8),   # Jupiter → Sagittarius
            (1, 5),   # Venus → Taurus (first own)
            (0, 5),   # Mars → Aries
        ]

    accumulated = 0
    for (lord_sign, span) in pieces:
        accumulated += span
        if d < accumulated:
            return lord_sign % 12
    return pieces[-1][0] % 12


def D40(lon: float) -> int:
    """Khavedamsha (D40). Movable→Aries, Fixed→Cancer, Dual→Libra."""
    from vedic_engine.config import SIGN_QUALITIES, SignQuality
    s = sign_of(lon)
    d = degree_in_sign(lon)
    span = 30.0 / 40
    seg = int(d / span)
    q = SIGN_QUALITIES[Sign(s)]
    start = {SignQuality.MOVABLE: 0, SignQuality.FIXED: 3, SignQuality.DUAL: 6}[q]
    return (start + seg) % 12


def D45(lon: float) -> int:
    """Akshavedamsha (D45). Movable→Aries, Fixed→Leo, Dual→Sagittarius."""
    from vedic_engine.config import SIGN_QUALITIES, SignQuality
    s = sign_of(lon)
    d = degree_in_sign(lon)
    span = 30.0 / 45
    seg = int(d / span)
    q = SIGN_QUALITIES[Sign(s)]
    start = {SignQuality.MOVABLE: 0, SignQuality.FIXED: 4, SignQuality.DUAL: 8}[q]
    return (start + seg) % 12


def D60(lon: float) -> int:
    """Shashtiamsha (D60). Start from same sign always."""
    return _generic_division(lon, 60, start_rule="same")


# ─── Registry ─────────────────────────────────────────────────────

VARGA_FUNCTIONS = {
    1: D1, 2: D2, 3: D3, 4: D4, 7: D7, 9: D9,
    10: D10, 12: D12, 16: D16, 20: D20, 24: D24,
    27: D27, 30: D30, 40: D40, 45: D45, 60: D60,
}

def get_varga(lon: float, d: int) -> int:
    """Get divisional chart placement for any supported D-number."""
    fn = VARGA_FUNCTIONS.get(d)
    if fn is None:
        raise ValueError(f"Divisional chart D{d} not implemented.")
    return fn(lon)


def compute_all_vargas(lon: float) -> dict:
    """Compute all supported divisional placements for a longitude."""
    return {d: fn(lon) for d, fn in VARGA_FUNCTIONS.items()}
