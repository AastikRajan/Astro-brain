"""
Jaimini Supplementary Dasha Systems Engine.

Implements 6 additional Jaimini dasha systems beyond Chara Dasha:
  1. Shoola Dasha         — Ayur Dasha; ALWAYS direct; Sthira periods; Rudra=2nd vs 8th lord
  2. Niryana Shoola Dasha — Ayur Dasha; directional (odd/even); fixed 9 years/sign
  3. Brahma Dasha         — Soul-level; Brahma planet + Sthira periods
  4. Navamsha Dasha       — Operates in D-9 chart; lord-based duration
  5. Sree Lagna Dasha (Sudasa) — KL/Panaphara/Apoklima sequence; footing-based duration
  6. Drig Dasha           — Spiritual timing; Trikuta Padakrama; Sthira durations
  7. Trikona Dasha        — Marriage/childbirth timing; Trikona strength start

Sources: Jaimini Upadesa Sutras, K.N. Rao, Sanjay Rath, Iranganti Rangacharya.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Sign categories (0-based)
_MOVABLE = frozenset({0, 3, 6, 9})   # Aries, Cancer, Libra, Capricorn
_FIXED   = frozenset({1, 4, 7, 10})  # Taurus, Leo, Scorpio, Aquarius
_DUAL    = frozenset({2, 5, 8, 11})  # Gemini, Virgo, Sagittarius, Pisces

# Sthira Dasha periods (years) — fixed by modality
_STHIRA_YEARS = {s: (7 if s in _MOVABLE else (8 if s in _FIXED else 9)) for s in range(12)}

# Sign lord (0-based) — primary lord
_SIGN_LORD: Dict[int, str] = {
    0:"MARS",1:"VENUS",2:"MERCURY",3:"MOON",4:"SUN",5:"MERCURY",
    6:"VENUS",7:"MARS",8:"JUPITER",9:"SATURN",10:"SATURN",11:"JUPITER",
}
_DUAL_LORDS: Dict[int, Tuple[str, str]] = {
    7: ("MARS", "KETU"),
    10: ("SATURN", "RAHU"),
}

# Exaltation / Debilitation sign indices
_EXALT_SIGN:  Dict[str, int] = {
    "SUN":0,"MOON":1,"MARS":9,"MERCURY":5,"JUPITER":3,"VENUS":11,"SATURN":6,
    "RAHU":1,"KETU":7,
}
_DEBIL_SIGN: Dict[str, int] = {
    "SUN":6,"MOON":7,"MARS":3,"MERCURY":11,"JUPITER":9,"VENUS":5,"SATURN":0,
    "RAHU":7,"KETU":1,
}

# Nakshatra lords for Sree Lagna calculation
_NAKSHATRA_LORDS = [
    "KETU","VENUS","SUN","MOON","MARS","RAHU","JUPITER","SATURN","MERCURY",
    "KETU","VENUS","SUN","MOON","MARS","RAHU","JUPITER","SATURN","MERCURY",
    "KETU","VENUS","SUN","MOON","MARS","RAHU","JUPITER","SATURN","MERCURY",
]
# Nakshatra durations in years (Vimshottari)
_NAKSHATRA_DURATIONS = {
    "KETU":7,"VENUS":20,"SUN":6,"MOON":10,"MARS":7,"RAHU":18,
    "JUPITER":16,"SATURN":19,"MERCURY":17,
}

# Rashi Drishti (sign aspects) — 0-based
_RASHI_DRISHTI: Dict[int, frozenset] = {
    0:frozenset({4,7,10}),3:frozenset({7,10,1}),6:frozenset({10,1,4}),9:frozenset({1,4,7}),
    1:frozenset({3,6,9}),4:frozenset({6,9,0}),7:frozenset({9,0,3}),10:frozenset({0,3,6}),
    2:frozenset({5,8,11}),5:frozenset({8,11,2}),8:frozenset({11,2,5}),11:frozenset({2,5,8}),
}

def _has_rashi_drishti(a: int, b: int) -> bool:
    return b in _RASHI_DRISHTI.get(a, frozenset()) or a in _RASHI_DRISHTI.get(b, frozenset())


def _sign_of(lon: float) -> int:
    return int(lon % 360.0 / 30.0) % 12


def _degree_in_sign(lon: float) -> float:
    return lon % 30.0


def _is_exalted(planet: str, sign: int) -> bool:
    return _EXALT_SIGN.get(planet, -1) == sign


def _is_debilitated(planet: str, sign: int) -> bool:
    return _DEBIL_SIGN.get(planet, -1) == sign


def _planet_sign(planet: str, planet_lons: Dict[str, float]) -> int:
    lon = planet_lons.get(planet, 0.0)
    return _sign_of(lon)


def _shadbala_stronger(p1: str, p2: str, shadbala: Optional[Dict[str, float]],
                        planet_lons: Optional[Dict[str, float]] = None) -> str:
    """Return the stronger of two planets (Shadbala fallback: degree in sign)."""
    if shadbala:
        s1 = shadbala.get(p1, 0.5)
        s2 = shadbala.get(p2, 0.5)
        if s1 != s2:
            return p1 if s1 > s2 else p2
    # Fallback: higher degree in sign
    if planet_lons:
        d1 = _degree_in_sign(planet_lons.get(p1, 0.0))
        d2 = _degree_in_sign(planet_lons.get(p2, 0.0))
        return p1 if d1 >= d2 else p2
    return p1


def _chara_duration(sign: int, direction: str, planet_lons: Dict[str, float]) -> int:
    """Standard Chara Dasha duration formula: count-to-lord - 1, ±exalt/debil."""
    lord = _SIGN_LORD.get(sign, "MARS")
    lord_sign = _sign_of(planet_lons.get(lord, 0.0))

    if lord_sign == sign:
        return 12  # own sign

    if direction == "forward":
        k = (lord_sign - sign) % 12
    else:
        k = (sign - lord_sign) % 12
    if k == 0:
        k = 12

    years = k - 1
    if _is_exalted(lord, lord_sign):
        years += 1
    elif _is_debilitated(lord, lord_sign):
        years -= 1

    return max(1, min(12, years))


def _format_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SHOOLA DASHA
# ═══════════════════════════════════════════════════════════════════════════════

def compute_shoola_dasha(
    lagna_sign: int,
    seventh_sign: int,
    planet_lons: Dict[str, float],
    birth_date: datetime,
    shadbala: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Shoola Dasha — Ayur (Longevity) Dasha.

    Rules:
      - ALWAYS progresses FORWARD (no reversal unlike Niryana Shoola).
      - Start: stronger of Lagna lord vs 7th lord.
      - Duration: Sthira years (Movable=7, Fixed=8, Dual=9). Max 108 years.
      - Rudra: stronger of 2nd lord vs 8th lord (death timing marker).
      - Trishoola: 1st + 5th + 9th from Rudra sign (critical mortality windows).
    """
    lagna_lord  = _SIGN_LORD[lagna_sign]
    seventh_lord = _SIGN_LORD[seventh_sign]

    # Starting sign: sign of the stronger lord
    stronger_lord = _shadbala_stronger(lagna_lord, seventh_lord, shadbala, planet_lons)
    start_sign = _sign_of(planet_lons.get(stronger_lord, 0.0))

    # Rudra = stronger of 2nd lord vs 8th lord
    second_sign  = (lagna_sign + 1) % 12
    eighth_sign  = (lagna_sign + 7) % 12
    second_lord  = _SIGN_LORD[second_sign]
    eighth_lord  = _SIGN_LORD[eighth_sign]
    rudra_lord   = _shadbala_stronger(second_lord, eighth_lord, shadbala, planet_lons)
    rudra_sign   = _sign_of(planet_lons.get(rudra_lord, 0.0))
    # Trishoola: 1st, 5th, 9th from Rudra
    trishoola_signs = [rudra_sign, (rudra_sign+4)%12, (rudra_sign+8)%12]

    # Generate 12-sign sequence forward from start_sign
    periods = []
    current = birth_date
    for i in range(12):
        sign = (start_sign + i) % 12
        years = _STHIRA_YEARS[sign]
        end = current + timedelta(days=years * 365.25)
        is_trishoola = sign in trishoola_signs
        periods.append({
            "sign": sign,
            "sign_name": SIGN_NAMES[sign],
            "years": years,
            "start": _format_date(current),
            "end":   _format_date(end),
            "is_trishoola": is_trishoola,
            "trishoola_note": "Critical mortality window (Trishoola)" if is_trishoola else "",
        })
        current = end

    return {
        "dasha_type": "Shoola Dasha",
        "category": "Ayur (Longevity)",
        "direction": "always forward",
        "start_sign": SIGN_NAMES[start_sign],
        "start_from": f"stronger of {lagna_lord}(lagna lord) vs {seventh_lord}(7th lord) = {stronger_lord}",
        "rudra": rudra_lord,
        "rudra_sign": SIGN_NAMES[rudra_sign],
        "trishoola": [SIGN_NAMES[s] for s in trishoola_signs],
        "periods": periods,
        "usage": "Use Sthira Karakas (not Chara) for sub-level event timing within Shoola.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. NIRYANA SHOOLA DASHA
# ═══════════════════════════════════════════════════════════════════════════════

def compute_niryana_shoola_dasha(
    lagna_sign: int,
    seventh_sign: int,
    planet_lons: Dict[str, float],
    birth_date: datetime,
    shadbala: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Niryana Shoola Dasha — Ayur Dasha.

    Rules:
      - Start: stronger of Lagna vs 7th lord's sign.
      - Odd sign (Aries,Gem,Leo,Lib,Sag,Aqu): DIRECT progression.
      - Even sign (Tau,Can,Vir,Sco,Cap,Pis): REVERSE progression.
      - Fixed 9 YEARS per sign (not variable).
      - Prani Rudra = stronger of 8th lord from Lagna vs 8th lord from 7th.
      - Trishoola = 1st + 5th + 9th from Prani Rudra sign.
    """
    lagna_lord  = _SIGN_LORD[lagna_sign]
    seventh_lord = _SIGN_LORD[seventh_sign]
    stronger_lord = _shadbala_stronger(lagna_lord, seventh_lord, shadbala, planet_lons)
    start_sign   = _sign_of(planet_lons.get(stronger_lord, 0.0))

    # Direction: odd signs (0-based: Aries=0,Gemini=2,Leo=4,Libra=6,Sagittarius=8,Aquarius=10)
    odd_signs = frozenset({0, 2, 4, 6, 8, 10})
    direction = "forward" if start_sign in odd_signs else "backward"
    step = 1 if direction == "forward" else -1

    # Prani Rudra: stronger of 8th lord from Lagna vs 8th lord from 7th
    eighth_from_lagna  = (lagna_sign + 7) % 12
    eighth_from_seventh = (seventh_sign + 7) % 12
    rudra_a = _SIGN_LORD[eighth_from_lagna]
    rudra_b = _SIGN_LORD[eighth_from_seventh]
    prani_rudra = _shadbala_stronger(rudra_a, rudra_b, shadbala, planet_lons)
    rudra_sign  = _sign_of(planet_lons.get(prani_rudra, 0.0))
    trishoola_signs = [rudra_sign, (rudra_sign+4)%12, (rudra_sign+8)%12]

    periods = []
    current = birth_date
    for i in range(12):
        sign = (start_sign + i * step) % 12
        years = 9  # fixed 9 years per sign
        end = current + timedelta(days=years * 365.25)
        is_trishoola = sign in trishoola_signs
        periods.append({
            "sign": sign,
            "sign_name": SIGN_NAMES[sign],
            "years": years,
            "start": _format_date(current),
            "end":   _format_date(end),
            "is_trishoola": is_trishoola,
            "trishoola_note": "Critical mortality window (Trishoola)" if is_trishoola else "",
        })
        current = end

    return {
        "dasha_type": "Niryana Shoola Dasha",
        "category": "Ayur (Longevity)",
        "direction": direction,
        "start_sign": SIGN_NAMES[start_sign],
        "start_from": f"stronger of {lagna_lord} vs {seventh_lord} = {stronger_lord}",
        "prani_rudra": prani_rudra,
        "rudra_sign": SIGN_NAMES[rudra_sign],
        "trishoola": [SIGN_NAMES[s] for s in trishoola_signs],
        "periods": periods,
        "usage": "Ayur Dasha — use Sthira Karakas, NOT Chara Karakas.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. BRAHMA DASHA
# ═══════════════════════════════════════════════════════════════════════════════

_BRAHMA_EXCLUDED = frozenset({"SATURN", "RAHU", "KETU"})  # Cannot be Brahma

def _find_brahma_planet(
    reference_sign: int,   # stronger of Lagna vs 7th lord's sign
    planet_lons: Dict[str, float],
    shadbala: Optional[Dict[str, float]] = None,
) -> str:
    """
    Brahma = strongest planet among 6th, 8th, 12th lords FROM reference sign.
    Saturn, Rahu, Ketu excluded from being Brahma.
    """
    sixth_sign  = (reference_sign + 5) % 12
    eighth_sign  = (reference_sign + 7) % 12
    twelfth_sign = (reference_sign + 11) % 12

    candidates: List[Tuple[str, float]] = []
    for s in (sixth_sign, eighth_sign, twelfth_sign):
        lord = _SIGN_LORD[s]
        if lord not in _BRAHMA_EXCLUDED:
            strength = shadbala.get(lord, 0.5) if shadbala else 0.5
            candidates.append((lord, strength))

    if not candidates:
        return "JUPITER"  # fallback

    # Strongest (highest Shadbala)
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]


def compute_brahma_dasha(
    lagna_sign: int,
    seventh_sign: int,
    ak_sign: int,            # Sign of Atmakaraka in D-1
    planet_lons: Dict[str, float],
    birth_date: datetime,
    shadbala: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Brahma Dasha — Soul-level timing dasha.

    Rules:
      - Determine stronger of Lagna vs 7th (reference sign).
      - Brahma = strongest of 6th/8th/12th lords from reference (excl Saturn/Rahu/Ketu).
      - Dasha starts from Brahma's sign.
      - Maheshwara = 8th lord from AK sign (in D-1).
      - Duration: Sthira periods (Movable=7, Fixed=8, Dual=9).
    """
    lagna_lord  = _SIGN_LORD[lagna_sign]
    seventh_lord = _SIGN_LORD[seventh_sign]
    stronger_lord = _shadbala_stronger(lagna_lord, seventh_lord, shadbala, planet_lons)
    ref_sign      = _sign_of(planet_lons.get(stronger_lord, 0.0))

    brahma_planet = _find_brahma_planet(ref_sign, planet_lons, shadbala)
    brahma_sign   = _sign_of(planet_lons.get(brahma_planet, 0.0))

    # Maheshwara = 8th lord from AK sign
    eighth_from_ak = (ak_sign + 7) % 12
    maheshwara     = _SIGN_LORD[eighth_from_ak]

    # Sthira Dasha sequence forward from Brahma sign
    periods = []
    current = birth_date
    for i in range(12):
        sign  = (brahma_sign + i) % 12
        years = _STHIRA_YEARS[sign]
        end   = current + timedelta(days=years * 365.25)
        periods.append({
            "sign": sign,
            "sign_name": SIGN_NAMES[sign],
            "years": years,
            "start": _format_date(current),
            "end":   _format_date(end),
        })
        current = end

    return {
        "dasha_type": "Brahma Dasha",
        "category": "Soul-level",
        "brahma_planet": brahma_planet,
        "brahma_sign": SIGN_NAMES[brahma_sign],
        "maheshwara": maheshwara,
        "maheshwara_sign": SIGN_NAMES[eighth_from_ak],
        "reference_sign": SIGN_NAMES[ref_sign],
        "direction": "forward (Sthira sequence)",
        "periods": periods,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. NAVAMSHA DASHA
# ═══════════════════════════════════════════════════════════════════════════════

def compute_navamsha_dasha(
    d9_lagna_sign: int,
    planet_d9_signs: Dict[str, int],
    planet_d1_lons: Dict[str, float],
    birth_date: datetime,
) -> Dict:
    """
    Navamsha Dasha — operates entirely in D-9 chart.

    Rules:
      - Start from Navamsha Lagna (D-9 Ascendant sign).
      - Odd sign → direct; Even sign → reverse.
      - Duration = distance from sign to its lord IN D-9 (k-1 years).
        If lord in own sign → 12 years.
        Exaltation → +1 year. Debilitation → -1 year.
    """
    odd_signs = frozenset({0, 2, 4, 6, 8, 10})
    direction = "forward" if d9_lagna_sign in odd_signs else "backward"
    step = 1 if direction == "forward" else -1

    def _d9_duration(sign: int) -> int:
        lord = _SIGN_LORD.get(sign, "MARS")
        lord_d9_sign = planet_d9_signs.get(lord, sign)
        if lord_d9_sign == sign:
            return 12
        if direction == "forward":
            k = (lord_d9_sign - sign) % 12
        else:
            k = (sign - lord_d9_sign) % 12
        if k == 0:
            k = 12
        years = k - 1

        # Exalt/debil in D-9
        if _is_exalted(lord, lord_d9_sign):
            years += 1
        elif _is_debilitated(lord, lord_d9_sign):
            years -= 1

        # Also check D-1 exaltation/debilitation
        d1_sign = _sign_of(planet_d1_lons.get(lord, 0.0))
        if _is_exalted(lord, d1_sign):
            years += 1
        elif _is_debilitated(lord, d1_sign):
            years -= 1

        return max(1, min(12, years))

    periods = []
    current = birth_date
    for i in range(12):
        sign  = (d9_lagna_sign + i * step) % 12
        years = _d9_duration(sign)
        end   = current + timedelta(days=years * 365.25)
        periods.append({
            "sign": sign,
            "sign_name": SIGN_NAMES[sign],
            "years": years,
            "start": _format_date(current),
            "end":   _format_date(end),
        })
        current = end

    return {
        "dasha_type": "Navamsha Dasha",
        "category": "Soul-microscope (D-9 based)",
        "d9_lagna": SIGN_NAMES[d9_lagna_sign],
        "direction": direction,
        "periods": periods,
        "usage": "Microscopic soul strength and inner spiritual reality. D-9 has veto power over D-1.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 5. SREE LAGNA DASHA (SUDASA)
# ═══════════════════════════════════════════════════════════════════════════════

def compute_sree_lagna(
    moon_lon: float,
    lagna_lon: float,
) -> float:
    """
    Compute Sree Lagna (SL) longitude.

    Formula:
      1. Compute Moon's nakshatra index (0-26) and elapsed fraction.
      2. Multiply elapsed fraction by 360° to get elapsed proportional arc.
      3. SL = Lagna longitude + elapsed arc (mod 360).
    """
    nakshatra_span = 360.0 / 27.0   # ≈ 13.333°
    moon_norm = moon_lon % 360.0
    nak_idx   = int(moon_norm / nakshatra_span)
    nak_start = nak_idx * nakshatra_span
    elapsed_fraction = (moon_norm - nak_start) / nakshatra_span
    elapsed_arc = elapsed_fraction * 360.0
    sl_lon = (lagna_lon + elapsed_arc) % 360.0
    return sl_lon


# Odd-footed signs (forward counting to lord)
_ODD_FOOTED = frozenset({0, 1, 2, 6, 7, 8})  # Aries,Taurus,Gemini,Libra,Scorpio,Sagittarius


def compute_sudasa(
    moon_lon: float,
    lagna_lon: float,
    planet_lons: Dict[str, float],
    birth_date: datetime,
    shadbala: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Sree Lagna Dasha (Sudasa) — wealth and prosperity timing.

    Sequence: Kendras from SL (1st,4th,7th,10th) →
              Panapharas (2nd,5th,8th,11th) →
              Apoklimas (3rd,6th,9th,12th)

    Duration: odd-footed → count forward to lord; even-footed → count backward.
              Subtract 1 = years. First period fractionally adjusted.
    """
    sl_lon  = compute_sree_lagna(moon_lon, lagna_lon)
    sl_sign = _sign_of(sl_lon)
    sl_deg  = sl_lon % 30.0

    # Sequence: Kendra → Panaphara → Apoklima from SL
    offsets = [0, 3, 6, 9,  1, 4, 7, 10,  2, 5, 8, 11]
    sequence = [(sl_sign + off) % 12 for off in offsets]

    def _sudasa_years(sign: int) -> int:
        lord = _SIGN_LORD.get(sign, "MARS")
        lord_sign = _sign_of(planet_lons.get(lord, 0.0))
        is_odd = sign in _ODD_FOOTED
        if lord_sign == sign:
            return 12 - 1  # own sign: distance=12, subtract 1 = 11
        if is_odd:
            k = (lord_sign - sign) % 12
        else:
            k = (sign - lord_sign) % 12
        if k == 0:
            k = 12
        return max(1, min(11, k - 1))

    # First period fractional adjustment based on SL's remaining degrees in sign
    remaining_frac = (30.0 - sl_deg) / 30.0

    periods = []
    current = birth_date
    for idx, sign in enumerate(sequence):
        raw_years = _sudasa_years(sign)
        if idx == 0:
            # First period is fractional
            years_float = raw_years * remaining_frac
        else:
            years_float = float(raw_years)

        end = current + timedelta(days=years_float * 365.25)
        periods.append({
            "sign":      sign,
            "sign_name": SIGN_NAMES[sign],
            "years":     round(years_float, 2),
            "start":     _format_date(current),
            "end":       _format_date(end),
            "cluster":   ("Kendra" if idx < 4 else
                          "Panaphara" if idx < 8 else "Apoklima"),
        })
        current = end

    return {
        "dasha_type": "Sree Lagna Dasha (Sudasa)",
        "category": "Phalita — wealth and Lakshmi blessings",
        "sree_lagna_lon": round(sl_lon, 4),
        "sree_lagna_sign": SIGN_NAMES[sl_sign],
        "sree_lagna_deg":  round(sl_deg, 4),
        "sequence": ["Kendras", "Panapharas", "Apoklimas"],
        "periods": periods,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 6. DRIG DASHA
# ═══════════════════════════════════════════════════════════════════════════════

def compute_drig_dasha(
    lagna_sign: int,
    birth_date: datetime,
) -> Dict:
    """
    Drig Dasha — spiritual evolution and Argala-based Raja Yoga timing.

    Sequence (Trikuta Padakrama):
      Cluster 1: 9th  house from Lagna + its 3 Rashi Drishti targets (4 signs)
      Cluster 2: 10th house from Lagna + its 3 Rashi Drishti targets (4 signs)
      Cluster 3: 11th house from Lagna + its 3 Rashi Drishti targets (4 signs)

    Duration: Sthira periods (Movable=7, Fixed=8, Dual=9).
    """
    def _get_rd_targets(sign: int) -> List[int]:
        return sorted(_RASHI_DRISHTI.get(sign, frozenset()))

    ninth  = (lagna_sign + 8) % 12
    tenth  = (lagna_sign + 9) % 12
    eleventh = (lagna_sign + 10) % 12

    sequence = (
        [ninth]   + _get_rd_targets(ninth) +
        [tenth]   + _get_rd_targets(tenth) +
        [eleventh] + _get_rd_targets(eleventh)
    )
    # Remove duplicates while preserving order
    seen = set()
    deduped = []
    for s in sequence:
        if s not in seen:
            seen.add(s)
            deduped.append(s)

    periods = []
    current = birth_date
    cluster_names = (
        [f"9th cluster ({SIGN_NAMES[ninth]})"] * 4 +
        [f"10th cluster ({SIGN_NAMES[tenth]})"] * 4 +
        [f"11th cluster ({SIGN_NAMES[eleventh]})"] * 4
    )
    for idx, sign in enumerate(deduped):
        years = _STHIRA_YEARS[sign]
        end   = current + timedelta(days=years * 365.25)
        cluster_label = cluster_names[idx] if idx < len(cluster_names) else "extended"
        periods.append({
            "sign":      sign,
            "sign_name": SIGN_NAMES[sign],
            "years":     years,
            "start":     _format_date(current),
            "end":       _format_date(end),
            "cluster":   cluster_label,
        })
        current = end

    return {
        "dasha_type": "Drig Dasha",
        "category": "Spiritual evolution; Argala Raja Yoga timing",
        "ninth_house":   SIGN_NAMES[ninth],
        "tenth_house":   SIGN_NAMES[tenth],
        "eleventh_house": SIGN_NAMES[eleventh],
        "sequence_signs": [SIGN_NAMES[s] for s in deduped],
        "periods": periods,
        "usage": "Spiritual milestones, renunciation periods, Argala-based Raja Yoga manifestation.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 7. TRIKONA DASHA
# ═══════════════════════════════════════════════════════════════════════════════

def compute_trikona_dasha(
    lagna_sign: int,
    planet_lons: Dict[str, float],
    birth_date: datetime,
    planet_houses: Optional[Dict[str, int]] = None,
    shadbala: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Trikona Dasha — marriage and childbirth timing.

    Rules:
      - Evaluate mathematical strengths of 1st, 5th, 9th houses from Lagna.
      - Start from the STRONGEST of these three trinal signs.
      - Strength = number of planets in sign + Rashi Drishti aspects + Shadbala.
      - Odd sign → forward. Even sign → backward.
      - Duration: Chara Dasha formula (distance to lord - 1).
    """
    trikona_signs = [
        lagna_sign,
        (lagna_sign + 4) % 12,   # 5th
        (lagna_sign + 8) % 12,   # 9th
    ]

    def _sign_strength(sign: int) -> float:
        score = 0.0
        # Count resident planets
        for p, lon in planet_lons.items():
            if _sign_of(lon) == sign:
                score += shadbala.get(p, 0.5) if shadbala else 0.5
        # Count Rashi Drishti aspects
        for p, lon in planet_lons.items():
            if _sign_of(lon) != sign and sign in _RASHI_DRISHTI.get(_sign_of(lon), frozenset()):
                score += 0.2
        return score

    strengths = {s: _sign_strength(s) for s in trikona_signs}
    start_sign = max(strengths, key=strengths.get)  # type: ignore

    odd_signs = frozenset({0, 2, 4, 6, 8, 10})
    direction = "forward" if start_sign in odd_signs else "backward"
    step = 1 if direction == "forward" else -1

    periods = []
    current = birth_date
    for i in range(12):
        sign  = (start_sign + i * step) % 12
        years = _chara_duration(sign, direction, planet_lons)
        end   = current + timedelta(days=years * 365.25)
        periods.append({
            "sign":      sign,
            "sign_name": SIGN_NAMES[sign],
            "years":     years,
            "start":     _format_date(current),
            "end":       _format_date(end),
        })
        current = end

    return {
        "dasha_type": "Trikona Dasha",
        "category": "Phalita — marriage, childbirth, auspicious events",
        "trikona_signs": {SIGN_NAMES[s]: round(strengths[s], 3) for s in trikona_signs},
        "start_sign": SIGN_NAMES[start_sign],
        "direction": direction,
        "periods": periods,
        "usage": "Confirms highly auspicious life events: marriage, childbirth. Use with UL+DK framework.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ACTIVE DASHA FINDER (shared utility)
# ═══════════════════════════════════════════════════════════════════════════════

def get_active_period(periods: List[Dict], on_date: datetime) -> Optional[Dict]:
    """Return the active period dict for the given date (from Shoola/Niryana/etc.)."""
    for p in periods:
        try:
            start = datetime.strptime(p["start"], "%Y-%m-%d")
            end   = datetime.strptime(p["end"],   "%Y-%m-%d")
            if start <= on_date < end:
                return p
        except Exception:
            pass
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# DEATH TIMING RULE (Shoola Dasha — SUTRA 9)
# ═══════════════════════════════════════════════════════════════════════════════

def check_death_timing_window(
    active_shoola_sign: int,
    shoola_antar_sign: int,
    rudra_sign: int,
    al_sign: int,
) -> Dict:
    """
    SUTRA 9: Death timing flag for critical mortality windows.

    Conditions:
      1. Active Shoola Maha = Trishoola sign (1/5/9 from Rudra).
      2. Shoola Antar = 6th/7th/8th/12th from Dasha sign or Arudha Lagna.
    Both must be true for HIGH risk window.
    """
    trishoola = {rudra_sign, (rudra_sign+4)%12, (rudra_sign+8)%12}
    maha_is_trishoola = active_shoola_sign in trishoola

    # Antar from Dasha sign
    antar_from_dasha = ((shoola_antar_sign - active_shoola_sign) % 12) + 1
    # Antar from AL
    antar_from_al    = ((shoola_antar_sign - al_sign) % 12) + 1

    critical_houses = {6, 7, 8, 12}
    antar_critical = (antar_from_dasha in critical_houses or antar_from_al in critical_houses)

    flag = maha_is_trishoola and antar_critical
    risk_level = "CRITICAL" if flag else ("ELEVATED" if maha_is_trishoola else "NORMAL")

    return {
        "death_risk_flag":        flag,
        "risk_level":             risk_level,
        "maha_is_trishoola":      maha_is_trishoola,
        "antar_critical_position": antar_critical,
        "antar_from_dasha":       antar_from_dasha,
        "antar_from_al":          antar_from_al,
        "note":                   (
            "SUTRA 9: Critical mortality window. Confirm with Sthira Karaka antardasha analysis."
            if flag else "No critical mortality convergence at this time."
        ),
    }
