"""
Phase 3C — Prashna (Vedic Horary) Astrology Computational Framework.

Implements seven domain-specific Prashna sub-modules:
  1. YES/NO oracle — Ithasala (applying) vs Ishrafa (separating) aspect logic
  2. Lost object retrieval — direction matrix + planetary object clues
  3. Medical diagnostic — anatomical house mapping + Tridosha analysis
  4. Legal/litigation — 1st vs 7th lord comparative strength
  5. Travel / return safety — benefic pattern evaluation
  6. Pregnancy — confirmation + gender prediction
  7. Timing matrix — modality × angularity → time unit multiplier

Also includes utility modules:
  - Number-based Prashna (1-108 Kalidas system)
  - Tajika orbs (Deeptamsha) for aspect validity
  - Nakta Yoga (translation of light via Moon/third planet)

Architecture Note: All functions are pure computation.
No prediction weights or domain blending — wiring belongs in engine.py (3F).
Prashna uses its OWN chart (the moment of the query), not the natal chart.

References: Prashna Astrology Computational Framework.md, Prashna Marga
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


# ─── Constants ────────────────────────────────────────────────────────────────

SIGN_NAMES: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Mute (mook) signs — water signs add delay/secrecy to timing
_MUTE_SIGNS = {3, 7, 11}  # Cancer, Scorpio, Pisces (0-indexed)

# Cardinal/Mutable/Fixed signs for timing matrix
_CARDINAL_SIGNS = {0, 3, 6, 9}   # Aries, Cancer, Libra, Capricorn
_MUTABLE_SIGNS  = {2, 5, 8, 11}  # Gemini, Virgo, Sagittarius, Pisces
_FIXED_SIGNS    = {1, 4, 7, 10}  # Taurus, Leo, Scorpio, Aquarius

# Angular houses (Kendras): 1, 4, 7, 10
_ANGULAR_HOUSES   = {1, 4, 7, 10}
# Succedent houses: 2, 5, 8, 11
_SUCCEDENT_HOUSES = {2, 5, 8, 11}
# Cadent houses: 3, 6, 9, 12
_CADENT_HOUSES    = {3, 6, 9, 12}

# Male (odd) signs for gender prediction
_MALE_SIGNS = {0, 2, 4, 6, 8, 10}   # Aries, Gemini, Leo, Libra, Sagittarius, Aquarius

# Tajika Deeptamsha (orbs of influence) — used for Ithasala/Ishrafa
_DEEPTAMSHA: Dict[str, float] = {
    "SUN": 15.0, "MOON": 12.0, "JUPITER": 9.0, "SATURN": 9.0,
    "MARS": 8.0, "MERCURY": 7.0, "VENUS": 7.0,
    "RAHU": 6.0, "KETU": 6.0,
}

# Classic planetary kinematic speed order (fastest → slowest)
_SPEED_ORDER = ["MOON", "MERCURY", "VENUS", "SUN", "MARS", "JUPITER", "SATURN", "RAHU", "KETU"]

# Anatomical house mapping for medical diagnostics
_HOUSE_ANATOMY: Dict[int, str] = {
    1:  "Head / Brain / Cranium",
    2:  "Face / Eyes / Throat / Oral Cavity",
    3:  "Shoulders / Arms / Nervous System",
    4:  "Chest / Lungs / Heart",
    5:  "Upper Stomach / Liver / Spleen",
    6:  "Lower Stomach / Intestines / Kidneys",
    7:  "Groin / Pelvic Region",
    8:  "Reproductive Organs / Excretory System",
    9:  "Thighs / Hips",
    10: "Knees / Joints",
    11: "Calves / Ankles",
    12: "Feet / Lymphatic System",
}

# Tridosha mapping: planet → dosha
_PLANET_DOSHA: Dict[str, str] = {
    "SUN": "Pitta", "MARS": "Pitta",
    "MOON": "Kapha", "VENUS": "Kapha",
    "SATURN": "Vata", "MERCURY": "Vata",
    "JUPITER": "Kapha",
    "RAHU": "Vata", "KETU": "Pitta",
}

# Planetary object associations for lost-object retrieval
_PLANET_OBJECTS: Dict[str, str] = {
    "SUN":     "gold items, government documents, leadership symbols",
    "MOON":    "white items, liquids, silver, perishables, maternal items",
    "MARS":    "sharp objects, metal items, sports equipment, weapons",
    "MERCURY": "books, documents, communication devices, keys, small items",
    "JUPITER": "religious items, gold jewelry, educational material, valuables",
    "VENUS":   "cosmetics, jewelry, luxury items, clothing, entertainment devices",
    "SATURN":  "old/dusty items, dark-colored objects, tools, antiques",
    "RAHU":    "foreign items, technology, unusual or hidden objects",
    "KETU":    "spiritual items, sharp things, ancestral objects",
}


# ─── Tajika Orb Helpers ───────────────────────────────────────────────────────

def _tajika_orb(p1: str, p2: str) -> float:
    """Compute the Tajika functional orb (semi-sum of Deeptamshas) for two planets."""
    d1 = _DEEPTAMSHA.get(p1.upper(), 7.0)
    d2 = _DEEPTAMSHA.get(p2.upper(), 7.0)
    return (d1 + d2) / 2.0


def _aspect_distance(lon1: float, lon2: float) -> float:
    """Minimum arc separation (0–180°) between two longitudes."""
    raw = abs(lon1 - lon2) % 360.0
    return raw if raw <= 180.0 else 360.0 - raw


def _is_faster(p1: str, p2: str) -> bool:
    """Return True if p1 is faster than p2 in the Tajika speed order."""
    i1 = _SPEED_ORDER.index(p1.upper()) if p1.upper() in _SPEED_ORDER else 99
    i2 = _SPEED_ORDER.index(p2.upper()) if p2.upper() in _SPEED_ORDER else 99
    return i1 < i2  # lower index = faster


def _check_ithasala_ishrafa(
    p_fast: str, p_slow: str,
    lon_fast: float, lon_slow: float,
) -> str:
    """
    Return "ithasala" (applying), "ishrafa" (separating), or "none".

    Ithasala: faster planet at lower degree, both within combined Tajika orb,
              and the faster will CATCH the slower (applying).
    Ishrafa:  faster planet already past the slower (separating).
    """
    orb = _tajika_orb(p_fast, p_slow)
    # Compute angular separation assuming trine, conjunction, etc.
    sep = _aspect_distance(lon_fast, lon_slow)

    # Check if within orb distance (at conjunction, 120°, 60°, 180°, 90° angles)
    for aspect_angle in [0.0, 60.0, 90.0, 120.0, 180.0]:
        dev = abs(sep - aspect_angle)
        if dev <= orb:
            # Within orb — is it applying or separating?
            # Applying: faster planet BEHIND slower (will catch up)
            diff = (lon_slow - lon_fast) % 360.0
            if diff <= 180.0:
                return "ithasala"   # faster hasn't caught up yet
            else:
                return "ishrafa"    # faster already passed slower
    return "none"


# ─── Sub-Module 1: YES/NO Oracle (Ithasala/Ishrafa) ─────────────────────────

def evaluate_yes_no(
    lagna_lord: str,
    lagna_lord_lon: float,
    karya_lord: str,
    karya_lord_lon: float,
    moon_lon: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Evaluate YES/NO outcome for a Prashna query using Tajika logic.

    1. Determine which of (lagna_lord, karya_lord) is faster.
    2. Check if they form an Ithasala (applying) or Ishrafa (separating).
    3. If no direct yoga, check for Nakta Yoga via Moon.

    Args:
        lagna_lord:     Planet ruling the Prashna lagna (querent).
        lagna_lord_lon: Its longitude.
        karya_lord:     Planet ruling the house of the query (quesited goal).
        karya_lord_lon: Its longitude.
        moon_lon:       Moon's longitude (for Nakta Yoga check). Optional.

    Returns:
        {
          "verdict":     "YES" | "NO" | "CONDITIONAL_YES" | "UNCERTAIN",
          "yoga":        "ithasala" | "ishrafa" | "nakta" | "none",
          "explanation": str,
          "orb_used":    float,
          "fast_planet": str,
          "slow_planet": str,
        }
    """
    ll = lagna_lord.upper()
    kl = karya_lord.upper()

    # Determine speed order
    if _is_faster(ll, kl):
        fast_p, fast_lon = ll, lagna_lord_lon
        slow_p, slow_lon = kl, karya_lord_lon
    else:
        fast_p, fast_lon = kl, karya_lord_lon
        slow_p, slow_lon = ll, lagna_lord_lon

    yoga = _check_ithasala_ishrafa(fast_p, slow_p, fast_lon, slow_lon)
    orb  = _tajika_orb(fast_p, slow_p)

    if yoga == "ithasala":
        sep = _aspect_distance(fast_lon, slow_lon)
        verdict     = "YES"
        explanation = (f"{fast_p} is applying to {slow_p} within {orb:.1f}° orb "
                       f"(separation {sep:.2f}°). Ithasala = success coming.")
    elif yoga == "ishrafa":
        verdict     = "NO"
        explanation = (f"{fast_p} has already passed {slow_p} (Ishrafa). "
                       f"The opportunity has elapsed. Outcome is failure or past.")
    else:
        # Check Nakta Yoga via Moon
        verdict     = "UNCERTAIN"
        explanation = f"No direct aspect between {ll} and {kl}. "
        yoga        = "none"

        if moon_lon is not None:
            # Moon must form Ithasala with BOTH lagna_lord and karya_lord
            ll_to_moon  = _check_ithasala_ishrafa(
                "MOON", ll, moon_lon, lagna_lord_lon
            ) if _is_faster("MOON", ll) else _check_ithasala_ishrafa(
                ll, "MOON", lagna_lord_lon, moon_lon
            )
            kl_to_moon  = _check_ithasala_ishrafa(
                "MOON", kl, moon_lon, karya_lord_lon
            ) if _is_faster("MOON", kl) else _check_ithasala_ishrafa(
                kl, "MOON", karya_lord_lon, moon_lon
            )
            if "ithasala" in (ll_to_moon, kl_to_moon):
                yoga        = "nakta"
                verdict     = "CONDITIONAL_YES"
                explanation += ("Moon is in Nakta Yoga, translating light between "
                                f"{ll} and {kl}. Goal achieved via third-party intermediary.")

    return {
        "verdict":     verdict,
        "yoga":        yoga,
        "explanation": explanation,
        "orb_used":    orb,
        "fast_planet": fast_p,
        "slow_planet": slow_p,
    }


# ─── Sub-Module 2: Lost Object Retrieval ────────────────────────────────────

def evaluate_lost_object(
    second_lord: str,
    second_lord_house: int,
    second_lord_sign: int,
    moon_sign: int,
    moon_house: int,
    lagna_sign: int,
    malefic_in_7th: bool = False,
    significator_planet: Optional[str] = None,
    significator_retro: bool = False,
) -> Dict[str, Any]:
    """
    Evaluate lost-object recovery probability and location clues.

    Classical rules from Prashna Marga (Chapter on lost/stolen items):
      - 2nd house = movable possessions
      - Moon strong + 2nd lord angular → recoverable
      - 7th house malefic → stolen / gone
      - Significator retrograde → in already-searched location

    Args:
        second_lord:        Planet ruling the 2nd house (possessions).
        second_lord_house:  Which house the 2nd lord occupies.
        second_lord_sign:   Which sign (0-indexed) the 2nd lord occupies.
        moon_sign:          Moon's current sign (0-indexed).
        moon_house:         Moon's current house.
        lagna_sign:         Prashna lagna sign (0-indexed).
        malefic_in_7th:     True if a malefic (Mars/Saturn/Rahu/Ketu) is in 7th.
        significator_planet:Planet most closely tied to the object type (optional).
        significator_retro: True if significator is retrograde.

    Returns:
        {
          "recoverable":     bool,
          "recovery_notes":  list[str],
          "direction":       str,     # compass direction to search
          "environment":     str,     # type of place to search
          "object_clues":    str,     # nature of object (if significator given)
          "retrograde_note": str,
        }
    """
    notes: List[str] = []
    recoverable = True

    # Recovery assessment
    if malefic_in_7th:
        recoverable = False
        notes.append("Malefic in 7th: object likely stolen or permanently gone.")
    elif second_lord_house in _ANGULAR_HOUSES:
        notes.append("2nd lord in angular house: object is nearby and easily recoverable.")
    elif second_lord_house in {6, 8, 12}:
        notes.append("2nd lord in dusthana: recovery is difficult; object hidden or damaged.")
        recoverable = False
    else:
        notes.append("2nd lord in succedent/cadent house: recovery possible with effort.")

    if moon_house in _ANGULAR_HOUSES:
        notes.append("Moon angular: strong indicator for recovery.")
    else:
        notes.append("Moon non-angular: weaker recovery signal.")

    # Direction from element of 2nd lord's sign
    element_idx = second_lord_sign % 4   # 0=Fire, 1=Earth, 2=Air, 3=Water
    direction_map = {0: "East", 1: "South", 2: "West", 3: "North"}
    environment_map = {
        0: "warm places near heat sources, kitchens, sunny areas",
        1: "ground level, storage, garden, basement, floor areas",
        2: "elevated spots, shelves, attic, near windows or ventilation",
        3: "near water, bathroom, kitchen, damp or humid areas",
    }
    direction   = direction_map.get(element_idx, "Unknown")
    environment = environment_map.get(element_idx, "Unknown location")

    # Object clues from significator planet
    object_clues = ""
    if significator_planet:
        object_clues = _PLANET_OBJECTS.get(significator_planet.upper(), "general item")

    # Retrograde note
    retro_note = ""
    if significator_retro:
        retro_note = ("Significator is retrograde: look in places already searched; "
                      "object may return unexpectedly.")

    return {
        "recoverable":     recoverable,
        "recovery_notes":  notes,
        "direction":       direction,
        "environment":     environment,
        "object_clues":    object_clues,
        "retrograde_note": retro_note,
    }


# ─── Sub-Module 3: Medical Diagnostic ────────────────────────────────────────

def evaluate_medical_prashna(
    planet_houses: Dict[str, int],
    planet_signs: Dict[str, int],
    sixth_lord: str,
    sixth_lord_house: int,
    first_lord: str,
    first_lord_house: int,
    eighth_lord: str,
    eighth_lord_house: int,
    malefic_planets: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Evaluate a medical/health Prashna query.

    Analysis:
      - House with most malefic affliction → primary anatomical zone of disease
      - Tridosha from afflicting planets → humoral imbalance type
      - 1st lord vitality vs 8th lord (death) — Ithasala between them = critical

    Args:
        planet_houses:    {planet_name: house_num} for Prashna chart.
        planet_signs:     {planet_name: sign_idx} for Prashna chart.
        sixth_lord:       Planet ruling 6th house (acute illness).
        sixth_lord_house: House occupied by 6th lord.
        first_lord:       Planet ruling 1st house (vitality).
        first_lord_house: House of 1st lord.
        eighth_lord:      Planet ruling 8th house (chronic/death).
        eighth_lord_house:House of 8th lord.
        malefic_planets:  List of natural malefics in the chart (defaults used if None).

    Returns:
        {
          "primary_afflicted_house":   int,
          "anatomical_zone":           str,
          "tridosha_imbalance":        str,   # Pitta/Kapha/Vata
          "vitality_assessment":       str,
          "critical_risk":             bool,
          "house_affliction_scores":   dict,
        }
    """
    if malefic_planets is None:
        malefic_planets = ["MARS", "SATURN", "RAHU", "KETU", "SUN"]

    # Score each house by affliction level
    affliction: Dict[int, int] = {h: 0 for h in range(1, 13)}
    for planet in malefic_planets:
        h = planet_houses.get(planet.upper())
        if h and 1 <= h <= 12:
            affliction[h] += 1

    # 6th lord in angular house amplifies affliction on the house it occupies
    if 1 <= sixth_lord_house <= 12:
        affliction[sixth_lord_house] = affliction.get(sixth_lord_house, 0) + 2

    # Find the most afflicted house
    primary_house = max(affliction, key=lambda k: affliction[k])
    anatomy       = _HOUSE_ANATOMY.get(primary_house, "General body")

    # Tridosha from most-afflicting planet
    afflicting_planets = [p for p in malefic_planets if planet_houses.get(p.upper()) == primary_house]
    dosha_votes: Dict[str, int] = {}
    for p in afflicting_planets:
        d = _PLANET_DOSHA.get(p.upper(), "Vata")
        dosha_votes[d] = dosha_votes.get(d, 0) + 1
    if sixth_lord:
        d = _PLANET_DOSHA.get(sixth_lord.upper(), "Pitta")
        dosha_votes[d] = dosha_votes.get(d, 0) + 1
    tridosha = max(dosha_votes, key=dosha_votes.get) if dosha_votes else "Vata"

    # Vitality: 1st lord in angular house → strong
    vitality = "Strong" if first_lord_house in _ANGULAR_HOUSES else "Moderate"
    if first_lord_house in {6, 8, 12}:
        vitality = "Weak"

    # Critical risk: 8th lord in 1st (or angular), or 1st lord in 8th
    critical = (eighth_lord_house == first_lord_house or
                (eighth_lord_house in _ANGULAR_HOUSES and first_lord_house in {6, 8, 12}))

    return {
        "primary_afflicted_house": primary_house,
        "anatomical_zone":         anatomy,
        "tridosha_imbalance":      tridosha,
        "vitality_assessment":     vitality,
        "critical_risk":           critical,
        "house_affliction_scores": dict(affliction),
    }


# ─── Sub-Module 4: Legal / Litigation ────────────────────────────────────────

def evaluate_legal_prashna(
    first_lord: str,
    first_lord_house: int,
    first_lord_strength: float,
    seventh_lord: str,
    seventh_lord_house: int,
    seventh_lord_strength: float,
    sixth_lord_house: int,
    sixth_lord_aspected_by_malefic: bool = False,
    first_sixth_exchange: bool = False,
) -> Dict[str, Any]:
    """
    Evaluate a legal/litigation Prashna query.

    Querent = 1st house. Opponent = 7th house. Litigation = 6th house.

    Classical rule: If 1st lord stronger + in angular house → querent wins.
    6th lord in kendra aspected by malefic → prolonged trouble.
    1st/6th exchange → deep entanglement in legal system.

    Args:
        first_lord:                   Name of 1st house lord.
        first_lord_house:             House occupied by 1st lord.
        first_lord_strength:          Numerical strength (e.g., shadbala ratio or panchavargeeya).
        seventh_lord:                 Name of 7th house lord.
        seventh_lord_house:           House of 7th lord.
        seventh_lord_strength:        Numerical strength.
        sixth_lord_house:             House of 6th lord.
        sixth_lord_aspected_by_malefic: True if malefic aspects the 6th lord.
        first_sixth_exchange:         True if 1st and 6th lords exchange signs (parivartana).

    Returns:
        {
          "verdict":         "QUERENT_WINS" | "OPPONENT_WINS" | "PROLONGED" | "ENTANGLED",
          "confidence":      float (0-1),
          "explanation":     str,
          "warnings":        list[str],
        }
    """
    warnings: List[str] = []
    querent_stronger = first_lord_strength > seventh_lord_strength
    querent_angular  = first_lord_house in _ANGULAR_HOUSES

    # Base verdict
    if querent_stronger and querent_angular:
        verdict    = "QUERENT_WINS"
        confidence = min(0.90, 0.6 + (first_lord_strength - seventh_lord_strength) * 0.1)
    elif not querent_stronger:
        verdict    = "OPPONENT_WINS"
        confidence = min(0.90, 0.5 + (seventh_lord_strength - first_lord_strength) * 0.1)
    else:
        verdict    = "PROLONGED"
        confidence = 0.45

    # Overrides / modifiers
    if first_sixth_exchange:
        verdict    = "ENTANGLED"
        confidence = 0.3
        warnings.append("Parivartana between 1st and 6th lords: courts trap, legal entanglement likely.")

    if sixth_lord_house in _ANGULAR_HOUSES and sixth_lord_aspected_by_malefic:
        warnings.append("6th lord in kendra aspected by malefic: severe prolonged trouble from enemies.")
        if verdict == "QUERENT_WINS":
            confidence -= 0.15
            verdict = "PROLONGED"

    explanation = (f"{first_lord} (querent, strength {first_lord_strength:.2f}, "
                   f"house {first_lord_house}) vs {seventh_lord} "
                   f"(opponent, strength {seventh_lord_strength:.2f}, "
                   f"house {seventh_lord_house}). Verdict: {verdict}.")

    return {
        "verdict":     verdict,
        "confidence":  round(max(0.0, min(1.0, confidence)), 3),
        "explanation": explanation,
        "warnings":    warnings,
    }


# ─── Sub-Module 5: Travel / Return Safety ────────────────────────────────────

def evaluate_travel_prashna(
    lagna_lord_house: int,
    seventh_house_has_malefic: bool,
    moon_house: int,
    second_lord_house: int,
    fourth_lord_house: int,
    lagna_sign: int,
    lagna_sign_modality: str,  # "cardinal"|"fixed"|"mutable"
) -> Dict[str, Any]:
    """
    Evaluate travel safety / return timing for a Prashna query.

    Rules from Prashna Marga:
      - Benefics in 2nd/3rd/5th AND Lagna lord Ithasala with angular planet → safe return
      - Malefics in 7th OR Fixed lagna under malefic aspect → no return / severe delay
      - Moon and Lagna lord in same sign + trikona → quick return

    Args:
        lagna_lord_house:         House of 1st lord.
        seventh_house_has_malefic:True if malefic occupies 7th house.
        moon_house:               Moon's house.
        second_lord_house:        2nd lord's house.
        fourth_lord_house:        4th lord's house (home base).
        lagna_sign:               Prashna lagna sign index (0-indexed).
        lagna_sign_modality:      "cardinal", "fixed", or "mutable".

    Returns:
        {
          "verdict":        "SAFE_RETURN" | "DELAYED" | "NO_RETURN",
          "timing_hint":    str,
          "explanation":    str,
        }
    """
    if seventh_house_has_malefic:
        return {
            "verdict":      "NO_RETURN",
            "timing_hint":  "Indefinite delay or non-return.",
            "explanation":  "Malefic in 7th house: traveler is stuck or the journey ends adversely.",
        }

    if lagna_sign_modality == "fixed" and seventh_house_has_malefic:
        return {
            "verdict":      "NO_RETURN",
            "timing_hint":  "Anchored away from home base.",
            "explanation":  "Fixed sign lagna under malefic pressure: traveler cannot leave far location.",
        }

    # Favourable indicators
    score = 0
    if lagna_lord_house in _ANGULAR_HOUSES:
        score += 2
    if moon_house in {2, 3, 5}:
        score += 1
    if second_lord_house in _ANGULAR_HOUSES:
        score += 1
    if fourth_lord_house in _ANGULAR_HOUSES:
        score += 1

    if score >= 3:
        timing = "Return expected within near term (days to weeks)."
        verdict = "SAFE_RETURN"
    elif score >= 1:
        timing = "Return delayed; within months."
        verdict = "DELAYED"
    else:
        timing = "Long delay or uncertain return."
        verdict = "DELAYED"

    return {
        "verdict":      verdict,
        "timing_hint":  timing,
        "explanation":  f"Travel score: {score}/5. {'Favorable indicators present.' if score >= 3 else 'Mixed signals.'}",
    }


# ─── Sub-Module 6: Pregnancy Prashna ─────────────────────────────────────────

def evaluate_pregnancy_prashna(
    fifth_lord: str,
    fifth_lord_house: int,
    moon_house: int,
    moon_sign: int,
    lagna_lord_house: int,
    fifth_house_has_malefic: bool,
    fifth_lord_retro: bool,
    fifth_house_sign: int,
) -> Dict[str, Any]:
    """
    Evaluate pregnancy confirmation and gender prediction for a Prashna query.

    Classical rules:
      - Confirmation: Moon + Lagna lord in 5th, or Ithasala from angular house.
      - Gender: Sign of 5th lord/Moon/Lagna → male (odd) or female (even).
      - Risk: Malefic in 5th OR 5th lord retrograde → complications.

    Args:
        fifth_lord:              Planet ruling the 5th house.
        fifth_lord_house:        House occupied by 5th lord.
        moon_house:              Moon's house.
        moon_sign:               Moon's sign (0-indexed).
        lagna_lord_house:        House of 1st lord.
        fifth_house_has_malefic: True if a malefic is in the 5th house.
        fifth_lord_retro:        True if 5th lord is retrograde.
        fifth_house_sign:        Sign of 5th house cusp (0-indexed).

    Returns:
        {
          "pregnancy_confirmed": bool,
          "gender_prediction":   "MALE" | "FEMALE" | "UNCERTAIN",
          "complication_risk":   bool,
          "explanation":         str,
        }
    """
    # Confirmation
    confirmed = False
    explanation_parts: List[str] = []

    if moon_house == 5 and lagna_lord_house == 5:
        confirmed = True
        explanation_parts.append("Moon and Lagna lord conjunct in 5th: strong pregnancy indicator.")
    elif moon_house in _ANGULAR_HOUSES and lagna_lord_house in _ANGULAR_HOUSES:
        confirmed = True
        explanation_parts.append("Both Moon and Lagna lord in angular houses: Ithasala confirmed.")
    elif fifth_lord_house in _ANGULAR_HOUSES:
        confirmed = True
        explanation_parts.append("5th lord strong in angular house: pregnancy likely.")
    else:
        explanation_parts.append("Weak indicators; pregnancy not confirmed this cycle.")

    # Gender: majority of male/female sign indicators
    votes = [moon_sign, fifth_house_sign]
    if fifth_lord_house:
        # sign of the house the 5th lord is in
        pass  # not enough info; use available
    male_votes   = sum(1 for s in votes if s in _MALE_SIGNS)
    female_votes = len(votes) - male_votes
    if male_votes > female_votes:
        gender = "MALE"
    elif female_votes > male_votes:
        gender = "FEMALE"
    else:
        gender = "UNCERTAIN"

    # Complication risk
    complication = fifth_house_has_malefic or fifth_lord_retro
    if complication:
        explanation_parts.append("Malefic in 5th or retrograde 5th lord: complication risk present.")

    return {
        "pregnancy_confirmed": confirmed,
        "gender_prediction":   gender,
        "complication_risk":   complication,
        "explanation":         " ".join(explanation_parts),
    }


# ─── Sub-Module 7: Timing Matrix ─────────────────────────────────────────────

def compute_prashna_timing(
    degrees_to_perfection: float,
    significator_sign: int,
    significator_house: int,
    is_retrograde: bool = False,
    is_mute_sign: bool = False,
) -> Dict[str, Any]:
    """
    Convert orbital degrees to a human time unit using the Modality-House matrix.

    Formula: Time = degrees_to_perfection × time_unit

    Matrix:
      Cardinal sign + Angular house → Days
      Mutable sign + Succedent house → Weeks
      Fixed sign + Cadent house → Years
      Mixed → intermediate (Months)

    Retrograde: halves the time estimate (sudden acceleration).
    Mute sign: doubles the time estimate (delay/secrecy).

    Args:
        degrees_to_perfection:   Exact degrees remaining until the aspect perfects.
        significator_sign:       Sign index of the primary significator (0–11).
        significator_house:      House of the primary significator (1–12).
        is_retrograde:           True if the applying planet is retrograde.
        is_mute_sign:            True if in a mute (water) sign. Auto-detected if not given.

    Returns:
        {
          "quantity":   float,
          "unit":       str  ("days" | "weeks" | "months" | "years"),
          "label":      str  (human-readable result),
          "modality":   str,
          "house_type": str,
          "notes":      list[str],
        }
    """
    notes: List[str] = []

    # Sign modality
    if significator_sign in _CARDINAL_SIGNS:
        modality = "cardinal"
    elif significator_sign in _MUTABLE_SIGNS:
        modality = "mutable"
    else:
        modality = "fixed"

    # House type
    if significator_house in _ANGULAR_HOUSES:
        house_type = "angular"
    elif significator_house in _SUCCEDENT_HOUSES:
        house_type = "succedent"
    else:
        house_type = "cadent"

    # Determine unit
    if modality == "cardinal" and house_type == "angular":
        unit  = "days"
    elif modality == "mutable" and house_type in ("succedent", "angular"):
        unit  = "weeks"
    elif modality == "fixed" and house_type == "cadent":
        unit  = "years"
    elif house_type == "cadent":
        unit  = "months"
    else:
        unit  = "months"   # default intermediate

    # Convert weeks/years to base quantity
    qty = round(degrees_to_perfection, 2)

    # Modifiers
    if is_retrograde:
        qty = round(qty * 0.5, 2)
        notes.append("Retrograde planet: timing halved (sudden event).")

    auto_mute = significator_sign in _MUTE_SIGNS
    if is_mute_sign or auto_mute:
        qty = round(qty * 2.0, 2)
        notes.append("Mute sign (Cancer/Scorpio/Pisces): timing doubled due to hidden factors.")

    label = f"Approximately {qty} {unit}"

    return {
        "quantity":   qty,
        "unit":       unit,
        "label":      label,
        "modality":   modality,
        "house_type": house_type,
        "notes":      notes,
    }


# ─── Number-Based Prashna (1-108 Kalidas System) ─────────────────────────────

def compute_number_prashna(number: int) -> Dict[str, Any]:
    """
    Convert a 1–108 Prashna number to an astrological lagna using the Kalidas method.

    The zodiac = 12 signs × 9 Navamsas = 108 divisions.
    quotient = (number - 1) // 9 → rising sign (0-indexed)
    remainder = (number - 1) %  9 → Navamsa within that sign (0-indexed)

    Args:
        number: Integer from 1 to 108 (inclusive).

    Returns:
        {
          "input_number":   int,
          "rising_sign":    int (0=Aries…11=Pisces),
          "rising_sign_name": str,
          "navamsa_number": int (1-9 within the sign),
          "navamsa_degree_start": float,  # start degree within sign
          "lagna_longitude":      float,  # approximate ASC longitude
        }
    """
    n = max(1, min(108, number))
    idx = n - 1
    sign_idx   = idx // 9
    navamsa    = idx %  9
    # Each navamsa = 30° / 9 = 3.333...° within the sign
    deg_start  = navamsa * (30.0 / 9.0)
    asc_lon    = sign_idx * 30.0 + deg_start + (30.0 / 9.0) / 2.0  # midpoint of navamsa

    return {
        "input_number":        n,
        "rising_sign":         sign_idx,
        "rising_sign_name":    SIGN_NAMES[sign_idx],
        "navamsa_number":      navamsa + 1,
        "navamsa_degree_start": round(deg_start, 4),
        "lagna_longitude":     round(asc_lon % 360.0, 4),
    }
