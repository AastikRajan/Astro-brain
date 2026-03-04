# Module: vimshopak.py
## Last Updated: 2026-03-02

## PURPOSE
Computes Vimshopaka Bala (20-point dignity score across divisional charts) for each planet. This metric measures how well-placed a planet is across its most important divisional charts. Higher Vimshopaka = more consistently dignified across D1/D9/D10/etc. = generally stronger planet.

## KEY FUNCTIONS

### compute_all_vimshopak(planet_longitudes) → Dict[str, dict]
- **Purpose:** Compute Vimshopaka Bala for all planets (16-varga system)
- **Returns:** dict planet → `{score, max_score, normalized, interpretation}`
- **Called by:** `engine.py:analyze_static()`

### compute_vimshopak(planet, natal_longitude) → dict
- **Purpose:** 16-varga Vimshopaka for one planet (full Shodashavarga, max 20)

### compute_shadvarga_vimshopak(planet, natal_longitude) → dict
- **Purpose:** 6-varga Vimshopaka (D1/D2/D3/D9/D12/D30, max 20, simpler)

### compute_all_shadvarga(planet_longitudes) → Dict[str, dict]
- **Purpose:** Shadvarga for all planets

### interpret_vimshopak_score(score, max_score) → dict
- **Purpose:** Map numerical score to band (Shobhana/Poorna/Adhama etc.)

### get_karakatwa_quality(planet, domain, vimshopak_results) → float
- **Purpose:** Extract karakatwa quality for a domain-planet pair

## DEPENDENCIES
divisional.py, config.py

## RECENT CHANGES
- 2026-03-02: Added get_karakatwa_quality() for domain scoring
