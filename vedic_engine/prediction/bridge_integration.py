"""
Phase 6 L3 — Bridge Cross-Validation & Integration
═══════════════════════════════════════════════════

Consumes PyJHora and VedAstro bridge data stored in
    computed["pyjhora"]   (Dict from compute_all_pyjhora)
    computed["vedastro"]  (Dict from compute_all_vedastro)

Integration principles (backed by the 6 research files):
  • Cross-validated data increases confidence  (RF1 §agreement)
  • Unconfirmed bridge-only yogas use 30% dormant weight  (RF4 §dormant)
  • VedAstro pre-computed predictions serve as independent Bayesian evidence
  • Bridge disagreement triggers conservative estimate (lower value wins)
  • Net modifier is multiplicative and bounded to [0.88, 1.15] so bridges
    can never wildly over-ride the core research pipeline.
"""
from __future__ import annotations

import logging
import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


def _yoga_name_forms(name: str) -> Set[str]:
    """Generate multiple normalised forms of a yoga name for fuzzy matching.

    E.g. "Gaja_Kesari_Yoga" → {"gajakesariyoga", "gajakesari", "gaja kesari"}
    """
    forms: Set[str] = set()
    if not name:
        return forms
    low = name.lower().strip()
    # Form 1: spaces normalised
    spaced = re.sub(r"[_\-]+", " ", low).strip()
    if spaced:
        forms.add(spaced)
    # Form 2: all separators removed (compound)
    collapsed = re.sub(r"[\s_\-]+", "", low)
    if collapsed:
        forms.add(collapsed)
    # Form 3: remove trailing "yoga"/"yog" suffix
    for suffix in ("yoga", "yog"):
        if collapsed.endswith(suffix) and len(collapsed) > len(suffix) + 2:
            forms.add(collapsed[:-len(suffix)])
        s2 = spaced.rstrip()
        if s2.endswith(" " + suffix):
            forms.add(s2[:-(len(suffix) + 1)].strip())
    return forms


# ══════════════════════════════════════════════════════════════════════
# 1. YOGA CROSS-VALIDATION  (Research File 4)
# ══════════════════════════════════════════════════════════════════════

def cross_validate_yogas(
    our_yogas: list,
    pyjhora: Dict[str, Any],
    domain: str,
) -> Dict[str, Any]:
    """
    Compare our yoga list with PyJHora's independently-detected yogas.

    Confirmed (both detect) → +2% per yoga, cap +10%.
    Extra PyJHora-only       → +0.6% per (30% dormant effect, RF4), cap +3%.
    """
    empty = {"available": False, "yoga_cross_boost": 0.0}
    if not isinstance(pyjhora, dict) or not pyjhora.get("available"):
        return empty

    pj_yogas = pyjhora.get("yogas")
    if not isinstance(pj_yogas, dict):
        return empty

    # ── Our yoga names (normalised — multiple forms for matching)
    our_names: set = set()
    our_name_map: Dict[str, str] = {}  # canonical → original
    for y in (our_yogas or []):
        name = ""
        if isinstance(y, dict):
            name = y.get("name", "")
        else:
            name = getattr(y, "name", "")
        for form in _yoga_name_forms(str(name)):
            our_names.add(form)
            our_name_map[form] = str(name)

    # ── PyJHora yoga names (non-null results = detected)
    pj_names: set = set()
    for key, val in pj_yogas.items():
        if val is not None and val not in (False, [], {}, 0, ""):
            for form in _yoga_name_forms(str(key)):
                pj_names.add(form)

    confirmed = our_names & pj_names
    extra_pj  = pj_names - our_names

    confirmed_boost = min(0.10, len(confirmed) * 0.02)
    extra_boost     = min(0.03, len(extra_pj)  * 0.006)
    total           = round(confirmed_boost + extra_boost, 4)

    return {
        "available": True,
        "confirmed_count": len(confirmed),
        "confirmed_yogas": sorted(confirmed)[:10],
        "extra_pj_count": len(extra_pj),
        "confirmed_boost": round(confirmed_boost, 4),
        "extra_boost": round(extra_boost, 4),
        "yoga_cross_boost": total,
    }


# ══════════════════════════════════════════════════════════════════════
# 2. VEDASTRO PREDICTION DOMAIN SCORING  (Research File 2)
# ══════════════════════════════════════════════════════════════════════

# Map VedAstro prediction tags → engine domains
_TAG_DOMAIN: Dict[str, str] = {
    # Career
    "Career": "career", "Profession": "career", "Government": "career",
    "Authority": "career", "Fame": "career", "Leadership": "career",
    "Power": "career", "Status": "career", "Business": "career",
    "Education": "career",
    # Finance
    "Finance": "finance", "Wealth": "finance", "Property": "finance",
    "Income": "finance", "Money": "finance", "Gains": "finance",
    "Prosperity": "finance", "Lottery": "finance",
    # Marriage
    "Marriage": "marriage", "Relationship": "marriage", "Partner": "marriage",
    "Spouse": "marriage", "Love": "marriage", "Romance": "marriage",
    "Children": "marriage", "Family": "marriage",
    # Health
    "Health": "health", "Disease": "health", "Longevity": "health",
    "Body": "health", "Mind": "health", "Medical": "health",
    "MedicalAstrology": "health", "Accident": "health", "Death": "health",
    "Danger": "health",
}


def extract_vedastro_domain_score(
    vedastro: Dict[str, Any],
    domain: str,
) -> Dict[str, Any]:
    """
    Extract domain-relevant VedAstro predictions and compute a
    weighted favourability score (0.0–1.0).

    Each prediction has:  name, description, weight, accuracy, tags
    """
    empty = {"available": False, "vedastro_domain_score": 0.5, "count": 0}
    if not isinstance(vedastro, dict) or not vedastro.get("available"):
        return empty

    predictions = vedastro.get("predictions")
    if not isinstance(predictions, list) or not predictions:
        return empty

    domain_lower = domain.lower()
    relevant: List[Dict] = []

    for pred in predictions:
        if not isinstance(pred, dict):
            continue
        tags = pred.get("tags", [])
        if not isinstance(tags, (list, tuple)):
            continue
        # Check if any tag maps to the requested domain
        for tag in tags:
            tag_str = str(tag).strip()
            mapped = _TAG_DOMAIN.get(tag_str)
            if mapped == domain_lower:
                relevant.append(pred)
                break

    if not relevant:
        return empty

    # VedAstro predictions may have weight=0 (binary presence indicators).
    # Use two strategies: weighted (if weights exist) or count-based.
    total_weight = 0.0
    weighted_sum = 0.0
    for pred in relevant:
        w = max(float(pred.get("weight", 0) or 0), 0.0)
        a = max(float(pred.get("accuracy", 0) or 0), 0.0)
        if w > 0:
            total_weight += w
            weighted_sum += w * min(a / 100.0, 1.0)

    if total_weight > 0:
        # Weighted approach
        score = weighted_sum / total_weight
    else:
        # Count-based: ratio of domain predictions to total predictions
        # More relevant predictions = higher domain signal
        all_count = max(len(predictions), 1)
        # Normalise: baseline is ~5% of predictions matching any given domain
        # If 10%+ match → positive signal; if <2% → negative signal
        ratio = len(relevant) / all_count
        score = min(1.0, max(0.0, 0.5 + (ratio - 0.05) * 5.0))

    return {
        "available": True,
        "vedastro_domain_score": round(min(1.0, max(0.0, score)), 4),
        "count": len(relevant),
        "total_predictions": len(predictions),
        "total_weight": round(total_weight, 2),
        "relevant_names": [p.get("name", "?") for p in relevant[:8]],
    }


# ══════════════════════════════════════════════════════════════════════
# 3. DASHA CROSS-VALIDATION  (Research File 5)
# ══════════════════════════════════════════════════════════════════════

# VedAstro uses full English planet names; our engine uses uppercase abbreviations.
_VA_PLANET_MAP: Dict[str, str] = {
    "sun": "SUN", "moon": "MOON", "mars": "MARS", "mercury": "MERCURY",
    "jupiter": "JUPITER", "venus": "VENUS", "saturn": "SATURN",
    "rahu": "RAHU", "ketu": "KETU",
}


def cross_validate_dasha(
    our_dasha_planet: str,
    vedastro: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Check if VedAstro's current dasha lord matches ours.

    Agreement → +2% confidence boost.
    """
    empty = {"available": False, "dasha_match": False, "boost": 0.0}
    if not isinstance(vedastro, dict) or not vedastro.get("available"):
        return empty

    dasa_now = vedastro.get("dasa_now")
    if dasa_now is None:
        return empty

    # VedAstro dasa_now formats:
    #   1. Dict with planet-name keys: {'Ketu': {'Type': 'Dasa', ...}}
    #   2. Dict with 'lord'/'planet' key
    #   3. List of period dicts
    va_lord = ""
    if isinstance(dasa_now, dict):
        # Format 1: planet name as top-level key
        for key in dasa_now:
            mapped = _VA_PLANET_MAP.get(key.strip().lower())
            if mapped:
                va_lord = mapped
                break
        # Format 2: explicit lord/planet key
        if not va_lord:
            for key in ("lord", "planet", "mahadasha", "dasha_lord", "Lord", "Planet"):
                val = dasa_now.get(key)
                if val:
                    va_lord = str(val).strip().lower()
                    va_lord = _VA_PLANET_MAP.get(va_lord, va_lord.upper())
                    break
        # Format 3: nested levels
        if not va_lord and isinstance(dasa_now.get("levels"), list):
            levels = dasa_now["levels"]
            if levels and isinstance(levels[0], dict):
                val = str(levels[0].get("lord", levels[0].get("planet", ""))).strip().lower()
                va_lord = _VA_PLANET_MAP.get(val, val.upper())
    elif isinstance(dasa_now, list) and dasa_now:
        first = dasa_now[0]
        if isinstance(first, dict):
            val = str(first.get("lord", first.get("planet", ""))).strip().lower()
            va_lord = _VA_PLANET_MAP.get(val, val.upper())
        elif isinstance(first, str):
            va_lord = _VA_PLANET_MAP.get(first.strip().lower(), first.strip().upper())

    if not va_lord:
        return empty

    mapped = _VA_PLANET_MAP.get(va_lord, va_lord.upper())
    match = mapped == our_dasha_planet.upper()

    return {
        "available": True,
        "vedastro_lord": mapped,
        "our_lord": our_dasha_planet.upper(),
        "dasha_match": match,
        "boost": 0.02 if match else 0.0,
    }


# ══════════════════════════════════════════════════════════════════════
# 4. DOSHA CROSS-VALIDATION  (Research File 3)
# ══════════════════════════════════════════════════════════════════════

def cross_validate_doshas(
    our_doshas: Dict[str, Any],
    pyjhora: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Cross-validate dosha detection between our engine and PyJHora.

    If both independently detect the same dosha, confidence in the
    override trigger increases.
    """
    empty = {"available": False, "confirmed": [], "dosha_boost": 0.0}
    if not isinstance(pyjhora, dict) or not pyjhora.get("available"):
        return empty

    pj_doshas = pyjhora.get("doshas")
    if not isinstance(pj_doshas, dict):
        return empty

    confirmed: List[str] = []

    # Kala Sarpa
    our_ks = our_doshas.get("kala_sarpa", {})
    pj_ks  = pj_doshas.get("kala_sarpa")
    our_ks_active = bool(
        (isinstance(our_ks, dict) and our_ks.get("active", our_ks.get("present", False)))
        or (isinstance(our_ks, bool) and our_ks)
    )
    pj_ks_active = bool(pj_ks is not None and pj_ks not in (False, [], {}, 0, ""))
    if our_ks_active and pj_ks_active:
        confirmed.append("kala_sarpa")

    # Manglik
    our_mg = our_doshas.get("manglik", {})
    pj_mg  = pj_doshas.get("manglik")
    our_mg_active = bool(
        (isinstance(our_mg, dict) and our_mg.get("active", our_mg.get("present", False)))
        or (isinstance(our_mg, bool) and our_mg)
    )
    pj_mg_active = bool(pj_mg is not None and pj_mg not in (False, [], {}, 0, ""))
    if our_mg_active and pj_mg_active:
        confirmed.append("manglik")

    # Shrapit
    pj_sh = pj_doshas.get("shrapit")
    our_sh = our_doshas.get("shrapit", {})
    our_sh_active = bool(
        (isinstance(our_sh, dict) and our_sh.get("active", our_sh.get("present", False)))
        or (isinstance(our_sh, bool) and our_sh)
    )
    pj_sh_active = bool(pj_sh is not None and pj_sh not in (False, [], {}, 0, ""))
    if our_sh_active and pj_sh_active:
        confirmed.append("shrapit")

    # Pitru dosha — PyJHora may include in all_dosha_details
    pj_all = pj_doshas.get("all_dosha_details")
    if isinstance(pj_all, (list, dict)):
        our_pitru = our_doshas.get("pitru", {})
        our_pitru_active = bool(
            (isinstance(our_pitru, dict) and our_pitru.get("active", our_pitru.get("present", False)))
            or (isinstance(our_pitru, bool) and our_pitru)
        )
        # Look for pitru-related entries in PyJHora results
        if our_pitru_active:
            pitru_found = False
            if isinstance(pj_all, dict):
                for k, v in pj_all.items():
                    if "pitru" in str(k).lower() or "pitr" in str(k).lower():
                        if v not in (None, False, [], {}, 0, ""):
                            pitru_found = True
                            break
            elif isinstance(pj_all, list):
                for item in pj_all:
                    s = str(item).lower()
                    if "pitru" in s or "pitr" in s:
                        pitru_found = True
                        break
            if pitru_found:
                confirmed.append("pitru")

    # Each confirmed dosha adds +1.5% (they're strong classical signals)
    boost = round(min(0.06, len(confirmed) * 0.015), 4)

    return {
        "available": True,
        "confirmed": confirmed,
        "confirmed_count": len(confirmed),
        "dosha_boost": boost,
    }


# ══════════════════════════════════════════════════════════════════════
# 5. PYJHORA STRENGTH DATA EXTRACTION  (Research File 1)
# ══════════════════════════════════════════════════════════════════════

def extract_pyjhora_harsha_bala(
    pyjhora: Dict[str, Any],
    planet: str,
) -> Dict[str, Any]:
    """
    Extract PyJHora's Harsha Bala (or Shadbala fallback) for a planet.
    Returns a quality signal [0,1].
    """
    empty = {"available": False, "harsha_score": 0.5}
    if not isinstance(pyjhora, dict) or not pyjhora.get("available"):
        return empty

    strengths = pyjhora.get("strengths", {})
    if not isinstance(strengths, dict):
        return empty

    _PLANET_ORDER = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]
    p_upper = planet.upper()

    # Try harsha_bala first
    harsha = strengths.get("harsha_bala")
    score = _extract_planet_score(harsha, p_upper, _PLANET_ORDER)

    if score is not None:
        try:
            raw = float(score)
            normalised = min(1.0, max(0.0, raw / 60.0)) if raw >= 0 else 0.0
            return {"available": True, "raw": raw, "harsha_score": round(normalised, 4), "source": "harsha_bala"}
        except (TypeError, ValueError):
            pass

    # Fallback: shad_bala — normalise differently (virupas, typical range 100-300)
    shad = strengths.get("shad_bala")
    score = _extract_planet_score(shad, p_upper, _PLANET_ORDER)
    if score is not None:
        try:
            raw = float(score)
            # PyJHora shad_bala is in virupas; 60 virupas = 1 rupa
            # Minimum required varies by planet (~300 virupas for Sun/Jupiter)
            # Normalise: 150 virupas = 0.5, 300 = 1.0
            normalised = min(1.0, max(0.0, raw / 300.0)) if raw >= 0 else 0.0
            return {"available": True, "raw": raw, "harsha_score": round(normalised, 4), "source": "shad_bala"}
        except (TypeError, ValueError):
            pass

    return empty


def _extract_planet_score(data, p_upper: str, planet_order: list):
    """Extract a planet's numeric score from various PyJHora formats.

    Handles:
      - Dict keyed by planet name: {"SATURN": 10}
      - Dict keyed by int index: {6: 10}  (PyJHora convention: 0=Sun..6=Saturn)
      - Flat list: [v0, v1, ..., v6]
      - Nested list: [[totals], [comp1], ...] → take first sub-list
      - List of pairs: [["Sun", 10], ...]
    """
    if data is None:
        return None

    if isinstance(data, dict):
        # Dict keyed by planet name (string)
        for key in (p_upper, p_upper.capitalize(), p_upper.lower()):
            val = data.get(key)
            if val is not None:
                return val
        # Dict keyed by integer index (PyJHora convention)
        try:
            idx = planet_order.index(p_upper)
            val = data.get(idx)
            if val is not None:
                return val
        except ValueError:
            pass
        return None

    if isinstance(data, (list, tuple)):
        # Flat list indexed by planet order: [val_sun, val_moon, ...]
        if data and isinstance(data[0], (int, float)):
            try:
                idx = planet_order.index(p_upper)
                if idx < len(data):
                    return data[idx]
            except ValueError:
                pass
        # Nested list of lists: [[totals], [comp1], ...] → first sub-list = totals
        if data and isinstance(data[0], (list, tuple)):
            first_row = data[0]
            if first_row and isinstance(first_row[0], (int, float)):
                try:
                    idx = planet_order.index(p_upper)
                    if idx < len(first_row):
                        return first_row[idx]
                except ValueError:
                    pass
            # List of name-value pairs: [["Sun", 10], ...]
            for item in first_row:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    if str(item[0]).upper().strip() == p_upper:
                        return item[1]
    return None


# ══════════════════════════════════════════════════════════════════════
# 6. PYJHORA ASHTAKAVARGA CROSS-CHECK  (Research File 6)
# ══════════════════════════════════════════════════════════════════════

def cross_validate_ashtakavarga(
    our_av: Dict[str, Any],
    pyjhora: Dict[str, Any],
    domain_houses: List[int],
) -> Dict[str, Any]:
    """
    Compare Sarvashtakavarga scores for domain houses between our
    engine and PyJHora.  Agreement → small boost.
    """
    empty = {"available": False, "av_boost": 0.0}
    if not isinstance(pyjhora, dict) or not pyjhora.get("available"):
        return empty

    pj_av = pyjhora.get("ashtakavarga", {})
    if not isinstance(pj_av, dict):
        return empty

    # Our SAV: static["ashtakvarga"]["sarva"] — typically list of 12 ints
    our_sarva = None
    if isinstance(our_av, dict):
        our_sarva = our_av.get("sarva", our_av.get("sav"))

    # PyJHora's ashtakavarga → bav_sav_prastara (complex nested structure)
    pj_bav_sav = pj_av.get("bav_sav_prastara")
    # Can't reliably parse without knowing exact PyJHora version format.
    # Use presence of matching high/low signals instead.
    if our_sarva is None or not isinstance(our_sarva, (list, tuple)):
        return empty
    if len(our_sarva) < 12:
        return empty

    # Check strength of domain houses (>= 28 = strong, < 25 = weak)
    strong_count = 0
    for h in domain_houses:
        idx = (h - 1) % 12
        if idx < len(our_sarva):
            val = our_sarva[idx]
            if isinstance(val, (int, float)) and val >= 28:
                strong_count += 1

    # If PyJHora AV exists at all, it's an additional data point
    pj_exists = pj_bav_sav is not None and pj_bav_sav not in ([], {}, None)
    av_boost = 0.01 if (strong_count > 0 and pj_exists) else 0.0

    return {
        "available": bool(pj_exists),
        "strong_domain_houses": strong_count,
        "av_boost": round(av_boost, 4),
    }


# ══════════════════════════════════════════════════════════════════════
# 7. VEDASTRO PLANET DATA CROSS-CHECK
# ══════════════════════════════════════════════════════════════════════

def extract_vedastro_planet_dignity(
    vedastro: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Extract Sun and Moon dignity/sign data from VedAstro for cross-validation.
    VedAstro's planet data contains sign, house, and dignity information.
    """
    result: Dict[str, Any] = {"available": False}
    if not isinstance(vedastro, dict) or not vedastro.get("available"):
        return result

    for key in ("sun_data", "moon_data"):
        data = vedastro.get(key)
        if isinstance(data, dict):
            result["available"] = True
            result[key] = {
                "sign": data.get("SignName", data.get("sign", data.get("Sign"))),
                "house": data.get("HouseNumber", data.get("house")),
                "dignity": data.get("Dignity", data.get("dignity")),
            }

    return result


# ══════════════════════════════════════════════════════════════════════
# 8. PYJHORA HOUSE ANALYSIS INTEGRATION  (Research Files 1 & 3)
# ══════════════════════════════════════════════════════════════════════

def extract_pyjhora_longevity(
    pyjhora: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Extract longevity classification from PyJHora's house_analysis
    (valuable for health domain overrides).
    """
    empty = {"available": False}
    if not isinstance(pyjhora, dict) or not pyjhora.get("available"):
        return empty

    ha = pyjhora.get("house_analysis", {})
    if not isinstance(ha, dict):
        return empty

    longevity = ha.get("longevity")
    marakas = ha.get("marakas")

    if longevity is None and marakas is None:
        return empty

    return {
        "available": True,
        "longevity": longevity,
        "marakas": marakas,
        "brahma": ha.get("brahma"),
        "rudra": ha.get("rudra"),
        "maheshwara": ha.get("maheshwara"),
    }


def extract_pyjhora_chara_karakas(
    pyjhora: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Extract Chara Karakas from PyJHora for cross-validation with
    our Jaimini module.
    """
    empty = {"available": False}
    if not isinstance(pyjhora, dict) or not pyjhora.get("available"):
        return empty

    ha = pyjhora.get("house_analysis", {})
    if not isinstance(ha, dict):
        return empty

    ck = ha.get("chara_karakas")
    if ck is None:
        return empty

    return {"available": True, "chara_karakas": ck}


# ══════════════════════════════════════════════════════════════════════
# 9. PYJHORA DASHA SYSTEMS — EXTRA CONVERGENCE SIGNALS  (RF5)
# ══════════════════════════════════════════════════════════════════════

def extract_pyjhora_extra_dashas(
    pyjhora: Dict[str, Any],
    domain_planets: List[str],
    domain_houses: List[int],
) -> Dict[str, Any]:
    """
    PyJHora computes 22 graha + 22 rasi dasha systems.
    Extract whether extra systems (beyond our core 4) support the domain.

    This provides additional dasha convergence evidence for RF5's
    multi-system agreement methodology.
    """
    empty = {"available": False, "extra_supporting": 0, "extra_total": 0, "convergence_boost": 0.0}
    if not isinstance(pyjhora, dict) or not pyjhora.get("available"):
        return empty

    graha_dashas = pyjhora.get("graha_dashas", {})
    rasi_dashas  = pyjhora.get("rasi_dashas", {})
    if not isinstance(graha_dashas, dict) and not isinstance(rasi_dashas, dict):
        return empty

    supporting = 0
    total_checked = 0
    domain_planets_set = set(p.upper() for p in domain_planets)

    # Check graha dashas: if the first lord is in our domain planet list
    if isinstance(graha_dashas, dict):
        for system_name, dasha_data in graha_dashas.items():
            if dasha_data is None:
                continue
            total_checked += 1
            lord = _extract_dasha_lord(dasha_data)
            if lord and lord.upper() in domain_planets_set:
                supporting += 1

    # Check rasi dashas: extract first sign index and check domain houses
    domain_houses_set = set(domain_houses)
    if isinstance(rasi_dashas, dict):
        for system_name, dasha_data in rasi_dashas.items():
            if dasha_data is None:
                continue
            total_checked += 1
            # Rasi dasha format: tuple (system_id, [(sign_idx, sub, date, dur),...])
            # or list of period tuples. Extract first sign index → house.
            sign_idx = _extract_rasi_sign(dasha_data)
            if sign_idx is not None and ((sign_idx + 1) in domain_houses_set):
                supporting += 1

    if total_checked == 0:
        return empty

    ratio = supporting / total_checked
    # Small convergence boost: capped at +3%
    boost = round(min(0.03, ratio * 0.05), 4)

    return {
        "available": True,
        "extra_supporting": supporting,
        "extra_total": total_checked,
        "support_ratio": round(ratio, 3),
        "convergence_boost": boost,
    }


def _extract_rasi_sign(dasha_data) -> Optional[int]:
    """Extract the first rasi (sign index 0-11) from PyJHora rasi dasha data."""
    periods = None
    if isinstance(dasha_data, tuple) and len(dasha_data) >= 2:
        periods = dasha_data[1]
    elif isinstance(dasha_data, list):
        periods = dasha_data

    if isinstance(periods, (list, tuple)) and periods:
        first = periods[0]
        if isinstance(first, (list, tuple)) and first:
            try:
                idx = int(first[0])
                if 0 <= idx <= 11:
                    return idx
            except (TypeError, ValueError):
                pass
    return None


_PLANET_INDEX_MAP = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU"]


def _extract_dasha_lord(dasha_data) -> Optional[str]:
    """Try to extract active dasha lord from various PyJHora formats.

    PyJHora graha_dasha format: tuple(int, list_of_period_tuples)
    where each period tuple = (planet_index, sub_index, date_str, duration).
    """
    # Format: tuple (system_id, [(planet_idx, sub_idx, date, dur), ...])
    if isinstance(dasha_data, tuple) and len(dasha_data) >= 2:
        _, periods = dasha_data[0], dasha_data[1]
        if isinstance(periods, (list, tuple)) and periods:
            first = periods[0]
            if isinstance(first, (list, tuple)) and len(first) >= 1:
                try:
                    idx = int(first[0])
                    if 0 <= idx < len(_PLANET_INDEX_MAP):
                        return _PLANET_INDEX_MAP[idx]
                except (TypeError, ValueError):
                    pass

    if isinstance(dasha_data, dict):
        for key in ("lord", "planet", "mahadasha", "active", "current"):
            val = dasha_data.get(key)
            if isinstance(val, str) and val:
                return val
            if isinstance(val, dict):
                for sub in ("lord", "planet", "name"):
                    sv = val.get(sub)
                    if isinstance(sv, str) and sv:
                        return sv
        # If dict has period entries, check first
        if isinstance(dasha_data.get("periods"), list):
            periods = dasha_data["periods"]
            if periods and isinstance(periods[0], dict):
                return periods[0].get("lord", periods[0].get("planet"))
    elif isinstance(dasha_data, list) and dasha_data:
        first = dasha_data[0]
        if isinstance(first, dict):
            return first.get("lord", first.get("planet"))
        if isinstance(first, str):
            return first
        # List of period tuples (same format as inside tuple)
        if isinstance(first, (list, tuple)) and len(first) >= 1:
            try:
                idx = int(first[0])
                if 0 <= idx < len(_PLANET_INDEX_MAP):
                    return _PLANET_INDEX_MAP[idx]
            except (TypeError, ValueError):
                pass
    return None


# ══════════════════════════════════════════════════════════════════════
# 10. PYJHORA SPHUTAS — SPECIAL POINT SIGNALS
# ══════════════════════════════════════════════════════════════════════

def extract_pyjhora_sphutas(
    pyjhora: Dict[str, Any],
    domain: str,
) -> Dict[str, Any]:
    """
    Extract domain-relevant sphutas from PyJHora.

    Domain relevance:
      career  → yogi_sphuta (favourable), avayogi_sphuta (unfavourable)
      finance → prana_sphuta, deha_sphuta
      health  → mrityu_sphuta, deha_sphuta
      marriage → kshetra_sphuta, beeja_sphuta
    """
    empty = {"available": False}
    if not isinstance(pyjhora, dict) or not pyjhora.get("available"):
        return empty

    sphutas = pyjhora.get("sphutas", {})
    if not isinstance(sphutas, dict) or not sphutas:
        return empty

    domain_keys = {
        "career":  ["yogi_sphuta", "avayogi_sphuta"],
        "finance": ["prana_sphuta", "deha_sphuta", "sri_lagna"],
        "health":  ["mrityu_sphuta", "deha_sphuta"],
        "marriage": ["kshetra_sphuta", "beeja_sphuta"],
    }
    keys = domain_keys.get(domain.lower(), [])
    extracted = {}
    for k in keys:
        val = sphutas.get(k)
        if val is not None:
            extracted[k] = val

    if not extracted:
        return empty

    return {"available": True, "sphutas": extracted}


# ══════════════════════════════════════════════════════════════════════
# ★ MASTER FUNCTION — Aggregate all bridge signals into one modifier
# ══════════════════════════════════════════════════════════════════════

_BRIDGE_MOD_FLOOR = 0.88   # Never penalise more than −12%
_BRIDGE_MOD_CAP   = 1.15   # Never boost more than +15%


def compute_bridge_modifier(
    pyjhora: Dict[str, Any],
    vedastro: Dict[str, Any],
    our_yogas: list,
    our_doshas: Dict[str, Any],
    our_av: Dict[str, Any],
    domain: str,
    dasha_planet: str,
    domain_planets: List[str],
    domain_houses: List[int],
) -> Dict[str, Any]:
    """
    Master aggregator: cross-validate all bridge data and return a
    single multiplicative modifier bounded to [0.88, 1.15].

    Returns dict with 'modifier' key plus diagnostic sub-results.
    """
    modifier = 1.0
    diagnostics: Dict[str, Any] = {"available": False}

    pj = pyjhora if isinstance(pyjhora, dict) else {}
    va = vedastro if isinstance(vedastro, dict) else {}

    # ── 1. Yoga cross-validation (RF4)
    yoga_result = cross_validate_yogas(our_yogas, pj, domain)
    if yoga_result.get("available"):
        modifier += yoga_result["yoga_cross_boost"]
        diagnostics["yoga_cross"] = yoga_result
        diagnostics["available"] = True

    # ── 2. VedAstro domain predictions (RF2)
    vedastro_score = extract_vedastro_domain_score(va, domain)
    if vedastro_score.get("available") and vedastro_score["count"] > 0:
        # VedAstro domain score deviates from neutral (0.5):
        #   score > 0.5 → positive signal → boost
        #   score < 0.5 → negative signal → reduce
        # Effect capped at ±4%
        va_deviation = (vedastro_score["vedastro_domain_score"] - 0.5) * 0.08
        va_mod = round(min(0.04, max(-0.04, va_deviation)), 4)
        modifier += va_mod
        diagnostics["vedastro_domain"] = vedastro_score
        diagnostics["vedastro_domain"]["applied_mod"] = va_mod
        diagnostics["available"] = True

    # ── 3. Dasha cross-validation (RF5)
    dasha_result = cross_validate_dasha(dasha_planet, va)
    if dasha_result.get("available"):
        modifier += dasha_result["boost"]
        diagnostics["dasha_cross"] = dasha_result
        diagnostics["available"] = True

    # ── 4. Dosha cross-validation (RF3)
    dosha_result = cross_validate_doshas(our_doshas, pj)
    if dosha_result.get("available") and dosha_result["confirmed"]:
        modifier += dosha_result["dosha_boost"]
        diagnostics["dosha_cross"] = dosha_result
        diagnostics["available"] = True

    # ── 5. Ashtakavarga cross-check (RF6)
    av_result = cross_validate_ashtakavarga(our_av, pj, domain_houses)
    if av_result.get("available"):
        modifier += av_result["av_boost"]
        diagnostics["av_cross"] = av_result
        diagnostics["available"] = True

    # ── 6. Extra dasha convergence (RF5)
    extra_dasha = extract_pyjhora_extra_dashas(pj, domain_planets, domain_houses)
    if extra_dasha.get("available"):
        modifier += extra_dasha["convergence_boost"]
        diagnostics["extra_dashas"] = extra_dasha
        diagnostics["available"] = True

    # ── 7. Harsha Bala quality signal (RF1)
    harsha = extract_pyjhora_harsha_bala(pj, dasha_planet)
    if harsha.get("available"):
        # Harsha > 0.6 = dasha lord in good shape → +1.5%
        # Harsha < 0.3 = dasha lord suffering → −2%
        h_score = harsha["harsha_score"]
        if h_score >= 0.6:
            modifier += 0.015
        elif h_score < 0.3:
            modifier -= 0.02
        diagnostics["harsha_bala"] = harsha
        diagnostics["available"] = True

    # ── 8. Longevity signal for health domain (RF3)
    if domain.lower() == "health":
        longevity = extract_pyjhora_longevity(pj)
        if longevity.get("available"):
            diagnostics["longevity"] = longevity
            diagnostics["available"] = True
            # Longevity classification affects health confidence
            lon_class = str(longevity.get("longevity", "")).lower()
            if "long" in lon_class or "full" in lon_class:
                modifier += 0.02
            elif "short" in lon_class:
                modifier -= 0.03

    # ── 9. Sphutas extraction (informational, no direct modifier)
    sphutas = extract_pyjhora_sphutas(pj, domain)
    if sphutas.get("available"):
        diagnostics["sphutas"] = sphutas

    # ── Clamp modifier to safety bounds
    modifier = round(min(_BRIDGE_MOD_CAP, max(_BRIDGE_MOD_FLOOR, modifier)), 4)

    diagnostics["modifier"] = modifier
    diagnostics["modifier_pct"] = f"{(modifier - 1.0) * 100:+.1f}%"

    return diagnostics
