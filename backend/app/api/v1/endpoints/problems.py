from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.leetcode import LeetCodeAssignRequest
from app.schemas.problem import AssignedProblemResponse, ProblemAssignRequest
from app.services.assignment_service import (
    assign_codeforces_problem,
    assign_leetcode_problem,
    get_user_by_discord_id,
)
from app.services.codeforces_service import sync_problemset

router = APIRouter()


def _as_response(assignment_id: str, problem) -> AssignedProblemResponse:
    return AssignedProblemResponse(
        assignment_id=assignment_id,
        problem_id=problem.id,
        platform=problem.platform,
        name=problem.name,
        url=problem.url,
        rating=problem.rating,
        tags=list(problem.tags or []),
    )


@router.post("/assign", response_model=AssignedProblemResponse)
def assign_problem(payload: ProblemAssignRequest, db: Session = Depends(get_db_session)) -> AssignedProblemResponse:
    user = get_user_by_discord_id(db, payload.discord_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        assignment, problem = assign_codeforces_problem(
            db,
            user=user,
            mode=payload.mode,
            tag=payload.tag,
            min_rating=payload.min_rating,
            max_rating=payload.max_rating,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return _as_response(assignment.id, problem)


@router.post("/assign/leetcode", response_model=AssignedProblemResponse)
def assign_leetcode_via_problems(
    payload: LeetCodeAssignRequest,
    db: Session = Depends(get_db_session),
) -> AssignedProblemResponse:
    user = get_user_by_discord_id(db, payload.discord_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        assignment, problem = assign_leetcode_problem(
            db,
            user=user,
            company=payload.company,
            difficulty=payload.difficulty,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return _as_response(assignment.id, problem)


@router.post("/sync/codeforces")
async def sync_codeforces(limit: int | None = None, db: Session = Depends(get_db_session)) -> dict[str, int]:
    inserted = await sync_problemset(db, limit)
    return {"inserted": inserted}
