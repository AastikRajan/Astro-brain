# Module: compatibility.py
## Last Updated: 2026-03-02

## PURPOSE
Implements Kundli Milan (compatibility matching) using the classical Ashtakoot (8-factor) system. Scores two charts on: Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, and Nadi — totaling 36 maximum points. Score ≥ 18 is compatible; ≥ 24 is excellent.

## KEY FUNCTIONS

### compute_compatibility(chart_a, chart_b) → dict
- **Purpose:** Full Ashtakoot score between two charts
- **Returns:** `{total_score, max_36, factors: {varna, vashya, tara, yoni, gana, maitri, bhakoot, nadi}, verdict}`
- **Called by:** `main.py` in compatibility mode

## IMPORTANT CONSTANTS
Max points: Varna=1, Vashya=2, Tara=3, Yoni=4, Graha Maitri=5, Gana=6, Bhakoot=7, Nadi=8

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: No changes
