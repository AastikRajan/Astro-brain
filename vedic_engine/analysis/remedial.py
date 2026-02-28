"""
Remedial Measures (Upāya) Engine.

Rules from BPHS Ch.84–86 (Parāśara) and classical commentaries:
  - Gem, Mantra (with count), Donation, Yantra, Deity for each planet
  - Contraindications (when NOT to prescribe a remedy)
  - Weakness/affliction triggers: debilitation, combustion, 6/8/12 house,
    enemy sign, malefic aspects, war defeat
  - Affliction severity score → recommended remedies ranked by urgency
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

# ─── Planet Remedy Data (BPHS canonical) ─────────────────────────────────────

REMEDIES: Dict[str, Dict] = {
    "SUN": {
        "gem":        "Ruby (Manikya) or Red Coral",
        "mantra":     "Om Ādityāya Namah",
        "mantra_count": 7000,
        "weekday":    "Sunday",
        "donation":   "Wheat, jaggery, red cloth, copper (to Brahmins/public workers on Sunday)",
        "yantra":     "Surya Yantra (copper)",
        "deity":      "Aditya (Sun god) / Lord Rāma",
        "color":      "Red / orange",
        "metal":      "Copper",                  # Parāśara idol material
        "fast":       "Sunday fast (Ravivar Vrat)",
        "contra": [
            "Do not weaken if Surya rules benefic houses (5th/9th from lagna) and is strong",
            "Avoid if Surya is combust (within 6° of itself — not applicable)",
            "Do not prescribe Ruby if Sun is severely afflicted by Saturn without benefic aspects",
        ],
    },
    "MOON": {
        "gem":        "Pearl (Moti) or White Sapphire",
        "mantra":     "Om Somāya Namah",
        "mantra_count": 11000,
        "weekday":    "Monday",
        "donation":   "Rice, milk, white foods, silver, white cloth (to women/Brahmins on Monday)",
        "yantra":     "Chandra Yantra (silver or quartz crystal)",
        "deity":      "Śiva / Pārvatī / Shiva as Chandraśekhara",
        "color":      "White / silver",
        "metal":      "Rock crystal (sphaṭika)",
        "fast":       "Monday fast (Somavar Vrat)",
        "contra": [
            "Avoid Pearl if Moon is debilitated in Scorpio",
            "Avoid if Moon is lord of benefic Kendra houses (e.g. Cancer/Taurus lagna — Moon is lagnesh)",
            "Do not wear if Moon is in inimical sign without remediation",
        ],
    },
    "MARS": {
        "gem":        "Red Coral (Moonga)",
        "mantra":     "Om Aṅgārakāya Namah",
        "mantra_count": 11000,
        "weekday":    "Tuesday",
        "donation":   "Red lentils (masoor dal), red cloth, copper items (Tuesday)",
        "yantra":     "Maṅgala Yantra or Hanuman Yantra (copper)",
        "deity":      "Hanumān / Kārttikeya (Skanda)",
        "color":      "Red",
        "metal":      "Red sandalwood / copper",
        "fast":       "Tuesday fast (Mangalvar Vrat)",
        "contra": [
            "Avoid Coral if Mars is lord of 8th or 12th from lagna",
            "Do not weaken Mars if it is lagnesh (Aries/Scorpio lagna) and strong",
            "Avoid if Mars is in own sign (Aries/Scorpio) without affliction",
        ],
    },
    "MERCURY": {
        "gem":        "Emerald (Panna)",
        "mantra":     "Om Budhāya Namah",
        "mantra_count": 9000,
        "weekday":    "Wednesday",
        "donation":   "Green foods, green cloth, books, moong dal (Wednesday)",
        "yantra":     "Budha Yantra (gold)",
        "deity":      "Kṛṣṇa / Viṣṇu",
        "color":      "Green",
        "metal":      "Gold",
        "fast":       "Wednesday fast (Budhavar Vrat)",
        "contra": [
            "Avoid Emerald if Mercury is lord of 2nd/11th (wealth houses) in strong position",
            "Do not use if Mercury is debilitated in Pisces without dignity",
            "Caution if Mercury is combust (within 14° of Sun for combustion)",
        ],
    },
    "JUPITER": {
        "gem":        "Yellow Sapphire (Pukhraj)",
        "mantra":     "Om Bṛhaspataye Namah",
        "mantra_count": 9000,
        "weekday":    "Thursday",
        "donation":   "Yellow cloth, books, cow's milk, gold, turmeric (to Brahmins on Thursday)",
        "yantra":     "Guru Yantra (golden / brass)",
        "deity":      "Viṣṇu / Brihaspati",
        "color":      "Yellow / gold",
        "metal":      "Gold",
        "fast":       "Thursday fast (Guruvar Vrat)",
        "contra": [
            "Avoid if Jupiter is exalted in Cancer and already rules benefic houses",
            "Use mantras instead of stone if Jupiter is combust or very debilitated",
            "Do not wear Pukhraj if Jupiter rules 3rd/6th/8th from lagna",
        ],
    },
    "VENUS": {
        "gem":        "Diamond (Heera) or White Sapphire (Safed Pukhraj)",
        "mantra":     "Om Śukrāya Namah",
        "mantra_count": 16000,
        "weekday":    "Friday",
        "donation":   "White garments, sweets, white flowers, silver, curd (Friday)",
        "yantra":     "Śukra Yantra (silver)",
        "deity":      "Lakṣmī / Śukrāchārya",
        "color":      "White / cream",
        "metal":      "Silver",
        "fast":       "Friday fast (Shukravar Vrat)",
        "contra": [
            "Avoid if Venus is extremely strong or lagnesh (Taurus/Libra lagna)",
            "Do not prescribe if Venus rules an auspicious Kendra and is already exalted",
        ],
    },
    "SATURN": {
        "gem":        "Blue Sapphire (Neelam)",
        "mantra":     "Om Śanaiścarāya Namah",
        "mantra_count": 23000,
        "weekday":    "Saturday",
        "donation":   "Black sesame seeds, black cloth, iron, mustard oil, feed poor/cows (Saturday)",
        "yantra":     "Śani Yantra (iron / lead)",
        "deity":      "Śani Dev / Hanumān",
        "color":      "Black / dark blue",
        "metal":      "Iron",
        "fast":       "Saturday fast (Shanivar Vrat)",
        "contra": [
            "EXTREME CAUTION: Never wear Neelam without expert advice — can intensify malefic periods",
            "Avoid if Saturn rules benefic 9th/10th houses and is strong (e.g. Aries lagna)",
            "Do not wear if Saturn is in Ardra or Jyeshtha nakshatra (extreme malefic placement)",
            "Avoid if Saturn is in Sade-Sati without proper dosage assessment",
        ],
    },
    "RAHU": {
        "gem":        "Hessonite Garnet (Gomed)",
        "mantra":     "Om Rāṁ Rāhave Namah",
        "mantra_count": 8000,
        "weekday":    "Wednesday (or Thursday evening — Rahu Kalam)",
        "donation":   "Dark items — black blankets, blue flowers, coconut, black sesame (Wednesday)",
        "yantra":     "Rahu Yantra (black glass / silver)",
        "deity":      "Gaṇeśa / Śiva / Durgā",
        "color":      "Smoky / dark blue",
        "metal":      "Glass (dark)",
        "fast":       "Rahu Kala worship each day; Saturday or Wednesday Rahu upaya",
        "contra": [
            "Avoid Gomed if Rahu is in an exalted position or in 5th/9th houses benefically",
            "Do not use if Rahu is already strong through good nakshatra (Swati, Ardra)",
        ],
    },
    "KETU": {
        "gem":        "Cat's Eye (Lehsunia / Vaidurya)",
        "mantra":     "Om Keṁ Ketave Namah",
        "mantra_count": 7000,
        "weekday":    "Thursday",
        "donation":   "Mustard seeds, blankets, camphor, sesame, offer in Ketu-ruled temples (Thursday)",
        "yantra":     "Ketu Yantra (bell-metal / iron)",
        "deity":      "Bhairava / Navagraha form / Gaṇapati",
        "color":      "Smoky / grey / multi-color",
        "metal":      "Bell-metal (kansa)",
        "fast":       "Thursday Ketu worship; Navagraha puja",
        "contra": [
            "Do not wear Cat's Eye if Ketu is in own nakshatra and functioning as natural benefic",
            "Avoid if Ketu occupies 9th/5th house without malefic aspects",
        ],
    },
}

# ─── Affliction Detection ─────────────────────────────────────────────────────

# Classical debilitation signs (0-indexed)
DEBILITATION_SIGNS = {
    "SUN": 6, "MOON": 7, "MARS": 3, "MERCURY": 11, "JUPITER": 9,
    "VENUS": 5, "SATURN": 0, "RAHU": 5, "KETU": 11,
}

# Exaltation signs
EXALTATION_SIGNS = {
    "SUN": 0, "MOON": 1, "MARS": 9, "MERCURY": 5, "JUPITER": 3,
    "VENUS": 11, "SATURN": 6, "RAHU": 2, "KETU": 8,
}


def _is_debilitated(planet: str, sign_idx: int) -> bool:
    return DEBILITATION_SIGNS.get(planet) == sign_idx


def _is_exalted(planet: str, sign_idx: int) -> bool:
    return EXALTATION_SIGNS.get(planet) == sign_idx


def compute_affliction_score(
    planet: str,
    sign_idx: int,
    house: int,                   # 1-12
    shadbala_ratio: float,        # 0-2+
    is_combust: bool = False,
    is_retrograde: bool = False,
    malefic_aspects: int = 0,     # number of malefic aspects received
    war_defeated: bool = False,
) -> float:
    """
    Compute affliction severity score (0.0 = fully healthy, 1.0 = severely afflicted).
    Used to rank which planets most need remediation.
    """
    score = 0.0

    # Debilitation
    if _is_debilitated(planet, sign_idx):
        score += 0.35

    # Dusthana houses (6, 8, 12)
    if house in (6, 8, 12):
        score += 0.25

    # Weak Shadbala
    if shadbala_ratio < 0.75:
        score += 0.20 * (1.0 - shadbala_ratio / 0.75)

    # Combustion
    if is_combust:
        score += 0.15

    # Malefic aspects
    score += min(0.15, malefic_aspects * 0.05)

    # Graha Yuddha defeat
    if war_defeated:
        score += 0.10

    # Retrograde (ambiguous — can be strong or weak; slight penalty)
    if is_retrograde and shadbala_ratio < 1.0:
        score += 0.05

    # Exaltation reduces score
    if _is_exalted(planet, sign_idx):
        score = max(0.0, score - 0.20)

    return min(1.0, score)


# ─── Remedy Recommendation ────────────────────────────────────────────────────

def get_remedies(
    planet_states: Dict[str, Dict],
    lagna: int = None,
    threshold: float = 0.30,
) -> List[Dict]:
    """
    Compute affliction scores for all planets and return ranked remedies.

    planet_states: {
        "SUN": {
            "sign_idx": 6, "house": 8, "shadbala_ratio": 0.7,
            "combust": False, "retrograde": False,
            "malefic_aspects": 1, "war_defeated": False
        }, ...
    }
    lagna: lagna sign index (0-11) for contraindication checks
    threshold: minimum affliction score to trigger recommendation

    Returns list of dicts sorted by affliction score descending:
    {planet, affliction_score, urgency, gem, mantra, mantra_count,
     weekday, donation, yantra, deity, contra, rationale}
    """
    results = []

    for planet, state in planet_states.items():
        if planet not in REMEDIES:
            continue

        score = compute_affliction_score(
            planet       = planet,
            sign_idx     = state.get("sign_idx", 0),
            house        = state.get("house", 1),
            shadbala_ratio = state.get("shadbala_ratio", 1.0),
            is_combust   = state.get("combust", False),
            is_retrograde = state.get("retrograde", False),
            malefic_aspects = state.get("malefic_aspects", 0),
            war_defeated = state.get("war_defeated", False),
        )

        if score < threshold:
            continue

        remedy = REMEDIES[planet]
        urgency = "HIGH" if score >= 0.65 else ("MODERATE" if score >= 0.45 else "LOW")

        rationale_parts = []
        si = state.get("sign_idx", 0)
        if _is_debilitated(planet, si):
            rationale_parts.append("debilitated")
        if state.get("house", 1) in (6, 8, 12):
            rationale_parts.append(f"in {state['house']}th house (dusthana)")
        if state.get("shadbala_ratio", 1.0) < 0.75:
            rationale_parts.append(f"weak Shadbala ({state['shadbala_ratio']:.2f})")
        if state.get("combust"):
            rationale_parts.append("combust")
        if state.get("malefic_aspects", 0) > 0:
            rationale_parts.append(f"{state['malefic_aspects']} malefic aspect(s)")
        if state.get("war_defeated"):
            rationale_parts.append("defeated in Graha Yuddha")

        results.append({
            "planet":           planet,
            "affliction_score": round(score, 3),
            "urgency":          urgency,
            "gem":              remedy["gem"],
            "mantra":           remedy["mantra"],
            "mantra_count":     remedy["mantra_count"],
            "weekday":          remedy["weekday"],
            "donation":         remedy["donation"],
            "yantra":           remedy["yantra"],
            "deity":            remedy["deity"],
            "color":            remedy["color"],
            "metal":            remedy["metal"],
            "fast":             remedy["fast"],
            "contra":           remedy["contra"],
            "rationale":        "; ".join(rationale_parts) if rationale_parts else "general weakness",
        })

    results.sort(key=lambda x: x["affliction_score"], reverse=True)
    return results


def format_remedies_text(remedies: List[Dict]) -> str:
    """Plain-text summary for display in main.py."""
    if not remedies:
        return "No severely afflicted planets requiring immediate remediation."
    lines = []
    for r in remedies:
        lines.append(
            f"  [{r['urgency']}] {r['planet']} (score={r['affliction_score']:.2f})  "
            f"Reason: {r['rationale']}"
        )
        lines.append(f"    Gem     : {r['gem']}")
        lines.append(f"    Mantra  : {r['mantra']}  (×{r['mantra_count']:,})")
        lines.append(f"    Donate  : {r['donation']}")
        lines.append(f"    Deity   : {r['deity']}")
        if r['contra']:
            lines.append(f"    ⚠ Caution: {r['contra'][0]}")
    return "\n".join(lines)
