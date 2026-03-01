"""
Conditional Dasha Systems (Branch D, File 5).

10 conditional dasha systems triggered by specific natal conditions.
Each has an eligibility check and a computation function.

Implemented here:
  1. Shodashottari  (116yr) — Day Krishna or Night Shukla + Moon Hora
  2. Dwadasottari   (112yr) — Lagna in Venus Navamsa (Taurus/Libra D-9)
  3. Panchottari    (105yr) — Cancer Lagna in D-1 AND D-12
  4. Shatabdika     (100yr) — Vargottama Lagna (same sign in D-1 and D-9)
  5. Chaturaashiti  ( 84yr) — 10th lord in 10th house
  6. Dwisaptati     ( 72yr) — Lagna lord in 7th OR 7th lord in Lagna
  7. Shat Trimsa    ( 36yr) — Day+Sun Hora OR Night+Moon Hora
  8. Moola Dasha    (variable) — Kendra/Panaphara/Apoklima, Vimshottari-mod years
  9. Tara Dasha     (120yr)  — Universal, 9-Tara Nakshatra filter

Note: Yogini Dasha (36yr) and Ashtottari Dasha (108yr) are in separate files.

Reference: Algorithmic Vedic Astrology Engine Development-5.md (Branch D)
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any

from vedic_engine.config import Planet

NAKSHATRA_SPAN = 13.333333  # degrees
SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Vimshottari base years (used as reference in Moola Dasha)
_VIMSHA_YEARS: Dict[str, int] = {
    "SUN": 6, "MOON": 10, "MARS": 7, "RAHU": 18, "JUPITER": 16,
    "SATURN": 19, "MERCURY": 17, "KETU": 7, "VENUS": 20,
}

# ── Nakshatra computation helpers ─────────────────────────────────────────────

def _nak_idx(longitude: float) -> int:
    """Return 0-indexed nakshatra (0=Ashwini ... 26=Revati)."""
    return int((longitude % 360.0) / NAKSHATRA_SPAN) % 27


def _nak_number(longitude: float) -> int:
    """Return 1-indexed nakshatra number."""
    return _nak_idx(longitude) + 1


def _nak_balance(longitude: float, period_years: float) -> float:
    """Remaining fraction of current nakshatra × period_years."""
    lon = longitude % 360.0
    pos_in_nak = lon % NAKSHATRA_SPAN
    remaining_frac = (NAKSHATRA_SPAN - pos_in_nak) / NAKSHATRA_SPAN
    return period_years * remaining_frac


# ── Sign helpers ──────────────────────────────────────────────────────────────

def _sign_of(longitude: float) -> int:
    """0-indexed sign (0=Aries ... 11=Pisces)."""
    return int((longitude % 360.0) / 30) % 12


def _sign_name(idx: int) -> str:
    return SIGN_NAMES[idx % 12]


# ── Conditional Dasha Implementations ─────────────────────────────────────────

# ─── 1. Shodashottari (116 Years) ─────────────────────────────────────────────

_SHODASHOTTARI_SEQ = ["SUN", "MARS", "JUPITER", "SATURN", "KETU", "MOON", "MERCURY", "VENUS"]
_SHODASHOTTARI_YEARS = [11, 12, 13, 14, 15, 16, 17, 18]
# Note: Rahu excluded; total = 116 years

def check_shodashottari_eligible(
        is_daytime: bool,
        paksha: str,       # "shukla" or "krishna"
        lagna_hora: str,   # "sun" or "moon" (hora of lagna sign)
) -> Dict[str, Any]:
    """
    Shodashottari eligibility:
    - Day birth + Krishna Paksha + Lagna in Moon Hora, OR
    - Night birth + Shukla Paksha + Lagna in Sun Hora
    """
    eligible = False
    reason = ""
    if is_daytime and paksha == "krishna" and lagna_hora == "moon":
        eligible = True
        reason = "Day birth, Krishna Paksha, Moon Hora Lagna"
    elif (not is_daytime) and paksha == "shukla" and lagna_hora == "sun":
        eligible = True
        reason = "Night birth, Shukla Paksha, Sun Hora Lagna"
    else:
        reason = (f"{'Day' if is_daytime else 'Night'} birth, {paksha.title()} Paksha, "
                  f"{lagna_hora.title()} Hora — conditions not met")
    return {"eligible": eligible, "reason": reason}


def compute_shodashottari(moon_longitude: float) -> Dict[str, Any]:
    """
    Shodashottari Dasha sequence.
    Count from Pushya (nak 7, 1-indexed 8) to Janma Nakshatra, divide by 8.
    Remainder = start index in sequence.
    """
    janma_nak = _nak_number(moon_longitude)          # 1–27
    pushya_nak = 8                                    # Pushya = 8th nakshatra

    count = (janma_nak - pushya_nak) % 27
    start_idx = count % 8

    # Balance of first period
    balance = _nak_balance(moon_longitude, _SHODASHOTTARI_YEARS[start_idx])

    periods: List[Dict] = []
    cumulative = 0.0
    for i in range(8):
        idx = (start_idx + i) % 8
        planet = _SHODASHOTTARI_SEQ[idx]
        years = _SHODASHOTTARI_YEARS[idx]
        effective = balance if i == 0 else float(years)
        periods.append({
            "planet": planet,
            "years": round(effective, 3),
            "full_years": years,
            "cumulative_start": round(cumulative, 3),
        })
        cumulative += effective

    return {
        "system": "Shodashottari Dasha",
        "total_years": 116,
        "starting_planet": _SHODASHOTTARI_SEQ[start_idx],
        "specialization": "Long-term health, systemic wealth accumulation",
        "periods": periods,
    }


# ─── 2. Dwadasottari (112 Years) ──────────────────────────────────────────────

_DWADASOTTARI_SEQ = ["SUN", "JUPITER", "KETU", "MERCURY", "RAHU", "MARS", "SATURN", "MOON"]
_DWADASOTTARI_YEARS = [7, 9, 11, 13, 15, 17, 19, 21]
# Venus excluded; total = 112 years

def check_dwadasottari_eligible(d9_lagna_sign: str) -> Dict[str, Any]:
    """
    Eligible if Lagna falls in Venus Navamsa = Taurus or Libra in D-9.
    """
    eligible = d9_lagna_sign in ("Taurus", "Libra")
    return {
        "eligible": eligible,
        "reason": (f"D-9 Lagna in {d9_lagna_sign} — "
                   f"{'Venus Navamsa' if eligible else 'not Venus Navamsa'}"),
    }


def compute_dwadasottari(moon_longitude: float) -> Dict[str, Any]:
    """
    Count from Janma Nakshatra to Revati (nak 27); remainder÷8 = start index.
    """
    janma_nak = _nak_number(moon_longitude)
    revati_nak = 27
    count = (revati_nak - janma_nak) % 27
    start_idx = count % 8

    balance = _nak_balance(moon_longitude, _DWADASOTTARI_YEARS[start_idx])
    periods: List[Dict] = []
    cumulative = 0.0
    for i in range(8):
        idx = (start_idx + i) % 8
        planet = _DWADASOTTARI_SEQ[idx]
        years = _DWADASOTTARI_YEARS[idx]
        effective = balance if i == 0 else float(years)
        periods.append({
            "planet": planet,
            "years": round(effective, 3),
            "full_years": years,
            "cumulative_start": round(cumulative, 3),
        })
        cumulative += effective

    return {
        "system": "Dwadasottari Dasha",
        "total_years": 112,
        "starting_planet": _DWADASOTTARI_SEQ[start_idx],
        "specialization": "Luxury, marital fidelity, artistic expression, material acquisition",
        "periods": periods,
    }


# ─── 3. Panchottari (105 Years) ───────────────────────────────────────────────

_PANCHOTTARI_SEQ = ["SUN", "MERCURY", "SATURN", "MARS", "VENUS", "MOON", "JUPITER"]
_PANCHOTTARI_YEARS = [12, 13, 14, 15, 16, 17, 18]
# total = 105 years

def check_panchottari_eligible(d1_lagna_sign: str, d12_lagna_sign: str) -> Dict[str, Any]:
    """
    Eligible only if Cancer Lagna in BOTH D-1 and D-12.
    """
    eligible = d1_lagna_sign == "Cancer" and d12_lagna_sign == "Cancer"
    return {
        "eligible": eligible,
        "reason": (f"D-1 Lagna={d1_lagna_sign}, D-12 Lagna={d12_lagna_sign} — "
                   f"{'both Cancer ✓' if eligible else 'Cancer required in both'}"),
    }


def compute_panchottari(moon_longitude: float) -> Dict[str, Any]:
    """
    Count from Anuradha (nak 17) to Janma Nakshatra, divide by 7.
    """
    janma_nak = _nak_number(moon_longitude)
    anuradha_nak = 17
    count = (janma_nak - anuradha_nak) % 27
    start_idx = count % 7

    balance = _nak_balance(moon_longitude, _PANCHOTTARI_YEARS[start_idx])
    periods: List[Dict] = []
    cumulative = 0.0
    for i in range(7):
        idx = (start_idx + i) % 7
        planet = _PANCHOTTARI_SEQ[idx]
        years = _PANCHOTTARI_YEARS[idx]
        effective = balance if i == 0 else float(years)
        periods.append({
            "planet": planet,
            "years": round(effective, 3),
            "full_years": years,
            "cumulative_start": round(cumulative, 3),
        })
        cumulative += effective

    return {
        "system": "Panchottari Dasha",
        "total_years": 105,
        "starting_planet": _PANCHOTTARI_SEQ[start_idx],
        "specialization": "Emotional trauma, psychological shifts, maternal inheritances, real estate",
        "periods": periods,
    }


# ─── 4. Shatabdika (100 Years) ────────────────────────────────────────────────

_SHATABDIKA_SEQ = ["SUN", "MOON", "VENUS", "MERCURY", "JUPITER", "MARS", "SATURN"]
_SHATABDIKA_YEARS = [5, 5, 10, 10, 20, 20, 30]
# total = 100 years

def check_shatabdika_eligible(d1_lagna_sign: str, d9_lagna_sign: str) -> Dict[str, Any]:
    """
    Eligible if Lagna is Vargottama (same sign in D-1 and D-9).
    """
    eligible = d1_lagna_sign == d9_lagna_sign
    return {
        "eligible": eligible,
        "reason": (f"D-1 Lagna={d1_lagna_sign}, D-9 Lagna={d9_lagna_sign} — "
                   f"{'Vargottama ✓' if eligible else 'not Vargottama'}"),
    }


def compute_shatabdika(moon_longitude: float) -> Dict[str, Any]:
    """
    Count from Revati (nak 27) to Janma Nakshatra, divide by 7.
    """
    janma_nak = _nak_number(moon_longitude)
    revati_nak = 27
    count = (janma_nak - revati_nak) % 27
    start_idx = count % 7

    balance = _nak_balance(moon_longitude, _SHATABDIKA_YEARS[start_idx])
    periods: List[Dict] = []
    cumulative = 0.0
    for i in range(7):
        idx = (start_idx + i) % 7
        planet = _SHATABDIKA_SEQ[idx]
        years = _SHATABDIKA_YEARS[idx]
        effective = balance if i == 0 else float(years)
        periods.append({
            "planet": planet,
            "years": round(effective, 3),
            "full_years": years,
            "cumulative_start": round(cumulative, 3),
        })
        cumulative += effective

    return {
        "system": "Shatabdika Dasha",
        "total_years": 100,
        "starting_planet": _SHATABDIKA_SEQ[start_idx],
        "specialization": "Sudden fortune shifts, global fame, sweeping public authority",
        "periods": periods,
    }


# ─── 5. Chaturaashiti Sama (84 Years) ─────────────────────────────────────────

_CHATURA_SEQ = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]
_CHATURA_YEARS = [12, 12, 12, 12, 12, 12, 12]
# All equal 12 years; total = 84

def check_chaturaashiti_eligible(
        tenth_lord: str,
        planet_houses: Dict[str, int],
) -> Dict[str, Any]:
    """
    Eligible if 10th house lord resides in the 10th house.
    """
    lord_house = planet_houses.get(tenth_lord, 0)
    eligible = lord_house == 10
    return {
        "eligible": eligible,
        "reason": (f"10th lord ({tenth_lord}) in H{lord_house} — "
                   f"{'10th house ✓' if eligible else 'must be in 10th'}"),
    }


def compute_chaturaashiti(moon_longitude: float) -> Dict[str, Any]:
    """
    Count from Swati (nak 15) to Janma Nakshatra, divide by 7.
    """
    janma_nak = _nak_number(moon_longitude)
    swati_nak = 15
    count = (janma_nak - swati_nak) % 27
    start_idx = count % 7

    balance = _nak_balance(moon_longitude, 12.0)  # all periods = 12yr
    periods: List[Dict] = []
    cumulative = 0.0
    for i in range(7):
        idx = (start_idx + i) % 7
        planet = _CHATURA_SEQ[idx]
        effective = balance if i == 0 else 12.0
        periods.append({
            "planet": planet,
            "years": round(effective, 3),
            "full_years": 12,
            "cumulative_start": round(cumulative, 3),
        })
        cumulative += effective

    return {
        "system": "Chaturaashiti Sama Dasha",
        "total_years": 84,
        "starting_planet": _CHATURA_SEQ[start_idx],
        "specialization": "Career mapping, professional zenith, political ascension, industry dominance",
        "periods": periods,
    }


# ─── 6. Dwisaptati Sama (72 Years) ────────────────────────────────────────────

_DWISAPTATI_SEQ = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU"]
_DWISAPTATI_YEARS_PER = 9  # all equal 9 years (Ketu omitted); total = 72

def check_dwisaptati_eligible(
        lagna_lord: str,
        planet_houses: Dict[str, int],
        seventh_lord: str,
) -> Dict[str, Any]:
    """
    Eligible if Lagna lord occupies 7th, OR 7th lord occupies Lagna (1st house).
    """
    lagna_lord_house = planet_houses.get(lagna_lord, 0)
    seventh_lord_house = planet_houses.get(seventh_lord, 0)
    c1 = lagna_lord_house == 7
    c2 = seventh_lord_house == 1
    eligible = c1 or c2
    reason_parts = []
    if c1:
        reason_parts.append(f"Lagna lord ({lagna_lord}) in 7th")
    if c2:
        reason_parts.append(f"7th lord ({seventh_lord}) in Lagna")
    if not eligible:
        reason_parts.append(f"Lagna lord ({lagna_lord}) in H{lagna_lord_house}, "
                            f"7th lord ({seventh_lord}) in H{seventh_lord_house}")
    return {"eligible": eligible, "reason": " + ".join(reason_parts)}


def compute_dwisaptati(moon_longitude: float) -> Dict[str, Any]:
    """
    Count from Moola (nak 19) to Janma nakshatra, expunge multiples of 8.
    Remainder = start index.
    """
    janma_nak = _nak_number(moon_longitude)
    moola_nak = 19
    count = (janma_nak - moola_nak) % 27
    start_idx = count % 8

    balance = _nak_balance(moon_longitude, float(_DWISAPTATI_YEARS_PER))
    periods: List[Dict] = []
    cumulative = 0.0
    for i in range(8):
        idx = (start_idx + i) % 8
        planet = _DWISAPTATI_SEQ[idx]
        effective = balance if i == 0 else float(_DWISAPTATI_YEARS_PER)
        periods.append({
            "planet": planet,
            "years": round(effective, 3),
            "full_years": _DWISAPTATI_YEARS_PER,
            "cumulative_start": round(cumulative, 3),
        })
        cumulative += effective

    return {
        "system": "Dwisaptati Sama Dasha",
        "total_years": 72,
        "starting_planet": _DWISAPTATI_SEQ[start_idx],
        "specialization": "Partnership dynamics, marriage timing, business/rivalry events",
        "periods": periods,
    }


# ─── 7. Shat Trimsa Sama (36 Years) ───────────────────────────────────────────

_SHAT_TRIMSA_SEQ = ["MOON", "SUN", "JUPITER", "MARS", "MERCURY", "SATURN", "VENUS", "RAHU"]
_SHAT_TRIMSA_YEARS = [1, 2, 3, 4, 5, 6, 7, 8]
# total = 36 years

def check_shat_trimsa_eligible(
        is_daytime: bool,
        lagna_hora: str,   # "sun" or "moon"
) -> Dict[str, Any]:
    """
    Day birth + Sun Hora Lagna, OR Night birth + Moon Hora Lagna.
    """
    c1 = is_daytime and lagna_hora == "sun"
    c2 = (not is_daytime) and lagna_hora == "moon"
    eligible = c1 or c2
    time_str = "Day" if is_daytime else "Night"
    return {
        "eligible": eligible,
        "reason": (f"{time_str} birth + {lagna_hora.title()} Hora Lagna — "
                   f"{'✓' if eligible else 'conditions not met'}"),
    }


def compute_shat_trimsa(moon_longitude: float) -> Dict[str, Any]:
    """
    Count from Shravana (nak 22, 1-indexed) to Janma, divide by 8.
    """
    janma_nak = _nak_number(moon_longitude)
    shravana_nak = 22
    count = (janma_nak - shravana_nak) % 27
    start_idx = count % 8

    balance = _nak_balance(moon_longitude, _SHAT_TRIMSA_YEARS[start_idx])
    periods: List[Dict] = []
    cumulative = 0.0
    for i in range(8):
        idx = (start_idx + i) % 8
        planet = _SHAT_TRIMSA_SEQ[idx]
        years = _SHAT_TRIMSA_YEARS[idx]
        effective = balance if i == 0 else float(years)
        periods.append({
            "planet": planet,
            "years": round(effective, 3),
            "full_years": years,
            "cumulative_start": round(cumulative, 3),
        })
        cumulative += effective

    return {
        "system": "Shat Trimsa Sama Dasha",
        "total_years": 36,
        "starting_planet": _SHAT_TRIMSA_SEQ[start_idx],
        "specialization": "Short-term vitality, rapid karmic burns, personal agency fluctuations",
        "periods": periods,
    }


# ─── 8. Moola Dasha (Lagnadi Kendradi Dasha) ────────────────────────────────

_KENDRA_HOUSES = {1, 4, 7, 10}
_PANAPHARA_HOUSES = {2, 5, 8, 11}
_APOKLIMA_HOUSES = {3, 6, 9, 12}

def compute_moola_dasha(
        planet_houses: Dict[str, int],
        strongest_initiator: str = "LAGNA",  # "SUN", "MOON", or "LAGNA"
        planet_lons: Optional[Dict[str, float]] = None,
        planet_signs: Optional[Dict[str, str]] = None,
        exalt_signs: Optional[Dict[str, str]] = None,
        debil_signs: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Moola Dasha: follows planets in Kendra → Panaphara → Apoklima order.
    Duration = Vimshottari base -1yr; +1yr if exalted; -1yr if debilitated.
    If net=0, use full base. Negative values use absolute value.
    """
    if planet_signs is None:
        planet_signs = {}
    if exalt_signs is None:
        exalt_signs = {
            "SUN": "Aries", "MOON": "Taurus", "MARS": "Capricorn",
            "MERCURY": "Virgo", "JUPITER": "Cancer", "VENUS": "Pisces", "SATURN": "Libra",
        }
    if debil_signs is None:
        debil_signs = {
            "SUN": "Libra", "MOON": "Scorpio", "MARS": "Cancer",
            "MERCURY": "Pisces", "JUPITER": "Capricorn", "VENUS": "Virgo", "SATURN": "Aries",
        }

    # Build planet → group assignment
    kendra_planets: List[str] = []
    panaphara_planets: List[str] = []
    apoklima_planets: List[str] = []

    all_planets = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU"]
    for p in all_planets:
        h = planet_houses.get(p, 0)
        if h in _KENDRA_HOUSES:
            kendra_planets.append(p)
        elif h in _PANAPHARA_HOUSES:
            panaphara_planets.append(p)
        elif h in _APOKLIMA_HOUSES:
            apoklima_planets.append(p)

    # Order: Kendra → Panaphara → Apoklima
    sequence = kendra_planets + panaphara_planets + apoklima_planets

    periods: List[Dict] = []
    cumulative = 0.0
    for p in sequence:
        base = _VIMSHA_YEARS.get(p, 10)
        net = base - 1  # standard reduction

        sign = planet_signs.get(p, "")
        if sign == exalt_signs.get(p, ""):
            net += 1
        elif sign == debil_signs.get(p, ""):
            net -= 1

        if net == 0:
            net = base
        net = abs(net)

        group = "Kendra" if p in kendra_planets else ("Panaphara" if p in panaphara_planets else "Apoklima")
        periods.append({
            "planet": p,
            "years": float(net),
            "base_years": base,
            "group": group,
            "house": planet_houses.get(p, 0),
            "cumulative_start": round(cumulative, 3),
        })
        cumulative += net

    return {
        "system": "Moola Dasha (Lagnadi Kendradi)",
        "initiator": strongest_initiator,
        "specialization": "Generational curses, past-life karma, deep psychological complexes",
        "total_years": round(cumulative, 1),
        "periods": periods[:7],  # display top 7
    }


# ─── 9. Tara Dasha ────────────────────────────────────────────────────────────

_TARA_NAMES = [
    "Janma (Birth/Danger)", "Sampat (Wealth)", "Vipat (Loss)",
    "Kshema (Prosperity)", "Pratyak (Obstacles)", "Sadhana (Achievement)",
    "Naidhana (Death/Danger)", "Mitra (Friendship)", "Parama Mitra (Great Friendship)",
]
_TARA_QUALITY = [
    "DANGER", "AUSPICIOUS", "INAUSPICIOUS", "AUSPICIOUS", "INAUSPICIOUS",
    "AUSPICIOUS", "DANGER", "AUSPICIOUS", "VERY AUSPICIOUS",
]

# Vimshottari sequence order (same as standard)
_VIMSHA_SEQ = ["SUN", "MOON", "MARS", "RAHU", "JUPITER", "SATURN", "MERCURY", "KETU", "VENUS"]
_VIMSHA_YEARS_LIST = [6, 10, 7, 18, 16, 19, 17, 7, 20]


def compute_tara_dasha(
        moon_longitude: float,
        planet_nakshatras: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """
    Tara Dasha: Universal system filtering Vimshottari through 9-Tara states.

    Each planet's Vimshottari period is tagged with its Tara state
    (counted from Janma Nakshatra) — modifying the prediction quality.

    A benefic in Vipat/Naidhana = destruction.
    A malefic in Sampat/Sadhana = fierce success.
    """
    janma_nak = _nak_idx(moon_longitude)  # 0-indexed

    # Compute Tara state for each nakshatra relative to Janma
    def tara_of_nak(nak: int) -> Tuple[str, str]:
        """Return (tara_name, tara_quality) for a nakshatra."""
        offset = (nak - janma_nak) % 27
        tara_idx = offset % 9
        return _TARA_NAMES[tara_idx], _TARA_QUALITY[tara_idx]

    # Compute Vimshottari start (standard formula)
    nak_lord_idx = janma_nak % 9
    pos_in_nak = (moon_longitude % 360.0) % NAKSHATRA_SPAN
    remaining_frac = (NAKSHATRA_SPAN - pos_in_nak) / NAKSHATRA_SPAN

    periods: List[Dict] = []
    cumulative = 0.0

    for i in range(9):
        planet_idx = (nak_lord_idx + i) % 9
        planet = _VIMSHA_SEQ[planet_idx]
        full_years = _VIMSHA_YEARS_LIST[planet_idx]

        if i == 0:
            effective_years = full_years * remaining_frac
        else:
            effective_years = float(full_years)

        # Tara state of the planet's own nakshatra
        planet_nak = planet_nakshatras.get(planet, janma_nak) if planet_nakshatras else planet_idx * 3
        tara_name, tara_quality = tara_of_nak(planet_nak)

        # Antardasha Taras
        antardashas: List[Dict] = []
        for j in range(9):
            sub_idx = (planet_idx + j) % 9
            sub_planet = _VIMSHA_SEQ[sub_idx]
            sub_full = _VIMSHA_YEARS_LIST[sub_idx]
            sub_years = (full_years * sub_full) / 120.0
            sub_nak = planet_nakshatras.get(sub_planet, sub_idx * 3) if planet_nakshatras else sub_idx * 3
            sub_tara_name, sub_tara_quality = tara_of_nak(sub_nak)
            antardashas.append({
                "planet": sub_planet,
                "years": round(sub_years, 3),
                "tara": sub_tara_name,
                "quality": sub_tara_quality,
            })

        periods.append({
            "planet": planet,
            "years": round(effective_years, 3),
            "full_years": full_years,
            "tara": tara_name,
            "tara_quality": tara_quality,
            "cumulative_start": round(cumulative, 3),
            "antardashas": antardashas[:3],  # top 3 for display
        })
        cumulative += effective_years

    return {
        "system": "Tara Dasha",
        "total_years": 120,
        "janma_nakshatra": janma_nak,
        "specialization": "Daily/micro-level transits, exact event timing within larger cycles",
        "periods": periods,
    }


# ── Master Eligibility Check ──────────────────────────────────────────────────

def check_all_conditional_eligibility(
        is_daytime: bool = True,
        paksha: str = "shukla",
        lagna_hora: str = "sun",
        d1_lagna_sign: str = "Aries",
        d9_lagna_sign: str = "Aries",
        d12_lagna_sign: str = "Aries",
        lagna_lord: str = "MARS",
        seventh_lord: str = "VENUS",
        tenth_lord: str = "SATURN",
        planet_houses: Optional[Dict[str, int]] = None,
) -> Dict[str, Dict]:
    """
    Check eligibility for all 7 conditional dasha systems simultaneously.
    Returns dict of {system_name: {eligible, reason}}.
    """
    if planet_houses is None:
        planet_houses = {}

    return {
        "Shodashottari": check_shodashottari_eligible(is_daytime, paksha, lagna_hora),
        "Dwadasottari": check_dwadasottari_eligible(d9_lagna_sign),
        "Panchottari": check_panchottari_eligible(d1_lagna_sign, d12_lagna_sign),
        "Shatabdika": check_shatabdika_eligible(d1_lagna_sign, d9_lagna_sign),
        "Chaturaashiti": check_chaturaashiti_eligible(tenth_lord, planet_houses),
        "Dwisaptati": check_dwisaptati_eligible(lagna_lord, planet_houses, seventh_lord),
        "Shat_Trimsa": check_shat_trimsa_eligible(is_daytime, lagna_hora),
    }
