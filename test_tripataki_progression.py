"""Milestone-C tests for Tripataki progression core."""

from vedic_engine.timing.varshaphala import compute_tripataki_progression


def test_tripataki_modulo_wrapping_case_age_45() -> None:
    # running_year = 46
    # Moon index = 46 % 9 = 1
    # Mars index = 46 % 6 = 4
    natal = {"MOON": 0, "MARS": 0}
    out = compute_tripataki_progression(natal_planet_signs=natal, completed_years=45, annual_lagna_sign=0)
    moon = out["progressions"]["MOON"]
    mars = out["progressions"]["MARS"]
    assert moon["index_step"] == 1
    assert mars["index_step"] == 4
    assert moon["progressed_sign"] == 1
    assert mars["progressed_sign"] == 4


def test_tripataki_nodes_reverse_case_age_33() -> None:
    # running_year = 34
    # Rahu/Ketu index = 34 % 6 = 4, reverse from natal sign.
    natal = {"RAHU": 10, "KETU": 4}
    out = compute_tripataki_progression(natal_planet_signs=natal, completed_years=33, annual_lagna_sign=0)
    rahu = out["progressions"]["RAHU"]
    ketu = out["progressions"]["KETU"]
    assert rahu["index_step"] == 4
    assert ketu["index_step"] == 4
    assert rahu["direction"] == "reverse"
    assert ketu["direction"] == "reverse"
    assert rahu["progressed_sign"] == 6
    assert ketu["progressed_sign"] == 0


def test_tripataki_reports_geometry_and_moon_vedha_payload() -> None:
    out = compute_tripataki_progression(
        natal_planet_signs={"MOON": 3, "SUN": 4, "RAHU": 9},
        completed_years=20,
        annual_lagna_sign=5,
    )
    assert out["vedha_geometry_available"] is True
    assert out["status"] == "vedha_scored"
    assert out.get("source_gap") is None

    sign_map = out.get("sign_map", [])
    assert isinstance(sign_map, list) and len(sign_map) == 12
    anchor_rows = [row for row in sign_map if row.get("point") == [3, 5]]
    assert anchor_rows and anchor_rows[0].get("sign_idx") == 5

    moon_vedha = out.get("moon_vedha", {})
    assert moon_vedha.get("status") in {"evaluated", "moon_progression_unavailable", "moon_point_unmapped"}
    assert isinstance(moon_vedha.get("vedha_signs", []), list)
    assert isinstance(moon_vedha.get("hit_planets", []), list)


if __name__ == "__main__":
    test_tripataki_modulo_wrapping_case_age_45()
    test_tripataki_nodes_reverse_case_age_33()
    test_tripataki_reports_geometry_and_moon_vedha_payload()
    print("test_tripataki_progression: PASS")
