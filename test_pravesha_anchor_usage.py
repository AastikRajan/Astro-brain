"""Regression test for natal-anchor passthrough in precise pravesha solver wiring."""

from datetime import datetime

import vedic_engine.core.astronomy as astro_mod
from vedic_engine.timing.tithi_pravesh import compute_tithi_pravesh


def test_precise_pravesha_uses_computed_natal_anchors() -> None:
    seen = {}

    original_anchors = astro_mod.compute_natal_pravesha_anchors
    original_nak = astro_mod.find_nakshatra_pravesha_epoch
    original_yoga = astro_mod.find_yoga_pravesha_epoch

    def fake_anchors(*, birth_datetime, tz_offset, ayanamsa):
        return {
            "status": "ok",
            "natal_tropical_sun_sign": 4,
            "natal_sidereal_moon_longitude": 222.25,
            "natal_sidereal_yoga_sum": 123.75,
        }

    def fake_nak(**kwargs):
        seen["nak"] = kwargs
        return {"status": "ok", "epoch_local": "2026-08-20T00:00:00"}

    def fake_yoga(**kwargs):
        seen["yoga"] = kwargs
        return {"status": "ok", "epoch_local": "2026-08-21T00:00:00"}

    try:
        astro_mod.compute_natal_pravesha_anchors = fake_anchors
        astro_mod.find_nakshatra_pravesha_epoch = fake_nak
        astro_mod.find_yoga_pravesha_epoch = fake_yoga

        out = compute_tithi_pravesh(
            natal_sun_lon=90.0,
            natal_moon_lon=120.0,
            natal_lagna_sign=2,
            year=2026,
            birth_datetime=datetime(1994, 2, 27, 6, 30, 0),
            tz_offset=5.5,
            ayanamsa="lahiri",
            enable_precise_solver=True,
        )

        assert seen["nak"]["natal_tropical_sun_sign"] == 4
        assert seen["nak"]["natal_sidereal_moon_longitude"] == 222.25
        assert seen["yoga"]["natal_tropical_sun_sign"] == 4
        assert seen["yoga"]["natal_sidereal_yoga_sum"] == 123.75

        pp = out.get("precise_pravesha", {})
        assert pp.get("status") == "ok"
        assert pp.get("natal_sidereal_moon_longitude") == 222.25
        assert pp.get("natal_sidereal_yoga_sum") == 123.75
        assert out.get("source_scope") == "diagnostic_plus_precise_pravesha_solver"
    finally:
        astro_mod.compute_natal_pravesha_anchors = original_anchors
        astro_mod.find_nakshatra_pravesha_epoch = original_nak
        astro_mod.find_yoga_pravesha_epoch = original_yoga


if __name__ == "__main__":
    test_precise_pravesha_uses_computed_natal_anchors()
    print("test_pravesha_anchor_usage: PASS")
