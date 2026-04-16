import os
import importlib


def test_milestone_a_flags_default_off():
    # Ensure default behavior is validated independent of shell env.
    os.environ.pop("VE_ENABLE_NATIVE_HARSHA_BALA", None)
    os.environ.pop("VE_ENABLE_TRIPATAKI", None)
    os.environ.pop("VE_ENABLE_PRAVESHA_TIMING", None)
    os.environ.pop("VE_ENABLE_SHODASHA_FUSION", None)
    os.environ.pop("VE_USE_TROPICAL_MONTH_FOR_PRAVESHA", None)

    from vedic_engine.prediction.engine import get_feature_flag_snapshot

    flags = get_feature_flag_snapshot()

    assert flags["VE_ENABLE_NATIVE_HARSHA_BALA"] is False
    assert flags["VE_ENABLE_TRIPATAKI"] is False
    assert flags["VE_ENABLE_PRAVESHA_TIMING"] is False
    assert flags["VE_ENABLE_SHODASHA_FUSION"] is False
    assert flags["VE_USE_TROPICAL_MONTH_FOR_PRAVESHA"] is True


def test_pravesha_tropical_default_can_be_overridden_off():
    import vedic_engine.prediction.engine as engine_mod

    prev = os.environ.get("VE_USE_TROPICAL_MONTH_FOR_PRAVESHA")
    try:
        os.environ["VE_USE_TROPICAL_MONTH_FOR_PRAVESHA"] = "0"
        importlib.reload(engine_mod)
        flags = engine_mod.get_feature_flag_snapshot()
        assert flags["VE_USE_TROPICAL_MONTH_FOR_PRAVESHA"] is False
    finally:
        if prev is None:
            os.environ.pop("VE_USE_TROPICAL_MONTH_FOR_PRAVESHA", None)
        else:
            os.environ["VE_USE_TROPICAL_MONTH_FOR_PRAVESHA"] = prev
        importlib.reload(engine_mod)


if __name__ == "__main__":
    test_milestone_a_flags_default_off()
    test_pravesha_tropical_default_can_be_overridden_off()
    print("test_milestone_a_flags_default_off: PASS")
