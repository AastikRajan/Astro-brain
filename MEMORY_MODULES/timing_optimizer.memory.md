# Module: timing_optimizer.py
## Last Updated: 2026-03-02

## PURPOSE
Scans a date range to find the best and worst prediction windows for a given domain. Runs predict() across multiple dates and ranks by final confidence score. Used to surface actionable "best times" in the prediction report.

## KEY FUNCTIONS

### find_best_windows(engine, chart, domain, start_date, end_date, top_n, static_data) → List[dict]
- **Purpose:** Find top N best dates/periods by confidence score
- **Inputs:** engine instance, chart, domain, date range, count
- **Returns:** List of `{date, score, dasha, transit_summary, reason}`
- **Called by:** `engine.py:predict()`

### find_worst_windows(engine, chart, domain, start_date, end_date, top_n, static_data) → List[dict]
- **Purpose:** Find top N worst dates (obstacles, caution periods)
- **Called by:** `engine.py:predict()`

## DEPENDENCIES
engine.py (calls predict internally), config.py

## RECENT CHANGES
- 2026-03-02: Created as standalone optimizer (was inline loop in engine.py)
