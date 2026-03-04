# Module: models.py
## Last Updated: 2026-03-02

## PURPOSE
Defines all core dataclasses used as data carriers between engine modules. Acts as the typed data contract between all subsystems. VedicChart is the root object that flows through the entire engine from loader to prediction output.

## KEY FUNCTIONS
No functions — pure dataclass definitions.

## KEY CLASSES

### BirthInfo
Fields: name, date, time, place, latitude, longitude, timezone, ayanamsa, ayanamsa_model

### PlanetPosition
Fields: planet, longitude, sign_index, degree_in_sign, nakshatra_index, nakshatra_name, nakshatra_lord, pada, is_retrograde, is_combust, speed, kp_rashi_lord, kp_nak_lord, kp_sub_lord, kp_sub_sub_lord, house_num, dignity

### HouseCusp
Fields: house_num, longitude, sign_index

### VedicChart
Fields: birth_info (BirthInfo), planets (Dict[str, PlanetPosition]), cusps (Dict[int, HouseCusp]), lagna_longitude, ayanamsa
- Core object passed to engine.py:analyze_static() and predict()

### ShadbalaPlanet, BhavaStrength, AshtakavargaData, DashaPeriod
Supporting dataclasses for strength and timing data.

## DEPENDENCIES
(none — root dataclass module)

## RECENT CHANGES
- 2026-03-02: Added KP layer fields to PlanetPosition (kp_sub_lord, kp_sub_sub_lord)
