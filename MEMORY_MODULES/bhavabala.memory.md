# Module: bhavabala.py
## Last Updated: 2026-03-02

## PURPOSE
Computes Bhava Bala (house strength) for each of the 12 houses. House strength combines the strength of the house lord (Bhavesha Bala), aspects to the house (Bhava Drishti Bala), and occupant modifiers. Used in the Promise gate to score Bhava pillar and as a modifier in confidence scoring.

## KEY FUNCTIONS

### compute_all_bhavabala(planet_houses, house_lords, shadbala_results, ...) → Dict[int, dict]
- **Purpose:** Compute Bhava Bala for all 12 houses
- **Returns:** dict house_num → `{total_rupas, classification, bhavesha_bala, drishti_bala, occupant_modifier}`
- **Called by:** `engine.py:analyze_static()`

### compute_bhavabala(house_num, planet_houses, house_lords, shadbala_results, ...) → dict
- **Purpose:** Compute Bhava Bala for one house
- **Calls:** `bhava_drishti_bala()`, `_occupant_modifier()`

### bhava_drishti_bala(house_lord, planet_houses, aspect_map, shadbala_results) → float
- **Purpose:** Portion of house strength from aspecting planets' strengths

### classify_bhavabala(total_rupas) → dict
- **Purpose:** Classify house strength into bands (Weak/Average/Strong/Very Strong)

### get_bhavabala_modifier_for_domain(domain, bhavabala_results) → float
- **Purpose:** Extract domain-relevant house strength as a modifier
- **Called by:** `confidence.py` (via engine injection)

### get_shadbala_ratio(planet, shadbala_virupas) → float
- **Purpose:** Divide virupas by required minimum → ratio ≥1.0 is strong

## DEPENDENCIES
shadbala.py (for lord strength), config.py

## RECENT CHANGES
- 2026-03-02: Added get_bhavabala_modifier_for_domain() for confidence module
