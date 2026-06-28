from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from config.settings import get_settings
from src.dashboard.database import create_tables
from src.dashboard.routes.api import router as api_router

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

app = FastAPI(title="FinLightAI", version="0.1.0")
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api")
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="frontend-assets")
app.mount(
    "/static",
    StaticFiles(directory=PROJECT_ROOT / "src" / "dashboard" / "static"),
    name="static",
)
create_tables()


@app.get("/")
def index() -> FileResponse:
    frontend_index = FRONTEND_DIST / "index.html"
    return FileResponse(frontend_index if frontend_index.exists() else PROJECT_ROOT / "src" / "dashboard" / "static" / "index.html")


@app.get("/login")
def login() -> FileResponse:
    frontend_index = FRONTEND_DIST / "index.html"
    return FileResponse(frontend_index if frontend_index.exists() else PROJECT_ROOT / "src" / "dashboard" / "static" / "login.html")


@app.get("/auth/kakao/start")
def kakao_auth_start() -> RedirectResponse:
    return RedirectResponse("/auth/kakao/callback?state=kakao_connected_existing_user", status_code=302)


@app.get("/auth/kakao/callback")
def kakao_auth_callback(state: str = "kakao_connected_existing_user") -> RedirectResponse:
    return RedirectResponse(f"/?auth={state}", status_code=302)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
