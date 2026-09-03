"""
api.py
--------
User Story: Dependency Detection
Week 3 (final 30%) — FastAPI endpoints exposing dependency detection
and graph data to the frontend.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_session
from .persistence import detect_and_persist_dependencies
from .graph_builder import build_dependency_graph, export_graph_for_frontend

router = APIRouter(prefix="/students/{student_id}", tags=["dependencies"])


@router.post("/detect-dependencies")
def detect_dependencies_endpoint(student_id: int, session: Session = Depends(get_session)):
    """Runs detection over the student's tasks and persists new dependencies."""
    created = detect_and_persist_dependencies(session, student_id)
    return {"new_dependencies_created": len(created)}


@router.get("/dependency-graph")
def get_dependency_graph_endpoint(student_id: int, session: Session = Depends(get_session)):
    """Returns the student's dependency graph as {nodes, edges} for the frontend."""
    graph = build_dependency_graph(session, student_id)
    return export_graph_for_frontend(graph)