"""Milestone-B tests for native Harsha Bala rules."""

from vedic_engine.timing.varshaphala import compute_harsha_bala, compute_all_harsha_bala


def _lon(sign_idx: int, deg: float = 0.0) -> float:
    return float(sign_idx * 30.0 + deg)


def test_sun_sthana_conflict_max_15_classical() -> None:
    # Lagna Leo (4), Sun in Aries (0) => house 9 (Sun's sthana), exalted, day chart.
    # With classical house-gender mapping, house 9 is feminine, so Stri-Purusha fails.
    out = compute_harsha_bala("SUN", _lon(0, 10.0), lagna_sign=4, is_day_chart=True)
    assert out["score"] == 15
    assert out["components"]["sthana"] is True
    assert out["components"]["own_exalt_moola"] is True
    assert out["components"]["dina_ratri"] is True
    assert out["components"]["stri_purusha"] is False


def test_mars_true_max_20_case() -> None:
    # Lagna Leo (4), Mars in Capricorn (9) => house 6 (Mars's sthana), exalted, day chart.
    out = compute_harsha_bala("MARS", _lon(9, 28.0), lagna_sign=4, is_day_chart=True)
    assert out["score"] == 20
    assert all(bool(v) for v in out["components"].values())


def test_moon_true_max_20_night_case() -> None:
    # Lagna Pisces (11), Moon in Taurus (1) => house 3 (Moon's sthana), exalted, night chart.
    out = compute_harsha_bala("MOON", _lon(1, 3.0), lagna_sign=11, is_day_chart=False)
    assert out["score"] == 20
    assert all(bool(v) for v in out["components"].values())


def test_compute_all_harsha_bala_shape() -> None:
    lons = {
        "SUN": _lon(0, 10.0),
        "MOON": _lon(1, 3.0),
        "MARS": _lon(9, 28.0),
        "MERCURY": _lon(4, 15.0),
        "JUPITER": _lon(3, 5.0),
        "VENUS": _lon(11, 27.0),
        "SATURN": _lon(6, 20.0),
    }
    out = compute_all_harsha_bala(lons, lagna_sign=4, is_day_chart=True)
    assert "by_planet" in out and isinstance(out["by_planet"], dict)
    assert "avg_score" in out
    assert "SUN" in out["by_planet"]


if __name__ == "__main__":
    test_sun_sthana_conflict_max_15_classical()
    test_mars_true_max_20_case()
    test_moon_true_max_20_night_case()
    test_compute_all_harsha_bala_shape()
    print("test_varshaphala_harsha: PASS")
