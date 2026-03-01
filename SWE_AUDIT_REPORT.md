# Swiss Ephemeris (pyswisseph) Leverage Audit — Complete Report

> **Scope**: Every `.py` file under `vedic_engine/` (79 files)  
> **Goal**: Find every place where SWE could increase accuracy but is NOT currently used  
> **Bridge module**: `vedic_engine/core/swisseph_bridge.py` (692 lines) — already provides `swe.calc_ut()`, `swe.houses()`, `swe.get_ayanamsa()`, `swe.rise_trans()` (unused!), planet speeds, solar return, Graha Yuddha precise detection  

---

## Priority Legend

| Priority | Meaning |
|----------|---------|
| **P0 – CRITICAL** | Directly corrupts dasha timelines, sublord assignments, or multi-year predictions |
| **P1 – HIGH** | Measurable accuracy degradation (>0.1° or >2 min) in a frequently-used module |
| **P2 – MEDIUM** | Hardcoded approximation where SWE could give exact value; affects secondary scoring |
| **P3 – LOW** | Theoretical improvement; module already receives good-enough input or is a fallback tier |

---

## FINDING 1 — `sunrise_utils.py`: NOAA Algorithm Instead of SWE `rise_trans()`

| Field | Value |
|---|---|
| **File** | `vedic_engine/core/sunrise_utils.py` |
| **Lines** | L27–L100 (entire sunrise/sunset algorithm) |
| **Priority** | **P0 – CRITICAL** |
| **Current approach** | NOAA / Spencer algorithm (pure Python trig). Accuracy: ±2 minutes. Default fallback parameters used by `special_points.py` are **sunrise=6:00 AM, sunset=6:00 PM** when this module isn't called. |
| **What SWE replaces** | `swe.rise_trans()` computes topocentric sunrise/sunset to ±1 second precision using refraction + altitude + lat/lon. Already available in the installed pyswisseph. |
| **Impact** | Affects: Shadbala (Tribhaga Bala, Hora Bala, Nathonnatha Bala), Gulika/Mandi longitude, Hora Lagna, Ghati Lagna, day/night birth classification, conditional dasha eligibility, Muhurta windows. A 2-minute sunrise error shifts Hora Bala assignment at the boundary by one planetary hour (~15° Lagna motion). |
| **Recommended fix** | Add `compute_sunrise_swe(jd, lat, lon, alt=0)` wrapper in `swisseph_bridge.py` calling `swe.rise_trans(jd, swe.SUN, geopos, rsmi=swe.CALC_RISE|swe.BIT_DISC_CENTER)`. Replace all callers. |

---

## FINDING 2 — `shadbala.py`: Multiple Hardcoded Sunrise/Time Approximations

| Field | Value |
|---|---|
| **File** | `vedic_engine/strength/shadbala.py` |
| **Priority** | **P0 – CRITICAL** (hora_bala, tribhaga_bala), **P2** (ayana_bala, abda_bala) |

### 2a. `hora_bala()` — Lines L303–L315
- **Current**: `hora_num = int(max(0, hour - 6))` — assumes sunrise = 6:00 AM exactly
- **Fix**: Accept actual SWE-computed sunrise time; `hora_num = int(max(0, hour - sunrise_hour))`

### 2b. `tribhaga_bala()` — Lines L333–L353
- **Current**: `if 6 <= hour < 18:` with 4-hour thirds — assumes 12hr day from 6AM–6PM
- **Fix**: Use actual sunrise/sunset to compute unequal Tribhaga thirds (classical method)

### 2c. `ayana_bala()` — Lines L356–L376
- **Current**: Month-based approximation for solar declination strength
- **Fix**: Compute actual solar declination via `swe.calc_ut(jd, swe.SUN)` → ecliptic latitude → declination formula = `sin(lon) × sin(obliquity)`

### 2d. `abda_bala()` — Lines L322–L330
- **Current**: Approximates Mesha Sankranti (Sun entering Aries) as April 14 every year
- **Fix**: Use SWE to find exact moment Sun's sidereal longitude = 0° (binary search on `swe.calc_ut()`)

### 2e. `masa_bala()` — Lines L332–L345
- **Current**: `birth_dt - deg_in_sign days` to approximate solar ingress
- **Fix**: Same as abda_bala — compute exact ingress via SWE

### 2f. `cheshta_bala()` — Lines L464–L500
- **Current**: Hardcoded `_AVG_SPEED` dict for mean daily speeds
- **Fix**: SWE bridge already provides actual daily speeds via `swe.calc_ut()` flag `swe.FLG_SPEED`; `swisseph_bridge.get_transit_speeds_swe()` already exists but isn't called here

---

## FINDING 3 — `coordinates.py`: Manual Topocentric Moon Parallax

| Field | Value |
|---|---|
| **File** | `vedic_engine/core/coordinates.py` |
| **Lines** | L148–L260 (`topocentric_moon_correction()`) |
| **Priority** | **P1 – HIGH** |
| **Current approach** | IAU simplified topocentric correction using `MOON_MEAN_DISTANCE_KM = 384400.0` (constant). Does not account for orbital eccentricity (distance varies 356,500–406,700 km = ±7% range). |
| **What SWE replaces** | `swe.calc_ut(jd, swe.MOON)` returns actual Earth-Moon distance in AU as result[2]. Also, `swe.calc_ut()` with `swe.FLG_TOPOCTR` flag + `swe.set_topo(lon, lat, alt)` computes **fully topocentric** Moon longitude directly — no manual parallax math needed. |
| **Impact** | Moon longitude error up to ~0.05° from wrong parallax. In Kalachakra Dasha, this can flip the pada entirely. In KP, it can change the sublord (smallest span ~0.667°). |
| **Recommended fix** | Add `swe.set_topo(lon, lat, alt)` + `swe.FLG_TOPOCTR` to the bridge. Deprecate manual parallax. |

---

## FINDING 4 — `lunations.py`: Uses PyEphem + Hardcoded Ayanamsa

| Field | Value |
|---|---|
| **File** | `vedic_engine/analysis/lunations.py` |
| **Lines** | L30–L80 (position computation), L53 (ayanamsa formula) |
| **Priority** | **P1 – HIGH** |
| **Current approach** | Uses `ephem.Moon()` and `ephem.Sun()` for positions. Lahiri ayanamsa hardcoded as `23.85 + days * (50.288 / (3600.0 * 365.25))` — a linear approximation that diverges from the official Lahiri value by ~0.01° per decade. Eclipse detection uses approximate node distance. |
| **What SWE replaces** | `swe.calc_ut()` for Moon/Sun positions + `swe.get_ayanamsa_ut()` for official Lahiri. SWE also has `swe.sol_eclipse_when_loc()` and `swe.lun_eclipse_when()` for **precise** eclipse computation. |
| **Impact** | Moon/Sun position errors and ayanamsa drift affect Tithi boundary timing, eclipse detection accuracy, and lunation significance scoring. |

---

## FINDING 5 — `transits.py`: Hardcoded Mean Speeds, Approximate Positions, Ephem Tier Hardcodes Ayanamsa

| Field | Value |
|---|---|
| **File** | `vedic_engine/prediction/transits.py` |
| **Priority** | **P2 – MEDIUM** (tier cascade already prefers SWE when available) |

### 5a. Lines L57–L79: `MEAN_SPEEDS` and `APPROX_POSITIONS_FEB2026`
- **Current**: Hardcoded mean daily speeds and a Feb 2026 reference snapshot as last-resort fallback
- **Risk**: Outer planets (Jupiter retrograde: −0.12°/day vs mean +0.083°/day) can be off by **10+ degrees** within a few months
- **Fix**: At minimum, cache a SWE-computed position snapshot at engine init time; ideally, never fall to this tier

### 5b. `_get_positions_ephem()` — Line L141
- **Current**: Hardcodes Lahiri as `23.8557 + days * (50.3 / (3600 * 365.25))`
- **Fix**: Use `swe.get_ayanamsa_ut()` or at least the same formula constant across all backends

### 5c. Rahu computation in ephem tier — Lines L155–L162
- **Current**: Meeus formula for mean lunar node
- **Fix**: SWE computes True Node (`swe.TRUE_NODE`) which includes periodic perturbations (±1.5° from mean)

---

## FINDING 6 — `skyfield_positions.py`: Hardcoded Ayanamsa + Meeus Rahu

| Field | Value |
|---|---|
| **File** | `vedic_engine/prediction/skyfield_positions.py` |
| **Lines** | L119 (`_lahiri_ayanamsa`), L130 (`_rahu_tropical`) |
| **Priority** | **P2 – MEDIUM** |
| **Current approach** | Linear Lahiri: `23.85 + days * (50.288 / 3600 / 365.25)`. Rahu via Meeus. |
| **What SWE replaces** | `swe.get_ayanamsa_ut()` for Lahiri. `swe.calc_ut(jd, swe.TRUE_NODE)` for True Rahu. |
| **Impact** | This is the **audit backend** — systematic bias in the reference corrupts the audit's ability to detect drift in other backends. |

---

## FINDING 7 — `astropy_positions.py`: Same Hardcoded Ayanamsa + Meeus Rahu

| Field | Value |
|---|---|
| **File** | `vedic_engine/prediction/astropy_positions.py` |
| **Lines** | L14–L19 (Lahiri formula), L22–L34 (Meeus Rahu) |
| **Priority** | **P2 – MEDIUM** |
| **Current approach** | Identical linear Lahiri formula and Meeus Rahu as skyfield_positions.py |
| **Fix**: When SWE is installed, import `get_ayanamsa` from bridge for consistent ayanamsa. Add a check: `try: from swisseph_bridge import get_ayanamsa; except: use formula` |

---

## FINDING 8 — `skyfield_audit.py`: Hardcoded Lahiri + Meeus Rahu in Audit Module

| Field | Value |
|---|---|
| **File** | `vedic_engine/core/skyfield_audit.py` |
| **Lines** | L79–L82 (Lahiri constants), L226–L240 (Rahu Meeus) |
| **Priority** | **P2 – MEDIUM** |
| **Same issue as Finding 6/7** — linear Lahiri approximation in the cross-validation module. |

---

## FINDING 9 — `special_points.py`: Default sunrise=6.0, sunset=18.0 Throughout

| Field | Value |
|---|---|
| **File** | `vedic_engine/analysis/special_points.py` |
| **Lines** | L73, L108, L118, L134, L275, L295 (all function signatures default `sunrise_hour=6.0, sunset_hour=18.0`) |
| **Priority** | **P1 – HIGH** |
| **Current approach** | `compute_gulika()`, `compute_hora_lagna()`, `compute_ghati_lagna()`, `compute_mandi()` all default sunrise/sunset to 6:00/18:00 if the caller doesn't pass actual values. |
| **Impact** | Gulika/Mandi longitude is wrong by ~7.5° per hour of sunrise error (Lagna moves 15°/hr, and the Prahara offset multiplies it). At latitudes >30° in summer, sunrise can be 4:30 AM — a 1.5hr error → ~22° Gulika error → wrong sign entirely. |
| **Fix**: Compute actual sunrise/sunset via SWE `rise_trans()` as described in Finding 1, and pass to all these functions. |

---

## FINDING 10 — All Nakshatra-Based Dasha Systems: Moon Longitude Precision Dependency

| Field | Value |
|---|---|
| **Files** | `vimshottari.py`, `ashtottari.py`, `yogini.py`, `conditional_dashas.py`, `kalachakra.py` |
| **Priority** | **P0 – CRITICAL** (caller responsibility — these modules accept longitude as input) |

### Current state
All dasha calculations use `moon_longitude % NAKSHATRA_SPAN` or `moon_longitude % PADA_SPAN` to compute the **dasha balance** at birth. The modules themselves are mathematically correct — but their output precision is **entirely dependent** on the Moon longitude precision of their input.

### Quantified impact
| Dasha System | Sensitive Span | Moon Error → Timeline Shift |
|---|---|---|
| **Vimshottari** (L33–44) | 13.333° nakshatra | 0.1° error → ~2.5 days/year of period |
| **Kalachakra** (L20–40) | 3.333° pada | 0.05° error → can **flip entire pada sequence** |
| **KP sublord** (L50–80) | 0.667° min sub | 0.03° error → **wrong sublord** |
| **Ashtottari** | 13.333° | Same as Vimshottari |
| **Yogini** | 13.333° | Same as Vimshottari pattern |
| **Conditional Dashas** (10 systems) | 13.333° | Same Moon sensitivity |

### Recommendation
Ensure the **entire pipeline** feeds SWE-computed Moon longitude (with topocentric correction per Finding 3) into all dasha calculations. Add a validation check at the `PredictionEngine.predict()` entry point that confirms Moon longitude came from SWE tier 1.

---

## FINDING 11 — `graha_yuddha.py`: Hardcoded Disc Circumferences

| Field | Value |
|---|---|
| **File** | `vedic_engine/analysis/graha_yuddha.py` |
| **Lines** | L15–L22 (`DISC_CIRCUMFERENCE_ARCSEC`) |
| **Priority** | **P2 – MEDIUM** |
| **Current approach** | Hardcoded apparent disc diameters: Mars=9.4″, Mercury=6.6″, Jupiter=190.4″, Venus=16.6″, Saturn=158.0″. These are **mean** values; actual apparent diameter varies 2:1 for Mars (3.5″ at aphelion vs 25″ at opposition). |
| **What SWE replaces** | `swe.calc_ut(jd, planet)` returns distance in AU. Apparent diameter = `angular_diameter_at_1AU / distance_AU`. The bridge already has `detect_graha_yuddha_precise()` using ecliptic latitude. |
| **Fix**: Use `swisseph_bridge.detect_graha_yuddha_precise()` and compute actual apparent disc diameters from SWE distances. |

---

## FINDING 12 — `aspect_transits.py` + `dasha_transit.py` + `timing_optimizer.py`: Hardcoded Mean Speeds

| Field | Value |
|---|---|
| **Files & Lines** | `aspect_transits.py` L68–L79, `dasha_transit.py` L82–L92, `timing_optimizer.py` L109–L120 |
| **Priority** | **P2 – MEDIUM** |
| **Current approach** | All three files define their own `MEAN_SPEED` / `MEAN_SPEED_PER_DAY` / `_MEAN_MOTION` dicts with identical hardcoded average daily speeds. Used for: applying/separating detection, next-sign-change estimation, approximate future position extrapolation. |
| **What SWE replaces** | `swisseph_bridge.get_transit_speeds_swe(dt)` returns actual speeds for the specific date. Actual vs mean divergence: Mercury can be −1.4°/day (retrograde) vs +1.38°/day mean. Mars ranges 0.3–0.8°/day. |
| **Impact** | `_is_applying()` in aspect_transits.py misidentifies applying vs separating when a planet is retrograde. `days_to_next_sign_change()` in dasha_transit.py can be off by weeks for Mercury/Venus retrogrades. The timing_optimizer extrapolates positions months ahead with mean motion — Jupiter/Saturn are reasonably close, but inner planets diverge rapidly. |
| **Fix**: Import `get_transit_speeds_swe()` from the bridge (it already exists!). For timing_optimizer's multi-month lookahead, compute positions at each date via SWE instead of linear extrapolation. |

---

## FINDING 13 — `varshaphala.py`: Duplicated Astronomical Constants

| Field | Value |
|---|---|
| **File** | `vedic_engine/timing/varshaphala.py` |
| **Lines** | L40–L80 (`EXALT_SIGN`, `OWN_SIGNS`, `DEBILITATION_DEGREES`, `_SIGN_LORD_NAMES`), L165–175 |
| **Priority** | **P3 – LOW** (data duplication, not a direct SWE issue) |
| **Current approach** | Maintains its own copy of exaltation degrees, debilitation degrees, own signs, and sign lords — separate from `config.py` canonical tables. The Tajika Hudda/Drekkana scoring uses these local copies. |
| **Risk** | If `config.py` tables are corrected, `varshaphala.py` won't pick up the fix. |
| **Fix**: Import from `config.py` instead of duplicating. Not an SWE issue per se, but relates to data consistency. |

---

## FINDING 14 — `panchanga.py`: No End-Time Computation for Tithi/Nakshatra

| Field | Value |
|---|---|
| **File** | `vedic_engine/timing/panchanga.py` |
| **Lines** | L1–L200 (computes instantaneous Panchanga only) |
| **Priority** | **P2 – MEDIUM** |
| **Current approach** | Computes Tithi, Nakshatra, Yoga, Karana at a single moment from given Sun/Moon longitudes. Does NOT compute when the current Tithi/Nakshatra ends (the boundary crossing time). |
| **What SWE enables** | Iteratively call `swe.calc_ut()` to binary-search the exact moment when `(Moon_lon - Sun_lon) mod 12° = 0` (next Tithi boundary) or `Moon_lon mod 13.333° = 0` (next Nakshatra boundary). Precision: sub-second. |
| **Impact** | Users need "Tithi ends at HH:MM" for Muhurta selection and fasting observance. Currently only the `jyotishganit_bridge` provides this. |

---

## FINDING 15 — `varshaphala.py`: Solar Return Computed Elsewhere but Tajika Aspects Need Precise Longitudes

| Field | Value |
|---|---|
| **File** | `vedic_engine/timing/varshaphala.py` |
| **Lines** | L800+ (Tajika Yoga detection uses longitude differences) |
| **Priority** | **P2 – MEDIUM** |
| **Current approach** | Tajika aspects (Ithasala, Ishraffa, etc.) depend on speed and longitude difference between planets. The module accepts longitudes as input. The `swisseph_bridge.compute_solar_return()` already provides precise solar return positions. |
| **Risk** | If the caller passes non-SWE positions, Tajika aspect direction (faster/slower planet classification) could be wrong, flipping Ithasala to Ishraffa. |
| **Fix**: Ensure `compute_varsha_analysis()` always receives SWE-computed positions for both the solar return chart and natal chart. |

---

## FILES WITH NO SWE IMPROVEMENTS NEEDED

These files were reviewed and found to be **pure logic / lookup / scoring** modules that don't compute astronomical positions:

| File | Reason |
|---|---|
| `config.py` | Static enum/lookup tables — no computation |
| `aspects.py` | House-based Parashari Drishti (integer house offsets) |
| `divisional.py` | Pure math varga formulas from longitude input |
| `timezone_utils.py` | Timezone resolution (geopolitical, not astronomical) |
| `ashtakvarga.py` | Sign-index BAV/SAV scoring rules |
| `vimshopak.py` | Vimshopak Bala from varga sign dignities |
| `bhavabala.py` | House strength combining lord Shadbala + fixed table |
| `yogas.py` | Yoga detection from house/sign placements |
| `compatibility.py` | Ashtakoota scoring from nakshatra/sign indices |
| `karakas.py` | Jaimini Chara Karaka ranking (degree within sign) |
| `karakamsha.py` | Karakamsha chart analysis (sign-based logic) |
| `arudha_padas.py` | Arudha computation (sign-lord-based) |
| `special_degrees.py` | Mrityu Bhaga / Gandanta / Pushkara (lookup tables) |
| `rashi_drishti.py` | Jaimini sign-based aspects (pure sign logic) |
| `dispositor.py` | Dispositor chain tracing (sign-lord logic) |
| `functional.py` | Functional benefic/malefic classification |
| `significations.py` | Planet-to-domain mapping (house logic) |
| `panchadha_maitri.py` | 5-fold friendship computation |
| `remedial.py` | Remedy prescription tables |
| `nakshatra_analysis.py` | Nakshatra data tables and Tarabala |
| `promise.py` | Three Pillar Rule scoring |
| `confidence.py` | Multi-system confidence aggregation |
| `fuzzy_confidence.py` | Fuzzy logic confidence layer |
| `bayesian_layer.py` | Bayesian confidence update |
| `calibration.py` | Confidence calibration |
| `dasha_quality.py` | Ishta/Kashta Phala + maturity ages |
| `dasha_transit.py` | Gochar scoring (accepts positions as input) |
| `chara_dasha.py` | Jaimini Chara Dasha (sign-based periods) |
| `jaimini_dashas.py` | 7 Jaimini dasha systems (sign-based) |
| `progressions.py` | Secondary progressions (uses `position_fn` callback) |
| `muhurta.py` | Muhurta scoring (consumes Panchanga output) |
| `varga_analysis.py` | Divisional chart interpretation |
| `argala.py` | Argala (obstruction) analysis |
| `badhaka.py` | Badhaka house analysis |
| `career_checklist.py` | Career analysis checklist |
| `marriage_synthesis.py` | Marriage timing synthesis |
| `medical_astrology.py` | Medical astrology analysis |
| `data/models.py` | Dataclass definitions |
| `data/loader.py` | JSON data loading |
| `data/nakshatra_db.py` | Nakshatra metadata |
| `ai/*.py` | GPT/AI interpretation layers |
| `ml/ml_pipeline.py` | ML pipeline |
| `ephemeris_audit.py` | Cross-backend comparison (uses backends as-is) |
| `engine.py` | Pipeline orchestrator (delegates to all modules) |

---

## SUMMARY TABLE — All Findings by Priority

| # | File(s) | Issue | Priority | Effort |
|---|---------|-------|----------|--------|
| 1 | `sunrise_utils.py` | NOAA algorithm → `swe.rise_trans()` | **P0** | Small |
| 2a | `shadbala.py` L303 | `hora_bala()` sunrise=6AM | **P0** | Small |
| 2b | `shadbala.py` L333 | `tribhaga_bala()` hardcoded 6AM–6PM | **P0** | Small |
| 10 | `vimshottari.py`, `kalachakra.py`, `kp.py`, `ashtottari.py`, `yogini.py`, `conditional_dashas.py` | Moon longitude precision gate (caller responsibility) | **P0** | Medium |
| 3 | `coordinates.py` L148 | Manual Moon parallax with mean distance | **P1** | Medium |
| 4 | `lunations.py` L30 | PyEphem + hardcoded Lahiri ayanamsa | **P1** | Medium |
| 9 | `special_points.py` | Default sunrise=6.0 in Gulika/Mandi/Hora/Ghati | **P1** | Small |
| 2c | `shadbala.py` L356 | `ayana_bala()` month-based declination | **P2** | Small |
| 2d | `shadbala.py` L322 | `abda_bala()` Mesha Sankranti ≈ Apr 14 | **P2** | Medium |
| 2e | `shadbala.py` L332 | `masa_bala()` approximate ingress | **P2** | Medium |
| 2f | `shadbala.py` L464 | `cheshta_bala()` hardcoded avg speeds | **P2** | Small |
| 5a | `transits.py` L57 | Hardcoded mean speeds + approx positions fallback | **P2** | Medium |
| 5b | `transits.py` L141 | Ephem tier hardcoded Lahiri ayanamsa | **P2** | Small |
| 5c | `transits.py` L155 | Ephem tier Meeus mean node (not True Node) | **P2** | Small |
| 6 | `skyfield_positions.py` L119 | Hardcoded Lahiri + Meeus Rahu | **P2** | Small |
| 7 | `astropy_positions.py` L14 | Hardcoded Lahiri + Meeus Rahu | **P2** | Small |
| 8 | `skyfield_audit.py` L79 | Hardcoded Lahiri + Meeus Rahu in audit | **P2** | Small |
| 11 | `graha_yuddha.py` L15 | Hardcoded disc circumferences | **P2** | Small |
| 12 | `aspect_transits.py`, `dasha_transit.py`, `timing_optimizer.py` | 3× duplicated mean speed dicts | **P2** | Small |
| 14 | `panchanga.py` | No Tithi/Nakshatra end-time computation | **P2** | Medium |
| 15 | `varshaphala.py` L800+ | Tajika aspects need SWE speeds for direction | **P2** | Small |
| 13 | `varshaphala.py` L40 | Duplicated astronomical constants | **P3** | Small |

---

## RECOMMENDED IMPLEMENTATION ORDER

### Phase 1 — Critical Path (eliminates largest error sources)
1. **Add `swe.rise_trans()` wrapper** to `swisseph_bridge.py`
2. **Wire SWE sunrise/sunset** into `shadbala.py` hora_bala + tribhaga_bala
3. **Wire SWE sunrise/sunset** into `special_points.py` Gulika/Mandi/Hora Lagna/Ghati Lagna
4. **Add `swe.FLG_TOPOCTR` Moon** to bridge → deprecate manual parallax in `coordinates.py`
5. **Add pipeline validation** in `engine.py` to guarantee Moon longitude from SWE

### Phase 2 — High-Value Improvements
6. **Replace PyEphem** in `lunations.py` with SWE positions + `swe.get_ayanamsa_ut()`
7. **Add `swe.sol_eclipse_when_loc()`** for precise eclipse detection
8. **Unify ayanamsa** across all backends: `skyfield_positions.py`, `astropy_positions.py`, `skyfield_audit.py`, `transits.py` ephem tier — all should call `swisseph_bridge.get_ayanamsa()` when SWE is available

### Phase 3 — Precision Polish
9. **Replace mean speeds** in `aspect_transits.py`, `dasha_transit.py`, `timing_optimizer.py` with `get_transit_speeds_swe()`
10. **Use SWE True Node** instead of Meeus Mean Node in all fallback backends
11. **Compute actual apparent disc diameters** from SWE distance in `graha_yuddha.py`
12. **Add Panchanga end-time computation** using SWE iterative search
13. **Consolidate duplicated constants** in `varshaphala.py` → import from `config.py`

---

## ARCHITECTURE NOTE

The `swisseph_bridge.py` module already has most of the SWE capabilities needed. The primary gap is:

1. **`swe.rise_trans()` is not exposed** — no sunrise/sunset wrapper exists
2. **`swe.FLG_TOPOCTR` is not used** — topocentric positions not available
3. **`swe.get_ayanamsa_ut()` is used internally** but not exported for other backends to call
4. **Eclipse functions** (`swe.sol_eclipse_when_loc()`, `swe.lun_eclipse_when()`) are not exposed

Adding these 4 capabilities to the bridge would enable all 15 findings to be resolved through the existing architecture without restructuring.
