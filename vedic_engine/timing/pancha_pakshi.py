"""
Pancha Pakshi — Five Bird Timing System.

The Pancha Pakshi system assigns one of five birds (Vulture, Owl, Crow,
Cock, Peacock) based on birth Nakshatra and Paksha. Each bird cycles
through 5 activities (Ruling, Eating, Walking, Sleeping, Dying) in
2h 24m (144 min) segments from sunrise/sunset.

Reference: Pancha Pakshi Shastra, Tamil Siddha tradition.
"""
from __future__ import annotations
from typing import Dict, Any, Optional, List, Tuple


# ── Bird Names ─────────────────────────────────────────────────
BIRDS = ["VULTURE", "OWL", "CROW", "COCK", "PEACOCK"]

# ── Bird Assignment by Nakshatra Group × Paksha ────────────────
# Nakshatra indices: 0=Ashwini .. 26=Revati
# Group 0: Nak 0–5   (Ashwini → Mrigashira)
# Group 1: Nak 6–10  (Ardra → Purva Phalguni)
# Group 2: Nak 11–15 (Uttara Phalguni → Vishakha)
# Group 3: Nak 16–20 (Anuradha → Uttara Ashadha)
# Group 4: Nak 21–26 (Shravana → Revati)

BIRD_ASSIGNMENT = {
    # (group_index, paksha) → bird
    (0, "SHUKLA"): "VULTURE",
    (1, "SHUKLA"): "OWL",
    (2, "SHUKLA"): "CROW",
    (3, "SHUKLA"): "COCK",
    (4, "SHUKLA"): "PEACOCK",
    (0, "KRISHNA"): "PEACOCK",
    (1, "KRISHNA"): "COCK",
    (2, "KRISHNA"): "CROW",
    (3, "KRISHNA"): "OWL",
    (4, "KRISHNA"): "VULTURE",
}

# ── Activities & Quality Ranking ───────────────────────────────
ACTIVITIES = ["RULING", "EATING", "WALKING", "SLEEPING", "DYING"]
ACTIVITY_QUALITY = {
    "RULING":   5,  # Best
    "EATING":   4,  # Good
    "WALKING":  3,  # Neutral
    "SLEEPING": 2,  # Bad
    "DYING":    1,  # Worst
}
ACTIVITY_LABELS = {
    "RULING":   "BEST",
    "EATING":   "GOOD",
    "WALKING":  "NEUTRAL",
    "SLEEPING": "BAD",
    "DYING":    "WORST",
}

# ── Activity Sequences (5 segments each for day/night × paksha) ──
# Key: (paksha, period) where period = "DAY" or "NIGHT"
# Value: list of 5 activities in segment order (0→4)
ACTIVITY_SEQUENCES = {
    ("SHUKLA", "DAY"):   ["EATING", "WALKING", "RULING", "SLEEPING", "DYING"],
    ("SHUKLA", "NIGHT"): ["EATING", "RULING", "DYING", "WALKING", "SLEEPING"],
    ("KRISHNA", "DAY"):  ["EATING", "DYING", "SLEEPING", "RULING", "WALKING"],
    ("KRISHNA", "NIGHT"):["EATING", "SLEEPING", "WALKING", "DYING", "RULING"],
}

# ── Segment duration in minutes ────────────────────────────────
SEGMENT_MINUTES = 144  # 2 hours 24 minutes = 144 min; 5 × 144 = 720 = 12 hr


def nakshatra_group(nak_index: int) -> int:
    """Return 0-4 group for a nakshatra index (0-26)."""
    if nak_index < 0 or nak_index > 26:
        return 0  # fallback
    if nak_index <= 5:
        return 0
    if nak_index <= 10:
        return 1
    if nak_index <= 15:
        return 2
    if nak_index <= 20:
        return 3
    return 4


def get_birth_bird(nak_index: int, paksha: str) -> str:
    """
    Determine birth bird from nakshatra index and paksha.

    Args:
        nak_index: 0-26 (Ashwini=0, Revati=26)
        paksha: "SHUKLA" or "KRISHNA"

    Returns:
        Bird name (VULTURE/OWL/CROW/COCK/PEACOCK)
    """
    group = nakshatra_group(nak_index)
    p = paksha.upper()
    return BIRD_ASSIGNMENT.get((group, p), "CROW")  # Crow as default fallback


def get_current_activity(
    paksha: str,
    is_daytime: bool,
    minutes_since_sunrise_or_sunset: float,
) -> Dict[str, Any]:
    """
    Get the current activity for a Pancha Pakshi bird.

    Args:
        paksha: "SHUKLA" or "KRISHNA"
        is_daytime: True if between sunrise and sunset
        minutes_since_sunrise_or_sunset: Minutes elapsed since sunrise (day)
            or sunset (night)

    Returns:
        Dict with activity, segment_index, quality, and label.
    """
    period = "DAY" if is_daytime else "NIGHT"
    seq = ACTIVITY_SEQUENCES.get((paksha.upper(), period), ACTIVITY_SEQUENCES[("SHUKLA", "DAY")])

    segment = int(minutes_since_sunrise_or_sunset / SEGMENT_MINUTES)
    segment = max(0, min(4, segment))  # clamp 0-4

    activity = seq[segment]
    return {
        "activity": activity,
        "segment_index": segment,
        "quality": ACTIVITY_QUALITY[activity],
        "label": ACTIVITY_LABELS[activity],
        "period": period,
        "paksha": paksha.upper(),
    }


def get_all_segments(paksha: str, is_daytime: bool) -> List[Dict[str, Any]]:
    """Return all 5 segment activities for given paksha and period."""
    period = "DAY" if is_daytime else "NIGHT"
    seq = ACTIVITY_SEQUENCES.get((paksha.upper(), period), ACTIVITY_SEQUENCES[("SHUKLA", "DAY")])

    segments = []
    for i, act in enumerate(seq):
        segments.append({
            "segment": i,
            "start_minutes": i * SEGMENT_MINUTES,
            "end_minutes": (i + 1) * SEGMENT_MINUTES,
            "activity": act,
            "quality": ACTIVITY_QUALITY[act],
            "label": ACTIVITY_LABELS[act],
        })
    return segments


def get_pakshi_compatibility(bird_a: str, bird_b: str) -> Dict[str, Any]:
    """
    Compatibility between two birds.

    Same bird → highly compatible
    Natural allies → moderate
    Natural enemies → incompatible

    Simplified traditional mapping:
        Peacock ↔ Cock: allies (both solar-diurnal)
        Vulture ↔ Owl: allies (both nocturnal-predatory)
        Crow: neutral to all (transitional)
    """
    a = bird_a.upper()
    b = bird_b.upper()

    if a == b:
        return {"compatibility": "EXCELLENT", "score": 5, "note": "Same bird — full harmony"}

    allies = {frozenset({"PEACOCK", "COCK"}), frozenset({"VULTURE", "OWL"})}
    enemies = {frozenset({"PEACOCK", "VULTURE"}), frozenset({"COCK", "OWL"})}

    pair = frozenset({a, b})
    if pair in allies:
        return {"compatibility": "GOOD", "score": 4, "note": "Natural allies"}
    if pair in enemies:
        return {"compatibility": "POOR", "score": 2, "note": "Natural enemies"}

    # Crow involved or other combinations
    if "CROW" in {a, b}:
        return {"compatibility": "NEUTRAL", "score": 3, "note": "Crow is transitional — moderate"}

    return {"compatibility": "MODERATE", "score": 3, "note": "Mixed pairing"}


def compute_pancha_pakshi(
    birth_nak_index: int,
    birth_paksha: str,
    current_paksha: Optional[str] = None,
    is_daytime: Optional[bool] = None,
    minutes_since_ref: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Full Pancha Pakshi computation for a native.

    Args:
        birth_nak_index: Birth nakshatra index 0-26
        birth_paksha: Paksha at birth ("SHUKLA" or "KRISHNA")
        current_paksha: Current paksha (for transit activity; optional)
        is_daytime: True=day, False=night (for transit; optional)
        minutes_since_ref: Minutes since sunrise/sunset (for transit; optional)

    Returns:
        Dict with birth bird, activity tables, and optional current activity.
    """
    bird = get_birth_bird(birth_nak_index, birth_paksha)
    group = nakshatra_group(birth_nak_index)

    result: Dict[str, Any] = {
        "birth_nakshatra_index": birth_nak_index,
        "birth_paksha": birth_paksha.upper(),
        "nakshatra_group": group,
        "birth_bird": bird,
        "day_segments_shukla": get_all_segments("SHUKLA", True),
        "night_segments_shukla": get_all_segments("SHUKLA", False),
        "day_segments_krishna": get_all_segments("KRISHNA", True),
        "night_segments_krishna": get_all_segments("KRISHNA", False),
    }

    if current_paksha is not None and is_daytime is not None and minutes_since_ref is not None:
        result["current_activity"] = get_current_activity(
            current_paksha, is_daytime, minutes_since_ref
        )

    return result
