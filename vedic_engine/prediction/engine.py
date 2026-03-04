"""
Vedic Prediction Engine — Main Pipeline.

Four-step pipeline:
  1. Static analysis  – chart features computed once
  2. Dynamic analysis – dasha + transits for a given date
  3. Domain queries   – filter/score by life area
  4. Confidence       – multi-system agreement scoring

Usage:
    engine = PredictionEngine()
    static = engine.analyze_static(chart)
    report = engine.predict(chart, domain="career", on_date=datetime.now())
"""
from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional, Any

# ── Core & Strength ─────────────────────────────────────────────
from vedic_engine.core.divisional import compute_all_vargas
from vedic_engine.core.aspects    import compute_all_drik_bala, get_aspect_map
from vedic_engine.strength.shadbala    import compute_all_shadbala
from vedic_engine.strength.ashtakvarga import compute_full_ashtakvarga
from vedic_engine.strength.bhavabala   import compute_all_bhavabala
from vedic_engine.strength.vimshopak   import compute_all_vimshopak

# ── Timing ──────────────────────────────────────────────────────
from vedic_engine.timing.vimshottari  import compute_mahadasha_periods, get_active_dasha, detect_dasha_sandhi
from vedic_engine.timing.yogini       import compute_yogini_periods, get_active_yogini
from vedic_engine.timing.ashtottari   import ashtottari_details_on_date, ASHTOTTARI_YEARS
from vedic_engine.timing.kp          import (
    get_kp_layers, build_kp_significations, build_cusp_significations,
    compute_ruling_planets,
)

# ── Analysis ────────────────────────────────────────────────────
from vedic_engine.analysis.yogas         import (
    detect_all_yogas, compute_yoga_compounding,
    compute_dhana_stacking_tier,
    score_md_ad_relationship, get_manduka_gati_life_phase,
    compute_all_extended_yogas,
)
from vedic_engine.analysis.karakas       import compute_chara_karakas, analyze_karaka_relationships
from vedic_engine.analysis.functional    import compute_functional_analysis
from vedic_engine.analysis.graha_yuddha  import detect_planetary_wars, apply_war_penalties
from vedic_engine.analysis.special_points import compute_all_special_points
from vedic_engine.analysis.avasthas      import compute_all_avasthas
from vedic_engine.analysis.dispositor    import analyze_dasha_lord_dispositor, compute_dispositor_graph
from vedic_engine.analysis.lunations     import compute_upcoming_lunations, get_eclipse_alerts, get_high_significance_lunations

# ── Prediction ──────────────────────────────────────────────────
from vedic_engine.prediction.transits   import get_transit_positions, evaluate_all_transits, detect_sade_sati
from vedic_engine.prediction.confidence import compute_confidence, multi_system_agreement
from vedic_engine.prediction.fuzzy_confidence import compute_fuzzy_confidence, aggregate_for_fuzzy
from vedic_engine.prediction.bayesian_layer import compute_bayesian_confidence
from vedic_engine.prediction.dasha_transit  import analyze_dasha_lord_transit, compute_ingress_calendar
from vedic_engine.prediction.calibration    import calibrate_confidence
from vedic_engine.prediction.timing_optimizer import find_best_windows, find_worst_windows
from vedic_engine.analysis.remedial          import get_remedies
from vedic_engine.analysis.varga_analysis    import compute_varga_report
from vedic_engine.timing.muhurta             import find_muhurta_windows
from vedic_engine.core.divisional            import D9, D10, D7, D4
from vedic_engine.timing.panchanga          import compute_panchanga
from vedic_engine.analysis.argala           import compute_all_argala
from vedic_engine.prediction.aspect_transits import (
    compute_transit_aspects, compute_natal_activation_score, top_transit_aspects,
)
from vedic_engine.timing.progressions import (
    compute_secondary_progressions, score_progression_activation, compute_solar_terms,
)

from vedic_engine.core.coordinates import sign_of
from vedic_engine.data.models import VedicChart

# ── Module-level sign name / lord lookup tables ─────────────────
SIGN_NAMES_LIST = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_LORDS_MAP: Dict[int, str] = {
    0: "MARS", 1: "VENUS", 2: "MERCURY", 3: "MOON", 4: "SUN", 5: "MERCURY",
    6: "VENUS", 7: "MARS", 8: "JUPITER", 9: "SATURN", 10: "SATURN", 11: "JUPITER",
}

# ── Jaimini / new modules ───────────────────────────────────────
from vedic_engine.analysis.arudha_padas import arudha_summary
from vedic_engine.analysis.rashi_drishti import rashi_drishti_summary
from vedic_engine.timing.chara_dasha import chara_dasha_details_on_date

# ── Phase 1E: Transit systems ────────────────────────────────────
try:
    from vedic_engine.timing.sudarshana import (
        evaluate_sudarshana_all_planets, compute_sudarshana_dasha,
    )
    _SUDARSHANA_AVAILABLE = True
except ImportError:
    _SUDARSHANA_AVAILABLE = False

try:
    from vedic_engine.analysis.sarvatobhadra import construct_sbc_grid, check_sbc_vedha
    _SBC_AVAILABLE = True
except ImportError:
    _SBC_AVAILABLE = False

try:
    from vedic_engine.analysis.kota_chakra import compute_kota_chakra, compute_kota_status
    _KOTA_AVAILABLE = True
except ImportError:
    _KOTA_AVAILABLE = False

from vedic_engine.prediction.transits import check_vedha  # Phase 1E.1 standalone Vedha

# ── Phase 1F: Longevity + Nadi Amsha ─────────────────────────────
try:
    from vedic_engine.analysis.longevity import compute_longevity
    _LONGEVITY_AVAILABLE = True
except ImportError:
    _LONGEVITY_AVAILABLE = False

try:
    from vedic_engine.analysis.nadi_amsha import compute_nadi_amsha
    _NADI_AMSHA_AVAILABLE = True
except ImportError:
    _NADI_AMSHA_AVAILABLE = False

# ── Deep Dive research modules (sliding scale combustion, career, marriage, badhaka)
try:
    from vedic_engine.analysis.career_checklist import compute_career_checklist
    _CAREER_CHECKLIST_AVAILABLE = True
except ImportError:
    _CAREER_CHECKLIST_AVAILABLE = False

try:
    from vedic_engine.analysis.marriage_synthesis import compute_marriage_synthesis
    _MARRIAGE_SYNTHESIS_AVAILABLE = True
except ImportError:
    _MARRIAGE_SYNTHESIS_AVAILABLE = False

try:
    from vedic_engine.analysis.badhaka import (
        get_badhaka_house, compute_badhaka_friction, apply_badhaka_to_confidence,
    )
    _BADHAKA_AVAILABLE = True
except ImportError:
    _BADHAKA_AVAILABLE = False

try:
    from vedic_engine.strength.vimshopak import compute_shadvarga_vimshopak, compute_all_shadvarga
    _SHADVARGA_AVAILABLE = True
except ImportError:
    _SHADVARGA_AVAILABLE = False

try:
    from vedic_engine.strength.bhavabala import get_bhavabala_modifier_for_domain
    _BHAVABALA_DOMAIN_AVAILABLE = True
except ImportError:
    _BHAVABALA_DOMAIN_AVAILABLE = False

try:
    from vedic_engine.timing.vimshottari import analyze_retrograde_dasha_lord
    _RETRO_DASHA_AVAILABLE = True
except ImportError:
    _RETRO_DASHA_AVAILABLE = False

# ── Promise Prerequisite Gate (Three Pillar Rule) ───────────────
try:
    from vedic_engine.prediction.promise import (
        compute_promise, check_marriage_promise,
        check_career_promise, check_wealth_promise,
    )
    _PROMISE_AVAILABLE = True
except ImportError:
    _PROMISE_AVAILABLE = False

# ── Dasha Diagnostic Matrix ──────────────────────────────────────
try:
    from vedic_engine.timing.vimshottari import dasha_diagnostic_matrix
    _DIAG_MATRIX_AVAILABLE = True
except ImportError:
    _DIAG_MATRIX_AVAILABLE = False

# ── Yoga Compounding ─────────────────────────────────────────────
try:
    from vedic_engine.analysis.yogas import compute_yoga_compounding
    _YOGA_COMPOUND_AVAILABLE = True
except ImportError:
    _YOGA_COMPOUND_AVAILABLE = False

# ── Nakshatra Analysis (File 2) ───────────────────────────────────
try:
    from vedic_engine.analysis.nakshatra_analysis import (
        compute_full_nakshatra_analysis,
        check_dwisaptati_eligibility,
        get_pada_syllable,
    )
    _NAKSHATRA_ANALYSIS_AVAILABLE = True
except ImportError:
    _NAKSHATRA_ANALYSIS_AVAILABLE = False

# ── Tajika Varshaphala (File 3) ───────────────────────────────────
try:
    from vedic_engine.timing.varshaphala import compute_varsha_analysis
    _VARSHAPHALA_AVAILABLE = True
except ImportError:
    _VARSHAPHALA_AVAILABLE = False

# ── Jaimini Extended (File 4) ─────────────────────────────────────
try:
    from vedic_engine.analysis.sthira_karakas import compute_sthira_karakas
    from vedic_engine.analysis.karakamsha import (
        compute_svamsha, compute_karakamsha_lagna, analyze_karakamsha,
        compute_jaimini_yogas, check_marriage_timing,
        check_career_timing, analyze_al_ul_relationship,
    )
    from vedic_engine.timing.jaimini_dashas import (
        compute_shoola_dasha, compute_niryana_shoola_dasha,
        compute_brahma_dasha, compute_navamsha_dasha,
        compute_sudasa, compute_drig_dasha, compute_trikona_dasha,
        compute_sree_lagna, get_active_period,
        compute_narayana_dasha, get_active_narayana,
    )
    from vedic_engine.analysis.arudha_padas import compute_arudha_extended_analysis
    _JAIMINI_EXTENDED_AVAILABLE = True
except ImportError as _je:
    _JAIMINI_EXTENDED_AVAILABLE = False

# ── File 5: Prashna, Kalachakra, Medical, Conditional Dashas ─────
try:
    from vedic_engine.timing.kalachakra import (
        compute_kalachakra_dasha, analyze_deha_jeeva_transits,
    )
    from vedic_engine.analysis.medical_astrology import compute_medical_analysis
    from vedic_engine.timing.conditional_dashas import (
        check_all_conditional_eligibility,
        compute_shodashottari, compute_dwadasottari, compute_panchottari,
        compute_shatabdika, compute_chaturaashiti, compute_dwisaptati,
        compute_shat_trimsa, compute_moola_dasha, compute_tara_dasha,
    )
    from vedic_engine.timing.kp import (
        compute_prashna_panchaka, analyze_ithasala_yoga,
        resolve_prashna_query,
    )
    _FILE5_AVAILABLE = True
except ImportError as _f5e:
    _FILE5_AVAILABLE = False

# ── GPT accuracy layer (graceful fallback if openai not installed) ──
try:
    from vedic_engine.ai.gpt_reasoner import (
        resolve_yoga_fructification,
        resolve_dasha_conflict,
        resolve_kp_ambiguity,
        apply_yoga_fructification,
        analyze_multi_dasha_consensus,
    )
    _GPT_REASONER_AVAILABLE = True
except ImportError:
    _GPT_REASONER_AVAILABLE = False

# ── Phase 3A: Nadi Jyotish timing ───────────────────────────────
try:
    from vedic_engine.timing.nadi_timing import compute_all_nadi_signals
    _NADI_TIMING_AVAILABLE = True
except ImportError:
    _NADI_TIMING_AVAILABLE = False

# ── Phase 3B: Hellenistic timing ────────────────────────────────
try:
    from vedic_engine.timing.hellenistic import compute_all_hellenistic_signals
    _HELLENISTIC_AVAILABLE = True
except ImportError:
    _HELLENISTIC_AVAILABLE = False

# ── Phase 3E: Scientific correlations ────────────────────────────
try:
    from vedic_engine.science.correlations import (
        compute_lunar_phase, compute_birth_month_risk, compute_hora_chronotherapy,
    )
    _SCIENCE_AVAILABLE = True
except ImportError:
    _SCIENCE_AVAILABLE = False


# ─── Domain definitions (KP-corrected) ──────────────────────────
DOMAIN_HOUSES = {
    "career":   [2, 6, 10, 11],        # 1/5/9 are NEGATORS for career
    "finance":  [2, 6, 11],            # active income; use finance_invest for investments
    "marriage": [2, 7, 11],            # 4 not in KP marriage set; 8 = duration only
    "health":   [1, 6, 8, 12],         # crisis set (recovery = {1,11})
    "children": [2, 5, 11],
    "property": [4, 12],
    "spiritual":[4, 8, 9, 12],
    "travel":   [3, 9, 12],
}

DOMAIN_NEGATORS = {
    "career":   [1, 5, 9],
    "finance":  [12],
    "marriage": [1, 6, 10],
    "health":   [],
    "children": [],
    "property": [],
    "spiritual":[],
    "travel":   [],
}

DOMAIN_PLANETS = {
    "career":   ["SUN", "SATURN", "MERCURY", "MARS", "JUPITER"],
    "finance":  ["VENUS", "JUPITER", "MERCURY", "MOON"],
    "marriage": ["VENUS", "JUPITER", "MOON", "MARS"],
    "health":   ["MARS", "SUN", "SATURN", "MOON"],
    "children": ["JUPITER", "VENUS", "MOON"],
    "property": ["MOON", "JUPITER", "MARS"],
    "spiritual":["JUPITER", "SATURN", "KETU", "MOON"],
    "travel":   ["MERCURY", "RAHU", "MARS", "SATURN"],
}


def _planet_domain_map(planet_house_map: Dict[str, int]) -> Dict[str, List[str]]:
    """Map each planet to domains whose houses it occupies."""
    result: Dict[str, List[str]] = {}
    for planet, house in planet_house_map.items():
        domains = [d for d, houses in DOMAIN_HOUSES.items() if house in houses]
        result[planet] = domains
    return result


class PredictionEngine:
    """End-to-end Vedic prediction pipeline."""

    # ── 1. Static Analysis ──────────────────────────────────────

    def analyze_static(self, chart: VedicChart) -> Dict[str, Any]:
        """
        Compute all chart features that don't depend on a specific date.
        Returns a rich dict of computed features.
        """
        # chart.planets is Dict[str, PlanetPosition]; fields: .planet, .longitude, .sign_index, .house_num, .is_retrograde
        planet_lons  = {name: p.longitude for name, p in chart.planets.items()}
        planet_signs = {name: p.sign_index for name, p in chart.planets.items()}
        planet_houses= {name: p.house_num for name, p in chart.planets.items()}
        retrogrades  = {name: p.is_retrograde for name, p in chart.planets.items()}
        # cusp_lons as list for KP layers; as dict for Shadbala (expects {house: lon})
        cusp_lons_list = [h.longitude for h in sorted(chart.houses, key=lambda h: h.house_num)]
        cusp_lons      = {i+1: lon for i, lon in enumerate(cusp_lons_list)}

        lagna_sign   = chart.lagna_sign   # VedicChart field name
        moon_lon     = planet_lons.get("MOON", 0.0)
        sun_lon      = planet_lons.get("SUN",  0.0)
        rahu_lon     = planet_lons.get("RAHU", 0.0)
        moon_sign    = sign_of(moon_lon)
        # BirthInfo has date/time strings; reconstruct datetime
        try:
            birth_dt = datetime.fromisoformat(f"{chart.birth_info.date}T{chart.birth_info.time}")
        except Exception:
            birth_dt = datetime.now()

        # ── Divisional charts
        vargas = {p: compute_all_vargas(lon) for p, lon in planet_lons.items()}

        # ── Aspects (use house numbers, not longitudes)
        asp_map = get_aspect_map(planet_houses)
        drik_bala = compute_all_drik_bala(planet_houses)

        # ── Shadbala
        try:
            shadbala = compute_all_shadbala(
                chart.planets, birth_dt, cusp_lons,
                latitude=chart.birth_info.latitude,
                longitude=chart.birth_info.longitude,
                tz_offset=chart.birth_info.timezone,
            )
        except Exception as e:
            shadbala = {"error": str(e)}

        # Shadbala ratios (actual / minimum required)
        shadbala_ratios = {}
        if isinstance(shadbala, dict) and "error" not in shadbala:
            for pname, data in shadbala.items():
                if isinstance(data, dict):
                    # compute_shadbala returns "rupas" and "ratio" directly
                    shadbala_ratios[pname] = data.get("ratio", data.get("rupas", 1.0))

        # ── Ashtakvarga
        try:
            av_data = compute_full_ashtakvarga(planet_signs, lagna_sign)
        except Exception as e:
            av_data = {"error": str(e)}

        # ── Bhavabala
        try:
            bhavabala = compute_all_bhavabala(lagna_sign, shadbala_ratios, planet_houses)
        except Exception as e:
            bhavabala = {"error": str(e)}

        # ── Vimshopak
        try:
            vimshopak = compute_all_vimshopak(planet_lons)
        except Exception as e:
            vimshopak = {"error": str(e)}

        # ── Yogas
        from vedic_engine.config import SIGN_LORDS, Sign as _Sign
        house_lords = {}
        for house_num in range(1, 13):
            sign_of_house = (lagna_sign + house_num - 1) % 12
            lord = SIGN_LORDS.get(_Sign(sign_of_house))
            if lord:
                house_lords[house_num] = lord.name

        retro_set = {name for name, val in retrogrades.items() if val}
        yogas = detect_all_yogas(
            planet_houses, planet_lons, shadbala_ratios,
            house_lords, asp_map,
            lagna_sign=lagna_sign,
            retrograde_planets=retro_set,
        )

        # ── Phase 1D: Extended unified yoga output ────────────────
        try:
            _extended_yogas = compute_all_extended_yogas(
                planet_houses, planet_lons, shadbala_ratios,
                house_lords, asp_map,
                lagna_sign=lagna_sign,
                retrograde_planets=retro_set,
            )
        except Exception:
            _extended_yogas = []

        # ── Dhana stacking tier
        try:
            dhana_stacking = compute_dhana_stacking_tier(
                yogas, planet_houses, house_lords, shadbala_ratios
            )
        except Exception:
            dhana_stacking = {}

        # ── Yoga Compounding (graph-based cluster boosting)
        yoga_compounding = {}
        if _YOGA_COMPOUND_AVAILABLE and yogas:
            try:
                yoga_compounding = compute_yoga_compounding(yogas)
            except Exception:
                yoga_compounding = {}

        # ── Phase 2A: Merge extended (graded) yogas over basic yogas ──────────
        # compute_dhana_stacking_tier and compute_yoga_compounding above need
        # YogaResult objects, so the merge happens AFTER those calls.
        # After this block, `yogas` is a List[Dict] with grade/score/domain fields.
        try:
            if _extended_yogas:
                ext_names = {y["name"] for y in _extended_yogas}
                # Convert basic yogas not already in extended to fallback dicts
                _basic_gap_dicts = [
                    {
                        "name":         getattr(y, "name", str(y)),
                        "type":         getattr(y, "category", "general"),
                        "planets":      list(getattr(y, "planets", [])),
                        "grade":        "C",
                        "score":        0.25,
                        "domain":       "general",
                        "active":       not bool(getattr(y, "cancellation_reason", None)),
                        "cancellation": getattr(y, "cancellation_reason", None),
                    }
                    for y in yogas
                    if getattr(y, "detected", True)
                    and getattr(y, "name", str(y)) not in ext_names
                ]
                yogas = _extended_yogas + _basic_gap_dicts
            else:
                # Fallback: convert YogaResult list to uniform dict format
                yogas = [
                    {
                        "name":         getattr(y, "name", str(y)),
                        "type":         getattr(y, "category", "general"),
                        "planets":      list(getattr(y, "planets", [])),
                        "grade":        "C",
                        "score":        0.25,
                        "domain":       "general",
                        "active":       not bool(getattr(y, "cancellation_reason", None)),
                        "cancellation": getattr(y, "cancellation_reason", None),
                    }
                    for y in yogas if getattr(y, "detected", True)
                ]
        except Exception:
            pass  # If merge fails, keep yogas as-is (YogaResult list); confidence handles both

        # ── Karakas
        karakas_list = compute_chara_karakas(planet_lons)
        karaka_analysis = analyze_karaka_relationships(
            karakas_list, planet_houses, shadbala_ratios
        )
        karakas = {"list": karakas_list, "analysis": karaka_analysis}

        # Extract AK (Atmakaraka) and DK (Dara Karaka) for Chara dasha enrichment
        ak_planet: Optional[str] = None
        dk_planet: Optional[str] = None
        karakas_dict: Dict[str, str] = {}        # {role: planet_name}
        try:
            for item in (karakas_list or []):
                if isinstance(item, dict):
                    role = str(item.get("role", item.get("karaka", ""))).upper()
                    planet = str(item.get("planet", ""))
                    if role and planet:
                        karakas_dict[role] = planet
            ak_planet = karakas_dict.get("AK") or karakas_dict.get("ATMAKARAKA")
            dk_planet = karakas_dict.get("DK") or karakas_dict.get("DARAKARAKA")
        except Exception:
            pass

        # ── Functional analysis (lagna-specific roles)
        try:
            func_analysis = compute_functional_analysis(lagna_sign)
        except Exception as e:
            func_analysis = {"error": str(e)}

        # ── Graha Yuddha (planetary war)
        try:
            wars = detect_planetary_wars(planet_lons)
            if wars:
                shadbala_ratios = apply_war_penalties(shadbala_ratios, wars)
        except Exception as e:
            wars = []

        # ── Special points (Gulika, Hora/Ghati Lagna, Varnada, Pranapada, Sri, Sahams…)
        _is_daytime_static = (6 <= birth_dt.hour < 18)
        _lagna_lord_name_static = SIGN_LORDS_MAP.get(lagna_sign, "MARS")
        _lagna_lord_lon_static = planet_lons.get(_lagna_lord_name_static, 0.0)
        try:
            lagna_lon_val = chart.lagna_degree
            special_pts = compute_all_special_points(
                birth_dt, lagna_lon_val, moon_lon, house_lords,
                sun_lon=sun_lon, rahu_lon=rahu_lon,
                latitude=chart.birth_info.latitude,
                longitude=chart.birth_info.longitude,
                tz_offset=chart.birth_info.timezone,
                planet_lons=planet_lons,
                house_cusps=cusp_lons,
                lagna_lord_lon=_lagna_lord_lon_static,
                is_daytime=_is_daytime_static,
            )
        except Exception as e:
            special_pts = {"error": str(e)}

        # ── Avasthas (Baladi, Shayanadi, Deeptadi) [Phase 1B 2026-03-02]
        try:
            _pdig = {pn: getattr(getattr(chart.planets.get(pn, None), "dignity", None), "name", "NEUTRAL")
                     for pn in planet_lons}
            _malefic_conj = {}
            _MALEFICS = {"SUN", "MARS", "SATURN", "RAHU", "KETU"}
            for pn, h in planet_houses.items():
                _malefic_conj[pn] = [p2 for p2, h2 in planet_houses.items()
                                      if p2 != pn and h2 == h and p2 in _MALEFICS]
            avasthas = compute_all_avasthas(
                planet_lons=planet_lons,
                planet_dignities=_pdig,
                moon_lon=moon_lon,
                sun_lon=sun_lon,
                lagna_sign=lagna_sign,
                birth_dt=birth_dt,
                sunrise_hour=6.0,
                malefic_conjunctions=_malefic_conj,
            )
        except Exception as e:
            avasthas = {"error": str(e)}

        # ── KP Significations
        # Build KP layers for each planet by longitude
        kp_layers_all = {pname: get_kp_layers(lon) for pname, lon in planet_lons.items()}
        kp_sigs = build_kp_significations(planet_houses, kp_layers_all,
                                          house_lords, lagna_sign)
        # Build KP layers for each house cusp by cusp longitude (uses list indexing)
        cusp_kp_layers = {i+1: get_kp_layers(cusp_lons_list[i])
                          for i in range(min(12, len(cusp_lons_list)))}
        cusp_sigs = build_cusp_significations(cusp_kp_layers, planet_houses, house_lords)

        # ── Arudha Padas (Jaimini) ──────────────
        try:
            arudha = arudha_summary(lagna_sign, planet_signs)
        except Exception as e:
            arudha = {"error": str(e)}

        # Extract UL (Upapada Lagna = A12) sign for marriage enrichment
        ul_sign: Optional[int] = None
        try:
            if isinstance(arudha, dict):
                ul_data = arudha.get("A12") or arudha.get("a12") or arudha.get("UL")
                if isinstance(ul_data, dict):
                    ul_sign = ul_data.get("sign") or ul_data.get("sign_index")
                elif isinstance(ul_data, (int, float)):
                    ul_sign = int(ul_data)
        except Exception:
            ul_sign = None

        # ── Rashi Drishti (Jaimini sign aspects) ───────────
        try:
            rashi_drishti = rashi_drishti_summary(planet_signs)
        except Exception as e:
            rashi_drishti = {"error": str(e)}

        # ── Domain map
        domain_map = _planet_domain_map(planet_houses)

        # ── Shadvarga Vimshopak (classical 6-chart quality scheme) ────
        shadvarga_vimshopak: Dict = {}
        if _SHADVARGA_AVAILABLE:
            try:
                shadvarga_vimshopak = compute_all_shadvarga(planet_lons)
            except Exception:
                shadvarga_vimshopak = {}

        # ── Badhaka house + friction coefficient ─────────────────────────
        badhaka_info: Dict = {}
        if _BADHAKA_AVAILABLE:
            try:
                badhaka_info = get_badhaka_house(lagna_sign)
                _badhakesh       = badhaka_info.get("badhakesh", "")
                _badhakesh_house = planet_houses.get(_badhakesh, 0)
                _is_malefic      = _badhakesh.upper() in {"SUN", "MARS", "SATURN", "RAHU", "KETU"}
                _shad_ratio      = shadbala_ratios.get(_badhakesh, 1.0)
                badhaka_info["friction"] = compute_badhaka_friction(
                    lagna_sign=lagna_sign,
                    badhakesh_house=_badhakesh_house,
                    badhakesh_is_functional_benefic=not _is_malefic,
                    badhakesh_shadbala_ratio=_shad_ratio,
                    badhakesh=_badhakesh,
                    event_domain="general",
                )
            except Exception as _e:
                badhaka_info = {"error": str(_e)}

        # ── Bhavabala domain modifier map ─────────────────────────────────
        bhavabala_domain_modifiers: Dict = {}

        # ── Special Degrees (Mrityu Bhaga, Gandanta, Pushkara) ────────────
        special_degrees: Dict = {}
        try:
            from vedic_engine.analysis.special_degrees import compute_all_special_degrees
            # Include Lagna longitude as a checkable point
            _sd_lons = dict(planet_lons)
            _sd_lons["LAGNA"] = chart.lagna_degree
            special_degrees = compute_all_special_degrees(
                planet_longitudes=_sd_lons,
            )
        except Exception:
            special_degrees = {}

        if _BHAVABALA_DOMAIN_AVAILABLE:
            try:
                _bh_data = bhavabala if isinstance(bhavabala, dict) else {}
                for _dom in DOMAIN_HOUSES:
                    _dom_houses = DOMAIN_HOUSES[_dom]
                    _mod = get_bhavabala_modifier_for_domain(_bh_data, _dom_houses)
                    bhavabala_domain_modifiers[_dom] = _mod
            except Exception:
                bhavabala_domain_modifiers = {}

        # ── Nakshatra Analysis (File 2) ───────────────────────────
        nakshatra_analysis = {}
        if _NAKSHATRA_ANALYSIS_AVAILABLE:
            try:
                _transit_moon_lon = planet_lons.get("MOON", moon_lon)  # natal = transit here
                nakshatra_analysis = compute_full_nakshatra_analysis(
                    planet_lons=planet_lons,
                    natal_moon_lon=moon_lon,
                    transit_moon_lon=_transit_moon_lon,
                    planet_houses=planet_houses,
                    house_lords=house_lords,
                )
            except Exception:
                nakshatra_analysis = {}

        # ── Tajika Varshaphala (File 3) ───────────────────────────
        varshaphala = {}
        if _VARSHAPHALA_AVAILABLE:
            try:
                _birth_dt = birth_dt
                _completed_years = max(0, _birth_dt.year - _birth_dt.year) if not hasattr(chart, "age") else getattr(chart, "age", 0)
                # Derive completed_years from birth datetime vs. now
                _now = datetime.now()
                _cy = (_now.year - _birth_dt.year
                       - ((_now.month, _now.day) < (_birth_dt.month, _birth_dt.day)))
                _cy = max(0, _cy)
                _is_day = 6 <= _birth_dt.hour < 18
                varshaphala = compute_varsha_analysis(
                    planet_lons      = planet_lons,
                    planet_speeds    = {p: 0.0 for p in planet_lons},
                    lagna_lon        = chart.lagna_degree,
                    natal_lagna_sign = lagna_sign,
                    natal_moon_lon   = moon_lon,
                    completed_years  = _cy,
                    is_day_chart     = _is_day,
                    return_date      = _now,
                )
            except Exception:
                varshaphala = {}

        # ── Jaimini Extended (File 4) ─────────────────────────────
        jaimini_extended: Dict[str, Any] = {}
        if _JAIMINI_EXTENDED_AVAILABLE:
            try:
                # D9 signs for all planets
                try:
                    from vedic_engine.core.divisional import D9 as _d9f
                    _planet_d9_signs = {p: _d9f(lon) for p, lon in planet_lons.items()}
                    _d9_lagna        = _d9f(chart.lagna_degree)
                except Exception:
                    _planet_d9_signs = {p: int(lon % 360 / 30) % 12 for p, lon in planet_lons.items()}
                    _d9_lagna        = int(chart.lagna_degree % 360 / 30) % 12

                _ak_d9_sign = _planet_d9_signs.get(ak_planet, lagna_sign) if ak_planet else lagna_sign
                _ak_d1_sign = planet_signs.get(ak_planet, lagna_sign) if ak_planet else lagna_sign
                _seventh_sign = (lagna_sign + 6) % 12

                # Sthira Karakas
                _sthira_k = compute_sthira_karakas(shadbala_ratios, planet_lons)

                # Karakamsha + Svamsha
                _karakamsha = analyze_karakamsha(
                    ak_d9_sign=_ak_d9_sign, planet_signs=planet_signs,
                    lagna_sign=lagna_sign, planet_lons=planet_lons,
                    shadbala_ratios=shadbala_ratios,
                )
                _svamsha = compute_svamsha(_ak_d9_sign)

                # Jaimini Yogas
                _j_yogas = compute_jaimini_yogas(
                    karakas_list=karakas_list or [],
                    planet_signs=planet_signs,
                    ak_d9_sign=_ak_d9_sign,
                    planet_d9_signs=_planet_d9_signs,
                    planet_lons=planet_lons,
                )

                # Arudha Extended Analysis
                _arudha_ext = compute_arudha_extended_analysis(lagna_sign, planet_signs)

                def _trim(d: dict) -> dict:
                    return {k: (v[:5] if k == "periods" else v) for k, v in d.items()}

                # Additional Jaimini Dasha systems
                _shoola  = _trim(compute_shoola_dasha(
                    lagna_sign, _seventh_sign, planet_lons, birth_dt, shadbala_ratios))
                _niryana = _trim(compute_niryana_shoola_dasha(
                    lagna_sign, _seventh_sign, planet_lons, birth_dt, shadbala_ratios))
                _brahma  = _trim(compute_brahma_dasha(
                    lagna_sign, _seventh_sign, _ak_d1_sign, planet_lons, birth_dt, shadbala_ratios))
                _navm    = _trim(compute_navamsha_dasha(
                    _d9_lagna, _planet_d9_signs, planet_lons, birth_dt))
                _sudasa  = _trim(compute_sudasa(
                    planet_lons.get("MOON", 90.0), chart.lagna_degree,
                    planet_lons, birth_dt, shadbala_ratios))
                _drig    = _trim(compute_drig_dasha(lagna_sign, birth_dt))
                _trikona = _trim(compute_trikona_dasha(
                    lagna_sign, planet_lons, birth_dt, planet_houses, shadbala_ratios))

                # Narayana Dasha (Phase 1C 2026-03-02)
                _narayana_periods = compute_narayana_dasha(birth_dt, lagna_sign, planet_lons)
                _narayana_active  = get_active_narayana(_narayana_periods, birth_dt)

                jaimini_extended = {
                    "sthira_karakas":   _sthira_k,
                    "karakamsha":       _karakamsha,
                    "svamsha":          _svamsha,
                    "jaimini_yogas":    _j_yogas,
                    "arudha_extended":  _arudha_ext,
                    "shoola_dasha":     _shoola,
                    "niryana_shoola":   _niryana,
                    "brahma_dasha":     _brahma,
                    "navamsha_dasha":   _navm,
                    "sudasa":           _sudasa,
                    "drig_dasha":       _drig,
                    "trikona_dasha":    _trikona,
                    "narayana_dasha":   {"periods": _narayana_periods[:12], "active": _narayana_active},
                }
            except Exception:
                jaimini_extended = {}

        # ── File 5: Kalachakra + Medical + Conditional Dashas ────
        file5_analysis: Dict[str, Any] = {}
        if _FILE5_AVAILABLE:
            try:
                # Kalachakra Dasha
                _kalach = compute_kalachakra_dasha(
                    moon_longitude=planet_lons.get("MOON", 0.0),
                    birth_year=birth_dt.year,
                    max_periods=9,
                )

                # Deha/Jeeva transit analysis (Saturn and Rahu current signs)
                _sat_sign = SIGN_NAMES_LIST[planet_signs.get("SATURN", 0)] if isinstance(planet_signs.get("SATURN"), int) else planet_signs.get("SATURN", "Aries")
                _rahu_sign = SIGN_NAMES_LIST[planet_signs.get("RAHU", 0)] if isinstance(planet_signs.get("RAHU"), int) else planet_signs.get("RAHU", "Aries")
                _djt = analyze_deha_jeeva_transits(
                    _kalach.get("deha_sign", "Aries"),
                    _kalach.get("jeeva_sign", "Aries"),
                    _sat_sign, _rahu_sign,
                )

                # Medical Analysis
                _combust = [p for p in retrogrades if p != "RAHU" and p != "KETU"]  # placeholder
                _vargottama_ps: List[str] = []
                try:
                    from vedic_engine.core.divisional import D9 as _d9fv
                    for _pname, _plon in planet_lons.items():
                        if _pname in ("RAHU", "KETU"):
                            continue
                        _d1s = int(_plon % 360 / 30) % 12
                        _d9s = _d9fv(_plon)
                        if _d1s == _d9s:
                            _vargottama_ps.append(_pname)
                except Exception:
                    pass

                # Determine strongest entity for longevity
                _sun_sb = shadbala_ratios.get("SUN", 0)
                _moon_sb = shadbala_ratios.get("MOON", 0)
                _lagna_sb = max(shadbala_ratios.values()) if shadbala_ratios else 1.0
                if _sun_sb >= _moon_sb and _sun_sb >= _lagna_sb * 0.6:
                    _strongest = "SUN"
                elif _moon_sb >= _sun_sb and _moon_sb >= _lagna_sb * 0.6:
                    _strongest = "MOON"
                else:
                    _strongest = "LAGNA"

                _planet_signs_str: Dict[str, str] = {}
                for _pp, _ps in planet_signs.items():
                    if isinstance(_ps, int):
                        _planet_signs_str[_pp] = SIGN_NAMES_LIST[_ps % 12]
                    else:
                        _planet_signs_str[_pp] = str(_ps)

                _medical = compute_medical_analysis(
                    planet_lons=planet_lons,
                    planet_signs=_planet_signs_str,
                    planet_houses=planet_houses,
                    lagna_sign=lagna_sign,
                    lagna_longitude=chart.lagna_degree,
                    combust_planets=_combust,
                    retrograde_planets=retrogrades,
                    vargottama_planets=_vargottama_ps,
                    strongest_entity=_strongest,
                )

                # Conditional Dashas — check eligibility
                _d9_lagna_name = SIGN_NAMES_LIST[_d9_lagna % 12] if "_d9_lagna" in dir() else "Aries"
                _lagna_name = SIGN_NAMES_LIST[lagna_sign % 12]
                _lagna_hora = "sun" if lagna_sign % 2 == 0 else "moon"

                # ── Daytime / Paksha — computed from actual astronomy ──────
                try:
                    from vedic_engine.core.sunrise_utils import (
                        compute_is_daytime as _calc_daytime,
                        compute_paksha as _calc_paksha,
                    )
                    _is_daytime = _calc_daytime(
                        latitude=chart.birth_info.latitude,
                        longitude=chart.birth_info.longitude,
                        birth_dt_local=birth_dt,
                        tz_offset_hours=chart.birth_info.timezone,
                    )
                    _paksha = _calc_paksha(sun_lon, moon_lon)
                except Exception:
                    _is_daytime = True    # safe fallback
                    _paksha = "shukla"   # safe fallback

                _lagna_lord = SIGN_LORDS_MAP.get(lagna_sign, "MARS")
                _seventh_lord = SIGN_LORDS_MAP.get((lagna_sign + 6) % 12, "VENUS")
                _tenth_lord = SIGN_LORDS_MAP.get((lagna_sign + 9) % 12, "SATURN")

                _cond_eligibility = check_all_conditional_eligibility(
                    is_daytime=_is_daytime,
                    paksha=_paksha,
                    lagna_hora=_lagna_hora,
                    d1_lagna_sign=_lagna_name,
                    d9_lagna_sign=_d9_lagna_name,
                    d12_lagna_sign=_lagna_name,  # simplified
                    lagna_lord=_lagna_lord,
                    seventh_lord=_seventh_lord,
                    tenth_lord=_tenth_lord,
                    planet_houses=planet_houses,
                )

                # Compute ELIGIBLE conditional dashas
                _moon_lon_val = planet_lons.get("MOON", 0.0)
                _cond_dashas: Dict[str, Any] = {}

                if _cond_eligibility.get("Shodashottari", {}).get("eligible"):
                    _cond_dashas["shodashottari"] = compute_shodashottari(_moon_lon_val)
                if _cond_eligibility.get("Dwadasottari", {}).get("eligible"):
                    _cond_dashas["dwadasottari"] = compute_dwadasottari(_moon_lon_val)
                if _cond_eligibility.get("Panchottari", {}).get("eligible"):
                    _cond_dashas["panchottari"] = compute_panchottari(_moon_lon_val)
                if _cond_eligibility.get("Shatabdika", {}).get("eligible"):
                    _cond_dashas["shatabdika"] = compute_shatabdika(_moon_lon_val)
                if _cond_eligibility.get("Chaturaashiti", {}).get("eligible"):
                    _cond_dashas["chaturaashiti"] = compute_chaturaashiti(_moon_lon_val)
                if _cond_eligibility.get("Dwisaptati", {}).get("eligible"):
                    _cond_dashas["dwisaptati"] = compute_dwisaptati(_moon_lon_val)
                if _cond_eligibility.get("Shat_Trimsa", {}).get("eligible"):
                    _cond_dashas["shat_trimsa"] = compute_shat_trimsa(_moon_lon_val)

                # Always compute Moola and Tara (universal)
                _cond_dashas["moola_dasha"] = compute_moola_dasha(
                    planet_houses=planet_houses,
                    strongest_initiator=_strongest,
                    planet_signs=_planet_signs_str,
                )
                _cond_dashas["tara_dasha"] = compute_tara_dasha(_moon_lon_val)

                file5_analysis = {
                    "kalachakra": _kalach,
                    "deha_jeeva_transits": _djt,
                    "medical": _medical,
                    "conditional_eligibility": _cond_eligibility,
                    "conditional_dashas": _cond_dashas,
                }
            except Exception as _f5err:
                file5_analysis = {"error": str(_f5err)}

        # ── Phase 1F: Longevity + Nadi Amsha ─────────────────────
        _longevity: Dict = {}
        if _LONGEVITY_AVAILABLE:
            try:
                _hora_lagna_sign: Optional[int] = None
                _sp = special_pts if isinstance(special_pts, dict) else {}
                _hl_raw = _sp.get("hora_lagna") or _sp.get("HL")
                if isinstance(_hl_raw, dict):
                    _hora_lagna_sign = _hl_raw.get("sign") or _hl_raw.get("sign_index")
                elif isinstance(_hl_raw, (int, float)):
                    _hora_lagna_sign = int(_hl_raw)
                _pdig2 = {pn: getattr(getattr(chart.planets.get(pn, None),
                                              "dignity", None), "name", "NEUTRAL")
                          for pn in planet_lons}
                _retro_bool = {p: bool(v) for p, v in retrogrades.items()}
                _longevity = compute_longevity(
                    planet_lons=planet_lons,
                    lagna_sign=lagna_sign,
                    lagna_lon=chart.lagna_degree,
                    hora_lagna_sign=_hora_lagna_sign,
                    retrogrades=_retro_bool,
                    planet_signs=planet_signs,
                    planet_dignities=_pdig2,
                )
            except Exception:
                _longevity = {}

        _nadi_amsha: Dict = {}
        if _NADI_AMSHA_AVAILABLE:
            try:
                _nadi_amsha = compute_nadi_amsha(
                    planet_lons=planet_lons,
                    lagna_lon=chart.lagna_degree,
                )
            except Exception:
                _nadi_amsha = {}

        # ── Phase 3A: Nadi Jyotish timing signals ─────────────────
        _nadi_3a: Dict = {}
        if _NADI_TIMING_AVAILABLE:
            try:
                _age_3a = max(0, int((datetime.now() - birth_dt).days / 365.25))
                # Navamsha ASC longitude: approximate as (natal ASC lon × 9) mod 360
                _nav_asc_3a = (chart.lagna_degree * 9.0) % 360.0
                _nadi_3a = compute_all_nadi_signals(
                    planet_signs=planet_signs,
                    planet_houses=planet_houses,
                    planet_lons=planet_lons,
                    retrogrades=retrogrades,
                    navamsha_asc_lon=_nav_asc_3a,
                    birth_date=birth_dt.date(),
                    age_years=_age_3a,
                    transit_saturn_lon=None,  # not available in static scope
                    patel_cycles=2,
                )
            except Exception:
                _nadi_3a = {}

        # ── Phase 3B: Hellenistic timing signals ──────────────────
        _hellen_3b: Dict = {}
        if _HELLENISTIC_AVAILABLE:
            try:
                _is_day_3b = (6 <= birth_dt.hour < 18)
                _age_3b    = max(0, int((datetime.now() - birth_dt).days / 365.25))
                _hellen_3b = compute_all_hellenistic_signals(
                    natal_asc_lon=chart.lagna_degree,
                    natal_asc_sign=lagna_sign,
                    sun_lon=sun_lon,
                    moon_lon=moon_lon,
                    planet_longitudes=planet_lons,
                    birth_date=birth_dt.date(),
                    target_date=datetime.now().date(),
                    age_years=_age_3b,
                    is_daytime=_is_day_3b,
                )
            except Exception:
                _hellen_3b = {}

        # ── Phase 3E: Scientific correlations (birth-month, lunar) ─
        _sci_3e: Dict = {}
        if _SCIENCE_AVAILABLE:
            try:
                _sci_3e["birth_month_risk"] = compute_birth_month_risk(birth_dt.month)
            except Exception:
                pass

        # ── Phase 1E: Kota Chakra + SBC Grid ─────────────────────
        _kota_chakra: Dict = {}
        _sbc_grid: Dict = {}
        try:
            _moon_nak_idx = int(moon_lon / (360.0 / 27))
            _kota_chakra = compute_kota_chakra(_moon_nak_idx)
        except Exception:
            _kota_chakra = {}
        try:
            _moon_nak_idx = int(moon_lon / (360.0 / 27))
            _birth_tithi = int(((moon_lon - sun_lon) % 360) / 12) + 1
            # Python weekday() 0=Mon → convert to 0=Sun standard
            _birth_wday = (birth_dt.weekday() + 1) % 7
            _sbc_grid = construct_sbc_grid(
                natal_nakshatra=_moon_nak_idx,
                natal_sign=moon_sign,
                birth_tithi=_birth_tithi,
                birth_weekday=_birth_wday,
            )
        except Exception:
            _sbc_grid = {}

        return {
            "meta": {
                "lagna_sign": lagna_sign,
                "lagna_lon": chart.lagna_degree,
                "moon_sign": moon_sign,
                "moon_lon": moon_lon,
                "birth_dt": birth_dt.isoformat(),
            },
            "chart_raw": {
                "planet_lons": planet_lons,
                "planet_signs": planet_signs,
                "planet_houses": planet_houses,
                "retrogrades": retrogrades,
            },
            "vargas": vargas,
            "aspects": {"asp_map": asp_map, "drik_bala": drik_bala},
            "shadbala": shadbala,
            "shadbala_ratios": shadbala_ratios,
            "ashtakvarga": av_data,
            "bhavabala": bhavabala,
            "bhavabala_domain_modifiers": bhavabala_domain_modifiers,
            "vimshopak": vimshopak,
            "shadvarga_vimshopak": shadvarga_vimshopak,
            "yogas": yogas,
            "karakas": karakas,
            "kp": {"planet_sigs": kp_sigs, "cusp_sigs": cusp_sigs},
            "domain_map":       domain_map,
            "house_lords":      house_lords,
            "functional":       func_analysis,
            "graha_yuddha":     wars,
            "special_points":   special_pts,
            "avasthas":         avasthas,
            "special_degrees":  special_degrees,
            "dispositor_graph": _compute_dispositor_graph_safe(planet_signs, shadbala_ratios),
            "varga_report":     _compute_varga_report_safe(
                                    planet_lons, vargas, chart.lagna_degree),
            "remedies":         _compute_remedies_safe(
                                    planet_signs, planet_houses, shadbala_ratios,
                                    retrogrades, wars),
            "arudha_padas":     arudha,
            "rashi_drishti":    rashi_drishti,
            "yoga_compounding": yoga_compounding,
            "dhana_stacking":   dhana_stacking,
            "ul_sign":          ul_sign,
            "ak_planet":        ak_planet,
            "dk_planet":        dk_planet,
            "karakas_dict":     karakas_dict,
            "badhaka":          badhaka_info,
            "nakshatra_analysis": nakshatra_analysis,
            "varshaphala":      varshaphala,
            "jaimini_extended": jaimini_extended,
            "file5_analysis":   file5_analysis,
            # ── Phase 1D-1F: unified computed outputs ──────────────
            "computed": {
                "yogas":       _extended_yogas,
                "kota_chakra": _kota_chakra,
                "sbc_grid":    _sbc_grid,
                "longevity":   _longevity,
                "nadi_amsha":  _nadi_amsha,
                # ── Phase 3A: Nadi Jyotish
                "bcp_active_house":              _nadi_3a.get("bcp_active_house"),
                "bcp_active_planets":            _nadi_3a.get("bcp_active_planets", []),
                "nadi_saturn_activated_planets": [x["planet"] for x in _nadi_3a.get("nadi_saturn_activated", [])],
                "patel_marriage_candidates":     _nadi_3a.get("patel_marriage_candidates", []),
                "bnn_graph":                     _nadi_3a.get("bnn_graph", []),
                "bnn_connectivity_scores":       _nadi_3a.get("bnn_connectivity_scores", {}),
                "spouse_career_sign":            _nadi_3a.get("spouse_career_sign"),
                "spouse_career_sign_name":       _nadi_3a.get("spouse_career_sign_name"),
                # ── Phase 3B: Hellenistic
                "annual_profection":             _hellen_3b.get("annual_profection", {}),
                "hellenistic_sect":              _hellen_3b.get("hellenistic_sect", {}),
                "lot_of_fortune_lon":            _hellen_3b.get("lot_of_fortune_lon"),
                "lot_of_spirit_lon":             _hellen_3b.get("lot_of_spirit_lon"),
                "zodiacal_releasing_spirit":     _hellen_3b.get("zodiacal_releasing_spirit", {}),
                "zodiacal_releasing_fortune":    _hellen_3b.get("zodiacal_releasing_fortune", {}),
                "midpoints":                     _hellen_3b.get("midpoints", {}),
                # ── Phase 3E: Science
                "birth_month_risk":              _sci_3e.get("birth_month_risk", {}),
                "lunar_health_modifier":         None,  # populated in predict() with transit moon
            },
        }

    # ── 2. Dynamic Analysis ─────────────────────────────────────
    def analyze_dynamic(self, chart: VedicChart, static: Dict,
                        on_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Compute time-dependent features: dashas + transits for on_date.
        """
        if on_date is None:
            on_date = datetime.now()

        moon_lon  = static["meta"]["moon_lon"]
        moon_sign = static["meta"]["moon_sign"]
        try:
            birth_dt = datetime.fromisoformat(f"{chart.birth_info.date}T{chart.birth_info.time}")
        except Exception:
            birth_dt = datetime.fromisoformat(static["meta"]["birth_dt"])

        # ── Vimshottari dasha (3 levels)
        try:
            vim_periods = compute_mahadasha_periods(moon_lon, birth_dt, levels=3)
            vim_active  = get_active_dasha(vim_periods, on_date)
            vim_sandhi  = detect_dasha_sandhi(vim_periods, on_date)
        except Exception as e:
            vim_periods, vim_active, vim_sandhi = [], {"error": str(e)}, {"in_sandhi": False}

        # ── Dasha Diagnostic Matrix (6-factor analysis)
        dasha_diag: Dict = {}
        if _DIAG_MATRIX_AVAILABLE:
            try:
                _vim_md = ""
                _vim_ad = ""
                if isinstance(vim_active, dict):
                    _vim_md = vim_active.get("mahadasha", vim_active.get("planet", ""))
                    _vim_ad = vim_active.get("antardasha", _vim_md)
                elif isinstance(vim_active, list) and vim_active:
                    _vim_md = vim_active[0].get("planet", "")
                    _vim_ad = vim_active[1].get("planet", _vim_md) if len(vim_active) > 1 else _vim_md
                if _vim_md:
                    _retro_dict = static.get("chart_raw", {}).get("retrogrades", {})
                    _retro_list = [p for p, r in _retro_dict.items() if r]
                    _ls         = static.get("meta", {}).get("lagna_sign", 0)
                    _hl_static  = {int(k): v for k, v in static.get("house_lords", {}).items()}
                    _lagna_lord = _hl_static.get(1, "")
                    dasha_diag = dasha_diagnostic_matrix(
                        dasha_planet=_vim_md,
                        antardasha_planet=_vim_ad,
                        planet_houses=static.get("chart_raw", {}).get("planet_houses", {}),
                        planet_lons=static.get("chart_raw", {}).get("planet_lons", {}),
                        house_lords=_hl_static,
                        shadbala_ratios=static.get("shadbala_ratios", {}),
                        lagna_lord=_lagna_lord,
                        retrograde_planets=_retro_list,
                        vargas=static.get("vargas"),
                    )
            except Exception as _e:
                dasha_diag = {"error": str(_e)}

        # ── Ashtottari dasha (conditional — Rahu in kendra/trikona from lagna lord)
        try:
            _lagna_sign       = static["meta"].get("lagna_sign", 2)   # 0-indexed
            _planet_signs     = static.get("chart_raw", {}).get("planet_signs", {})
            _lagna_lord_map   = {2: "MERCURY", 0: "MARS", 1: "VENUS", 3: "MOON", 4: "SUN",
                                 5: "MERCURY", 6: "VENUS", 7: "MARS", 8: "JUPITER",
                                 9: "SATURN", 10: "SATURN", 11: "JUPITER"}
            _lagna_lord_name  = _lagna_lord_map.get(_lagna_sign, "MERCURY")
            _lagna_lord_sign  = _planet_signs.get(_lagna_lord_name, _lagna_sign)
            _rahu_sign        = _planet_signs.get("RAHU", 1)  # default Taurus
            ashto = ashtottari_details_on_date(
                moon_lon, birth_dt,
                lagna_sign=_lagna_sign,
                lagna_lord_sign=_lagna_lord_sign,
                rahu_sign=_rahu_sign,
                on_date=on_date, levels=2,
            )
        except Exception as e:
            ashto = {"eligible": False, "active": {}, "error": str(e)}

        # ── Yogini dasha
        try:
            yog_periods = compute_yogini_periods(moon_lon, birth_dt)
            yog_active  = get_active_yogini(yog_periods, on_date)
        except Exception as e:
            yog_periods, yog_active = [], {"error": str(e)}

        # ── Transits
        try:
            transit_pos = get_transit_positions(on_date)
            av_data = static.get("ashtakvarga", {})
            bhinna_av = av_data.get("bhinna", {}) if isinstance(av_data, dict) else {}
            sarva_av  = av_data.get("sarva", None) if isinstance(av_data, dict) else None

            natal_moon_nak = int(moon_lon / (360.0 / 27))
            transit_evals = evaluate_all_transits(
                transit_positions=transit_pos,
                natal_moon_sign=moon_sign,
                bhinna_av=bhinna_av,
                sarva_av=sarva_av,
                natal_moon_nak=natal_moon_nak,
            )
        except Exception as e:
            transit_pos, transit_evals = {}, {"error": str(e)}

        # ── Sudarshana Chakra evaluation (Phase 1E) ─────────────
        sudarshana_eval: Dict = {}
        try:
            _t_signs = {p: int(lon % 360 / 30) % 12
                        for p, lon in transit_pos.items()
                        if isinstance(lon, (int, float))}
            _s_lagna = static.get("meta", {}).get("lagna_sign", 0)
            _s_moon  = static.get("meta", {}).get("moon_sign", 0)
            _s_sun   = int(
                static.get("chart_raw", {}).get("planet_lons", {}).get("SUN", 0)
                % 360 / 30
            ) % 12
            sudarshana_eval = {
                "planets": evaluate_sudarshana_all_planets(
                    _t_signs, _s_lagna, _s_moon, _s_sun
                ),
            }
            try:
                _birth_dt_s = datetime.fromisoformat(
                    static.get("meta", {}).get("birth_dt", "")
                )
                _cy = (
                    on_date.year - _birth_dt_s.year
                    - ((on_date.month, on_date.day) < (_birth_dt_s.month, _birth_dt_s.day))
                )
                sudarshana_eval["dasha"] = compute_sudarshana_dasha(
                    _s_lagna, max(0, _cy)
                )
            except Exception:
                pass
        except Exception:
            sudarshana_eval = {}

        # ── Sade Sati
        sade_sati = {}
        if "SATURN" in transit_pos:
            sat_sign = sign_of(transit_pos["SATURN"])
            sat_bav  = bhinna_av.get("SATURN") if isinstance(bhinna_av, dict) else None
            sade_sati = detect_sade_sati(sat_sign, moon_sign, sat_bav)

        # ── Ruling planets (KP) — needs longitude not sign index
        try:
            lagna_lon = static.get("meta", {}).get("lagna_lon", moon_lon)
            ruling = compute_ruling_planets(on_date, moon_lon, lagna_lon)
        except Exception as e:
            ruling = {"error": str(e)}

        # ── Panchanga (5 limbs of Vedic calendar for current date)
        try:
            sun_transit  = transit_pos.get("SUN", 0.0)
            moon_transit = transit_pos.get("MOON", 0.0)
            panchanga = compute_panchanga(sun_transit, moon_transit, on_date)
        except Exception as e:
            panchanga = {"error": str(e)}

        # ── Dasha lord transit tracker
        try:
            vim_active_here = dynamic_vim_active if 'dynamic_vim_active' in dir() else vim_active
            md_lord = "RAHU"
            ad_lord = "SATURN"
            if isinstance(vim_active, dict):
                md_lord = vim_active.get("mahadasha", vim_active.get("planet", "RAHU"))
                ad_lord = vim_active.get("antardasha", vim_active.get("planet", "SATURN"))
            elif isinstance(vim_active, list) and vim_active:
                md_lord = vim_active[0].get("planet", "RAHU")
                ad_lord = vim_active[1].get("planet", "SATURN") if len(vim_active) > 1 else md_lord
            natal_positions = static.get("chart_raw", {}).get("planet_lons", {})
            natal_lagna_lon = static.get("meta", {}).get("lagna_lon", 0.0)
            dasha_transit_info = analyze_dasha_lord_transit(
                mahadasha_lord=md_lord,
                antardasha_lord=ad_lord,
                transit_positions=transit_pos,
                natal_positions=natal_positions,
                natal_moon_lon=moon_lon,
                natal_lagna_lon=natal_lagna_lon,
                on_date=on_date,
            )
            ingress_calendar = compute_ingress_calendar(transit_pos, on_date)
        except Exception as e:
            dasha_transit_info = {"error": str(e)}
            ingress_calendar = []

        # ── Transit-to-natal longitude aspects (continuous orb weighting + applying/separating)
        try:
            natal_lons = static.get("chart_raw", {}).get("planet_lons", {})
            transit_aspects = compute_transit_aspects(transit_pos, natal_lons)
        except Exception as e:
            transit_aspects = {"error": str(e)}

        # ── Secondary progressions + Solar arc directions (day-for-year symbolic chart)
        try:
            natal_lons = static.get("chart_raw", {}).get("planet_lons", {})
            progressions = compute_secondary_progressions(
                natal_positions=natal_lons,
                birth_datetime=birth_dt,
                analysis_date=on_date,
                position_fn=get_transit_positions,
            )
        except Exception as e:
            progressions = {"error": str(e)}

        # ── Solar terms (Sun at every 15° multiple — 24 Vedic/East-Asian timing markers)
        try:
            solar_terms = compute_solar_terms(transit_pos.get("SUN", 0.0), on_date)
        except Exception as e:
            solar_terms = []

        # ── Jaimini Chara Dasha
        try:
            _ps  = static.get("chart_raw", {}).get("planet_signs", {})
            _pls = static.get("chart_raw", {}).get("planet_lons",  {})
            _ls  = static.get("meta", {}).get("lagna_sign", 0)
            # Pass Jaimini karakas + UL for marriage/AK enrichment
            _karakas_dict = static.get("karakas_dict", {})
            _ul_sign      = static.get("ul_sign")
            _dk_planet    = static.get("dk_planet")
            chara = chara_dasha_details_on_date(
                lagna_sign=_ls,
                planet_signs=_ps,
                planet_lons=_pls,
                birth_date=birth_dt,
                on_date=on_date,
                levels=2,
                karakas=_karakas_dict,
                ul_sign=_ul_sign,
                dara_karaka=_dk_planet,
            )
        except Exception as e:
            chara = {"error": str(e)}

        return {
            "date": on_date.isoformat(),
            "vimshottari": {
                "periods_summary": len(vim_periods),
                "active": vim_active,
                "sandhi": vim_sandhi,
                "retrograde_lords": {
                    lvl: pname
                    for lvl, pname in {
                        "mahadasha":    vim_active.get("mahadasha", "") if isinstance(vim_active, dict) else "",
                        "antardasha":   vim_active.get("antardasha", "") if isinstance(vim_active, dict) else "",
                    }.items()
                    if pname and static.get("chart_raw", {}).get("retrogrades", {}).get(pname, False)
                },
            },
            "ashtottari": ashto,
            "yogini": {"active": yog_active},
            "transits": transit_evals,
            "transit_positions": transit_pos,
            "sade_sati": sade_sati,
            "ruling_planets": ruling,
            "panchanga": panchanga,
            "dasha_transit": dasha_transit_info,
            "ingress_calendar": ingress_calendar,
            "transit_aspects":  transit_aspects,
            "bhrigu_bindu_transit": _compute_bb_transit_safe(transit_pos, static),
            "progressions":     progressions,
            "solar_terms":      solar_terms,
            "chara_dasha":      chara,
            "lunations":        _compute_lunations_safe(on_date, static, vim_periods, on_date),
            "timing_windows":   _compute_timing_windows_safe(on_date, transit_pos, static),
            "dasha_diagnostic": dasha_diag,
            "dasha_quality":    _compute_dasha_quality_safe(vim_active, static, on_date),
            "retrograde_dasha": _compute_retrograde_dasha_safe(
                vim_active, transit_pos, static
            ),
            "sudarshana":       sudarshana_eval,
        }

    # ── 3+4. Full Prediction ─────────────────────────────────────

    def predict(self,
                chart: VedicChart,
                domain: str = "career",
                on_date: Optional[datetime] = None,
                static: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Full domain prediction with confidence scoring.

        Args:
            chart:    The VedicChart to analyse
            domain:   life area ('career','finance','marriage','health',...)
            on_date:  prediction date (default: today)
            static:   pre-computed static analysis (avoids recomputing)

        Returns:
            Structured prediction report dict.
        """
        if on_date is None:
            on_date = datetime.now()
        if static is None:
            static = self.analyze_static(chart)

        dynamic = self.analyze_dynamic(chart, static, on_date)

        # ── Gather inputs for confidence scoring
        vim_active = dynamic["vimshottari"].get("active", {})
        yog_active = dynamic["yogini"].get("active", {})

        dasha_planet = "SATURN"       # fallback
        antar_planet = "SATURN"
        if isinstance(vim_active, list) and vim_active:
            dasha_planet = vim_active[0].get("planet", dasha_planet)
            if len(vim_active) > 1:
                antar_planet = vim_active[1].get("planet", antar_planet)
        elif isinstance(vim_active, dict):
            # Keys: mahadasha, antardasha, pratyantardasha
            dasha_planet = vim_active.get("mahadasha",
                           vim_active.get("planet", dasha_planet))
            antar_planet = vim_active.get("antardasha",
                           vim_active.get("planet", dasha_planet))

        yogini_lord = (yog_active.get("major_planet",
                        yog_active.get("planet")) if isinstance(yog_active, dict)
                       else None) or dasha_planet

        av_data   = static.get("ashtakvarga", {})
        sarva_av  = av_data.get("sarva") if isinstance(av_data, dict) else None
        bhinna_av = av_data.get("bhinna", {}) if isinstance(av_data, dict) else {}
        dp_bav    = bhinna_av.get(dasha_planet) if isinstance(bhinna_av, dict) else None

        # ── Karaka-BAV data bundle for 3-signal AV blend (§AV upgrade) ──
        karaka_bav_data: Optional[Dict] = None
        if isinstance(bhinna_av, dict) and bhinna_av:
            _planet_signs_map = static.get("chart_raw", {}).get("planet_signs", {})
            if not _planet_signs_map and chart:
                _planet_signs_map = {name: p.sign_index
                                     for name, p in chart.planets.items()}
            _house_lords_map  = {int(k): v for k, v in static.get("house_lords", {}).items()}
            karaka_bav_data = {
                "bhinna":       bhinna_av,
                "planet_signs": _planet_signs_map,
                "house_lords":  _house_lords_map,
            }

        domain_houses  = DOMAIN_HOUSES.get(domain.lower(), [1, 10])
        negator_houses = DOMAIN_NEGATORS.get(domain.lower(), [])
        domain_planets_list = DOMAIN_PLANETS.get(domain.lower(), [])

        relevant_signs = [(static["meta"]["lagna_sign"] + h - 1) % 12 for h in domain_houses]

        transit_evals = dynamic.get("transits", {})
        if isinstance(transit_evals, dict) and "error" in transit_evals:
            transit_evals = {}

        # ── Phase 2C: Vedha nullification + Phase 2D: Sudarshana blend ───────────
        # Creates transit_evals_adj — modified copy used by compute_confidence().
        # Original transit_evals is untouched (used for display/reporting).
        transit_evals_adj: Dict[str, Dict] = {}
        try:
            if transit_evals:
                # Map of {planet: house_from_moon} for all transiting planets
                _all_h_from_moon = {
                    _p: _v.get("house_from_moon", 0)
                    for _p, _v in transit_evals.items()
                    if isinstance(_v, dict)
                }
                # Sudarshana scores: normalize final_score [-3,+3] → [0,1]
                _suda_list = dynamic.get("sudarshana", {}).get("planets", []) or []
                _suda_map  = {
                    _e["planet"]: min(1.0, max(0.0, (_e["final_score"] + 3.0) / 6.0))
                    for _e in _suda_list
                    if isinstance(_e, dict) and "planet" in _e and "final_score" in _e
                }
                for _pn, _pd in transit_evals.items():
                    if not isinstance(_pd, dict):
                        transit_evals_adj[_pn] = _pd
                        continue
                    _entry = dict(_pd)  # shallow copy — never mutate original
                    _net   = float(_entry.get("net_score", 0.3))

                    # 2C — Vedha: favorable transit obstructed → 80% reduction
                    _oth_h = {_k: _v for _k, _v in _all_h_from_moon.items() if _k != _pn}
                    _vh = check_vedha(
                        transiting_planet=_pn,
                        transit_house_from_moon=_all_h_from_moon.get(_pn, 0),
                        other_planet_houses_from_moon=_oth_h,
                    )
                    if _vh.get("vedha_blocked"):
                        _net = round(_net * 0.20, 4)   # 80% reduction
                        _entry["_vedha_blocked_2c"] = _vh["vedha_by"]
                    elif _vh.get("vipareeta"):
                        # Vipareeta: negative transit cancelled → lift toward neutral
                        _net = round(min(0.50, _net + 0.15), 4)
                        _entry["_vipareeta_2c"] = _vh["vipareeta_by"]

                    # 2D — Sudarshana: blend triple-frame score (60% existing / 40% SC)
                    if _pn in _suda_map:
                        _suda_n = _suda_map[_pn]
                        _net = round(0.60 * _net + 0.40 * _suda_n, 4)
                        _entry["_sudarshana_norm_2d"] = _suda_n

                    _entry["net_score"] = max(0.0, min(1.0, _net))
                    transit_evals_adj[_pn] = _entry
            else:
                transit_evals_adj = {}
        except Exception:
            transit_evals_adj = dict(transit_evals)   # fallback: pass through unchanged

        # ── Phase 2I: Upagraha affliction + Phase 2K: Shodhya Pinda — second pass ───
        # 2I: Transit planets occupying the natal sign of a major aprakasha (shadow)
        #     upagraha (Gulika, Mandi, Dhuma, Vyatipata) are further penalised.
        # 2K: Each planet's Shodhya Pinda (net post-shodhana bindu strength) is used
        #     as a transit-effectiveness multiplier (0.80–1.20 range).
        try:
            _sp_pts = static.get("special_points", {})
            # Collect natal sign_idx of the four most malefic sensitive points
            _malefic_upagraha_signs: set = set()
            for _mname in ("gulika", "mandi"):
                _mu = _sp_pts.get(_mname, {})
                if isinstance(_mu, dict) and "sign_idx" in _mu:
                    _malefic_upagraha_signs.add(int(_mu["sign_idx"]))
            _upag_block = _sp_pts.get("upagrahas", {})
            if isinstance(_upag_block, dict):
                for _usubname in ("dhuma", "vyatipata"):  # most malefic of 5
                    _us = _upag_block.get(_usubname, {})
                    if isinstance(_us, dict) and "sign_idx" in _us:
                        _malefic_upagraha_signs.add(int(_us["sign_idx"]))

            # Shodhya Pinda per planet (already in static[ashtakvarga])
            _shodhya_pinda: dict = (
                static.get("ashtakvarga", {}).get("shodhya_pinda", {}) or {}
            )
            # Normalization reference: ~350 is a typical mid-strength chart value.
            # Factor is clamped to [0.80, 1.20] so the swing never exceeds ±20%.
            _SP_REF = 350.0

            for _pn2, _pd2 in list(transit_evals_adj.items()):
                if not isinstance(_pd2, dict):
                    continue
                _net2 = float(_pd2.get("net_score", 0.3))

                # 2I: Upagraha affliction — transiting into a malefic natal sign
                _tr_sign = _pd2.get("transit_sign_idx", -1)
                if isinstance(_tr_sign, (int, float)) and int(_tr_sign) in _malefic_upagraha_signs:
                    _net2 = round(_net2 * 0.88, 4)   # 12% affliction penalty
                    _pd2["_upagraha_afflicted_2i"] = True

                # 2K: Shodhya Pinda scaling
                _sp_val = _shodhya_pinda.get(_pn2.upper())
                if _sp_val is not None:
                    _sp_factor = round(min(1.20, max(0.80, float(_sp_val) / _SP_REF)), 4)
                    _net2 = round(_net2 * _sp_factor, 4)
                    _pd2["_sp_factor_2k"] = _sp_factor

                # Phase 3F.2: Nadi Saturn activation bonus (+10% for activated domain planets)
                _nadi_sat_3f = static.get("computed", {}).get("nadi_saturn_activated_planets", [])
                if _nadi_sat_3f and _pn2 in _nadi_sat_3f and _pn2 in domain_planets_list:
                    _net2 = round(min(1.0, _net2 + 0.10), 4)
                    _pd2["_nadi_saturn_activated_3f"] = True

                _pd2["net_score"] = round(max(0.0, min(1.0, _net2)), 4)
                transit_evals_adj[_pn2] = _pd2
        except Exception:
            pass   # 2I/2K are best-effort; transit_evals_adj stays as-is

        kp_sigs = static.get("kp", {}).get("planet_sigs", {}) or {}
        # Transform Dict[str, Dict] → Dict[str, List[int]] (extract signified_houses)
        kp_sigs_houses = {
            p: (data.get("signified_houses", []) if isinstance(data, dict) else [])
            for p, data in kp_sigs.items()
        }
        yogas   = static.get("yogas", []) or []

        # ── GPT accuracy layer (yoga fructification + KP ambiguity) ──
        gpt_adjustments: Dict = {}
        if _GPT_REASONER_AVAILABLE:
            # 1. Yoga fructification — are detected yogas actually active?
            chart_ctx = {
                "lagna_sign": static.get("meta", {}).get("lagna_name", ""),
                "yogakarakas": static.get("functional", {}).get("yogakarakas", []),
            }
            fruct_results = resolve_yoga_fructification(
                yogas, dasha_planet, antar_planet, chart_ctx
            )
            if fruct_results:
                yogas = apply_yoga_fructification(yogas, fruct_results)

            # 2. KP ambiguity — when sublord signifies both domain + negator houses
            raw_kp_score_prelim = sum(
                1 for h in kp_sigs_houses.get(dasha_planet, []) if h in domain_houses
            ) / max(len(domain_houses), 1)
            kp_ambi = resolve_kp_ambiguity(
                sublord_chain=kp_sigs_houses,
                domain=domain,
                domain_houses=domain_houses,
                negator_houses=negator_houses,
                raw_kp_score=raw_kp_score_prelim,
            )
            if kp_ambi and "adjusted_kp_score" in kp_ambi:
                gpt_adjustments["adjusted_kp_score"] = kp_ambi["adjusted_kp_score"]

        # ── Extract Dasha Diagnostic Matrix params for confidence gate ──
        dasha_diag       = dynamic.get("dasha_diagnostic", {}) or {}
        dasha_house      = dasha_diag.get("dasha_house", 0)
        antardasha_house = dasha_diag.get("antardasha_house", 0)
        dasha_lord_combust    = bool(dasha_diag.get("dasha_lord_combust", False))
        dasha_lord_retrograde = bool(dasha_diag.get("dasha_lord_retrograde", False))

        # ── Promise Prerequisite Gate (Three Pillar Rule) ──────────────
        promise_result: Optional[Dict] = None
        if _PROMISE_AVAILABLE:
            try:
                planet_houses_raw_for_pr = static.get("chart_raw", {}).get("planet_houses", {})
                house_lords_for_pr        = {int(k): v for k, v in static.get("house_lords", {}).items()}
                shadbala_for_pr           = static.get("shadbala_ratios", {})
                vargas_for_pr             = static.get("vargas", {})
                planet_lons_for_pr        = static.get("chart_raw", {}).get("planet_lons", {})
                promise_result = compute_promise(
                    domain=domain,
                    planet_houses=planet_houses_raw_for_pr,
                    house_lords=house_lords_for_pr,
                    shadbala_ratios=shadbala_for_pr,
                    planet_lons=planet_lons_for_pr,
                    vargas=vargas_for_pr,
                )
            except Exception as _pe:
                promise_result = None

        # ── Build Jaimini sub-score data (wire 4 pre-computed modules → confidence) ──
        jaimini_data: Optional[Dict] = None
        try:
            _j_ext = static.get("jaimini_extended", {}) or {}
            _arudha_data = static.get("arudha_padas", {}) or {}
            _rd_data = static.get("rashi_drishti", {}) or {}
            _chara_diag_pre = dynamic.get("chara_dasha", {}) or {}
            _chara_enrich = _chara_diag_pre.get("enrichment", {}) or {}
            _chara_h = _chara_enrich.get("house_from_lagna", 0)

            # 1. Chara alignment: does active Chara Dasha sign fall in a domain house?
            _c_align = 0.3
            if _chara_h and _chara_h in domain_houses:
                _c_align = 0.75
            elif _chara_h and any(abs(_chara_h - dh) <= 1 or abs(_chara_h - dh) == 11 for dh in domain_houses):
                _c_align = 0.50

            # 2. Karakamsha score: check if karakamsha analysis shows benefic influences on domain
            _k_score = 0.3
            _kk = _j_ext.get("karakamsha", {})
            if isinstance(_kk, dict):
                _kk_houses = _kk.get("house_analyses", [])
                if isinstance(_kk_houses, list):
                    for _hinfo in _kk_houses:
                        if isinstance(_hinfo, dict) and _hinfo.get("house") in domain_houses:
                            _occ = _hinfo.get("occupants", [])
                            if any(p in {"JUPITER", "VENUS", "MERCURY"} for p in _occ):
                                _k_score = max(_k_score, 0.7)
                            elif _occ:
                                _k_score = max(_k_score, 0.5)

            # 3. Arudha alignment: relevant Arudha Pada well-placed?
            _a_align = 0.3
            _domain_arudha_key = {
                "career": "A10", "finance": "A2", "marriage": "A7", "health": "A1",
            }.get(domain.lower(), "A1")
            _a_pad = _arudha_data.get(_domain_arudha_key, {})
            if isinstance(_a_pad, dict):
                _a_sign = _a_pad.get("sign", _a_pad.get("sign_index"))
                if isinstance(_a_sign, int):
                    _a_from_lagna = ((_a_sign - static.get("meta", {}).get("lagna_sign", 0)) % 12) + 1
                    if _a_from_lagna in {1, 4, 5, 7, 9, 10}:  # kendra/trikona
                        _a_align = 0.7
                    elif _a_from_lagna in {2, 11}:  # dhana houses
                        _a_align = 0.55
                    else:
                        _a_align = 0.35

            # 4. Rashi Drishti score: benefic sign aspects to domain houses
            _rd_score = 0.3
            if isinstance(_rd_data, dict) and not _rd_data.get("error"):
                _benefic_hits = 0
                _domain_sign_set = set(relevant_signs)
                for _aspect_info in _rd_data.values():
                    if isinstance(_aspect_info, dict):
                        _from_s = _aspect_info.get("from_sign")
                        _to_s = _aspect_info.get("to_sign")
                        _planets_there = _aspect_info.get("planets", [])
                        if _to_s in _domain_sign_set and any(
                            p in {"JUPITER", "VENUS", "MERCURY"} for p in _planets_there
                        ):
                            _benefic_hits += 1
                if _benefic_hits >= 2:
                    _rd_score = 0.75
                elif _benefic_hits == 1:
                    _rd_score = 0.55

            jaimini_data = {
                "chara_alignment":     _c_align,
                "karakamsha_score":    _k_score,
                "arudha_alignment":    _a_align,
                "rashi_drishti_score": _rd_score,
            }
        except Exception:
            jaimini_data = None

        # ── Phase 2B: Baladi Avastha modifier on Shadbala (prediction layer only) ────
        # Core compute_baladi_avasthas() is untouched; modifier applied here so it
        # cascades into dasha alignment, house-lord strength, and promise scoring
        # that compute_confidence() does internally with the ratios.
        _raw_shadbala   = static.get("shadbala_ratios", {})
        _avasthas_data  = static.get("avasthas", {})
        _baladi_map     = (_avasthas_data.get("baladi", {})
                           if isinstance(_avasthas_data, dict) else {})
        _effective_shadbala: Dict[str, float] = {}
        for _p, _ratio in _raw_shadbala.items():
            _b    = _baladi_map.get(_p, {})
            _mult = _b.get("multiplier", 1.0) if isinstance(_b, dict) else 1.0
            # Floor at 0.15 so Mrita never completely zeros out a planet
            _effective_shadbala[_p] = round(_ratio * max(0.15, _mult), 4)

        confidence = compute_confidence(
            dasha_planet=dasha_planet,
            antardasha_planet=antar_planet,
            domain=domain,
            planet_domain_map=static.get("domain_map", {}),
            shadbala_ratios=_effective_shadbala,
            transit_scores=transit_evals_adj,
            domain_planets=domain_planets_list,
            sarva_av=sarva_av,
            relevant_signs=relevant_signs,
            active_yogas=yogas,
            kp_significations=kp_sigs_houses,
            domain_houses=domain_houses,
            dasha_planet_bav=dp_bav,
            functional_analysis=static.get("functional"),
            house_lords={int(k): v for k, v in static.get("house_lords", {}).items()},
            vargas=static.get("vargas"),
            planet_houses=static.get("chart_raw", {}).get("planet_houses"),
            negator_houses=negator_houses,
            gpt_adjustments=gpt_adjustments if gpt_adjustments else None,
            promise_result=promise_result,
            dasha_house=dasha_house,
            antardasha_house=antardasha_house,
            dasha_lord_combust=dasha_lord_combust,
            dasha_lord_retrograde=dasha_lord_retrograde,
            jaimini_data=jaimini_data,
            karaka_bav_data=karaka_bav_data,
        )

        # ── Double Transit Gate (§5.1) ──────────────────────────────────
        # If Jupiter+Saturn are NOT in beneficial houses from natal Moon,
        # cap the confidence at 0.50 (event unlikely to manifest fully).
        _dt_info = dynamic.get("dasha_transit", {}) or {}
        _dbl_tr  = _dt_info.get("double_transit", {}) or {}
        _double_transit_active = bool(_dbl_tr.get("active"))
        if not _double_transit_active and isinstance(confidence, dict):
            _raw = confidence.get("final_score", confidence.get("score", 0.5))
            if isinstance(_raw, (int, float)) and _raw > 0.50:
                confidence["final_score"] = 0.50
                confidence["score"]       = 0.50
                confidence.setdefault("gates_applied", []).append(
                    "double_transit_cap: Jupiter+Saturn not in beneficial houses"
                )

        # ── Multi-Dasha AND Consensus (Research Brief Block 3C) ──────────
        chara_diag     = dynamic.get("chara_dasha", {}) or {}
        chara_enrichment = chara_diag.get("enrichment", {}) or {}
        chara_house    = chara_enrichment.get("house_from_lagna", 0)

        # Determine which domains each system "supports" based on planet positioning
        dasha_planet_map = static.get("domain_map", {}).get(dasha_planet, [])
        yogini_planet_map = static.get("domain_map", {}).get(yogini_lord, [])
        chara_active_sign = chara_diag.get("active", {})
        if isinstance(chara_active_sign, dict):
            chara_active_sign = chara_active_sign.get("mahadasha", "")
        chara_lord_name = str(chara_active_sign)

        vim_supports   = domain.lower() in [d.lower() for d in dasha_planet_map]
        yogini_supports = domain.lower() in [d.lower() for d in yogini_planet_map]
        # Chara supports if dasha sign is in domain-relevant houses
        chara_supports = chara_house in domain_houses

        consensus_result: Dict = {}
        if _GPT_REASONER_AVAILABLE:
            try:
                consensus_result = analyze_multi_dasha_consensus(
                    vim_supports_domain=vim_supports,
                    yogini_supports_domain=yogini_supports,
                    chara_supports_domain=chara_supports,
                    vim_lord=dasha_planet,
                    yogini_lord=yogini_lord,
                    chara_lord=chara_lord_name,
                    domain=domain,
                    chara_house=chara_house,
                    active_yogas=[
                        (y.get("name") if isinstance(y, dict) else getattr(y, "name", ""))
                        for y in yogas
                    ],
                    lagna_sign=static.get("meta", {}).get("lagna_name", ""),
                )
            except Exception:
                consensus_result = {}

        # Apply consensus multiplier to confidence
        if consensus_result:
            c_mult = consensus_result.get("confidence_multiplier", 1.0)
            if consensus_result.get("blocked"):
                # Hard denial: Vim denies → major capacity blocked
                confidence["overall"] = min(confidence["overall"], 0.20)
            elif c_mult != 1.0:
                confidence["overall"] = round(
                    min(1.0, max(0.0, confidence["overall"] * c_mult)), 3
                )

        agreement = multi_system_agreement(
            vimshottari_active=dasha_planet,
            yogini_active=yogini_lord,
            domain=domain,
            planet_domain_map=static.get("domain_map", {}),
        )
        # Apply agreement boost
        boosted = min(1.0, confidence["overall"] + agreement["confidence_boost"])

        # ── Fuzzy inference — non-linear multi-system convergence ──
        try:
            fuzzy_inputs = aggregate_for_fuzzy(confidence["components"])
            fuzzy_result = compute_fuzzy_confidence(**fuzzy_inputs)
            # Blend: 55% linear weighted + 45% fuzzy (fuzzy captures convergence better)
            blended = 0.55 * boosted + 0.45 * fuzzy_result["fuzzy_confidence"]
            confidence["fuzzy"] = fuzzy_result
            confidence["fuzzy_inputs"] = fuzzy_inputs
            confidence["overall_boosted"] = round(min(1.0, blended), 3)
        except Exception:
            confidence["overall_boosted"] = round(boosted, 3)
            confidence["fuzzy"] = {}

        confidence["overall_boosted"] = round(confidence["overall_boosted"], 3)
        confidence["multi_system_agreement"] = agreement

        # ── Phase 2G: Multi-dasha convergence score (Bayesian evidence) ──────
        # Counts how many active dasha systems support the domain.
        # Returns 0.0–1.0 ratio; injected as 1.5 pseudo-obs into Bayesian layer.
        _dasha_conv: "float | None" = None
        try:
            _dasha_signals: list = [vim_supports, yogini_supports, chara_supports]
            # Ashtottari (if eligible): MD lord in domain planets list?
            _ashto_block = dynamic.get("ashtottari", {})
            if isinstance(_ashto_block, dict) and _ashto_block.get("eligible", False):
                _ashto_md = _ashto_block.get("active", {}).get("mahadasha", "")
                _dasha_signals.append(bool(_ashto_md and _ashto_md in domain_planets_list))
            # Narayana dasha: active sign's relative house in domain_houses?
            _nara = static.get("jaimini_extended", {}).get("narayana_dasha", {})
            _nara_active = _nara.get("active", {})
            if isinstance(_nara_active, dict) and _nara_active:
                _nara_sign = _nara_active.get("sign", _nara_active.get("mahadasha_sign", None))
                if _nara_sign is not None:
                    try:
                        _lagna_sign = int(static.get("chart_raw", {}).get(
                            "planet_lons", {}).get("ASC", static.get("meta", {}).get(
                            "lagna_lon", 0.0)) / 30) % 12
                        _nara_house = (int(_nara_sign) - _lagna_sign) % 12 + 1
                        _dasha_signals.append(_nara_house in domain_houses)
                    except Exception:
                        pass
            # ── Phase 3F.1: BCP + Annual Profection + ZR Spirit into convergence ─
            _comp_3f = static.get("computed", {})
            _bcp_h = _comp_3f.get("bcp_active_house")
            if _bcp_h is not None:
                _dasha_signals.append(bool(_bcp_h in domain_houses))
            _prof_3f = _comp_3f.get("annual_profection", {})
            _tl_3f   = _prof_3f.get("time_lord")
            if _tl_3f:
                _dasha_signals.append(bool(_tl_3f in domain_planets_list))
            _zr_spirit_3f = _comp_3f.get("zodiacal_releasing_spirit", {})
            _zr_cur_3f    = _zr_spirit_3f.get("current_period", {}) if isinstance(_zr_spirit_3f, dict) else {}
            if _zr_cur_3f:
                _zr_sign_3f  = _zr_cur_3f.get("sign")
                _lot_sign_3f = _zr_spirit_3f.get("lot_sign")
                if _zr_sign_3f is not None and _lot_sign_3f is not None:
                    _dist_3f = (int(_zr_sign_3f) - int(_lot_sign_3f)) % 12
                    _dasha_signals.append(bool(_dist_3f in {0, 3, 6, 9}))

            _dasha_conv = round(sum(_dasha_signals) / len(_dasha_signals), 3) if _dasha_signals else None
            confidence["dasha_convergence_2g"] = _dasha_conv
        except Exception:
            _dasha_conv = None

        # ── Phase 2H: Varshaphala annual-chart alignment score ───────────────
        # Scores annual Solar-return chart relevance for the domain.
        # Returns 0.0–1.0; injected as 1.0 pseudo-obs into Bayesian layer.
        _varsha_score: "float | None" = None
        try:
            _varsha = static.get("varshaphala", {})
            if _varsha and isinstance(_varsha, dict):
                _vh_score = 0.50  # neutral baseline
                # Muntha house: 1/5/9/10/11 = auspicious; 6/8/12 = inauspicious
                _muntha_house = _varsha.get("muntha", {}).get("house", 0)
                if _muntha_house in {1, 5, 9, 10, 11}:
                    _vh_score += 0.15
                elif _muntha_house in {6, 8, 12}:
                    _vh_score -= 0.15
                # Varsha Pati in domain_planets_list?
                _vp_block = _varsha.get("varsha_pati", {})
                if isinstance(_vp_block, dict):
                    _vp_planet = _vp_block.get("varsha_pati", "")
                    _vp_pvb    = float(_vp_block.get("pvb", 0.0))
                    if _vp_planet in domain_planets_list:
                        _vh_score += 0.12 if _vp_pvb >= 10 else 0.06
                    elif _vp_pvb <= 5:   # Nirbali Varsha Pati → annual weakness
                        _vh_score -= 0.05
                # Tajika yogas involving domain planets
                for _ty in (_varsha.get("tajika_yogas", []) or []):
                    if not isinstance(_ty, dict):
                        continue
                    _ty_quality  = _ty.get("quality", "")
                    _ty_planets  = _ty.get("planets", [])
                    _ty_relevant = any(p in domain_planets_list for p in _ty_planets)
                    if _ty_relevant:
                        if _ty_quality in ("good", "very_good"):        # Itthasala etc.
                            _vh_score += 0.08
                        elif _ty_quality in ("bad", "very_bad"):        # Ishrafa / Rodha
                            _vh_score -= 0.05
                _varsha_score = round(min(1.0, max(0.0, _vh_score)), 3)
                confidence["varshaphala_score_2h"] = _varsha_score
        except Exception:
            _varsha_score = None

        # ── Bayesian posterior — Beta-conjugate update for domain probability ──
        try:
            # Inject overlap-detection keys into components for Bayesian layer
            _bayes_components = dict(confidence["components"])
            _bayes_components["dasha_planet"] = dasha_planet
            # Build list of strong transit planets (net_score ≥ 0.5)
            _strong_tp = []
            if isinstance(transit_evals, dict):
                for _tp, _tv in transit_evals.items():
                    if isinstance(_tv, dict) and _tv.get("net_score", 0) >= 0.5:
                        _strong_tp.append(_tp)
            _bayes_components["strong_transit_planets"] = _strong_tp

            bayes_result = compute_bayesian_confidence(
                _bayes_components, domain=domain,
                dasha_convergence=_dasha_conv,      # Phase 2G: multi-dasha signal
                varshaphala_score=_varsha_score,    # Phase 2H: annual chart quality
            )
            # Triple-blend: 45% linear + 35% fuzzy + 20% Bayesian posterior
            fuzzy_score = confidence.get("fuzzy", {}).get("fuzzy_confidence",
                                                           confidence["overall_boosted"])
            bayes_score = bayes_result["posterior_mean"]
            triple_blend = round(min(1.0,
                0.45 * boosted
                + 0.35 * fuzzy_score
                + 0.20 * bayes_score
            ), 3)
            confidence["bayesian"] = bayes_result
            confidence["overall_boosted"] = triple_blend
        except Exception:
            confidence["bayesian"] = {}

        # ── Vimshopak boost: dasha lord's multi-varga dignity score ──
        try:
            vimshopak_data = static.get("vimshopak", {})
            if isinstance(vimshopak_data, dict) and dasha_planet in vimshopak_data:
                vp = vimshopak_data[dasha_planet]
                vp_pct = vp.get("percentage", 50.0) / 100.0      # 0-1 scale
                # Apply as small modifier: if dasha lord is strong across vargas,
                # boost overall by up to +4%; if weak, penalize by up to -4%
                vm_mod = (vp_pct - 0.5) * 0.08
                confidence["overall_boosted"] = round(
                    min(1.0, max(0.0, confidence["overall_boosted"] + vm_mod)), 3
                )
                confidence["vimshopak_mod"] = round(vm_mod, 4)
                confidence["vimshopak_pct"] = round(vp_pct * 100, 1)
        except Exception:
            pass

        # ── Phase 2J: Special Lagnas as domain cross-validators [±4% cap] ─────────
        # Each domain has 1-3 relevant special lagnas (classical Jyotish sources).
        # A lagna in a kendra/trikona from natal lagna → positive; dusthana → negative.
        # Net modifier capped at ±0.04 (4 pp).
        try:
            _sp_pts_j = static.get("special_points", {})
            _lagna_sign_j = static.get("meta", {}).get("lagna_sign", 0)

            # Domain → relevant special lagna keys and their house-score maps
            _DOMAIN_LAGNA_KEYS = {
                "career":   ["ghati_lagna"],
                "finance":  ["hora_lagna", "indu_lagna", "sri_lagna"],
                "marriage": ["varnada_lagna", "pranapada"],
                "health":   ["varnada_lagna", "pranapada"],
            }
            _lagna_keys = _DOMAIN_LAGNA_KEYS.get(domain.lower(), [])
            _auspicious_houses = {1, 4, 5, 7, 9, 10}
            _dusthana_houses   = {6, 8, 12}

            _j_points = 0.0
            _j_count  = 0
            for _lkey in _lagna_keys:
                _lobj = _sp_pts_j.get(_lkey, {})
                if not isinstance(_lobj, dict):
                    continue
                _lsign = _lobj.get("sign_idx")
                if _lsign is None:
                    continue
                _lhouse = (int(_lsign) - int(_lagna_sign_j)) % 12 + 1
                if _lhouse in _auspicious_houses:
                    _j_points += 1.0
                elif _lhouse in _dusthana_houses:
                    _j_points -= 1.0
                # houses 2/3/11 = neutral (0)
                _j_count += 1

            if _j_count:
                _j_raw_mod = (_j_points / _j_count) * 0.04   # ±0.04 max
                _j_mod = round(min(0.04, max(-0.04, _j_raw_mod)), 4)
                confidence["overall_boosted"] = round(
                    min(1.0, max(0.0, confidence["overall_boosted"] + _j_mod)), 3
                )
                confidence["special_lagna_mod_2j"] = _j_mod
        except Exception:
            pass

        # ── Phase 3F.3: Hellenistic Sect → in-sect domain planet bonus [±5%] ──
        try:
            _sect_3f = static.get("computed", {}).get("hellenistic_sect", {})
            if isinstance(_sect_3f, dict):
                _sb_3f    = _sect_3f.get("sect_benefics", []) or []
                _sb_bonus = min(0.10, sum(0.05 for p in domain_planets_list if p in _sb_3f))
                if _sb_bonus:
                    confidence["overall_boosted"] = round(
                        min(1.0, confidence["overall_boosted"] + _sb_bonus), 3)
                    confidence["sect_bonus_3f"] = round(_sb_bonus, 4)
        except Exception:
            pass

        # ── Phase 3F.4: Lunar health modifier (science hook, health domain only) ─
        if domain.lower() == "health" and _SCIENCE_AVAILABLE:
            try:
                _trans_pos_3f = dynamic.get("transit_positions", {})
                _moon_obj_3f  = _trans_pos_3f.get("MOON", {})
                _sun_obj_3f   = _trans_pos_3f.get("SUN", {})
                _moon_lon_3f  = (float(_moon_obj_3f.get("longitude", 0.0))
                                  if isinstance(_moon_obj_3f, dict) else float(_moon_obj_3f or 0.0))
                _sun_lon_3f   = (float(_sun_obj_3f.get("longitude", 0.0))
                                  if isinstance(_sun_obj_3f, dict) else float(_sun_obj_3f or 0.0))
                # Approximate synodic phase from transit moon/sun positions
                _phase_deg_3f = (_moon_lon_3f - _sun_lon_3f) % 360.0
                # Use lunar phase calculation via direct formula (avoids extra import)
                import math as _math
                _lhm_mod = round(-0.03 * _math.cos(_math.radians(_phase_deg_3f)), 5)
                if _lhm_mod:
                    confidence["overall_boosted"] = round(
                        min(1.0, confidence["overall_boosted"] + _lhm_mod), 3)
                    confidence["lunar_health_mod_3f"] = _lhm_mod
            except Exception:
                pass

        # ── Natal Argala modifier ──
        try:
            planet_houses_raw = static.get("chart_raw", {}).get("planet_houses", {})
            shadbala_ratios   = static.get("shadbala_ratios", {})
            dasha_lord_house  = planet_houses_raw.get(dasha_planet)
            antar_lord_house  = planet_houses_raw.get(antar_planet)
            argala_data = compute_all_argala(
                planet_houses=planet_houses_raw,
                lagna_house=1,
                dasha_lord_house=dasha_lord_house,
                antardasha_lord_house=antar_lord_house,
                shadbala_ratios=shadbala_ratios,
            )
            argala_mod = argala_data.get("combined_confidence_mod", 0.0)
            confidence["overall_boosted"] = round(
                min(1.0, max(0.0, confidence["overall_boosted"] + argala_mod)), 3
            )
            confidence["argala_mod"] = round(argala_mod, 4)
        except Exception:
            argala_data = {}

        # ── Transit-to-natal longitude aspects: weighted orb, applying/separating, [±5%]
        try:
            natal_lons_for_asp = static.get("chart_raw", {}).get("planet_lons", {})
            trans_pos_for_asp  = dynamic.get("transit_positions", {})
            aspect_transit_data = compute_transit_aspects(trans_pos_for_asp, natal_lons_for_asp)
            asp_score = compute_natal_activation_score(aspect_transit_data, domain_planets_list)
            asp_mod   = (asp_score - 0.5) * 0.10    # ±5% max modifier
            confidence["overall_boosted"] = round(
                min(1.0, max(0.0, confidence["overall_boosted"] + asp_mod)), 3
            )
            confidence["aspect_transit_score"] = round(asp_score, 3)
            confidence["aspect_transit_mod"]   = round(asp_mod, 4)
        except Exception:
            aspect_transit_data = {}
            asp_score = 0.5

        # ── Secondary progressions + Solar arc activation boost [±8% cap]
        try:
            prog_data  = dynamic.get("progressions", {})
            prog_boost = prog_data.get("combined_boost", 0.0) if isinstance(prog_data, dict) else 0.0
            if prog_boost:
                confidence["overall_boosted"] = round(
                    min(1.0, max(0.0, confidence["overall_boosted"] + prog_boost)), 3
                )
            confidence["progression_boost"] = prog_boost
        except Exception:
            prog_boost = 0.0

        # ── Domain-relevant transit summary
        domain_transits = {p: transit_evals[p] for p in domain_planets_list
                           if p in transit_evals}
        favorable_transits = [p for p, t in domain_transits.items()
                               if isinstance(t, dict) and t.get("is_favorable_gochar")]
        vedha_blocked = [p for p, t in domain_transits.items()
                         if isinstance(t, dict) and t.get("vedha_blocked")]

        # ── Active domain yogas
        domain_yoga_names = []
        for y in yogas:
            if isinstance(y, dict):
                domain_yoga_names.append(y.get("name", str(y)))
            else:
                domain_yoga_names.append(getattr(y, "name", str(y)))

        # ── Prediction text
        prediction_text = _generate_prediction_text(
            domain, confidence["level"], boosted,
            dasha_planet, antar_planet, yogini_lord,
            favorable_transits, vedha_blocked, domain_yoga_names,
        )

        # ── Dispositor chain for dasha lords
        try:
            planet_signs  = static.get("chart_raw", {}).get("planet_signs", {})
            planet_houses_raw = static.get("chart_raw", {}).get("planet_houses", {})
            shadbala_ratios   = static.get("shadbala_ratios", {})
            dispositor_analysis = analyze_dasha_lord_dispositor(
                dasha_planet, antar_planet,
                planet_signs, planet_houses_raw, shadbala_ratios,
            )
        except Exception as e:
            dispositor_analysis = {"error": str(e)}

        # ── Calibrate confidence score ─────────────────────────────────────
        raw_conf = confidence.get("overall_boosted", confidence.get("overall", 0.5))
        try:
            calibrated = calibrate_confidence(raw_conf, domain)
        except Exception:
            calibrated = {"raw": raw_conf, "calibrated": raw_conf, "reliability_band": "Unknown"}

        return {
            "domain": domain,
            "date": on_date.isoformat(),
            "dasha": {
                "maha_dasha": dasha_planet,
                "antar_dasha": antar_planet,
                "yogini_lord": yogini_lord,
            },
            "confidence": confidence,
            "calibrated_confidence": calibrated,
            "transits": {
                "domain_relevant": domain_transits,
                "favorable": favorable_transits,
                "vedha_blocked": vedha_blocked,
            },
            "active_yogas": domain_yoga_names,
            "sade_sati": dynamic.get("sade_sati", {}),
            "ruling_planets": dynamic.get("ruling_planets", {}),
            "karakas": static.get("karakas", {}),
            "prediction": prediction_text,
            "dispositor": dispositor_analysis,
            "panchanga":       dynamic.get("panchanga", {}),
            "dasha_transit":   dynamic.get("dasha_transit", {}),
            "ingress_calendar":dynamic.get("ingress_calendar", []),
            "argala":          argala_data,
            "transit_aspects": aspect_transit_data,
            "progressions":    dynamic.get("progressions", {}),
            "solar_terms":     dynamic.get("solar_terms", []),
            "lunations":       dynamic.get("lunations", {}),
            "timing_windows":  dynamic.get("timing_windows", {}).get(domain, {}),
            "dispositor_graph":static.get("dispositor_graph", {}),
            "varga_report":    static.get("varga_report", {}),
            "remedies":        static.get("remedies", []),
            # ── New promise / diagnostic / consensus layers ──
            "promise":         promise_result or {},
            "dasha_diagnostic":dasha_diag,
            "multi_dasha_consensus": consensus_result,
            "yoga_compounding":static.get("yoga_compounding", {}),
            "chara_dasha":     dynamic.get("chara_dasha", {}),
            "retrograde_dasha":dynamic.get("retrograde_dasha", {}),
            # ── Deep Dive: Badhaka, Bhavabala domain, Career/Marriage synthesis ──
            "badhaka": _compute_predict_badhaka(
                static, domain, dasha_planet, antar_planet
            ),
            "bhavabala_domain_modifier": static.get(
                "bhavabala_domain_modifiers", {}
            ).get(domain.lower(), {}),
            "shadvarga_vimshopak": static.get("shadvarga_vimshopak", {}),
            "career_checklist": _compute_career_checklist_safe(static, dynamic, domain),
            # ── Yoga system enhancements ──
            "graha_yuddha":    static.get("graha_yuddha", []),
            "dhana_stacking":  static.get("dhana_stacking", {}),
            # ── Nakshatra Analysis (File 2) ──
            "nakshatra_analysis": static.get("nakshatra_analysis", {}),
            "varshaphala": static.get("varshaphala", {}),
            # ── Jaimini Extended (File 4) ──
            "jaimini_extended": static.get("jaimini_extended", {}),
            # ── File 5: Prashna, Kalachakra, Medical, Conditional Dashas ──
            "file5_analysis":   static.get("file5_analysis", {}),
        }

    def full_report(self,
                    chart: VedicChart,
                    on_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate predictions for ALL domains in one call.
        """
        if on_date is None:
            on_date = datetime.now()
        static  = self.analyze_static(chart)
        dynamic = self.analyze_dynamic(chart, static, on_date)

        reports = {}
        for domain in DOMAIN_HOUSES:
            reports[domain] = self.predict(chart, domain, on_date, static)

        # Sort domains by confidence
        sorted_domains = sorted(
            reports.items(),
            key=lambda kv: kv[1]["confidence"]["overall_boosted"],
            reverse=True,
        )

        return {
            "date": on_date.isoformat(),
            "static_analysis": static,
            "dynamic_analysis": dynamic,
            "domain_reports": dict(sorted_domains),
            "top_domains": [d for d, _ in sorted_domains[:3]],
        }


# ─── Safe wrappers for new modules ───────────────────────────────

def _compute_dispositor_graph_safe(
        planet_signs: dict,
        shadbala_ratios: dict,
) -> dict:
    try:
        return compute_dispositor_graph(planet_signs, shadbala_ratios)
    except Exception as e:
        return {"error": str(e)}


def _compute_varga_report_safe(
        planet_lons: dict,
        vargas: dict,                 # {planet: {d_num: sign_idx}}
        lagna_lon: float,
) -> dict:
    try:
        d9_signs  = {p: vargas[p][9]  for p in vargas if 9  in vargas[p]}
        d10_signs = {p: vargas[p][10] for p in vargas if 10 in vargas[p]}
        d7_signs  = {p: vargas[p][7]  for p in vargas if 7  in vargas[p]}
        d4_signs  = {p: vargas[p][4]  for p in vargas if 4  in vargas[p]}
        d9_lagna  = D9(lagna_lon)
        d10_lagna = D10(lagna_lon)
        d7_lagna  = D7(lagna_lon)
        d4_lagna  = D4(lagna_lon)
        return compute_varga_report(
            planet_d1_lons=planet_lons,
            planet_d9_signs=d9_signs,
            planet_d10_signs=d10_signs,
            planet_d7_signs=d7_signs,
            planet_d4_signs=d4_signs,
            d9_lagna=d9_lagna,
            d10_lagna=d10_lagna,
            d7_lagna=d7_lagna,
            d4_lagna=d4_lagna,
        )
    except Exception as e:
        return {"error": str(e)}


def _compute_remedies_safe(
        planet_signs: dict,
        planet_houses: dict,
        shadbala_ratios: dict,
        retrogrades: dict,
        wars: list,
) -> list:
    try:
        war_losers = {w["loser"] for w in wars if isinstance(w, dict) and "loser" in w}
        planet_states = {}
        for planet, sign in planet_signs.items():
            planet_states[planet] = {
                "sign_idx":        sign,
                "house":           planet_houses.get(planet, 1),
                "shadbala_ratio":  shadbala_ratios.get(planet, 1.0),
                "retrograde":      retrogrades.get(planet, False),
                "war_defeated":    planet in war_losers,
                "malefic_aspects": 0,   # can be augmented later
                "combust":         False,
            }
        return get_remedies(planet_states, threshold=0.12)
    except Exception as e:
        return [{"error": str(e)}]


def _compute_lunations_safe(
        on_date,
        static: dict,
        vim_periods: list,
        analysis_date,
) -> dict:
    try:
        planet_lons = static.get("chart_raw", {}).get("planet_lons", {})
        rahu_lon = planet_lons.get("RAHU", 45.0)
        # Include Lagna in natal_lons for proximity checks
        lagna_lon = static.get("meta", {}).get("lagna_lon", 0.0)
        natal_for_lunations = dict(planet_lons)
        natal_for_lunations["LAGNA"] = lagna_lon
        lunations = compute_upcoming_lunations(
            on_date=on_date,
            natal_lons=natal_for_lunations,
            rahu_lon=rahu_lon,
            months_ahead=12,
        )
        return {
            "all": lunations,
            "eclipses": get_eclipse_alerts(lunations),
            "high_significance": get_high_significance_lunations(lunations),
        }
    except Exception as e:
        return {"error": str(e)}


def _compute_timing_windows_safe(
        on_date,
        transit_pos: dict,
        static: dict,
) -> dict:
    try:
        natal_moon_sign = static.get("meta", {}).get("moon_sign", 0)
        av_data = static.get("ashtakvarga", {})
        sarva_av_raw = av_data.get("sarva", None) if isinstance(av_data, dict) else None
        sarva_av = list(sarva_av_raw) if sarva_av_raw else None

        results = {}
        for domain in ["career", "finance", "health", "relationships"]:
            best  = find_best_windows(
                base_transit_lons=transit_pos,
                reference_date=on_date,
                natal_moon_sign=natal_moon_sign,
                domain=domain,
                months_ahead=12,
                sarva_av=sarva_av,
                top_k=3,
            )
            worst = find_worst_windows(
                base_transit_lons=transit_pos,
                reference_date=on_date,
                natal_moon_sign=natal_moon_sign,
                domain=domain,
                months_ahead=12,
                sarva_av=sarva_av,
                top_k=2,
            )
            results[domain] = {"best": best, "worst": worst}
        return results
    except Exception as e:
        return {"error": str(e)}


# ─── Prediction text generator ───────────────────────────────────

def _generate_prediction_text(
        domain: str, level: str, score: float,
        maha: str, antar: str, yogini: str,
        favorable: List[str], blocked: List[str], yogas: List[str]) -> str:

    lines = [
        f"DOMAIN: {domain.upper()} | Confidence: {level} ({score:.1%})",
        f"Active dasha: {maha} / {antar}  (Yogini: {yogini})",
    ]

    if favorable:
        lines.append(f"Supportive transits: {', '.join(favorable)}")
    if blocked:
        lines.append(f"Vedha (transit obstruction) by: {', '.join(blocked)} — results may be delayed")
    if yogas:
        lines.append(f"Active yogas: {', '.join(yogas[:5])}")

    domain_advice = {
        "career":   "Good period for professional assertion, visibility, and new responsibilities.",
        "finance":  "Track income sources carefully; auspicious for investments when Jupiter supports.",
        "marriage": "Relationship harmony depends on Venus/Jupiter dasha strength.",
        "health":   "Attend to vitality; Saturn transit periods require rest and discipline.",
        "spiritual":"Ideal for inner work, retreats, study of philosophy and meditation.",
        "travel":   "Foreign travel or relocation indicated; confirm timing via muhurtha.",
        "children": "Jupiter's significations are paramount; check 5th house strength.",
        "property": "4th house activity; Moon-Mars combination favourable for property.",
    }
    lines.append(domain_advice.get(domain.lower(), "General period of activity in this area."))
    return "\n".join(lines)


def _compute_bb_transit_safe(transit_pos: dict, static: dict) -> dict:
    """Check if slow-movers transit over Bhrigu Bindu — karmic activation."""
    try:
        from vedic_engine.analysis.special_points import check_bhrigu_bindu_transit
        sp = static.get("special_points", {})
        bb_info = sp.get("bhrigu_bindu", {}) if isinstance(sp, dict) else {}
        bb_deg = bb_info.get("longitude") if isinstance(bb_info, dict) else None
        if bb_deg is None:
            return {}
        return check_bhrigu_bindu_transit(
            bb_degree=float(bb_deg),
            transit_planet_lons=transit_pos,
        )
    except Exception:
        return {}


def _compute_dasha_quality_safe(vim_active, static: dict, on_date) -> dict:
    """Compute Ishta/Kashta dasha quality score for the active Mahadasha lord."""
    try:
        from vedic_engine.timing.dasha_quality import dasha_quality_score
        _md = ""
        if isinstance(vim_active, str):
            _md = vim_active
        elif isinstance(vim_active, dict):
            _md = vim_active.get("mahadasha", vim_active.get("planet", ""))
        elif isinstance(vim_active, list) and vim_active:
            _md = vim_active[0].get("planet", "")
        if not _md:
            return {}
        # Compute native age
        _bdate_str = static.get("meta", {}).get("birth_date", "")
        _age = 30.0  # safe default
        if _bdate_str and on_date:
            from datetime import datetime as _dt
            try:
                _bdate = _dt.strptime(str(_bdate_str), "%Y-%m-%d")
                _age = (on_date - _bdate).days / 365.25
            except Exception:
                pass
        _sb = static.get("shadbala_ratios", {}).get(_md, 1.0)
        _func = static.get("functional", {}) or {}
        _yk = _func.get("yogakarakas", [])
        _fb = _func.get("functional_benefics", [])
        _retro = static.get("chart_raw", {}).get("retrogrades", {}).get(_md, False)
        return dasha_quality_score(
            planet=_md,
            native_age=_age,
            shadbala_ratio=_sb,
            is_yogakaraka=(_md in _yk),
            is_functional_benefic=(_md in _fb),
            is_retrograde=bool(_retro),
        )
    except Exception:
        return {}


def _compute_retrograde_dasha_safe(
        vim_active,
        transit_pos: dict,
        static: dict,
) -> dict:
    """
    Compute retrograde Dasha lord mechanics for the active Mahadasha lord.
    Called from analyze_dynamic() — wrapped so any failure returns empty dict.
    """
    if not _RETRO_DASHA_AVAILABLE:
        return {}
    try:
        _planet_lons = static.get("chart_raw", {}).get("planet_lons", {})
        _retros      = static.get("chart_raw", {}).get("retrogrades", {})
        _ph          = static.get("chart_raw", {}).get("planet_houses", {})
        _ls          = static.get("meta", {}).get("lagna_sign", 0)

        _md_lord = "SATURN"
        if isinstance(vim_active, dict):
            _md_lord = vim_active.get("mahadasha", vim_active.get("planet", "SATURN"))
        elif isinstance(vim_active, list) and vim_active:
            _md_lord = vim_active[0].get("planet", "SATURN")

        if not _retros.get(_md_lord, False):
            return {"is_retrograde": False, "planet": _md_lord}

        _md_lon   = _planet_lons.get(_md_lord, 0.0)
        _md_house = _ph.get(_md_lord, 0)

        # Detect station: if transit speed is near zero (sign change pending)
        _transit_lon = transit_pos.get(_md_lord, _md_lon)
        _was_retro   = _retros.get(_md_lord, False)
        # Use speed proxy: if transit lon differs direction from natal, likely direct now
        _is_retro_now = _was_retro   # best approximation without live speed data

        return analyze_retrograde_dasha_lord(
            dasha_planet=_md_lord,
            planet_longitude=_md_lon,
            planet_house=_md_house,
            lagna_sign=_ls,
            transit_was_retrograde=_was_retro,
            transit_is_retrograde=_is_retro_now,
        )
    except Exception as _e:
        return {"error": str(_e)}


def _compute_predict_badhaka(
        static: dict,
        domain: str,
        md_lord: str,
        ad_lord: str,
) -> dict:
    """Compute Badhaka friction for the predict() call's domain and active Dasha."""
    if not _BADHAKA_AVAILABLE:
        return {}
    try:
        _ls = static.get("meta", {}).get("lagna_sign", 0)
        _bh_info = get_badhaka_house(_ls)
        _badhakesh = _bh_info.get("badhakesh", "")
        _ph = static.get("chart_raw", {}).get("planet_houses", {})
        _sr = static.get("shadbala_ratios", {})
        _badhakesh_house = _ph.get(_badhakesh, 0)
        _is_malefic = _badhakesh.upper() in {"SUN", "MARS", "SATURN", "RAHU", "KETU"}
        _shad_ratio = _sr.get(_badhakesh, 1.0)

        friction = compute_badhaka_friction(
            lagna_sign=_ls,
            badhakesh_house=_badhakesh_house,
            badhakesh_is_functional_benefic=not _is_malefic,
            badhakesh_shadbala_ratio=_shad_ratio,
            current_dasha_lord=md_lord,
            badhakesh=_badhakesh,
            event_domain=domain,
        )
        friction["badhaka_info"] = _bh_info
        return friction
    except Exception as _e:
        return {"error": str(_e)}


def _compute_career_checklist_safe(
        static: dict,
        dynamic: dict,
        domain: str,
) -> dict:
    """Run the 5-step career checklist — only when domain == 'career'."""
    if not _CAREER_CHECKLIST_AVAILABLE or domain.lower() != "career":
        return {}
    try:
        _ls = static.get("meta", {}).get("lagna_sign", 0)
        _ps = static.get("chart_raw", {}).get("planet_signs", {})
        _ph = static.get("chart_raw", {}).get("planet_houses", {})
        _ms = static.get("meta", {}).get("moon_sign", 0)
        _sun_s = _ps.get("SUN", 0)

        # Jaimini karakas
        _kd = static.get("karakas_dict", {})
        _ak_planet  = _kd.get("AK", "SUN")
        _amk_planet = _kd.get("AmK", "SATURN")
        _ak_sign    = _ps.get(_ak_planet, 0)
        _amk_sign   = _ps.get(_amk_planet, 0)

        # D10 planet houses (from vargas dict)
        _vargas = static.get("vargas", {})
        _d10_planet_houses: dict = {}
        _hl = {int(k): v for k, v in static.get("house_lords", {}).items()}
        _d10_lagna_sign = _ls  # fallback if D10 lagna not computed
        for _p, _vg in _vargas.items():
            if isinstance(_vg, dict) and 10 in _vg:
                _d10_sign = _vg[10]
                _d10_planet_houses[_p] = ((_d10_sign - _d10_lagna_sign) % 12) + 1

        # D3 10th house occupants
        _d3_tenth_lord_sign = (_ls + 9) % 12   # 10th from D3 lagna (approx = D1 lagna)
        _d3_tenth_planets = [
            _p for _p, _vg in _vargas.items()
            if isinstance(_vg, dict) and _vg.get(3) == _d3_tenth_lord_sign
        ]
        _d3_tenth_lord = {0: "MARS", 1: "VENUS", 2: "MERCURY", 3: "MOON",
                          4: "SUN", 5: "MERCURY", 6: "VENUS", 7: "MARS",
                          8: "JUPITER", 9: "SATURN", 10: "SATURN",
                          11: "JUPITER"}.get(_d3_tenth_lord_sign, "SATURN")
        _d3_tenth_lord_house = _ph.get(_d3_tenth_lord, 0)

        # Active dasha lords
        _vim = dynamic.get("vimshottari", {}).get("active", {})
        _md_lord = "SATURN"
        _ad_lord = "SATURN"
        if isinstance(_vim, dict):
            _md_lord = _vim.get("mahadasha", _vim.get("planet", "SATURN"))
            _ad_lord = _vim.get("antardasha", _md_lord)
        elif isinstance(_vim, list) and _vim:
            _md_lord = _vim[0].get("planet", "SATURN")
            _ad_lord = _vim[1].get("planet", _md_lord) if len(_vim) > 1 else _md_lord

        # 10th house occupants in D1
        _tenth_sign = (_ls + 9) % 12
        _tenth_occupants = [_p for _p, _s in _ps.items() if _s == _tenth_sign]

        # Saturn and Jupiter transit houses from lagna
        _tp = dynamic.get("transit_positions", {})
        from vedic_engine.core.coordinates import sign_of as _so
        _sat_t_sign = _so(_tp.get("SATURN", 0.0))
        _jup_t_sign = _so(_tp.get("JUPITER", 0.0))
        _sat_t_house = ((_sat_t_sign - _ls) % 12) + 1
        _jup_t_house = ((_jup_t_sign - _ls) % 12) + 1

        return compute_career_checklist(
            lagna_sign=_ls,
            moon_sign=_ms,
            sun_sign=_sun_s,
            planet_signs=_ps,
            planet_houses=_ph,
            ak_sign=_ak_sign,
            amk_sign=_amk_sign,
            amk_planet=_amk_planet,
            d10_planet_houses=_d10_planet_houses,
            d3_tenth_house_planets=_d3_tenth_planets,
            d3_tenth_lord=_d3_tenth_lord,
            d3_tenth_lord_house=_d3_tenth_lord_house,
            md_lord=_md_lord,
            ad_lord=_ad_lord,
            tenth_house_occupants=_tenth_occupants,
            saturn_transit_house=_sat_t_house,
            jupiter_transit_house=_jup_t_house,
        )
    except Exception as _e:
        return {"error": str(_e)}

