# Module: sunrise_utils.py
## Last Updated: 2026-03-02

## PURPOSE
Computes sunrise and sunset times for a given date and geographic location. Used by Shadbala computation (Nathonnatha Bala, Hora Bala, Tribhaga Bala all require whether birth was day or night). Also used by Panchanga and Muhurta modules.

## KEY FUNCTIONS

### get_sunrise(date, lat, lon) → datetime
- **Purpose:** Compute local sunrise time for date and location
- **Called by:** `shadbala.py:nathonnatha_bala()`, `shadbala.py:hora_bala()`

### get_sunset(date, lat, lon) → datetime
- **Purpose:** Compute local sunset time
- **Called by:** `shadbala.py:nathonnatha_bala()`

## DEPENDENCIES
(pure math or ephem library)

## RECENT CHANGES
- 2026-03-02: No changes
