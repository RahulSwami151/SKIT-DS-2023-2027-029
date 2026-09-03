"""SQLAlchemy models for tasks and detected dependencies."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, Integer, String
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
