import pytest

from tests.helpers import login_user, register_user


@pytest.mark.integration
def test_robots_and_sitemap_are_available(client) -> None:
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "Sitemap:" in response.text

    sitemap_response = client.get("/sitemap.xml")
    assert sitemap_response.status_code == 200
    assert "<urlset" in sitemap_response.text


@pytest.mark.integration
def test_sitemap_contains_public_pet_page(client) -> None:
    credentials = register_user(client, email="seo@example.com")
    login_user(client, **credentials)
    create_response = client.post(
        "/pets/",
        json={
            "type": "dog",
            "breed": "Corgi",
            "name": "Atlas",
            "color": "black",
            "sex": "male",
            "age": "3 years",
            "chip_number": "SEO-1",
            "brand_number": "SEO-2",
            "found_date": "2026-03-24",
            "found_time": "11:20:00",
            "address": "Moscow Kremlin",
            "description": "Friendly dog seen near the main square.",
            "status": "lost",
        },
    )
    pet_id = create_response.json()["id"]

    sitemap_response = client.get("/sitemap.xml")

    assert sitemap_response.status_code == 200
    assert f"/pets/{pet_id}-atlas" in sitemap_response.text
