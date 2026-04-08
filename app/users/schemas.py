from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.security import Role


class SUserBase(BaseModel):
    email: EmailStr


class SUserCreate(SUserBase):
    password: str


class SUserLogin(BaseModel):
    email: EmailStr
    password: str


class SUserRoleUpdate(BaseModel):
    role: Role


class STokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SUserResponse(SUserBase):
    id: int
    role: Role
    created_at: datetime

    class Config:
        from_attributes = True
