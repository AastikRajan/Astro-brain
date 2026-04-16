"""Regression tests for classical dasha-pravesha lagna relation mapping."""

from vedic_engine.prediction.engine import PredictionEngine


def test_pravesha_lagna_trine_support_multiplier() -> None:
    # Natal lagna Aries(0), Pravesha lagna Leo(4) -> 5th house from natal.
    out = PredictionEngine._pravesha_lagna_relation(4, 0)
    assert out["house_from_natal_lagna"] == 5
    assert out["relation"] == "trine_support"
    assert out["multiplier"] == 1.30


def test_pravesha_lagna_dusthana_friction_multiplier() -> None:
    # Natal lagna Aries(0), Pravesha lagna Virgo(5) -> 6th house from natal.
    out = PredictionEngine._pravesha_lagna_relation(5, 0)
    assert out["house_from_natal_lagna"] == 6
    assert out["relation"] == "dusthana_friction"
    assert out["multiplier"] == 0.70


if __name__ == "__main__":
    test_pravesha_lagna_trine_support_multiplier()
    test_pravesha_lagna_dusthana_friction_multiplier()
    print("test_dasha_pravesha_relation: PASS")
