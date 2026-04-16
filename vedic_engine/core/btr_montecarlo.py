"""
Birth Time Rectification (BTR) via Monte Carlo Simulation.

═══════════════════════════════════════════════════════════════════════
ARCHITECTURE — How This Module Fits In
═══════════════════════════════════════════════════════════════════════

Problem
-------
No one has a provably accurate birth time. A 15-minute error in birth time
can shift the Ascendant by ~3.75° (at average birth latitudes), change the
Ascendant's nakshatra pada, shift house cusps, alter KP sub-lord assignments,
and change which Dasha is active at birth.

Consequence: a prediction engine that ignores birth time uncertainty will
output single-point confidence scores with false precision.

Solution — Monte Carlo BTR
--------------------------
Instead of running a chart for exactly "10:30 AM", run N simulations sampling
birth times uniformly over a ±window window (e.g. ±20 minutes).

For each simulated birth time:
  1. Recompute the chart (VedicChart) for that birth time.
  2. Run the full prediction engine for one or more domains.
  3. Collect the confidence scores.

Output statistics:
  - mean_confidence:   expected prediction confidence across all samples
  - std_confidence:    standard deviation — HIGH std = brittle prediction
  - p90:               90th percentile confidence
  - p10:               10th percentile confidence
  - brittleness_score: (p90 - p10) / mean — >0.30 flags brittle predictions
  - stable_predictions: domains/events consistent across >90% of simulations

Interpretive power:
  - 450 of 500 simulations agree → confidence that birth time error doesn't
    break the prediction. Report it confidently.
  - Prediction collapses at +2 minutes → flag as time-sensitive; recommendation
    to verify birth record.

Integration Points (NOT YET WIRED — scaffold only)
---------------------------------------------------
  - PredictionEngine.predict_domain() → already exists; callable per simulation
  - VedicChart / load_from_dict() → already accepts dict; re-constructible
  - Output stored in domain_report["btr"] = <BTRResult dict>

Usage (future, once wired)
--------------------------
    from vedic_engine.core.btr_montecarlo import run_btr_simulation
    btr = run_btr_simulation(
        base_chart=chart,
        domain="career",
        window_minutes=20,
        n_simulations=200,
    )
    print(btr.summary())

Dependencies (already installed)
---------------------------------
  numpy — vectorized random sampling, statistics
  scipy — optional: scipy.stats for distribution fitting
  concurrent.futures — parallel chart computation (stdlib)

Status: SCAFFOLD — structure complete, engine wiring pending.
"""

from __future__ import annotations

import logging
import random
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ─── Configuration ────────────────────────────────────────────────────────────

BTR_DEFAULT_WINDOW_MINUTES  = 20    # ± minutes around stated birth time
BTR_DEFAULT_N_SIMULATIONS   = 200   # number of Monte Carlo samples
BTR_DEFAULT_PARALLEL_JOBS   = 4     # concurrent.futures thread pool size
BTR_BRITTLENESS_THRESHOLD   = 0.30  # p90-p10 / mean; above = unstable


# ─── Data structures ──────────────────────────────────────────────────────────

@dataclass
class BTRSample:
    """Result of running the engine for one simulated birth time."""
    birth_dt:   datetime
    confidence: float                    # domain confidence 0–1
    domain:     str
    prediction_level: str               # e.g. "STRONG", "MODERATE"
    details:    Dict[str, Any] = field(default_factory=dict)


@dataclass
class BTRResult:
    """Aggregate statistics over all Monte Carlo samples."""
    domain:             str
    base_birth_dt:      datetime
    window_minutes:     int
    n_simulations:      int
    n_successful:       int
    samples:            List[BTRSample] = field(default_factory=list)

    # Statistics (populated by _compute_stats)
    mean_confidence:    float = 0.0
    std_confidence:     float = 0.0
    p10:                float = 0.0
    p90:                float = 0.0
    min_confidence:     float = 0.0
    max_confidence:     float = 0.0
    brittleness_score:  float = 0.0
    is_brittle:         bool  = False
    stable_level:       Optional[str] = None   # modal prediction_level

    def compute_stats(self) -> None:
        """Populate statistical fields from samples list."""
        if not self.samples:
            return
        confs = sorted(s.confidence for s in self.samples)
        n = len(confs)
        self.mean_confidence   = sum(confs) / n
        self.min_confidence    = confs[0]
        self.max_confidence    = confs[-1]
        self.p10               = confs[int(n * 0.10)]
        self.p90               = confs[int(n * 0.90)]
        variance = sum((c - self.mean_confidence) ** 2 for c in confs) / n
        self.std_confidence    = math.sqrt(variance)
        if self.mean_confidence > 0:
            self.brittleness_score = (self.p90 - self.p10) / self.mean_confidence
        self.is_brittle        = self.brittleness_score > BTR_BRITTLENESS_THRESHOLD

        # Modal prediction level
        from collections import Counter
        levels = [s.prediction_level for s in self.samples if s.prediction_level]
        if levels:
            self.stable_level = Counter(levels).most_common(1)[0][0]

    def summary(self) -> str:
        """Human-readable summary string."""
        lines = [
            f"BTR Monte Carlo — {self.domain.upper()} domain",
            f"  Base birth time : {self.base_birth_dt.strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Window          : ±{self.window_minutes} minutes",
            f"  Simulations     : {self.n_successful}/{self.n_simulations} successful",
            f"  Mean confidence : {self.mean_confidence:.3f}",
            f"  Std dev         : {self.std_confidence:.3f}",
            f"  P10–P90 range   : {self.p10:.3f} – {self.p90:.3f}",
            f"  Brittleness     : {self.brittleness_score:.3f} "
            f"({'⚠ BRITTLE' if self.is_brittle else '✓ STABLE'})",
            f"  Modal level     : {self.stable_level or 'N/A'}",
        ]
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain":           self.domain,
            "base_birth_dt":    self.base_birth_dt.isoformat(),
            "window_minutes":   self.window_minutes,
            "n_simulations":    self.n_simulations,
            "n_successful":     self.n_successful,
            "mean_confidence":  round(self.mean_confidence, 4),
            "std_confidence":   round(self.std_confidence, 4),
            "p10":              round(self.p10, 4),
            "p90":              round(self.p90, 4),
            "brittleness_score": round(self.brittleness_score, 4),
            "is_brittle":       self.is_brittle,
            "stable_level":     self.stable_level,
        }


# ─── Core simulation ──────────────────────────────────────────────────────────

def run_btr_simulation(
    base_chart,                 # VedicChart
    domain: str,
    window_minutes: int = BTR_DEFAULT_WINDOW_MINUTES,
    n_simulations: int  = BTR_DEFAULT_N_SIMULATIONS,
    engine_fn: Optional[Callable] = None,
    parallel_jobs: int  = BTR_DEFAULT_PARALLEL_JOBS,
    seed: Optional[int] = None,
) -> BTRResult:
    """
    Run Monte Carlo BTR simulation for a given chart and domain.

    SCAFFOLD — Engine wiring not yet implemented.
    When wired: engine_fn = PredictionEngine().predict_domain

    Parameters
    ----------
    base_chart    : VedicChart with birth_info.date/time/latitude/longitude/tz
    domain        : prediction domain (e.g. "career", "marriage")
    window_minutes: ± range in minutes for sampling
    n_simulations : number of Monte Carlo samples
    engine_fn     : callable(VedicChart, domain) → {"confidence": float, ...}
                    If None, returns an empty BTRResult and logs a warning.
    parallel_jobs : number of parallel workers
    seed          : random seed for reproducibility

    Returns
    -------
    BTRResult with .compute_stats() already called.
    """
    # Parse base birth datetime
    bi = base_chart.birth_info
    try:
        base_dt = datetime.fromisoformat(f"{bi.date}T{bi.time}")
    except Exception:
        base_dt = datetime.now()

    result = BTRResult(
        domain=domain,
        base_birth_dt=base_dt,
        window_minutes=window_minutes,
        n_simulations=n_simulations,
        n_successful=0,
    )

    if engine_fn is None:
        logger.warning(
            "[BTR] engine_fn is None; returning empty simulation result. "
            "Pass engine_fn(chart, domain) to execute Monte Carlo BTR."
        )
        result.compute_stats()
        return result

    if seed is not None:
        random.seed(seed)

    # Generate random birth times
    offsets_sec = [
        random.uniform(-window_minutes * 60, window_minutes * 60)
        for _ in range(n_simulations)
    ]

    # ── Parallel execution (stdlib, no extra deps) ────────────────────────
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def _run_one(offset_sec: float) -> Optional[BTRSample]:
        try:
            sim_dt = base_dt + timedelta(seconds=offset_sec)

            # Recompute natal chart for the sampled birth time.
            from vedic_engine.core.swisseph_bridge import build_chart_from_birth_data
            from vedic_engine.data.loader import load_from_dict

            _ayanamsa_model = (bi.ayanamsa_model or "Lahiri").lower()
            _house_system = "placidus"

            sim_raw = build_chart_from_birth_data(
                name=bi.name,
                date_str=sim_dt.strftime("%Y-%m-%d"),
                time_str=sim_dt.strftime("%H:%M:%S"),
                place=bi.place,
                latitude=bi.latitude,
                longitude=bi.longitude,
                tz_offset=bi.timezone,
                ayanamsa=_ayanamsa_model,
                house_system=_house_system,
                use_true_node=False,
            )
            sim_chart = load_from_dict(sim_raw)

            prediction = engine_fn(sim_chart, domain)

            conf = 0.5
            level = "UNKNOWN"
            if isinstance(prediction, dict):
                # Support both flat and nested confidence payloads.
                c = prediction.get("confidence")
                if isinstance(c, dict):
                    conf = float(c.get("overall", c.get("final", 0.5)))
                    level = str(c.get("level", prediction.get("prediction_level", "UNKNOWN")))
                elif isinstance(c, (int, float)):
                    conf = float(c)
                    level = str(prediction.get("prediction_level", "UNKNOWN"))
                else:
                    conf = float(prediction.get("overall", prediction.get("final", 0.5)))
                    level = str(prediction.get("prediction_level", "UNKNOWN"))

            return BTRSample(
                birth_dt=sim_dt,
                confidence=max(0.0, min(1.0, conf)),
                domain=domain,
                prediction_level=level,
                details=prediction if isinstance(prediction, dict) else {"raw": str(prediction)},
            )
        except Exception as e:
            logger.debug(f"[BTR] sample failed: {e}")
            return None

    with ThreadPoolExecutor(max_workers=parallel_jobs) as pool:
        futures = {pool.submit(_run_one, off): off for off in offsets_sec}
        for fut in as_completed(futures):
            sample = fut.result()
            if sample is not None:
                result.samples.append(sample)
                result.n_successful += 1

    result.compute_stats()
    return result


# ─── Sensitivity analysis ─────────────────────────────────────────────────────

def lagna_sensitivity(
    base_birth_dt: datetime,
    latitude: float,
    longitude: float,
    timezone_offset: float,
    window_minutes: int = 30,
    resolution_minutes: int = 1,
) -> List[Dict[str, Any]]:
    """
    Compute how the Ascendant (Lagna) sign and degree changes across a time window.

    Useful for understanding how sensitive the chart is to birth time error
    BEFORE running the full engine.

    Returns
    -------
    List of dicts: [{
        "minutes_offset": int,
        "birth_time": str,
        "lagna_sign": str,
        "lagna_degree": float,
        "sign_changed": bool,   # changed from base
    }]

    Status: SCAFFOLD — works independently without engine.
    """
    results = []
    offsets = range(-window_minutes, window_minutes + 1, resolution_minutes)

    # Average Ascendant speed: ~1° per 4 minutes (varies by latitude and sign)
    # More accurate: call our chart computation for each minute step.
    # Simplified linear approximation shown here; full version calls the engine.

    # Approximate Ascendant rate: 360° / (23h 56m 4s) ≈ 0.2507°/min
    ASC_RATE_DEG_PER_MIN = 360.0 / (23 * 60 + 56.067)

    try:
        from vedic_engine.config import SIGN_NAMES
        sign_names = list(SIGN_NAMES) if hasattr(SIGN_NAMES, '__iter__') else [
            "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
            "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
        ]
    except Exception:
        sign_names = [
            "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
            "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
        ]

    # Compute base Lagna (stub — would call our engine in real version)
    base_lagna_deg = 0.0  # placeholder; wiring required

    for offset in offsets:
        sim_dt = base_birth_dt + timedelta(minutes=offset)
        sim_lagna = (base_lagna_deg + offset * ASC_RATE_DEG_PER_MIN) % 360.0
        sign_idx  = int(sim_lagna / 30)
        deg_in_sign = sim_lagna % 30

        results.append({
            "minutes_offset":  offset,
            "birth_time":      sim_dt.strftime("%H:%M:%S"),
            "lagna_approx_deg": round(sim_lagna, 3),
            "lagna_sign":      sign_names[sign_idx % 12],
            "degree_in_sign":  round(deg_in_sign, 3),
            "sign_changed":    (sign_idx != int(base_lagna_deg / 30)),
        })

    return results


# ─── D60 Temporal Brittleness Score (Logic Integration Manifest §3.9) ─────────

# Classical rule: each D60 segment spans exactly 0.5° of ecliptic longitude.
# At the average ascendant speed of ~1° per 4 minutes, 0.5° ≈ 2 real minutes.
# If the birth moment falls within 120 seconds (2 minutes) of any D60 boundary,
# the entire D60 layer becomes unreliable — the planet's D60 quality (shubha vs
# krura) could flip on a 2-minute birth time error, so predictions relying on
# D60 spiritual/karmic refinement should be flagged as brittle.

D60_DEG_PER_SEGMENT      = 0.5        # each D60 segment = 0.5° ecliptic
D10_DEG_PER_SEGMENT      = 3.0        # each D10 segment = 3°
D9_DEG_PER_SEGMENT       = 10.0 / 3   # each D9 segment = 3°20' ≈ 3.333°

# Ascendant average drift: 1° per 4 minutes = 0.25°/min = 15°/hour
# In seconds: 1° per 240 seconds
ASC_DEG_PER_SECOND       = 1.0 / 240.0  # degrees per second of real time

# Brittleness thresholds (seconds)
D60_HIGH_BRITTLE_SEC     = 120   # < 2 minutes → HIGH brittleness
D60_MEDIUM_BRITTLE_SEC   = 300   # < 5 minutes → MEDIUM brittleness


def compute_brittleness_score(
    lagna_degree_absolute: float,
    planet_longitudes: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Compute the D60 Temporal Brittleness Score for a chart.

    Determines how close each planet (and the Lagna) is to its D60 segment
    boundary and classifies prediction reliability accordingly.

    Classical basis (BPHS / Logic Integration Manifest §3.9):
      - Each D60 segment = 0.5° ecliptic longitude
      - Ascendant drifts ~1° per 4 minutes in real birth time
      - 0.5° segment ≈ 2 minutes (120 seconds) of birth time sensitivity
      - If a planet/Lagna is ≤120 seconds from its D60 boundary → HIGH brittleness
      - 120-300 seconds → MEDIUM brittleness
      - > 300 seconds → LOW brittleness

    Also reports D10 (career) and D9 (inner/marriage) boundary proximity.

    Args:
        lagna_degree_absolute : Lagna absolute sidereal longitude (0-360°)
        planet_longitudes     : Optional dict of planet absolute lons

    Returns:
        Dict with brittleness levels per item, summary, and advisory
    """
    all_points: Dict[str, float] = {"LAGNA": lagna_degree_absolute}
    if planet_longitudes:
        all_points.update(planet_longitudes)

    results: Dict[str, Dict] = {}
    overall_worst = "LOW"

    for name, lon in all_points.items():
        # ── D60 boundary proximity ─────────────────────────────────────────
        within_d60_seg = lon % D60_DEG_PER_SEGMENT
        # Distance to nearest boundary: min of (within_seg, seg_size - within_seg)
        dist_to_d60_bdry = min(within_d60_seg, D60_DEG_PER_SEGMENT - within_d60_seg)
        d60_sec = dist_to_d60_bdry / ASC_DEG_PER_SECOND

        if d60_sec < D60_HIGH_BRITTLE_SEC:
            d60_level = "HIGH"
        elif d60_sec < D60_MEDIUM_BRITTLE_SEC:
            d60_level = "MEDIUM"
        else:
            d60_level = "LOW"

        # ── D10 boundary proximity ─────────────────────────────────────────
        within_d10_seg = lon % D10_DEG_PER_SEGMENT
        dist_to_d10_bdry = min(within_d10_seg, D10_DEG_PER_SEGMENT - within_d10_seg)
        d10_sec = dist_to_d10_bdry / ASC_DEG_PER_SECOND
        d10_level = "HIGH" if d10_sec < 720 else ("MEDIUM" if d10_sec < 1800 else "LOW")  # 12/30-min thresholds

        # ── D9 boundary proximity ──────────────────────────────────────────
        within_d9_seg = lon % D9_DEG_PER_SEGMENT
        dist_to_d9_bdry = min(within_d9_seg, D9_DEG_PER_SEGMENT - within_d9_seg)
        d9_sec = dist_to_d9_bdry / ASC_DEG_PER_SECOND
        d9_level = "HIGH" if d9_sec < 800 else ("MEDIUM" if d9_sec < 2000 else "LOW")  # ~13/33-min thresholds

        # Composite worst-level for this planet
        levels = [d60_level, d10_level, d9_level]
        planet_worst = "HIGH" if "HIGH" in levels else ("MEDIUM" if "MEDIUM" in levels else "LOW")
        if planet_worst == "HIGH" or (planet_worst == "MEDIUM" and overall_worst == "LOW"):
            overall_worst = planet_worst

        results[name] = {
            "lon":               round(lon, 4),
            "d60_sec_to_boundary": round(d60_sec, 1),
            "d60_brittleness":   d60_level,
            "d10_sec_to_boundary": round(d10_sec, 1),
            "d10_brittleness":   d10_level,
            "d9_sec_to_boundary": round(d9_sec, 1),
            "d9_brittleness":    d9_level,
            "worst_brittleness": planet_worst,
        }

    # Build summary
    high_items   = [n for n, v in results.items() if v["worst_brittleness"] == "HIGH"]
    medium_items = [n for n, v in results.items() if v["worst_brittleness"] == "MEDIUM"]

    advisory = ""
    if overall_worst == "HIGH":
        advisory = (
            f"CRITICAL: {', '.join(high_items)} within 2 minutes of a D60 boundary. "
            "D60-dependent predictions are unreliable. Rectify birth time before using "
            "D60/D10 spiritual or career-timing overlays."
        )
    elif overall_worst == "MEDIUM":
        advisory = (
            f"CAUTION: {', '.join(medium_items)} within 5 minutes of a divisional boundary. "
            "Use Monte Carlo time-jitter validation before finalising fine-grained predictions."
        )
    else:
        advisory = "LOW BRITTLENESS: All planets well within divisional segments. Predictions are stable."

    return {
        "overall_brittleness": overall_worst,
        "details":             results,
        "high_brittleness":    high_items,
        "medium_brittleness":  medium_items,
        "advisory":            advisory,
        "d60_threshold_high_sec": D60_HIGH_BRITTLE_SEC,
        "d60_threshold_medium_sec": D60_MEDIUM_BRITTLE_SEC,
    }
