"""SQLAlchemy models for users, tasks, detected dependencies, and journal entries.

MERGE NOTE (Database Design, Week 2):
  - Task, TaskDependency, and TaskType are Rahul's original code from the
    Dependency Detection story — column names (prerequisite_task_id, reason)
    are UNCHANGED so dependency_detector.py and persistence.py keep working.
  - Added: User, JournalEntry (new tables — didn't exist before).
  - Added to Task: priority, importance, mood, status, sor_score, updated_at.
  - Added to TaskDependency: created_at, UNIQUE(task_id, prerequisite_task_id),
    CHECK(task_id != prerequisite_task_id).
  - student_id now has ForeignKey("users.id") added — FLAG FOR RAHUL: this is
    a real behavior change. Any existing code inserting tasks with a
    student_id that doesn't exist in `users` will now fail. Confirm with him
    before merging.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column, DateTime, Enum as SAEnum, ForeignKey, Integer, String,
    SmallInteger, Numeric, Text, CheckConstraint, UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TaskType(str, Enum):
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
    subject = Column(String(100), nullable=True)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    depends_on = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.task_id",
        back_populates="task",
        cascade="all, delete-orphan",
    )


class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    prerequisite_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    reason = Column(String(255), nullable=True)

    task = relationship("Task", foreign_keys=[task_id], back_populates="depends_on")
    prerequisite_task = relationship("Task", foreign_keys=[prerequisite_task_id])
