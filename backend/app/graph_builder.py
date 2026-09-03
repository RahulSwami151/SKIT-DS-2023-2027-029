"""Build dependency graph data for the frontend."""

from typing import Any, Dict

import networkx as nx
from sqlalchemy.orm import Session

from .models import Task, TaskDependency


def build_dependency_graph(session: Session, student_id: int) -> nx.DiGraph:
    graph = nx.DiGraph()
    tasks = session.query(Task).filter(Task.student_id == student_id).all()
    task_ids = {task.id for task in tasks}

    for task in tasks:
        graph.add_node(
            task.id,
            title=task.title,
            task_type=task.task_type.value,
            subject=task.subject,
        )

    dependencies = (
        session.query(TaskDependency)
        .filter(TaskDependency.task_id.in_(task_ids))
        .all()
        if task_ids
        else []
    )
    for dependency in dependencies:
        if dependency.prerequisite_task_id in task_ids:
            graph.add_edge(
                dependency.task_id,
                dependency.prerequisite_task_id,
                reason=dependency.reason,
            )

    return graph


def export_graph_for_frontend(graph: nx.DiGraph) -> Dict[str, Any]:
    return {
        "nodes": [
            {"id": node_id, **attributes}
            for node_id, attributes in graph.nodes(data=True)
        ],
        "edges": [
            {"source": source, "target": target, **attributes}
            for source, target, attributes in graph.edges(data=True)
        ],
    }
