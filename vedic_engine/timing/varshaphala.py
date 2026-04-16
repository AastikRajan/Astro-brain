"""
Tajika Varshaphala (Annual Chart / Solar Return) Engine.

Computes (File-3 complete spec):
  1. Solar return moment (Sun returns to natal sidereal longitude)
  2. Muntha – progressed Lagna sign, longitude & house interpretations
  3. Pancha-Vargeeya Bala (PVB) – 5-factor Tajika planetary strength
  4. Varsha Pati (Varshesha) – correct Pancha-Adhikari candidates + Tri-Rashi
  5. Full 16 Tajika Yogas with house-count aspect system (Friendly/Inimical/Neutral)
  6. 16 Sahams (Arabic Parts) with day/night inversion
  7. Mudda Dasha – intra-year timing (360-day base)
  8. Static analysis entry-point for the engine pipeline

Reference:
  * "Tajika Shastra" by Neelakantha
  * "Annual Horoscopy" by Nagarajan
  * File-3 research spec: Algorithmic Vedic Astrology Engine Specification-3.md
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple

# ─── Tajika Deepthamsha (orb table by planet) ─────────────────────────────────
# Sun=15°, Moon=12°, Jupiter/Saturn=9°, Mars=8°, Venus/Mercury=7°
TAJIKA_ORBS: Dict[str, float] = {
    "SUN": 15.0, "MOON": 12.0,
    "JUPITER": 9.0, "SATURN": 9.0,
    "MARS": 8.0, "VENUS": 7.0, "MERCURY": 7.0,
    "RAHU": 8.0, "KETU": 8.0,
}

# ─── House-count categories for Tajika aspects ────────────────────────────────
# Distance measured from planet A's sign to planet B's sign (1-based).
# Friendly houses = mutual beneficial aspect (3rd,5th,9th,11th from each other)
# Inimical houses = mutual inimical aspect (1st,4th,7th,10th)
# Neutral   houses = NO Tajika aspect (2nd,6th,8th,12th)
FRIENDLY_HOUSES  = {3, 5, 9, 11}
INIMICAL_HOUSES  = {1, 4, 7, 10}
NEUTRAL_HOUSES   = {2, 6, 8, 12}

# ─── Sign lord mapping (0=Aries … 11=Pisces) ──────────────────────────────────
_SIGN_LORDS: Dict[int, str] = {
    0: "MARS",    1: "VENUS",   2: "MERCURY", 3: "MOON",
    4: "SUN",     5: "MERCURY", 6: "VENUS",   7: "MARS",
    8: "JUPITER", 9: "SATURN",  10: "SATURN", 11: "JUPITER",
}

# ─── Natural friendship table ──────────────────────────────────────────────────
_FRIENDS: Dict[str, frozenset] = {
    "SUN":     frozenset({"MOON", "MARS", "JUPITER"}),
    "MOON":    frozenset({"SUN", "MERCURY"}),
    "MARS":    frozenset({"SUN", "MOON", "JUPITER"}),
    "MERCURY": frozenset({"SUN", "VENUS"}),
    "JUPITER": frozenset({"SUN", "MOON", "MARS"}),
    "VENUS":   frozenset({"MERCURY", "SATURN"}),
    "SATURN":  frozenset({"MERCURY", "VENUS"}),
}
_ENEMIES: Dict[str, frozenset] = {
    "SUN":     frozenset({"VENUS", "SATURN"}),
    "MOON":    frozenset(),
    "MARS":    frozenset({"MERCURY"}),
    "MERCURY": frozenset({"MOON"}),
    "JUPITER": frozenset({"MERCURY", "VENUS"}),
    "VENUS":   frozenset({"SUN", "MOON"}),
    "SATURN":  frozenset({"SUN", "MOON", "MARS"}),
}


def _friendship(p: str, q: str) -> str:
    """Return 'own'/'friend'/'neutral'/'enemy' from p's perspective toward q."""
    if p.upper() == q.upper():
        return "own"
    pu, qu = p.upper(), q.upper()
    if qu in _FRIENDS.get(pu, frozenset()):
        return "friend"
    if qu in _ENEMIES.get(pu, frozenset()):
        return "enemy"
    return "neutral"


def _sign_lord(sign_idx: int) -> str:
    return _SIGN_LORDS[sign_idx % 12]


# ─── Helper: angular arithmetic ───────────────────────────────────────────────

def _angular_diff(lon_a: float, lon_b: float) -> float:
    """Signed arc from lon_b to lon_a (positive = a ahead of b); range [-180,180]."""
    d = (lon_a - lon_b) % 360.0
    return d if d <= 180.0 else d - 360.0


def _house_count(from_sign: int, to_sign: int) -> int:
    """Count of houses from from_sign to to_sign (1-based, 1–12)."""
    return ((to_sign - from_sign) % 12) + 1


# ═══════════════════════════════════════════════════════════════════════════════
# 1. TAJIKA HOUSE-COUNT ASPECT SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

# Map house count → ideal degree separation for within-orb check
_HOUSE_IDEAL_DEG: Dict[int, float] = {
    1: 0.0, 4: 90.0, 7: 180.0, 10: 90.0,   # inimical
    3: 60.0, 5: 120.0, 9: 120.0, 11: 60.0, # friendly
}


def tajika_aspect(planet_a: str, lon_a: float,
                  planet_b: str, lon_b: float) -> Dict[str, Any]:
    """
    Determine whether two planets share a Tajika aspect.

    Uses HOUSE-COUNT method (not simple degree arcs):
      combined orb = (orb_a + orb_b) / 2
      category: Friendly / Inimical / Neutral (no aspect)

    Returns dict:
        {connected, category, house_count_fwd, house_count_rev,
         separation_deg, combined_orb, within_orb}
    """
    orb_a = TAJIKA_ORBS.get(planet_a.upper(), 8.0)
    orb_b = TAJIKA_ORBS.get(planet_b.upper(), 8.0)
    combined_orb = (orb_a + orb_b) / 2.0

    sign_a = int(lon_a / 30) % 12
    sign_b = int(lon_b / 30) % 12

    fwd_count = _house_count(sign_a, sign_b)  # from A to B
    rev_count = _house_count(sign_b, sign_a)  # from B to A

    fwd_cat = ("friendly" if fwd_count in FRIENDLY_HOUSES else
               "inimical" if fwd_count in INIMICAL_HOUSES else "neutral")
    rev_cat = ("friendly" if rev_count in FRIENDLY_HOUSES else
               "inimical" if rev_count in INIMICAL_HOUSES else "neutral")

    # Aspect exists if either direction is non-neutral
    connected = (fwd_cat != "neutral") or (rev_cat != "neutral")
    category  = fwd_cat if fwd_cat != "neutral" else rev_cat

    sep_deg = abs(_angular_diff(lon_a, lon_b))
    ideal   = _HOUSE_IDEAL_DEG.get(fwd_count,
              _HOUSE_IDEAL_DEG.get(rev_count, -1.0))
    within_orb = (ideal >= 0.0 and abs(sep_deg - ideal) <= combined_orb)

    return {
        "connected":       connected,
        "category":        category,
        "house_count_fwd": fwd_count,
        "house_count_rev": rev_count,
        "separation_deg":  round(sep_deg, 3),
        "combined_orb":    combined_orb,
        "within_orb":      within_orb,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PANCHA-VARGEEYA BALA (PVB) — 5-factor Tajika planetary strength
# ═══════════════════════════════════════════════════════════════════════════════

# Debilitation longitudes (absolute degrees 0–360)
DEBILITATION_DEGREES: Dict[str, float] = {
    "SUN": 180.0, "MOON": 216.0, "MARS": 118.0, "MERCURY": 345.0,
    "JUPITER": 270.0, "VENUS": 177.0, "SATURN": 0.0,
    "RAHU": 270.0, "KETU": 90.0,
}

# Exaltation sign index (0=Aries … 11=Pisces)
EXALT_SIGN: Dict[str, int] = {
    "SUN": 0, "MOON": 1, "MARS": 9, "MERCURY": 5,
    "JUPITER": 3, "VENUS": 11, "SATURN": 6, "RAHU": 1, "KETU": 7,
}

# Debilitation sign index
DEBIL_SIGN: Dict[str, int] = {
    "SUN": 6, "MOON": 7, "MARS": 3, "MERCURY": 11,
    "JUPITER": 9, "VENUS": 5, "SATURN": 0, "RAHU": 7, "KETU": 1,
}

# Own signs (planet → list of sign indices)
OWN_SIGNS: Dict[str, List[int]] = {
    "SUN": [4], "MOON": [3], "MARS": [0, 7],
    "MERCURY": [2, 5], "JUPITER": [8, 11],
    "VENUS": [1, 6], "SATURN": [9, 10],
}

# Egyptian Bounds (Hudda): [sign_idx] = [(upper_degree, planet_lord), ...]
_HUDDA_BOUNDS: Dict[int, List[Tuple[float, str]]] = {
    0:  [(6,"JUPITER"),(12,"VENUS"),(20,"MERCURY"),(25,"MARS"),(30,"SATURN")],
    1:  [(8,"VENUS"),(14,"MERCURY"),(22,"JUPITER"),(27,"SATURN"),(30,"MARS")],
    2:  [(6,"MERCURY"),(12,"JUPITER"),(17,"VENUS"),(24,"MARS"),(30,"SATURN")],
    3:  [(7,"MARS"),(13,"VENUS"),(19,"MERCURY"),(26,"JUPITER"),(30,"SATURN")],
    4:  [(6,"SATURN"),(11,"MERCURY"),(18,"VENUS"),(24,"JUPITER"),(30,"MARS")],
    5:  [(7,"MERCURY"),(17,"VENUS"),(21,"JUPITER"),(28,"SATURN"),(30,"MARS")],
    6:  [(6,"SATURN"),(14,"VENUS"),(21,"MERCURY"),(28,"JUPITER"),(30,"MARS")],
    7:  [(7,"MARS"),(11,"VENUS"),(19,"MERCURY"),(24,"JUPITER"),(30,"SATURN")],
    8:  [(12,"JUPITER"),(17,"VENUS"),(21,"MERCURY"),(26,"SATURN"),(30,"MARS")],
    9:  [(7,"MERCURY"),(14,"JUPITER"),(22,"VENUS"),(26,"SATURN"),(30,"MARS")],
    10: [(7,"SATURN"),(13,"MERCURY"),(20,"VENUS"),(25,"JUPITER"),(30,"MARS")],
    11: [(12,"VENUS"),(16,"JUPITER"),(19,"MERCURY"),(28,"MARS"),(30,"SATURN")],
}

# Tajika Drekkana sequence: cycle of 7 planets for decan lords
_TAJIKA_DREK_SEQ: List[str] = [
    "MARS","MERCURY","JUPITER","VENUS","SATURN","SUN","MOON"
]

# Scoring tables
_KSHETRA_SCORES = {"exaltation": 20, "own": 20, "friend": 15,
                   "neutral": 10, "enemy": 5, "debilitation": 5}
_HUDDA_SCORES    = {"own": 15, "friend": 12, "neutral": 9, "enemy": 6}
_DREKKANA_SCORES = {"own": 15, "friend": 9,  "neutral": 6, "enemy": 3}
_NAVAMSHA_SCORES = {"own": 10, "friend": 8,  "neutral": 6, "enemy": 4}


def _get_kshetra_bala(planet: str, longitude: float) -> float:
    """Kshetra Bala: sign-dignity score (max 20)."""
    sign = int(longitude / 30) % 12
    p = planet.upper()
    if sign == EXALT_SIGN.get(p, -1):
        return 20.0
    if sign == DEBIL_SIGN.get(p, -99):
        return 5.0
    if sign in OWN_SIGNS.get(p, []):
        return 20.0
    rel = _friendship(_sign_lord(sign), p)
    return _KSHETRA_SCORES.get(rel, 10.0)


def _get_uchcha_bala(planet: str, longitude: float) -> float:
    """Uchcha Bala: exaltation proximity score (max 20)."""
    debil_lon = DEBILITATION_DEGREES.get(planet.upper(), 0.0)
    dist = (longitude - debil_lon) % 360.0
    return min(20.0, (dist / 180.0) * 20.0)


def _get_hudda_lord(longitude: float) -> str:
    """Return the Egyptian Bounds lord for the given absolute longitude."""
    sign = int(longitude / 30) % 12
    deg  = longitude % 30.0
    for end_deg, lord in _HUDDA_BOUNDS.get(sign, []):
        if deg < end_deg:
            return lord
    return "JUPITER"


def _get_hudda_bala(planet: str, longitude: float) -> float:
    """Hudda Bala: Egyptian Bounds lord relationship score (max 15)."""
    lord = _get_hudda_lord(longitude)
    rel  = _friendship(lord, planet.upper()) if lord != planet.upper() else "own"
    return float(_HUDDA_SCORES.get(rel, 9))


def _get_drekkana_bala(planet: str, longitude: float) -> float:
    """Drekkana Bala: Tajika decan lord score (max 15)."""
    sign = int(longitude / 30) % 12
    drek = int((longitude % 30.0) / 10.0)  # 0,1,2
    lord = _TAJIKA_DREK_SEQ[(sign * 3 + drek) % 7]
    rel  = _friendship(lord, planet.upper()) if lord != planet.upper() else "own"
    return float(_DREKKANA_SCORES.get(rel, 6))


def _get_navamsha_sign(longitude: float) -> int:
    """Navamsha (D9) sign index for a longitude."""
    sign = int(longitude / 30) % 12
    nav  = int((longitude % 30.0) / (30.0 / 9.0))
    # Start: movable=0(Aries), fixed=9(Capricorn), dual=6(Libra)
    start = {0:0,3:0,6:0,9:0, 1:9,4:9,7:9,10:9, 2:6,5:6,8:6,11:6}[sign]
    return (start + nav) % 12


def _get_navamsha_bala(planet: str, longitude: float) -> float:
    """Navamsha Bala: D9 dignity score (max 10)."""
    nav_sign = _get_navamsha_sign(longitude)
    p = planet.upper()
    if nav_sign == EXALT_SIGN.get(p, -1) or nav_sign in OWN_SIGNS.get(p, []):
        return 10.0
    rel = _friendship(_sign_lord(nav_sign), p)
    return float(_NAVAMSHA_SCORES.get(rel, 6))


def compute_pvb(planet: str, longitude: float) -> Dict[str, Any]:
    """
    Compute Pancha-Vargeeya Bala (5-factor Tajika strength).

    Components (max):
        Kshetra  (sign dignity)   — 20
        Uchcha   (exaltation)     — 20
        Hudda    (bounds)         — 15
        Drekkana (Tajika decan)   — 15
        Navamsha (D9 dignity)     — 10
        Raw total                 — 80  → normalised to 20 (÷4)

    Thresholds: PVB ≥ 15 = Parakrami | PVB ≤ 5 = Nirbali
    """
    k = _get_kshetra_bala(planet, longitude)
    u = _get_uchcha_bala(planet, longitude)
    h = _get_hudda_bala(planet, longitude)
    d = _get_drekkana_bala(planet, longitude)
    n = _get_navamsha_bala(planet, longitude)

    raw   = k + u + h + d + n
    total = round(raw / 4.0, 2)

    tier = "Parakrami" if total >= 15 else "Madhyama" if total >= 8 else "Nirbali"

    return {
        "kshetra": round(k,2), "uchcha": round(u,2),
        "hudda": round(h,2), "drekkana": round(d,2), "navamsha": round(n,2),
        "pvb_raw": round(raw,2), "pvb": total, "tier": tier,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. MUNTHA (Annual Progressed Lagna)
# ═══════════════════════════════════════════════════════════════════════════════

_SIGN_NAMES = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
]

# Classical house meanings for Muntha position from Varsha Lagna
MUNTHA_HOUSE_MEANINGS: Dict[int, str] = {
    1:  "Good vitality — Muntha in Lagna augments health and self-expression",
    2:  "Moderate gains — wealth and speech domains show mixed results",
    3:  "Courage and short journeys — siblings may bring news",
    4:  "Domestic strife and possible illness — home affairs troubled",
    5:  "Success, wisdom, children — creative efforts rewarded",
    6:  "Disease, debt, enemies — health vigilance required",
    7:  "Volatile partnerships, litigation, possible illness",
    8:  "Chronic crises, mortality risks — major transformations",
    9:  "Desires fulfilled, dharma elevation — spiritual gains",
    10: "Career elevation — professional recognition and power",
    11: "Financial gains and fulfilment of wishes",
    12: "Expenditures, hospitalisation, isolation — foreign travels possible",
}


def compute_muntha(
    natal_lagna_sign: int,
    years_elapsed:    int,
    months_elapsed:   int = 0,
    days_elapsed:     int = 0,
    days_in_month:    int = 30,
) -> Dict[str, Any]:
    """
    Compute Muntha sign and longitude.

    Rule: 1 sign per completed year; 1°/month sub-progression.
    natal_lagna_sign: 0=Aries … 11=Pisces
    """
    total_deg = (years_elapsed  * 30.0
               + months_elapsed * (30.0 / 12.0)
               + days_elapsed   * (30.0 / 360.0))

    muntha_lon  = (natal_lagna_sign * 30.0 + total_deg) % 360.0
    muntha_sign = int(muntha_lon / 30.0) % 12

    return {
        "sign_idx":       muntha_sign,
        "sign":           _SIGN_NAMES[muntha_sign],
        "longitude":      round(muntha_lon, 3),
        "degree_in_sign": round(muntha_lon % 30.0, 3),
        "lord":           _sign_lord(muntha_sign),
    }


def get_muntha_house(muntha_sign: int, varsha_lagna_sign: int) -> int:
    """House number (1–12) of Muntha counted from Varsha Lagna."""
    return ((muntha_sign - varsha_lagna_sign) % 12) + 1


def get_muntha_interpretation(muntha_sign: int, varsha_lagna_sign: int) -> str:
    h = get_muntha_house(muntha_sign, varsha_lagna_sign)
    return f"House {h}: {MUNTHA_HOUSE_MEANINGS.get(h, '')}"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. VARSHA PATI — Pancha-Adhikari system with PVB + Tri-Rashi
# ═══════════════════════════════════════════════════════════════════════════════

# Tri-Rashi Pati (classical matrix): annual lagna sign × day/night
_TRI_RASHI_DAY: Dict[int, str] = {
    0:"SUN",  1:"VENUS",   2:"SATURN",  3:"VENUS",   4:"JUPITER", 5:"MOON",
    6:"MERCURY", 7:"MARS", 8:"SATURN",  9:"MARS",   10:"JUPITER",11:"MOON",
}
_TRI_RASHI_NIGHT: Dict[int, str] = {
    0:"JUPITER", 1:"MOON",    2:"MERCURY", 3:"MARS",   4:"SUN",     5:"VENUS",
    6:"SATURN",  7:"VENUS",   8:"JUPITER", 9:"MARS",  10:"JUPITER",11:"MOON",
}


def _planet_aspects_lagna(planet_lon: float, lagna_sign: int) -> bool:
    """True if planet casts a Tajika aspect on the Lagna sign."""
    p_sign = int(planet_lon / 30) % 12
    fwd = _house_count(p_sign, lagna_sign)
    rev = _house_count(lagna_sign, p_sign)
    return (fwd in FRIENDLY_HOUSES or fwd in INIMICAL_HOUSES or
            rev in FRIENDLY_HOUSES or rev in INIMICAL_HOUSES)


def compute_varsha_pati(
    natal_lagna_sign:  int,
    varsha_lagna_sign: int,
    varsha_lagna_lon:  float,
    muntha_sign:       int,
    planet_lons:       Dict[str, float],
    is_day_return:     bool = True,
) -> Dict[str, Any]:
    """
    Determine Varsha Pati from 5 Pancha-Adhikari candidates.

    Candidates:
      1. Janma Lagna Pati  — lord of natal lagna sign
      2. Varsha Lagna Pati — lord of annual lagna sign
      3. Muntha Pati       — lord of Muntha sign
      4. Dina-Ratri Pati   — day→Sun's sign lord; night→Moon's sign lord
      5. Tri-Rashi Pati    — from Tri-Rashi matrix

    Selection: highest PVB among those aspecting annual Lagna.
    Moon chosen only as last resort.
    Thresholds: PVB ≥ 15 = Parakrami; PVB ≤ 5 = Nirbali.
    """
    sun_sign  = int(planet_lons.get("SUN",  0.0) / 30) % 12
    moon_sign = int(planet_lons.get("MOON", 0.0) / 30) % 12

    dina_ratri = _sign_lord(sun_sign) if is_day_return else _sign_lord(moon_sign)
    tri_rashi  = (_TRI_RASHI_DAY if is_day_return else _TRI_RASHI_NIGHT).get(
                  varsha_lagna_sign % 12, "JUPITER")

    candidates = [
        ("Janma Lagna Pati",  _sign_lord(natal_lagna_sign)),
        ("Varsha Lagna Pati", _sign_lord(varsha_lagna_sign)),
        ("Muntha Pati",       _sign_lord(muntha_sign)),
        ("Dina-Ratri Pati",   dina_ratri),
        ("Tri-Rashi Pati",    tri_rashi),
    ]

    pvb_results: List[Dict[str, Any]] = []
    for role, planet in candidates:
        lon = planet_lons.get(planet, 0.0)
        pvb = compute_pvb(planet, lon)
        pvb_results.append({
            "role": role, "planet": planet,
            "pvb": pvb["pvb"], "tier": pvb["tier"],
            "aspects_lagna": _planet_aspects_lagna(lon, varsha_lagna_sign),
            "pvb_detail": pvb,
        })

    aspecting  = [r for r in pvb_results if r["aspects_lagna"]]
    pool       = aspecting if aspecting else pvb_results
    non_moon   = [r for r in pool if r["planet"] != "MOON"]
    final_pool = non_moon if non_moon else pool
    final_pool.sort(key=lambda r: -r["pvb"])
    chosen     = final_pool[0]

    return {
        "varsha_pati":   chosen["planet"],
        "role":          chosen["role"],
        "pvb":           chosen["pvb"],
        "tier":          chosen["tier"],
        "pvb_detail":    chosen["pvb_detail"],
        "candidates":    pvb_results,
        "moon_exception": not bool(non_moon and pool),
    }


# ─── Backward-compat alias ────────────────────────────────────────────────────
def compute_varshesha(annual_lagna_sign, annual_lagna_lon, muntha_sign,
                      natal_lagna_sign, annual_planet_lons,
                      shadbala_scores=None):
    """Legacy alias → compute_varsha_pati."""
    result = compute_varsha_pati(
        natal_lagna_sign=natal_lagna_sign,
        varsha_lagna_sign=annual_lagna_sign,
        varsha_lagna_lon=annual_lagna_lon,
        muntha_sign=muntha_sign,
        planet_lons=annual_planet_lons,
    )
    result["varshesha"] = result["varsha_pati"]
    result["reason"]    = result["role"]
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# 5. FULL 16 TAJIKA YOGAS — house-count based aspect system
# ═══════════════════════════════════════════════════════════════════════════════

def _is_itthasala(pa: str, la: float, sa: float,
                  pb: str, lb: float, sb: float) -> Tuple[bool, float]:
    """
    Itthasala check: faster planet applying toward slower within combined orb.
    Returns (is_itthasala, signed_residual).
    residual < 0 = still applying; > 0 = already separated.
    """
    asp = tajika_aspect(pa, la, pb, lb)
    if not asp["connected"]:
        return False, 0.0

    # Determine ideal degree for this house relationship
    hf = asp["house_count_fwd"]
    ideal = _HOUSE_IDEAL_DEG.get(hf, _HOUSE_IDEAL_DEG.get(asp["house_count_rev"], -1.0))
    if ideal < 0:
        return False, 0.0

    sep = asp["separation_deg"]
    residual = sep - ideal           # > 0 = beyond ideal, < 0 = not yet there
    if abs(residual) > asp["combined_orb"]:
        return False, residual

    # Faster applies toward exact IF it is still short of ideal
    rel_speed = sa - sb
    if rel_speed > 0:
        # a faster: applying when lon_a hasn't yet reached exact separation
        applying = (residual < 0) if la > lb else (residual < 0)
    else:
        applying = (residual < 0)

    return applying, residual


def detect_tajika_yogas(
    planet_lons:   Dict[str, float],
    planet_speeds: Dict[str, float],
    lagna_lon:     float,
    lagnesh:       str,
) -> List[Dict[str, Any]]:
    """
    Detect all 16 Tajika Yogas in an annual chart.

    Parameters
    ----------
    planet_lons   : Sidereal longitudes of all planets.
    planet_speeds : Daily motion (negative = retrograde).
    lagna_lon     : Annual Ascendant longitude.
    lagnesh       : Lord of the annual Lagna sign.

    Returns list of yoga dicts: {yoga, description, planets, quality}.
    """
    yogas: List[Dict[str, Any]] = []
    planets = list(planet_lons.keys())
    lagna_sign = int(lagna_lon / 30) % 12

    def _add(yoga: str, desc: str, involv: List[str], quality: str) -> None:
        yogas.append({"yoga": yoga, "description": desc,
                      "planets": involv, "quality": quality})

    # House of each planet from Lagna
    def _house(p: str) -> int:
        return ((int(planet_lons[p] / 30) % 12 - lagna_sign) % 12) + 1

    planet_houses = {p: _house(p) for p in planets if p in planet_lons}

    # ── 1. Ikkavala ─────────────────────────────────────────────────────────────
    if planet_houses and all(h not in {3,6,9,12} for h in planet_houses.values()):
        _add("Ikkavala",
             "All planets in Kendra/Panaphara — fortune and success for the year",
             list(planet_houses.keys()), "very_good")

    # ── 2. Induvara ──────────────────────────────────────────────────────────────
    if planet_houses and all(h in {3,6,9,12} for h in planet_houses.values()):
        _add("Induvara",
             "All planets in Apoklimas — frustration, failure, wasted efforts",
             list(planet_houses.keys()), "very_bad")

    # Collect all Itthasala pairs first
    itthasala_pairs: List[Tuple[str, str, float]] = []
    for i, pa in enumerate(planets):
        for pb in planets[i+1:]:
            if pa not in planet_lons or pb not in planet_lons:
                continue
            sa, sb = planet_speeds.get(pa, 0.0), planet_speeds.get(pb, 0.0)
            # Determine faster
            if abs(sa) >= abs(sb):
                faster, slower, sf, ss = pa, pb, sa, sb
                lf, ls = planet_lons[pa], planet_lons[pb]
            else:
                faster, slower, sf, ss = pb, pa, sb, sa
                lf, ls = planet_lons[pb], planet_lons[pa]
            is_itt, sep = _is_itthasala(faster, lf, sf, slower, ls, ss)
            if is_itt:
                itthasala_pairs.append((faster, slower, sep))

    # ── 3–5. Itthasala / Tambira / Rodha ─────────────────────────────────────────
    for faster, slower, sep in itthasala_pairs:
        lf = planet_lons[faster]
        sf = planet_speeds.get(faster, 0.0)
        ss = planet_speeds.get(slower, 0.0)

        if sf < 0 or ss < 0:
            # Retrograde blocks completion → Rodha
            _add("Rodha",
                 f"{faster}→{slower}: Retrograde prevents completion of Itthasala",
                 [faster, slower], "bad")
            continue

        # Tambira: faster in last 3° of sign
        if (lf % 30.0) >= 27.0:
            _add("Tambira",
                 f"{faster}→{slower}: Last-minute applying (within final 3° of sign)",
                 [faster, slower], "mixed")
        else:
            _add("Itthasala",
                 f"{faster} applying to {slower} — success for {abs(sep):.1f}° residual",
                 [faster, slower], "good")

    # ── 4. Muthasila ─────────────────────────────────────────────────────────────
    for faster, slower, sep in itthasala_pairs:
        if abs(sep) < 1.0:
            _add("Muthasila",
                 f"{faster}–{slower}: Near-exact mutual aspect ({abs(sep):.2f}°) — instant success",
                 [faster, slower], "very_good")

    # ── 5. Ishrafa ────────────────────────────────────────────────────────────────
    for i, pa in enumerate(planets):
        for pb in planets[i+1:]:
            if pa not in planet_lons or pb not in planet_lons:
                continue
            asp = tajika_aspect(pa, planet_lons[pa], pb, planet_lons[pb])
            if not asp["connected"] or not asp["within_orb"]:
                continue
            sa, sb = planet_speeds.get(pa, 0.0), planet_speeds.get(pb, 0.0)
            faster, slower = (pa, pb) if abs(sa) >= abs(sb) else (pb, pa)
            lf, ls = planet_lons[faster], planet_lons[slower]
            sf, ss = planet_speeds.get(faster, 0.0), planet_speeds.get(slower, 0.0)
            is_itt, _ = _is_itthasala(faster, lf, sf, slower, ls, ss)
            already_itt = any((a == faster and b == slower) or (a == slower and b == faster)
                              for a, b, _ in itthasala_pairs)
            if not is_itt and not already_itt:
                _add("Ishrafa",
                     f"{faster} separating from {slower} — opportunity closed, failure likely",
                     [faster, slower], "bad")

    # ── 6. Nakta (Light Transfer) ─────────────────────────────────────────────────
    checked_nakta: set = set()
    for pa in planets:
        for pb in planets:
            if pa == pb or pa not in planet_lons or pb not in planet_lons:
                continue
            if tajika_aspect(pa, planet_lons[pa], pb, planet_lons[pb])["connected"]:
                continue  # already direct
            for pc in planets:
                if pc in {pa, pb} or pc not in planet_lons:
                    continue
                key = tuple(sorted([pa, pb, pc]))
                if key in checked_nakta:
                    continue
                sc, sa, sb = (planet_speeds.get(pc,0.0), planet_speeds.get(pa,0.0),
                              planet_speeds.get(pb,0.0))
                if (tajika_aspect(pc,planet_lons[pc],pa,planet_lons[pa])["connected"] and
                        tajika_aspect(pc,planet_lons[pc],pb,planet_lons[pb])["connected"] and
                        abs(sc) >= abs(sa) and abs(sc) >= abs(sb)):
                    checked_nakta.add(key)
                    _add("Nakta",
                         f"{pc} transfers light between {pa} and {pb} — 3rd-party mediates",
                         [pa, pc, pb], "good")

    # ── 7. Yamaya (Collection of Light) ──────────────────────────────────────────
    checked_yam: set = set()
    for i, pa in enumerate(planets):
        for j, pb in enumerate(planets):
            if i >= j:
                continue
            for pc in planets:
                if pc in {pa, pb} or pc not in planet_lons or pa not in planet_lons or pb not in planet_lons:
                    continue
                key = tuple(sorted([pa, pb, pc]))
                if key in checked_yam:
                    continue
                lc, la, lb = planet_lons[pc], planet_lons[pa], planet_lons[pb]
                sc, sa, sb = (planet_speeds.get(pc,0.0), planet_speeds.get(pa,0.0),
                              planet_speeds.get(pb,0.0))
                ita, _ = _is_itthasala(pa, la, sa, pc, lc, sc)
                itb, _ = _is_itthasala(pb, lb, sb, pc, lc, sc)
                if ita and itb and abs(sc) < abs(sa) and abs(sc) < abs(sb):
                    checked_yam.add(key)
                    _add("Yamaya",
                         f"{pa} and {pb} collecting light toward slow {pc} — success after delays",
                         [pa, pb, pc], "good")

    # ── 8. Manau (Obstruction in Itthasala) ──────────────────────────────────────
    malefics = {"SATURN","MARS","RAHU","KETU","SUN"}
    for faster, slower, _ in itthasala_pairs:
        lf, ls = planet_lons[faster], planet_lons[slower]
        diff_fs = _angular_diff(ls, lf)
        for interp in planets:
            if interp in {faster, slower} or interp not in planet_lons:
                continue
            diff_fi = _angular_diff(planet_lons[interp], lf)
            if (diff_fs * diff_fi > 0) and abs(diff_fi) < abs(diff_fs):
                if interp.upper() in malefics:
                    _add("Manau",
                         f"Malefic {interp} obstructs {faster}→{slower} — destroyed by opponents",
                         [faster, interp, slower], "bad")
                    break

    # ── 9 & 10. Kamboola / Gairi-Kamboola ──────────────────────────────────────
    moon_lon = planet_lons.get("MOON")
    moon_spd = planet_speeds.get("MOON", 13.0)
    if moon_lon is not None:
        moon_afflicted = any(
            tajika_aspect("MOON", moon_lon, mp, planet_lons[mp])["connected"]
            and mp.upper() in malefics
            for mp in planets if mp in planet_lons and mp != "MOON"
        )
        for faster, slower, sep in itthasala_pairs:
            asp_ma = tajika_aspect("MOON", moon_lon, faster, planet_lons[faster])
            asp_mb = tajika_aspect("MOON", moon_lon, slower, planet_lons[slower])
            if asp_ma["connected"] or asp_mb["connected"]:
                if not moon_afflicted:
                    _add("Kamboola",
                         f"Moon joins {faster}–{slower} Itthasala — highly successful",
                         ["MOON", faster, slower], "very_good")
                else:
                    _add("Gairi Kamboola",
                         f"Afflicted Moon neutralises {faster}–{slower} Itthasala — success cancelled",
                         ["MOON", faster, slower], "bad")

    # ── 11. Khallasara (Total Stagnation) ────────────────────────────────────────
    if lagnesh in planet_lons:
        lagnesh_active = any(pa == lagnesh or pb == lagnesh
                             for pa, pb, _ in itthasala_pairs)
        if not lagnesh_active:
            _add("Khallasara",
                 f"Lagnesh {lagnesh} has no Itthasala — total stagnation for the year",
                 [lagnesh], "very_bad")

    # ── 13. Dutthottha (Rescuer) ──────────────────────────────────────────────────
    for faster, slower, _ in itthasala_pairs:
        pva = compute_pvb(faster, planet_lons[faster])["pvb"]
        pvb = compute_pvb(slower, planet_lons[slower])["pvb"]
        if pva <= 5 and pvb <= 5:
            for pr in planets:
                if pr in {faster, slower} or pr not in planet_lons:
                    continue
                if (compute_pvb(pr, planet_lons[pr])["pvb"] >= 15 and
                        tajika_aspect(pr,planet_lons[pr],faster,planet_lons[faster])["connected"]):
                    _add("Dutthottha",
                         f"Strong {pr} rescues weak {faster}+{slower} — unexpected helper",
                         [faster, slower, pr], "good")
                    break

    # ── 14. Duttho (Mutual Reception) ────────────────────────────────────────────
    for i, pa in enumerate(planets):
        for pb in planets[i+1:]:
            if pa not in planet_lons or pb not in planet_lons:
                continue
            sa_sign = int(planet_lons[pa] / 30) % 12
            sb_sign = int(planet_lons[pb] / 30) % 12
            if (_sign_lord(sa_sign) == pb and _sign_lord(sb_sign) == pa):
                already_itt = any((a == pa and b == pb) or (a == pb and b == pa)
                                  for a, b, _ in itthasala_pairs)
                if not already_itt:
                    _add("Duttho",
                         f"{pa}–{pb}: Mutual sign exchange without Itthasala — success by cooperation",
                         [pa, pb], "good")

    # ── 16. Kuttha (Rapid Elevation) ─────────────────────────────────────────────
    for pa in planets:
        if pa not in planet_lons:
            continue
        if planet_houses.get(pa) == 1:  # In Lagna
            for pb in planets:
                if pb == pa or pb not in planet_lons:
                    continue
                if planet_houses.get(pb) in {1,2,4,5,7,8,10,11}:
                    if tajika_aspect(pb,planet_lons[pb],pa,planet_lons[pa])["connected"]:
                        _add("Kuttha",
                             f"{pa} in Lagna aspected by {pb} (house {planet_houses[pb]}) — rapid elevation",
                             [pa, pb], "good")

    # ── 17. Duphali-Kuttha (Catastrophe) ─────────────────────────────────────────
    for faster, slower, _ in itthasala_pairs:
        hf = planet_houses.get(faster, 0)
        hs = planet_houses.get(slower, 0)
        if hf in {6,8,12} and hs in {6,8,12}:
            _add("Duphali-Kuttha",
                 f"{faster}(H{hf})–{slower}(H{hs}): Itthasala between dusthana planets — catastrophic failure",
                 [faster, slower], "very_bad")

    # ── 18. Trikhala (Stressful Resolution) ──────────────────────────────────────
    benefics_set = {"JUPITER","VENUS","MOON","MERCURY"}
    weak_malefics = [p for p in planets
                     if p in planet_lons and p.upper() in malefics
                     and compute_pvb(p, planet_lons[p])["pvb"] <= 8]
    strong_benefs = [p for p in planets
                     if p in planet_lons and p.upper() in benefics_set
                     and compute_pvb(p, planet_lons[p])["pvb"] >= 12]
    if len(weak_malefics) >= 2 and strong_benefs:
        sv = strong_benefs[0]
        if all(tajika_aspect(sv,planet_lons[sv],af,planet_lons[af])["connected"]
               for af in weak_malefics[:2]):
            _add("Trikhala",
                 f"Strong {sv} resolves pressure from {','.join(weak_malefics[:2])} — stressful but resolved",
                 weak_malefics[:2] + [sv], "mixed")

    return yogas


# Legacy two-planet classifier (backward-compat)
def classify_tajika_yoga(planet_a: str, lon_a: float, speed_a: float,
                         planet_b: str, lon_b: float, speed_b: float,
                         ) -> Optional[Dict[str, Any]]:
    """Backward-compatible pairwise yoga detection."""
    result = detect_tajika_yogas(
        {planet_a: lon_a, planet_b: lon_b},
        {planet_a: speed_a, planet_b: speed_b},
        lagna_lon=0.0, lagnesh=planet_a,
    )
    return result[0] if result else None


def compute_all_tajika_yogas(
    planet_lons:   Dict[str, float],
    planet_speeds: Dict[str, float],
    lagna_lon:     float = 0.0,
    lagnesh:       str   = "SUN",
) -> List[Dict[str, Any]]:
    """Full yoga detection (all planets). Delegates to detect_tajika_yogas."""
    return detect_tajika_yogas(planet_lons, planet_speeds, lagna_lon, lagnesh)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. SAHAMS (Arabic Parts / Lots) — 16 classical Tajika Sahams
# ═══════════════════════════════════════════════════════════════════════════════

# Formula key → (LA, LB, LC): result = (LA - LB + LC) % 360
SAHAM_FORMULAS: Dict[str, Dict[str, Tuple[str, str, str]]] = {
    "Punya":    {"day": ("MOON","SUN","ASC"),     "night": ("SUN","MOON","ASC")},
    "Vidya":    {"day": ("SUN","MOON","ASC"),      "night": ("MOON","SUN","ASC")},
    "Yashas":   {"day": ("JUP","Punya","ASC"),     "night": ("Punya","JUP","ASC")},
    "Mitra":    {"day": ("JUP","Punya","VEN"),     "night": ("Punya","JUP","VEN")},
    "Mahatmya": {"day": ("Punya","MARS","ASC"),    "night": ("MARS","Punya","ASC")},
    "Asha":     {"day": ("SAT","MARS","ASC"),      "night": ("MARS","SAT","ASC")},
    "Samartha": {"day": ("MARS","L1","ASC"),       "night": ("L1","MARS","ASC")},
    "Bhratri":  {"day": ("JUP","SAT","ASC"),       "night": ("JUP","SAT","ASC")},
    "Gaurava":  {"day": ("JUP","MOON","SUN"),      "night": ("MOON","JUP","SUN")},
    "Pitri":    {"day": ("SAT","SUN","ASC"),       "night": ("SUN","SAT","ASC")},
    "Rajya":    {"day": ("SAT","SUN","ASC"),       "night": ("SUN","SAT","ASC")},
    "Matri":    {"day": ("MOON","VEN","ASC"),      "night": ("VEN","MOON","ASC")},
    "Putra":    {"day": ("JUP","MOON","ASC"),      "night": ("MOON","JUP","ASC")},
    "Jeeva":    {"day": ("SAT","JUP","ASC"),       "night": ("JUP","SAT","ASC")},
    "Karma":    {"day": ("MARS","MER","ASC"),      "night": ("MER","MARS","ASC")},
    "Vivaha":   {"day": ("VEN","SAT","ASC"),       "night": ("VEN","SAT","ASC")},
}

_PLANET_ALIASES = {
    "JUP":"JUPITER","SAT":"SATURN","MAR":"MARS","MER":"MERCURY",
    "VEN":"VENUS","MOO":"MOON","SUN":"SUN","MARS":"MARS",
    "MOON":"MOON","ASC":"ASC","L1":"L1","Punya":"Punya",
}

_SAHAM_SIGNIFICATIONS = {
    "Punya":"General fortune and merit","Vidya":"Education and intellect",
    "Yashas":"Fame and reputation","Mitra":"Friendships and alliances",
    "Mahatmya":"Honour and courage","Asha":"Hope and desires",
    "Samartha":"Capacity and achievement","Bhratri":"Siblings and co-workers",
    "Gaurava":"Social respect","Pitri":"Father and authority",
    "Rajya":"Power and rulership","Matri":"Mother and property",
    "Putra":"Children and creativity","Jeeva":"Longevity and vitality",
    "Karma":"Career and profession","Vivaha":"Marriage and partnerships",
}


def compute_saham(name: str, planet_lons: Dict[str, float],
                  asc_lon: float, punya_lon: float,
                  lagnesh_lon: float, is_day: bool) -> float:
    """
    Compute one Saham: (LA - LB + LC) % 360.
    Geometric correction: if ASC not between LB and LA, add 30°.
    """
    triple = SAHAM_FORMULAS.get(name, {}).get("day" if is_day else "night",
             SAHAM_FORMULAS.get(name, {}).get("day", ("ASC","ASC","ASC")))
    la_k, lb_k, lc_k = triple

    def _resolve(k: str) -> float:
        if k == "ASC":    return asc_lon
        if k == "Punya":  return punya_lon
        if k == "L1":     return lagnesh_lon
        return planet_lons.get(_PLANET_ALIASES.get(k, k), 0.0)

    la, lb, lc = _resolve(la_k), _resolve(lb_k), _resolve(lc_k)
    result = (la - lb + lc) % 360.0

    # Geometric correction
    if lc_k == "ASC":
        lb_to_la  = (la - lb) % 360.0
        lb_to_asc = (asc_lon - lb) % 360.0
        if lb_to_asc >= lb_to_la:
            result = (result + 30.0) % 360.0

    return round(result, 3)


def compute_all_sahams(planet_lons: Dict[str, float], asc_lon: float,
                       is_day: bool, lagnesh_lon: Optional[float] = None,
                       ) -> Dict[str, Any]:
    """Compute all 16 Tajika Sahams. Returns dict of name → saham data."""
    ll = lagnesh_lon if lagnesh_lon is not None else asc_lon
    punya_lon = compute_saham("Punya", planet_lons, asc_lon, 0.0, ll, is_day)

    result = {}
    for name in SAHAM_FORMULAS:
        lon      = compute_saham(name, planet_lons, asc_lon, punya_lon, ll, is_day)
        sign_idx = int(lon / 30) % 12
        result[name] = {
            "longitude":    lon,
            "sign_idx":     sign_idx,
            "sign":         _SIGN_NAMES[sign_idx],
            "lord":         _sign_lord(sign_idx),
            "significance": _SAHAM_SIGNIFICATIONS.get(name, ""),
        }
    return result


def check_saham_activation(sahams: Dict[str, Any],
                           planet_lons: Dict[str, float], lagnesh: str,
                           planet_speeds: Dict[str, float]) -> List[Dict[str, Any]]:
    """Return activated Sahams (lord forms Itthasala with Varsha Lagnesh)."""
    lg_lon = planet_lons.get(lagnesh, 0.0)
    lg_spd = planet_speeds.get(lagnesh, 0.0)
    active = []
    for name, data in sahams.items():
        lord = data["lord"]
        l_lon = planet_lons.get(lord)
        if l_lon is None:
            continue
        l_spd = planet_speeds.get(lord, 0.0)
        is_itt, sep = _is_itthasala(lord, l_lon, l_spd, lagnesh, lg_lon, lg_spd)
        if is_itt:
            active.append({"name": name, "lord": lord,
                           "itthasala_sep": round(abs(sep),2),
                           "significance": data["significance"]})
    return active


# ═══════════════════════════════════════════════════════════════════════════════
# 7. MUDDA DASHA (Intra-year timing — 360-day base)
# ═══════════════════════════════════════════════════════════════════════════════

MUDDA_PERIODS: Dict[str, int] = {
    "SUN":18, "MOON":30, "MARS":21, "RAHU":54,
    "JUPITER":48, "SATURN":57, "MERCURY":51, "KETU":21, "VENUS":60,
}
MUDDA_ORDER = ["SUN","MOON","MARS","RAHU","JUPITER","SATURN","MERCURY","KETU","VENUS"]
_NAK_LORD_ORDER = ["KETU","VENUS","SUN","MOON","MARS","RAHU","JUPITER","SATURN","MERCURY"]


def compute_mudda_dasha(natal_moon_lon: float,
                        return_date: Optional[datetime] = None,
                        ) -> List[Dict[str, Any]]:
    """
    Compute Mudda Dasha sequence for the Tajika year (360-day base).

    Starting lord: from natal Moon's nakshatra (Vimshottari mapping).
    Bhogya (balance): fraction of current nakshatra remaining at return moment.
    """
    start_dt = return_date or datetime.now()

    nak_span = 360.0 / 27.0
    nak_idx  = int(natal_moon_lon / nak_span) % 27
    starting = _NAK_LORD_ORDER[nak_idx % 9]

    # Bhogya fraction
    arc_traveled = (natal_moon_lon % nak_span) * 60.0   # in arc-minutes
    bhogya = max(0.0, 1.0 - (arc_traveled / (nak_span * 60.0)))

    lord_idx  = MUDDA_ORDER.index(starting)
    sequence: List[Dict[str, Any]] = []
    elapsed   = 0.0

    for i in range(len(MUDDA_ORDER)):
        lord      = MUDDA_ORDER[(lord_idx + i) % len(MUDDA_ORDER)]
        full_days = float(MUDDA_PERIODS[lord])
        days      = full_days * bhogya if i == 0 else full_days
        if days < 0.01:
            continue
        seq_start = start_dt + timedelta(days=elapsed)
        seq_end   = start_dt + timedelta(days=elapsed + days)
        sequence.append({
            "lord":       lord,
            "days":       round(days, 2),
            "start_day":  round(elapsed, 2),
            "end_day":    round(elapsed + days, 2),
            "start_date": seq_start.strftime("%Y-%m-%d"),
            "end_date":   seq_end.strftime("%Y-%m-%d"),
        })
        elapsed += days

    # Fill remainder with full normal periods
    while elapsed < 360.0 and len(sequence) < 18:
        lord  = MUDDA_ORDER[(lord_idx + len(sequence)) % len(MUDDA_ORDER)]
        days  = min(float(MUDDA_PERIODS[lord]), 360.0 - elapsed)
        seq_start = start_dt + timedelta(days=elapsed)
        seq_end   = start_dt + timedelta(days=elapsed + days)
        sequence.append({
            "lord": lord, "days": round(days,2),
            "start_day": round(elapsed,2), "end_day": round(elapsed+days,2),
            "start_date": seq_start.strftime("%Y-%m-%d"),
            "end_date":   seq_end.strftime("%Y-%m-%d"),
        })
        elapsed += days

    return sequence


def get_current_mudda(sequence: List[Dict[str, Any]],
                      query_date: Optional[datetime] = None,
                      ) -> Optional[Dict[str, Any]]:
    """Return the Mudda Dasha period active on query_date (defaults to today)."""
    qd = (query_date or datetime.now()).strftime("%Y-%m-%d")
    for period in sequence:
        if period["start_date"] <= qd <= period["end_date"]:
            return period
    return sequence[0] if sequence else None


# ═══════════════════════════════════════════════════════════════════════════════
# 7B. HARSHA BALA (Native Tajika 20-point model)
# ═══════════════════════════════════════════════════════════════════════════════

# Classical fixed Sthana houses (from Tajika/Varshaphala presentation)
_HARSHA_STHANA_HOUSE: Dict[str, int] = {
    "SUN": 9,
    "MOON": 3,
    "MARS": 6,
    "SATURN": 12,
    "MERCURY": 1,
    "JUPITER": 11,
    "VENUS": 5,
}

# Classical Stri-Purusha planet groups used by this rule set.
_HARSHA_MALE_PLANETS = {"SUN", "MARS", "JUPITER"}
_HARSHA_FEMALE_PLANETS = {"MOON", "MERCURY", "VENUS", "SATURN"}

# Classical house-gender mapping used by Harsha Bala.
_HARSHA_FEMALE_HOUSES = {1, 2, 3, 7, 8, 9}
_HARSHA_MALE_HOUSES = {4, 5, 6, 10, 11, 12}


def _harsha_is_own_exalt_or_moola(planet: str, longitude: float) -> bool:
    """True when planet is in own/exaltation/moolatrikona sign-state."""
    p = str(planet).upper()
    if p not in _HARSHA_STHANA_HOUSE:
        return False

    sign_idx = int(longitude / 30) % 12
    deg_in_sign = float(longitude % 30.0)

    try:
        from vedic_engine.config import Planet, OWN_SIGNS, MOOLATRIKONA, EXALTATION_DEGREES
    except Exception:
        return False

    try:
        p_enum = Planet[p]
    except Exception:
        return False

    own_ok = any(int(s.value) == sign_idx for s in OWN_SIGNS.get(p_enum, []))
    exalt_lon = float(EXALTATION_DEGREES.get(p_enum, -999.0))
    exalt_sign = int(exalt_lon / 30.0) % 12 if exalt_lon >= 0 else -1
    exalt_ok = sign_idx == exalt_sign

    moola = MOOLATRIKONA.get(p_enum)
    moola_ok = False
    if isinstance(moola, tuple) and len(moola) == 3:
        m_sign, m_start, m_end = moola
        moola_ok = int(m_sign.value) == sign_idx and float(m_start) <= deg_in_sign < float(m_end)

    return bool(own_ok or exalt_ok or moola_ok)


def compute_harsha_bala(
    planet: str,
    longitude: float,
    lagna_sign: int,
    is_day_chart: bool,
) -> Dict[str, Any]:
    """
    Compute native Harsha Bala (0-20), 5 points per classical condition:
      1. Sthana Bala (fixed house per planet)
      2. Own/Exaltation/Moolatrikona
      3. Stri-Purusha (planet gender vs occupied house gender)
      4. Dina-Ratri (male planets by day, female planets by night)
    """
    p = str(planet).upper()
    if p not in _HARSHA_STHANA_HOUSE:
        return {
            "planet": p,
            "score": 0,
            "max": 20,
            "eligible": False,
            "reason": "unsupported_planet",
        }

    sign_idx = int(longitude / 30) % 12
    house_num = ((sign_idx - int(lagna_sign)) % 12) + 1

    sthana_ok = house_num == int(_HARSHA_STHANA_HOUSE[p])
    dignity_ok = _harsha_is_own_exalt_or_moola(p, longitude)

    if p in _HARSHA_MALE_PLANETS:
        gender_ok = house_num in _HARSHA_MALE_HOUSES
        day_night_ok = bool(is_day_chart)
    else:
        gender_ok = house_num in _HARSHA_FEMALE_HOUSES
        day_night_ok = not bool(is_day_chart)

    score = 0
    score += 5 if sthana_ok else 0
    score += 5 if dignity_ok else 0
    score += 5 if gender_ok else 0
    score += 5 if day_night_ok else 0

    return {
        "planet": p,
        "score": int(score),
        "max": 20,
        "eligible": True,
        "house": int(house_num),
        "sign_idx": int(sign_idx),
        "is_day_chart": bool(is_day_chart),
        "components": {
            "sthana": bool(sthana_ok),
            "own_exalt_moola": bool(dignity_ok),
            "stri_purusha": bool(gender_ok),
            "dina_ratri": bool(day_night_ok),
        },
    }


def compute_all_harsha_bala(
    planet_lons: Dict[str, float],
    lagna_sign: int,
    is_day_chart: bool,
) -> Dict[str, Any]:
    """Compute Harsha Bala for the 7 classical planets in annual chart context."""
    planets = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]
    per_planet: Dict[str, Any] = {}
    for p in planets:
        if p in planet_lons:
            per_planet[p] = compute_harsha_bala(p, float(planet_lons[p]), lagna_sign, is_day_chart)

    avg_score = 0.0
    if per_planet:
        avg_score = sum(float(v.get("score", 0.0)) for v in per_planet.values()) / float(len(per_planet))

    return {
        "by_planet": per_planet,
        "avg_score": round(avg_score, 3),
        "scale": "0_to_20",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 7C. TRIPATAKI CHAKRA (progression core; vedha geometry pending)
# ═══════════════════════════════════════════════════════════════════════════════

_TRIPATAKI_MODULO_9 = {"MOON"}
_TRIPATAKI_MODULO_4 = {"SUN", "MERCURY", "JUPITER", "VENUS", "SATURN"}
_TRIPATAKI_MODULO_6 = {"MARS", "RAHU", "KETU"}

# Runtime line map sourced from bundled pyjhora Tripataki chakra geometry.
_TRIPATAKI_POINT_RING: List[Tuple[int, int]] = [
    (1, 3), (1, 4), (2, 5), (3, 5), (4, 5), (5, 4),
    (5, 3), (5, 2), (4, 1), (3, 1), (2, 1), (1, 2),
]
_TRIPATAKI_ANCHOR_POINT: Tuple[int, int] = (3, 5)  # Classical point 'a'.
_TRIPATAKI_VEDHA_LINES: Dict[Tuple[int, int], List[Tuple[int, int]]] = {
    (2, 5): [(1, 4), (2, 1), (5, 2)],
    (3, 5): [(1, 3), (3, 1), (5, 3)],
    (4, 5): [(1, 2), (4, 1), (5, 4)],
    (2, 1): [(1, 2), (5, 4)],
    (3, 1): [(1, 3), (5, 3)],
    (4, 1): [(1, 4), (5, 2)],
    (1, 2): [(5, 2)],
    (1, 3): [(5, 3)],
    (1, 4): [(5, 4)],
}

_TRIPATAKI_BENEFICS = {"JUPITER", "VENUS", "MERCURY"}
_TRIPATAKI_MALEFICS = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}


def _tripataki_step(planet: str, running_year: int) -> int:
    """Return classical Tripataki progression step for a planet."""
    p = str(planet).upper()
    if p in _TRIPATAKI_MODULO_9:
        rem = running_year % 9
        return rem if rem != 0 else 9
    if p in _TRIPATAKI_MODULO_4:
        rem = running_year % 4
        return rem if rem != 0 else 4
    if p in _TRIPATAKI_MODULO_6:
        rem = running_year % 6
        return rem if rem != 0 else 6
    return 0


def _tripataki_sign_map(annual_lagna_sign: int) -> Dict[Tuple[int, int], int]:
    """Map Tripataki points to signs with annual lagna at point 'a'."""
    lagna = int(annual_lagna_sign) % 12
    a_idx = _TRIPATAKI_POINT_RING.index(_TRIPATAKI_ANCHOR_POINT)
    mapping: Dict[Tuple[int, int], int] = {}
    for idx, point in enumerate(_TRIPATAKI_POINT_RING):
        # Classical instruction: distribute remaining signs anti-clockwise from point 'a'.
        sign_idx = (lagna + ((a_idx - idx) % 12)) % 12
        mapping[point] = sign_idx
    return mapping


def _tripataki_point_adjacency() -> Dict[Tuple[int, int], List[Tuple[int, int]]]:
    """Build undirected vedha adjacency from the Tripataki line map."""
    adj: Dict[Tuple[int, int], set] = {}
    for start, ends in _TRIPATAKI_VEDHA_LINES.items():
        adj.setdefault(start, set())
        for end in ends:
            adj.setdefault(start, set()).add(end)
            adj.setdefault(end, set()).add(start)
    return {k: sorted(v) for k, v in adj.items()}


def compute_tripataki_progression(
    natal_planet_signs: Dict[str, int],
    completed_years: int,
    annual_lagna_sign: int,
) -> Dict[str, Any]:
    """
    Compute Tripataki progression indices/signs per classical modulo rules.

    Uses runtime line-map geometry to evaluate Vedha on progressed Moon.
    """
    running_year = int(completed_years) + 1
    progressed: Dict[str, Any] = {}

    for p_raw, natal_sign in (natal_planet_signs or {}).items():
        p = str(p_raw).upper()
        if p not in (_TRIPATAKI_MODULO_9 | _TRIPATAKI_MODULO_4 | _TRIPATAKI_MODULO_6):
            continue
        step = _tripataki_step(p, running_year)
        base_sign = int(natal_sign) % 12
        if p in {"RAHU", "KETU"}:
            prog_sign = (base_sign - step) % 12  # reverse progression for nodes
            direction = "reverse"
        else:
            prog_sign = (base_sign + step) % 12
            direction = "forward"

        progressed[p] = {
            "natal_sign": base_sign,
            "index_step": int(step),
            "direction": direction,
            "progressed_sign": int(prog_sign),
            "progressed_sign_name": _SIGN_NAMES[int(prog_sign)],
        }

    moon_prog_sign = progressed.get("MOON", {}).get("progressed_sign")

    sign_by_point = _tripataki_sign_map(annual_lagna_sign)
    point_by_sign = {sign: point for point, sign in sign_by_point.items()}
    point_adj = _tripataki_point_adjacency()

    moon_vedha: Dict[str, Any] = {
        "status": "moon_progression_unavailable",
        "moon_point": None,
        "vedha_points": [],
        "vedha_signs": [],
        "vedha_sign_names": [],
        "hit_planets": [],
        "benefic_hits": 0,
        "malefic_hits": 0,
        "weighted_score": 0.0,
    }

    if isinstance(moon_prog_sign, int):
        moon_point = point_by_sign.get(int(moon_prog_sign) % 12)
        if moon_point in point_adj:
            vedha_points = point_adj.get(moon_point, [])
            vedha_signs = [int(sign_by_point[pt]) for pt in vedha_points if pt in sign_by_point]
            benefic_hits = 0
            malefic_hits = 0
            hit_planets: List[Dict[str, Any]] = []

            for p in sorted(progressed.keys()):
                if p == "MOON":
                    continue
                p_sign = int((progressed.get(p, {}) or {}).get("progressed_sign", -1))
                if p_sign not in vedha_signs:
                    continue

                cls = "neutral"
                if p in _TRIPATAKI_BENEFICS:
                    cls = "benefic"
                    benefic_hits += 1
                elif p in _TRIPATAKI_MALEFICS:
                    cls = "malefic"
                    malefic_hits += 1

                hit_planets.append(
                    {
                        "planet": p,
                        "classification": cls,
                        "progressed_sign": p_sign,
                        "progressed_sign_name": _SIGN_NAMES[p_sign],
                    }
                )

            weighted_score = float(benefic_hits - malefic_hits)
            moon_vedha = {
                "status": "evaluated",
                "moon_point": list(moon_point),
                "vedha_points": [list(pt) for pt in vedha_points],
                "vedha_signs": vedha_signs,
                "vedha_sign_names": [_SIGN_NAMES[s] for s in vedha_signs],
                "hit_planets": hit_planets,
                "benefic_hits": benefic_hits,
                "malefic_hits": malefic_hits,
                "weighted_score": round(weighted_score, 3),
            }
        else:
            moon_vedha["status"] = "moon_point_unmapped"

    return {
        "running_year": running_year,
        "annual_lagna_sign": int(annual_lagna_sign) % 12,
        "annual_lagna_sign_name": _SIGN_NAMES[int(annual_lagna_sign) % 12],
        "sign_map": [
            {
                "point": list(point),
                "sign_idx": int(sign_by_point[point]),
                "sign_name": _SIGN_NAMES[int(sign_by_point[point])],
            }
            for point in _TRIPATAKI_POINT_RING
        ],
        "progressions": progressed,
        "moon_progressed_sign": moon_prog_sign,
        "moon_progressed_sign_name": _SIGN_NAMES[int(moon_prog_sign)] if isinstance(moon_prog_sign, int) else None,
        "moon_vedha": moon_vedha,
        "status": "vedha_scored",
        "vedha_geometry_available": True,
        "geometry_source": "pyjhora_tripataki_line_map",
        "source_gap": None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 8. SOLAR RETURN COMPUTATION (requires ephemeris callback)
# ═══════════════════════════════════════════════════════════════════════════════

def compute_solar_return_dt(
    natal_sun_lon:     float,
    birth_dt:          datetime,
    target_year:       int,
    get_sun_lon:       Callable[[datetime], float],
    precision_minutes: float = 0.5,
) -> datetime:
    """
    Find the solar return moment in target_year via binary search.

    Args:
        natal_sun_lon:   Natal Sun longitude (sidereal degrees).
        birth_dt:        Birth datetime (used as seed).
        target_year:     Year of the desired solar return.
        get_sun_lon:     Callable(datetime) → sidereal Sun longitude.
        precision_minutes: Convergence threshold.

    Returns: datetime of solar return.
    """
    try:
        seed = birth_dt.replace(year=target_year) - timedelta(days=10)
    except ValueError:
        seed = datetime(target_year, birth_dt.month, 28) - timedelta(days=10)

    lo, hi = seed, seed + timedelta(days=30)

    def _diff(dt: datetime) -> float:
        d = (get_sun_lon(dt) - natal_sun_lon) % 360.0
        return d if d <= 180.0 else d - 360.0

    # Walk forward to bracket the crossing
    step      = timedelta(hours=4)
    dt_walk   = lo
    prev_diff = _diff(dt_walk)
    for _ in range(200):
        dt_walk  += step
        curr_diff = _diff(dt_walk)
        if prev_diff < 0.0 <= curr_diff or (abs(curr_diff) < abs(prev_diff) < 0.1):
            lo, hi = dt_walk - step, dt_walk
            break
        prev_diff = curr_diff

    # Binary-search refine
    for _ in range(60):
        if (hi - lo).total_seconds() / 60.0 < precision_minutes:
            break
        mid = lo + (hi - lo) / 2
        if _diff(mid) < 0:
            lo = mid
        else:
            hi = mid

    return lo + (hi - lo) / 2


# ═══════════════════════════════════════════════════════════════════════════════
# 9. PRIMARY STATIC ENTRY-POINT (for engine.py pipeline)
# ═══════════════════════════════════════════════════════════════════════════════

def compute_varsha_analysis(
    planet_lons:      Dict[str, float],
    planet_speeds:    Dict[str, float],
    lagna_lon:        float,
    natal_lagna_sign: int,
    natal_moon_lon:   float,
    completed_years:  int,
    months_elapsed:   int            = 0,
    days_elapsed:     int            = 0,
    is_day_chart:     bool           = True,
    return_date:      Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Full Tajika Varshaphala static analysis — no ephemeris callbacks needed.

    Parameters
    ----------
    planet_lons      : Sidereal planetary longitudes.
    planet_speeds    : Daily motions (negative = retrograde).
    lagna_lon        : Ascendant longitude.
    natal_lagna_sign : Natal Lagna sign index (0–11).
    natal_moon_lon   : Natal Moon longitude (for Mudda Dasha starting lord).
    completed_years  : Completed years (age).
    months_elapsed   : Additional months beyond full years.
    days_elapsed     : Additional days beyond full months.
    is_day_chart     : True if solar return is during daytime.
    return_date      : Solar return datetime (for Mudda Dasha dates).

    Returns
    -------
    dict covering: lagna, muntha, pvb, varsha_pati,
                   tajika_yogas, sahams, active_sahams, mudda_dasha.
    """
    lagna_sign = int(lagna_lon / 30) % 12
    lagnesh    = _sign_lord(lagna_sign)

    # Muntha
    muntha          = compute_muntha(natal_lagna_sign, completed_years,
                                     months_elapsed, days_elapsed)
    muntha_house    = get_muntha_house(muntha["sign_idx"], lagna_sign)
    muntha_interp   = get_muntha_interpretation(muntha["sign_idx"], lagna_sign)

    # PVB for all planets
    pvb_all = {p: compute_pvb(p, lon) for p, lon in planet_lons.items()}

    # Native Harsha Bala (annual efficacy diagnostic)
    harsha_bala = compute_all_harsha_bala(
        planet_lons=planet_lons,
        lagna_sign=lagna_sign,
        is_day_chart=is_day_chart,
    )

    # Native Tripataki progression core (no invented vedha geometry)
    _natal_signs = {str(p).upper(): (int(float(lon) / 30.0) % 12) for p, lon in planet_lons.items()}
    tripataki = compute_tripataki_progression(
        natal_planet_signs=_natal_signs,
        completed_years=completed_years,
        annual_lagna_sign=lagna_sign,
    )

    # Varsha Pati
    vp = compute_varsha_pati(
        natal_lagna_sign  = natal_lagna_sign,
        varsha_lagna_sign = lagna_sign,
        varsha_lagna_lon  = lagna_lon,
        muntha_sign       = muntha["sign_idx"],
        planet_lons       = planet_lons,
        is_day_return     = is_day_chart,
    )

    # Tajika Yogas
    yogas = detect_tajika_yogas(planet_lons, planet_speeds, lagna_lon, lagnesh)

    # Sahams
    lagnesh_lon  = planet_lons.get(lagnesh, lagna_lon)
    sahams       = compute_all_sahams(planet_lons, lagna_lon, is_day_chart, lagnesh_lon)
    active_sahams = check_saham_activation(sahams, planet_lons, lagnesh, planet_speeds)

    # Mudda Dasha
    mudda_seq     = compute_mudda_dasha(natal_moon_lon, return_date)
    current_mudda = get_current_mudda(mudda_seq)

    return {
        "lagna_sign":      lagna_sign,
        "lagna_sign_name": _SIGN_NAMES[lagna_sign],
        "lagnesh":         lagnesh,
        "muntha": {
            **muntha,
            "house":          muntha_house,
            "interpretation": muntha_interp,
        },
        "pvb":             pvb_all,
        "harsha_bala":     harsha_bala,
        "tripataki":       tripataki,
        "varsha_pati":     vp,
        "tajika_yogas":    yogas,
        "sahams":          sahams,
        "active_sahams":   active_sahams,
        "mudda_dasha": {
            "sequence": mudda_seq,
            "current":  current_mudda,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 10. LEGACY FULL PIPELINE (requires ephemeris callbacks)
# ═══════════════════════════════════════════════════════════════════════════════

def compute_varshaphala(
    natal_lagna_sign:  int,
    natal_sun_lon:     float,
    birth_dt:          datetime,
    target_year:       int,
    years_elapsed:     int,
    get_sun_lon:       Callable[[datetime], float],
    get_annual_chart:  Callable[[datetime], Dict[str, Any]],
    shadbala_scores:   Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Legacy full pipeline with ephemeris callbacks. Backward-compatible."""
    sr_dt = compute_solar_return_dt(natal_sun_lon, birth_dt, target_year, get_sun_lon)

    try:
        annual = get_annual_chart(sr_dt)
    except Exception as exc:
        annual = {"error": str(exc), "lagna_lon": 0.0, "lagna_sign": 0,
                  "planets": {}, "speeds": {}}

    annual_planets   = annual.get("planets", {})
    annual_speeds    = annual.get("speeds", {p: 0.0 for p in annual_planets})
    annual_lagna_lon = annual.get("lagna_lon", 0.0)

    static = compute_varsha_analysis(
        planet_lons      = annual_planets,
        planet_speeds    = annual_speeds,
        lagna_lon        = annual_lagna_lon,
        natal_lagna_sign = natal_lagna_sign,
        natal_moon_lon   = annual_planets.get("MOON", 0.0),
        completed_years  = years_elapsed,
        is_day_chart     = True,
        return_date      = sr_dt,
    )

    return {
        "solar_return_dt": sr_dt.isoformat(),
        "annual_chart":    annual,
        "target_year":     target_year,
        **static,
        "varshesha":   static["varsha_pati"],   # legacy key
        "tajika_yogas": static["tajika_yogas"],
    }
