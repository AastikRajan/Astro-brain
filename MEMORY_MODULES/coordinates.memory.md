# Module: coordinates.py
## Last Updated: 2026-03-02

## PURPOSE
Core longitude math utilities used throughout the engine. All sidereal longitude calculations, sign/nakshatra derivations, and angular separation computations go through this module. Zero dependencies — pure Python math.

## KEY FUNCTIONS

### sign_of(longitude) → int
- **Purpose:** Get sign index (0–11) from absolute longitude (0–360)
- **Called by:** Nearly every module in the engine

### nakshatra_of(longitude) → Tuple[int, str, str, int]
- **Purpose:** Get nakshatra index, name, lord, and pada from longitude
- **Returns:** (index, name, lord, pada)

### degree_in_sign(longitude) → float
- **Purpose:** Get degree within sign (0–30) from absolute longitude

### normalize(longitude) → float
- **Purpose:** Normalize longitude to 0–360 range

### angular_distance(lon_a, lon_b) → float
- **Purpose:** Shortest arc between two longitudes (0–180)

### house_from_moon(planet_lon, moon_lon) → int
- **Purpose:** Compute Gochar house count from natal Moon to a planet (1–12)
- **Called by:** transits.py, yogas.py

## DEPENDENCIES
(none)

## RECENT CHANGES
- 2026-03-02: No changes (stable core utility)
