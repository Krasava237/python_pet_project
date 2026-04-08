from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import async_session
from app.health import router as health_router
from app.pets.routers import router as pets_router
from app.seo import router as seo_router
from app.users.repositories import UserRepository
from app.users.routers import router as users_router
from app.users.services import UserService
from app.utils.files import ensure_media_dir

app = FastAPI(title="Pet Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_noindex_headers(request: Request, call_next):
    response = await call_next(request)
    # Закрываем служебные и приватные маршруты от индексации на уровне HTTP-заголовка.
    if request.url.path not in {"/robots.txt", "/sitemap.xml"} and request.url.path.startswith(
        ("/users", "/pets", "/media", "/docs", "/openapi.json")
    ):
        response.headers.setdefault("X-Robots-Tag", "noindex, nofollow")
    return response


app.mount("/media", StaticFiles(directory="media"), name="media")
app.include_router(health_router)
app.include_router(seo_router)
app.include_router(users_router)
app.include_router(pets_router)

# В тестовом режиме подключаем специальные фейки и служебные эндпоинты для e2e.
if settings.TESTING:
    # В тестовом режиме подменяем внешние интеграции детерминированными сервисами.
    from app.pets.dependencies import get_nominatim_service, get_storage_service
    from app.testing import (
        get_test_nominatim_service,
        get_test_storage_service,
        router as testing_router,
    )

    app.dependency_overrides[get_storage_service] = get_test_storage_service
    app.dependency_overrides[get_nominatim_service] = get_test_nominatim_service
    app.include_router(testing_router)


@app.on_event("startup")
async def bootstrap_admin() -> None:
    ensure_media_dir()
    async with async_session() as session:
        user_service = UserService(UserRepository(session))
        await user_service.ensure_bootstrap_admin(
            settings.BOOTSTRAP_ADMIN_EMAIL,
            settings.BOOTSTRAP_ADMIN_PASSWORD,
        )
