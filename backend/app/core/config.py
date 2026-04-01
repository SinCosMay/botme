from pathlib import Path
from random import random
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"


class Settings(BaseSettings):
    DATABASE_URL: str | None = None
    REDIS_URL: str = "redis://localhost:6379"
    DISCORD_TOKEN: str = ""
    API_URL: str = "http://localhost:8000"
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False
    LOG_SAMPLE_RATE: float = 1.0
    METRICS_PATH_BUCKET_LIMIT: int = 50

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "change_me"
    POSTGRES_DB: str = "botme"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    CODEFORCES_API_BASE: str = "https://codeforces.com/api"
    CODEFORCES_VERIFY_HANDLES: bool = False
    CODEFORCES_SYNC_LIMIT: int = 2000
    ENABLE_SCHEDULER: bool = False
    SCHEDULER_CACHE_WARM_MINUTES: int = 10
    SCHEDULER_CF_SYNC_HOURS: int = 6
    SCHEDULER_LEADERBOARD_PAGES: int = 2
    SCHEDULER_LEADERBOARD_LIMIT: int = 10
    SCHEDULER_TIMESERIES_DAYS: int = 30
    SCHEDULER_TIMESERIES_TOP_USERS: int = 5
    SCHEDULER_ENABLE_CF_SYNC: bool = False

    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql://{user}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
