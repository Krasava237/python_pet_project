import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
load_dotenv(ROOT_DIR / ".env.test", override=True)


async def prepare_schema() -> None:
    import app.pets.models  # noqa: F401
    import app.users.models  # noqa: F401

    from app.database import Base, engine

    # Для e2e нам нужен готовый schema-only контур, а сами данные тесты сбрасывают через /_test/reset.
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    import asyncio

    asyncio.run(prepare_schema())
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001)
