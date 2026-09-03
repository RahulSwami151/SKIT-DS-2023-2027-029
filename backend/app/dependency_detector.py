"""Rule-based dependency detection for academic tasks."""

from typing import List

from .models import Task, TaskDependency, TaskType

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
    if prerequisite.deadline is None or task.deadline is None:
        return True
    return prerequisite.deadline <= task.deadline


def _type_precedes(prerequisite: Task, task: Task) -> bool:
    return TYPE_PRECEDENCE.get(prerequisite.task_type, 1) < TYPE_PRECEDENCE.get(
        task.task_type, 1
    )


def detect_dependencies(tasks: List[Task]) -> List[TaskDependency]:
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

            detected.append(
                TaskDependency(
                    task_id=task.id,
                    prerequisite_task_id=candidate.id,
                    reason=(
                        f"type '{candidate.task_type.value}' precedes "
                        f"'{task.task_type.value}' in same subject "
                        f"'{task.subject}'"
                    ),
                )
            )

    return detected
