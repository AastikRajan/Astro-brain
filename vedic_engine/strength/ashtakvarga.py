"""
Ashtakvarga Engine.
Computes Bhinna Ashtakvarga (BAV), Sarvashtakvarga (SAV),
Trikona Shodhana, Ekadhipatya Shodhana, and Pinda Sadhana.

All rules from deep-research-report.md + BPHS offset tables in config.py.
Checksum invariant: SAV total must equal 337.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

from vedic_engine.config import (
    Planet, Sign, ASHTAKVARGA_RULES, ASHTAKVARGA_TOTALS,
    SARVASHTAKVARGA_TOTAL, TRIKONA_GROUPS,
    RASHI_MULTIPLIERS, GRAHA_MULTIPLIERS,
    OWN_SIGNS, SIGN_LORDS,
)

PLANET_NAMES_7 = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]
SIGN_NAMES = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
              "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

PLANET_BAV_GOOD_THRESHOLD = {
    "SUN": 4,
    "MOON": 5,
    "MARS": 4,
    "MERCURY": 5,
    "JUPITER": 5,
    "VENUS": 5,
    "SATURN": 4,
}

SAV_HOUSE_MINIMUM = {
    1: 25,
    2: 22,
    3: 29,
    4: 24,
    5: 25,
    6: 34,
    7: 19,
    8: 24,
    9: 29,
    10: 36,
    11: 54,
    12: 16,
}

_DUSTHANA_HOUSES = {6, 8, 12}

_P = {
    "SUN": Planet.SUN, "MOON": Planet.MOON, "MARS": Planet.MARS,
    "MERCURY": Planet.MERCURY, "JUPITER": Planet.JUPITER,
    "VENUS": Planet.VENUS, "SATURN": Planet.SATURN,
}


def compute_bhinna_ashtakvarga(
        recipient: str,
        planet_signs: Dict[str, int],   # planet_name → sign_index (0-11)
        lagna_sign: int,
) -> List[int]:
    """
    Compute Bhinna Ashtakvarga for one recipient planet.

    For each donor in {7 planets + ASC}:
      favorable_signs = {(donor_sign + offset - 1) % 12 for offset in OFFSETS[recipient][donor]}
      Add 1 to those signs.

    Returns list of 12 bindu counts (0-8 max per sign).
    """
    p_enum = _P.get(recipient.upper())
    if p_enum is None:
        return [0] * 12

    rules = ASHTAKVARGA_RULES.get(p_enum, {})
    bindus = [0] * 12

    # 7 planet donors
    for donor_name, donor_sign in planet_signs.items():
        donor_p = _P.get(donor_name.upper())
        if donor_p is None:
            continue
        offsets = rules.get(donor_p, [])
        for offset in offsets:
            target_sign = (donor_sign + offset - 1) % 12
            bindus[target_sign] += 1

    # Lagna (ASC) donor
    lagna_offsets = rules.get('ASC', [])
    for offset in lagna_offsets:
        target_sign = (lagna_sign + offset - 1) % 12
        bindus[target_sign] += 1

    return bindus


def compute_all_bhinna(
        planet_signs: Dict[str, int],  # {planet: sign_index}
        lagna_sign: int,
) -> Dict[str, List[int]]:
    """Compute BAV for all 7 classical planets. Returns {planet: [12 bindus]}."""
    result = {}
    for pname in PLANET_NAMES_7:
        result[pname] = compute_bhinna_ashtakvarga(pname, planet_signs, lagna_sign)
    return result


def compute_sarvashtakvarga(bhinna: Dict[str, List[int]]) -> List[int]:
    """SAV[sign] = sum of all 7 planets' BAV for that sign. Should total 337."""
    sarva = [0] * 12
    for pname in PLANET_NAMES_7:
        bav = bhinna.get(pname, [0] * 12)
        for i in range(12):
            sarva[i] += bav[i]
    return sarva


def compute_sav_profile(sarva: List[int]) -> Dict:
    """
    Build advanced SAV diagnostics: house threshold status, wealth/loss ratios,
    and core comparative rules used in prediction explanations.
    """
    if not isinstance(sarva, list) or len(sarva) < 12:
        return {
            "error": "Invalid SAV list",
            "houses": {},
        }

    houses: Dict[int, Dict] = {}
    for h in range(1, 13):
        val = int(sarva[h - 1])
        min_req = SAV_HOUSE_MINIMUM.get(h, 28)
        if h in _DUSTHANA_HOUSES:
            status = "PROTECTIVE" if val <= min_req else "VULNERABLE"
        else:
            status = "SUPPORTED" if val >= min_req else "UNDER_MIN"
        houses[h] = {
            "sav": val,
            "minimum": min_req,
            "status": status,
            "reversed": h in _DUSTHANA_HOUSES,
        }

    vittya = int(sarva[1] + sarva[3] + sarva[8] + sarva[9] + sarva[10])
    teertha = int(sarva[5] + sarva[7] + sarva[11])
    h2 = int(sarva[1])
    h12 = int(sarva[11])
    h1 = int(sarva[0])
    h8 = int(sarva[7])

    return {
        "houses": houses,
        "vittya": {
            "score": vittya,
            "threshold": 164,
            "status": "PROSPEROUS" if vittya > 164 else ("BALANCED" if vittya == 164 else "STRAINED"),
            "ratio": round(vittya / 164.0, 3),
        },
        "teertha": {
            "score": teertha,
            "threshold": 76,
            "status": "PROTECTED" if teertha < 76 else "VULNERABLE",
            "ratio": round(teertha / 76.0, 3),
        },
        "savings_capacity": {
            "h2": h2,
            "h12": h12,
            "can_save": h2 > h12,
            "ratio": round((h2 / h12), 3) if h12 > 0 else None,
        },
        "h1_vs_h8": {
            "h1": h1,
            "h8": h8,
            "healthy_balance": h1 > h8,
        },
    }


def validate_checksum(bhinna: Dict[str, List[int]]) -> Dict[str, bool]:
    """Validate that each planet's BAV sums to the expected total."""
    results = {}
    for pname in PLANET_NAMES_7:
        actual = sum(bhinna.get(pname, []))
        expected = ASHTAKVARGA_TOTALS.get(_P[pname], 0)
        results[pname] = actual == expected
        if not results[pname]:
            print(f"  [WARN] {pname} BAV sum={actual}, expected={expected}")
    sarva_total = sum(sum(bhinna.get(p, [])) for p in PLANET_NAMES_7)
    results["SARVA_337"] = sarva_total == SARVASHTAKVARGA_TOTAL
    return results


def trikona_shodhana(bindus: List[int]) -> List[int]:
    """
    Trikona (trine) reduction on a single planet's BAV.
    Groups: (Aries,Leo,Sag), (Taurus,Virgo,Cap), (Gemini,Lib,Aqua), (Cancer,Sco,Pis)
    Rule:
      - If any in trine is 0, no reduction.
      - If all equal, reduce all to 0.
      - Otherwise, subtract the minimum from the other two.
    Returns new list of 12 bindus.
    """
    result = list(bindus)
    for group in TRIKONA_GROUPS:
        indices = [s.value for s in group]
        vals = [result[i] for i in indices]

        if 0 in vals:
            continue  # Any zero → no reduction
        if vals[0] == vals[1] == vals[2]:
            for i in indices:
                result[i] = 0
        else:
            mn = min(vals)
            for i in indices:
                result[i] -= mn
    return result


def ekadhipatya_shodhana(
        bindus: List[int],
        recipient_planet: str,
        planet_signs: Dict[str, int],
) -> List[int]:
    """
    Ekadhipatya (dual-lordship) reduction applied AFTER Trikona Shodhana.

    For each planet that owns TWO signs:
      - If both signs have values AND one is sign-less (0), no reduction.
      - If both occupied by planets, no reduction.
      - If neither occupied or one occupied: subtract smaller from larger.
    """
    result = list(bindus)
    occupied_signs = set(planet_signs.values())

    for planet, own_sign_list in OWN_SIGNS.items():
        if len(own_sign_list) < 2:
            continue
        s1, s2 = own_sign_list[0].value, own_sign_list[1].value
        v1, v2 = result[s1], result[s2]

        # If any is 0-valued from trikona: skip
        if v1 == 0 or v2 == 0:
            continue

        # If both signs are occupied by planets: no reduction
        if s1 in occupied_signs and s2 in occupied_signs:
            continue

        # Apply: subtract lesser from greater
        mn = min(v1, v2)
        result[s1] -= mn
        result[s2] -= mn
    return result


def pinda_sadhana(
        reduced_bindus: List[int],   # After shodhana reductions
        planet_name: str,
        planet_signs: Dict[str, int],  # Which sign each planet is in
) -> int:
    """
    Pinda Sadhana: weighted sum of reduced bindus.
    Pinda(g) = Σ_s [ reduced(s) × rashi_multiplier(s) × graha_multiplier(g, s) ]
    graha multiplier only applied when a planet is IN that sign.
    """
    p = _P.get(planet_name)
    if p is None:
        return 0

    total = 0
    g_mult = GRAHA_MULTIPLIERS.get(p, 1)
    planets_in_sign: Dict[int, bool] = {}
    for pn, si in planet_signs.items():
        planets_in_sign[si] = True

    for s_idx, r_mult in RASHI_MULTIPLIERS.items():
        val = reduced_bindus[s_idx.value]
        if val == 0:
            continue
        mult = r_mult
        if planets_in_sign.get(s_idx.value, False):
            mult *= g_mult
        total += val * mult

    return total


def compute_full_ashtakvarga(
        planet_signs: Dict[str, int],  # {planet_name: sign_index}
        lagna_sign: int,
) -> Dict:
    """
    Complete Ashtakvarga computation pipeline:
    1. Bhinna AV for all 7 planets
    2. Sarvashtakvarga
    3. Checksum validation
    4. Trikona + Ekadhipatya Shodhana per planet
    5. Pinda Sadhana per planet (legacy combined formula)
    6. Shodhya Pinda per planet (Phase 1C: correct R+G formula)
    7. Prastharashtakavarga / PAV (Phase 1C: full 8×12 kakshya matrix)
    """
    bhinna = compute_all_bhinna(planet_signs, lagna_sign)
    sarva = compute_sarvashtakvarga(bhinna)
    checks = validate_checksum(bhinna)

    shodhana_results = {}
    pinda_results = {}
    for pname in PLANET_NAMES_7:
        bav = bhinna[pname]
        after_trikona = trikona_shodhana(bav)
        after_ekad = ekadhipatya_shodhana(after_trikona, pname, planet_signs)
        shodhana_results[pname] = after_ekad
        pinda_results[pname] = pinda_sadhana(after_ekad, pname, planet_signs)

    # Phase 1C: Shodhya Pinda (correct Rashi Pinda + Graha Pinda formula)
    shodhya_pinda = compute_shodhya_pinda(shodhana_results, planet_signs)

    # Phase 1C: Prastharashtakavarga (PAV) — full 8-contributor × 12-sign matrices
    pav = compute_prastharashtakavarga(planet_signs, lagna_sign)

    return {
        "bhinna": bhinna,
        "sarva": sarva,
        "sarva_total": sum(sarva),
        "sav_profile": compute_sav_profile(sarva),
        "checksums": checks,
        "shodhana": shodhana_results,
        "pinda": pinda_results,
        "shodhya_pinda": shodhya_pinda,
        "pav": pav,
        "sign_names": SIGN_NAMES,
    }


def transit_av_score(
        planet: str,
        transit_sign: int,
        bhinna: Dict[str, List[int]],
        sarva: List[int],
) -> Dict:
    """
    Transit evaluation for a planet entering a given sign.
    Returns BAV score, SAV score, and whether it's above average.
    """
    bav = bhinna.get(planet.upper(), [0] * 12)
    bav_score = bav[transit_sign]
    sav_score = sarva[transit_sign]
    sav_avg = SARVASHTAKVARGA_TOTAL / 12.0  # ≈ 28.08

    return {
        "planet": planet,
        "transit_sign": SIGN_NAMES[transit_sign],
        "bav_score": bav_score,
        "sav_score": sav_score,
        "sav_above_average": sav_score > sav_avg,
        "bav_above_average": bav_score > 4,  # >4 of 8 is above average
        "overall_favorable": bav_score > 3 and sav_score > sav_avg,
    }


def calculate_transit_quality(
        transiting_planet: str,
        transit_sign: int,
        bhinna: Dict[str, List[int]],
) -> Dict:
    """
    Classify transit quality from planet-specific BAV threshold with a bounded
    multiplier, suitable for optional use in scoring layers.
    """
    p = (transiting_planet or "").upper()
    bav_list = bhinna.get(p, [4] * 12)
    score = int(bav_list[transit_sign]) if transit_sign < len(bav_list) else 4
    threshold = PLANET_BAV_GOOD_THRESHOLD.get(p, 5)

    if score <= 1:
        quality, mult = "HIGHLY_OBSTRUCTED", 0.20
    elif score <= 3:
        quality, mult = "WEAK", 0.50
    elif score == 4:
        quality, mult = "NEUTRAL", 1.00
    elif score <= 6:
        quality, mult = "STRONG", 1.30
    else:
        quality, mult = "EXCELLENT", 1.60

    return {
        "planet": p,
        "sign": transit_sign,
        "bav_score": score,
        "planet_good_threshold": threshold,
        "is_good_by_planet_rule": score >= threshold,
        "quality": quality,
        "multiplier": mult,
    }


def evaluate_kakshya_transit(
        transiting_planet: str,
        transit_sign: int,
        degree_in_sign: float,
        pav: Dict[str, Dict[str, List[int]]],
) -> Dict:
    """
    Evaluate if a transit is favorable in the current kakshya using PAV.
    Expects PAV from compute_prastharashtakavarga().
    """
    p = (transiting_planet or "").upper()
    kakshya_ruler = kakshya_lord_of_degree(float(degree_in_sign))

    p_pav = pav.get(p, {}) if isinstance(pav, dict) else {}
    ruler_row = p_pav.get(kakshya_ruler, []) if isinstance(p_pav, dict) else []
    bindu = int(ruler_row[transit_sign]) if isinstance(ruler_row, list) and transit_sign < len(ruler_row) else 0

    return {
        "planet": p,
        "sign": transit_sign,
        "degree_in_sign": round(float(degree_in_sign), 3),
        "kakshya_ruler": kakshya_ruler,
        "bindu": bindu,
        "result": "AUSPICIOUS" if bindu == 1 else "BARREN",
    }


# ─── Shodhya Pinda (Phase 1C 2026-03-02) ────────────────────────────────────

_RASHI_GUN: List[int] = [7, 10, 8, 4, 10, 5, 7, 8, 9, 5, 11, 12]  # Aries–Pisces
_GRAHA_GUN: Dict[str, int] = {
    "SUN": 5, "MOON": 5, "MARS": 8, "MERCURY": 5,
    "JUPITER": 10, "VENUS": 7, "SATURN": 5,
}


def compute_shodhya_pinda(
        shodhana: Dict[str, List[int]],
        planet_signs: Dict[str, int],
) -> Dict[str, int]:
    """
    Compute Shodhya Pinda for each planet (Phase 1C).

    Formula (BPHS):
      Rashi Pinda  = Σ_s (reduced_bindu[s] × RASHI_GUN[s])   for ALL 12 signs
      Graha Pinda  = Σ_p (reduced_bindu[sign_of_p] × GRAHA_GUN[p])  for each planet
      Shodhya Pinda = Rashi Pinda + Graha Pinda

    Args:
        shodhana:     {planet: [12 reduced bindus]} — output of ekadhipatya_shodhana
        planet_signs: {planet_name: sign_index (0-11)}

    Returns: {planet: shodhya_pinda_integer}
    """
    result: Dict[str, int] = {}
    for pname, bindus in shodhana.items():
        # Rashi Pinda
        rashi_pinda = sum(bindus[s] * _RASHI_GUN[s] for s in range(12))
        # Graha Pinda — for each planet located in a sign, add reduced_bindu × graha_gun
        graha_pinda = 0
        for contrib_name, g_mult in _GRAHA_GUN.items():
            s = planet_signs.get(contrib_name)
            if s is not None:
                graha_pinda += bindus[s] * g_mult
        result[pname] = rashi_pinda + graha_pinda
    return result


# ─── Prastharashtakavarga / PAV (Phase 1C 2026-03-02) ───────────────────────
# 7 planets' PAV contribution tables: {recipient → {contributor → [house_offsets_1based]}}
# Source: Research File 5 (Vedic Astrology Engine: Ashtakavarga & Dashas)

_PAV_TABLES: Dict[str, Dict[str, List[int]]] = {
    "SUN": {
        "SUN":     [1,2,4,7,8,9,10,11],
        "MOON":    [3,6,10,11],
        "MARS":    [1,2,4,7,8,9,10,11],
        "MERCURY": [3,5,6,9,10,11,12],
        "JUPITER": [5,6,9,11],
        "VENUS":   [6,7,12],
        "SATURN":  [1,2,4,7,8,9,10,11],
        "ASC":     [3,4,6,10,11,12],
    },
    "MOON": {
        "SUN":     [3,6,7,8,10,11],
        "MOON":    [1,3,6,7,10,11],
        "MARS":    [2,3,5,6,9,10,11],
        "MERCURY": [1,3,4,5,7,8,10,11],
        "JUPITER": [1,4,7,8,10,11,12],
        "VENUS":   [3,4,5,7,9,10,11],
        "SATURN":  [3,5,6,11],
        "ASC":     [3,6,10,11],
    },
    "MARS": {
        "SUN":     [3,5,6,10,11],
        "MOON":    [3,6,11],
        "MARS":    [1,2,4,7,8,10,11],
        "MERCURY": [3,5,6,11],
        "JUPITER": [6,10,11,12],
        "VENUS":   [6,8,11,12],
        "SATURN":  [1,4,7,8,9,10,11],
        "ASC":     [1,3,6,10,11],
    },
    "MERCURY": {
        "SUN":     [5,6,9,11,12],
        "MOON":    [2,4,6,8,10,11],
        "MARS":    [1,2,4,7,8,9,10,11],
        "MERCURY": [1,3,5,6,9,10,11,12],
        "JUPITER": [6,8,11,12],
        "VENUS":   [1,2,3,4,5,8,9,11],
        "SATURN":  [1,2,4,7,8,9,10,11],
        "ASC":     [1,2,4,6,8,10,11],
    },
    "JUPITER": {
        "SUN":     [1,2,3,4,7,8,9,10,11],
        "MOON":    [2,5,7,9,11],
        "MARS":    [1,2,4,7,8,10,11],
        "MERCURY": [1,2,4,5,6,9,10,11],
        "JUPITER": [1,2,3,4,7,8,10,11],
        "VENUS":   [2,5,6,9,10,11],
        "SATURN":  [3,5,6,12],
        "ASC":     [1,2,4,5,6,7,9,10,11],
    },
    "VENUS": {
        "SUN":     [8,11,12],
        "MOON":    [1,2,3,4,5,8,9,11,12],
        "MARS":    [3,5,6,9,11,12],
        "MERCURY": [3,5,6,9,11],
        "JUPITER": [5,8,9,10,11],
        "VENUS":   [1,2,3,4,5,8,9,10,11],
        "SATURN":  [3,4,5,8,9,10,11],
        "ASC":     [1,2,3,4,5,8,9,11],
    },
    "SATURN": {
        "SUN":     [1,2,4,7,8,10,11],
        "MOON":    [3,6,11],
        "MARS":    [3,5,6,10,11,12],
        "MERCURY": [6,8,9,10,11,12],
        "JUPITER": [5,6,11,12],
        "VENUS":   [6,11,12],
        "SATURN":  [3,5,6,11],
        "ASC":     [1,3,4,6,10,11],
    },
}

_CONTRIBUTORS = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "ASC"]


def compute_prastharashtakavarga(
        planet_signs: Dict[str, int],
        lagna_sign: int,
) -> Dict[str, Dict[str, List[int]]]:
    """
    Compute Prastharashtakavarga (PAV) — the full 8-contributor × 12-sign matrix
    for each of the 7 classical planets. (Phase 1C 2026-03-02)

    PAV[recipient][contributor] = [12 bindus (0 or 1)]
    A bindu of 1 at sign S means contributor at natal_sign gave a benefic to sign S.

    Contributors: SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, ASC(Lagna)

    Kakshya use: Each sign divides into 8 kakshyas (3°45' each), ruled by
    SAT→JUP→MAR→SUN→VEN→MER→MOO→ASC. A transit is favorable in a kakshya if
    PAV[planet][kakshya_lord][transit_sign] == 1.

    Returns:
        { recipient_planet: { contributor: [12 int (0/1)] }, ... }
    """
    result: Dict[str, Dict[str, List[int]]] = {}

    for recipient, contributor_table in _PAV_TABLES.items():
        pav_planet: Dict[str, List[int]] = {}

        for contrib_name in _CONTRIBUTORS:
            bindus = [0] * 12

            # Determine contributor's natal sign
            if contrib_name == "ASC":
                contrib_sign = lagna_sign
            else:
                contrib_sign = planet_signs.get(contrib_name)
                if contrib_sign is None:
                    pav_planet[contrib_name] = bindus
                    continue

            offsets = contributor_table.get(contrib_name, [])
            for h in offsets:                              # h is 1-based house offset
                target = (contrib_sign + h - 1) % 12
                bindus[target] = 1

            pav_planet[contrib_name] = bindus

        result[recipient] = pav_planet

    return result


def kakshya_lord_of_degree(degree_in_sign: float) -> str:
    """
    Return the Kakshya lord for a given degree within a sign (0–30°).
    8 Kakshyas, each 3°45' (3.75°). Order: SAT, JUP, MAR, SUN, VEN, MER, MOO, ASC.
    """
    _KAKSHYA_LORDS = ["SATURN", "JUPITER", "MARS", "SUN", "VENUS", "MERCURY", "MOON", "ASC"]
    idx = min(int(degree_in_sign / 3.75), 7)
    return _KAKSHYA_LORDS[idx]


def get_kaksha_lord(sign: int, degree_in_sign: float) -> str:
    """
    Kaksha system: each sign is divided into 8 equal parts of 3°45'.
    Order: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna.
    Returns the kaksha lord name for a given transit degree.
    """
    kaksha_lords = ["SATURN", "JUPITER", "MARS", "SUN", "VENUS", "MERCURY", "MOON", "LAGNA"]
    kaksha_span = 30.0 / 8  # 3.75°
    kaksha_idx = int(degree_in_sign / kaksha_span)
    return kaksha_lords[min(kaksha_idx, 7)]


# ─── Domain-Specific BAV Mapping (ad.md §3.1) ────────────────────────────────
#
# For each life domain, identifies which planets' Bhinna Ashtakvarga (BAV)
# scores in which houses are most relevant for domain strength assessment.
#
# Structure: {domain: {
#     "primary":   [(planet, house), ...],  # 70% weight
#     "secondary": [(planet, house), ...],  # 30% weight
# }}
#
# Sources: BPHS Ch. 66-68 (domain-specific Ashtakvarga interpretations),
#          Phaladeepika Ch. 26, Saravali Ashtakvarga section.
DOMAIN_BAV_MAPPING: Dict[str, Dict] = {
    "CAREER": {
        "primary":   [("SUN",     10), ("SATURN",   10), ("MERCURY",  10)],
        "secondary": [("JUPITER",  9), ("MARS",      3)],
    },
    "FINANCE": {
        "primary":   [("JUPITER",  2), ("JUPITER",  11)],
        "secondary": [("VENUS",    2), ("SATURN",   11)],
    },
    "MARRIAGE": {
        "primary":   [("VENUS",    7), ("JUPITER",   7)],
        "secondary": [("MOON",     7), ("VENUS",     4)],
    },
    "HEALTH": {
        "primary":   [("SUN",      1), ("MOON",      1)],
        "secondary": [("MARS",     8), ("SATURN",    8)],
    },
    "CHILDREN": {
        "primary":   [("JUPITER",  5), ("MOON",      5)],
        "secondary": [("VENUS",    5), ("MERCURY",   5)],
    },
    "PROPERTY": {
        "primary":   [("MOON",     4), ("MARS",      4)],
        "secondary": [("VENUS",    4), ("SATURN",    4)],
    },
    "SPIRITUAL": {
        "primary":   [("JUPITER",  9), ("SATURN",   12)],
        "secondary": [("KETU",    12), ("MOON",     12)],
    },
}

# Alias for case-insensitive lookups
_DOMAIN_ALIAS = {d.lower(): d for d in DOMAIN_BAV_MAPPING}


def domain_specific_bav_score(
    domain: str,
    bhinna_av: Dict[str, List[int]],
    house_sign_map: Dict[int, int],
) -> Dict:
    """
    Compute a domain-specific Ashtakvarga quality score using the classical
    planet-house pairings for each life domain (DOMAIN_BAV_MAPPING above).

    Formula (ad.md §3.1):
        primary_avg   = mean(BAV[planet][sign] for each (planet, house) in primary)
        secondary_avg = mean(BAV[planet][sign] for each (planet, house) in secondary)
        domain_bav    = (0.70 × primary_avg + 0.30 × secondary_avg) / 8.0

    Normalised to [0, 1] where 0 = 0 bindus, 1 = 8 bindus (maximum per planet).

    Args:
        domain        : Life domain string (e.g. "career", "FINANCE")
        bhinna_av     : {planet_name: [12 BAV bindus per sign]} from compute_all_bhinna()
        house_sign_map: {house_number: sign_index (0-11)} — natal house-to-sign mapping

    Returns:
        Dict with domain_bav_score, primary_avg, secondary_avg, detail, domain
    """
    domain_key = _DOMAIN_ALIAS.get(domain.lower())
    if domain_key is None:
        return {
            "domain":           domain,
            "domain_bav_score": 0.30,  # neutral fallback
            "primary_avg":      None,
            "secondary_avg":    None,
            "detail":           [],
            "note":             f"Domain '{domain}' not in DOMAIN_BAV_MAPPING — using neutral score.",
        }

    mapping = DOMAIN_BAV_MAPPING[domain_key]
    detail = []

    def _lookup_bav(planet: str, house: int) -> Optional[float]:
        """Get BAV bindus for planet in the sign that contains the given natal house."""
        p = planet.upper()
        bav_list = bhinna_av.get(p)
        if not bav_list or len(bav_list) < 12:
            return None
        sign_idx = house_sign_map.get(house)
        if sign_idx is None:
            return None
        return float(bav_list[sign_idx])

    # ── Primary planets (70% weight) ──────────────────────────────────────────
    primary_vals = []
    for planet, house in mapping["primary"]:
        val = _lookup_bav(planet, house)
        entry = {"planet": planet, "house": house, "bav_bindus": val, "tier": "primary"}
        detail.append(entry)
        if val is not None:
            primary_vals.append(val)

    # ── Secondary planets (30% weight) ────────────────────────────────────────
    secondary_vals = []
    for planet, house in mapping["secondary"]:
        val = _lookup_bav(planet, house)
        entry = {"planet": planet, "house": house, "bav_bindus": val, "tier": "secondary"}
        detail.append(entry)
        if val is not None:
            secondary_vals.append(val)

    primary_avg   = sum(primary_vals)   / len(primary_vals)   if primary_vals   else 4.0
    secondary_avg = sum(secondary_vals) / len(secondary_vals) if secondary_vals else 4.0

    # Weighted composite; divide by 8.0 to normalise to [0,1]
    composite = (0.70 * primary_avg + 0.30 * secondary_avg) / 8.0
    composite  = max(0.0, min(1.0, round(composite, 3)))

    return {
        "domain":           domain_key,
        "domain_bav_score": composite,
        "primary_avg":      round(primary_avg, 2),
        "secondary_avg":    round(secondary_avg, 2),
        "detail":           detail,
        "note": (
            f"Domain BAV for {domain_key}: primary={primary_avg:.2f}/8, "
            f"secondary={secondary_avg:.2f}/8 → score={composite:.3f}"
        ),
    }