import asyncio
import importlib
import os
from pathlib import Path

import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient


def _load_test_environment() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env.test"
    for key, value in dotenv_values(env_path).items():
        if value is not None:
            # Test config must win over CI job env so pytest is reproducible everywhere.
            os.environ[key] = value


# Сначала подготавливаем test-env, и только потом импортируем приложение.
_load_test_environment()

database = importlib.import_module("app.database")
Base = database.Base
engine = database.engine
app = importlib.import_module("app.main").app


async def _recreate_schema() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


async def _dispose_engine() -> None:
    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def prepare_database() -> None:
    asyncio.run(_recreate_schema())
    yield
    asyncio.run(_dispose_engine())


@pytest.fixture
def client(prepare_database: None) -> TestClient:
    with TestClient(app) as test_client:
        # Каждый тест стартует с чистого состояния, чтобы не зависеть от порядка запуска.
        response = test_client.post("/_test/reset")
        assert response.status_code == 204
        yield test_client
