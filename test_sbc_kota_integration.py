"""Regression tests for Sarvatobhadra/Kota transit integration and input normalization."""

from vedic_engine.analysis.kota_chakra import compute_kota_chakra
from vedic_engine.analysis.sarvatobhadra import construct_sbc_grid
from vedic_engine.prediction.transits import evaluate_all_transits


def test_construct_sbc_grid_accepts_integer_nak_and_filters_invalid_cells() -> None:
    grid = construct_sbc_grid(
        natal_nakshatra=0,  # 0-based Ashwini
        natal_sign=0,
        birth_tithi=1,
        birth_weekday=0,
    )
    assert grid["natal_nakshatra"] == "Ashwini"
    assert all((isinstance(c, tuple) and None not in c) for c in grid["sensitive_cells"])


def test_compute_kota_chakra_accepts_integer_nak() -> None:
    out = compute_kota_chakra(0)  # 0-based Ashwini
    assert out["janma_nakshatra"] == "Ashwini"
    assert "Ashwini" in out["nak_zone"]
    assert out["nak_zone"]["Ashwini"] in {"stambha", "durgantara", "prakaara", "bahya"}


def test_evaluate_all_transits_attaches_sbc_and_kota_payloads() -> None:
    sbc_grid = construct_sbc_grid(
        natal_nakshatra="Ashwini",
        natal_sign=0,
        birth_tithi=1,
        birth_weekday=0,
    )
    kota = compute_kota_chakra("Ashwini")

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
    out = evaluate_all_transits(
        transit_positions=transits,
        natal_moon_sign=0,
        sbc_grid=sbc_grid,
        kota_chakra=kota,
        retrograde_planets=["RAHU", "KETU"],
    )

    assert "sbc_vedha" in out["SUN"]
    assert "kota" in out["SUN"]
    assert "severity" in out["SUN"]["sbc_vedha"]
    assert "severity" in out["SUN"]["kota"]


if __name__ == "__main__":
    test_construct_sbc_grid_accepts_integer_nak_and_filters_invalid_cells()
    test_compute_kota_chakra_accepts_integer_nak()
    test_evaluate_all_transits_attaches_sbc_and_kota_payloads()
    print("test_sbc_kota_integration: PASS")
