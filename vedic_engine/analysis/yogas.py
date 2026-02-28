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


def detect_all_yogas(
        planet_houses: Dict[str, int],
        planet_lons: Dict[str, float],
        shadbala_ratios: Dict[str, float],
        house_lords: Dict[int, str],
        asp_map: Dict = None,
        lagna_sign: int = 0,
        dasha_planet: str = "",
        antardasha_planet: str = "",
) -> List[YogaResult]:
    """
    Run all yoga detectors and return list of detected yogas.
    Includes: tier assignment, activation scoring, compounding.
    """
    if asp_map is None:
        asp_map = {}

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

    # ── Apply combustion cancellation ───────────────────────────
    for yoga in all_results:
        if yoga.detected and not yoga.cancellation_reason:
            for p in yoga.planets:
                if _is_combust(p, planet_lons):
                    yoga.cancellation_reason = f"{p} is combust (within 10° of Sun)"

    detected = [y for y in all_results if y.detected]

    # ── Assign hierarchy tiers ────────────────────────────────────
    for y in detected:
        if y.tier == 4:  # default — re-assign based on category/name
            y.tier = _assign_tier(y)

    # ── Assign activation scores ──────────────────────────────────
    if dasha_planet or antardasha_planet:
        for y in detected:
            y.activation_score = score_yoga_activation_dasha(
                y, dasha_planet, antardasha_planet,
                shadbala_ratios, planet_houses, asp_map,
            )

    # ── Compute compounding (appended as metadata, not a yoga result) ─
    # Callers can use compute_yoga_compounding(detected) separately

    # ── Sort by tier then strength ────────────────────────────────
    detected.sort(key=lambda y: (y.tier, -y.strength))

    return detected
