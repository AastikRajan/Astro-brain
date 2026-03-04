# Module: yogas.py
## Last Updated: 2026-03-02

## PURPOSE
Detects and scores classical planetary combinations (yogas) from the natal chart. Implements ~30+ major yogas across categories: Pancha Mahapurusha, Raja, Dhana, Nabhasa, and simple yogas. Each yoga has a detection predicate, strength modifier (via Shadbala), cancellation check (combustion/debilitation/malefic aspect), and domain tags for routing to the confidence scorer.

## KEY FUNCTIONS

### detect_all_yogas(planet_houses, planet_signs, shadbala_ratios, ...) → List[YogaResult]
- **Purpose:** Detect all yoga conditions in the natal chart
- **Inputs:** planet placement dicts, shadbala ratios, lagna sign, aspect map
- **Returns:** List of YogaResult dataclass objects
- **Called by:** `engine.py:analyze_static()`
- **Calls:** Individual yoga detector functions

### compute_yoga_compounding(yoga_results, domain) → dict
- **Purpose:** Compute domain-filtered yoga score with compounding
- **Inputs:** yoga_results list, domain str
- **Returns:** `{domain_score, active_yogas, compounding_tier, stacking_bonus}`
- **Called by:** `confidence.py` (via engine injection)
- **Key logic:** Tiered compounding — multiple Raja/Dhana yogas stack non-linearly

### compute_dhana_stacking_tier(yoga_results) → int
- **Purpose:** Determine wealth yoga stacking tier (1–4)
- **Called by:** `engine.py`

### score_md_ad_relationship(md_planet, ad_planet, yoga_results) → float
- **Purpose:** Score the synergy between Maha and Antar dasha lords in active yogas
- **Called by:** `engine.py:predict()`

### get_manduka_gati_life_phase(age, yoga_results) → dict
- **Purpose:** Determine life phase based on Manduka Gati planetary maturity
- **Called by:** `engine.py`

## IMPORTANT CONSTANTS
- `YogaResult` dataclass: name, category, detected, strength, planets, houses, description, tier, activation_score
- Yoga tiers: 1=Pancha Mahapurusha, 2=Raja, 3=Dhana, 4=Simple
- `PLANET_NAMES_7` — the 7 grahas (no nodes) for yoga detection

## DEPENDENCIES
config.py (Planet, NATURAL_BENEFICS, EXALTATION_DEGREES, SIGN_LORDS, etc.), coordinates.py

## RECENT CHANGES
- 2026-03-02: Added score_md_ad_relationship() for dasha quality scoring
- 2026-03-02: Added get_manduka_gati_life_phase()
- 2026-03-02: Expanded yoga tier and activation_score fields to YogaResult
- 2026-03-02 [Phase 1D]: Added has_sambandha(planet_a, planet_b, planet_houses, planet_lons, house_lords, asp_map) → bool
  - Checks: conjunction (same house), mutual aspect (asp_map), parivartana (sign exchange via SIGN_LORDS)
- 2026-03-02 [Phase 1D]: Added grade_yoga(yoga_planets, planet_houses, planet_lons, shadbala_ratios, asp_map) → {grade, score}
  - S (1.0): exalted/moolatrikona + kendra/trikona + not combust
  - A (0.75): own sign or avg shadbala >= 1.0 + kendra/trikona
  - B (0.50): avg shadbala >= 0.7, not in dusthana
  - C (0.25): default fallback
- 2026-03-02 [Phase 1D]: Added _daridra_yogas() — L11/L2 in dusthana (6/8/12); Kemadruma as subtype; Viparita override if lord also rules dusthana
- 2026-03-02 [Phase 1D]: Added _aristha_yogas() — Balarishta cases: (a) Moon in dusthana+malefic asp, (b) Moon+Rahu/Ketu conj, (c) Luminaries+node; Bhanga via Jupiter in H1
- 2026-03-02 [Phase 1D]: Added _pravrajya_yogas() — 4+ planets in sign; flavor from highest Shadbala; Ketu 12th+L5/L9/Jup asp bonus; combust cancel
- 2026-03-02 [Phase 1D]: Added compute_all_extended_yogas() — master function returning List[Dict] in unified Phase 1D.9 format
  - Combines detect_all_yogas() + daridra + aristha + pravrajya, applies grade_yoga() to each, converts to {name, type, planets, grade, score, domain, active, cancellation}
  - Stored in static["computed"]["yogas"] via engine.py

## UNIFIED YOGA FORMAT (Phase 1D.9)
```python
{
    "name": str,        # yoga name
    "type": str,        # raj/dhana/daridra/aristha/nabhasa/pravrajya/etc.
    "planets": List[str],
    "grade": str,       # S/A/B/C
    "score": float,     # 1.0/0.75/0.5/0.25
    "domain": str,      # career/finance/health/spiritual/general
    "active": bool,     # False if cancellation_reason set
    "cancellation": str|None
}
```
