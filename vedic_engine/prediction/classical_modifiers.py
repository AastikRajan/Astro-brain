from __future__ import annotations

import math
from typing import Any, Dict


DOMAIN_CONFIG = {
    "career": {
        "primary_house": 10,
        "secondary_houses": [1, 6],
        "karaka": "SATURN",
        "house_lord_key": 10,
        "kp_cusp": 10,
        "divisional": "D10",
        "yoga_tags": ["raja", "mahapurusha", "adhi", "bhadra", "ruchaka", "saraswati", "career", "power"],
        "yoga_boosts": {"dharma_karmadhipati": 0.35, "adhi": 0.25, "bhadra": 0.20, "ruchaka": 0.20, "saraswati": 0.20},
    },
    "finance": {
        "primary_house": 11,
        "secondary_houses": [2, 5, 9],
        "karaka": "JUPITER",
        "house_lord_key": 11,
        "kp_cusp": 11,
        "divisional": "D2",
        "yoga_tags": ["dhana", "wealth", "lakshmi", "finance"],
        "yoga_boosts": {"maha_dhan": 0.40, "dhana": 0.30, "lakshmi": 0.25, "gajakesari": 0.15},
    },
    "marriage": {
        "primary_house": 7,
        "secondary_houses": [1, 2],
        "karaka": "VENUS",
        "house_lord_key": 7,
        "kp_cusp": 7,
        "divisional": "D9",
        "yoga_tags": ["marriage", "kalatra", "vivaha", "parivartana"],
        "yoga_boosts": {"parivartana_7h": 0.25, "early_marriage": 0.20, "love_marriage": 0.15, "gajakesari": 0.10},
    },
    "health": {
        "primary_house": 1,
        "secondary_houses": [6, 8, 12],
        "karaka": "SUN",
        "house_lord_key": 1,
        "kp_cusp": 1,
        "divisional": "D30",
        "yoga_tags": ["health", "longevity", "aristha", "balarishta", "medical"],
        "yoga_boosts": {"balarishta_bhanga": 0.40, "purna_ayush": 0.35, "arishta": -0.30, "vipreet_raja": 0.30},
    },
}


DASHA_WEIGHTS = {
    "career": {"vimshottari": 0.40, "chara": 0.25, "yogini": 0.15, "ashtottari": 0.10, "other": 0.10},
    "finance": {"vimshottari": 0.45, "ashtottari": 0.25, "chara": 0.15, "yogini": 0.10, "other": 0.05},
    "marriage": {"vimshottari": 0.40, "chara": 0.25, "yogini": 0.20, "ashtottari": 0.10, "other": 0.05},
    "health": {"niryana_shoola": 0.40, "kalachakra": 0.20, "vimshottari": 0.20, "sudarshana": 0.15, "other": 0.05},
}


CONVERGENCE_TABLE = {
    0.0: 0.05,
    0.2: 0.10,
    0.4: 0.325,
    0.6: 0.725,
    0.8: 0.965,
    1.0: 0.999,
}


BAV_TRANSIT_MULTIPLIERS = {
    0: 0.0,
    1: 0.0,
    2: 0.0,
    3: 0.0,
    4: 1.0,
    5: 1.5,
    6: 1.5,
    7: 1.5,
    8: 1.5,
}


TRANSIT_FRAME_WEIGHTS = {
    "lagna": 0.50,
    "moon": 0.275,
    "dasha_lord": 0.20,
}


CONFIDENCE_LABELS = {
    (0.00, 0.08): "Highly Unlikely",
    (0.08, 0.15): "Event Latent / No Trigger",
    (0.15, 0.35): "Unlikely but Possible",
    (0.35, 0.58): "Average Results / High Friction",
    (0.58, 0.63): "Neutral Results",
    (0.63, 0.70): "Likely",
    (0.70, 0.78): "Moderate Success",
    (0.78, 0.88): "Highly Probable",
    (0.88, 1.00): "Will Definitely Happen",
}


AVASTHA_COEFFICIENTS = {
    "deepta": 1.00,
    "swastha": 0.875,
    "mudita": 0.75,
    "normal": 0.50,
    "dina": 0.125,
    "dukhita": 0.25,
    "kshobhita": 0.125,
    "vriddha": 0.10,
    "mrita": 0.00,
}


def compute_dosha_modifier(computed: Dict[str, Any], domain: str) -> float:
    mod = 1.0
    doshas = computed.get("doshas", {}) if isinstance(computed, dict) else {}
    if not isinstance(doshas, dict):
        return mod

    if domain == "marriage":
        manglik = doshas.get("manglik", {})
        if isinstance(manglik, dict) and manglik.get("present", False):
            severity = int(manglik.get("severity", 0) or 0)
            cancelled = bool(manglik.get("cancelled", False))
            if not cancelled:
                if severity >= 3:
                    mod *= 0.70
                elif severity >= 1:
                    mod *= 0.85

    kala_sarpa = doshas.get("kala_sarpa", {})
    if isinstance(kala_sarpa, dict) and kala_sarpa.get("present", False):
        mod *= 0.50 if kala_sarpa.get("partial", False) else 0.85

    if domain == "health":
        pitru = doshas.get("pitru", {})
        if isinstance(pitru, dict) and pitru.get("present", False):
            mod *= 0.80

    return max(0.05, min(mod, 1.5))


def compute_planet_effectiveness(planet_name: str, computed: Dict[str, Any]) -> float:
    planet_name = str(planet_name or "").upper()

    avasthas = computed.get("avasthas", {})
    if isinstance(avasthas, dict) and isinstance(avasthas.get("deeptadi"), dict):
        avasthas = avasthas.get("deeptadi", {})
    avastha_data = avasthas.get(planet_name, {}) if isinstance(avasthas, dict) else {}
    state = str((avastha_data.get("state") if isinstance(avastha_data, dict) else None) or "normal").lower()
    avastha_coeff = AVASTHA_COEFFICIENTS.get(state, 0.50)
    if avastha_coeff == 0.0:
        return 0.0

    # Use net_ratio (total - saptavargaja) to avoid double-counting with Vimshopak
    # (Research File 1: Saptavargaja measures varga dignity, same as Vimshopak)
    ratio = 1.0
    shadbala = computed.get("shadbala", {})
    if isinstance(shadbala, dict) and isinstance(shadbala.get(planet_name), dict):
        sb_data = shadbala[planet_name]
        ratio = float(sb_data.get("net_ratio", sb_data.get("ratio", sb_data.get("ratio_to_min", 1.0))) or 1.0)
    else:
        shadbala_ratios = computed.get("shadbala_ratios", {})
        if isinstance(shadbala_ratios, dict):
            ratio = float(shadbala_ratios.get(planet_name, 1.0) or 1.0)
    shadbala_component = min(max(ratio, 0.0), 2.0)

    vim_score = 10.0
    vimshopak = computed.get("vimshopak", {})
    if isinstance(vimshopak, dict) and isinstance(vimshopak.get(planet_name), dict):
        vim_score = float(vimshopak[planet_name].get("score", 10) or 10)
    vimshopak_component = vim_score / 20.0

    bav_score = 4
    ashtakvarga = computed.get("ashtakvarga", {})
    bav_data = None
    if isinstance(ashtakvarga, dict):
        bav_data = (ashtakvarga.get("bav", {}) or {}).get(planet_name)
        if bav_data is None:
            bav_data = (ashtakvarga.get("bhinna", {}) or {}).get(planet_name)
    if isinstance(bav_data, list):
        planet_sign_idx = (computed.get("planet_signs", {}) or {}).get(planet_name)
        if isinstance(planet_sign_idx, int) and 0 <= planet_sign_idx < len(bav_data):
            bav_score = int(bav_data[planet_sign_idx])
    bav_component = max(0.0, min(bav_score / 8.0, 1.0))

    raw_effectiveness = 0.45 * shadbala_component + 0.35 * vimshopak_component + 0.20 * bav_component
    return max(0.0, min(2.0, avastha_coeff * raw_effectiveness))


def compute_bhava_effectiveness(house_num: int, lord_planet: str, computed: Dict[str, Any]) -> float:
    bhavabala = computed.get("bhavabala", {})
    house_data = {}
    if isinstance(bhavabala, dict):
        house_data = bhavabala.get(house_num, bhavabala.get(str(house_num), {}))
    rupas = float(house_data.get("rupas", 7.0) if isinstance(house_data, dict) else 7.0)
    normalized_bhava = rupas / 7.0

    lord_effectiveness = compute_planet_effectiveness(lord_planet, computed)
    lord_factor = math.log(lord_effectiveness + 1.0) / math.log(2.0)
    return max(0.0, normalized_bhava * max(lord_factor, 0.1))


def compute_classical_modifier(computed: Dict[str, Any], domain: str) -> float:
    domain_norm = str(domain or "").lower()
    cfg = DOMAIN_CONFIG.get(domain_norm, {})
    if not cfg:
        return 1.0

    karaka = cfg.get("karaka", "SUN")
    house_lord_key = cfg.get("house_lord_key", cfg.get("primary_house", 10))
    house_lords = computed.get("house_lords", {}) if isinstance(computed, dict) else {}
    lord_planet = house_lords.get(house_lord_key, house_lords.get(str(house_lord_key), karaka))

    planet_eff = compute_planet_effectiveness(str(lord_planet), computed)
    bhava_eff = compute_bhava_effectiveness(int(cfg.get("primary_house", 10)), str(lord_planet), computed)
    domain_modifier = 0.60 * planet_eff + 0.40 * bhava_eff
    return max(0.10, min(domain_modifier, 2.0))


def get_convergence_confidence(ratio: float) -> float:
    ratio = float(max(0.0, min(ratio, 1.0)))
    if ratio <= 0.0:
        return 0.05
    if ratio >= 1.0:
        return 0.999
    keys = sorted(CONVERGENCE_TABLE.keys())
    for i in range(len(keys) - 1):
        low_k, high_k = keys[i], keys[i + 1]
        if low_k <= ratio <= high_k:
            low_v, high_v = CONVERGENCE_TABLE[low_k], CONVERGENCE_TABLE[high_k]
            t = (ratio - low_k) / (high_k - low_k)
            return low_v + t * (high_v - low_v)
    return 0.50


def system_supports_domain(system: str, support_map: Dict[str, bool]) -> bool:
    return bool((support_map or {}).get(system, False))


def compute_yoga_domain_boost(computed: Dict[str, Any], domain: str) -> float:
    cfg = DOMAIN_CONFIG.get(str(domain or "").lower(), {})
    yoga_boosts = cfg.get("yoga_boosts", {})
    yogas = computed.get("yogas", []) if isinstance(computed, dict) else []
    active_dasha_lord = str((computed.get("active_dasha", {}) or {}).get("lord", "")).upper()

    activated_boosts = []
    if isinstance(yogas, list):
        for yoga in yogas:
            if not isinstance(yoga, dict):
                continue
            name = str(yoga.get("name", "")).lower().replace(" ", "_")
            planets = [str(p).upper() for p in yoga.get("planets", [])]
            for boost_key, boost_val in yoga_boosts.items():
                if boost_key in name:
                    if active_dasha_lord and active_dasha_lord in planets:
                        activated_boosts.append(float(boost_val))
                    else:
                        activated_boosts.append(float(boost_val) * 0.30)

    if not activated_boosts:
        return 0.0

    activated_boosts.sort(reverse=True)
    total_boost = 0.0
    for idx, boost in enumerate(activated_boosts):
        total_boost += boost / (1.0 + idx * 0.5)
    return min(total_boost, 0.50)


def confidence_label(score: float) -> str:
    val = max(0.0, min(float(score), 0.999))
    for (lo, hi), label in CONFIDENCE_LABELS.items():
        if lo <= val < hi:
            return label
    return "Will Definitely Happen"
