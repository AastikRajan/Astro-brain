```markdown
# Module: special_points.py
## Last Updated: 2026-03-02 (Phase 1B)

## PURPOSE
Computes special chart points: Gulika/Mandi (shadow upagrahas), Hora Lagna, Ghati Lagna,
Indu Lagna, Varnada Lagna, Pranapada Lagna, Sri Lagna, 19 Natal Sahams, Upagrahas
(5 Aprakasha grahas), Yogi/Avayogi, Bhrigu Bindu, Tarabala, Chandrabala.

## KEY FUNCTIONS

### compute_all_special_points(birth_dt, lagna_lon, moon_lon, ...) -> dict
- **Purpose:** Master function - computes all special points for natal chart
- **Signature (updated Phase 1B):** planet_lons, house_cusps, lagna_lord_lon, is_daytime params added
- **Returns:** {gulika, mandi, hora_lagna, ghati_lagna, indu_lagna, varnada_lagna, pranapada, sri_lagna, upagrahas, yogi_avayogi, bhrigu_bindu, lagna_drekkana, natal_sahams}
- **Called by:** engine.py:analyze_static()

### compute_hora_lagna(birth_dt, sun_lon, sunrise_hour=6.0) -> float
- **BUG FIXED Phase 1B:** Anchor changed from lagna_lon to sun_lon
- **Formula:** sun_lon + (minutes_since_sunrise x 0.5 deg) = 30 deg/hour (1 sign/hour)

### compute_ghati_lagna(birth_dt, sun_lon, sunrise_hour=6.0) -> float
- **BUG FIXED Phase 1B:** Anchor changed from lagna_lon to sun_lon
- **Formula:** sun_lon + (minutes_since_sunrise x 1.25 deg) = 1 sign per Ghati (24 min)

### compute_varnada_lagna(lagna_lon, hora_lagna_lon) -> float [NEW Phase 1B]
- Sign-parity vector algorithm; ODD lagna projects forward from Aries, EVEN backward from Pisces

### compute_pranapada_lagna(birth_dt, sun_lon, sunrise_hour=6.0) -> float [NEW Phase 1B]
- Vighati since sunrise; base by Sun modality: Movable=Aries, Fixed=Capricorn, Dual=Libra

### compute_sri_lagna(lagna_lon, moon_lon) -> float [NEW Phase 1B]
- Fractional Moon traversal of its nakshatra x 360 + lagna_lon

### compute_natal_sahams(planet_lons, asc_lon, house_cusps, lagna_lord_lon, is_daytime) -> Dict [NEW Phase 1B]
- 19 classical Arabic Parts with day/night reversal; no-reversal: Bhratri, Roga, Mrityu, Paradesa

### compute_tarabala / compute_chandrabala (unchanged)
- Tarabala: 9-fold star relationship (transit nak vs natal Moon nak)
- Chandrabala: transit Moon house from natal Moon (1,3,6,7,10,11 = auspicious)

## IMPORTANT CONSTANTS
- _ODD_SIGNS_SET: {0,2,4,6,8,10} for Varnada parity check
- _PRANAPADA_BASE_BY_MODALITY: Movable=0, Fixed=270, Dual=180
- _NAK_SPAN: 13.3333 deg (360/27)
- Bhrigu Bindu = (Moon_lon + Rahu_lon) / 2

## DEPENDENCIES
- vedic_engine.core.coordinates.sign_of, normalize
- Optional: vedic_engine.core.sunrise_utils.get_sunrise_sunset_hours

## RECENT CHANGES
- 2026-03-02 Phase 1B: FIX hora_lagna + ghati_lagna anchor to sun_lon (was lagna_lon - BUG)
- 2026-03-02 Phase 1B: ADD compute_varnada_lagna, compute_pranapada_lagna, compute_sri_lagna
- 2026-03-02 Phase 1B: ADD compute_natal_sahams (19 Sahams, day/night reversal)
- 2026-03-02 Phase 1B: UPDATE compute_all_special_points - new params + calls all new functions
- 2026-03-02: Added Bhrigu Bindu, Gulika, Upagrahas, Yogi/Avayogi
```
