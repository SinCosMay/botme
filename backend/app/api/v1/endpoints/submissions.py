from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.models.problem import Problem
from app.schemas.leetcode import LeetCodeSolvedRequest
from app.schemas.submission import SubmissionResultResponse, SubmissionVerifyRequest
from app.services.assignment_service import get_active_assignment_for_platform, get_user_by_discord_id
from app.services.codeforces_service import verify_codeforces_assignment
from app.services.followup_service import get_or_create_followup_question
from app.services.verification_service import record_codeforces_solve, record_leetcode_solve

router = APIRouter()


@router.post("/verify", response_model=SubmissionResultResponse)
async def verify_codeforces_submission(
    payload: SubmissionVerifyRequest,
    db: Session = Depends(get_db_session),
) -> SubmissionResultResponse:
    user = get_user_by_discord_id(db, payload.discord_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    active = get_active_assignment_for_platform(db, user_id=user.id, platform="codeforces")
    if active is None:
        raise HTTPException(status_code=404, detail="No active Codeforces assignment")

    assignment, problem = active
    if problem.cf_contest_id is None or not problem.cf_index:
        raise HTTPException(status_code=400, detail="Assigned problem does not contain CF identifiers")

    verified, submission_id = await verify_codeforces_assignment(
        cf_handle=user.cf_handle,
        contest_id=problem.cf_contest_id,
        index=problem.cf_index,
        assigned_at=assignment.assigned_at,
    )
    if not verified or submission_id is None:
        return SubmissionResultResponse(
            status="not_verified",
            message="No accepted submission found after assignment time",
        )

    submission, xp_awarded, rating_delta = record_codeforces_solve(
        db,
        user=user,
        problem_id=problem.id,
        rating=problem.rating,
        cf_submission_id=submission_id,
    )

    assignment.status = "solved"
    db.commit()

    followup_question = get_or_create_followup_question(db, problem=problem)
    db.commit()

    return SubmissionResultResponse(
        status="verified",
        submission_id=submission.id,
        xp_awarded=xp_awarded,
        rating_delta=rating_delta,
        message="Codeforces solve verified",
        followup_question_id=followup_question.id,
        followup_prompt=followup_question.prompt,
    )


@router.post("/leetcode/mark-solved", response_model=SubmissionResultResponse)
def mark_leetcode_solved(
    payload: LeetCodeSolvedRequest,
    db: Session = Depends(get_db_session),
) -> SubmissionResultResponse:
    user = get_user_by_discord_id(db, payload.discord_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    problem = (
        db.query(Problem)
        .filter(Problem.platform == "leetcode", Problem.lc_slug == payload.slug)
        .one_or_none()
    )
    if problem is None:
        raise HTTPException(status_code=404, detail="LeetCode problem not found")

    submission, created = record_leetcode_solve(
        db,
        user=user,
        problem_id=problem.id,
        proof_url=payload.proof_url,
    )

    active = get_active_assignment_for_platform(db, user_id=user.id, platform="leetcode")
    if active is not None and active[1].id == problem.id:
        active[0].status = "solved"
        db.commit()

    return SubmissionResultResponse(
        status="recorded" if created else "duplicate",
        submission_id=submission.id,
        xp_awarded=0,
        rating_delta=0,
        message="LeetCode solve tracked without Codeforces rating/XP changes",
    )
