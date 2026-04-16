"""Milestone-E tests for domain-isolated shodasha fusion helper."""

from vedic_engine.prediction.engine import _compute_shodasha_domain_fusion


def test_shodasha_fusion_applies_positive_delta_when_domain_stronger() -> None:
    vim = {
        "SUN": {"percentage": 85.0},
        "SATURN": {"percentage": 80.0},
        "MERCURY": {"percentage": 75.0},
        "MOON": {"percentage": 40.0},
        "VENUS": {"percentage": 45.0},
    }
    out = _compute_shodasha_domain_fusion(vim, ["SUN", "SATURN", "MERCURY"])
    assert out["status"] == "applied"
    assert out["domain_avg_pct"] > out["global_avg_pct"]
    assert 0.0 < out["delta_applied"] <= 0.06
    assert out["diagnostic_score"] is not None


def test_shodasha_fusion_unavailable_without_domain_planets() -> None:
    vim = {
        "SUN": {"percentage": 70.0},
        "MOON": {"percentage": 65.0},
    }
    out = _compute_shodasha_domain_fusion(vim, ["RAHU", "KETU"])
    assert out["status"] == "unavailable"
    assert out["delta_applied"] == 0.0
    assert out["source_gap"] == "no_domain_planet_vimshopak_data"


def test_shodasha_fusion_applies_domain_varga_policy_from_breakdown() -> None:
    vim = {
        "MERCURY": {
            "percentage": 62.0,
            "breakdown": {
                "D1": {"weight": 3.5, "contribution": 1.75},
                "D2": {"weight": 1.0, "contribution": 1.0},
                "D9": {"weight": 3.0, "contribution": 1.5},
                "D10": {"weight": 0.5, "contribution": 0.1},
                "D60": {"weight": 4.0, "contribution": 1.2},
            },
        },
    }

    out_career = _compute_shodasha_domain_fusion(vim, ["MERCURY"], domain="career")
    out_finance = _compute_shodasha_domain_fusion(vim, ["MERCURY"], domain="finance")

    assert out_career["status"] == "applied"
    assert out_finance["status"] == "applied"
    assert "D10" in out_career["policy_vargas"]
    assert "D2" in out_finance["policy_vargas"]
    # Finance policy includes D2, where Mercury is intentionally strongest.
    assert out_finance["domain_avg_pct"] > out_career["domain_avg_pct"]


def test_shodasha_fusion_falls_back_to_percentage_without_breakdown() -> None:
    vim = {
        "SUN": {"percentage": 78.0},
        "SATURN": {"percentage": 72.0},
        "MOON": {"percentage": 40.0},
    }
    out = _compute_shodasha_domain_fusion(vim, ["SUN", "SATURN"], domain="career")

    assert out["status"] == "applied"
    assert out["domain_avg_pct"] is not None
    assert out["policy_global_source"] in {"policy_varga_avg", "full_vimshopak_avg"}


if __name__ == "__main__":
    test_shodasha_fusion_applies_positive_delta_when_domain_stronger()
    test_shodasha_fusion_unavailable_without_domain_planets()
    test_shodasha_fusion_applies_domain_varga_policy_from_breakdown()
    test_shodasha_fusion_falls_back_to_percentage_without_breakdown()
    print("test_shodasha_fusion: PASS")
