"""Regression test for Swabhukti (MD=AD) preparatory damping in confidence scoring."""

from vedic_engine.prediction.confidence import compute_confidence


def _base_kwargs() -> dict:
    return {
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
        "dasha_lord_retrograde": False,
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


def test_swabhukti_dasha_alignment_is_preparatory() -> None:
    base = _base_kwargs()

    out_normal = compute_confidence(
        dasha_planet="SATURN",
        antardasha_planet="MERCURY",
        **base,
    )
    out_swabhukti = compute_confidence(
        dasha_planet="SATURN",
        antardasha_planet="SATURN",
        **base,
    )

    assert out_swabhukti["components"]["dasha_alignment"] < out_normal["components"]["dasha_alignment"]
    assert "swabhukti_preparatory_delay" in out_swabhukti["md_ad_geometry"]


if __name__ == "__main__":
    test_swabhukti_dasha_alignment_is_preparatory()
    print("test_swabhukti_dasha_alignment_is_preparatory: PASS")
