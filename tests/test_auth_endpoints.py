import pytest

from tests.helpers import login_user, register_user


@pytest.mark.integration
def test_user_can_register_login_open_profile_refresh_and_logout(client) -> None:
    credentials = register_user(client, email="user@example.com")

    login_response = login_user(client, **credentials)
    assert login_response["token_type"] == "bearer"

    me_response = client.get("/users/me")
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.com"

    refresh_response = client.post("/users/refresh")
    assert refresh_response.status_code == 200
    assert refresh_response.json()["token_type"] == "bearer"

    logout_response = client.post("/users/logout")
    assert logout_response.status_code == 200

    me_after_logout = client.get("/users/me")
    assert me_after_logout.status_code == 401

    refresh_after_logout = client.post("/users/refresh")
    assert refresh_after_logout.status_code == 401


@pytest.mark.integration
def test_admin_can_list_users_but_regular_user_cannot(client) -> None:
    register_user(client, email="member@example.com")
    login_user(client, email="admin@local.dev", password="Admin123!")

    admin_response = client.get("/users/")
    assert admin_response.status_code == 200
    assert {user["email"] for user in admin_response.json()} == {
        "admin@local.dev",
        "member@example.com",
    }

    client.post("/users/logout")
    login_user(client, email="member@example.com", password="User12345!")

    member_response = client.get("/users/")
    assert member_response.status_code == 403


@pytest.mark.integration
def test_non_admin_cannot_change_roles(client) -> None:
    register_user(client, email="author@example.com")
    register_user(client, email="viewer@example.com")
    login_user(client, email="author@example.com", password="User12345!")

    response = client.patch("/users/3/role", json={"role": "admin"})

    assert response.status_code == 403
