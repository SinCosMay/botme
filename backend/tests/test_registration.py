def test_register_user(client):
    payload = {"discord_id": "12345", "cf_handle": "tourist"}
    response = client.post("/v1/users/register", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["discord_id"] == "12345"
    assert body["cf_handle"] == "tourist"
    assert body["rating"] == 1000


def test_register_duplicate_discord_id(client):
    payload = {"discord_id": "12345", "cf_handle": "tourist"}
    client.post("/v1/users/register", json=payload)

    duplicate = client.post(
        "/v1/users/register",
        json={"discord_id": "12345", "cf_handle": "another_handle"},
    )
    assert duplicate.status_code == 409
