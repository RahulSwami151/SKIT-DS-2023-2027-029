"""
graph_builder.py
------------------
User Story: Dependency Detection
Week 2 — build the dependency GRAPH using NetworkX (per tech stack)
from a student's tasks + persisted dependencies, and export it in a
simple node/edge format the frontend (React) can render.
"""

from typing import Dict, List
import networkx as nx
from sqlalchemy.orm import Session

from .models import Task, TaskDependency


def build_dependency_graph(session: Session, student_id: int) -> nx.DiGraph:
    """
    Builds a directed graph where an edge (A -> B) means
    "A is a prerequisite of B" (i.e. A must be done before B).
    """
    graph = nx.DiGraph()

    tasks = session.query(Task).filter(Task.student_id == student_id).all()
    task_ids = {t.id for t in tasks}

    for task in tasks:
        graph.add_node(
            task.id,
            title=task.title,
            task_type=task.task_type.value,
            subject=task.subject,
            deadline=task.deadline.isoformat() if task.deadline else None,
        )

    dependencies = (
        session.query(TaskDependency)
        .filter(TaskDependency.task_id.in_(task_ids))
        .all()
    )
    for dep in dependencies:
        # edge direction: prerequisite -> dependent task
        graph.add_edge(dep.prerequisite_task_id, dep.task_id, reason=dep.reason)

    return graph


def export_graph_for_frontend(graph: nx.DiGraph) -> Dict[str, List[dict]]:
    """
    Converts the NetworkX graph into a plain {nodes, edges} dict,
    ready to be returned as JSON from a FastAPI endpoint and consumed
    by the React dependency-graph visualization.
    """
    nodes = [
        {"id": node_id, **attrs}
        for node_id, attrs in graph.nodes(data=True)
    ]
    edges = [
        {"source": u, "target": v, "reason": attrs.get("reason")}
        for u, v, attrs in graph.edges(data=True)
    ]
    return {"nodes": nodes, "edges": edges}


def get_task_prerequisites(graph: nx.DiGraph, task_id: int) -> List[int]:
    """Returns the direct prerequisite task IDs for a given task."""
    return list(graph.predecessors(task_id))


def has_circular_dependency(graph: nx.DiGraph) -> bool:
    """
    Sanity check: a valid task dependency graph should have NO cycles
    (a task can't depend on itself, even indirectly).
    """
    return not nx.is_directed_acyclic_graph(graph)
