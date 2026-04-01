from pydantic import BaseModel


class SubmissionVerifyRequest(BaseModel):
    discord_id: str


class SubmissionResultResponse(BaseModel):
    status: str
    submission_id: str | None = None
    xp_awarded: int = 0
    rating_delta: int = 0
    message: str
    followup_question_id: str | None = None
    followup_prompt: str | None = None
