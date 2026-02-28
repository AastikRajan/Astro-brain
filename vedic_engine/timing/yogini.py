"""
Yogini Dasha Engine.
36-year cycle with 8 Yoginis.

From deep-research-report.md:
  Start formula: (Moon_Nakshatra_Number + 3) mod 8
  Remainder maps to Yogini (0/8 → Sankata, 1 → Mangala, etc.)
  Balance: (YoginiPeriod × remaining_minutes_in_nak) / 800
  Sub-periods: proportional, starting from the major yogini.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

from vedic_engine.config import (
    YOGINI_NAMES, YOGINI_PLANETS, YOGINI_YEARS, YOGINI_TOTAL,
    NAKSHATRA_SPAN, Planet
)
from vedic_engine.core.coordinates import nakshatra_of

DAYS_PER_YEAR = 365.25


def _yogini_start(moon_longitude: float) -> Tuple[int, float]:
    """
    Returns (yogini_index 0-7, balance_years).

    Formula:
      N = nakshatra index (1-27, 1-indexed)
      yogini_idx = (N + 3) % 8  → 0..7
      (0 maps to Sankata/index 7)
      balance = (YoginiPeriod_of_start × remaining_arc_minutes) / 800
    """
    nak_idx = nakshatra_of(moon_longitude)   # 0-26
    N = nak_idx + 1                           # make 1-indexed

    remainder = (N + 3) % 8
    # Remainder 0 → Sankata (index 7), 1 → Mangala (index 0), ... 7 → Siddha (index 6)
    yogini_idx = (remainder - 1) % 8

    pos_in_nak = moon_longitude % NAKSHATRA_SPAN
    remaining_arc_min = (NAKSHATRA_SPAN - pos_in_nak) * 60  # arc-minutes remaining
    period_years = YOGINI_YEARS[yogini_idx]
    balance = (period_years * remaining_arc_min) / 800.0   # 800' = 13°20'

    return yogini_idx, balance


def compute_yogini_periods(
        moon_longitude: float,
        birth_date: datetime,
        levels: int = 2,
) -> List[dict]:
    """
    Compute complete Yogini Dasha timeline from birth.
    """
    start_idx, balance_years = _yogini_start(moon_longitude)
    current_date = birth_date
    periods = []

    total_years = 0.0
    cycle_pos = start_idx
    first = True

    while total_years < 100:   # Generate ~100 years
        year_count = balance_years if first else float(YOGINI_YEARS[cycle_pos])
        first = False

        end_date = current_date + timedelta(days=int(year_count * DAYS_PER_YEAR))
        period = {
            "level": 1,
            "yogini": YOGINI_NAMES[cycle_pos],
            "planet": YOGINI_PLANETS[cycle_pos].name,
            "start": current_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(year_count, 4),
            "sub_periods": [],
        }

        if levels >= 2:
            period["sub_periods"] = _yogini_sub_periods(
                cycle_pos, year_count, current_date
            )

        periods.append(period)
        current_date = end_date
        total_years += year_count
        cycle_pos = (cycle_pos + 1) % 8

    return periods


def _yogini_sub_periods(
        start_idx: int,
        major_duration: float,
        major_start: datetime,
) -> List[dict]:
    """
    Sub-periods within a Yogini period.
    Each sub-period = (major_duration × sub_years) / YOGINI_TOTAL
    Order starts from the major yogini.
    """
    current_date = major_start
    subs = []
    total_sub = float(YOGINI_TOTAL)

    for i in range(8):
        idx = (start_idx + i) % 8
        sub_years = (major_duration * YOGINI_YEARS[idx]) / total_sub
        end_date = current_date + timedelta(days=int(sub_years * 365.25))
        subs.append({
            "level": 2,
            "yogini": YOGINI_NAMES[idx],
            "planet": YOGINI_PLANETS[idx].name,
            "start": current_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(sub_years, 5),
        })
        current_date = end_date

    return subs


def get_active_yogini(periods: List[dict], on_date: Optional[datetime] = None) -> dict:
    """Return the active Yogini period (major + sub) for a given date."""
    if on_date is None:
        on_date = datetime.now()

    def _find(plist, dt):
        for p in plist:
            s = datetime.strptime(p["start"], "%Y-%m-%d")
            e = datetime.strptime(p["end"], "%Y-%m-%d")
            if s <= dt < e:
                return p
        return None

    major = _find(periods, on_date)
    if not major:
        return {}

    result = {
        "major_yogini": major["yogini"],
        "major_planet": major["planet"],
    }
    sub = _find(major.get("sub_periods", []), on_date)
    if sub:
        result["sub_yogini"] = sub["yogini"]
        result["sub_planet"] = sub["planet"]
    return result