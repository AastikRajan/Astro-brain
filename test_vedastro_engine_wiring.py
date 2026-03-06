from vedic_engine.data.loader import build_chart_swe
from vedic_engine.prediction.engine import PredictionEngine


def main() -> int:
    chart = build_chart_swe(
        "Nehru",
        "1889-11-14",
        "23:26:00",
        "Allahabad",
        25.4358,
        81.8463,
        5.5,
    )

    static = PredictionEngine().analyze_static(chart)
    computed = (static or {}).get("computed") or {}
    vedastro = computed.get("vedastro")

    assert isinstance(vedastro, dict), "FAIL: computed.vedastro missing or not a dict"
    assert "available" in vedastro, "FAIL: computed.vedastro.available key missing"

    print("PASS: computed.vedastro exists")
    print(f"PASS: computed.vedastro.available = {vedastro.get('available')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
