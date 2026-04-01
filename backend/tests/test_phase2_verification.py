from datetime import datetime, timedelta, timezone

from app.main import app
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.services.verification_service import record_codeforces_solve


def test_phase2_codeforces_solve_updates_profile_and_streak(client):
    db = app.state.testing_session_local()
    try:
        user = User(
            discord_id="phase2_u1",
            cf_handle="tourist_phase2",
            xp=0,
            rating=1000,
            level=1,
            current_streak=3,
            longest_streak=4,
            last_solved_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        problem = Problem(
            platform="codeforces",
            cf_contest_id=1000,
            cf_index="B",
            name="CF B",
            rating=1200,
            tags=["math"],
            url="https://codeforces.com/problemset/problem/1000/B",
        )
        db.add_all([user, problem])
        db.commit()
        db.refresh(user)
        db.refresh(problem)

        submission, xp_awarded, rating_delta = record_codeforces_solve(
            db,
            user=user,
            problem_id=problem.id,
            rating=problem.rating,
            cf_submission_id="9001",
        )

        assert submission.platform == "codeforces"
        assert xp_awarded > 0
        assert rating_delta != 0

        db.refresh(user)
        assert user.current_streak == 4
        assert user.longest_streak == 4
        assert user.level >= 1
    finally:
        db.close()


def test_phase2_duplicate_codeforces_solve_is_idempotent(client):
    db = app.state.testing_session_local()
    try:
        user = User(discord_id="phase2_u2", cf_handle="petr_phase2")
        problem = Problem(
            platform="codeforces",
            cf_contest_id=1000,
            cf_index="C",
            name="CF C",
            rating=800,
            tags=["implementation"],
            url="https://codeforces.com/problemset/problem/1000/C",
        )
        db.add_all([user, problem])
        db.commit()
        db.refresh(user)
        db.refresh(problem)

        first_submission, first_xp, _ = record_codeforces_solve(
            db,
            user=user,
            problem_id=problem.id,
            rating=problem.rating,
            cf_submission_id="9002",
        )
        second_submission, second_xp, second_delta = record_codeforces_solve(
            db,
            user=user,
            problem_id=problem.id,
            rating=problem.rating,
            cf_submission_id="9003",
        )

        assert first_submission.id == second_submission.id
        assert first_xp > 0
        assert second_xp == 0
        assert second_delta == 0

        submissions_count = db.query(Submission).filter(Submission.user_id == user.id).count()
        assert submissions_count == 1
    finally:
        db.close()
