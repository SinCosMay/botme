from pydantic import BaseModel, Field


class FollowupAnswerRequest(BaseModel):
    submission_id: str
    question_id: str
    answer: str = Field(min_length=1, max_length=2000)


class FollowupAnswerResponse(BaseModel):
    is_correct: bool
    awarded_xp: int
    user_xp: int
    user_level: int
    message: str
