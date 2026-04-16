"""Milestone-F tests for precise pravesha solver wiring."""

from datetime import datetime

from vedic_engine.timing.tithi_pravesh import compute_tithi_pravesh


ALLOWED_STATUSES = {
    "ok",
    "unavailable",
    "no_sun_sign_window",
    "no_root_bracket",
    "not_requested",
}


def test_precision_block_not_requested_by_default() -> None:
    out = compute_tithi_pravesh(
        natal_sun_lon=90.0,
        natal_moon_lon=120.0,
        natal_lagna_sign=2,
        year=2026,
    )
    pp = out.get("precise_pravesha", {})
    assert pp.get("status") == "not_requested"


def test_precision_block_present_when_enabled() -> None:
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
    pp = out.get("precise_pravesha", {})
    assert isinstance(pp, dict)
    assert pp.get("status") in ALLOWED_STATUSES
    if pp.get("status") == "ok":
        nk = pp.get("nakshatra_pravesha", {})
        yg = pp.get("yoga_pravesha", {})
        assert nk.get("status") in ALLOWED_STATUSES
        assert yg.get("status") in ALLOWED_STATUSES


if __name__ == "__main__":
    test_precision_block_not_requested_by_default()
    test_precision_block_present_when_enabled()
    print("test_pravesha_precision: PASS")
