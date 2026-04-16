"""Tests for dedicated Moorti Nirnaya/Paya helpers."""

from vedic_engine.timing.moorti_nirnaya import compute_moorti_from_signs, compute_paya


def test_compute_paya_gold_house() -> None:
    out = compute_paya(1)
    assert out["house_from_moon"] == 1
    assert out["metal"] == "Gold"
    assert out["moorti"] == "Gold"
    assert out["moorti_multiplier"] == 1.0


def test_compute_paya_iron_house() -> None:
    out = compute_paya(8)
    assert out["house_from_moon"] == 8
    assert out["metal"] == "Iron"
    assert out["moorti_multiplier"] == 0.25


def test_compute_moorti_from_signs_maps_house_correctly() -> None:
    # Transit sign 2 (Gemini) from natal Moon sign 0 (Aries) => 3rd from Moon.
    out = compute_moorti_from_signs(2, 0)
    assert out["house_from_moon"] == 3
    assert out["metal"] == "Copper"
    assert out["moorti_multiplier"] == 0.5


if __name__ == "__main__":
    test_compute_paya_gold_house()
    test_compute_paya_iron_house()
    test_compute_moorti_from_signs_maps_house_correctly()
    print("test_moorti_nirnaya: PASS")
