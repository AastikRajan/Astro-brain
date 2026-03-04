# Module: muhurta.py
## Last Updated: 2026-03-02

## PURPOSE
Finds auspicious timing windows (Muhurta) for specific event types by scoring Panchanga quality across a date range. Uses Tithi, Nakshatra, Vara, Yoga, and Karana quality ratings, excluding eclipse dates. Returns ranked windows for marriage, travel, business, surgery, etc.

## KEY FUNCTIONS

### find_muhurta_windows(event_type, start_date, end_date, lat, lon) → List[dict]
- **Purpose:** Find best Muhurta windows in a date range for an event type
- **Inputs:** event type str, start/end dates, location
- **Returns:** List of `{date, score, factors, warnings}` sorted best-first
- **Called by:** `engine.py:predict()` for timing optimization

### score_window(panchanga, event_type, eclipse) → Tuple[float, List[str], List[str]]
- **Purpose:** Score a single time window based on Panchanga and event type rules
- **Returns:** (score, positives, negatives)
- **Called by:** `find_muhurta_windows()`

### check_muhurta_date(event_type, target_date, lat, lon) → dict
- **Purpose:** Check a specific date's Muhurta quality
- **Returns:** `{score, verdict, factors, eclipse_alert}`
- **Called by:** `main.py` for single-date check

## DEPENDENCIES
panchanga.py, transits.py (for eclipse data), config.py

## RECENT CHANGES
- 2026-03-02: Integrated eclipse alerts from lunations.py
