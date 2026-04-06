from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    DISCORD_TOKEN: str = ""
    API_URL: str = "http://localhost:8000"
    DISCORD_GUILD_ID: int | None = 740102523716763668
    DISCORD_SYNC_GUILD_ONLY: bool = True
    DISCORD_CLEAR_GLOBAL_WHEN_GUILD_SYNC: bool = True
    LEETCODE_COMPANY_REPO: str = "liquidslr/interview-company-wise-problems"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = BotSettings()
