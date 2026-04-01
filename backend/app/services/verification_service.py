from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.submission import Submission
from app.models.user import User
from app.models.user_platform_stat import UserPlatformStat
from app.services.progress_service import base_xp_for_rating, codeforces_rating_delta, recompute_level


def _get_or_create_stat(db: Session, user_id: str, platform: str) -> UserPlatformStat:
    stat = (
        db.query(UserPlatformStat)
        .filter(UserPlatformStat.user_id == user_id, UserPlatformStat.platform == platform)
        .one_or_none()
    )
    if stat is None:
        stat = UserPlatformStat(user_id=user_id, platform=platform)
        db.add(stat)
        db.flush()
    return stat


def _next_streak(last_solved_at: datetime | None, current_streak: int, now: datetime) -> int:
    if last_solved_at is None:
        return 1

    previous_day = last_solved_at.astimezone(timezone.utc).date()
    today = now.astimezone(timezone.utc).date()
    day_gap = (today - previous_day).days

    if day_gap <= 0:
        return max(1, current_streak)
    if day_gap == 1:
        return max(1, current_streak) + 1
    return 1


def record_codeforces_solve(
    db: Session,
    *,
    user: User,
    problem_id: str,
    rating: int | None,
    cf_submission_id: str,
) -> tuple[Submission, int, int]:
    duplicate = (
        db.query(Submission)
        .filter(Submission.user_id == user.id, Submission.problem_id == problem_id)
        .one_or_none()
    )
    if duplicate:
        return duplicate, 0, 0

    xp_awarded = base_xp_for_rating(rating)
    rating_delta = codeforces_rating_delta(rating, user.rating)

    now = datetime.now(timezone.utc)

    submission = Submission(
        user_id=user.id,
        problem_id=problem_id,
        platform="codeforces",
        cf_submission_id=cf_submission_id,
        verdict="OK",
        xp_awarded=xp_awarded,
        solved_at=now,
    )
    db.add(submission)

    user.current_streak = _next_streak(user.last_solved_at, user.current_streak, now)
    user.longest_streak = max(user.longest_streak, user.current_streak)
    user.xp += xp_awarded
    user.rating += rating_delta
    user.level = recompute_level(user.xp)
    user.last_solved_at = now

    stat = _get_or_create_stat(db, user.id, "codeforces")
    stat.streak = _next_streak(stat.last_solved_at, stat.streak, now)
    stat.solved_count += 1
    stat.xp += xp_awarded
    stat.rating = user.rating
    stat.last_solved_at = now

    db.commit()
    db.refresh(submission)
    return submission, xp_awarded, rating_delta


def record_leetcode_solve(
    db: Session,
    *,
    user: User,
    problem_id: str,
    proof_url: str | None,
) -> tuple[Submission, bool]:
    duplicate = (
        db.query(Submission)
        .filter(Submission.user_id == user.id, Submission.problem_id == problem_id)
        .one_or_none()
    )
    if duplicate:
        return duplicate, False

    now = datetime.now(timezone.utc)

    submission = Submission(
        user_id=user.id,
        problem_id=problem_id,
        platform="leetcode",
        proof_url=proof_url,
        verdict="SELF_REPORTED",
        xp_awarded=0,
        solved_at=now,
    )
    db.add(submission)

    stat = _get_or_create_stat(db, user.id, "leetcode")
    stat.streak = _next_streak(stat.last_solved_at, stat.streak, now)
    stat.solved_count += 1
    stat.last_solved_at = now

    db.commit()
    db.refresh(submission)
    return submission, True
