"""
test_graph_builder.py
------------------------
Week 2 sanity tests for:
  - persisting detected dependencies to the DB (persistence.py)
  - building the NetworkX dependency graph (graph_builder.py)

Uses an in-memory SQLite database so tests are fast and don't touch
the real dev/production database.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import Base, Task, TaskType
from backend.app.persistence import detect_and_persist_dependencies
from backend.app.graph_builder import (
    build_dependency_graph,
    export_graph_for_frontend,
    get_task_prerequisites,
    has_circular_dependency,
)


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def seed_tasks(session):
    reading = Task(
        student_id=1, title="Read Ch.5", task_type=TaskType.READING,
        subject="DBMS", deadline=datetime.utcnow() + timedelta(days=1),
    )
    assignment = Task(
        student_id=1, title="Assignment 2", task_type=TaskType.ASSIGNMENT,
        subject="DBMS", deadline=datetime.utcnow() + timedelta(days=3),
    )
    exam = Task(
        student_id=1, title="Mid-Sem Exam", task_type=TaskType.EXAM,
        subject="DBMS", deadline=datetime.utcnow() + timedelta(days=5),
    )
    session.add_all([reading, assignment, exam])
    session.commit()
    return reading, assignment, exam


def test_detect_and_persist_dependencies():
    session = make_session()
    reading, assignment, exam = seed_tasks(session)

    created = detect_and_persist_dependencies(session, student_id=1)
    assert len(created) > 0

    # Running it again should NOT create duplicates
    created_again = detect_and_persist_dependencies(session, student_id=1)
    assert created_again == []


def test_build_graph_has_correct_nodes_and_edges():
    session = make_session()
    reading, assignment, exam = seed_tasks(session)
    detect_and_persist_dependencies(session, student_id=1)

    graph = build_dependency_graph(session, student_id=1)

    assert graph.number_of_nodes() == 3
    assert graph.has_edge(reading.id, assignment.id)
    assert graph.has_edge(reading.id, exam.id)
    assert graph.has_edge(assignment.id, exam.id)


def test_export_graph_for_frontend_shape():
    session = make_session()
    seed_tasks(session)
    detect_and_persist_dependencies(session, student_id=1)

    graph = build_dependency_graph(session, student_id=1)
    data = export_graph_for_frontend(graph)

    assert "nodes" in data and "edges" in data
    assert len(data["nodes"]) == 3
    assert all("title" in n for n in data["nodes"])


def test_get_task_prerequisites():
    session = make_session()
    reading, assignment, exam = seed_tasks(session)
    detect_and_persist_dependencies(session, student_id=1)

    graph = build_dependency_graph(session, student_id=1)
    prereqs = get_task_prerequisites(graph, exam.id)

    assert reading.id in prereqs
    assert assignment.id in prereqs


def test_no_circular_dependency():
    session = make_session()
    seed_tasks(session)
    detect_and_persist_dependencies(session, student_id=1)

    graph = build_dependency_graph(session, student_id=1)
    assert has_circular_dependency(graph) is False
