"""Core computation layer: coordinates, divisionals, aspects, Swiss Ephemeris."""
from vedic_engine.core.coordinates import (
    sign_of, nakshatra_of, pada_of, angular_distance,
    house_from, full_position_info,
)
from vedic_engine.core.divisional import compute_all_vargas, get_varga
from vedic_engine.core.aspects import (
    compute_all_drik_bala, get_aspect_map, houses_aspected,
)

# Swiss Ephemeris bridge (optional — graceful fallback if pyswisseph not installed)
try:
    from vedic_engine.core.swisseph_bridge import (
        compute_natal_positions as swe_natal_positions,
        compute_house_cusps as swe_house_cusps,
        build_chart_from_birth_data as swe_build_chart,
        get_transit_positions_swe,
        get_transit_speeds_swe,
        get_ayanamsa as swe_ayanamsa,
    )
    _SWE_AVAILABLE = True
except ImportError:
    _SWE_AVAILABLE = False

__all__ = [
    "sign_of", "nakshatra_of", "pada_of", "angular_distance",
    "house_from", "full_position_info",
    "compute_all_vargas", "get_varga",
    "compute_all_drik_bala", "get_aspect_map", "houses_aspected",
]
