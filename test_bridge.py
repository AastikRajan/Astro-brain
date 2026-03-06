                    # -*- coding: utf-8 -*-
"""
Test the PyJHora bridge — Nehru's chart.
Target: all sections return data, zero crashes.
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from vedic_engine.bridges.pyjhora_bridge import (
    compute_all_pyjhora,
    PYJHORA_AVAILABLE,
)

print(f"PyJHora available: {PYJHORA_AVAILABLE}")
print("Computing all PyJHora data for Nehru...", flush=True)

result = compute_all_pyjhora(1889, 11, 14, 23, 11, 0, 25.4358, 81.8463, 5.5)

print(f"\nAvailable: {result['available']}")
print(f"JD: {result.get('jd')}")

sections = [
    ("Panchanga",         "panchanga"),
    ("Divisional Charts", "divisional_charts"),
    ("Graha Dashas",      "graha_dashas"),
    ("Rasi Dashas",       "rasi_dashas"),
    ("Annual Dashas",     "annual_dashas"),
    ("Yogas",             "yogas"),
    ("Sphutas",           "sphutas"),
    ("Strengths",         "strengths"),
    ("Ashtakavarga",      "ashtakavarga"),
    ("Doshas",            "doshas"),
    ("Arudhas",           "arudhas"),
    ("House Analysis",    "house_analysis"),
]

total_items = 0
empty_sections = []
for label, key in sections:
    data = result.get(key, {})
    count = len(data) if isinstance(data, dict) else (1 if data else 0)
    total_items += count
    status = f"{count} items" if count > 0 else "EMPTY"
    if count == 0:
        empty_sections.append(label)
    print(f"  {label:25s}: {status}")

    # Show first few keys for dicts
    if isinstance(data, dict) and data:
        keys_preview = list(data.keys())[:5]
        print(f"    keys: {keys_preview}")

print(f"\n{'='*60}")
print(f"TOTAL: {total_items} items across {len(sections)} sections")
if empty_sections:
    print(f"EMPTY sections: {empty_sections}")
else:
    print("ALL sections have data!")
print(f"{'='*60}")
