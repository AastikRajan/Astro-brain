"""
Run Nehru's chart through PyJHora v4.7.0 and capture everything it computes.
Save raw output to pyjhora_nehru_output.txt

API conventions discovered:
  - place = drik.Place('name', lat, lon, tz)  (namedtuple, NOT plain tuple)
  - drik/charts/strength/vimsottari/raja_yoga/prediction: (jd, place)
  - most graha dashas / rasi dashas / sphutas: (dob, tob, place)
  - ashtakavarga/dosha/house/arudhas: (house_to_planet_list) or (planet_positions)
  - sudarshana: (jd, place, dob)
  - navamsa_chart/dasamsa_chart: (planet_positions_in_rasi)
"""
import json
import traceback
import inspect
from datetime import datetime

from jhora.panchanga import drik
from jhora import utils as jhora_utils

place = drik.Place('Allahabad', 25.4358, 81.8463, 5.5)
year, month, day = 1889, 11, 14
dob = (year, month, day)
tob = (23, 26, 0)
jd = jhora_utils.julian_day_number(dob, tob)

output = []

def log(section, data):
    output.append(f"\n{'='*60}")
    output.append(f"  {section}")
    output.append(f"{'='*60}")
    if isinstance(data, (dict, list)):
        output.append(json.dumps(data, indent=2, default=str))
    else:
        output.append(str(data))

log("Julian Day", jd)
log("Place object", repr(place))

# ===================================================================
# A: Basic Positions  (jd, place)
# ===================================================================
planets = None
try:
    planets = drik.planetary_positions(jd, place)
    log("Planet Positions (raw)", planets)
except Exception as e:
    log("Planet Positions", f"FAILED: {e}\n{traceback.format_exc()}")

try:
    asc = drik.ascendant(jd, place)
    log("Ascendant", asc)
except Exception as e:
    log("Ascendant", f"FAILED: {e}")

for name, fn in [("Tithi", "tithi"), ("Nakshatra", "nakshatra"),
                 ("Yoga", "yogam"), ("Karana", "karana")]:
    try:
        result = getattr(drik, fn)(jd, place)
        log(name, result)
    except Exception as e:
        log(name, f"FAILED: {e}")

try:
    v = drik.vaara(jd)
    log("Vaara (weekday)", v)
except Exception as e:
    log("Vaara", f"FAILED: {e}")

# ===================================================================
# B: Divisional Charts
# ===================================================================
rasi_chart = None
try:
    from jhora.horoscope.chart import charts
    rasi_chart = charts.rasi_chart(jd, place)
    log("Rasi Chart (D1)", rasi_chart)
except Exception as e:
    log("Rasi Chart (D1)", f"FAILED: {e}\n{traceback.format_exc()}")

if rasi_chart is not None:
    try:
        nav = charts.navamsa_chart(rasi_chart)
        log("Navamsa Chart (D9)", nav)
    except Exception as e:
        log("Navamsa (D9)", f"FAILED: {e}")
    try:
        das = charts.dasamsa_chart(rasi_chart)
        log("Dasamsa Chart (D10)", das)
    except Exception as e:
        log("Dasamsa (D10)", f"FAILED: {e}")

try:
    bhava = charts.bhava_chart(jd, place)
    log("Bhava Chart", bhava)
except Exception as e:
    log("Bhava Chart", f"FAILED: {e}")

# ===================================================================
# C: Strength  (jd, place)
# ===================================================================
try:
    from jhora.horoscope.chart import strength
    sb = strength.shad_bala(jd, place)
    log("Shadbala", sb)
except Exception as e:
    log("Shadbala", f"FAILED: {e}")

try:
    bb = strength.bhava_bala(jd, place)
    log("Bhava Bala", bb)
except Exception as e:
    log("Bhava Bala", f"FAILED: {e}")

# ===================================================================
# D: Ashtakavarga  (house_to_planet_list)
# ===================================================================
try:
    from jhora.horoscope.chart import ashtakavarga
    if rasi_chart is not None:
        av = ashtakavarga.get_ashtaka_varga(rasi_chart)
        log("Ashtakavarga", av)
    else:
        log("Ashtakavarga", "SKIPPED: no rasi_chart")
except Exception as e:
    log("Ashtakavarga", f"FAILED: {e}")

# ===================================================================
# E: Vimshottari Dasha  (jd, place)
# ===================================================================
try:
    from jhora.horoscope.dhasa.graha import vimsottari
    vd = vimsottari.get_vimsottari_dhasa_bhukthi(jd, place)
    log("Vimshottari Dasha", vd)
except Exception as e:
    log("Vimshottari Dasha", f"FAILED: {e}\n{traceback.format_exc()}")

# ===================================================================
# F: Graha Dashas  — auto-detect (jd, place) vs (dob, tob, place)
# ===================================================================
graha_dashas = ['buddhi_gathi', 'kaala', 'karaka', 'naisargika',
                'shastihayani', 'yoga_vimsottari', 'tithi_ashtottari',
                'tithi_yogini', 'saptharishi_nakshathra', 'ashtottari',
                'yogini', 'shodasottari', 'dwadasottari', 'dwisatpathi',
                'panchottari', 'sataatbika', 'chathuraaseethi_sama',
                'shattrimsa_sama', 'tara']

for dasha_name in graha_dashas:
    try:
        mod = __import__(f'jhora.horoscope.dhasa.graha.{dasha_name}', fromlist=[dasha_name])
        fn = None
        for candidate in ['get_dhasa_bhukthi', 'get_dhasa_antardhasa']:
            if hasattr(mod, candidate):
                fn = getattr(mod, candidate)
                break
        if fn is None:
            funcs = [f for f in dir(mod) if 'dhasa' in f.lower() or 'bhukthi' in f.lower()]
            log(f"Graha Dasha: {dasha_name}", f"Available functions: {funcs}")
            continue
        sig = inspect.signature(fn)
        params = list(sig.parameters.keys())
        if len(params) >= 1 and params[0] == 'dob':
            result = fn(dob, tob, place)
        else:
            result = fn(jd, place)
        log(f"Graha Dasha: {dasha_name}", result)
    except Exception as e:
        log(f"Graha Dasha: {dasha_name}", f"FAILED: {e}")

# ===================================================================
# G: Rasi Dashas  — auto-detect (jd, place) vs (dob, tob, place)
# ===================================================================
rasi_dashas = ['chakra', 'kendradhi_rasi', 'sthira', 'varnada',
               'yogardha', 'paryaaya', 'sandhya', 'tara_lagna',
               'lagnamsaka', 'narayana', 'chara', 'brahma', 'shoola',
               'sudasa', 'drig', 'nirayana', 'mandooka', 'padhanadhamsa',
               'navamsa', 'trikona', 'moola']

for dasha_name in rasi_dashas:
    try:
        mod = __import__(f'jhora.horoscope.dhasa.raasi.{dasha_name}', fromlist=[dasha_name])
        fn = None
        for candidate in ['get_dhasa_antardhasa', 'get_dhasa_bhukthi']:
            if hasattr(mod, candidate):
                fn = getattr(mod, candidate)
                break
        if fn is None:
            funcs = [f for f in dir(mod) if 'dhasa' in f.lower() or 'bhukthi' in f.lower()]
            log(f"Rasi Dasha: {dasha_name}", f"Available functions: {funcs}")
            continue
        sig = inspect.signature(fn)
        params = list(sig.parameters.keys())
        if len(params) >= 1 and params[0] == 'dob':
            result = fn(dob, tob, place)
        else:
            result = fn(jd, place)
        log(f"Rasi Dasha: {dasha_name}", result)
    except Exception as e:
        log(f"Rasi Dasha: {dasha_name}", f"FAILED: {e}")

# ===================================================================
# H: Sudarshana  (jd, place, dob)
# ===================================================================
try:
    from jhora.horoscope.dhasa import sudharsana_chakra
    sc = sudharsana_chakra.sudharsana_chakra_dhasa_for_divisional_chart(jd, place, dob)
    log("Sudarshana Chakra Dasha", sc)
except Exception as e:
    log("Sudarshana Chakra Dasha", f"FAILED: {e}")

# ===================================================================
# I: Sphutas  (dob, tob, place)
# ===================================================================
try:
    from jhora.horoscope.chart import sphuta
    sphuta_list = ['tri_sphuta', 'chatur_sphuta', 'pancha_sphuta',
                   'prana_sphuta', 'deha_sphuta', 'mrityu_sphuta',
                   'sookshma_tri_sphuta', 'beeja_sphuta', 'kshetra_sphuta',
                   'tithi_sphuta', 'yoga_sphuta', 'yogi_sphuta',
                   'avayogi_sphuta', 'rahu_tithi_sphuta']
    for sp in sphuta_list:
        if hasattr(sphuta, sp):
            try:
                result = getattr(sphuta, sp)(dob, tob, place)
                log(f"Sphuta: {sp}", result)
            except Exception as e:
                log(f"Sphuta: {sp}", f"FAILED: {e}")
        else:
            log(f"Sphuta: {sp}", "NOT FOUND")
except Exception as e:
    log("SPHUTAS", f"FAILED: {e}\n{traceback.format_exc()}")

# ===================================================================
# J: Yogas  — _from_jd_place(jd, place) or _from_planet_positions(rasi)
# ===================================================================
try:
    from jhora.horoscope.chart import yoga
    yoga_funcs = [f for f in dir(yoga) if not f.startswith('_') and callable(getattr(yoga, f, None))]
    log("Yoga module: callable functions (first 50)", yoga_funcs[:50])
    log("Yoga module: total callable functions", len(yoga_funcs))

    test_yogas = ['gaja_kesari_yoga', 'amala_yoga', 'lakshmi_yoga',
        'saraswathi_yoga', 'chandra_mangala_yoga', 'budha_yoga',
        'vesi_yoga', 'vosi_yoga', 'adhi_yoga', 'ruchaka_yoga',
        'bhadra_yoga', 'sasa_yoga', 'hamsa_yoga', 'maalavya_yoga',
        'dhana_yoga', 'dharidhra_yoga', 'raja_yoga',
        'kemadruma_yoga', 'parijatha_yoga', 'siva_yoga']

    for yname in test_yogas:
        found = False
        jdp = f'{yname}_from_jd_place'
        if hasattr(yoga, jdp):
            try:
                result = getattr(yoga, jdp)(jd, place)
                log(f"Yoga: {yname}", result)
                found = True
            except Exception as e:
                log(f"Yoga: {yname}", f"FAILED ({jdp}): {e}")
                found = True
        if not found:
            ppos = f'{yname}_from_planet_positions'
            if hasattr(yoga, ppos) and rasi_chart is not None:
                try:
                    result = getattr(yoga, ppos)(rasi_chart)
                    log(f"Yoga: {yname}", result)
                    found = True
                except Exception as e:
                    log(f"Yoga: {yname}", f"FAILED ({ppos}): {e}")
                    found = True
        if not found:
            log(f"Yoga: {yname}", "NOT FOUND")
except Exception as e:
    log("YOGAS", f"FAILED: {e}\n{traceback.format_exc()}")

# ===================================================================
# K: Raja Yogas  (jd, place)
# ===================================================================
try:
    from jhora.horoscope.chart import raja_yoga
    ry = raja_yoga.get_raja_yoga_details(jd, place)
    log("Raja Yoga Details", ry)
except Exception as e:
    log("Raja Yoga", f"FAILED: {e}")

# ===================================================================
# L: Doshas
# ===================================================================
try:
    from jhora.horoscope.chart import dosha
    dosha_funcs = [f for f in dir(dosha) if not f.startswith('_') and callable(getattr(dosha, f, None))]
    log("Dosha module functions", dosha_funcs)

    # get_dosha_details(jd, place)
    try:
        dd = dosha.get_dosha_details(jd, place)
        log("Dosha Details (all)", dd)
    except Exception as e:
        log("Dosha Details", f"FAILED: {e}")

    # 1-arg doshas that take house_to_planet_list
    for dname in ['kala_sarpa', 'pitru_dosha', 'ghata', 'shrapit',
                  'ganda_moola', 'guru_chandala_dosha']:
        if hasattr(dosha, dname):
            try:
                result = getattr(dosha, dname)(rasi_chart)
                log(f"Dosha: {dname}", result)
            except Exception as e:
                log(f"Dosha: {dname}", f"FAILED: {e}")

    # manglik / kalathra take (planet_positions)
    for dname in ['manglik', 'kalathra']:
        if hasattr(dosha, dname) and rasi_chart is not None:
            try:
                result = getattr(dosha, dname)(rasi_chart)
                log(f"Dosha: {dname}", result)
            except Exception as e:
                log(f"Dosha: {dname}", f"FAILED: {e}")
except Exception as e:
    log("DOSHAS", f"FAILED: {e}\n{traceback.format_exc()}")

# ===================================================================
# M: Arudhas  (chart / planet_positions)
# ===================================================================
try:
    from jhora.horoscope.chart import arudhas
    if rasi_chart is not None:
        ar = arudhas.bhava_arudhas(rasi_chart)
        log("Bhava Arudhas", ar)
    else:
        log("Bhava Arudhas", "SKIPPED")
except Exception as e:
    log("Arudhas", f"FAILED: {e}")

# ===================================================================
# N: House Analysis  (planet_positions / dob,tob,place)
# ===================================================================
try:
    from jhora.horoscope.chart import house
    if rasi_chart is not None:
        try:
            ck = house.chara_karakas(rasi_chart)
            log("Chara Karakas", ck)
        except Exception as e:
            log("Chara Karakas", f"FAILED: {e}")
        try:
            mk = house.marakas(rasi_chart)
            log("Marakas", mk)
        except Exception as e:
            log("Marakas", f"FAILED: {e}")
    try:
        lon = house.longevity(dob, tob, place)
        log("Longevity (house)", lon)
    except Exception as e:
        log("Longevity (house)", f"FAILED: {e}")
except Exception as e:
    log("HOUSE ANALYSIS", f"FAILED: {e}\n{traceback.format_exc()}")

# ===================================================================
# O: Compatibility (list functions)
# ===================================================================
try:
    from jhora.horoscope.match import compatibility
    comp_funcs = [f for f in dir(compatibility) if not f.startswith('_') and callable(getattr(compatibility, f, None))]
    log("Compatibility module functions", comp_funcs)
except Exception as e:
    log("COMPATIBILITY", f"FAILED: {e}")

# ===================================================================
# P: Prediction  (jd, place)
# ===================================================================
try:
    from jhora.horoscope.prediction import general as pred_general
    pred = pred_general.get_prediction_details(jd, place)
    log("Prediction Details", pred)
except Exception as e:
    log("Prediction", f"FAILED: {e}")

# ===================================================================
# Q: Longevity prediction  (jd, place)
# ===================================================================
try:
    from jhora.horoscope.prediction import longevity as pred_longevity
    lon_result = pred_longevity.life_span_range(jd, place)
    log("Longevity (Prediction)", lon_result)
except Exception as e:
    log("Longevity (Prediction)", f"FAILED: {e}")

# ===================================================================
# R: Tajaka (list functions)
# ===================================================================
try:
    from jhora.horoscope.transit import tajaka_yoga
    tajaka_funcs = [f for f in dir(tajaka_yoga) if not f.startswith('_') and callable(getattr(tajaka_yoga, f, None))]
    log("Tajaka Yoga functions", tajaka_funcs)
except Exception as e:
    log("Tajaka Yoga", f"FAILED: {e}")

# ===================================================================
# SAVE
# ===================================================================
with open("pyjhora_nehru_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print(f"Done. Output saved to pyjhora_nehru_output.txt ({len(output)} lines)")
