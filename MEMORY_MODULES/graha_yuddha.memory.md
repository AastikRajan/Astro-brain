# Module: graha_yuddha.py
## Last Updated: 2026-03-02

## PURPOSE
Detects Graha Yuddha (Planetary War) — when two planets (excluding Sun, Moon, Rahu, Ketu) are within 1° of each other in the same sign. The planet with lower longitude wins; the loser has significantly weakened effects during its dasha. Applies war penalties to shadbala ratios used in prediction.

## KEY FUNCTIONS

### detect_planetary_wars(planet_longitudes) → List[dict]
- **Purpose:** Find all pairs of planets currently in war
- **Inputs:** planet longitudes dict
- **Returns:** List of `{winner, loser, separation_degrees, sign}`
- **Called by:** `engine.py:analyze_static()`

### apply_war_penalties(shadbala_ratios, war_results) → Dict[str, float]
- **Purpose:** Reduce shadbala ratios of Graha Yuddha losers
- **Inputs:** current shadbala ratios, war detection results
- **Returns:** Modified shadbala ratios dict
- **Called by:** `engine.py:analyze_static()`

## IMPORTANT CONSTANTS
War threshold: 1° separation in same sign. Eligible planets: MARS, MERCURY, JUPITER, VENUS, SATURN only.

## DEPENDENCIES
config.py, coordinates.py

## RECENT CHANGES
- 2026-03-02: No changes (stable module)
