"""Pravesha precision utilities backed by Swiss Ephemeris when available."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple


def _signed_angle_diff(a: float, b: float) -> float:
    """Shortest signed angular difference a-b in degrees, range [-180, 180]."""
    return ((a - b + 180.0) % 360.0) - 180.0


def _try_import_swe():
    try:
        import swisseph as swe  # type: ignore
        return swe
    except Exception:
        return None


def _local_dt_to_jd_utc(swe: Any, local_dt: datetime, tz_offset: float) -> float:
    utc_dt = local_dt - timedelta(hours=tz_offset)
    return swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0,
    )


def _jd_to_local_dt(swe: Any, jd: float, tz_offset: float) -> datetime:
    y, m, d, h = swe.revjul(jd)
    utc_dt = datetime(int(y), int(m), int(d), int(h), int((h % 1) * 60), int(((h * 60) % 1) * 60))
    return utc_dt + timedelta(hours=tz_offset)


def _longitudes_at_local_dt(
    swe: Any,
    local_dt: datetime,
    tz_offset: float,
    ayanamsa_sidm: int,
) -> Dict[str, float]:
    """Return tropical Sun and sidereal Sun/Moon at a local datetime."""
    swe.set_sid_mode(ayanamsa_sidm)
    jd = _local_dt_to_jd_utc(swe, local_dt, tz_offset)
    ayan = swe.get_ayanamsa(jd)

    sun_r, _ = swe.calc_ut(jd, swe.SUN)
    moon_r, _ = swe.calc_ut(jd, swe.MOON)
    sun_trop = float(sun_r[0]) % 360.0
    sun_sid = (sun_trop - ayan) % 360.0
    moon_sid = (float(moon_r[0]) - ayan) % 360.0
    return {
        "jd": jd,
        "sun_tropical": sun_trop,
        "sun_sidereal": sun_sid,
        "moon_sidereal": moon_sid,
    }


def _ayanamsa_sidm(swe: Any, ayanamsa: str) -> int:
    amap = {
        "lahiri": swe.SIDM_LAHIRI,
        "raman": swe.SIDM_RAMAN,
        "krishnamurti": swe.SIDM_KRISHNAMURTI,
        "kp": swe.SIDM_KRISHNAMURTI,
        "fagan_bradley": swe.SIDM_FAGAN_BRADLEY,
        "true_chitra": swe.SIDM_TRUE_CITRA,
    }
    return int(amap.get(str(ayanamsa).lower().strip(), swe.SIDM_LAHIRI))


def compute_natal_pravesha_anchors(
    birth_datetime: datetime,
    tz_offset: float = 0.0,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """Compute natal anchors needed by Pravesha solvers."""
    swe = _try_import_swe()
    if swe is None:
        return {"status": "unavailable", "reason": "pyswisseph_not_installed"}

    sidm = _ayanamsa_sidm(swe, ayanamsa)
    lons = _longitudes_at_local_dt(swe, birth_datetime, tz_offset, sidm)

    return {
        "status": "ok",
        "natal_tropical_sun_sign": int(lons["sun_tropical"] / 30.0) % 12,
        "natal_sidereal_moon_longitude": round(lons["moon_sidereal"], 8),
        "natal_sidereal_yoga_sum": round((lons["sun_sidereal"] + lons["moon_sidereal"]) % 360.0, 8),
    }


def _find_tropical_sun_sign_window(
    swe: Any,
    target_year: int,
    target_tropical_sign: int,
    tz_offset: float,
    ayanamsa_sidm: int,
) -> Optional[Tuple[datetime, datetime]]:
    """Find local datetime window in which Sun transits target tropical sign."""
    dt = datetime(target_year, 1, 1, 0, 0, 0)
    end_scan = datetime(target_year + 1, 1, 31, 23, 0, 0)
    step = timedelta(hours=6)

    in_sign_start: Optional[datetime] = None
    prev_dt = dt
    prev_sign = int(_longitudes_at_local_dt(swe, dt, tz_offset, ayanamsa_sidm)["sun_tropical"] / 30.0) % 12
    dt = dt + step

    while dt <= end_scan:
        cur_sign = int(_longitudes_at_local_dt(swe, dt, tz_offset, ayanamsa_sidm)["sun_tropical"] / 30.0) % 12
        if in_sign_start is None and prev_sign != target_tropical_sign and cur_sign == target_tropical_sign:
            in_sign_start = prev_dt
        if in_sign_start is not None and prev_sign == target_tropical_sign and cur_sign != target_tropical_sign:
            return (in_sign_start, dt)
        prev_dt, prev_sign = dt, cur_sign
        dt = dt + step

    return None


def _bisection_root(
    swe: Any,
    start_local: datetime,
    end_local: datetime,
    tz_offset: float,
    ayanamsa_sidm: int,
    fn,
    max_iter: int = 60,
) -> Optional[Dict[str, Any]]:
    """Find a sign-change bracket in window, then refine root by bisection."""
    step = timedelta(hours=1)
    t0 = start_local
    f0 = float(fn(t0))
    t = t0 + step

    bracket: Optional[Tuple[datetime, datetime, float, float]] = None
    best_t = t0
    best_abs = abs(f0)

    while t <= end_local:
        f = float(fn(t))
        af = abs(f)
        if af < best_abs:
            best_abs = af
            best_t = t
        if f0 == 0.0:
            bracket = (t0, t0, f0, f0)
            break
        if f == 0.0 or (f0 < 0.0 and f > 0.0) or (f0 > 0.0 and f < 0.0):
            bracket = (t0, t, f0, f)
            break
        t0, f0 = t, f
        t = t + step

    if bracket is None:
        return {
            "status": "no_root_bracket",
            "epoch_local": best_t.isoformat(),
            "error_deg": round(best_abs, 8),
        }

    a_t, b_t, a_f, b_f = bracket
    if a_t == b_t:
        return {
            "status": "ok",
            "epoch_local": a_t.isoformat(),
            "error_deg": 0.0,
            "iterations": 0,
        }

    it = 0
    while it < max_iter and (b_t - a_t).total_seconds() > 1.0:
        it += 1
        mid = a_t + (b_t - a_t) / 2
        mid_f = float(fn(mid))
        if mid_f == 0.0:
            a_t, b_t = mid, mid
            a_f, b_f = 0.0, 0.0
            break
        if (a_f < 0.0 and mid_f > 0.0) or (a_f > 0.0 and mid_f < 0.0):
            b_t, b_f = mid, mid_f
        else:
            a_t, a_f = mid, mid_f

    epoch = a_t + (b_t - a_t) / 2
    final_err = abs(float(fn(epoch)))
    return {
        "status": "ok",
        "epoch_local": epoch.isoformat(),
        "error_deg": round(final_err, 8),
        "iterations": it,
    }


def find_nakshatra_pravesha_epoch(
    natal_tropical_sun_sign: int,
    natal_sidereal_moon_longitude: float,
    target_year: int,
    tz_offset: float = 0.0,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """
    Find annual Nakshatra Pravesha epoch:
    Sun in natal tropical sign and Moon at natal sidereal longitude.
    """
    swe = _try_import_swe()
    if swe is None:
        return {"status": "unavailable", "reason": "pyswisseph_not_installed"}

    sidm = _ayanamsa_sidm(swe, ayanamsa)
    window = _find_tropical_sun_sign_window(
        swe,
        target_year=target_year,
        target_tropical_sign=int(natal_tropical_sun_sign) % 12,
        tz_offset=tz_offset,
        ayanamsa_sidm=sidm,
    )
    if window is None:
        return {"status": "no_sun_sign_window"}

    w_start, w_end = window

    def _f(local_dt: datetime) -> float:
        moon_sid = _longitudes_at_local_dt(swe, local_dt, tz_offset, sidm)["moon_sidereal"]
        return _signed_angle_diff(moon_sid, float(natal_sidereal_moon_longitude) % 360.0)

    root = _bisection_root(
        swe,
        start_local=w_start,
        end_local=w_end,
        tz_offset=tz_offset,
        ayanamsa_sidm=sidm,
        fn=_f,
    )

    if root.get("status") == "ok":
        local_dt = datetime.fromisoformat(root["epoch_local"])
        jd = _local_dt_to_jd_utc(swe, local_dt, tz_offset)
        utc_dt = _jd_to_local_dt(swe, jd, 0.0)
        root["epoch_utc"] = utc_dt.isoformat()

    root["window_start_local"] = w_start.isoformat()
    root["window_end_local"] = w_end.isoformat()
    root["method"] = "tropical_sun_window_plus_sidereal_moon_root"
    return root


def find_yoga_pravesha_epoch(
    natal_tropical_sun_sign: int,
    natal_sidereal_yoga_sum: float,
    target_year: int,
    tz_offset: float = 0.0,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """
    Find annual Yoga Pravesha epoch:
    Sun in natal tropical sign and (sidereal Sun + sidereal Moon) matches natal sum.
    """
    swe = _try_import_swe()
    if swe is None:
        return {"status": "unavailable", "reason": "pyswisseph_not_installed"}

    sidm = _ayanamsa_sidm(swe, ayanamsa)
    window = _find_tropical_sun_sign_window(
        swe,
        target_year=target_year,
        target_tropical_sign=int(natal_tropical_sun_sign) % 12,
        tz_offset=tz_offset,
        ayanamsa_sidm=sidm,
    )
    if window is None:
        return {"status": "no_sun_sign_window"}

    w_start, w_end = window

    def _f(local_dt: datetime) -> float:
        vals = _longitudes_at_local_dt(swe, local_dt, tz_offset, sidm)
        cur = (vals["sun_sidereal"] + vals["moon_sidereal"]) % 360.0
        return _signed_angle_diff(cur, float(natal_sidereal_yoga_sum) % 360.0)

    root = _bisection_root(
        swe,
        start_local=w_start,
        end_local=w_end,
        tz_offset=tz_offset,
        ayanamsa_sidm=sidm,
        fn=_f,
    )

    if root.get("status") == "ok":
        local_dt = datetime.fromisoformat(root["epoch_local"])
        jd = _local_dt_to_jd_utc(swe, local_dt, tz_offset)
        utc_dt = _jd_to_local_dt(swe, jd, 0.0)
        root["epoch_utc"] = utc_dt.isoformat()

    root["window_start_local"] = w_start.isoformat()
    root["window_end_local"] = w_end.isoformat()
    root["method"] = "tropical_sun_window_plus_sidereal_yoga_root"
    return root
