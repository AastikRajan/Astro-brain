"""
GPT Reasoner — Accuracy-improvement layer for the Vedic engine.

Uses GPT-4o-mini in JSON mode to resolve ambiguities and improve accuracy at
4 specific decision points where human/AI reasoning beats hardcoded lookup:

  1. resolve_yoga_fructification  — Is a yoga actually active in THIS dasha?
  2. resolve_dasha_conflict       — When Vimshottari / Chara / Yogini disagree
  3. resolve_kp_ambiguity         — KP sublord signifies both favorable & negator houses
  4. get_adaptive_weights         — Per-chart confidence weight calibration

Design principles:
  - JSON mode only (response_format={"type":"json_object"})
  - GPT-4o-mini (cheaper, ~same quality for structured output)
  - max_tokens = 200-350 per call
  - Results cached (in-memory) per session to avoid redundant API calls
  - Graceful fallback (None / defaults) when openai not installed or API fails
  - These outputs feed DIRECTLY into the math pipeline (not narration)
"""
from __future__ import annotations
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# ─── Attempt OpenAI import ────────────────────────────────────────
try:
    import openai as _openai
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False


# ─── In-memory session cache ──────────────────────────────────────

_CACHE: Dict[str, Any] = {}


def _cache_key(*parts: Any) -> str:
    raw = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.md5(raw.encode()).hexdigest()


def _call_gpt(system_prompt: str, user_prompt: str, max_tokens: int = 280) -> Optional[Dict]:
    """
    Core JSON-mode GPT call with caching and graceful fallback.
    Returns parsed dict or None on failure.
    """
    if not _OPENAI_AVAILABLE:
        return None

    key = _cache_key(system_prompt, user_prompt)
    if key in _CACHE:
        return _CACHE[key]

    try:
        client = _openai.OpenAI()       # uses OPENAI_API_KEY env var
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
            temperature=0.2,            # low temp for consistent structured output
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
        )
        raw = response.choices[0].message.content
        result = json.loads(raw)
        _CACHE[key] = result
        return result
    except Exception as e:
        logger.debug(f"GPT reasoner call failed: {e}")
        return None


# ─── Decision Point 1: Yoga Fructification ────────────────────────

_YOGA_FRUCT_SYSTEM = """You are a Vedic astrology computational assistant.
Analyze whether each yoga can fructify during the given dasha period.
Return ONLY valid JSON in this exact schema:
{
  "yoga_results": [
    {"name": "<yoga_name>", "active": true|false, "strength_multiplier": 0.0-1.5, "reason": "<brief>"}
  ]
}
Rules:
- A yoga fructifies when: dasha lord is a constituent planet OR dasha lord is naturally
  friendly to BOTH constituent planets OR antardasha lord is a constituent.
- strength_multiplier > 1.0 = enhanced; = 1.0 = normal; < 1.0 = muted; 0 = dormant.
- Be concise in reason (max 8 words)."""


def resolve_yoga_fructification(
    yogas: List[Dict],
    dasha_lord: str,
    antardasha_lord: str,
    chart_context: Dict,
) -> Optional[List[Dict]]:
    """
    Ask GPT to evaluate whether each detected yoga is actively fructifying
    in the current dasha/antardasha.

    Returns list of {name, active, strength_multiplier, reason} or None on failure.
    The returned list feeds into score_yoga_activation via multiplier.
    """
    if not yogas:
        return None

    # Build compact context (token-efficient)
    yoga_names = [y.get("name", str(y)) if isinstance(y, dict) else str(y) for y in yogas[:8]]
    user_content = json.dumps({
        "yogas": yoga_names,
        "dasha_lord": dasha_lord,
        "antardasha_lord": antardasha_lord,
        "lagna": chart_context.get("lagna_sign", ""),
        "yogakarakas": chart_context.get("yogakarakas", []),
    }, separators=(",", ":"))

    result = _call_gpt(_YOGA_FRUCT_SYSTEM, user_content, max_tokens=320)
    if result and "yoga_results" in result:
        return result["yoga_results"]
    return None


# ─── Decision Point 2: Multi-Dasha Conflict Resolution ───────────

_DASHA_CONFLICT_SYSTEM = """You are a senior Vedic astrology dasha analyst with deep knowledge of BPHS and Jaimini.
Three dasha systems give different active lords. You MUST synthesize conflicting signals — not cancel them.

Research principle: "Conflicting signals = HOW the event manifests, not WHETHER it manifests."
Example: Vimshottari=Jupiter(career good) + Chara=8th house running →
  Synthesis: "Career success via 8th house themes: crisis management, OPM, transformation, relocation."

Return ONLY valid JSON in this exact schema:
{
  "dominant_system": "vimshottari|chara|yogini",
  "consensus_level": "full|partial|low",
  "weights": {"vimshottari": 0.0-1.0, "chara": 0.0-1.0, "yogini": 0.0-1.0},
  "synthesis": "<How the domain event manifests given all three systems — be specific, 15-30 words>",
  "avenue": "<The mechanism/avenue through which the event occurs>",
  "timing_note": "<Any timing nuance from conflict e.g. 'delayed but strong in mid-period'>",
  "reason": "<Brief reasoning max 10 words>"
}

Rules:
- consensus_level: 'full' if all 3 agree, 'partial' if 2 agree, 'low' if only 1 agrees.
- 'low' consensus AND Vimshottari+Chara both oppose: weights into the event being very muted.
- weights must sum to 1.0. Vimshottari is default primary system.
- synthesis MUST explain HOW the domain manifests through the conflicting houses (never say 'unclear').
- If chara_lord indicates 8th/12th house → 'via transformation/foreign/hidden themes'.
- If yogini disagrees → use as timing modifier, not cancellation.
- Be specific about the avenue (e.g., 'through restructuring role', 'via partner's resources')."""


def resolve_dasha_conflict(
    vim_lord: str,
    chara_lord: str,
    yogini_lord: str,
    lagna_sign: str,
    active_yogas: List[str],
    domain: str,
    chara_house: int = 0,      # Active Chara Dasha house number from lagna
    vim_house: int = 0,        # Active Vimshottari MD lord's natal house
) -> Optional[Dict]:
    """
    When Vimshottari, Chara, and Yogini dasha lords disagree,
    ask GPT to SYNTHESIZE (not cancel) the conflicting signals.

    Key research insight: Conflicting signals indicate HOW the event manifests,
    not whether it manifests. GPT synthesizes the 'avenue': e.g., career success
    coming via 8th house themes (crisis, OPM, transformation) rather than straightforward.

    Returns {dominant_system, consensus_level, weights, synthesis, avenue, timing_note, reason}
    or None on failure.

    The 'synthesis' and 'avenue' fields output human-readable explanation of HOW events occur.
    The 'weights' feed into multi_system_agreement() confidence boost factor.
    """
    if vim_lord == chara_lord == yogini_lord:
        # Full agreement — no conflict; still synthesize for output quality
        return {
            "dominant_system": "vimshottari",
            "consensus_level": "full",
            "weights": {"vimshottari": 0.60, "chara": 0.25, "yogini": 0.15},
            "synthesis": f"All three dasha systems agree on {vim_lord}: {domain} manifests directly.",
            "avenue": "Direct manifestation — no conflicting themes to route through.",
            "timing_note": "High confidence timing.",
            "reason": "Full consensus",
        }

    user_content = json.dumps({
        "vimshottari_lord": vim_lord,
        "vimshottari_lord_natal_house": vim_house,
        "chara_lord": chara_lord,
        "chara_house_from_lagna": chara_house,
        "yogini_lord": yogini_lord,
        "lagna":       lagna_sign,
        "domain":      domain,
        "active_yogas": active_yogas[:5],
    }, separators=(",", ":"))

    result = _call_gpt(_DASHA_CONFLICT_SYSTEM, user_content, max_tokens=350)

    # Fallback: if GPT unavailable, do hardcoded synthesis
    if result is None:
        return _fallback_dasha_synthesis(
            vim_lord, chara_lord, yogini_lord, domain, chara_house
        )
    return result


def _fallback_dasha_synthesis(
    vim_lord: str,
    chara_lord: str,
    yogini_lord: str,
    domain: str,
    chara_house: int = 0,
) -> Dict:
    """
    Hardcoded fallback synthesis when GPT unavailable.
    Implements the Research Brief's basic house-theme synthesis rules.
    """
    agree_count = len({vim_lord, chara_lord, yogini_lord}) == 1
    partial_agree = (vim_lord == chara_lord or vim_lord == yogini_lord or
                     chara_lord == yogini_lord)

    if agree_count:
        consensus = "full"
        weights = {"vimshottari": 0.60, "chara": 0.25, "yogini": 0.15}
    elif partial_agree:
        consensus = "partial"
        weights = {"vimshottari": 0.50, "chara": 0.30, "yogini": 0.20}
    else:
        consensus = "low"
        weights = {"vimshottari": 0.55, "chara": 0.30, "yogini": 0.15}

    # House-theme routing
    _HOUSE_THEMES = {
        1: "via personal reinvention / health focus",
        2: "through financial negotiation / speech / family",
        3: "via courageous self-effort / short travel",
        4: "through domestic change / relocation / mother",
        5: "via creativity / speculation / children / education",
        6: "through overcoming obstacles / service / competition",
        7: "via partnerships / business dealings",
        8: "via transformation / crisis management / OPM / hidden matters",
        9: "through higher learning / dharma / foreign / mentors",
        10: "via career action / public recognition / authority",
        11: "through networks / gains / aspirations fulfilled",
        12: "via foreign / withdrawal / hidden / spiritual / losses that lead to liberation",
    }
    avenue_suffix = _HOUSE_THEMES.get(chara_house, "through standard path")

    synthesis = (f"{domain.capitalize()} manifests {avenue_suffix}. "
                 f"Vimshottari={vim_lord} is primary driver; "
                 f"Chara={chara_lord} provides physical avenue.")

    return {
        "dominant_system": "vimshottari",
        "consensus_level": consensus,
        "weights": weights,
        "synthesis": synthesis,
        "avenue": avenue_suffix,
        "timing_note": "Low consensus → manifestation delayed or indirect.",
        "reason": "Fallback hardcoded synthesis (GPT unavailable)",
    }


# ─── Multi-Dasha AND Consensus Logic ─────────────────────────────

def analyze_multi_dasha_consensus(
    vim_supports_domain: bool,
    yogini_supports_domain: bool,
    chara_supports_domain: bool,
    vim_lord: str,
    yogini_lord: str,
    chara_lord: str,
    domain: str,
    chara_house: int = 0,
    active_yogas: List[str] = None,
    lagna_sign: str = "",
) -> Dict:
    """
    AND Consensus logic (Research Brief, Block 3C):

    All 3 agree    → absolute certainty, zero friction (0.95+ confidence)
    2 of 3 agree   → event manifests (0.75-0.85 confidence)
    1 agrees       → if Vimshottari AND Chara oppose → event cannot manifest

    Vimshottari role: PRIMARY BASELINE (macro 120-yr roadmap)
      If Vimshottari DENIES → event cannot occur in major capacity
    Chara role: SPECIFIC TRIGGER (physical events, location, status)
      Can locally override Vimshottari for geography/tangible wealth
    Yogini role: VALIDATION LAYER (micro 36-yr, Kali Yuga emphasis)
      If aligns with Vimshottari → 90%+ confidence

    Returns:
      {
        consensus_level: "full|partial|low",
        supports_domain: bool,
        confidence_multiplier: 0.0-1.2,
        blocked: bool,  # True if Vim AND Chara BOTH oppose
        synthesis_needed: bool,  # True if dasha systems conflict → need GPT synthesis
        detail: str,
      }
    """
    agree_count = sum([vim_supports_domain, yogini_supports_domain, chara_supports_domain])

    # Research Brief Block 3C: "Only 1 agrees: if Vimshottari AND Chara BOTH oppose
    # → event cannot manifest"  (Yogini alone cannot save if both primary systems deny)
    vim_and_chara_oppose = (not vim_supports_domain and not chara_supports_domain)

    if vim_and_chara_oppose:
        return {
            "consensus_level": "blocked",
            "supports_domain": False,
            "confidence_multiplier": 0.15,
            "blocked": True,
            "synthesis_needed": False,
            "detail": (f"Both Vimshottari ({vim_lord}) AND Chara ({chara_lord}) DENY "
                       f"{domain} → event cannot manifest in current period even if "
                       "Yogini aligns. Natal promise exists but timing not ripe."),
        }

    # Vimshottari denies alone (Chara partially supports) → low, not blocked
    if not vim_supports_domain and chara_supports_domain:
        return {
            "consensus_level": "low",
            "supports_domain": True,   # Chara keeps door open
            "confidence_multiplier": 0.55,
            "blocked": False,
            "synthesis_needed": True,
            "detail": (f"Vimshottari ({vim_lord}) doesn't favor {domain} directly, "
                       f"but Chara ({chara_lord}) in house {chara_house} partially supports. "
                       "Event can occur via indirect avenue."),
        }

    if agree_count == 3:
        return {
            "consensus_level": "full",
            "supports_domain": True,
            "confidence_multiplier": 1.20,  # Bonus for full agreement
            "blocked": False,
            "synthesis_needed": False,
            "detail": (f"All 3 systems agree ({vim_lord}/{chara_lord}/{yogini_lord}) for "
                       f"{domain} → absolute certainty, zero friction."),
        }
    elif agree_count == 2:
        return {
            "consensus_level": "partial",
            "supports_domain": True,
            "confidence_multiplier": 1.00,  # Standard
            "blocked": False,
            "synthesis_needed": chara_lord != vim_lord,  # Conflict = need synthesis
            "detail": (f"2 of 3 systems support {domain} → event manifests. "
                       f"Synthesis needed for conflicting system."),
        }
    else:
        # Only Vimshottari supports (yogini + chara both oppose or neutral)
        return {
            "consensus_level": "low",
            "supports_domain": True,   # Vim supports, so it can happen
            "confidence_multiplier": 0.60,  # Heavily muted
            "blocked": False,
            "synthesis_needed": True,
            "detail": (f"Only Vimshottari ({vim_lord}) supports {domain}. "
                       f"Chara ({chara_lord}) and Yogini ({yogini_lord}) oppose/neutral. "
                       f"Event can occur but with low probability and indirect avenue."),
        }


# ─── Decision Point 3: KP Sublord Ambiguity Resolution ───────────

_KP_AMBIGUITY_SYSTEM = """You are a KP (Krishnamurti Paddhati) astrology analyst.
The KP sub-lord signifies BOTH favorable domain houses AND negator houses.
Determine the net verdict for the domain.
Return ONLY valid JSON:
{
  "verdict": "blocked|partial|strong",
  "adjusted_kp_score": 0.0-1.0,
  "dominant_signification": "positive|negative",
  "reason": "<max 10 words>"
}
Rules:
- 'blocked': negator houses clearly dominant → adjusted_kp_score <= 0.2
- 'partial': mixed → 0.2 < adjusted_kp_score <= 0.55
- 'strong':  domain houses clearly dominant → adjusted_kp_score > 0.55
- 6th+12th together for marriage = 'blocked'. 2nd+11th for career = 'strong'."""


def resolve_kp_ambiguity(
    sublord_chain: Dict[str, Any],
    domain: str,
    domain_houses: List[int],
    negator_houses: List[int],
    raw_kp_score: float,
) -> Optional[Dict]:
    """
    When KP sublord signifies both favorable and negator houses,
    ask GPT to resolve the net verdict.

    Returns {verdict, adjusted_kp_score, dominant_signification, reason} or None.
    adjusted_kp_score feeds directly into the confidence gate logic.
    """
    # Only invoke when there's genuine ambiguity (negators and domain houses both non-empty)
    if not negator_houses or not domain_houses:
        return None
    if raw_kp_score > 0.65 or raw_kp_score < 0.10:
        return None  # Clear positive or clear failure — no ambiguity

    user_content = json.dumps({
        "domain":          domain,
        "domain_houses":   domain_houses,
        "negator_houses":  negator_houses,
        "sublord_chain":   sublord_chain,
        "raw_kp_score":    round(raw_kp_score, 3),
    }, separators=(",", ":"))

    return _call_gpt(_KP_AMBIGUITY_SYSTEM, user_content, max_tokens=200)


# ─── Decision Point 4: Adaptive Weight Calibration ───────────────

_ADAPTIVE_WEIGHTS_SYSTEM = """You are a Vedic astrology prediction calibrator.
Given chart characteristics (lagna type, active yogas, dominant karakas),
determine the optimal confidence weight distribution for this specific chart.
Return ONLY valid JSON:
{
  "dasha": 0.15-0.35,
  "transit": 0.15-0.45,
  "ashtakvarga": 0.08-0.20,
  "yoga": 0.08-0.18,
  "kp": 0.08-0.18,
  "functional": 0.04-0.12,
  "house_lord": 0.03-0.10,
  "reason": "<max 10 words>"
}
Weights MUST sum to 1.0. Default: dasha=0.25, transit=0.25, rest proportional.
Favor transit more when multiple Raja Yogas present. Favor dasha when Kala Sarpa Yoga."""


def get_adaptive_weights(
    lagna_sign: str,
    active_yogas: List[str],
    karakas: Dict[str, str],
    shadbala_summary: Dict[str, float],
    gate_status: str,
) -> Optional[Dict]:
    """
    Per-chart adaptive weight calibration.
    When multiple strong Raja Yogas are present, transit becomes more decisive.
    When Kala Sarpa constraints exist, dasha is more reliable.

    Returns weight dict or None (engine falls back to gate-based weights).
    Only called once per analysis session (cached aggressively).
    """
    user_content = json.dumps({
        "lagna":             lagna_sign,
        "yogas":             active_yogas[:6],
        "atmakaraka":        karakas.get("AtmaKaraka", ""),
        "amatyakaraka":      karakas.get("AmatyaKaraka", ""),
        "has_raja_yoga":     any("Raja" in y for y in active_yogas),
        "has_kala_sarpa":    any("Kala Sarpa" in y for y in active_yogas),
        "gate_status":       gate_status,
    }, separators=(",", ":"))

    result = _call_gpt(_ADAPTIVE_WEIGHTS_SYSTEM, user_content, max_tokens=220)
    if result is None:
        return None
    # Validate weights sum ~1.0
    keys = ["dasha", "transit", "ashtakvarga", "yoga", "kp", "functional", "house_lord"]
    total = sum(float(result.get(k, 0)) for k in keys)
    if abs(total - 1.0) > 0.05:
        logger.debug(f"GPT adaptive weights don't sum to 1.0 ({total:.3f}) — discarding")
        return None
    return result


# ─── Convenience: apply yoga fructification multipliers ──────────

def apply_yoga_fructification(
    active_yogas: List[Dict],
    fructification_results: Optional[List[Dict]],
) -> List[Dict]:
    """
    Apply GPT-determined fructification multipliers to yoga list.
    Yogas marked inactive get suppressed; enhanced ones boosted.
    Returns modified yoga list safe to pass to score_yoga_activation().
    """
    if not fructification_results:
        return active_yogas

    fruct_map = {r["name"]: r for r in fructification_results}
    updated = []
    for yoga in active_yogas:
        name = yoga.get("name", str(yoga)) if isinstance(yoga, dict) else str(yoga)
        fr = fruct_map.get(name)
        if fr and not fr.get("active", True):
            continue   # drop dormant yogas
        if fr and isinstance(yoga, dict):
            mult = float(fr.get("strength_multiplier", 1.0))
            yoga = dict(yoga)
            yoga["_gpt_multiplier"] = mult
        updated.append(yoga)
    return updated
