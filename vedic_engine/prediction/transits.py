"""
Transit Engine.
Handles real-time planetary positions and transit analysis for any date.

Two modes:
1. Ephemeris mode: uses pyswisseph if available for exact positions.
2. Fallback mode: approximate solar-system positions for transit sign tracking.

Transit evaluation uses:
  - Gochar rules (house from Moon)
  - Ashtakvarga scores  
  - Vedha obstruction check
  - Sade Sati detection
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from vedic_engine.config import (
    TRANSIT_FAVORABLE, VEDHA_TABLE, VEDHA_EXCEPTIONS,
    GOCHAR_EFFECTS, COMBUSTION_DEGREES,
    VEDHA_REDUCTION, KAKSHYA_LORDS, KAKSHYA_SPAN,
    MANIFESTATION_ZONES, MANIFESTATION_OUTSIDE_MULTIPLIER,
    NAISARGIKA_FRIENDS, NAISARGIKA_ENEMIES,
    Planet, Sign, SIGN_LORDS, VIMSHOTTARI_SEQUENCE,
)
from vedic_engine.core.coordinates import sign_of, nakshatra_of
from vedic_engine.analysis.special_points import compute_tarabala, compute_chandrabala


PLANET_NAMES = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU"]
SIGN_NAMES = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
              "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

_P = {
    "SUN": Planet.SUN, "MOON": Planet.MOON, "MARS": Planet.MARS,
    "MERCURY": Planet.MERCURY, "JUPITER": Planet.JUPITER,
    "VENUS": Planet.VENUS, "SATURN": Planet.SATURN,
    "RAHU": Planet.RAHU, "KETU": Planet.KETU,
}


# ─── Approximate planet positions (fallback) ──────────────────────

# Mean sidereal speeds deg/day (Lahiri approximate)
MEAN_SPEEDS = {
    "SUN": 0.9856,
    "MOON": 13.1764,
    "MARS": 0.5240,
    "MERCURY": 1.3833,
    "JUPITER": 0.0831,
    "VENUS": 1.2022,
    "SATURN": 0.0335,
    "RAHU": -0.0529,    # retrograde
    "KETU": -0.0529,
}

# Approximate sidereal longitudes on 2026-02-27
# (Based on chart analysis context - Saturn in Aquarius, Jupiter in Gemini/Taurus area, Rahu in Pisces)
APPROX_POSITIONS_FEB2026 = {
    "SUN": 315.0,      # ~Aquarius
    "MOON": 200.0,     # approximate (changes daily)
    "MARS": 100.0,     # ~Cancer
    "MERCURY": 320.0,  # ~Aquarius
    "JUPITER": 52.0,   # ~Taurus (sidereal)
    "VENUS": 280.0,    # ~Capricorn
    "SATURN": 320.0,   # ~Aquarius (sidereal)
    "RAHU": 348.0,     # ~Pisces
    "KETU": 168.0,     # ~Virgo
}
REFERENCE_DATE = datetime(2026, 2, 27)


def get_transit_positions(on_date: datetime) -> Dict[str, float]:
    """
    Get accurate sidereal planetary positions for any date.

    Priority / accuracy tier:
      1) pyswisseph  — Swiss Ephemeris, industry gold standard; needs MSVC on Windows
      2) skyfield    — Skyfield + JPL DE440s/DE421 BSP; pure Python, NASA reference;
                       agrees with Swiss Ephemeris to <0.001° for classical planets
      3) astropy     — ERFA/SOFA, sub-arcminute, pure Python; currently installed
      4) ephem       — PyEphem, ~0.1° accuracy
      5) approximate — Linear extrapolation from 2026-02-27 snapshot; last resort

    For audit purposes, run_ephemeris_audit() uses Skyfield as the reference
    standard to cross-check all other tiers — see ephemeris_audit.py.
    """
    try:
        return _get_positions_swisseph(on_date)
    except (ImportError, Exception):
        pass
    try:
        return _get_positions_skyfield(on_date)
    except (ImportError, Exception):
        pass
    try:
        return _get_positions_astropy(on_date)
    except (ImportError, Exception):
        pass
    try:
        return _get_positions_ephem(on_date)
    except (ImportError, Exception):
        return _get_positions_approximate(on_date)


def _get_positions_astropy(on_date: datetime) -> Dict[str, float]:
    """
    Tier-3 (fast pure-Python): Use astropy + ERFA for geocentric ecliptic positions.
    Accuracy: sub-arcminute for classical planets, comparable to Swiss Ephemeris
    for sign-level analysis. Rahu/Ketu via Meeus formula (~0.05° accuracy).
    """
    from vedic_engine.prediction.astropy_positions import get_positions_astropy
    return get_positions_astropy(on_date)


def _get_positions_skyfield(on_date: datetime) -> Dict[str, float]:
    """
    Tier-2: Skyfield + JPL DE440s/DE421 ephemeris — research-grade pure Python.

    Accuracy vs Swiss Ephemeris: < 0.001° for classical planets (both derive
    from JPL integrations). Used as audit reference in ephemeris_audit.py.

    First call triggers a one-time BSP file download (~32 MB for de440s).
    Subsequent calls load from local cache in vedic_engine/data/ephemeris/.
    """
    from vedic_engine.prediction.skyfield_positions import get_positions_skyfield
    return get_positions_skyfield(on_date)


def _get_positions_ephem(on_date: datetime) -> Dict[str, float]:
    """
    Use PyEphem for accurate geocentric ecliptic positions with Lahiri ayanamsa.
    Much more accurate than linear interpolation for dates far from reference.
    """
    import ephem
    import math

    date_str = on_date.strftime("%Y/%m/%d %H:%M:%S")

    # Lahiri ayanamsa: 23.8557° at J2000.0, precessing ~50.3" per Julian year
    days_from_j2000 = (on_date - datetime(2000, 1, 1, 12, 0)).total_seconds() / 86400.0
    ayanamsa = 23.8557 + days_from_j2000 * (50.3 / (3600 * 365.25))  # degrees

    BODIES = {
        "SUN":     ephem.Sun,
        "MOON":    ephem.Moon,
        "MARS":    ephem.Mars,
        "MERCURY": ephem.Mercury,
        "JUPITER": ephem.Jupiter,
        "VENUS":   ephem.Venus,
        "SATURN":  ephem.Saturn,
    }

    positions: Dict[str, float] = {}
    for name, cls in BODIES.items():
        body = cls(date_str)
        # Ecliptic longitude at equinox of date → tropical longitude
        ecl = ephem.Ecliptic(body, epoch=date_str)
        trop_lon = math.degrees(float(ecl.lon)) % 360.0
        sid_lon = (trop_lon - ayanamsa) % 360.0
        positions[name] = sid_lon

    # Mean Lunar Node (Rahu) — standard astronomical formula
    jd = ephem.julian_date(ephem.Date(date_str))
    T = (jd - 2451545.0) / 36525.0
    rahu_trop = (125.0445479 - 1934.1362608 * T +
                 0.0020754 * T * T +
                 T * T * T / 467441.0) % 360.0
    positions["RAHU"] = (rahu_trop - ayanamsa) % 360.0
    positions["KETU"] = (positions["RAHU"] + 180.0) % 360.0

    return positions


def _get_positions_swisseph(on_date: datetime) -> Dict[str, float]:
    """
    Tier-1 (gold standard): Use Swiss Ephemeris via swisseph_bridge.
    Accuracy: < 0.001° for all classical planets.
    Lahiri ayanamsa from official Swiss Ephemeris computation.
    """
    from vedic_engine.core.swisseph_bridge import get_transit_positions_swe
    return get_transit_positions_swe(on_date)


def _get_positions_approximate(on_date: datetime) -> Dict[str, float]:
    """Linear extrapolation from reference date. Accurate for sign-level analysis."""
    delta_days = (on_date - REFERENCE_DATE).days
    positions = {}
    for pname, base_lon in APPROX_POSITIONS_FEB2026.items():
        speed = MEAN_SPEEDS.get(pname, 0)
        lon = (base_lon + speed * delta_days) % 360
        positions[pname] = lon
    return positions


# ─── Ephemeris Audit (research-grade cross-validation) ───────────────────────

def run_ephemeris_audit(n: int = 20, verbose: bool = True) -> Dict:
    """
    Run a research-grade audit comparing all backends against Skyfield + JPL.

    Skyfield + DE440s is used as the independent reference (NASA source).
    Compares astropy, pyswisseph (if installed), and PyEphem (if installed)
    against Skyfield across n randomly sampled dates.

    Notes the mean error, max error, systematic bias, sign agreement %, and
    nakshatra agreement % per planet.  Prints human-readable report if verbose.

    Requires Skyfield to be installed (pip install skyfield) and internet
    access on first run to download the ~32 MB de440s.bsp JPL kernel.

    Parameters
    ----------
    n       : number of random dates to sample (default 20, increase to 100+
              for publication-quality accuracy statistics)
    verbose : if True, prints the formatted report to stdout

    Returns
    -------
    {'spot': spot_check_result, 'random': random_audit_result}

    Example
    -------
    >>> from vedic_engine.prediction.transits import run_ephemeris_audit
    >>> results = run_ephemeris_audit(n=50)
    """
    from vedic_engine.prediction.ephemeris_audit import full_report
    return full_report(n=n, verbose=verbose)


# ─── Relationship Helpers ─────────────────────────────────────────

def _get_naisargika_relationship(p1: Planet, p2: Planet) -> str:
    """
    Return the natural relationship of p2 towards p1.
    Used to determine Vedha reduction intensity.
    """
    if p2 in NAISARGIKA_FRIENDS.get(p1, frozenset()):
        return "friend"
    if p2 in NAISARGIKA_ENEMIES.get(p1, frozenset()):
        return "enemy"
    return "neutral"


def _vedha_reduction_factor(transiting: Planet, obstructor: Planet) -> float:
    """
    Return the fraction of the gochar score to KEEP after Vedha obstruction.
    1.0 = no reduction, 0.0 = full nullification.
    Based on relationship of obstructor to transiting planet.
    """
    rel = _get_naisargika_relationship(transiting, obstructor)
    reduction = VEDHA_REDUCTION.get(rel, 0.75)   # default: neutral
    return max(0.0, 1.0 - reduction)


def _manifestation_multiplier(planet_name: str, degree_in_sign: float) -> float:
    """
    Asymmetric zone multiplier: each planet delivers primary results in a
    specific 10° window within the sign.  Outside → MANIFESTATION_OUTSIDE_MULTIPLIER.
    """
    zone = MANIFESTATION_ZONES.get(planet_name.upper())
    if zone is None:
        return 1.0
    start, end = zone
    if start <= degree_in_sign < end:
        return 1.0
    return MANIFESTATION_OUTSIDE_MULTIPLIER


def _kakshya_info(
    planet_name: str,
    degree_in_sign: float,
    bhinna_av: Optional[List[int]],
    transit_sign: int,
) -> Dict:
    """
    Determine Kakshya sub-division (1–8) for the current transit position
    and return whether the Kakshya lord gave a bindu or rekha in the planet's BAV.

    Returns:
        kakshya_num:   1-8 (1=Saturn, 2=Jupiter, ..., 8=Lagna)
        kakshya_lord:  string name of the sub-lord
        bindu_state:   'bindu' | 'rekha' | 'unknown'
        precision_boost: float (+0.05 or -0.02 or 0.0) to add to net_score
    """
    kakshya_num = min(int(degree_in_sign / KAKSHYA_SPAN), 7)  # 0-indexed → 0-7
    lord_name = KAKSHYA_LORDS[kakshya_num]

    # To check bindu/rekha we need the BAV contribution table — a simplified
    # heuristic: if the planet's bhinna_av for this sign ≥ 5 (generally good),
    # treat the current Kakshya as favourable (bindu), otherwise rekha.
    # A full implementation would store per-Kakshya donor contributions.
    bindu_state = "unknown"
    precision_boost = 0.0
    if bhinna_av is not None and 0 <= transit_sign < 12:
        bav_in_sign = bhinna_av[transit_sign]
        # Map BAV bindus to Kakshya sub-grid (approximation):
        # Each sign has up to 8 donors; bav_in_sign tells how many gave bindus.
        # If the specific kakshya lord's position in the donor sequence gave a bindu
        # we boost, else penalise.  Use a threshold approach here.
        if bav_in_sign >= 6:
            bindu_state = "bindu"
            precision_boost = 0.05
        elif bav_in_sign <= 2:
            bindu_state = "rekha"
            precision_boost = -0.02
        else:
            bindu_state = "mixed"
            precision_boost = 0.0

    return {
        "kakshya_num":     kakshya_num + 1,   # 1-indexed for display
        "kakshya_lord":    lord_name,
        "bindu_state":     bindu_state,
        "precision_boost": precision_boost,
    }


# ─── Transit Evaluation ───────────────────────────────────────────

def evaluate_transit(
        planet: str,
        transit_lon: float,
        natal_moon_sign: int,
        bhinna_av: Optional[List[int]] = None,
        sarva_av: Optional[List[int]] = None,
        other_transit_signs: Optional[Dict[str, int]] = None,
        transit_sun_lon: Optional[float] = None,
) -> Dict:
    """
    Evaluate a planet's transit for a given moment.

    Args:
        planet: planet name
        transit_lon: transit longitude (sidereal)
        natal_moon_sign: birth Moon sign index (0-11)
        bhinna_av: planet's Bhinna AV for each sign (list of 12)
        sarva_av: Sarvashtakvarga for each sign (list of 12)
        other_transit_signs: {other_planet: sign_idx} for Vedha check
        transit_sun_lon: current Sun longitude (sidereal) for combustion check
    """
    transit_sign = sign_of(transit_lon)
    degree_in_sign = transit_lon % 30.0        # 0-30° within sign
    house_from_moon = ((transit_sign - natal_moon_sign) % 12) + 1

    p = _P.get(planet.upper())
    favorable_houses = TRANSIT_FAVORABLE.get(p, []) if p else []
    is_favorable = house_from_moon in favorable_houses

    # Ashtakvarga
    bav_score = bhinna_av[transit_sign] if bhinna_av else None
    sav_score = sarva_av[transit_sign] if sarva_av else None
    sav_avg = 337 / 12.0  # ≈ 28.08

    # ── Manifestation Zone multiplier ────────────────────────────
    zone_mult = _manifestation_multiplier(planet, degree_in_sign)

    # ── Kakshya Pravesha sub-precision ───────────────────────────
    kakshya = _kakshya_info(planet, degree_in_sign, bhinna_av, transit_sign)

    # ── Vedha check — quantitative reduction (not binary) ────────
    vedha_blocked = False
    vedha_by = ""
    vedha_keep_factor = 1.0   # 1.0 = no obstruction
    if is_favorable and other_transit_signs and p:
        vedha_pairs = VEDHA_TABLE.get(p, {})
        vedha_house = vedha_pairs.get(house_from_moon)
        if vedha_house:
            for other_p, other_sign in other_transit_signs.items():
                if other_p == planet:
                    continue
                other_from_moon = ((other_sign - natal_moon_sign) % 12) + 1
                if other_from_moon == vedha_house:
                    other_p_enum = _P.get(other_p)
                    if other_p_enum and p:
                        exception = frozenset({p, other_p_enum})
                        if exception not in VEDHA_EXCEPTIONS:
                            keep = _vedha_reduction_factor(p, other_p_enum)
                            # Use the strongest (lowest keep) obstructor found
                            if keep < vedha_keep_factor:
                                vedha_keep_factor = keep
                                vedha_by = other_p
                                vedha_blocked = True

    # Net score: 0-1  (weighted sum of 4 components)
    # ── Gochar (house from Moon) ──────────────────────────────
    gochar_score = 0.4 if is_favorable else 0.0
    if vedha_blocked:
        # Quantitative reduction: enemy=full nullify, friend=50% reduction, etc.
        gochar_score *= vedha_keep_factor

    # ── Manifestation zone: dampen score outside primary zone ──
    gochar_score *= zone_mult

    # ── BAV bindu count in transit sign — TIERED (not linear) ──
    # Research: 0-3 = malefic/disastrous (even exalted planet fails)
    #           4   = neutral equilibrium  →  0.20
    #           5-8 = exponentially positive; overrides natal debilitation
    # BAV supersedes natal dignity for transit evaluation.
    bav_score_component = 0.0
    if bav_score is not None:
        if bav_score >= 6:
            bav_score_component = 0.30   # 6-8 bindus: strongly positive
        elif bav_score == 5:
            bav_score_component = 0.23   # positive, exponential rise starts
        elif bav_score == 4:
            bav_score_component = 0.15   # neutral
        elif bav_score == 3:
            bav_score_component = 0.05   # mildly negative but some support
        else:
            bav_score_component = 0.0   # 0-2 bindus = unfavorable transit sign

    # ── SAV (Sarvashtakvarga) strength of the transit sign ───
    sav_score_component = 0.0
    sav_avg = 337.0 / 12.0  # ≈ 28.1
    if sav_score is not None:
        if sav_score >= 30:
            sav_score_component = 0.20
        elif sav_score >= 25:
            sav_score_component = 0.10
        # < 25 = weak sign → 0

    # ── House from Lagna (secondary gochar check) ─────────────
    # Not computed here (lagna_sign not passed); placeholder 0.10 if favorable
    # left as a hook — set to 0.10 when is_favorable as proxy
    lagna_score = 0.10 if is_favorable else 0.0

    # ── Combustion Check ──────────────────────────────────────────
    is_combust = False
    combust_orb_actual = None
    combust_pct = 0.0
    combust_strength_retained = 1.0
    karakatwa_burned = False
    lordship_survives = False
    karmic_amplified = False
    karmic_boost = 0.0
    karmic_domains: list[str] = []
    combust_note = ""
    planet_upper = planet.upper()
    p_enum = _P.get(planet_upper)
    # Sun cannot combust itself; Rahu/Ketu are shadow planets (no combustion)
    if transit_sun_lon is not None and planet_upper not in ("SUN", "RAHU", "KETU") and p_enum:
        combust_orb_limit = COMBUSTION_DEGREES.get(p_enum, 0)
        if combust_orb_limit > 0:
            raw_diff = abs(transit_lon - transit_sun_lon)
            angular_dist = min(raw_diff, 360.0 - raw_diff)
            combust_orb_actual = round(angular_dist, 3)
            if angular_dist <= combust_orb_limit:
                is_combust = True
                # ── Sliding-scale combustion (Parashara proportionate strength) ──
                # 0° from Sun → 0% retained; at the limit edge → 100% retained
                combust_strength_retained = angular_dist / combust_orb_limit  # 0.0 – 1.0
                combust_pct = round((1.0 - combust_strength_retained) * 100, 1)
                gochar_score *= combust_strength_retained
                # ── Bifurcated combustion logic ────────────────────────────────
                # Karakatwa (natural significations) = burned/destroyed
                # Lordship (house rules/Yogas) = survives but with Sun-flavored stress
                karakatwa_burned = True
                lordship_survives = True

                # ── Combustion Retention Filter (Logic Integration Manifest §3.6) ─
                # Material traits: dampened ×0.3 (already absorbed in strength_retained)
                # Karmic / Spiritual traits: AMPLIFIED ×1.5 (Agni burns externals,
                # but refines inner light). Planets with strong spiritual natural
                # significations gain extra karmic potency when combust.
                _KARMIC_PLANETS = {
                    "JUPITER": 0.30,  # wisdom, dharma, inner guru
                    "SATURN":  0.25,  # discipline, karma, renunciation
                    "MOON":    0.20,  # inner mind, spiritual sensitivity
                    "KETU":    0.35,  # moksha, past-life karma (though Ketu can't combust, listed for docs)
                    "VENUS":   0.10,  # devotion, Bhakti when spiritualized
                    "MERCURY": 0.08,  # mantra, scriptural pursuit
                }
                karmic_boost = 0.0
                karmic_amplified = False
                karmic_domains: list[str] = []
                base_karmic_weight = _KARMIC_PLANETS.get(planet_upper, 0.0)
                if base_karmic_weight > 0.0:
                    # Amplification scales with combustion depth: deeper = more inner burn
                    # Factor: (1 - combust_strength_retained) = degree of combustion
                    # Net karmic boost = base_weight × (1 - retained) × 1.5 amplifier
                    karmic_amplifier = 1.5
                    karmic_boost = round(
                        base_karmic_weight * (1.0 - combust_strength_retained) * karmic_amplifier,
                        4,
                    )
                    if karmic_boost > 0.005:
                        karmic_amplified = True
                        # Tag the specific karmic domains awakened
                        _KARMIC_DOMAIN_MAP = {
                            "JUPITER": ["dharma", "inner_wisdom", "guru_awakening"],
                            "SATURN":  ["karma_clearing", "renunciation", "tapas"],
                            "MOON":    ["inner_mind_sensitivity", "spiritual_emotions"],
                            "VENUS":   ["bhakti", "devotional_arts"],
                            "MERCURY": ["mantra_power", "scriptural_insight"],
                        }
                        karmic_domains = _KARMIC_DOMAIN_MAP.get(planet_upper, [])

                combust_note = (
                    f"{planet_upper} is {combust_pct}% combust ({combust_orb_actual}\u00b0 from Sun). "
                    "Living significations (Karakatwa) are heavily suppressed. "
                    "Lordship events WILL manifest but with authority clashes, "
                    "ego friction, lack of recognition, and internal anxiety."
                )
                if karmic_amplified:
                    combust_note += (
                        f" KARMIC AMPLIFICATION ACTIVE: {planet_upper}'s spiritual domains "
                        f"{karmic_domains} are intensified (×{karmic_amplifier}) — "
                        f"karmic boost +{karmic_boost:.3f}."
                    )

    score = gochar_score + bav_score_component + sav_score_component + lagna_score
    score += kakshya["precision_boost"]   # Kakshya sub-precision ±0.05/0.02
    score += karmic_boost                 # Combustion karmic amplification (can add positive)
    score = max(0.0, min(1.0, score))

    return {
        "planet": planet,
        "transit_sign": SIGN_NAMES[transit_sign],
        "transit_sign_idx": transit_sign,
        "degree_in_sign": round(degree_in_sign, 2),
        "house_from_moon": house_from_moon,
        "is_favorable_gochar": is_favorable,
        "bav_score": bav_score,
        "sav_score": sav_score,
        "sav_above_avg": sav_score > sav_avg if sav_score else None,
        "vedha_blocked": vedha_blocked,
        "vedha_by": vedha_by,
        "vedha_keep_pct": round(vedha_keep_factor * 100, 1) if vedha_blocked else 100.0,
        "manifestation_zone_active": zone_mult == 1.0,
        "kakshya": kakshya,
        "combust": is_combust,
        "combust_orb": combust_orb_actual,
        "combust_pct": combust_pct,
        "combust_strength_retained": round(combust_strength_retained, 3),
        "karakatwa_burned": karakatwa_burned,
        "lordship_survives": lordship_survives,
        "karmic_amplified": karmic_amplified,
        "karmic_boost": karmic_boost,
        "karmic_domains": karmic_domains,
        "combust_note": combust_note,
        "net_score": round(score, 3),
        "interpretation": _gochar_interpretation(planet, house_from_moon),
    }


def _gochar_interpretation(planet: str, house_from_moon: int) -> str:
    """Plain-language transit interpretation using full 9-planet × 12-house GOCHAR_EFFECTS."""
    key = (planet.upper(), house_from_moon)
    entry = GOCHAR_EFFECTS.get(key)
    if entry:
        domain, description = entry
        return description
    # Generic fallback for entries not in the table (mixed/neutral houses)
    return f"{planet.capitalize()} transiting {house_from_moon}th from Moon — observe results"


def evaluate_all_transits(
        transit_positions: Dict[str, float],
        natal_moon_sign: int,
        bhinna_av: Optional[Dict[str, List[int]]] = None,
        sarva_av: Optional[List[int]] = None,
        natal_moon_nak: Optional[int] = None,
) -> Dict[str, Dict]:
    """Evaluate all planet transits including Tarabala and Chandrabala for Moon."""
    other_signs = {p: sign_of(lon) for p, lon in transit_positions.items()}
    sun_lon = transit_positions.get("SUN")   # for combustion check
    results = {}
    for pname, lon in transit_positions.items():
        bav = bhinna_av.get(pname) if bhinna_av else None
        results[pname] = evaluate_transit(
            planet=pname,
            transit_lon=lon,
            natal_moon_sign=natal_moon_sign,
            bhinna_av=bav,
            sarva_av=sarva_av,
            other_transit_signs=other_signs,
            transit_sun_lon=sun_lon,
        )

    # ── Tarabala (transit Moon nakshatra vs birth Moon nakshatra) ──
    if "MOON" in transit_positions and natal_moon_nak is not None:
        transit_moon_nak = nakshatra_of(transit_positions["MOON"])
        tarabala = compute_tarabala(natal_moon_nak, transit_moon_nak)
        results["MOON"]["tarabala"] = tarabala
        # Boost or reduce Moon transit score
        moon_entry = results["MOON"]
        tara_boost = tarabala["score"] * 0.15   # ±0.15 max
        moon_entry["net_score"] = round(
            max(0.0, min(1.0, moon_entry["net_score"] + tara_boost)), 3
        )

    # ── Chandrabala (transit Moon sign vs natal Moon sign) ─────────
    if "MOON" in transit_positions:
        transit_moon_sign = sign_of(transit_positions["MOON"])
        chandrabala = compute_chandrabala(natal_moon_sign, transit_moon_sign)
        results["MOON"]["chandrabala"] = chandrabala

    return results


def detect_sade_sati(
        transit_saturn_sign: int,
        natal_moon_sign: int,
        saturn_bav_by_sign: Optional[List[int]] = None,
) -> Dict:
    """
    Sade Sati = Saturn transiting 12th, 1st, or 2nd from natal Moon.
    Dhaiya = Saturn in 4th or 8th from Moon.
    Returns phase, intensity, and approximate dates.
    """
    saturn_from_moon = ((transit_saturn_sign - natal_moon_sign) % 12) + 1

    in_sade_sati = saturn_from_moon in (12, 1, 2)
    in_dhaiya = saturn_from_moon in (4, 8)

    phase = ""
    if saturn_from_moon == 12:
        phase = "Rising Phase (12th): mental pressure, foreign travel, expenses rise"
    elif saturn_from_moon == 1:
        phase = "Peak Phase (1st from Moon): health, identity challenges, major transformation"
    elif saturn_from_moon == 2:
        phase = "Setting Phase (2nd): financial strain, family pressure, ending of cycle"
    elif saturn_from_moon == 4:
        phase = "Dhaiya (4th): property/mother concerns, domestic challenges"
    elif saturn_from_moon == 8:
        phase = "Dhaiya (8th): obstacles, delays, introspection required"

    # Intensity modifier from Ashtakvarga
    intensity = "moderate"
    if saturn_bav_by_sign:
        bav_score = saturn_bav_by_sign[transit_saturn_sign]
        if bav_score >= 5:
            intensity = "mild (Saturn gives good results → high AV score)"
        elif bav_score <= 2:
            intensity = "intense (low AV score amplifies difficulties)"

    return {
        "in_sade_sati": in_sade_sati,
        "in_dhaiya": in_dhaiya,
        "saturn_from_moon": saturn_from_moon,
        "phase": phase,
        "intensity": intensity,
        "paya": _compute_paya(saturn_from_moon),
        "advice": (
            "Focus on discipline, service, patience. Avoid major new ventures in peak phase."
            if in_sade_sati else
            "Normal Saturn influence. Keep commitments, avoid shortcuts."
        ),
    }


# ─── Paya (Saturn Transit Quality by Moon House) ─────────────────
# Research: "Paya = Feet classification based on Moon's house relative to
# Saturn's transit ingress." — Vedic Astrology Computational Logic.md
#   Gold Paya   : Moon in 1, 6, 11 from transit Saturn → Very Auspicious
#   Silver Paya : Moon in 2, 5, 9             → Auspicious
#   Copper Paya : Moon in 3, 7, 10            → Average
#   Iron Paya   : Moon in 4, 8, 12            → Difficult

_PAYA_MAP = {
    1: ("Gold",   "Very Auspicious — Saturn transit carries hidden blessings"),
    6: ("Gold",   "Very Auspicious — Saturn transit carries hidden blessings"),
    11:("Gold",   "Very Auspicious — Saturn transit carries hidden blessings"),
    2: ("Silver", "Auspicious — some hardship with silver lining"),
    5: ("Silver", "Auspicious — some hardship with silver lining"),
    9: ("Silver", "Auspicious — some hardship with silver lining"),
    3: ("Copper", "Average — mixed results, effort required"),
    7: ("Copper", "Average — mixed results, effort required"),
    10:("Copper", "Average — mixed results, effort required"),
    4: ("Iron",   "Difficult — intensified pressure, patience key"),
    8: ("Iron",   "Difficult — intensified pressure, patience key"),
    12:("Iron",   "Difficult — intensified pressure, patience key"),
}


def _compute_paya(saturn_from_moon: int) -> dict:
    metal, desc = _PAYA_MAP.get(saturn_from_moon, ("Iron", "Unknown"))
    return {"metal": metal, "description": desc}
