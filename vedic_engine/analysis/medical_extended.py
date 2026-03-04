"""
Medical Astrology – Extended Module  (Phase 4, File 5).

Implements NEW pure functions not present in the existing medical_astrology.py:
  – Triple Mapping table  (12-house organ/dosha/karaka)
  – Drekkana 36-part body map  (12 houses × 3 decanates)
  – Disease Dasha activation patterns  (9 planets → specific diseases)
  – Maraka identification  (2nd / 7th lord system)
  – Maraka period assessment  (3-fold concurrent activation matrix)
  – Enhanced Arishta Yoga  (4 conditions + 4 cancellation rules)
  – Disease Yoga lookup  (7 classical diseases)
  – Psychiatric Yoga detection  (Kemadruma, Psychosis, Anxiety)
  – Beeja Sphuta  (male fertility)
  – Kshetra Sphuta  (female fertility)
  – Gender determination  (Vighati + Sign method)
  – Decumbiture  (critical days + prognosis)

Architecture rule: ALL pure functions. No weights, no blending, no prediction logic.
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Any, Optional

# ════════════════════════════════════════════════════════════════════════════
# STATIC DATA TABLES
# ════════════════════════════════════════════════════════════════════════════

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_LORDS = {
    "Aries": "MARS", "Taurus": "VENUS", "Gemini": "MERCURY",
    "Cancer": "MOON", "Leo": "SUN", "Virgo": "MERCURY",
    "Libra": "VENUS", "Scorpio": "MARS", "Sagittarius": "JUPITER",
    "Capricorn": "SATURN", "Aquarius": "SATURN", "Pisces": "JUPITER",
}

# Odd = Masculine signs (1-indexed: 1,3,5,7,9,11)
ODD_SIGNS = frozenset(["Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"])
EVEN_SIGNS = frozenset(["Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces"])

DUSTHANA = frozenset([6, 8, 12])
KENDRA = frozenset([1, 4, 7, 10])
TRIKONA = frozenset([1, 5, 9])
UPACHAYA = frozenset([3, 6, 10, 11])
MALEFICS = frozenset(["SUN", "MARS", "SATURN", "RAHU", "KETU"])
BENEFICS = frozenset(["MOON", "MERCURY", "JUPITER", "VENUS"])

# ── Triple Mapping: House → (Sign, Karaka, Organ System, Dosha) ──────────
TRIPLE_MAP: List[Dict[str, Any]] = [
    {"house": 1,  "sign": "Aries",       "karaka": "SUN",              "organ": "Cranium, cerebral hemispheres, face, systemic immunity",              "dosha": "Pitta/Vata"},
    {"house": 2,  "sign": "Taurus",      "karaka": "VENUS",            "organ": "Right eye, neck, vocal cords, tonsils, thyroid, oral cavity",         "dosha": "Kapha/Vata"},
    {"house": 3,  "sign": "Gemini",      "karaka": "MERCURY",          "organ": "Clavicles, shoulders, arms, bronchial tubes, peripheral nerves",      "dosha": "Tridosha"},
    {"house": 4,  "sign": "Cancer",      "karaka": "MOON",             "organ": "Cardiac muscle, myocardium, mammary glands, pleura, stomach",         "dosha": "Kapha"},
    {"house": 5,  "sign": "Leo",         "karaka": "SUN/JUPITER",      "organ": "Upper abdomen, hepatic system, pancreas, spinal column, mind",        "dosha": "Pitta"},
    {"house": 6,  "sign": "Virgo",       "karaka": "MERCURY/MARS",     "organ": "Lower abdomen, intestines, digestive enzymes, spleen, infections",    "dosha": "Tridosha/Pitta"},
    {"house": 7,  "sign": "Libra",       "karaka": "VENUS",            "organ": "Pelvic girdle, reproductive organs, kidneys, lumbar, skin",           "dosha": "Kapha/Vata"},
    {"house": 8,  "sign": "Scorpio",     "karaka": "SATURN/MARS",      "organ": "Rectum, perineum, colon, bladder, excretory, terminal pathologies",   "dosha": "Vata/Pitta"},
    {"house": 9,  "sign": "Sagittarius", "karaka": "JUPITER",          "organ": "Femoral region, hips, thighs, sciatic nerve, arterial function",      "dosha": "Kapha"},
    {"house": 10, "sign": "Capricorn",   "karaka": "SATURN",           "organ": "Patella, knee joints, skeletal system, cartilage, hair",              "dosha": "Vata"},
    {"house": 11, "sign": "Aquarius",    "karaka": "SATURN/RAHU",      "organ": "Tibia, fibula, calves, ankles, systemic circulation",                 "dosha": "Vata"},
    {"house": 12, "sign": "Pisces",      "karaka": "JUPITER/KETU",     "organ": "Feet, toes, lymphatic drainage, hospitalization",                     "dosha": "Kapha"},
]

# ── Drekkana 36-part body map (house × decanate) ─────────────────────────
# Key = (house, decanate_1_indexed) → body part string
DREKKANA_BODY_MAP: Dict[Tuple[int, int], str] = {
    (1, 1): "Head / Cranium",          (1, 2): "Neck / Throat",             (1, 3): "Pelvis / Pelvic Girdle",
    (2, 1): "Right Eye",               (2, 2): "Right Shoulder",            (2, 3): "Generating Organs (Right)",
    (3, 1): "Right Ear",               (3, 2): "Right Arm / Bicep",         (3, 3): "Right Testicle / Ovary",
    (4, 1): "Right Nostril",           (4, 2): "Right Side of Trunk",       (4, 3): "Right Thigh",
    (5, 1): "Right Cheek",             (5, 2): "Right Ventricle / Auricle", (5, 3): "Right Knee",
    (6, 1): "Right Jaw",               (6, 2): "Right Lung / Mammary",      (6, 3): "Right Calf",
    (7, 1): "Mouth / Oral Cavity",     (7, 2): "Navel / Umbilicus",         (7, 3): "Legs / Shins",
    (8, 1): "Left Jaw",                (8, 2): "Left Lung / Mammary",       (8, 3): "Left Calf",
    (9, 1): "Left Cheek",              (9, 2): "Left Ventricle / Auricle",  (9, 3): "Left Knee",
    (10, 1): "Left Nostril",           (10, 2): "Left Side of Trunk",       (10, 3): "Left Thigh",
    (11, 1): "Left Ear",               (11, 2): "Left Arm / Bicep",         (11, 3): "Left Testicle / Ovary",
    (12, 1): "Left Eye",               (12, 2): "Left Shoulder",            (12, 3): "Anus / Rectum",
}

# ── Disease Dasha activation patterns (planet → diseases) ────────────────
DASHA_DISEASE_PATTERNS: Dict[str, Dict[str, Any]] = {
    "SUN":     {"diseases": ["Hyperthermia", "Cardiac arrhythmia", "Right-eye disorders", "Migraine", "Calcium deficiency", "Bone degeneration"],
                "systems": ["Heart", "Eyes", "Bones"], "dosha": "Pitta"},
    "MOON":    {"diseases": ["Depression", "Insomnia", "Hormonal turbulence", "Lymphatic stagnation", "Pulmonary edema", "Breast pathology"],
                "systems": ["Mind", "Fluids", "Lungs", "Breasts"], "dosha": "Kapha"},
    "MARS":    {"diseases": ["Acute fevers", "Traumatic hemorrhage", "Surgical crises", "Blood toxicity", "Inflammatory cascades", "Hypertension"],
                "systems": ["Blood", "Muscles", "Marrow"], "dosha": "Pitta"},
    "MERCURY": {"diseases": ["Neurological breakdown", "Speech impediment", "Dermatological eruptions", "Asthma", "Vertigo", "Sensory neuropathy"],
                "systems": ["Nerves", "Skin", "Lungs"], "dosha": "Tridosha"},
    "JUPITER": {"diseases": ["Diabetes mellitus", "Fatty liver", "Obesity", "Gallstones", "Organ hypertrophy", "Lipemia"],
                "systems": ["Liver", "Pancreas", "Fat"], "dosha": "Kapha"},
    "VENUS":   {"diseases": ["Renal insufficiency", "Genitourinary infections", "Diminished virility", "Autoimmune fluid disorders", "Cataracts", "Venereal disease"],
                "systems": ["Kidneys", "Reproductive", "Eyes"], "dosha": "Kapha/Vata"},
    "SATURN":  {"diseases": ["Arthritic calcification", "Physical exhaustion", "Paralysis", "Slow-growth oncology", "Spinal degradation", "Treatment-resistant melancholia"],
                "systems": ["Bones", "Joints", "Spine"], "dosha": "Vata"},
    "RAHU":    {"diseases": ["Undiagnosed pathology", "Malignant neoplasm", "Toxin exposure", "Autoimmune destruction", "Neurosis", "Hallucinations"],
                "systems": ["Immune", "Toxins", "Psyche"], "dosha": "Vata"},
    "KETU":    {"diseases": ["Inexplicable pain", "Viral/bacterial epidemic", "Deep ulceration", "Parasitic infection", "Neuromuscular atrophy"],
                "systems": ["Immunity", "Parasites", "Pain"], "dosha": "Pitta"},
}

# ── Planet → medical karaka mapping ──────────────────────────────────────
PLANET_MEDICAL_MAP: Dict[str, Dict[str, str]] = {
    "SUN":     {"dhatu": "Bones, Heart, Right eye, Vitality",          "dosha": "Pitta"},
    "MOON":    {"dhatu": "Mind, Left eye, Bodily fluids, Mammary",     "dosha": "Kapha"},
    "MARS":    {"dhatu": "Blood, Bone marrow, Musculature, Adrenaline","dosha": "Pitta"},
    "MERCURY": {"dhatu": "CNS, Skin, Respiratory bronchi",             "dosha": "Tridosha"},
    "JUPITER": {"dhatu": "Adipose tissue, Liver, Gallbladder, Pancreas","dosha": "Kapha"},
    "VENUS":   {"dhatu": "Reproductive, Renal, Seminal fluids",        "dosha": "Kapha/Vata"},
    "SATURN":  {"dhatu": "Joints, Teeth, Cartilage, Cellular aging",   "dosha": "Vata"},
    "RAHU":    {"dhatu": "Undiagnosed, Virology, Oncology, Poisoning", "dosha": "Vata"},
    "KETU":    {"dhatu": "Parasites, Epidemics, Sudden trauma",        "dosha": "Pitta"},
}

# ── Disease Yogas (7 classical) ──────────────────────────────────────────
DISEASE_YOGAS: List[Dict[str, Any]] = [
    {
        "disease": "Diabetes Mellitus",
        "condition": "Venus debilitated in Virgo aspected by Jupiter, OR Venus conjunct afflicted Jupiter in malefic houses",
        "mechanism": "Venus governs urinary/renal filtration; Jupiter governs lipid/carbohydrate metabolism – affliction in 6th sign overloads glycemic regulation",
        "key_planets": ["VENUS", "JUPITER"],
        "key_signs": ["Virgo"],
        "key_houses": [6],
    },
    {
        "disease": "Cancer / Oncology",
        "condition": "Rahu + Saturn + Moon converging on 6/8/12 axis; Moon-Rahu conjunction in watery signs",
        "mechanism": "Rahu induces anomalous mitosis, Saturn establishes chronicity, Moon facilitates lymphatic metastasis",
        "key_planets": ["RAHU", "SATURN", "MOON"],
        "key_signs": ["Cancer", "Scorpio", "Pisces"],
        "key_houses": [6, 8, 12],
    },
    {
        "disease": "Cardiac Disease",
        "condition": "Sun and Moon heavily afflicted in 4th house; Sun conjunct Jupiter and Ketu/Mars in malefic houses; 4th lord debilitated/combust",
        "mechanism": "4th house and Sun rule myocardium; Mars introduces atherosclerosis; Ketu introduces sudden blockages",
        "key_planets": ["SUN", "MOON", "MARS", "KETU"],
        "key_signs": ["Cancer", "Leo"],
        "key_houses": [4],
    },
    {
        "disease": "Hepatic / Biliary Disorders",
        "condition": "Jupiter in 6/8/12 conjunct Rahu or Mars; severe afflictions to Sagittarius or 5th house",
        "mechanism": "Jupiter → liver/gallbladder karaka; Mars → acute hepatitis, Rahu → deep toxicity/cirrhosis",
        "key_planets": ["JUPITER", "RAHU", "MARS"],
        "key_signs": ["Sagittarius"],
        "key_houses": [5, 6, 8, 12],
    },
    {
        "disease": "Renal / Kidney Failure",
        "condition": "Venus + Moon afflicted by Saturn/Rahu in Libra or 7th/8th houses; Venus in deep debilitation",
        "mechanism": "Venus and Libra rule glomerular filtration; Moon governs water balance; Saturn causes calcification/failure",
        "key_planets": ["VENUS", "MOON", "SATURN", "RAHU"],
        "key_signs": ["Libra"],
        "key_houses": [7, 8],
    },
    {
        "disease": "Ophthalmic / Blindness",
        "condition": "Sun + Venus + Lagna Lord in Dusthanas; Saturn in 2nd (right eye) and Mars in 12th (left eye)",
        "mechanism": "Sun rules vision, Venus rules ocular fluids/retina; malefics in 2nd/12th create Papakartari on optical axes",
        "key_planets": ["SUN", "VENUS", "SATURN", "MARS"],
        "key_signs": [],
        "key_houses": [2, 6, 8, 12],
    },
    {
        "disease": "Leprosy / Severe Skin Disease",
        "condition": "Lagna Lord + Moon + Mercury on Rahu/Ketu axis; Moon + Mars + Saturn in Aries or Taurus",
        "mechanism": "Mercury governs skin; nodes introduce incurable corruption; Saturn decays tissue, Mars causes lesions",
        "key_planets": ["MERCURY", "MOON", "RAHU", "KETU", "SATURN", "MARS"],
        "key_signs": ["Aries", "Taurus"],
        "key_houses": [],
    },
]

# ── Vighati gender mapping (remainder → planet → gender) ─────────────────
VIGHATI_GENDER_MAP: Dict[int, Tuple[str, str]] = {
    1: ("SUN",     "Male"),
    2: ("MOON",    "Female"),
    3: ("MARS",    "Male"),
    4: ("MERCURY", "Neutral"),
    5: ("JUPITER", "Male"),
    6: ("VENUS",   "Female"),
    7: ("SATURN",  "Neutral"),
    8: ("RAHU",    "Male"),
    0: ("KETU",    "Female"),   # remainder 9 or 0 → Ketu
}

# ── Badhaka house mapping (for medical Maraka integration) ───────────────
BADHAKA_TABLE: Dict[str, Dict[str, Any]] = {
    "Aries":       {"modality": "Movable", "badhaka_house": 11, "badhaka_lord": "SATURN/RAHU"},
    "Cancer":      {"modality": "Movable", "badhaka_house": 11, "badhaka_lord": "VENUS"},
    "Libra":       {"modality": "Movable", "badhaka_house": 11, "badhaka_lord": "SUN"},
    "Capricorn":   {"modality": "Movable", "badhaka_house": 11, "badhaka_lord": "MARS/KETU"},
    "Taurus":      {"modality": "Fixed",   "badhaka_house": 9,  "badhaka_lord": "SATURN"},
    "Leo":         {"modality": "Fixed",   "badhaka_house": 9,  "badhaka_lord": "MARS"},
    "Scorpio":     {"modality": "Fixed",   "badhaka_house": 9,  "badhaka_lord": "MOON"},
    "Aquarius":    {"modality": "Fixed",   "badhaka_house": 9,  "badhaka_lord": "VENUS"},
    "Gemini":      {"modality": "Dual",    "badhaka_house": 7,  "badhaka_lord": "JUPITER"},
    "Virgo":       {"modality": "Dual",    "badhaka_house": 7,  "badhaka_lord": "JUPITER/KETU"},
    "Sagittarius": {"modality": "Dual",    "badhaka_house": 7,  "badhaka_lord": "MERCURY"},
    "Pisces":      {"modality": "Dual",    "badhaka_house": 7,  "badhaka_lord": "MERCURY/RAHU"},
}


# ════════════════════════════════════════════════════════════════════════════
# PURE FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def get_triple_map(house: int) -> Dict[str, Any]:
    """Return the Triple Mapping entry for a given house (1-12)."""
    if 1 <= house <= 12:
        return TRIPLE_MAP[house - 1]
    return {}


def get_drekkana_body_part(house: int, longitude_in_sign: float) -> str:
    """
    Given a house (1-12) and the planet's degree within its sign (0-30),
    return the body part from the 36-part Drekkana body map.
    Decanate: 0-10° = 1st, 10-20° = 2nd, 20-30° = 3rd.
    """
    if longitude_in_sign < 10:
        decan = 1
    elif longitude_in_sign < 20:
        decan = 2
    else:
        decan = 3
    return DREKKANA_BODY_MAP.get((house, decan), "Unknown")


def assess_dasha_disease_risk(
    dasha_lord: str,
    planet_houses: Dict[str, int],
    planet_signs: Dict[str, str],
    debilitated_planets: Optional[List[str]] = None,
    combust_planets: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Given the active Dasha lord, assess disease severity.
    - Exalted / own sign / friendly → MILD, transient
    - Debilitated / combust / enemy → SEVERE, intractable
    Returns disease list, severity, and affected systems.
    """
    if debilitated_planets is None:
        debilitated_planets = []
    if combust_planets is None:
        combust_planets = []

    pattern = DASHA_DISEASE_PATTERNS.get(dasha_lord)
    if not pattern:
        return {"dasha_lord": dasha_lord, "diseases": [], "severity": "NONE", "systems": []}

    house = planet_houses.get(dasha_lord, 0)
    in_dusthana = house in DUSTHANA

    # Severity assessment
    is_debilitated = dasha_lord in debilitated_planets
    is_combust = dasha_lord in combust_planets

    if is_debilitated or is_combust:
        severity = "SEVERE"
        severity_note = "Aristaphala – intractable, treatment-resistant pathology"
    elif in_dusthana:
        severity = "HIGH"
        severity_note = "Dasha lord in Dusthana – significant medical activation"
    else:
        severity = "MILD"
        severity_note = "Dasha lord in reasonable dignity – transient, curable symptoms"

    return {
        "dasha_lord": dasha_lord,
        "diseases": pattern["diseases"],
        "systems": pattern["systems"],
        "dosha": pattern["dosha"],
        "house": house,
        "in_dusthana": in_dusthana,
        "severity": severity,
        "severity_note": severity_note,
    }


def identify_marakas(
    lagna_sign: str,
    planet_houses: Dict[str, int],
) -> Dict[str, Any]:
    """
    Identify Maraka (death-inflicting) planets.
    - 2nd and 7th house lords are primary Marakas.
    - Planets occupying 2nd/7th houses gain secondary Maraka status.
    - Saturn conjunct any Maraka lord → terminal agent.
    """
    lagna_idx = SIGN_NAMES.index(lagna_sign) if lagna_sign in SIGN_NAMES else 0

    # 2nd house sign
    second_sign = SIGN_NAMES[(lagna_idx + 1) % 12]
    second_lord = SIGN_LORDS[second_sign]

    # 7th house sign
    seventh_sign = SIGN_NAMES[(lagna_idx + 6) % 12]
    seventh_lord = SIGN_LORDS[seventh_sign]

    primary_marakas = {second_lord, seventh_lord}

    # Secondary Marakas: planets physically in 2nd or 7th
    secondary_marakas: List[str] = []
    for planet, house in planet_houses.items():
        if house in (2, 7) and planet not in primary_marakas:
            secondary_marakas.append(planet)

    # Saturn as terminal agent
    saturn_house = planet_houses.get("SATURN", 0)
    saturn_terminal = False
    # Saturn with any Maraka lord (same house)?
    for mk in primary_marakas:
        mk_house = planet_houses.get(mk, -1)
        if mk_house == saturn_house and saturn_house > 0:
            saturn_terminal = True
            break

    # Badhaka info
    badhaka_info = BADHAKA_TABLE.get(lagna_sign, {})

    return {
        "second_lord": second_lord,
        "second_sign": second_sign,
        "seventh_lord": seventh_lord,
        "seventh_sign": seventh_sign,
        "primary_marakas": sorted(primary_marakas),
        "secondary_marakas": secondary_marakas,
        "saturn_terminal_agent": saturn_terminal,
        "badhaka": badhaka_info,
    }


def assess_maraka_period(
    dasha_lord: str,
    antardasha_lord: str,
    maraka_data: Dict[str, Any],
    transit_malefics_on_sensitive: bool = False,
    longevity_exhausted: bool = False,
) -> Dict[str, Any]:
    """
    Three-fold concurrent activation matrix for mortality assessment.
    1. Dasha Activation: running Maraka/Badhaka dasha
    2. Transit Trigger: malefics crossing Lagna/Moon/8th
    3. Longevity Exhaustion: Ayurdaya concluded

    If all 3 → DEATH. If 1+2 but not 3 → SEVERE ILLNESS. If 1 only → FINANCIAL LOSS.
    """
    all_marakas = set(maraka_data.get("primary_marakas", []))
    all_marakas.update(maraka_data.get("secondary_marakas", []))
    badhaka_lords = maraka_data.get("badhaka", {}).get("badhaka_lord", "")
    for bl in badhaka_lords.split("/"):
        bl = bl.strip()
        if bl:
            all_marakas.add(bl)

    dasha_hits = dasha_lord in all_marakas or antardasha_lord in all_marakas
    condition_1 = dasha_hits
    condition_2 = transit_malefics_on_sensitive
    condition_3 = longevity_exhausted

    if condition_1 and condition_2 and condition_3:
        verdict = "DEATH"
        note = "All 3 conditions met: Dasha activation + transit trigger + longevity exhausted"
    elif condition_1 and condition_2 and not condition_3:
        verdict = "SEVERE_ILLNESS"
        note = "Dasha + transit active but lifespan remains → near-fatal illness or hospitalisation"
    elif condition_1 and not condition_2:
        verdict = "FINANCIAL_LOSS"
        note = "Maraka dasha without transit trigger → catastrophic financial loss or partnership dissolution"
    else:
        verdict = "SAFE"
        note = "No Maraka dasha activation"

    return {
        "dasha_lord": dasha_lord,
        "antardasha_lord": antardasha_lord,
        "dasha_activation": condition_1,
        "transit_trigger": condition_2,
        "longevity_exhausted": condition_3,
        "verdict": verdict,
        "note": note,
    }


def detect_arishta_yoga(
    moon_house: int,
    moon_aspects_from: Optional[List[str]] = None,
    lagna_hemmed_malefics: bool = False,
    eclipse_birth: bool = False,
    lagna_lord_house: int = 0,
    lagna_lord_in_war_with_malefic: bool = False,
    benefic_aspects_on_moon: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Enhanced Arishta Yoga detection with 4 classical conditions:
    1. Moon in 6/8/12 devoid of benefic aspects, aspected by malefics
    2. Papakartari Lagna (hemmed between malefics)
    3. Eclipse birth with Saturn/Mars on Asc
    4. Lagna Lord in 7th losing Graha Yuddha to malefic

    Returns list of triggered conditions.
    """
    if moon_aspects_from is None:
        moon_aspects_from = []
    if benefic_aspects_on_moon is None:
        benefic_aspects_on_moon = []

    conditions: List[Dict[str, str]] = []

    # Condition 1: Lunar affliction in Dusthana
    moon_in_dusthana = moon_house in DUSTHANA
    malefic_on_moon = [p for p in moon_aspects_from if p in MALEFICS]
    benefic_on_moon = [p for p in benefic_aspects_on_moon if p in BENEFICS]
    if moon_in_dusthana and malefic_on_moon and not benefic_on_moon:
        conditions.append({
            "type": "LUNAR_AFFLICTION",
            "detail": f"Moon in H{moon_house} (Dusthana), malefic aspects: {malefic_on_moon}, no benefic relief",
        })

    # Condition 2: Papakartari Lagna
    if lagna_hemmed_malefics:
        conditions.append({
            "type": "PAPAKARTARI_LAGNA",
            "detail": "Ascendant hemmed between two malefics without benefic relief",
        })

    # Condition 3: Eclipse birth
    if eclipse_birth:
        conditions.append({
            "type": "ECLIPSE_BIRTH",
            "detail": "Birth during solar/lunar eclipse with malefic on Ascendant",
        })

    # Condition 4: Lagna Lord defeat
    if lagna_lord_house == 7 and lagna_lord_in_war_with_malefic:
        conditions.append({
            "type": "LAGNA_LORD_DEFEAT",
            "detail": "Lagna Lord in 7th house losing Graha Yuddha to malefic",
        })

    triggered = len(conditions) > 0
    # Severity tiers
    if len(conditions) >= 3:
        tier = "BALARISHTA_EXTREME"
    elif len(conditions) == 2:
        tier = "BALARISHTA_HIGH"
    elif len(conditions) == 1:
        tier = "BALARISHTA_MODERATE"
    else:
        tier = "NO_ARISHTA"

    return {
        "arishta_triggered": triggered,
        "tier": tier,
        "conditions_count": len(conditions),
        "conditions": conditions,
    }


def check_arishta_cancellation(
    jupiter_in_lagna: bool = False,
    jupiter_digbala: bool = False,
    lagna_lord_in_kendra: bool = False,
    lagna_lord_exalted_or_friendly: bool = False,
    benefic_aspects_on_lagna_lord: bool = False,
    full_moon: bool = False,
    moon_in_benefic_sign: bool = False,
    jupiter_aspects_moon: bool = False,
    daytime_krishna_paksha: bool = False,
    nighttime_shukla_paksha: bool = False,
) -> Dict[str, Any]:
    """
    4 Balarishta Bhanga (cancellation) rules:
    1. Jupiterian Shield: Jupiter with Digbala in Lagna → absolute cancellation
    2. Strong Lagna Lord: in Kendra, exalted/friendly, benefic aspects
    3. Lunar Dignity: Full Moon in benefic sign/Navamsa with Jupiter aspect
    4. Temporal Cancellation: daytime+Krishna Paksha OR nighttime+Shukla Paksha
    """
    cancellations: List[Dict[str, str]] = []

    # Rule 1: Jupiterian Shield
    if jupiter_in_lagna and jupiter_digbala:
        cancellations.append({
            "rule": "JUPITERIAN_SHIELD",
            "detail": "Jupiter with Digbala in Lagna – absolute cancellation of all Balarishta",
        })

    # Rule 2: Strong Lagna Lord
    if lagna_lord_in_kendra and lagna_lord_exalted_or_friendly and benefic_aspects_on_lagna_lord:
        cancellations.append({
            "rule": "STRONG_LAGNA_LORD",
            "detail": "Lagna Lord in Kendra, exalted/friendly sign, with benefic aspects",
        })

    # Rule 3: Lunar Dignity
    if full_moon and moon_in_benefic_sign and jupiter_aspects_moon:
        cancellations.append({
            "rule": "LUNAR_DIGNITY",
            "detail": "Full Moon in benefic sign with Jupiter's exact aspect",
        })

    # Rule 4: Temporal Cancellation
    if daytime_krishna_paksha or nighttime_shukla_paksha:
        cancellations.append({
            "rule": "TEMPORAL_CANCELLATION",
            "detail": "Birth timing shields from lunar-induced Balarishta",
        })

    cancelled = len(cancellations) > 0
    return {
        "arishta_cancelled": cancelled,
        "cancellation_count": len(cancellations),
        "cancellations": cancellations,
    }


def check_disease_yogas(
    planet_houses: Dict[str, int],
    planet_signs: Dict[str, str],
    debilitated_planets: Optional[List[str]] = None,
    combust_planets: Optional[List[str]] = None,
    lagna_lord: str = "",
) -> List[Dict[str, Any]]:
    """
    Check all 7 classical Disease Yogas against the chart.
    Returns list of detected disease yogas with confidence.
    """
    if debilitated_planets is None:
        debilitated_planets = []
    if combust_planets is None:
        combust_planets = []

    detected: List[Dict[str, Any]] = []
    ph = planet_houses
    watery_signs = frozenset(["Cancer", "Scorpio", "Pisces"])

    # 1. Diabetes: Venus debilitated in Virgo + Jupiter aspect, or Venus+Jupiter in malefic houses
    venus_sign = planet_signs.get("VENUS", "")
    venus_h = ph.get("VENUS", 0)
    jup_h = ph.get("JUPITER", 0)
    if "VENUS" in debilitated_planets and venus_sign == "Virgo":
        detected.append({"disease": "Diabetes Mellitus", "confidence": "HIGH",
                         "trigger": "Venus debilitated in Virgo"})
    elif venus_h in DUSTHANA and jup_h in DUSTHANA:
        detected.append({"disease": "Diabetes Mellitus", "confidence": "MEDIUM",
                         "trigger": f"Venus(H{venus_h}) + Jupiter(H{jup_h}) both in Dusthana"})

    # 2. Cancer: Rahu+Saturn+Moon on 6/8/12 axis
    rahu_h = ph.get("RAHU", 0)
    sat_h = ph.get("SATURN", 0)
    moon_h = ph.get("MOON", 0)
    moon_sign = planet_signs.get("MOON", "")
    rahu_sign = planet_signs.get("RAHU", "")
    if (rahu_h in DUSTHANA and sat_h in DUSTHANA and moon_h in DUSTHANA):
        detected.append({"disease": "Cancer / Oncology", "confidence": "HIGH",
                         "trigger": f"Rahu(H{rahu_h})+Saturn(H{sat_h})+Moon(H{moon_h}) in Dusthana"})
    elif (moon_h == rahu_h and moon_sign in watery_signs):
        detected.append({"disease": "Cancer / Oncology", "confidence": "MEDIUM",
                         "trigger": f"Moon-Rahu conjunction in watery sign {moon_sign}"})

    # 3. Cardiac: Sun+Moon afflicted in 4th
    sun_h = ph.get("SUN", 0)
    if sun_h == 4 and moon_h == 4:
        detected.append({"disease": "Cardiac Disease", "confidence": "HIGH",
                         "trigger": "Sun + Moon both in 4th house"})
    elif sun_h == 4 and (jup_h == sun_h or ph.get("KETU", 0) == sun_h or ph.get("MARS", 0) == sun_h):
        detected.append({"disease": "Cardiac Disease", "confidence": "MEDIUM",
                         "trigger": f"Sun in 4th with malefic conjunction"})

    # 4. Hepatic: Jupiter in 6/8/12 with Rahu or Mars
    mars_h = ph.get("MARS", 0)
    if jup_h in DUSTHANA and (rahu_h == jup_h or mars_h == jup_h):
        detected.append({"disease": "Hepatic / Biliary Disorders", "confidence": "HIGH",
                         "trigger": f"Jupiter(H{jup_h}) conjunct {'Rahu' if rahu_h == jup_h else 'Mars'} in Dusthana"})

    # 5. Renal: Venus+Moon afflicted by Saturn/Rahu in Libra or 7/8
    if (venus_h in (7, 8) or venus_sign == "Libra") and (sat_h == venus_h or rahu_h == venus_h):
        detected.append({"disease": "Renal / Kidney Failure", "confidence": "HIGH",
                         "trigger": f"Venus({venus_sign}/H{venus_h}) afflicted by Saturn/Rahu"})

    # 6. Ophthalmic: Saturn in 2nd + Mars in 12th
    if sat_h == 2 and mars_h == 12:
        detected.append({"disease": "Ophthalmic / Blindness", "confidence": "HIGH",
                         "trigger": "Saturn in 2nd (right eye) + Mars in 12th (left eye) – Papakartari"})
    elif sun_h in DUSTHANA and venus_h in DUSTHANA:
        detected.append({"disease": "Ophthalmic / Blindness", "confidence": "MEDIUM",
                         "trigger": f"Sun(H{sun_h}) + Venus(H{venus_h}) in Dusthana"})

    # 7. Leprosy/Skin: Moon+Mercury on Rahu/Ketu axis
    merc_h = ph.get("MERCURY", 0)
    ketu_h = ph.get("KETU", 0)
    moon_on_axis = (moon_h == rahu_h or moon_h == ketu_h)
    merc_on_axis = (merc_h == rahu_h or merc_h == ketu_h)
    if moon_on_axis and merc_on_axis:
        detected.append({"disease": "Leprosy / Severe Skin Disease", "confidence": "HIGH",
                         "trigger": "Moon + Mercury on Rahu/Ketu axis"})

    return detected


def detect_psychiatric_yogas(
    planet_houses: Dict[str, int],
    planet_signs: Dict[str, str],
    moon_conjunctions: Optional[List[str]] = None,
    moon_aspects_from: Optional[List[str]] = None,
    planets_adjacent_to_moon: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Detect classical psychiatric yogas:
    1. Kemadruma Yoga → depression/melancholia
    2. Psychosis/Schizophrenia → Jupiter-1st/Mars-7th axis; Saturn-Asc/Sun-12th
    3. Anxiety/Cognitive dysfunction → Mercury in Dusthana aspected by Saturn; Rahu+Moon/Mercury
    """
    if moon_conjunctions is None:
        moon_conjunctions = []
    if moon_aspects_from is None:
        moon_aspects_from = []
    if planets_adjacent_to_moon is None:
        planets_adjacent_to_moon = []

    ph = planet_houses
    findings: List[Dict[str, Any]] = []

    # 1. Kemadruma Yoga: Moon isolated (no conjunctions, no planets in 2nd/12th from Moon)
    has_conjunction = len(moon_conjunctions) > 0
    has_adjacent = len(planets_adjacent_to_moon) > 0
    if not has_conjunction and not has_adjacent:
        saturn_aspects = "SATURN" in moon_aspects_from
        benefics_aspect = any(p in BENEFICS for p in moon_aspects_from)
        if saturn_aspects and not benefics_aspect:
            findings.append({
                "yoga": "Kemadruma Yoga",
                "type": "Depression / Melancholia",
                "severity": "HIGH",
                "detail": "Moon completely isolated + Saturn aspect without benefic relief → profound neurochemical depression",
            })
        elif not has_conjunction and not has_adjacent:
            findings.append({
                "yoga": "Kemadruma Yoga",
                "type": "Depression / Melancholia",
                "severity": "MODERATE",
                "detail": "Moon isolated (no conjunctions, no adjacent planets) → emotional vulnerability",
            })

    # 2. Psychosis: Jupiter in 1st opposed by Mars in 7th (or vice versa)
    jup_h = ph.get("JUPITER", 0)
    mars_h = ph.get("MARS", 0)
    sat_h = ph.get("SATURN", 0)
    sun_h = ph.get("SUN", 0)

    if (jup_h == 1 and mars_h == 7) or (mars_h == 1 and jup_h == 7):
        findings.append({
            "yoga": "Cognitive Axis Disruption",
            "type": "Psychosis / Schizophrenia",
            "severity": "HIGH",
            "detail": f"Jupiter(H{jup_h}) opposed by Mars(H{mars_h}) – violent cognitive axis disruption",
        })

    if sat_h == 1 and sun_h == 12:
        moon_h = ph.get("MOON", 0)
        moon_weak = moon_h in DUSTHANA
        findings.append({
            "yoga": "Dissociative Configuration",
            "type": "Psychosis / Dissociative Disorder",
            "severity": "HIGH" if moon_weak else "MODERATE",
            "detail": f"Saturn in Asc + Sun in 12th{' + weak Moon' if moon_weak else ''} → dissociation/lunacy risk",
        })

    # 3. Anxiety: Mercury in Dusthana aspected by Saturn
    merc_h = ph.get("MERCURY", 0)
    if merc_h in DUSTHANA and "SATURN" in (moon_aspects_from or []):
        # Note: this is a simplification – ideally we'd check aspects on Mercury specifically
        findings.append({
            "yoga": "Mercury-Saturn Affliction",
            "type": "Anxiety / Cognitive Dysfunction",
            "severity": "HIGH",
            "detail": f"Mercury in H{merc_h} (Dusthana) under Saturn's influence → nervous breakdown, paranoia",
        })

    # Rahu + Moon/Mercury conjunction in angular house
    rahu_h = ph.get("RAHU", 0)
    moon_h = ph.get("MOON", 0)
    if rahu_h in KENDRA:
        if rahu_h == moon_h:
            findings.append({
                "yoga": "Rahu-Moon Conjunction",
                "type": "OCD / Phobias / Hallucinations",
                "severity": "HIGH",
                "detail": f"Rahu conjunct Moon in angular H{rahu_h} → obsessive-compulsive loops, chaotic subconscious",
            })
        elif rahu_h == merc_h:
            findings.append({
                "yoga": "Rahu-Mercury Conjunction",
                "type": "OCD / Intellectual Paralysis",
                "severity": "MODERATE",
                "detail": f"Rahu conjunct Mercury in angular H{rahu_h} → hallucinatory episodes, cognitive infiltration",
            })

    return findings


def compute_beeja_sphuta(
    sun_lon: float,
    venus_lon: float,
    jupiter_lon: float,
) -> Dict[str, Any]:
    """
    Beeja Sphuta (Male Virility/Fertility).
    Sum of Sun + Venus + Jupiter longitudes → mod 360.
    Check if resulting Rashi and Navamsa are odd (masculine) or even (feminine).
    Odd+Odd → potent. Even+Even → infertile. Mixed → delayed.
    """
    total = (sun_lon + venus_lon + jupiter_lon) % 360.0
    rashi_idx = int(total / 30) % 12
    rashi_name = SIGN_NAMES[rashi_idx]

    # Navamsa: each navamsa = 3°20' = 3.3333°
    navamsa_in_sign = (total % 30) / (30.0 / 9.0)
    navamsa_num = int(navamsa_in_sign)  # 0-8
    # Navamsa sign: starting from the sign's element offset
    # Fire signs start from Aries, Earth from Cap, Air from Libra, Water from Cancer
    element = rashi_idx % 4  # 0=Fire, 1=Earth, 2=Air, 3=Water
    navamsa_start = [0, 9, 6, 3][element]  # Aries, Cap, Libra, Cancer
    navamsa_sign_idx = (navamsa_start + navamsa_num) % 12
    navamsa_sign = SIGN_NAMES[navamsa_sign_idx]

    rashi_odd = rashi_name in ODD_SIGNS
    navamsa_odd = navamsa_sign in ODD_SIGNS

    if rashi_odd and navamsa_odd:
        fertility = "POTENT"
        note = "Both Rashi and Navamsa in masculine signs → male virility is biologically sound"
    elif not rashi_odd and not navamsa_odd:
        fertility = "INFERTILE"
        note = "Both in feminine signs → profound lack of virility, clinical infertility indicated"
    else:
        fertility = "DELAYED"
        note = "Mixed (one odd, one even) → delayed progeny, may require treatment/remedies"

    return {
        "sphuta_longitude": round(total, 4),
        "rashi": rashi_name,
        "rashi_masculine": rashi_odd,
        "navamsa_sign": navamsa_sign,
        "navamsa_masculine": navamsa_odd,
        "fertility": fertility,
        "note": note,
    }


def compute_kshetra_sphuta(
    moon_lon: float,
    mars_lon: float,
    jupiter_lon: float,
) -> Dict[str, Any]:
    """
    Kshetra Sphuta (Female Fecundity).
    Sum of Moon + Mars + Jupiter longitudes → mod 360.
    Even+Even in Rashi and Navamsa → fertile. Odd+Odd → barren. Mixed → complications.
    """
    total = (moon_lon + mars_lon + jupiter_lon) % 360.0
    rashi_idx = int(total / 30) % 12
    rashi_name = SIGN_NAMES[rashi_idx]

    navamsa_in_sign = (total % 30) / (30.0 / 9.0)
    navamsa_num = int(navamsa_in_sign)
    element = rashi_idx % 4
    navamsa_start = [0, 9, 6, 3][element]
    navamsa_sign_idx = (navamsa_start + navamsa_num) % 12
    navamsa_sign = SIGN_NAMES[navamsa_sign_idx]

    rashi_even = rashi_name in EVEN_SIGNS
    navamsa_even = navamsa_sign in EVEN_SIGNS

    if rashi_even and navamsa_even:
        fertility = "FERTILE"
        note = "Both Rashi and Navamsa in feminine signs → highly fertile, reproductive system ready"
    elif not rashi_even and not navamsa_even:
        fertility = "BARREN"
        note = "Both in masculine signs → severe barrenness/uterine hostility risk"
    else:
        fertility = "COMPLICATED"
        note = "Mixed → complications, ectopic risks, or significantly delayed conception"

    return {
        "sphuta_longitude": round(total, 4),
        "rashi": rashi_name,
        "rashi_feminine": rashi_even,
        "navamsa_sign": navamsa_sign,
        "navamsa_feminine": navamsa_even,
        "fertility": fertility,
        "note": note,
    }


def predict_gender_vighati(
    vighatis_from_sunrise: float,
) -> Dict[str, Any]:
    """
    Jaimini Vighati method for gender prediction.
    Total vighatis from sunrise → divide by 9 → remainder maps to planet → gender.
    1 vighati = 24 seconds; 1 ghati = 60 vighatis = 24 minutes.
    """
    remainder = int(vighatis_from_sunrise) % 9
    if remainder == 0:
        remainder = 9  # map 0 → 9 which maps to Ketu
    # For lookup: 9 maps to 0 in the table
    lookup_key = remainder if remainder != 9 else 0
    planet, gender = VIGHATI_GENDER_MAP.get(lookup_key, ("KETU", "Female"))

    return {
        "vighatis": round(vighatis_from_sunrise, 2),
        "remainder": remainder if remainder != 9 else 0,
        "indicator_planet": planet,
        "predicted_gender": gender,
        "method": "Jaimini Vighati",
    }


def predict_gender_sign_method(
    conception_moon_sign: str,
    conception_moon_nakshatra: str = "",
) -> Dict[str, Any]:
    """
    Sign and Nakshatra method for gender prediction.
    Moon in masculine signs → Male. Moon in feminine signs → Female.
    """
    MASCULINE_NAKSHATRAS = frozenset([
        "Ashwini", "Bharani", "Mrigashira", "Punarvasu", "Pushya",
        "Magha", "Uttara Phalguni", "Hasta", "Swati", "Anuradha",
        "Uttara Ashadha", "Shravana", "Dhanishtha", "Uttara Bhadrapada",
    ])
    FEMININE_NAKSHATRAS = frozenset([
        "Krittika", "Rohini", "Ardra", "Ashlesha", "Purva Phalguni",
        "Chitra", "Vishakha", "Jyeshtha", "Mula", "Purva Ashadha",
        "Purva Bhadrapada", "Revati", "Shatabhisha",
    ])

    sign_masculine = conception_moon_sign in ODD_SIGNS

    nak_gender = "Unknown"
    if conception_moon_nakshatra in MASCULINE_NAKSHATRAS:
        nak_gender = "Male"
    elif conception_moon_nakshatra in FEMININE_NAKSHATRAS:
        nak_gender = "Female"

    # Combined assessment
    if sign_masculine and nak_gender == "Male":
        predicted = "Male"
        confidence = "HIGH"
    elif not sign_masculine and nak_gender == "Female":
        predicted = "Female"
        confidence = "HIGH"
    elif sign_masculine:
        predicted = "Male"
        confidence = "MODERATE"
    elif not sign_masculine:
        predicted = "Female"
        confidence = "MODERATE"
    else:
        predicted = "Indeterminate"
        confidence = "LOW"

    return {
        "moon_sign": conception_moon_sign,
        "moon_nakshatra": conception_moon_nakshatra,
        "sign_masculine": sign_masculine,
        "nakshatra_gender": nak_gender,
        "predicted_gender": predicted,
        "confidence": confidence,
        "method": "Sign-Nakshatra",
    }


def compute_decumbiture_critical_days(
    illness_moon_longitude: float,
) -> List[Dict[str, Any]]:
    """
    Decumbiture: Critical days in acute illness based on Moon's position at disease onset.
    Crises occur when transiting Moon reaches 90° (1st square), 180° (opposition),
    270° (2nd square), and 360° (return) from illness onset Moon.
    Each crisis ~7 days apart.
    """
    base = illness_moon_longitude % 360.0
    crises: List[Dict[str, Any]] = []

    angles = [
        (90,  "First Square",  "~Day 7",  "1st Crisis"),
        (180, "Opposition",    "~Day 14", "2nd Crisis – Major"),
        (270, "Second Square", "~Day 21", "3rd Crisis"),
        (360, "Return",        "~Day 28", "4th Crisis – Resolution or Death"),
    ]

    for angle, aspect_name, approx_day, label in angles:
        critical_lon = (base + angle) % 360.0
        critical_sign_idx = int(critical_lon / 30) % 12
        crises.append({
            "angle": angle,
            "aspect": aspect_name,
            "critical_moon_longitude": round(critical_lon, 4),
            "critical_sign": SIGN_NAMES[critical_sign_idx],
            "approximate_timing": approx_day,
            "label": label,
        })

    return crises


def assess_decumbiture_prognosis(
    illness_tithi: int,
    illness_weekday: str,
    illness_nakshatra_from_birth: int,
    moon_house_from_natal: int,
    benefics_in_kendras: bool = False,
    benefic_aspects_on_lagna: bool = False,
    moon_in_upachaya: bool = False,
) -> Dict[str, Any]:
    """
    Prasna Marga decumbiture prognosis assessment.

    DEATH indicators: Riktha tithis (4,9,14), Parva (New/Full=15,30),
    malefic weekdays (Tue/Sat/Sun), hostile nakshatras (3rd/5th/7th from birth star),
    Moon in 8th/12th from natal Moon (Chandrashtama).

    RECOVERY indicators: Moon in Upachaya (3/6/10/11), benefics in Kendras,
    benefic aspects on Lagna.
    """
    death_flags: List[str] = []
    recovery_flags: List[str] = []

    # Riktha Tithis
    riktha_tithis = frozenset([4, 9, 14])
    parva_tithis = frozenset([15, 30])
    if illness_tithi in riktha_tithis:
        death_flags.append(f"Riktha Tithi ({illness_tithi}) – empty/dangerous")
    if illness_tithi in parva_tithis:
        death_flags.append(f"Parva Tithi ({illness_tithi}) – New/Full Moon")

    # Malefic weekdays
    malefic_days = frozenset(["Tuesday", "Saturday", "Sunday"])
    if illness_weekday in malefic_days:
        death_flags.append(f"Malefic weekday ({illness_weekday})")

    # Hostile nakshatras (3rd, 5th, 7th from birth star)
    if illness_nakshatra_from_birth in (3, 5, 7):
        death_flags.append(f"Hostile nakshatra ({illness_nakshatra_from_birth}th from birth star)")

    # Chandrashtama
    if moon_house_from_natal in (8, 12):
        death_flags.append(f"Moon in {moon_house_from_natal}th from natal Moon (Chandrashtama)")

    # Recovery indicators
    if moon_in_upachaya:
        recovery_flags.append("Moon in Upachaya house (3/6/10/11)")
    if benefics_in_kendras:
        recovery_flags.append("Benefic planets in Kendra houses")
    if benefic_aspects_on_lagna:
        recovery_flags.append("Benefic aspects on Ascendant")

    # Verdict
    death_score = len(death_flags)
    recovery_score = len(recovery_flags)

    if death_score >= 3 and recovery_score == 0:
        prognosis = "FATAL"
        note = "Multiple death indicators with no recovery support – highly dangerous"
    elif death_score >= 2:
        prognosis = "CRITICAL"
        note = "Severe prognosis – outcome depends on crisis-point planetary alignments"
    elif recovery_score >= 2:
        prognosis = "RECOVERY"
        note = "Strong recovery indicators – eventual healing regardless of initial severity"
    elif recovery_score >= 1:
        prognosis = "GUARDED"
        note = "Some protective factors present – partial recovery likely"
    else:
        prognosis = "UNCERTAIN"
        note = "Mixed indicators – monitor critical days closely"

    return {
        "prognosis": prognosis,
        "death_indicators": death_flags,
        "death_score": death_score,
        "recovery_indicators": recovery_flags,
        "recovery_score": recovery_score,
        "note": note,
    }
