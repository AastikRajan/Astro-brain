"""
Signification analyzer — maps planets to life domains via house significations.
Used by the prediction engine to determine domain relevance of each planet.
"""
from __future__ import annotations
from typing import Dict, List, Optional

from vedic_engine.config import Planet, SIGN_LORDS, Sign as _Sign

DOMAIN_HOUSES = {
    # KP-corrected promise houses (fruitification triggers)
    "career":          {2, 6, 10, 11},      # 1/5/9 are NEGATORS for career
    "finance_active":  {2, 6, 11},          # active earned income
    "finance_invest":  {2, 5, 8, 11},       # investments / windfalls (12 = drain)
    "finance":         {2, 6, 11},          # alias → active income (most queries)
    "marriage":        {2, 7, 11},          # 4 is NOT marriage; 8 = duration only
    "health_recovery": {1, 11},             # recovery from illness
    "health_crisis":   {1, 6, 8, 12},       # onset of health problems
    "health":          {1, 6, 8, 12},       # alias → crisis set for most queries
    "children":        {2, 5, 11},          # 9 removed (9 = father, not children)
    "property":        {4, 12},             # 4 = home; 12 = loss/purchase abroad
    "spiritual":       {4, 8, 9, 12},
    "travel":          {3, 9, 12},          # 8 = near-death travel only
}

# Houses that NEGATE (deny) a domain when sub-lord signifies them instead
DOMAIN_NEGATORS = {
    "career":   {1, 5, 9},    # 1=self-employment loss, 5=education break, 9=non-job luck
    "marriage": {1, 6, 10},   # 1=self, 6=delay/obstacles, 10=career over marriage
    "finance":  {12},          # 12 = capital drain
    "health":   set(),
    "children": set(),
    "property": set(),
    "spiritual":set(),
    "travel":   set(),
    "finance_active":  {12},
    "finance_invest":  {12},
    "health_recovery": set(),
    "health_crisis":   set(),
}

NATURAL_KARAKAS: Dict[str, List[str]] = {
    "SUN":     ["career", "health", "health_crisis", "spiritual"],
    "MOON":    ["finance", "finance_active", "health", "property"],
    "MARS":    ["career", "health", "health_crisis", "property", "travel"],
    "MERCURY": ["career", "finance", "finance_active", "travel"],
    "JUPITER": ["finance", "finance_invest", "marriage", "children", "spiritual"],
    "VENUS":   ["finance", "finance_active", "marriage"],
    "SATURN":  ["career", "property", "spiritual", "travel"],
    "RAHU":    ["travel", "career"],
    "KETU":    ["spiritual", "health", "health_crisis"],
}


def build_planet_significations(
        planet_houses: Dict[str, int],
        lagna_sign: int,
        kp_significations: Optional[Dict] = None,
) -> Dict[str, Dict]:
    """
    For each planet compute its domain signification scores.

    Combines:
      - House it occupies (direct signification)
      - Houses it lords  (natural domain from sign lordship)
      - Natural karaka domains
      - Optional KP chain significations
      - KP negator reduction: if planet strongly signifies negator houses,
        its domain score is reduced proportionally.

    Returns {planet: {domain: score 0-1}}
    """
    # Build lord->house map
    lord_of_houses: Dict[str, List[int]] = {}
    for house_num in range(1, 13):
        sign_idx = (lagna_sign + house_num - 1) % 12
        lord = SIGN_LORDS.get(_Sign(sign_idx))
        if lord:
            lord_of_houses.setdefault(lord.name, []).append(house_num)

    result = {}
    for planet, occ_house in planet_houses.items():
        domain_scores: Dict[str, float] = {}

        for domain, houses in DOMAIN_HOUSES.items():
            score = 0.0

            # Occupation (strongest – 0.5 pts)
            if occ_house in houses:
                score += 0.5

            # Lordship (medium – 0.3 pts per house lorded)
            lorded = lord_of_houses.get(planet, [])
            for lh in lorded:
                if lh in houses:
                    score += 0.3

            # Natural karaka (0.2 pts)
            if domain in NATURAL_KARAKAS.get(planet, []):
                score += 0.2

            # KP chain (0.15 pts)
            if kp_significations and planet in kp_significations:
                kp_houses = set(kp_significations[planet])
                for kph in kp_houses:
                    if kph in houses:
                        score += 0.15
                        break

            # KP negator penalty: if planet occupies or lords negator houses,
            # reduce its promise score for this domain.
            negators = DOMAIN_NEGATORS.get(domain, set())
            if negators:
                neg_score = 0.0
                if occ_house in negators:
                    neg_score += 0.4
                for lh in lorded:
                    if lh in negators:
                        neg_score += 0.25
                if kp_significations and planet in kp_significations:
                    kp_houses = set(kp_significations[planet])
                    for kph in kp_houses:
                        if kph in negators:
                            neg_score += 0.15
                            break
                # Apply: negator reduces promise proportionally
                score = max(0.0, score - neg_score * 0.6)

            domain_scores[domain] = min(1.0, round(score, 3))

        result[planet] = domain_scores

    return result


def rank_planets_for_domain(
        significations: Dict[str, Dict[str, float]],
        domain: str,
) -> List[Dict]:
    """Return planets ranked by their score for a given domain."""
    ranked = []
    for planet, domains in significations.items():
        score = domains.get(domain, 0.0)
        if score > 0:
            ranked.append({"planet": planet, "score": score})
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked
