from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register")
def register_user():
    return {"message": "Регистрация пользователя"}

@router.post("/login")
def login_user():
    return {"message": "Авторизация пользователя"}