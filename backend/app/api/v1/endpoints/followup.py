from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.models.followup_question import FollowupQuestion
from app.models.submission import Submission
from app.models.user import User
from app.schemas.followup import FollowupAnswerRequest, FollowupAnswerResponse
from app.services.followup_service import answer_followup

router = APIRouter()


@router.post("/answer", response_model=FollowupAnswerResponse)
def submit_followup_answer(
    payload: FollowupAnswerRequest,
    db: Session = Depends(get_db_session),
) -> FollowupAnswerResponse:
    submission = db.query(Submission).filter(Submission.id == payload.submission_id).one_or_none()
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    user = db.query(User).filter(User.id == submission.user_id).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    question = db.query(FollowupQuestion).filter(FollowupQuestion.id == payload.question_id).one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Follow-up question not found")

    if question.problem_id != submission.problem_id:
        raise HTTPException(status_code=400, detail="Question does not belong to submission problem")

    attempt, awarded_xp = answer_followup(
        db,
        user=user,
        submission=submission,
        question=question,
        answer=payload.answer,
    )

    if awarded_xp > 0:
        message = "Correct answer. Bonus XP awarded."
    elif attempt.is_correct:
        message = "Already answered before. No additional bonus XP."
    else:
        expected_keywords = [
            str(keyword).strip()
            for keyword in (question.expected_answer or {}).get("keywords", [])
            if str(keyword).strip()
        ]
        if expected_keywords:
            message = (
                "Answer recorded. No bonus XP awarded. "
                f"Expected concept keywords: {', '.join(expected_keywords[:3])}."
            )
        else:
            message = "Answer recorded. No bonus XP awarded."

    return FollowupAnswerResponse(
        is_correct=attempt.is_correct,
        awarded_xp=awarded_xp,
        user_xp=user.xp,
        user_level=user.level,
        message=message,
    )
