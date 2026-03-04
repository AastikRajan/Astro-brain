# Module: jaimini_dashas.py
## Last Updated: 2026-03-02

## PURPOSE
Implements multiple Jaimini-derived dasha systems: Shoola, Niryana Shoola, Brahma, Navamsha, Sudasa, Drig, and Trikona Dasha. These sign-based timing systems are used for specialized predictions (longevity, spirituality, karma). Also includes Sree Lagna computation and death-timing window analysis.

## KEY FUNCTIONS

### compute_shoola_dasha(planet_lons, lagna_sign, birth_date) → List[dict]
- **Purpose:** Shoola Dasha sequence (malefic-strength based)

### compute_niryana_shoola_dasha(planet_lons, lagna_sign, birth_date) → List[dict]
- **Purpose:** Niryana Shoola Dasha (for longevity/ayur analysis)

### compute_brahma_dasha(planet_lons, lagna_sign, birth_date) → List[dict]
- **Purpose:** Brahma Dasha (from 9th-from-9th Brahma planet)
- **Calls:** `_find_brahma_planet()`

### compute_navamsha_dasha(planet_lons, lagna_sign, birth_date) → List[dict]
- **Purpose:** Navamsha-based dasha sequence

### compute_sudasa(planet_lons, sree_lagna, birth_date) → List[dict]
- **Purpose:** Sudasa Dasha from Sree Lagna (wealth timing)
- **Calls:** `compute_sree_lagna()`

### compute_drig_dasha(planet_lons, lagna_sign, birth_date) → List[dict]
- **Purpose:** Drig Dasha (aspect-based strength ordering)

### compute_trikona_dasha(planet_lons, lagna_sign, birth_date) → List[dict]
- **Purpose:** Trikona Dasha (trine-based sequence)

### check_death_timing_window(active_shoola_sign, shoola_antar_sign, rudra_sign, al_sign) -> dict
- **Purpose:** Critical mortality window flag (Sutra 9)

### compute_narayana_dasha(birth_dt, lagna_sign, planet_lons) -> List[Dict] [NEW Phase 1C]
- **Purpose:** Narayana Sign Dasha — Jaimini's universal environmental timing system
- **Start sign:** Stronger of Lagna vs 7th by 6-step Jaimini strength cascade
- **Duration:** count from sign to its lord's sign (forward or backward), max 12 yrs; exalted +1, debilitated -1
- **Sequence:** by modality of start sign: Movable=adjacent, Fixed=6th-step, Dual=trinal (1-5-9 → 10-2-6 → 7-11-3 → 4-8-12)
- **Direction:** 9th from start — odd-footed → forward, even-footed → backward
- **Saturn override:** forces adjacent sequence; **Ketu override:** reverses direction
- **Returns:** [{sign, sign_name, lord, duration_years, start_date, end_date, direction}]

### get_active_narayana(periods, on_date) -> Dict [NEW Phase 1C]
- Generic active-period finder for Narayana Dasha timeline

### get_active_period(periods, on_date) -> Optional[dict]
- **Purpose:** Generic active period finder (shared by all Jaimini systems)

## DEPENDENCIES
config.py, coordinates.py

## RECENT CHANGES
- 2026-03-02 Phase 1C: ADD compute_narayana_dasha (full Jaimini sign-based: direction, modality, Saturn/Ketu overrides)
- 2026-03-02 Phase 1C: ADD get_active_narayana
- 2026-03-02: Full suite implemented (Shoola, Brahma, Navamsha, Sudasa, Drig, Trikona)
