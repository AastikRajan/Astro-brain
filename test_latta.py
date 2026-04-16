"""Regression tests for native Latta (planetary kick) helpers."""

from vedic_engine.prediction.transits import evaluate_all_transits
from vedic_engine.timing.latta import (
    compute_latta_from_nakshatra_map,
    compute_latta_from_longitudes,
    compute_latta_star,
)


def test_compute_latta_star_reference_cases() -> None:
    # Reference cases from pyjhora pvr_tests.lattha_test expected stars.
    expected = {
        "SUN": (18, 1),
        "MOON": (15, 22),
        "MARS": (11, 13),
        "MERCURY": (19, 13),
        "JUPITER": (20, 25),
        "VENUS": (16, 12),
        "SATURN": (26, 5),
        "RAHU": (13, 5),
        "KETU": (26, 18),
    }
    for planet, (source_star, latta_star) in expected.items():
        out = compute_latta_star(planet, source_star, include_abhijit=True)
        assert out["source_star"] == source_star
        assert out["latta_star"] == latta_star


def test_compute_latta_from_nakshatra_map_order_and_names() -> None:
    out = compute_latta_from_nakshatra_map({"MOON": 15, "SUN": 18}, include_abhijit=True)
    assert list(out.keys()) == ["SUN", "MOON"]
    assert out["SUN"]["latta_star_name"] == "Ashwini"
    assert out["MOON"]["latta_star_name"] == "Abhijit"


def test_compute_latta_from_longitudes_basic() -> None:
    out = compute_latta_from_longitudes({"SUN": 0.0, "MOON": 0.0}, include_abhijit=True)
    assert out["SUN"]["source_star"] == 1
    assert out["SUN"]["latta_star"] == 12
    assert out["MOON"]["latta_star"] == 8


def test_evaluate_all_transits_attaches_latta_payload() -> None:
    transits = {
        "SUN": 10.0,
        "MOON": 40.0,
        "MARS": 80.0,
        "MERCURY": 120.0,
        "JUPITER": 150.0,
        "VENUS": 200.0,
        "SATURN": 250.0,
        "RAHU": 300.0,
        "KETU": 120.0,
    }
    out = evaluate_all_transits(transits, natal_moon_sign=0)
    assert "latta" in out["SATURN"]
    assert out["SATURN"]["latta"]["planet"] == "SATURN"


if __name__ == "__main__":
    test_compute_latta_star_reference_cases()
    test_compute_latta_from_nakshatra_map_order_and_names()
    test_compute_latta_from_longitudes_basic()
    test_evaluate_all_transits_attaches_latta_payload()
    print("test_latta: PASS")
