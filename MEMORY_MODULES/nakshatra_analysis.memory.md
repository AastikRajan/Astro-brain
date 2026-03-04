# Module: nakshatra_analysis.py
## Last Updated: 2026-03-02

## PURPOSE
Provides deeper analysis of nakshatra placements beyond basic identification. Analyzes the natal Moon nakshatra for Tarabala scoring setup, planetary nakshatra lords for timing quality, and nakshatra-based compatibility and prediction modifiers.

## KEY FUNCTIONS

### compute_nakshatra_analysis(planet_longitudes, birth_date) → dict
- **Purpose:** Full nakshatra quality analysis for all planets
- **Returns:** dict planet → `{nakshatra, lord, pada, quality, deity, nature, gana}`
- **Called by:** `engine.py:analyze_static()`

## DEPENDENCIES
nakshatra_db.py, config.py

## RECENT CHANGES
- 2026-03-02: No changes
