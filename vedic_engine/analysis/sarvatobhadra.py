"""
Sarvatobhadra Chakra (SBC) — Phase 1E.4 / 1E.5
================================================
9×9 grid astrological matrix for nakshatra-level transit analysis.
Implements grid construction and Vedha (ray-cast) detection.

Source: Research File 3 (Vedic Astrology Computational Systems, Part C)
"""
from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple

# ── 28 Nakshatras (including Abhijit) ─────────────────────────────
NAKSHATRAS_28 = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyestha", "Moola", "Purvashadha", "Uttarashadha",
    "Abhijit", "Shravana", "Dhanishta", "Shatabhisha",
    "Purvabhadrapada", "Uttarabhadrapada", "Revati",
]

NAKSHATRAS_27 = [n for n in NAKSHATRAS_28 if n != "Abhijit"]

# ── SBC 9×9 grid: (row, col) for each nakshatra + signs ──────────
# Row 0 = North edge (top), Row 8 = South edge (bottom)
# Col 0 = West edge (left), Col 8 = East edge (right)
# Outer perimeter: corners (0,0),(0,8),(8,0),(8,8) = vowels
#
# East edge  (col=8, rows 1-7): Krittika→Ashlesha (top to bottom)
# South edge (row=8, cols 1-7): Magha→Vishakha (left to right)
# West edge  (col=0, rows 1-7): Anuradha→Shravana (top=row1 to bottom=row7)
# North edge (row=0, cols 1-7): Bharani→Dhanishta (left=col1 to right=col7)

_EAST  = ["Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha"]
_SOUTH = ["Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha"]
_WEST  = ["Anuradha", "Jyestha", "Moola", "Purvashadha", "Uttarashadha", "Abhijit", "Shravana"]
_NORTH = ["Bharani", "Ashwini", "Revati", "Uttarabhadrapada", "Purvabhadrapada",
          "Shatabhisha", "Dhanishta"]

# Build nakshatra → (row, col) map
NAK_POSITIONS: Dict[str, Tuple[int, int]] = {}
for i, nak in enumerate(_EAST):
    NAK_POSITIONS[nak] = (i + 1, 8)
for i, nak in enumerate(_SOUTH):
    NAK_POSITIONS[nak] = (8, i + 1)
for i, nak in enumerate(_WEST):
    NAK_POSITIONS[nak] = (i + 1, 0)
for i, nak in enumerate(_NORTH):
    NAK_POSITIONS[nak] = (0, i + 1)

# Inverse map: (row, col) → nakshatra
POS_TO_NAK: Dict[Tuple[int, int], str] = {v: k for k, v in NAK_POSITIONS.items()}

# ── Sign ring (one level in from outer perimeter) ─────────────────
# East inner: col=7, rows 1-3 → Taurus, Gemini, Cancer
# South inner: row=7, cols 5-7 → Leo, Virgo, Libra
# West inner: col=1, rows 7-5 → Scorpio, Sagittarius, Capricorn
# North inner: row=1, cols 3-1 → Aquarius, Pisces, Aries
SIGN_RING_CELLS: Dict[str, Tuple[int, int]] = {
    "Taurus": (1, 7), "Gemini": (2, 7), "Cancer": (3, 7),
    "Leo": (7, 7), "Virgo": (7, 6), "Libra": (7, 5),
    "Scorpio": (7, 1), "Sagittarius": (6, 1), "Capricorn": (5, 1),
    "Aquarius": (1, 3), "Pisces": (1, 2), "Aries": (1, 1),
}
SIGN_CELL_MAP: Dict[Tuple[int, int], str] = {v: k for k, v in SIGN_RING_CELLS.items()}

# ── Tithi groups (inner ring, 5 types) ────────────────────────────
TITHI_CELLS: Dict[str, List[Tuple[int, int]]] = {
    "Nanda":  [(2, 6), (6, 6)],
    "Bhadra": [(2, 2), (6, 2)],
    "Jaya":   [(4, 6), (4, 2)],
    "Rikta":  [(2, 4), (6, 4)],
    "Poorna": [(4, 4)],           # center group
}

TITHI_GROUPS = {
    "Nanda":  [1, 6, 11, 16, 21, 26],
    "Bhadra": [2, 7, 12, 17, 22, 27],
    "Jaya":   [3, 8, 13, 18, 23, 28],
    "Rikta":  [4, 9, 14, 19, 24, 29],
    "Poorna": [5, 10, 15, 20, 25, 30],
}

# ── Weekday cells (center) ────────────────────────────────────────
WEEKDAY_CELLS: Dict[str, Tuple[int, int]] = {
    "Sunday": (4, 5), "Monday": (4, 3), "Tuesday": (3, 4),
    "Wednesday": (5, 4), "Thursday": (3, 5), "Friday": (3, 3),
    "Saturday": (5, 5),
}


def nakshatra_of_lon(longitude: float) -> str:
    """Return the 27-nakshatra name for a given ecliptic longitude (0-360)."""
    idx = int(longitude / (360 / 27)) % 27
    return NAKSHATRAS_27[idx]


def _normalize_natal_nakshatra(natal_nakshatra) -> Optional[str]:
    """Normalize natal nakshatra input to a valid name.

    Supported inputs:
      - str nakshatra name
      - int index (0-based preferred; 1-based fallback)
    """
    if isinstance(natal_nakshatra, str):
        name = natal_nakshatra.strip()
        if name in NAK_POSITIONS:
            return name
        return None

    if isinstance(natal_nakshatra, int):
        idx = int(natal_nakshatra)
        # Prefer 0-based handling used by engine internals.
        if 0 <= idx < len(NAKSHATRAS_27):
            return NAKSHATRAS_27[idx]
        # Fallback for 1-based indexing.
        if 1 <= idx <= len(NAKSHATRAS_27):
            return NAKSHATRAS_27[idx - 1]

    return None


def _edge_of(row: int, col: int) -> str:
    """Return which edge/location a cell is on."""
    if col == 8: return "east"
    if row == 8: return "south"
    if col == 0: return "west"
    if row == 0: return "north"
    return "inner"


def _cast_ray(start_row: int, start_col: int, direction: str) -> List[Tuple[int, int]]:
    """
    Cast a ray from a perimeter cell and return all cells it passes through.
    direction: "front" (opposite across grid), "left", "right"
    """
    row, col = start_row, start_col
    edge = _edge_of(row, col)
    cells: List[Tuple[int, int]] = []

    if direction == "front":
        # Go straight to the opposite edge
        if edge == "east":
            # Move left across all columns
            for c in range(col - 1, -1, -1):
                cells.append((row, c))
        elif edge == "west":
            for c in range(col + 1, 9):
                cells.append((row, c))
        elif edge == "north":
            for r in range(row + 1, 9):
                cells.append((r, col))
        elif edge == "south":
            for r in range(row - 1, -1, -1):
                cells.append((r, col))
    elif direction in ("left", "right"):
        # Diagonal movement
        if edge == "east":
            dr = 1 if direction == "left" else -1
            dc = -1
        elif edge == "west":
            dr = -1 if direction == "left" else 1
            dc = 1
        elif edge == "north":
            dr = 1
            dc = 1 if direction == "left" else -1
        elif edge == "south":
            dr = -1
            dc = -1 if direction == "left" else 1
        else:
            return cells
        r, c = row + dr, col + dc
        while 0 <= r <= 8 and 0 <= c <= 8:
            cells.append((r, c))
            r += dr
            c += dc

    return cells


def construct_sbc_grid(
    natal_nakshatra,
        natal_sign: int,           # 0-based
        birth_tithi: int,          # 1-30
        birth_weekday: int,        # 0=Sunday, 1=Monday, ...
) -> Dict:
    """
    Construct SBC metadata for a natal chart.
    Returns reference data used for transit Vedha detection.
    """
    # Find which tithi group the birth belongs to
    birth_tithi_group = ""
    for grp, tithis in TITHI_GROUPS.items():
        if birth_tithi in tithis:
            birth_tithi_group = grp
            break

    _SIGN_NAMES = [
        "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
        "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
    ]
    _WEEKDAY_NAMES = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

    natal_sign_name  = _SIGN_NAMES[natal_sign % 12]
    birth_weekday_name = _WEEKDAY_NAMES[birth_weekday % 7]

    normalized_nak = _normalize_natal_nakshatra(natal_nakshatra)

    # Natal nakshatra cell
    nak_cell = NAK_POSITIONS.get(normalized_nak)
    sign_cell = SIGN_RING_CELLS.get(natal_sign_name)
    tithi_cells = TITHI_CELLS.get(birth_tithi_group, [])
    weekday_cell = WEEKDAY_CELLS.get(birth_weekday_name)

    sensitive_cells = {
        c
        for c in [nak_cell, sign_cell, weekday_cell] + tithi_cells
        if isinstance(c, tuple) and len(c) == 2 and None not in c
    }

    return {
        "natal_nakshatra":  normalized_nak,
        "natal_sign":       natal_sign_name,
        "birth_tithi":      birth_tithi,
        "birth_tithi_group": birth_tithi_group,
        "birth_weekday":    birth_weekday_name,
        "nak_cell":         nak_cell,
        "sign_cell":        sign_cell,
        "tithi_cells":      tithi_cells,
        "weekday_cell":     weekday_cell,
        # Sensitive cells = all natal reference cells
        "sensitive_cells":  sensitive_cells,
    }


def check_sbc_vedha(
        transit_planet: str,
        transit_nakshatra: str,
        sbc_grid: Dict,
        is_retrograde: bool = False,
        is_fast: bool = False,
) -> Dict:
    """
    Detect SBC Vedha: which sensitive points are pierced by the transit.

    Direction rules:
      - Direct/normal speed: Front-Vedha (straight across)
      - Fast motion (Atichara): Left-Vedha (left diagonal)
      - Retrograde: Right-Vedha (right diagonal)
      - Sun/Rahu/Ketu: Front + Left + Right (three-way)

    Returns:
        {
          "pierced_cells": List[Tuple],
          "pierced_nakshatras": List[str],
          "pierced_signs": List[str],
          "pierced_tithi_groups": List[str],
          "natal_sensitive_pierced": bool,   # True if any natal point is hit
          "severity": float,                 # 0.0–1.0
          "directions_used": List[str],
        }
    """
    nak_pos = NAK_POSITIONS.get(transit_nakshatra)
    if not nak_pos:
        return {
            "pierced_cells": [], "pierced_nakshatras": [],
            "pierced_signs": [], "pierced_tithi_groups": [],
            "natal_sensitive_pierced": False, "severity": 0.0,
            "directions_used": [],
        }

    r, c = nak_pos
    THREE_WAY_PLANETS = {"SUN", "RAHU", "KETU", "NORTHNODE", "SOUTHNODE"}
    if transit_planet in THREE_WAY_PLANETS:
        directions = ["front", "left", "right"]
    elif is_retrograde:
        directions = ["right"]
    elif is_fast:
        directions = ["left"]
    else:
        directions = ["front"]

    all_cells: Set[Tuple[int, int]] = set()
    for d in directions:
        all_cells.update(_cast_ray(r, c, d))

    pierced_naks   = [POS_TO_NAK[cell] for cell in all_cells if cell in POS_TO_NAK]
    pierced_signs  = [SIGN_CELL_MAP[cell] for cell in all_cells if cell in SIGN_CELL_MAP]

    pierced_tithi_groups: List[str] = []
    for grp, tcells in TITHI_CELLS.items():
        if any(tc in all_cells for tc in tcells):
            pierced_tithi_groups.append(grp)

    sensitive = sbc_grid.get("sensitive_cells", set())
    natal_hit = bool(sensitive & all_cells)

    # Severity: based on number of sensitive points pierced
    n_pierced = len(sensitive & all_cells)
    severity = min(1.0, n_pierced * 0.25)

    return {
        "pierced_cells":         list(all_cells),
        "pierced_nakshatras":    pierced_naks,
        "pierced_signs":         pierced_signs,
        "pierced_tithi_groups":  pierced_tithi_groups,
        "natal_sensitive_pierced": natal_hit,
        "severity":              round(severity, 2),
        "directions_used":       directions,
    }
