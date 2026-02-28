"""
JSON / dict loader for chart data.
Accepts the raw kundli JSON export from astrology software and maps it
into VedicChart model.  Fields that can be computed from scratch are
re-computed by the engine; fields taken from export are validated.
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from vedic_engine.data.models import (
    BirthInfo, VedicChart, PlanetPosition, HouseCusp,
    ShadbalaPlanet, BhavaStrength, AshtakavargaData, DashaPeriod
)
from vedic_engine.config import (
    Planet, Sign, SIGN_LORDS, NAKSHATRA_NAMES, VIMSHOTTARI_SEQUENCE,
    NAKSHATRA_SPAN, VIMSHOTTARI_YEARS, SHADBALA_MINIMUMS
)

PLANET_NAMES = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU"]
SIGN_NAMES = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
              "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]


def _planet_enum(name: str):
    mapping = {
        "SUN": Planet.SUN, "MOON": Planet.MOON, "MARS": Planet.MARS,
        "MERCURY": Planet.MERCURY, "JUPITER": Planet.JUPITER,
        "VENUS": Planet.VENUS, "SATURN": Planet.SATURN,
        "RAHU": Planet.RAHU, "KETU": Planet.KETU,
    }
    return mapping.get(name.upper())


def _sign_index(name: str) -> int:
    try:
        return SIGN_NAMES.index(name)
    except ValueError:
        return -1


def _dms_to_deg(dms: str) -> float:
    """Convert '24°14'18\"' or '24:14:18' to decimal degrees."""
    dms = dms.replace("°", ":").replace("'", ":").replace('"', "")
    parts = [p for p in dms.split(":") if p.strip()]
    d = float(parts[0]) if len(parts) > 0 else 0
    m = float(parts[1]) if len(parts) > 1 else 0
    s = float(parts[2]) if len(parts) > 2 else 0
    return d + m / 60.0 + s / 3600.0


def load_from_json(path: str) -> VedicChart:
    """Load VedicChart from a JSON file exported by astrology software."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return load_from_dict(raw)


def load_from_dict(raw: Dict[str, Any]) -> VedicChart:
    """Parse a raw dict (from JSON) into a VedicChart object."""
    # ── Birth info ──────────────────────────────────────────────
    bi_raw = raw.get("birth_info", raw.get("birth", {}))
    birth_info = BirthInfo(
        name=bi_raw.get("name", "Unknown"),
        date=bi_raw.get("date", ""),
        time=bi_raw.get("time", ""),
        place=bi_raw.get("place", ""),
        latitude=float(bi_raw.get("latitude", 0)),
        longitude=float(bi_raw.get("longitude", 0)),
        timezone=float(bi_raw.get("timezone", 5.5)),
        ayanamsa=float(bi_raw.get("ayanamsa", 23.0)),
        ayanamsa_model=bi_raw.get("ayanamsa_model", "Lahiri"),
    )

    # ── Lagna ───────────────────────────────────────────────────
    lagna_raw = raw.get("lagna", raw.get("ascendant", {}))
    lagna_sign_name = lagna_raw.get("sign", "Aries")
    lagna_sign = _sign_index(lagna_sign_name)
    deg_str = lagna_raw.get("degree", lagna_raw.get("longitude", "0"))
    lagna_degree = _dms_to_deg(str(deg_str)) if isinstance(deg_str, str) else float(deg_str)
    # make absolute
    if lagna_degree < 30:
        lagna_degree = lagna_sign * 30 + lagna_degree

    chart = VedicChart(
        birth_info=birth_info,
        lagna_sign=lagna_sign,
        lagna_degree=lagna_degree,
    )

    # ── Planets ─────────────────────────────────────────────────
    planets_raw = raw.get("planets", {})
    for pname, pdata in planets_raw.items():
        pname = pname.upper()
        if pname not in PLANET_NAMES:
            continue

        sign_name = pdata.get("sign", "Aries")
        sign_idx = _sign_index(sign_name)
        deg_str = pdata.get("degree_in_sign", pdata.get("degree", "0"))
        deg_in_sign = _dms_to_deg(str(deg_str)) if isinstance(deg_str, str) else float(deg_str)
        abs_lon = sign_idx * 30 + deg_in_sign

        nak_idx = int(abs_lon / NAKSHATRA_SPAN)
        nak_idx = min(nak_idx, 26)
        nak_lord = VIMSHOTTARI_SEQUENCE[nak_idx % 9]
        pos_in_nak = abs_lon % NAKSHATRA_SPAN
        pada = int(pos_in_nak / (NAKSHATRA_SPAN / 4)) + 1
        pada = min(pada, 4)

        pp = PlanetPosition(
            planet=pname,
            longitude=abs_lon,
            sign_index=sign_idx,
            degree_in_sign=deg_in_sign,
            nakshatra_index=nak_idx,
            nakshatra_name=NAKSHATRA_NAMES[nak_idx],
            nakshatra_lord=nak_lord.name,
            pada=pada,
            is_retrograde=bool(pdata.get("retrograde", False)),
            is_combust=bool(pdata.get("combust", False)),
            speed=float(pdata.get("speed", 0.0)),
            kp_rashi_lord=pdata.get("kp_rashi_lord", ""),
            kp_nak_lord=pdata.get("kp_nak_lord", ""),
            kp_sub_lord=pdata.get("kp_sub_lord", ""),
            kp_sub_sub_lord=pdata.get("kp_sub_sub_lord", ""),
        )

        # Assign house from lagna
        pp.house_num = ((sign_idx - lagna_sign) % 12) + 1
        chart.planets[pname] = pp

    # ── Houses / Cusps ──────────────────────────────────────────
    houses_raw = raw.get("houses", raw.get("cusps", []))
    if isinstance(houses_raw, dict):
        houses_raw = [{"house": int(k), **v} for k, v in houses_raw.items()]
    for h in houses_raw:
        hn = int(h.get("house", h.get("house_num", 1)))
        sign_name = h.get("sign", SIGN_NAMES[(lagna_sign + hn - 1) % 12])
        sign_idx = _sign_index(sign_name)
        lon_val = h.get("longitude", h.get("degree", sign_idx * 30.0))
        if isinstance(lon_val, str):
            lon_val = _dms_to_deg(lon_val)
        lord = SIGN_LORDS[Sign(sign_idx)].name
        chart.houses.append(HouseCusp(
            house_num=hn, longitude=float(lon_val), sign_index=sign_idx,
            sign_name=sign_name, lord=lord,
            kp_nak_lord=h.get("kp_nak_lord", ""),
            kp_sub_lord=h.get("kp_sub_lord", ""),
        ))
    if not chart.houses:
        # Generate equal-house cusps from lagna
        for i in range(12):
            si = (lagna_sign + i) % 12
            chart.houses.append(HouseCusp(
                house_num=i + 1,
                longitude=(lagna_degree + i * 30) % 360,
                sign_index=si,
                sign_name=SIGN_NAMES[si],
                lord=SIGN_LORDS[Sign(si)].name,
            ))

    # ── Shadbala (from export) ───────────────────────────────────
    sb_raw = raw.get("shadbala", {})
    for pname, sb in sb_raw.items():
        pname = pname.upper()
        p_enum = _planet_enum(pname)
        min_req = SHADBALA_MINIMUMS.get(p_enum, 5.0) if p_enum else 5.0

        sbp = ShadbalaPlanet(
            planet=pname,
            sthana_bala=float(sb.get("sthana", sb.get("sthana_bala", 0))),
            dig_bala=float(sb.get("dig", sb.get("dig_bala", 0))),
            kala_bala=float(sb.get("kala", sb.get("kala_bala", 0))),
            cheshta_bala=float(sb.get("cheshta", sb.get("cheshta_bala", 0))),
            naisargika_bala=float(sb.get("naisargika", sb.get("naisargika_bala", 0))),
            drik_bala=float(sb.get("drik", sb.get("drik_bala", 0))),
            minimum_required=min_req,
        )
        sbp.compute()
        chart.shadbala[pname] = sbp

    # ── Bhavabala (from export) ──────────────────────────────────
    bb_raw = raw.get("bhavabala", {})
    for house_key, bb in bb_raw.items():
        hn = int(house_key)
        bhs = BhavaStrength(
            house_num=hn,
            bhavadhipati_bala=float(bb.get("bhavadhipati", bb.get("lord_strength", 0))),
            bhava_dig_bala=float(bb.get("dig_bala", bb.get("bhava_dig", 0))),
            bhava_drishti_bala=float(bb.get("drishti", bb.get("aspect_strength", 0))),
        )
        bhs.compute()
        chart.bhavabala.append(bhs)

    # ── Ashtakvarga (from export) ────────────────────────────────
    av_raw = raw.get("ashtakvarga", {})
    if av_raw:
        av = AshtakavargaData()
        if "bhinna" in av_raw:
            av.bhinna = {k.upper(): v for k, v in av_raw["bhinna"].items()}
        if "sarva" in av_raw:
            sarva = av_raw["sarva"]
            if isinstance(sarva, dict):
                for s, v in sarva.items():
                    idx = _sign_index(s)
                    if 0 <= idx < 12:
                        av.sarva[idx] = int(v)
            elif isinstance(sarva, list):
                av.sarva = [int(x) for x in sarva[:12]]
        chart.ashtakvarga = av

    # ── Vimshottari Dasha (from export or compute) ───────────────
    vd_raw = raw.get("vimshottari", raw.get("dasha", []))
    chart.vimshottari = _parse_dasha_list(vd_raw, level=1)

    return chart


def _parse_dasha_list(raw_list: Any, level: int = 1) -> list:
    """Recursively parse dasha period lists."""
    periods = []
    if not isinstance(raw_list, list):
        return periods
    for item in raw_list:
        planet = item.get("planet", item.get("lord", ""))
        start = _parse_date(item.get("start", item.get("start_date", "")))
        end = _parse_date(item.get("end", item.get("end_date", "")))
        dur = float(item.get("duration_years", item.get("years", 0)))
        dp = DashaPeriod(
            planet=planet.upper(),
            start_date=start or datetime(1900, 1, 1),
            end_date=end or datetime(1900, 1, 1),
            duration_years=dur,
            level=level,
        )
        sub_key = "antardashas" if level == 1 else ("pratyantardashas" if level == 2 else "sub")
        sub_raw = item.get(sub_key, item.get("sub_periods", []))
        dp.sub_periods = _parse_dasha_list(sub_raw, level=level + 1)
        periods.append(dp)
    return periods


def _parse_date(val: Any) -> Optional[datetime]:
    if not val:
        return None
    if isinstance(val, datetime):
        return val
    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
        try:
            return datetime.strptime(str(val), fmt)
        except ValueError:
            pass
    return None


def load_sample_chart() -> VedicChart:
    """
    Load the known chart data from astrology_system_analysis.md.
    Used for development/testing without a JSON export file.
    Birth: Gemini Lagna, exact birth data (see analysis doc).
    """
    sample = {
        "birth_info": {
            "name": "Chart Subject",
            "date": "1994-02-27",        # approximate from dasha balance calcs
            "time": "06:30:00",
            "place": "India",
            "latitude": 20.5937,
            "longitude": 78.9629,
            "timezone": 5.5,
            "ayanamsa": 23.5,
            "ayanamsa_model": "Lahiri",
        },
        "lagna": {"sign": "Gemini", "degree": "01:46:00"},
        "planets": {
            "SUN":     {"sign": "Sagittarius", "degree_in_sign": "00:33:00", "retrograde": False},
            "MOON":    {"sign": "Aries",        "degree_in_sign": "24:14:18", "retrograde": False},
            "MARS":    {"sign": "Libra",        "degree_in_sign": "15:47:00", "retrograde": False},
            "MERCURY": {"sign": "Sagittarius",  "degree_in_sign": "17:43:00", "retrograde": False},
            "JUPITER": {"sign": "Cancer",       "degree_in_sign": "23:58:00", "retrograde": True},
            "VENUS":   {"sign": "Libra",        "degree_in_sign": "16:45:00", "retrograde": False},
            "SATURN":  {"sign": "Gemini",       "degree_in_sign": "01:46:00", "retrograde": True},
            "RAHU":    {"sign": "Taurus",       "degree_in_sign": "15:00:00", "retrograde": True},
            "KETU":    {"sign": "Scorpio",      "degree_in_sign": "15:00:00", "retrograde": True},
        },
        "shadbala": {
            "SUN":     {"sthana": 226.85, "dig": 24.17, "kala": 37.21, "cheshta": 1.85, "naisargika": 60.00, "drik": 9.30},
            "MOON":    {"sthana": 199.58, "dig": 12.06, "kala": 196.68,"cheshta": 47.89,"naisargika": 51.42,"drik": -3.61},
            "MARS":    {"sthana": 160.93, "dig": 9.24,  "kala": 89.14, "cheshta": 17.36,"naisargika": 17.16,"drik": 15.74},
            "MERCURY": {"sthana": 164.09, "dig": 2.65,  "kala": 191.27,"cheshta": 25.65,"naisargika": 25.74,"drik": 4.13},
            "JUPITER": {"sthana": 213.05, "dig": 50.57, "kala": 181.89,"cheshta": 43.16,"naisargika": 34.26,"drik": -10.26},
            "VENUS":   {"sthana": 147.21, "dig": 50.43, "kala": 98.13, "cheshta": 42.85,"naisargika": 42.84,"drik": 16.83},
            "SATURN":  {"sthana": 145.17, "dig": 7.96,  "kala": 48.11, "cheshta": 58.77,"naisargika": 8.58, "drik": -24.56},
        },
        "ashtakvarga": {
            "sarva": [33, 28, 30, 25, 33, 30, 30, 27, 22, 22, 32, 25],  # Aries...Pisces
        },
    }
    return load_from_dict(sample)
