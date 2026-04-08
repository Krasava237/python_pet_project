from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DATABASE_URL_OVERRIDE: str | None = None

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    BOOTSTRAP_ADMIN_EMAIL: str | None = "admin@local.dev"
    BOOTSTRAP_ADMIN_PASSWORD: str | None = "Admin123!"

    API_BASE_URL: str = "http://localhost:8001"
    PUBLIC_APP_URL: str = "http://localhost:5173"
    FRONTEND_ORIGINS: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:4173,"
        "http://127.0.0.1:4173"
    )

    STORAGE_ENABLED: bool = True
    STORAGE_ENDPOINT_URL: str = "http://127.0.0.1:9000"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_BUCKET: str = "pet-finder-files"
    STORAGE_REGION: str = "us-east-1"
    STORAGE_USE_SSL: bool = False
    STORAGE_MAX_FILE_SIZE: int = 5 * 1024 * 1024
    STORAGE_PRESIGNED_URL_TTL_SECONDS: int = 600

    NOMINATIM_BASE_URL: str = "https://nominatim.openstreetmap.org"
    NOMINATIM_USER_AGENT: str = "pet-finder-labs/1.0"
    NOMINATIM_TIMEOUT_SECONDS: float = 5.0
    NOMINATIM_RETRY_ATTEMPTS: int = 2
    NOMINATIM_RATE_LIMIT_SECONDS: float = 1.0

    SEO_SITE_NAME: str = "Pet Finder"
    TESTING: bool = False

    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_URL_OVERRIDE:
            return self.DATABASE_URL_OVERRIDE
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def frontend_origins(self) -> list[str]:
        return [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",") if origin.strip()]


settings = Settings()
