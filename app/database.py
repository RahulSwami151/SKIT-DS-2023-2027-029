"""
database.py
------------
User Story: Dependency Detection
Week 2 — database connection setup.

Creates the SQLAlchemy engine + session used to persist Task and
TaskDependency rows. Uses SQLite locally for development/testing
(zero setup), but the connection string is the ONLY thing that needs
to change to point this at the real PostgreSQL database in
production (per our tech stack: PostgreSQL).

Example for production:
    DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/tim_db"
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Local/dev default — swap this for the real PostgreSQL URL when deploying.
DATABASE_URL = "sqlite:///./tim_dev.db"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    """Create all tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Yield a new database session (use as a context manager)."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()