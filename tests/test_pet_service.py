from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.pets.services import PetService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_public_by_id_returns_none_when_pet_is_missing() -> None:
    repository = SimpleNamespace(get_by_id=AsyncMock(return_value=None))
    storage_service = SimpleNamespace()
    service = PetService(repository, storage_service)

    result = await service.get_public_by_id(999)

    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_photo_redirect_url_uses_external_photo_when_available() -> None:
    repository = SimpleNamespace(get_latest_image_attachment=AsyncMock(return_value=None))
    storage_service = SimpleNamespace(generate_download_url=AsyncMock())
    service = PetService(repository, storage_service)
    pet = SimpleNamespace(id=5, photo_url="https://cdn.example.com/pet.jpg")

    result = await service.get_photo_redirect_url(pet)

    assert result == "https://cdn.example.com/pet.jpg"
    storage_service.generate_download_url.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_attachment_download_url_returns_presigned_payload() -> None:
    attachment = SimpleNamespace(storage_key="attachments/test.pdf")
    repository = SimpleNamespace(get_attachment=AsyncMock(return_value=attachment))
    storage_service = SimpleNamespace(
        presigned_ttl_seconds=600,
        generate_download_url=AsyncMock(return_value="https://storage.test/attachments/test.pdf"),
    )
    service = PetService(repository, storage_service)

    result = await service.get_attachment_download_url(1, 2)

    assert result == {
        "url": "https://storage.test/attachments/test.pdf",
        "expires_in": 600,
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_pet_removes_all_attachment_objects_before_deleting_pet() -> None:
    attachments = [
        SimpleNamespace(storage_key="attachments/1/a.pdf"),
        SimpleNamespace(storage_key="attachments/1/b.pdf"),
    ]
    repository = SimpleNamespace(
        list_attachments=AsyncMock(return_value=attachments),
        delete=AsyncMock(),
    )
    storage_service = SimpleNamespace(delete_object=AsyncMock())
    service = PetService(repository, storage_service)
    pet = SimpleNamespace(id=1)

    await service.delete_pet(pet)

    assert storage_service.delete_object.await_count == 2
    repository.delete.assert_awaited_once_with(pet)
