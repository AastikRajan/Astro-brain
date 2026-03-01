"""
LLM Agent Swarm Architecture — Multi-Expert Council for Vedic Prediction.

═══════════════════════════════════════════════════════════════════════
ARCHITECTURE OVERVIEW
═══════════════════════════════════════════════════════════════════════

Problem with single-LLM approach (current gpt_reasoner.py)
-----------------------------------------------------------
One GPT call to resolve all ambiguities forces the model to:
  - Hold 2000 tokens of context simultaneously
  - Be both "Parashara expert" AND "KP expert" AND "Jaimini expert"
  - Risk "confusion hallucinations" when classical systems contradict each other

The Multi-Agent Solution
------------------------
Separate, highly-prompted agents each hold ONLY their classical corpus.
They "debate" — each contributes their system's conclusion.
A Chief Synthesizer makes the final call using explicit override hierarchy.

Agent Roster
------------
  AGENT_PARASHARA   : Brihat Parashara Hora Shastra — yogas, functional lords,
                      Vimshottari timing, all classical Parashara rules.
  AGENT_KP          : KP (Krishnamurti Paddhati) — sub-lord theory, significators,
                      promise via sub-lord stellium.
  AGENT_JAIMINI     : Jaimini Sutras — Chara karakas, Chara dasha, Rashi drishti,
                      Argala, Arudha padas, Karakamsha.
  AGENT_MEDICAL     : Medical astrology — Ayurvedic planetary physiology, 6th/8th
                      lord diseases, longevity (Alpa/Madhya/Purna Ayus).
  AGENT_SYNTHESIZER : Chief Synthesizer — receives all agent opinions, applies
                      classical override hierarchy, outputs final prediction.

Override Hierarchy (from research)
-----------------------------------
  1. D9 position over D1 for spiritual/marriage domains
  2. KP sub-lord "denied at sub-lord level" overrides Parashara yoga activation
  3. Promise gate: DENIED status is absolute (no timing can overcome no promise)
  4. Medical: longevity guardrail (Alpa Ayus → cap at 32y) overrides timing

Framework
---------
  Uses LangChain + LangGraph (already installed).
  Each agent = LangGraph Node with its own system prompt + tool access.
  State: SharedPredictionState (typed dict) passed between nodes.

Status: SCAFFOLD — LangGraph graph and prompts defined; wiring to run()
        not yet connected to PredictionEngine. See TODO comments.

Dependencies (installed)
------------------------
  langchain-core == latest
  langchain-openai == latest
  langgraph == latest
  openai (via langchain-openai)
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, TypedDict

logger = logging.getLogger(__name__)

# ─── Availability guards ──────────────────────────────────────────────────────

try:
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    from langchain_core.prompts import ChatPromptTemplate
    _LC_AVAILABLE = True
except ImportError:
    _LC_AVAILABLE = False
    logger.warning("[agent_swarm] langchain-core not installed.")

try:
    from langgraph.graph import StateGraph, END
    _LG_AVAILABLE = True
except ImportError:
    _LG_AVAILABLE = False
    logger.warning("[agent_swarm] langgraph not installed.")

try:
    from langchain_openai import ChatOpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False


# ─── Shared State (passed between all graph nodes) ─────────────────────────

class SwarmState(TypedDict, total=False):
    """State flowing through the LangGraph agent network."""
    # Input: computed features from PredictionEngine
    chart_summary:      str     # JSON string of key chart facts
    domain:             str     # "career", "marriage", etc.
    domain_houses:      List[int]
    planet_positions:   Dict[str, float]
    dashas:             Dict[str, Any]
    transits:           Dict[str, Any]
    yogas:              List[Dict]
    kp_significators:   Dict[str, Any]
    jaimini_data:       Dict[str, Any]
    promise_result:     Dict[str, Any]
    confidence_raw:     float

    # Agent outputs
    opinion_parashara:  str
    opinion_kp:         str
    opinion_jaimini:    str
    opinion_medical:    str

    # Final output
    synthesis:          str
    final_confidence:   float
    final_level:        str     # "STRONG/MODERATE/WEAK/DENIED"
    override_applied:   str     # which override rule was triggered
    reasoning_trace:    List[str]


# ─── System prompts ────────────────────────────────────────────────────────────

SYSTEM_PARASHARA = """You are a Parashara expert with complete knowledge of
Brihat Parashara Hora Shastra. Your ONLY job is to evaluate the given chart
data strictly using Parashara principles:
- Functional benefics/malefics based on Lagna lord
- Yoga identification (Dhana, Raja, Viparita, Neecha Bhanga, etc.)
- Vimshottari dasha timing — mahadasha + antardasha lord house occupancy
- Aspect rules (7th house dristi + special aspects for Mars/Jupiter/Saturn)
- D9 (Navamsa) quality of the Dasha lord

Return ONLY a structured JSON:
{"conclusion": "STRONG|MODERATE|WEAK|DENIED", "confidence": 0.0-1.0,
 "key_factors": ["...", "..."], "override_flags": ["..."]}"""

SYSTEM_KP = """You are a KP (Krishnamurti Paddhati) expert. Evaluate using
ONLY KP principles:
- Sub-lord of the domain cusps (2nd, 7th, 10th, 11th etc.)
- Sub-lord must signify at least 2 of the relevant houses (star-lord + sub-lord chain)
- A sub-lord in the 6th/8th/12th house constellation DENIES the event
- Running dasha lord must be a significator in the KP sense

Return ONLY: {"conclusion": "STRONG|MODERATE|WEAK|DENIED", "confidence": 0.0-1.0,
 "key_factors": ["...", "..."], "override_flags": ["kp_denied if applicable"]}"""

SYSTEM_JAIMINI = """You are a Jaimini Sutras expert. Evaluate using ONLY
Jaimini principles:
- Chara Karakas: AK, AmK, BK, MK, PK, GK, DK — their sign position and D9
- Chara Dasha current period (Rashi level): which sign is running?
- House from AK (Karakamsha) relevant to the domain
- Argala and Virodha Argala on relevant house/sign
- Arudha Lagna and domain Arudha (A7 for marriage, A10 for career, etc.)

Return ONLY: {"conclusion": "STRONG|MODERATE|WEAK|DENIED", "confidence": 0.0-1.0,
 "key_factors": ["...", "..."], "override_flags": []}"""

SYSTEM_MEDICAL = """You are a Vedic medical astrology expert. Evaluate ONLY
health and longevity implications:
- Longevity class: Alpa Ayus (<32y), Madhya Ayus (32–75y), Purna Ayus (>75y)
  [from planets in kendras vs dusthanas, lord strengths, Gulika position]
- If Alpa Ayus: OVERRIDE any optimistic prediction — cap confidence at 0.30
- Active disease indicators: 6th lord + Saturn/Mars conjunction patterns
- Moon affliction indicators for mental health
- Return a GUARDRAIL flag if longevity calculations suggest <32 year life span.

Return ONLY: {"longevity_class": "Alpa|Madhya|Purna", "guardrail_active": bool,
 "confidence_cap": 1.0, "key_factors": ["...", "..."], "override_flags": []}"""

SYSTEM_SYNTHESIZER = """You are the Chief Synthesizer in a Vedic astrology
council. You receive structured opinions from 4 specialized agents:
  - Parashara agent
  - KP agent
  - Jaimini agent
  - Medical agent

Use this STRICT override hierarchy:
  1. IF medical.guardrail_active → cap final_confidence at medical.confidence_cap
  2. IF kp.conclusion == "DENIED" → final = "DENIED", confidence ≤ 0.15
  3. IF promise_result.denied == True → final = "DENIED" regardless of timing
  4. ELSE: weight-average opinions:
       Parashara 35%, KP 30%, Jaimini 25%, Medical 10%
  5. Reconcile contradictions: if 3 of 4 agents agree, follow majority unless
     override rules above apply.

Return structured JSON:
{"final_level": "STRONG|MODERATE|WEAK|DENIED",
 "final_confidence": 0.0-1.0,
 "override_applied": "none|kp_denied|medical_guardrail|promise_gate|...",
 "synthesis_reasoning": "2-4 sentence explanation",
 "agent_weights_used": {"parashara": 0.35, "kp": 0.3, "jaimini": 0.25, "medical": 0.1}}"""


# ─── Agent node functions ─────────────────────────────────────────────────────

def _make_llm(model: str = "gpt-4o-mini", temperature: float = 0.1):
    """Create ChatOpenAI instance (requires OPENAI_API_KEY in environment)."""
    if not _OPENAI_AVAILABLE:
        raise RuntimeError("langchain-openai not installed.")
    return ChatOpenAI(model=model, temperature=temperature)


def node_parashara(state: SwarmState) -> SwarmState:
    """Agent node: Parashara analysis."""
    if not _LC_AVAILABLE:
        state["opinion_parashara"] = '{"conclusion":"MODERATE","confidence":0.5,"key_factors":["unavailable"]}'
        return state
    try:
        llm = _make_llm()
        messages = [
            SystemMessage(content=SYSTEM_PARASHARA),
            HumanMessage(content=f"Domain: {state.get('domain')}\n\n"
                                  f"Chart Data:\n{state.get('chart_summary', 'N/A')}\n\n"
                                  f"Active Dashas: {json.dumps(state.get('dashas', {}))}\n"
                                  f"Promise: {json.dumps(state.get('promise_result', {}))}\n"
                                  f"Yogas: {json.dumps(state.get('yogas', [])[:10])}")
        ]
        response = llm.invoke(messages)
        state["opinion_parashara"] = response.content
    except Exception as e:
        state["opinion_parashara"] = f'{{"error": "{e}"}}'
    return state


def node_kp(state: SwarmState) -> SwarmState:
    """Agent node: KP analysis."""
    if not _LC_AVAILABLE:
        state["opinion_kp"] = '{"conclusion":"MODERATE","confidence":0.5}'
        return state
    try:
        llm = _make_llm()
        messages = [
            SystemMessage(content=SYSTEM_KP),
            HumanMessage(content=f"Domain: {state.get('domain')}\n"
                                  f"Domain Houses: {state.get('domain_houses')}\n"
                                  f"KP Significators: {json.dumps(state.get('kp_significators', {}))}\n"
                                  f"Active Dashas: {json.dumps(state.get('dashas', {}))}")
        ]
        response = llm.invoke(messages)
        state["opinion_kp"] = response.content
    except Exception as e:
        state["opinion_kp"] = f'{{"error": "{e}"}}'
    return state


def node_jaimini(state: SwarmState) -> SwarmState:
    """Agent node: Jaimini analysis."""
    if not _LC_AVAILABLE:
        state["opinion_jaimini"] = '{"conclusion":"MODERATE","confidence":0.5}'
        return state
    try:
        llm = _make_llm()
        messages = [
            SystemMessage(content=SYSTEM_JAIMINI),
            HumanMessage(content=f"Domain: {state.get('domain')}\n"
                                  f"Jaimini Data: {json.dumps(state.get('jaimini_data', {}))}")
        ]
        response = llm.invoke(messages)
        state["opinion_jaimini"] = response.content
    except Exception as e:
        state["opinion_jaimini"] = f'{{"error": "{e}"}}'
    return state


def node_medical(state: SwarmState) -> SwarmState:
    """Agent node: Medical/Longevity guardrail."""
    if not _LC_AVAILABLE:
        state["opinion_medical"] = '{"longevity_class":"Madhya","guardrail_active":false,"confidence_cap":1.0}'
        return state
    try:
        llm = _make_llm()
        messages = [
            SystemMessage(content=SYSTEM_MEDICAL),
            HumanMessage(content=f"Chart Summary:\n{state.get('chart_summary', 'N/A')}")
        ]
        response = llm.invoke(messages)
        state["opinion_medical"] = response.content
    except Exception as e:
        state["opinion_medical"] = f'{{"longevity_class":"Madhya","guardrail_active":false}}'
    return state


def node_synthesizer(state: SwarmState) -> SwarmState:
    """Chief Synthesizer node — final decision."""
    if not _LC_AVAILABLE:
        state["final_confidence"] = state.get("confidence_raw", 0.5)
        state["final_level"] = "MODERATE"
        state["override_applied"] = "none"
        return state
    try:
        llm = _make_llm(model="gpt-4o", temperature=0.0)   # use stronger model for synthesis
        council_summary = (
            f"PARASHARA AGENT:\n{state.get('opinion_parashara', 'N/A')}\n\n"
            f"KP AGENT:\n{state.get('opinion_kp', 'N/A')}\n\n"
            f"JAIMINI AGENT:\n{state.get('opinion_jaimini', 'N/A')}\n\n"
            f"MEDICAL AGENT:\n{state.get('opinion_medical', 'N/A')}\n\n"
            f"Engine Raw Confidence: {state.get('confidence_raw', 0.5):.3f}\n"
            f"Promise Gate Result: {json.dumps(state.get('promise_result', {}))}"
        )
        messages = [
            SystemMessage(content=SYSTEM_SYNTHESIZER),
            HumanMessage(content=council_summary),
        ]
        response = llm.invoke(messages)
        try:
            parsed = json.loads(response.content)
            state["final_confidence"]  = parsed.get("final_confidence", state.get("confidence_raw", 0.5))
            state["final_level"]       = parsed.get("final_level", "MODERATE")
            state["override_applied"]  = parsed.get("override_applied", "none")
            state["synthesis"]         = parsed.get("synthesis_reasoning", "")
        except json.JSONDecodeError:
            state["synthesis"] = response.content
            state["final_confidence"] = state.get("confidence_raw", 0.5)
            state["final_level"] = "MODERATE"
            state["override_applied"] = "none"
    except Exception as e:
        state["synthesis"] = f"Synthesis error: {e}"
        state["final_confidence"] = state.get("confidence_raw", 0.5)
        state["override_applied"] = "none"
    return state


# ─── Graph construction ───────────────────────────────────────────────────────

def build_swarm_graph():
    """
    Build and compile the LangGraph multi-agent graph.

    Topology: All 4 specialist nodes run in parallel → Synthesizer node → END

    NOTE: LangGraph parallel execution via fan-out requires LangGraph 0.2+.
    If fan-out fails, nodes run sequentially (still correct, just slower).

    Returns compiled graph or None if LangGraph not available.
    """
    if not _LG_AVAILABLE:
        logger.warning("[agent_swarm] LangGraph not available — graph not built.")
        return None

    graph = StateGraph(SwarmState)

    # Add specialist nodes
    graph.add_node("parashara", node_parashara)
    graph.add_node("kp",        node_kp)
    graph.add_node("jaimini",   node_jaimini)
    graph.add_node("medical",   node_medical)
    graph.add_node("synthesize", node_synthesizer)

    # Entry point fans out to all 4 specialists
    graph.set_entry_point("parashara")

    # Sequential for now (parallel fan-out requires conditional routing in LG)
    graph.add_edge("parashara", "kp")
    graph.add_edge("kp",        "jaimini")
    graph.add_edge("jaimini",   "medical")
    graph.add_edge("medical",   "synthesize")
    graph.add_edge("synthesize", END)

    return graph.compile()


# ─── Public API ───────────────────────────────────────────────────────────────

def run_agent_swarm(
    domain: str,
    chart_summary: str,
    dashas: Dict,
    kp_significators: Dict,
    jaimini_data: Dict,
    promise_result: Dict,
    yogas: List,
    confidence_raw: float,
    domain_houses: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """
    Run the full agent swarm for a prediction domain.

    Parameters
    ----------
    domain            : e.g. "career"
    chart_summary     : JSON string of key chart facts
    dashas            : {"mahadasha": ..., "antardasha": ...}
    kp_significators  : KP house significators dict
    jaimini_data      : Jaimini karakas + chara dasha data
    promise_result    : from promise.py assess_promise_strength()
    yogas             : list of active yoga dicts
    confidence_raw    : engine's raw confidence (pre-swarm)
    domain_houses     : relevant house numbers for this domain

    Returns
    -------
    {
      "final_confidence":  float,
      "final_level":       str,
      "override_applied":  str,
      "synthesis":         str,
      "agent_opinions":    dict,
    }
    """
    compiled = build_swarm_graph()
    if compiled is None:
        return {
            "final_confidence": confidence_raw,
            "final_level": "MODERATE",
            "override_applied": "none",
            "synthesis": "Agent swarm unavailable (LangGraph not installed).",
            "agent_opinions": {},
        }

    initial_state: SwarmState = {
        "domain": domain,
        "chart_summary": chart_summary,
        "dashas": dashas,
        "kp_significators": kp_significators,
        "jaimini_data": jaimini_data,
        "promise_result": promise_result,
        "yogas": yogas,
        "confidence_raw": confidence_raw,
        "domain_houses": domain_houses or [],
        "reasoning_trace": [],
    }

    try:
        final_state = compiled.invoke(initial_state)
        return {
            "final_confidence": final_state.get("final_confidence", confidence_raw),
            "final_level":      final_state.get("final_level", "MODERATE"),
            "override_applied": final_state.get("override_applied", "none"),
            "synthesis":        final_state.get("synthesis", ""),
            "agent_opinions": {
                "parashara": final_state.get("opinion_parashara", ""),
                "kp":        final_state.get("opinion_kp", ""),
                "jaimini":   final_state.get("opinion_jaimini", ""),
                "medical":   final_state.get("opinion_medical", ""),
            },
        }
    except Exception as e:
        logger.error(f"[agent_swarm] Swarm execution failed: {e}")
        return {
            "final_confidence": confidence_raw,
            "final_level": "MODERATE",
            "override_applied": "none",
            "synthesis": f"Swarm error: {e}",
            "agent_opinions": {},
        }
