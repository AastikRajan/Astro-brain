"""
Vimshottari Dasha Engine.
Computes the complete dasha timeline from birth to any depth.

Core formulas from deep-research-report.md:
  Balance = (remaining_arc_in_nak / nakshatra_span) × mahadasha_years
  Antardasha duration = (Maha_years × Antar_years) / 120
  Deeper levels: same proportional multiplication.

Cycle: Ketu(7) → Venus(20) → Sun(6) → Moon(10) → Mars(7) →
       Rahu(18) → Jupiter(16) → Saturn(19) → Mercury(17)  = 120 years
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

from vedic_engine.config import (
    Planet, VIMSHOTTARI_SEQUENCE, VIMSHOTTARI_YEARS,
    VIMSHOTTARI_TOTAL, NAKSHATRA_SPAN,
)
from vedic_engine.core.coordinates import nakshatra_of

PLANET_LABELS = {p.name: p for p in Planet}
DAYS_PER_YEAR = 365.25


def _years_to_days(years: float) -> int:
    return int(years * DAYS_PER_YEAR)


def _birth_dasha_balance(moon_longitude: float) -> Tuple[Planet, float]:
    """
    Determine the starting (first) Mahadasha planet and remaining years at birth.
    Algorithm:
      1. Find nakshatra of Moon (0-26).
      2. Get nakshatra lord (Vimshottari sequence mod 9).
      3. Compute fraction of nakshatra remaining: remaining_arc / 13.333°
      4. Balance = lord's dasha years × fraction.
    """
    nak_idx = nakshatra_of(moon_longitude)
    lord_idx = nak_idx % 9
    lord = VIMSHOTTARI_SEQUENCE[lord_idx]

    pos_in_nak = moon_longitude % NAKSHATRA_SPAN
    remaining_arc = NAKSHATRA_SPAN - pos_in_nak
    fraction = remaining_arc / NAKSHATRA_SPAN
    balance = VIMSHOTTARI_YEARS[lord] * fraction

    return lord, balance


def _dasha_sequence_from(start_planet: Planet) -> List[Planet]:
    """Get the dasha sequence starting from a given planet."""
    idx = VIMSHOTTARI_SEQUENCE.index(start_planet)
    return [VIMSHOTTARI_SEQUENCE[(idx + i) % 9] for i in range(9)]


def compute_mahadasha_periods(
        moon_longitude: float,
        birth_date: datetime,
        levels: int = 3,   # 1=Maha only, 2=+Antar, 3=+Pratyantar, 4=+Sukshma, 5=+Prana
) -> List[dict]:
    """
    Compute Vimshottari Dasha timeline up to `levels` depth.

    Level depth names (classic sub-divisions):
      1 = Mahadasha           (years)
      2 = Antardasha / Bhukti (months)
      3 = Pratyantar Dasha    (weeks)
      4 = Sukshma Dasha       (days)   — needs birth time accurate to minutes
      5 = Prana Dasha         (hours)  — needs birth time accurate to seconds

    Formula for each sub-level:
      duration = parent_duration × planet_years / 120
    """
    """
    Compute Vimshottari Dasha timeline.
    Returns list of Mahadasha periods, each with nested sub-periods.
    """
    start_planet, balance_years = _birth_dasha_balance(moon_longitude)
    sequence = _dasha_sequence_from(start_planet)

    current_date = birth_date
    periods = []

    for i, maha_planet in enumerate(sequence):
        duration = balance_years if i == 0 else float(VIMSHOTTARI_YEARS[maha_planet])
        end_date = current_date + timedelta(days=_years_to_days(duration))

        maha = {
            "level": 1,
            "planet": maha_planet.name,
            "start": current_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(duration, 4),
            "sub_periods": [],
        }

        if levels >= 2:
            maha["sub_periods"] = _compute_sub_periods(
                maha_planet, duration, current_date, levels
            )

        periods.append(maha)
        current_date = end_date

        # After balance period, run full remaining cycles
        if i == 0 and balance_years < VIMSHOTTARI_YEARS[start_planet]:
            # First period was partial; next cycles are full
            pass

    # Run the remaining 8 full cycles (total = 9 planets × full years + balance)
    # The above loop only gives one cycle. Add remaining cycles up to ~120yr.
    # Extend to cover at least 120 years total lifespan
    total_days = sum(_years_to_days(d["duration_years"]) for d in periods)
    while total_days < _years_to_days(120):
        for maha_planet in sequence:
            duration = float(VIMSHOTTARI_YEARS[maha_planet])
            end_date = current_date + timedelta(days=_years_to_days(duration))
            maha = {
                "level": 1,
                "planet": maha_planet.name,
                "start": current_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "duration_years": duration,
                "sub_periods": [],
            }
            if levels >= 2:
                maha["sub_periods"] = _compute_sub_periods(
                    maha_planet, duration, current_date, levels
                )
            periods.append(maha)
            current_date = end_date
            total_days += _years_to_days(duration)
            if total_days >= _years_to_days(120):
                break

    return periods


def _compute_sub_periods(
        maha_planet: Planet,
        maha_duration: float,
        maha_start: datetime,
        max_level: int,
        current_level: int = 2,
) -> List[dict]:
    """Recursively compute sub-periods (Antar, Pratyantar, Sookshma)."""
    if current_level > max_level:
        return []

    sequence = _dasha_sequence_from(maha_planet)
    current_date = maha_start
    sub_periods = []

    for antar_planet in sequence:
        # Antardasha duration = (MahaDuration × AntarYears) / 120
        duration = (maha_duration * VIMSHOTTARI_YEARS[antar_planet]) / VIMSHOTTARI_TOTAL
        end_date = current_date + timedelta(days=_years_to_days(duration))

        sub = {
            "level": current_level,
            "planet": antar_planet.name,
            "start": current_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(duration, 5),
            "sub_periods": [],
        }

        if current_level < max_level:
            sub["sub_periods"] = _compute_sub_periods(
                antar_planet, duration, current_date, max_level, current_level + 1
            )

        sub_periods.append(sub)
        current_date = end_date

    return sub_periods


def get_active_dasha(periods: List[dict], on_date: Optional[datetime] = None) -> dict:
    """
    Find the active dasha period (at any level) for a given date.
    Returns nested dict with maha, antar, pratyantar.
    """
    if on_date is None:
        on_date = datetime.now()

    def _find_active(plist, date):
        for p in plist:
            s = datetime.strptime(p["start"], "%Y-%m-%d")
            e = datetime.strptime(p["end"], "%Y-%m-%d")
            if s <= date < e:
                return p
        return None

    maha = _find_active(periods, on_date)
    if not maha:
        return {}

    result = {"mahadasha": maha["planet"]}
    antar = _find_active(maha.get("sub_periods", []), on_date)
    if antar:
        result["antardasha"] = antar["planet"]
        prat = _find_active(antar.get("sub_periods", []), on_date)
        if prat:
            result["pratyantardasha"] = prat["planet"]

    return result


def dasha_details_on_date(
        moon_longitude: float,
        birth_date: datetime,
        on_date: Optional[datetime] = None,
        levels: int = 3,
) -> dict:
    """High-level: compute full timeline and return active period on given date."""
    if on_date is None:
        on_date = datetime.now()
    periods = compute_mahadasha_periods(moon_longitude, birth_date, levels)
    active = get_active_dasha(periods, on_date)
    # Sukshma (level-4) and Prana (level-5) are included when levels>=4/5
    sukshma = None
    prana = None
    if levels >= 4 or levels >= 5:
        maha = next((p for p in periods if
                     datetime.strptime(p['start'], '%Y-%m-%d') <= on_date <
                     datetime.strptime(p['end'], '%Y-%m-%d')), None)
        if maha:
            antar = next((s for s in maha.get('sub_periods', []) if
                          datetime.strptime(s['start'], '%Y-%m-%d') <= on_date <
                          datetime.strptime(s['end'], '%Y-%m-%d')), None)
            if antar:
                prat = next((s for s in antar.get('sub_periods', []) if
                             datetime.strptime(s['start'], '%Y-%m-%d') <= on_date <
                             datetime.strptime(s['end'], '%Y-%m-%d')), None)
                if prat:
                    sk = next((s for s in prat.get('sub_periods', []) if
                               datetime.strptime(s['start'], '%Y-%m-%d') <= on_date <
                               datetime.strptime(s['end'], '%Y-%m-%d')), None)
                    if sk:
                        sukshma = sk.get('planet')
                        pr = next((s for s in sk.get('sub_periods', []) if
                                   datetime.strptime(s['start'], '%Y-%m-%d') <= on_date <
                                   datetime.strptime(s['end'], '%Y-%m-%d')), None)
                        if pr:
                            prana = pr.get('planet')
    if sukshma:
        active['sukshma'] = sukshma
    if prana:
        active['prana'] = prana
    return {'active': active, 'all_periods': periods}


def detect_dasha_sandhi(
        periods: list,
        on_date: Optional[datetime] = None,
        sandhi_days: int = 10,
) -> dict:
    """
    Dasha Sandhi (junction) detection.

    A Sandhi period occurs in the last/first 'sandhi_days' days of a Mahadasha
    or Antardasha.  Results during Sandhi are considered unpredictable — the
    native is "between two worlds" and the outgoing planet's energy fades while
    the incoming planet's energy has not yet crystallised.

    Returns:
        {
          "in_sandhi": bool,
          "level": "maha" | "antar" | None,
          "transition_from": str,   # planet whose period is ending
          "transition_to": str,     # planet whose period is starting
          "boundary_date": str,     # ISO date of the transition
          "days_to_boundary": int,  # negative = days SINCE boundary (first days)
          "phase": "closing" | "opening",
        }
    """
    if on_date is None:
        on_date = datetime.now()

    def _parse(d: str) -> datetime:
        return datetime.strptime(d[:10], "%Y-%m-%d")

    def _check_boundary(curr_period: dict, prev_planet: Optional[str], level: str) -> Optional[dict]:
        s = _parse(curr_period["start"])
        e = _parse(curr_period["end"])
        days_from_start = (on_date - s).days
        days_to_end = (e - on_date).days

        # Opening sandhi: first sandhi_days of this period
        if 0 <= days_from_start <= sandhi_days and prev_planet:
            return {
                "in_sandhi": True,
                "level": level,
                "transition_from": prev_planet,
                "transition_to": curr_period["planet"],
                "boundary_date": s.strftime("%Y-%m-%d"),
                "days_to_boundary": -days_from_start,
                "phase": "opening",
            }
        # Closing sandhi: last sandhi_days of this period
        if 0 <= days_to_end <= sandhi_days:
            return {
                "in_sandhi": True,
                "level": level,
                "transition_from": curr_period["planet"],
                "transition_to": "?",   # next period unknown without look-ahead
                "boundary_date": e.strftime("%Y-%m-%d"),
                "days_to_boundary": days_to_end,
                "phase": "closing",
            }
        return None

    # ── Check Mahadasha level ────────────────────────────────────────
    prev_maha: Optional[str] = None
    active_maha: Optional[dict] = None
    for mp in periods:
        s = _parse(mp["start"])
        e = _parse(mp["end"])
        if s <= on_date < e:
            active_maha = mp
            break
        prev_maha = mp["planet"]

    if active_maha is None:
        return {"in_sandhi": False}

    result = _check_boundary(active_maha, prev_maha, "maha")
    if result:
        # Patch transition_to from next period when closing
        if result["phase"] == "closing":
            idx = periods.index(active_maha)
            if idx + 1 < len(periods):
                result["transition_to"] = periods[idx + 1]["planet"]
        return result

    # ── Check Antardasha level ───────────────────────────────────────
    sub_periods = active_maha.get("sub_periods", [])
    prev_antar: Optional[str] = None
    for sp in sub_periods:
        s = _parse(sp["start"])
        e = _parse(sp["end"])
        if s <= on_date < e:
            result = _check_boundary(sp, prev_antar, "antar")
            if result:
                if result["phase"] == "closing":
                    idx = sub_periods.index(sp)
                    if idx + 1 < len(sub_periods):
                        result["transition_to"] = sub_periods[idx + 1]["planet"]
                return result
            break
        prev_antar = sp["planet"]

    return {"in_sandhi": False}

# ─── Vimshottari 6-Factor Diagnostic Matrix ────────────────────────────────

_NATURAL_BENEFICS = {"MOON", "MERCURY", "JUPITER", "VENUS"}
_NATURAL_MALEFICS = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}
_KENDRA_H   = {1, 4, 7, 10}
_TRIKONA_H  = {1, 5, 9}
_DUSTHANA_H = {6, 8, 12}

_COMBUSTION_ORBS = {
    "MOON": 12.0, "MARS": 17.0, "MERCURY": 14.0,
    "JUPITER": 11.0, "VENUS": 10.0, "SATURN": 15.0,
}

_NATURAL_ENEMIES: dict = {
    "SUN":     {"SATURN", "VENUS"},
    "MOON":    {"MARS", "SATURN"},
    "MARS":    {"MERCURY"},
    "MERCURY": {"MOON"},
    "JUPITER": {"MERCURY", "VENUS"},
    "VENUS":   {"SUN", "MOON"},
    "SATURN":  {"SUN", "MOON", "MARS"},
    "RAHU":    {"SUN", "MOON"},
    "KETU":    {"SUN", "MOON"},
}
_NATURAL_FRIENDS_D: dict = {
    "SUN":     {"MOON", "MARS", "JUPITER"},
    "MOON":    {"SUN", "MERCURY"},
    "MARS":    {"SUN", "MOON", "JUPITER"},
    "MERCURY": {"SUN", "VENUS"},
    "JUPITER": {"SUN", "MOON", "MARS"},
    "VENUS":   {"MERCURY", "SATURN"},
    "SATURN":  {"MERCURY", "VENUS"},
    "RAHU":    {"MERCURY", "SATURN", "VENUS"},
    "KETU":    {"MARS", "VENUS", "SATURN"},
}


def dasha_diagnostic_matrix(
    dasha_planet: str,
    antardasha_planet: str,
    planet_houses: dict,
    planet_lons: dict,
    house_lords: dict,
    shadbala_ratios: dict,
    lagna_lord: str,
    retrograde_planets: list = None,
    vargas: dict = None,
) -> dict:
    """
    Vimshottari 6-Factor Diagnostic Matrix (Research Brief, Block 3A).

    Factor 1: House + Lordship
    Factor 2: Dual Nature Rule (natural benefic owning dusthana = troublemaker)
    Factor 3: Lagna Lord relationship
    Factor 4: Dignity in D1 (quantity) + D9 (quality/sustainability)
    Factor 5: Combustion penalty
    Factor 6: Retrogression
    + MD/AD Geometry: AD in 6/8/12 from MD → friction; kendra/trikona → boost
    """
    retrograde_set = set(retrograde_planets or [])
    sun_lon = planet_lons.get("SUN", 0)

    def _is_combust(p: str) -> bool:
        if p in ("SUN", "RAHU", "KETU") or p not in planet_lons:
            return False
        orb = _COMBUSTION_ORBS.get(p, 10.0)
        p_lon = planet_lons[p]
        diff = abs(p_lon - sun_lon) % 360
        if diff > 180:
            diff = 360 - diff
        return diff < orb

    def _house_of(p: str) -> int:
        return planet_houses.get(p, 0)

    def _lorded_houses(p: str) -> list:
        return [h for h, lord in house_lords.items() if lord == p]

    def _is_trikona_lord(p: str) -> bool:
        return any(h in (1, 5, 9) for h in _lorded_houses(p))

    def _is_dusthana_lord(p: str) -> bool:
        return any(h in (6, 8, 12) for h in _lorded_houses(p))

    def _is_kendra_lord(p: str) -> bool:
        return any(h in (1, 4, 7, 10) for h in _lorded_houses(p))

    def _dignities(p: str) -> dict:
        h = _house_of(p)
        d1 = ("strong" if h in (_KENDRA_H | _TRIKONA_H) else
               "weak" if h in _DUSTHANA_H else "neutral")
        d9 = "unknown"
        if vargas:
            d9_data = vargas.get("D9", {})
            d9_lagna   = d9_data.get("lagna_sign", 0)
            d9_planets = d9_data.get("planet_signs", {})
            if p in d9_planets:
                d9_sign  = d9_planets[p]
                d9_house = (d9_sign - d9_lagna) % 12 + 1
                d9 = ("strong" if d9_house in (_KENDRA_H | _TRIKONA_H) else
                       "weak" if d9_house in _DUSTHANA_H else "neutral")
        return {"d1": d1, "d9": d9}

    # Factor 1
    if _is_trikona_lord(dasha_planet):
        f1_quality, f1_detail = "benefic", (
            f"{dasha_planet} lords trikona → benefic even if natural malefic; fortune-giving.")
    elif _is_dusthana_lord(dasha_planet) and not _is_trikona_lord(dasha_planet):
        f1_quality, f1_detail = "challenging", (
            f"{dasha_planet} lords dusthana (6/8/12) → obstacles, hidden enemies, transformative crises.")
    elif _is_kendra_lord(dasha_planet):
        f1_quality, f1_detail = "strong", (
            f"{dasha_planet} lords kendra → structural support, authority.")
    else:
        f1_quality, f1_detail = "neutral", f"{dasha_planet} lords neutral house."

    # Factor 2
    is_nat_ben = dasha_planet in _NATURAL_BENEFICS
    f2_quality, f2_detail = "neutral", ""
    if is_nat_ben and _is_dusthana_lord(dasha_planet):
        f2_quality = "troublemaker"
        f2_detail  = (f"{dasha_planet} natural benefic but dusthana lord → functional troublemaker; "
                      "pleasure-seeking undermines; over-expansion, hidden losses.")
    elif not is_nat_ben and _is_trikona_lord(dasha_planet):
        f2_quality = "reformed_malefic"
        f2_detail  = f"{dasha_planet} natural malefic + trikona lord → Raja Yoga karaka; fortune through effort."

    # Factor 3
    f3_quality, f3_detail = "neutral", ""
    if lagna_lord and dasha_planet:
        if dasha_planet in _NATURAL_FRIENDS_D.get(lagna_lord, set()):
            f3_quality = "smooth"
            f3_detail  = f"{dasha_planet} natural friend of Lagna lord {lagna_lord} → smooth period."
        elif dasha_planet in _NATURAL_ENEMIES.get(lagna_lord, set()):
            f3_quality = "friction"
            f3_detail  = f"{dasha_planet} enemy of Lagna lord {lagna_lord} → friction, health struggles."
        elif dasha_planet == lagna_lord:
            f3_quality = "identity"
            f3_detail  = f"{dasha_planet} IS Lagna lord → identity-defining period."

    # Factor 4
    md_dig = _dignities(dasha_planet)
    d1, d9 = md_dig["d1"], md_dig["d9"]
    if d1 == "strong" and d9 in ("strong", "unknown"):
        f4_quality, f4_detail = "sustained_excellence", (
            f"{dasha_planet} strong D1+D9 → grand, sustainable results.")
    elif d1 == "strong" and d9 == "weak":
        f4_quality, f4_detail = "grand_start_collapse", (
            f"{dasha_planet} strong D1 + weak D9 → spectacular start, eventual structural collapse.")
    elif d1 == "weak" and d9 == "strong":
        f4_quality, f4_detail = "delayed_recovery", (
            f"{dasha_planet} weak D1 + strong D9 → initial struggle, eventual qualitative recovery.")
    elif d1 == "weak" and d9 == "weak":
        f4_quality, f4_detail = "persistent_weakness", (
            f"{dasha_planet} weak in both D1 and D9 → persistently difficult dasha.")
    else:
        f4_quality, f4_detail = "neutral", f"{dasha_planet} neutral dignity."

    # Factor 5
    md_combust = _is_combust(dasha_planet)
    ad_combust = _is_combust(antardasha_planet)
    f5_quality = "burned" if md_combust else "clear"
    f5_detail  = (f"{dasha_planet} combust → domains drastically reduced, hidden, conflicted."
                  if md_combust else "")

    # Factor 6
    md_retro = dasha_planet in retrograde_set
    ad_retro  = antardasha_planet in retrograde_set
    if md_retro and dasha_planet in _NATURAL_BENEFICS:
        f6_quality = "retrograde_benefic_delayed_massive"
        f6_detail  = f"{dasha_planet} retrograde benefic → eventual massive results, but significantly delayed."
    elif md_retro:
        f6_quality = "retrograde_malefic_destabilizing"
        f6_detail  = f"{dasha_planet} retrograde malefic → exceptionally destabilizing; past karma resurfaces."
    else:
        f6_quality = "direct"
        f6_detail  = ""

    # MD/AD Geometry
    dasha_house      = _house_of(dasha_planet)
    antardasha_house = _house_of(antardasha_planet)
    md_ad_geometry = "neutral"
    md_ad_detail   = ""
    if dasha_house > 0 and antardasha_house > 0:
        ad_from_md = (antardasha_house - dasha_house) % 12 + 1
        if ad_from_md in (6, 8, 12):
            md_ad_geometry = f"friction_dusthana_{ad_from_md}th_from_MD"
            md_ad_detail   = (f"AD lord {antardasha_planet} is {ad_from_md}th from MD lord {dasha_planet} → "
                              "Shadashtaka/Ashtama friction: health, enmity, obstacles even if both benefics.")
        elif ad_from_md in (5, 9):
            md_ad_geometry = f"trikona_{ad_from_md}th_from_MD"
            md_ad_detail   = (f"AD lord {antardasha_planet} is {ad_from_md}th from MD lord {dasha_planet} → "
                              "Trikona: fortune-bearing, overrides MD negativity.")
        elif ad_from_md in (1, 4, 7, 10):
            md_ad_geometry = f"kendra_{ad_from_md}th_from_MD"
            md_ad_detail   = (f"AD lord {antardasha_planet} is {ad_from_md}th from MD lord {dasha_planet} → "
                              "Kendra: fruitful structural support.")

    # Overall quality
    pos = sum(1 for q in [f1_quality, f2_quality, f3_quality, f4_quality]
              if q in ("benefic", "strong", "smooth", "sustained_excellence",
                       "reformed_malefic", "identity", "delayed_recovery"))
    neg = sum(1 for q in [f1_quality, f2_quality, f3_quality, f4_quality, f5_quality, f6_quality]
              if q in ("challenging", "troublemaker", "friction", "burned",
                       "persistent_weakness", "grand_start_collapse",
                       "retrograde_malefic_destabilizing"))
    if "friction" in md_ad_geometry:
        neg += 1
    elif "kendra" in md_ad_geometry or "trikona" in md_ad_geometry:
        pos += 1

    overall_quality = ("beneficial" if pos > neg + 1 else
                       "challenging" if neg > pos + 1 else "mixed")

    summary = " | ".join(filter(None, [
        f1_detail, f3_detail, f4_detail, f5_detail, f6_detail, md_ad_detail
    ]))

    return {
        "dasha_planet":      dasha_planet,
        "antardasha_planet": antardasha_planet,
        "dasha_house":       dasha_house,
        "antardasha_house":  antardasha_house,
        "dasha_lord_combust":    md_combust,
        "dasha_lord_retrograde": md_retro,
        "ad_lord_combust":       ad_combust,
        "ad_lord_retrograde":    ad_retro,
        "overall_quality": overall_quality,
        "md_ad_geometry":  md_ad_geometry,
        "factors": {
            "1_house_lordship":      {"quality": f1_quality, "detail": f1_detail},
            "2_dual_nature":         {"quality": f2_quality, "detail": f2_detail},
            "3_lagna_lord_relation": {"quality": f3_quality, "detail": f3_detail},
            "4_dignity_d1_d9":       {"quality": f4_quality, "detail": f4_detail,
                                      "d1": d1, "d9": d9},
            "5_combustion":          {"quality": f5_quality, "detail": f5_detail,
                                      "combust": md_combust},
            "6_retrogression":       {"quality": f6_quality, "detail": f6_detail,
                                      "retrograde": md_retro},
            "md_ad_geometry":        {"quality": md_ad_geometry, "detail": md_ad_detail},
        },
        "summary": summary,
    }


# ─── Retrograde Dasha Lord Mechanics (Research Brief: Jyotish Logic) ────────

_NATURAL_BENEFIC_PLANETS = {"JUPITER", "VENUS", "MERCURY", "MOON"}
_NATURAL_MALEFIC_PLANETS  = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}

# Dignity classification for reversal logic
_EXALTED_SIGNS: Dict[str, int] = {
    "SUN": 0, "MOON": 1, "MARS": 9, "MERCURY": 5, "JUPITER": 3,
    "VENUS": 11, "SATURN": 6, "RAHU": 1, "KETU": 7,
}
_DEBILITATED_SIGNS: Dict[str, int] = {
    "SUN": 6, "MOON": 7, "MARS": 3, "MERCURY": 11, "JUPITER": 9,
    "VENUS": 5, "SATURN": 0, "RAHU": 7, "KETU": 1,
}


def analyze_retrograde_dasha_lord(
    dasha_planet: str,
    planet_longitude: float,     # natal longitude of dasha lord
    planet_house: int,           # natal house of dasha lord
    is_retrograde: bool,
    shadbala_ratio: float = 1.0,
    transit_is_retrograde: bool = False,   # current transit state of this planet
    transit_was_retrograde: bool = False,  # was it retrograde last check (for station detect)
    dasha_start_date: str = "",
    dasha_end_date: str = "",
) -> Dict:
    """
    Research Brief: Retrograde planet as Mahadasha lord — specific computational rules.

    Rule 1 — Previous house / sign effect:
      • Previous SIGN: Only Jupiter (per Kalaprakashika text).
      • Previous HOUSE: All planets, but ONLY if planet is in 0-10° of current sign.
        Beyond 10° → strictly gives current house results.

    Rule 2 — Dignity inversion:
      • Exalted + retrograde → behaves as DEBILITATED (sudden fall from grace,
        frustration despite high status).
      • Debilitated + retrograde → behaves as EXALTED (unexpected success via
        unconventional means).

    Rule 3 — Chesta Bala amplification:
      • Retrogression provides maximum Chesta Bala → planet is erratic, intense,
        unyielding. Functional benefic = resolute success via unconventional means.
        Functional malefic = violently firm in delivering negative results.

    Rule 4 — Chronological parabola:
      • Natural benefic: Explosive success UPFRONT → then stagnation/reversal.
      • Natural malefic: Intense frustration first → then wisdom/unconventional success.

    Rule 5 — "Going Direct" station trigger:
      • When natal retrograde planet goes DIRECT (or retrograde) in TRANSIT
        while running Mahadasha/Antardasha → ±3-4 days volatile activation window.
        Major long-pending events suddenly materialize or shift direction.

    Returns comprehensive retrograde analysis dict.
    """
    if not is_retrograde:
        return {
            "is_retrograde": False,
            "planet": dasha_planet,
            "note": "Planet is direct — standard delivery mechanics apply.",
        }

    degree_in_sign = planet_longitude % 30.0
    sign_idx = int(planet_longitude / 30) % 12

    # ── Rule 1: Previous house/sign effect ───────────────────────────
    early_degrees = degree_in_sign < 10.0
    prev_house_active = early_degrees
    prev_sign_active  = (dasha_planet.upper() == "JUPITER")   # only Jupiter per Kalaprakashika

    prev_house = ((planet_house - 2) % 12) + 1  # previous house (wrap around 12)
    prev_sign  = (sign_idx - 1) % 12

    # ── Rule 2: Dignity inversion ─────────────────────────────────────
    exalt_sign = _EXALTED_SIGNS.get(dasha_planet.upper(), -1)
    debil_sign = _DEBILITATED_SIGNS.get(dasha_planet.upper(), -1)
    is_exalted    = (sign_idx == exalt_sign)
    is_debilitated = (sign_idx == debil_sign)

    if is_exalted:
        effective_dignity = "DEBILITATED_BEHAVIOR"
        dignity_note = (f"{dasha_planet} is exalted but retrograde → behaves as debilitated. "
                        "Sudden falls from grace, frustration despite high status, "
                        "success that brings dissatisfaction.")
    elif is_debilitated:
        effective_dignity = "EXALTED_BEHAVIOR"
        dignity_note = (f"{dasha_planet} is debilitated but retrograde → behaves as exalted! "
                        "Unexpected, immense success via highly unconventional means. "
                        "Neechabhanga Raj Yoga strengthened.")
    else:
        effective_dignity = "STANDARD_INVERTED"
        dignity_note = f"{dasha_planet} retrograde in standard sign → erratic but powerful delivery."

    # ── Rule 3: Chesta Bala + natural benefic/malefic ────────────────
    is_nat_benefic = dasha_planet.upper() in _NATURAL_BENEFIC_PLANETS
    chesta_bala_note = (
        f"Maximum Chesta Bala: {dasha_planet} is resolute in delivering results. "
        + ("Benefic → success via unconventional/rebellious means."
           if is_nat_benefic else
           "Malefic → violently stubborn in delivering negative karma; past-life debt.")
    )

    # ── Rule 4: Parabolic trajectory ────────────────────────────────
    if is_nat_benefic:
        trajectory = "benefic_parabolic"
        trajectory_note = ("BENEFIC SEQUENCE: Explosive success at Dasha START → "
                           "stagnation, re-evaluation, and reversal in LATTER HALF. "
                           "Map as parabola — never linear.")
    else:
        trajectory = "malefic_inverted_parabolic"
        trajectory_note = ("MALEFIC SEQUENCE: Intense frustration, delays, internalized pressure "
                           "in EARLY phase → karmic debt resolves into deep wisdom and "
                           "unconventional success in SECOND HALF of Dasha.")

    # ── Rule 5: Station trigger detection ────────────────────────────
    station_trigger = False
    station_note = ""
    if transit_was_retrograde != transit_is_retrograde:
        # Planet changed direction in transit (went direct or retrograde)
        station_trigger = True
        direction_change = "went DIRECT" if not transit_is_retrograde else "turned RETROGRADE"
        station_note = (
            f"STATION TRIGGER: {dasha_planet} {direction_change} in transit. "
            f"±3-4 day volatile window: major long-pending events in H{planet_house} "
            f"(and H{prev_house} if early degrees) will suddenly materialize or shift direction."
        )

    return {
        "is_retrograde": True,
        "planet": dasha_planet,
        "degree_in_sign": round(degree_in_sign, 2),
        "sign_idx": sign_idx,
        # Rule 1
        "prev_house_effect_active": prev_house_active,
        "prev_house": prev_house if prev_house_active else planet_house,
        "prev_sign_effect_active": prev_sign_active,
        "prev_sign": prev_sign if prev_sign_active else sign_idx,
        # Rule 2
        "effective_dignity": effective_dignity,
        "dignity_note": dignity_note,
        # Rule 3
        "chesta_bala": "MAXIMUM",
        "chesta_bala_note": chesta_bala_note,
        # Rule 4
        "trajectory": trajectory,
        "trajectory_note": trajectory_note,
        # Rule 5
        "station_trigger": station_trigger,
        "station_note": station_note,
        # Summary
        "primary_house_delivery": prev_house if prev_house_active else planet_house,
        "primary_sign_delivery": prev_sign if prev_sign_active else sign_idx,
        "summary": (f"{dasha_planet} retrograde Dasha: {effective_dignity}. "
                    f"{trajectory_note[:80]}...")
    }