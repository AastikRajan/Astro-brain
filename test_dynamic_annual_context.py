"""Regression tests for dynamic annual context wiring in PredictionEngine."""

from datetime import datetime
from types import SimpleNamespace

import vedic_engine.prediction.engine as engine_mod


def _fake_chart():
    return SimpleNamespace(
        lagna_sign=2,
        birth_info=SimpleNamespace(
            date="1990-08-15",
            time="10:30:00",
            latitude=12.97,
            longitude=77.59,
            timezone=5.5,
        ),
    )


def test_dynamic_annual_context_uses_active_solar_year() -> None:
    engine = engine_mod.PredictionEngine()
    static = {
        "meta": {
            "lagna_sign": 2,
            "moon_lon": 120.0,
            "sun_lon": 90.0,
        }
    }
    chart = _fake_chart()
    calls = []
    seen_birth_weekdays = []

    original_flag = engine_mod._SWE_SOLAR_RETURN_AVAILABLE
    original_compute_solar_return = getattr(engine_mod, "compute_solar_return", None)
    original_compute_varsha_analysis = engine_mod.compute_varsha_analysis
    original_compute_tithi_pravesh = engine_mod.compute_tithi_pravesh

    def fake_compute_solar_return(*, birth_dt, year, latitude, longitude, tz_offset, ayanamsa):
        calls.append(year)
        local_dt = datetime(year, 8, 16, 12, 0, 0)
        return {
            "solar_return_local": local_dt.isoformat(),
            "solar_return_utc": local_dt.isoformat(),
            "chart": {
                "lagna": {"degree": 75.0},
                "planets": {
                    "SUN": {"longitude": 90.0, "speed": 1.0},
                    "MOON": {"longitude": 120.0, "speed": 13.0},
                    "MARS": {"longitude": 150.0, "speed": 0.5},
                },
            },
        }

    def fake_compute_varsha_analysis(**kwargs):
        return {
            "lagna_sign": 2,
            "muntha": {"house": 10},
            "varsha_pati": {"varsha_pati": "SUN", "pvb": 12.0},
            "tajika_yogas": [],
            "mudda_dasha": {"current": {"lord": "SUN"}},
            "harsha_bala": {"by_planet": {}},
            "tripataki": {},
            "echo_completed_years": kwargs["completed_years"],
        }

    def fake_compute_tithi_pravesh(**kwargs):
        seen_birth_weekdays.append(kwargs.get("birth_weekday"))
        return {
            "year": kwargs.get("year", kwargs.get("query_year")),
            "calendar_basis": "sidereal_month",
            "echo_birth_weekday": kwargs.get("birth_weekday"),
        }

    try:
        engine_mod._SWE_SOLAR_RETURN_AVAILABLE = True
        engine_mod.compute_solar_return = fake_compute_solar_return
        engine_mod.compute_varsha_analysis = fake_compute_varsha_analysis
        engine_mod.compute_tithi_pravesh = fake_compute_tithi_pravesh

        out = engine._build_dynamic_annual_context(
            chart=chart,
            static=static,
            birth_dt=datetime(1990, 8, 15, 10, 30, 0),
            on_date=datetime(2026, 1, 10, 9, 0, 0),
        )

        assert out["active_year"] == 2025
        assert out["varshaphala"]["annual_context_year"] == 2025
        assert out["varshaphala"]["analysis_basis"] == "active_solar_return_chart"
        assert out["varshaphala"]["echo_completed_years"] == 35
        assert out["tithi_pravesh"]["year"] == 2025
        assert out["tithi_pravesh"]["echo_birth_weekday"] == 3
        assert calls == [2026, 2025]
        assert seen_birth_weekdays == [3]
    finally:
        engine_mod._SWE_SOLAR_RETURN_AVAILABLE = original_flag
        if original_compute_solar_return is not None:
            engine_mod.compute_solar_return = original_compute_solar_return
        engine_mod.compute_varsha_analysis = original_compute_varsha_analysis
        engine_mod.compute_tithi_pravesh = original_compute_tithi_pravesh


if __name__ == "__main__":
    test_dynamic_annual_context_uses_active_solar_year()
    print("test_dynamic_annual_context_uses_active_solar_year: PASS")
