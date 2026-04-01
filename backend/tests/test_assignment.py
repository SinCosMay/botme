def _seed_cf_problem():
    from app.main import app
    from app.models.problem import Problem

    db = app.state.testing_session_local()
    try:
        problem = Problem(
            platform="codeforces",
            cf_contest_id=1000,
            cf_index="A",
            name="CF A",
            rating=800,
            tags=["implementation"],
            url="https://codeforces.com/problemset/problem/1000/A",
        )
        db.add(problem)
        db.commit()
    finally:
        db.close()


def _seed_lc_problem():
    from app.main import app
    from app.models.problem import Problem

    db = app.state.testing_session_local()
    try:
        problem = Problem(
            platform="leetcode",
            lc_slug="two-sum",
            name="Two Sum",
            url="https://leetcode.com/problems/two-sum/",
            tags=["array", "difficulty:easy"],
            companies=["google"],
        )
        db.add(problem)
        db.commit()
    finally:
        db.close()


def test_assign_codeforces_problem(client):
    client.post("/v1/users/register", json={"discord_id": "u1", "cf_handle": "tourist"})
    _seed_cf_problem()

    response = client.post(
        "/v1/problems/assign",
        json={"discord_id": "u1", "mode": "topic", "tag": "implementation"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["platform"] == "codeforces"
    assert body["name"] == "CF A"


def test_phase_1_5_lc_assign_and_mark_solved(client):
    register = client.post("/v1/users/register", json={"discord_id": "u2", "cf_handle": "petr"})
    user_id = register.json()["id"]

    _seed_lc_problem()

    assigned = client.post(
        "/v1/problems/assign/leetcode",
        json={"discord_id": "u2", "company": "google", "difficulty": "easy"},
    )
    assert assigned.status_code == 200
    assert assigned.json()["platform"] == "leetcode"

    solved = client.post(
        "/v1/submissions/leetcode/mark-solved",
        json={"discord_id": "u2", "slug": "two-sum", "proof_url": "https://example.com/proof"},
    )
    assert solved.status_code == 200
    assert solved.json()["status"] == "recorded"

    profile = client.get("/v1/users/u2/profile")
    assert profile.status_code == 200
    assert profile.json()["xp"] == 0
    assert profile.json()["rating"] == 1000

    analytics = client.get(f"/v1/analytics/{user_id}?platform=leetcode")
    assert analytics.status_code == 200
    assert analytics.json()["solved_count"] == 1
