# Module: aspects.py
## Last Updated: 2026-03-02

## PURPOSE
Computes Drik Bala (aspectual strength) — the strength each planet gains from aspects of other planets. Implements Parashari graha drishti: all planets have 7th house full aspect; MARS has 4th and 8th; JUPITER has 5th and 9th; SATURN has 3rd and 10th. Weighted by aspecting planet's strength.

## KEY FUNCTIONS

### compute_all_drik_bala(planet_houses, shadbala_results) → Dict[str, float]
- **Purpose:** Drik Bala for all planets
- **Returns:** dict planet → net drik bala virupa score
- **Called by:** `engine.py:analyze_static()`

### get_aspect_map(planet_houses) → Dict[str, List[str]]
- **Purpose:** Build map of which planets each planet aspects
- **Returns:** dict planet → list of aspected planets
- **Called by:** `engine.py:analyze_static()`, `yogas.py`

## IMPORTANT CONSTANTS
Special aspect houses: MARS=[4,7,8], JUPITER=[5,7,9], SATURN=[3,7,10]. All others=[7].

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: No changes (stable)
