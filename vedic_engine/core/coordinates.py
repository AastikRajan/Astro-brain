"""
Core coordinate math: sign, nakshatra, pada, varga decomposition.
Every formula here is derived from the deep-research-report.md.
All inputs/outputs in decimal degrees unless noted.
"""
from __future__ import annotations
from typing import Dict, Tuple

from vedic_engine.config import (
    Sign, Element, SignQuality, SIGN_ELEMENTS, SIGN_QUALITIES,
    NAKSHATRA_SPAN, PADA_SPAN, NAKSHATRA_NAMES, VIMSHOTTARI_SEQUENCE,
    SIGN_LORDS
)

SIGN_NAMES = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
              "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]


def normalize(lon: float) -> float:
    """Force 0 ≤ lon < 360."""
    return lon % 360.0


def sign_of(lon: float) -> int:
    """Return 0-11 sign index for absolute sidereal longitude."""
    return int(normalize(lon) / 30) % 12


def degree_in_sign(lon: float) -> float:
    """Return 0-30 degree position within sign."""
    return normalize(lon) % 30.0


def nakshatra_of(lon: float) -> int:
    """Return 0-26 nakshatra index."""
    return min(int(normalize(lon) / NAKSHATRA_SPAN), 26)


def pada_of(lon: float) -> int:
    """Return 1-4 pada within nakshatra."""
    pos_in_nak = normalize(lon) % NAKSHATRA_SPAN
    return int(pos_in_nak / PADA_SPAN) + 1


def nakshatra_lord_of(lon: float):
    """Return Planet enum for the nakshatra lord."""
    return VIMSHOTTARI_SEQUENCE[nakshatra_of(lon) % 9]


def angular_distance(lon_a: float, lon_b: float) -> float:
    """
    Shortest angular distance between two longitudes.
    Returns value in [0, 180].
    """
    diff = abs(normalize(lon_a) - normalize(lon_b))
    if diff > 180.0:
        diff = 360.0 - diff
    return diff


def signed_distance(from_lon: float, to_lon: float) -> float:
    """
    Directional arc: to_lon - from_lon, normalised to (-180, 180].
    Positive = to_lon is ahead (counter-clockwise / zodiac forward).
    """
    d = normalize(to_lon) - normalize(from_lon)
    if d > 180:
        d -= 360
    elif d <= -180:
        d += 360
    return d


def house_from(planet_sign: int, lagna_sign: int) -> int:
    """Return 1-indexed house number of planet from lagna."""
    return (planet_sign - lagna_sign) % 12 + 1


def house_from_moon(planet_sign: int, moon_sign: int) -> int:
    """Return 1-indexed house number of planet counted from Moon sign."""
    return (planet_sign - moon_sign) % 12 + 1


def sign_name(idx: int) -> str:
    return SIGN_NAMES[idx % 12]


def full_position_info(lon: float) -> dict:
    """
    Given an absolute sidereal longitude, return a complete breakdown dict.
    This is the 'single number maps to all overlays' principle.
    """
    lon = normalize(lon)
    s = sign_of(lon)
    n = nakshatra_of(lon)
    p = pada_of(lon)
    nak_lord = VIMSHOTTARI_SEQUENCE[n % 9]
    pos_in_nak = lon % NAKSHATRA_SPAN
    pos_in_pada = lon % PADA_SPAN

    return {
        "longitude": lon,
        "sign_index": s,
        "sign_name": SIGN_NAMES[s],
        "sign_lord": SIGN_LORDS[Sign(s)].name,
        "degree_in_sign": lon % 30,
        "nakshatra_index": n,
        "nakshatra_name": NAKSHATRA_NAMES[n],
        "nakshatra_lord": nak_lord.name,
        "pos_in_nakshatra": pos_in_nak,
        "pada": p,
        "pos_in_pada": pos_in_pada,
        "element": SIGN_ELEMENTS[Sign(s)].value,
        "quality": SIGN_QUALITIES[Sign(s)].value,
        "decanate": int((lon % 30) / 10) + 1,  # 1, 2, or 3
    }
