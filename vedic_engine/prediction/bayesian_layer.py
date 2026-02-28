"""
Bayesian Confidence Layer — Vedic Astrology Engine.

Classical Vedic prediction requires multiple timing systems to CONVERGE.
This module models each domain's success probability as a Beta distribution
that gets updated by evidence from each active system.

Why Bayesian over simple weighted sum:
  - Multiple weak positive signals compound (product of posteriors > mean)
  - A strong contradictory signal (e.g., Saturn transit opposing) suppresses
    the posterior significantly — matching classical "obstacle" teaching
  - Yields a credible interval (uncertainty range), not just a point estimate
  - Separates NATAL potential (prior) from CURRENT activation (likelihood)

Usage:
    from vedic_engine.prediction.bayesian_layer import compute_bayesian_confidence
    result = compute_bayesian_confidence(components, domain)
    # result: {posterior_mean, credible_interval, evidence_weight, ...}
"""
from __future__ import annotations
from typing import Dict, Tuple


# ─── Prior setting ────────────────────────────────────────────────────────────

def _structural_prior(yoga: float, functional: float, house_lord: float
                      ) -> Tuple[float, float]:
    """
    Build Beta(α, β) prior from natal chart strength.
    Strong natal potential → optimistic prior (α > β).
    Weak natal potential  → pessimistic prior (β > α).

    Prior concentration: total α+β = 4 (weak prior, data will dominate).
    """
    # Composite natal score
    natal = 0.40 * yoga + 0.35 * functional + 0.25 * house_lord
    natal = max(0.05, min(0.95, natal))

    concentration = 4.0   # how strongly we trust the prior (4 = weak)
    alpha = natal * concentration
    beta_ = (1.0 - natal) * concentration
    return alpha, beta_


# ─── Evidence updates ─────────────────────────────────────────────────────────
# Each active system contributes pseudo-counts to the posterior.
# Think of each "unit of evidence" as a Bernoulli trial: success = favors domain,
# failure = doesn't. Beta is the conjugate prior for Bernoulli.

def _dasha_evidence(dasha_alignment: float) -> Tuple[float, float]:
    """Dasha is the primary timer — carries most weight (equiv. 3 observations)."""
    strength = 3.0
    return dasha_alignment * strength, (1.0 - dasha_alignment) * strength


def _transit_evidence(transit_support: float, ashtakvarga: float) -> Tuple[float, float]:
    """Transit + BAV composite (equiv. 2 observations)."""
    composite = 0.65 * transit_support + 0.35 * ashtakvarga
    strength = 2.0
    return composite * strength, (1.0 - composite) * strength


def _kp_evidence(kp_confirmation: float) -> Tuple[float, float]:
    """
    KP sublord is a binary precision signal.
    If confirmed (>0.5) → strong positive (equiv. 2 successes).
    If denied (<0.2)   → strong negative (equiv. 2 failures).
    In between         → weak ambiguous (0.5 successes each).
    """
    if kp_confirmation > 0.5:
        return 2.0, 0.2
    elif kp_confirmation < 0.2:
        return 0.2, 2.0
    else:
        return 0.6, 0.6


# ─── Main function ─────────────────────────────────────────────────────────────

def compute_bayesian_confidence(
    components: Dict[str, float],
    domain: str = "generic",
) -> Dict:
    """
    Bayesian Beta-conjugate update of domain success probability.

    Parameters
    ----------
    components : dict of confidence component scores (from confidence.py)
        Keys: dasha_alignment, transit_support, ashtakvarga_support,
              yoga_activation, kp_confirmation, functional_alignment,
              house_lord_strength
    domain : str — used for labelling only

    Returns
    -------
    dict:
        posterior_mean     : float [0,1] — best estimate of domain probability
        credible_low       : float — 10th percentile of posterior
        credible_high      : float — 90th percentile of posterior
        uncertainty        : float — width of 80% credible interval
        evidence_weight    : float — total pseudo-count (prior+evidence)
        alpha              : float — posterior Beta alpha
        beta_              : float — posterior Beta beta
        bayesian_verdict   : str
        factors            : dict — contribution of each system
    """
    from scipy.stats import beta as beta_dist

    da  = float(components.get("dasha_alignment",     0.30))
    ts  = float(components.get("transit_support",     0.30))
    av  = float(components.get("ashtakvarga_support", 0.30))
    yo  = float(components.get("yoga_activation",     0.30))
    kp  = float(components.get("kp_confirmation",     0.00))
    fn  = float(components.get("functional_alignment",0.50))
    hl  = float(components.get("house_lord_strength", 0.30))

    # ── Prior from natal chart ────────────────────────────────────
    alpha, beta_ = _structural_prior(yo, fn, hl)
    factors = {"prior_natal": round(alpha / (alpha + beta_), 3)}

    # ── Likelihood updates ────────────────────────────────────────
    da_a, da_b = _dasha_evidence(da)
    alpha += da_a; beta_ += da_b
    factors["dasha"] = round(da_a / (da_a + da_b + 1e-9), 3)

    tr_a, tr_b = _transit_evidence(ts, av)
    alpha += tr_a; beta_ += tr_b
    factors["transit"] = round(tr_a / (tr_a + tr_b + 1e-9), 3)

    kp_a, kp_b = _kp_evidence(kp)
    alpha += kp_a; beta_ += kp_b
    factors["kp"] = round(kp_a / (kp_a + kp_b + 1e-9), 3)

    # ── Posterior statistics ──────────────────────────────────────
    posterior_mean = alpha / (alpha + beta_)
    # 80% credible interval (10th – 90th percentile)
    credible_low  = beta_dist.ppf(0.10, alpha, beta_)
    credible_high = beta_dist.ppf(0.90, alpha, beta_)
    uncertainty   = credible_high - credible_low

    # ── Verdict ───────────────────────────────────────────────────
    if posterior_mean >= 0.70:
        verdict = "STRONG"
    elif posterior_mean >= 0.55:
        verdict = "MODERATE"
    elif posterior_mean >= 0.40:
        verdict = "MARGINAL"
    elif posterior_mean >= 0.25:
        verdict = "WEAK"
    else:
        verdict = "VERY WEAK"

    # Confidence classification based on uncertainty
    if uncertainty < 0.15:
        certainty = "HIGH CERTAINTY"
    elif uncertainty < 0.25:
        certainty = "MODERATE CERTAINTY"
    else:
        certainty = "UNCERTAIN"

    return {
        "posterior_mean":   round(posterior_mean, 3),
        "credible_low":     round(credible_low, 3),
        "credible_high":    round(credible_high, 3),
        "uncertainty":      round(uncertainty, 3),
        "evidence_weight":  round(alpha + beta_, 2),
        "alpha":            round(alpha, 3),
        "beta_":            round(beta_, 3),
        "bayesian_verdict": verdict,
        "certainty_label":  certainty,
        "factors":          factors,
        "domain":           domain,
    }


if __name__ == "__main__":
    # Self-test
    test = {
        "dasha_alignment": 0.33,
        "transit_support": 0.07,
        "ashtakvarga_support": 0.30,
        "yoga_activation": 0.40,
        "kp_confirmation": 0.00,
        "functional_alignment": 0.50,
        "house_lord_strength": 0.33,
    }
    r = compute_bayesian_confidence(test, "CAREER")
    print("Bayesian result:")
    for k, v in r.items():
        print(f"  {k:25s}: {v}")
