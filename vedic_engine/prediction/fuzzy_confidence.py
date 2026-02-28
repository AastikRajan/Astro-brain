"""
Fuzzy Logic Confidence Engine.

Classical Vedic astrology requires CONVERGENCE of multiple timing systems
to deliver a prediction with confidence. A simple weighted average fails to
model this because:

  - When ALL systems agree strongly → confidence should compound
  - When systems DISAGREE         → confidence should be suppressed below average
  - Partial agreements have non-linear weights

This module uses scikit-fuzzy to build a 3-input fuzzy inference system:

  timing_support   → dasha + KP sublord  (WHEN something activates)
  transit_support  → transit gochar + ashtakvarga  (environmental support)
  structural_support → yogas + functional role + house lord  (natal potential)

The output `fuzzy_confidence` (0-1) replaces the linear weighted sum when
available, providing a more accurate multi-system agreement score.

Fallback: if scikit-fuzzy is unavailable, returns None and the linear score is used.

Usage:
    from vedic_engine.prediction.fuzzy_confidence import compute_fuzzy_confidence
    result = compute_fuzzy_confidence(timing=0.7, transit=0.5, structural=0.8)
    # result: {"fuzzy_confidence": 0.68, "verdict": "HIGH", "method": "fuzzy"}
"""
from __future__ import annotations
from typing import Dict, Optional


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


# ─── Fuzzy system (built once and cached) ────────────────────────────────────

_fuzzy_ctrl = None   # cached ControlSystem (rules only, no mutable state)


def _build_fuzzy_system():
    """Build the scikit-fuzzy control system. Called once, cached globally."""
    import numpy as np
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl

    # ── Universe of discourse ──────────────────────────────────────
    universe = np.arange(0, 1.01, 0.01)

    # ── Antecedents (inputs) ───────────────────────────────────────
    timing     = ctrl.Antecedent(universe, "timing")
    transit    = ctrl.Antecedent(universe, "transit")
    structural = ctrl.Antecedent(universe, "structural")

    # ── Consequent (output) ────────────────────────────────────────
    confidence = ctrl.Consequent(universe, "confidence", defuzzify_method="centroid")

    # ── Membership functions (3 levels each) ─────────────────────
    for var in [timing, transit, structural, confidence]:
        var["low"]    = fuzz.trimf(var.universe, [0.0, 0.00, 0.40])
        var["medium"] = fuzz.trimf(var.universe, [0.20, 0.50, 0.80])
        var["high"]   = fuzz.trimf(var.universe, [0.60, 1.00, 1.00])

    # ── Fuzzy rules ────────────────────────────────────────────────
    # Principle: timing + transit must BOTH agree for high confidence;
    # structural (natal) is the enabling condition.
    rules = [
        # All three agree high → very high confidence
        ctrl.Rule(timing["high"] & transit["high"] & structural["high"],
                  confidence["high"]),

        # Two high + one medium → high confidence
        ctrl.Rule(timing["high"] & transit["high"] & structural["medium"],
                  confidence["high"]),
        ctrl.Rule(timing["high"] & transit["medium"] & structural["high"],
                  confidence["high"]),
        ctrl.Rule(timing["medium"] & transit["high"] & structural["high"],
                  confidence["high"]),

        # Two high + one low → medium-high confidence (strong opposition from one system)
        ctrl.Rule(timing["high"] & transit["high"] & structural["low"],
                  confidence["medium"]),
        ctrl.Rule(timing["high"] & transit["low"] & structural["high"],
                  confidence["medium"]),
        ctrl.Rule(timing["low"] & transit["high"] & structural["high"],
                  confidence["medium"]),

        # One high + two medium → medium confidence
        ctrl.Rule(timing["high"] & transit["medium"] & structural["medium"],
                  confidence["medium"]),
        ctrl.Rule(timing["medium"] & transit["high"] & structural["medium"],
                  confidence["medium"]),
        ctrl.Rule(timing["medium"] & transit["medium"] & structural["high"],
                  confidence["medium"]),

        # Balanced medium → medium confidence
        ctrl.Rule(timing["medium"] & transit["medium"] & structural["medium"],
                  confidence["medium"]),

        # One high + one medium + one low → low-medium
        ctrl.Rule(timing["high"] & transit["medium"] & structural["low"],
                  confidence["low"]),
        ctrl.Rule(timing["high"] & transit["low"] & structural["medium"],
                  confidence["low"]),
        ctrl.Rule(timing["medium"] & transit["high"] & structural["low"],
                  confidence["low"]),
        ctrl.Rule(timing["low"] & transit["high"] & structural["medium"],
                  confidence["low"]),
        ctrl.Rule(timing["medium"] & transit["low"] & structural["high"],
                  confidence["low"]),
        ctrl.Rule(timing["low"] & transit["medium"] & structural["high"],
                  confidence["low"]),

        # One high + two low → low confidence
        ctrl.Rule(timing["high"] & transit["low"] & structural["low"],
                  confidence["low"]),
        ctrl.Rule(timing["low"] & transit["high"] & structural["low"],
                  confidence["low"]),
        ctrl.Rule(timing["low"] & transit["low"] & structural["high"],
                  confidence["low"]),

        # One medium + two low → low confidence
        ctrl.Rule(timing["medium"] & transit["low"] & structural["low"],
                  confidence["low"]),
        ctrl.Rule(timing["low"] & transit["medium"] & structural["low"],
                  confidence["low"]),
        ctrl.Rule(timing["low"] & transit["low"] & structural["medium"],
                  confidence["low"]),

        # All low → very low confidence
        ctrl.Rule(timing["low"] & transit["low"] & structural["low"],
                  confidence["low"]),
    ]

    system = ctrl.ControlSystem(rules)
    return system  # return ControlSystem (immutable rules), not the simulation


def compute_fuzzy_confidence(
    timing: float,
    transit: float,
    structural: float,
) -> Optional[Dict]:
    """
    Apply fuzzy inference to compute multi-system convergence confidence.

    Parameters
    ----------
    timing      : 0-1 score representing dasha + KP activation strength
    transit     : 0-1 score representing transit + ashtakvarga support
    structural  : 0-1 score representing yoga + functional + house lord potential

    Returns
    -------
    dict with:
        fuzzy_confidence : float 0-1
        verdict          : str ("VERY HIGH" / "HIGH" / "MODERATE" / "LOW" / "VERY LOW")
        convergence_level: str ("STRONG" / "PARTIAL" / "WEAK" / "SCATTERED")
        method           : "fuzzy" | "fallback"
    or None if scikit-fuzzy is not available.
    """
    global _fuzzy_sim

    global _fuzzy_ctrl

    # ── Attempt primary scikit-fuzzy inference ───────────────────
    try:
        if _fuzzy_ctrl is None:
            _fuzzy_ctrl = _build_fuzzy_system()

        # Fresh simulation each call (ControlSystemSimulation holds mutable state)
        import skfuzzy.control as ctrl
        sim = ctrl.ControlSystemSimulation(_fuzzy_ctrl)
        sim.input["timing"]     = _clamp01(timing)
        sim.input["transit"]    = _clamp01(transit)
        sim.input["structural"] = _clamp01(structural)
        sim.compute()
        fuzzy_val = float(sim.output["confidence"])
        return _format_result(fuzzy_val, "skfuzzy")

    except Exception:
        # Invalidate cache in case build was partial
        _fuzzy_ctrl = None

    # ── Fallback: harmonic mean (non-linear, punishes low outliers) ──
    t, tr, s = _clamp01(timing), _clamp01(transit), _clamp01(structural)
    try:
        fuzzy_val = 3.0 / (1.0/max(t, 0.01) + 1.0/max(tr, 0.01) + 1.0/max(s, 0.01))
    except Exception:
        fuzzy_val = (t + tr + s) / 3.0
    return _format_result(fuzzy_val, "fallback-harmonic")


def _format_result(score: float, method: str) -> Dict:
    score = _clamp01(score)
    verdict = (
        "VERY HIGH" if score >= 0.75 else
        "HIGH"      if score >= 0.60 else
        "MODERATE"  if score >= 0.40 else
        "LOW"       if score >= 0.25 else "VERY LOW"
    )
    convergence = (
        "STRONG"   if score >= 0.65 else
        "PARTIAL"  if score >= 0.40 else
        "WEAK"     if score >= 0.20 else
        "SCATTERED"
    )
    return {
        "fuzzy_confidence": round(score, 3),
        "verdict":          verdict,
        "convergence_level": convergence,
        "method":           method,
    }


# ─── Aggregate confidence scores → fuzzy inputs ──────────────────────────────

def aggregate_for_fuzzy(components: Dict[str, float]) -> Dict[str, float]:
    """
    Map the 7 confidence components from confidence.py into the 3 fuzzy inputs.

    timing     = 0.65×dasha_alignment + 0.35×kp_confirmation
    transit    = 0.70×transit_support + 0.30×ashtakvarga_support
    structural = 0.40×yoga_activation + 0.35×functional_alignment + 0.25×house_lord_strength
    """
    da  = components.get("dasha_alignment",    0.3)
    ts  = components.get("transit_support",    0.3)
    av  = components.get("ashtakvarga_support",0.3)
    yo  = components.get("yoga_activation",    0.3)
    kp  = components.get("kp_confirmation",    0.3)
    fn  = components.get("functional_alignment",0.5)
    hl  = components.get("house_lord_strength", 0.3)

    return {
        "timing":     _clamp01(0.65 * da + 0.35 * kp),
        "transit":    _clamp01(0.70 * ts + 0.30 * av),
        "structural": _clamp01(0.40 * yo + 0.35 * fn + 0.25 * hl),
    }
