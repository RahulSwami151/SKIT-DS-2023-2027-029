"""
dependency_detector.py
-----------------------
User Story: Dependency Detection
Week 1 draft — logic to identify prerequisite relationships between
academic tasks, based on task type ordering, shared subject, and
deadline sequencing.

This is a first-pass RULE-BASED detector (not ML-based). It looks at
pairs of tasks belonging to the same subject and applies simple
heuristics to decide whether one task is a likely prerequisite of
another. This will feed the dependency graph generation (NetworkX)
planned for Week 2.

Heuristics used (v1):
1. TYPE ORDER: certain task types naturally precede others
   e.g. reading -> assignment -> quiz -> exam -> project (loosely)
2. SAME SUBJECT: dependencies are only considered within the same
   subject/course, to avoid false positives across unrelated tasks.
3. DEADLINE ORDER: the prerequisite's deadline must be <= the
   dependent task's deadline (can't depend on something due later).
"""

from typing import List
from .models import Task, TaskDependency, TaskType

# Rough precedence order of task types (lower index = earlier / prerequisite)
TYPE_PRECEDENCE = {
    TaskType.READING: 0,
    TaskType.ASSIGNMENT: 1,
    TaskType.QUIZ: 2,
    TaskType.PROJECT: 2,
    TaskType.EXAM: 3,
    TaskType.OTHER: 1,
}


def _same_subject(task_a: Task, task_b: Task) -> bool:
    if not task_a.subject or not task_b.subject:
        return False
    return task_a.subject.strip().lower() == task_b.subject.strip().lower()


def _deadline_allows_dependency(prerequisite: Task, task: Task) -> bool:
    """Prerequisite must be due on or before the dependent task."""
    if prerequisite.deadline is None or task.deadline is None:
        # Without both deadlines we can't be sure — be conservative (allow it),
        # final decision will also weigh in type precedence.
        return True
    return prerequisite.deadline <= task.deadline


def _type_precedes(prerequisite: Task, task: Task) -> bool:
    return TYPE_PRECEDENCE.get(prerequisite.task_type, 1) < TYPE_PRECEDENCE.get(
        task.task_type, 1
    )


def detect_dependencies(tasks: List[Task]) -> List[TaskDependency]:
    """
    Given a flat list of a student's tasks, return a list of
    TaskDependency objects representing detected prerequisite links.

    This is intentionally simple for Week 1 — O(n^2) comparison is fine
    at expected task-list sizes (dozens, not thousands).
    """
    detected: List[TaskDependency] = []

    for task in tasks:
        for candidate in tasks:
            if candidate.id == task.id:
                continue
            if not _same_subject(task, candidate):
                continue
            if not _type_precedes(candidate, task):
                continue
            if not _deadline_allows_dependency(candidate, task):
                continue

            reason = (
                f"type '{candidate.task_type.value}' precedes "
                f"'{task.task_type.value}' in same subject "
                f"'{task.subject}'"
            )
            detected.append(
                TaskDependency(
                    task_id=task.id,
                    prerequisite_task_id=candidate.id,
                    reason=reason,
                )
            )

    return detected
