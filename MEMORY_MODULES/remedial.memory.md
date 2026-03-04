# Module: remedial.py
## Last Updated: 2026-03-02

## PURPOSE
Returns remedial measure recommendations based on the afflicted planets and domain weakness identified in the prediction report. Maps weak/malefic planets to classical remedies: gemstones, mantras, charity, fasting days, colors, and deity propitiation.

## KEY FUNCTIONS

### get_remedies(weak_planets, domain, promise_pct, functional_analysis) → dict
- **Purpose:** Recommend remedies for prediction domain weakness
- **Inputs:** list of weak/afflicted planets, domain, promise score, functional roles
- **Returns:** `{priority_planet, remedies: [type: str, description: str, rationale: str]}`
- **Called by:** `engine.py:predict()`

## DEPENDENCIES
config.py

## RECENT CHANGES
- 2026-03-02: No changes
