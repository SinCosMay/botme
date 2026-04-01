from pydantic import BaseModel


class PlatformAnalyticsResponse(BaseModel):
    user_id: str
    platform: str
    solved_count: int
    xp: int
    rating: int | None
    streak: int
