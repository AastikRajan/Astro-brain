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
    5. Pinda Sadhana per planet
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

    return {
        "bhinna": bhinna,
        "sarva": sarva,
        "sarva_total": sum(sarva),
        "checksums": checks,
        "shodhana": shodhana_results,
        "pinda": pinda_results,
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
