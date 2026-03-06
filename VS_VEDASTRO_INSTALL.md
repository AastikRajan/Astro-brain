# VedAstro.Python — Install, Test, Bridge
# New VS Code chat or same chat. Do steps IN ORDER.

---

## STEP 1: Install vedastro package

```
cd "C:\Users\aasti\Downloads\New folder (3)"
.venv\Scripts\pip.exe install vedastro
```

If it fails, check error and install any missing dependency.

## STEP 2: Read their README / docs

```python
# Check what's available
import vedastro
print(dir(vedastro))

# Check their demo file pattern
from vedastro import *
print(dir(Calculate))
```

Also check:
```python
# List all Calculate methods
methods = [m for m in dir(Calculate) if not m.startswith('_')]
print(f"Total methods: {len(methods)}")
for m in methods:
    print(f"  {m}")
```

## STEP 3: Test basic functionality

Their API pattern from their demo:
```python
import json
from vedastro import *

# Set free API key
Calculate.SetAPIKey('FreeAPIUser')

# Set birth location
geolocation = GeoLocation("Allahabad, India", 81.8463, 25.4358)

# Birth time (day/month/year format with timezone)
birth_time = Time("23:26 14/11/1889 +05:30", geolocation)

# Test 1: Planet data
try:
    sun_data = Calculate.AllPlanetData(PlanetName.Sun, birth_time)
    print("Sun data OK:", json.dumps(sun_data, indent=2, default=str)[:500])
except Exception as e:
    print(f"Sun data FAIL: {e}")

# Test 2: House data
try:
    h1_data = Calculate.AllHouseData(HouseName.House1, birth_time)
    print("House1 data OK:", json.dumps(h1_data, indent=2, default=str)[:500])
except Exception as e:
    print(f"House1 data FAIL: {e}")

# Test 3: Horoscope Predictions (THIS IS THE KEY ONE)
try:
    predictions = Calculate.HoroscopePredictions(birth_time, "Empty")
    print("Predictions OK:", json.dumps(predictions, indent=2, default=str)[:1000])
except Exception as e:
    print(f"Predictions FAIL: {e}")
```

Save output to `vedastro_test_output.txt`.

**IMPORTANT:** This library makes HTTP calls to vedastro.org. You need internet.
If any call fails with timeout/connection error, that's an API issue not our code.

## STEP 4: Discover ALL available methods

```python
import json, inspect
from vedastro import *

Calculate.SetAPIKey('FreeAPIUser')
geolocation = GeoLocation("Allahabad, India", 81.8463, 25.4358)
birth_time = Time("23:26 14/11/1889 +05:30", geolocation)

output = []

# Get all Calculate methods
all_methods = [m for m in dir(Calculate) if not m.startswith('_') and callable(getattr(Calculate, m))]
output.append(f"Total Calculate methods: {len(all_methods)}")
for m in all_methods:
    output.append(f"  {m}")

# Get all enum values
output.append(f"\nPlanetName values: {[p for p in dir(PlanetName) if not p.startswith('_')]}")
output.append(f"HouseName values: {[h for h in dir(HouseName) if not h.startswith('_')]}")
output.append(f"ZodiacName values: {[z for z in dir(ZodiacName) if not z.startswith('_')]}")

# Try each major method category
test_calls = {
    'AllPlanetData_Sun': lambda: Calculate.AllPlanetData(PlanetName.Sun, birth_time),
    'AllPlanetData_Moon': lambda: Calculate.AllPlanetData(PlanetName.Moon, birth_time),
    'AllPlanetData_Jupiter': lambda: Calculate.AllPlanetData(PlanetName.Jupiter, birth_time),
    'AllHouseData_H1': lambda: Calculate.AllHouseData(HouseName.House1, birth_time),
    'AllHouseData_H10': lambda: Calculate.AllHouseData(HouseName.House10, birth_time),
    'HoroscopePredictions': lambda: Calculate.HoroscopePredictions(birth_time, "Empty"),
}

# Check if these methods exist and try them
for name, call in test_calls.items():
    try:
        result = call()
        if isinstance(result, (dict, list)):
            output.append(f"\n[OK] {name}: {len(result)} items")
            output.append(json.dumps(result, indent=2, default=str)[:800])
        else:
            output.append(f"\n[OK] {name}: {str(result)[:500]}")
    except Exception as e:
        output.append(f"\n[FAIL] {name}: {e}")

# Also check for these if they exist
extra_methods = [
    'MatchReport', 'Numerology', 'AllZodiacSignData',
    'PlanetZodiacSign', 'PlanetConstellation', 'HousePlanetIsIn',
    'PlanetShadpilaStrength', 'DasaForLife', 'CurrentDasa',
]
for m in extra_methods:
    if hasattr(Calculate, m):
        output.append(f"\n[EXISTS] Calculate.{m}")
    else:
        output.append(f"\n[MISSING] Calculate.{m}")

with open("vedastro_discovery.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print(f"Done. Saved to vedastro_discovery.txt ({len(output)} lines)")
```

## STEP 5: Download their EventDataList.xml

This is their prediction rules database. Download it from their GitHub:

```python
import urllib.request, os

# EventDataList.xml contains all their prediction rules
url = "https://raw.githubusercontent.com/VedAstro/VedAstro/master/Library/Data/EventDataList.xml"
dest = r"C:\Users\aasti\Downloads\New folder (3)\libs\vedastro_data\EventDataList.xml"
os.makedirs(os.path.dirname(dest), exist_ok=True)

try:
    urllib.request.urlretrieve(url, dest)
    size = os.path.getsize(dest)
    print(f"Downloaded EventDataList.xml: {size} bytes")
    
    # Quick peek at structure
    with open(dest, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"Total chars: {len(content)}")
    print(f"First 1000 chars:\n{content[:1000]}")
    
    # Count events
    import re
    events = re.findall(r'<Name>(.*?)</Name>', content)
    print(f"\nTotal events/predictions defined: {len(events)}")
    print("First 20 events:")
    for e in events[:20]:
        print(f"  {e}")
except Exception as e:
    print(f"Download FAIL: {e}")
    print("Try manually downloading from:")
    print("  https://github.com/VedAstro/VedAstro/tree/master/Library/Data")
    print("  Look for EventDataList.xml")
```

## STEP 6: Check HuggingFace datasets

```python
import urllib.request

# Check what datasets they have
url = "https://huggingface.co/api/models?author=vedastro-org"
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        import json
        data = json.loads(response.read())
        print(f"VedAstro HuggingFace models/datasets: {len(data)}")
        for item in data:
            print(f"  {item.get('id', '?')} — {item.get('description', '')[:100]}")
except Exception as e:
    print(f"HuggingFace check FAIL: {e}")
    print("Manually check: https://huggingface.co/vedastro-org")
```

## STEP 7: Report back

Give me:
1. Did `pip install vedastro` succeed?
2. How many Calculate methods are available?
3. Did HoroscopePredictions work? What does it return? (structure, not full data)
4. Did EventDataList.xml download? How many events are defined?
5. What datasets are on HuggingFace?
6. vedastro_discovery.txt (the full output)

DO NOT build the bridge yet. Just report what's available. I'll design the bridge after seeing the output.