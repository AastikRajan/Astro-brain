"""
Vedic Astrology Engine — Main Entry Point
==========================================
Run this script to generate a full astrological report for the sample chart
(or pass a JSON path as first argument for a custom chart).

Usage:
    python main.py                              # sample chart, today
    python main.py chart.json                   # custom chart file
    python main.py chart.json 2026-09-15        # custom chart + specific date
    python main.py chart.json 2026-09-15 career # single domain
    python main.py --ai                         # add GPT-4o narrative (needs OPENAI_API_KEY)
    python main.py chart.json today career --ai # GPT + single domain
"""
import sys
import json
import textwrap
from datetime import datetime
from pathlib import Path

# ── Ensure UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError) ─
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Engine imports ──────────────────────────────────────────────
from vedic_engine.data.loader import load_sample_chart, load_from_dict, build_chart_swe
from vedic_engine.prediction.engine import PredictionEngine

# ── AI interpreter (optional — requires OPENAI_API_KEY) ─────────
try:
    from vedic_engine.ai.interpreter import VedicInterpreter
    _AI_MODULE_AVAILABLE = True
except ImportError:
    _AI_MODULE_AVAILABLE = False

SIGN_NAMES = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]
PLANET_SYMBOLS = {
    "SUN":"Su", "MOON":"Mo", "MARS":"Ma", "MERCURY":"Me",
    "JUPITER":"Ju", "VENUS":"Ve", "SATURN":"Sa", "RAHU":"Ra", "KETU":"Ke",
}


# ─── Pretty-print helpers ─────────────────────────────────────────

def banner(title: str, width: int = 70) -> str:
    pad   = (width - len(title) - 2) // 2
    line  = "=" * width
    inner = "=" * pad + f" {title} " + "=" * pad
    if len(inner) < width:
        inner += "="
    return f"\n{line}\n{inner}\n{line}"


def section(title: str) -> str:
    return f"\n{'-'*60}\n  {title}\n{'-'*60}"


def fmt_sign(idx: int) -> str:
    return SIGN_NAMES[idx % 12]


def print_static_summary(static: dict):
    meta = static.get("meta", {})
    print(banner("NATAL CHART ANALYSIS"))
    print(f"  Lagna (Ascendant) : {fmt_sign(meta.get('lagna_sign', 0))}")
    print(f"  Moon Sign (Rashi) : {fmt_sign(meta.get('moon_sign', 0))}")
    print()

    # Planet positions
    print(section("PLANET POSITIONS"))
    chart_raw = static.get("chart_raw", {})
    lons  = chart_raw.get("planet_lons", {})
    signs = chart_raw.get("planet_signs", {})
    houses= chart_raw.get("planet_houses", {})
    retros= chart_raw.get("retrogrades", {})
    for planet in ["SUN","MOON","MARS","MERCURY","JUPITER","VENUS","SATURN","RAHU","KETU"]:
        sym  = PLANET_SYMBOLS.get(planet, planet[:2])
        lon  = lons.get(planet, 0)
        sgn  = signs.get(planet, 0)
        hse  = houses.get(planet, "?")
        retro= " [R]" if retros.get(planet) else ""
        print(f"  {sym} {planet:<9} {lon:>7.3f}°  {fmt_sign(sgn):<12} H{hse}{retro}")

    # Karakas
    kr  = static.get("karakas", {})
    karaka_list = []
    if isinstance(kr, dict):
        karaka_list = kr.get("list", [])
    elif isinstance(kr, list):
        karaka_list = kr
    if karaka_list:
        print(section("JAIMINI CHARA KARAKAS"))
        for k in karaka_list:
            if isinstance(k, dict):
                role = k.get("role", "?")
                rname = k.get("role_name", "?")
                planet = k.get("planet", "?")
                deg = k.get("degree", 0.0)
                print(f"  {role:<5} {rname:<20} {planet:<10} {deg:.2f}\u00b0 in sign")
        # AK-AmK relationship
        analysis = kr.get("analysis", {}) if isinstance(kr, dict) else {}
        if analysis and "ak_amk_relationship" in analysis:
            ak_p  = analysis.get("atma_karaka", {}).get("planet", "?")
            amk_p = analysis.get("amatya_karaka", {}).get("planet", "?")
            rel   = analysis.get("ak_amk_relationship", "")
            print(f"  AK({ak_p}) \u2014 AmK({amk_p}) : {rel}")

    # Yogas
    yogas = static.get("yogas", [])
    if yogas:
        print(section(f"ACTIVE YOGAS ({len(yogas)} detected)"))
        for y in yogas[:10]:
            # handle both dict and YogaResult dataclass
            if isinstance(y, dict):
                name = y.get("name", "Unknown")
                desc = y.get("description", "")
            else:
                name = getattr(y, "name", str(y))
                desc = getattr(y, "description", "")
            print(f"  * {name}")
            if desc:
                wrapped = textwrap.fill(desc, width=60, initial_indent="      ",
                                       subsequent_indent="      ")
                print(wrapped)

    # Shadbala
    sha = static.get("shadbala_ratios", {})
    if sha:
        print(section("SHADBALA STRENGTH RATIOS  (>1.0 = above minimum)"))
        for planet, ratio in sorted(sha.items(), key=lambda x: -x[1]):
            bar = "█" * int(ratio * 10)
            status = "STRONG" if ratio >= 1.0 else "WEAK"
            print(f"  {planet:<10} {ratio:>5.2f}x  {bar:<15} {status}")

    # Ashtakvarga
    av = static.get("ashtakvarga", {})
    if isinstance(av, dict) and ("sarvashtakvarga" in av or "sarva" in av):
        sav = av.get("sarvashtakvarga") or av.get("sarva", [])
        total = sum(sav)
        print(section(f"SARVASHTAKVARGA  (total: {total}/337)"))
        signs_row = "  " + "  ".join(f"{SIGN_NAMES[i][:3]}" for i in range(12))
        scores_row = "  " + "  ".join(f"{s:>3}" for s in sav)
        print(signs_row)
        print(scores_row)
        sav_profile = av.get("sav_profile", {}) if isinstance(av, dict) else {}
        if isinstance(sav_profile, dict) and sav_profile:
            vit = sav_profile.get("vittya", {})
            tee = sav_profile.get("teertha", {})
            sca = sav_profile.get("savings_capacity", {})
            h18 = sav_profile.get("h1_vs_h8", {})
            if vit or tee or sca or h18:
                print("  Advanced SAV:")
                if vit:
                    print(f"    Vittya   : {vit.get('score', 0)}  [{vit.get('status', '?')}]  ratio={vit.get('ratio', 0):.2f}")
                if tee:
                    print(f"    Teertha  : {tee.get('score', 0)}  [{tee.get('status', '?')}]  ratio={tee.get('ratio', 0):.2f}")
                if sca:
                    can_save = "YES" if sca.get("can_save") else "NO"
                    print(f"    H2 vs H12: {sca.get('h2', '?')} vs {sca.get('h12', '?')}  can_save={can_save}")
                if h18:
                    h18_ok = "OK" if h18.get("healthy_balance") else "RISK"
                    print(f"    H1 vs H8 : {h18.get('h1', '?')} vs {h18.get('h8', '?')}  [{h18_ok}]")

    # Functional Analysis (lagna-specific roles)
    fa = static.get("functional", {})
    if isinstance(fa, dict) and "classifications" in fa:
        print(section(f"FUNCTIONAL ANALYSIS  (Lagna: {fa.get('lagna_name','')})"))
        yks = fa.get("yogakarakas", [])
        fbs = [p for p in fa.get("functional_benefics", []) if p not in yks]
        fms = fa.get("functional_malefics", [])
        bad = fa.get("badhaka", "")
        mar = fa.get("marakas", [])
        print(f"  Yogakaraka(s)       : {', '.join(yks) or 'None'}")
        print(f"  Functional Benefics : {', '.join(fbs) or 'None'}")
        print(f"  Functional Malefics : {', '.join(fms) or 'None'}")
        print(f"  Badhaka (H{fa.get('badhaka_house','?')} lord): {bad or 'None'}")
        print(f"  Marakas (H2+H7 lords): {', '.join(mar) or 'None'}")

    # Graha Yuddha
    wars = static.get("graha_yuddha", [])
    if wars:
        print(section(f"GRAHA YUDDHA (PLANETARY WAR)  [{len(wars)} active]"))
        for w in wars:
            print(f"  {w['p1']} vs {w['p2']}: sep={w['separation_deg']:.2f}°  "
                  f"Winner={w['winner']}  Loser={w['loser']}  "
                  f"Penalty={w['strength_penalty']:.0%}")

    # Dispositor Graph (networkx)
    dg = static.get("dispositor_graph", {})
    if isinstance(dg, dict) and "error" not in dg and dg.get("graph_summary"):
        print(section("DISPOSITOR GRAPH ANALYSIS"))
        print(f"  {dg.get('graph_summary','')}")
        if dg.get("mutual_receptions"):
            pairs = [f"{a}↔{b}" for a, b in dg["mutual_receptions"]]
            print(f"  Mutual receptions : {', '.join(pairs)}")
        if dg.get("final_dispositors"):
            print(f"  Final dispositors : {', '.join(dg['final_dispositors'])}")

    # Special Points
    sp = static.get("special_points", {})
    if isinstance(sp, dict) and "gulika" in sp:
        print(section("SPECIAL POINTS"))
        # Flat longitude points
        _FLAT_SP = ["gulika","mandi","hora_lagna","ghati_lagna",
                    "indu_lagna","bhrigu_bindu"]
        for key in _FLAT_SP:
            data = sp.get(key)
            if isinstance(data, dict):
                label = key.replace('_',' ').title()
                print(f"  {label:<16} {data.get('longitude',0):>7.2f}\u00b0  {data.get('sign','?')}")

        # Upagrahas (nested sub-points)
        upag = sp.get("upagrahas", {})
        if isinstance(upag, dict) and upag:
            print(f"  {'Upagrahas':<16}")
            _UP_LABELS = {
                "dhuma":"Dhuma","vyatipata":"Vyatipata",
                "parivesha":"Parivesha","indrachapa":"Indrachapa",
                "upaketu":"Upaketu"
            }
            for uk, ulabel in _UP_LABELS.items():
                ud = upag.get(uk, {})
                if isinstance(ud, dict):
                    print(f"    {ulabel:<14} {ud.get('longitude',0):>7.2f}\u00b0  {ud.get('sign','?')}")

        # Yogi / Avayogi
        ya = sp.get("yogi_avayogi", {})
        if isinstance(ya, dict) and "yogi_point" in ya:
            print(f"  {'Yogi Point':<16} {ya.get('yogi_point',0):>7.2f}\u00b0  "
                  f"{ya.get('yogi_sign','?')}  [planet: {ya.get('yogi_planet','?')}, "
                  f"dup-yogi: {ya.get('duplicate_yogi','?')}]")
            print(f"  {'Avayogi Point':<16} {ya.get('avayogi_point',0):>7.2f}\u00b0  "
                  f"{ya.get('avayogi_sign','?')}  [planet: {ya.get('avayogi_planet','?')}]")

        # Lagna Drekkana nature
        ld = sp.get("lagna_drekkana", {})
        if isinstance(ld, dict) and "nature" in ld:
            sarpa_flag = "  [!] SARPA — health risk" if ld.get("is_sarpa") else ""
            pakshi_flag = "  [!] PAKSHI — instability" if ld.get("is_pakshi") else ""
            print(f"  {'Lagna Drekkana':<16} {ld.get('drekkana','?')}/3  "
                  f"{ld.get('sign','?')}  [{ld.get('nature','?')}]{sarpa_flag}{pakshi_flag}")

    # ── Special Degrees (Mrityu Bhaga, Gandanta, Pushkara Bhaga) ────
    sd = static.get("special_degrees", {})
    sd_summary = sd.get("summary", []) if isinstance(sd, dict) else []
    if sd_summary:
        print(section("SPECIAL DEGREES (Mrityu Bhaga / Gandanta / Pushkara)"))
        for note in sd_summary:
            print(f"  ⚠ {note}")

    # ── Varga (Divisional Chart) Report
    vr = static.get("varga_report", {})
    if isinstance(vr, dict) and "error" not in vr:
        print(section("DIVISIONAL CHARTS (VARGA) ANALYSIS"))
        # D60 summary
        print(f"  D60 Karma  : {vr.get('d60_summary','')}")
        # Vargottama
        vot = vr.get("vargottama", [])
        if vot:
            print(f"  Vargottama : {', '.join(vot)}  (same sign in D1 & D9 — maximum stability)")
        # Pushkara
        pka = vr.get("pushkara", [])
        if pka:
            print(f"  Pushkara   : {', '.join(pka)}  (Pushkara Navamsa — auspicious blessing)")
        # D9 marriage
        d9 = vr.get("d9", {})
        for ind in d9.get("marriage_indications", [])[:3]:
            print(f"  D9 Marriage: {ind}")
        # D10 career
        d10 = vr.get("d10", {})
        for fav in d10.get("favorable", [])[:3]:
            print(f"  D10 Career+: {fav}")
        for ch in d10.get("challenges", [])[:2]:
            print(f"  D10 Career-: {ch}")
        print(f"  {d10.get('tenth_house','')}")
        # D7 children
        d7 = vr.get("d7", {})
        if d7.get("indications"):
            print(f"  D7 Children: est. {d7.get('estimated_children','?')} children indicated")
            for ind in d7["indications"][:2]:
                print(f"    {ind}")
        # D4 property
        d4 = vr.get("d4", {})
        for ind in d4.get("indications", [])[:2]:
            print(f"  D4 Property: {ind}")
        # D60 per planet (top 3 krura for awareness)
        d60 = vr.get("d60", {})
        krura_planets = [p for p, v in d60.items() if isinstance(v, dict) and v.get("status") == "krura"]
        if krura_planets:
            print(f"  D60 Krura  : {', '.join(krura_planets[:5])} — karma fine-print may offset D1 results")

    # ── Arudha Padas (Jaimini)
    ap = static.get("arudha_padas", {})
    if isinstance(ap, dict) and "error" not in ap and ap.get("al_sign") is not None:
        print(section("ARUDHA PADAS (Jaimini Manifested Image)"))
        al  = ap.get("al_sign",  "?")
        ul  = ap.get("ul_sign",  "?")
        a7  = ap.get("a7_sign",  "?")
        a10 = ap.get("a10_sign", "?")
        print(f"  AL  (Arudha Lagna / world image)   : {al}")
        print(f"  UL  (Upapada Lagna / marriage)     : {ul}")
        print(f"  A7  (Darapada / spouse image)      : {a7}")
        print(f"  A10 (Career/profession image)      : {a10}")
        for bhava, data in ap.get("arudhas", {}).items():
            if isinstance(data, dict) and "analysis" in data:
                notes = data["analysis"].get("notes", [])
                if notes:
                    print(f"  A{bhava} notes : {', '.join(notes[:2])}")

    # ── Rashi Drishti overview
    rd = static.get("rashi_drishti", {})
    if isinstance(rd, dict) and "error" not in rd and rd:
        print(section("RASHI DRISHTI (Jaimini Sign Aspects — planets aspecting each sign)"))
        SIGN_N2 = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                   "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        shown = 0
        for sign_idx in range(12):
            planets_asp = rd.get(sign_idx, [])
            if planets_asp:
                sign_name = SIGN_N2[sign_idx % 12]
                print(f"  {sign_name:<13}: aspected by {', '.join(planets_asp)}")
                shown += 1
                if shown >= 8:
                    break

    # ── Remedial Measures (Upāya)
    remedies = static.get("remedies", [])
    if remedies and not (len(remedies) == 1 and "error" in remedies[0]):
        print(section(f"REMEDIAL MEASURES (UPĀYA)  [{len(remedies)} planets need attention]"))
        for r in remedies[:4]:
            print(f"  [{r.get('urgency','?')}] {r.get('planet','?')}  "
                  f"affliction={r.get('affliction_score',0):.2f}  "
                  f"({r.get('rationale','')})")
            print(f"    Gem    : {r.get('gem','?')}")
            print(f"    Mantra : {r.get('mantra','?')}  ×{r.get('mantra_count',0):,}")
            print(f"    Donate : {r.get('donation','?')[:70]}")
            print(f"    Deity  : {r.get('deity','?')}")
            if r.get("contra"):
                print(f"    CAUTION: {r['contra'][0][:80]}")


def print_dynamic_summary(dynamic: dict):
    print(banner("CURRENT TIMING ANALYSIS"))

    # Dasha periods
    vim = dynamic.get("vimshottari", {})
    active = vim.get("active", [])
    print(section("VIMSHOTTARI DASHA (Active Periods)"))
    if isinstance(active, dict):
        print(f"  Maha-dasha   : {active.get('mahadasha', '?')}")
        print(f"  Antar-dasha  : {active.get('antardasha', '?')}")
        prat = active.get('pratyantardasha', '')
        if prat:
            print(f"  Pratyantar   : {prat}")
    elif isinstance(active, list):
        labels = ["Maha-dasha", "Antar-dasha", "Pratyantar-dasha"]
        for i, period in enumerate(active[:3]):
            if isinstance(period, dict):
                label = labels[i] if i < len(labels) else "Sub"
                planet = period.get("planet", period.get("mahadasha", "?"))
                start  = str(period.get("start", ""))[:10]
                end    = str(period.get("end", ""))[:10]
                print(f"  {label:<20} {planet:<12} {start} -> {end}")

    # Sandhi (junction) warning
    sandhi = vim.get("sandhi", {})
    if sandhi.get("in_sandhi"):
        lvl   = sandhi.get("level", "maha").capitalize()
        phase = sandhi.get("phase", "")
        frm   = sandhi.get("transition_from", "?")
        to    = sandhi.get("transition_to", "?")
        bd    = sandhi.get("boundary_date", "")
        dtb   = sandhi.get("days_to_boundary", 0)
        if phase == "closing":
            print(f"  [!] DASHA SANDHI ({lvl}): {frm} period ending in {dtb} day(s) ({bd}) → {to} begins")
            print(f"       Results unpredictable — junction period. Avoid major decisions.")
        else:
            print(f"  [!] DASHA SANDHI ({lvl}): {abs(dtb)} day(s) since {frm}→{to} transition ({bd})")
            print(f"       New dasha energy still crystallising — mixed results likely.")

    # Retrograde dasha-lord flag
    rl = vim.get("retrograde_lords", {})
    for lvl_key, pname in rl.items():
        label = "Maha" if lvl_key == "mahadasha" else "Antar"
        print(f"  [R] {label}-dasha lord {pname} is RETROGRADE in natal chart")

    # Ashtottari Dasha (conditional 108-year cycle)
    ashto = dynamic.get("ashtottari", {})
    if ashto.get("eligible"):
        print(section("ASHTOTTARI DASHA (108-yr Conditional)"))
        aact = ashto.get("active", {})
        print(f"  Maha-dasha   : {aact.get('mahadasha', '?')}")
        if aact.get("antardasha"):
            print(f"  Antar-dasha  : {aact.get('antardasha', '?')}")
        if ashto.get("dual_verified"):
            print(f"  [**] DUAL VERIFIED: Vimshottari + Ashtottari agree → near-absolute certainty")
        if ashto.get("note"):
            print(f"  Note: {ashto['note']}")
    elif ashto and not ashto.get("eligible"):
        pass  # Silently skip when not applicable (Rahu not in kendra/trikona from lagna lord)

    # Yogini
    yog = dynamic.get("yogini", {}).get("active", {})
    if isinstance(yog, dict) and yog:
        print(section("YOGINI DASHA"))
        yogini_name  = yog.get('major_yogini', yog.get('yogini', '?'))
        yogini_planet = yog.get('major_planet', yog.get('planet', '?'))
        sub_yogini   = yog.get('sub_yogini', '')
        print(f"  Yogini Lord  : {yogini_name}  (ruled by {yogini_planet})")
        if sub_yogini:
            sub_planet = yog.get('sub_planet', '')
            print(f"  Sub-Yogini   : {sub_yogini}  (ruled by {sub_planet})")

    # Chara Dasha (Jaimini sign-based)
    chara = dynamic.get("chara_dasha", {})
    if chara and isinstance(chara, dict) and "error" not in chara:
        print(section("JAIMINI CHARA DASHA"))
        direction = chara.get("direction", "?")
        active_ch = chara.get("active", {})
        if active_ch and "mahadasha" in active_ch:
            md_sign  = active_ch.get("mahadasha", "?")
            md_start = str(active_ch.get("start", ""))[:10]
            md_end   = str(active_ch.get("end",   ""))[:10]
            print(f"  Direction    : {direction}")
            print(f"  Maha-dasha   : {md_sign:<15} {md_start} → {md_end}")
            antar = active_ch.get("antardasha", {})
            if isinstance(antar, dict) and "sign" in antar:
                ad_sign  = antar.get("sign", "?")
                ad_start = str(antar.get("start", ""))[:10]
                ad_end   = str(antar.get("end",   ""))[:10]
                print(f"  Antar-dasha  : {ad_sign:<15} {ad_start} → {ad_end}")

    # Dasha Quality (Ishta/Kashta Phala)
    dq = dynamic.get("dasha_quality", {})
    if dq and dq.get("quality_label"):
        print(section("DASHA QUALITY (Ishta/Kashta Phala)"))
        print(f"  Maha-dasha lord: {dq.get('planet', '?')}")
        print(f"  Quality        : {dq['quality_label']}  ({dq.get('dasha_quality', 0):.0%})")
        print(f"  Maturity stage : {dq.get('maturity_tier', '?')}  (×{dq.get('maturity_modifier', 1.0):.2f})")
        comps = dq.get("component_scores", {})
        if comps:
            print(f"    Ishta/Kashta: {comps.get('ishta_kashta',0):.2f}  "
                  f"Shadbala: {comps.get('shadbala',0):.2f}  "
                  f"Functional: {comps.get('functional',0):.2f}  "
                  f"D9 dignity: {comps.get('d9_dignity',0):.2f}")

    # Sade Sati
    ss = dynamic.get("sade_sati", {})
    if ss:
        print(section("SADE SATI / DHAIYA STATUS"))
        if ss.get("in_sade_sati"):
            paya = ss.get("paya", {})
            paya_str = f" [{paya.get('metal','')} Paya]" if paya else ""
            print(f"  [!] SADE SATI ACTIVE - {ss.get('phase','')}{paya_str}")
            print(f"     Intensity: {ss.get('intensity','')}")
            if paya:
                print(f"     Moorti multiplier: ×{paya.get('moorti_multiplier', ss.get('moorti_multiplier', 1.0)):.2f}")
            if paya and paya.get('metal') in ('Iron', 'Copper'):
                print(f"     Paya note: {paya.get('description','')}")
        elif ss.get("in_dhaiya"):
            paya = ss.get("paya", {})
            paya_str = f" [{paya.get('metal','')} Paya]" if paya else ""
            print(f"  [!] DHAIYA ACTIVE - {ss.get('phase','')}{paya_str}")
            if paya:
                print(f"     Moorti multiplier: ×{paya.get('moorti_multiplier', ss.get('moorti_multiplier', 1.0)):.2f}")
        else:
            print("  [OK] No Sade Sati or Dhaiya at this time.")

    # Panchanga (5 limbs)
    panch = dynamic.get("panchanga", {})
    if panch and "tithi" in panch:
        print(section("PANCHANGA (Daily Timing Quality)"))
        t  = panch.get("tithi", {})
        v  = panch.get("vara", {})
        n  = panch.get("nakshatra", {})
        yg = panch.get("yoga", {})
        k  = panch.get("karana", {})
        print(f"  Tithi     : {t.get('name','?')} ({t.get('paksha','?')}) — {t.get('quality','?')}")
        print(f"  Vara      : {v.get('name','?')} — ruled by {v.get('planet','?')} ({v.get('quality','?')})")
        print(f"  Nakshatra : {n.get('name','?')} Pada {n.get('pada','?')} [{n.get('nature','?')}] — lord: {n.get('lord','?')}")
        print(f"  Yoga      : {yg.get('name','?')} ({yg.get('quality','?')})")
        print(f"  Karana    : {k.get('name','?')} ({k.get('quality','?')})")
        moon_ph = panch.get("moon_phase","?")
        tq      = panch.get("timing_quality","?")
        ts      = panch.get("timing_score", 0.0)
        print(f"  Moon Phase: {moon_ph}  |  Timing Quality: {tq} ({ts:+.2f})")
        for w in panch.get("warnings", []):
            print(f"  [!] {w}")

    # KP Ruling Planets
    rp = dynamic.get("ruling_planets", {})
    if isinstance(rp, dict) and rp.get("ruling_planets"):
        print(section("KP RULING PLANETS (Current Moment)"))
        print(f"  Day Lord        : {rp.get('day_lord','?')}")
        print(f"  Moon Star Lord  : {rp.get('moon_nak_lord','?')}")
        print(f"  Moon Sign Lord  : {rp.get('moon_sign_lord','?')}")
        print(f"  Lagna Sign Lord : {rp.get('lagna_sign_lord','?')}")
        print(f"  Lagna Star Lord : {rp.get('lagna_nak_lord','?')}")
        unique = rp.get('ruling_planets', [])
        print(f"  Active RPs      : {', '.join(unique)}")

    # Dasha Lord Transit
    dt = dynamic.get("dasha_transit", {})
    if dt and isinstance(dt, dict) and "mahadasha" in dt:
        print(section("DASHA LORD TRANSIT (Gochar)"))
        for lt in ["mahadasha", "antardasha"]:
            info = dt.get(lt, {})
            if not isinstance(info, dict) or "error" in info:
                continue
            label = "Maha" if lt == "mahadasha" else "Antar"
            lord  = info.get("lord", "?")
            sgn   = info.get("transit_sign", "?")
            hm    = info.get("house_from_moon", "?")
            hl    = info.get("house_from_lagna", "?")
            gs    = info.get("gochar_score", 0.0)
            gd    = info.get("gochar_desc", "")
            print(f"  {label}-dasha lord {lord}: {sgn}  H{hm} from Moon  H{hl} from Lagna  Gochar={gs:+.2f}")
            print(f"    {gd}")
            for act in info.get("natal_activations", []):
                print(f"    *** Activating natal {act.get('natal_planet','?')} ({act.get('orb_degrees',0):.1f}° orb): {act.get('significance','')}")
            nx = info.get("next_sign_change")
            if nx and isinstance(nx, dict) and "error" not in nx:
                print(f"    Next ingress -> {nx.get('sign','?')} in {nx.get('days','?')} days ({nx.get('date','?')})")
        tq2 = dt.get("transit_quality", "?")
        cs  = dt.get("combined_transit_score", 0.0)
        print(f"  Combined transit quality: {tq2} ({cs:.0%})")
        dbl = dt.get("double_transit", {})
        if isinstance(dbl, dict) and dbl.get("active"):
            print(f"  *** DOUBLE TRANSIT ACTIVE: {dbl.get('note','Guru+Shani in favourable houses')}")

    # Ingress Calendar
    ingress = dynamic.get("ingress_calendar", [])
    if ingress:
        print(section("UPCOMING PLANETARY INGRESSES"))
        for entry in ingress[:6]:
            pl  = entry.get("planet", "?")
            cs2 = entry.get("current_sign", "?")
            ns  = entry.get("next_sign", "?")
            dy  = entry.get("days", "?")
            dt2 = entry.get("date", "?")
            print(f"  {pl:<10} {cs2:<14} -> {ns:<14} in {dy} days  ({dt2})")

    # Key Transits
    transits = dynamic.get("transits", {})
    if isinstance(transits, dict) and "error" not in transits:
        print(section("TRANSIT HIGHLIGHTS (House from Moon)"))
        for planet in ["SATURN","JUPITER","MARS","VENUS","SUN"]:
            if planet in transits:
                t = transits[planet]
                if not isinstance(t, dict):
                    continue
                sym     = PLANET_SYMBOLS.get(planet, "")
                hs      = t.get("house_from_moon", "?")
                sgn     = t.get("transit_sign", "?")
                fav     = "+" if t.get("is_favorable_gochar") else "-"
                vedha   = " [VEDHA]" if t.get("vedha_blocked") else ""
                score   = t.get("net_score", 0)
                print(f"  {sym} {planet:<10} H{hs:<3} in {sgn:<14} {fav} score={score:.2f}{vedha}")
                if t.get("net_score_moorti_adjusted") is not None:
                    ms = t.get("net_score_moorti_adjusted", score)
                    mf = t.get("moorti_adjustment_factor", 1.0)
                    mm = (t.get("moorti", {}) or {}).get("moorti", "?")
                    print(f"    Moorti adj : {mm} ×{mf:.2f} -> score={ms:.2f}")

    # Transit-to-Natal Longitude Aspects (top aspects by strength)
    ta = dynamic.get("transit_aspects", {})
    if ta and isinstance(ta, dict) and "error" not in ta:
        from vedic_engine.prediction.aspect_transits import top_transit_aspects
        top = top_transit_aspects(ta, top_n=6)
        if top:
            print(section("TRANSIT-TO-NATAL ASPECTS (Weighted Orb)"))
            for asp in top:
                tp  = asp.get("transit_planet", "?")
                np  = asp.get("natal_planet",   "?")
                an  = asp.get("aspect",         "?")
                orb = asp.get("orb",            0.0)
                st  = asp.get("strength",       0.0)
                app = "Applying" if asp.get("applying") else "Separating"
                nat = asp.get("nature", "?")
                bar = "█" * int(st * 10)
                print(f"  {tp:<10} {an:<12} {np:<10} [{nat:<8}] orb={orb:.1f}° str={st:.2f} {bar} ({app})")

    # Bhrigu Bindu Transit (karmic activation check)
    bb_tr = dynamic.get("bhrigu_bindu_transit", {})
    if bb_tr and (bb_tr.get("triggered") or bb_tr.get("approaching")):
        print(section("BHRIGU BINDU TRANSIT (Karmic Activation)"))
        print(f"  Bhrigu Bindu     : {bb_tr.get('bb_degree', 0):.2f}°")
        for bp in bb_tr.get("activating_planets", []):
            icon = "🔴" if bp.get("zone") == "EXACT" else "🟡"
            print(f"  {icon} {bp['planet']:<10} {bp['zone']:<10} orb={bp['arc_degrees']:.1f}°  strength={bp['strength']:.2f}")
        print(f"  {bb_tr.get('transit_summary', '')}")

    # Secondary Progressions + Solar Arc
    prog = dynamic.get("progressions", {})
    if prog and isinstance(prog, dict) and "error" not in prog:
        print(section("SECONDARY PROGRESSIONS (Day-for-Year)"))
        print(f"  Progressed date  : {prog.get('progressed_date','?')}")
        print(f"  Solar arc        : {prog.get('solar_arc_degrees', 0.0):+.2f}°")
        print(f"  Prog Sun sign    : {prog.get('progressed_sun_sign','?')}")
        print(f"  Prog Moon sign   : {prog.get('progressed_moon_sign','?')}")
        print(f"  Prog lunation    : {prog.get('progressed_lunation','?')}")
        pa = prog.get("progressed_activations", [])
        sa = prog.get("solar_arc_activations",  [])
        if pa:
            print(f"  Progressed activations ({len(pa)}):")
            for act in pa[:3]:
                print(f"    {act.get('progressed_planet','?')} conj natal {act.get('natal_planet','?')} ({act.get('orb',0):.2f}°)")
        if sa:
            print(f"  Solar arc activations ({len(sa)}):")
            for act in sa[:3]:
                print(f"    SA-{act.get('directed_planet','?')} conj natal {act.get('natal_planet','?')} ({act.get('orb',0):.2f}°)")
        boost = prog.get("combined_boost", 0.0)
        print(f"  Activation boost : {boost:+.2%}")

    # Solar Terms (Sun at 15° multiples — 24 Vedic/East-Asian timing markers)
    solar_terms = dynamic.get("solar_terms", [])
    if solar_terms:
        print(section("UPCOMING SOLAR TERMS (Sun at 15° Multiples)"))
        for term in solar_terms[:6]:
            print(f"  {term.get('date','?')}  {term.get('note','?')}  (in {int(term.get('days',0))} days)")

    # Upcoming Lunations & Eclipses
    lun_data = dynamic.get("lunations", {})
    if isinstance(lun_data, dict) and "error" not in lun_data:
        eclipses = lun_data.get("eclipses", [])
        high_sig = lun_data.get("high_significance", [])
        if eclipses:
            print(section(f"UPCOMING ECLIPSES  [{len(eclipses)} in 12 months]"))
            for e in eclipses[:4]:
                nm = e.get('nakshatra', '?')
                ec = e.get('eclipse', '?')
                dt = e.get('date', '?')
                hn = e.get('from_natal_moon_house', '?')
                near = ', '.join(e.get('near_natal_planets', []))
                sig  = e.get('significance', 0)
                print(f"  [{dt}] {ec} Eclipse in {nm}  H{hn} from Moon  sig={sig:.2f}")
                if near:
                    print(f"    Near natal: {near} — {e.get('impact','')[:80]}")
                else:
                    print(f"    {e.get('impact','')[:90]}")
        elif high_sig:
            print(section(f"IMPORTANT UPCOMING NEW/FULL MOONS  [top {min(3,len(high_sig))}]"))
            for l in high_sig[:3]:
                print(f"  [{l.get('date','?')}] {l.get('type','?')} in {l.get('nakshatra','?')}  "
                      f"H{l.get('from_natal_moon_house','?')} from Moon  sig={l.get('significance',0):.2f}")

    # Best/Worst Timing Windows
    tw_data = dynamic.get("timing_windows", {})
    if isinstance(tw_data, dict) and "error" not in tw_data and tw_data:
        print(section("NEXT 12 MONTHS — TIMING WINDOWS"))
        for dom_key in ["career", "finance", "health", "relationships"]:
            dom_tw = tw_data.get(dom_key, {})
            best  = dom_tw.get("best", [])
            worst = dom_tw.get("worst", [])
            if not best and not worst:
                continue
            print(f"  {dom_key.upper()}:")
            for w in best[:2]:
                print(f"    + BEST  {w.get('window_start','?')} — {w.get('window_end','?')}  "
                      f"(peak {w.get('peak_date','?')})  score={w.get('score',0):.2f}")
            for w in worst[:1]:
                print(f"    - AVOID {w.get('window_start','?')} — {w.get('window_end','?')}  "
                      f"(trough {w.get('trough_date','?')})  score={w.get('score',0):.2f}")


def print_domain_report(domain_report: dict):
    domain = domain_report.get("domain", "").upper()
    conf   = domain_report.get("confidence", {})
    level  = conf.get("level", "?")
    score  = conf.get("overall_boosted", conf.get("overall", 0))
    bar    = "█" * int(score * 20)

    print(section(f"{domain}  —  {level}  ({score:.1%})"))
    print(f"  Confidence : [{bar:<20}] {score:.1%}")

    # Calibrated confidence
    cal = domain_report.get("calibrated_confidence", {})
    if isinstance(cal, dict) and "calibrated" in cal:
        cal_pct = cal["calibrated"]
        band    = cal.get("reliability_band", "?")
        lo, hi  = cal.get("confidence_interval", (cal_pct, cal_pct))
        print(f"  Calibrated : {cal_pct:.0%}  ({lo:.0%}–{hi:.0%})  Reliability: {band}")

    comp = conf.get("components", {})
    if comp:
        for k, v in comp.items():
            mini_bar = "█" * int(v * 10)
            print(f"    {k:<30} {v:.2f}  {mini_bar}")

    # ── Classical Phase-1 (diagnostic-first) ───────────────────────────
    cph = conf.get("classical_phase1", {})
    if cph and isinstance(cph, dict):
        enabled = cph.get("enabled", False)
        base_c  = cph.get("baseline_before_classical", score)
        cand_c  = cph.get("adjusted_candidate", score)
        tmult   = cph.get("total_multiplier_capped", 1.0)
        pmult   = cph.get("pushkara_multiplier", 1.0)
        mmult   = cph.get("moorti_multiplier", 1.0)
        taram   = cph.get("tarabala_multiplier", 1.0)
        state   = "ENABLED" if enabled else "DIAGNOSTIC"
        print(f"\n  Classical Phase-1    : {state}")
        print(f"    baseline={base_c:.0%}  adjusted={cand_c:.0%}  total×{tmult:.2f}")
        print(f"    pushkara×{pmult:.2f}  moorti×{mmult:.2f}  tarabala×{taram:.2f}")

    # ── Dispositor chain insight
    disp = domain_report.get("dispositor", {})
    if disp and isinstance(disp, dict) and "error" not in disp:
        verdict = disp.get("chain_verdict", "?")
        md_final = disp.get("mahadasha_final_dispositor", "?")
        ad_final = disp.get("antardasha_final_dispositor", "?")
        cs = disp.get("combined_strength", 0.0)
        dasha = domain_report.get("dasha", {})
        md = dasha.get("maha_dasha", "?")
        ad = dasha.get("antar_dasha", "?")
        print(f"\n  Dispositor Chain [{verdict}]  (combined strength {cs:.0%})")
        print(f"    {md} chain -> final lord: {md_final}")
        print(f"    {ad} chain -> final lord: {ad_final}")

    # ── Fuzzy convergence
    conf = domain_report.get("confidence", {})
    fuzzy = conf.get("fuzzy", {})
    if fuzzy and isinstance(fuzzy, dict) and "convergence_level" in fuzzy:
        cvg = fuzzy.get("convergence_level", "?")
        fv  = fuzzy.get("fuzzy_confidence", 0.0)
        mth = fuzzy.get("method", "?")
        fi  = conf.get("fuzzy_inputs", {})
        t   = fi.get("timing", 0.0)
        tr  = fi.get("transit", 0.0)
        st  = fi.get("structural", 0.0)
        print(f"\n  Fuzzy Convergence [{cvg}]  (fuzzy={fv:.0%}, method={mth})")
        print(f"    timing={t:.2f}  transit={tr:.2f}  structural={st:.2f}")

    # ── Bayesian posterior
    bayes = conf.get("bayesian", {})
    if bayes and isinstance(bayes, dict) and "posterior_mean" in bayes:
        pm    = bayes.get("posterior_mean", 0.0)
        cl    = bayes.get("credible_low", 0.0)
        ch    = bayes.get("credible_high", 0.0)
        bv    = bayes.get("bayesian_verdict", "?")
        cert  = bayes.get("certainty_label", "?")
        print(f"\n  Bayesian Posterior [{bv}]  (p={pm:.0%}, 80% CI: {cl:.0%}-{ch:.0%}, {cert})")

    # ── Vimshopak modifier
    vm_mod = conf.get("vimshopak_mod")
    vm_pct = conf.get("vimshopak_pct")
    if vm_mod is not None:
        direction = "boost" if vm_mod >= 0 else "drag"
        print(f"\n  Vimshopak Modifier: {vm_mod:+.1%} ({direction})  [dasha lord dignity {vm_pct:.0f}%]")

    # ── Argala modifier
    argala_mod = conf.get("argala_mod")
    if argala_mod is not None:
        argala_data = domain_report.get("argala", {})
        lagna_argala = argala_data.get("lagna", {}) if isinstance(argala_data, dict) else {}
        lagna_verdict = lagna_argala.get("verdict", "")
        unob_cnt = lagna_argala.get("unobstructable_count")
        reverse_mode = lagna_argala.get("node_reverse_mode")
        print(f"  Argala Modifier      : {argala_mod:+.1%}  [{lagna_verdict}]")
        if unob_cnt is not None or reverse_mode:
            print(f"    Argala details     : unobstructable={int(unob_cnt or 0)}  node_mode={reverse_mode or 'ketu'}")

    # ── Aspect transit modifier (longitude-based weighted orb)
    asp_mod   = conf.get("aspect_transit_mod")
    asp_score = conf.get("aspect_transit_score")
    if asp_mod is not None:
        direction = "boost" if asp_mod >= 0 else "drag"
        print(f"  Aspect Transit Mod   : {asp_mod:+.1%} ({direction})  [activation={asp_score:.2f}]")

    # ── Progression boost
    prog_boost = conf.get("progression_boost")
    if prog_boost is not None and prog_boost != 0.0:
        print(f"  Progression Boost    : {prog_boost:+.2%}  [SA/Secondary activations]")

    # ── Promise Gate (Three Pillar Rule)
    promise = domain_report.get("promise", {})
    if promise and isinstance(promise, dict):
        p_pct   = promise.get("promise_pct", promise.get("promise_percentage", -1))
        p_level = promise.get("promise_level", "")
        denied  = promise.get("denied", False)
        suppressed = promise.get("suppressed", False)
        if p_pct >= 0:
            flag = " [DENIED]" if denied else (" [SUPPRESSED]" if suppressed else "")
            print(f"\n  Three-Pillar Promise : {p_pct}%  [{p_level}]{flag}")
            pillars = promise.get("pillars", {})
            if pillars:
                for pname, pval in pillars.items():
                    print(f"    {pname:<12} = {pval:.2f}" if isinstance(pval, float) else f"    {pname:<12} = {pval}")

    # ── Dasha Diagnostic Matrix
    dasha_diag = domain_report.get("dasha_diagnostic", {})
    if dasha_diag and isinstance(dasha_diag, dict) and "error" not in dasha_diag:
        diag_qual = dasha_diag.get("overall_quality", "")
        diag_geom = dasha_diag.get("md_ad_geometry", "")
        diag_summary = dasha_diag.get("summary", "")
        if diag_qual:
            combust_flag = " COMBUST" if dasha_diag.get("dasha_lord_combust") else ""
            retro_flag   = " RETROGRADE" if dasha_diag.get("dasha_lord_retrograde") else ""
            print(f"\n  Dasha Diagnostic     : {diag_qual.upper()}{combust_flag}{retro_flag}"
                  f"  [MD/AD geometry: {diag_geom}]")
            if diag_summary:
                for sline in diag_summary.split(". ")[:2]:
                    if sline.strip():
                        print(f"    {sline.strip()}.")

    # ── Multi-Dasha Consensus
    consensus = domain_report.get("multi_dasha_consensus", {})
    if consensus and isinstance(consensus, dict):
        c_level  = consensus.get("consensus_level", "")
        c_mult   = consensus.get("confidence_multiplier", 1.0)
        c_detail = consensus.get("detail", "")
        if c_level:
            print(f"\n  Dasha Consensus      : {c_level.upper()}  (multiplier ×{c_mult:.2f})")
            if c_detail:
                print(f"    {c_detail[:100]}")

    # ── Yoga Compounding
    ycomp = domain_report.get("yoga_compounding", {})
    if ycomp and isinstance(ycomp, dict):
        clusters = ycomp.get("clusters", [])
        comp_score = ycomp.get("compounded_score", 0.0)
        if clusters:
            print(f"\n  Yoga Compounding     : {len(clusters)} cluster(s), score={comp_score:.2f}")
            for cl in clusters[:2]:
                cl_names = ", ".join(cl.get("yogas", [])[:3])
                cl_boost = cl.get("compounded_strength", 0.0)
                print(f"    [{cl_names}]  → boost {cl_boost:.2f}")

    # ── Chara Dasha Enrichment (marriage / AK / career flags)
    chara = domain_report.get("chara_dasha", {})
    if chara and isinstance(chara, dict) and "enrichment" in chara:
        enrichment = chara["enrichment"]
        if enrichment.get("marriage_flag"):
            reasons = enrichment.get("marriage_reasons", [])
            print(f"\n  Chara Dasha (Marriage flag): {', '.join(reasons)}")
        if enrichment.get("ak_soul_event_flag"):
            ak_pos = enrichment.get("ak_position", "")
            print(f"  Chara Dasha (AK Soul event): AK position={ak_pos}")
        if enrichment.get("amk_career_boost"):
            print(f"  Chara Dasha (AmK Career boost): active")
        dasha_h = enrichment.get("house_from_lagna", 0)
        dasha_meaning = enrichment.get("house_from_lagna_meaning", "")
        if dasha_h:
            print(f"  Chara Dasha sign     : H{dasha_h} ({dasha_meaning})")
        rashi_d = enrichment.get("rashi_drishti_on_dasha", [])
        if rashi_d:
            nature = enrichment.get("rashi_drishti_nature", "neutral")
            print(f"  Rashi Drishti on dasha sign: {', '.join(rashi_d)} [{nature}]")

    ob = conf.get("overall_boosted", conf.get("overall", 0.0))
    print(f"\n  >> Final confidence (all layers blended): {ob:.0%}")

    print()
    prediction = domain_report.get("prediction", "")
    for line in prediction.split("\n"):
        print(f"  {line}")

    fav = domain_report.get("transits", {}).get("favorable", [])
    blk = domain_report.get("transits", {}).get("vedha_blocked", [])
    if fav:
        print(f"\n  Supporting transits : {', '.join(fav)}")
    if blk:
        print(f"  Blocked by Vedha    : {', '.join(blk)}")

    # ── Badhaka Friction Coefficient ─────────────────────────────────────────
    badhaka = domain_report.get("badhaka", {})
    if badhaka and isinstance(badhaka, dict) and "friction_label" in badhaka:
        bfr = badhaka.get("friction_pct", 0.0)
        bfl = badhaka.get("friction_label", "?")
        bba = badhaka.get("badhaka_active_in_dasha", False)
        bksh = badhaka.get("badhakesh", "?")
        bfm = badhaka.get("friction_multiplier", 1.0)
        print(f"\n  Badhaka [{bfl.upper()} friction]  Badhakesh={bksh}"
              f"  reduction={bfr:.0f}%  multiplier={bfm:.2f}")
        if bba:
            print(f"  [!] Badhaka Dasha ACTIVE — obstacle friction is NOW operational")
        bh_info = badhaka.get("badhaka_info", {})
        if bh_info.get("badhaka_house"):
            print(f"  Badhaka Sthana: H{bh_info['badhaka_house']} ({bh_info.get('lagna_modality','')} ascendant)")

    # ── Combustion Analysis for Domain Transit Planets ────────────────────────
    domain_transits = domain_report.get("transits", {}).get("domain_relevant", {})
    combust_planets = [
        (p, t) for p, t in domain_transits.items()
        if isinstance(t, dict) and t.get("combust")
    ]
    if combust_planets:
        print(f"\n  [COMBUSTION REPORT]")
        for p, t in combust_planets:
            cpct = t.get("combust_pct", 0.0)
            csr  = t.get("combust_strength_retained", 1.0)
            ckt  = "BURNED" if t.get("karakatwa_burned") else "OK"
            cls  = "SURVIVES" if t.get("lordship_survives") else "N/A"
            note_short = (t.get("combust_note") or "")[:80]
            print(f"  {p}: {cpct:.0f}% combust  Retained={csr:.0%}  "
                  f"Karakatwa={ckt}  Lordship={cls}")
            if note_short:
                print(f"    {note_short}")

    # ── Career Checklist (5-step decision tree) ───────────────────────────────
    cc = domain_report.get("career_checklist", {})
    if cc and isinstance(cc, dict) and "career_score" in cc:
        print(section("CAREER DECISION TREE (5-Step Checklist)"))
        print(f"  Direction    : {cc.get('career_direction','?')}")
        print(f"  Career Score : {cc.get('career_score',0):.0%}")
        print(f"  Soul Alignment (AK-AmK): {cc.get('soul_alignment','?')}")
        print(f"  D10 Sustainability  : {cc.get('d10_sustainability','?')}")
        print(f"  Dasha Activated     : {'YES' if cc.get('current_dasha_active') else 'NO'}")
        print(f"  Double Transit      : {'YES - MAJOR EVENT IMMINENT' if cc.get('double_transit_active') else 'NO'}")
        karmic = cc.get("karmic_skills", [])
        if karmic:
            print(f"  Karmic Skills (D3) : {karmic[0][:70]}")
        for note in cc.get("notes", [])[:3]:
            if len(note) > 10:
                print(f"    → {note[:90]}")

    # ── Bhavabala Domain Modifier ─────────────────────────────────────────────
    bh_mod = domain_report.get("bhavabala_domain_modifier", {})
    if bh_mod and isinstance(bh_mod, dict):
        bh_bottleneck = bh_mod.get("bottleneck_house")
        bh_boost      = bh_mod.get("boost_house")
        bh_cm         = bh_mod.get("confidence_modifier", 0.0)
        if bh_bottleneck or bh_boost:
            print(f"\n  Bhavabala Domain Modifier: {bh_cm:+.2f}")
            if bh_bottleneck:
                print(f"    Bottleneck: H{bh_bottleneck} (WEAK) — limits domain delivery")
            if bh_boost:
                print(f"    Boost: H{bh_boost} (HIGH) — amplifies domain results")

    # ── Retrograde Dasha Lord Analysis ───────────────────────────────────────
    retro_dasha = domain_report.get("retrograde_dasha", {})
    if retro_dasha and isinstance(retro_dasha, dict) and retro_dasha.get("is_retrograde"):
        print(section(f"RETROGRADE DASHA LORD — {retro_dasha.get('planet','?')}"))
        print(f"  Effective Dignity : {retro_dasha.get('effective_dignity','?')}")
        print(f"  {retro_dasha.get('dignity_note','')}")
        print(f"  Trajectory : {retro_dasha.get('trajectory','?')}")
        traj_note = retro_dasha.get('trajectory_note', '')
        if traj_note:
            print(f"    {traj_note[:100]}")
        if retro_dasha.get("prev_house_effect_active"):
            print(f"  Previous house H{retro_dasha.get('prev_house','?')} effect ACTIVE "
                  f"(planet at {retro_dasha.get('degree_in_sign',0):.1f}° — within 0-10° threshold)")
        if retro_dasha.get("station_trigger"):
            print(f"  [!!!] {retro_dasha.get('station_note','')[:120]}")

    # ── Shadvarga Vimshopak summary ───────────────────────────────────────────
    shad = domain_report.get("shadvarga_vimshopak", {})
    if shad and isinstance(shad, dict):
        import vedic_engine.prediction.engine as _eng
        _dasha = domain_report.get("dasha", {})
        _md = _dasha.get("maha_dasha", "")
        _ad = _dasha.get("antar_dasha", "")
        for _lord in [_md, _ad]:
            if _lord and _lord in shad:
                sv = shad[_lord]
                if isinstance(sv, dict) and "total" in sv:
                    sv_score = sv.get("total", 0.0)
                    sv_tier  = sv.get("tier", "?")
                    print(f"\n  Shadvarga Vimshopak [{_lord}]: {sv_score:.2f}/20  [{sv_tier}]")

    # ── Graha Yuddha (Planetary War) in natal chart ───────────────────────────
    graha_wars = domain_report.get("graha_yuddha", [])
    if graha_wars and isinstance(graha_wars, list):
        print("\n  GRAHA YUDDHA (Planetary War):")
        for war in graha_wars[:4]:  # show up to 4 wars
            if isinstance(war, dict):
                v = war.get("victor", "?")
                d = war.get("defeated", "?")
                sev = war.get("severity", "?")
                orb = war.get("orb_deg", 0)
                print(f"    {v} defeats {d}  [{sev}, {orb:.2f}° orb] — {d}'s yogas reduced")

    # ── Dhana Stacking Tier ───────────────────────────────────────────────────
    dhana_st = domain_report.get("dhana_stacking", {})
    if dhana_st and isinstance(dhana_st, dict) and dhana_st.get("wealth_tier", "none") != "none":
        tier   = dhana_st.get("wealth_tier", "?").upper()
        n_d    = dhana_st.get("dhana_count", 0)
        pariv  = dhana_st.get("parivartana_2_11", False)
        dharma = dhana_st.get("dharma_integrated", False)
        print(f"\n  Dhana Stacking: {n_d} Dhana Yoga(s) → Wealth Tier: [{tier}]")
        if pariv:
            print("    Parivartana 2L↔11L: maximum wealth circuit active")
        if dharma:
            print("    5th/9th lord integrated into 2-11 axis: dharmic prosperity")
        ceiling = dhana_st.get("ceiling_note", "")
        if ceiling:
            print(f"    CEILING: {ceiling[:100]}")



    # ── Tajika Varshaphala and further chart sections moved to print_chart_sections()


# ─── Chart-Level Sections (printed once, not per domain) ─────────────────────

def print_chart_sections(domain_report: dict):
    """Print chart-level sections that are the same regardless of domain."""

    # ── Nakshatra Analysis (File 2) ───────────────────────────────────────────
    nak_data = domain_report.get("nakshatra_analysis", {})
    if nak_data and isinstance(nak_data, dict):
        print("\n  ── NAKSHATRA ANALYSIS ──")
        tara = nak_data.get("tarabala", {})
        if tara:
            tara_name = tara.get("tara_name", "?")
            tara_num  = tara.get("tara_num", "?")
            nature    = tara.get("nature", "?")
            mult      = tara.get("multiplier", 0)
            eff_mult  = tara.get("effective_multiplier", mult)
            paryaya   = tara.get("paryaya_cycle")
            flag = "⚠ NAIDHANA — avoid major decisions" if tara.get("is_highly_negative") else ""
            print(f"  Tarabala: Tara {tara_num} ({tara_name}) — {nature}  "
                f"[multiplier {mult:+.2f}, effective {eff_mult:+.2f}]  {flag}")
            if paryaya in (1, 2, 3):
                decay = tara.get("paryaya_malefic_decay", 1.0)
                print(f"    Paryaya cycle: {paryaya}  (malefic decay ×{decay:.2f})")
        chandra = nak_data.get("chandrabala", {})
        if chandra:
            house_fm = chandra.get("house_from_natal_moon", "?")
            qtier    = chandra.get("quality_tier", "?")
            score    = chandra.get("score", 0)
            print(f"  Chandrabala: House {house_fm} from natal Moon — "
                  f"{qtier}  [score {score:.2f}]")
            note = chandra.get("chandrabala_note", "")
            if note and qtier in ("severe", "favorable_exception"):
                print(f"    {note}")
        moon_pada = nak_data.get("moon_naming_star", {})
        if moon_pada:
            nak_name = moon_pada.get("nakshatra", "?")
            pada_n   = moon_pada.get("pada", "?")
            syllable = moon_pada.get("syllable", "?")
            tatwa    = moon_pada.get("tatwa", "?")
            dosha    = moon_pada.get("dosha", "?")
            purpose  = moon_pada.get("purpose", "?")
            print(f"  Natal Moon: {nak_name} pada {pada_n}  "
                  f"Bija Akshara: '{syllable}'  "
                  f"[{tatwa} / {dosha} / {purpose}]")
        vargo = nak_data.get("vargottama_planets", [])
        if vargo:
            print(f"  Vargottama Planets: {', '.join(vargo)}  "
                  f"[D1=D9 sign — amplified natural expression]")
        pushkara = nak_data.get("pushkara_planets", {})
        if pushkara:
            for pname, pk in pushkara.items():
                mult = pk.get("multiplier", 1)
                eff_mult = pk.get("effective_multiplier", mult)
                label = "PUSHKARA BHAGA (3×)" if pk.get("is_pushkara_bhaga") else "Pushkara Navamsa (2×)"
                dusthana_note = " [dusthana nullified]" if pk.get("dusthana_nullified") else ""
                print(f"  {pname}: {label}  [raw {mult:.2f}×, effective {eff_mult:.2f}×]{dusthana_note}"
                      f"  — {pk.get('note', '')[:80]}")
        pk_diag = nak_data.get("pushkara_diagnostic", {})
        if pk_diag and isinstance(pk_diag, dict) and pk_diag.get("planet_count", 0) > 0:
            print(f"  Pushkara A/B : raw={pk_diag.get('raw_factor', 1.0):.2f}×  "
                  f"effective={pk_diag.get('effective_factor', 1.0):.2f}×  "
                  f"delta={pk_diag.get('a_b_delta', 0.0):+.2f}")
        dwi = nak_data.get("dwisaptati", {})
        if dwi and dwi.get("eligible"):
            print(f"\n  DWISAPTATI SAMA DASHA ACTIVE — 72-year cycle")
            print(f"    Reason: {dwi.get('reason', '')}")
            print(f"    Planets: {', '.join(dwi.get('dasha_planets', []))}")

    # ── Tajika Varshaphala (File 3) ───────────────────────────────────────────
    vp_data = domain_report.get("varshaphala", {})
    if vp_data and not vp_data.get("error"):
        print("\n  ── TAJIKA VARSHAPHALA ──")

        # Muntha
        muntha = vp_data.get("muntha", {})
        if muntha:
            print(f"  Muntha      : {muntha.get('sign','?')} "
                  f"({muntha.get('degree_in_sign',0):.1f}°) "
                  f"— Lord: {muntha.get('lord','?')}")
            print(f"    {muntha.get('interpretation','')}")

        # Varsha Pati
        vp = vp_data.get("varsha_pati", {})
        if vp:
            print(f"  Varsha Pati : {vp.get('varsha_pati','?')}  "
                  f"({vp.get('role','')})  "
                  f"PVB={vp.get('pvb',0):.1f} [{vp.get('tier','')}]")

        # PVB summary (top 3 strongest planets)
        pvb_all = vp_data.get("pvb", {})
        if pvb_all:
            ranked = sorted(pvb_all.items(), key=lambda x: -x[1]["pvb"])[:3]
            pvb_strs = [f"{p}={d['pvb']:.1f}({d['tier'][0]})" for p, d in ranked]
            print(f"  PVB Leaders : {', '.join(pvb_strs)}")

        # Tajika Yogas
        yogas = vp_data.get("tajika_yogas", [])
        if yogas:
            print(f"\n  Tajika Yogas ({len(yogas)} detected):")
            quality_order = {"very_good": 0, "good": 1, "mixed": 2, "bad": 3, "very_bad": 4}
            for y in sorted(yogas, key=lambda x: quality_order.get(x.get("quality","mixed"),2))[:6]:
                q_sym = {"very_good":"✦","good":"◆","mixed":"◇","bad":"●","very_bad":"✖"}.get(
                    y.get("quality","?"),"?")
                pl = "+".join(y.get("planets",[]))[:30]
                print(f"    {q_sym} {y['yoga']:<18} [{pl}]: {y['description'][:55]}")

        # Active Sahams
        active_sahams = vp_data.get("active_sahams", [])
        if active_sahams:
            print(f"\n  Active Sahams ({len(active_sahams)} activated):")
            for s in active_sahams[:5]:
                print(f"    {s['name']:<12} — {s['significance']}  "
                      f"(lord {s['lord']}, sep {s['itthasala_sep']:.1f}°)")

        # Mudda Dasha
        mudda = vp_data.get("mudda_dasha", {})
        current = mudda.get("current") if mudda else None
        if current:
            print(f"\n  Mudda Dasha : {current['lord']}  "
                  f"{current['start_date']} → {current['end_date']}  "
                  f"({current['days']:.0f} days)")
            # Show next 3 periods
            seq = mudda.get("sequence", [])
            if len(seq) > 1:
                ci = next((i for i, p in enumerate(seq) if p["lord"] == current["lord"]
                           and p["start_date"] == current["start_date"]), 0)
                upcoming = seq[ci+1:ci+4]
                if upcoming:
                    nxt = "  ".join(f"{p['lord']}({p['start_date'][:7]})" for p in upcoming)
                    print(f"    Next: {nxt}")

    # ── Jaimini Extended (File 4) ───────────────────────────────────────────────
    je = domain_report.get("jaimini_extended", {})
    if je:
        print("\n  ── JAIMINI EXTENDED ANALYSIS ──")

        # Sthira Karakas
        sk = je.get("sthira_karakas", {})
        if sk:
            k_map = sk.get("karakas", {})
            print(f"\n  Sthira Karakas (Ayur Dasha use only):")
            print(f"    Father: {k_map.get('father','?')}  "
                  f"Mother: {k_map.get('mother','?')}  "
                  f"Longevity: {k_map.get('elder_sibling_longevity','SATURN')}")

        # Svamsha + Karakamsha
        sv = je.get("svamsha", {})
        km = je.get("karakamsha", {})
        if sv:
            print(f"\n  Svamsha     : AK in {sv.get('sign_name','?')} Navamsha")
            print(f"    {sv.get('indication','')[:90]}")
        if km:
            print(f"  Karakamsha  : {km.get('karakamsha_sign','?')} (D-1 rotated) — "
                  f"Ishta Devata: {km.get('ishta_devata','?')}  "
                  f"Moksha Yoga: {'YES' if km.get('moksha_yoga') else 'No'}")
            if km.get("profession_indicator"):
                print(f"    10th Lord (career indicator): {km['profession_indicator']}")

        # Jaimini Yogas
        jy = je.get("jaimini_yogas", [])
        if jy:
            print(f"\n  Jaimini Yogas ({len(jy)} detected):")
            for y in jy[:5]:
                strength_sym = {"very high":"★★★","high":"★★","absolute":"★★★","extraordinary":"★★★"}.get(
                    y.get("strength",""), "★")
                planets_str = "+".join(y.get("planets", []))[:25]
                print(f"    {strength_sym} {y['name'][:38]:<38} [{planets_str}]")
                print(f"       {y['meaning'][:80]}")

        # Arudha Extended
        ae = je.get("arudha_extended", {})
        if ae:
            print(f"\n  AL-UL Analysis:")
            print(f"    AL={ae.get('al_sign','?')}  UL={ae.get('ul_sign','?')}  "
                  f"A10={ae.get('a10_sign','?')}")
            verdict = ae.get("al_ul_verdict","")
            verdict_sym = {"SUSTAINABLE":"✓","FRICTION":"✗","NEUTRAL":"~"}.get(verdict, verdict)
            print(f"    Marriage Axis: {verdict_sym} {verdict} — {ae.get('al_ul_note','')[:65]}")
            if ae.get("node_affliction"):
                print(f"    ⚠ {ae.get('node_note','')[:85]}")
            print(f"    A10 Career Reputation: {ae.get('a10_reputation','')[:70]}")
            if ae.get("contraargala_note"):
                print(f"    Contraargala: {ae.get('contraargala_note','')[:75]}")

        # Additional Jaimini Dashas summary
        dasha_keys = [
            ("shoola_dasha",  "Shoola  "),
            ("niryana_shoola","Niryana "),
            ("brahma_dasha",  "Brahma  "),
            ("navamsha_dasha","Navamsha"),
            ("sudasa",        "Sudasa  "),
            ("drig_dasha",    "Drig    "),
            ("trikona_dasha", "Trikona "),
        ]
        print(f"\n  Additional Jaimini Dasha Systems:")
        for key, label in dasha_keys:
            dd = je.get(key, {})
            if dd:
                start_sign = (dd.get("start_sign")
                              or dd.get("brahma_sign")
                              or dd.get("sree_lagna_sign")
                              or dd.get("ninth_house")
                              or dd.get("d9_lagna")
                              or "?")
                periods = dd.get("periods", [])
                active_label = ""
                if periods:
                    first_p = periods[0]
                    active_label = f"[{first_p.get('sign_name','?')} {first_p.get('years','?')}yr]"
                rudra = dd.get("rudra","") or dd.get("brahma_planet","") or dd.get("prani_rudra","")
                rudra_info = f" | Rudra={rudra}" if rudra else ""
                print(f"    {label}: starts {start_sign}{rudra_info}  {active_label}")

    # ── File 5: Kalachakra, Medical, Conditional Dashas ────────────────────────
    f5 = domain_report.get("file5_analysis", {})
    if f5 and not f5.get("error"):
        print(banner("FILE 5: KALACHAKRA · MEDICAL · CONDITIONAL DASHAS"))

        # ─ Kalachakra ────────────────────────────────────────────────────────
        kc = f5.get("kalachakra", {})
        if kc:
            print(f"\n  ── KALACHAKRA DASHA ──")
            print(f"  Direction   : {kc.get('direction','?')} | Group {kc.get('group','?')} | Pada {kc.get('pada','?')}")
            print(f"  Paramayus   : {kc.get('paramayus','?')} years | Deha: {kc.get('deha_sign','?')} | Jeeva: {kc.get('jeeva_sign','?')}")
            kc_periods = kc.get("periods", [])[:5]
            for kp_item in kc_periods:
                tag = ""
                if kp_item.get("is_deha"):
                    tag += " [DEHA]"
                if kp_item.get("is_jeeva"):
                    tag += " [JEEVA]"
                gati = f" ← {kp_item['gati']}" if kp_item.get("gati") else ""
                print(f"    {kp_item.get('maha_sign','?'):14} {kp_item.get('full_years','?'):2}yr{tag}{gati}")

        djt = f5.get("deha_jeeva_transits", {})
        if djt:
            verdict_dj = djt.get("verdict", "")
            if "ALERT" in verdict_dj or "CRITICAL" in verdict_dj:
                print(f"\n  ⚠ Deha/Jeeva Transit: {verdict_dj}")

        # ─ Medical Analysis ────────────────────────────────────────────────
        med = f5.get("medical", {})
        if med:
            print(f"\n  ── MEDICAL ANALYSIS ──")
            # Disease alerts
            alerts = med.get("disease_alerts", [])
            if alerts:
                print(f"  Disease Alerts ({len(alerts)} detected):")
                for al in alerts[:4]:
                    sev = al.get("severity","")
                    print(f"    [{sev:8}] {al.get('condition','?')}")
                    print(f"             {al.get('trigger','')}")
            else:
                print(f"  Disease Alerts: None detected (strong chart)")

            # 22nd Drekkana
            d22 = med.get("drekkana_22", {})
            if d22:
                print(f"  22nd Drekkana : {d22.get('khara_sign','?')} (lord: {d22.get('lord','?')}) {d22.get('zodiac_span','')}")

            # Balarishta
            bal = med.get("balarishta", {})
            if bal and bal.get("balarishta"):
                print(f"  ⚠ Balarishta  : {bal.get('verdict','')}")

            # Longevity — classical bands with ethical disclaimer
            lon = med.get("longevity", {})
            if lon:
                if lon.get("final_estimate_years"):
                    _yrs = float(lon.get('final_estimate_years', 0))
                    # Classical Alpa/Madhya/Purna longevity bands
                    if _yrs < 32:
                        _band = "Alpa Ayus (Short)"
                    elif _yrs < 75:
                        _band = "Madhya Ayus (Medium)"
                    else:
                        _band = "Purna Ayus (Full)"
                    print(f"  Longevity Band: {_band}  ({lon.get('method_used', '?')})")
                    print(f"    ⚠ Classical estimate only — NOT a medical prognosis.")
                    print(f"    Pindayu / Nisargayu / Amsayu median yields this band.")
                else:
                    print(f"  Longevity     : {lon.get('note','Balarishta override')}")

        # ─ Conditional Dashas ──────────────────────────────────────────────
        cond_elig = f5.get("conditional_eligibility", {})
        cond_dashas = f5.get("conditional_dashas", {})
        if cond_elig:
            print(f"\n  ── CONDITIONAL DASHA ELIGIBILITY ──")
            for sys_name, elig_data in cond_elig.items():
                mark = "✓" if elig_data.get("eligible") else "✗"
                print(f"    {mark} {sys_name:20} {elig_data.get('reason','')}")

        if cond_dashas:
            print(f"\n  Active Conditional Dasha Systems:")
            _COND_DISPLAY = [
                ("shodashottari","Shodashottari (116yr)"),
                ("dwadasottari",  "Dwadasottari  (112yr)"),
                ("panchottari",   "Panchottari   (105yr)"),
                ("shatabdika",    "Shatabdika    (100yr)"),
                ("chaturaashiti", "Chaturaashiti ( 84yr)"),
                ("dwisaptati",    "Dwisaptati    ( 72yr)"),
                ("shat_trimsa",   "Shat Trimsa   ( 36yr)"),
                ("moola_dasha",   "Moola Dasha   (var yr)"),
                ("tara_dasha",    "Tara Dasha    (120yr)"),
            ]
            for ckey, clabel in _COND_DISPLAY:
                cd = cond_dashas.get(ckey)
                if cd:
                    cperiods = cd.get("periods", [])
                    start_planet = (cd.get("starting_planet")
                                    or (cperiods[0].get("planet") if cperiods else "?")
                                    or "?")
                    if cperiods:
                        fp = cperiods[0]
                        first_info = f"{fp.get('planet',fp.get('maha_sign','?'))} {fp.get('years','?')}yr"
                    else:
                        first_info = "?"
                    tara_q = ""
                    if ckey == "tara_dasha" and cperiods:
                        tara_q = f" [{cperiods[0].get('tara_quality','?')}]"
                    print(f"    {clabel}: starts {start_planet} → {first_info}{tara_q}")





# ─── AI Reading (GPT) ─────────────────────────────────────────────────────────


def _ai_section(title: str) -> str:
    line = "═" * 70
    return f"\n{line}\n  GPT-4o — {title}\n{line}"


def print_ai_reading(
    static: dict,
    dynamic: dict,
    domain_reports: list,
    domains: list,
    interpreter,
) -> None:
    """Print GPT narrative sections appended after the mathematical report."""
    print(banner("GPT-4o NARRATIVE INTERPRETATION"))

    if not interpreter.available:
        print(f"\n  [!] {interpreter._error}")
        print("  Set the key (PowerShell): $env:OPENAI_API_KEY = 'sk-...'")
        print("  Set the key (bash/zsh) : export OPENAI_API_KEY='sk-...'")
        return

    # 1. Natal overview
    print(_ai_section("NATAL CHART"))
    print("  [Calling GPT…]", end="\r", flush=True)
    natal_text = interpreter.interpret_natal(static)
    print(" " * 20, end="\r")
    for line in natal_text.split("\n"):
        if line.strip():
            print(textwrap.fill(line, width=68, initial_indent="  ", subsequent_indent="  "))
        else:
            print()

    # 2. Timing synthesis
    print(_ai_section("CURRENT TIMING"))
    print("  [Calling GPT…]", end="\r", flush=True)
    timing_text = interpreter.synthesize_timing(dynamic)
    print(" " * 20, end="\r")
    for line in timing_text.split("\n"):
        if line.strip():
            print(textwrap.fill(line, width=68, initial_indent="  ", subsequent_indent="  "))
        else:
            print()

    # 3. Domain interpretations
    for dr in domain_reports:
        dom = dr.get("domain", "?").upper()
        print(_ai_section(f"{dom} DOMAIN"))
        print(f"  [Calling GPT for {dom}…]", end="\r", flush=True)
        dom_text = interpreter.interpret_domain(dr, static, dynamic)
        print(" " * 30, end="\r")
        for line in dom_text.split("\n"):
            if line.strip():
                print(textwrap.fill(line, width=68, initial_indent="  ", subsequent_indent="  "))
            else:
                print()

    print("\n" + "═" * 70)
    print("  Mathematical data: Vedic Engine  |  Narrative: OpenAI GPT-4o")
    print("═" * 70 + "\n")


# ─── Main ─────────────────────────────────────────────────────────

def main():
    # ── Parse args  (strip --ai flag before positional parsing)
    args   = sys.argv[1:]
    use_ai = "--ai" in args
    args   = [a for a in args if a != "--ai"]

    chart_path    = args[0] if args else None
    date_str      = args[1] if len(args) > 1 else None
    single_domain = args[2] if len(args) > 2 else None

    on_date = datetime.now()
    if date_str and date_str.lower() != "today":
        try:
            on_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print(f"[!] Invalid date '{date_str}', using today.")

    # ── Load chart
    if chart_path:
        with open(chart_path, "r", encoding="utf-8") as f:
            chart_data = json.load(f)
        chart = load_from_dict(chart_data)
        print(f"[Chart loaded from: {chart_path}]")
    else:
        # Default: compute positions via Swiss Ephemeris (gold standard)
        try:
            chart = build_chart_swe(
                name="Chart Subject",
                date_str="1994-02-27",
                time_str="06:30:00",
                place="India",
                latitude=20.5937,
                longitude=78.9629,
                tz_offset=5.5,
            )
            if chart.metadata.get("engine") == "pyswisseph":
                print("[Chart computed via Swiss Ephemeris (SWE-powered)]")
            else:
                print("[Using built-in sample chart (Gemini lagna)]")
        except Exception as exc:
            chart = load_sample_chart()
            print(f"[SWE unavailable ({exc}); using hardcoded sample chart]")

    print(f"[Analysis date: {on_date.strftime('%d %b %Y')}]")

    # ── Provenance header (what computed the positions)
    meta = getattr(chart, "metadata", {})
    if meta:
        ayan_lbl = meta.get("ayanamsa_model", "?").capitalize()
        ayan_val = meta.get("ayanamsa_value", "?")
        ayan_str = f"{ayan_lbl} ({ayan_val:.4f}°)" if isinstance(ayan_val, (int, float)) else ayan_lbl
        node_lbl = "True" if meta.get("use_true_node") else "Mean"
        print(f"[Engine: {meta.get('engine', '?')}  |  "
              f"Ayanamsa: {ayan_str}  |  "
              f"Houses: {meta.get('house_system', '?').capitalize()}  |  "
              f"Nodes: {node_lbl}]")
    if use_ai:
        print("[AI mode: GPT-4o narrative interpretation enabled]")

    # ── Run engine
    engine = PredictionEngine()

    print("\nComputing static analysis …", end=" ", flush=True)
    static = engine.analyze_static(chart)
    print("done.")

    print("Computing dynamic analysis …", end=" ", flush=True)
    dynamic = engine.analyze_dynamic(chart, static, on_date)
    print("done.")

    # ── Print mathematical reports
    print_static_summary(static)
    print_dynamic_summary(dynamic)

    if single_domain:
        domains_to_show = [single_domain.lower()]
    else:
        domains_to_show = ["career", "finance", "marriage", "health"]

    print(banner("DOMAIN PREDICTIONS"))
    domain_reports_list = []
    for domain in domains_to_show:
        report = engine.predict(chart, domain, on_date, static)
        domain_reports_list.append(report)

    # Chart-level sections printed once (same data regardless of domain)
    if domain_reports_list:
        print_chart_sections(domain_reports_list[0])

    # Per-domain prediction reports
    for report in domain_reports_list:
        print_domain_report(report)

    # ── GPT AI narrative (only when --ai flag is passed)
    if use_ai:
        if not _AI_MODULE_AVAILABLE:
            print("\n[!] vedic_engine.ai module could not be loaded.")
        else:
            ai = VedicInterpreter()   # reads OPENAI_API_KEY from environment
            print_ai_reading(static, dynamic, domain_reports_list, domains_to_show, ai)

    # ── Footer
    print("\n" + "=" * 70)
    print("  Vedic Astrology Engine | github.com/vedic-engine")
    print("  Results are computed mathematically; consult a jyotishi for interpretation.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
