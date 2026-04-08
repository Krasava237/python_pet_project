from enum import Enum


class Role(str, Enum):
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


class Permission:
    PETS_READ = "pets.read"
    PETS_CREATE = "pets.create"
    PETS_UPDATE_OWN = "pets.update_own"
    PETS_DELETE_OWN = "pets.delete_own"
    PETS_UPLOAD_PHOTO_OWN = "pets.upload_photo_own"
    PETS_ATTACHMENTS_READ_OWN = "pets.attachments_read_own"
    PETS_ATTACHMENTS_WRITE_OWN = "pets.attachments_write_own"
    PETS_ATTACHMENTS_DELETE_OWN = "pets.attachments_delete_own"
    USERS_READ_SELF = "users.read_self"
    USERS_READ_ALL = "users.read_all"
    ROLES_MANAGE = "roles.manage"


ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.GUEST: {
        Permission.PETS_READ,
    },
    Role.USER: {
        Permission.PETS_READ,
        Permission.PETS_CREATE,
        Permission.PETS_UPDATE_OWN,
        Permission.PETS_DELETE_OWN,
        Permission.PETS_UPLOAD_PHOTO_OWN,
        Permission.PETS_ATTACHMENTS_READ_OWN,
        Permission.PETS_ATTACHMENTS_WRITE_OWN,
        Permission.PETS_ATTACHMENTS_DELETE_OWN,
        Permission.USERS_READ_SELF,
    },
    Role.ADMIN: {
        Permission.PETS_READ,
        Permission.PETS_CREATE,
        Permission.PETS_UPDATE_OWN,
        Permission.PETS_DELETE_OWN,
        Permission.PETS_UPLOAD_PHOTO_OWN,
        Permission.PETS_ATTACHMENTS_READ_OWN,
        Permission.PETS_ATTACHMENTS_WRITE_OWN,
        Permission.PETS_ATTACHMENTS_DELETE_OWN,
        Permission.USERS_READ_SELF,
        Permission.USERS_READ_ALL,
        Permission.ROLES_MANAGE,
    },
}


def normalize_role(role: str | Role | None) -> Role:
    if isinstance(role, Role):
        return role
    if not role:
        return Role.USER
    try:
        return Role(role)
    except ValueError:
        return Role.USER


def has_permission(role: str | Role | None, permission: str) -> bool:
    normalized_role = normalize_role(role)
    return permission in ROLE_PERMISSIONS[normalized_role]
