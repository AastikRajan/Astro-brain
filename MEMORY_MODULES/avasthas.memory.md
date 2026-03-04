```markdown
# Module: vedic_engine/analysis/avasthas.py
## Last Updated: 2026-03-02 (Phase 1B)
## Status: NEW

## PURPOSE
Three-system Avastha (planetary state) computation for per-planet dignity and
strength multipliers. Results stored in `static["computed"]["avasthas"]`.

## KEY FUNCTIONS

### compute_baladi_avasthas(planet_lons) → Dict[str, Dict]
- **Purpose:** 5-state / 6°-segment system for each planet within its sign
- **States:** Bala (infancy), Kumara (youth), Yuva (prime), Vriddha (old), Mrita (dead)
- **Multipliers:** Yuva=1.0, Kumara=0.75, Bala=0.5, Vriddha=0.25, Mrita=0.0
- **ODD sign order:** Bala→Kumara→Yuva→Vriddha→Mrita (ascending degree segments)
- **EVEN sign order:** reversed — Mrita→Vriddha→Yuva→Kumara→Bala
- **Planet overrides:** SUN/MARS peak at Bala (Bala→1.0); MOON/SAT peak at Vriddha (Vriddha→1.0); MERCURY=always 1.0
- **Returns:** `{planet: {avastha, multiplier, sign_idx, segment}}`

### compute_shayanadi_avasthas(planet_lons, moon_lon, lagna_sign, birth_dt, sunrise_hour) → Dict
- **Purpose:** 12-state complex formula using 6 weighted input variables
- **Formula:** `I_p = (N_p × P_p × NA_p × N_m × IG × L) % 12`
  - `N_p` = nakshatra index of planet (0–26)
  - `P_p` = planet index (SUN=1…SAT=7, RAHU=8, KETU=9)
  - `NA_p` = navamsha of planet (1–9)
  - `N_m` = nakshatra index of Moon
  - `IG` = Ishta Ghati = elapsed ghatika from sunrise (24 secs intervals)
  - `L` = lagna sign + 1 (1–12)
  - 0 maps to state 12 (Nidra); order: Shayana→Upaveshana→Netrapani→Prakashana→Gamana→Agamana→Sabha→Agama→Bhojana→Nritya/Lila→Kautuka→Nidra
- **Sub-state:** `S_p = ((I_p² + anka) % 12 + D_p) % 3` → {0:Vicheshta, 1:Drishti, 2:Cheshta}
- **Returns:** `{planet: {avastha, base_index, sub_state, sub_multiplier, ishta_ghati}}`

### compute_deeptadi_avasthas(planet_dignities, planet_lons, sun_lon, malefic_conjunctions) → Dict
- **Purpose:** 9-state dignity-hierarchy avastha (Deepta = highest, Kopa = lowest)
- **Hierarchy (top→bottom):** Deepta → Swastha → Pramudita → Shanta → Dina → Dukhita → Khala → Vikala → Kopa
- **State assignment logic:**
  - Combust (within orb of Sun) → Kopa (orbs: Moon=12°, Mars=17°, Mer=14°, Jup=11°, Ven=10°, Sat=15°)
  - Malefic conjunction in same house → Vikala
  - Debilitated: Khala; Neutral sign: Dukhita; Enemy sign: Dina; Great Friend sign: Shanta
  - Friend sign: Pramudita; Own sign: Swastha; Exalted: Deepta
- **Returns:** `{planet: {avastha, condition, multiplier, dignity, combust_pct}}`

### compute_all_avasthas(planet_lons, planet_dignities, moon_lon, sun_lon, lagna_sign, birth_dt, sunrise_hour, malefic_conjunctions) → Dict
- **Purpose:** Master function returning all 3 avastha systems
- **Returns:** `{"baladi": {...}, "shayanadi": {...}, "deeptadi": {...}}`
- **Storage key:** `static["avasthas"]`

## DEPENDENCIES
- `vedic_engine.core.coordinates.sign_of`, `normalize`
- No external ephemeris required (all formula-based)

## INTEGRATION
- Called by `engine.py:analyze_static()` after Graha Yuddha block
- `compute_all_avasthas` imported at top of engine.py (line 46)
- Stored in returned static dict under `"avasthas"` key

## RECENT CHANGES
- 2026-03-02 Phase 1B: Module created — 3 avastha systems (Baladi, Shayanadi, Deeptadi)
```
