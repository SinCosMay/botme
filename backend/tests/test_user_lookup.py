def test_get_profile_by_handle(client):
    client.post("/v1/users/register", json={"discord_id": "lookup_u1", "cf_handle": "lookup_cf_u1"})

    response = client.get("/v1/users/handle/lookup_cf_u1/profile")
    assert response.status_code == 200
    payload = response.json()
    assert payload["discord_id"] == "lookup_u1"
    assert payload["cf_handle"] == "lookup_cf_u1"
