from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.jobs.scheduler import start_scheduler, stop_scheduler

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


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "botme-backend"}
