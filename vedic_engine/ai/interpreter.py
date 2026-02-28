"""
Vedic Engine — GPT Interpretation Layer
========================================
Converts the engine's structured numerical output into rich, personalized
Vedic astrology narratives using OpenAI GPT-4o.

All interpretation functions gracefully degrade: if no API key is set,
they return a fallback message instead of raising an exception.

Usage:
    from vedic_engine.ai.interpreter import VedicInterpreter

    vi = VedicInterpreter()                        # reads OPENAI_API_KEY from env
    vi = VedicInterpreter(api_key="sk-...")        # or pass directly
    vi = VedicInterpreter(model="gpt-4.1")        # override model

    text = vi.interpret_natal(static)
    text = vi.interpret_domain(domain_report, static, dynamic)
    text = vi.synthesize_timing(dynamic)
    text = vi.chat(static, dynamic, "Will I change jobs this year?")
    text = vi.full_reading(static, dynamic, domain_reports)
"""
from __future__ import annotations

import os
import json
from typing import Dict, Any, List, Optional

# ─── OpenAI client (optional dependency) ───────────────────────────────────
try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

SIGN_NAMES = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
]

PLANET_SYMBOLS = {
    "SUN":"Sun","MOON":"Moon","MARS":"Mars","MERCURY":"Mercury",
    "JUPITER":"Jupiter","VENUS":"Venus","SATURN":"Saturn","RAHU":"Rahu","KETU":"Ketu",
}

_SYSTEM_PROMPT = """You are an expert Vedic astrologer (Jyotishi) with deep knowledge of:
- Classical Parashari and Jaimini systems
- All 6 Shadbala components, Ashtakvarga, Bhavabala, Vimshopak dignities
- Vimshottari, Yogini, Ashtottari, and Chara dasha systems
- Yogas (Raj, Dhana, Viparita, Panchamahapurusha, etc.)
- Gochar (transit) evaluation against natal moon and Ashtakvarga bindus
- KP (Krishnamurti Paddhati) sublord significations
- Jaimini: Chara Karakas, Arudha Padas, Rashi Drishti, Upapada Lagna

Your role is INTERPRETATION and SYNTHESIS, not calculation. The numerical data
is already computed by a precise mathematical engine. Your job is to:
1. Weave the numbers into a coherent, personalized narrative
2. Identify the most important themes from the data
3. Prioritize insights by strength/certainty — don't just list everything
4. Be specific with timing references (dasha periods, transit windows)
5. Balance positive and challenging indications honestly
6. Write in clear, accessible English — no jargon dumps

IMPORTANT RULES:
- Do NOT invent planetary positions or data not given to you
- Do NOT flatly promise outcomes — use language like "strong indication", "period favors", "tendency toward"
- Keep responses focused: 200-350 words per section unless instructed otherwise
- If a domain confidence score < 40%, lead with the caveats
"""

# ─── Context Builders ──────────────────────────────────────────────────────

def _fmt_sign(idx) -> str:
    try:
        return SIGN_NAMES[int(idx) % 12]
    except Exception:
        return str(idx)


def build_natal_context(static: Dict[str, Any]) -> str:
    """Distill static analysis into a compact text block for GPT context."""
    meta    = static.get("meta", {})
    raw     = static.get("chart_raw", {})
    lagna   = _fmt_sign(meta.get("lagna_sign", 0))
    moon    = _fmt_sign(meta.get("moon_sign", 0))
    p_lons  = raw.get("planet_lons", {})
    p_houses= raw.get("planet_houses", {})
    retro   = raw.get("retrogrades", {})
    sha_r   = static.get("shadbala_ratios", {})

    # Planet table
    planet_lines = []
    for pname, lon in p_lons.items():
        sign = _fmt_sign(int(float(lon)) // 30)
        house = p_lons and p_houses.get(pname, "?")
        r_tag = " [R]" if retro.get(pname) else ""
        strength = sha_r.get(pname, None)
        s_tag = f"  Shadbala={strength:.2f}x" if strength else ""
        planet_lines.append(f"  {pname}: {sign} H{house}{r_tag}{s_tag}")

    # Yogas
    yogas = static.get("yogas", [])
    yoga_names = [y.get("name","?") for y in yogas[:8]] if isinstance(yogas, list) else []

    # Karakas
    karakas_list = static.get("karakas", {}).get("list", [])
    karaka_lines = []
    for k in karakas_list[:7]:
        karaka_lines.append(f"  {k.get('karaka','?')}: {k.get('planet','?')}")

    # Functional
    func = static.get("functional", {})
    yks  = func.get("yogakarakas", [])
    fms  = func.get("functional_malefics", [])
    bad  = func.get("badhaka","")

    # Ashtakvarga
    av = static.get("ashtakvarga", {})
    sarva = av.get("sarva", [])
    sarva_total = av.get("sarva_total", sum(sarva) if sarva else 0)

    # Arudha Padas
    ap = static.get("arudha_padas", {})
    al_sign = ap.get("al_sign", "?")
    ul_sign = ap.get("ul_sign", "?")
    a10_sign= ap.get("a10_sign","?")

    # Dispositor
    disp = static.get("dispositor_graph", {})
    final_disp = disp.get("final_dispositors", [])

    # Special points
    sp = static.get("special_points", {})
    yogi_pt   = sp.get("yogi_point", {})
    gulika    = sp.get("gulika", {})

    lines = [
        f"NATAL CHART — Lagna: {lagna}, Moon: {moon}",
        "",
        "PLANET POSITIONS (sign, house, retrograde, Shadbala ratio vs minimum):",
        *planet_lines,
        "",
        f"ACTIVE YOGAS ({len(yoga_names)} detected): {', '.join(yoga_names) if yoga_names else 'None'}",
        "",
        "JAIMINI CHARA KARAKAS:",
        *karaka_lines,
        "",
        f"FUNCTIONAL ROLES (Lagna={lagna}):",
        f"  Yogakaraka(s): {', '.join(yks) or 'None'}",
        f"  Functional Malefics: {', '.join(fms) or 'None'}",
        f"  Badhaka lord: {bad or 'None'}",
        "",
        f"SARVASHTAKVARGA total: {sarva_total}/337",
        f"  Sign scores: { {SIGN_NAMES[i]: s for i, s in enumerate(sarva)} if sarva else 'N/A' }",
        "",
        "ARUDHA PADAS (Jaimini public image):",
        f"  Arudha Lagna (AL): {al_sign}",
        f"  Upapada Lagna (UL/marriage): {ul_sign}",
        f"  A10 (career image): {a10_sign}",
        "",
        f"Final dispositor(s): {', '.join(str(d) for d in final_disp) if final_disp else disp.get('final_dispositor','?')}",
        f"Yogi planet: {yogi_pt.get('planet','?')}  Gulika in: {gulika.get('sign_name','?')}",
    ]
    return "\n".join(lines)


def build_dynamic_context(dynamic: Dict[str, Any]) -> str:
    """Distill dynamic (timing) analysis into compact text."""
    vim = dynamic.get("vimshottari", {})
    active = vim.get("active", {})
    sandhi = vim.get("sandhi", {})

    if isinstance(active, dict):
        md = active.get("mahadasha", active.get("planet","?"))
        ad = active.get("antardasha","?")
        pd = active.get("pratyantardasha","")
    elif isinstance(active, list) and active:
        md = active[0].get("planet","?")
        ad = active[1].get("planet","?") if len(active) > 1 else "?"
        pd = active[2].get("planet","?") if len(active) > 2 else ""
    else:
        md = ad = pd = "?"

    in_sandhi = sandhi.get("in_sandhi", False) if isinstance(sandhi, dict) else False

    # Chara Dasha
    chara = dynamic.get("chara_dasha", {})
    ch_active = chara.get("active", {})
    ch_md = ch_active.get("mahadasha", "?")
    ch_ad = ch_active.get("antardasha", {})
    ch_ad_sign = ch_ad.get("sign","?") if isinstance(ch_ad, dict) else "?"
    ch_dir = chara.get("direction","?")

    # Yogini
    yog_active = dynamic.get("yogini", {}).get("active", {})
    yogini_name = yog_active.get("major_yogini", yog_active.get("yogini","?"))

    # Transits (summary)
    tr = dynamic.get("transits", {})
    transit_pos = dynamic.get("transit_positions", {})
    tr_lines = []
    for planet, tdata in (tr.items() if isinstance(tr, dict) else []):
        if isinstance(tdata, dict) and "score" in tdata:
            score = tdata.get("score", 0)
            house = tdata.get("from_moon_house","?")
            if abs(score) > 0.3:
                tr_lines.append(f"  {planet} transit score={score:+.2f}  H{house} from Moon")

    # Sade Sati
    ss = dynamic.get("sade_sati", {})
    ss_active = ss.get("in_sade_sati", False) or ss.get("in_dhaiya", False)
    ss_phase  = ss.get("phase","") if ss_active else "None"

    # Panchanga
    panch = dynamic.get("panchanga", {})
    tithi = panch.get("tithi", {}).get("name","?")
    nakshatra = panch.get("nakshatra", {}).get("name","?")
    timing_q = panch.get("timing_quality","?")
    timing_s = panch.get("timing_score", 0.0)

    # Dasha transit
    dt = dynamic.get("dasha_transit", {})
    dt_md = dt.get("mahadasha_lord_transit","") if isinstance(dt, dict) else ""

    lines = [
        "CURRENT TIMING ANALYSIS",
        "",
        "VIMSHOTTARI DASHA (active periods):",
        f"  Maha-dasha:       {md}",
        f"  Antar-dasha:      {ad}",
        f"  Pratyantar-dasha: {pd}" if pd else "",
        f"  Dasha Sandhi:     {'YES — transitional/unstable period' if in_sandhi else 'No'}",
        "",
        "JAIMINI CHARA DASHA:",
        f"  Direction: {ch_dir}",
        f"  Maha sign: {ch_md}",
        f"  Antar sign: {ch_ad_sign}",
        "",
        f"YOGINI DASHA active: {yogini_name}",
        "",
        "TRANSIT HIGHLIGHTS (score > ±0.30):",
        *([f"  No strong transits" ] if not tr_lines else tr_lines),
        "",
        f"SADE SATI / DHAIYA: {'ACTIVE — ' + ss_phase if ss_active else 'Not active'}",
        "",
        "PANCHANGA (daily quality):",
        f"  Tithi: {tithi}  Nakshatra: {nakshatra}",
        f"  Timing quality: {timing_q} (score {timing_s:+.2f})",
    ]
    return "\n".join(l for l in lines if l is not None)


def build_domain_context(domain_report: Dict[str, Any]) -> str:
    """Distill a domain prediction report into compact text."""
    domain  = domain_report.get("domain","?").upper()
    conf    = domain_report.get("confidence", {})
    score   = conf.get("overall_boosted", conf.get("overall", 0.0))
    level   = conf.get("level","?")
    comps   = conf.get("components", {})

    cal     = domain_report.get("calibrated_confidence", {})
    cal_pct = cal.get("calibrated", score)
    band    = cal.get("reliability_band","?")
    lo, hi  = cal.get("confidence_interval", (cal_pct, cal_pct))

    # Key factors
    factors = domain_report.get("key_factors", [])
    kf_lines = [f"  - {f}" for f in factors[:6]] if factors else []

    # Timing windows
    tw  = domain_report.get("timing_windows", {})
    best  = tw.get("best", [])[:2]
    worst = tw.get("worst", [])[:1]
    tw_lines = []
    for w in best:
        tw_lines.append(f"  BEST:  {w.get('window_start','?')} – {w.get('window_end','?')}  score={w.get('score',0):.2f}")
    for w in worst:
        tw_lines.append(f"  AVOID: {w.get('window_start','?')} – {w.get('window_end','?')}  score={w.get('score',0):.2f}")

    # Dasha lord transit
    dasha_t = domain_report.get("dasha_lord_transit", {})
    dt_md = dasha_t.get("mahadasha_lord","?")
    dt_score = dasha_t.get("transit_score", None)

    lines = [
        f"DOMAIN: {domain}",
        f"  Overall confidence: {score:.1%}  Level: {level}",
        f"  Calibrated:        {cal_pct:.0%}  Band: {band}  CI: {lo:.0%}–{hi:.0%}",
        "",
        "CONFIDENCE COMPONENTS:",
        *[f"  {k}: {v:.2f}" for k, v in comps.items()],
        "",
        "KEY FACTORS:",
        *(kf_lines or ["  (not available)"]),
        "",
        "TIMING WINDOWS (next 12 months):",
        *(tw_lines or ["  (not computed)"]),
        "",
        f"DASHA LORD TRANSIT: {dt_md}" + (f"  transit_score={dt_score:.2f}" if dt_score is not None else ""),
    ]
    return "\n".join(lines)


# ─── Main Interpreter Class ─────────────────────────────────────────────────

class VedicInterpreter:
    """
    GPT-powered natural-language interpreter for Vedic engine output.

    All public methods return a string. If OpenAI is unavailable or the
    API call fails, a descriptive fallback string is returned instead.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        max_tokens: int = 600,
        temperature: float = 0.7,
    ):
        self.model       = model
        self.max_tokens  = max_tokens
        self.temperature = temperature
        self._client     = None

        key = api_key or os.environ.get("OPENAI_API_KEY","")
        if not _OPENAI_AVAILABLE:
            self._error = "openai package not installed. Run: pip install openai"
        elif not key:
            self._error = "OPENAI_API_KEY not set. Export it or pass api_key= to VedicInterpreter()."
        else:
            try:
                self._client = OpenAI(api_key=key)
                self._error  = None
            except Exception as e:
                self._error = f"OpenAI client init failed: {e}"

    @property
    def available(self) -> bool:
        return self._client is not None

    def _call(self, user_message: str, system: str = _SYSTEM_PROMPT,
              max_tokens: Optional[int] = None) -> str:
        """Make a single GPT call. Returns text or an error string."""
        if not self.available:
            return f"[AI unavailable: {self._error}]"
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user_message},
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[GPT call failed: {e}]"

    # ── Public interpretation methods ────────────────────────────────────────

    def interpret_natal(self, static: Dict[str, Any]) -> str:
        """
        Generate a 250-350 word narrative interpretation of the natal chart.
        Covers lagna character, key yogas, planetary strengths, and life themes.
        """
        context = build_natal_context(static)
        prompt = (
            f"Based on the following Vedic chart data, write a 250-350 word natal "
            f"chart interpretation. Highlight the most important themes: lagna lord "
            f"placement, key yogas, atma karaka significance, overall planetary strength "
            f"pattern, and what this chart suggests about the native's core life path "
            f"and character.\n\n"
            f"CHART DATA:\n{context}"
        )
        return self._call(prompt)

    def interpret_domain(
        self,
        domain_report: Dict[str, Any],
        static: Dict[str, Any],
        dynamic: Dict[str, Any],
    ) -> str:
        """
        Generate a focused interpretation for one life domain
        (career, finance, marriage, health).
        """
        domain = domain_report.get("domain","?").upper()
        natal_ctx   = build_natal_context(static)
        timing_ctx  = build_dynamic_context(dynamic)
        domain_ctx  = build_domain_context(domain_report)

        score = domain_report.get("confidence",{}).get("overall_boosted",
                domain_report.get("confidence",{}).get("overall",0.5))

        prompt = (
            f"Interpret the {domain} domain prediction for this chart. "
            f"The mathematical confidence is {score:.0%}. "
            f"Write 200-280 words covering: (1) what the natal chart shows about "
            f"this life area, (2) what the current dasha + transits indicate, "
            f"(3) the best timing window to act, and (4) one key caution.\n\n"
            f"NATAL CHART:\n{natal_ctx}\n\n"
            f"TIMING:\n{timing_ctx}\n\n"
            f"DOMAIN REPORT:\n{domain_ctx}"
        )
        return self._call(prompt, max_tokens=500)

    def synthesize_timing(self, dynamic: Dict[str, Any]) -> str:
        """
        Generate a concise timing overview covering dasha + transit themes.
        """
        timing_ctx = build_dynamic_context(dynamic)
        prompt = (
            f"Write a 200-250 word timing synthesis for the current period. "
            f"Integrate all three dasha systems shown (Vimshottari, Chara, Yogini) "
            f"and the transit highlights into a coherent narrative about what themes "
            f"are active right now, what opportunities or challenges stand out, "
            f"and any important cautions (Sade Sati, sandhi periods).\n\n"
            f"TIMING DATA:\n{timing_ctx}"
        )
        return self._call(prompt)

    def chat(
        self,
        static: Dict[str, Any],
        dynamic: Dict[str, Any],
        question: str,
    ) -> str:
        """
        Answer a specific astrological question about the chart.

        Example questions:
            "Will I get a promotion this year?"
            "What does my 7th house say about marriage timing?"
            "Is Saturn transit good or bad for me right now?"
        """
        natal_ctx  = build_natal_context(static)
        timing_ctx = build_dynamic_context(dynamic)

        prompt = (
            f"The native has the following Vedic chart and timing:\n\n"
            f"NATAL CHART:\n{natal_ctx}\n\n"
            f"CURRENT TIMING:\n{timing_ctx}\n\n"
            f"QUESTION: {question}\n\n"
            f"Answer in 150-250 words. Be specific with reference to the actual "
            f"planetary data. State your confidence level honestly."
        )
        return self._call(prompt, max_tokens=400)

    def full_reading(
        self,
        static: Dict[str, Any],
        dynamic: Dict[str, Any],
        domain_reports: List[Dict[str, Any]],
        include_domains: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        Generate a full multi-section reading.
        Returns a dict: {"natal": str, "timing": str, "career": str, ...}

        Tip: cache the result — each key is a separate GPT call.
        """
        if include_domains is None:
            include_domains = ["career", "finance", "marriage", "health"]

        results: Dict[str, str] = {}

        results["natal"]  = self.interpret_natal(static)
        results["timing"] = self.synthesize_timing(dynamic)

        for dr in domain_reports:
            dom = dr.get("domain","?").lower()
            if dom in include_domains:
                results[dom] = self.interpret_domain(dr, static, dynamic)

        return results

    def __repr__(self) -> str:
        status = f"model={self.model}" if self.available else f"unavailable: {self._error}"
        return f"VedicInterpreter({status})"
