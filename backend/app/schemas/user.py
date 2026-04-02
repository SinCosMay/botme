from pydantic import BaseModel, ConfigDict, Field


class UserRegisterRequest(BaseModel):
    discord_id: str = Field(min_length=2, max_length=64)
    cf_handle: str = Field(min_length=2, max_length=64)


class UserProfileResponse(BaseModel):
    id: str
    discord_id: str
    cf_handle: str
    xp: int
    rating: int
    level: int
    current_streak: int
    longest_streak: int

    model_config = ConfigDict(from_attributes=True)
