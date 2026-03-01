"""
Lunation Engine — Moon Phase & Eclipse Alert System.

Tier-1: Swiss Ephemeris (pyswisseph) — sub-arcsecond accuracy, SWE ayanamsa.
Tier-2: PyEphem fallback — accurate to <0.01° if SWE unavailable.

Classical Vedic teaching:
  - New Moon (Amavasya) in 12th/8th/6th from natal Moon → extra caution
  - Full Moon (Purnima) on natal Moon nakshatra → heightened emotional/health sensitivity
  - Eclipse near natal planet → that planet's domains activated/disrupted for 6 months
  - Eclipse near natal Rahu/Ketu axis → major life turning point
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import math

# ─── Swiss Ephemeris tier-1 ───────────────────────────────────────────────────

_SWE_LUNATION_AVAILABLE = False
try:
    from vedic_engine.core.swisseph_bridge import (
        compute_next_new_moon_jd,
        compute_next_full_moon_jd,
        get_sidereal_longitude_at,
        datetime_to_jd_utc,
        jd_to_datetime,
        get_ayanamsa,
    )
    import swisseph as _swe
    _SWE_LUNATION_AVAILABLE = True
except ImportError:
    pass

# PyEphem tier-2 fallback
_EPHEM_AVAILABLE = False
try:
    import ephem
    _EPHEM_AVAILABLE = True
except ImportError:
    pass

# ─── Nakshatra lookup ─────────────────────────────────────────────────────────
_NAKSHATRA_SPAN = 360.0 / 27  # 13.333°

_NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

_NAKSHATRA_LORDS = [
    "KETU", "VENUS", "SUN", "MOON", "MARS",
    "RAHU", "JUPITER", "SATURN", "MERCURY", "KETU",
    "VENUS", "SUN", "MOON", "MARS", "RAHU",
    "JUPITER", "SATURN", "MERCURY", "KETU", "VENUS",
    "SUN", "MOON", "MARS", "RAHU", "JUPITER",
    "SATURN", "MERCURY",
]

# ─── Lahiri ayanamsa ──────────────────────────────────────────────────────────

def _lahiri_ayanamsa(dt: datetime) -> float:
    """Tier-2 fallback: linear Lahiri approximation (used only if SWE unavailable)."""
    days = (dt - datetime(2000, 1, 1, 12)).total_seconds() / 86400.0
    return 23.85 + days * (50.288 / (3600.0 * 365.25))


def _ephem_to_sidereal(tropical_deg: float, dt: datetime) -> float:
    """Convert tropical ecliptic longitude to Lahiri sidereal (tier-2 only)."""
    return (tropical_deg - _lahiri_ayanamsa(dt)) % 360.0


def _ephem_date_to_dt(ephem_date) -> datetime:
    """Convert ephem.Date to Python datetime (UTC). Tier-2 only."""
    tup = ephem_date.tuple()
    yr, mo, d = int(tup[0]), int(tup[1]), int(tup[2])
    frac_days = tup[2] - d
    hours = int(frac_days * 24)
    mins = int((frac_days * 24 - hours) * 60)
    secs = int(((frac_days * 24 - hours) * 60 - mins) * 60)
    return datetime(yr, mo, d, hours, mins, secs)


def _moon_longitude_at(dt: datetime) -> float:
    """Sidereal Moon longitude — SWE tier-1, PyEphem tier-2."""
    if _SWE_LUNATION_AVAILABLE:
        jd = datetime_to_jd_utc(dt)
        return get_sidereal_longitude_at(jd, _swe.MOON)
    if _EPHEM_AVAILABLE:
        m = ephem.Moon(dt)
        ecl_lon = math.degrees(float(m.hlong))
        return _ephem_to_sidereal(ecl_lon, dt)
    return 0.0


def _sun_longitude_at(dt: datetime) -> float:
    """Sidereal Sun longitude — SWE tier-1, PyEphem tier-2."""
    if _SWE_LUNATION_AVAILABLE:
        jd = datetime_to_jd_utc(dt)
        return get_sidereal_longitude_at(jd, _swe.SUN)
    if _EPHEM_AVAILABLE:
        s = ephem.Sun(dt)
        ecl_lon = math.degrees(float(s.hlong))
        return _ephem_to_sidereal(ecl_lon, dt)
    return 0.0


def _nakshatra_of(lon: float) -> int:
    """Return nakshatra index (0-26) for a sidereal longitude."""
    return int(lon / _NAKSHATRA_SPAN) % 27


def _tithi_of(moon_lon: float, sun_lon: float) -> int:
    """Return Tithi number (1-30). Tithi = every 12° Moon ahead of Sun."""
    diff = (moon_lon - sun_lon) % 360.0
    return int(diff / 12.0) + 1  # 1=Pratipad to 30=Amavasya


def _angular_distance(a: float, b: float) -> float:
    """Shortest angular distance between two ecliptic longitudes."""
    d = abs(a - b) % 360.0
    return d if d <= 180.0 else 360.0 - d


# ─── Eclipse detection ────────────────────────────────────────────────────────

def _check_eclipse(moon_lon: float, sun_lon: float,
                   is_full: bool, rahu_lon: float) -> Optional[str]:
    """
    Detect eclipse type.
    - Solar eclipse: new moon (sun ≈ moon) when Moon near Rahu/Ketu axis (within 18°)
    - Lunar eclipse: full moon when Moon near Rahu/Ketu axis (within 12°)

    Returns: "Solar", "Lunar", "Penumbral", or None
    """
    ketu_lon = (rahu_lon + 180.0) % 360.0
    moon_to_rahu  = _angular_distance(moon_lon, rahu_lon)
    moon_to_ketu  = _angular_distance(moon_lon, ketu_lon)
    node_distance = min(moon_to_rahu, moon_to_ketu)

    if not is_full:  # New Moon = potential Solar eclipse
        if node_distance <= 18.0:
            return "Solar" if node_distance <= 12.0 else "Partial Solar"
    else:            # Full Moon = potential Lunar eclipse
        if node_distance <= 12.0:
            return "Lunar" if node_distance <= 9.0 else "Penumbral Lunar"
    return None


# ─── Natal planet proximity ───────────────────────────────────────────────────

def _near_natal_planets(
        moon_lon: float,
        natal_lons: Dict[str, float],
        orb: float = 7.0,
) -> List[str]:
    """Return list of natal planets within 'orb' degrees of current Moon longitude."""
    hits = []
    for pname, nlon in natal_lons.items():
        if _angular_distance(moon_lon, nlon) <= orb:
            hits.append(pname)
    return hits


def _lunation_significance(
        is_full: bool,
        eclipse: Optional[str],
        nak_same_as_natal_moon: bool,
        nak_same_as_natal_lagna: bool,
        near_natal: List[str],
        from_natal_moon: int,
        tithi: int,
) -> float:
    """
    Significance score (0.0 – 1.0) for a lunation.
    Higher = more important for prediction.
    """
    score = 0.3  # baseline

    if eclipse:
        score += 0.5 if "Solar" in eclipse or "Lunar" in eclipse else 0.3
    if nak_same_as_natal_moon:
        score += 0.25
    if nak_same_as_natal_lagna:
        score += 0.15
    if near_natal:
        score += min(0.2, len(near_natal) * 0.07)
    # From natal Moon: 12th/8th/6th = stress, 1st/5th/9th = good
    if from_natal_moon in (12, 8, 6):
        score += 0.1 if not is_full else 0.05
    if from_natal_moon in (1, 5, 9, 11):
        score += 0.08
    # Amavasya and Purnima get baseline boost
    if tithi in (15, 30):
        score += 0.05

    return min(1.0, score)


# ─── Domain impact ────────────────────────────────────────────────────────────

_HOUSE_FROM_MOON_IMPACT: Dict[int, str] = {
    1:  "Self/health — heightened sensitivity, mind active",
    2:  "Finance/family — impulse spending, family dynamics",
    3:  "Effort/siblings — good for courageous action",
    4:  "Home/mother — emotional needs at home",
    5:  "Creativity/children — good for creativity, romance",
    6:  "Enemies/debt — conflict possible, health caution",
    7:  "Partnership — relationships highlighted",
    8:  "Obstacles/transformation — caution for health, avoid risks",
    9:  "Luck/dharma — travel, spiritual insight favoured",
    10: "Career/status — public visibility, work activity",
    11: "Gains/network — income, social connections open",
    12: "Loss/foreign — expenses, introspection, isolation risk",
}

_ECLIPSE_PLANET_IMPACT: Dict[str, str] = {
    "SUN":     "Ego, authority, government — career matters disrupted/reset for 6 months",
    "MOON":    "Mind, mother, home — emotional upheaval, health sensitivity",
    "MARS":    "Courage, land, siblings — conflict or injury risk, energy redirected",
    "MERCURY": "Communication, business, intellect — deals/plans may reverse",
    "JUPITER": "Wealth, guru, children, dharma — major philosophical/financial shift",
    "VENUS":   "Relationships, luxury, creativity — partnerships recalibrated",
    "SATURN":  "Karma, career, discipline — long-term structural change begins",
    "RAHU":    "Desires, foreign, technology — sudden worldly ambition activated",
    "KETU":    "Spirituality, detachment, past karma — release, moksha themes",
}


# ─── Main functions ───────────────────────────────────────────────────────────

def compute_upcoming_lunations(
        on_date: datetime,
        natal_lons: Dict[str, float],
        rahu_lon: float,                  # natal Rahu longitude
        months_ahead: int = 12,
) -> List[Dict]:
    """
    Compute all new moons and full moons for the next `months_ahead` months.

    Returns list of dicts sorted by date, each containing:
      date, type, moon_lon_sidereal, nakshatra, nakshatra_lord, tithi,
      from_natal_moon_house, eclipse, near_natal_planets,
      significance, impact_text
    """
    # Derive natal Moon sign from natal_lons
    natal_moon_lon = natal_lons.get("MOON", 0.0)
    natal_moon_sign = int(natal_moon_lon / 30.0)   # 0-11
    natal_moon_nak  = _nakshatra_of(natal_moon_lon)
    natal_lagna_lon = natal_lons.get("LAGNA", natal_lons.get("ASC", 0.0))
    natal_lagna_nak = _nakshatra_of(natal_lagna_lon) if natal_lagna_lon else -1

    results: List[Dict] = []
    cutoff = on_date + timedelta(days=months_ahead * 30.44)

    # ── Walk through new and full moons using tiered backend ──
    if _SWE_LUNATION_AVAILABLE:
        # Tier-1: Swiss Ephemeris Newton-Raphson lunation search
        jd_cur = datetime_to_jd_utc(on_date)
        jd_end = datetime_to_jd_utc(cutoff)
        while jd_cur < jd_end:
            jd_nm = compute_next_new_moon_jd(jd_cur)
            jd_fm = compute_next_full_moon_jd(jd_cur)
            for jd_ev, is_full in [(jd_nm, False), (jd_fm, True)]:
                if jd_ev > jd_end:
                    continue
                dt = jd_to_datetime(jd_ev)
                if dt < on_date:
                    continue
                moon_lon = _moon_longitude_at(dt)
                sun_lon = _sun_longitude_at(dt)
                tithi = _tithi_of(moon_lon, sun_lon)
                nak_idx = _nakshatra_of(moon_lon)
                moon_sign = int(moon_lon / 30.0)
                from_moon = ((moon_sign - natal_moon_sign) % 12) + 1
                eclipse = _check_eclipse(moon_lon, sun_lon, is_full, rahu_lon)
                near_natal = _near_natal_planets(moon_lon, natal_lons)
                sig = _lunation_significance(
                    is_full, eclipse, nak_idx == natal_moon_nak,
                    nak_idx == natal_lagna_nak, near_natal, from_moon, tithi,
                )
                impact = _HOUSE_FROM_MOON_IMPACT.get(from_moon, "")
                if eclipse and near_natal:
                    eclipse_impacts = [_ECLIPSE_PLANET_IMPACT.get(p, "") for p in near_natal]
                    impact = f"ECLIPSE near natal {', '.join(near_natal)} — " + "; ".join(e for e in eclipse_impacts if e)
                elif eclipse:
                    impact = "ECLIPSE — general disruption/reset in all domains"
                results.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "type": "Full Moon" if is_full else "New Moon",
                    "phase": "Purnima" if is_full else "Amavasya",
                    "moon_lon": round(moon_lon, 3),
                    "nakshatra": _NAKSHATRA_NAMES[nak_idx],
                    "nakshatra_lord": _NAKSHATRA_LORDS[nak_idx],
                    "tithi": tithi,
                    "from_natal_moon_house": from_moon,
                    "eclipse": eclipse,
                    "near_natal_planets": near_natal,
                    "significance": round(sig, 3),
                    "impact": impact,
                })
            jd_cur = min(jd_nm, jd_fm) + 1.0  # advance ~1 day past event

    elif _EPHEM_AVAILABLE:
        # Tier-2: PyEphem
        cur = ephem.Date(on_date)
        for _ in range(months_ahead * 2 + 4):
            nm_date = ephem.next_new_moon(cur)
            fm_date = ephem.next_full_moon(cur)
            for (ephem_dt, is_full) in [(nm_date, False), (fm_date, True)]:
                dt = _ephem_date_to_dt(ephem_dt)
                if dt > cutoff or dt < on_date:
                    continue
                moon_lon = _moon_longitude_at(dt)
                sun_lon = _sun_longitude_at(dt)
                tithi = _tithi_of(moon_lon, sun_lon)
                nak_idx = _nakshatra_of(moon_lon)
                moon_sign = int(moon_lon / 30.0)
                from_moon = ((moon_sign - natal_moon_sign) % 12) + 1
                eclipse = _check_eclipse(moon_lon, sun_lon, is_full, rahu_lon)
                near_natal = _near_natal_planets(moon_lon, natal_lons)
                sig = _lunation_significance(
                    is_full, eclipse, nak_idx == natal_moon_nak,
                    nak_idx == natal_lagna_nak, near_natal, from_moon, tithi,
                )
                impact = _HOUSE_FROM_MOON_IMPACT.get(from_moon, "")
                if eclipse and near_natal:
                    eclipse_impacts = [_ECLIPSE_PLANET_IMPACT.get(p, "") for p in near_natal]
                    impact = f"ECLIPSE near natal {', '.join(near_natal)} — " + "; ".join(e for e in eclipse_impacts if e)
                elif eclipse:
                    impact = "ECLIPSE — general disruption/reset in all domains"
                results.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "type": "Full Moon" if is_full else "New Moon",
                    "phase": "Purnima" if is_full else "Amavasya",
                    "moon_lon": round(moon_lon, 3),
                    "nakshatra": _NAKSHATRA_NAMES[nak_idx],
                    "nakshatra_lord": _NAKSHATRA_LORDS[nak_idx],
                    "tithi": tithi,
                    "from_natal_moon_house": from_moon,
                    "eclipse": eclipse,
                    "near_natal_planets": near_natal,
                    "significance": round(sig, 3),
                    "impact": impact,
                })
            cur = min(nm_date, fm_date) + ephem.Date(1)

    # Sort by date and deduplicate
    results.sort(key=lambda x: x["date"])
    seen = set()
    unique = []
    for r in results:
        key = (r["date"], r["type"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


def get_eclipse_alerts(lunations: List[Dict]) -> List[Dict]:
    """Filter and return only eclipses from the lunation list."""
    return [l for l in lunations if l.get("eclipse")]


def get_high_significance_lunations(
        lunations: List[Dict], threshold: float = 0.65
) -> List[Dict]:
    """Return lunations above significance threshold."""
    return [l for l in lunations if l["significance"] >= threshold]
