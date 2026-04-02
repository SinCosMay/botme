def test_metrics_endpoint_returns_counters(client):
    client.get("/")
    client.get("/v1/health")

    response = client.get("/v1/metrics")
    assert response.status_code == 200
    payload = response.json()
    assert payload["requests_total"] >= 2
    assert payload["request_duration_ms_sum"] >= 0
    assert payload["request_duration_ms_avg"] >= 0


def test_metrics_tracks_errors(client):
    client.get("/v1/users/non-existent/profile")

    response = client.get("/v1/metrics")
    assert response.status_code == 200
    payload = response.json()
    assert payload["requests_error_total"] >= 1
