from typing import Literal

from pydantic import BaseModel, Field


class ProblemAssignRequest(BaseModel):
    discord_id: str
    mode: Literal["random", "topic", "rating"] = "random"
    tag: str | None = None
    min_rating: int | None = None
    max_rating: int | None = None


class AssignedProblemResponse(BaseModel):
    assignment_id: str
    problem_id: str
    platform: str
    name: str
    url: str
    rating: int | None
    tags: list[str] = Field(default_factory=list)
