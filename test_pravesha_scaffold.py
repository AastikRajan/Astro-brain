"""Milestone-D tests for pravesha scaffold compatibility and diagnostics."""

from vedic_engine.timing.tithi_pravesh import compute_tithi_pravesh


def test_tithi_pravesh_backward_compatible_aliases() -> None:
    out = compute_tithi_pravesh(
        natal_moon_lon=120.0,
        natal_sun_lon=90.0,
        natal_lagna_sign=2,
        query_year=2026,
        birth_weekday=3,
        lagna_sign=5,
    )
    assert out["year"] == 2026
    assert out["year_lord_weekday"] == 3
    assert out["pravesh_lagna_sign"] == 5
    assert out["calendar_basis"] == "sidereal_month"
    assert out["source_scope"] == "diagnostic_without_iterative_solver"


def test_tithi_pravesh_calendar_basis_toggle() -> None:
    out = compute_tithi_pravesh(
        natal_moon_lon=200.0,
        natal_sun_lon=170.0,
        natal_lagna_sign=8,
        year=2027,
        use_tropical_month=True,
    )
    assert out["year"] == 2027
    assert out["calendar_basis"] == "tropical_month"


if __name__ == "__main__":
    test_tithi_pravesh_backward_compatible_aliases()
    test_tithi_pravesh_calendar_basis_toggle()
    print("test_pravesha_scaffold: PASS")
