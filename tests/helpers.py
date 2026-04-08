from typing import Any

from fastapi.testclient import TestClient


def register_user(
    client: TestClient,
    *,
    email: str,
    password: str = "User12345!",
) -> dict[str, Any]:
    response = client.post(
        "/users/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201, response.text
    return {"email": email, "password": password}


def login_user(
    client: TestClient,
    *,
    email: str,
    password: str,
) -> dict[str, Any]:
    response = client.post(
        "/users/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()
