# VedAstro Bridge Spec Matrix (MVP, no implementation)

## Scope
- Goal: define a minimal, implementation-ready bridge contract based on discovered VedAstro APIs.
- Source of truth: `vedastro_discovery.txt`, `vedastro_method_groups.txt`, and runtime signatures in `vedastro_method_signatures.json`.
- This document is a design spec only; no bridge code is added.

## Common Bridge Types
- `BirthContext`: `{ location_name, latitude, longitude, datetime_tz }` mapped to `GeoLocation` + `Time`.
- `TimeRange`: `{ start_datetime_tz, end_datetime_tz }`.
- `PlanetRef`: VedAstro enum value (for example `PlanetName.Sun`).
- `HouseRef`: VedAstro enum value (for example `HouseName.House1`).

## P0 Operations (recommended first)
| Priority | Bridge operation | VedAstro method | Signature | Input contract | Output contract |
|---|---|---|---|---|---|
| P0 | `get_horoscope_predictions` | `Calculate.HoroscopePredictions` | `(birthTime, filterTag)` | `birth: BirthContext`, `filter_tag: string` | **Verified**: `list[object]` with keys like `Name`, `Description`, `RelatedBody`, `Weight`, `Accuracy`, `Tags` |
| P0 | `get_horoscope_prediction_names` | `Calculate.HoroscopePredictionNames` | `(birthTime)` | `birth: BirthContext` | Unverified shape (likely list of names/identifiers) |
| P0 | `get_match_report` | `Calculate.MatchReport` | `(maleBirthTime, femaleBirthTime)` | `male_birth: BirthContext`, `female_birth: BirthContext` | Unverified shape (structured compatibility report expected) |
| P0 | `get_dasa_for_now` | `Calculate.DasaForNow` | `(birthTime, levels)` | `birth: BirthContext`, `levels: int` | Unverified shape (active dasa timeline block expected) |
| P0 | `get_dasa_for_life` | `Calculate.DasaForLife` | `(birthTime, levels, precisionHours, scanYears)` | `birth: BirthContext`, `levels: int`, `precision_hours: int`, `scan_years: int` | Unverified shape (full dasa periods expected) |
| P0 | `get_events_at_time` | `Calculate.EventsAtTime` | `(birthTime, checkTime, eventTagList)` | `birth: BirthContext`, `check_time: datetime_tz`, `event_tags: list[string]` | Unverified shape (event list expected) |
| P0 | `get_events_in_range` | `Calculate.EventsAtRange` | `(birthTime, startTime, endTime, eventTagList, precisionHours)` | `birth: BirthContext`, `range: TimeRange`, `event_tags: list[string]`, `precision_hours: int` | Unverified shape (event windows expected) |
| P0 | `list_event_catalog_by_tag` | `Calculate.GetAllEventDataGroupedByTag` | `()` | none | Unverified shape (tag → events mapping expected) |

## P1 Operations (next wave)
| Priority | Bridge operation | VedAstro method | Signature | Input contract | Output contract |
|---|---|---|---|---|---|
| P1 | `get_planet_sign_transits` | `Calculate.PlanetSignTransit` | `(startTime, endTime, planetName)` | `range: TimeRange`, `planet: PlanetRef` | Unverified shape (transit intervals expected) |
| P1 | `get_transit_house_from_lagna` | `Calculate.TransitHouseFromLagna` | `(transitPlanet, checkTime, birthTime)` | `planet: PlanetRef`, `check_time: datetime_tz`, `birth: BirthContext` | Unverified scalar/object (house index expected) |
| P1 | `get_transit_house_from_moon` | `Calculate.TransitHouseFromMoon` | `(transitPlanet, checkTime, birthTime)` | `planet: PlanetRef`, `check_time: datetime_tz`, `birth: BirthContext` | Unverified scalar/object (house index expected) |
| P1 | `get_gochara_kakshas` | `Calculate.GocharaKakshas` | `(checkTime, birthTime)` | `check_time: datetime_tz`, `birth: BirthContext` | Unverified shape |
| P1 | `is_gochara_occurring` | `Calculate.IsGocharaOccurring` | `(birthTime, time, planet, gocharaHouse)` | `birth: BirthContext`, `check_time: datetime_tz`, `planet: PlanetRef`, `gochara_house: HouseRef/int` | `bool`/boolean-like expected |
| P1 | `list_event_algorithms` | `Calculate.GetAllEventsChartAlgorithms` | `()` | none | Unverified shape (list of algo names expected) |

## P2 Operations (optional; chat/feedback)
| Priority | Bridge operation | VedAstro method | Signature | Notes |
|---|---|---|---|---|
| P2 | `horoscope_chat` | `Calculate.HoroscopeChat` | `(birthTime, userQuestion, userId, sessionId)` | Depends on remote LLM/API behavior; requires stable session handling |
| P2 | `horoscope_follow_up_chat` | `Calculate.HoroscopeFollowUpChat` | `(birthTime, followUpQuestion, primaryAnswerHash, userId, sessionId)` | Requires persisted `primaryAnswerHash` |
| P2 | `submit_chat_feedback` | `Calculate.HoroscopeChatFeedback` | `(answerHash, feedbackScore)` | Side-effecting endpoint |
| P2 | `match_chat` | `Calculate.MatchChat` | `(maleBirthTime, femaleBirthTime, userQuestion, chatSession)` | Side-effecting/session-based behavior |

## Error Contract (bridge-level)
- Normalize all VedAstro exceptions into `{ code, message, vedastro_method, retriable }`.
- Suggested codes: `VALIDATION_ERROR`, `UPSTREAM_TIMEOUT`, `UPSTREAM_HTTP_ERROR`, `UPSTREAM_SCHEMA_ERROR`, `INTERNAL_ERROR`.
- Mark `UPSTREAM_TIMEOUT` and transient HTTP 5xx as `retriable=true`.

## Minimal Validation Rules
- Require timezone in every datetime string (`+05:30`, `Z`, etc.).
- Validate latitude in `[-90, 90]`, longitude in `[-180, 180]`.
- Validate enum-backed fields (`planet`, `house`) before calling VedAstro.
- For range operations, enforce `start < end`.

## Suggested MVP Build Order
1. `get_horoscope_predictions`
2. `get_match_report`
3. `get_dasa_for_now` and `get_dasa_for_life`
4. `get_events_at_time` + `list_event_catalog_by_tag`
5. transit endpoints (`get_planet_sign_transits`, `get_transit_house_from_lagna`)

## Notes from current discovery run
- `Calculate` callable methods discovered: 478.
- Verified working in isolated env: `AllPlanetData`, `AllHouseData`, `HoroscopePredictions`.
- `HoroscopePredictions` returned list length 110 for the test chart.
