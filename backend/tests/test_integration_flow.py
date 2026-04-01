from app.main import app
from app.models.problem import Problem


def _seed_cf_problem() -> None:
    db = app.state.testing_session_local()
    try:
        db.add(
            Problem(
                platform="codeforces",
                cf_contest_id=1700,
                cf_index="A",
                name="Flow Test Problem",
                rating=900,
                tags=["implementation"],
                url="https://codeforces.com/problemset/problem/1700/A",
            )
        )
        db.commit()
    finally:
        db.close()


def test_full_register_assign_verify_followup_flow(client, monkeypatch):
    _seed_cf_problem()

    register = client.post(
        "/v1/users/register",
        json={"discord_id": "integration_u1", "cf_handle": "integration_cf_u1"},
    )
    assert register.status_code == 201

    assign = client.post(
        "/v1/problems/assign",
        json={"discord_id": "integration_u1", "mode": "random"},
    )
    assert assign.status_code == 200

    async def fake_verify_codeforces_assignment(**kwargs):
        return True, "123456789"

    monkeypatch.setattr(
        "app.api.v1.endpoints.submissions.verify_codeforces_assignment",
        fake_verify_codeforces_assignment,
    )

    verify = client.post("/v1/submissions/verify", json={"discord_id": "integration_u1"})
    assert verify.status_code == 200
    verify_payload = verify.json()
    assert verify_payload["status"] == "verified"
    assert verify_payload["followup_question_id"] is not None

    followup = client.post(
        "/v1/followup/answer",
        json={
            "submission_id": verify_payload["submission_id"],
            "question_id": verify_payload["followup_question_id"],
            "answer": "implementation is the key idea here",
        },
    )
    assert followup.status_code == 200
    assert followup.json()["awarded_xp"] == 10

    profile = client.get("/v1/users/integration_u1/profile")
    assert profile.status_code == 200
    profile_payload = profile.json()
    assert profile_payload["xp"] > 0
    assert profile_payload["rating"] >= 1000
