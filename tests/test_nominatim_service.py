import unittest

import httpx

from app.integrations.nominatim import NominatimService


class FakeResponse:
    def __init__(self, status_code: int, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.calls = 0

    async def get(self, *args, **kwargs):
        self.calls += 1
        return self.response


class ErrorClient:
    async def get(self, *args, **kwargs):
        raise httpx.ConnectError("boom")


class NominatimServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_lookup_address_normalizes_success_response_and_uses_cache(self):
        service = NominatimService()
        service._client = FakeClient(
            FakeResponse(
                200,
                [
                    {
                        "display_name": "Moscow Kremlin",
                        "lat": "55.7516212",
                        "lon": "37.618122",
                        "importance": 0.9,
                    }
                ],
            )
        )

        first = await service.lookup_address("Moscow Kremlin")
        second = await service.lookup_address("Moscow Kremlin")

        self.assertEqual(first["status"], "ok")
        self.assertEqual(first["display_name"], "Moscow Kremlin")
        self.assertEqual(first["lat"], 55.7516212)
        self.assertEqual(service._client.calls, 1)
        self.assertEqual(first, second)

    async def test_lookup_address_returns_unavailable_after_http_error(self):
        service = NominatimService()
        service._client = ErrorClient()

        result = await service.lookup_address("Moscow Kremlin")

        self.assertEqual(result["status"], "unavailable")
        self.assertIn("temporarily unavailable", result["message"])


if __name__ == "__main__":
    unittest.main()
