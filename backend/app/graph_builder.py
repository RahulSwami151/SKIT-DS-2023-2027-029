"""Build dependency graph data for the frontend."""

from typing import Any, Dict, Set

import networkx as nx
from sqlalchemy.orm import Session

from .models import Task, TaskDependency
from .sor_scoring import calculate_sor_score


def calculate_overload_associations(graph: nx.DiGraph) -> Dict[int, int]:
    """Count each task's unique, incomplete prerequisite chain."""
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("Cannot calculate overload for a cyclic dependency graph.")

    prerequisite_first_graph = graph.reverse(copy=False)
    unresolved_prerequisites: Dict[int, Set[int]] = {}
    for task_id in nx.topological_sort(prerequisite_first_graph):
        unresolved: Set[int] = set()
        if graph.nodes[task_id].get("status") != "completed":
            for prerequisite_id in prerequisite_first_graph.predecessors(task_id):
                if graph.nodes[prerequisite_id].get("status") != "completed":
                    unresolved.add(prerequisite_id)
                    unresolved.update(unresolved_prerequisites[prerequisite_id])
        unresolved_prerequisites[task_id] = unresolved

    return {
        task_id: len(prerequisites)
        for task_id, prerequisites in unresolved_prerequisites.items()
    }


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
            deadline=task.deadline,
            status=task.status,
            priority=task.priority,
            importance=task.importance,
            mood=task.mood,
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
    overload_associations = calculate_overload_associations(graph)
    nodes = []
    for node_id, attributes in graph.nodes(data=True):
        score = calculate_sor_score(
            importance=attributes["importance"],
            overload_association=overload_associations[node_id],
            deadline=attributes["deadline"],
            mood=attributes["mood"],
        )
        nodes.append(
            {
                "id": node_id,
                **attributes,
                "structural_impact": score["sor_components"]["structural_impact"],
                **score,
            }
        )

    return {
        "nodes": nodes,
        "edges": [
            {"source": source, "target": target, **attributes}
            for source, target, attributes in graph.edges(data=True)
        ],
    }
