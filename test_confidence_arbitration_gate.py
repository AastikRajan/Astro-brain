"""Regression tests for deterministic confidence arbitration gate."""

from vedic_engine.prediction.engine import PredictionEngine


def test_arbitration_caps_promise_failed_output() -> None:
    out = PredictionEngine._apply_confidence_arbitration_gate(
        {
            "overall_boosted": 0.82,
            "gate_status": "PROMISE_FAILED",
            "weak_promise_elevated": False,
            "multi_system_agreement": {"lock_level": 1},
            "components": {
                "kp_confirmation": 0.15,
                "dasha_alignment": 0.18,
                "transit_support": 0.72,
                "d9_quality": 0.45,
            },
            "bayesian": {
                "uncertainty": 0.12,
                "bayesian_verdict": "MODERATE",
            },
        }
    )

    assert out["applied"] is True
    assert out["final"] == 0.3
    assert "promise_failed_cap" in out.get("reasons", [])


def test_arbitration_caps_high_uncertainty_and_weak_bayes() -> None:
    out = PredictionEngine._apply_confidence_arbitration_gate(
        {
            "overall_boosted": 0.88,
            "gate_status": "BOTH_GATES_PASSED",
            "multi_system_agreement": {"lock_level": 3},
            "components": {
                "kp_confirmation": 0.9,
                "dasha_alignment": 0.8,
                "transit_support": 0.82,
                "d9_quality": 0.72,
            },
            "bayesian": {
                "uncertainty": 0.33,
                "bayesian_verdict": "WEAK",
            },
        }
    )

    assert out["applied"] is True
    assert out["final"] == 0.55
    assert "bayesian_high_uncertainty_cap" in out.get("reasons", [])
    assert "bayesian_weak_verdict_cap" in out.get("reasons", [])


def test_arbitration_no_change_when_signals_align() -> None:
    out = PredictionEngine._apply_confidence_arbitration_gate(
        {
            "overall_boosted": 0.62,
            "gate_status": "BOTH_GATES_PASSED",
            "multi_system_agreement": {"lock_level": 3},
            "components": {
                "kp_confirmation": 0.62,
                "dasha_alignment": 0.58,
                "transit_support": 0.61,
                "d9_quality": 0.68,
            },
            "bayesian": {
                "uncertainty": 0.14,
                "bayesian_verdict": "MODERATE",
            },
        }
    )

    assert out["applied"] is False
    assert out["final"] == 0.62
    assert out.get("reasons", []) == []


def test_arbitration_domain_profiles_are_stricter_for_finance_than_career() -> None:
    base_payload = {
        "overall_boosted": 0.74,
        "gate_status": "DASHA_NOT_CONFIRMED",
        "multi_system_agreement": {"lock_level": 1},
        "components": {
            "kp_confirmation": 0.28,
            "dasha_alignment": 0.20,
            "transit_support": 0.69,
            "d9_quality": 0.52,
        },
        "bayesian": {
            "uncertainty": 0.26,
            "bayesian_verdict": "MODERATE",
        },
    }
    out_career = PredictionEngine._apply_confidence_arbitration_gate(
        {**base_payload, "domain": "career"}
    )
    out_finance = PredictionEngine._apply_confidence_arbitration_gate(
        {**base_payload, "domain": "finance"}
    )

    assert out_finance["final"] < out_career["final"]
    assert out_finance["final"] == 0.39
    assert out_career["final"] == 0.5


def test_arbitration_marriage_weak_bayes_cap() -> None:
    out = PredictionEngine._apply_confidence_arbitration_gate(
        {
            "domain": "marriage",
            "overall_boosted": 0.83,
            "gate_status": "BOTH_GATES_PASSED",
            "multi_system_agreement": {"lock_level": 3},
            "components": {
                "kp_confirmation": 0.85,
                "dasha_alignment": 0.82,
                "transit_support": 0.79,
                "d9_quality": 0.77,
            },
            "bayesian": {
                "uncertainty": 0.18,
                "bayesian_verdict": "WEAK",
            },
        }
    )

    assert out["final"] == 0.38
    assert "bayesian_weak_verdict_cap" in out.get("reasons", [])


def test_arbitration_structural_promise_precedence_skips_non_structural_penalties() -> None:
    out = PredictionEngine._apply_confidence_arbitration_gate(
        {
            "domain": "career",
            "overall_boosted": 0.44,
            "gate_status": "PROMISE_FAILED",
            "weak_promise_elevated": True,
            "multi_system_agreement": {"lock_level": 3},
            "components": {
                "kp_confirmation": 0.10,
                "dasha_alignment": 0.10,
                "transit_support": 0.90,
                "d9_quality": 0.25,
            },
            "bayesian": {
                "uncertainty": 0.35,
                "bayesian_verdict": "WEAK",
            },
        }
    )

    assert out["precedence_stage"] == "structural_promise"
    assert out["final"] == 0.44
    assert "kp_vs_transit_contradiction" not in out.get("reasons", [])
    assert "dasha_vs_transit_contradiction" not in out.get("reasons", [])
    assert "bayesian_high_uncertainty_cap" not in out.get("reasons", [])


def test_arbitration_structural_dasha_precedence_skips_transit_contradiction_stack() -> None:
    out = PredictionEngine._apply_confidence_arbitration_gate(
        {
            "domain": "career",
            "overall_boosted": 0.48,
            "gate_status": "DASHA_NOT_CONFIRMED",
            "multi_system_agreement": {"lock_level": 3},
            "components": {
                "kp_confirmation": 0.10,
                "dasha_alignment": 0.10,
                "transit_support": 0.90,
                "d9_quality": 0.20,
            },
            "bayesian": {
                "uncertainty": 0.10,
                "bayesian_verdict": "MODERATE",
            },
        }
    )

    assert out["precedence_stage"] == "structural_dasha"
    assert out["final"] == 0.48
    assert "dasha_not_confirmed_cap" in out.get("reasons", [])
    assert "kp_vs_transit_contradiction" not in out.get("reasons", [])
    assert "dasha_vs_transit_contradiction" not in out.get("reasons", [])
    assert "d9_quality_contradiction_cap" not in out.get("reasons", [])


if __name__ == "__main__":
    test_arbitration_caps_promise_failed_output()
    test_arbitration_caps_high_uncertainty_and_weak_bayes()
    test_arbitration_no_change_when_signals_align()
    test_arbitration_domain_profiles_are_stricter_for_finance_than_career()
    test_arbitration_marriage_weak_bayes_cap()
    test_arbitration_structural_promise_precedence_skips_non_structural_penalties()
    test_arbitration_structural_dasha_precedence_skips_transit_contradiction_stack()
    print("test_confidence_arbitration_gate: PASS")
