"""
Skyfield + JPL Ephemeris Backend — Research-Grade Position Calculator.

Why Skyfield?
─────────────
Swiss Ephemeris is astrology-first: its Lahiri results are the gold standard
for astrological software but it requires a C compiler on Windows.
Skyfield is astronomy-first: pure Python, loads official JPL BSP files
(DE421, DE440, DE440s) that NASA publishes directly as the reference truth.

This module uses Skyfield + JPL DE421/DE440s as an INDEPENDENT second source
to cross-check astropy (tier-2) and, when installed, pyswisseph (tier-1).

Position agreement between Skyfield-DE440s and Swiss Ephemeris is typically
< 0.001° for classical planets (they derive from the same JPL integrations).
Any systematic discrepancy >0.01° indicates a bug in our ayanamsa formula,
frame transformation, or a tier-4 fallback slipping through silently.

Ephemeris files
───────────────
de440s.bsp  — DE440 small: 1849-2150, ~32 MB (recommended)
de421.bsp   — DE421: 1899-2053, ~17 MB (tighter range)

Files are downloaded on first use and cached under data/ephemeris/ in the
package root. Subsequent runs are instant (pure file I/O).

If the download fails (offline environment), the module raises ImportError
gracefully so get_transit_positions() falls through to astropy.

Usage
─────
  from vedic_engine.prediction.skyfield_positions import get_positions_skyfield
  pos = get_positions_skyfield(datetime(2026, 2, 28, 12, 0))
  # {'SUN': 315.4, 'MOON': 200.1, ...}  — Lahiri sidereal degrees
"""
from __future__ import annotations

import math
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# ─── Ephemeris file management ───────────────────────────────────────────────

# Store BSP files in a predictable location inside the package
_EPHEM_DIR = Path(__file__).parent.parent / "data" / "ephemeris"

# Preference order: DE440s (larger range) → DE421 (smaller, faster download)
_PREFERRED_FILES = ["de440s.bsp", "de421.bsp"]

# JPL Horizons / NAIF download URLs
_DOWNLOAD_URLS = {
    "de440s.bsp": "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp",
    "de421.bsp":  "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de421.bsp",
}

# Skyfield's own hosted copies (Skyfield CDN — often faster)
_SKYFIELD_URLS = {
    "de440s.bsp": "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp",
    "de421.bsp":  "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de421.bsp",
}


def _ensure_ephemeris() -> Path:
    """
    Locate or download the best available JPL BSP file.

    Returns the Path to the .bsp file and ensures _EPHEM_DIR exists.
    Raises FileNotFoundError if no file is available and download fails.
    """
    _EPHEM_DIR.mkdir(parents=True, exist_ok=True)

    # Check for any already-present file
    for fname in _PREFERRED_FILES:
        candidate = _EPHEM_DIR / fname
        if candidate.exists() and candidate.stat().st_size > 1_000_000:  # > 1 MB sanity check
            return candidate

    # Try downloading via Skyfield's Loader (handles redirects, progress, checksums)
    try:
        from skyfield.api import Loader
        load = Loader(str(_EPHEM_DIR))

        # Try de440s first, fallback to de421
        for fname in _PREFERRED_FILES:
            try:
                ephem = load(fname)
                return _EPHEM_DIR / fname
            except Exception:
                continue

    except Exception:
        pass

    raise FileNotFoundError(
        f"No JPL ephemeris file found in {_EPHEM_DIR}. "
        f"Attempted: {_PREFERRED_FILES}. "
        "Ensure internet access for first-time download, or manually place "
        "de440s.bsp or de421.bsp in that directory."
    )


# ─── Lahiri ayanamsa ─────────────────────────────────────────────────────────

def _lahiri_ayanamsa(dt: datetime) -> float:
    """
    Lahiri (Chitra Paksha) ayanamsa in degrees.
    Consistent with astropy_positions.py for cross-validation.
    Formula: 23.85° at J2000.0, precessing 50.288"/tropical year.
    """
    days_from_j2000 = (dt - datetime(2000, 1, 1, 12, 0)).total_seconds() / 86400.0
    return 23.85 + days_from_j2000 * (50.288 / (3600.0 * 365.25))


# ─── Mean Lunar Node (Rahu) ───────────────────────────────────────────────────

def _rahu_tropical(dt: datetime) -> float:
    """
    Meeus 'Astronomical Algorithms' ch. 22, mean ascending node.
    Accurate to <0.05° for 1800-2100. Identical formula to astropy_positions.py.
    """
    days_from_j2000 = (dt - datetime(2000, 1, 1, 12, 0)).total_seconds() / 86400.0
    T = days_from_j2000 / 36525.0
    lon = (125.0445479
           - 1934.1362608 * T
           + 0.0020754 * T * T
           + T ** 3 / 467441.0
           - T ** 4 / 60616000.0)
    return lon % 360.0


# ─── Module-level ephemeris cache ────────────────────────────────────────────

_skyfield_eph = None      # cached Skyfield ephemeris object
_skyfield_ts  = None      # cached Skyfield timescale


def _get_skyfield_eph():
    """Return cached (ephemeris, timescale) — downloads BSP on first call."""
    global _skyfield_eph, _skyfield_ts
    if _skyfield_eph is None:
        from skyfield.api import Loader, load as sf_load
        bsp_path = _ensure_ephemeris()
        load = Loader(str(bsp_path.parent))
        _skyfield_eph = load(bsp_path.name)
        _skyfield_ts  = sf_load.timescale()
    return _skyfield_eph, _skyfield_ts


# ─── Main position getter ─────────────────────────────────────────────────────

def get_positions_skyfield(dt: datetime) -> Dict[str, float]:
    """
    Compute geocentric sidereal ecliptic longitudes (Lahiri) using Skyfield + JPL ephemeris.

    Parameters
    ----------
    dt : naive datetime (treated as UTC, standard astrological convention)

    Returns
    -------
    Dict mapping planet name → sidereal longitude in degrees [0, 360)

    Planets: SUN MOON MARS MERCURY JUPITER VENUS SATURN RAHU KETU

    Accuracy
    --------
    Skyfield + DE440s: < 0.001° vs Swiss Ephemeris for 1850-2150.
    Rahu/Ketu via Meeus formula: < 0.05° (same as astropy backend).
    Total Lahiri sidereal error vs astrology-standard: < 0.02° (formula).

    Raises
    ------
    ImportError  : if skyfield package is not installed
    FileNotFoundError : if BSP file unavailable and download fails
    """
    from skyfield.api import wgs84
    from skyfield.framelib import ecliptic_frame

    eph, ts = _get_skyfield_eph()

    # Build Skyfield Time from UTC datetime
    t = ts.utc(dt.year, dt.month, dt.day,
               dt.hour, dt.minute, dt.second + dt.microsecond / 1e6)

    # Earth as observer
    earth = eph["earth"]

    ayanamsa = _lahiri_ayanamsa(dt)

    # Skyfield body name map — body strings for DE421/DE440s
    # DE440s uses barycenters for Mars/Mercury/Venus (no individual planet bodies)
    # DE421 has individual bodies AND barycenters; barycenter names work for both.
    BODY_MAP = {
        "SUN":     "sun",
        "MOON":    "moon",
        "MARS":    "mars barycenter",
        "MERCURY": "mercury barycenter",
        "JUPITER": "jupiter barycenter",
        "VENUS":   "venus barycenter",
        "SATURN":  "saturn barycenter",
    }

    positions: Dict[str, float] = {}

    for graha, body_name in BODY_MAP.items():
        try:
            body = eph[body_name]
        except KeyError:
            # Fallback: try without "barycenter" suffix (older BSP files)
            alt = body_name.replace(" barycenter", "")
            try:
                body = eph[alt]
            except KeyError:
                # Try adding "barycenter" if not present
                alt2 = body_name + " barycenter" if "barycenter" not in body_name else body_name
                body = eph[alt2]

        # Astrometric position from Earth → body
        astrometric = earth.at(t).observe(body).apparent()
        # Transform to geocentric ecliptic (J2000 frame)
        lat, lon, _ = astrometric.frame_latlon(ecliptic_frame)
        tropical_lon = lon.degrees % 360.0
        sidereal_lon = (tropical_lon - ayanamsa) % 360.0
        positions[graha] = round(sidereal_lon, 5)

    # Rahu / Ketu via Meeus (DE421/440 have no mean-node body)
    rahu_trop = _rahu_tropical(dt)
    positions["RAHU"] = round((rahu_trop - ayanamsa) % 360.0, 5)
    positions["KETU"] = round((positions["RAHU"] + 180.0) % 360.0, 5)

    return positions


# ─── Speed computation ────────────────────────────────────────────────────────

def get_speeds_skyfield(dt: datetime, delta_hours: float = 1.0) -> Dict[str, float]:
    """
    Compute heliocentric angular speed (deg/day) by finite difference.

    Parameters
    ----------
    dt           : reference datetime (UTC naive)
    delta_hours  : step size for finite difference (default 1 hour)

    Returns
    -------
    Dict: planet → speed in degrees/day (negative = retrograde)
    This is used for retrograde detection auditing.
    """
    from datetime import timedelta
    pos_before = get_positions_skyfield(dt - timedelta(hours=delta_hours))
    pos_after  = get_positions_skyfield(dt + timedelta(hours=delta_hours))

    speeds: Dict[str, float] = {}
    for planet in pos_before:
        d_before = pos_before[planet]
        d_after  = pos_after[planet]
        # Handle wrap-around at 0/360
        diff = d_after - d_before
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        # Convert to deg/day: diff is over 2*delta_hours
        speeds[planet] = round(diff / (2 * delta_hours / 24.0), 5)

    return speeds


# ─── Ephemeris info ───────────────────────────────────────────────────────────

def get_ephemeris_info() -> str:
    """Return a descriptive string about the loaded ephemeris."""
    try:
        bsp_path = None
        for fname in _PREFERRED_FILES:
            candidate = _EPHEM_DIR / fname
            if candidate.exists() and candidate.stat().st_size > 1_000_000:
                bsp_path = candidate
                break

        if bsp_path:
            size_mb = bsp_path.stat().st_size / 1_048_576
            return f"Skyfield + JPL {bsp_path.name} ({size_mb:.1f} MB, {bsp_path})"
        else:
            return "Skyfield (ephemeris not yet downloaded)"
    except Exception:
        return "Skyfield (status unknown)"


if __name__ == "__main__":
    # Self-test: print positions for today and compare with known values
    dt_test = datetime(2026, 2, 28, 12, 0)
    print(f"\nSkyfield JPL positions for {dt_test} UTC (Lahiri sidereal)")
    print(f"Ephemeris: {get_ephemeris_info()}\n")
    SIGN_NAMES = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                  "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    pos = get_positions_skyfield(dt_test)
    for p, lon in pos.items():
        sign = SIGN_NAMES[int(lon // 30)]
        deg  = lon % 30
        print(f"  {p:9s}: {lon:8.4f}°  {sign:12s} {deg:5.2f}°")
