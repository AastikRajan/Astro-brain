"""
Validation Test — Jawaharlal Nehru's chart with known life events.
Generates content41_validation.txt with full engine output for every event.
"""
import sys
import os
import textwrap
from datetime import datetime, timedelta

# ── UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from vedic_engine.data.loader import build_chart_swe, load_from_dict
from vedic_engine.prediction.engine import PredictionEngine
from vedic_engine.config import SIGN_LORDS, NAKSHATRA_NAMES, VIMSHOTTARI_SEQUENCE

SIGN_NAMES = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

# ═══════════════════════════════════════════════════════════════════════════════
# NEHRU BIRTH DATA
# ═══════════════════════════════════════════════════════════════════════════════
NEHRU_BIRTH = {
    "name": "Jawaharlal Nehru",
    "date": "1889-11-14",
    "time": "23:11:00",       # 11:11 PM IST
    "place": "Allahabad, India",
    "lat": 25.4358,
    "lon": 81.8463,
    "tz": 5.5,                # IST
}

# Known life events with exact dates and expected domain
KNOWN_EVENTS = [
    {
        "label": "Daughter (Indira) born",
        "date": "1917-11-19",
        "domain": "marriage",   # 5th house: children
        "expected": "HIGH activation of 5th house (children/progeny)",
    },
    {
        "label": "First imprisonment (civil disobedience)",
        "date": "1921-12-06",
        "domain": "career",
        "expected": "Saturn/Rahu activation, 12th house (imprisonment)",
    },
    {
        "label": "Father Motilal Nehru's death",
        "date": "1931-02-06",
        "domain": "health",     # family loss
        "expected": "Maraka / 4th house (mother/father) affliction, dasha of 2/7 lord",
    },
    {
        "label": "Wife Kamala Nehru's death",
        "date": "1936-02-28",
        "domain": "marriage",
        "expected": "7th lord / Venus affliction, maraka dasha",
    },
    {
        "label": "Became Prime Minister of India",
        "date": "1947-08-15",
        "domain": "career",
        "expected": "PEAK career — 10th house, Raja Yoga activation, Double Transit on 10H",
    },
    {
        "label": "Re-elected PM (first general election)",
        "date": "1952-01-01",
        "domain": "career",
        "expected": "Continued career dominance",
    },
    {
        "label": "Re-elected PM (second general election)",
        "date": "1957-04-01",
        "domain": "career",
        "expected": "Continued career dominance",
    },
    {
        "label": "Indo-China War disaster",
        "date": "1962-10-20",
        "domain": "career",
        "expected": "Career CRISIS — Rahu dasha, 12th house loss, foreign enemy",
    },
    {
        "label": "Re-elected PM (third general election)",
        "date": "1962-04-01",
        "domain": "career",
        "expected": "Career activation despite coming crisis",
    },
    {
        "label": "Death",
        "date": "1964-05-27",
        "domain": "health",
        "expected": "Maraka activation, 8th house transit, health collapse",
    },
]


def banner(title, width=80):
    line = "=" * width
    pad = (width - len(title) - 2) // 2
    inner = "=" * pad + f" {title} " + "=" * pad
    if len(inner) < width:
        inner += "="
    return f"\n{line}\n{inner}\n{line}"


def section(title):
    return f"\n{'-'*80}\n  {title}\n{'-'*80}"


def fmt_sign(idx):
    return SIGN_NAMES[idx % 12]


def safe_predict(engine, chart, domain, on_date, static):
    """Run predict() with error handling."""
    try:
        return engine.predict(chart, domain, on_date, static)
    except Exception as e:
        return {"error": str(e), "domain": domain}


def get_dasha_info(dynamic):
    """Extract dasha info from dynamic analysis."""
    vim = dynamic.get("vimshottari", {}).get("active", {})
    md, ad, pd_str = "?", "?", "?"
    if isinstance(vim, dict):
        md = vim.get("mahadasha", "?")
        ad = vim.get("antardasha", "?")
        pd_str = vim.get("pratyantardasha", "?")
    elif isinstance(vim, list):
        if len(vim) > 0:
            md = vim[0].get("planet", "?")
        if len(vim) > 1:
            ad = vim[1].get("planet", "?")
        if len(vim) > 2:
            pd_str = vim[2].get("planet", "?")
    return md, ad, pd_str


def get_yogini_info(dynamic):
    """Extract yogini dasha info."""
    yog = dynamic.get("yogini", {}).get("active", {})
    if isinstance(yog, dict):
        return f"{yog.get('major_yogini', '?')} ({yog.get('major_planet', '?')})"
    return "?"


def get_chara_info(dynamic):
    """Extract chara dasha info."""
    chara = dynamic.get("chara_dasha", {})
    if isinstance(chara, dict) and "active" in chara:
        active = chara.get("active", {})
        if isinstance(active, dict):
            md_sign = active.get("mahadasha", "?")
            antar = active.get("antardasha", {})
            ad_sign = antar.get("sign", "?") if isinstance(antar, dict) else "?"
            return f"{md_sign} / {ad_sign}"
    return "?"


def get_transit_positions(dynamic):
    """Get transit positions for key planets."""
    tp = dynamic.get("transit_positions", {})
    result = {}
    for planet in ["SATURN", "JUPITER", "RAHU", "KETU", "SUN", "MOON", "MARS"]:
        lon = tp.get(planet, 0.0)
        sign_idx = int(lon / 30) % 12
        deg_in_sign = lon % 30
        result[planet] = {
            "lon": lon,
            "sign": fmt_sign(sign_idx),
            "sign_idx": sign_idx,
            "deg": deg_in_sign,
        }
    return result


def check_double_transit(transit_info, lagna_sign, target_houses):
    """Check if Saturn AND Jupiter are both activating target houses."""
    sat_house = ((transit_info.get("SATURN", {}).get("sign_idx", 0) - lagna_sign) % 12) + 1
    jup_house = ((transit_info.get("JUPITER", {}).get("sign_idx", 0) - lagna_sign) % 12) + 1

    # Include aspect houses too (Saturn: 3,7,10 from self; Jupiter: 5,7,9 from self)
    sat_activated = {sat_house}
    for asp in [3, 7, 10]:
        sat_activated.add(((sat_house - 1 + asp) % 12) + 1)

    jup_activated = {jup_house}
    for asp in [5, 7, 9]:
        jup_activated.add(((jup_house - 1 + asp) % 12) + 1)

    sat_hits = sat_activated & set(target_houses)
    jup_hits = jup_activated & set(target_houses)

    if sat_hits and jup_hits:
        return f"YES — Saturn activates H{sat_hits}, Jupiter activates H{jup_hits}"
    elif sat_hits:
        return f"PARTIAL — Only Saturn activates H{sat_hits} (Jupiter missing)"
    elif jup_hits:
        return f"PARTIAL — Only Jupiter activates H{jup_hits} (Saturn missing)"
    else:
        return f"NO — Neither Saturn (H{sat_house}) nor Jupiter (H{jup_house}) on target houses {target_houses}"


def compute_bcp_house(birth_date, event_date):
    """BCP Active House = ((age-1) % 12) + 1"""
    birth_dt = datetime.strptime(birth_date, "%Y-%m-%d")
    event_dt = datetime.strptime(event_date, "%Y-%m-%d")
    age = event_dt.year - birth_dt.year
    if (event_dt.month, event_dt.day) < (birth_dt.month, birth_dt.day):
        age -= 1
    bcp_house = ((age - 1) % 12) + 1
    return age, bcp_house


def compute_profection(birth_date, event_date, lagna_sign):
    """Annual Profection: which house/sign activated by age."""
    birth_dt = datetime.strptime(birth_date, "%Y-%m-%d")
    event_dt = datetime.strptime(event_date, "%Y-%m-%d")
    age = event_dt.year - birth_dt.year
    if (event_dt.month, event_dt.day) < (birth_dt.month, birth_dt.day):
        age -= 1
    profection_house = (age % 12) + 1
    profection_sign = (lagna_sign + age) % 12
    return age, profection_house, fmt_sign(profection_sign)


def print_full_prediction(report, label=""):
    """Print detailed prediction output."""
    domain = report.get("domain", "?").upper()
    conf = report.get("confidence", {})
    level = conf.get("level", "?")
    score = conf.get("overall_boosted", conf.get("overall", 0))

    if label:
        print(f"\n  --- {label} ---")
    print(f"  DOMAIN: {domain} | Confidence: {level} ({score:.1%})")

    # Components
    comp = conf.get("components", {})
    if comp:
        print(f"  Components:")
        for k, v in comp.items():
            print(f"    {k:<30} {v:.3f}")

    # Bayesian
    bayes = conf.get("bayesian", {})
    if bayes and "posterior_mean" in bayes:
        pm = bayes.get("posterior_mean", 0)
        cl = bayes.get("credible_low", 0)
        ch = bayes.get("credible_high", 0)
        cert = bayes.get("certainty_label", "?")
        print(f"  Bayesian: p={pm:.1%}, CI=[{cl:.1%}-{ch:.1%}], {cert}")

    # Fuzzy
    fuzzy = conf.get("fuzzy", {})
    if fuzzy and "fuzzy_confidence" in fuzzy:
        fc = fuzzy.get("fuzzy_confidence", 0)
        meth = fuzzy.get("method", "?")
        print(f"  Fuzzy: {fc:.1%} ({meth})")

    fi = conf.get("fuzzy_inputs", {})
    if fi:
        print(f"    timing={fi.get('timing',0):.2f}  transit={fi.get('transit',0):.2f}  structural={fi.get('structural',0):.2f}")

    # Promise
    promise = report.get("promise", {})
    if promise:
        p_pct = promise.get("promise_pct", promise.get("promise_percentage", -1))
        p_level = promise.get("promise_level", "?")
        pillars = promise.get("pillars", {})
        print(f"  Promise: {p_pct}% [{p_level}]")
        if pillars:
            for pn, pv in pillars.items():
                print(f"    {pn}: {pv}")

    # Dasha diagnostic
    dd = report.get("dasha_diagnostic", {})
    if dd and "overall_quality" in dd:
        print(f"  Dasha Diagnostic: {dd.get('overall_quality', '?')} | geometry={dd.get('md_ad_geometry','?')}")
        if dd.get("summary"):
            print(f"    {dd['summary'][:120]}")

    # Multi-dasha consensus
    mdc = report.get("multi_dasha_consensus", {})
    if mdc and "consensus_level" in mdc:
        print(f"  Dasha Consensus: {mdc.get('consensus_level', '?')} (x{mdc.get('confidence_multiplier',1):.2f})")
        if mdc.get("detail"):
            print(f"    {mdc['detail'][:120]}")

    # Argala
    argala_mod = conf.get("argala_mod")
    if argala_mod is not None:
        print(f"  Argala Mod: {argala_mod:+.1%}")

    # Aspect transit
    asp_mod = conf.get("aspect_transit_mod")
    if asp_mod is not None:
        print(f"  Aspect Transit Mod: {asp_mod:+.1%}")

    # Progression
    prog = conf.get("progression_boost")
    if prog is not None and prog != 0:
        print(f"  Progression Boost: {prog:+.2%}")

    # Vimshopak
    vm = conf.get("vimshopak_mod")
    if vm is not None:
        print(f"  Vimshopak Mod: {vm:+.1%}")

    # Badhaka
    bad = report.get("badhaka", {})
    if bad and "friction_label" in bad:
        print(f"  Badhaka: {bad.get('friction_label','?')} ({bad.get('friction_multiplier',1):.2f}x)")

    # Error
    if "error" in report:
        print(f"  [ERROR] {report['error']}")

    # Prediction text (first 3 lines)
    pred = report.get("prediction", "")
    if pred:
        lines = pred.strip().split("\n")
        for line in lines[:3]:
            print(f"  >> {line}")

    return score


def main():
    out_path = os.path.join(os.path.dirname(__file__), "content41_validation.txt")

    # Redirect stdout to both console and file
    class Tee:
        def __init__(self, *files):
            self.files = files
        def write(self, data):
            for f in self.files:
                f.write(data)
                f.flush()
        def flush(self):
            for f in self.files:
                f.flush()

    outfile = open(out_path, "w", encoding="utf-8", errors="replace")
    old_stdout = sys.stdout
    sys.stdout = Tee(sys.stdout, outfile)

    try:
        _run_validation()
    finally:
        sys.stdout = old_stdout
        outfile.close()
        print(f"\n[Output saved to {out_path}]")


def _run_validation():
    print(banner("VALIDATION TEST: Jawaharlal Nehru"))
    print(f"  Birth: {NEHRU_BIRTH['date']} at {NEHRU_BIRTH['time']} IST")
    print(f"  Place: {NEHRU_BIRTH['place']} ({NEHRU_BIRTH['lat']}N, {NEHRU_BIRTH['lon']}E)")
    print(f"  Events to validate: {len(KNOWN_EVENTS)}")
    print(f"  Run date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ═══════════════════════════════════════════════════════════════════
    # BUILD CHART
    # ═══════════════════════════════════════════════════════════════════
    print(banner("SECTION 1: CHART COMPUTATION"))
    print("  Building chart via Swiss Ephemeris...")

    chart = build_chart_swe(
        name=NEHRU_BIRTH["name"],
        date_str=NEHRU_BIRTH["date"],
        time_str=NEHRU_BIRTH["time"],
        place=NEHRU_BIRTH["place"],
        latitude=NEHRU_BIRTH["lat"],
        longitude=NEHRU_BIRTH["lon"],
        tz_offset=NEHRU_BIRTH["tz"],
    )

    engine = PredictionEngine()

    print("  Computing static analysis...")
    static = engine.analyze_static(chart)
    print("  Static analysis complete.")

    # ── Meta info
    meta = static.get("meta", {})
    lagna_sign = meta.get("lagna_sign", 0)
    moon_sign = meta.get("moon_sign", 0)
    moon_lon = meta.get("moon_lon", 0)

    lagna_deg = meta.get('lagna_degree', chart.lagna_degree % 30)
    print(f"\n  Lagna (Ascendant): {fmt_sign(lagna_sign)} ({lagna_deg:.2f}°)")
    print(f"  Moon Sign: {fmt_sign(moon_sign)} (longitude: {moon_lon:.2f}°)")
    moon_nak_idx = int(moon_lon / (360/27)) % 27
    print(f"  Moon Nakshatra: {NAKSHATRA_NAMES[moon_nak_idx]} (index {moon_nak_idx})")

    # ── Planet Positions
    print(section("PLANET POSITIONS"))
    chart_raw = static.get("chart_raw", {})
    lons = chart_raw.get("planet_lons", {})
    signs = chart_raw.get("planet_signs", {})
    houses = chart_raw.get("planet_houses", {})
    retros = chart_raw.get("retrogrades", {})

    planets_list = ["SUN","MOON","MARS","MERCURY","JUPITER","VENUS","SATURN","RAHU","KETU"]
    for planet in planets_list:
        lon = lons.get(planet, 0)
        sgn = signs.get(planet, 0)
        hse = houses.get(planet, "?")
        retro = " [R]" if retros.get(planet) else ""
        nak_idx = int(lon / (360/27)) % 27
        deg_in_sign = lon % 30
        print(f"  {planet:<10} {lon:>8.3f}°  {fmt_sign(sgn):<13} H{hse:<3} "
              f"Nak: {NAKSHATRA_NAMES[nak_idx]:<14} {deg_in_sign:.2f}° in sign{retro}")

    # ── House Lords
    print(section("HOUSE LORDS"))
    hl = static.get("house_lords", {})
    # Also build from chart.houses as fallback
    hl_full = {}
    for hc in chart.houses:
        hl_full[hc.house_num] = hc.lord
    for h in range(1, 13):
        lord = hl.get(h, hl.get(str(h), hl_full.get(h, "?")))
        h_sign = (lagna_sign + h - 1) % 12
        print(f"  H{h:<3} {fmt_sign(h_sign):<13} Lord: {lord}")

    # ── Vimshottari Dasha Periods
    print(section("VIMSHOTTARI DASHA PERIODS"))
    if chart.vimshottari:
        for md in chart.vimshottari:
            start = md.start_date.strftime("%Y-%m-%d") if md.start_date else "?"
            end = md.end_date.strftime("%Y-%m-%d") if md.end_date else "?"
            print(f"  {md.planet:<10} {start} to {end}  ({md.duration_years:.1f} yrs)")
            for ad in (md.sub_periods or [])[:20]:
                ad_start = ad.start_date.strftime("%Y-%m-%d") if ad.start_date else "?"
                ad_end = ad.end_date.strftime("%Y-%m-%d") if ad.end_date else "?"
                print(f"    └─ {ad.planet:<8} {ad_start} to {ad_end}  ({ad.duration_years:.2f} yrs)")
    else:
        print("  [Dasha periods computed dynamically — see per-event analysis below]")

    # ── Yogas
    print(section("ACTIVE YOGAS"))
    yogas = static.get("yogas", [])
    if yogas:
        for i, y in enumerate(yogas):
            if isinstance(y, dict):
                name = y.get("name", "?")
                grade = y.get("grade", "?")
                dom = y.get("domain", "?")
                desc = y.get("description", "")[:80]
                print(f"  {i+1:>3}. {name:<30} Grade: {grade:<8} Domain: {dom}")
                if desc:
                    print(f"       {desc}")
            else:
                name = getattr(y, "name", str(y))
                grade = getattr(y, "grade", "?")
                dom = getattr(y, "domain", "?")
                print(f"  {i+1:>3}. {name:<30} Grade: {grade:<8} Domain: {dom}")
    else:
        print("  No yogas detected (or stored in different format)")

    # ── Shadbala
    print(section("SHADBALA STRENGTH RATIOS"))
    sha = static.get("shadbala_ratios", {})
    if sha:
        for planet, ratio in sorted(sha.items(), key=lambda x: -x[1]):
            bar = "█" * int(ratio * 10)
            status = "STRONG" if ratio >= 1.0 else "WEAK"
            print(f"  {planet:<10} {ratio:>5.2f}x  {bar:<15} {status}")
    else:
        print("  [Shadbala not computed or unavailable]")

    # ── Ashtakavarga
    print(section("SARVASHTAKVARGA"))
    av = static.get("ashtakvarga", {})
    sav = None
    if isinstance(av, dict):
        sav = av.get("sarvashtakvarga") or av.get("sarva", [])
    if sav:
        total = sum(sav) if sav else 0
        print(f"  Total: {total}/337")
        signs_row = "  " + "  ".join(f"{SIGN_NAMES[i][:3]:>5}" for i in range(12))
        scores_row = "  " + "  ".join(f"{s:>5}" for s in sav)
        print(signs_row)
        print(scores_row)
    else:
        print("  [SAV not available]")

    # ── Doshas
    print(section("DOSHA ANALYSIS"))
    computed = static.get("computed", {})
    doshas_to_check = [
        ("kala_sarpa", "Kala Sarpa Yoga"),
        ("manglik", "Manglik Dosha"),
        ("pitru_dosha", "Pitru Dosha"),
        ("combustion", "Combustion"),
        ("gandanta", "Gandanta"),
    ]
    for key, label in doshas_to_check:
        val = computed.get(key)
        if val:
            if isinstance(val, dict):
                present = val.get("present", val.get("active", val.get("detected", False)))
                details = val.get("details", val.get("type", val.get("summary", "")))
                if isinstance(details, list):
                    details = "; ".join(str(d) for d in details[:3])
                print(f"  {label}: {'PRESENT' if present else 'Absent'} — {str(details)[:100]}")
            elif isinstance(val, list):
                print(f"  {label}: {len(val)} item(s) detected")
                for item in val[:3]:
                    print(f"    {str(item)[:100]}")
            else:
                print(f"  {label}: {str(val)[:100]}")
        else:
            print(f"  {label}: Not detected / not computed")

    # ── Longevity
    print(section("LONGEVITY"))
    longevity = computed.get("longevity", static.get("longevity", {}))
    if isinstance(longevity, dict):
        for k, v in longevity.items():
            print(f"  {k}: {v}")
    else:
        print(f"  {longevity}")

    # ── Jaimini Chara Karakas
    print(section("JAIMINI CHARA KARAKAS"))
    kr = static.get("karakas", {})
    karaka_list = []
    if isinstance(kr, dict):
        karaka_list = kr.get("list", [])
    elif isinstance(kr, list):
        karaka_list = kr
    if karaka_list:
        for k in karaka_list:
            if isinstance(k, dict):
                role = k.get("role", "?")
                rname = k.get("role_name", "?")
                planet = k.get("planet", "?")
                deg = k.get("degree", 0.0)
                print(f"  {role:<5} {rname:<20} {planet:<10} {deg:.2f}°")
    else:
        print("  [Karakas not available in expected format]")

    # ── Functional Analysis
    print(section("FUNCTIONAL ANALYSIS"))
    fa = static.get("functional", {})
    if isinstance(fa, dict) and "classifications" in fa:
        yks = fa.get("yogakarakas", [])
        fbs = fa.get("functional_benefics", [])
        fms = fa.get("functional_malefics", [])
        mar = fa.get("marakas", [])
        bad = fa.get("badhaka", "")
        print(f"  Lagna: {fa.get('lagna_name', '?')}")
        print(f"  Yogakaraka(s): {', '.join(yks) or 'None'}")
        print(f"  Functional Benefics: {', '.join(fbs) or 'None'}")
        print(f"  Functional Malefics: {', '.join(fms) or 'None'}")
        print(f"  Marakas (H2+H7 lords): {', '.join(mar) or 'None'}")
        print(f"  Badhaka: {bad or 'None'}")

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 2: EVENT-BY-EVENT VALIDATION
    # ═══════════════════════════════════════════════════════════════════
    print(banner("SECTION 2: EVENT-BY-EVENT VALIDATION"))

    event_results = []  # Store (event_label, match_result, score) for summary

    for evt in KNOWN_EVENTS:
        evt_date = datetime.strptime(evt["date"], "%Y-%m-%d")
        evt_domain = evt["domain"]

        print(section(f"EVENT: {evt['label']} — {evt['date']}"))
        print(f"  Expected: {evt['expected']}")

        # Compute dynamic analysis for event date
        try:
            dynamic = engine.analyze_dynamic(chart, static, evt_date)
            dyn_error = False
        except Exception as e:
            print(f"  [ERROR computing dynamic analysis: {e}]")
            dynamic = {}
            dyn_error = True

        # Vimshottari Dasha
        md, ad, pd_str = get_dasha_info(dynamic) if not dyn_error else ("?", "?", "?")
        print(f"\n  VIMSHOTTARI DASHA: {md} / {ad} / {pd_str}")

        # Yogini Dasha
        yogi = get_yogini_info(dynamic) if not dyn_error else "?"
        print(f"  YOGINI DASHA: {yogi}")

        # Chara Dasha
        chara = get_chara_info(dynamic) if not dyn_error else "?"
        print(f"  CHARA DASHA: {chara}")

        # Transit Planets
        if not dyn_error:
            transit_info = get_transit_positions(dynamic)
            print(f"\n  TRANSIT PLANETS:")
            for tp_name in ["SATURN", "JUPITER", "RAHU", "MARS"]:
                tp_data = transit_info.get(tp_name, {})
                h_from_lagna = ((tp_data.get("sign_idx", 0) - lagna_sign) % 12) + 1
                h_from_moon = ((tp_data.get("sign_idx", 0) - moon_sign) % 12) + 1
                print(f"    {tp_name:<10} {tp_data.get('sign', '?'):<13} "
                      f"{tp_data.get('deg', 0):.1f}°  H{h_from_lagna} from Lagna  H{h_from_moon} from Moon")

            # Double Transit check
            # Determine target houses based on domain
            domain_target_houses = {
                "career": [1, 10, 9, 11],
                "finance": [2, 11, 5, 9],
                "marriage": [7, 2, 5, 11],
                "health": [1, 6, 8],
            }
            target_h = domain_target_houses.get(evt_domain, [1, 10])
            dt_result = check_double_transit(transit_info, lagna_sign, target_h)
            print(f"\n  DOUBLE TRANSIT (on houses {target_h}): {dt_result}")
        else:
            transit_info = {}
            print(f"  [Transit data unavailable for this date]")

        # BCP Active House
        age, bcp_house = compute_bcp_house(NEHRU_BIRTH["date"], evt["date"])
        print(f"  BCP ACTIVE HOUSE: H{bcp_house} (age {age})")

        # Annual Profection
        _, prof_house, prof_sign = compute_profection(NEHRU_BIRTH["date"], evt["date"], lagna_sign)
        print(f"  ANNUAL PROFECTION: H{prof_house} ({prof_sign})")

        # Relevant Yogas
        domain_yoga_keywords = {
            "career": ["raja", "career", "power", "authority", "government", "mahapurusha",
                       "amala", "budhaditya", "adhipati", "10", "fame"],
            "finance": ["dhana", "wealth", "lakshmi", "fortune", "money", "finance"],
            "marriage": ["marriage", "7th", "venus", "spouse", "parivartana", "kalatra"],
            "health": ["health", "longevity", "arishta", "maraka", "death", "disease", "8th"],
        }
        keywords = domain_yoga_keywords.get(evt_domain, [])
        relevant_yogas = []
        for y in yogas:
            y_name = (y.get("name", "") if isinstance(y, dict) else getattr(y, "name", "")).lower()
            y_dom = (y.get("domain", "") if isinstance(y, dict) else getattr(y, "domain", "")).lower()
            y_desc = (y.get("description", "") if isinstance(y, dict) else getattr(y, "description", "")).lower()
            combined = f"{y_name} {y_dom} {y_desc}"
            if any(kw in combined for kw in keywords):
                name = y.get("name", "") if isinstance(y, dict) else getattr(y, "name", "")
                relevant_yogas.append(name)
        print(f"  RELEVANT YOGAS: {', '.join(relevant_yogas[:8]) or 'None matching domain keywords'}")

        # Ashtakavarga - sign where event house lord sits
        if sav:
            evt_house_map = {"career": 10, "finance": 2, "marriage": 7, "health": 1}
            evt_house = evt_house_map.get(evt_domain, 1)
            evt_sign = (lagna_sign + evt_house - 1) % 12
            lord = hl.get(str(evt_house), hl.get(evt_house, "?"))
            lord_sign = signs.get(lord, 0) if isinstance(lord, str) else 0
            bav_score = sav[lord_sign] if lord_sign < len(sav) else "?"
            print(f"  ASHTAKAVARGA: H{evt_house} lord ({lord}) in {fmt_sign(lord_sign)}, SAV={bav_score}")

        # Engine Prediction
        print(f"\n  ENGINE PREDICTION ({evt_domain.upper()} on {evt['date']}):")
        report = safe_predict(engine, chart, evt_domain, evt_date, static)
        score = print_full_prediction(report)

        # Also run all 4 domains briefly
        print(f"\n  ALL DOMAINS BRIEF ({evt['date']}):")
        for dom in ["career", "finance", "marriage", "health"]:
            r = safe_predict(engine, chart, dom, evt_date, static)
            c = r.get("confidence", {})
            s = c.get("overall_boosted", c.get("overall", 0))
            print(f"    {dom.upper():<10} {s:.1%}")

        # Determine match
        if score >= 0.45:
            match = "YES — Engine shows high activation"
        elif score >= 0.30:
            match = "PARTIAL — Engine shows moderate activation"
        else:
            match = "NO — Engine shows low activation"

        # For events where we expect LOW confidence (e.g., death = health crisis),
        # a low score might actually be correct (health domain should show risk)
        print(f"\n  MATCH: {match}")
        event_results.append((evt["label"], match, score, evt_domain))

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 3: DOMAIN PREDICTIONS ON KEY DATES
    # ═══════════════════════════════════════════════════════════════════
    print(banner("SECTION 3: FULL DOMAIN PREDICTIONS ON KEY DATES"))

    key_dates = [
        ("1947-08-15", "Became PM of India"),
        ("1962-10-20", "China War"),
        ("1964-05-27", "Death"),
        ("1931-02-06", "Father's death"),
    ]

    for date_str, label in key_dates:
        evt_date = datetime.strptime(date_str, "%Y-%m-%d")
        print(section(f"{label} — {date_str}"))

        try:
            dynamic = engine.analyze_dynamic(chart, static, evt_date)
        except Exception as e:
            print(f"  [ERROR: {e}]")
            continue

        # Print dasha info
        md, ad, pd_str = get_dasha_info(dynamic)
        print(f"  Vimshottari: {md} / {ad} / {pd_str}")
        print(f"  Yogini: {get_yogini_info(dynamic)}")
        print(f"  Chara: {get_chara_info(dynamic)}")

        # Transit info
        transit_info = get_transit_positions(dynamic)
        for tp_name in ["SATURN", "JUPITER", "RAHU"]:
            tp_data = transit_info.get(tp_name, {})
            h_from_lagna = ((tp_data.get("sign_idx", 0) - lagna_sign) % 12) + 1
            print(f"  {tp_name}: {tp_data.get('sign','?')} H{h_from_lagna} from Lagna")

        print(f"\n  All 4 domains:")
        for dom in ["career", "finance", "marriage", "health"]:
            report = safe_predict(engine, chart, dom, evt_date, static)
            print(f"\n  === {dom.upper()} ===")
            print_full_prediction(report)

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 4: TIMELINE ANALYSIS (1945-1950)
    # ═══════════════════════════════════════════════════════════════════
    print(banner("SECTION 4: TIMELINE ANALYSIS 1945-1950"))
    print("  Month-by-month career confidence around Independence")

    timeline_scores = []
    start_year, end_year = 1945, 1950

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            date = datetime(year, month, 15)
            try:
                report = safe_predict(engine, chart, "career", date, static)
                score = report.get("confidence", {}).get(
                    "overall_boosted", report.get("confidence", {}).get("overall", 0))

                dynamic = engine.analyze_dynamic(chart, static, date)
                md, ad, _ = get_dasha_info(dynamic)
            except Exception:
                score = 0
                md, ad = "?", "?"

            timeline_scores.append((date, score, md, ad))
            bar = "█" * int(score * 40)
            marker = " <<<< INDEPENDENCE" if year == 1947 and month == 8 else ""
            print(f"  {year}-{month:02d}  {md:>8}/{ad:<8}  {score:5.1%}  {bar}{marker}")

    # Text-based chart
    print(section("CAREER CONFIDENCE TIMELINE (text chart)"))
    print(f"  {'Date':<10} {'Score':>6}  {'Chart':50}")
    print(f"  {'----':<10} {'-----':>6}  {'-'*50}")
    for date, score, md, ad in timeline_scores:
        bar_len = int(score * 50)
        bar = "#" * bar_len
        marker = " <--" if date.year == 1947 and date.month == 8 else ""
        print(f"  {date.strftime('%Y-%m'):<10} {score:5.1%}  |{bar:<50}|{marker}")

    # Check if peak is around Aug 1947
    aug47_scores = [s for d, s, _, _ in timeline_scores if d.year == 1947 and d.month == 8]
    max_score = max(s for _, s, _, _ in timeline_scores) if timeline_scores else 0
    max_date = [d for d, s, _, _ in timeline_scores if s == max_score]

    print(f"\n  Aug 1947 career score: {aug47_scores[0]:.1%}" if aug47_scores else "  Aug 1947: N/A")
    print(f"  Peak score in period: {max_score:.1%} on {max_date[0].strftime('%Y-%m') if max_date else '?'}")
    if aug47_scores and aug47_scores[0] >= max_score * 0.9:
        print(f"  RESULT: Aug 1947 IS near the peak — engine correctly identifies this period")
    else:
        print(f"  RESULT: Aug 1947 is NOT the peak — engine may not correctly identify this event")

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 5: WHAT WORKED AND WHAT DIDN'T
    # ═══════════════════════════════════════════════════════════════════
    print(banner("SECTION 5: VALIDATION SUMMARY"))

    correct = [(label, score, domain) for label, match, score, domain in event_results if "YES" in match]
    partial = [(label, score, domain) for label, match, score, domain in event_results if "PARTIAL" in match]
    missed = [(label, score, domain) for label, match, score, domain in event_results if "NO" in match]

    print(section("EVENTS WHERE ENGINE CORRECTLY IDENTIFIED HIGH ACTIVATION"))
    if correct:
        for label, score, domain in correct:
            print(f"  ✓ {label} ({domain}) — {score:.1%}")
    else:
        print("  None")

    print(section("EVENTS WHERE ENGINE SHOWED PARTIAL ACTIVATION"))
    if partial:
        for label, score, domain in partial:
            print(f"  ~ {label} ({domain}) — {score:.1%}")
    else:
        print("  None")

    print(section("EVENTS WHERE ENGINE MISSED (LOW CONFIDENCE)"))
    if missed:
        for label, score, domain in missed:
            print(f"  ✗ {label} ({domain}) — {score:.1%}")
    else:
        print("  None")

    print(section("POSSIBLE REASONS FOR MISSES"))
    reasons = [
        "1. Historical dates (1889-1964) — transit ephemeris accuracy may differ from modern era.",
        "2. Prediction engine is tuned for CURRENT-DATE predictions; running for historical dates",
        "   means the dynamic transit analysis uses Swiss Ephemeris for past dates which is accurate,",
        "   but the Gochar scoring assumes modern context.",
        "3. Nehru's chart has Rashi Sandhi (ASC/Sun near sign boundaries) — ayanamsa sensitivity",
        "   of ±0.5° could shift the lagna sign entirely, changing ALL house placements.",
        "4. The engine uses 'promise_pct' as a hard gate — if natal promise for a domain is weak,",
        "   even perfectly timed dashas/transits cannot push the score above the ceiling.",
        "5. Multi-dasha consensus requires Vimshottari + Chara + Yogini to agree — historical",
        "   periods often show BLOCKED consensus because Chara dasha computation depends on exact",
        "   house cusps which are ayanamsa-sensitive.",
        "6. Death prediction is inherently limited — the engine deliberately avoids strong ",
        "   pronouncements about mortality (ethical guardrails).",
        "7. Dasha periods were computed from the SWE-built chart which may differ slightly from",
        "   the traditionally published Nehru dasha periods in textbooks.",
    ]
    for r in reasons:
        print(f"  {r}")

    # Overall summary
    total = len(event_results)
    correct_count = len(correct)
    partial_count = len(partial)
    missed_count = len(missed)

    print(section("OVERALL VALIDATION SCORECARD"))
    print(f"  Total events tested:    {total}")
    print(f"  Correct (score >= 45%): {correct_count}  ({correct_count/total:.0%})")
    print(f"  Partial (score 30-45%): {partial_count}  ({partial_count/total:.0%})")
    print(f"  Missed  (score < 30%):  {missed_count}  ({missed_count/total:.0%})")
    print(f"  Accuracy (correct+partial): {(correct_count+partial_count)/total:.0%}")

    print(f"\n{'='*80}")
    print(f"  Validation complete. Output saved to content41_validation.txt")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
