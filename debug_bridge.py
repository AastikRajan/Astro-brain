"""Quick debug script to check bridge data in engine pipeline."""
from vedic_engine.prediction.engine import PredictionEngine
from vedic_engine.data.loader import load_from_dict, BirthInfo
import json, traceback

nehru_data = json.load(open('nehru_reference.json'))
chart = load_from_dict(nehru_data)
chart.birth_info = BirthInfo(
    name='Nehru', date='1889-11-14', time='23:11:00',
    place='Allahabad', latitude=25.45, longitude=81.85,
    timezone=5.5, ayanamsa=22.32, ayanamsa_model='Lahiri',
)

# Monkey-patch the bridge call to add error logging
import vedic_engine.prediction.engine as eng_mod
orig_static = PredictionEngine.analyze_static

def patched_static(self, chart):
    from datetime import datetime
    from vedic_engine.bridges.pyjhora_bridge import compute_all_pyjhora
    bi = chart.birth_info
    print(f"[DBG] birth_info: date={bi.date!r} time={bi.time!r} lat={bi.latitude} lon={bi.longitude} tz={bi.timezone}")
    try:
        b_dt = datetime.fromisoformat(f"{bi.date}T{bi.time}")
        print(f"[DBG] Calling compute_all_pyjhora with {b_dt.year}/{b_dt.month}/{b_dt.day} {b_dt.hour}:{b_dt.minute}:{b_dt.second}")
        pj = compute_all_pyjhora(
            year=b_dt.year, month=b_dt.month, day=b_dt.day,
            hour=b_dt.hour, minute=b_dt.minute, second=b_dt.second,
            lat=bi.latitude, lon=bi.longitude, tz=bi.timezone,
        )
        print(f"[DBG] PyJHora result: available={pj.get('available')}, yoga_count={len(pj.get('yogas', {}))}")
    except Exception:
        print("[DBG] PyJHora EXCEPTION:")
        traceback.print_exc()

    result = orig_static(self, chart)
    computed = result.get('computed', {})
    pj_data = computed.get('pyjhora', {})
    va_data = computed.get('vedastro', {})
    print(f"[DBG] In static result: pyjhora available={pj_data.get('available')}, keys={list(pj_data.keys())[:5]}")
    print(f"[DBG] In static result: vedastro available={va_data.get('available')}, keys={list(va_data.keys())[:5]}")
    if pj_data.get('available'):
        print(f"[DBG]   pj yogas: {len(pj_data.get('yogas', {}))}")
        print(f"[DBG]   pj doshas: {list(pj_data.get('doshas', {}).keys())}")
        print(f"[DBG]   pj strengths: {list(pj_data.get('strengths', {}).keys())[:5]}")
        # Inspect actual strength VALUES
        st = pj_data.get('strengths', {})
        for sk, sv in st.items():
            if sv is None:
                print(f"[DBG]   str/{sk}: None")
            else:
                s = str(sv)
                if len(s) > 150: s = s[:150] + '...'
                print(f"[DBG]   str/{sk}: {type(sv).__name__} = {s}")
    return result

PredictionEngine.analyze_static = patched_static

eng = PredictionEngine()
result = eng.predict(chart, 'career')
bridge = result.get('confidence', {}).get('bridge_cross_validation', {})
print(f"\n=== Bridge Result ===")
print(f"available: {bridge.get('available')}")
print(f"modifier: {bridge.get('modifier')}")
print(f"modifier_pct: {bridge.get('modifier_pct')}")
for k, v in bridge.items():
    if k in ('available', 'modifier', 'modifier_pct'):
        continue
    if isinstance(v, dict):
        print(f"\n  [{k}]")
        for sk, sv in v.items():
            # Truncate long lists/dicts
            s = str(sv)
            if len(s) > 120:
                s = s[:120] + '...'
            print(f"    {sk}: {s}")
    else:
        print(f"  {k}: {v}")

# Also check what data is available in computed
# Note: predict() may not expose static directly — check bridge data via confidence
pj = bridge  # the bridge result itself has the sub-results
print("\n=== Direct PyJHora data probe ===")
print("  (Skipping 3rd call — SWE state corrupted by engine run)")
print("  Strength values printed above from patched_static")

# Check active_yogas from predict
ay = result.get('active_yogas', [])
print(f"\n=== active_yogas from predict: count={len(ay)}")
if ay:
    for y in ay[:5]:
        if isinstance(y, dict):
            print(f"    {y.get('name', y.get('yoga', '?'))}")
        else:
            print(f"    {repr(y)[:80]}")

print("\n=== Yoga name samples ===")
our_yogas = result.get('static', {}).get('yogas', [])
if our_yogas:
    print(f"  Our yoga count: {len(our_yogas)}")
    for y in our_yogas[:5]:
        if isinstance(y, dict):
            print(f"    {y.get('name', '?')}")
        else:
            print(f"    {getattr(y, 'name', repr(y)[:80])}")
else:
    print("  Our yogas: EMPTY")

pj_yogas = pj_data.get('yogas', {})
if isinstance(pj_yogas, dict) and pj_yogas:
    sample_keys = list(pj_yogas.keys())[:10]
    print(f"  PyJHora yoga sample keys: {sample_keys}")
    # Show values for first 3
    for k in sample_keys[:3]:
        v = pj_yogas[k]
        s = str(v)
        if len(s) > 100: s = s[:100] + '...'
        print(f"    {k}: {type(v).__name__} = {s}")
else:
    print(f"  PyJHora yogas: {type(pj_yogas).__name__}, len={len(pj_yogas) if hasattr(pj_yogas, '__len__') else 'N/A'}")
