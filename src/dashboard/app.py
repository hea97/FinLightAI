from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
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


@app.get("/auth/kakao/start")
def kakao_auth_start() -> RedirectResponse:
    return RedirectResponse("/auth/kakao/callback?state=kakao_connected_existing_user", status_code=302)


@app.get("/auth/kakao/callback")
def kakao_auth_callback(state: str = "kakao_connected_existing_user") -> RedirectResponse:
    return RedirectResponse(f"/?auth={state}", status_code=302)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
