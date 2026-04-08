from fastapi import APIRouter, Depends, HTTPException, Response

from app.config import settings
from app.security import Permission
from app.users.auth_service import AuthService
from app.users.dependencies import (
    AccessControlService,
    get_access_control_service,
    get_auth_service,
    get_current_user,
    get_optional_refresh_token,
    get_refresh_token_from_request,
    get_user_service,
    require_permission,
)
from app.users.models import User
from app.users.schemas import (
    STokenResponse,
    SUserCreate,
    SUserLogin,
    SUserResponse,
    SUserRoleUpdate,
)
from app.users.services import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key="pets_access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="pets_refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


@router.get("/", response_model=list[SUserResponse])
async def get_users(
    _: User = Depends(require_permission(Permission.USERS_READ_ALL)),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.list_users()


@router.get("/me", response_model=SUserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=SUserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    access_control: AccessControlService = Depends(get_access_control_service),
):
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    access_control.ensure_can_read_user(current_user, user)
    return user


@router.post("/register", status_code=201)
async def register_user(
    user_data: SUserCreate,
    user_service: UserService = Depends(get_user_service),
):
    try:
        await user_service.create_user(user_data.email, user_data.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"detail": "User registered successfully"}


@router.post("/login", response_model=STokenResponse)
async def login_user(
    response: Response,
    user_data: SUserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token, refresh_token = await auth_service.issue_token_pair(user)
    _set_auth_cookies(response, access_token, refresh_token)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=STokenResponse)
async def refresh_access_token(
    response: Response,
    refresh_token: str = Depends(get_refresh_token_from_request),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        access_token, new_refresh_token = await auth_service.rotate_refresh_token(refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    _set_auth_cookies(response, access_token, new_refresh_token)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout_user(
    response: Response,
    refresh_token: str | None = Depends(get_optional_refresh_token),
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.logout(refresh_token)
    response.delete_cookie("pets_access_token")
    response.delete_cookie("pets_refresh_token")
    return {"detail": "User logged out"}


@router.patch("/{user_id}/role", response_model=SUserResponse)
async def update_user_role(
    user_id: int,
    role_data: SUserRoleUpdate,
    _: User = Depends(require_permission(Permission.ROLES_MANAGE)),
    user_service: UserService = Depends(get_user_service),
):
    try:
        return await user_service.assign_role(user_id, role_data.role.value)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
