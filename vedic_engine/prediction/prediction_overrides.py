from __future__ import annotations

from typing import Any, Dict, Tuple


def _extract_longitude(item: Any) -> float | None:
    if isinstance(item, dict):
        val = item.get("longitude")
        if isinstance(val, (int, float)):
            return float(val)
    if isinstance(item, (int, float)):
        return float(item)
    return None


def _angular_distance(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def check_master_overrides(
    computed: Dict[str, Any],
    domain: str,
) -> Tuple[bool, float | None, str | None]:
    """
    5 override situations that bypass normal scoring.
    Returns (is_override, override_confidence, override_description).
    """
    # NOTE: Negative overrides return LOW confidence (domain outcome improbable).
    # Research File 3 gives 95/90/85% confidence in the *negative* prediction;
    # since engine confidence = probability of positive domain outcome, we invert.
    sade_sati = computed.get("sade_sati", {})
    if isinstance(sade_sati, dict) and sade_sati.get("active", False):
        moon_bav_total = computed.get("ashtakvarga", {}).get("sav", [0] * 12)
        moon_sign_idx = computed.get("moon_sign_index")
        if isinstance(moon_bav_total, list) and isinstance(moon_sign_idx, int):
            if 0 <= moon_sign_idx < len(moon_bav_total) and moon_bav_total[moon_sign_idx] < 25:
                return (True, 0.05, "Sade Sati + Weak Moon SAV: Extreme stress period")

    dasha_sandhi = computed.get("dasha_sandhi", False)
    dasha_sandhi_active = False
    if isinstance(dasha_sandhi, bool):
        dasha_sandhi_active = dasha_sandhi
    elif isinstance(dasha_sandhi, dict):
        dasha_sandhi_active = bool(dasha_sandhi.get("active", False))
    if dasha_sandhi_active:
        return (True, 0.10, "Dasha Sandhi: High volatility, avoid major decisions")

    transit_positions = computed.get("transit_positions", {})
    moon_lon = _extract_longitude(computed.get("moon_longitude"))
    lagna_lon = _extract_longitude(computed.get("lagna_longitude"))
    sat_lon = _extract_longitude(transit_positions.get("SATURN")) if isinstance(transit_positions, dict) else None
    rahu_lon = _extract_longitude(transit_positions.get("RAHU")) if isinstance(transit_positions, dict) else None
    if sat_lon is not None and rahu_lon is not None:
        if _angular_distance(sat_lon, rahu_lon) <= 3.0:
            if (moon_lon is not None and _angular_distance(sat_lon, moon_lon) <= 5.0) or (
                lagna_lon is not None and _angular_distance(sat_lon, lagna_lon) <= 5.0
            ):
                return (True, 0.15, "Transit Saturn-Rahu conjunction on Lagna/Moon: Karmic crisis window")

    active_dasha_lord = str(computed.get("active_dasha", {}).get("lord", "")).upper()
    yogas = computed.get("yogas", [])
    if isinstance(yogas, list):
        for yoga in yogas:
            if isinstance(yoga, dict):
                name = str(yoga.get("name", "")).lower()
                planets = [str(p).upper() for p in yoga.get("planets", [])]
                if "vipreet" in name and active_dasha_lord and active_dasha_lord in planets:
                    return (True, 0.85, "Vipreet Raja Yoga active: Crisis followed by massive gain")

    vimshopak = computed.get("vimshopak", {}).get(active_dasha_lord, {})
    vim_score = float(vimshopak.get("score", 0) if isinstance(vimshopak, dict) else 0)
    if vim_score >= 18:
        return (True, 0.90, "Dasha lord has exceptional Vimshopak: Guaranteed benefic results")

    return (False, None, None)
