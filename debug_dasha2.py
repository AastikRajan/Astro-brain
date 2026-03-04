"""Debug: understand the dasha date computation approach."""
from datetime import datetime, timedelta

birth = datetime(1889, 11, 14)
balance = 15.246450  # our balance for Mercury

# Method 1: timedelta with 365.25
end1 = birth + timedelta(days=balance * 365.25)
print(f"Method 1 (365.25 days/yr): {end1.strftime('%Y-%m-%d')}")

# Method 2: timedelta with 365.0
end2 = birth + timedelta(days=balance * 365.0)
print(f"Method 2 (365.0 days/yr):  {end2.strftime('%Y-%m-%d')}")

# Method 3: Calendar-based Y/M/D
years = int(balance)
rem = balance - years
months = int(rem * 12)
rem2 = rem * 12 - months
days = round(rem2 * 30)
print(f"Method 3 (Y/M/D): {years}y {months}m {days}d")
# Add calendar-wise:
try:
    from dateutil.relativedelta import relativedelta
    end3 = birth + relativedelta(years=years, months=months, days=days)
    print(f"  -> {end3.strftime('%Y-%m-%d')}")
except ImportError:
    print("  (dateutil not available)")

# Full period dates with timedelta vs calendar years
print("\n--- Full period comparison ---")
# Ketu 7 years from 1905-02-08
d = datetime(1905, 2, 8)
print(f"Ketu: timedelta = {(d + timedelta(days=7*365.25)).strftime('%Y-%m-%d')}, calendar = 1912-02-08")
# Venus 20 years from 1912-02-08
d = datetime(1912, 2, 8)
print(f"Venus: timedelta = {(d + timedelta(days=20*365.25)).strftime('%Y-%m-%d')}, calendar = 1932-02-08")

# Key insight: AstroSage uses calendar year addition for full periods
# So we should too. The balance period needs different handling.

# What year-to-days factor makes Mercury end on Feb 8?
target = datetime(1905, 2, 8)
target_days = (target - birth).days
factor = target_days / balance
print(f"\nTarget Feb 8: {target_days} days")
print(f"Required factor: {factor:.6f}")
print(f"365.00 gives: {(birth + timedelta(days=balance * 365.0)).strftime('%Y-%m-%d')}")
print(f"365.25 gives: {(birth + timedelta(days=balance * 365.25)).strftime('%Y-%m-%d')}")

# Check ref Moon balance
ref_balance = 15.232043
print(f"\nRef Moon balance: {ref_balance}")
print(f"365.25 gives: {(birth + timedelta(days=ref_balance * 365.25)).strftime('%Y-%m-%d')}")
