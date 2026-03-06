# PyJHora: Install + Test Output
# New VS Code chat. Fresh context. Don't touch vedic_engine/ at all.

---

## STEP 1: Install PyJHora in our venv

```
cd "C:\Users\aasti\Downloads\New folder (3)"
.venv\Scripts\pip.exe install PyJHora
```

If it fails due to pyqt6 or UI dependencies, try:
```
.venv\Scripts\pip.exe install PyJHora --no-deps
.venv\Scripts\pip.exe install pyswisseph
```

We only need the computation modules, not the UI.

## STEP 2: Test if it imports

```python
# test_pyjhora.py
try:
    from jhora.panchanga import drik
    print("drik module: OK")
except Exception as e:
    print(f"drik: FAIL - {e}")

try:
    from jhora.horoscope.chart import charts
    print("charts module: OK")
except Exception as e:
    print(f"charts: FAIL - {e}")

try:
    from jhora.horoscope.chart import yoga
    print("yoga module: OK")
except Exception as e:
    print(f"yoga: FAIL - {e}")

try:
    from jhora.horoscope.chart import sphuta
    print("sphuta module: OK")
except Exception as e:
    print(f"sphuta: FAIL - {e}")

try:
    from jhora.horoscope.dhasa.graha import vimsottari
    print("vimsottari dasha: OK")
except Exception as e:
    print(f"vimsottari: FAIL - {e}")

try:
    from jhora.horoscope.match import compatibility
    print("compatibility: OK")
except Exception as e:
    print(f"compatibility: FAIL - {e}")

print("\nAll import tests done.")
```

## STEP 3: Run Nehru chart through PyJHora and capture ALL output

```python
# pyjhora_nehru_test.py
"""
Run Nehru's chart through PyJHora and capture everything it computes.
Save raw output to pyjhora_nehru_output.txt
"""
import json
from datetime import datetime

# PyJHora uses Julian Day + place tuple
# Place = (latitude, longitude, timezone_offset_hours)
place = (25.4358, 81.8463, 5.5)  # Allahabad

# Birth: 1889-11-14, 23:26:00 IST
# PyJHora needs year, month, day as separate args
year, month, day = 1889, 11, 14
birth_time = "23:26:00"  # or as hours: 23 + 26/60 = 23.4333

output = []

def log(section, data):
    output.append(f"\n{'='*60}")
    output.append(f"  {section}")
    output.append(f"{'='*60}")
    if isinstance(data, (dict, list)):
        output.append(json.dumps(data, indent=2, default=str))
    else:
        output.append(str(data))

# --- Figure out how PyJHora wants input ---
# Check their API: most functions take (jd, place) or (dob, tob, place)
# dob = date of birth as (year, month, day)
# tob = time of birth as (hour, minute, second) or decimal hours

try:
    from jhora.panchanga import drik
    
    # Get Julian Day
    # PyJHora may have its own JD calculator
    jd = drik.julian_day_number((year, month, day), (23, 26, 0))
    log("Julian Day", jd)
    
    # Planet positions
    planets = drik.planet_positions(jd, place)
    log("Planet Positions", planets)
    
    # Ascendant
    asc = drik.ascendant(jd, place)
    log("Ascendant", asc)
    
except Exception as e:
    log("BASIC POSITIONS", f"FAILED: {e}")

# --- Dashas ---
try:
    from jhora.horoscope.dhasa.graha import vimsottari
    vd = vimsottari.get_dhasa_bhukthi(jd, place)
    log("Vimshottari Dasha", vd)
except Exception as e:
    log("Vimshottari", f"FAILED: {e}")

# Try dashas we DON'T have
for dasha_name in ['buddhi_gathi', 'kaala', 'karaka', 'naisargika', 
                     'shastihayani', 'yoga_vimsottari', 'tithi_ashtottari',
                     'tithi_yogini', 'saptharishi_nakshathra']:
    try:
        mod = __import__(f'jhora.horoscope.dhasa.graha.{dasha_name}', fromlist=[dasha_name])
        result = mod.get_dhasa_bhukthi(jd, place)
        log(f"Dasha: {dasha_name}", result)
    except Exception as e:
        log(f"Dasha: {dasha_name}", f"FAILED: {e}")

# Try rasi dashas we DON'T have
for dasha_name in ['chakra', 'kendradhi_rasi', 'sthira', 'varnada', 
                     'yogardha', 'paryaaya', 'sandhya', 'tara_lagna',
                     'lagnamsaka']:
    try:
        mod = __import__(f'jhora.horoscope.dhasa.raasi.{dasha_name}', fromlist=[dasha_name])
        result = mod.get_dhasa_bhukthi(jd, place)
        log(f"Rasi Dasha: {dasha_name}", result)
    except Exception as e:
        log(f"Rasi Dasha: {dasha_name}", f"FAILED: {e}")

# --- Yogas ---
try:
    from jhora.horoscope.chart import yoga
    # Try to get all yogas — function name may vary
    # Check if there's a function like yoga_results or get_all_yogas
    import inspect
    yoga_funcs = [f for f in dir(yoga) if not f.startswith('_')]
    log("Yoga module functions (first 30)", yoga_funcs[:30])
    
    # Try calling a few specific yogas
    for yname in ['gajakesari_yoga', 'pancha_mahapurusha_yoga', 
                   'raja_yoga', 'dhana_yoga', 'saraswathi_yoga']:
        for suffix in ['', '_from_planet_positions']:
            fname = yname + suffix
            if hasattr(yoga, fname):
                try:
                    result = getattr(yoga, fname)(jd, place)
                    log(f"Yoga: {fname}", result)
                except:
                    pass
                break
except Exception as e:
    log("YOGAS", f"FAILED: {e}")

# --- Sphutas ---
try:
    from jhora.horoscope.chart import sphuta
    sphuta_funcs = [f for f in dir(sphuta) if not f.startswith('_')]
    log("Sphuta module functions", sphuta_funcs)
    
    for sp in ['tri_sphuta', 'chatur_sphuta', 'pancha_sphuta', 
               'prana_sphuta', 'deha_sphuta', 'mrityu_sphuta',
               'beeja_sphuta', 'kshetra_sphuta', 'yogi_sphuta',
               'avayogi']:
        if hasattr(sphuta, sp):
            try:
                result = getattr(sphuta, sp)(jd, place)
                log(f"Sphuta: {sp}", result)
            except Exception as e:
                log(f"Sphuta: {sp}", f"FAILED: {e}")
except Exception as e:
    log("SPHUTAS", f"FAILED: {e}")

# --- Compatibility (just check what functions exist) ---
try:
    from jhora.horoscope.match import compatibility
    comp_funcs = [f for f in dir(compatibility) if not f.startswith('_')]
    log("Compatibility functions", comp_funcs)
except Exception as e:
    log("COMPATIBILITY", f"FAILED: {e}")

# --- Doshas ---
try:
    from jhora.horoscope.chart import dosha
    dosha_funcs = [f for f in dir(dosha) if not f.startswith('_')]
    log("Dosha functions", dosha_funcs)
except Exception as e:
    log("DOSHAS", f"FAILED: {e}")

# --- Save everything ---
with open("pyjhora_nehru_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print(f"Done. Output saved to pyjhora_nehru_output.txt ({len(output)} lines)")
```

## STEP 4: Save and report

After running, give me:
1. Which imports succeeded vs failed
2. pyjhora_nehru_output.txt (the raw output)
3. Any errors or dependency issues

## RULES
- DO NOT modify anything in vedic_engine/
- DO NOT copy any PyJHora code into our project
- This is READ-ONLY exploration
- If PyJHora needs ephemeris files manually copied, note it but skip (we just want to see what functions return)
- If UI dependencies block install, skip them — we only need computation modules