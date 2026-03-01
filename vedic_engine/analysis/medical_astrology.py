"""
Medical Astrology Engine (Branch C).

Implements:
  C1: Anatomical body mapping (planet × sign × house)
  C2: Disease identification algorithm (Dusthana, cancer, psychiatric, arthritis)
  C3: Timing of health events (22nd Drekkana, Gulika, Dasha triggers)
  C4: Longevity calculation — Pindayu, Nisargayu, Amsayu + Balarishta check

Reference: File 5 (Algorithmic Vedic Astrology Engine Development-5.md)
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Any, Optional

# ────────────────────────────────────────────────────────────────────────────
# C1: Anatomical Body Mapping Matrix
# ────────────────────────────────────────────────────────────────────────────

BODY_MAP: List[Dict[str, Any]] = [
    {"system": "Brain, Head, Vitality",       "planet": "SUN",     "signs": ["Aries"],                      "houses": [1]},
    {"system": "Body Fluids, Chest, Breasts", "planet": "MOON",    "signs": ["Cancer"],                     "houses": [4]},
    {"system": "Blood, Muscles, Marrow",      "planet": "MARS",    "signs": ["Scorpio", "Aries"],           "houses": [6, 8]},
    {"system": "Lungs, Nerves, Speech",       "planet": "MERCURY", "signs": ["Gemini", "Virgo"],            "houses": [3, 6]},
    {"system": "Liver, Fat, Pancreas",        "planet": "JUPITER", "signs": ["Sagittarius"],                "houses": [5, 9]},
    {"system": "Kidneys, Reproductive, Skin", "planet": "VENUS",   "signs": ["Taurus", "Libra"],            "houses": [7]},
    {"system": "Bones, Joints, Teeth",        "planet": "SATURN",  "signs": ["Capricorn", "Aquarius"],      "houses": [10, 11]},
    {"system": "Toxins, Irregular Growth",    "planet": "RAHU",    "signs": [],                             "houses": [8]},
    {"system": "Immunity, Undiagnosed Pain",  "planet": "KETU",    "signs": [],                             "houses": [12]},
]

# Dusthana houses (disease triangle)
DUSTHANA = frozenset([6, 8, 12])

# ────────────────────────────────────────────────────────────────────────────
# C2: Disease Identification Algorithm
# ────────────────────────────────────────────────────────────────────────────

def _house_of(planet: str, planet_signs: Dict[str, str], lagna_sign: int) -> int:
    """Compute which house a planet is in (1-indexed)."""
    sign_name = planet_signs.get(planet, "")
    sign_order = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]
    if sign_name not in sign_order:
        return 0
    p_sign_idx = sign_order.index(sign_name)
    house = ((p_sign_idx - lagna_sign) % 12) + 1
    return house


def analyze_disease_potential(
        planet_signs: Dict[str, str],
        planet_houses: Dict[str, int],
        lagna_sign: int,
) -> List[Dict[str, Any]]:
    """
    Identify disease vulnerabilities from planetary configurations.
    Returns list of detected pathological patterns with descriptions.
    """
    alerts: List[Dict[str, Any]] = []
    ph = planet_houses  # convenience alias

    def in_dusthana(planet: str) -> bool:
        return ph.get(planet, 0) in DUSTHANA

    # ─── Mars + Saturn in 6th or 8th: Arthritis / Surgery ───────────────────
    mars_h = ph.get("MARS", 0)
    saturn_h = ph.get("SATURN", 0)
    if mars_h in (6, 8) and saturn_h in (6, 8):
        alerts.append({
            "condition": "Severe Arthritis / Complex Fracture / Surgery Risk",
            "planets": ["MARS", "SATURN"],
            "trigger": f"Mars in H{mars_h} + Saturn in H{saturn_h}",
            "severity": "HIGH",
        })
    elif mars_h == saturn_h and mars_h in DUSTHANA:
        alerts.append({
            "condition": "Inflammatory Bone/Joint Disease",
            "planets": ["MARS", "SATURN"],
            "trigger": f"Mars-Saturn conjunct in H{mars_h} (Dusthana)",
            "severity": "MEDIUM",
        })

    # ─── Cancer indicatiors: Moon afflicted + Rahu/Ketu + Saturn in Dusthana ─
    moon_h = ph.get("MOON", 0)
    rahu_h = ph.get("RAHU", 0)
    ketu_h = ph.get("KETU", 0)

    moon_afflicted = moon_h in DUSTHANA
    rahu_in_dusthana = rahu_h in DUSTHANA
    ketu_in_dusthana = ketu_h in DUSTHANA
    saturn_in_dusthana = saturn_h in DUSTHANA

    if moon_afflicted and (rahu_in_dusthana or ketu_in_dusthana) and saturn_in_dusthana:
        alerts.append({
            "condition": "Malignancy / Cancer Risk",
            "planets": ["MOON", "RAHU/KETU", "SATURN"],
            "trigger": (f"Afflicted Moon (H{moon_h}) + Rahu/Ketu in Dusthana "
                        f"+ Saturn (H{saturn_h}) in Dusthana"),
            "severity": "HIGH",
            "note": "Triple confluence: lymphatic disruption + toxic growth + chronicity",
        })

    # ─── Moon + Saturn + Rahu conjunct in 6th: GI / Breast malignancy ────────
    if (moon_h == saturn_h == rahu_h) and moon_h == 6:
        alerts.append({
            "condition": "Gastrointestinal or Breast Malignancy",
            "planets": ["MOON", "SATURN", "RAHU"],
            "trigger": "Moon + Saturn + Rahu in 6th house",
            "severity": "VERY HIGH",
        })

    # ─── Psychiatric / Autoimmune: Afflicted Moon + Mercury + Ketu ───────────
    mercury_h = ph.get("MERCURY", 0)
    if moon_afflicted and mercury_h in DUSTHANA and ketu_in_dusthana:
        alerts.append({
            "condition": "Psychiatric Disorder / Autoimmune / Neurological",
            "planets": ["MOON", "MERCURY", "KETU"],
            "trigger": (f"Afflicted Moon (H{moon_h}) + Mercury (H{mercury_h}) "
                        f"+ Ketu (H{ketu_h}) in Dusthana"),
            "severity": "HIGH",
            "note": "Mental health degradation, autoimmune origin obfuscated",
        })

    # ─── Mars in 6th/8th alone: Inflammatory conditions ──────────────────────
    if mars_h in (6, 8) and saturn_h not in (6, 8):
        alerts.append({
            "condition": "Inflammation / Ulceration / Bleeding",
            "planets": ["MARS"],
            "trigger": f"Mars in H{mars_h} (Dusthana)",
            "severity": "MEDIUM",
        })

    # ─── Saturn in 6th/8th alone: Chronic degenerative ───────────────────────
    if saturn_h in (6, 8) and mars_h not in (6, 8):
        alerts.append({
            "condition": "Chronic Condition / Bone Degradation / Blockage",
            "planets": ["SATURN"],
            "trigger": f"Saturn in H{saturn_h} (Dusthana)",
            "severity": "MEDIUM",
        })

    return alerts


# ────────────────────────────────────────────────────────────────────────────
# C3: 22nd Drekkana + Health Timing
# ────────────────────────────────────────────────────────────────────────────

def compute_22nd_drekkana(lagna_longitude: float) -> Dict[str, Any]:
    """
    Compute the 22nd Drekkana (Khara) — the 8th house of D-3 chart.

    D-3 Lagna = Lagna sign (same element series).
    8th house from D-3 Lagna = the "Khara" (malefic) point.
    22nd Drekkana = 8th from D-3 Lagna = spans 10° of parent sign.

    Returns the degree range and sign of the 22nd Drekkana.
    """
    SIGN_NAMES = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]
    # D-3 Lagna sign: same element sign progression
    # Fire: Aries(0), Leo(4), Sagittarius(8)
    # Earth: Taurus(1), Virgo(5), Capricorn(9)
    # Air: Gemini(2), Libra(6), Aquarius(10)
    # Water: Cancer(3), Scorpio(7), Pisces(11)
    lon = lagna_longitude % 360.0
    lagna_sign_idx = int(lon / 30)
    pos_in_sign = lon % 30

    # Drekkana within sign: 0-9°=first, 10-19°=second, 20-29°=third
    if pos_in_sign < 10:
        decan = 0
    elif pos_in_sign < 20:
        decan = 1
    else:
        decan = 2

    # D-3 Lagna sign index (same element, stepped by 4 for next element sign)
    element_base = lagna_sign_idx  # Aries=0, Taurus=1, ...
    d3_lagna_idx = (element_base + decan * 4) % 12

    # 22nd Drekkana = 8th house in D-3, 3 decans per sign → (8-1)*3+2 = 23rd decan overall
    # Actually: 22nd Drekkana = decan 22 counting from Aries first decan
    # = sign_idx = (22-1) // 3 = 7 = Scorpio, decan = (22-1)%3 = 0 = 0-10°
    # But the "22nd from Lagna" version: 7th house in D-3 from d3_lagna
    # Standard: 22nd drekkana = 8th house from D-3 lagna (Scorpio logic)
    # We implement as: the 7 signs from D-3 Lagna (i.e., 7th sign away)

    eighth_d3_sign_idx = (d3_lagna_idx + 7) % 12  # 8th house = 7 signs ahead
    eighth_d3_sign = SIGN_NAMES[eighth_d3_sign_idx]

    # The decan within the 8th D-3 sign maps back to parent chart span:
    # Each D-3 sign spans 10° of the zodiac in sequence
    # Parent sign = eighth_d3_sign_idx // 3 (roughly), decan = eighth_d3_sign_idx % 3
    parent_sign_idx = (eighth_d3_sign_idx * 10) // 30
    decan_within = eighth_d3_sign_idx % 3
    start_deg = parent_sign_idx * 30 + decan_within * 10
    end_deg = start_deg + 10

    # Planetary lord of 22nd Drekkana sign
    _SIGN_LORDS_STR = {
        "Aries": "MARS", "Taurus": "VENUS", "Gemini": "MERCURY",
        "Cancer": "MOON", "Leo": "SUN", "Virgo": "MERCURY",
        "Libra": "VENUS", "Scorpio": "MARS", "Sagittarius": "JUPITER",
        "Capricorn": "SATURN", "Aquarius": "SATURN", "Pisces": "JUPITER",
    }
    lord = _SIGN_LORDS_STR.get(eighth_d3_sign, "?")

    return {
        "d3_lagna_sign": SIGN_NAMES[d3_lagna_idx],
        "khara_sign": eighth_d3_sign,
        "lord": lord,
        "zodiac_span": f"{start_deg}°–{end_deg}°",
        "note": (f"22nd Drekkana (Khara) = {eighth_d3_sign} ruled by {lord}. "
                 f"Transiting malefic (Saturn/Rahu) crossing this span signals "
                 f"acute illness or bodily threat."),
    }


def analyze_health_timing(
        planet_houses: Dict[str, int],
        active_dasha_planet: str,
        active_antardasha_planet: str,
) -> Dict[str, Any]:
    """
    Flag health crisis periods based on Dasha/Antardasha of 6th/8th lords.
    """
    DUSTHANA = frozenset([6, 8, 12])
    triggers: List[str] = []
    severity = "LOW"

    if planet_houses.get(active_dasha_planet, 0) in DUSTHANA:
        triggers.append(
            f"Maha Dasha of {active_dasha_planet} (H{planet_houses[active_dasha_planet]}) — Dusthana lord"
        )
        severity = "MEDIUM"

    if planet_houses.get(active_antardasha_planet, 0) in DUSTHANA:
        triggers.append(
            f"Antardasha of {active_antardasha_planet} (H{planet_houses[active_antardasha_planet]}) — Dusthana lord"
        )
        severity = "HIGH" if severity == "MEDIUM" else "MEDIUM"

    if not triggers:
        triggers.append("No active Dusthana lord in current Dasha/Antardasha.")
        severity = "LOW"

    return {
        "active_dasha": active_dasha_planet,
        "active_antardasha": active_antardasha_planet,
        "triggers": triggers,
        "health_risk_level": severity,
    }


# ────────────────────────────────────────────────────────────────────────────
# C4: Longevity Calculation (Ayurdaya)
# ────────────────────────────────────────────────────────────────────────────

# Pindayu base years (at full exaltation)
_PINDAYU_BASE = {
    "SUN": 19, "MOON": 25, "MARS": 15, "MERCURY": 12,
    "JUPITER": 15, "VENUS": 21, "SATURN": 20,
}

# Nisargayu base years (different bases)
_NISARGAYU_BASE = {
    "SUN": 20, "MOON": 1, "MARS": 2, "MERCURY": 9,
    "JUPITER": 18, "VENUS": 20, "SATURN": 50,
}

# Deep exaltation degrees for each planet (sidereal)
_EXALT_DEG = {
    "SUN": 10.0,      # Aries 10°
    "MOON": 33.0,     # Taurus 3°  → 30+3
    "MARS": 298.0,    # Capricorn 28° → 270+28
    "MERCURY": 165.0, # Virgo 15° → 150+15
    "JUPITER": 95.0,  # Cancer 5° → 90+5
    "VENUS": 357.0,   # Pisces 27° → 330+27
    "SATURN": 200.0,  # Libra 20° → 180+20
}


def _effective_arc(planet: str, longitude: float) -> float:
    """
    Effective Arc of Longevity = |longitude - exaltation_point|.
    If > 180°, reduce by 180°. Used in Pindayu/Nisargayu.
    """
    exalt = _EXALT_DEG.get(planet, 0.0)
    arc = abs((longitude % 360.0) - exalt)
    if arc > 180:
        arc -= 180
    return arc


def _apply_haranas(
        gross_years: float,
        planet: str,
        longitude: float,
        planet_signs: Dict[str, str],
        lagna_sign: int,
        combust_planets: List[str],
) -> Tuple[float, List[str]]:
    """
    Apply Harana (reduction) factors to gross longevity years.
    Returns (net_years, list_of_applied_haranas).
    """
    SIGN_LORDS_STR = {
        "Aries": "MARS", "Taurus": "VENUS", "Gemini": "MERCURY",
        "Cancer": "MOON", "Leo": "SUN", "Virgo": "MERCURY",
        "Libra": "VENUS", "Scorpio": "MARS", "Sagittarius": "JUPITER",
        "Capricorn": "SATURN", "Aquarius": "SATURN", "Pisces": "JUPITER",
    }
    EXALT_SIGNS = {
        "SUN": "Aries", "MOON": "Taurus", "MARS": "Capricorn",
        "MERCURY": "Virgo", "JUPITER": "Cancer", "VENUS": "Pisces", "SATURN": "Libra",
    }
    DEBIL_SIGNS = {
        "SUN": "Libra", "MOON": "Scorpio", "MARS": "Cancer",
        "MERCURY": "Pisces", "JUPITER": "Capricorn", "VENUS": "Virgo", "SATURN": "Aries",
    }
    FRIEND_MAP = {
        "SUN": ["MOON", "MARS", "JUPITER"],
        "MOON": ["SUN", "MERCURY"],
        "MARS": ["SUN", "MOON", "JUPITER"],
        "MERCURY": ["SUN", "VENUS"],
        "JUPITER": ["SUN", "MOON", "MARS"],
        "VENUS": ["MERCURY", "SATURN"],
        "SATURN": ["MERCURY", "VENUS"],
    }

    net = gross_years
    applied: List[str] = []

    # Astangata (combustion): halve the value
    if planet in combust_planets:
        net /= 2.0
        applied.append(f"Astangata (combustion) → ÷2")

    # Shatrukshetra (enemy sign): reduce by 1/3
    sign_name = planet_signs.get(planet, "")
    sign_lord = SIGN_LORDS_STR.get(sign_name, "")
    friends = FRIEND_MAP.get(planet, [])
    if sign_lord and sign_lord not in friends and sign_lord != planet:
        if sign_name != EXALT_SIGNS.get(planet, "") and sign_name != DEBIL_SIGNS.get(planet, ""):
            net *= (2.0 / 3.0)
            applied.append(f"Shatrukshetra (enemy sign {sign_name}) → ×2/3")

    # Chakrapata (visible hemisphere): subtract 1/4 if below horizon (houses 1-6 approximate)
    # Approximate: planet in houses 7-12 = above horizon = visible; 1-6 = below
    # We use lagna_sign and planet sign to estimate house
    sign_order = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]
    if sign_name in sign_order:
        p_sign_idx = sign_order.index(sign_name)
        p_house = ((p_sign_idx - lagna_sign) % 12) + 1
        if p_house <= 6:  # below horizon
            net *= 0.75
            applied.append(f"Chakrapata (below horizon, H{p_house}) → ×3/4")

    return round(net, 2), applied


def compute_pindayu(
        planet_lons: Dict[str, float],
        planet_signs: Dict[str, str],
        lagna_sign: int,
        combust_planets: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Pindayu Longevity: sum of individual planet contributions.
    Best when Sun is strongest.
    """
    if combust_planets is None:
        combust_planets = []

    total: float = 0.0
    details: List[Dict] = []

    planets = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]
    for p in planets:
        if p not in planet_lons:
            continue
        lon = planet_lons[p]
        base = _PINDAYU_BASE[p]
        arc = _effective_arc(p, lon)
        gross = base * (arc / 360.0)
        net, haranas = _apply_haranas(gross, p, lon, planet_signs, lagna_sign, combust_planets)
        total += net
        details.append({
            "planet": p,
            "base_years": base,
            "effective_arc": round(arc, 2),
            "gross_years": round(gross, 2),
            "net_years": net,
            "haranas": haranas,
        })

    return {
        "method": "Pindayu",
        "applicable_when": "Sun is strongest among Sun/Moon/Lagna",
        "total_years": round(total, 1),
        "details": details,
    }


def compute_nisargayu(
        planet_lons: Dict[str, float],
        planet_signs: Dict[str, str],
        lagna_sign: int,
        combust_planets: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Nisargayu Longevity: similar to Pindayu but different base years.
    Best when Moon is strongest.
    """
    if combust_planets is None:
        combust_planets = []

    total: float = 0.0
    details: List[Dict] = []

    planets = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]
    for p in planets:
        if p not in planet_lons:
            continue
        lon = planet_lons[p]
        base = _NISARGAYU_BASE[p]
        arc = _effective_arc(p, lon)
        gross = base * (arc / 360.0)
        net, haranas = _apply_haranas(gross, p, lon, planet_signs, lagna_sign, combust_planets)
        total += net
        details.append({
            "planet": p,
            "base_years": base,
            "effective_arc": round(arc, 2),
            "gross_years": round(gross, 2),
            "net_years": net,
            "haranas": haranas,
        })

    return {
        "method": "Nisargayu",
        "applicable_when": "Moon is strongest among Sun/Moon/Lagna",
        "total_years": round(total, 1),
        "details": details,
    }


def compute_amsayu(
        planet_lons: Dict[str, float],
        planet_signs: Dict[str, str],
        lagna_sign: int,
        vargottama_planets: Optional[List[str]] = None,
        retrograde_planets: Optional[List[str]] = None,
        combust_planets: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Amsayu Longevity: based strictly on Navamsa degrees.
    Best when Lagna is strongest.
    Incorporates Bharanas (increases) for exalted/retrograde/vargottama.
    """
    if vargottama_planets is None:
        vargottama_planets = []
    if retrograde_planets is None:
        retrograde_planets = []
    if combust_planets is None:
        combust_planets = []

    EXALT_SIGNS_MAP = {
        "SUN": "Aries", "MOON": "Taurus", "MARS": "Capricorn",
        "MERCURY": "Virgo", "JUPITER": "Cancer", "VENUS": "Pisces", "SATURN": "Libra",
    }

    total: float = 0.0
    details: List[Dict] = []

    planets = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]
    for p in planets:
        if p not in planet_lons:
            continue
        lon = planet_lons[p] % 360.0
        lon_minutes = lon * 60.0  # convert degrees to arc-minutes

        # Base: lon_minutes / 200, mod 12
        base_raw = (lon_minutes / 200.0) % 12.0
        base = base_raw

        # Bharana (increases)
        sign_name = planet_signs.get(p, "")
        multiplier = 1.0
        bharana_notes: List[str] = []
        if sign_name == EXALT_SIGNS_MAP.get(p, ""):
            multiplier *= 3.0
            bharana_notes.append("×3 (exalted)")
        elif p in retrograde_planets:
            multiplier *= 3.0
            bharana_notes.append("×3 (retrograde)")
        elif p in vargottama_planets:
            multiplier *= 2.0
            bharana_notes.append("×2 (vargottama)")

        gross = base * multiplier

        # Amsayu uses same Haranas EXCEPT Krurodaya is bypassed
        net = gross
        haranas: List[str] = []

        # Astangata (combustion): halve
        if p in combust_planets:
            net /= 2.0
            haranas.append("Astangata ÷2")

        # Chakrapata (visible hemisphere): ×3/4 if houses 1-6
        sign_order = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
        ]
        if sign_name in sign_order:
            p_sign_idx = sign_order.index(sign_name)
            p_house = ((p_sign_idx - lagna_sign) % 12) + 1
            if p_house <= 6:
                net *= 0.75
                haranas.append(f"Chakrapata ×3/4 (H{p_house})")

        total += net
        details.append({
            "planet": p,
            "lon_degrees": round(lon, 3),
            "base_raw": round(base_raw, 3),
            "multiplier": multiplier,
            "gross": round(gross, 2),
            "net_years": round(net, 2),
            "bharana": bharana_notes,
            "haranas": haranas,
        })

    return {
        "method": "Amsayu",
        "applicable_when": "Lagna is strongest among Sun/Moon/Lagna",
        "total_years": round(total, 1),
        "details": details,
    }


def check_balarishta(
        moon_house: int,
        moon_aspects_from: Optional[List[str]] = None,
        benefic_mitigators: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Balarishta: infant mortality check.

    If natal Moon is in 6th, 8th, or 12th, flanked/aspected by cruel malefics
    WITHOUT benefic intervention → high infant mortality probability.
    Long-term Ayurdaya calculations become null if triggered.
    """
    if moon_aspects_from is None:
        moon_aspects_from = []
    if benefic_mitigators is None:
        benefic_mitigators = []

    MALEFICS = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}
    BENEFICS = {"MOON", "MERCURY", "JUPITER", "VENUS"}

    in_dusthana = moon_house in (6, 8, 12)
    malefic_aspects = [p for p in moon_aspects_from if p in MALEFICS]
    benefic_aspects = [p for p in moon_aspects_from if p in BENEFICS]
    has_mitigation = bool(set(benefic_mitigators) & BENEFICS) or bool(benefic_aspects)

    if in_dusthana and malefic_aspects and not has_mitigation:
        return {
            "balarishta": True,
            "moon_house": moon_house,
            "malefic_aspects": malefic_aspects,
            "benefic_mitigation": False,
            "verdict": "HIGH INFANT MORTALITY RISK — Moon in Dusthana + malefic aspects + no benefic relief",
            "ayurdaya_valid": False,
            "note": "Standard longevity calculations overridden by Balarishta yoga.",
        }
    elif in_dusthana and malefic_aspects and has_mitigation:
        return {
            "balarishta": False,
            "moon_house": moon_house,
            "malefic_aspects": malefic_aspects,
            "benefic_mitigation": True,
            "verdict": "Balarishta MITIGATED by benefic intervention — moderate early-life health challenges",
            "ayurdaya_valid": True,
            "note": "Benefic cancels infant mortality risk but health vulnerabilities remain in early years.",
        }
    else:
        return {
            "balarishta": False,
            "moon_house": moon_house,
            "malefic_aspects": malefic_aspects,
            "benefic_mitigation": has_mitigation,
            "verdict": "No Balarishta — normal longevity calculations apply",
            "ayurdaya_valid": True,
            "note": "Moon not in Dusthana; standard Ayurdaya models are valid.",
        }


def synthesize_longevity(
        pindayu: Dict[str, Any],
        nisargayu: Dict[str, Any],
        amsayu: Dict[str, Any],
        strongest_entity: str,  # "SUN", "MOON", or "LAGNA"
        balarishta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Synthesize final longevity estimate from the three methods.
    If multiple entities share equal strength, average the results.
    Balarishta overrides all calculations if triggered.
    """
    if balarishta and not balarishta.get("ayurdaya_valid", True):
        return {
            "final_estimate_years": None,
            "method_used": "BALARISHTA OVERRIDE",
            "note": balarishta["verdict"],
            "balarishta": True,
        }

    if strongest_entity == "SUN":
        estimate = pindayu["total_years"]
        method = "Pindayu (Sun strongest)"
    elif strongest_entity == "MOON":
        estimate = nisargayu["total_years"]
        method = "Nisargayu (Moon strongest)"
    elif strongest_entity == "LAGNA":
        estimate = amsayu["total_years"]
        method = "Amsayu (Lagna strongest)"
    else:
        # Equal strength — average all three
        estimate = (pindayu["total_years"] + nisargayu["total_years"] + amsayu["total_years"]) / 3.0
        method = "Average of Pindayu + Nisargayu + Amsayu (equal strength)"

    return {
        "final_estimate_years": round(estimate, 1),
        "method_used": method,
        "pindayu_years": pindayu["total_years"],
        "nisargayu_years": nisargayu["total_years"],
        "amsayu_years": amsayu["total_years"],
        "balarishta": False,
        "note": f"Longevity estimate based on {method}.",
    }


def compute_medical_analysis(
        planet_lons: Dict[str, float],
        planet_signs: Dict[str, str],
        planet_houses: Dict[str, int],
        lagna_sign: int,
        lagna_longitude: float,
        combust_planets: Optional[List[str]] = None,
        retrograde_planets: Optional[List[str]] = None,
        vargottama_planets: Optional[List[str]] = None,
        strongest_entity: str = "SUN",
) -> Dict[str, Any]:
    """
    Master medical analysis entry point.
    Returns complete medical profile: body map, diseases, longevity, Balarishta.
    """
    if combust_planets is None:
        combust_planets = []
    if retrograde_planets is None:
        retrograde_planets = []
    if vargottama_planets is None:
        vargottama_planets = []

    diseases = analyze_disease_potential(planet_signs, planet_houses, lagna_sign)
    drekkana_22 = compute_22nd_drekkana(lagna_longitude)

    moon_house = planet_houses.get("MOON", 0)
    moon_afflictors: List[str] = []
    for p, h in planet_houses.items():
        if h == moon_house and p != "MOON" and p in {"SUN", "MARS", "SATURN", "RAHU", "KETU"}:
            moon_afflictors.append(p)

    balarishta = check_balarishta(moon_house, moon_afflictors, ["JUPITER", "VENUS"])

    pindayu = compute_pindayu(planet_lons, planet_signs, lagna_sign, combust_planets)
    nisargayu = compute_nisargayu(planet_lons, planet_signs, lagna_sign, combust_planets)
    amsayu = compute_amsayu(planet_lons, planet_signs, lagna_sign,
                            vargottama_planets, retrograde_planets, combust_planets)

    longevity = synthesize_longevity(pindayu, nisargayu, amsayu, strongest_entity, balarishta)

    return {
        "disease_alerts": diseases,
        "disease_count": len(diseases),
        "drekkana_22": drekkana_22,
        "balarishta": balarishta,
        "pindayu": pindayu,
        "nisargayu": nisargayu,
        "amsayu": amsayu,
        "longevity": longevity,
    }
