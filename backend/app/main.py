"""
main.py
---------
FastAPI app entrypoint. Run with: uvicorn backend.app.main:app --reload
"""

from fastapi import FastAPI

from .database import init_db
from .api import router

app = FastAPI(title="TIM - Dependency Detection Service")
app.include_router(router)


@app.on_event("startup")
def on_startup():
    init_db()