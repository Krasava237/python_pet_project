from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.security import Permission, has_permission
from app.users.auth_service import AuthService
from app.users.models import User
from app.users.repositories import RefreshSessionRepository, UserRepository
from app.users.services import UserService


class AccessControlService:
    def ensure_permission(self, user: User, permission: str) -> None:
        if not has_permission(user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

    def ensure_can_read_user(self, current_user: User, target_user: User) -> None:
        if current_user.id == target_user.id and has_permission(current_user.role, Permission.USERS_READ_SELF):
            return
        if has_permission(current_user.role, Permission.USERS_READ_ALL):
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    def ensure_pet_permission(self, current_user: User, pet, permission: str) -> None:
        if current_user.role == "admin":
            return
        if pet.owner_id == current_user.id and has_permission(current_user.role, permission):
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )


def get_access_token_from_request(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer" and token:
            return token

    cookie_token = request.cookies.get("pets_access_token")
    if cookie_token:
        return cookie_token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Access token is missing",
    )


def get_refresh_token_from_request(request: Request) -> str:
    refresh_token = request.cookies.get("pets_refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing",
        )
    return refresh_token


def get_optional_refresh_token(request: Request) -> str | None:
    return request.cookies.get("pets_refresh_token")


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_refresh_session_repository(
    db: AsyncSession = Depends(get_db),
) -> RefreshSessionRepository:
    return RefreshSessionRepository(db)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repository)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    refresh_repository: RefreshSessionRepository = Depends(get_refresh_session_repository),
) -> AuthService:
    return AuthService(user_repository, refresh_repository)


def get_access_control_service() -> AccessControlService:
    return AccessControlService()


async def get_current_user(
    token: str = Depends(get_access_token_from_request),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_access_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )
    return user


def require_permission(permission: str):
    async def dependency(
        current_user: User = Depends(get_current_user),
        access_control: AccessControlService = Depends(get_access_control_service),
    ):
        access_control.ensure_permission(current_user, permission)
        return current_user

    return dependency
