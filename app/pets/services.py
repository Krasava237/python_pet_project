import contextlib
from math import ceil

import numpy as np

from app.config import settings
from app.pets.repositories import PetRepository
from app.pets.schemas import SPaginatedPetsResponse, SPaginationMeta, SPetListParams, SPetResponse
from app.storage.service import StorageService


class PetService:
    def __init__(self, repository: PetRepository, storage_service: StorageService):
        self.repository = repository
        self.storage_service = storage_service

    def _build_photo_url(self, pet_id: int) -> str:
        return f"{settings.API_BASE_URL.rstrip('/')}/pets/{pet_id}/photo"

    def _normalize_photo_url(self, photo_url: str) -> str:
        if photo_url.startswith(("http://", "https://")):
            return photo_url
        if photo_url.startswith("/"):
            return f"{settings.API_BASE_URL.rstrip('/')}{photo_url}"
        return f"{settings.API_BASE_URL.rstrip('/')}/{photo_url.lstrip('/')}"

    async def _resolve_photo_url(self, pet) -> str | None:
        if pet.photo_url:
            return self._normalize_photo_url(pet.photo_url)

        latest_image = await self.repository.get_latest_image_attachment(pet.id)
        if latest_image:
            return self._build_photo_url(pet.id)

        return None

    async def _serialize_pet(self, pet) -> SPetResponse:
        response = SPetResponse.model_validate(pet)
        return response.model_copy(update={"photo_url": await self._resolve_photo_url(pet)})

    async def _build_paginated_response(
        self,
        pets,
        *,
        page: int,
        page_size: int,
        total: int,
    ) -> SPaginatedPetsResponse:
        total_pages = max(1, ceil(total / page_size)) if total else 1
        items: list[SPetResponse] = []
        for pet in pets:
            items.append(await self._serialize_pet(pet))

        return SPaginatedPetsResponse(
            items=items,
            meta=SPaginationMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1,
            ),
        )

    async def list_pets(self, params: SPetListParams):
        pets, total = await self.repository.list_filtered(params)
        return await self._build_paginated_response(
            pets,
            page=params.page,
            page_size=params.page_size,
            total=total,
        )

    async def get_by_id(self, pet_id: int):
        return await self.repository.get_by_id(pet_id)

    async def find_by_owner(self, owner_id: int, params: SPetListParams):
        pets, total = await self.repository.list_filtered(params, owner_id=owner_id)
        return await self._build_paginated_response(
            pets,
            page=params.page,
            page_size=params.page_size,
            total=total,
        )

    async def get_public_by_id(self, pet_id: int) -> SPetResponse | None:
        pet = await self.repository.get_by_id(pet_id)
        if not pet:
            return None
        return await self._serialize_pet(pet)

    async def get_photo_redirect_url(self, pet) -> str | None:
        if pet.photo_url:
            normalized_photo_url = self._normalize_photo_url(pet.photo_url)
            if normalized_photo_url != self._build_photo_url(pet.id):
                return normalized_photo_url

        latest_image = await self.repository.get_latest_image_attachment(pet.id)
        if not latest_image:
            return None

        return await self.storage_service.generate_download_url(latest_image.storage_key)

    async def create_pet(self, pet_data: dict):
        return await self.repository.create(pet_data)

    async def update_pet(self, pet, pet_data: dict):
        return await self.repository.update(pet, pet_data)

    async def delete_pet(self, pet):
        attachments = await self.repository.list_attachments(pet.id)
        for attachment in attachments:
            await self.storage_service.delete_object(attachment.storage_key)
        await self.repository.delete(pet)

    async def list_attachments(self, pet_id: int):
        return await self.repository.list_attachments(pet_id)

    async def upload_attachment(
        self,
        pet,
        *,
        uploaded_by_id: int | None,
        file,
        images_only: bool = False,
    ):
        validated_file = await self.storage_service.validate_upload(file, images_only=images_only)
        object_key = self.storage_service.build_object_key(pet.id, validated_file.extension)

        try:
            await self.storage_service.upload_bytes(
                object_key,
                validated_file.payload,
                validated_file.content_type,
            )
            return await self.repository.create_attachment(
                {
                    "pet_id": pet.id,
                    "uploaded_by_id": uploaded_by_id,
                    "storage_key": object_key,
                    "original_filename": validated_file.original_filename,
                    "content_type": validated_file.content_type,
                    "size_bytes": validated_file.size_bytes,
                    "is_image": validated_file.is_image,
                }
            )
        except Exception:
            with contextlib.suppress(Exception):
                await self.storage_service.delete_object(object_key)
            raise

    async def get_attachment_download_url(self, pet_id: int, attachment_id: int):
        attachment = await self.repository.get_attachment(pet_id, attachment_id)
        if not attachment:
            raise LookupError("Attachment not found")
        url = await self.storage_service.generate_download_url(attachment.storage_key)
        return {
            "url": url,
            "expires_in": self.storage_service.presigned_ttl_seconds,
        }

    async def delete_attachment(self, pet_id: int, attachment_id: int) -> None:
        attachment = await self.repository.get_attachment(pet_id, attachment_id)
        if not attachment:
            raise LookupError("Attachment not found")
        await self.storage_service.delete_object(attachment.storage_key)
        await self.repository.delete_attachment(attachment)

    async def find_similar_by_embedding(self, pet_type: str, emb: list[float], top_k: int = 5):
        emb_np = np.array(emb, dtype=np.float32)
        pets = await self.repository.list_with_embeddings_by_type(pet_type)

        if not pets:
            return []

        scored = []
        for pet in pets:
            vec = np.array(pet.embedding, dtype=np.float32)
            score = float(np.dot(emb_np, vec))
            scored.append(
                {
                    "pet": SPetResponse.model_validate(pet),
                    "score": score,
                }
            )

        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]
