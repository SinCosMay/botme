from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    DISCORD_TOKEN: str = ""
    API_URL: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = BotSettings()
