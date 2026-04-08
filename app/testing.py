from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Response, UploadFile, status
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel
from sqlalchemy import delete, text

from app.config import settings
from app.database import async_session
from app.pets.models import Pet, PetAttachment
from app.storage.service import ALLOWED_FILE_TYPES, ValidatedUpload
from app.users.models import RefreshSession, User
from app.users.repositories import UserRepository
from app.users.services import UserService


@dataclass(slots=True)
class StoredObject:
    content_type: str
    payload: bytes


class InMemoryStorageService:
    def __init__(self) -> None:
        self.presigned_ttl_seconds = settings.STORAGE_PRESIGNED_URL_TTL_SECONDS
        self._objects: dict[str, StoredObject] = {}

    def reset(self) -> None:
        self._objects.clear()

    async def validate_upload(
        self,
        upload_file: UploadFile,
        *,
        images_only: bool = False,
    ) -> ValidatedUpload:
        # Повторяем ключевые проверки production-хранилища, чтобы e2e-тесты ловили реальные ошибки.
        filename = Path(upload_file.filename or "").name
        if not filename:
            await upload_file.close()
            raise ValueError("Filename is required")

        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_FILE_TYPES:
            await upload_file.close()
            raise ValueError("Unsupported file type. Allowed: jpg, jpeg, png, webp, pdf")

        expected_content_type, is_image = ALLOWED_FILE_TYPES[extension]
        if images_only and not is_image:
            await upload_file.close()
            raise ValueError("Only image files are allowed for this endpoint")

        try:
            payload = await upload_file.read()
        finally:
            await upload_file.close()

        if not payload:
            raise ValueError("Uploaded file is empty")

        if is_image:
            try:
                image = Image.open(BytesIO(payload))
                image.verify()
            except (UnidentifiedImageError, OSError) as exc:
                raise ValueError("Uploaded file is not a valid image") from exc
        elif not payload.startswith(b"%PDF"):
            raise ValueError("Uploaded file is not a valid PDF document")

        return ValidatedUpload(
            original_filename=filename[:255],
            content_type=expected_content_type,
            size_bytes=len(payload),
            is_image=is_image,
            extension=extension,
            payload=payload,
        )

    def build_object_key(self, pet_id: int, extension: str) -> str:
        return f"test-attachments/{pet_id}/{uuid4().hex}{extension}"

    async def upload_bytes(self, object_key: str, payload: bytes, content_type: str) -> None:
        self._objects[object_key] = StoredObject(content_type=content_type, payload=payload)

    async def delete_object(self, object_key: str) -> None:
        self._objects.pop(object_key, None)

    async def generate_download_url(self, object_key: str) -> str:
        if object_key not in self._objects:
            raise LookupError("Attachment not found in fake storage")
        return f"https://storage.test/{object_key}"


class TestNominatimService:
    def __init__(self) -> None:
        self.mode: Literal["ok", "not_found", "unavailable"] = "ok"

    def reset(self) -> None:
        self.mode = "ok"

    def set_mode(self, mode: Literal["ok", "not_found", "unavailable"]) -> None:
        self.mode = mode

    async def lookup_address(self, query: str) -> dict:
        # Режимы ответа позволяют отдельно показать успех, отсутствие результата и временную недоступность.
        if self.mode == "not_found":
            return {
                "status": "not_found",
                "query": query,
                "provider": "Nominatim",
                "attribution": "Test provider",
                "message": "No matching address found",
                "display_name": None,
                "lat": None,
                "lon": None,
                "importance": None,
            }

        if self.mode == "unavailable":
            return {
                "status": "unavailable",
                "query": query,
                "provider": "Nominatim",
                "attribution": "Test provider",
                "message": "Nominatim is temporarily unavailable",
                "display_name": None,
                "lat": None,
                "lon": None,
                "importance": None,
            }

        return {
            "status": "ok",
            "query": query,
            "provider": "Nominatim",
            "attribution": "Test provider",
            "message": None,
            "display_name": f"Normalized: {query}",
            "lat": 55.7558,
            "lon": 37.6173,
            "importance": 0.8,
        }


_test_storage_service = InMemoryStorageService()
_test_nominatim_service = TestNominatimService()


def get_test_storage_service() -> InMemoryStorageService:
    return _test_storage_service


def get_test_nominatim_service() -> TestNominatimService:
    return _test_nominatim_service


class NominatimModePayload(BaseModel):
    mode: Literal["ok", "not_found", "unavailable"]


router = APIRouter(prefix="/_test", tags=["Testing"], include_in_schema=False)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_test_state() -> Response:
    async with async_session() as session:
        # Очищаем данные без привязки к конкретной СУБД, чтобы тесты одинаково шли локально и в CI.
        for model in (PetAttachment, Pet, RefreshSession, User):
            await session.execute(delete(model))

        if session.bind and session.bind.dialect.name == "sqlite":
            sequence_table_exists = await session.execute(
                text(
                    "SELECT name FROM sqlite_master "
                    "WHERE type = 'table' AND name = 'sqlite_sequence'"
                )
            )
            if sequence_table_exists.scalar_one_or_none():
                await session.execute(text("DELETE FROM sqlite_sequence"))

        await session.commit()

        # После очистки восстанавливаем bootstrap-администратора для сценариев входа.
        user_service = UserService(UserRepository(session))
        await user_service.ensure_bootstrap_admin(
            settings.BOOTSTRAP_ADMIN_EMAIL,
            settings.BOOTSTRAP_ADMIN_PASSWORD,
        )

    _test_storage_service.reset()
    _test_nominatim_service.reset()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/nominatim-mode", status_code=status.HTTP_204_NO_CONTENT)
async def set_nominatim_mode(payload: NominatimModePayload) -> Response:
    _test_nominatim_service.set_mode(payload.mode)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
