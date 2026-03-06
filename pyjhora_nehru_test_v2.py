# -*- coding: utf-8 -*-
"""
PyJHora v4.7.0 — Comprehensive Nehru Chart Test (v2 - Fixed)
Jawaharlal Nehru: 14 Nov 1889, 23:11 IST, Allahabad (25.4358N, 81.8463E)

Fixes applied:
  - dob = drik.Date(y,m,d) not plain tuple (required by sphutas, gulika, etc.)
  - house_planet_list format for ashtakavarga, arudhas, marakas, kala_sarpa
  - Correct function names for each dasha module
  - drig dasha: use drig_dhasa_bhukthi(dob,tob,place) not get_dhasa_antardhasa(jd,place)
"""
import sys, io, os, json, traceback, inspect, importlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── Setup ──────────────────────────────────────────────────────────────
from jhora.panchanga import drik
from jhora import utils as jhora_utils, const
from jhora.horoscope.main import Horoscope
import swisseph as swe

place = drik.Place('Allahabad', 25.4358, 81.8463, 5.5)
year, month, day = 1889, 11, 14
dob = drik.Date(year, month, day)
dob_tuple = (year, month, day)  # some functions still want plain tuple
tob = (23, 11, 0)  # 23:11 IST
jd = jhora_utils.julian_day_number(dob, tob)

output = []
section_num = 0
success_count = 0
fail_count = 0
section_summary = []

def log(section, data, status='OK'):
    global section_num, success_count, fail_count
    section_num += 1
    tag = 'OK' if status == 'OK' else 'FAIL'
    output.append(f"\n{'='*70}")
    output.append(f"  [{section_num:02d}] {section}  [{tag}]")
    output.append(f"{'='*70}")
    if isinstance(data, (dict, list, tuple)):
        try:
            output.append(json.dumps(data, indent=2, default=str, ensure_ascii=False))
        except:
            output.append(repr(data)[:5000])
    else:
        output.append(str(data)[:5000])
    if status == 'OK':
        success_count += 1
        preview = str(data)[:120].replace('\n', ' ')
        section_summary.append(f"  [{section_num:02d}] OK   {section}: {preview}")
    else:
        fail_count += 1
        section_summary.append(f"  [{section_num:02d}] FAIL {section}: {str(data)[:100]}")

def safe(section, fn, *args, **kwargs):
    try:
        result = fn(*args, **kwargs)
        log(section, result)
        return result
    except Exception as e:
        log(section, f"{e}\n{traceback.format_exc()}", status='FAIL')
        return None

# ======================================================================
# 0) BASIC INFO
# ======================================================================
log("Setup: Julian Day", jd)
log("Setup: Place", repr(place))

# ======================================================================
# 1) HOROSCOPE CLASS — Full Information
# ======================================================================
print("[1] Horoscope class...", flush=True)
h = Horoscope(
    place_with_country_code='Allahabad,IN',
    latitude=25.4358, longitude=81.8463, timezone_offset=5.5,
    date_in=drik.Date(1889, 11, 14),
    birth_time='23:11:00'
)

horo_info = safe("Horoscope.get_horoscope_information()", h.get_horoscope_information)
cal_info = safe("Horoscope.get_calendar_information()", h.get_calendar_information)
chart_info = safe("Horoscope.get_horoscope_information_for_chart(D1)",
    h.get_horoscope_information_for_chart, chart_index=0, chart_method=1, divisional_chart_factor=1)

# ======================================================================
# 2) PANCHANGA DATA
# ======================================================================
print("[2] Panchanga...", flush=True)
safe("Ascendant", drik.ascendant, jd, place)
safe("Tithi", drik.tithi, jd, place)
safe("Nakshatra", drik.nakshatra, jd, place)
safe("Yogam", drik.yogam, jd, place)
safe("Karana", drik.karana, jd, place)
safe("Vaara (weekday)", drik.vaara, jd)
safe("Sunrise/Sunset", lambda: (drik.sunrise(jd, place), drik.sunset(jd, place)))
safe("Moonrise", drik.moonrise, jd, place)

for fn_name in ['abhijit_muhurta', 'durmuhurtam', 'gulikai_kaalam',
                'raahu_kaalam', 'yamagandam']:
    if hasattr(drik, fn_name):
        safe(f"Panchanga: {fn_name}", getattr(drik, fn_name), jd, place)

for fn_name in ['lunar_month', 'day_length', 'is_night_birth']:
    if hasattr(drik, fn_name):
        fn = getattr(drik, fn_name)
        sig = inspect.signature(fn)
        params = list(sig.parameters.keys())
        try:
            if len(params) == 1:
                result = fn(jd)
            else:
                result = fn(jd, place)
            log(f"Panchanga: {fn_name}", result)
        except Exception as e:
            log(f"Panchanga: {fn_name}", f"{e}", status='FAIL')

# ======================================================================
# 3) DIVISIONAL CHARTS
# ======================================================================
print("[3] Charts...", flush=True)
from jhora.horoscope.chart import charts

rasi_chart = safe("Rasi Chart (D1)", charts.rasi_chart, jd, place)

# Convert to house_planet_list for functions that need it
h_to_p_list = None
if rasi_chart is not None:
    h_to_p_list = jhora_utils.get_house_planet_list_from_planet_positions(rasi_chart)

dcf_names = {2:'Hora', 3:'Drekkana', 4:'Chaturthamsa', 7:'Saptamsa', 9:'Navamsa',
             10:'Dasamsa', 12:'Dwadasamsa', 16:'Shodasamsa', 20:'Vimsamsa',
             24:'Chaturvimsamsa', 27:'Nakshatramsa', 30:'Trimsamsa', 40:'Khavedamsa',
             45:'Akshavedamsa', 60:'Shashtiamsa'}

for dcf, dname in dcf_names.items():
    safe(f"Divisional Chart D-{dcf} ({dname})", charts.divisional_chart, jd, place, dcf)

safe("Bhava Chart", charts.bhava_chart, jd, place)
safe("Benefics & Malefics", charts.benefics_and_malefics, jd, place)

if rasi_chart is not None:
    safe("Navamsa from Rasi", charts.navamsa_chart, rasi_chart)
    safe("Dasamsa from Rasi", charts.dasamsa_chart, rasi_chart)

# ======================================================================
# 4) STRENGTH
# ======================================================================
print("[4] Strength...", flush=True)
from jhora.horoscope.chart import strength

safe("Shadbala", strength.shad_bala, jd, place)
safe("Bhava Bala", strength.bhava_bala, jd, place)
safe("Pancha Vargeeya Bala", strength.pancha_vargeeya_bala, jd, place)
safe("Dwadhasa Vargeeya Bala", strength.dwadhasa_vargeeya_bala, jd, place)
safe("Harsha Bala", strength.harsha_bala, dob, tob, place)

# ======================================================================
# 5) ASHTAKAVARGA
# ======================================================================
print("[5] Ashtakavarga...", flush=True)
from jhora.horoscope.chart import ashtakavarga

if h_to_p_list is not None:
    av = safe("Ashtakavarga (BAV + SAV + Prastara)", ashtakavarga.get_ashtaka_varga, h_to_p_list)
    if av is not None:
        safe("Sodhaya Pindas", ashtakavarga.sodhaya_pindas, av, h_to_p_list)

# ======================================================================
# 6) SPHUTAS  (need drik.Date dob)
# ======================================================================
print("[6] Sphutas...", flush=True)
from jhora.horoscope.chart import sphuta

sphuta_names = ['tri_sphuta', 'chatur_sphuta', 'pancha_sphuta',
                'prana_sphuta', 'deha_sphuta', 'mrityu_sphuta',
                'sookshma_tri_sphuta', 'beeja_sphuta', 'kshetra_sphuta',
                'avayogi_sphuta', 'rahu_tithi_sphuta']

for sp in sphuta_names:
    if hasattr(sphuta, sp):
        safe(f"Sphuta: {sp}", getattr(sphuta, sp), dob, tob, place)

# ======================================================================
# 7) ARUDHAS  (need house_planet_list)
# ======================================================================
print("[7] Arudhas...", flush=True)
from jhora.horoscope.chart import arudhas

if h_to_p_list is not None:
    safe("Bhava Arudhas", arudhas.bhava_arudhas, h_to_p_list)
    safe("Graha Arudhas", arudhas.graha_arudhas, h_to_p_list)

if rasi_chart is not None:
    safe("Bhava Arudhas (from positions)", arudhas.bhava_arudhas_from_planet_positions, rasi_chart)
    safe("Chandra Arudhas", arudhas.chandra_arudhas_from_planet_positions, rasi_chart)
    safe("Surya Arudhas", arudhas.surya_arudhas_from_planet_positions, rasi_chart)

# ======================================================================
# 8) HOUSE ANALYSIS
# ======================================================================
print("[8] House Analysis...", flush=True)
from jhora.horoscope.chart import house

if rasi_chart is not None:
    safe("Chara Karakas", house.chara_karakas, rasi_chart)
    safe("Brahma", house.brahma, rasi_chart)
    safe("Rudra", house.rudra, rasi_chart)

if h_to_p_list is not None:
    safe("Marakas", house.marakas, h_to_p_list)

safe("Maheshwara", house.maheshwara, dob, tob, place)
safe("Longevity (house)", house.longevity, dob, tob, place)

# ======================================================================
# 9) DOSHAS
# ======================================================================
print("[9] Doshas...", flush=True)
from jhora.horoscope.chart import dosha

safe("Dosha Details (all)", dosha.get_dosha_details, jd, place)

if h_to_p_list is not None:
    safe("Kala Sarpa Dosha", dosha.kala_sarpa, h_to_p_list)

if rasi_chart is not None:
    safe("Manglik Dosha", dosha.manglik, rasi_chart)
    safe("Shrapit Dosha", dosha.shrapit, rasi_chart)

# ======================================================================
# 10) RAJA YOGAS
# ======================================================================
print("[10] Raja Yogas...", flush=True)
from jhora.horoscope.chart import raja_yoga

safe("Raja Yoga Details (D1)", raja_yoga.get_raja_yoga_details, jd, place)

# ======================================================================
# 11) YOGAS (comprehensive)
# ======================================================================
print("[11] Yogas...", flush=True)
from jhora.horoscope.chart import yoga

test_yogas = [
    'gaja_kesari_yoga', 'amala_yoga', 'lakshmi_yoga', 'saraswathi_yoga',
    'chandra_mangala_yoga', 'budha_yoga', 'vesi_yoga', 'vosi_yoga',
    'adhi_yoga', 'ruchaka_yoga', 'bhadra_yoga', 'sasa_yoga', 'hamsa_yoga',
    'maalavya_yoga', 'dhana_yoga', 'dharidhra_yoga', 'raja_yoga',
    'kemadruma_yoga', 'parijatha_yoga', 'siva_yoga', 'vishnu_yoga',
    'brahma_yoga', 'harsha_yoga', 'sarala_yoga', 'vimala_yoga',
    'anaphaa_yoga', 'sunapha_yoga', 'durudhura_yoga', 'parvatha_yoga',
    'kaahala_yoga', 'chaamara_yoga',
]

yoga_results = {}
for yname in test_yogas:
    jdp = f'{yname}_from_jd_place'
    if hasattr(yoga, jdp):
        try:
            result = getattr(yoga, jdp)(jd, place)
            yoga_results[yname] = result
        except Exception as e:
            yoga_results[yname] = f'FAIL: {e}'
    elif hasattr(yoga, yname):
        try:
            fn = getattr(yoga, yname)
            sig = inspect.signature(fn)
            params = list(sig.parameters.keys())
            if 'jd' in params or 'jd_at_dob' in params:
                result = fn(jd, place)
            elif 'planet_positions' in params and rasi_chart is not None:
                result = fn(rasi_chart)
            else:
                result = f'UNKNOWN SIG: {sig}'
            yoga_results[yname] = result
        except Exception as e:
            yoga_results[yname] = f'FAIL: {e}'
    else:
        yoga_results[yname] = 'NOT FOUND'

log("Yogas (31 tested)", yoga_results)

# ======================================================================
# 12) VIMSHOTTARI DASHA
# ======================================================================
print("[12] Vimshottari...", flush=True)
from jhora.horoscope.dhasa.graha import vimsottari
safe("Vimshottari Dasha", vimsottari.get_vimsottari_dhasa_bhukthi, jd, place)

# ======================================================================
# 13) ASHTOTTARI DASHA
# ======================================================================
from jhora.horoscope.dhasa.graha import ashtottari
safe("Ashtottari Dasha", ashtottari.get_ashtottari_dhasa_bhukthi, jd, place)

# ======================================================================
# 14-33) ALL GRAHA DASHAS
# ======================================================================
print("[14-33] Graha Dashas...", flush=True)

graha_dasha_calls = {
    'buddhi_gathi':    ('get_dhasa_bhukthi', 'dob'),
    'kaala':           ('get_dhasa_antardhasa', 'dob'),
    'karaka':          ('get_dhasa_antardhasa', 'dob'),
    'naisargika':      ('get_dhasa_bhukthi', 'dob'),
    'shastihayani':    ('get_dhasa_bhukthi', 'dob'),
    'yoga_vimsottari': ('get_dhasa_bhukthi', 'jd'),
    'tithi_ashtottari':('get_ashtottari_dhasa_bhukthi', 'jd'),
    'tithi_yogini':    ('get_dhasa_bhukthi', 'dob'),
    'saptharishi_nakshathra': ('get_dhasa_bhukthi', 'dob'),
    'yogini':          ('get_dhasa_bhukthi', 'dob'),
    'shodasottari':    ('get_dhasa_bhukthi', 'dob'),
    'dwadasottari':    ('get_dhasa_bhukthi', 'dob'),
    'dwisatpathi':     ('get_dhasa_bhukthi', 'dob'),
    'panchottari':     ('get_dhasa_bhukthi', 'dob'),
    'sataatbika':      ('get_dhasa_bhukthi', 'dob'),
    'chathuraaseethi_sama': ('get_dhasa_bhukthi', 'dob'),
    'shattrimsa_sama': ('get_dhasa_bhukthi', 'dob'),
    'tara':            ('get_dhasa_bhukthi', 'dob'),
    'karana_chathuraaseethi_sama': ('get_dhasa_bhukthi', 'dob'),
    'aayu':            ('get_dhasa_antardhasa', 'jd'),
}

for dasha_name, (fn_name, arg_type) in graha_dasha_calls.items():
    mod_path = f'jhora.horoscope.dhasa.graha.{dasha_name}'
    try:
        mod = importlib.import_module(mod_path)
        fn = getattr(mod, fn_name)
        if arg_type == 'dob':
            result = fn(dob, tob, place)
        else:
            result = fn(jd, place)
        log(f"Graha Dasha: {dasha_name}", result)
    except Exception as e:
        log(f"Graha Dasha: {dasha_name}", f"{e}\n{traceback.format_exc()}", status='FAIL')

# ======================================================================
# 34-55) ALL RAASI DASHAS
# ======================================================================
print("[34-55] Raasi Dashas...", flush=True)

rasi_dasha_calls = {
    'chakra':       ('get_dhasa_antardhasa', 'dob'),
    'sthira':       ('get_dhasa_antardhasa', 'dob'),
    'varnada':      ('get_dhasa_antardhasa', 'dob'),
    'yogardha':     ('get_dhasa_antardhasa', 'dob'),
    'paryaaya':     ('get_dhasa_antardhasa', 'dob'),
    'sandhya':      ('get_dhasa_antardhasa', 'dob'),
    'tara_lagna':   ('get_dhasa_antardhasa', 'dob'),
    'lagnamsaka':   ('get_dhasa_antardhasa', 'dob'),
    'chara':        ('get_dhasa_antardhasa', 'dob'),
    'brahma':       ('get_dhasa_antardhasa', 'dob'),
    'mandooka':     ('get_dhasa_antardhasa', 'dob'),
    'padhanadhamsa':('get_dhasa_antardhasa', 'dob'),
    'navamsa':      ('get_dhasa_antardhasa', 'dob'),
    'trikona':      ('get_dhasa_antardhasa', 'dob'),
    # Custom function names:
    'narayana':     ('narayana_dhasa_for_rasi_chart', 'dob'),
    'kendradhi_rasi': ('kendradhi_rasi_dhasa', 'dob'),
    'shoola':       ('shoola_dhasa_bhukthi', 'dob'),
    'sudasa':       ('sudasa_dhasa_bhukthi', 'dob'),
    'nirayana':     ('nirayana_shoola_dhasa_bhukthi', 'dob'),
    'moola':        ('moola_dhasa', 'dob'),
    'kalachakra':   ('get_dhasa_bhukthi', 'dob'),
    'drig':         ('drig_dhasa_bhukthi', 'dob'),
}

for dasha_name, (fn_name, arg_type) in rasi_dasha_calls.items():
    mod_path = f'jhora.horoscope.dhasa.raasi.{dasha_name}'
    try:
        mod = importlib.import_module(mod_path)
        fn = getattr(mod, fn_name)
        if arg_type == 'dob':
            result = fn(dob, tob, place)
        else:
            result = fn(jd, place)
        log(f"Raasi Dasha: {dasha_name}", result)
    except Exception as e:
        log(f"Raasi Dasha: {dasha_name}", f"{e}\n{traceback.format_exc()}", status='FAIL')

# ======================================================================
# 56) SUDARSHANA CHAKRA DASHA
# ======================================================================
print("[56] Sudarshana...", flush=True)
try:
    from jhora.horoscope.dhasa import sudharsana_chakra
    safe("Sudarshana Chakra Dasha",
         sudharsana_chakra.sudharsana_chakra_dhasa_for_divisional_chart,
         jd, place, dob_tuple)
except Exception as e:
    log("Sudarshana Chakra Dasha", f"{e}", status='FAIL')

# ======================================================================
# 57) ANNUAL DASHAS
# ======================================================================
print("[57] Annual Dashas...", flush=True)
try:
    from jhora.horoscope.dhasa.annual import mudda
    safe("Mudda Dasha (Varsha Vimsottari)", mudda.varsha_vimsottari_dhasa_bhukthi, jd, place, 1)
except Exception as e:
    log("Mudda Dasha", f"{e}", status='FAIL')

try:
    from jhora.horoscope.dhasa.annual import patyayini
    safe("Patyayini Dasha", patyayini.patyayini_dhasa, jd, place)
except Exception as e:
    log("Patyayini Dasha", f"{e}", status='FAIL')

# ======================================================================
# 58) SPECIAL LAGNAS & KARAKAS (via Horoscope class)
# ======================================================================
print("[58] Special Lagnas & Karakas...", flush=True)
safe("Special Lagnas (D1)", h.get_special_lagnas_for_chart, jd, place)
safe("Chara Karakas for Chart (D1)", h.get_chara_karakas_for_chart, jd, place)
safe("Sahams", lambda: h.get_sahams(rasi_chart) if rasi_chart else "NO RASI CHART")
safe("Sphutas for Chart (D1)", h.get_sphutas_for_chart, jd, place)
safe("Bhava Chart Info", h.get_bhava_chart_information, jd, place)
safe("Ava Saha Yoga (D1)", h.get_ava_saha_yoga_info_for_chart, jd, place)
safe("Varnada Lagna (D1)", h.get_varnada_lagna_for_chart, dob_tuple, tob, place)
safe("Special Planets (D1)", h.get_special_planets_for_chart, jd, place)

# ======================================================================
# SAVE OUTPUT
# ======================================================================
outfile = "pyjhora_nehru_output_v2.txt"
with open(outfile, "w", encoding="utf-8") as f:
    f.write(f"PyJHora v4.7.0 — Nehru Chart Comprehensive Output\n")
    f.write(f"Generated: {__import__('datetime').datetime.now()}\n")
    f.write(f"Subject: Jawaharlal Nehru, 14 Nov 1889, 23:11 IST, Allahabad\n")
    f.write(f"JD: {jd}\n")
    f.write(f"{'='*70}\n")
    f.write(f"RESULTS: {success_count} succeeded, {fail_count} failed out of {section_num} sections\n")
    f.write(f"{'='*70}\n\n")
    f.write("SECTION SUMMARY:\n")
    for s in section_summary:
        f.write(s + "\n")
    f.write("\n" + "="*70 + "\n")
    f.write("DETAILED OUTPUT\n")
    f.write("="*70 + "\n")
    f.write("\n".join(output))

print(f"\n{'='*70}")
print(f"DONE: {success_count} OK / {fail_count} FAIL / {section_num} total")
print(f"Output saved to {outfile}")
print(f"{'='*70}")
