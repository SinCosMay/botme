from datetime import datetime, timezone

from app.main import app
from app.models.assignment import Assignment
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User


def _seed_user_problem_assignment(discord_id: str, cf_handle: str) -> tuple[str, str]:
    db = app.state.testing_session_local()
    try:
        user = User(discord_id=discord_id, cf_handle=cf_handle)
        problem = Problem(
            platform="codeforces",
            cf_contest_id=1000,
            cf_index="A",
            name="CF A",
            rating=800,
            tags=["implementation"],
            url="https://codeforces.com/problemset/problem/1000/A",
        )
        db.add_all([user, problem])
        db.flush()

        assignment = Assignment(
            user_id=user.id,
            problem_id=problem.id,
            assigned_at=datetime.now(timezone.utc),
            status="assigned",
        )
        db.add(assignment)
        db.commit()
        return user.id, assignment.id
    finally:
        db.close()


def test_verify_submission_endpoint_marks_assignment_solved(client, monkeypatch):
    user_id, assignment_id = _seed_user_problem_assignment("verify_u1", "tourist_verify_u1")

    async def fake_verify_codeforces_assignment(**kwargs):
        return True, "777777"

    monkeypatch.setattr(
        "app.api.v1.endpoints.submissions.verify_codeforces_assignment",
        fake_verify_codeforces_assignment,
    )

    response = client.post("/v1/submissions/verify", json={"discord_id": "verify_u1"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "verified"
    assert payload["xp_awarded"] > 0

    db = app.state.testing_session_local()
    try:
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).one()
        assert assignment.status == "solved"

        submission_count = db.query(Submission).filter(Submission.user_id == user_id).count()
        assert submission_count == 1
    finally:
        db.close()


def test_verify_submission_endpoint_not_verified_keeps_assignment_active(client, monkeypatch):
    _, assignment_id = _seed_user_problem_assignment("verify_u2", "tourist_verify_u2")

    async def fake_verify_codeforces_assignment(**kwargs):
        return False, None

    monkeypatch.setattr(
        "app.api.v1.endpoints.submissions.verify_codeforces_assignment",
        fake_verify_codeforces_assignment,
    )

    response = client.post("/v1/submissions/verify", json={"discord_id": "verify_u2"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "not_verified"

    db = app.state.testing_session_local()
    try:
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).one()
        assert assignment.status == "assigned"
    finally:
        db.close()
