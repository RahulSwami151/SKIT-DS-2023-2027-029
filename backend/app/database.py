"""Database connection and session management."""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from .models import Base

DATABASE_URL = "sqlite:///./tim_dev.db"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# SQLite does NOT enforce foreign keys (e.g. ON DELETE CASCADE, the
# student_id -> users.id and task_id/prerequisite_task_id -> tasks.id
# relationships) unless explicitly turned on per connection. Without this,
# things like cascading deletes or FK constraint checks silently do nothing
# in local dev, even though they work correctly in production Postgres.
@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()