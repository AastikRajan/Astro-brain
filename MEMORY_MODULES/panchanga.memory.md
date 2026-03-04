# Module: panchanga.py
## Last Updated: 2026-03-02

## PURPOSE
Computes the 5 limbs of the Panchanga (Hindu almanac) for any date: Tithi (lunar day), Vara (weekday), Nakshatra (Moon's nakshatra), Yoga (sun+moon combination), and Karana (half-tithi). Used for Muhurta (auspicious timing) quality scoring.

## KEY FUNCTIONS

### compute_panchanga(on_date, sun_lon, moon_lon) → dict
- **Purpose:** Full 5-limb Panchanga for a given date
- **Inputs:** date, current Sun and Moon longitudes
- **Returns:** `{tithi, vara, nakshatra, yoga, karana, quality_score}`
- **Called by:** `engine.py:predict()`, muhurta.py

### tithi(sun_lon, moon_lon) → dict
- **Purpose:** Compute Tithi (1–30) from Sun-Moon separation
- **Returns:** `{number, name, lord, type, quality}`

### vara(analysis_date) → dict
- **Purpose:** Compute Vara (weekday lord)
- **Returns:** `{number, name, lord, quality}`

### nakshatra_info(moon_lon) → dict
- **Purpose:** Moon's nakshatra and its quality
- **Returns:** `{index, name, lord, pada, quality}`

### yoga(sun_lon, moon_lon) → dict
- **Purpose:** Yoga = (sun_lon + moon_lon) / 13.333° — 27 yogas
- **Returns:** `{number, name, quality}` (Vishkumbha through Vaidhriti)

### karana(sun_lon, moon_lon) → dict
- **Purpose:** Karana = half-tithi (11 karana types, 60 total per month)
- **Returns:** `{number, name, type, lord, quality}`

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: Integrated into engine.py predict() for Muhurta-aware windows
