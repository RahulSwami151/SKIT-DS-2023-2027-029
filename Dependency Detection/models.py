"""
models.py
---------
User Story: Dependency Detection
Week 1 draft — initial data model for tasks and task dependencies.

This defines the SQLAlchemy ORM models that will back the
dependency-detection logic. A "dependency" here means: task B cannot
(or should not) be started/completed until task A is done — e.g.
"finish readings" -> "write assignment" -> "submit before exam".

NOTE: This is a Week-1 draft. Fields/relationships may be extended in
Week 2 once the full dependency graph generation (NetworkX/Neo4j) is
implemented.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TaskType(str, Enum):
    """Rough categories of academic tasks used for dependency heuristics."""
    READING = "reading"
    ASSIGNMENT = "assignment"
    PROJECT = "project"
    QUIZ = "quiz"
    EXAM = "exam"
    OTHER = "other"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    task_type = Column(SAEnum(TaskType), default=TaskType.OTHER, nullable=False)
    subject = Column(String(100), nullable=True)   # e.g. "DBMS", "OS"
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Outgoing dependencies: tasks that THIS task depends on (prerequisites)
    depends_on = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.task_id",
        back_populates="task",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Task id={self.id} title={self.title!r} type={self.task_type}>"


class TaskDependency(Base):
    """
    Represents a directed edge: task -> prerequisite_task
    i.e. `task` cannot reasonably start until `prerequisite_task` is done.
    """
    __tablename__ = "task_dependencies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    prerequisite_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    # How the dependency was found (helps debugging / SOR scoring later)
    reason = Column(String(255), nullable=True)

    task = relationship("Task", foreign_keys=[task_id], back_populates="depends_on")
    prerequisite_task = relationship("Task", foreign_keys=[prerequisite_task_id])

    def __repr__(self):
        return (
            f"<TaskDependency task={self.task_id} "
            f"depends_on={self.prerequisite_task_id} reason={self.reason!r}>"
        )
