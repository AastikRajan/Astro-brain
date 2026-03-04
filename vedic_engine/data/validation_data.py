"""
Validation Data — Benchmark Charts, BVB Marriage Parameters, Edge Cases.

Contains:
  1. 10 historically verified benchmark horoscopes with events & dasha triggers
  2. BVB (Bharatiya Vidya Bhavan) Marriage Parameters P1-P8 with 5 validation cases
  3. Career and Health event validation cases
  4. Edge case definitions (Rashi Sandhi, High Latitude, Eclipse, Kala Sarpa, Neechabhanga)

Reference: K.N. Rao marriage studies (218 charts), Prashna Marga, standard textbooks.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional


# ═══════════════════════════════════════════════════════════════
# 1. BENCHMARK HOROSCOPES
# ═══════════════════════════════════════════════════════════════

BENCHMARK_CHARTS: List[Dict[str, Any]] = [
    {
        "id": "INDIRA_GANDHI",
        "name": "Indira Gandhi",
        "birth": {"date": "1917-11-19", "time": "23:11:00", "timezone": "IST",
                  "rectified_time": "23:12:48", "lat": 25.459, "lon": 81.860,
                  "location": "Allahabad, India"},
        "lagna": "CANCER",
        "key_events": [
            {"event": "Prime Minister", "date": "1966-01-24",
             "dasha": "Sudarshana activation + Vimshottari 10th house",
             "validation": "10th house power activation"},
            {"event": "Emergency imposed", "date": "1975-06-25",
             "dasha": "SA-ME", "validation": "Saturn taskmaster, Mercury 12L from Moon"},
            {"event": "Assassination", "date": "1984-10-31",
             "dasha": "SA-RA-MO", "validation": "Saturn=7L Maraka, Rahu=8L in 6H violence, Moon=12L loss"},
        ],
    },
    {
        "id": "AMITABH_BACHCHAN",
        "name": "Amitabh Bachchan",
        "birth": {"date": "1942-10-11", "time": "16:00:00", "timezone": "IST",
                  "rectified_time": "15:59:00", "lat": 25.433, "lon": 81.817,
                  "location": "Allahabad, India"},
        "lagna": "AQUARIUS",
        "ayanamsha_ref": "Chitra Paksha 23°03'19\"",
        "key_events": [
            {"event": "Superstardom", "date": "1971-01-01",
             "dasha": "SA MD onset", "validation": "Saturn = Lagna lord for Aquarius = public fame"},
            {"event": "Near-fatal accident (Coolie)", "date": "1982-07-01",
             "dasha": "SA-SU-KE", "validation": "Sun=7L Maraka, Ketu=sudden impact"},
            {"event": "Recovery", "date": "1982-08-09",
             "dasha": "SA-SU-VE shift", "validation": "Venus = Yoga Karaka for Aquarius"},
            {"event": "Bankruptcy", "date": "1997-01-01",
             "dasha": "ME-KE, ME-VE", "validation": "Financial downfall"},
            {"event": "TV comeback (KBC)", "date": "2000-07-01",
             "dasha": "ME-RA", "validation": "Massive comeback via Rahu media influence"},
        ],
    },
    {
        "id": "SACHIN_TENDULKAR",
        "name": "Sachin Tendulkar",
        "birth": {"date": "1973-04-24", "time": "12:54:00", "timezone": "IST",
                  "lat": 19.050, "lon": 72.850, "location": "Mumbai, India"},
        "lagna": "CANCER",
        "key_events": [
            {"event": "International debut", "date": "1989-11-15",
             "dasha": "MO-KE", "validation": "Transit Saturn in 6H aspecting 3H (sports/courage), Sade-Sati onset"},
            {"event": "World Cup victory", "date": "2011-04-02",
             "dasha": "RA-VE", "validation": "Venus=11L achievements in D1, 10L career in D10"},
            {"event": "Retirement + Bharat Ratna", "date": "2013-11-16",
             "dasha": "RA-VE-KE", "validation": "Ketu in 12H = closure/retirement, Venus = honors"},
            {"event": "Marriage", "date": "1995-05-19",
             "dasha": "MA-SA", "validation": "Mars=5L in 7H, Saturn=7L — P1 marriage parameter"},
        ],
        "special_yogas": ["Neechabhanga Raj Yoga (Jupiter debil + exalted Mars in Capricorn)"],
    },
    {
        "id": "STEVE_JOBS",
        "name": "Steve Jobs",
        "birth": {"date": "1955-02-24", "time": "19:15:00", "timezone": "PST",
                  "lat": 37.767, "lon": -122.417, "location": "San Francisco, USA"},
        "lagna": "VIRGO",
        "key_events": [
            {"event": "Apple founding", "date": "1976-04-01",
             "dasha": "KE→VE transition", "validation": "Uranus-Jupiter in 10H = unconventional tech innovation"},
            {"event": "Liver transplant", "date": "2009-04-01",
             "dasha": "VE-ME", "validation": "Mercury=LL+Rogesha(6L), severe medical intervention"},
            {"event": "Death (pancreatic cancer)", "date": "2011-10-05",
             "dasha": "MO-JU", "validation": "Moon in 8H(Pisces), ruled by Jupiter = fatal link"},
        ],
    },
    {
        "id": "NARENDRA_MODI",
        "name": "Narendra Modi",
        "birth": {"date": "1950-09-17", "time": "11:00:00", "timezone": "IST",
                  "lat": 23.783, "lon": 72.633, "location": "Vadnagar, Gujarat, India"},
        "lagna": "SCORPIO",
        "key_events": [
            {"event": "PM election", "date": "2014-05-16",
             "dasha": "MO MD", "validation": "Moon=9L destiny + conjunct Mars(LL) in 1H → Dharma-Karma Adhipati Yoga"},
            {"event": "Re-election", "date": "2019-05-23",
             "dasha": "MO-KE", "validation": "Ketu in 11H gains, tr. Jupiter crossing ASC activating Moon-Mars"},
        ],
        "special_yogas": ["Ruchaka Mahapurusha Yoga", "Chandra-Mangala Yoga"],
    },
    {
        "id": "ALBERT_EINSTEIN",
        "name": "Albert Einstein",
        "birth": {"date": "1879-03-14", "time": "10:50:00", "timezone": "LMT",
                  "lat": 48.400, "lon": 9.983, "location": "Ulm, Germany"},
        "lagna": "GEMINI",
        "key_events": [
            {"event": "Unemployment + illegitimate child", "date_range": "1900-1902",
             "dasha": "VE-MA", "validation": "Venus=12L isolation, Mars=6L+11L in 8H scandal"},
            {"event": "Annus Mirabilis papers", "date": "1905-01-01",
             "dasha": "VE-JU", "validation": "Jupiter=10L career, lifted from 8H obscurity to global fame"},
        ],
    },
    {
        "id": "JAWAHARLAL_NEHRU",
        "name": "Jawaharlal Nehru",
        "birth": {"date": "1889-11-14", "time": "23:36:00", "timezone": "LMT",
                  "lat": 25.450, "lon": 81.850, "location": "Allahabad, India"},
        "lagna": "CANCER",
        "key_events": [
            {"event": "First PM of India", "date": "1947-08-15",
             "dasha": "MO MD", "validation": "Moon=LL, own sign in D9+D10"},
            {"event": "Indo-China War + decline", "date": "1962-10-20",
             "dasha": "RA MD", "validation": "Rahu in 12H Gemini = foreign dispute, loss, deterioration"},
            {"event": "Death", "date": "1964-05-27",
             "dasha": "RA MD continuing", "validation": "Transit Saturn hostile alignment"},
        ],
        "edge_cases": ["Rashi Sandhi: ASC+Sun near sign boundaries; Ayanamsha sensitivity critical"],
    },
    {
        "id": "PRINCESS_DIANA",
        "name": "Princess Diana",
        "birth": {"date": "1961-07-01", "time": "19:45:00", "timezone": "BST",
                  "lat": 52.833, "lon": 0.500, "location": "Sandringham, UK"},
        "lagna": "SAGITTARIUS",
        "key_events": [
            {"event": "Marriage to Prince Charles", "date": "1981-07-29",
             "dasha": "Progressed Moon+Neptune conjunct pr.ASC in Scorpio; tr.Pluto on natal ASC"},
            {"event": "Divorce finalized", "date": "1996-08-28",
             "dasha": "Asteroid Diana 29°Aqu conjunct tr.Hera"},
            {"event": "Fatal car crash", "date": "1997-08-31",
             "dasha": "RA MD", "validation": "Tr.Saturn in Pisces=2H from Moon(Sade-Sati lethal); Jaimini Shoola: Cap-Aqu triggered; Tr.Jupiter debilitated in Cap=zero protection"},
        ],
    },
    {
        "id": "RAJIV_GANDHI",
        "name": "Rajiv Gandhi",
        "birth": {"date": "1944-08-20", "time": "10:09:00", "timezone": "IST",
                  "lat": 19.050, "lon": 72.850, "location": "Mumbai, India"},
        "lagna": "VIRGO",
        "key_events": [
            {"event": "Marriage", "date": "1968-02-25",
             "dasha": "RA-JU", "validation": "Jupiter=7L marriage"},
            {"event": "Mother death + became PM", "date": "1984-10-31",
             "dasha": "RA-JU", "validation": "Jupiter=5L (Maraka to 4H mother); inherits power"},
            {"event": "Assassination", "date": "1991-05-21",
             "dasha": "RA-ME", "validation": "Mercury=2L Maraka; Mars-Moon conj ASC + Neptune aspect = violent explosion"},
        ],
        "kp_longevity": {"lifespan": "46y 9m 1d", "method": "KP sublord 1st+8th cusp"},
    },
    {
        "id": "BV_RAMAN",
        "name": "Dr. B.V. Raman",
        "birth": {"date": "1912-08-08", "time": "19:43:00", "timezone": "IST",
                  "lat": 12.983, "lon": 77.583, "location": "Bangalore, India"},
        "lagna": "AQUARIUS",
        "lagna_degree": "10°35'",
        "cusps": {
            "2nd": "Pisces 16°12'", "3rd": "Aries 18°35'", "4th": "Taurus", "5th": "Gemini",
            "6th": "Cancer", "7th": "Leo", "8th": "Virgo", "9th": "Libra",
            "10th": "Scorpio", "11th": "Sagittarius", "12th": "Capricorn 9°31'",
        },
        "validation_points": [
            "Saturn in Taurus in 3rd Bhava (Rohini Nakshatra)",
            "Moon Exalted in Taurus in 4th Bhava",
            "Saturn-Uranus 120° trine",
            "Jupiter-Saturn 180° opposition",
            "Jupiter(9L) in 10th house(Scorpio) → Dharma-Karma Adhipati Yoga",
        ],
        "note": "Universal benchmark chart from 'How to Judge a Horoscope'",
    },
]


# ═══════════════════════════════════════════════════════════════
# 2. BVB MARRIAGE PARAMETERS (P1-P8)
# ═══════════════════════════════════════════════════════════════

BVB_MARRIAGE_PARAMETERS = {
    "P1": {
        "name": "Vimshottari Dasha-House Connection",
        "description": "Dasha lords (MD/AD/PD) connect with Lagna, 7H, LL, or 7L in D1 or D9",
        "accuracy": 1.00,
        "charts_tested": 218,
    },
    "P2": {
        "name": "Jaimini Chara Connection",
        "description": "Chara Antardasha connects with DK, DKN, Darapada, or UL",
        "accuracy": 0.96,
        "charts_tested": 218,
    },
    "P3": {
        "name": "Jupiter-Vivah Saham Aspect",
        "description": "Transiting Jupiter aspects the Vivah Saham coordinate",
        "accuracy": 0.77,
        "charts_tested": 218,
    },
    "P4": {
        "name": "Double Transit (Saturn+Jupiter)",
        "description": "Saturn and Jupiter simultaneously activate Lagna, 7H, LL, or 7L",
        "accuracy": 0.85,
        "charts_tested": 218,
    },
    "P5": {
        "name": "Transit LL-7L Mutual Connection",
        "description": "Transiting Lagna Lord and 7th Lord in mutual geometric connection",
        "accuracy": 0.98,
        "charts_tested": 218,
    },
    "P6": {
        "name": "Jupiter on Venus/Mars",
        "description": "Transiting Jupiter activates natal Venus (male) or natal Mars (female)",
        "accuracy": 0.68,
        "charts_tested": 218,
    },
    "P7": {
        "name": "Sun/Cluster near Lagna/7H",
        "description": "Sun or planet cluster transits near Lagna or 7H on marriage date",
        "accuracy": 0.70,
        "charts_tested": 218,
    },
    "P8": {
        "name": "Transit LL through 7H or vice versa",
        "description": "Transiting LL passes through 7H, or transiting 7L passes through Lagna",
        "accuracy": 0.59,
        "charts_tested": 218,
    },
}

BVB_VALIDATION_CASES: List[Dict[str, Any]] = [
    {
        "id": "CASE_1_AMRITSAR",
        "birth": {"date": "1941-08-28", "time": "22:45:00", "timezone": "IST",
                  "location": "Amritsar"},
        "marriage_date": "1967-11-18",
        "params_true": ["P1", "P2", "P4", "P5", "P6"],
        "params_false": ["P3", "P7", "P8"],
        "trigger": "Tr.Saturn+Jupiter double aspects; Tr.7L(Sun) received 10th aspect from tr.LL(Saturn) → P5",
    },
    {
        "id": "CASE_2_BHAGALPUR",
        "birth": {"date": "1968-04-05", "time": "09:25:00", "timezone": "IST",
                  "location": "Bhagalpur"},
        "marriage_date": "1989-05-22",
        "params_true": ["P1", "P2", "P4", "P5", "P6", "P7", "P8"],
        "params_false": ["P3"],
        "trigger": "Jupiter mutual aspect 7L Mars; Upapada=Aries; Saturn Scorpio+Jupiter Taurus activate 7H",
    },
    {
        "id": "CASE_3_DELHI",
        "birth": {"date": "1975-06-26", "time": "07:14:00", "timezone": "IST",
                  "location": "New Delhi"},
        "marriage_date": "derived via Manu Smriti",
        "params_true": ["P1", "P4"],
        "params_false": [],
        "trigger": "Venus in ASC → 50% baseline; D9 Lagna Vargottama; 7L Saturn in D9 confirms stability",
    },
    {
        "id": "CASE_4_SACHIN",
        "birth": {"date": "1973-04-24", "time": "12:54:00", "timezone": "IST",
                  "location": "Mumbai"},
        "marriage_date": "1995-05-19",
        "params_true": ["P1", "P4", "P5"],
        "params_false": [],
        "trigger": "Mars MD + Saturn AD; Mars=5L in 7H, Saturn=7L → P1 satisfied",
    },
    {
        "id": "CASE_5_RAJIV_GANDHI",
        "birth": {"date": "1944-08-20", "time": "10:09:00", "timezone": "IST",
                  "location": "Mumbai"},
        "marriage_date": "1968-02-25",
        "params_true": ["P1", "P4"],
        "params_false": [],
        "trigger": "Rahu MD + Jupiter AD; Jupiter=7L marriage → P1 requirement",
    },
]


# ═══════════════════════════════════════════════════════════════
# 3. EDGE CASE DEFINITIONS
# ═══════════════════════════════════════════════════════════════

EDGE_CASES = {
    "RASHI_SANDHI": {
        "description": "Planet/Lagna at 29°59' — Ayanamsha shift of 0.001° flips sign",
        "test_chart": "JAWAHARLAL_NEHRU",
        "action": "Flag 'RASHI_SANDHI' warning; test Lahiri, Raman, Sri Surya Siddhanta ayanamshas",
        "threshold_degrees": 0.5,  # Within 0.5° of sign boundary
    },
    "HIGH_LATITUDE": {
        "description": "Latitude >60°N causes arcsin failure in Placidus/Koch systems",
        "formula": "tan(lat) * tan(declination) > 1 → undefined",
        "action": "Auto-default to Equal House or Porphyry system",
        "threshold_latitude": 60.0,
    },
    "ECLIPSE_BIRTH": {
        "description": "Birth during solar/lunar eclipse needs topocentric parallax adjustment",
        "condition": "|Sun_lon - Moon_lon| ≈ 0° AND |Sun_lon - Node_lon| < 18°",
        "action": "Flag 'Eclipse Birth / Grahan Dosha'; apply topocentric correction",
        "sun_moon_orb": 5.0,
        "sun_node_orb": 18.0,
    },
    "KALA_SARPA": {
        "description": "All 7 planets hemmed between Rahu-Ketu 180° axis",
        "test_chart": "Visti Larsen (1981-11-21, 06:06, Nairobi)",
        "algorithm": "Sort longitudes; check all 7 within Rahu→Ketu arc",
        "distinguish": "Kala Sarpa (toward tail) vs Kala Amrita (toward head)",
        "true_vs_mean_node": "Can differ by up to 1.5°; may flip result",
    },
    "NEECHABHANGA": {
        "description": "Debilitated planet cancellation → Raj Yoga",
        "test_chart": "SACHIN_TENDULKAR",
        "conditions": [
            "Lord of debilitation sign in Kendra from Lagna or Moon",
            "Planet exalted in that sign conjoins debilitated planet",
            "Debilitated planet in Kendra from Lagna or Moon",
            "Lord of exaltation sign aspects debilitated planet",
        ],
        "action": "Replace debilitation penalty with Neechabhanga Raj Yoga bonus",
    },
}


# ═══════════════════════════════════════════════════════════════
# 4. UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def check_rashi_sandhi(longitude: float, threshold: float = 0.5) -> Dict[str, Any]:
    """Check if a longitude is near a sign boundary (Rashi Sandhi)."""
    degree_in_sign = longitude % 30
    near_start = degree_in_sign < threshold
    near_end = degree_in_sign > (30 - threshold)
    is_sandhi = near_start or near_end
    return {
        "longitude": longitude,
        "degree_in_sign": round(degree_in_sign, 4),
        "is_rashi_sandhi": is_sandhi,
        "boundary": "START" if near_start else ("END" if near_end else "NONE"),
        "warning": "Ayanamsha-sensitive: sign may flip with small correction" if is_sandhi else None,
    }


def check_high_latitude(latitude: float, threshold: float = 60.0) -> Dict[str, Any]:
    """Check if latitude exceeds Placidus/Koch breakdown threshold."""
    import math
    is_extreme = abs(latitude) > threshold
    return {
        "latitude": latitude,
        "is_extreme": is_extreme,
        "recommended_system": "EQUAL_HOUSE" if is_extreme else "PLACIDUS",
        "warning": f"Latitude {latitude}° exceeds {threshold}° — Placidus undefined" if is_extreme else None,
    }


def check_eclipse_birth(
    sun_lon: float, moon_lon: float, rahu_lon: float,
    sun_moon_orb: float = 5.0, sun_node_orb: float = 18.0,
) -> Dict[str, Any]:
    """Check if birth occurred during an eclipse."""
    sun_moon_diff = abs((sun_lon - moon_lon + 180) % 360 - 180)
    sun_node_diff = abs((sun_lon - rahu_lon + 180) % 360 - 180)
    is_solar = sun_moon_diff < sun_moon_orb and sun_node_diff < sun_node_orb
    # Lunar: Moon opposite Sun, near node
    moon_opp_diff = abs(((moon_lon - sun_lon + 180) % 360) - 180)
    is_lunar = (180 - moon_opp_diff) < sun_moon_orb and sun_node_diff < sun_node_orb
    return {
        "sun_moon_diff": round(sun_moon_diff, 4),
        "sun_node_diff": round(sun_node_diff, 4),
        "is_solar_eclipse": is_solar,
        "is_lunar_eclipse": is_lunar,
        "grahan_dosha": is_solar or is_lunar,
        "warning": "Eclipse birth — Grahan Dosha flagged" if (is_solar or is_lunar) else None,
    }


def check_kala_sarpa(
    planet_longitudes: Dict[str, float],
    rahu_lon: float,
    ketu_lon: float,
    use_true_node: bool = True,
) -> Dict[str, Any]:
    """
    Check Kala Sarpa Yoga: all 7 planets between Rahu-Ketu axis.

    Args:
        planet_longitudes: dict of planet→longitude (SUN,MOON,MARS,MERCURY,JUPITER,VENUS,SATURN)
        rahu_lon: Rahu longitude
        ketu_lon: Ketu longitude
        use_true_node: True=true node, False=mean node

    Returns:
        Kala Sarpa / Kala Amrita analysis.
    """
    # Normalize Rahu→Ketu arc (clockwise)
    planets_in_arc = 0
    planets_outside = 0
    trad_planets = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]

    for pname in trad_planets:
        plon = planet_longitudes.get(pname, planet_longitudes.get(pname[:2], None))
        if plon is None:
            continue
        # Check if planet is in the Rahu→Ketu arc (going forward)
        if rahu_lon < ketu_lon:
            in_arc = rahu_lon <= plon <= ketu_lon
        else:
            in_arc = plon >= rahu_lon or plon <= ketu_lon

        if in_arc:
            planets_in_arc += 1
        else:
            planets_outside += 1

    is_kala_sarpa_forward = (planets_in_arc == 7)

    # Check reverse arc (Kala Amrita)
    planets_in_reverse = 0
    for pname in trad_planets:
        plon = planet_longitudes.get(pname, planet_longitudes.get(pname[:2], None))
        if plon is None:
            continue
        if ketu_lon < rahu_lon:
            in_arc = ketu_lon <= plon <= rahu_lon
        else:
            in_arc = plon >= ketu_lon or plon <= rahu_lon
        if in_arc:
            planets_in_reverse += 1

    is_kala_amrita = (planets_in_reverse == 7)

    return {
        "is_kala_sarpa": is_kala_sarpa_forward,
        "is_kala_amrita": is_kala_amrita,
        "yoga_present": is_kala_sarpa_forward or is_kala_amrita,
        "type": "KALA_SARPA" if is_kala_sarpa_forward else ("KALA_AMRITA" if is_kala_amrita else "NONE"),
        "planets_in_rahu_ketu_arc": planets_in_arc,
        "node_type": "TRUE" if use_true_node else "MEAN",
        "note": "True vs Mean node can differ ~1.5° — may flip result" if not use_true_node else None,
    }


def check_neechabhanga(
    debilitated_planet: str,
    debil_sign: int,
    debil_sign_lord_house: int,
    exalted_planet_in_sign: Optional[str] = None,
    exalted_planet_conjunct: bool = False,
    debil_planet_in_kendra: bool = False,
    lagna_sign: int = 0,
    moon_sign: int = 0,
) -> Dict[str, Any]:
    """
    Check conditions for Neechabhanga Raj Yoga (cancellation of debilitation).

    Conditions (any one true = cancellation):
    1. Lord of debilitation sign in Kendra from Lagna or Moon
    2. Planet exalted in debilitation sign conjoins debilitated planet
    3. Debilitated planet itself in Kendra from Lagna or Moon
    4. Lord of exaltation sign aspects debilitated planet
    """
    kendra_houses = {0, 3, 6, 9}  # offsets (0-indexed)

    # Check if debil sign lord is in Kendra from Lagna or Moon
    lord_kendra_from_lagna = ((debil_sign_lord_house - lagna_sign) % 12) in kendra_houses
    lord_kendra_from_moon = ((debil_sign_lord_house - moon_sign) % 12) in kendra_houses
    cond1 = lord_kendra_from_lagna or lord_kendra_from_moon

    cond2 = exalted_planet_conjunct
    cond3 = debil_planet_in_kendra

    cancelled = cond1 or cond2 or cond3

    return {
        "planet": debilitated_planet,
        "debilitation_sign": debil_sign,
        "condition_1_lord_in_kendra": cond1,
        "condition_2_exalted_conjunct": cond2,
        "condition_3_debil_in_kendra": cond3,
        "neechabhanga": cancelled,
        "yoga": "NEECHABHANGA_RAJ_YOGA" if cancelled else "NEECHA_DEBILITATED",
        "strength_modifier": "BONUS" if cancelled else "PENALTY",
    }


def get_benchmark_chart(chart_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a benchmark chart by ID."""
    for chart in BENCHMARK_CHARTS:
        if chart["id"] == chart_id:
            return chart
    return None


def get_all_benchmark_ids() -> List[str]:
    """Return all benchmark chart IDs."""
    return [c["id"] for c in BENCHMARK_CHARTS]


def evaluate_bvb_parameters(
    params_fulfilled: List[str],
) -> Dict[str, Any]:
    """
    Evaluate BVB marriage parameter match score.

    Args:
        params_fulfilled: list of parameter keys that are True (e.g. ["P1","P4","P5"])

    Returns:
        Score and confidence assessment.
    """
    total_accuracy = 0.0
    count = 0
    for pk in params_fulfilled:
        if pk in BVB_MARRIAGE_PARAMETERS:
            total_accuracy += BVB_MARRIAGE_PARAMETERS[pk]["accuracy"]
            count += 1

    avg_accuracy = total_accuracy / max(count, 1)
    p1_present = "P1" in params_fulfilled

    # Minimum: P1 must be True (100% in study)
    if not p1_present:
        confidence = "LOW"
    elif count >= 5:
        confidence = "VERY_HIGH"
    elif count >= 3:
        confidence = "HIGH"
    elif count >= 2:
        confidence = "MODERATE"
    else:
        confidence = "LOW"

    return {
        "params_fulfilled": params_fulfilled,
        "count": count,
        "avg_accuracy": round(avg_accuracy, 3),
        "p1_present": p1_present,
        "confidence": confidence,
    }
