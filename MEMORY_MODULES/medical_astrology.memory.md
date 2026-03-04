# Module: medical_astrology.py
## Last Updated: 2026-03-02

## PURPOSE
Implements health domain analysis using medical astrology principles: 1st house (longevity), 6th house (disease predispositions), 8th house (chronic/serious conditions), Sun (vitality), Moon (mind/constitution), and Saturn (chronic conditions). Maps planetary positions to body systems and potential health vulnerabilities.

## KEY FUNCTIONS

### compute_medical_analysis(planet_houses, planet_signs, planet_lons, lagna_sign, shadbala) → dict
- **Purpose:** Full medical astrology analysis for health domain predictions
- **Returns:** `{constitution, vulnerabilities: [system: str, afflicting_planet: str], vitality_score, mental_health_score, longevity_assessment}`
- **Called by:** `engine.py:predict()` when domain="health"

## IMPORTANT CONSTANTS
Body system mappings: SUN→heart/spine, MOON→fluids/mind, MARS→blood/muscles, MERCURY→nervous system, JUPITER→liver/fat, VENUS→kidneys/reproductive, SATURN→bones/joints/chronic

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: No major changes
