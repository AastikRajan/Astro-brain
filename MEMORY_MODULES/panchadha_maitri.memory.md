# Module: panchadha_maitri.py
## Last Updated: 2026-03-02

## PURPOSE
Computes Panchadha Maitri (5-fold compound friendship) between planets. Combines the Naisargika (natural/permanent) and Tatkalika (temporary/chart-based) friendships to produce the actual compound relationship. Used in yoga detection, functional benefic/malefic classification, and dasha quality assessment.

## KEY FUNCTIONS

### compute_panchadha_maitri(planet_a, planet_b, planet_signs) → dict
- **Purpose:** Compound friendship between two planets in the natal chart
- **Inputs:** two planet names, all planet sign placements
- **Returns:** `{natural: str, temporary: str, compound: str}` — values are "intimate_friend" through "bitter_enemy"
- **Called by:** `yogas.py`, `functional.py`, `dasha_quality.py`

## IMPORTANT CONSTANTS
5 compound relationships: Adhimitra (great friend), Mitra (friend), Sama (neutral), Shatru (enemy), Adhishatru (great enemy)

## DEPENDENCIES
config.py (NAISARGIKA_FRIENDS, NAISARGIKA_ENEMIES)

## RECENT CHANGES
- 2026-03-02: No changes
