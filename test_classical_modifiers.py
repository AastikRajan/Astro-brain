from vedic_engine.prediction.classical_modifiers import compute_classical_modifier


mock_computed = {
    "doshas": {
        "manglik": {"present": True, "severity": 3, "cancelled": False},
    },
    "combustion": {},
    "graha_yuddha": [],
    "shadbala": {"VENUS": {"ratio": 0.8}},
    "vimshopak": {"VENUS": {"score": 12}},
    "bhavabala": {7: {"rupas": 6.5}},
    "avasthas": {"VENUS": {"state": "normal"}},
    "transit_activations": {
        "SATURN": {"houses_activated": [7]},
        "JUPITER": {"houses_activated": [12]},
    },
    "yogas": [
        {"name": "Marriage Prosperity Yoga", "planets": ["MOON", "JUPITER"]},
    ],
    "active_dasha": {"lord": "VENUS"},
}


if __name__ == "__main__":
    mod = compute_classical_modifier(mock_computed, "marriage")
    print(f"Marriage modifier: {mod:.4f}")
    expected = 0.70 * 0.80 * 0.85 * 0.90
    print(f"Expected approx: {expected:.4f}")
