"""Regression tests for Sanghatta Chakra transit integration and scoring hooks."""

from vedic_engine.analysis.sanghatta_chakra import (
    compute_sanghatta_chakra,
    evaluate_sanghatta_transit,
)
from vedic_engine.prediction.transits import evaluate_all_transits


def test_compute_sanghatta_chakra_accepts_integer_input() -> None:
    out = compute_sanghatta_chakra(0, include_abhijit=True)  # 0-based Ashwini
    assert out["janma_nakshatra"] == "Ashwini"
    assert out["sanghatika"]["offset"] == 16
    assert out["sanghatika"]["nakshatra"] == "Vishakha"


def test_evaluate_sanghatta_transit_malefic_hit_is_adverse() -> None:
    chakra = compute_sanghatta_chakra("Ashwini", include_abhijit=True)
    out = evaluate_sanghatta_transit(
        transit_planet="SATURN",
        transit_nakshatra="Vishakha",
        sanghatta_chakra=chakra,
    )

    assert out["is_hit"] is True
    assert out["classification"] == "malefic"
    assert out["impact_score"] < 0.0


def test_evaluate_all_transits_attaches_sanghatta_payload() -> None:
    chakra = compute_sanghatta_chakra("Ashwini", include_abhijit=True)

    transits = {
        "SUN": 205.0,       # Vishakha -> Sanghatika hit for Ashwini base
        "MOON": 40.0,
        "MARS": 80.0,
        "MERCURY": 120.0,
        "JUPITER": 150.0,
        "VENUS": 200.0,
        "SATURN": 250.0,
        "RAHU": 300.0,
        "KETU": 120.0,
    }
    out = evaluate_all_transits(
        transit_positions=transits,
        natal_moon_sign=0,
        sanghatta_chakra=chakra,
        retrograde_planets=["RAHU", "KETU"],
    )

    assert "sanghatta" in out["SUN"]
    assert out["SUN"]["sanghatta"]["is_hit"] is True
    assert "impact_score" in out["SUN"]["sanghatta"]


if __name__ == "__main__":
    test_compute_sanghatta_chakra_accepts_integer_input()
    test_evaluate_sanghatta_transit_malefic_hit_is_adverse()
    test_evaluate_all_transits_attaches_sanghatta_payload()
    print("test_sanghatta_integration: PASS")
