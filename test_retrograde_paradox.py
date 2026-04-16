"""Regression tests for retrograde paradox handling in confidence scoring."""

from vedic_engine.prediction.confidence import compute_confidence


def _base_kwargs() -> dict:
    return {
        "dasha_planet": "SATURN",
        "antardasha_planet": "MERCURY",
        "domain": "career",
        "planet_domain_map": {
            "SATURN": ["career"],
            "MERCURY": ["career"],
        },
        "shadbala_ratios": {
            "SATURN": 1.2,
            "MERCURY": 1.1,
        },
        "transit_scores": {
            "SATURN": {"net_score": 0.70},
            "MERCURY": {"net_score": 0.60},
        },
        "domain_planets": ["SATURN", "MERCURY"],
        "sarva_av": [30] * 12,
        "relevant_signs": [0, 5, 8],
        "active_yogas": [],
        "kp_significations": {
            "SATURN": [10],
            "MERCURY": [10],
        },
        "domain_houses": [10],
        "dasha_planet_bav": [5] * 12,
        "functional_analysis": {},
        "house_lords": {
            1: "MARS",
            7: "VENUS",
            10: "SATURN",
        },
        "vargas": {
            "SATURN": {9: 6, 10: 9},
            "MERCURY": {9: 2, 10: 5},
            "VENUS": {9: 1},
            "JUPITER": {9: 3},
        },
        "planet_houses": {
            "SATURN": 10,
            "MERCURY": 10,
            "VENUS": 7,
            "JUPITER": 9,
        },
        "negator_houses": [1, 5, 9],
        "promise_result": {
            "denied": False,
            "suppressed": False,
            "promise_pct": 90,
            "promise_level": "STRONG",
        },
        "dasha_house": 10,
        "antardasha_house": 10,
        "dasha_lord_combust": False,
        "dasha_lord_retrograde": True,
        "pratyantar_planet": None,
        "age_years": 35,
        "planet_lons": {
            "SATURN": 250.0,
            "MERCURY": 170.0,
            "VENUS": 60.0,
            "JUPITER": 95.0,
        },
        "dasha_lord_gochar_mult": 1.0,
    }


def _dasha_alignment_for_saturn_sign(sign_idx: int) -> float:
    kwargs = _base_kwargs()
    kwargs["planet_lons"]["SATURN"] = sign_idx * 30.0 + 10.0
    out = compute_confidence(**kwargs)
    return float(out["components"]["dasha_alignment"])


def test_retrograde_exalted_vs_debilitated_inversion() -> None:
    # Saturn exaltation sign: Libra (6). Debilitation sign: Aries (0).
    # Expected order with retrograde paradox handling:
    # retro+debilitated > retro+neutral > retro+exalted
    dasha_exalted = _dasha_alignment_for_saturn_sign(6)
    dasha_neutral = _dasha_alignment_for_saturn_sign(8)
    dasha_debil = _dasha_alignment_for_saturn_sign(0)

    assert dasha_debil > dasha_neutral
    assert dasha_neutral > dasha_exalted


if __name__ == "__main__":
    test_retrograde_exalted_vs_debilitated_inversion()
    print("test_retrograde_paradox: PASS")
