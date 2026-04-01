from fastapi import FastAPI

from app.api.v1.router import router as v1_router

app = FastAPI(title="BotMe API", version="0.1.0")
app.include_router(v1_router, prefix="/v1")


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "botme-backend"}
