"""
VedAstro Bridge — wraps VedAstro Python library.
VedAstro calls their remote API (needs internet).
If unavailable, all functions return None gracefully.
"""
from __future__ import annotations

import json
import os
import subprocess
from typing import Any, Dict, List, Optional, Tuple


_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_VEDASTRO_PYTHON = os.path.join(_ROOT_DIR, "vedastro_isolated", ".venv", "Scripts", "python.exe")
_JSON_START = "__VEDASTRO_JSON_START__"
_JSON_END = "__VEDASTRO_JSON_END__"


def _vedastro_available() -> bool:
    """Check if VedAstro isolated env exists."""
    return os.path.exists(_VEDASTRO_PYTHON)


def _py_literal(value: Any) -> str:
    """Return a safe Python literal representation for subprocess script injection."""
    return json.dumps(value)


def _extract_json(stdout: str) -> Optional[Any]:
    """Extract JSON payload from noisy stdout (banner/logs + payload)."""
    if not stdout:
        return None

    start_idx = stdout.find(_JSON_START)
    end_idx = stdout.rfind(_JSON_END)
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        payload = stdout[start_idx + len(_JSON_START):end_idx].strip()
        if payload:
            try:
                return json.loads(payload)
            except Exception:
                return None

    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    for line in reversed(lines):
        if line.startswith("{") or line.startswith("[") or line.startswith('"'):
            try:
                return json.loads(line)
            except Exception:
                continue
    return None


def _safe_call(script: str, timeout: int = 120) -> Optional[Any]:
    """Run VedAstro code in isolated env, return parsed JSON or None."""
    if not _vedastro_available():
        return None

    wrapped = (
        "import json\n"
        "try:\n"
        f"    {script.replace(chr(10), chr(10) + '    ')}\n"
        f"    print({_py_literal(_JSON_START)})\n"
        "    print(json.dumps(result, default=str))\n"
        f"    print({_py_literal(_JSON_END)})\n"
        "except Exception:\n"
        "    raise\n"
    )

    try:
        proc = subprocess.run(
            [_VEDASTRO_PYTHON, "-c", wrapped],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except Exception:
        return None

    if proc.returncode != 0:
        return None

    return _extract_json(proc.stdout)


def _build_init_code(lat: float, lon: float, location_name: str, datetime_str: str, tz_str: str) -> str:
    """Build common VedAstro setup script body, defining `geo` and `bt`."""
    return (
        "from vedastro import *\n"
        "Calculate.SetAPIKey('FreeAPIUser')\n"
        f"geo = GeoLocation({_py_literal(location_name)}, {float(lon)}, {float(lat)})\n"
        f"bt = Time({_py_literal(f'{datetime_str} {tz_str}')}, geo)\n"
    )


def get_horoscope_predictions(
    lat: float,
    lon: float,
    location_name: str,
    datetime_str: str,
    tz_str: str,
) -> Optional[List[Dict[str, Any]]]:
    """Get all horoscope predictions for a birth chart."""
    init = _build_init_code(lat, lon, location_name, datetime_str, tz_str)
    script = (
        init
        + "raw = Calculate.HoroscopePredictions(bt, 'Empty')\n"
        + "out = []\n"
        + "for item in raw:\n"
        + "    if isinstance(item, dict):\n"
        + "        out.append({\n"
        + "            'name': str(item.get('Name', '')),\n"
        + "            'description': str(item.get('Description', '')),\n"
        + "            'related_body': item.get('RelatedBody', {}),\n"
        + "            'weight': float(item.get('Weight', 0) or 0),\n"
        + "            'accuracy': float(item.get('Accuracy', 0) or 0),\n"
        + "            'tags': list(item.get('Tags', [])),\n"
        + "        })\n"
        + "    else:\n"
        + "        out.append({\n"
        + "            'name': str(getattr(item, 'Name', '')),\n"
        + "            'description': str(getattr(item, 'Description', '')),\n"
        + "            'related_body': getattr(item, 'RelatedBody', {}),\n"
        + "            'weight': float(getattr(item, 'Weight', 0) or 0),\n"
        + "            'accuracy': float(getattr(item, 'Accuracy', 0) or 0),\n"
        + "            'tags': list(getattr(item, 'Tags', [])),\n"
        + "        })\n"
        + "result = out\n"
    )
    value = _safe_call(script)
    return value if isinstance(value, list) else None


def get_dasa_for_life(
    lat: float,
    lon: float,
    location_name: str,
    datetime_str: str,
    tz_str: str,
    levels: int = 2,
) -> Optional[Any]:
    """Get full Vimshottari dasha periods for life."""
    init = _build_init_code(lat, lon, location_name, datetime_str, tz_str)
    script = init + f"result = Calculate.DasaForLife(bt, {int(levels)}, 24, 120)\n"
    return _safe_call(script, timeout=180)


def get_dasa_for_now(
    lat: float,
    lon: float,
    location_name: str,
    datetime_str: str,
    tz_str: str,
    levels: int = 3,
) -> Optional[Any]:
    """Get currently active dasha period."""
    init = _build_init_code(lat, lon, location_name, datetime_str, tz_str)
    script = init + f"result = Calculate.DasaForNow(bt, {int(levels)})\n"
    return _safe_call(script)


def get_events_at_time(
    lat: float,
    lon: float,
    location_name: str,
    birth_datetime_str: str,
    check_datetime_str: str,
    tz_str: str,
    tags: Optional[List[str]] = None,
) -> Optional[Any]:
    """Get astrological events at a specific time."""
    tag_str = _py_literal(tags or ["All"])
    init = _build_init_code(lat, lon, location_name, birth_datetime_str, tz_str)
    script = (
        init
        + f"check_time = Time({_py_literal(f'{check_datetime_str} {tz_str}')}, geo)\n"
        + f"result = Calculate.EventsAtTime(bt, check_time, {tag_str})\n"
    )
    return _safe_call(script)


def get_events_in_range(
    lat: float,
    lon: float,
    location_name: str,
    birth_datetime_str: str,
    start_str: str,
    end_str: str,
    tz_str: str,
    tags: Optional[List[str]] = None,
    precision_hours: int = 24,
) -> Optional[Any]:
    """Get events occurring in a date range."""
    tag_str = _py_literal(tags or ["All"])
    init = _build_init_code(lat, lon, location_name, birth_datetime_str, tz_str)
    script = (
        init
        + f"start = Time({_py_literal(f'{start_str} {tz_str}')}, geo)\n"
        + f"end = Time({_py_literal(f'{end_str} {tz_str}')}, geo)\n"
        + f"result = Calculate.EventsAtRange(bt, start, end, {tag_str}, {int(precision_hours)})\n"
    )
    return _safe_call(script, timeout=300)


def get_planet_data(
    lat: float,
    lon: float,
    location_name: str,
    datetime_str: str,
    tz_str: str,
    planet: str = "Sun",
) -> Optional[Any]:
    """Get all data for a specific planet."""
    init = _build_init_code(lat, lon, location_name, datetime_str, tz_str)
    script = init + f"result = Calculate.AllPlanetData(PlanetName.{planet}, bt)\n"
    return _safe_call(script)


def get_house_data(
    lat: float,
    lon: float,
    location_name: str,
    datetime_str: str,
    tz_str: str,
    house: int = 1,
) -> Optional[Any]:
    """Get all data for a specific house."""
    house_no = max(1, min(12, int(house)))
    init = _build_init_code(lat, lon, location_name, datetime_str, tz_str)
    script = init + f"result = Calculate.AllHouseData(HouseName.House{house_no}, bt)\n"
    return _safe_call(script)


def get_transit_house(
    lat: float,
    lon: float,
    location_name: str,
    birth_datetime_str: str,
    check_datetime_str: str,
    tz_str: str,
    planet: str = "Saturn",
    from_ref: str = "Lagna",
) -> Optional[Any]:
    """Get transit house relative to Lagna or Moon."""
    safe_ref = from_ref if from_ref in {"Lagna", "Moon", "NavamsaLagna", "NavamsaMoon"} else "Lagna"
    method = f"TransitHouseFrom{safe_ref}"
    init = _build_init_code(lat, lon, location_name, birth_datetime_str, tz_str)
    script = (
        init
        + f"check_time = Time({_py_literal(f'{check_datetime_str} {tz_str}')}, geo)\n"
        + f"result = Calculate.{method}(PlanetName.{planet}, check_time, bt)\n"
    )
    return _safe_call(script)


def get_gochara_kakshas(
    lat: float,
    lon: float,
    location_name: str,
    birth_datetime_str: str,
    check_datetime_str: str,
    tz_str: str,
) -> Optional[Any]:
    """Get Gochara Kaksha positions for all planets."""
    init = _build_init_code(lat, lon, location_name, birth_datetime_str, tz_str)
    script = (
        init
        + f"check_time = Time({_py_literal(f'{check_datetime_str} {tz_str}')}, geo)\n"
        + "result = Calculate.GocharaKakshas(check_time, bt)\n"
    )
    return _safe_call(script)


def get_match_report(
    male_birth: Tuple[float, float, str, str, str],
    female_birth: Tuple[float, float, str, str, str],
) -> Optional[Any]:
    """Get marriage compatibility report."""
    script = (
        "from vedastro import *\n"
        "Calculate.SetAPIKey('FreeAPIUser')\n"
        f"geo_m = GeoLocation({_py_literal(male_birth[2])}, {float(male_birth[1])}, {float(male_birth[0])})\n"
        f"bt_m = Time({_py_literal(f'{male_birth[3]} {male_birth[4]}')}, geo_m)\n"
        f"geo_f = GeoLocation({_py_literal(female_birth[2])}, {float(female_birth[1])}, {float(female_birth[0])})\n"
        f"bt_f = Time({_py_literal(f'{female_birth[3]} {female_birth[4]}')}, geo_f)\n"
        "result = Calculate.MatchReport(bt_m, bt_f)\n"
    )
    return _safe_call(script)


def get_event_catalog() -> Optional[Any]:
    """Get full catalog of all event types grouped by tag."""
    script = (
        "from vedastro import *\n"
        "Calculate.SetAPIKey('FreeAPIUser')\n"
        "result = Calculate.GetAllEventDataGroupedByTag()\n"
    )
    return _safe_call(script)


def _get_all_planet_data_batch(
    lat: float,
    lon: float,
    location_name: str,
    datetime_str: str,
    tz_str: str,
) -> Optional[Dict[str, Any]]:
    """Fetch planet data for ALL 9 planets in a single subprocess call."""
    init = _build_init_code(lat, lon, location_name, datetime_str, tz_str)
    script = (
        init
        + "planets = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']\n"
        + "out = {}\n"
        + "for p in planets:\n"
        + "    try:\n"
        + "        pn = getattr(PlanetName, p, None)\n"
        + "        if pn is not None:\n"
        + "            out[p] = Calculate.AllPlanetData(pn, bt)\n"
        + "    except Exception:\n"
        + "        pass\n"
        + "result = out\n"
    )
    return _safe_call(script, timeout=120)


def compute_all_vedastro(
    lat: float,
    lon: float,
    location_name: str,
    datetime_str: str,
    tz_str: str,
) -> Dict[str, Any]:
    """Master function: get predictions + dasha + all planet data.

    Fetches:
      1. All 200+ horoscope predictions (with tags, weights, accuracy)
      2. Currently-active Vimshottari dasha period (3 levels)
      3. Planet data for all 9 grahas (batched in 1 subprocess call)
    """
    if not _vedastro_available():
        return {"available": False}

    args = (lat, lon, location_name, datetime_str, tz_str)

    predictions = get_horoscope_predictions(*args)
    dasa_now = get_dasa_for_now(*args)

    # Batch planet data: 1 subprocess call instead of 9 sequential ones
    all_planet_data = _get_all_planet_data_batch(*args)
    if not isinstance(all_planet_data, dict):
        all_planet_data = {}

    return {
        "available": True,
        "predictions": predictions,
        "prediction_count": len(predictions) if isinstance(predictions, list) else 0,
        "dasa_now": dasa_now,
        "planet_data": all_planet_data,
        # Backward compat: keep sun/moon at top level
        "sun_data": all_planet_data.get("Sun"),
        "moon_data": all_planet_data.get("Moon"),
    }
