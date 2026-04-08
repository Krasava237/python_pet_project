import asyncio
import mimetypes
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.config import settings


ALLOWED_FILE_TYPES: dict[str, tuple[str, bool]] = {
    ".jpg": ("image/jpeg", True),
    ".jpeg": ("image/jpeg", True),
    ".png": ("image/png", True),
    ".webp": ("image/webp", True),
    ".pdf": ("application/pdf", False),
}


class StorageUnavailableError(RuntimeError):
    pass


@dataclass(slots=True)
class ValidatedUpload:
    original_filename: str
    content_type: str
    size_bytes: int
    is_image: bool
    extension: str
    payload: bytes


class StorageService:
    def __init__(self) -> None:
        self.enabled = settings.STORAGE_ENABLED
        self.bucket_name = settings.STORAGE_BUCKET
        self.presigned_ttl_seconds = settings.STORAGE_PRESIGNED_URL_TTL_SECONDS
        self._bucket_ready = False
        self._bucket_lock = asyncio.Lock()
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.STORAGE_ENDPOINT_URL,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY,
            region_name=settings.STORAGE_REGION,
            use_ssl=settings.STORAGE_USE_SSL,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        )

    async def validate_upload(
        self,
        upload_file: UploadFile,
        *,
        images_only: bool = False,
    ) -> ValidatedUpload:
        filename = Path(upload_file.filename or "").name
        if not filename:
            await upload_file.close()
            raise ValueError("Filename is required")

        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_FILE_TYPES:
            await upload_file.close()
            raise ValueError("Unsupported file type. Allowed: jpg, jpeg, png, webp, pdf")
        if images_only and not ALLOWED_FILE_TYPES[extension][1]:
            await upload_file.close()
            raise ValueError("Only image files are allowed for this endpoint")

        try:
            payload = await upload_file.read()
        finally:
            await upload_file.close()

        if not payload:
            raise ValueError("Uploaded file is empty")
        if len(payload) > settings.STORAGE_MAX_FILE_SIZE:
            raise ValueError(
                f"File is too large. Max size is {settings.STORAGE_MAX_FILE_SIZE // (1024 * 1024)} MB"
            )

        expected_content_type, is_image = ALLOWED_FILE_TYPES[extension]
        guessed_content_type = mimetypes.guess_type(filename)[0]
        declared_content_type = upload_file.content_type or guessed_content_type or expected_content_type
        if declared_content_type not in {expected_content_type, "application/octet-stream"}:
            raise ValueError("File content type does not match its extension")

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
        return f"pet-attachments/{pet_id}/{uuid4().hex}{extension}"

    async def ensure_bucket(self) -> None:
        if not self.enabled:
            raise StorageUnavailableError("Object storage is disabled in settings")
        if self._bucket_ready:
            return

        async with self._bucket_lock:
            if self._bucket_ready:
                return
            try:
                await asyncio.to_thread(self._ensure_bucket_sync)
            except (BotoCoreError, ClientError, OSError) as exc:
                raise StorageUnavailableError("Object storage is unavailable") from exc
            self._bucket_ready = True

    def _ensure_bucket_sync(self) -> None:
        try:
            self._client.head_bucket(Bucket=self.bucket_name)
            return
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code")
            if error_code not in {"404", "NoSuchBucket"}:
                raise

        if settings.STORAGE_REGION == "us-east-1":
            self._client.create_bucket(Bucket=self.bucket_name)
        else:
            self._client.create_bucket(
                Bucket=self.bucket_name,
                CreateBucketConfiguration={"LocationConstraint": settings.STORAGE_REGION},
            )

    async def upload_bytes(self, object_key: str, payload: bytes, content_type: str) -> None:
        await self.ensure_bucket()
        try:
            await asyncio.to_thread(
                self._client.put_object,
                Bucket=self.bucket_name,
                Key=object_key,
                Body=payload,
                ContentType=content_type,
            )
        except (BotoCoreError, ClientError, OSError) as exc:
            raise StorageUnavailableError("Could not upload file to object storage") from exc

    async def delete_object(self, object_key: str) -> None:
        await self.ensure_bucket()
        try:
            await asyncio.to_thread(
                self._client.delete_object,
                Bucket=self.bucket_name,
                Key=object_key,
            )
        except (BotoCoreError, ClientError, OSError) as exc:
            raise StorageUnavailableError("Could not delete file from object storage") from exc

    async def generate_download_url(self, object_key: str) -> str:
        await self.ensure_bucket()
        try:
            return await asyncio.to_thread(
                self._client.generate_presigned_url,
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_key},
                ExpiresIn=self.presigned_ttl_seconds,
            )
        except (BotoCoreError, ClientError, OSError) as exc:
            raise StorageUnavailableError("Could not generate a pre-signed download URL") from exc
