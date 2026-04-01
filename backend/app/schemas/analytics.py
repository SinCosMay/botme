from pydantic import BaseModel


class PlatformAnalyticsResponse(BaseModel):
    user_id: str
    platform: str
    solved_count: int
    xp: int
    rating: int | None
    streak: int


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    discord_id: str
    cf_handle: str
    xp: int
    rating: int
    level: int


class LeaderboardResponse(BaseModel):
    metric: str
    page: int
    limit: int
    total: int
    entries: list[LeaderboardEntry]


class TimeSeriesPoint(BaseModel):
    day: str
    value: int


class UserTimeSeriesResponse(BaseModel):
    user_id: str
    metric: str
    days: int
    points: list[TimeSeriesPoint]
