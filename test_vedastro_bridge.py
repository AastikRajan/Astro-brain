from vedic_engine.bridges.vedastro_bridge import get_horoscope_predictions, get_dasa_for_now


# Nehru
result = get_horoscope_predictions(25.4358, 81.8463, "Allahabad", "23:26 14/11/1889", "+05:30")
if result:
    print(f"Predictions: {len(result)} items")
    first = result[0]
    print(f"First: {first.get('name', '')} — {str(first.get('description', ''))[:80]}")
else:
    print("FAIL: No predictions returned")

dasa = get_dasa_for_now(25.4358, 81.8463, "Allahabad", "23:26 14/11/1889", "+05:30")
print(f"Dasa now: {'OK' if dasa is not None else 'None'}")

print("Bridge test done.")
