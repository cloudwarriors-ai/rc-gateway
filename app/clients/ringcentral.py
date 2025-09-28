from __future__ import annotations

# pyright: reportMissingImports=false

import asyncio
import time
from typing import Any, Awaitable, Callable, Optional

import httpx

from ..core.config import RingCentralCredentials, get_settings

TOKEN_ENDPOINT = "/restapi/oauth/token"


class TokenCache:
    def __init__(self) -> None:
        self._token: Optional[str] = None
        self._expires_at: float = 0.0
        self._lock = asyncio.Lock()

    async def get(self, fetcher: Callable[[], Awaitable[tuple[str, int]]], buffer_seconds: int) -> str:
        async with self._lock:
            if self._token and time.time() < self._expires_at - buffer_seconds:
                return self._token

            token, expires_in = await fetcher()
            self._token = token
            self._expires_at = time.time() + expires_in
            return token


class RingCentralClient:
    def __init__(self, credentials: Optional[RingCentralCredentials] = None) -> None:
        self._settings = get_settings()
        self._credentials = credentials or self._settings.load_ringcentral_credentials()
        self._base_url = self._credentials.base_url.rstrip("/")
        self._token_cache = TokenCache()
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=30.0)

    async def _fetch_access_token(self) -> tuple[str, int]:
        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": self._credentials.jwt,
        }
        auth = (self._credentials.client_id, self._credentials.client_secret)

        response = await self._client.post(TOKEN_ENDPOINT, data=payload, auth=auth)
        response.raise_for_status()
        data = response.json()
        return data["access_token"], int(data.get("expires_in", self._credentials.token_cache_seconds))

    async def _get_access_token(self) -> str:
        buffer_seconds = min(60, self._credentials.token_cache_seconds // 10)
        return await self._token_cache.get(self._fetch_access_token, buffer_seconds)

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        token = await self._get_access_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        response = await self._client.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("DELETE", url, **kwargs)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "RingCentralClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
