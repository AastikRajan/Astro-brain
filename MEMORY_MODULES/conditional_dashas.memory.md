# Module: conditional_dashas.py
## Last Updated: 2026-03-02

## PURPOSE
Implements 8 conditional dasha systems from classical texts, each applicable only under specific birth conditions. Provides eligibility checks and full period computation for: Shodashottari, Dwadasottari, Panchottari, Shatabdika, Chaturaashiti, Dwisaptati, Shat Trimsa, Moola, and Tara Dasha systems.

## KEY FUNCTIONS

### check_all_conditional_eligibility(planet_houses, lagna_sign, d9_lagna_sign, d12_lagna_sign) → dict
- **Purpose:** Check all 8 systems for eligibility in one call
- **Returns:** dict system_name → {eligible, reason}
- **Called by:** `engine.py:analyze_static()`

### compute_shodashottari(moon_longitude) → dict
- **Eligibility:** Moon in Rahu's sign (Gemini/Virgo controversy — uses Virgo)
- **Total years:** 116

### compute_dwadasottari(moon_longitude) → dict
- **Eligibility:** Venus in D9 Lagna (Libra)
- **Total years:** 112

### compute_panchottari(moon_longitude) → dict
- **Eligibility:** Lagna in Cancer in D1 AND D12
- **Total years:** 105

### compute_shatabdika(moon_longitude) → dict
- **Eligibility:** Lagna in Aries in D1 and Lagna in Aries in D9
- **Total years:** 100

### compute_chaturaashiti(moon_longitude) → dict
- **Eligibility:** Sun in own sign (7th from Lagna) or Lagna lord in 7th
- **Total years:** 84

### compute_dwisaptati(moon_longitude) → dict
- **Eligibility:** Lagna lord in 7th or Sun in Lagna
- **Total years:** 72

### compute_shat_trimsa(moon_longitude) → dict
- **Eligibility:** Born at night with Moon in Lagna
- **Total years:** 36 (repeating)

### compute_moola_dasha(planet_lons, birth_date) → List[dict]
- **Purpose:** Moola Dasha based on lagna nakshatra lord

### compute_tara_dasha(moon_longitude, birth_date) → List[dict]
- **Purpose:** Tara Dasha based on star relationships from birth nakshatra

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: Full suite of 8 conditional systems implemented
