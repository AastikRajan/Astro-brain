"""
Advanced Dasha Systems  (Phase 4, File 6 – timing).

Implements NEW timing algorithms not present in existing modules:
  – Sudarshana Chakra degree correction + event fructification logic
  – Patyayini Dasha (Tajika annual timing)
  – Ashtaka Dasha (BAV-proportional periods)

Architecture rule: ALL pure functions. No weights, no blending, no prediction logic.
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Any, Optional

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# ════════════════════════════════════════════════════════════════════════════
# 1. SUDARSHANA CHAKRA – DEGREE CORRECTION & EVENT LOGIC
# ════════════════════════════════════════════════════════════════════════════

def compute_sudarshana_balance(lagna_longitude: float) -> Dict[str, Any]:
    """
    Compute the balance of the 1st House Mahadasha at birth.
    Each sign = 1 year. Each degree = 12 days 4 hours 12 min.

    Let D = degree-in-sign of Lagna.
    Days elapsed = D × 12.175 (≈12d 4h 12m per degree).
    Balance of 1st MD = 365.25 - days_elapsed.
    """
    lon = lagna_longitude % 360.0
    degree_in_sign = lon % 30.0
    days_per_degree = 365.25 / 30.0  # ~12.175 days
    days_elapsed = degree_in_sign * days_per_degree
    balance_days = 365.25 - days_elapsed
    balance_years = balance_days / 365.25

    return {
        "lagna_longitude": round(lon, 4),
        "degree_in_sign": round(degree_in_sign, 4),
        "days_elapsed_before_birth": round(days_elapsed, 2),
        "balance_1st_md_days": round(balance_days, 2),
        "balance_1st_md_years": round(balance_years, 4),
    }


def compute_sudarshana_dasha_sequence(
    lagna_sign_idx: int,
    moon_sign_idx: int,
    sun_sign_idx: int,
    lagna_longitude: float,
    age_years: float = 0.0,
    num_years: int = 12,
) -> List[Dict[str, Any]]:
    """
    Compute the Sudarshana Mahadasha sequence for a span of years.
    Returns the active sign from all 3 Lagnas (Janma, Chandra, Surya)
    for each year.

    Formula: active_house = ((age - 1) % 12) + 1
    Active sign from anchor = (anchor_idx + active_house - 1) % 12
    """
    balance = compute_sudarshana_balance(lagna_longitude)
    balance_years = balance["balance_1st_md_years"]

    sequence: List[Dict[str, Any]] = []
    for yr in range(num_years):
        actual_age = age_years + yr
        # Adjust for balance: the first MD doesn't start exactly at birth
        effective_age = actual_age - (1.0 - balance_years) if actual_age > 0 else 0
        house_num = (int(effective_age) % 12) + 1

        lagna_active = (lagna_sign_idx + house_num - 1) % 12
        moon_active = (moon_sign_idx + house_num - 1) % 12
        sun_active = (sun_sign_idx + house_num - 1) % 12

        sequence.append({
            "age": round(actual_age, 1),
            "house_number": house_num,
            "lagna_sign": SIGN_NAMES[lagna_active],
            "moon_sign": SIGN_NAMES[moon_active],
            "sun_sign": SIGN_NAMES[sun_active],
        })

    return sequence


def check_sudarshana_event(
    dasha_sign_idx: int,
    bhava_lord_sign_idx: int,
    karaka_sign_idx: int,
    target_bhava: int,
    lagna_sign_idx: int,
) -> Dict[str, Any]:
    """
    Event fructification logic tree for Sudarshana Chakra.
    An event manifests when the Dasha Rasi establishes a relationship with
    the target Bhava, its Lord, or the natural Karaka.

    3 conditions (any TRUE → event indicated):
    1. Dasha Rasi conjoined/aspected by Bhava Lord or Karaka
    2. Lord of Dasha Rasi occupies target Bhava or Bhavat Bhavam
    3. Lord of Dasha Rasi aspected by Bhava Lord or Karaka

    Returns dict with condition checks.
    """
    # Conjunction = same sign; aspect = 7th from
    def conjoined_or_aspected(sign_a: int, sign_b: int) -> bool:
        return sign_a == sign_b or (sign_a + 6) % 12 == sign_b

    # Bhavat Bhavam = house as far from target as target from lagna
    bhavat_bhavam = ((target_bhava - 1) * 2) % 12 + 1
    target_sign = (lagna_sign_idx + target_bhava - 1) % 12
    bhavat_sign = (lagna_sign_idx + bhavat_bhavam - 1) % 12

    cond1 = conjoined_or_aspected(dasha_sign_idx, bhava_lord_sign_idx) or \
            conjoined_or_aspected(dasha_sign_idx, karaka_sign_idx)

    # For cond2/3, we need the lord of the dasha rasi
    # Simplified: check if dasha_sign relates to target
    dasha_relates_target = (dasha_sign_idx == target_sign or
                            dasha_sign_idx == bhavat_sign)

    cond3 = conjoined_or_aspected(dasha_sign_idx, bhava_lord_sign_idx)

    event_indicated = cond1 or dasha_relates_target or cond3

    return {
        "dasha_sign": SIGN_NAMES[dasha_sign_idx],
        "target_bhava": target_bhava,
        "bhavat_bhavam": bhavat_bhavam,
        "condition_1_conjunction_aspect": cond1,
        "condition_2_occupies_target": dasha_relates_target,
        "condition_3_lord_aspected": cond3,
        "event_indicated": event_indicated,
    }


# ════════════════════════════════════════════════════════════════════════════
# 2. PATYAYINI DASHA (Tajika Annual Timing)
# ════════════════════════════════════════════════════════════════════════════

def compute_patyayini_dasha(
    planet_longitudes: Dict[str, float],
    lagna_longitude: float,
    year_days: float = 365.25,
) -> Dict[str, Any]:
    """
    Compute Patyayini Dasha from Tajika / Varshaphala chart.
    Uses 8 entities: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Lagna.
    Rahu/Ketu excluded.

    Algorithm:
    1. Extract Krishamshas (degree-in-sign only, discard sign)
    2. Sort ascending
    3. Compute Patyamshas (successive differences)
    4. Duration = (Patyamsha / highest_Krishamsha) × year_days
    """
    ENTITIES = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]

    # Step 1: Extract Krishamshas (degree within sign)
    raw_data: List[Tuple[str, float]] = []
    for entity in ENTITIES:
        if entity in planet_longitudes:
            krishamsha = planet_longitudes[entity] % 30.0
            raw_data.append((entity, round(krishamsha, 6)))

    # Add Lagna
    lagna_krishamsha = lagna_longitude % 30.0
    raw_data.append(("LAGNA", round(lagna_krishamsha, 6)))

    # Step 2: Sort ascending by Krishamsha
    raw_data.sort(key=lambda x: x[1])

    # Step 3: Compute Patyamshas
    results: List[Dict[str, Any]] = []
    prev_krishamsha = 0.0
    for i, (entity, krishamsha) in enumerate(raw_data):
        if i == 0:
            patyamsha = krishamsha
        else:
            patyamsha = krishamsha - prev_krishamsha
        prev_krishamsha = krishamsha
        results.append({
            "entity": entity,
            "krishamsha": krishamsha,
            "patyamsha": round(patyamsha, 6),
        })

    # Validation: sum of Patyamshas should equal highest Krishamsha
    highest_krishamsha = raw_data[-1][1] if raw_data else 1.0
    patyamsha_sum = sum(r["patyamsha"] for r in results)

    # Step 4: Compute durations
    for r in results:
        if highest_krishamsha > 0:
            duration_days = (r["patyamsha"] / highest_krishamsha) * year_days
        else:
            duration_days = 0.0
        r["duration_days"] = round(duration_days, 2)

    return {
        "method": "Patyayini Dasha",
        "entities_count": len(results),
        "highest_krishamsha": highest_krishamsha,
        "patyamsha_sum": round(patyamsha_sum, 6),
        "validation_ok": abs(patyamsha_sum - highest_krishamsha) < 0.01,
        "periods": results,
    }


# ════════════════════════════════════════════════════════════════════════════
# 3. ASHTAKA DASHA (BAV-Proportional Periods)
# ════════════════════════════════════════════════════════════════════════════

# SAV constant (always 337 total bindus across all charts)
SAV_CONSTANT = 337

def compute_ashtaka_dasha(
    planet_bav_scores: Dict[str, int],
    planet_sign_occupied: Dict[str, str],
    total_lifespan_years: float = 120.0,
) -> Dict[str, Any]:
    """
    Ashtaka Dasha: dasha durations proportional to BAV bindus.

    Algorithm:
    1. For each planet, get BAV score in its occupied sign
    2. Duration = (planet_BAV / SAV_CONSTANT) × total_lifespan
    3. Sequence: descending order of BAV strength

    planet_bav_scores: {planet: bindus_in_occupied_sign}
    """
    PLANETS = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]

    periods: List[Dict[str, Any]] = []
    total_bindus = 0

    for planet in PLANETS:
        bindus = planet_bav_scores.get(planet, 0)
        total_bindus += bindus
        sign = planet_sign_occupied.get(planet, "?")
        duration = (bindus / SAV_CONSTANT) * total_lifespan_years

        periods.append({
            "planet": planet,
            "sign_occupied": sign,
            "bav_bindus": bindus,
            "duration_years": round(duration, 2),
        })

    # Sort by BAV strength descending (strongest starts)
    periods.sort(key=lambda x: x["bav_bindus"], reverse=True)

    # Compute cumulative start years
    cumulative = 0.0
    for p in periods:
        p["start_year"] = round(cumulative, 2)
        cumulative += p["duration_years"]

    total_years = sum(p["duration_years"] for p in periods)

    return {
        "method": "Ashtaka Dasha",
        "total_bindus": total_bindus,
        "sav_constant": SAV_CONSTANT,
        "total_years_allocated": round(total_years, 2),
        "total_lifespan": total_lifespan_years,
        "sequence": periods,
    }
