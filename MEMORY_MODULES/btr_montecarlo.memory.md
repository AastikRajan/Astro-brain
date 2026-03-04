# Module: btr_montecarlo.py
## Last Updated: 2026-03-02

## PURPOSE
Birth Time Rectification (BTR) via Monte Carlo simulation. Takes a range of possible birth times, runs the engine for each variation, and scores predictions against known life events to find the most probable exact birth time. Sensitive to Lagna and Bhava cusp positions which shift rapidly.

## KEY FUNCTIONS

### run_btr_montecarlo(birth_data, known_events, time_range_minutes, n_samples) → dict
- **Purpose:** Run Monte Carlo BTR over ±time_range_minutes from given birth time
- **Inputs:** birth data dict, list of known life events with dates/domains, range, sample count
- **Returns:** `{best_time, best_score, time_distribution, top_candidates}`
- **Called by:** `main.py` in BTR mode (--rectify flag)

## DEPENDENCIES
engine.py (runs full prediction for each sample), numpy

## RECENT CHANGES
- 2026-03-02: Created as scaffold module
