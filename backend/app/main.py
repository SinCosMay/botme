from contextlib import asynccontextmanager
import logging
import time
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.jobs.scheduler import start_scheduler, stop_scheduler

configure_logging()
logger = logging.getLogger(__name__)
WEB_DIR = Path(__file__).resolve().parent / "web"

@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.ENABLE_SCHEDULER:
        start_scheduler()
    try:
        yield
    finally:
        if settings.ENABLE_SCHEDULER:
            stop_scheduler()


app = FastAPI(title="BotMe API", version="0.1.0", lifespan=lifespan)
app.include_router(v1_router, prefix="/v1")
app.mount("/dashboard/static", StaticFiles(directory=str(WEB_DIR)), name="dashboard-static")


@app.middleware("http")
async def request_tracing_middleware(request, call_next):
    request_id = str(uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "botme-backend"}


@app.get("/dashboard")
def dashboard_home() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/dashboard/leaderboard")
def dashboard_leaderboard() -> FileResponse:
    return FileResponse(WEB_DIR / "leaderboard.html")


@app.get("/dashboard/profile")
def dashboard_profile() -> FileResponse:
    return FileResponse(WEB_DIR / "profile.html")
