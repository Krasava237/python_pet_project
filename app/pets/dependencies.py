from functools import lru_cache

from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.integrations.nominatim import NominatimService
from app.pets.repositories import PetRepository
from app.pets.schemas import PetStatus, SPetListParams
from app.pets.services import PetService
from app.storage.service import StorageService
from app.users.dependencies import (
    AccessControlService,
    get_access_control_service,
    get_current_user,
)
from app.users.models import User


def get_pet_repository(db: AsyncSession = Depends(get_db)) -> PetRepository:
    return PetRepository(db)


@lru_cache
def _get_storage_service() -> StorageService:
    return StorageService()


def get_storage_service() -> StorageService:
    return _get_storage_service()


@lru_cache
def _get_nominatim_service() -> NominatimService:
    return NominatimService()


def get_nominatim_service() -> NominatimService:
    return _get_nominatim_service()


def get_pet_service(
    pet_repository: PetRepository = Depends(get_pet_repository),
    storage_service: StorageService = Depends(get_storage_service),
) -> PetService:
    return PetService(pet_repository, storage_service)


def get_pet_list_params(
    search: str | None = Query(default=None, max_length=120),
    pet_type: str | None = Query(default=None, alias="type", max_length=50),
    status: PetStatus | None = Query(default=None),
    sex: str | None = Query(default=None, max_length=20),
    color: str | None = Query(default=None, max_length=100),
    sort_by: str = Query(default="found_date", pattern="^(found_date|name|type|status|id)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1, le=1000),
    page_size: int = Query(default=9, ge=1, le=50),
) -> SPetListParams:
    return SPetListParams(
        search=search,
        type=pet_type,
        status=status,
        sex=sex,
        color=color,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )


def require_pet_access(permission: str):
    async def dependency(
        pet_id: int,
        current_user: User = Depends(get_current_user),
        pet_service: PetService = Depends(get_pet_service),
        access_control: AccessControlService = Depends(get_access_control_service),
    ):
        pet = await pet_service.get_by_id(pet_id)
        if not pet:
            raise HTTPException(status_code=404, detail="Pet not found")
        access_control.ensure_pet_permission(current_user, pet, permission)
        return pet

    return dependency
