from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.dashboard.routes.api import router as api_router

app = FastAPI(title="FinLightAI", version="0.1.0")
app.include_router(api_router, prefix="/api")
app.mount("/static", StaticFiles(directory="src/dashboard/static"), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse("src/dashboard/static/index.html")


@app.get("/login")
def login() -> FileResponse:
    return FileResponse("src/dashboard/static/login.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
