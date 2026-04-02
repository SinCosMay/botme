from datetime import datetime, timezone

from app.main import app
from app.models.assignment import Assignment
from app.models.followup_question import FollowupQuestion
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User


def _seed_assignment(discord_id: str, cf_handle: str) -> None:
    db = app.state.testing_session_local()
    try:
        user = User(discord_id=discord_id, cf_handle=cf_handle)
        problem = Problem(
            platform="codeforces",
            cf_contest_id=1001,
            cf_index="B",
            name="CF B",
            rating=1000,
            tags=["implementation"],
            url="https://codeforces.com/problemset/problem/1001/B",
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
    finally:
        db.close()


def test_followup_answer_awards_bonus_xp(client, monkeypatch):
    _seed_assignment("followup_u1", "tourist_followup_u1")

    async def fake_verify_codeforces_assignment(**kwargs):
        return True, "888888"

    monkeypatch.setattr(
        "app.api.v1.endpoints.submissions.verify_codeforces_assignment",
        fake_verify_codeforces_assignment,
    )

    verify = client.post("/v1/submissions/verify", json={"discord_id": "followup_u1"})
    assert verify.status_code == 200
    verify_payload = verify.json()
    assert verify_payload["followup_question_id"] is not None

    response = client.post(
        "/v1/followup/answer",
        json={
            "submission_id": verify_payload["submission_id"],
            "question_id": verify_payload["followup_question_id"],
            "answer": "I used implementation and direct simulation",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["is_correct"] is True
    assert payload["awarded_xp"] == 10


def test_followup_duplicate_attempt_returns_zero_bonus(client, monkeypatch):
    _seed_assignment("followup_u2", "tourist_followup_u2")

    async def fake_verify_codeforces_assignment(**kwargs):
        return True, "999999"

    monkeypatch.setattr(
        "app.api.v1.endpoints.submissions.verify_codeforces_assignment",
        fake_verify_codeforces_assignment,
    )

    verify = client.post("/v1/submissions/verify", json={"discord_id": "followup_u2"})
    verify_payload = verify.json()

    first = client.post(
        "/v1/followup/answer",
        json={
            "submission_id": verify_payload["submission_id"],
            "question_id": verify_payload["followup_question_id"],
            "answer": "implementation is used",
        },
    )
    assert first.status_code == 200
    assert first.json()["awarded_xp"] == 10

    second = client.post(
        "/v1/followup/answer",
        json={
            "submission_id": verify_payload["submission_id"],
            "question_id": verify_payload["followup_question_id"],
            "answer": "implementation again",
        },
    )
    assert second.status_code == 200
    assert second.json()["awarded_xp"] == 0


def test_followup_accepts_keyword_alias(client):
    db = app.state.testing_session_local()
    try:
        user = User(discord_id="followup_u3", cf_handle="tourist_followup_u3")
        problem = Problem(
            platform="codeforces",
            cf_contest_id=3001,
            cf_index="A",
            name="DP Problem",
            rating=1400,
            tags=["dp"],
            url="https://codeforces.com/problemset/problem/3001/A",
        )
        db.add_all([user, problem])
        db.flush()

        submission = Submission(
            user_id=user.id,
            problem_id=problem.id,
            platform="codeforces",
            verdict="ok",
            xp_awarded=10,
        )
        db.add(submission)
        db.flush()

        question = FollowupQuestion(
            problem_id=problem.id,
            question_type="key_idea",
            prompt="Explain the key idea",
            expected_answer={"keywords": ["dp"]},
            bonus_xp=10,
        )
        db.add(question)
        db.commit()

        response = client.post(
            "/v1/followup/answer",
            json={
                "submission_id": submission.id,
                "question_id": question.id,
                "answer": "I used dynamic programming with states over prefix length.",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["is_correct"] is True
        assert payload["awarded_xp"] == 10
    finally:
        db.close()
