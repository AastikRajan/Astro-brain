"""
Astropy-based planetary position calculator for Vedic astrology.

Uses astropy + ERFA (IAU SOFA) for geocentric ecliptic longitudes.
Accuracy: sub-arcminute for all classical planets, comparable to Swiss Ephemeris
for sign-level Vedic analysis. No C compiler or ephemeris files required.

Priority in transits.py:
  Tier 1: astropy (this module)   ← most accurate pure-Python
  Tier 2: ephem (PyEphem)
  Tier 3: linear approximation
"""
from __future__ import annotations
from datetime import datetime
from typing import Dict


# ─── Lahiri ayanamsa ─────────────────────────────────────────────────────────

def _lahiri_ayanamsa(dt: datetime) -> float:
    """
    Lahiri (Chitra Paksha) ayanamsa in degrees.
    Formula: 23.85° at J2000.0, precessional rate 50.288"/tropical year.
    This matches the Indian Astronomical Almanac values to within ~2'.
    """
    days_from_j2000 = (dt - datetime(2000, 1, 1, 12, 0)).total_seconds() / 86400.0
    return 23.85 + days_from_j2000 * (50.288 / (3600.0 * 365.25))


# ─── Rahu via Meeus formula ────────────────────────────────────────────────

def _rahu_tropical(dt: datetime) -> float:
    """
    Mean Lunar Ascending Node (Rahu) tropical longitude.
    Meeus 'Astronomical Algorithms' ch. 22. Accurate to <0.05° for 1800-2100.
    """
    days_from_j2000 = (dt - datetime(2000, 1, 1, 12, 0)).total_seconds() / 86400.0
    T = days_from_j2000 / 36525.0  # Julian centuries
    lon = (125.0445479
           - 1934.1362608 * T
           + 0.0020754 * T * T
           + T ** 3 / 467441.0
           - T ** 4 / 60616000.0)
    return lon % 360.0


# ─── Main position getter ─────────────────────────────────────────────────────

def get_positions_astropy(dt: datetime) -> Dict[str, float]:
    """
    Compute geocentric sidereal ecliptic longitudes (Lahiri) for all 9 grahas.

    Returns dict: planet_name → sidereal longitude in degrees [0, 360)
    Uses astropy's built-in ephemeris (ERFA/SOFA, accurate to ~0.1").

    Raises ImportError if astropy is not installed.
    """
    from astropy.coordinates import get_body
    from astropy.time import Time

    # astropy Time from datetime (UTC assumed — standard astrology practice)
    t = Time(dt.strftime("%Y-%m-%d %H:%M:%S"), format="iso", scale="utc")

    ayanamsa = _lahiri_ayanamsa(dt)

    BODY_MAP = {
        "SUN":     "sun",
        "MOON":    "moon",
        "MARS":    "mars",
        "MERCURY": "mercury",
        "JUPITER": "jupiter",
        "VENUS":   "venus",
        "SATURN":  "saturn",
    }

    positions: Dict[str, float] = {}

    for graha, body_name in BODY_MAP.items():
        # Get geocentric GCRS position, then transform to GeocentricMeanEcliptic
        sky = get_body(body_name, t)
        # .geocentricmeanecliptic is a property that gives ecliptic coords
        ecl = sky.geocentricmeanecliptic
        tropical_lon = ecl.lon.deg % 360.0
        sidereal_lon = (tropical_lon - ayanamsa) % 360.0
        positions[graha] = round(sidereal_lon, 4)

    # Rahu / Ketu via Meeus (astropy has no node body)
    rahu_trop = _rahu_tropical(dt)
    positions["RAHU"] = round((rahu_trop - ayanamsa) % 360.0, 4)
    positions["KETU"] = round((positions["RAHU"] + 180.0) % 360.0, 4)

    return positions


# ─── Validation helper ────────────────────────────────────────────────────────

def get_accuracy_note() -> str:
    """Return a short human-readable note about the ephemeris accuracy."""
    try:
        import astropy
        return f"astropy {astropy.__version__} / ERFA (sub-arcminute, IAU SOFA)"
    except ImportError:
        return "astropy not available"


if __name__ == "__main__":
    # Quick self-test
    from datetime import datetime
    dt = datetime(2026, 2, 27, 12, 0)
    pos = get_positions_astropy(dt)
    print(f"Positions for {dt.date()} (Lahiri sidereal)")
    print(f"Ephemeris: {get_accuracy_note()}")
    SIGN_NAMES = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                  "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    for p, lon in pos.items():
        sign = SIGN_NAMES[int(lon // 30)]
        deg_in_sign = lon % 30
        print(f"  {p:8s}: {lon:7.3f}°  {sign} {deg_in_sign:.2f}°")
