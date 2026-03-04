"""Quick debug script for dasha balance computation."""
from datetime import datetime, timedelta

NAKSHATRA_SPAN = 360.0 / 27.0  # 13.33333...

def balance_calc(moon_lon):
    nak_idx = min(int(moon_lon / NAKSHATRA_SPAN), 26)
    pos_in_nak = moon_lon % NAKSHATRA_SPAN
    remaining_arc = NAKSHATRA_SPAN - pos_in_nak
    fraction = remaining_arc / NAKSHATRA_SPAN
    balance = 17.0 * fraction  # Mercury = 17 years
    return nak_idx, pos_in_nak, remaining_arc, fraction, balance

birth = datetime(1889, 11, 14)
target = datetime(1905, 2, 8)
target_days = (target - birth).days

# Our Moon longitude
our_moon = 108.042
n,p,r,f,b = balance_calc(our_moon)
fmt = "%Y-%m-%d"
print(f"Our Moon {our_moon}: nak={n}, pos={p:.6f}, rem={r:.6f}, frac={f:.6f}, balance={b:.6f}y")
print(f"  End (365.25):   {(birth + timedelta(days=b * 365.25)).strftime(fmt)}")
print(f"  End (365.2422): {(birth + timedelta(days=b * 365.2422)).strftime(fmt)}")
print(f"  End (365.0):    {(birth + timedelta(days=b * 365.0)).strftime(fmt)}")

# Reference Moon longitude
ref_moon = 108.0533
n,p,r,f,b = balance_calc(ref_moon)
print(f"\nRef Moon {ref_moon}: nak={n}, pos={p:.6f}, rem={r:.6f}, frac={f:.6f}, balance={b:.6f}y")
print(f"  End (365.25):   {(birth + timedelta(days=b * 365.25)).strftime(fmt)}")
print(f"  End (365.2422): {(birth + timedelta(days=b * 365.2422)).strftime(fmt)}")
print(f"  End (365.0):    {(birth + timedelta(days=b * 365.0)).strftime(fmt)}")

print(f"\nTarget 1905-02-08: {target_days} days")
n,p,r,f,b_our = balance_calc(our_moon)
print(f"Required year-length for our Moon: {target_days / b_our:.4f}")
n,p,r,f,b_ref = balance_calc(ref_moon)
print(f"Required year-length for ref Moon: {target_days / b_ref:.4f}")

# Also check: what if we use 365.25 per full dasha year but different for balance?
# Check full-year periods: 7 years (Ketu) * 365.25 = 2556.75 days
# 1905-02-08 + 2556.75 days = ?
print(f"\n--- Full dasha year checks ---")
ketu_end_ref = datetime(1912, 2, 8)
ketu_days = (ketu_end_ref - datetime(1905, 2, 8)).days
print(f"Ketu 7yr reference: {ketu_days} days, year={ketu_days/7.0:.4f}")
venus_end_ref = datetime(1932, 2, 8)
venus_days = (venus_end_ref - datetime(1912, 2, 8)).days
print(f"Venus 20yr reference: {venus_days} days, year={venus_days/20.0:.4f}")
sun_end_ref = datetime(1938, 2, 8)
sun_days = (sun_end_ref - datetime(1932, 2, 8)).days
print(f"Sun 6yr reference: {sun_days} days, year={sun_days/6.0:.4f}")
