# -*- coding: utf-8 -*-
import sys, io, importlib, pkgutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Chart modules
import jhora.horoscope.chart as ch
print('=== CHART MODULES ===')
for importer, modname, ispkg in pkgutil.iter_modules(ch.__path__):
    full = f'jhora.horoscope.chart.{modname}'
    try:
        mod = importlib.import_module(full)
        funcs = [f for f in dir(mod) if not f.startswith('_') and callable(getattr(mod, f))]
        print(f'{modname}: {funcs[:20]}')
    except Exception as e:
        print(f'{modname}: FAILED - {e}')

# Other important modules
print('\n=== OTHER MODULES ===')
other_mods = [
    'jhora.horoscope.chart.ashtakavarga',
    'jhora.horoscope.chart.yoga',
    'jhora.horoscope.chart.strength',
    'jhora.horoscope.chart.raja_yoga',
    'jhora.horoscope.chart.house',
    'jhora.horoscope.chart.charts',
    'jhora.horoscope.chart.dosha',
    'jhora.horoscope.chart.sphuta',
    'jhora.panchanga.drik',
]

for mod_path in other_mods:
    try:
        mod = importlib.import_module(mod_path)
        funcs = [f for f in dir(mod) if not f.startswith('_') and callable(getattr(mod, f))]
        short = mod_path.split('.')[-1]
        print(f'{short}: {len(funcs)} funcs - {funcs[:15]}')
    except Exception as e:
        short = mod_path.split('.')[-1]
        print(f'{short}: FAILED - {e}')

# Check drik functions for panchanga-related
print('\n=== DRIK PANCHANGA FUNCTIONS ===')
from jhora.panchanga import drik
panch_funcs = [f for f in dir(drik) if not f.startswith('_') and callable(getattr(drik, f))]
for f in sorted(panch_funcs):
    print(f'  {f}')
