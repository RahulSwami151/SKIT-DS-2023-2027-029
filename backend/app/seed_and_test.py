"""
TIM — Seed data + constraint verification script.
Matches the MERGED models.py (Rahul's Task/TaskDependency column names preserved:
student_id, prerequisite_task_id, reason).

Run this after the merged models.py is in place, to (1) populate sample data
and (2) prove the CHECK/UNIQUE constraints actually reject bad data.

Usage:
    python seed_and_test.py
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from models import Base, User, Task, TaskDependency, JournalEntry, TaskType

DATABASE_URL = "sqlite:///./tim_dev.db"
engine = create_engine(DATABASE_URL, echo=False, future=True)
Session = sessionmaker(bind=engine)


def seed():
    # Start fresh every run — drop any existing tables from a previous test run
    # before recreating them, so this script is safe to re-run any number of times.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = Session()

    # ---- Users ----
    alice = User(name="Alice Verma", email="alice@example.com", password_hash="hashed_pw_1")
    bob = User(name="Bob Iyer", email="bob@example.com", password_hash="hashed_pw_2")
    session.add_all([alice, bob])
    session.commit()

    now = datetime.now(timezone.utc)

    # ---- Tasks (5-6 realistic ones for Alice) ----
    t1 = Task(student_id=alice.id, title="Finish DBMS assignment", deadline=now + timedelta(days=1),
              subject="DBMS", task_type=TaskType.ASSIGNMENT, priority=5, importance=5,
              mood="stressed", status="pending")
    t2 = Task(student_id=alice.id, title="Read DBMS Chapter 4", deadline=now + timedelta(hours=20),
              subject="DBMS", task_type=TaskType.READING, priority=4, importance=3,
              mood="okay", status="pending")
    t3 = Task(student_id=alice.id, title="Prepare project ppt", deadline=now + timedelta(days=3),
              subject="Project", task_type=TaskType.PROJECT, priority=3, importance=4,
              mood="tired", status="pending")
    t4 = Task(student_id=alice.id, title="Submit project abstract", deadline=now + timedelta(days=2),
              subject="Project", task_type=TaskType.ASSIGNMENT, priority=4, importance=5,
              mood="okay", status="in_progress")
    t5 = Task(student_id=alice.id, title="Gym", deadline=now + timedelta(days=1),
              subject="Personal", task_type=TaskType.OTHER, priority=1, importance=2,
              mood="good", status="pending")
    session.add_all([t1, t2, t3, t4, t5])
    session.commit()

    # ---- Dependencies (matches Rahul's column names) ----
    session.add_all([
        TaskDependency(task_id=t1.id, prerequisite_task_id=t2.id,
                        reason="reading precedes assignment in same subject"),
        TaskDependency(task_id=t3.id, prerequisite_task_id=t4.id,
                        reason="ppt depends on abstract being finalized first"),
    ])
    session.commit()

    # ---- Journal entries ----
    session.add_all([
        JournalEntry(user_id=alice.id, mood_rating=2, stress_level=4, energy_level=2,
                     note="Feeling behind on DBMS stuff."),
        JournalEntry(user_id=bob.id, mood_rating=4, stress_level=2, energy_level=4,
                     note=None),
    ])
    session.commit()
    session.close()
    print("Seed data inserted: 2 users, 5 tasks, 2 dependencies, 2 journal entries.")


def test_constraints():
    session = Session()
    alice = session.query(User).filter_by(email="alice@example.com").first()
    tasks = session.query(Task).filter_by(student_id=alice.id).all()
    t1, t2 = tasks[0], tasks[1]

    # 1. priority out of range should fail
    try:
        bad = Task(student_id=alice.id, title="Bad priority task", deadline=datetime.now(timezone.utc),
                   task_type=TaskType.OTHER, priority=9, importance=3, status="pending")
        session.add(bad)
        session.commit()
        print("FAIL: priority=9 was accepted (should have been rejected)")
    except IntegrityError:
        session.rollback()
        print("PASS: priority CHECK constraint correctly rejected priority=9")

    # 2. duplicate dependency pair should fail
    try:
        dup = TaskDependency(task_id=t1.id, prerequisite_task_id=t2.id, reason="duplicate test")
        session.add(dup)
        session.commit()
        print("FAIL: duplicate dependency pair was accepted (should have been rejected)")
    except IntegrityError:
        session.rollback()
        print("PASS: UNIQUE constraint correctly rejected duplicate dependency pair")

    # 3. task depending on itself should fail
    try:
        self_dep = TaskDependency(task_id=t1.id, prerequisite_task_id=t1.id, reason="self test")
        session.add(self_dep)
        session.commit()
        print("FAIL: self-dependency was accepted (should have been rejected)")
    except IntegrityError:
        session.rollback()
        print("PASS: CHECK constraint correctly rejected task depending on itself")

    session.close()


if __name__ == "__main__":
    seed()
    test_constraints()