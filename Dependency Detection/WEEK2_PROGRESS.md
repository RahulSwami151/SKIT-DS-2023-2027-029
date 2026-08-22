# Week 2 Progress — User Story: Dependency Detection

**Sprint:** Dependency Graph Development & SOR Recommendation Engine
**Owner:** Rahul Swami (Team Lead)
**Period:** 30/8/26 – 5/9/26 (Week 2 of User Story 1)
**Progress this week:** ~40% (Cumulative: ~70%)

## What was done this week

1. **Database connection (`app/database.py`)**
   Set up the SQLAlchemy engine and session so tasks/dependencies can actually be saved, not just modeled. Uses SQLite for local development (zero setup) with a single connection-string change needed to point it at our real PostgreSQL database.

2. **Persistence layer (`app/persistence.py`)**
   Connects Week 1's detection logic to the database:
   - Fetches a student's tasks from the DB
   - Runs the dependency detector on them
   - Saves any *new* dependency links, skipping duplicates on repeat runs

## Not yet done (planned for remaining weeks)
- FastAPI endpoint to expose graph data to the frontend
- Frontend rendering of the graph (React + graph visualization library)
- Switching from SQLite (dev) to PostgreSQL (production)

## How to run
```bash
pip install -r requirements.txt
pytest backend/tests/ -v
```
