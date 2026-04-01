from sqlalchemy.orm import Session

from app.models.followup_attempt import FollowupAttempt
from app.models.followup_question import FollowupQuestion
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.models.xp_history import XpHistory
from app.services.progress_service import recompute_level


def _normalized_words(value: str) -> list[str]:
    return [token.strip().lower() for token in value.split() if token.strip()]


def get_or_create_followup_question(db: Session, *, problem: Problem) -> FollowupQuestion:
    existing = db.query(FollowupQuestion).filter(FollowupQuestion.problem_id == problem.id).first()
    if existing is not None:
        return existing

    tags = [str(tag).strip().lower() for tag in (problem.tags or [])]
    if tags:
        key_topic = tags[0]
        prompt = (
            f"In one line, explain the core idea used in {problem.name}. "
            f"Mention this concept explicitly: {key_topic}."
        )
        expected_answer = {"keywords": [key_topic]}
        question_type = "key_idea"
    else:
        prompt = (
            f"What is the typical time complexity approach for solving {problem.name}? "
            "Use Big-O notation."
        )
        expected_answer = {"keywords": ["o("]}
        question_type = "complexity"

    question = FollowupQuestion(
        problem_id=problem.id,
        question_type=question_type,
        prompt=prompt,
        expected_answer=expected_answer,
        bonus_xp=10,
    )
    db.add(question)
    db.flush()
    return question


def answer_followup(
    db: Session,
    *,
    user: User,
    submission: Submission,
    question: FollowupQuestion,
    answer: str,
) -> tuple[FollowupAttempt, int]:
    existing_attempt = (
        db.query(FollowupAttempt)
        .filter(FollowupAttempt.submission_id == submission.id)
        .order_by(FollowupAttempt.attempted_at.desc())
        .first()
    )
    if existing_attempt is not None:
        return existing_attempt, 0

    keywords = [str(k).strip().lower() for k in (question.expected_answer or {}).get("keywords", [])]
    answer_words = _normalized_words(answer)
    normalized_answer = " ".join(answer_words)

    is_correct = bool(keywords) and all(keyword in normalized_answer for keyword in keywords)
    awarded_xp = question.bonus_xp if is_correct else 0

    attempt = FollowupAttempt(
        submission_id=submission.id,
        question_id=question.id,
        user_answer=answer,
        is_correct=is_correct,
        awarded_xp=awarded_xp,
    )
    db.add(attempt)

    if awarded_xp > 0:
        user.xp += awarded_xp
        user.level = recompute_level(user.xp)
        submission.bonus_xp_awarded += awarded_xp
        db.add(
            XpHistory(
                user_id=user.id,
                amount=awarded_xp,
                source="followup_bonus",
                metadata_json={
                    "submission_id": submission.id,
                    "question_id": question.id,
                },
            )
        )

    db.commit()
    db.refresh(attempt)
    return attempt, awarded_xp
