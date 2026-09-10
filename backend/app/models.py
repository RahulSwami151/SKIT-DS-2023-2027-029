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


# ============================================================
# NEW — User (didn't exist before; everything else hangs off this)
# ============================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    journal_entries = relationship(
        "JournalEntry", back_populates="user", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # FK added — see merge note
    title = Column(String(255), nullable=False)
    task_type = Column(SAEnum(TaskType), default=TaskType.OTHER, nullable=False)
    subject = Column(String(100), nullable=True)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- NEW columns for Dashboard / SOR scoring ---
    priority = Column(SmallInteger, nullable=True)      # 1-5, set on Add/Edit Task
    importance = Column(SmallInteger, nullable=True)    # 1-5, set on Add/Edit Task
    mood = Column(String(40), nullable=True)             # captured at task creation
    status = Column(String(20), default="pending", nullable=False)  # pending/in_progress/completed
    sor_score = Column(Numeric(5, 2), nullable=True)     # computed by backend, never user-entered
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("priority BETWEEN 1 AND 5", name="ck_tasks_priority"),
        CheckConstraint("importance BETWEEN 1 AND 5", name="ck_tasks_importance"),
        CheckConstraint("status IN ('pending','in_progress','completed')", name="ck_tasks_status"),
    )

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
    created_at = Column(DateTime, default=datetime.utcnow)  # NEW

    __table_args__ = (
        UniqueConstraint("task_id", "prerequisite_task_id", name="uq_task_prerequisite_pair"),  # NEW
        CheckConstraint("task_id != prerequisite_task_id", name="ck_task_not_self_dependent"),   # NEW
    )

    task = relationship("Task", foreign_keys=[task_id], back_populates="depends_on")
    prerequisite_task = relationship("Task", foreign_keys=[prerequisite_task_id])


# ============================================================
# NEW — JournalEntry (didn't exist before)
# ============================================================
class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mood_rating = Column(SmallInteger, nullable=False)
    stress_level = Column(SmallInteger, nullable=False)
    energy_level = Column(SmallInteger, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("mood_rating BETWEEN 1 AND 5", name="ck_journal_mood"),
        CheckConstraint("stress_level BETWEEN 1 AND 5", name="ck_journal_stress"),
        CheckConstraint("energy_level BETWEEN 1 AND 5", name="ck_journal_energy"),
    )

    user = relationship("User", back_populates="journal_entries")