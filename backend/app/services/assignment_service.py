import random

from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User


def get_user_by_discord_id(db: Session, discord_id: str) -> User | None:
    return db.query(User).filter(User.discord_id == discord_id).one_or_none()


def assign_codeforces_problem(
    db: Session,
    *,
    user: User,
    mode: str,
    tag: str | None,
    min_rating: int | None,
    max_rating: int | None,
) -> tuple[Assignment, Problem]:
    mode = (mode or "random").strip().lower()
    solved_problem_ids = {
        s.problem_id
        for s in db.query(Submission)
        .filter(Submission.user_id == user.id, Submission.platform == "codeforces")
        .all()
    }

    query = db.query(Problem).filter(Problem.platform == "codeforces")
    if min_rating is not None:
        query = query.filter(Problem.rating >= min_rating)
    if max_rating is not None:
        query = query.filter(Problem.rating <= max_rating)

    normalized_tag: str | None = None
    if tag:
        normalized_tag = tag.strip().lower()

    if mode == "topic" and not normalized_tag:
        raise ValueError("Topic mode requires a tag")

    candidates = [p for p in query.all() if p.id not in solved_problem_ids]

    if normalized_tag:
        candidates = [
            p
            for p in candidates
            if normalized_tag in [str(t).strip().lower() for t in (p.tags or [])]
        ]

    if not candidates:
        raise ValueError("No matching Codeforces problems available")

    problem = random.choice(candidates)

    assignment = Assignment(user_id=user.id, problem_id=problem.id, status="assigned")
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment, problem


def assign_leetcode_problem(
    db: Session,
    *,
    user: User,
    company: str,
    difficulty: str | None,
) -> tuple[Assignment, Problem]:
    solved_problem_ids = {
        s.problem_id
        for s in db.query(Submission)
        .filter(Submission.user_id == user.id, Submission.platform == "leetcode")
        .all()
    }

    normalized_company = company.strip().lower()
    difficulty_key = f"difficulty:{difficulty.strip().lower()}" if difficulty else None

    candidates = []
    for problem in db.query(Problem).filter(Problem.platform == "leetcode").all():
        companies = [str(c).strip().lower() for c in (problem.companies or [])]
        if normalized_company not in companies:
            continue
        if difficulty_key and difficulty_key not in [str(t).strip().lower() for t in (problem.tags or [])]:
            continue
        if problem.id in solved_problem_ids:
            continue
        candidates.append(problem)

    if not candidates:
        raise ValueError("No matching LeetCode problems available")

    problem = random.choice(candidates)

    assignment = Assignment(user_id=user.id, problem_id=problem.id, status="assigned")
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment, problem


def get_active_assignment_for_platform(db: Session, *, user_id: str, platform: str) -> tuple[Assignment, Problem] | None:
    assignment = (
        db.query(Assignment)
        .join(Problem, Problem.id == Assignment.problem_id)
        .filter(Assignment.user_id == user_id, Assignment.status == "assigned", Problem.platform == platform)
        .order_by(Assignment.assigned_at.desc())
        .first()
    )

    if assignment is None:
        return None

    problem = db.query(Problem).filter(Problem.id == assignment.problem_id).one()
    return assignment, problem
