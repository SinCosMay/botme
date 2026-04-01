from app.main import app
from app.models.problem import Problem


def _seed_cf_problems() -> None:
    db = app.state.testing_session_local()
    try:
        db.add_all(
            [
                Problem(
                    platform="codeforces",
                    cf_contest_id=1800,
                    cf_index="A",
                    name="Negative Flow A",
                    rating=900,
                    tags=["alpha"],
                    url="https://codeforces.com/problemset/problem/1800/A",
                ),
                Problem(
                    platform="codeforces",
                    cf_contest_id=1800,
                    cf_index="B",
                    name="Negative Flow B",
                    rating=1000,
                    tags=["beta"],
                    url="https://codeforces.com/problemset/problem/1800/B",
                ),
            ]
        )
        db.commit()
    finally:
        db.close()


def test_verify_without_assignment_returns_404(client):
    client.post("/v1/users/register", json={"discord_id": "neg_u1", "cf_handle": "neg_cf_u1"})
    verify = client.post("/v1/submissions/verify", json={"discord_id": "neg_u1"})
    assert verify.status_code == 404


def test_followup_rejects_mismatched_question_submission_pair(client, monkeypatch):
    _seed_cf_problems()

    client.post("/v1/users/register", json={"discord_id": "neg_u2", "cf_handle": "neg_cf_u2"})
    client.post("/v1/users/register", json={"discord_id": "neg_u3", "cf_handle": "neg_cf_u3"})

    a1 = client.post("/v1/problems/assign", json={"discord_id": "neg_u2", "mode": "topic", "tag": "alpha"})
    a2 = client.post("/v1/problems/assign", json={"discord_id": "neg_u3", "mode": "topic", "tag": "beta"})
    assert a1.status_code == 200
    assert a2.status_code == 200

    async def fake_verify_codeforces_assignment(**kwargs):
        return True, f"sub_{kwargs['contest_id']}_{kwargs['index']}"

    monkeypatch.setattr(
        "app.api.v1.endpoints.submissions.verify_codeforces_assignment",
        fake_verify_codeforces_assignment,
    )

    v1 = client.post("/v1/submissions/verify", json={"discord_id": "neg_u2"})
    v2 = client.post("/v1/submissions/verify", json={"discord_id": "neg_u3"})
    assert v1.status_code == 200
    assert v2.status_code == 200

    p1 = v1.json()
    p2 = v2.json()

    bad = client.post(
        "/v1/followup/answer",
        json={
            "submission_id": p1["submission_id"],
            "question_id": p2["followup_question_id"],
            "answer": "this should fail",
        },
    )
    assert bad.status_code == 400
