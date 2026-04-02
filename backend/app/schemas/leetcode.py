from pydantic import BaseModel, Field


class LeetCodeProblemIn(BaseModel):
    slug: str
    name: str
    url: str
    companies: list[str] = Field(default_factory=list)
    difficulty: str | None = None
    tags: list[str] = Field(default_factory=list)
    problem_id: str | None = None


class LeetCodeImportRequest(BaseModel):
    problems: list[LeetCodeProblemIn] = Field(default_factory=list)


class LeetCodeAssignRequest(BaseModel):
    discord_id: str
    company: str
    difficulty: str | None = None


class LeetCodeImportResponse(BaseModel):
    inserted: int
    updated: int


class LeetCodeSolvedRequest(BaseModel):
    discord_id: str
    slug: str
    proof_url: str | None = None
