"""
Kota Chakra (Fortress Matrix) — Phase 1E.6
==========================================
Computes 4-zone concentric fortress structure from natal Moon's nakshatra.
Evaluates transit planet direction (inward/outward) and crisis severity.

Source: Research File 3 (Vedic Astrology Computational Systems, Part D)
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

# ── 28 Nakshatras (including Abhijit) starting from Ashwini=1 ─────
_NAK28 = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyestha", "Moola", "Purvashadha", "Uttarashadha",
    "Abhijit", "Shravana", "Dhanishta", "Shatabhisha",
    "Purvabhadrapada", "Uttarabhadrapada", "Revati",
]
_NAK27 = [n for n in _NAK28 if n != "Abhijit"]

# 28-nakshatra sequence retaining Abhijit at index 21 (between Uttarashadha=20, Shravana=22)
_NAK28_IDX = {nak: i for i, nak in enumerate(_NAK28)}
_NAK27_IDX = {nak: i for i, nak in enumerate(_NAK27)}

# ── Zone position offsets from Janma Nakshatra (1-based) ──────────
# Positions 1-28 relative to Janma Nakshatra
_STAMBHA_OFFSETS    = {4, 11, 18, 25}          # innermost (heart)
_DURGANTARA_OFFSETS = {3, 5, 10, 12, 17, 19, 24, 26}
_PRAKAARA_OFFSETS   = {2, 6, 9, 13, 16, 20, 23, 27}
_BAHYA_OFFSETS      = {1, 7, 8, 14, 15, 21, 22, 28}

# ── Diagonal positions (Entry path for direct planets) ────────────
# Positions 1, 8, 15, 22 from Janma = corners of fortress = inward for direct motion
_DIAGONAL_OFFSETS = {1, 8, 15, 22}

# Cardinal positions = all non-diagonal = exit path for direct planets
_CARDINAL_OFFSETS = set(range(1, 29)) - _DIAGONAL_OFFSETS

PLANET_SIGN_LORDS = {
    "Aries": "MARS", "Taurus": "VENUS", "Gemini": "MERCURY",
    "Cancer": "MOON", "Leo": "SUN", "Virgo": "MERCURY",
    "Libra": "VENUS", "Scorpio": "MARS", "Sagittarius": "JUPITER",
    "Capricorn": "SATURN", "Aquarius": "SATURN", "Pisces": "JUPITER",
}
_SIGN_NAMES = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
]


def _offset(janma_idx: int, transit_idx: int, total: int = 28) -> int:
    """Compute 1-based offset of transit nakshatra from janma nakshatra."""
    return ((transit_idx - janma_idx) % total) + 1


def nakshatra_of_lon(longitude: float, include_abhijit: bool = False) -> str:
    """Return nakshatra name for a given sidereal longitude."""
    if include_abhijit:
        # Abhijit is roughly 276.67° - 280.53° (within Capricorn)
        if 276.67 <= (longitude % 360) < 280.53:
            return "Abhijit"
        idx = int(longitude / (360 / 27)) % 27
        nak = _NAK27[idx]
        # Map through Uttarashadha/Shravana depending on whether it falls in Abhijit
        return nak
    idx = int(longitude / (360 / 27)) % 27
    return _NAK27[idx]


def compute_kota_chakra(moon_nakshatra: str) -> Dict:
    """
    Build Kota Chakra from the native's Janma Nakshatra (natal Moon's star).

    Returns:
        {
          "janma_nakshatra": str,
          "kota_swami": str,      # lord of natal Moon sign
          "zones": {
            "stambha": List[str],
            "durgantara": List[str],
            "prakaara": List[str],
            "bahya": List[str],
          },
          "nak_zone": Dict[str, str],   # nakshatra → zone name
          "nak_direction": Dict[str, str], # nakshatra → "diagonal" or "cardinal"
        }
    """
    # Determine janma nakshatra index in 28-nak list
    # If 27-nak nakshatra, find in 28-nak by name
    if moon_nakshatra in _NAK28_IDX:
        janma_28 = _NAK28_IDX[moon_nakshatra]
    elif moon_nakshatra in _NAK27_IDX:
        # Map 27→28 by inserting Abhijit at its position
        nak27_idx = _NAK27_IDX[moon_nakshatra]
        # Abhijit is inserted between index 20 (Uttarashadha) and 21 (Shravana) in 28-nak
        janma_28 = nak27_idx if nak27_idx <= 20 else nak27_idx + 1
    else:
        janma_28 = 0  # fallback

    # Categorise all 28 nakshatras into zones
    zones: Dict[str, List[str]] = {"stambha": [], "durgantara": [], "prakaara": [], "bahya": []}
    nak_zone: Dict[str, str] = {}
    nak_direction: Dict[str, str] = {}

    for idx, nak in enumerate(_NAK28):
        off = _offset(janma_28, idx, total=28)
        if off in _STAMBHA_OFFSETS:
            zone = "stambha"
        elif off in _DURGANTARA_OFFSETS:
            zone = "durgantara"
        elif off in _PRAKAARA_OFFSETS:
            zone = "prakaara"
        else:
            zone = "bahya"
        zones[zone].append(nak)
        nak_zone[nak] = zone
        nak_direction[nak] = "diagonal" if off in _DIAGONAL_OFFSETS else "cardinal"

    # Kota Swami = lord of natal Moon sign (approximate from first nakshatra of zone)
    kota_swami = "unknown"

    return {
        "janma_nakshatra": moon_nakshatra,
        "kota_swami":      kota_swami,
        "zones":           zones,
        "nak_zone":        nak_zone,
        "nak_direction":   nak_direction,
    }


def evaluate_kota_transit(
        transit_planet: str,
        transit_nakshatra: str,
        kota_chakra: Dict,
        is_retrograde: bool = False,
) -> Dict:
    """
    Evaluate a transit planet's effect on the Kota Chakra.

    Direction rules (from research file):
      - Direct planet on diagonal → moves INWARD (dangerous for malefics)
      - Direct planet on cardinal → moves OUTWARD (less dangerous)
      - Retrograde REVERSES direction
      - Rahu/Ketu always retrograde → their cardinal transits = inward

    Returns:
        {
          "zone": str,         # stambha/durgantara/prakaara/bahya
          "direction": str,    # "inward" or "outward"
          "severity": float,   # 0.0-1.0
          "is_malefic": bool,
          "interpretation": str,
        }
    """
    _MALEFICS = {"SUN", "MARS", "SATURN", "RAHU", "KETU", "NORTHNODE", "SOUTHNODE"}
    _ALWAYS_RETRO = {"RAHU", "KETU", "NORTHNODE", "SOUTHNODE"}

    is_malefic = transit_planet in _MALEFICS
    effective_retro = is_retrograde or transit_planet in _ALWAYS_RETRO

    nak_zone = kota_chakra.get("nak_zone", {})
    nak_dir  = kota_chakra.get("nak_direction", {})

    zone = nak_zone.get(transit_nakshatra, "bahya")
    base_dir = nak_dir.get(transit_nakshatra, "cardinal")  # "diagonal" or "cardinal"

    # Direct: diagonal=inward, cardinal=outward; retrograde reverses
    if not effective_retro:
        direction = "inward" if base_dir == "diagonal" else "outward"
    else:
        direction = "outward" if base_dir == "diagonal" else "inward"

    # Severity calculation
    zone_depth = {"stambha": 1.0, "durgantara": 0.75, "prakaara": 0.5, "bahya": 0.25}
    zone_weight = zone_depth.get(zone, 0.25)

    if is_malefic and direction == "inward":
        severity = zone_weight          # danger — malefic penetrating inner zones
    elif is_malefic and direction == "outward":
        severity = zone_weight * 0.3   # malefic fleeing = minimal harm
    elif not is_malefic and direction == "inward":
        severity = 0.0                  # benefic entering = protection
    else:
        severity = 0.0                  # benefic outward = neutral

    # Special: Durga Bhanga (Fort Destruction)
    durga_bhanga = (is_malefic and direction == "inward" and zone in {"stambha", "durgantara"})

    if durga_bhanga:
        interp = (
            f"{transit_planet} (malefic) penetrating {zone.capitalize()} via {base_dir} path. "
            "Durga Bhanga risk — potential health crisis, professional setback, or personal danger. "
            "Severity is high; protective measures recommended."
        )
    elif is_malefic and direction == "inward":
        interp = f"{transit_planet} moving inward through {zone}. Pressure increases; monitor carefully."
    elif is_malefic and direction == "outward":
        interp = f"{transit_planet} in {zone} moving outward — danger receding."
    elif not is_malefic and direction == "inward":
        interp = f"{transit_planet} (benefic) moving into {zone} — fortification and protection."
    else:
        interp = f"{transit_planet} in {zone} moving outward — neutral."

    return {
        "zone":           zone,
        "direction":      direction,
        "base_direction": base_dir,
        "severity":       round(severity, 2),
        "is_malefic":     is_malefic,
        "durga_bhanga":   durga_bhanga,
        "interpretation": interp,
    }


def compute_kota_status(
        kota_chakra: Dict,
        transit_planets: Dict[str, str],    # {planet_name: nakshatra}
        retrograde_planets: set = None,
) -> Dict:
    """
    Evaluate all transiting planets against the Kota Chakra.
    Returns a summary with overall danger score.
    """
    if retrograde_planets is None:
        retrograde_planets = set()

    planet_evals = {}
    total_severity = 0.0
    inward_malefics = []
    outward_benefics = []

    for planet, nak in transit_planets.items():
        is_retro = planet in retrograde_planets
        ev = evaluate_kota_transit(planet, nak, kota_chakra, is_retrograde=is_retro)
        planet_evals[planet] = ev
        total_severity += ev["severity"]
        if ev["is_malefic"] and ev["direction"] == "inward":
            inward_malefics.append(planet)
        if not ev["is_malefic"] and ev["direction"] == "outward":
            outward_benefics.append(planet)

    # Durga Bhanga Yoga: malefics inward + benefics outward simultaneously
    durga_bhanga_yoga = bool(inward_malefics and outward_benefics)

    overall = min(1.0, total_severity / max(len(transit_planets), 1))

    return {
        "planet_evaluations": planet_evals,
        "inward_malefics":    inward_malefics,
        "outward_benefics":   outward_benefics,
        "durga_bhanga_yoga":  durga_bhanga_yoga,
        "overall_severity":   round(overall, 3),
        "summary": (
            "DURGA BHANGA YOGA: Fort under severe assault. High risk period."
            if durga_bhanga_yoga else
            f"Kota severity: {overall:.0%}. "
            + ("Malefics advancing." if inward_malefics else "Relatively stable.")
        ),
    }
