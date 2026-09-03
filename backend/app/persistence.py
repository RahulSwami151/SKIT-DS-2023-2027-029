"""Persistence bridge for detected task dependencies."""

from typing import List

from sqlalchemy.orm import Session

from .dependency_detector import detect_dependencies
from .models import Task, TaskDependency


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


def detect_and_persist_dependencies(
    session: Session, student_id: int
) -> List[TaskDependency]:
    tasks = get_student_tasks(session, student_id)
    detected = detect_dependencies(tasks)
    newly_created = []

    for dependency in detected:
        if not _dependency_exists(
            session, dependency.task_id, dependency.prerequisite_task_id
        ):
            session.add(dependency)
            newly_created.append(dependency)

    session.commit()
    return newly_created
