def test_create_family_unauthenticated(client):
    response = client.post("api/families/create", json={"name": "Test Family"})
    assert response.status_code == 401


def test_create_family_not_authorized(client, get_token):
    token = get_token(username="user")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "api/families/create", json={"name": "Test Family"}, headers=headers
    )
    assert response.status_code == 403


def test_create_family_authenticated(client, get_token):
    token = get_token(username="admin")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "api/families/create", json={"name": "Test Family"}, headers=headers
    )
    assert response.status_code == 201


def test_get_family_unauthenticated(client):
    response = client.get("api/families/1")
    assert response.status_code == 401


def test_get_family_authorized(client, get_token):
    token = get_token(username="user")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/families/1", headers=headers)
    assert response.status_code == 200


def test_get_unknown_family(client, get_token):
    token = get_token(username="user")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/families/999", headers=headers)
    assert response.status_code == 404
