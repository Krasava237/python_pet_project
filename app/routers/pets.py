from fastapi import APIRouter

router = APIRouter(prefix="/pets", tags=["Pets"])

@router.get("/")
def get_pets():
    return {"message": "Список питомцев"}

@router.post("/add")
def add_pet():
    return {"message": "Добавление питомца"}