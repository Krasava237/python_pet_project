import asyncio
import time
from dataclasses import dataclass

import httpx

from app.config import settings


ATTRIBUTION = "© OpenStreetMap contributors, via Nominatim"


@dataclass(slots=True)
class CacheEntry:
    expires_at: float
    payload: dict


class NominatimService:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.NOMINATIM_BASE_URL,
            headers={
                "User-Agent": settings.NOMINATIM_USER_AGENT,
                "Accept-Language": "ru,en;q=0.8",
            },
            timeout=settings.NOMINATIM_TIMEOUT_SECONDS,
        )
        self._cache: dict[str, CacheEntry] = {}
        self._rate_limit_lock = asyncio.Lock()
        self._last_request_at = 0.0

    async def _respect_rate_limit(self) -> None:
        async with self._rate_limit_lock:
            elapsed = time.monotonic() - self._last_request_at
            wait_time = settings.NOMINATIM_RATE_LIMIT_SECONDS - elapsed
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self._last_request_at = time.monotonic()

    def _cache_get(self, key: str) -> dict | None:
        entry = self._cache.get(key)
        if entry and entry.expires_at > time.monotonic():
            return entry.payload
        if entry:
            self._cache.pop(key, None)
        return None

    def _cache_set(self, key: str, payload: dict, ttl_seconds: float) -> dict:
        self._cache[key] = CacheEntry(
            expires_at=time.monotonic() + ttl_seconds,
            payload=payload,
        )
        return payload

    def _unavailable(self, query: str, message: str) -> dict:
        return {
            "status": "unavailable",
            "query": query,
            "provider": "Nominatim",
            "attribution": ATTRIBUTION,
            "message": message,
            "display_name": None,
            "lat": None,
            "lon": None,
            "importance": None,
        }

    async def lookup_address(self, query: str) -> dict:
        normalized_query = query.strip()
        if not normalized_query:
            return {
                "status": "not_found",
                "query": query,
                "provider": "Nominatim",
                "attribution": ATTRIBUTION,
                "message": "Address is empty",
                "display_name": None,
                "lat": None,
                "lon": None,
                "importance": None,
            }

        cache_key = normalized_query.lower()
        cached = self._cache_get(cache_key)
        if cached:
            return cached

        for attempt in range(settings.NOMINATIM_RETRY_ATTEMPTS + 1):
            try:
                await self._respect_rate_limit()
                response = await self._client.get(
                    "/search",
                    params={
                        "q": normalized_query,
                        "format": "jsonv2",
                        "limit": 1,
                        "addressdetails": 1,
                    },
                )
                if response.status_code == 200:
                    items = response.json()
                    if not items:
                        return self._cache_set(
                            cache_key,
                            {
                                "status": "not_found",
                                "query": normalized_query,
                                "provider": "Nominatim",
                                "attribution": ATTRIBUTION,
                                "message": "No matching address found",
                                "display_name": None,
                                "lat": None,
                                "lon": None,
                                "importance": None,
                            },
                            ttl_seconds=1800,
                        )

                    first = items[0]
                    return self._cache_set(
                        cache_key,
                        {
                            "status": "ok",
                            "query": normalized_query,
                            "provider": "Nominatim",
                            "attribution": ATTRIBUTION,
                            "display_name": first.get("display_name"),
                            "lat": float(first["lat"]) if "lat" in first else None,
                            "lon": float(first["lon"]) if "lon" in first else None,
                            "importance": first.get("importance"),
                            "message": None,
                        },
                        ttl_seconds=1800,
                    )

                if response.status_code in {429, 500, 502, 503, 504} and attempt < settings.NOMINATIM_RETRY_ATTEMPTS:
                    await asyncio.sleep(min(2**attempt, 2))
                    continue

                return self._cache_set(
                    cache_key,
                    self._unavailable(
                        normalized_query,
                        f"Nominatim returned HTTP {response.status_code}",
                    ),
                    ttl_seconds=60,
                )
            except httpx.HTTPError:
                if attempt < settings.NOMINATIM_RETRY_ATTEMPTS:
                    await asyncio.sleep(min(2**attempt, 2))
                    continue
                return self._cache_set(
                    cache_key,
                    self._unavailable(
                        normalized_query,
                        "Nominatim is temporarily unavailable",
                    ),
                    ttl_seconds=60,
                )

        return self._cache_set(
            cache_key,
            self._unavailable(normalized_query, "Nominatim is temporarily unavailable"),
            ttl_seconds=60,
        )
