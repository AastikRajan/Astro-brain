"""Regression tests for dedicated Chandravali helpers."""

from vedic_engine.prediction.transits import evaluate_all_transits
from vedic_engine.timing.chandravali import compute_chandravali


def test_chandravali_transit_profile_matches_existing_behavior() -> None:
    out_good = compute_chandravali(natal_moon_sign=0, transit_moon_sign=0, profile="transit")
    assert out_good["house_from_natal_moon"] == 1
    assert out_good["is_good"] is True
    assert out_good["score"] == 0.75

    out_bad = compute_chandravali(natal_moon_sign=0, transit_moon_sign=1, profile="transit")
    assert out_bad["house_from_natal_moon"] == 2
    assert out_bad["is_good"] is False
    assert out_bad["score"] == 0.25

    # 11th from natal Moon remains favorable in transit profile.
    out_11 = compute_chandravali(natal_moon_sign=0, transit_moon_sign=10, profile="transit")
    assert out_11["house_from_natal_moon"] == 11
    assert out_11["is_good"] is True


def test_chandravali_muhurta_profile_matches_pyjhora_house_set() -> None:
    # 10th is good in pyjhora chandrabalam list.
    out_10 = compute_chandravali(natal_moon_sign=0, transit_moon_sign=9, profile="muhurta")
    assert out_10["house_from_natal_moon"] == 10
    assert out_10["is_good"] is True
    assert out_10["score"] == 1.0

    # 11th is not included in pyjhora's cb_good list.
    out_11 = compute_chandravali(natal_moon_sign=0, transit_moon_sign=10, profile="muhurta")
    assert out_11["house_from_natal_moon"] == 11
    assert out_11["is_good"] is False
    assert out_11["score"] == 0.0


def test_evaluate_all_transits_attaches_chandravali_payload() -> None:
    out = evaluate_all_transits({"MOON": 0.0}, natal_moon_sign=0)
    moon = out["MOON"]

    assert "chandrabala" in moon
    assert moon["chandrabala"]["profile"] == "transit"
    assert moon["chandrabala"]["house_from_natal_moon"] == 1
    assert moon["chandrabala"]["score"] == 0.75


if __name__ == "__main__":
    test_chandravali_transit_profile_matches_existing_behavior()
    test_chandravali_muhurta_profile_matches_pyjhora_house_set()
    test_evaluate_all_transits_attaches_chandravali_payload()
    print("test_chandravali: PASS")
