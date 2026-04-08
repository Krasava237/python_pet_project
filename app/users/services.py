from app.security import Role
from app.users.auth import get_password_hash
from app.users.repositories import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def list_users(self):
        return await self.repository.list_all()

    async def get_by_id(self, user_id: int):
        return await self.repository.get_by_id(user_id)

    async def get_by_email(self, email: str):
        return await self.repository.get_by_email(email)

    async def create_user(self, email: str, password: str, role: str = Role.USER.value):
        existing_user = await self.repository.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")

        return await self.repository.create(
            email=email,
            hashed_password=get_password_hash(password),
            role=role,
        )

    async def assign_role(self, user_id: int, role: str):
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise LookupError("User not found")
        return await self.repository.update_role(user, role)

    async def ensure_bootstrap_admin(self, email: str | None, password: str | None):
        if not email or not password:
            return None

        admin_user = await self.repository.get_by_email(email)
        if admin_user:
            if admin_user.role != Role.ADMIN.value:
                admin_user = await self.repository.update_role(admin_user, Role.ADMIN.value)
            return admin_user

        if await self.repository.has_any_admin():
            return None

        return await self.repository.create(
            email=email,
            hashed_password=get_password_hash(password),
            role=Role.ADMIN.value,
        )
