# Module: varshaphala.py
## Last Updated: 2026-03-02

## PURPOSE
Implements the Tajika (Persian-derived) Varshaphala (Annual Chart) system. Computes the Solar Return chart, Varsha (annual) Lagna, Muntha, Varshesha (year lord), Panchavargheeya Bala (PVB), Mudda Dasha (monthly periods), all Tajika yogas, and Sahams (Arabic Parts). Full Varshaphala analysis for the solar return year.

## KEY FUNCTIONS

### compute_varshaphala(natal_data, target_year, lat, lon) → dict
- **Purpose:** Complete annual chart analysis for a given year
- **Inputs:** natal chart data, target year int, birth coordinates
- **Returns:** Full dict with solar return positions, Muntha, Varshesha, yogas, Mudda Dasha, Sahams
- **Called by:** `engine.py:analyze_static()`
- **Calls:** `compute_solar_return_dt()`, `compute_varsha_analysis()`, `detect_tajika_yogas()`, `compute_all_sahams()`, `compute_mudda_dasha()`

### compute_varsha_analysis(varsha_lagna, positions, natal_positions) → dict
- **Purpose:** Inner analysis of the annual chart positions
- **Calls:** `compute_muntha()`, `compute_varsha_pati()`, `compute_pahama_bala()`

### detect_tajika_yogas(positions, lagna_lon) → List[dict]
- **Purpose:** Detect all Tajika-specific yogas (Itthasala, Ishrafa, Nakta, etc.)
- **Calls:** `_is_itthasala()`, `classify_tajika_yoga()`

### compute_all_sahams(planet_lons, asc_lon, is_day) → Dict[str, float]
- **Purpose:** Compute Arabic Parts (Sahams) for all standard lots
- **Includes:** Punya Saham (Fortune), Karma Saham, Vivaha Saham, etc.

### compute_mudda_dasha(natal_moon_lon, varsha_start_dt) → List[dict]
- **Purpose:** Compute monthly (Mudda) Dasha for the year
- **Returns:** 12 monthly sub-periods

### compute_pvb(planet, longitude) → dict
- **Purpose:** Panchavargheeya Bala for a planet in the annual chart

## DEPENDENCIES
config.py, coordinates.py

## RECENT CHANGES
- 2026-03-02: Full implementation added (Sahams, Mudda Dasha, Tajika yogas, PVB, Muntha, Varshesha)
