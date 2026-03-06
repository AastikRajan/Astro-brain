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
