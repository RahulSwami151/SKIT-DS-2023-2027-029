"""Compute Structural Overload Relief scores for academic tasks."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

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


def _structural_impact_value(importance: Optional[Union[int, str]]) -> int:
    if importance is None:
        return 0
    if isinstance(importance, str):
        label = importance.strip().title()
        if label in importances:
            return importances[label]
        try:
            importance = int(label)
        except ValueError as exc:
            allowed = ", ".join(importances)
            raise ValueError(
                f"Unsupported structural impact '{importance}'. "
                f"Expected one of: {allowed}, or an integer from 1 to 5."
            ) from exc
    if not 1 <= importance <= 5:
        raise ValueError("Structural impact must be between 1 and 5.")
    return importance


def _deadline_pressure(deadline: Optional[datetime], now: datetime) -> float:
    if deadline is None:
        return 0.0

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
    importance: Optional[Union[int, str]],
    overload_association: int,
    deadline: Optional[datetime],
    mood: Optional[str],
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Return a live score and its component values for one task."""
    mood_label = mood.strip().lower() if mood else None
    if mood_label is not None and mood_label not in MOOD_RELIEF:
        allowed_moods = ", ".join(sorted(MOOD_RELIEF))
        raise ValueError(
            f"Unsupported mood '{mood}'. Expected one of: {allowed_moods}."
        )

    if overload_association < 0:
        raise ValueError("Overload association cannot be negative.")

    current_time = now or datetime.now(timezone.utc)
    deadline_score = _deadline_pressure(deadline, current_time)
    mood_relief = MOOD_RELIEF[mood_label] if mood_label else 0
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
