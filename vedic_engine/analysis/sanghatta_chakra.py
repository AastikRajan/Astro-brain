"""
Sanghatta Chakra (Sanghatika Nakshatra) helpers.

Implements the special-tara mapping used to derive the Sanghatika star from
the Janma Nakshatra, then evaluates transit hits at that collision point.

Source alignment:
- pyjhora const.special_thaara_map (Sanghatika offset = 16)
- classical special-tara sequence (Janma, Karma, Samudayika, Sanghatika, ...)
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from vedic_engine.config import NAKSHATRA_NAMES


NAKSHATRA_NAMES_27: List[str] = list(NAKSHATRA_NAMES)
NAKSHATRA_NAMES_28: List[str] = [*NAKSHATRA_NAMES_27[:21], "Abhijit", *NAKSHATRA_NAMES_27[21:]]

# Order from pyjhora const comment:
# Janma, Karma, Samudayika, Sanghatika, Jaathi, Naidhana,
# Desha, Abhisheka, Aadhaana, Vainasika, Maanasa
SPECIAL_THAARA_SEQUENCE: Tuple[Tuple[str, int], ...] = (
    ("janma", 1),
    ("karma", 10),
    ("samudayika", 18),
    ("sanghatika", 16),
    ("jaathi", 4),
    ("naidhana", 7),
    ("desha", 12),
    ("abhisheka", 27),
    ("aadhaana", 19),
    ("vainasika", 22),
    ("manasa", 25),
)

_MALEFICS = {"SUN", "MARS", "SATURN", "RAHU", "KETU", "NORTHNODE", "SOUTHNODE"}
_BENEFICS = {"MOON", "MERCURY", "JUPITER", "VENUS"}


def _slug(name: str) -> str:
    return "".join(ch for ch in str(name).strip().lower() if ch.isalnum())


def _build_alias_map() -> Dict[str, str]:
    out: Dict[str, str] = {}

    for nak in NAKSHATRA_NAMES_28:
        out[_slug(nak)] = nak

    # Common spelling variants used across runtime modules and research inputs.
    variants = {
        "Jyeshtha": ["Jyestha", "Jyeshta"],
        "Mula": ["Moola"],
        "Purvashadha": ["Purva Ashadha"],
        "Uttarashadha": ["Uttara Ashadha"],
        "Dhanishta": ["Dhanishtha"],
        "Purva Bhadrapada": ["Purvabhadrapada", "PurvaBhadrapada"],
        "Uttara Bhadrapada": ["Uttarabhadrapada", "UttaraBhadrapada"],
    }
    for canonical, names in variants.items():
        for alias in names:
            out[_slug(alias)] = canonical

    return out


_NAKSHATRA_ALIAS_MAP = _build_alias_map()


def _normalize_nakshatra_name(name: str, include_abhijit: bool = True) -> Optional[str]:
    canonical = _NAKSHATRA_ALIAS_MAP.get(_slug(name), "")
    if not canonical:
        return None
    if not include_abhijit and canonical == "Abhijit":
        return None
    return canonical


def _normalize_janma_nakshatra(janma_nakshatra, include_abhijit: bool = True) -> Optional[str]:
    if isinstance(janma_nakshatra, str):
        return _normalize_nakshatra_name(janma_nakshatra, include_abhijit=include_abhijit)

    if isinstance(janma_nakshatra, int):
        idx = int(janma_nakshatra)
        # Prefer 0-based 27-nakshatra indexing used by runtime internals.
        if 0 <= idx < len(NAKSHATRA_NAMES_27):
            return NAKSHATRA_NAMES_27[idx]
        # Optional 0-based 28-cycle fallback.
        if include_abhijit and 0 <= idx < len(NAKSHATRA_NAMES_28):
            return NAKSHATRA_NAMES_28[idx]
        # 1-based 27-cycle fallback.
        if 1 <= idx <= len(NAKSHATRA_NAMES_27):
            return NAKSHATRA_NAMES_27[idx - 1]
        # Optional 1-based 28-cycle fallback.
        if include_abhijit and 1 <= idx <= len(NAKSHATRA_NAMES_28):
            return NAKSHATRA_NAMES_28[idx - 1]

    return None


def _cycle_names(include_abhijit: bool) -> List[str]:
    return NAKSHATRA_NAMES_28 if include_abhijit else NAKSHATRA_NAMES_27


def _offset_index(janma_idx: int, offset: int, cycle_len: int) -> int:
    return (int(janma_idx) + int(offset) - 1) % int(cycle_len)


def nakshatra_of_lon(longitude: float, include_abhijit: bool = True) -> str:
    """Return nakshatra name for a sidereal longitude."""
    lon = float(longitude) % 360.0
    if include_abhijit and 276.667 <= lon < 280.889:
        return "Abhijit"
    idx = int(lon / (360.0 / 27.0)) % 27
    return NAKSHATRA_NAMES_27[idx]


def compute_sanghatta_chakra(
    janma_nakshatra,
    include_abhijit: bool = True,
) -> Dict:
    """Build special-tara map from Janma Nakshatra and expose Sanghatika target."""
    cycle = _cycle_names(include_abhijit=include_abhijit)
    cycle_len = len(cycle)

    normalized_janma = _normalize_janma_nakshatra(
        janma_nakshatra,
        include_abhijit=include_abhijit,
    )
    if not normalized_janma:
        normalized_janma = cycle[0]

    if normalized_janma == "Abhijit" and not include_abhijit:
        normalized_janma = "Uttarashadha"

    janma_idx = cycle.index(normalized_janma)

    special_taras: Dict[str, Dict] = {}
    for label, offset in SPECIAL_THAARA_SEQUENCE:
        target_idx = _offset_index(janma_idx, offset, cycle_len)
        target_nak = cycle[target_idx]
        special_taras[label] = {
            "offset": int(offset),
            "star_index": int(target_idx + 1),
            "nakshatra": target_nak,
        }

    sanghatika = special_taras.get("sanghatika", {})

    return {
        "janma_nakshatra": normalized_janma,
        "include_abhijit": bool(include_abhijit),
        "star_count": int(cycle_len),
        "special_taras": special_taras,
        "sanghatika": sanghatika,
        "source": "pyjhora const.special_thaara_map + classical Sanghatika (16th) rule",
    }


def evaluate_sanghatta_transit(
    transit_planet: str,
    transit_nakshatra: str,
    sanghatta_chakra: Dict,
    is_retrograde: bool = False,
) -> Dict:
    """Evaluate whether a transit planet is striking the Sanghatika collision star."""
    planet = str(transit_planet).upper()

    include_abhijit = bool(sanghatta_chakra.get("include_abhijit", True))
    target_nak = str((sanghatta_chakra.get("sanghatika", {}) or {}).get("nakshatra", ""))
    target_nak = _normalize_nakshatra_name(target_nak, include_abhijit=include_abhijit) or ""

    transit_nak = _normalize_nakshatra_name(
        str(transit_nakshatra),
        include_abhijit=include_abhijit,
    ) or ""

    classification = "neutral"
    if planet in _MALEFICS:
        classification = "malefic"
    elif planet in _BENEFICS:
        classification = "benefic"

    is_hit = bool(target_nak and transit_nak and transit_nak == target_nak)

    if not is_hit:
        impact_score = 0.0
        severity = 0.0
        interpretation = "No Sanghatika collision."
    elif classification == "malefic":
        impact_score = -0.20
        severity = 0.80
        interpretation = "Malefic strike on Sanghatika star: collision pressure and social friction rise."
    elif classification == "benefic":
        impact_score = 0.08
        severity = 0.35
        interpretation = "Benefic activation on Sanghatika star: constructive group support and uplift potential."
    else:
        impact_score = -0.05
        severity = 0.25
        interpretation = "Neutral collision on Sanghatika star: mild instability, monitor outcomes."

    return {
        "planet": planet,
        "classification": classification,
        "transit_nakshatra": transit_nak,
        "sanghatika_nakshatra": target_nak,
        "is_hit": is_hit,
        "is_retrograde": bool(is_retrograde),
        "impact_score": round(impact_score, 3),
        "severity": round(severity, 3),
        "interpretation": interpretation,
    }


def compute_sanghatta_status(
    sanghatta_chakra: Dict,
    transit_planets: Dict[str, str],
    retrograde_planets: Optional[set] = None,
) -> Dict:
    """Evaluate Sanghatika collision status for all transiting planets."""
    retro = {str(p).upper() for p in (retrograde_planets or set())}

    by_planet: Dict[str, Dict] = {}
    hit_planets: List[str] = []
    total_impact = 0.0

    for planet, transit_nak in (transit_planets or {}).items():
        p = str(planet).upper()
        ev = evaluate_sanghatta_transit(
            transit_planet=p,
            transit_nakshatra=str(transit_nak),
            sanghatta_chakra=sanghatta_chakra,
            is_retrograde=(p in retro),
        )
        by_planet[p] = ev
        if ev.get("is_hit"):
            hit_planets.append(p)
        total_impact += float(ev.get("impact_score", 0.0) or 0.0)

    overall = max(-1.0, min(1.0, total_impact))

    return {
        "planet_evaluations": by_planet,
        "hit_planets": sorted(hit_planets),
        "overall_impact": round(overall, 3),
        "summary": (
            "Sanghatika collision active"
            if hit_planets else
            "No active Sanghatika collision"
        ),
    }


__all__ = [
    "SPECIAL_THAARA_SEQUENCE",
    "NAKSHATRA_NAMES_28",
    "nakshatra_of_lon",
    "compute_sanghatta_chakra",
    "evaluate_sanghatta_transit",
    "compute_sanghatta_status",
]
