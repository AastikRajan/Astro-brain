"""Regression tests for dasha-pravesha context computation in PredictionEngine."""

from datetime import datetime
from types import SimpleNamespace

import vedic_engine.prediction.engine as engine_mod


def _fake_chart() -> SimpleNamespace:
    return SimpleNamespace(
        lagna_sign=0,
        birth_info=SimpleNamespace(
            date="1990-01-01",
            time="10:00:00",
            latitude=12.97,
            longitude=77.59,
            timezone=5.5,
            place="Bengaluru",
        ),
    )


def test_dasha_pravesha_context_weighted_with_debility_diagnostic() -> None:
    engine = engine_mod.PredictionEngine()
    chart = _fake_chart()
    static = {"meta": {"lagna_sign": 0}}
    vim_periods = [
        {
            "planet": "SATURN",
            "start": "2020-01-01",
            "end": "2030-01-01",
            "sub_periods": [
                {
                    "planet": "MERCURY",
                    "start": "2025-01-01",
                    "end": "2027-01-01",
                }
            ],
        }
    ]

    original_build_available = engine_mod._SWE_CHART_BUILD_AVAILABLE
    original_builder = getattr(engine_mod, "build_chart_from_birth_data", None)

    def fake_build_chart_from_birth_data(**kwargs):
        name = str(kwargs.get("name", ""))
        if "Mahadasha" in name:
            # Leo lagna (5th from Aries) => trine support 1.30
            return {
                "lagna": {"degree": 135.0},
                "planets": {
                    "SATURN": {"longitude": 300.0},
                },
            }

        # Virgo lagna (6th from Aries) => dusthana friction 0.70
        # Mercury in Pisces (debilitation) => additional 0.90 dampener.
        return {
            "lagna": {"degree": 165.0},
            "planets": {
                "MERCURY": {"longitude": 350.0},
            },
        }

    try:
        engine_mod._SWE_CHART_BUILD_AVAILABLE = True
        engine_mod.build_chart_from_birth_data = fake_build_chart_from_birth_data

        out = engine._compute_dasha_pravesha_context(
            chart=chart,
            static=static,
            vim_periods=vim_periods,
            on_date=datetime(2026, 4, 14),
        )

        assert out["status"] == "applied"

        w_md = float(engine_mod.DASHA_WEIGHTS.get("mahadasha", 0.50))
        w_ad = float(engine_mod.DASHA_WEIGHTS.get("antardasha", 0.30))
        md_mult = 1.30
        ad_mult = max(0.50, 0.70 * 0.90)
        expected = round(max(0.70, min(1.30, ((md_mult * w_md) + (ad_mult * w_ad)) / (w_md + w_ad))), 3)

        assert out["multiplier"] == expected

        details = out.get("details", [])
        assert len(details) == 2

        md_entry = next(d for d in details if d.get("level") == "mahadasha")
        ad_entry = next(d for d in details if d.get("level") == "antardasha")

        assert md_entry["relation"] == "trine_support"
        assert md_entry["multiplier"] == 1.3

        assert ad_entry["relation"] == "dusthana_friction"
        assert ad_entry["multiplier"] == round(ad_mult, 3)
        assert "lord_debilitated_in_pravesha_chart" in ad_entry.get("diagnostics", [])
    finally:
        engine_mod._SWE_CHART_BUILD_AVAILABLE = original_build_available
        if original_builder is not None:
            engine_mod.build_chart_from_birth_data = original_builder


def test_dasha_pravesha_context_unavailable_when_chart_builder_missing() -> None:
    engine = engine_mod.PredictionEngine()
    chart = _fake_chart()

    original_build_available = engine_mod._SWE_CHART_BUILD_AVAILABLE
    try:
        engine_mod._SWE_CHART_BUILD_AVAILABLE = False
        out = engine._compute_dasha_pravesha_context(
            chart=chart,
            static={"meta": {"lagna_sign": 0}},
            vim_periods=[],
            on_date=datetime(2026, 4, 14),
        )
        assert out["status"] == "unavailable"
        assert out["multiplier"] == 1.0
        assert out["source_gap"] == "swisseph_chart_builder_unavailable"
    finally:
        engine_mod._SWE_CHART_BUILD_AVAILABLE = original_build_available


if __name__ == "__main__":
    test_dasha_pravesha_context_weighted_with_debility_diagnostic()
    test_dasha_pravesha_context_unavailable_when_chart_builder_missing()
    print("test_dasha_pravesha_context: PASS")
