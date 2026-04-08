import re
import unicodedata
from xml.sax.saxutils import escape

from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.database import async_session
from app.pets.repositories import PetRepository

router = APIRouter(tags=["SEO"])


def _slugify(value: str | None) -> str:
    source = value or "pet"
    normalized = unicodedata.normalize("NFKD", source).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    return slug or "pet"


def _build_public_url(path: str) -> str:
    base_url = settings.PUBLIC_APP_URL.rstrip("/")
    return f"{base_url}{path}"


def _build_pet_public_path(pet) -> str:
    return f"/pets/{pet.id}-{_slugify(pet.name or pet.type)}"


@router.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
async def robots_txt() -> str:
    return "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /login",
            "Disallow: /me",
            "Disallow: /admin",
            "Disallow: /users",
            "Disallow: /docs",
            "Disallow: /openapi.json",
            "",
            f"Sitemap: {settings.API_BASE_URL.rstrip('/')}/sitemap.xml",
        ]
    )


@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap_xml() -> Response:
    async with async_session() as session:
        repository = PetRepository(session)
        pets = await repository.list_for_sitemap()

    urls = [
        (_build_public_url("/"), "1.0"),
        (_build_public_url("/pets"), "0.9"),
    ]
    urls.extend((_build_public_url(_build_pet_public_path(pet)), "0.8") for pet in pets)

    chunks = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, priority in urls:
        chunks.append("<url>")
        chunks.append(f"<loc>{escape(loc)}</loc>")
        chunks.append(f"<priority>{priority}</priority>")
        chunks.append("</url>")
    chunks.append("</urlset>")

    return Response("".join(chunks), media_type="application/xml")
