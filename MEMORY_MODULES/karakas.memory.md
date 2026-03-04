# Module: karakas.py
## Last Updated: 2026-03-02

## PURPOSE
Computes Chara Karakas (variable significators) — the 7 or 8 planets ranked by degree within sign, from Atmakaraka (highest degree) down to Darakaraka (lowest). Also analyzes karaka relationships in the D9 chart and identifies which planets carry the karaka role for each domain.

## KEY FUNCTIONS

### compute_chara_karakas(planet_longitudes) → dict
- **Purpose:** Rank planets by degree-in-sign to assign 7 Chara Karaka roles
- **Inputs:** planet longitudes (excludes Rahu/Ketu by default; 8-karaka includes Rahu)
- **Returns:** `{AK: planet, AmK: planet, BK: planet, MK: planet, PK: planet, GK: planet, DK: planet}`
- **Called by:** `engine.py:analyze_static()`

### analyze_karaka_relationships(karakas, planet_houses, planet_signs, shadbala) → dict
- **Purpose:** Analyze strength and placement of each karaka planet
- **Returns:** dict karaka_role → `{planet, house, sign, strength, interpretation}`
- **Called by:** `engine.py:analyze_static()`

## IMPORTANT CONSTANTS
Chara Karaka roles: AK (Atmakaraka), AmK (Amatyakaraka), BK (Bhratrukaraka), MK (Matrukaraka), PK (Putrakaraka), GK (Gnatikaraka), DK (Darakaraka); + ASK (Dara AK) in 8-karaka system

## DEPENDENCIES
config.py, coordinates.py

## RECENT CHANGES
- 2026-03-02: No changes (stable)
