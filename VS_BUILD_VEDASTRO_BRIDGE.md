# Build VedAstro Bridge
# Same VS Code chat.

---

## WHAT TO BUILD

Create: `vedic_engine/bridges/vedastro_bridge.py`

This bridge wraps VedAstro's Python library (which calls their API) and stores results in our engine's format. It must use the ISOLATED venv at `vedastro_isolated/.venv` since vedastro needs Python 3.12.

**IMPORTANT:** VedAstro runs on a SEPARATE Python 3.12 venv. Our engine runs on the main .venv. The bridge needs to handle this. Two options:

**Option A (recommended):** Run VedAstro calls via subprocess using the isolated Python:
```python
import subprocess, json

def _call_vedastro(script_code):
    """Run a VedAstro computation in the isolated 3.12 venv."""
    python = r"C:\Users\aasti\Downloads\New folder (3)\vedastro_isolated\.venv\Scripts\python.exe"
    result = subprocess.run(
        [python, "-c", script_code],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None
```

**Option B:** If vedastro also works in the main .venv (it was pip installed there earlier), just import directly like PyJHora bridge.

Check which option works first, then build the bridge.

---

## BRIDGE CODE

```python
"""
VedAstro Bridge — wraps VedAstro Python library.
VedAstro calls their remote API (needs internet).
If unavailable, all functions return None gracefully.
"""

import json, subprocess, os

# Path to isolated venv python (VedAstro needs Python 3.12)
_VEDASTRO_PYTHON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "vedastro_isolated", ".venv", "Scripts", "python.exe"
)

def _vedastro_available():
    """Check if VedAstro isolated env exists."""
    return os.path.exists(_VEDASTRO_PYTHON)

def _safe_call(script, timeout=120):
    """Run VedAstro code in isolated env, return parsed JSON or None."""
    if not _vedastro_available():
        return None
    try:
        result = subprocess.run(
            [_VEDASTRO_PYTHON, "-c", script],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout.strip())
    except Exception:
        pass
    return None

def _build_init_code(lat, lon, location_name, datetime_str, tz_str):
    """Build the common VedAstro setup code."""
    return f"""
import json
from vedastro import *
Calculate.SetAPIKey('FreeAPIUser')
geo = GeoLocation("{location_name}", {lon}, {lat})
bt = Time("{datetime_str} {tz_str}", geo)
"""


def get_horoscope_predictions(lat, lon, location_name, datetime_str, tz_str):
    """Get all horoscope predictions for a birth chart.
    Returns list of dicts with Name, Description, RelatedBody, Weight, Tags."""
    init = _build_init_code(lat, lon, location_name, datetime_str, tz_str)
    script = init + """
result = Calculate.HoroscopePredictions(bt, "Empty")
# Convert to serializable format
out = []
for item in result:
    out.append({
        "name": str(getattr(item, 'Name', item.get('Name','') if isinstance(item,dict) else '')),
        "description": str(getattr(item, 'Description', item.get('Description','') if isinstance(item,dict) else '')),
        "related_body": item.get('RelatedBody', {}) if isinstance(item, dict) else {},
        "weight": float(item.get('Weight', 0) if isinstance(item, dict) else getattr(item, 'Weight', 0)),
        "accuracy": float(item.get('Accuracy', 0) if isinstance(item, dict) else getattr(item, 'Accuracy', 0)),
        "tags": item.get('Tags', []) if isinstance(item, dict) else list(getattr(item, 'Tags', []))
    })
print(json.dumps(out))
"""
    return _safe_call(script)


def get_dasa_for_life(lat, lon, location_name, datetime_str, tz_str, levels=2):
    """Get full Vimshottari dasha periods for life."""
    init = _build_init_code(lat, lon, location_name, datetime_str, tz_str)
    script = init + f"""
result = Calculate.DasaForLife(bt, {levels}, 24, 120)
print(json.dumps(result, default=str))
"""
    return _safe_call(script, timeout=180)


def get_dasa_for_now(lat, lon, location_name, datetime_str, tz_str, levels=3):
    """Get currently active dasha period."""
    init = _build_init_code(lat, lon, location_name, datetime_str, tz_str)
    script = init + f"""
result = Calculate.DasaForNow(bt, {levels})
print(json.dumps(result, default=str))
"""
    return _safe_call(script)


def get_events_at_time(lat, lon, location_name, birth_datetime_str, check_datetime_str, tz_str, tags=None):
    """Get which astrological events are occurring at a specific time."""
    tag_str = json.dumps(tags or ["All"])
    init = _build_init_code(lat, lon, location_name, birth_datetime_str, tz_str)
    script = init + f"""
check_time = Time("{check_datetime_str} {tz_str}", geo)
result = Calculate.EventsAtTime(bt, check_time, {tag_str})
print(json.dumps(result, default=str))
"""
    return _safe_call(script)


def get_events_in_range(lat, lon, location_name, birth_datetime_str, start_str, end_str, tz_str, tags=None, precision_hours=24):
    """Get events occurring in a date range."""
    tag_str = json.dumps(tags or ["All"])
    init = _build_init_code(lat, lon, location_name, birth_datetime_str, tz_str)
    script = init + f"""
start = Time("{start_str} {tz_str}", geo)
end = Time("{end_str} {tz_str}", geo)
result = Calculate.EventsAtRange(bt, start, end, {tag_str}, {precision_hours})
print(json.dumps(result, default=str))
"""
    return _safe_call(script, timeout=300)


def get_planet_data(lat, lon, location_name, datetime_str, tz_str, planet="Sun"):
    """Get all data for a specific planet."""
    init = _build_init_code(lat, lon, location_name, datetime_str, tz_str)
    script = init + f"""
result = Calculate.AllPlanetData(PlanetName.{planet}, bt)
print(json.dumps(result, default=str))
"""
    return _safe_call(script)


def get_house_data(lat, lon, location_name, datetime_str, tz_str, house=1):
    """Get all data for a specific house."""
    init = _build_init_code(lat, lon, location_name, datetime_str, tz_str)
    script = init + f"""
result = Calculate.AllHouseData(HouseName.House{house}, bt)
print(json.dumps(result, default=str))
"""
    return _safe_call(script)


def get_transit_house(lat, lon, location_name, birth_datetime_str, check_datetime_str, tz_str, planet="Saturn", from_ref="Lagna"):
    """Get which house a transiting planet is in relative to birth lagna or moon."""
    init = _build_init_code(lat, lon, location_name, birth_datetime_str, tz_str)
    method = f"TransitHouseFrom{from_ref}"
    script = init + f"""
check_time = Time("{check_datetime_str} {tz_str}", geo)
result = Calculate.{method}(PlanetName.{planet}, check_time, bt)
print(json.dumps(result, default=str))
"""
    return _safe_call(script)


def get_gochara_kakshas(lat, lon, location_name, birth_datetime_str, check_datetime_str, tz_str):
    """Get Gochara Kaksha positions for all planets."""
    init = _build_init_code(lat, lon, location_name, birth_datetime_str, tz_str)
    script = init + f"""
check_time = Time("{check_datetime_str} {tz_str}", geo)
result = Calculate.GocharaKakshas(check_time, bt)
print(json.dumps(result, default=str))
"""
    return _safe_call(script)


def get_match_report(male_birth, female_birth):
    """Get marriage compatibility report.
    Each birth = (lat, lon, location_name, datetime_str, tz_str)"""
    script = f"""
import json
from vedastro import *
Calculate.SetAPIKey('FreeAPIUser')
geo_m = GeoLocation("{male_birth[2]}", {male_birth[1]}, {male_birth[0]})
bt_m = Time("{male_birth[3]} {male_birth[4]}", geo_m)
geo_f = GeoLocation("{female_birth[2]}", {female_birth[1]}, {female_birth[0]})
bt_f = Time("{female_birth[3]} {female_birth[4]}", geo_f)
result = Calculate.MatchReport(bt_m, bt_f)
print(json.dumps(result, default=str))
"""
    return _safe_call(script)


def get_event_catalog():
    """Get the full catalog of all event types grouped by tag."""
    script = """
import json
from vedastro import *
result = Calculate.GetAllEventDataGroupedByTag()
print(json.dumps(result, default=str))
"""
    return _safe_call(script)


def compute_all_vedastro(lat, lon, location_name, datetime_str, tz_str):
    """Master function: get predictions + dasha + planet data.
    Stored in static["computed"]["vedastro"]."""
    if not _vedastro_available():
        return {"available": False}

    args = (lat, lon, location_name, datetime_str, tz_str)

    predictions = get_horoscope_predictions(*args)
    dasa_now = get_dasa_for_now(*args)
    sun_data = get_planet_data(*args, planet="Sun")
    moon_data = get_planet_data(*args, planet="Moon")

    return {
        "available": True,
        "predictions": predictions,
        "prediction_count": len(predictions) if predictions else 0,
        "dasa_now": dasa_now,
        "sun_data": sun_data,
        "moon_data": moon_data,
    }
```

---

## WIRE INTO ENGINE

In `engine.py`, add after the PyJHora bridge section:

```python
# Phase 6B: VedAstro bridge (optional, needs internet)
try:
    from vedic_engine.bridges.vedastro_bridge import compute_all_vedastro
    # Build datetime string in VedAstro format: "HH:MM DD/MM/YYYY"
    bi = chart.birth_info
    va_datetime = f"{bi.hour:02d}:{bi.minute:02d} {bi.day:02d}/{bi.month:02d}/{bi.year}"
    va_tz = f"+{bi.timezone:05.2f}".replace(".", ":") if bi.timezone >= 0 else f"{bi.timezone:06.2f}".replace(".", ":")
    _vedastro = compute_all_vedastro(
        bi.latitude, bi.longitude, bi.place_name or "Unknown",
        va_datetime, va_tz
    )
except Exception:
    _vedastro = {"available": False}
```

Then merge: `static["computed"]["vedastro"] = _vedastro`

---

## TEST

```python
# test_vedastro_bridge.py
from vedic_engine.bridges.vedastro_bridge import *

# Nehru
result = get_horoscope_predictions(25.4358, 81.8463, "Allahabad", "23:26 14/11/1889", "+05:30")
if result:
    print(f"Predictions: {len(result)} items")
    print(f"First: {result[0]['name']} — {result[0]['description'][:80]}")
else:
    print("FAIL: No predictions returned")

dasa = get_dasa_for_now(25.4358, 81.8463, "Allahabad", "23:26 14/11/1889", "+05:30")
print(f"Dasa now: {dasa}")

print("Bridge test done.")
```

## RULES
- VedAstro needs INTERNET. If offline, everything returns None.
- Use subprocess to call isolated 3.12 venv. Don't mix with main venv imports.
- All calls wrapped in try/except. Never crash.
- DO NOT modify any existing vedic_engine files except adding import + call in engine.py.
- Keep it simple. This is an API client, not a computation engine.