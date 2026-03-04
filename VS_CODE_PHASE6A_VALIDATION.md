# PHASE 6A: Core Validation Against Reference Data
# START A NEW VS CODE CHAT — fresh context, efficient tokens
# Copy this file + the reference JSON into the new chat

---

## STEP 1: Fix Birth Time + Re-run (5 minutes)

The reference data uses birth time 23:26:00, not 23:11:00. Update the test to use the CORRECT time.

```python
# In run_validation.py or a new validate_core.py:
chart = build_chart_swe('Nehru', '1889-11-14', '23:26:00', 'Allahabad', 25.4358, 81.8463, 5.5)
```

Run `analyze_static(chart)` and save output.

---

## STEP 2: Line-by-Line Comparison Script (the efficient way)

Create `validate_core.py` that does this AUTOMATICALLY — no manual checking:

```python
"""
Automated core validation: compares engine output against AstroSage reference JSON.
Prints PASS/FAIL for each check with exact delta values.
"""

import json
from vedic_engine.data.loader import build_chart_swe
from vedic_engine.prediction.engine import PredictionEngine

# ── Reference data (paste the full JSON or load from file) ──
REFERENCE = {
    # ... paste the AstroSage JSON here, or load from new5/nehru_reference.json
}

# ── Build chart with CORRECT birth time ──
chart = build_chart_swe('Nehru', '1889-11-14', '23:26:00', 'Allahabad', 25.4358, 81.8463, 5.5)
engine = PredictionEngine()
static = engine.analyze_static(chart)

results = {"pass": 0, "fail": 0, "details": []}

def check(name, ours, theirs, tolerance=0.0):
    """Compare a value, print PASS/FAIL"""
    if isinstance(ours, (int, float)) and isinstance(theirs, (int, float)):
        delta = abs(ours - theirs)
        ok = delta <= tolerance
    else:
        ok = str(ours).upper() == str(theirs).upper()
        delta = None
    
    status = "PASS" if ok else "FAIL"
    results["pass" if ok else "fail"] += 1
    detail = f"[{status}] {name}: ours={ours}, ref={theirs}"
    if delta is not None:
        detail += f", delta={delta:.4f}"
    results["details"].append(detail)
    print(detail)

# ══════════════════════════════════════════════════════════════
# CHECK 1: LAGNA
# ══════════════════════════════════════════════════════════════
check("Lagna sign", chart.lagna_sign, "Cancer")

# Convert reference DMS to decimal degrees for lagna
# 27-24-41 = 27 + 24/60 + 41/3600 = 27.4114°
ref_lagna_deg = 27 + 24/60 + 41/3600  # 27.4114
check("Lagna degree", chart.lagna_degree, ref_lagna_deg, tolerance=0.5)
# tolerance 0.5° because slight ephemeris/ayanamsha differences

# ══════════════════════════════════════════════════════════════
# CHECK 2: ALL PLANET POSITIONS
# ══════════════════════════════════════════════════════════════
ref_planets = REFERENCE["SECTION_1_planet_positions"]["planets"]

for ref_p in ref_planets:
    name = ref_p["name"].upper()
    ref_sign = ref_p["sign"]
    ref_house = ref_p["house_whole_sign_from_cancer_lagna"]
    ref_nak = ref_p["nakshatra"]
    
    # Parse reference absolute longitude from DMS
    dms = ref_p["absolute_longitude_0_360_dms"]  # e.g., "210-17-20"
    parts = dms.split("-")
    ref_lon = int(parts[0]) + int(parts[1])/60 + int(parts[2])/3600
    
    # Find our planet
    our_planet = None
    for p in chart.planets:
        if p.name.upper() == name or p.name.upper() == ref_p["name"].upper():
            our_planet = p
            break
    
    if our_planet is None:
        # Try alternate name mapping
        name_map = {"RAHU": "RAHU", "KETU": "KETU", "SUN": "SUN", "MOON": "MOON",
                     "MARS": "MARS", "MERCURY": "MERCURY", "JUPITER": "JUPITER",
                     "VENUS": "VENUS", "SATURN": "SATURN"}
        print(f"[SKIP] {name}: planet not found in chart object")
        continue
    
    check(f"{name} sign", our_planet.sign_name, ref_sign)
    check(f"{name} longitude", our_planet.longitude, ref_lon, tolerance=0.5)
    check(f"{name} house", our_planet.house_num, ref_house)
    # Nakshatra check (name matching may need fuzzy match)
    our_nak = our_planet.nakshatra_name if hasattr(our_planet, 'nakshatra_name') else "?"
    check(f"{name} nakshatra", our_nak, ref_nak)

# ══════════════════════════════════════════════════════════════
# CHECK 3: VIMSHOTTARI DASHA SEQUENCE
# ══════════════════════════════════════════════════════════════
ref_dashas = REFERENCE["SECTION_2_dasha_periods_vimshottari"]["mahadasha_sequence_birth_to_1964"]
our_dashas = static.get("dashas", {}).get("vimshottari", [])

for ref_d in ref_dashas:
    ref_lord = ref_d["md"].upper()
    ref_start = ref_d["start"]
    ref_end = ref_d["end"]
    
    # Find matching dasha in our output
    found = False
    for our_d in our_dashas:
        our_lord = our_d.get("lord", our_d.get("planet", "")).upper()
        if our_lord == ref_lord:
            our_start = str(our_d.get("start", ""))[:10]
            our_end = str(our_d.get("end", ""))[:10]
            check(f"Dasha {ref_lord} start", our_start, ref_start)
            check(f"Dasha {ref_lord} end", our_end, ref_end)
            found = True
            break
    if not found:
        print(f"[FAIL] Dasha {ref_lord}: not found in engine output")
        results["fail"] += 1

# Key event dashas
check("1947-08-15 MD", "MOON", REFERENCE["SECTION_2_dasha_periods_vimshottari"]["queries"]["on_1947_08_15"]["md"].upper())
check("1964-05-27 MD", "RAHU", REFERENCE["SECTION_2_dasha_periods_vimshottari"]["queries"]["on_1964_05_27"]["md"].upper())

# ══════════════════════════════════════════════════════════════
# CHECK 4: ASHTAKAVARGA
# ══════════════════════════════════════════════════════════════
ref_sav = REFERENCE["SECTION_5_ashtakavarga"]["sav_totals_by_sign_order_aries_to_pisces"]
our_av = static.get("ashtakvarga", {})
our_sav = our_av.get("sav", our_av.get("SAV", []))

if our_sav:
    # SAV should be 12 numbers summing to 337
    our_sav_list = our_sav if isinstance(our_sav, list) else [our_sav.get(i, 0) for i in range(12)]
    check("SAV sum", sum(our_sav_list), 337)
    for i in range(12):
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                       "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        check(f"SAV {sign_names[i]}", our_sav_list[i], ref_sav[i], tolerance=1)

# ══════════════════════════════════════════════════════════════
# CHECK 5: JAIMINI CHARA KARAKAS
# ══════════════════════════════════════════════════════════════
ref_karakas = REFERENCE["SECTION_6_jaimini"]["computed_from_reported_within_sign_degrees"]["method_A_7_karakas_excluding_rahu"]
our_karakas = static.get("chara_karakas", {})

for role, ref_planet in ref_karakas.items():
    our_planet = our_karakas.get(role, our_karakas.get(role.lower(), "?"))
    if isinstance(our_planet, dict):
        our_planet = our_planet.get("planet", our_planet.get("name", "?"))
    check(f"Karaka {role}", str(our_planet).upper(), ref_planet.upper())

# ══════════════════════════════════════════════════════════════
# CHECK 6: HOUSE LORDS
# ══════════════════════════════════════════════════════════════
ref_lords = REFERENCE["SECTION_7_house_lords"]["lords_by_house_1_to_12"]
for h_num, ref_lord in ref_lords.items():
    our_lord = "?"
    for h in chart.houses:
        if h.house_num == int(h_num):
            our_lord = h.lord
            break
    check(f"H{h_num} lord", str(our_lord).upper(), ref_lord.upper())

# ══════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print(f"VALIDATION SUMMARY: {results['pass']} PASS / {results['fail']} FAIL")
print(f"Accuracy: {results['pass']/(results['pass']+results['fail'])*100:.1f}%")
print("="*60)

# Print all failures for debugging
fails = [d for d in results["details"] if d.startswith("[FAIL]")]
if fails:
    print("\nFAILURES:")
    for f in fails:
        print(f"  {f}")

# Save full report
with open("content42_core_validation.txt", "w") as f:
    f.write(f"CORE VALIDATION: {results['pass']} PASS / {results['fail']} FAIL\n")
    f.write(f"Accuracy: {results['pass']/(results['pass']+results['fail'])*100:.1f}%\n\n")
    for d in results["details"]:
        f.write(d + "\n")
```

---

## STEP 3: What to tell Opus

Give Opus this file + the reference JSON. Tell it:

"Save the reference JSON as new5/nehru_reference.json. Create validate_core.py based on this template. Adapt the planet/dasha/AV field access to match our actual data model (check chart.planets attribute names, static dict key names, etc.). Run it. Fix any access errors. Output content42_core_validation.txt with PASS/FAIL for every check. DO NOT modify engine.py — this is READ-ONLY validation. Only fix the validation script itself."

---

## STEP 4: What comes back

content42 will show something like:
```
[PASS] Lagna sign: ours=Cancer, ref=Cancer
[PASS] SUN sign: ours=Scorpio, ref=Scorpio
[FAIL] SUN longitude: ours=210.05, ref=210.289, delta=0.239
[PASS] Dasha MERCURY start: ours=1889-11-14, ref=1889-11-14
[FAIL] SAV Leo: ours=34, ref=35, delta=1
...
VALIDATION SUMMARY: 85 PASS / 12 FAIL
Accuracy: 87.6%
```

This tells us EXACTLY which core computations need fixing.

---

## WHY NEW CHAT IN VS CODE

Start fresh because:
1. Current VS chat has consumed massive context on Phase 1-5 implementation
2. Validation is a READ-ONLY task — doesn't need implementation history
3. Fresh chat = full token budget for reading engine.py data model and writing the comparison script
4. Keep it focused: "validate core, don't change core"

Give the new chat:
1. This instruction file
2. The reference JSON (as nehru_reference.json)
3. Tell it where engine.py is and to read MEMORY_INDEX.md for data model understanding