"""
test_api.py
-------------
Week 3 tests for the FastAPI dependency-detection endpoints.
"""

import sys, os , sqlalchemy
import fastapi
import sqlalchemy.orm
from datetime import datetime, timedelta
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import networkx as nx

from backend.app.models import Base, Task, TaskType
from backend.app.main import app
from backend.app.database import get_session
from backend.app.graph_builder import calculate_overload_associations
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
                    status="in_progress", priority=4, importance="High", mood="good")
    assignment = Task(student_id=1, title="Assignment 2", task_type=TaskType.ASSIGNMENT,
                       subject="DBMS", deadline=datetime.utcnow() + timedelta(days=3),
                       status="pending", priority=3, importance="Med", mood="neutral")
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
    assert reading["importance"] == "High"
    for node in data["nodes"]:
        assert node["structural_impact"] == {"High": 3, "Med": 2, "Low": 1}[
            node["importance"]
        ]
    assert any(
        node_titles[edge["source"]] == "Assignment 2"
        and node_titles[edge["target"]] == "Read Ch.5"
        for edge in data["edges"]
    )
    assert reading["sor_score"] is not None
    assert reading["sor_components"]["structural_impact"] == 3
    assert reading["sor_components"]["overload_association"] == 0
    assert reading["sor_components"]["feasibility_relief"] == 4


def test_sor_score_combines_structural_impact_overload_deadline_and_mood():
    now = datetime(2026, 11, 4)
    score = calculate_sor_score(
        importance="Med",
        overload_association=2,
        deadline=now + timedelta(days=1),
        mood="good",
        now=now,
    )

    assert score == {
        "sor_score": 2.5,
        "sor_components": {
            "structural_impact": 2,
            "overload_association": 2,
            "deadline_pressure": 2.5,
            "feasibility_relief": 4,
        },
    }


def test_sor_score_rejects_missing_required_inputs():
    inputs = {
        "importance": "Med",
        "overload_association": 0,
        "deadline": datetime(2026, 11, 5),
        "mood": "good",
        "now": datetime(2026, 11, 4),
    }
    required_inputs = {
        "importance": "Structural impact is required.",
        "deadline": "Deadline is required.",
        "mood": "Mood is required.",
        "overload_association": "Overload association is required.",
    }

    for field, message in required_inputs.items():
        missing_input = {**inputs, field: None}
        with pytest.raises(ValueError, match=message):
            calculate_sor_score(**missing_input)


def test_tasks_require_all_sor_inputs():
    required_fields = ("deadline", "importance", "mood")
    session = TestSession()
    for field in required_fields:
        task_values = {
            "student_id": 4,
            "title": f"Task missing {field}",
            "task_type": TaskType.OTHER,
            "deadline": datetime(2026, 11, 5),
            "importance": "High",
            "mood": "good",
        }
        task_values[field] = None
        session.add(Task(**task_values))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
    session.close()


def test_completed_prerequisite_reduces_downstream_overload():
    graph = nx.DiGraph()
    graph.add_nodes_from([
        (1, {"status": "pending"}),
        (2, {"status": "pending"}),
        (3, {"status": "pending"}),
    ])
    graph.add_edges_from([(2, 1), (3, 2)])

    assert calculate_overload_associations(graph) == {1: 0, 2: 1, 3: 2}

    graph.nodes[1]["status"] = "completed"
    assert calculate_overload_associations(graph) == {1: 0, 2: 0, 3: 1}


def test_overload_rejects_cyclic_dependencies():
    graph = nx.DiGraph([(1, 2), (2, 1)])

    try:
        calculate_overload_associations(graph)
    except ValueError as exc:
        assert "cyclic dependency graph" in str(exc)
    else:
        raise AssertionError("Cyclic dependencies must not receive an overload score.")


def test_dependency_graph_reports_unsupported_mood():
    session = TestSession()
    session.add(
        Task(
            student_id=2,
            title="Task with unrecognized mood",
            task_type=TaskType.OTHER,
            importance="Low",
            deadline=datetime.utcnow(),
            mood="unknown",
        )
    )
    session.commit()
    session.close()

    response = client.get("/students/2/dependency-graph")
    assert response.status_code == 422
    assert "Unsupported mood" in response.json()["detail"]
