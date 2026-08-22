# Week 1 Progress — User Story: Dependency Detection

**Sprint:** Dependency Graph Development & SOR Recommendation Engine
**Owner:** Rahul Swami (Team Lead)
**Period:** 23/8/26 – 29/8/26
**Progress:** ~30%

## What was done this week

1. **Data model (`app/models.py`)**
   Defined the initial SQLAlchemy models:
   - `Task` — a student's task with type (reading/assignment/quiz/project/exam), subject, and deadline.
   - `TaskDependency` — a directed edge storing that one task is a prerequisite of another, with a `reason` field for traceability.

2. **Dependency detection logic (`app/dependency_detector.py`)**
   Implemented a first-pass **rule-based** detector that identifies prerequisite relationships between academic tasks using three heuristics:
   - Same subject/course (avoids false positives across unrelated tasks)
   - Task-type precedence (e.g. reading → assignment → quiz/project → exam)
   - Deadline ordering (a prerequisite can't be due after the dependent task)

3. **Tests (`tests/test_dependency_detector.py`)**
   4 unit tests verifying correct detection and correct rejection of invalid dependencies (different subjects, wrong deadline order, multi-prerequisite case). All passing.

## Not yet done (planned for Week 2)
- Persisting detected dependencies to the database
- Building the actual dependency **graph** structure using NetworkX
- API endpoint to trigger detection for a student's task list
- Graph visualization data export for the frontend

## How to run
```bash
pip install sqlalchemy pytest
pytest backend/tests/test_dependency_detector.py -v
```
