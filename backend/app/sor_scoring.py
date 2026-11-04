"""Compute Structural Overload Relief scores for academic tasks."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

MOOD_RELIEF = {
    "good": 5,
    "okay": 3,
    "tired": 2,
    "stressed": 1,
}


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
    importance: Optional[int],
    priority: Optional[int],
    deadline: Optional[datetime],
    mood: Optional[str],
    structural_impact: int,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Return a live score and its component values for one task."""
    mood_label = mood.strip().lower() if mood else None
    if mood_label is not None and mood_label not in MOOD_RELIEF:
        allowed_moods = ", ".join(sorted(MOOD_RELIEF))
        raise ValueError(
            f"Unsupported mood '{mood}'. Expected one of: {allowed_moods}."
        )

    current_time = now or datetime.now(timezone.utc)
    deadline_score = _deadline_pressure(deadline, current_time)
    mood_relief = MOOD_RELIEF[mood_label] if mood_label else 0
    importance_score = importance or 0
    overload_association = priority or 0
    structural_score = structural_impact + importance_score
    score = (
        structural_score
        + overload_association
        + deadline_score
        - mood_relief
    )

    return {
        "sor_score": round(score, 2),
        "sor_components": {
            "structural_impact": structural_impact,
            "importance": importance_score,
            "structural_score": structural_score,
            "overload_association": overload_association,
            "deadline_pressure": deadline_score,
            "feasibility_relief": mood_relief,
        },
    }
