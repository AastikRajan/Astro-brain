# Module: strength/ashtakvarga.py
## Last Updated: 2026-03-02 (Phase 1C)

## PURPOSE
Full Ashtakvarga pipeline: BAV, SAV, Trikona/Ekadhipatya Shodhana, Shodhya Pinda (Phase 1C), PAV (Phase 1C).

## KEY FUNCTIONS

### compute_shodhya_pinda(shodhana, planet_signs) -> Dict[str, int] [NEW Phase 1C]
- Rashi Pinda + Graha Pinda (correct BPHS formula, not combined multiply)
- RASHI_GUN: Aries=7,Tau=10,Gem=8,Can=4,Leo=10,Vir=5,Lib=7,Sco=8,Sag=9,Cap=5,Aqu=11,Pis=12
- GRAHA_GUN: SUN=5,MOON=5,MARS=8,MER=5,JUP=10,VEN=7,SAT=5

### compute_prastharashtakavarga(planet_signs, lagna_sign) -> Dict [NEW Phase 1C]
- PAV[recipient][contributor] = [12 ints 0/1]
- All 7 planets, 8 contributors (7 planets + ASC), hard-coded _PAV_TABLES
- Kakshya = 3.75 deg divisions; lord order: SAT,JUP,MAR,SUN,VEN,MER,MOO,ASC

### kakshya_lord_of_degree(degree_in_sign) -> str [NEW Phase 1C]

### compute_full_ashtakvarga(planet_signs, lagna_sign) -> Dict
- Now returns: bhinna + sarva + shodhana + pinda + shodhya_pinda + pav + checksums

### trikona_shodhana / ekadhipatya_shodhana / pinda_sadhana (unchanged)

## IMPORTANT CONSTANTS (Phase 1C FIX)
- RASHI_MULTIPLIERS[Virgo] fixed 8 -> 5 in config.py (research file canonical value)
- _PAV_TABLES: full 7-planet PAV contribution offsets from Research File 5

## RECENT CHANGES
- 2026-03-02 Phase 1C: FIX Virgo RASHI_MULTIPLIER 8->5
- 2026-03-02 Phase 1C: ADD compute_shodhya_pinda (Rashi+Graha Pinda)
- 2026-03-02 Phase 1C: ADD compute_prastharashtakavarga + _PAV_TABLES + kakshya_lord_of_degree
- 2026-03-02 Phase 1C: UPDATE compute_full_ashtakvarga return dict
