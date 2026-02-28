"""
Ashtottari Dasha Engine  (108-year conditional cycle).

Eligibility (Parashara, BPHS):
  Ashtottari applies when Rahu occupies a kendra (1/4/7/10) or trikona (1/5/9)
  counted from the Lord-of-the-Lagna's position, BUT Rahu must NOT be in the
  Lagna sign itself.

Planets & Year-lengths (total = 108):
  Sun(6), Moon(15), Mars(8), Mercury(17), Saturn(10),
  Jupiter(19), Rahu(12), Venus(21).
  Ketu is OMITTED in Ashtottari.

Nakshatra → Dasha-lord mapping (0-indexed nakshatras 0–26):
  0  Ashwini   → Rahu
  1  Bharani   → Rahu
  2  Krittika  → Venus
  3  Rohini    → Venus
  4  Mrigashira → Venus
  5  Ardra     → Sun
  6  Punarvasu  → Sun
  7  Pushya    → Sun
  8  Ashlesha  → Sun
  9  Magha     → Moon
  10 Purva Phalguni → Moon
  11 Uttara Phalguni → Moon
  12 Hasta     → Mars
  13 Chitra    → Mars
  14 Swati     → Mars
  15 Vishakha  → Mars
  16 Anuradha  → Mercury
  17 Jyeshtha  → Mercury
  18 Moola     → Mercury
  19 Purvashadha → Saturn
  20 Uttarashadha → Saturn
  21 Shravana  → Saturn
  22 Dhanishta → Jupiter
  23 Shatabhisha → Jupiter
  24 PurvaBhadra → Jupiter
  25 UttaraBhadra → Rahu
  26 Revati    → Rahu

Fixed sequence: Sun → Moon → Mars → Mercury → Saturn → Jupiter → Rahu → Venus
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from vedic_engine.config import Planet
from vedic_engine.core.coordinates import nakshatra_of

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DAYS_PER_YEAR: float = 365.25
ASHTOTTARI_TOTAL: int = 108  # total cycle in years

# Fixed sequence of 8 planets (Ketu excluded)
ASHTOTTARI_SEQUENCE: List[str] = [
    "SUN", "MOON", "MARS", "MERCURY", "SATURN", "JUPITER", "RAHU", "VENUS"
]

ASHTOTTARI_YEARS: dict = {
    "SUN": 6, "MOON": 15, "MARS": 8, "MERCURY": 17,
    "SATURN": 10, "JUPITER": 19, "RAHU": 12, "VENUS": 21,
}

# Nakshatra index (0=Ashwini) → Ashtottari dasha lord name
_NAK_TO_LORD: List[str] = [
    "RAHU",     # 0 Ashwini
    "RAHU",     # 1 Bharani
    "VENUS",    # 2 Krittika
    "VENUS",    # 3 Rohini
    "VENUS",    # 4 Mrigashira
    "SUN",      # 5 Ardra
    "SUN",      # 6 Punarvasu
    "SUN",      # 7 Pushya
    "SUN",      # 8 Ashlesha
    "MOON",     # 9 Magha
    "MOON",     # 10 Purva Phalguni
    "MOON",     # 11 Uttara Phalguni
    "MARS",     # 12 Hasta
    "MARS",     # 13 Chitra
    "MARS",     # 14 Swati
    "MARS",     # 15 Vishakha
    "MERCURY",  # 16 Anuradha
    "MERCURY",  # 17 Jyeshtha
    "MERCURY",  # 18 Moola
    "SATURN",   # 19 Purvashadha
    "SATURN",   # 20 Uttarashadha
    "SATURN",   # 21 Shravana
    "JUPITER",  # 22 Dhanishta
    "JUPITER",  # 23 Shatabhisha
    "JUPITER",  # 24 Purva Bhadra
    "RAHU",     # 25 Uttara Bhadra
    "RAHU",     # 26 Revati
]

NAKSHATRA_SPAN: float = 360.0 / 27.0  # ≈ 13.333°


# ---------------------------------------------------------------------------
# Eligibility check
# ---------------------------------------------------------------------------

def is_ashtottari_eligible(
    lagna_sign: int,           # 0-11 (0=Aries)
    lagna_lord_sign: int,      # sign where lagna lord is placed (Paka Lagna) (0-11)
    rahu_sign: int,            # sign where Rahu is placed (0-11)
    moon_longitude: float = -1.0,   # if provided, adds lunar phase check
    sun_longitude: float = -1.0,    # if provided, adds lunar phase check
    birth_is_daytime: bool = True,  # True if birth was during daytime
) -> dict:
    """
    Return eligibility dict for Ashtottari Dasha.

    Research Brief (Jyotish Logic Architecture):
    Classical BPHS conditions:
      1. Lunar Phase: birth during DAYTIME in Krishna Paksha (waning moon),
         OR during NIGHTTIME in Shukla Paksha (waxing moon).
      2. Geometric: Rahu in Kendra (1/4/7/10) or Trikona (1/5/9) from the
         PAKA LAGNA (sign of the Lagna Lord) — NOT from the Lagna itself.
         Rahu must NOT occupy the Lagna sign itself.

    Returns {eligible: bool, reason: str, paka_lagna_rahu_house: int,
             paksha: str, lunar_phase_ok: bool}
    """
    # ── Paka Lagna check (Research Brief: correct algorithmic route) ──
    if rahu_sign == lagna_sign:
        return {
            "eligible": False,
            "reason": "Rahu occupies the Lagna sign itself → not eligible",
            "paka_lagna_rahu_house": 1,
            "paksha": "unknown",
            "lunar_phase_ok": False,
        }

    house_from_lord = ((rahu_sign - lagna_lord_sign) % 12) + 1  # 1-based
    kendra_trikona  = {1, 4, 5, 7, 9, 10}
    paka_lagna_ok   = house_from_lord in kendra_trikona

    # ── Lunar phase check (BPHS condition) ──────────────────────────────
    # Moon-Sun elongation 0-180 = Shukla Paksha (waxing); 180-360 = Krishna Paksha (waning)
    lunar_phase_ok = True   # default: skip if longitude data not provided
    paksha = "unknown"
    if moon_longitude >= 0 and sun_longitude >= 0:
        elongation = (moon_longitude - sun_longitude) % 360.0
        is_krishna_paksha = elongation >= 180.0
        paksha = "Krishna (waning)" if is_krishna_paksha else "Shukla (waxing)"
        # BPHS: eligible if (daytime AND Krishna) OR (nighttime AND Shukla)
        lunar_phase_ok = (
            (birth_is_daytime and is_krishna_paksha) or
            (not birth_is_daytime and not is_krishna_paksha)
        )

    eligible = paka_lagna_ok and lunar_phase_ok
    reason_parts = []
    if not paka_lagna_ok:
        reason_parts.append(
            f"Rahu in H{house_from_lord} from Paka Lagna — not a kendra/trikona"
        )
    if not lunar_phase_ok:
        day_night = "daytime" if birth_is_daytime else "nighttime"
        reason_parts.append(f"Lunar phase mismatch: {paksha} birth, {day_night}")
    if not reason_parts:
        reason_parts.append(
            f"Rahu in H{house_from_lord} from Paka Lagna (kendra/trikona) ✓; {paksha} ✓"
        )

    return {
        "eligible": eligible,
        "reason": "; ".join(reason_parts),
        "paka_lagna_rahu_house": house_from_lord,
        "paksha": paksha,
        "lunar_phase_ok": lunar_phase_ok,
        "paka_lagna_ok": paka_lagna_ok,
    }


# ---------------------------------------------------------------------------
# Birth dasha balance
# ---------------------------------------------------------------------------

def _birth_dasha_balance(moon_longitude: float) -> Tuple[str, float]:
    """Return (starting_lord_name, remaining_years_at_birth)."""
    nak_idx = int(moon_longitude / NAKSHATRA_SPAN) % 27
    lord_name = _NAK_TO_LORD[nak_idx]

    pos_in_nak = moon_longitude % NAKSHATRA_SPAN
    remaining_arc = NAKSHATRA_SPAN - pos_in_nak
    fraction = remaining_arc / NAKSHATRA_SPAN
    balance = ASHTOTTARI_YEARS[lord_name] * fraction

    return lord_name, balance


def _sequence_from(start_lord: str) -> List[str]:
    """Get 8-planet cycle starting at start_lord."""
    idx = ASHTOTTARI_SEQUENCE.index(start_lord)
    return [ASHTOTTARI_SEQUENCE[(idx + i) % 8] for i in range(8)]


# ---------------------------------------------------------------------------
# Sub-period computation
# ---------------------------------------------------------------------------

def _compute_sub_periods(
    maha_lord: str,
    maha_duration: float,
    maha_start: datetime,
    max_level: int,
    current_level: int = 2,
) -> List[dict]:
    """
    Recursively compute Ashtottari sub-periods.
    Duration formula (same proportion as Vimshottari but total=108):
      sub_duration = parent_duration × sub_lord_years / 108
    """
    if current_level > max_level:
        return []

    seq = _sequence_from(maha_lord)
    current_date = maha_start
    sub_periods = []

    for lord in seq:
        duration = (maha_duration * ASHTOTTARI_YEARS[lord]) / ASHTOTTARI_TOTAL
        end_date = current_date + timedelta(days=int(duration * DAYS_PER_YEAR))

        sub = {
            "level": current_level,
            "planet": lord,
            "start": current_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(duration, 5),
            "sub_periods": [],
        }

        if current_level < max_level:
            sub["sub_periods"] = _compute_sub_periods(
                lord, duration, current_date, max_level, current_level + 1
            )

        sub_periods.append(sub)
        current_date = end_date

    return sub_periods


# ---------------------------------------------------------------------------
# Main compute function
# ---------------------------------------------------------------------------

def compute_ashtottari_periods(
    moon_longitude: float,
    birth_date: datetime,
    levels: int = 2,  # 1=Maha only, 2=+Antar, 3=+Pratyantar
) -> List[dict]:
    """
    Compute Ashtottari Dasha timeline.
    Returns list of Mahadasha dicts (nested sub_periods if levels >= 2).
    """
    start_lord, balance = _birth_dasha_balance(moon_longitude)
    sequence = _sequence_from(start_lord)

    current_date = birth_date
    periods: List[dict] = []
    total_days = 0

    # First run of 8-planet cycle (balance first, then full years)
    for i, lord in enumerate(sequence):
        duration = balance if i == 0 else float(ASHTOTTARI_YEARS[lord])
        end_date = current_date + timedelta(days=int(duration * DAYS_PER_YEAR))

        maha = {
            "level": 1,
            "planet": lord,
            "start": current_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(duration, 4),
            "sub_periods": [],
        }
        if levels >= 2:
            maha["sub_periods"] = _compute_sub_periods(
                lord, duration, current_date, levels
            )

        periods.append(maha)
        total_days += int(duration * DAYS_PER_YEAR)
        current_date = end_date

    # Extend to cover ~108 years
    while total_days < int(108 * DAYS_PER_YEAR):
        for lord in sequence:
            duration = float(ASHTOTTARI_YEARS[lord])
            end_date = current_date + timedelta(days=int(duration * DAYS_PER_YEAR))
            maha = {
                "level": 1,
                "planet": lord,
                "start": current_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "duration_years": duration,
                "sub_periods": [],
            }
            if levels >= 2:
                maha["sub_periods"] = _compute_sub_periods(
                    lord, duration, current_date, levels
                )
            periods.append(maha)
            total_days += int(duration * DAYS_PER_YEAR)
            current_date = end_date
            if total_days >= int(108 * DAYS_PER_YEAR):
                break

    return periods


def get_active_ashtottari(
    periods: List[dict],
    on_date: Optional[datetime] = None,
) -> dict:
    """Return the active Mahadasha/Antar dasha on a given date."""
    if on_date is None:
        on_date = datetime.now()

    def _find(plist, date):
        for p in plist:
            s = datetime.strptime(p["start"], "%Y-%m-%d")
            e = datetime.strptime(p["end"], "%Y-%m-%d")
            if s <= date < e:
                return p
        return None

    maha = _find(periods, on_date)
    if not maha:
        return {}

    result: dict = {"mahadasha": maha["planet"]}
    antar = _find(maha.get("sub_periods", []), on_date)
    if antar:
        result["antardasha"] = antar["planet"]

    return result


def ashtottari_details_on_date(
    moon_longitude: float,
    birth_date: datetime,
    lagna_sign: int,
    lagna_lord_sign: int,
    rahu_sign: int,
    on_date: Optional[datetime] = None,
    levels: int = 2,
    sun_longitude: float = -1.0,
    birth_is_daytime: bool = True,
) -> dict:
    """
    High-level: check eligibility (Paka Lagna + lunar phase), compute, return active period.

    Research Brief: When BOTH Vimshottari AND Ashtottari indicate an event in
    the same year → confidence near-absolute certainty (dual verification matrix).

    Returns {eligible, eligibility_detail, active, all_periods, dual_verified}
    """
    eligibility = is_ashtottari_eligible(
        lagna_sign, lagna_lord_sign, rahu_sign,
        moon_longitude=moon_longitude,
        sun_longitude=sun_longitude,
        birth_is_daytime=birth_is_daytime,
    )
    if not eligibility["eligible"]:
        return {
            "eligible": False,
            "eligibility_detail": eligibility,
            "active": {},
            "all_periods": [],
            "dual_verified": False,
        }

    if on_date is None:
        on_date = datetime.now()

    periods = compute_ashtottari_periods(moon_longitude, birth_date, levels)
    active  = get_active_ashtottari(periods, on_date)
    return {
        "eligible": True,
        "eligibility_detail": eligibility,
        "active": active,
        "all_periods": periods,
        "dual_verified": False,   # set True in engine.py when Vimshottari agrees
        "note": ("Research Brief: Run Ashtottari alongside Vimshottari. "
                 "If both confirm same domain/event → near-absolute certainty."),
    }
