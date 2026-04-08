from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import RefreshSession, User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(self) -> list[User]:
        result = await self.session.execute(select(User).order_by(User.id))
        return list(result.scalars().all())

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, *, email: str, hashed_password: str, role: str) -> User:
        user = User(email=email, hashed_password=hashed_password, role=role)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_role(self, user: User, role: str) -> User:
        user.role = role
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def has_any_admin(self) -> bool:
        result = await self.session.execute(
            select(func.count()).select_from(User).where(User.role == "admin")
        )
        return bool(result.scalar_one())


class RefreshSessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        user_id: int,
        jti: str,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshSession:
        refresh_session = RefreshSession(
            user_id=user_id,
            jti=jti,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.session.add(refresh_session)
        await self.session.commit()
        await self.session.refresh(refresh_session)
        return refresh_session

    async def get_by_jti(self, jti: str) -> RefreshSession | None:
        result = await self.session.execute(
            select(RefreshSession).where(RefreshSession.jti == jti)
        )
        return result.scalar_one_or_none()

    async def revoke(self, refresh_session: RefreshSession) -> RefreshSession:
        if refresh_session.revoked_at is None:
            refresh_session.revoked_at = datetime.now(timezone.utc)
            await self.session.commit()
            await self.session.refresh(refresh_session)
        return refresh_session
