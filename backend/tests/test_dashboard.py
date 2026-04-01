def test_dashboard_pages_are_served(client):
    for path in ("/dashboard", "/dashboard/leaderboard", "/dashboard/profile"):
        response = client.get(path)
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


def test_request_id_header_is_attached(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")
