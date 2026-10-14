"""
main.py
---------
FastAPI app entrypoint. Run with: uvicorn backend.app.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .database import init_db
from .api import router

app = FastAPI(title="TIM - Dependency Detection Service")
app.include_router(router)
dashboard_path = Path(__file__).resolve().parents[2] / "frontend" / "task_graph_dashboard.html"


@app.get("/", include_in_schema=False)
@app.get("/dashboard", include_in_schema=False)
def get_dashboard():
    """Serve the task graph dashboard from the application origin."""
    return FileResponse(dashboard_path, media_type="text/html")


@app.on_event("startup")
def on_startup():
    init_db()