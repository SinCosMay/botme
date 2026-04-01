from datetime import datetime, timezone

from app.main import app
from app.models.rating_history import RatingHistory
from app.models.user import User
from app.models.xp_history import XpHistory


def _seed_phase4_users() -> tuple[str, str]:
    db = app.state.testing_session_local()
    try:
        u1 = User(discord_id="lb_u1", cf_handle="lb_cf_u1", xp=300, rating=1200, level=2)
        u2 = User(discord_id="lb_u2", cf_handle="lb_cf_u2", xp=500, rating=1100, level=3)
        db.add_all([u1, u2])
        db.flush()

        db.add_all(
            [
                XpHistory(
                    user_id=u1.id,
                    amount=100,
                    source="test",
                    metadata_json={},
                    created_at=datetime.now(timezone.utc),
                ),
                XpHistory(
                    user_id=u1.id,
                    amount=200,
                    source="test",
                    metadata_json={},
                    created_at=datetime.now(timezone.utc),
                ),
                RatingHistory(
                    user_id=u1.id,
                    old_rating=1000,
                    new_rating=1100,
                    reason="test",
                    created_at=datetime.now(timezone.utc),
                ),
                RatingHistory(
                    user_id=u1.id,
                    old_rating=1100,
                    new_rating=1200,
                    reason="test",
                    created_at=datetime.now(timezone.utc),
                ),
            ]
        )
        db.commit()
        return u1.id, u2.id
    finally:
        db.close()


def test_phase4_leaderboard_orders_by_xp(client):
    _, _ = _seed_phase4_users()

    response = client.get("/v1/analytics/leaderboard?metric=xp&page=1&limit=10")
    assert response.status_code == 200

    payload = response.json()
    assert payload["metric"] == "xp"
    assert payload["total"] == 2
    assert payload["entries"][0]["xp"] >= payload["entries"][1]["xp"]


def test_phase4_timeseries_returns_points(client):
    user_id, _ = _seed_phase4_users()

    xp_series = client.get(f"/v1/analytics/{user_id}/timeseries?metric=xp&days=30")
    assert xp_series.status_code == 200
    xp_payload = xp_series.json()
    assert xp_payload["metric"] == "xp"
    assert len(xp_payload["points"]) >= 1

    rating_series = client.get(f"/v1/analytics/{user_id}/timeseries?metric=rating&days=30")
    assert rating_series.status_code == 200
    rating_payload = rating_series.json()
    assert rating_payload["metric"] == "rating"
    assert len(rating_payload["points"]) >= 1
