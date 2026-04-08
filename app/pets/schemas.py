from datetime import date, datetime, time
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PetStatus(str, Enum):
    lost = "lost"
    found = "found"
    returned = "returned"
    closed = "closed"


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


class SPetBase(BaseModel):
    type: str = Field(min_length=2, max_length=50)
    breed: Optional[str] = Field(default=None, max_length=100)
    name: Optional[str] = Field(default=None, max_length=255)
    color: str = Field(min_length=2, max_length=100)
    sex: str = Field(min_length=2, max_length=20)
    age: Optional[str] = Field(default=None, max_length=50)

    chip_number: Optional[str] = Field(default=None, max_length=100)
    brand_number: Optional[str] = Field(default=None, max_length=100)

    found_date: date
    found_time: time
    address: str = Field(min_length=5, max_length=255)

    description: str = Field(min_length=10, max_length=4000)
    status: PetStatus = PetStatus.lost

    @field_validator(
        "breed",
        "name",
        "age",
        "chip_number",
        "brand_number",
        mode="before",
    )
    @classmethod
    def normalize_optional_fields(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("type", "color", "sex", "address", "description", mode="before")
    @classmethod
    def strip_required_fields(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Field must not be empty")
        return normalized

    @field_validator("type", "color", "sex", mode="after")
    @classmethod
    def lowercase_searchable_fields(cls, value: str) -> str:
        return value.lower()


class SPetCreate(SPetBase):
    pass


class SPetUpdate(BaseModel):
    type: Optional[str] = Field(default=None, min_length=2, max_length=50)
    breed: Optional[str] = Field(default=None, max_length=100)
    name: Optional[str] = Field(default=None, max_length=255)
    color: Optional[str] = Field(default=None, min_length=2, max_length=100)
    sex: Optional[str] = Field(default=None, min_length=2, max_length=20)
    age: Optional[str] = Field(default=None, max_length=50)

    chip_number: Optional[str] = Field(default=None, max_length=100)
    brand_number: Optional[str] = Field(default=None, max_length=100)

    found_date: Optional[date] = None
    found_time: Optional[time] = None
    address: Optional[str] = Field(default=None, min_length=5, max_length=255)

    description: Optional[str] = Field(default=None, min_length=10, max_length=4000)
    status: Optional[PetStatus] = None

    photo_url: Optional[str] = Field(default=None, max_length=500)

    @field_validator(
        "breed",
        "name",
        "age",
        "chip_number",
        "brand_number",
        mode="before",
    )
    @classmethod
    def normalize_optional_fields(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("type", "color", "sex", "address", "description", mode="before")
    @classmethod
    def strip_optional_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Field must not be empty")
        return normalized

    @field_validator("type", "color", "sex", mode="after")
    @classmethod
    def lowercase_searchable_fields(cls, value: str | None) -> str | None:
        return value.lower() if value is not None else None


class SPetResponse(SPetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    photo_url: Optional[str] = None


PetSortBy = Literal["found_date", "name", "type", "status", "id"]
SortOrder = Literal["asc", "desc"]


class SPetListParams(BaseModel):
    search: Optional[str] = Field(default=None, max_length=120)
    type: Optional[str] = Field(default=None, max_length=50)
    status: Optional[PetStatus] = None
    sex: Optional[str] = Field(default=None, max_length=20)
    color: Optional[str] = Field(default=None, max_length=100)
    sort_by: PetSortBy = "found_date"
    sort_order: SortOrder = "desc"
    page: int = Field(default=1, ge=1, le=1000)
    page_size: int = Field(default=9, ge=1, le=50)

    @field_validator("search", "type", "sex", "color", mode="before")
    @classmethod
    def normalize_filters(cls, value: str | None) -> str | None:
        normalized = _normalize_optional_text(value)
        return normalized.lower() if normalized else None


class SPaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool


class SPaginatedPetsResponse(BaseModel):
    items: list[SPetResponse]
    meta: SPaginationMeta


class SPetAttachmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pet_id: int
    uploaded_by_id: int | None
    original_filename: str
    content_type: str
    size_bytes: int
    is_image: bool
    created_at: datetime


class SPetAttachmentDownloadResponse(BaseModel):
    url: str
    expires_in: int


class SPetLocationInsightResponse(BaseModel):
    status: Literal["ok", "not_found", "unavailable"]
    query: str
    provider: str
    attribution: str
    display_name: str | None = None
    lat: float | None = None
    lon: float | None = None
    importance: float | None = None
    message: str | None = None
