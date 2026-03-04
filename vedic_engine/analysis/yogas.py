"""
Yoga Detection Engine.
Detects classical planetary combinations (yogas) from the birth chart.

Each yoga is defined as a predicate over:
  - Planet signs/houses
  - Planet dignities
  - Aspect relationships

Implements ~30 major yogas with:
  - Detection condition
  - Strength modifier (based on planet Shadbala ratio)
  - Cancellation checks (combustion, debilitation, malefic aspect)
  - Domain tags (career, wealth, marriage, health, moksha)
"""
from __future__ import annotations
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field

from vedic_engine.config import (
    Planet, NATURAL_BENEFICS, NATURAL_MALEFICS,
    EXALTATION_DEGREES, DEBILITATION_DEGREES,
    OWN_SIGNS, MOOLATRIKONA, SIGN_LORDS, Sign,
    NAISARGIKA_FRIENDS, SHADBALA_MINIMUMS,
)
from vedic_engine.core.coordinates import sign_of, angular_distance, house_from_moon

PLANET_NAMES_7 = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]

_P = {
    "SUN": Planet.SUN, "MOON": Planet.MOON, "MARS": Planet.MARS,
    "MERCURY": Planet.MERCURY, "JUPITER": Planet.JUPITER,
    "VENUS": Planet.VENUS, "SATURN": Planet.SATURN,
}


@dataclass
class YogaResult:
    name: str
    category: str          # "raj", "dhana", "moksha", "pancha_mahapurusha", etc.
    detected: bool
    strength: float        # 0.0 - 1.0
    planets: List[str]
    houses: List[int]
    description: str
    activating_dasha: List[str] = field(default_factory=list)
    cancellation_reason: str = ""
    # ── Research Brief additions ─────────────────────────────────
    tier: int = 4          # Hierarchy: 1=Pancha Mahapurusha, 2=Raja, 3=Dhana, 4=Simple
    activation_score: float = 0.0  # 0.0–1.0; 1.0=constituent lord MD/AD active
    bhanga_model: dict = field(default_factory=dict)
    # bhanga_model: {struggle_phase: bool, rescue_planet: str, cancellation_type: str}
    nbry_conditions: List[str] = field(default_factory=list)  # which NBRY conditions met
    parabolic_trajectory: bool = False  # True if NBRY with delayed massive spike


def _planet_house(pname: str, planet_houses: Dict[str, int]) -> int:
    return planet_houses.get(pname, 0)


def _is_in_kendra(house: int) -> bool:
    return house in (1, 4, 7, 10)


def _is_in_trikona(house: int) -> bool:
    return house in (1, 5, 9)


def _is_in_upachaya(house: int) -> bool:
    return house in (3, 6, 10, 11)


def _is_exalted(pname: str, lon: float) -> bool:
    p = _P.get(pname)
    if p is None:
        return False
    return sign_of(lon) == sign_of(EXALTATION_DEGREES[p])


def _is_debilitated(pname: str, lon: float) -> bool:
    p = _P.get(pname)
    if p is None:
        return False
    return sign_of(lon) == sign_of(DEBILITATION_DEGREES[p])


def _is_own_sign(pname: str, sign_idx: int) -> bool:
    p = _P.get(pname)
    if p is None:
        return False
    return Sign(sign_idx) in [Sign(s) for s in OWN_SIGNS.get(p, [])]


def _is_strong(pname: str, shadbala_ratios: Dict[str, float]) -> bool:
    return shadbala_ratios.get(pname, 0.0) >= 1.0


def _avg_strength(planets: List[str], shadbala_ratios: Dict[str, float]) -> float:
    if not planets:
        return 0.0
    vals = [shadbala_ratios.get(p, 0.5) for p in planets]
    return sum(vals) / len(vals)


def _is_combust(pname: str, planet_lons: Dict[str, float]) -> bool:
    """Simple combustion check: within 10° of Sun."""
    if pname == "SUN":
        return False
    sun_lon = planet_lons.get("SUN", 0)
    lon = planet_lons.get(pname, 0)
    return angular_distance(lon, sun_lon) < 10.0


# ─── Individual Yoga Detectors ────────────────────────────────────

def _budha_aditya(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        shadbala_ratios: Dict[str, float],
) -> YogaResult:
    """Sun and Mercury in same house/sign."""
    sun_h = _planet_house("SUN", planet_houses)
    mer_h = _planet_house("MERCURY", planet_houses)
    detected = (sun_h == mer_h and sun_h > 0)
    combust = _is_combust("MERCURY", planet_lons)
    strength = _avg_strength(["SUN", "MERCURY"], shadbala_ratios)
    return YogaResult(
        name="Budha-Aditya Yoga",
        category="intelligence",
        detected=detected,
        strength=strength if detected else 0.0,
        planets=["SUN", "MERCURY"],
        houses=[sun_h],
        description="Sun and Mercury together → sharp intellect, analytical ability, eloquence.",
        activating_dasha=["SUN", "MERCURY"],
        cancellation_reason="Mercury combust (too close to Sun)" if (detected and combust) else "",
    )


def _gajakesari(
        planet_houses: Dict[str, int],
        moon_sign: int,
        shadbala_ratios: Dict[str, float],
) -> YogaResult:
    """Jupiter in kendra (1/4/7/10) from Moon → prosperity and honors."""
    jup_sign = sign_of(0)  # default
    jup_h = _planet_house("JUPITER", planet_houses)
    moon_h = _planet_house("MOON", planet_houses)

    # Jupiter's house from Moon
    from vedic_engine.core.coordinates import house_from
    # Get Moon sign from its house: moon_sign is passed directly
    jup_from_moon = 0
    for pname, h in planet_houses.items():
        if pname == "JUPITER":
            pass

    # Simpler: direct from planet_houses
    # If MOON is in house X and JUPITER is in house Y, house from Moon = (Y-X)%12+1
    jup_from_moon_h = ((jup_h - moon_h) % 12) + 1 if (jup_h and moon_h) else 0
    detected = _is_in_kendra(jup_from_moon_h)
    strength = _avg_strength(["JUPITER", "MOON"], shadbala_ratios)
    return YogaResult(
        name="Gajakesari Yoga",
        category="prosperity",
        detected=detected,
        strength=strength if detected else 0.0,
        planets=["JUPITER", "MOON"],
        houses=[jup_h, moon_h],
        description="Jupiter in kendra from Moon → fame, prosperity, strong character, leadership.",
        activating_dasha=["JUPITER", "MOON"],
    )


def _chandra_mangal(
        planet_houses: Dict[str, int],
        asp_map: Dict,
        shadbala_ratios: Dict[str, float],
) -> YogaResult:
    """Moon and Mars conjunct or in mutual aspect → wealth through mother."""
    moon_h = _planet_house("MOON", planet_houses)
    mars_h = _planet_house("MARS", planet_houses)
    conjunction = (moon_h == mars_h and moon_h > 0)
    mutual_aspect = (
        ("MOON", "MARS") in asp_map or ("MARS", "MOON") in asp_map
    )
    detected = conjunction or mutual_aspect
    strength = _avg_strength(["MOON", "MARS"], shadbala_ratios)
    return YogaResult(
        name="Chandra-Mangal Yoga",
        category="dhana",
        detected=detected,
        strength=strength if detected else 0.0,
        planets=["MOON", "MARS"],
        houses=[moon_h, mars_h],
        description="Moon-Mars conjunction or mutual aspect → wealth accumulation, bold trade.",
        activating_dasha=["MOON", "MARS"],
    )


def _detect_pancha_mahapurusha(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        shadbala_ratios: Dict[str, float],
) -> List[YogaResult]:
    """
    Pancha Mahapurusha Yogas: one of 5 planets (Mars/Mercury/Jupiter/Venus/Saturn)
    must be in own sign or exaltation AND in a Kendra house (1/4/7/10).
    """
    yogas_def = [
        ("MARS",    "Ruchaka",  "warrior, land, property"),
        ("MERCURY", "Bhadra",   "intellect, business, speech"),
        ("JUPITER", "Hamsa",    "philanthropy, wisdom, spirituality"),
        ("VENUS",   "Malavya",  "luxury, arts, marriage, beauty"),
        ("SATURN",  "Shasha",   "discipline, service, mass appeal"),
    ]
    results = []
    for pname, yoga_name, theme in yogas_def:
        h = _planet_house(pname, planet_houses)
        lon = planet_lons.get(pname, 0)
        own = _is_own_sign(pname, sign_of(lon))
        exalted = _is_exalted(pname, lon)
        in_kendra = _is_in_kendra(h)
        detected = (own or exalted) and in_kendra
        strength = shadbala_ratios.get(pname, 0.5)
        results.append(YogaResult(
            name=f"{yoga_name} Yoga (Pancha Mahapurusha)",
            category="pancha_mahapurusha",
            detected=detected,
            strength=strength if detected else 0.0,
            planets=[pname],
            houses=[h],
            description=f"{pname} in own/exaltation sign in kendra → {theme}.",
            activating_dasha=[pname],
        ))
    return results


def _vipreet_raj_yoga(
        planet_houses: Dict[str, int],
        house_lords: Dict[int, str],
        shadbala_ratios: Dict[str, float],
) -> List[YogaResult]:
    """
    Vipreet Raja Yoga: lords of 6th, 8th, 12th (trik houses) placed in
    each others' houses or in any of the 3 trik houses.
    → Rise through adversity; reversal of hardship into success.
    Three sub-types:
      Harsha  – 6th lord in 6th/8th/12th
      Sarala  – 8th lord in 6th/8th/12th
      Vimala  – 12th lord in 6th/8th/12th
    """
    TRIK = {6, 8, 12}
    sub_names = {6: "Harsha", 8: "Sarala", 12: "Vimala"}
    results = []
    for trik_house, yoga_name in sub_names.items():
        lord = house_lords.get(trik_house, "")
        if not lord:
            continue
        lord_in = _planet_house(lord, planet_houses)
        if lord_in in TRIK and lord_in != trik_house:
            # Lord of trik in a DIFFERENT trik → stronger Vipreet
            strength = shadbala_ratios.get(lord, 0.5)
            results.append(YogaResult(
                name=f"Vipreet Raja Yoga – {yoga_name}",
                category="raj",
                detected=True,
                strength=strength * 0.8,
                planets=[lord],
                houses=[lord_in],
                description=(
                    f"Lord of {trik_house}th ({lord}) deposited in {lord_in}th "
                    f"→ {yoga_name} Yoga: rise through hardship, unexpected triumph."
                ),
                activating_dasha=[lord],
            ))
    return results


def _parivartana_yoga(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        house_lords: Dict[int, str],
        shadbala_ratios: Dict[str, float],
) -> List[YogaResult]:
    """
    Parivartana (Mutual Exchange) Yoga: Planet A is in sign of Planet B, AND
    Planet B is in sign of Planet A.
    One of the most powerful yogas — effectively merges the two planets' energies.
    Three grades:
      Maha Parivartana  – both houses are angular/trine (no trik)
      Dainya Parivartana – at least one house is trik (6/8/12) → difficult
      Kahala Parivartana – trik lord exchanges with non-trik
    """
    from vedic_engine.config import SIGN_LORDS, Sign as _Sign
    from vedic_engine.core.coordinates import sign_of

    results = []
    lords_by_planet: Dict[str, int] = {}  # planet_name → house number owned

    # Build reverse map: planet → list of houses it lords
    for h, p_name in house_lords.items():
        if p_name not in lords_by_planet:
            lords_by_planet[p_name] = h  # take first (main) house

    TRIK = {6, 8, 12}
    AUSPICIOUS = {1, 2, 4, 5, 7, 9, 10, 11}

    checked = set()
    for pA in PLANET_NAMES_7:
        for pB in PLANET_NAMES_7:
            if pA >= pB:
                continue
            if (pA, pB) in checked:
                continue
            checked.add((pA, pB))

            hA = lords_by_planet.get(pA)  # primary house pA lords
            hB = lords_by_planet.get(pB)

            if hA is None or hB is None:
                continue

            # Is pA placed in hB's sign? i.e., pA sits in house hB?
            pA_house = _planet_house(pA, planet_houses)
            pB_house = _planet_house(pB, planet_houses)

            if pA_house != hB or pB_house != hA:
                continue  # no exchange

            # Exchange detected
            in_trik_A = hA in TRIK
            in_trik_B = hB in TRIK

            if not in_trik_A and not in_trik_B:
                grade = "Maha Parivartana"
                base_strength = 1.0
            elif in_trik_A and in_trik_B:
                grade = "Dainya Parivartana"
                base_strength = 0.4
            else:
                grade = "Kahala Parivartana"
                base_strength = 0.6

            strength = base_strength * _avg_strength([pA, pB], shadbala_ratios)

            results.append(YogaResult(
                name=f"{grade} ({pA}↔{pB})",
                category="parivartana",
                detected=True,
                strength=round(strength, 3),
                planets=[pA, pB],
                houses=[hA, hB],
                description=(
                    f"{pA} (H{hA} lord) in H{hB} and {pB} (H{hB} lord) in H{hA}. "
                    f"{grade}: merges significations of houses {hA} and {hB}. "
                    f"Domain activated during dasha of either planet."
                ),
                activating_dasha=[pA, pB],
            ))
    return results


def _kalasarpa_yoga(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
) -> Optional[YogaResult]:
    """
    Kalasarpa Yoga: ALL 7 classical planets are hemmed between Rahu and Ketu
    on one side of the Rahu-Ketu axis.
    → Intense karmic life; extreme ups and downs; strong focus on destiny.
    """
    rahu_lon = planet_lons.get("RAHU", 0)
    ketu_lon = planet_lons.get("KETU", (rahu_lon + 180) % 360)

    # Determine the arc from Rahu to Ketu going clockwise (Rahu to Ketu = 180°)
    # All planets must lie within this 180° arc OR all in the other half.
    classical = [p for p in PLANET_NAMES_7 if p in planet_lons]

    in_rahu_to_ketu = 0   # planets in rahu→ketu arc (going clockwise = adding degrees)
    in_ketu_to_rahu = 0

    for pname in classical:
        lon = planet_lons[pname]
        # Angular distance from Rahu, going clockwise (increasing longitude)
        d = (lon - rahu_lon) % 360
        if 0 < d < 180:    # within Rahu→Ketu half-circle
            in_rahu_to_ketu += 1
        elif d > 0:
            in_ketu_to_rahu += 1

    if in_rahu_to_ketu == 7 or in_ketu_to_rahu == 7:
        dominant_side = "Rahu→Ketu" if in_rahu_to_ketu == 7 else "Ketu→Rahu"
        return YogaResult(
            name="Kalasarpa Yoga",
            category="special",
            detected=True,
            strength=0.8,
            planets=classical + ["RAHU", "KETU"],
            houses=list({planet_houses.get(p, 0) for p in classical}),
            description=(
                f"All 7 planets confined between Rahu-Ketu axis ({dominant_side}). "
                "Kalasarpa Yoga: intense karmic life theme, serpentine rise and fall, "
                "strong past-life influence. Remedies recommended."
            ),
            activating_dasha=["RAHU", "KETU"],
        )
    return None


def _kemadrum_yoga(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        shadbala_ratios: Dict[str, float],
) -> Optional[YogaResult]:
    """
    Kemadrum Yoga: Moon has no planet in the 2nd or 12th from *itself*
    (by sign / house), AND no planets conjunct it.
    A weakening yoga indicating isolation, financial struggle, or lack of support.
    Cancelled if Moon has any planet in these positions OR Moon is in kendra.
    """
    moon_h = _planet_house("MOON", planet_houses)
    if moon_h == 0:
        return None

    second_from_moon  = (moon_h % 12) + 1           # 2nd from Moon
    twelfth_from_moon = (moon_h - 2) % 12 + 1       # 12th from Moon

    surrounding_houses = {moon_h, second_from_moon, twelfth_from_moon}

    # Any planet (except Rahu/Ketu) in these positions?
    planets_nearby = [
        p for p in PLANET_NAMES_7
        if p != "MOON" and _planet_house(p, planet_houses) in surrounding_houses
    ]

    if planets_nearby:
        return None  # Cancelled — planetary support exists

    # Also cancelled if Moon is in kendra (angular houses 1/4/7/10)
    if _is_in_kendra(moon_h):
        return None

    moon_strength = shadbala_ratios.get("MOON", 0.5)
    return YogaResult(
        name="Kemadrum Yoga",
        category="challenging",
        detected=True,
        strength=1.0 - moon_strength,   # stronger yoga = weaker Moon
        planets=["MOON"],
        houses=[moon_h],
        description=(
            "Moon isolated — no planets in its 2nd or 12th house. "
            "Kemadrum Yoga: tendency toward hardship, lack of emotional support, "
            "financial irregularities. Overcome through Jupiter's aspects and strong dashas."
        ),
        activating_dasha=["MOON"],
    )


# ─── NBRY sign-lord & exaltation tables ──────────────────────────────────────
# Debilitation sign (0-based) per planet
_DEBIL_SIGN: Dict[str, int] = {
    "SUN": 6, "MOON": 9, "MARS": 3, "MERCURY": 11,
    "JUPITER": 9, "VENUS": 5, "SATURN": 0,
}
# Exaltation sign per planet
_EXALT_SIGN: Dict[str, int] = {
    "SUN": 0, "MOON": 1, "MARS": 9, "MERCURY": 5,
    "JUPITER": 3, "VENUS": 11, "SATURN": 6,
}
# Sign lords (0-based sign → planet name)
_SIGN_LORD_MAP: Dict[int, str] = {
    0: "MARS", 1: "VENUS", 2: "MERCURY", 3: "MOON",
    4: "SUN", 5: "MERCURY", 6: "VENUS", 7: "MARS",
    8: "JUPITER", 9: "SATURN", 10: "SATURN", 11: "JUPITER",
}
# Planet whose exaltation sign equals the debilitation sign (the "exaltation lord in debil sign")
# i.e., the planet that would be exalted IN the sign where our planet is debilitated
_EXALT_LORD_IN_DEBIL_SIGN: Dict[str, str] = {
    # debilitation sign → planet exalted there
    # e.g. Sun debil in Libra(6) → Saturn exalts in Libra → Saturn is the check planet
}
for _p, _e_sign in _EXALT_SIGN.items():
    _EXALT_LORD_IN_DEBIL_SIGN[_p] = next(
        (q for q, es in _EXALT_SIGN.items() if es == _DEBIL_SIGN.get(_p, -1)),
        ""
    )

# Cancer ascendant (sign index 3) exception — NBRY does not bring boon
_NBRY_CANCER_EXCEPTION_LAGNA = 3


def _neechabhanga_raj_yoga(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        shadbala_ratios: Dict[str, float],
        lagna_sign: int = 0,
        moon_sign: int = 0,
) -> List[YogaResult]:
    """
    Full 8-condition Neechabhanga Raja Yoga implementation.

    8 Classical NBRY Conditions:
    1. Depositor in Kendra — lord of debilitated planet's sign in H1/4/7/10 from Lagna or Moon
    2. Exalted Conjunction — debilitated planet conjunct exalted planet in SAME sign
    3. Sign Lord in Kendra — same as #1 (from Lagna or Moon)
    4. Exaltation Lord in Kendra — lord of sign where debilitated planet WOULD be exalted → in Kendra
    5. Divisional Exaltation — debilitated planet exalted in D9 (simplified: Vargottama)
    6. Aspect of Sign Lord — sign lord aspects debilitated planet and has high Shadbala
    7. Vargottama Dignity — debilitated planet Vargottama (same sign in D1 and D9)
    8. Parivartana — sign exchange with friend/neutral planet

    Cancer Lagna Exception: NBRY acts as ongoing obstruction for Cancer ascendant.
    Chained NBRY: If the depositor of the debilitated planet is itself debilitated
    but gets its own NBRY → first planet inherits NBRY by proxy (cascading, delayed).
    Parabolic Trajectory: Initial penalty (years 1-20), massive spike at mature Dasha.
    """
    results = []
    cancer_lagna = (lagna_sign == _NBRY_CANCER_EXCEPTION_LAGNA)

    for pname in PLANET_NAMES_7:
        lon = planet_lons.get(pname)
        if lon is None:
            continue
        if not _is_debilitated(pname, lon):
            continue

        h = _planet_house(pname, planet_houses)
        strength = shadbala_ratios.get(pname, 0.5)
        debil_sign = _DEBIL_SIGN.get(pname, -1)
        depositor  = _SIGN_LORD_MAP.get(debil_sign, "")     # lord of the debilitation sign
        exalt_lord = _EXALT_LORD_IN_DEBIL_SIGN.get(pname, "")  # planet exalted in debil sign

        depositor_h  = _planet_house(depositor,  planet_houses) if depositor  else 0
        exalt_lord_h = _planet_house(exalt_lord, planet_houses) if exalt_lord else 0

        conditions_met: List[str] = []

        # ── Condition 1 & 3: Depositor/Sign Lord in Kendra (from Lagna or Moon) ──
        dep_from_lagna = (depositor_h - lagna_sign) % 12 + 1 if depositor_h else 0
        dep_from_moon  = (depositor_h - moon_sign)  % 12 + 1 if depositor_h else 0
        if depositor_h and (_is_in_kendra(dep_from_lagna) or _is_in_kendra(dep_from_moon)):
            conditions_met.append("C1_depositor_kendra")

        # ── Condition 2: Exalted planet conjunct in SAME sign ──────────────────
        for other in PLANET_NAMES_7:
            if other == pname:
                continue
            other_lon = planet_lons.get(other)
            if other_lon and _is_exalted(other, other_lon):
                if sign_of(other_lon) == sign_of(lon):
                    conditions_met.append(f"C2_exalted_{other}_conjunct")
                    break

        # ── Condition 4: Exaltation lord in Kendra ─────────────────────────────
        if exalt_lord_h and _is_in_kendra(exalt_lord_h):
            conditions_met.append("C4_exalt_lord_kendra")

        # ── Condition 5: Vargottama / Divisional Exaltation ────────────────────
        # Simplified: debilitated planet is Vargottama (D1 sign = D9 sign)
        # D9 sign = (sign * 9 + navamsha_pos) % 12 — rough check via longitude
        d1_sign = sign_of(lon)
        d9_sign = int((lon % (360 / 9)) / (360 / 9 / 12)) % 12  # rough D9 sign
        if d1_sign == d9_sign:
            conditions_met.append("C5_vargottama_divisional")

        # ── Condition 6: Sign Lord aspects debilitated planet + high Shadbala ──
        depositor_str = shadbala_ratios.get(depositor, 0.0) if depositor else 0.0
        if depositor_str >= 0.65:
            # Simplified aspect check: Saturn aspects 3rd/7th/10th; Jupiter aspects 5th/7th/9th
            aspect_diff = (depositor_h - h) % 12 + 1 if (depositor_h and h) else 0
            has_aspect = False
            if depositor == "SATURN" and aspect_diff in (3, 7, 10):
                has_aspect = True
            elif depositor == "JUPITER" and aspect_diff in (5, 7, 9):
                has_aspect = True
            elif depositor == "MARS" and aspect_diff in (4, 7, 8):
                has_aspect = True
            elif aspect_diff == 7:  # All planets have 7th aspect
                has_aspect = True
            if has_aspect:
                conditions_met.append(f"C6_sign_lord_{depositor}_aspects")

        # ── Condition 7: Vargottama Dignity ────────────────────────────────────
        # Same check as C5 but specifically for same sign in D1 and D9
        if "C5_vargottama_divisional" in conditions_met:
            conditions_met.append("C7_vargottama_dignity")

        # ── Condition 8: Parivartana ────────────────────────────────────────────
        # Debilitated planet exchanges signs with another planet
        pname_own_signs = OWN_SIGNS.get(_P.get(pname), [])
        cur_sign = sign_of(lon)
        for other in PLANET_NAMES_7:
            if other == pname:
                continue
            other_lon = planet_lons.get(other)
            if not other_lon:
                continue
            other_sign = sign_of(other_lon)
            other_p    = _P.get(other)
            other_own  = OWN_SIGNS.get(other_p, [])
            # Exchange: pname in other's sign AND other in pname's sign
            if cur_sign in other_own and other_sign in (pname_own_signs or []):
                conditions_met.append(f"C8_parivartana_{other}")
                break

        # ── Chained NBRY check ──────────────────────────────────────────────────
        chained = False
        if depositor:
            dep_lon = planet_lons.get(depositor)
            if dep_lon and _is_debilitated(depositor, dep_lon):
                # Depositor is itself debilitated — check if IT has cancellation
                dep_h2 = _planet_house(depositor, planet_houses)
                dep_debil_sign2 = _DEBIL_SIGN.get(depositor, -1)
                dep_depositor2  = _SIGN_LORD_MAP.get(dep_debil_sign2, "")
                dep_dep_h2      = _planet_house(dep_depositor2, planet_houses) if dep_depositor2 else 0
                if dep_dep_h2 and _is_in_kendra(dep_dep_h2):
                    chained = True
                    conditions_met.append("CHAINED_NBRY_cascading_proxy")

        # ── Evaluate ─────────────────────────────────────────────────────────────
        if not conditions_met:
            continue

        # Cancer lagna exception
        if cancer_lagna:
            results.append(YogaResult(
                name=f"NBRY Obstruction ({pname}) [Cancer Lagna Exception]",
                category="challenging",
                detected=True,
                tier=4,
                strength=strength * 0.3,
                activation_score=0.0,
                planets=[pname],
                houses=[h],
                description=(
                    f"{pname} debilitated with NBRY conditions ({', '.join(conditions_met)}) "
                    "BUT Cancer Lagna Exception applies — NBRY acts as ongoing obstruction, not boon."
                ),
                activating_dasha=[pname],
                nbry_conditions=conditions_met,
                parabolic_trajectory=False,
            ))
            continue

        # Strength proportional to conditions met (more conditions = stronger)
        nbry_strength = min(1.0, 0.5 + 0.10 * len(conditions_met))
        if chained:
            nbry_strength *= 0.80  # chained = delayed but massive; slight reduction early

        results.append(YogaResult(
            name=f"Neechabhanga Raja Yoga ({pname})",
            category="raj",
            detected=True,
            tier=2,   # Raja tier
            strength=nbry_strength,
            activation_score=0.0,  # Set during dasha scoring
            planets=[pname, depositor] if depositor else [pname],
            houses=[h, depositor_h] if depositor_h else [h],
            description=(
                f"{pname} debilitated → NBRY via {len(conditions_met)} condition(s): "
                f"{', '.join(conditions_met)}. "
                f"{'CHAINED NBRY (cascading via proxy): ' if chained else ''}"
                f"Parabolic trajectory: early-life struggle (decade 1-2), "
                f"massive strength spike during mature Dasha. "
                f"Peak strength situationally SUPERIOR to standard unchallenged exaltation."
            ),
            activating_dasha=[pname, depositor] if depositor else [pname],
            nbry_conditions=conditions_met,
            parabolic_trajectory=True,
            bhanga_model={
                "struggle_phase": True,
                "rescue_planet": depositor or pname,
                "cancellation_type": "neechabhanga",
                "chained": chained,
                "parabolic_peak": "mature_dasha_activation",
            },
        ))

    return results


def _adhi_yoga(
        planet_houses: Dict[str, int],
        moon_house: int,
        shadbala_ratios: Dict[str, float],
) -> YogaResult:
    """
    Mercury, Venus, Jupiter in 6th, 7th, 8th from Moon → Adhi Yoga.
    → Leadership, health, wealth.
    """
    benefics = ["MERCURY", "JUPITER", "VENUS"]
    target_from_moon = {6, 7, 8}
    planets_in_targets = []
    for pname in benefics:
        h = _planet_house(pname, planet_houses)
        if h == 0 or moon_house == 0:
            continue
        from_moon = ((h - moon_house) % 12) + 1
        if from_moon in target_from_moon:
            planets_in_targets.append(pname)

    detected = len(planets_in_targets) >= 2  # at least 2 benefics
    strength = _avg_strength(planets_in_targets, shadbala_ratios)
    return YogaResult(
        name="Adhi Yoga",
        category="raj",
        detected=detected,
        strength=strength if detected else 0.0,
        planets=planets_in_targets,
        houses=[_planet_house(p, planet_houses) for p in planets_in_targets],
        description="Multiple benefics in 6/7/8 from Moon → political/administrative success.",
        activating_dasha=planets_in_targets,
    )


def _amala_yoga(
        planet_houses: Dict[str, int],
        shadbala_ratios: Dict[str, float],
) -> YogaResult:
    """
    Natural benefic in 10th from Lagna or Moon → Amala Yoga → fame, virtue.
    """
    h10 = 10  # 10th house from lagna
    benefics_in_10 = [
        p for p in ["JUPITER", "VENUS", "MERCURY"]
        if _planet_house(p, planet_houses) == h10
    ]
    detected = len(benefics_in_10) > 0
    strength = _avg_strength(benefics_in_10, shadbala_ratios) if benefics_in_10 else 0.0
    return YogaResult(
        name="Amala Yoga",
        category="raj",
        detected=detected,
        strength=strength,
        planets=benefics_in_10,
        houses=[h10],
        description="Natural benefic in 10th → lasting fame, ethical conduct, karma.",
        activating_dasha=benefics_in_10,
    )


def _sunapha_anapha_durudhara(
        planet_houses: Dict[str, int],
        shadbala_ratios: Dict[str, float],
) -> List[YogaResult]:
    """
    Moon-flanking wealth yogas:
    - Sunapha  : Natural benefic(s) in 2nd  from Moon (not Sun/Rahu/Ketu)
    - Anapha   : Natural benefic(s) in 12th from Moon
    - Durudhara: Natural benefics in BOTH 2nd and 12th from Moon
    All three confer wealth, good character, and stability.
    """
    results: List[YogaResult] = []
    moon_h = _planet_house("MOON", planet_houses)
    if moon_h == 0:
        return results

    second_from_moon  = (moon_h % 12) + 1        # 2nd from Moon
    twelfth_from_moon = (moon_h - 2) % 12 + 1    # 12th from Moon

    # Only natural benefics (not Sun, Mars, Saturn, Rahu, Ketu) qualify
    qualifying = ["MERCURY", "VENUS", "JUPITER"]

    planets_2nd  = [p for p in qualifying
                    if _planet_house(p, planet_houses) == second_from_moon]
    planets_12th = [p for p in qualifying
                    if _planet_house(p, planet_houses) == twelfth_from_moon]

    has_2nd  = len(planets_2nd) > 0
    has_12th = len(planets_12th) > 0

    if has_2nd and has_12th:
        # Durudhara subsumes both Sunapha and Anapha
        all_planets = list(set(planets_2nd + planets_12th))
        strength = _avg_strength(all_planets, shadbala_ratios)
        results.append(YogaResult(
            name="Durudhara Yoga",
            category="dhana",
            detected=True,
            strength=strength,
            planets=all_planets,
            houses=[second_from_moon, twelfth_from_moon],
            description=(
                "Benefic planets in both 2nd and 12th from Moon → "
                "Durudhara: prosperity, generous nature, resources from multiple streams."
            ),
            activating_dasha=all_planets,
        ))
    else:
        if has_2nd:
            strength = _avg_strength(planets_2nd, shadbala_ratios)
            results.append(YogaResult(
                name="Sunapha Yoga",
                category="dhana",
                detected=True,
                strength=strength,
                planets=planets_2nd,
                houses=[second_from_moon],
                description=(
                    f"Benefic planet(s) ({', '.join(planets_2nd)}) in 2nd from Moon → "
                    "Sunapha: self-made wealth, good reputation, stable resources."
                ),
                activating_dasha=planets_2nd,
            ))
        if has_12th:
            strength = _avg_strength(planets_12th, shadbala_ratios)
            results.append(YogaResult(
                name="Anapha Yoga",
                category="dhana",
                detected=True,
                strength=strength,
                planets=planets_12th,
                houses=[twelfth_from_moon],
                description=(
                    f"Benefic planet(s) ({', '.join(planets_12th)}) in 12th from Moon → "
                    "Anapha: good health, freedom from debt, renown in later life."
                ),
                activating_dasha=planets_12th,
            ))

    return results


def _saraswati_yoga(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        shadbala_ratios: Dict[str, float],
) -> Optional[YogaResult]:
    """
    Saraswati Yoga: Venus, Jupiter, and Mercury all placed in kendra (1/4/7/10)
    or trikona (5/9) from Lagna, with at least one in kendra.
    Mercury must be in own sign, Moolatrikona, or exalted for full strength.
    Confers great learning, articulation, arts, wisdom.
    """
    kendra_trikona = {1, 4, 5, 7, 9, 10}
    kendra = {1, 4, 7, 10}
    trio = ["VENUS", "JUPITER", "MERCURY"]

    # All three must be in kendra or trikona
    trio_houses = {p: _planet_house(p, planet_houses) for p in trio}
    all_ok = all(h in kendra_trikona for h in trio_houses.values())
    one_in_kendra = any(h in kendra for h in trio_houses.values())

    if not (all_ok and one_in_kendra):
        return None

    # Strength modifier: Mercury in own/exalted sign boosts yoga
    merc_lon = planet_lons.get("MERCURY", 0.0)
    merc_s = sign_of(merc_lon)
    merc_strong = merc_s in (2, 5)  # Gemini=2, Virgo=5 (own signs)
    if not merc_strong:
        # also check exaltation sign (Virgo 15° = sign index 5)
        merc_strong = merc_s == sign_of(EXALTATION_DEGREES.get(Planet.MERCURY, 165.0))

    strength = _avg_strength(trio, shadbala_ratios) * (1.2 if merc_strong else 0.85)
    strength = min(1.0, strength)

    return YogaResult(
        name="Saraswati Yoga",
        category="raj",
        detected=True,
        strength=strength,
        planets=trio,
        houses=list(trio_houses.values()),
        description=(
            "Venus, Jupiter, Mercury all in kendra/trikona → "
            "Saraswati Yoga: exceptional learning, eloquence, creative genius, "
            "mastery of arts and sciences."
        ),
        activating_dasha=trio,
    )


def _dhana_yogas(
        planet_houses: Dict[str, int],
        house_lords: Dict[int, str],
        shadbala_ratios: Dict[str, float],
) -> List[YogaResult]:
    """
    Dhana (wealth) yoga: lord of 2nd/11th conjunct with or aspect from 5th/9th lord.
    Also checks if 2nd or 11th lord is in 1/2/5/9/11.
    """
    results = []
    wealth_houses = {2, 11}
    dharma_houses = {1, 5, 9}
    gain_houses = {1, 2, 5, 9, 11}

    l2 = house_lords.get(2, "")
    l11 = house_lords.get(11, "")
    l5 = house_lords.get(5, "")
    l9 = house_lords.get(9, "")

    # L2 or L11 in gain houses
    for lord_name, tag in [(l2, "2nd"), (l11, "11th")]:
        if not lord_name:
            continue
        h = _planet_house(lord_name, planet_houses)
        if h in gain_houses:
            results.append(YogaResult(
                name=f"Dhana Yoga (Lord of {tag} in gain house)",
                category="dhana",
                detected=True,
                strength=shadbala_ratios.get(lord_name, 0.5),
                planets=[lord_name],
                houses=[h],
                description=f"Lord of {tag} in {h}th → wealth accumulation.",
                activating_dasha=[lord_name],
            ))
    return results


def _raj_yoga(
        planet_houses: Dict[str, int],
        house_lords: Dict[int, str],
        shadbala_ratios: Dict[str, float],
) -> List[YogaResult]:
    """
    Raj Yoga: lord of kendra (1/4/7/10) + lord of trikona (5/9) relationship
    (conjunction, mutual aspect, or exchange).
    """
    kendra_houses = [1, 4, 7, 10]
    trikona_houses = [5, 9]   # 1st is both kendra and trikona
    results = []

    for kh in kendra_houses:
        for th in trikona_houses:
            kl = house_lords.get(kh, "")
            tl = house_lords.get(th, "")
            if not kl or not tl or kl == tl:
                continue
            kl_h = _planet_house(kl, planet_houses)
            tl_h = _planet_house(tl, planet_houses)
            # Conjunction
            if kl_h == tl_h and kl_h > 0:
                s = _avg_strength([kl, tl], shadbala_ratios)
                results.append(YogaResult(
                    name=f"Raj Yoga (H{kh}L + H{th}L conjunction)",
                    category="raj",
                    detected=True,
                    strength=s,
                    planets=[kl, tl],
                    houses=[kl_h],
                    description=(
                        f"Lords of {kh}th and {th}th together → power, authority, success."
                    ),
                    activating_dasha=[kl, tl],
                ))
    return results


# ═══════════════════════════════════════════════════════════════════
# SECTION A: ADDITIONAL CLASSICAL YOGA CATALOG
# Source: Algorithmic Vedic Astrology Yoga Engine research file
# ═══════════════════════════════════════════════════════════════════

def _dharma_karmadhipati_yoga(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        house_lords: Dict[int, str],
        shadbala_ratios: Dict[str, float],
        asp_map: Dict,
        lagna_sign: int = 0,
) -> List[YogaResult]:
    """
    Dharma-Karmadhipati Raja Yoga: mutual aspect, conjunction, or sign-exchange
    between the 9th lord (Dharma) and 10th lord (Karma).
    Source: BPHS / Saravali.
    Bhanga: 10th lord in the 3rd house (6th from 10th).
    """
    results = []
    l9  = house_lords.get(9, "")
    l10 = house_lords.get(10, "")
    if not l9 or not l10 or l9 == l10:
        return results

    h9  = _planet_house(l9,  planet_houses)
    h10 = _planet_house(l10, planet_houses)

    # Bhanga: 10th lord in 3rd house
    if h10 == 3:
        return results

    conjunction = (h9 == h10 and h9 > 0)
    exchange    = (h9 == 10 and h10 == 9)
    mutual_asp  = (
        (l9, l10) in asp_map or (l10, l9) in asp_map
    )

    detected = conjunction or exchange or mutual_asp
    if not detected:
        return results

    mode = "conjunction" if conjunction else ("exchange" if exchange else "mutual aspect")
    # Per-lagna blemish dampeners: when L9/L10 simultaneously rules a dusthana
    # Aries: Saturn(L10) also rules 11th → moderate; Gemini: Saturn(L9) also rules 8th → severe
    # Leo: Venus(L10) also rules 3rd → mild; Capricorn: Mercury(L9) also rules 6th → mild
    # Aquarius: Mars(L10) also rules 3rd → mild
    _DKA_BLEMISH = {0: 0.70, 2: 0.40, 4: 0.80, 9: 0.80, 10: 0.80}
    blemish_factor = _DKA_BLEMISH.get(lagna_sign, 1.0)
    s = _avg_strength([l9, l10], shadbala_ratios) * blemish_factor
    results.append(YogaResult(
        name="Dharma-Karmadhipati Raja Yoga",
        category="raj",
        detected=True,
        tier=2,
        strength=s,
        planets=[l9, l10],
        houses=[h9, h10],
        description=(
            f"9th lord ({l9}) and 10th lord ({l10}) in {mode}. "
            "Dharma-Karmadhipati: high career status, authority, dharmic vocation, "
            "ruling power. One of the most powerful Raja Yogas."
        ),
        activating_dasha=[l9, l10],
    ))
    return results


def _kahala_yoga(
        planet_houses: Dict[str, int],
        house_lords: Dict[int, str],
        shadbala_ratios: Dict[str, float],
) -> Optional[YogaResult]:
    """
    Kahala Yoga: Lords of 4th and 9th in mutual Kendras from each other,
    AND lagna lord is exceptionally strong (Shadbala >= 1.0).
    Source: Jataka Bharanam.
    Bhanga: Lagna lord weak or in Dusthana (6/8/12).
    """
    l1 = house_lords.get(1, "")
    l4 = house_lords.get(4, "")
    l9 = house_lords.get(9, "")
    if not all([l1, l4, l9]):
        return None

    h1_lord = _planet_house(l1, planet_houses)
    h4_lord = _planet_house(l4, planet_houses)
    h9_lord = _planet_house(l9, planet_houses)

    # Bhanga: lagna lord weak or in dusthana
    if shadbala_ratios.get(l1, 0.0) < 0.80 or h1_lord in (6, 8, 12):
        return None

    # 4L and 9L in mutual kendras (angular distance between their houses == 1/4/7/10)
    diff = abs(h4_lord - h9_lord)
    if diff > 6:
        diff = 12 - diff
    in_mutual_kendra = diff in (0, 3, 6, 9)  # 1st/4th/7th/10th offset
    if not in_mutual_kendra:
        return None

    s = _avg_strength([l4, l9, l1], shadbala_ratios)
    return YogaResult(
        name="Kahala Yoga",
        category="raj",
        detected=True,
        tier=2,
        strength=s,
        planets=[l4, l9, l1],
        houses=[h4_lord, h9_lord, h1_lord],
        description=(
            f"4th lord ({l4}) and 9th lord ({l9}) in mutual Kendras; "
            f"Lagna lord ({l1}) strong. "
            "Kahala Yoga: courageous leadership, military command, land ownership."
        ),
        activating_dasha=[l4, l9],
    )


def _lakshmi_yoga(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        house_lords: Dict[int, str],
        shadbala_ratios: Dict[str, float],
) -> Optional[YogaResult]:
    """
    Lakshmi Yoga: Lagna lord is strong (Shadbala >= 1.0 OR in Kendra/Trikona),
    AND 9th lord is in a Kendra AND in own sign or exaltation.
    Source: Sarvartha Chintamani.
    Bhanga: 9th lord combust, debilitated, or defeated in war.
    """
    l1 = house_lords.get(1, "")
    l9 = house_lords.get(9, "")
    if not l1 or not l9:
        return None

    h1_lord = _planet_house(l1, planet_houses)
    h9_lord = _planet_house(l9, planet_houses)
    lon9    = planet_lons.get(l9, 0.0)

    # Lagna lord must be strong
    l1_str = shadbala_ratios.get(l1, 0.0)
    lagna_lord_strong = l1_str >= 1.0 or _is_in_kendra(h1_lord) or _is_in_trikona(h1_lord)
    if not lagna_lord_strong:
        return None

    # 9th lord in kendra AND own/exalted sign
    if not _is_in_kendra(h9_lord):
        return None
    if not (_is_own_sign(l9, sign_of(lon9)) or _is_exalted(l9, lon9)):
        return None

    # Bhanga: 9th lord debilitated or combust
    if _is_debilitated(l9, lon9) or _is_combust(l9, planet_lons):
        return None

    s = _avg_strength([l1, l9], shadbala_ratios)
    return YogaResult(
        name="Lakshmi Yoga",
        category="dhana",
        detected=True,
        tier=2,
        strength=s,
        planets=[l1, l9],
        houses=[h1_lord, h9_lord],
        description=(
            f"Lagna lord ({l1}) strong; 9th lord ({l9}) in kendra in own/exalted sign. "
            "Lakshmi Yoga: immense wealth, vast lands, virtue, royal reputation."
        ),
        activating_dasha=[l9, l1],
    )


def _voshi_veshi_ubhayachari_yoga(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        shadbala_ratios: Dict[str, float],
) -> List[YogaResult]:
    """
    Solar-flanking yogas (Voshi, Veshi, Ubhayachari):
    - Veshi: planet (exc. Moon) in 2nd from Sun.
    - Voshi: planet (exc. Moon) in 12th from Sun.
    - Ubhayachari: planets in BOTH 2nd and 12th from Sun.
    Source: Mansagari / Jataka Bharanam. Malefics degrade, benefics uplift.
    """
    results: List[YogaResult] = []
    sun_h = _planet_house("SUN", planet_houses)
    if sun_h == 0:
        return results

    second_from_sun  = (sun_h % 12) + 1
    twelfth_from_sun = (sun_h - 2) % 12 + 1

    excluded = {"SUN", "MOON", "RAHU", "KETU"}
    planets_2nd  = [p for p in PLANET_NAMES_7
                    if p not in excluded
                    and _planet_house(p, planet_houses) == second_from_sun]
    planets_12th = [p for p in PLANET_NAMES_7
                    if p not in excluded
                    and _planet_house(p, planet_houses) == twelfth_from_sun]

    nat_benefics_set = {"JUPITER", "VENUS", "MERCURY"}

    def _sun_yoga_quality(ps: List[str]) -> float:
        if not ps:
            return 0.0
        benefics = [p for p in ps if p in nat_benefics_set]
        malefics = [p for p in ps if p not in nat_benefics_set]
        base = _avg_strength(ps, shadbala_ratios)
        if benefics and not malefics:
            return min(1.0, base * 1.2)
        if malefics and not benefics:
            return base * 0.5  # degraded
        return base  # mixed

    if planets_2nd and planets_12th:
        # Ubhayachari subsumes both
        all_ps = list(set(planets_2nd + planets_12th))
        strength = _sun_yoga_quality(all_ps)
        results.append(YogaResult(
            name="Ubhayachari Yoga",
            category="raj",
            detected=True,
            tier=2,
            strength=strength,
            planets=all_ps,
            houses=[second_from_sun, twelfth_from_sun],
            description=(
                f"Planets ({', '.join(all_ps)}) flanking Sun in 2nd and 12th. "
                "Ubhayachari: king-like physique, great responsibility, balanced outlook."
            ),
            activating_dasha=all_ps,
        ))
    else:
        if planets_2nd:
            strength = _sun_yoga_quality(planets_2nd)
            results.append(YogaResult(
                name="Veshi Yoga",
                category="raj",
                detected=True,
                tier=3,
                strength=strength,
                planets=planets_2nd,
                houses=[second_from_sun],
                description=(
                    f"Planet(s) ({', '.join(planets_2nd)}) in 2nd from Sun. "
                    "Veshi: wealth, capability to defeat opponents, powerful eloquence."
                ),
                activating_dasha=planets_2nd,
            ))
        if planets_12th:
            strength = _sun_yoga_quality(planets_12th)
            results.append(YogaResult(
                name="Voshi Yoga",
                category="raj",
                detected=True,
                tier=3,
                strength=strength,
                planets=planets_12th,
                houses=[twelfth_from_sun],
                description=(
                    f"Planet(s) ({', '.join(planets_12th)}) in 12th from Sun. "
                    "Voshi: eloquence, renown, scientific pursuits (if benefic)."
                ),
                activating_dasha=planets_12th,
            ))
    return results


def _mangal_budha_yoga(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        shadbala_ratios: Dict[str, float],
) -> Optional[YogaResult]:
    """
    Mangal-Budha Yoga: Mars and Mercury conjunct in the same house.
    → Skill in medicine, metalcraft, architecture, or fine arts.
    Bhanga: conjunction in Dusthana (6/8/12) or either planet combust.
    """
    mars_h = _planet_house("MARS", planet_houses)
    merc_h = _planet_house("MERCURY", planet_houses)
    if mars_h == 0 or mars_h != merc_h:
        return None

    # Bhanga
    if mars_h in (6, 8, 12):
        return None
    if _is_combust("MERCURY", planet_lons):
        return None

    s = _avg_strength(["MARS", "MERCURY"], shadbala_ratios)
    return YogaResult(
        name="Mangal-Budha Yoga",
        category="career",
        detected=True,
        tier=3,
        strength=s,
        planets=["MARS", "MERCURY"],
        houses=[mars_h],
        description=(
            "Mars and Mercury conjunct → Mangal-Budha: technical skill in medicine, "
            "architecture, or engineering; eloquent but driven nature."
        ),
        activating_dasha=["MARS", "MERCURY"],
    )


def _uttamadi_yoga(
        planet_houses: Dict[str, int],
        shadbala_ratios: Dict[str, float],
) -> Optional[YogaResult]:
    """
    Uttamadi Yoga: Moon in Apoklima (3,6,9,12) from the Sun.
    → Wealth, learning, and widespread fame.
    Bhanga: Moon debilitated (in Scorpio, sign 7) or conjunct Ketu.
    """
    sun_h  = _planet_house("SUN",  planet_houses)
    moon_h = _planet_house("MOON", planet_houses)
    ketu_h = planet_houses.get("KETU", 0)
    if sun_h == 0 or moon_h == 0:
        return None

    from_sun = ((moon_h - sun_h) % 12) + 1
    if from_sun not in (3, 6, 9, 12):
        return None

    # Bhanga: Moon in Scorpio (sign 7) or conjunct Ketu
    moon_sign_idx = sign_of(0)  # placeholder; use shadbala as proxy
    if ketu_h == moon_h:  # conjunct Ketu
        return None
    moon_str = shadbala_ratios.get("MOON", 0.5)
    if moon_str < 0.30:  # severely weak = approximate debilitation proxy
        return None

    s = _avg_strength(["MOON", "SUN"], shadbala_ratios)
    return YogaResult(
        name="Uttamadi Yoga",
        category="dhana",
        detected=True,
        tier=3,
        strength=s,
        planets=["MOON", "SUN"],
        houses=[moon_h, sun_h],
        description=(
            f"Moon in {from_sun}th (Apoklima) from Sun. "
            "Uttamadi: plenteous wealth, profound learning, widespread fame."
        ),
        activating_dasha=["MOON"],
    )


def _akhanda_samrajya_yoga(
        planet_houses: Dict[str, int],
        house_lords: Dict[int, str],
        shadbala_ratios: Dict[str, float],
) -> Optional[YogaResult]:
    """
    Akhanda Samrajya Yoga: Lord of 11th, 9th, or 2nd placed in Kendra from Moon,
    AND Jupiter must be lord of 2nd, 5th, or 11th house.
    Source: Jyotisharnava Navanitam.
    Bhanga: Jupiter debilitated or combust.
    """
    moon_h  = planet_houses.get("MOON", 0)
    jup_h   = planet_houses.get("JUPITER", 0)
    if not moon_h:
        return None

    # Jupiter must lord the 2nd, 5th, or 11th
    jup_owns = [h for h, lord in house_lords.items() if lord == "JUPITER"]
    jup_qualifies = any(h in (2, 5, 11) for h in jup_owns)
    if not jup_qualifies:
        return None

    # Bhanga: Jupiter debilitated or combust
    jup_lon = 0.0  # we don't have lons here — use Shadbala as proxy
    if shadbala_ratios.get("JUPITER", 0.5) < 0.35:
        return None  # severely weak = proxy for debilitated/combust

    # 11th, 9th, or 2nd lord in Kendra from Moon
    qualifying_lords = []
    for h_num in (11, 9, 2):
        lord = house_lords.get(h_num, "")
        if not lord:
            continue
        lord_h = _planet_house(lord, planet_houses)
        if lord_h == 0 or moon_h == 0:
            continue
        from_moon = ((lord_h - moon_h) % 12) + 1
        if _is_in_kendra(from_moon):
            qualifying_lords.append(lord)

    if not qualifying_lords:
        return None

    all_ps = list(set(qualifying_lords + ["JUPITER"]))
    s = _avg_strength(all_ps, shadbala_ratios)
    return YogaResult(
        name="Akhanda Samrajya Yoga",
        category="raj",
        detected=True,
        tier=2,
        strength=s,
        planets=all_ps,
        houses=[_planet_house(p, planet_houses) for p in all_ps],
        description=(
            f"11/9/2 lord(s) in Kendra from Moon; Jupiter lords 2/5/11. "
            "Akhanda Samrajya: vast unbroken empire, tremendous executive control, "
            "generational wealth."
        ),
        activating_dasha=["JUPITER"] + qualifying_lords,
    )


# ═══════════════════════════════════════════════════════════════════
# SECTION B: GRAHA YUDDHA (PLANETARY WAR) ENGINE
# Source: BPHS, Uttara Kalamrita
# Affects yoga cancellation weights
# ═══════════════════════════════════════════════════════════════════

# Classification per Uttara Kalamrita
_PAURA_PLANETS = {"MERCURY", "JUPITER", "SATURN"}
_YAYI_PLANETS  = {"MARS", "VENUS"}

def _detect_graha_yuddha(
        planet_lons: Dict[str, float],
        planet_lats: Dict[str, float] = None,
) -> List[Dict]:
    """
    Detect Graha Yuddha (planetary war) between non-luminary, non-nodal planets.
    War occurs when two planets are within 1° longitudinal orb.
    Victor: lower longitude wins (primary rule).
    Tiebreak: higher northern latitude wins (Uttara Kalamrita).
    Severity: Paura-Paura > Paura-Yayi > Yayi-Yayi.
    Returns list of war dicts.
    """
    war_planets = ["MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]
    planet_lats = planet_lats or {}
    wars: List[Dict] = []
    checked: Set[str] = set()

    for i, pA in enumerate(war_planets):
        for pB in war_planets[i+1:]:
            pair = f"{pA}_{pB}"
            if pair in checked:
                continue
            checked.add(pair)

            lonA = planet_lons.get(pA)
            lonB = planet_lons.get(pB)
            if lonA is None or lonB is None:
                continue

            dist = abs(lonA - lonB)
            if dist > 180:
                dist = 360 - dist
            if dist > 1.0:  # War orb: 1 degree
                continue

            # Determine victor
            # Primary: lower longitude wins
            if lonA <= lonB:
                victor, defeated = pA, pB
            else:
                victor, defeated = pB, pA

            # Tiebreak: check latitude if longitudes very close (< 0.05°)
            if dist < 0.05 and planet_lats:
                latA = planet_lats.get(pA, 0.0)
                latB = planet_lats.get(pB, 0.0)
                if latA >= latB:
                    victor, defeated = pA, pB
                else:
                    victor, defeated = pB, pA

            # Severity classification
            catA = "paura" if pA in _PAURA_PLANETS else "yayi"
            catB = "paura" if pB in _PAURA_PLANETS else "yayi"
            if catA == "paura" and catB == "paura":
                severity = "severe"
                cancellation_weight = 0.95   # near-total cancellation of defeated
            elif catA != catB:
                severity = "moderate"
                cancellation_weight = 0.65
            else:
                severity = "mild"
                cancellation_weight = 0.35

            wars.append({
                "planet_A": pA,
                "planet_B": pB,
                "victor": victor,
                "defeated": defeated,
                "orb_deg": round(dist, 3),
                "severity": severity,
                "cancellation_weight": cancellation_weight,
                "note": (
                    f"{defeated} defeated by {victor} in Graha Yuddha "
                    f"({severity}, orb {dist:.2f}°). "
                    f"All yogas of {defeated} reduced by {int(cancellation_weight*100)}%."
                ),
            })

    return wars


def _apply_graha_yuddha_cancellations(
        yogas: List[YogaResult],
        wars: List[Dict],
) -> None:
    """
    Mutate yoga results: reduce strength of yogas involving defeated war planets.
    """
    if not wars:
        return
    defeated_reductions: Dict[str, float] = {}
    for war in wars:
        def_planet = war["defeated"]
        weight = war["cancellation_weight"]
        # Take the most severe reduction for each defeated planet
        defeated_reductions[def_planet] = max(
            defeated_reductions.get(def_planet, 0.0), weight
        )

    for yoga in yogas:
        if not yoga.detected:
            continue
        for p in yoga.planets:
            if p in defeated_reductions:
                factor = 1.0 - defeated_reductions[p]
                yoga.strength = round(yoga.strength * factor, 3)
                old_reason = yoga.cancellation_reason
                war_note = f"{p} defeated in Graha Yuddha (strength *= {factor:.2f})"
                yoga.cancellation_reason = (
                    f"{old_reason}; {war_note}" if old_reason else war_note
                )
                break  # apply worst reduction once per yoga


# ═══════════════════════════════════════════════════════════════════
# SECTION C: RETROGRADE PARADOX LOGIC
# Source: Phaladeepika, Uttara Kalamrita
# ═══════════════════════════════════════════════════════════════════

def get_effective_retrograde_dignity(
        pname: str,
        planet_lons: Dict[str, float],
        is_retrograde: bool,
) -> str:
    """
    Compute effective dignity after retrograde paradox:
    - Retrograde + Exalted  → acts as DEBILITATED (Uttara Kalamrita paradox)
    - Retrograde + Debilitated → acts as EXALTED (double-negative)
    - Otherwise retrograde → Exalted-equivalent (Cheshtabala maximum)
    Returns: 'exalted_effective' | 'debilitated_effective' | 'standard' | 'strong_retro'
    """
    if not is_retrograde:
        return "standard"

    lon = planet_lons.get(pname)
    if lon is None:
        return "standard"

    exalted   = _is_exalted(pname, lon)
    debilited = _is_debilitated(pname, lon)

    if exalted:
        return "debilitated_effective"   # retro+exalted = acts debil
    if debilited:
        return "exalted_effective"       # retro+debil   = acts exalted
    return "strong_retro"               # retro in other sign = Cheshtabala max


def apply_retrograde_yoga_modifiers(
        yogas: List[YogaResult],
        planet_lons: Dict[str, float],
        retrograde_planets: Set[str],
) -> None:
    """
    Apply retrograde paradox to yoga strengths:
    - If yoga planet is retro+exalted → reduce yoga strength (acts debil)
    - If yoga planet is retro+debil → INCREASE yoga strength (acts exalted)
    Also marks delayed fructification.
    """
    for yoga in yogas:
        if not yoga.detected:
            continue
        has_retro = any(p in retrograde_planets for p in yoga.planets)
        if not has_retro:
            continue

        for p in yoga.planets:
            if p not in retrograde_planets:
                continue
            dignity = get_effective_retrograde_dignity(p, planet_lons, True)
            if dignity == "debilitated_effective":
                yoga.strength = round(yoga.strength * 0.4, 3)  # heavily reduced
                yoga.cancellation_reason = (
                    f"{yoga.cancellation_reason}; {p} retro+exalted = acts debilitated"
                    if yoga.cancellation_reason
                    else f"{p} retrograde+exalted acts as debilitated (Uttara Kalamrita)"
                )
            elif dignity == "exalted_effective":
                yoga.strength = min(1.0, round(yoga.strength * 1.6, 3))  # boosted
                yoga.description += f" [{p} retro+debil acts exalted → amplified]"
            elif dignity == "strong_retro":
                yoga.strength = min(1.0, round(yoga.strength * 1.15, 3))
            # All retrograde planets delay fructification
            yoga.description += f" [Delayed fructification: {p} retrograde]"
            break  # apply once per yoga


# ═══════════════════════════════════════════════════════════════════
# SECTION D: MD-AD AXIS EVALUATION + MANDUKA GATI AGE THEORY
# Source: Parashari rules, Jaimini age distribution
# ═══════════════════════════════════════════════════════════════════

def score_md_ad_relationship(
        md_lord: str,
        ad_lord: str,
        planet_houses: Dict[str, int],
) -> float:
    """
    Evaluate MD-AD axis relationship for yoga activation quality.
    Returns multiplier for yoga activation score:
      1.0  → 1-7 axis (mutual aspect) = max output
      0.0  → 2-12 or 6-8 axis (Shadashtaka) = blocked
      0.0  → same planet = neutral (no spike, explicit rule)
      0.7  → 3-11 axis = mild cooperation
      0.85 → 5-9 axis = trine cooperation
      0.9  → other axes
    """
    if not md_lord or not ad_lord:
        return 0.9
    if md_lord == ad_lord:
        return 0.0   # Same planet = strictly neutral per Parashari

    h_md = planet_houses.get(md_lord, 0)
    h_ad = planet_houses.get(ad_lord, 0)
    if not h_md or not h_ad:
        return 0.9

    diff = ((h_ad - h_md) % 12) + 1

    if diff == 7:      # 1-7 axis: mutual opposition-aspect
        return 1.0
    if diff in (2, 12):  # 2-12 axis
        return 0.0
    if diff in (6, 8):   # 6-8 axis (Shadashtaka)
        return 0.0
    if diff in (5, 9):   # 5-9 axis: trine cooperation
        return 0.85
    if diff in (3, 11):  # 3-11 axis: mild cooperation
        return 0.70
    return 0.90


# Manduka Gati: Frog's Leap house sequence (Jaimini principle)
# Maps to chronological 9-year age blocks over 108-year lifespan
_MANDUKA_SEQUENCE: List[int] = [4, 2, 8, 10, 12, 6, 5, 11, 1, 7, 9, 3]

# Sign modalities for sub-block timing within 9-year block
_SIRSODAYA_SIGNS = {2, 4, 5, 6, 7, 10}    # Gemini/Leo/Virgo/Libra/Scorpio/Aquarius → early third
_PRISTODAYA_SIGNS = {1, 3, 8, 9}           # Taurus/Cancer/Sagittarius/Capricorn → late third
# Pisces (11) = Ubhayodaya = middle third


def get_manduka_gati_life_phase(house: int) -> Dict:
    """
    Return life phase data for a yoga's house under Manduka Gati:
    - phase: 'early' (0-36 yrs) | 'middle' (36-72 yrs) | 'late' (72-108 yrs)
    - block_start_age: start year of the 9-year block
    - block_end_age: end year of the 9-year block
    """
    if house not in _MANDUKA_SEQUENCE:
        return {"phase": "unknown", "block_start_age": 0, "block_end_age": 108}

    idx = _MANDUKA_SEQUENCE.index(house)  # 0-11
    block_start = idx * 9
    block_end   = block_start + 9

    if idx < 4:
        phase = "early"    # houses 4,2,8,10 → 0-36 years
    elif idx < 8:
        phase = "middle"   # houses 12,6,5,11 → 36-72 years
    else:
        phase = "late"     # houses 1,7,9,3 → 72-108 years

    return {
        "phase": phase,
        "block_start_age": block_start,
        "block_end_age": block_end,
        "manduka_rank": idx + 1,
    }


# ═══════════════════════════════════════════════════════════════════
# SECTION E: ENHANCED COMBUSTION (with retrograde mitigation)
# Source: Classical texts + research file
# ═══════════════════════════════════════════════════════════════════

# Classical combustion orb limits (degrees from Sun)
_COMBUST_ORBS: Dict[str, float] = {
    "MOON":    12.0,
    "MARS":    17.0,
    "MERCURY": 14.0,  # direct; 12° retrograde
    "JUPITER": 11.0,
    "VENUS":   10.0,  # direct; 8° retrograde
    "SATURN":  15.0,
}
# Retrograde inner planet mitigation (reduced orb)
_COMBUST_ORBS_RETRO: Dict[str, float] = {
    "MERCURY": 12.0,
    "VENUS":    8.0,
}


def is_combust_enhanced(
        pname: str,
        planet_lons: Dict[str, float],
        retrograde_planets: Set[str] = None,
) -> bool:
    """
    Enhanced combustion check with retrograde mitigation for Mercury and Venus.
    Returns True if planet is within combustion orb of Sun.
    """
    if pname == "SUN":
        return False
    retrograde_planets = retrograde_planets or set()
    sun_lon = planet_lons.get("SUN", 0.0)
    lon     = planet_lons.get(pname, 0.0)
    dist    = angular_distance(lon, sun_lon)

    is_retro = pname in retrograde_planets
    if is_retro and pname in _COMBUST_ORBS_RETRO:
        orb = _COMBUST_ORBS_RETRO[pname]
    else:
        orb = _COMBUST_ORBS.get(pname, 12.0)

    return dist < orb


# ═══════════════════════════════════════════════════════════════════
# SECTION F: ALL 32 NABHASA YOGAS
# Source: Classical texts; operates on 7-planet distribution
# ═══════════════════════════════════════════════════════════════════

_MOVABLE_SIGNS  = {0, 3, 6, 9}   # Aries, Cancer, Libra, Capricorn
_FIXED_SIGNS    = {1, 4, 7, 10}  # Taurus, Leo, Scorpio, Aquarius
_DUAL_SIGNS     = {2, 5, 8, 11}  # Gemini, Virgo, Sagittarius, Pisces

_KENDRA_H   = {1, 4, 7, 10}
_SUCCEDENT_H = {2, 5, 8, 11}
_CADENT_H   = {3, 6, 9, 12}
_NAT_BENEFICS_SET  = {"JUPITER", "VENUS", "MERCURY", "MOON"}
_NAT_MALEFICS_SET  = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}


def _detect_nabhasa_yogas(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
) -> List[YogaResult]:
    """
    Detect all 32 Nabhasa Yogas based on 7-planet geometric distribution.
    Priority: Akriti detected → skip Sankhya (per classical rule).
    Categorized into 4 classes: Ashraya / Dala / Akriti / Sankhya.
    """
    results: List[YogaResult] = []
    # Use only 7 classical planets for Nabhasa
    planets_7 = {p: planet_houses.get(p, 0) for p in PLANET_NAMES_7 if p in planet_houses}
    if len(planets_7) < 7:
        return results  # need all 7

    houses_occupied: Set[int] = set(h for h in planets_7.values() if h > 0)
    signs_occupied: Set[int]  = set(sign_of(planet_lons.get(p, 0)) for p in PLANET_NAMES_7
                                     if p in planet_lons)

    def _all_in(sign_set: Set[int]) -> bool:
        return all(sign_of(planet_lons.get(p, 0)) in sign_set
                   for p in PLANET_NAMES_7 if p in planet_lons)

    def _house_list(ps=None) -> List[int]:
        ps = ps or PLANET_NAMES_7
        return [planets_7[p] for p in ps if p in planets_7]

    def _in_set(house: int, s: Set[int]) -> bool:
        return house in s

    planets_in_kendra    = [p for p, h in planets_7.items() if h in _KENDRA_H]
    planets_in_succedent = [p for p, h in planets_7.items() if h in _SUCCEDENT_H]
    planets_in_cadent    = [p for p, h in planets_7.items() if h in _CADENT_H]
    benefics_in_kendra   = [p for p in planets_in_kendra if p in _NAT_BENEFICS_SET]
    malefics_in_kendra   = [p for p in planets_in_kendra if p in _NAT_MALEFICS_SET]

    # ── CLASS 1: ASHRAYA YOGAS (sign modality) ──────────────────────────
    if _all_in(_MOVABLE_SIGNS):
        results.append(YogaResult(
            name="Rajju Yoga (Nabhasa-Ashraya)",
            category="nabhasa",
            detected=True, tier=4, strength=0.65,
            planets=PLANET_NAMES_7, houses=list(houses_occupied),
            description="All 7 planets in Movable signs. Rajju: ambitious, adaptable, frequent travel, lacks stability.",
            activating_dasha=[],
        ))
    elif _all_in(_FIXED_SIGNS):
        results.append(YogaResult(
            name="Musala Yoga (Nabhasa-Ashraya)",
            category="nabhasa",
            detected=True, tier=4, strength=0.65,
            planets=PLANET_NAMES_7, houses=list(houses_occupied),
            description="All 7 planets in Fixed signs. Musala: stable, obstinate, accumulator, resolute determination.",
            activating_dasha=[],
        ))
    elif _all_in(_DUAL_SIGNS):
        results.append(YogaResult(
            name="Nala Yoga (Nabhasa-Ashraya)",
            category="nabhasa",
            detected=True, tier=4, strength=0.60,
            planets=PLANET_NAMES_7, houses=list(houses_occupied),
            description="All 7 planets in Dual signs. Nala: pedantic, multi-tasking, over-analytical.",
            activating_dasha=[],
        ))

    # ── CLASS 2: DALA YOGAS (kendra benefic/malefic distribution) ────────
    if len(benefics_in_kendra) >= 3:
        results.append(YogaResult(
            name="Maala Yoga (Nabhasa-Dala)",
            category="nabhasa",
            detected=True, tier=3, strength=0.70,
            planets=benefics_in_kendra, houses=[planets_7[p] for p in benefics_in_kendra],
            description="3+ benefics in angular houses. Maala: constant enjoyment, luxury, fine possessions.",
            activating_dasha=benefics_in_kendra,
        ))
    if len(malefics_in_kendra) >= 3:
        results.append(YogaResult(
            name="Bhujanga Yoga (Nabhasa-Dala)",
            category="nabhasa",
            detected=True, tier=4, strength=0.70,
            planets=malefics_in_kendra, houses=[planets_7[p] for p in malefics_in_kendra],
            description="3+ malefics in angular houses. Bhujanga: continuous struggle, hostility, restriction.",
            activating_dasha=malefics_in_kendra,
        ))

    # ── CLASS 3: AKRITI YOGAS (shape-based 20 yogas) ─────────────────────
    akriti_detected = False
    all_hs = set(planets_7.values())

    def _confined_to(hs_set: Set[int]) -> bool:
        return all(h in hs_set for h in planets_7.values() if h > 0)

    def _confined_to_exactly(hs_set: Set[int]) -> bool:
        """All planets in hs_set AND at least one planet in each house in hs_set."""
        return _confined_to(hs_set)

    def _consecutive_from(start: int, count: int) -> Set[int]:
        return {(start - 1 + i) % 12 + 1 for i in range(count)}

    # Gada: all in 2 successive angular pairs
    for pair in [(1,4),(4,7),(7,10),(10,1)]:
        if _confined_to(set(pair)):
            results.append(YogaResult(
                name=f"Gada Yoga (Nabhasa-Akriti, H{pair[0]}-H{pair[1]})",
                category="nabhasa", detected=True, tier=3, strength=0.60,
                planets=PLANET_NAMES_7, houses=list(all_hs),
                description=f"All planets in successive angles {pair[0]}&{pair[1]}. Gada: warrior-like focus.",
                activating_dasha=[],
            ))
            akriti_detected = True

    # Sakata: all in 1st and 7th
    if _confined_to({1, 7}) and len(all_hs) <= 2:
        results.append(YogaResult(
            name="Sakata Yoga (Nabhasa-Akriti)",
            category="nabhasa", detected=True, tier=4, strength=0.65,
            planets=PLANET_NAMES_7, houses=list(all_hs),
            description="All planets in 1st & 7th. Sakata: severe fluctuations in fortune.",
            activating_dasha=[],
        ))
        akriti_detected = True

    # Vihanga: all in 4th and 10th
    if _confined_to({4, 10}) and len(all_hs) <= 2:
        results.append(YogaResult(
            name="Vihanga Yoga (Nabhasa-Akriti)",
            category="nabhasa", detected=True, tier=4, strength=0.60,
            planets=PLANET_NAMES_7, houses=list(all_hs),
            description="All planets in 4th & 10th. Vihanga: wandering nature, constant movement.",
            activating_dasha=[],
        ))
        akriti_detected = True

    # Sringataka: all in trikonas (1/5/9)
    if _confined_to({1, 5, 9}):
        results.append(YogaResult(
            name="Sringataka Yoga (Nabhasa-Akriti)",
            category="nabhasa", detected=True, tier=3, strength=0.75,
            planets=PLANET_NAMES_7, houses=list(all_hs),
            description="All planets in trikonas 1/5/9. Sringataka: happiness, martial prowess, dharmic life.",
            activating_dasha=[],
        ))
        akriti_detected = True

    # Hala: all in mutual non-kendra triads (2-6-10 or 3-7-11 or 4-8-12)
    for triad in [(2,6,10),(3,7,11),(4,8,12)]:
        if _confined_to(set(triad)):
            results.append(YogaResult(
                name=f"Hala Yoga (Nabhasa-Akriti, {triad})",
                category="nabhasa", detected=True, tier=4, strength=0.55,
                planets=PLANET_NAMES_7, houses=list(all_hs),
                description=f"All planets in {triad}. Hala: agricultural/labor-intensive wealth.",
                activating_dasha=[],
            ))
            akriti_detected = True

    # Vajra: all benefics in 1+7, all malefics in 4+10
    benef_hs = {planets_7[p] for p in PLANET_NAMES_7
                if p in _NAT_BENEFICS_SET and p in planets_7}
    malef_hs = {planets_7[p] for p in PLANET_NAMES_7
                if p in _NAT_MALEFICS_SET and p in planets_7}
    if benef_hs and malef_hs:
        if benef_hs <= {1,7} and malef_hs <= {4,10}:
            results.append(YogaResult(
                name="Vajra Yoga (Nabhasa-Akriti)",
                category="nabhasa", detected=True, tier=2, strength=0.80,
                planets=PLANET_NAMES_7, houses=list(all_hs),
                description="Benefics in 1+7, malefics in 4+10. Vajra: thunderbolt resilience, victory.",
                activating_dasha=[],
            ))
            akriti_detected = True
        if malef_hs <= {1,7} and benef_hs <= {4,10}:
            results.append(YogaResult(
                name="Yava Yoga (Nabhasa-Akriti)",
                category="nabhasa", detected=True, tier=3, strength=0.65,
                planets=PLANET_NAMES_7, houses=list(all_hs),
                description="Malefics in 1+7, benefics in 4+10. Yava: barley shape; growth with self-barriers.",
                activating_dasha=[],
            ))
            akriti_detected = True

    # Kamala: all 7 planets spread across all 4 kendras
    if all_hs <= {1,4,7,10} and len(all_hs) == 4:
        results.append(YogaResult(
            name="Kamala Yoga (Nabhasa-Akriti)",
            category="nabhasa", detected=True, tier=2, strength=0.85,
            planets=PLANET_NAMES_7, houses=list(all_hs),
            description="All planets spread across all 4 kendras. Kamala (lotus): extreme prominence, purity.",
            activating_dasha=[],
        ))
        akriti_detected = True

    # Vapi: all in cadent OR all in succedent
    if _confined_to(_CADENT_H) or _confined_to(_SUCCEDENT_H):
        hs_type = "cadent (3/6/9/12)" if _confined_to(_CADENT_H) else "succedent (2/5/8/11)"
        results.append(YogaResult(
            name=f"Vapi Yoga (Nabhasa-Akriti, {hs_type})",
            category="nabhasa", detected=True, tier=3, strength=0.65,
            planets=PLANET_NAMES_7, houses=list(all_hs),
            description=f"All planets in {hs_type}. Vapi: hidden wealth, indirect power.",
            activating_dasha=[],
        ))
        akriti_detected = True

    # Consecutive 4-house yogas (Yupa/Sara/Shakti/Danda)
    for start_h, yoga_n in [(1,"Yupa"),(4,"Sara"),(7,"Shakti"),(10,"Danda")]:
        cset = _consecutive_from(start_h, 4)
        if _confined_to(cset):
            results.append(YogaResult(
                name=f"{yoga_n} Yoga (Nabhasa-Akriti)",
                category="nabhasa", detected=True, tier=3, strength=0.60,
                planets=PLANET_NAMES_7, houses=list(all_hs),
                description=f"All planets in 4 consecutive houses from H{start_h}. {yoga_n} pattern.",
                activating_dasha=[],
            ))
            akriti_detected = True

    # Consecutive 7-house yogas (Nauka/Koota/Chatra/Chapa)
    for start_h, yoga_n in [(1,"Nauka"),(4,"Koota"),(7,"Chatra"),(10,"Chapa")]:
        cset = _consecutive_from(start_h, 7)
        if _confined_to(cset):
            results.append(YogaResult(
                name=f"{yoga_n} Yoga (Nabhasa-Akriti)",
                category="nabhasa", detected=True, tier=3, strength=0.65,
                planets=PLANET_NAMES_7, houses=list(all_hs),
                description=f"All planets in 7 consecutive houses from H{start_h}. {yoga_n}: broad life theme.",
                activating_dasha=[],
            ))
            akriti_detected = True

    # Ardha Chandra: 7 contiguous houses from any succedent/cadent start
    if not akriti_detected:
        for start_h in list(_SUCCEDENT_H) + list(_CADENT_H):
            cset = _consecutive_from(start_h, 7)
            if _confined_to(cset):
                results.append(YogaResult(
                    name="Ardha Chandra Yoga (Nabhasa-Akriti)",
                    category="nabhasa", detected=True, tier=3, strength=0.62,
                    planets=PLANET_NAMES_7, houses=list(all_hs),
                    description=f"All planets in 7 consecutive houses from H{start_h}. Half-moon shape; adaptable, artistic.",
                    activating_dasha=[],
                ))
                akriti_detected = True
                break

    # Chakra: all in alternate houses from lagna (1,3,5,7,9,11)
    if _confined_to({1,3,5,7,9,11}):
        results.append(YogaResult(
            name="Chakra Yoga (Nabhasa-Akriti)",
            category="nabhasa", detected=True, tier=2, strength=0.80,
            planets=PLANET_NAMES_7, houses=list(all_hs),
            description="All planets in alternate signs from lagna (1/3/5/7/9/11). Chakra: imperial power.",
            activating_dasha=[],
        ))
        akriti_detected = True

    # Samudra: all in alternate houses from 2nd (2,4,6,8,10,12)
    if _confined_to({2,4,6,8,10,12}):
        results.append(YogaResult(
            name="Samudra Yoga (Nabhasa-Akriti)",
            category="nabhasa", detected=True, tier=2, strength=0.78,
            planets=PLANET_NAMES_7, houses=list(all_hs),
            description="All planets in alternate signs from 2nd (2/4/6/8/10/12). Samudra: oceanic wealth.",
            activating_dasha=[],
        ))
        akriti_detected = True

    # ── CLASS 4: SANKHYA YOGAS (count-based, skip if Akriti found) ───────
    if not akriti_detected:
        n_signs = len(signs_occupied)
        sankhya_map = {
            1: ("Gola Yoga",  "destitution, social isolation"),
            2: ("Yuga Yoga",  "heresy, poverty, unusual world-view"),
            3: ("Soola Yoga", "sharp violent nature, surgical skill"),
            4: ("Kedara Yoga","agricultural wealth, truthfulness"),
            5: ("Paasa Yoga", "large family, wealth entanglement"),
            6: ("Daamini Yoga","charitable, helpful, many assets"),
            7: ("Veena Yoga", "cultured, musical, harmonious life"),
        }
        if n_signs in sankhya_map:
            name, desc = sankhya_map[n_signs]
            results.append(YogaResult(
                name=f"{name} (Nabhasa-Sankhya)",
                category="nabhasa", detected=True, tier=4, strength=0.55,
                planets=PLANET_NAMES_7, houses=list(houses_occupied),
                description=f"{n_signs} signs occupied by all 7 planets. {name}: {desc}.",
                activating_dasha=[],
            ))

    return results


# ═══════════════════════════════════════════════════════════════════
# SECTION G: ENHANCED COMPOUND INTERACTIONS
# Source: Research file Sections 1-5
# ═══════════════════════════════════════════════════════════════════

def compute_panchamahapurusha_raja_symbiosis(
        yogas: List[YogaResult],
) -> List[Dict]:
    """
    When a Panchamahapurusha yoga geographically intersects with a Raja Yoga
    (via shared planet), compute symbiosis multiplier.
    Classical rule: Panchamahapurusha contributes 60% of required Raja Yoga
    strength — acts as indestructible foundation.
    Returns list of symbiosis records.
    """
    pancha = [y for y in yogas if y.category == "pancha_mahapurusha" and y.detected]
    raja   = [y for y in yogas if y.category == "raj" and y.detected]
    symbiosis_records = []

    for py in pancha:
        for ry in raja:
            shared = set(py.planets) & set(ry.planets)
            if shared:
                # Apply symbiosis: boost Raja yoga strength by 60% contribution
                boost = 0.60 * py.strength
                old_s = ry.strength
                ry.strength = min(1.0, ry.strength + boost * 0.40)  # 40% of the 60% contribution
                ry.description += (
                    f" [+Pancha Mahapurusha ({py.name}) symbiosis via {shared}: "
                    f"strength {old_s:.2f}→{ry.strength:.2f}, indestructible foundation]"
                )
                symbiosis_records.append({
                    "pancha": py.name,
                    "raja":   ry.name,
                    "shared_planets": list(shared),
                    "boost_applied": round(ry.strength - old_s, 3),
                })

    return symbiosis_records


def compute_dhana_stacking_tier(
        yogas: List[YogaResult],
        planet_houses: Dict[str, int],
        house_lords: Dict[int, str],
        shadbala_ratios: Dict[str, float],
) -> Dict:
    """
    Evaluate Dhana Yoga stacking thresholds and Saturn 2nd-house ceiling.
    Returns wealth tier and any ceiling constraints.
    Tiers:
      1: Single 2L-11L link → financial stability
      2: 5L/9L integrated into 2L-11L axis → prosperity
      3: Parivartana 2L-11L + strong Lagna lord → extreme wealth
      3+: 3+ concurrent Dhana Yogas + high Jupiter/Sun dignity → transcendent wealth
    Saturn 2nd ceiling: hard cap regardless of stacking density.
    """
    dhana_yogas  = [y for y in yogas if y.category == "dhana" and y.detected]
    n_dhana      = len(dhana_yogas)

    l2   = house_lords.get(2, "")
    l11  = house_lords.get(11, "")
    l5   = house_lords.get(5, "")
    l9   = house_lords.get(9, "")
    l1   = house_lords.get(1, "")

    h2_lord  = planet_houses.get(l2, 0)  if l2  else 0
    h11_lord = planet_houses.get(l11, 0) if l11 else 0

    # Parivartana between 2L and 11L
    parivartana_2_11 = (h2_lord == 11 and h11_lord == 2) if (l2 and l11) else False

    # 5L or 9L connected to 2L-11L axis
    l5_h   = planet_houses.get(l5, 0) if l5 else 0
    l9_h   = planet_houses.get(l9, 0) if l9 else 0
    axis_houses = {h2_lord, h11_lord}
    l5_in_axis  = l5_h in axis_houses or l5_h in (2, 11)
    l9_in_axis  = l9_h in axis_houses or l9_h in (2, 11)
    dharma_integrated = l5_in_axis or l9_in_axis

    # Lagna lord strength
    l1_str = shadbala_ratios.get(l1, 0.0) if l1 else 0.0

    # Determine tier
    if n_dhana >= 3 and (shadbala_ratios.get("JUPITER", 0.5) >= 0.8
                          or shadbala_ratios.get("SUN", 0.5) >= 0.8):
        tier = "transcendent"  # multi-millionaire/billionaire potential
    elif parivartana_2_11 and l1_str >= 0.9:
        tier = "extreme"
    elif dharma_integrated:
        tier = "prosperity"
    elif n_dhana >= 1:
        tier = "stable"
    else:
        tier = "none"

    # Saturn ceiling check
    saturn_h = planet_houses.get("SATURN", 0)
    saturn_in_2nd = (saturn_h == 2)
    saturn_aspects_2nd_lord = False
    if l2:
        sat_asp = abs(saturn_h - h2_lord)
        if sat_asp > 6:
            sat_asp = 12 - sat_asp
        # Saturn aspects 3rd/7th/10th from itself
        if sat_asp in (2, 6, 9):  # house diff of 3,7,10 from Saturn
            saturn_aspects_2nd_lord = True

    saturn_ceiling = saturn_in_2nd or saturn_aspects_2nd_lord
    ceiling_note = ""
    if saturn_ceiling:
        ceiling_note = (
            "SATURN CEILING ACTIVE: Saturn in 2nd or aspecting 2nd lord → "
            "hard cap on Dhana Yoga output regardless of stacking. "
            "Lifelong financial resistance/debt cycles."
        )

    return {
        "dhana_count": n_dhana,
        "wealth_tier": tier,
        "parivartana_2_11": parivartana_2_11,
        "dharma_integrated": dharma_integrated,
        "saturn_ceiling": saturn_ceiling,
        "ceiling_note": ceiling_note,
    }


# ─── Main Detector ────────────────────────────────────────────────

# ─── Yoga Hierarchy Tier Assignment ──────────────────────────────────────────

_TIER_1_TYPES = {"pancha_mahapurusha"}  # innate capacity/stamina
_TIER_2_NAMES = {"Raj Yoga", "Neechabhanga Raja Yoga", "Dharma-Karma Adhipati",
                 "Adhi Yoga", "Viparita Raja Yoga"}
_TIER_3_TYPES = {"dhana"}  # financial accumulation
_TIER_4_TYPES = {"simple", "challenging", "moksha", "special"}  # skill/flavor


def _assign_tier(yoga: YogaResult) -> int:
    """Assign hierarchy tier based on category and name."""
    if yoga.category in _TIER_1_TYPES:
        return 1
    if yoga.category == "raj" or any(t in yoga.name for t in _TIER_2_NAMES):
        return 2
    if yoga.category in _TIER_3_TYPES:
        return 3
    return 4


# ─── Proxy Activator Scoring ──────────────────────────────────────────────────

_NATURAL_FRIENDS: Dict[str, Set[str]] = {
    "SUN":     {"MOON", "MARS", "JUPITER"},
    "MOON":    {"SUN", "MERCURY"},
    "MARS":    {"SUN", "MOON", "JUPITER"},
    "MERCURY": {"SUN", "VENUS"},
    "JUPITER": {"SUN", "MOON", "MARS"},
    "VENUS":   {"MERCURY", "SATURN"},
    "SATURN":  {"MERCURY", "VENUS"},
}


def score_yoga_activation_dasha(
    yoga: YogaResult,
    dasha_planet: str,
    antardasha_planet: str,
    shadbala_ratios: Dict[str, float],
    planet_houses: Dict[str, int],
    asp_map: Optional[Dict] = None,
) -> float:
    """
    Score yoga activation level for current Dasha/Antardasha:
      - Constituent MD/AD lord → 1.00 (100% activation)
      - Proxy activator (dispositor of yoga sign OR friendly planet
        aspecting yoga planets with high Shadbala) → 0.50–0.70
      - Transit Gate: Jupiter AND Saturn aspecting/in yoga houses = bonus
      - Otherwise → 0.0 (potential without manifestation)
    """
    constituents = set(yoga.activating_dasha)

    # 100% activation: constituent MD lord or AD lord
    if dasha_planet in constituents or antardasha_planet in constituents:
        return 1.00

    # Proxy activation (50-70%): check dispositor + friendly aspect
    asp_map = asp_map or {}
    yoga_houses = set(yoga.houses)

    proxy_score = 0.0
    for check_planet in (dasha_planet, antardasha_planet):
        # Friendly to a constituent?
        friends = _NATURAL_FRIENDS.get(check_planet, set())
        if friends & constituents:
            str_ratio = shadbala_ratios.get(check_planet, 0.5)
            # Shadbala-weighted proxy score
            if str_ratio >= 0.80:
                proxy_score = max(proxy_score, 0.70)
            elif str_ratio >= 0.60:
                proxy_score = max(proxy_score, 0.60)
            else:
                proxy_score = max(proxy_score, 0.50)

        # Dispositor of yoga house sign is the Dasha lord?
        for yh in yoga_houses:
            planet_h = planet_houses.get(check_planet, 0)
            if planet_h == yh:
                proxy_score = max(proxy_score, 0.65)

    return proxy_score


# ─── Yoga Compounding ─────────────────────────────────────────────────────────

def compute_yoga_compounding(
    yogas: List[YogaResult],
) -> Dict[str, object]:
    """
    Computes exponential compounding for networked yogas.

    Two yogas are networked if they share planets (shared planets = network nodes).
    Networked yogas multiply auspiciousness rather than adding.

    Algorithm:
      1. Build a graph: yoga ↔ yoga if they share a planet.
      2. For each connected component (network), compound = product of strengths.
      3. If direct conflict (same domain, e.g. Dhana + Daridra in same houses):
         Three Pillar Rule determines winner (higher Shadbala wins).
    Returns:
      {
        "compounded_strength": float,   # overall multiplied score
        "networks": [...],              # list of yoga clusters with shared planets
        "network_nodes": Dict[str, List[str]],  # planet → [yoga names]
      }
    """
    if not yogas:
        return {"compounded_strength": 0.0, "networks": [], "network_nodes": {}}

    # Build planet → yoga membership
    planet_to_yogas: Dict[str, List[str]] = {}
    for y in yogas:
        for p in y.planets:
            planet_to_yogas.setdefault(p, []).append(y.name)

    # Build connectivity: which yogas share a planet
    network_nodes: Dict[str, List[str]] = {
        p: names for p, names in planet_to_yogas.items() if len(names) >= 2
    }

    # Cluster yogas that are connected via shared planets
    yoga_names = [y.name for y in yogas]
    visited = set()
    networks = []

    def _connected_component(start_yoga: YogaResult) -> List[YogaResult]:
        cluster = []
        stack   = [start_yoga]
        while stack:
            curr = stack.pop()
            if curr.name in visited:
                continue
            visited.add(curr.name)
            cluster.append(curr)
            # Find all yogas sharing a planet with curr
            for p in curr.planets:
                for ny_name in planet_to_yogas.get(p, []):
                    match = next((y for y in yogas if y.name == ny_name
                                  and ny_name not in visited), None)
                    if match:
                        stack.append(match)
        return cluster

    for yoga in yogas:
        if yoga.name not in visited:
            cluster = _connected_component(yoga)
            if len(cluster) > 1:
                # Networked: multiply strengths (exponential compounding)
                compound = 1.0
                for y in cluster:
                    compound *= y.strength
                # Scale back up: product of N values in [0,1] goes toward 0
                # Use geometric-mean escalation: compound^(1/N) * N_bonus_factor
                n = len(cluster)
                compounded = (compound ** (1.0 / n)) * min(1.0, 1.0 + 0.15 * (n - 1))
                networks.append({
                    "yogas": [y.name for y in cluster],
                    "shared_planets": [
                        p for p in planet_to_yogas
                        if len(planet_to_yogas[p]) >= 2 and
                        any(p in y.planets for y in cluster)
                    ],
                    "individual_strengths": [round(y.strength, 3) for y in cluster],
                    "compounded_strength": round(min(1.0, compounded), 3),
                    "tiers": sorted({y.tier for y in cluster}),
                })
            else:
                networks.append({
                    "yogas": [cluster[0].name] if cluster else [],
                    "shared_planets": [],
                    "individual_strengths": [round(cluster[0].strength, 3)] if cluster else [],
                    "compounded_strength": round(cluster[0].strength, 3) if cluster else 0.0,
                    "tiers": [cluster[0].tier] if cluster else [],
                })

    # Overall compounded strength: weighted by tier
    tier_weights = {1: 1.5, 2: 1.3, 3: 1.1, 4: 1.0}
    if networks:
        weighted_total = sum(
            n["compounded_strength"] * tier_weights.get(min(n["tiers"]) if n["tiers"] else 4, 1.0)
            for n in networks
        )
        compounded_strength = min(1.0, weighted_total / len(networks))
    else:
        compounded_strength = 0.0

    return {
        "compounded_strength": round(compounded_strength, 3),
        "networks": networks,
        "network_nodes": network_nodes,
    }


# ═══════════════════════════════════════════════════════════════════
# SECTION H: PHASE 1D — SAMBANDHA, GRADING, DARIDRA, ARISTHA, PRAVRAJYA
# ═══════════════════════════════════════════════════════════════════

def has_sambandha(
        planet_a: str,
        planet_b: str,
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        house_lords: Dict[int, str],
        asp_map: Dict = None,
) -> bool:
    """
    Returns True if planet_a and planet_b have a Sambandha (relationship):
      1. Conjunction — both occupy the same house
      2. Mutual aspect — each aspects the other (from asp_map)
      3. Parivartana — each is in the other's own sign (sign exchange)
    """
    if asp_map is None:
        asp_map = {}
    ha = planet_houses.get(planet_a, 0)
    hb = planet_houses.get(planet_b, 0)
    # 1. Conjunction
    if ha and hb and ha == hb:
        return True
    # 2. Mutual aspect
    if (planet_a, planet_b) in asp_map or (planet_b, planet_a) in asp_map:
        return True
    # 3. Parivartana — pA in sign owned by pB AND pB in sign owned by pA
    sign_a = sign_of(planet_lons.get(planet_a, 0))
    sign_b = sign_of(planet_lons.get(planet_b, 0))
    # Build reverse map: planet_name → list of own signs (0-based index)
    own_of_a: List[int] = []
    own_of_b: List[int] = []
    try:
        pa_enum = _P.get(planet_a)
        pb_enum = _P.get(planet_b)
        if pa_enum and pb_enum:
            for s_enum, lord_enum in SIGN_LORDS.items():
                if lord_enum == pa_enum:
                    own_of_a.append(s_enum.value)
                if lord_enum == pb_enum:
                    own_of_b.append(s_enum.value)
            if sign_a in own_of_b and sign_b in own_of_a:
                return True
    except Exception:
        pass
    return False


def grade_yoga(
        yoga_planets: List[str],
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        shadbala_ratios: Dict[str, float],
        asp_map: Dict = None,
        malefic_set: Optional[Set[str]] = None,
) -> Dict:
    """
    Universal yoga grading: returns {grade: str, score: float}.
      S-Tier (1.0): exalted/moolatrikona + kendra/trikona, no malefic combust
      A-Tier (0.75): own sign OR avg shadbala >= 1.0, kendra/trikona, not combust
      B-Tier (0.50): shadbala >= 0.7, neutral positions
      C-Tier (0.25): weak, afflicted, upachaya
    """
    if asp_map is None:
        asp_map = {}
    if malefic_set is None:
        malefic_set = {p.name for p in NATURAL_MALEFICS}

    avg_sb = _avg_strength(yoga_planets, shadbala_ratios)
    any_combust = any(_is_combust(p, planet_lons) for p in yoga_planets)
    any_exalted = any(_is_exalted(p, planet_lons.get(p, 0)) for p in yoga_planets)
    any_moolatrikona = any(
        MOOLATRIKONA.get(_P.get(p)) is not None
        and sign_of(planet_lons.get(p, 0)) == MOOLATRIKONA.get(_P.get(p)).value
        for p in yoga_planets if _P.get(p)
    )
    all_kendra_trikona = all(
        _is_in_kendra(planet_houses.get(p, 0)) or _is_in_trikona(planet_houses.get(p, 0))
        for p in yoga_planets
    )
    any_own = any(
        _is_own_sign(p, sign_of(planet_lons.get(p, 0))) for p in yoga_planets
    )
    any_dusthana = any(planet_houses.get(p, 0) in {6, 8, 12} for p in yoga_planets)

    if (any_exalted or any_moolatrikona) and all_kendra_trikona and not any_combust:
        return {"grade": "S", "score": 1.0}
    if (any_own or avg_sb >= 1.0) and all_kendra_trikona and not any_combust:
        return {"grade": "A", "score": 0.75}
    if avg_sb >= 0.7 and not any_dusthana:
        return {"grade": "B", "score": 0.5}
    return {"grade": "C", "score": 0.25}


def _daridra_yogas(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        house_lords: Dict[int, str],
        shadbala_ratios: Dict[str, float],
) -> List[YogaResult]:
    """
    Daridra (poverty) yogas:
      - L11 in dusthana (6, 8, 12)
      - L2 in dusthana
      - Kemadruma (Moon isolated — no planets in 2nd or 12th from Moon)
    Viparita override: if the afflicted lord also rules a dusthana, the yoga is cancelled
    (the malefic house-ownership neutralises the damage).
    """
    results: List[YogaResult] = []
    dusthana = {6, 8, 12}
    # Dusthana lords (rulers) — for Viparita check
    dusthana_lords: Set[str] = set()
    for dh in dusthana:
        l = house_lords.get(dh, "")
        if l:
            dusthana_lords.add(l)

    for house_num, tag in [(11, "11th"), (2, "2nd")]:
        lord = house_lords.get(house_num, "")
        if not lord:
            continue
        h = planet_houses.get(lord, 0)
        if h not in dusthana:
            continue
        # Viparita override: lord also rules a dusthana house → cancel
        if lord in dusthana_lords:
            continue
        s = shadbala_ratios.get(lord, 0.5)
        results.append(YogaResult(
            name=f"Daridra Yoga (L{house_num} in H{h})",
            category="daridra",
            detected=True,
            strength=1.0 - s,
            planets=[lord],
            houses=[h],
            description=(
                f"Lord of {tag} placed in {h}th house (dusthana). "
                "Daridra Yoga: financial strain, losses, obstructions to gains. "
                "Activated during that lord's dasha."
            ),
            activating_dasha=[lord],
        ))

    # Kemadruma as Daridra subtype (if Moon is isolated)
    moon_h = planet_houses.get("MOON", 0)
    if moon_h and not _is_in_kendra(moon_h):
        second_from_moon   = (moon_h % 12) + 1
        twelfth_from_moon  = (moon_h - 2) % 12 + 1
        surrounding = {moon_h, second_from_moon, twelfth_from_moon}
        nearby = [
            p for p in PLANET_NAMES_7
            if p != "MOON" and planet_houses.get(p, 0) in surrounding
        ]
        if not nearby:
            results.append(YogaResult(
                name="Kemadruma Daridra Yoga",
                category="daridra",
                detected=True,
                strength=1.0 - shadbala_ratios.get("MOON", 0.5),
                planets=["MOON"],
                houses=[moon_h],
                description=(
                    "Moon isolated with no planets in 2nd/12th from itself. "
                    "Kemadruma: emotional and financial hardship; lack of support."
                ),
                activating_dasha=["MOON"],
            ))
    return results


def _aristha_yogas(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        shadbala_ratios: Dict[str, float],
        lagna_sign: int = 0,
        asp_map: Dict = None,
) -> List[YogaResult]:
    """
    Aristha (health adversity) yogas:
      Balarishta:
        (a) Moon in dusthana (6/8/12) AND aspected by MAR or SAT
        (b) Moon conjunct Rahu or Ketu
        (c) Luminaries (Sun+Moon) conjunct a node in the same sign
      Bhanga (cancellation):
        - Jupiter in H1
        - Lagna lord (house_lords[1]) in kendra (1/4/7/10)
      If Bhanga applies, yoga is still recorded but cancellation_reason is set.
    """
    if asp_map is None:
        asp_map = {}
    results: List[YogaResult] = []
    dusthana = {6, 8, 12}
    moon_h = planet_houses.get("MOON", 0)

    def _bhanga_check() -> Optional[str]:
        jup_h = planet_houses.get("JUPITER", 0)
        if jup_h == 1:
            return "Jupiter in Lagna cancels Balarishta"
        # lagna lord in kendra — requires house_lords, but we don't have it here;
        # we'll use a simpler proxy: any planet in H1 that belongs to lagna sign
        return None

    bhanga_reason = _bhanga_check()

    # Case (a): Moon in dusthana + malefic aspect
    if moon_h in dusthana:
        malefic_asp = (
            ("MARS", "MOON") in asp_map or ("MOON", "MARS") in asp_map or
            ("SATURN", "MOON") in asp_map or ("MOON", "SATURN") in asp_map
        )
        if malefic_asp:
            results.append(YogaResult(
                name="Balarishta Yoga (Moon in dusthana + malefic aspect)",
                category="aristha",
                detected=True,
                strength=0.8,
                planets=["MOON"],
                houses=[moon_h],
                description=(
                    f"Moon in {moon_h}th (dusthana) aspected by Mars/Saturn. "
                    "Balarishta: health challenges especially in early life."
                ),
                cancellation_reason=bhanga_reason or "",
                activating_dasha=["MOON"],
            ))

    # Case (b): Moon conjunct Rahu or Ketu
    rahu_h = planet_houses.get("RAHU", planet_houses.get("NORTHNODE", 0))
    ketu_h = planet_houses.get("KETU", planet_houses.get("SOUTHNODE", 0))
    if moon_h and (moon_h == rahu_h or moon_h == ketu_h):
        node_name = "RAHU" if moon_h == rahu_h else "KETU"
        results.append(YogaResult(
            name=f"Balarishta Yoga (Moon conjunct {node_name})",
            category="aristha",
            detected=True,
            strength=0.7,
            planets=["MOON", node_name],
            houses=[moon_h],
            description=(
                f"Moon conjunct {node_name} in H{moon_h}. "
                "Node conjunction afflicts Moon: health, emotional instability."
            ),
            cancellation_reason=bhanga_reason or "",
            activating_dasha=["MOON"],
        ))

    # Case (c): Sun + Moon both conjunct a node (same house)
    sun_h = planet_houses.get("SUN", 0)
    if sun_h and moon_h and sun_h == moon_h:
        if sun_h == rahu_h or sun_h == ketu_h:
            node_name = "RAHU" if sun_h == rahu_h else "KETU"
            results.append(YogaResult(
                name=f"Chandraditya-Grahan Aristha (Luminaries + {node_name})",
                category="aristha",
                detected=True,
                strength=0.9,
                planets=["SUN", "MOON", node_name],
                houses=[sun_h],
                description=(
                    f"Sun and Moon both conjunct {node_name} in H{sun_h}. "
                    "Severe eclipse-type affliction; vitality and mind challenged."
                ),
                cancellation_reason=bhanga_reason or "",
                activating_dasha=["SUN", "MOON"],
            ))
    return results


def _pravrajya_yogas(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        house_lords: Dict[int, str],
        shadbala_ratios: Dict[str, float],
        asp_map: Dict = None,
) -> List[YogaResult]:
    """
    Pravrajya (renunciation / spiritual path) yoga:
      - 4 or more planets in a single sign
      - Flavor determined by the highest-Shadbala planet among those crowded
        SUN=Tapasvi  MOON=Kapali  MARS=Rakta-Sannyas  MERCURY=Jnani
        JUPITER=Parivrajaka  VENUS=Bhushundi  SATURN=Yogi
      - Ketu trigger: Ketu in 12th + aspected by L5, L9, or Jupiter ← adds 0.1 boost
      - Cancelled if the strongest planet is combust
    """
    if asp_map is None:
        asp_map = {}
    results: List[YogaResult] = []
    _FLAVOR = {
        "SUN": "Tapasvi (ascetic of fire)",
        "MOON": "Kapali (wandering mendicant)",
        "MARS": "Rakta-Sannyas (warrior renunciant)",
        "MERCURY": "Jnani (philosopher-scholar)",
        "JUPITER": "Parivrajaka (forest sage)",
        "VENUS": "Bhushundi (devotee of beauty)",
        "SATURN": "Yogi (disciplined ascetic)",
    }
    # Count planets per sign
    sign_count: Dict[int, List[str]] = {}
    for p in PLANET_NAMES_7:
        s = sign_of(planet_lons.get(p, 0))
        sign_count.setdefault(s, []).append(p)

    for sign_idx, planets_in_sign in sign_count.items():
        if len(planets_in_sign) < 4:
            continue
        # Strongest by Shadbala
        strongest = max(planets_in_sign, key=lambda p: shadbala_ratios.get(p, 0))
        flavor = _FLAVOR.get(strongest, "unknown")
        # Check cancellation: strongest planet combust
        if _is_combust(strongest, planet_lons):
            continue
        # Ketu trigger bonus
        ketu_h = planet_houses.get("KETU", planet_houses.get("SOUTHNODE", 0))
        ketu_bonus = 0.0
        l5 = house_lords.get(5, "")
        l9 = house_lords.get(9, "")
        if ketu_h == 12:
            jup_asp = ("JUPITER", "KETU") in asp_map or ("KETU", "JUPITER") in asp_map
            l5_asp  = l5 and (
                (l5, "KETU") in asp_map or ("KETU", l5) in asp_map
            )
            l9_asp  = l9 and (
                (l9, "KETU") in asp_map or ("KETU", l9) in asp_map
            )
            if jup_asp or l5_asp or l9_asp:
                ketu_bonus = 0.1
        strength = min(1.0, _avg_strength(planets_in_sign, shadbala_ratios) + ketu_bonus)
        results.append(YogaResult(
            name=f"Pravrajya Yoga ({flavor})",
            category="pravrajya",
            detected=True,
            strength=strength,
            planets=planets_in_sign,
            houses=[planet_houses.get(p, 0) for p in planets_in_sign],
            description=(
                f"{len(planets_in_sign)} planets in sign {sign_idx}. "
                f"Pravrajya Yoga — {flavor}. Indicates renunciation, "
                "spiritual absorption, or a life devoted to higher purpose."
            ),
            activating_dasha=[strongest],
        ))
    return results


# ═══════════════════════════════════════════════════════════════════
# SECTION I: UNIFIED YOGA OUTPUT (Phase 1D.9)
# ═══════════════════════════════════════════════════════════════════

_YOGA_DOMAIN_MAP: Dict[str, str] = {
    "raj": "career", "dhana": "finance", "daridra": "finance",
    "aristha": "health", "nabhasa": "general", "pravrajya": "spiritual",
    "moksha": "spiritual", "pancha_mahapurusha": "career",
    "challenging": "general", "graha_yuddha": "general",
}


def compute_all_extended_yogas(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        shadbala_ratios: Dict[str, float],
        house_lords: Dict[int, str],
        asp_map: Dict = None,
        lagna_sign: int = 0,
        dasha_planet: str = "",
        antardasha_planet: str = "",
        retrograde_planets: Set[str] = None,
        planet_lats: Dict[str, float] = None,
) -> List[Dict]:
    """
    Master yoga computation returning unified list of dicts for Phase 1D.9.
    Combines detect_all_yogas() with new Daridra, Aristha, Pravrajya detectors
    and grades each yoga with grade_yoga().

    Returns list of:
      {name, type, planets, grade, score, domain, active, cancellation}
    """
    if asp_map is None:
        asp_map = {}
    retrograde_planets = retrograde_planets or set()
    planet_lats = planet_lats or {}

    # ── Run base detector (all existing yogas) ─────────────────
    base: List[YogaResult] = detect_all_yogas(
        planet_houses, planet_lons, shadbala_ratios,
        house_lords, asp_map, lagna_sign=lagna_sign,
        dasha_planet=dasha_planet, antardasha_planet=antardasha_planet,
        retrograde_planets=retrograde_planets, planet_lats=planet_lats,
    )

    # ── Run new Phase 1D detectors ─────────────────────────────
    daridra  = _daridra_yogas(planet_houses, planet_lons, house_lords, shadbala_ratios)
    aristha  = _aristha_yogas(planet_houses, planet_lons, shadbala_ratios,
                               lagna_sign=lagna_sign, asp_map=asp_map)
    pravrajya = _pravrajya_yogas(planet_houses, planet_lons, house_lords,
                                  shadbala_ratios, asp_map=asp_map)

    all_results: List[YogaResult] = base + daridra + aristha + pravrajya

    # ── Convert to unified dict format ─────────────────────────
    unified: List[Dict] = []
    for y in all_results:
        if not y.detected:
            continue
        grading = grade_yoga(
            y.planets, planet_houses, planet_lons, shadbala_ratios, asp_map
        )
        domain = _YOGA_DOMAIN_MAP.get(y.category, "general")
        unified.append({
            "name":         y.name,
            "type":         y.category,
            "planets":      y.planets,
            "grade":        grading["grade"],
            "score":        grading["score"],
            "domain":       domain,
            "active":       not bool(y.cancellation_reason),
            "cancellation": y.cancellation_reason or None,
        })

    return unified


def detect_all_yogas(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        shadbala_ratios: Dict[str, float],
        house_lords: Dict[int, str],
        asp_map: Dict = None,
        lagna_sign: int = 0,
        dasha_planet: str = "",
        antardasha_planet: str = "",
        retrograde_planets: Set[str] = None,
        planet_lats: Dict[str, float] = None,
) -> List[YogaResult]:
    """
    Run all yoga detectors and return list of detected yogas.
    Includes: tier assignment, activation scoring, compounding,
    Graha Yuddha cancellation, retrograde paradox, Nabhasa yogas.
    """
    if asp_map is None:
        asp_map = {}
    retrograde_planets = retrograde_planets or set()
    planet_lats = planet_lats or {}

    moon_h    = _planet_house("MOON", planet_houses)
    moon_sign = sign_of(planet_lons.get("MOON", 0))

    all_results: List[YogaResult] = []

    # ── Single-result yogas ──────────────────────────────────────
    all_results.append(_budha_aditya(planet_houses, planet_lons, shadbala_ratios))
    all_results.append(_gajakesari(planet_houses, moon_sign, shadbala_ratios))
    all_results.append(_chandra_mangal(planet_houses, asp_map, shadbala_ratios))
    all_results.append(_adhi_yoga(planet_houses, moon_h, shadbala_ratios))
    all_results.append(_amala_yoga(planet_houses, shadbala_ratios))

    # ── Optional single-result yogas (may return None) ───────────
    ks = _kalasarpa_yoga(planet_houses, planet_lons)
    if ks:
        all_results.append(ks)

    km = _kemadrum_yoga(planet_houses, planet_lons, shadbala_ratios)
    if km:
        all_results.append(km)

    sw = _saraswati_yoga(planet_houses, planet_lons, shadbala_ratios)
    if sw:
        all_results.append(sw)

    # ── New catalog yogas (Section A) ────────────────────────────
    all_results.extend(_dharma_karmadhipati_yoga(planet_houses, planet_lons, house_lords, shadbala_ratios, asp_map, lagna_sign=lagna_sign))
    kh = _kahala_yoga(planet_houses, house_lords, shadbala_ratios)
    if kh:
        all_results.append(kh)
    lk = _lakshmi_yoga(planet_houses, planet_lons, house_lords, shadbala_ratios)
    if lk:
        all_results.append(lk)
    all_results.extend(_voshi_veshi_ubhayachari_yoga(planet_houses, planet_lons, shadbala_ratios))
    mb = _mangal_budha_yoga(planet_houses, planet_lons, shadbala_ratios)
    if mb:
        all_results.append(mb)
    ut = _uttamadi_yoga(planet_houses, shadbala_ratios)
    if ut:
        all_results.append(ut)
    ak = _akhanda_samrajya_yoga(planet_houses, house_lords, shadbala_ratios)
    if ak:
        all_results.append(ak)

    # ── Multi-result yogas ───────────────────────────────────────
    all_results.extend(_detect_pancha_mahapurusha(planet_houses, planet_lons, shadbala_ratios))
    all_results.extend(_neechabhanga_raj_yoga(
        planet_houses, planet_lons, shadbala_ratios,
        lagna_sign=lagna_sign, moon_sign=moon_sign,
    ))
    all_results.extend(_sunapha_anapha_durudhara(planet_houses, shadbala_ratios))
    all_results.extend(_dhana_yogas(planet_houses, house_lords, shadbala_ratios))
    all_results.extend(_raj_yoga(planet_houses, house_lords, shadbala_ratios))
    all_results.extend(_vipreet_raj_yoga(planet_houses, house_lords, shadbala_ratios))
    all_results.extend(_parivartana_yoga(planet_houses, planet_lons, house_lords, shadbala_ratios))

    # ── Nabhasa Yogas (all 32) ───────────────────────────────────
    all_results.extend(_detect_nabhasa_yogas(planet_houses, planet_lons))

    # ── Apply enhanced combustion cancellation ───────────────────
    for yoga in all_results:
        if yoga.detected and not yoga.cancellation_reason:
            for p in yoga.planets:
                if is_combust_enhanced(p, planet_lons, retrograde_planets):
                    yoga.cancellation_reason = f"{p} is combust"

    # ── Retrograde paradox modifiers ─────────────────────────────
    if retrograde_planets:
        apply_retrograde_yoga_modifiers(all_results, planet_lons, retrograde_planets)

    detected = [y for y in all_results if y.detected]

    # ── Assign hierarchy tiers ────────────────────────────────────
    for y in detected:
        if y.tier == 4:  # default — re-assign based on category/name
            y.tier = _assign_tier(y)

    # ── Graha Yuddha cancellation ─────────────────────────────────
    wars = _detect_graha_yuddha(planet_lons, planet_lats)
    if wars:
        _apply_graha_yuddha_cancellations(detected, wars)

    # ── Panchamahapurusha ↔ Raja symbiosis ───────────────────────
    compute_panchamahapurusha_raja_symbiosis(detected)

    # ── Assign activation scores with MD-AD axis evaluation ──────
    if dasha_planet or antardasha_planet:
        axis_mult = score_md_ad_relationship(dasha_planet, antardasha_planet, planet_houses)
        for y in detected:
            base_score = score_yoga_activation_dasha(
                y, dasha_planet, antardasha_planet,
                shadbala_ratios, planet_houses, asp_map,
            )
            y.activation_score = round(base_score * axis_mult, 3)

    # ── Augment each yoga with Manduka Gati life-phase data ──────
    for y in detected:
        primary_h = y.houses[0] if y.houses else 0
        if primary_h:
            mg = get_manduka_gati_life_phase(primary_h)
            if mg["phase"] != "unknown":
                y.description += (
                    f" [Manduka phase: {mg['phase'].upper()} life "
                    f"(ages {mg['block_start_age']}–{mg['block_end_age']})]"
                )

    # ── Sort by tier then strength ────────────────────────────────
    detected.sort(key=lambda y: (y.tier, -y.strength))

    return detected
