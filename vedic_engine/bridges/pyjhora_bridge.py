"""
PyJHora Bridge — wraps PyJHora library as an optional compute backend.
If PyJHora is not installed, all functions return None gracefully.

Proven API patterns taken from pyjhora_nehru_test_v2.py (129/130 OK).
Key rules:
  - dob must be drik.Date(y, m, d) — a namedtuple, NOT a plain tuple
  - tob is a plain tuple (h, m, s)
  - Ashtakavarga / arudhas / marakas / kala_sarpa need house_planet_list
  - Divisional chart factor 1 = Rasi, 9 = Navamsa, etc.
  - Each dasha module has its own function name + arg pattern (mapped below)
"""
from __future__ import annotations

import importlib
import inspect
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────
# Conditional import — everything fails gracefully if PyJHora is absent
# ──────────────────────────────────────────────────────────────────────
try:
    from jhora.panchanga import drik
    from jhora import utils as jhora_utils
    from jhora.horoscope.chart import (
        charts, yoga, sphuta, strength,
        ashtakavarga, arudhas, house, dosha,
        raja_yoga,
    )
    from jhora.horoscope.main import Horoscope
    from jhora.horoscope.match import compatibility
    PYJHORA_AVAILABLE = True
except ImportError:
    PYJHORA_AVAILABLE = False


# ──────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────

def _safe_call(func, *args, **kwargs):
    """Call a PyJHora function; return None on any error (never crash)."""
    if not PYJHORA_AVAILABLE:
        return None
    try:
        result = func(*args, **kwargs)
        return result
    except Exception as exc:
        logger.debug("PyJHora _safe_call(%s) failed: %s", getattr(func, '__name__', func), exc)
        return None


def _make_place(lat: float, lon: float, tz: float):
    """Create a PyJHora Place object."""
    if not PYJHORA_AVAILABLE:
        return None
    return drik.Place('', lat, lon, tz)


def _make_jd(year: int, month: int, day: int,
             hour: int, minute: int, second: int):
    """Create Julian Day + dob + tob from birth data.

    Returns (jd, dob, tob) or None on failure.
    dob is drik.Date (namedtuple with .year, .month, .day).
    """
    if not PYJHORA_AVAILABLE:
        return None
    try:
        dob = drik.Date(year, month, day)
        tob = (hour, minute, second)
        jd = jhora_utils.julian_day_number(dob, tob)
        return jd, dob, tob
    except Exception as exc:
        logger.debug("_make_jd failed: %s", exc)
        return None


def _get_chart_data(jd, place):
    """Get rasi chart (planet_positions) + house_planet_list.

    Returns (planet_positions, house_planet_list) or (None, None).
    """
    try:
        pp = charts.rasi_chart(jd, place)
        h_to_p = jhora_utils.get_house_planet_list_from_planet_positions(pp)
        return pp, h_to_p
    except Exception as exc:
        logger.debug("_get_chart_data failed: %s", exc)
        return None, None


# ──────────────────────────────────────────────────────────────────────
# Section 1: ALL Graha Dashas (22 systems — exact API from test script)
# ──────────────────────────────────────────────────────────────────────

# Maps module_name → (function_name, arg_type)
#   arg_type 'dob' → fn(dob, tob, place)   where dob=drik.Date
#   arg_type 'jd'  → fn(jd, place)
_GRAHA_DASHA_MAP: Dict[str, Tuple[str, str]] = {
    # ── vimsottari & ashtottari (the two "standard" ones) ──
    'vimsottari':       ('get_vimsottari_dhasa_bhukthi', 'jd'),
    'ashtottari':       ('get_ashtottari_dhasa_bhukthi', 'jd'),
    # ── remaining 20 graha dashas proven in test v2 ──
    'buddhi_gathi':                 ('get_dhasa_bhukthi', 'dob'),
    'kaala':                        ('get_dhasa_antardhasa', 'dob'),
    'karaka':                       ('get_dhasa_antardhasa', 'dob'),
    'naisargika':                   ('get_dhasa_bhukthi', 'dob'),
    'shastihayani':                 ('get_dhasa_bhukthi', 'dob'),
    'yoga_vimsottari':              ('get_dhasa_bhukthi', 'jd'),
    'tithi_ashtottari':             ('get_ashtottari_dhasa_bhukthi', 'jd'),
    'tithi_yogini':                 ('get_dhasa_bhukthi', 'dob'),
    'saptharishi_nakshathra':       ('get_dhasa_bhukthi', 'dob'),
    'yogini':                       ('get_dhasa_bhukthi', 'dob'),
    'shodasottari':                 ('get_dhasa_bhukthi', 'dob'),
    'dwadasottari':                 ('get_dhasa_bhukthi', 'dob'),
    'dwisatpathi':                  ('get_dhasa_bhukthi', 'dob'),
    'panchottari':                  ('get_dhasa_bhukthi', 'dob'),
    'sataatbika':                   ('get_dhasa_bhukthi', 'dob'),
    'chathuraaseethi_sama':         ('get_dhasa_bhukthi', 'dob'),
    'shattrimsa_sama':              ('get_dhasa_bhukthi', 'dob'),
    'tara':                         ('get_dhasa_bhukthi', 'dob'),
    'karana_chathuraaseethi_sama':  ('get_dhasa_bhukthi', 'dob'),
    'aayu':                         ('get_dhasa_antardhasa', 'jd'),
}


def get_all_graha_dashas(jd, place, dob, tob) -> Dict[str, Any]:
    """Compute ALL 22 graha dasha systems.

    Returns dict mapping dasha_name → result (list of period tuples).
    Failed dashas are silently omitted.
    """
    if not PYJHORA_AVAILABLE:
        return {}
    results: Dict[str, Any] = {}
    for dasha_name, (fn_name, arg_type) in _GRAHA_DASHA_MAP.items():
        mod_path = f'jhora.horoscope.dhasa.graha.{dasha_name}'
        try:
            mod = importlib.import_module(mod_path)
            fn = getattr(mod, fn_name)
            if arg_type == 'dob':
                result = fn(dob, tob, place)
            else:
                result = fn(jd, place)
            if result is not None:
                results[dasha_name] = result
        except Exception as exc:
            logger.debug("Graha dasha %s failed: %s", dasha_name, exc)
    return results


# ──────────────────────────────────────────────────────────────────────
# Section 2: ALL Raasi Dashas (22 systems — exact API from test script)
# ──────────────────────────────────────────────────────────────────────

_RASI_DASHA_MAP: Dict[str, Tuple[str, str]] = {
    # Standard get_dhasa_antardhasa(dob, tob, place) pattern:
    'chakra':           ('get_dhasa_antardhasa', 'dob'),
    'sthira':           ('get_dhasa_antardhasa', 'dob'),
    'varnada':          ('get_dhasa_antardhasa', 'dob'),
    'yogardha':         ('get_dhasa_antardhasa', 'dob'),
    'paryaaya':         ('get_dhasa_antardhasa', 'dob'),
    'sandhya':          ('get_dhasa_antardhasa', 'dob'),
    'tara_lagna':       ('get_dhasa_antardhasa', 'dob'),
    'lagnamsaka':       ('get_dhasa_antardhasa', 'dob'),
    'chara':            ('get_dhasa_antardhasa', 'dob'),
    'brahma':           ('get_dhasa_antardhasa', 'dob'),
    'mandooka':         ('get_dhasa_antardhasa', 'dob'),
    'padhanadhamsa':    ('get_dhasa_antardhasa', 'dob'),
    'navamsa':          ('get_dhasa_antardhasa', 'dob'),
    'trikona':          ('get_dhasa_antardhasa', 'dob'),
    # Custom function names:
    'narayana':         ('narayana_dhasa_for_rasi_chart', 'dob'),
    'kendradhi_rasi':   ('kendradhi_rasi_dhasa', 'dob'),
    'shoola':           ('shoola_dhasa_bhukthi', 'dob'),
    'sudasa':           ('sudasa_dhasa_bhukthi', 'dob'),
    'nirayana':         ('nirayana_shoola_dhasa_bhukthi', 'dob'),
    'moola':            ('moola_dhasa', 'dob'),
    'kalachakra':       ('get_dhasa_bhukthi', 'dob'),
    'drig':             ('drig_dhasa_bhukthi', 'dob'),
}


def get_all_rasi_dashas(jd, place, dob, tob) -> Dict[str, Any]:
    """Compute ALL 22 rasi dasha systems.

    Returns dict mapping dasha_name → result.
    Failed dashas are silently omitted.
    """
    if not PYJHORA_AVAILABLE:
        return {}
    results: Dict[str, Any] = {}
    for dasha_name, (fn_name, arg_type) in _RASI_DASHA_MAP.items():
        mod_path = f'jhora.horoscope.dhasa.raasi.{dasha_name}'
        try:
            mod = importlib.import_module(mod_path)
            fn = getattr(mod, fn_name)
            if arg_type == 'dob':
                result = fn(dob, tob, place)
            else:
                result = fn(jd, place)
            if result is not None:
                results[dasha_name] = result
        except Exception as exc:
            logger.debug("Rasi dasha %s failed: %s", dasha_name, exc)
    return results


# ──────────────────────────────────────────────────────────────────────
# Section 2b: Annual Dashas + Sudarshana Chakra
# ──────────────────────────────────────────────────────────────────────

def get_annual_dashas(jd, place, dob_tuple) -> Dict[str, Any]:
    """Compute annual/special dasha systems.

    dob_tuple: plain (year, month, day) tuple for Sudarshana.
    """
    if not PYJHORA_AVAILABLE:
        return {}
    results: Dict[str, Any] = {}

    # Mudda (Varsha Vimsottari)
    try:
        from jhora.horoscope.dhasa.annual import mudda
        r = mudda.varsha_vimsottari_dhasa_bhukthi(jd, place, 1)
        if r is not None:
            results['mudda_varsha_vimsottari'] = r
    except Exception as exc:
        logger.debug("mudda dasha failed: %s", exc)

    # Patyayini
    try:
        from jhora.horoscope.dhasa.annual import patyayini
        r = patyayini.patyayini_dhasa(jd, place)
        if r is not None:
            results['patyayini'] = r
    except Exception as exc:
        logger.debug("patyayini dasha failed: %s", exc)

    # Sudarshana Chakra
    try:
        from jhora.horoscope.dhasa import sudharsana_chakra
        r = sudharsana_chakra.sudharsana_chakra_dhasa_for_divisional_chart(
            jd, place, dob_tuple
        )
        if r is not None:
            results['sudarshana_chakra'] = r
    except Exception as exc:
        logger.debug("sudarshana chakra dasha failed: %s", exc)

    return results


# ──────────────────────────────────────────────────────────────────────
# Section 3: ALL Yogas (300+ via _from_jd_place functions)
# ──────────────────────────────────────────────────────────────────────

def get_all_yogas(jd, place) -> Dict[str, Any]:
    """Detect ALL yogas from PyJHora's yoga module (~300 functions).

    Uses the *_from_jd_place variant of each yoga function (proven pattern).
    Also includes raja_yoga details.
    Returns dict mapping yoga_name → result.
    """
    if not PYJHORA_AVAILABLE:
        return {}
    results: Dict[str, Any] = {}

    # Discover all *_from_jd_place functions (proven to work with (jd, place))
    jd_place_funcs = [
        f for f in dir(yoga)
        if f.endswith('_from_jd_place') and callable(getattr(yoga, f, None))
    ]

    for fname in jd_place_funcs:
        # Derive a clean yoga name: "gaja_kesari_yoga_from_jd_place" → "gaja_kesari_yoga"
        clean_name = fname.replace('_from_jd_place', '')
        try:
            result = getattr(yoga, fname)(jd, place)
            if result is not None:
                results[clean_name] = result
        except Exception as exc:
            logger.debug("Yoga %s failed: %s", fname, exc)

    # Raja Yoga details (separate module)
    try:
        raja = raja_yoga.get_raja_yoga_details(jd, place)
        if raja is not None:
            results['raja_yoga_details'] = raja
    except Exception as exc:
        logger.debug("raja_yoga failed: %s", exc)

    return results


# ──────────────────────────────────────────────────────────────────────
# Section 4: ALL Sphutas (need drik.Date dob)
# ──────────────────────────────────────────────────────────────────────

_SPHUTA_NAMES = [
    'tri_sphuta', 'chatur_sphuta', 'pancha_sphuta',
    'prana_sphuta', 'deha_sphuta', 'mrityu_sphuta',
    'sookshma_tri_sphuta', 'beeja_sphuta', 'kshetra_sphuta',
    'tithi_sphuta', 'yoga_sphuta', 'yogi_sphuta',
    'avayogi_sphuta', 'rahu_tithi_sphuta',
]


def get_all_sphutas(dob, tob, place) -> Dict[str, Any]:
    """Get all sphuta calculations.

    dob MUST be drik.Date(y, m, d), NOT a plain tuple.
    """
    if not PYJHORA_AVAILABLE:
        return {}
    results: Dict[str, Any] = {}
    for name in _SPHUTA_NAMES:
        fn = getattr(sphuta, name, None)
        if fn is not None:
            result = _safe_call(fn, dob, tob, place)
            if result is not None:
                results[name] = result
    return results


# ──────────────────────────────────────────────────────────────────────
# Section 5: Strengths (Shadbala, Bhava Bala, Harsha Bala, Vargeeya)
# ──────────────────────────────────────────────────────────────────────

def get_strengths(jd, place, dob, tob) -> Dict[str, Any]:
    """Shadbala, Bhava/Pancha/Dwadhasa Vargeeya Bala, Harsha Bala."""
    if not PYJHORA_AVAILABLE:
        return {}
    return {
        'shad_bala':             _safe_call(strength.shad_bala, jd, place),
        'bhava_bala':            _safe_call(strength.bhava_bala, jd, place),
        'pancha_vargeeya_bala':  _safe_call(strength.pancha_vargeeya_bala, jd, place),
        'dwadhasa_vargeeya_bala': _safe_call(strength.dwadhasa_vargeeya_bala, jd, place),
        'harsha_bala':           _safe_call(strength.harsha_bala, dob, tob, place),
    }


# ──────────────────────────────────────────────────────────────────────
# Section 6: Ashtakavarga
# ──────────────────────────────────────────────────────────────────────

def get_ashtakavarga(h_to_p_list) -> Dict[str, Any]:
    """Ashtakavarga (BAV + SAV + Prastara) from house_planet_list.

    h_to_p_list: 12-element list from
        jhora_utils.get_house_planet_list_from_planet_positions(rasi_chart)
    """
    if not PYJHORA_AVAILABLE or h_to_p_list is None:
        return {}
    av = _safe_call(ashtakavarga.get_ashtaka_varga, h_to_p_list)
    if av is None:
        return {}
    result = {'bav_sav_prastara': av}
    # Sodhaya pindas (has a library bug, but try anyway)
    sp = _safe_call(ashtakavarga.sodhaya_pindas, av, h_to_p_list)
    if sp is not None:
        result['sodhaya_pindas'] = sp
    return result


# ──────────────────────────────────────────────────────────────────────
# Section 7: Doshas
# ──────────────────────────────────────────────────────────────────────

def get_doshas(jd, place, pp, h_to_p_list) -> Dict[str, Any]:
    """All doshas from PyJHora.

    pp: planet_positions from charts.rasi_chart()
    h_to_p_list: house_planet_list (12-element list of planet strings)
    """
    if not PYJHORA_AVAILABLE:
        return {}
    results: Dict[str, Any] = {}

    # Full dosha details (jd, place)
    r = _safe_call(dosha.get_dosha_details, jd, place)
    if r is not None:
        results['all_dosha_details'] = r

    # Kala Sarpa needs house_planet_list
    if h_to_p_list is not None:
        r = _safe_call(dosha.kala_sarpa, h_to_p_list)
        if r is not None:
            results['kala_sarpa'] = r

    # Manglik & Shrapit need planet_positions
    if pp is not None:
        r = _safe_call(dosha.manglik, pp)
        if r is not None:
            results['manglik'] = r
        r = _safe_call(dosha.shrapit, pp)
        if r is not None:
            results['shrapit'] = r

    return results


# ──────────────────────────────────────────────────────────────────────
# Section 8: Arudhas (Bhava, Graha, Chandra, Surya)
# ──────────────────────────────────────────────────────────────────────

def get_arudhas(pp, h_to_p_list) -> Dict[str, Any]:
    """All arudha computations.

    pp: planet_positions from charts.rasi_chart()
    h_to_p_list: house_planet_list
    """
    if not PYJHORA_AVAILABLE:
        return {}
    results: Dict[str, Any] = {}

    if h_to_p_list is not None:
        r = _safe_call(arudhas.bhava_arudhas, h_to_p_list)
        if r is not None:
            results['bhava_arudhas'] = r
        r = _safe_call(arudhas.graha_arudhas, h_to_p_list)
        if r is not None:
            results['graha_arudhas'] = r

    if pp is not None:
        r = _safe_call(arudhas.bhava_arudhas_from_planet_positions, pp)
        if r is not None:
            results['bhava_arudhas_from_pp'] = r
        r = _safe_call(arudhas.chandra_arudhas_from_planet_positions, pp)
        if r is not None:
            results['chandra_arudhas'] = r
        r = _safe_call(arudhas.surya_arudhas_from_planet_positions, pp)
        if r is not None:
            results['surya_arudhas'] = r

    return results


# ──────────────────────────────────────────────────────────────────────
# Section 9: House Analysis (Karakas, Brahma, Rudra, Marakas, Longevity)
# ──────────────────────────────────────────────────────────────────────

def get_house_analysis(dob, tob, place, pp, h_to_p_list) -> Dict[str, Any]:
    """House-based analysis: chara karakas, brahma, rudra, marakas, longevity."""
    if not PYJHORA_AVAILABLE:
        return {}
    results: Dict[str, Any] = {}

    if pp is not None:
        r = _safe_call(house.chara_karakas, pp)
        if r is not None:
            results['chara_karakas'] = r
        r = _safe_call(house.brahma, pp)
        if r is not None:
            results['brahma'] = r
        r = _safe_call(house.rudra, pp)
        if r is not None:
            results['rudra'] = r

    if h_to_p_list is not None:
        r = _safe_call(house.marakas, h_to_p_list)
        if r is not None:
            results['marakas'] = r

    r = _safe_call(house.maheshwara, dob, tob, place)
    if r is not None:
        results['maheshwara'] = r

    r = _safe_call(house.longevity, dob, tob, place)
    if r is not None:
        results['longevity'] = r

    return results


# ──────────────────────────────────────────────────────────────────────
# Section 10: Divisional Charts (D1–D60)
# ──────────────────────────────────────────────────────────────────────

_DIVISIONAL_FACTORS = {
    1: 'Rasi', 2: 'Hora', 3: 'Drekkana', 4: 'Chaturthamsa',
    7: 'Saptamsa', 9: 'Navamsa', 10: 'Dasamsa', 12: 'Dwadasamsa',
    16: 'Shodasamsa', 20: 'Vimsamsa', 24: 'Chaturvimsamsa',
    27: 'Nakshatramsa', 30: 'Trimsamsa', 40: 'Khavedamsa',
    45: 'Akshavedamsa', 60: 'Shashtiamsa',
}


def get_divisional_charts(jd, place) -> Dict[str, Any]:
    """Compute all 16 standard divisional charts + bhava chart."""
    if not PYJHORA_AVAILABLE:
        return {}
    results: Dict[str, Any] = {}

    for dcf, dname in _DIVISIONAL_FACTORS.items():
        r = _safe_call(charts.divisional_chart, jd, place, dcf)
        if r is not None:
            results[f'D{dcf}_{dname}'] = r

    r = _safe_call(charts.bhava_chart, jd, place)
    if r is not None:
        results['bhava_chart'] = r

    r = _safe_call(charts.benefics_and_malefics, jd, place)
    if r is not None:
        results['benefics_malefics'] = r

    return results


# ──────────────────────────────────────────────────────────────────────
# Section 11: Panchanga Data
# ──────────────────────────────────────────────────────────────────────

def get_panchanga(jd, place) -> Dict[str, Any]:
    """Core panchanga data: tithi, nakshatra, yogam, karana, vaara, etc."""
    if not PYJHORA_AVAILABLE:
        return {}
    results: Dict[str, Any] = {}

    for name, fn, args in [
        ('ascendant',       drik.ascendant,       (jd, place)),
        ('tithi',           drik.tithi,            (jd, place)),
        ('nakshatra',       drik.nakshatra,        (jd, place)),
        ('yogam',           drik.yogam,            (jd, place)),
        ('karana',          drik.karana,            (jd, place)),
        ('vaara',           drik.vaara,            (jd,)),
        ('moonrise',        drik.moonrise,         (jd, place)),
    ]:
        r = _safe_call(fn, *args)
        if r is not None:
            results[name] = r

    # Sunrise / Sunset
    sr = _safe_call(drik.sunrise, jd, place)
    ss = _safe_call(drik.sunset, jd, place)
    if sr is not None or ss is not None:
        results['sunrise'] = sr
        results['sunset'] = ss

    # Extra panchanga items
    for fn_name in ['abhijit_muhurta', 'durmuhurtam', 'gulikai_kaalam',
                    'raahu_kaalam', 'yamagandam', 'lunar_month',
                    'day_length', 'is_night_birth']:
        fn = getattr(drik, fn_name, None)
        if fn is None:
            continue
        try:
            sig = inspect.signature(fn)
            params = list(sig.parameters.keys())
            if len(params) == 1:
                r = fn(jd)
            else:
                r = fn(jd, place)
            if r is not None:
                results[fn_name] = r
        except Exception:
            pass

    return results


# ──────────────────────────────────────────────────────────────────────
# Section 12: Compatibility (for synastry)
# ──────────────────────────────────────────────────────────────────────

def get_compatibility(jd1, place1, jd2, place2) -> Optional[Any]:
    """Compute Ashtakoota compatibility between two charts.

    Returns compatibility result or None.
    """
    if not PYJHORA_AVAILABLE:
        return None
    try:
        return compatibility.Ashtakoota(jd1, place1, jd2, place2)
    except Exception as exc:
        logger.debug("Compatibility failed: %s", exc)
        return None


# ══════════════════════════════════════════════════════════════════════
# MASTER FUNCTION — compute EVERYTHING PyJHora offers
# ══════════════════════════════════════════════════════════════════════

def compute_all_pyjhora(
    year: int, month: int, day: int,
    hour: int, minute: int, second: int,
    lat: float, lon: float, tz: float,
) -> Dict[str, Any]:
    """
    Master function: compute EVERYTHING PyJHora offers.

    Returns a single dict with all results, suitable for storing in
    static["computed"]["pyjhora"].

    If PyJHora is not installed or any setup fails, returns {"available": False}.
    Individual sections that fail are omitted from their sub-dict (never crash).
    """
    if not PYJHORA_AVAILABLE:
        return {"available": False}

    jd_data = _make_jd(year, month, day, hour, minute, second)
    if jd_data is None:
        return {"available": False}

    jd, dob, tob = jd_data
    place = _make_place(lat, lon, tz)
    if place is None:
        return {"available": False}

    # Get the core chart data needed by many sub-functions
    pp, h_to_p = _get_chart_data(jd, place)
    dob_tuple = (year, month, day)  # plain tuple for Sudarshana

    return {
        "available": True,
        "jd": jd,
        "panchanga":        get_panchanga(jd, place),
        "divisional_charts": get_divisional_charts(jd, place),
        "graha_dashas":     get_all_graha_dashas(jd, place, dob, tob),
        "rasi_dashas":      get_all_rasi_dashas(jd, place, dob, tob),
        "annual_dashas":    get_annual_dashas(jd, place, dob_tuple),
        "yogas":            get_all_yogas(jd, place),
        "sphutas":          get_all_sphutas(dob, tob, place),
        "strengths":        get_strengths(jd, place, dob, tob),
        "ashtakavarga":     get_ashtakavarga(h_to_p),
        "doshas":           get_doshas(jd, place, pp, h_to_p),
        "arudhas":          get_arudhas(pp, h_to_p),
        "house_analysis":   get_house_analysis(dob, tob, place, pp, h_to_p),
    }
