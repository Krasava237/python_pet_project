from datetime import datetime, timezone

from app.users.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
    verify_password,
)
from app.users.repositories import RefreshSessionRepository, UserRepository


def _normalize_utc_datetime(value: datetime) -> datetime:
    # SQLite в тестовом контуре возвращает naive datetime, поэтому нормализуем оба формата к UTC.
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_repository: RefreshSessionRepository,
    ):
        self.user_repository = user_repository
        self.refresh_repository = refresh_repository

    async def authenticate_user(self, email: str, password: str):
        user = await self.user_repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    async def issue_token_pair(self, user):
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token, expires_at = create_refresh_token({"sub": str(user.id)})
        payload = decode_token(refresh_token)
        if not payload or "jti" not in payload:
            raise ValueError("Unable to issue refresh token")

        await self.refresh_repository.create(
            user_id=user.id,
            jti=payload["jti"],
            token_hash=hash_token(refresh_token),
            expires_at=expires_at,
        )
        return access_token, refresh_token

    async def get_user_from_access_token(self, token: str):
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        return await self.user_repository.get_by_id(int(user_id))

    async def rotate_refresh_token(self, refresh_token: str):
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        user_id = payload.get("sub")
        jti = payload.get("jti")
        if not user_id or not jti:
            raise ValueError("Invalid refresh token")

        refresh_session = await self.refresh_repository.get_by_jti(jti)
        if not refresh_session:
            raise ValueError("Refresh session not found")
        if refresh_session.revoked_at is not None:
            raise ValueError("Refresh token already revoked")
        if _normalize_utc_datetime(refresh_session.expires_at) <= datetime.now(timezone.utc):
            raise ValueError("Refresh token expired")
        if refresh_session.token_hash != hash_token(refresh_token):
            raise ValueError("Refresh token does not match the stored session")

        await self.refresh_repository.revoke(refresh_session)

        user = await self.user_repository.get_by_id(int(user_id))
        if not user:
            raise ValueError("User not found")

        return await self.issue_token_pair(user)

    async def logout(self, refresh_token: str | None):
        if not refresh_token:
            return

        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return

        jti = payload.get("jti")
        if not jti:
            return

        refresh_session = await self.refresh_repository.get_by_jti(jti)
        if refresh_session:
            await self.refresh_repository.revoke(refresh_session)
