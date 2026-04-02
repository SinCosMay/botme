from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.leetcode import LeetCodeAssignRequest, LeetCodeImportRequest, LeetCodeImportResponse
from app.schemas.problem import AssignedProblemResponse
from app.services.assignment_service import assign_leetcode_problem, get_user_by_discord_id
from app.services.leetcode_service import import_leetcode_problems

router = APIRouter()


@router.post("/import/company-problems", response_model=LeetCodeImportResponse)
def import_company_problems(
    payload: LeetCodeImportRequest,
    db: Session = Depends(get_db_session),
) -> LeetCodeImportResponse:
    inserted, updated = import_leetcode_problems(
        db,
        [item.model_dump() for item in payload.problems],
    )
    return LeetCodeImportResponse(inserted=inserted, updated=updated)


@router.post("/assign", response_model=AssignedProblemResponse)
def assign_leetcode(
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

    return AssignedProblemResponse(
        assignment_id=assignment.id,
        problem_id=problem.id,
        platform=problem.platform,
        name=problem.name,
        url=problem.url,
        rating=problem.rating,
        tags=list(problem.tags or []),
    )
