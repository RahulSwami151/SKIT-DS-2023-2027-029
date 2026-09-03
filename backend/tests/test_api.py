"""
test_api.py
-------------
Week 3 tests for the FastAPI dependency-detection endpoints.
"""

import sys, os , sqlalchemy
import fastapi
import sqlalchemy.orm

from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models import Base, Task, TaskType
from backend.app.main import app
from backend.app.database import get_session

# StaticPool keeps the SAME in-memory SQLite connection alive across
# sessions in this test module.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def override_get_session():
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_session] = override_get_session
client = TestClient(app)


def seed_tasks():
    session = TestSession()
    reading = Task(student_id=1, title="Read Ch.5", task_type=TaskType.READING,
                    subject="DBMS", deadline=datetime.utcnow() + timedelta(days=1))
    assignment = Task(student_id=1, title="Assignment 2", task_type=TaskType.ASSIGNMENT,
                       subject="DBMS", deadline=datetime.utcnow() + timedelta(days=3))
    session.add_all([reading, assignment])
    session.commit()
    session.close()


def test_detect_dependencies_endpoint():
    seed_tasks()
    response = client.post("/students/1/detect-dependencies")
    assert response.status_code == 200
    assert response.json()["new_dependencies_created"] >= 1


def test_get_dependency_graph_endpoint():
    response = client.get("/students/1/dependency-graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data and "edges" in data
    assert len(data["nodes"]) == 2
