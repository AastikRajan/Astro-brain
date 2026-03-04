# Module: shadbala.py
## Last Updated: 2026-03-02

## PURPOSE
Computes the full classical Shadbala (6-fold planetary strength) for each of the 9 Vedic planets. Shadbala is the primary natal strength metric used throughout the engine — it feeds confidence scoring, yoga detection, dasha quality, and the Promise gate. Returns strength in Virupas (unit) and as a ratio against classical minimums.

## KEY FUNCTIONS

### compute_shadbala(planet, planet_lon, ...) → dict
- **Purpose:** Compute all 6 Shadbala components for one planet
- **Inputs:** planet name, longitude, birth_dt, chart positions
- **Returns:** `{sthana_bala, dig_bala, kala_bala, cheshta_bala, naisargika_bala, drik_bala, total_virupas, shadbala_ratio}`
- **Called by:** `compute_all_shadbala()`
- **Calls:** `sthana_bala()`, `dig_bala()`, `kala_bala()`, `cheshta_bala()`, `naisargika_bala()`

### compute_all_shadbala(planet_longitudes, birth_dt, ...) → Dict[str, dict]
- **Purpose:** Compute Shadbala for all 9 planets
- **Inputs:** planet longitudes dict, birth datetime, lagna longitude
- **Returns:** dict planet → shadbala result
- **Called by:** `engine.py:analyze_static()`

### sthana_bala(planet, longitude, ...) → float
- **Purpose:** Positional strength (exaltation, own sign, mulatrikona, etc.)
- **Calls:** `uccha_bala()`, `saptavargaja_bala()`, `ojhayugma_bala()`, `kendradi_bala()`, `drekkana_bala()`

### kala_bala(planet, birth_dt, ...) → float
- **Purpose:** Temporal strength (nathonnatha, paksha, vara, hora, abda, masa, tribhaga, ayana)
- **Calls:** `nathonnatha_bala()`, `paksha_bala()`, `vara_bala()`, `hora_bala()`, `abda_bala()`, `masa_bala()`, `tribhaga_bala()`, `ayana_bala()`

### cheshta_bala(planet, is_retrograde, speed) → float
- **Purpose:** Motional strength — retrograde planets get bonus
- **Key logic:** Retrograde = max score; combust = 0; rates by speed relative to mean

### naisargika_bala(planet) → float
- **Purpose:** Fixed natural strength hierarchy (SAT < MAR < MER < JUP < VEN < MOO < SUN)

## IMPORTANT CONSTANTS
- `SHADBALA_MINIMUMS` from config.py — minimum virupas per planet
- All sub-bala weights from BPHS classical tables

## DEPENDENCIES
config.py (extensive), datetime

## RECENT CHANGES
- 2026-03-02 Phase 1A Audit + Fixes (7 changes):
  - FIX ojhayugma_bala: Mercury + Saturn now return 0.0 (neutral parity; no odd/even bonus)
  - FIX paksha_bala: Moon's result multiplied ×2 (BPHS doubling rule; max 120 virupas)
  - FIX hora_bala: proportional temporal horas (unequal day/night lengths); sunset_hour param added
  - REWRITE ayana_bala: per-planet tropical declination formula; Sun/Mars/Jup/Ven north-strong;
    Moon/Saturn south-strong; Mercury uses abs(dec); Sun DOUBLED (max 120); planet_trop_lon param added
  - REWRITE cheshta_bala: Seeghrocha classical formula primary (true_lon param); speed-state fallback;
    Sun/Moon stubs → 0.0 (caller overrides with Ayana/Paksha); _SEEGHROCHA constants added
  - ADD compute_yuddha_adjustments: Planetary War mass-transfer (Bimba Parimana diff); _BIMBA_PARIMANA dict
  - UPDATE kala_bala: passes sunset_hour + planet_trop_lon + yuddha_adjustment; signature expanded
  - UPDATE compute_shadbala: Sun Cheshta = Ayana; Moon Cheshta = Paksha; planet_trop_lon + yuddha_adjustment params
  - UPDATE compute_all_shadbala: computes tropical lons (sidereal + ayanamsa via get_ayanamsa());
    pre-computes yuddha adjustments; passes both to per-planet compute_shadbala
