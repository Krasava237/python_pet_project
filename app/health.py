from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from app.database import async_session

router = APIRouter(tags=["Health"])


@router.get("/health/live", include_in_schema=False)
async def health_live() -> dict[str, str]:
    # Liveness показывает, что процесс жив и принимает HTTP-запросы.
    return {"status": "ok"}


@router.get("/health/ready", include_in_schema=False)
async def health_ready() -> dict[str, str]:
    try:
        # Проверяем, что приложение видит базу данных до приема пользовательского трафика.
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from exc

    return {"status": "ready", "database": "ok"}
