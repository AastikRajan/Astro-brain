# Module: progressions.py
## Last Updated: 2026-03-02

## PURPOSE
Implements Secondary Progressions (1 day = 1 year of life) for the natal chart and Solar Terms (Ingresses of Sun through 12 signs at 30° each). Used to identify slow-moving natal activation patterns that complement dashas and transits.

## KEY FUNCTIONS

### compute_secondary_progressions(planet_lons, birth_date, on_date) → dict
- **Purpose:** Compute progressed planet positions for a native's age
- **Inputs:** natal longitudes, birth date, analysis date
- **Returns:** dict of progressed longitudes and aspects to natal positions
- **Called by:** `engine.py:predict()`

### score_progression_activation(progressed, natal, domain_houses) → float
- **Purpose:** Score how much progressed planets activate domain-relevant houses/signs
- **Inputs:** progressed positions, natal positions, domain house list
- **Returns:** float 0–1 activation score
- **Called by:** `engine.py:predict()`

### compute_solar_terms(on_date, year) → List[dict]
- **Purpose:** Compute the 12 solar ingress dates (Mesha Sankranti through Mina Sankranti)
- **Called by:** `engine.py:analyze_static()` for solar calendar context

## DEPENDENCIES
(none — pure Python date math)

## RECENT CHANGES
- 2026-03-02: Created as new module
