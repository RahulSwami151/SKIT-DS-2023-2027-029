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
from backend.app.sor_scoring import calculate_sor_score

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


def test_dashboard_is_served_by_app():
    for path in ("/", "/dashboard"):
        response = client.get(path)

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert "Task Dependency Graph" in response.text


def seed_tasks():
    session = TestSession()
    reading = Task(student_id=1, title="Read Ch.5", task_type=TaskType.READING,
                    subject="DBMS", deadline=datetime.utcnow() + timedelta(days=1),
                    status="in_progress", priority=4, importance=5)
    assignment = Task(student_id=1, title="Assignment 2", task_type=TaskType.ASSIGNMENT,
                       subject="DBMS", deadline=datetime.utcnow() + timedelta(days=3),
                       status="pending", priority=3, importance=4)
    session.add_all([reading, assignment])
    session.commit()
    session.close()


def test_detect_dependencies_endpoint():
    seed_tasks()
    response = client.post("/students/1/detect-dependencies")
    assert response.status_code == 200
    assert response.json()["new_dependencies_created"] >= 1


def test_get_dependency_graph_endpoint():
    seed_tasks()
    detect_response = client.post("/students/1/detect-dependencies")
    assert detect_response.status_code == 200

    response = client.get("/students/1/dependency-graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data and "edges" in data
    node_titles = {node["id"]: node["title"] for node in data["nodes"]}
    assert "Read Ch.5" in node_titles.values()
    assert "Assignment 2" in node_titles.values()
    reading = next(node for node in data["nodes"] if node["title"] == "Read Ch.5")
    assert reading["deadline"] is not None
    assert reading["status"] == "in_progress"
    assert reading["priority"] == 4
    assert reading["importance"] == 5
    for node in data["nodes"]:
        assert node["structural_impact"] == sum(
            edge["target"] == node["id"] for edge in data["edges"]
        )
    assert reading["structural_impact"] > 0
    assert any(
        node_titles[edge["source"]] == "Assignment 2"
        and node_titles[edge["target"]] == "Read Ch.5"
        for edge in data["edges"]
    )
    assert reading["sor_score"] is not None
    assert reading["sor_components"]["importance"] == 5
    assert reading["sor_components"]["structural_impact"] > 0
    assert reading["sor_components"]["overload_association"] == 4
    assert reading["sor_components"]["feasibility_relief"] == 0


def test_sor_score_combines_importance_priority_deadline_and_mood_relief():
    now = datetime(2026, 11, 4)
    score = calculate_sor_score(
        importance=4,
        priority=3,
        deadline=now + timedelta(days=1),
        mood="good",
        structural_impact=2,
        now=now,
    )

    assert score == {
        "sor_score": 6.5,
        "sor_components": {
            "structural_impact": 2,
            "importance": 4,
            "structural_score": 6,
            "overload_association": 3,
            "deadline_pressure": 2.5,
            "feasibility_relief": 5,
        },
    }


def test_sor_score_handles_missing_optional_inputs():
    score = calculate_sor_score(
        importance=None,
        priority=None,
        deadline=None,
        mood=None,
        structural_impact=0,
        now=datetime(2026, 11, 4),
    )

    assert score["sor_score"] == 0
    assert score["sor_components"]["deadline_pressure"] == 0
    assert score["sor_components"]["feasibility_relief"] == 0


def test_dependency_graph_reports_unsupported_mood():
    session = TestSession()
    session.add(
        Task(
            student_id=2,
            title="Task with unrecognized mood",
            task_type=TaskType.OTHER,
            mood="unknown",
        )
    )
    session.commit()
    session.close()

    response = client.get("/students/2/dependency-graph")
    assert response.status_code == 422
    assert "Unsupported mood" in response.json()["detail"]
