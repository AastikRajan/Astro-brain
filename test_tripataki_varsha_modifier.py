"""Regression tests for Tripataki annual confidence delta mapping."""

from vedic_engine.prediction.engine import PredictionEngine


def test_tripataki_modifier_progression_only_no_delta() -> None:
    out = PredictionEngine._compute_tripataki_varsha_delta(
        {
            "status": "progression_only",
            "vedha_geometry_available": False,
            "source_gap": "tripataki_vedha_line_map_not_defined_in_runtime_sources",
        }
    )
    assert out["status"] == "progression_only"
    assert out["delta"] == 0.0
    assert isinstance(out.get("source_gap"), str)


def test_tripataki_modifier_applies_negative_delta() -> None:
    out = PredictionEngine._compute_tripataki_varsha_delta(
        {
            "vedha_geometry_available": True,
            "moon_vedha": {
                "weighted_score": -3.0,
                "hit_planets": [{"planet": "SATURN"}, {"planet": "RAHU"}],
            },
        }
    )
    assert out["status"] == "applied"
    assert out["delta"] == -0.06
    assert out["weighted_score"] == -3.0
    assert out["hit_count"] == 2


def test_tripataki_modifier_clamps_positive_delta() -> None:
    out = PredictionEngine._compute_tripataki_varsha_delta(
        {
            "vedha_geometry_available": True,
            "moon_vedha": {
                "weighted_score": 12.0,
                "hit_planets": [{"planet": "JUPITER"}],
            },
        }
    )
    assert out["status"] == "applied"
    assert out["delta"] == 0.08
    assert out["weighted_score"] == 12.0


if __name__ == "__main__":
    test_tripataki_modifier_progression_only_no_delta()
    test_tripataki_modifier_applies_negative_delta()
    test_tripataki_modifier_clamps_positive_delta()
    print("test_tripataki_varsha_modifier: PASS")
