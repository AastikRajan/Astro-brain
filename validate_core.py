"""
Automated core validation: compares engine output against AstroSage reference JSON.
Prints PASS/FAIL for each check with exact delta values.

READ-ONLY validation — does NOT modify engine.py or any engine module.
"""

import json
import sys
import traceback
from datetime import datetime

# ── Load reference data ──────────────────────────────────────────────────────
with open("new5/nehru_reference.json", "r", encoding="utf-8") as f:
    REFERENCE = json.load(f)

# ── Build chart with CORRECT birth time (23:26:00) ──────────────────────────
from vedic_engine.data.loader import build_chart_swe
from vedic_engine.prediction.engine import PredictionEngine

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

print("=" * 60)
print("BUILDING CHART: Nehru, 1889-11-14, 23:26:00, Allahabad")
print("=" * 60)

chart = build_chart_swe(
    'Nehru', '1889-11-14', '23:26:00', 'Allahabad',
    25.4358, 81.8463, 5.5,
)

print("Chart built. Running analyze_static()...")
engine = PredictionEngine()
static = engine.analyze_static(chart)
print("Static analysis complete.\n")

# ── Validation framework ────────────────────────────────────────────────────

results = {"pass": 0, "fail": 0, "skip": 0, "details": []}


def check(name, ours, theirs, tolerance=0.0):
    """Compare a value, print PASS/FAIL."""
    if ours is None and theirs is None:
        status = "PASS"
        delta = None
    elif ours is None or theirs is None:
        status = "FAIL"
        delta = None
    elif isinstance(ours, (int, float)) and isinstance(theirs, (int, float)):
        delta = abs(ours - theirs)
        status = "PASS" if delta <= tolerance else "FAIL"
    else:
        status = "PASS" if str(ours).upper().strip() == str(theirs).upper().strip() else "FAIL"
        delta = None

    results["pass" if status == "PASS" else "fail"] += 1
    detail = f"[{status}] {name}: ours={ours}, ref={theirs}"
    if delta is not None:
        detail += f", delta={delta:.4f}"
    if tolerance > 0 and delta is not None:
        detail += f" (tol={tolerance})"
    results["details"].append(detail)
    print(detail)


def skip(name, reason):
    results["skip"] += 1
    detail = f"[SKIP] {name}: {reason}"
    results["details"].append(detail)
    print(detail)


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 1: LAGNA
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("CHECK 1: LAGNA")
print("=" * 60)

ref_lagna = REFERENCE["SECTION_1_planet_positions"]["lagna"]

# chart.lagna_sign is int 0-11; ref is "Cancer"
our_lagna_sign_name = SIGN_NAMES[chart.lagna_sign]
check("Lagna sign", our_lagna_sign_name, ref_lagna["sign"])

# lagna degree (absolute longitude)
ref_lagna_lon = ref_lagna["absolute_longitude"]  # 117.4114
check("Lagna longitude", chart.lagna_degree, ref_lagna_lon, tolerance=1.0)

# Lagna degree within sign
our_lagna_deg_in_sign = chart.lagna_degree - (chart.lagna_sign * 30)
check("Lagna degree in sign", our_lagna_deg_in_sign, ref_lagna["degree_within_sign"], tolerance=1.0)


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 2: ALL PLANET POSITIONS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("CHECK 2: PLANET POSITIONS")
print("=" * 60)

ref_planets = REFERENCE["SECTION_1_planet_positions"]["planets"]

for ref_p in ref_planets:
    name = ref_p["name"].upper()
    ref_sign = ref_p["sign"]
    ref_house = ref_p["house"]
    ref_nak = ref_p["nakshatra"]
    ref_lon = ref_p["longitude"]

    # Find our planet in chart.planets (Dict[str, PlanetPosition])
    our_planet = chart.planets.get(name)

    if our_planet is None:
        skip(f"{name}", "planet not found in chart.planets")
        continue

    # Sign check: our_planet.sign_index is 0-11
    our_sign_name = SIGN_NAMES[our_planet.sign_index]
    check(f"{name} sign", our_sign_name, ref_sign)

    # Longitude check (absolute sidereal 0-360)
    check(f"{name} longitude", our_planet.longitude, ref_lon, tolerance=1.0)

    # House check (whole-sign from Cancer lagna)
    check(f"{name} house", our_planet.house_num, ref_house)

    # Nakshatra check (fuzzy string match — reference may abbreviate)
    our_nak = our_planet.nakshatra_name if hasattr(our_planet, 'nakshatra_name') else "?"
    # Some nakshatras may be abbreviated differently; do prefix match
    nak_match = (
        str(our_nak).upper().startswith(str(ref_nak).upper()[:5])
        or str(ref_nak).upper().startswith(str(our_nak).upper()[:5])
        or str(our_nak).upper() == str(ref_nak).upper()
    )
    status = "PASS" if nak_match else "FAIL"
    results["pass" if status == "PASS" else "fail"] += 1
    detail = f"[{status}] {name} nakshatra: ours={our_nak}, ref={ref_nak}"
    results["details"].append(detail)
    print(detail)

    # Pada check
    ref_pada = ref_p.get("pada")
    if ref_pada is not None:
        check(f"{name} pada", our_planet.pada, ref_pada)

    # Retrograde check (for Rahu/Ketu)
    if "retrograde" in ref_p:
        check(f"{name} retrograde", our_planet.is_retrograde, ref_p["retrograde"])


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 3: VIMSHOTTARI DASHA SEQUENCE
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("CHECK 3: VIMSHOTTARI DASHA")
print("=" * 60)

ref_dashas = REFERENCE["SECTION_2_dasha_periods_vimshottari"]["mahadasha_sequence"]

# Get dasha periods from static analysis — computed by engine
# The engine computes mahadasha periods via compute_mahadasha_periods()
# which returns list of dicts with "planet", "start", "end"
# We access them from the dynamic analysis or compute directly
try:
    from vedic_engine.timing.vimshottari import compute_mahadasha_periods
    birth_dt = datetime.fromisoformat("1889-11-14T23:26:00")
    moon_lon = chart.planets["MOON"].longitude
    our_vim_periods = compute_mahadasha_periods(moon_lon, birth_dt, levels=1)
    print(f"  Computed {len(our_vim_periods)} mahadasha periods")
except Exception as e:
    our_vim_periods = []
    print(f"  ERROR computing mahadashas: {e}")

for ref_d in ref_dashas:
    ref_lord = ref_d["lord"].upper()
    ref_start = ref_d["start"]
    ref_end = ref_d["end"]

    # Find matching dasha in our output
    found = False
    for our_d in our_vim_periods:
        our_lord = our_d.get("planet", "").upper()
        if our_lord == ref_lord:
            our_start = str(our_d.get("start", ""))[:10]
            our_end = str(our_d.get("end", ""))[:10]
            check(f"Dasha {ref_lord} start", our_start, ref_start)
            check(f"Dasha {ref_lord} end", our_end, ref_end)
            found = True
            break
    if not found:
        results["fail"] += 1
        detail = f"[FAIL] Dasha {ref_lord}: not found in engine output"
        results["details"].append(detail)
        print(detail)

# Key event dasha checks
ref_events = REFERENCE["SECTION_2_dasha_periods_vimshottari"].get("key_events", {})
if ref_events and our_vim_periods:
    for event_date_str, ref_event in ref_events.items():
        event_dt = datetime.fromisoformat(event_date_str)
        ref_md = ref_event["md"].upper()

        # Find which mahadasha covers this date
        our_md = "?"
        for p in our_vim_periods:
            try:
                p_start = datetime.fromisoformat(p["start"])
                p_end = datetime.fromisoformat(p["end"])
                if p_start <= event_dt <= p_end:
                    our_md = p["planet"].upper()
                    break
            except Exception:
                continue
        check(f"Event {event_date_str} MD", our_md, ref_md)


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 4: ASHTAKAVARGA
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("CHECK 4: ASHTAKAVARGA")
print("=" * 60)

ref_av = REFERENCE["SECTION_5_ashtakavarga"]
ref_sav = ref_av["sav_by_sign_aries_to_pisces"]
ref_sav_sum = ref_av["sav_sum"]

# static["ashtakvarga"] comes from compute_full_ashtakvarga()
# Returns: {"bhinna": {planet: [12 ints]}, "sarva": [12 ints], "sarva_total": int, ...}
our_av = static.get("ashtakvarga", {})

if isinstance(our_av, dict) and "error" not in our_av:
    our_sav = our_av.get("sarva", [])
    our_sav_total = our_av.get("sarva_total", sum(our_sav) if our_sav else 0)

    check("SAV sum", our_sav_total, ref_sav_sum, tolerance=2)

    if our_sav and len(our_sav) >= 12:
        for i in range(12):
            check(f"SAV {SIGN_NAMES[i]}", our_sav[i], ref_sav[i], tolerance=2)
    else:
        skip("SAV per-sign", f"our SAV has {len(our_sav) if our_sav else 0} entries")

    # Sun BAV check
    ref_sun_bav = ref_av.get("sun_bav_aries_to_pisces")
    our_bhinna = our_av.get("bhinna", {})
    our_sun_bav = our_bhinna.get("SUN", [])
    if ref_sun_bav and our_sun_bav and len(our_sun_bav) >= 12:
        for i in range(12):
            check(f"Sun BAV {SIGN_NAMES[i]}", our_sun_bav[i], ref_sun_bav[i], tolerance=1)
    else:
        skip("Sun BAV", "data not available")

    # Moon BAV check
    ref_moon_bav = ref_av.get("moon_bav_aries_to_pisces")
    our_moon_bav = our_bhinna.get("MOON", [])
    if ref_moon_bav and our_moon_bav and len(our_moon_bav) >= 12:
        for i in range(12):
            check(f"Moon BAV {SIGN_NAMES[i]}", our_moon_bav[i], ref_moon_bav[i], tolerance=1)
    else:
        skip("Moon BAV", "data not available")

else:
    skip("Ashtakavarga", f"error or missing: {our_av}")


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 5: JAIMINI CHARA KARAKAS (7-planet)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("CHECK 5: JAIMINI CHARA KARAKAS")
print("=" * 60)

ref_karakas = REFERENCE["SECTION_6_jaimini_karakas_7planet"]

# static["karakas"] = {"list": [...], "analysis": {...}}
# list items: {"rank", "role", "role_name", "planet", "degree", "signifies"}
our_karakas_data = static.get("karakas", {})
our_karakas_list = our_karakas_data.get("list", [])

# Build role-to-planet map from our data
our_karaka_map = {}
for k in our_karakas_list:
    if isinstance(k, dict):
        role = k.get("role", "").upper()
        planet = k.get("planet", "").upper()
        if role and planet:
            our_karaka_map[role] = planet

# Compare each role
for role in ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]:
    ref_planet = ref_karakas.get(role, "?").upper()
    our_planet = our_karaka_map.get(role, "?")
    # Also try alternate key names
    if our_planet == "?":
        our_planet = our_karaka_map.get(role.upper(), "?")
    check(f"Karaka {role}", our_planet, ref_planet)

# Karakamsha check
ref_karakamsha = ref_karakas.get("karakamsha_sign", "")
# Try computed.karakamsha_sign first, then jaimini_extended.karakamsha.karakamsha_sign
our_karakamsha_sign = static.get("computed", {}).get("karakamsha_sign", "")
if not our_karakamsha_sign:
    our_jaimini_ext = static.get("jaimini_extended", {})
    our_karakamsha_data = our_jaimini_ext.get("karakamsha", {})
    if isinstance(our_karakamsha_data, dict):
        our_karakamsha_sign = our_karakamsha_data.get("karakamsha_sign",
            our_karakamsha_data.get("sign", our_karakamsha_data.get("sign_name", "")))
        if not our_karakamsha_sign:
            ks_idx = our_karakamsha_data.get("sign_index")
            if ks_idx is not None and 0 <= ks_idx < 12:
                our_karakamsha_sign = SIGN_NAMES[ks_idx]
if ref_karakamsha:
    check("Karakamsha sign", our_karakamsha_sign, ref_karakamsha)


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 6: HOUSE LORDS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("CHECK 6: HOUSE LORDS")
print("=" * 60)

ref_lords = REFERENCE["SECTION_7_house_lords"]

# static["house_lords"] = {house_num_int: planet_name_str}
our_house_lords = static.get("house_lords", {})

# Also can get from chart.houses list
for h_str, ref_lord in ref_lords.items():
    h_num = int(h_str)
    # Try static dict first (int keys)
    our_lord = our_house_lords.get(h_num, "")
    if not our_lord:
        # Try string key
        our_lord = our_house_lords.get(str(h_num), "")
    if not our_lord:
        # Fallback to chart.houses
        for h in chart.houses:
            if h.house_num == h_num:
                our_lord = h.lord
                break
    check(f"H{h_num} lord", str(our_lord).upper(), ref_lord.upper())


# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
total_checks = results["pass"] + results["fail"]
accuracy = (results["pass"] / total_checks * 100) if total_checks > 0 else 0.0

print("\n" + "=" * 60)
print(f"VALIDATION SUMMARY: {results['pass']} PASS / {results['fail']} FAIL / {results['skip']} SKIP")
print(f"Accuracy: {accuracy:.1f}%  ({results['pass']}/{total_checks})")
print("=" * 60)

# Print all failures for quick debugging
fails = [d for d in results["details"] if d.startswith("[FAIL]")]
if fails:
    print(f"\n--- {len(fails)} FAILURES ---")
    for f in fails:
        print(f"  {f}")

# ── Save full report to content42_core_validation.txt ────────────────────────
with open("content42_core_validation.txt", "w", encoding="utf-8") as f:
    f.write(f"CORE VALIDATION: {results['pass']} PASS / {results['fail']} FAIL / {results['skip']} SKIP\n")
    f.write(f"Accuracy: {accuracy:.1f}%  ({results['pass']}/{total_checks})\n")
    f.write(f"Reference: AstroSage | Nehru 1889-11-14 23:26:00 Allahabad\n")
    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
    f.write("=" * 60 + "\n\n")
    for d in results["details"]:
        f.write(d + "\n")
    f.write("\n" + "=" * 60 + "\n")
    f.write(f"SUMMARY: {results['pass']} PASS / {results['fail']} FAIL / {results['skip']} SKIP\n")
    f.write(f"Accuracy: {accuracy:.1f}%\n")
    if fails:
        f.write(f"\n--- {len(fails)} FAILURES ---\n")
        for fl in fails:
            f.write(f"  {fl}\n")

print(f"\nReport saved to content42_core_validation.txt")
