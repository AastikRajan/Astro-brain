"""Regression tests for non-fatal runtime warning capture helper."""

from vedic_engine.prediction.engine import _record_runtime_warning


def test_record_runtime_warning_stores_message() -> None:
    target = {}
    _record_runtime_warning(
        target,
        "phase_2c2g_transit_adjustment",
        ValueError("bad transit payload"),
    )
    assert "_runtime_warnings" in target
    assert target["_runtime_warnings"]["phase_2c2g_transit_adjustment"] == "bad transit payload"


def test_record_runtime_warning_preserves_existing_entries() -> None:
    target = {"_runtime_warnings": {"existing": "kept"}}
    _record_runtime_warning(
        target,
        "confidence_calibration",
        RuntimeError("calibrator unavailable"),
    )
    assert target["_runtime_warnings"]["existing"] == "kept"
    assert target["_runtime_warnings"]["confidence_calibration"] == "calibrator unavailable"


if __name__ == "__main__":
    test_record_runtime_warning_stores_message()
    test_record_runtime_warning_preserves_existing_entries()
    print("test_runtime_warning_capture: PASS")
