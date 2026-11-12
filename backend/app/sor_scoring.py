"""Compute Structural Overload Relief scores for academic tasks."""

from datetime import datetime, timezone
from typing import Any, Dict

MOOD_RELIEF = {
    "high energy": 5,
    "good": 4,
    "neutral": 3,
    "fatigued": 2,
    "overwhelmed": 1,
}

importances = {
    "High" : 3,
    "Med" : 2,
    "Low" : 1,
}


def _structural_impact_value(importance: str) -> int:
    if not isinstance(importance, str) or not importance.strip():
        raise ValueError("Structural impact is required.")
    label = importance.strip().title()
    try:
        return importances[label]
    except KeyError as exc:
        allowed = ", ".join(importances)
        raise ValueError(
            f"Unsupported structural impact '{importance}'. "
            f"Expected one of: {allowed}."
        ) from exc


def _deadline_pressure(deadline: datetime, now: datetime) -> float:
    if deadline is None:
        raise ValueError("Deadline is required.")

    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    days_remaining = (deadline - now).total_seconds() / 86400
    if days_remaining <= 0:
        return 5.0
    return round(min(5.0, 5.0 / (1.0 + days_remaining)), 2)


def calculate_sor_score(
    *,
    importance: str,
    overload_association: int,
    deadline: datetime,
    mood: str,
    now: datetime,
) -> Dict[str, Any]:
    """Return a live score and its component values for one task."""
    if not mood or not mood.strip():
        raise ValueError("Mood is required.")
    mood_label = mood.strip().lower()
    if mood_label not in MOOD_RELIEF:
        allowed_moods = ", ".join(sorted(MOOD_RELIEF))
        raise ValueError(
            f"Unsupported mood '{mood}'. Expected one of: {allowed_moods}."
        )

    if overload_association is None:
        raise ValueError("Overload association is required.")
    if overload_association < 0:
        raise ValueError("Overload association cannot be negative.")

    deadline_score = _deadline_pressure(deadline, now)
    mood_relief = MOOD_RELIEF[mood_label]
    structural_score = _structural_impact_value(importance)
    score = structural_score + overload_association + deadline_score - mood_relief

    return {
        "sor_score": round(score, 2),
        "sor_components": {
            "structural_impact": structural_score,
            "overload_association": overload_association,
            "deadline_pressure": deadline_score,
            "feasibility_relief": mood_relief,
        },
    }
