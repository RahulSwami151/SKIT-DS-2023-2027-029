"""
persistence.py
----------------
User Story: Dependency Detection
Week 2 — persisting detected dependencies to the database.

Bridges dependency_detector.py (Week 1: pure detection logic) with
the database: runs detection over a student's stored tasks and
saves any newly-found TaskDependency rows, skipping duplicates.
"""

from typing import List
from sqlalchemy.orm import Session

from .models import Task, TaskDependency
from .dependency_detector import detect_dependencies


def get_student_tasks(session: Session, student_id: int) -> List[Task]:
    return session.query(Task).filter(Task.student_id == student_id).all()


def _dependency_exists(session: Session, task_id: int, prerequisite_task_id: int) -> bool:
    return (
        session.query(TaskDependency)
        .filter(
            TaskDependency.task_id == task_id,
            TaskDependency.prerequisite_task_id == prerequisite_task_id,
        )
        .first()
        is not None
    )


def detect_and_persist_dependencies(session: Session, student_id: int) -> List[TaskDependency]:
    """
    Runs the Week-1 detector over a student's tasks and saves any new
    dependency links to the database. Returns the list of NEWLY
    created TaskDependency rows (already-existing ones are skipped).
    """
    tasks = get_student_tasks(session, student_id)
    detected = detect_dependencies(tasks)

    newly_created = []
    for dep in detected:
        if not _dependency_exists(session, dep.task_id, dep.prerequisite_task_id):
            session.add(dep)
            newly_created.append(dep)

    session.commit()
    return newly_created