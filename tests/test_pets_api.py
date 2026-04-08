import pytest

from tests.helpers import login_user, register_user


def build_pet_payload(name: str = "Lucky") -> dict:
    return {
        "type": "dog",
        "breed": "Corgi",
        "name": name,
        "color": "black",
        "sex": "male",
        "age": "2 years",
        "chip_number": "A-100",
        "brand_number": "B-100",
        "found_date": "2026-03-24",
        "found_time": "11:20:00",
        "address": "Moscow Kremlin",
        "description": "Friendly dog seen near the main square.",
        "status": "lost",
    }


@pytest.mark.integration
def test_guest_can_view_public_pet_list_but_cannot_create_pet(client) -> None:
    response = client.get("/pets/")
    assert response.status_code == 200
    assert response.json()["items"] == []

    create_response = client.post("/pets/", json=build_pet_payload())
    assert create_response.status_code == 401


@pytest.mark.integration
def test_owner_can_crud_pet_filter_results_and_manage_attachments(client) -> None:
    credentials = register_user(client, email="owner@example.com")
    login_user(client, **credentials)

    create_response = client.post("/pets/", json=build_pet_payload(name="Luna"))
    assert create_response.status_code == 201
    pet_id = create_response.json()["id"]

    list_response = client.get("/pets/", params={"search": "luna"})
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["total"] == 1

    my_pets_response = client.get("/pets/my")
    assert my_pets_response.status_code == 200
    assert my_pets_response.json()["items"][0]["id"] == pet_id

    insight_response = client.get(f"/pets/{pet_id}/location-insight")
    assert insight_response.status_code == 200
    assert insight_response.json()["status"] == "ok"

    upload_response = client.post(
        f"/pets/{pet_id}/attachments",
        files={"file": ("note.pdf", b"%PDF-1.4 test attachment", "application/pdf")},
    )
    assert upload_response.status_code == 201
    attachment_id = upload_response.json()["id"]

    attachments_response = client.get(f"/pets/{pet_id}/attachments")
    assert attachments_response.status_code == 200
    assert attachments_response.json()[0]["original_filename"] == "note.pdf"

    download_response = client.get(f"/pets/{pet_id}/attachments/{attachment_id}/download-url")
    assert download_response.status_code == 200
    assert download_response.json()["url"].startswith("https://storage.test/")

    update_response = client.put(
        f"/pets/{pet_id}",
        json={"status": "found", "description": "Friendly dog safely placed in shelter."},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "found"

    delete_attachment_response = client.delete(f"/pets/{pet_id}/attachments/{attachment_id}")
    assert delete_attachment_response.status_code == 200

    delete_pet_response = client.delete(f"/pets/{pet_id}")
    assert delete_pet_response.status_code == 200

    final_list_response = client.get("/pets/my")
    assert final_list_response.json()["meta"]["total"] == 0


@pytest.mark.integration
def test_foreign_user_cannot_edit_someone_else_pet(client) -> None:
    owner_credentials = register_user(client, email="owner@example.com")
    intruder_credentials = register_user(client, email="intruder@example.com")

    login_user(client, **owner_credentials)
    create_response = client.post("/pets/", json=build_pet_payload())
    pet_id = create_response.json()["id"]

    client.post("/users/logout")
    login_user(client, **intruder_credentials)

    response = client.put(
        f"/pets/{pet_id}",
        json={"description": "Changed by another user."},
    )

    assert response.status_code == 403


@pytest.mark.integration
def test_create_pet_rejects_invalid_payload(client) -> None:
    credentials = register_user(client, email="validator@example.com")
    login_user(client, **credentials)
    payload = build_pet_payload()
    payload["description"] = "too short"

    response = client.post("/pets/", json=payload)

    assert response.status_code == 422
