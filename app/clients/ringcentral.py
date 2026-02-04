from __future__ import annotations

import asyncio
import time
from typing import Any, Awaitable, Callable, Optional
import logging

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from ..core.cache import get_cache
from ..core.config import RingCentralCredentials, get_settings

TOKEN_ENDPOINT = "/restapi/oauth/token"
logger = logging.getLogger(__name__)


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


class RateLimitError(Exception):
    pass


class CircuitBreakerError(Exception):
    pass


class RingCentralClient:
    def __init__(self, credentials: Optional[RingCentralCredentials] = None) -> None:
        self._settings = get_settings()
        self._credentials = credentials or self._settings.load_ringcentral_credentials()
        self._base_url = self._credentials.base_url.rstrip("/")
        self._token_cache = TokenCache()
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=30.0)
        self._circuit_breaker_failures = 0
        self._circuit_breaker_open_until = 0.0
        self._circuit_breaker_threshold = 5
        self._circuit_breaker_timeout = 60
        self._cache = get_cache()

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

    def _check_circuit_breaker(self) -> None:
        if time.time() < self._circuit_breaker_open_until:
            raise CircuitBreakerError(
                f"Circuit breaker open until {self._circuit_breaker_open_until}"
            )
        if self._circuit_breaker_failures >= self._circuit_breaker_threshold:
            self._circuit_breaker_open_until = time.time() + self._circuit_breaker_timeout
            logger.warning(
                f"Circuit breaker opened for {self._circuit_breaker_timeout}s after "
                f"{self._circuit_breaker_failures} failures"
            )
            raise CircuitBreakerError("Circuit breaker opened due to repeated failures")

    def _record_success(self) -> None:
        self._circuit_breaker_failures = max(0, self._circuit_breaker_failures - 1)

    def _record_failure(self) -> None:
        self._circuit_breaker_failures += 1

    async def _handle_rate_limit(self, response: httpx.Response) -> None:
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "60"))
            logger.warning(f"Rate limit hit, waiting {retry_after}s")
            await asyncio.sleep(retry_after)
            raise RateLimitError(f"Rate limited, retry after {retry_after}s")

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        # Check cache for GET requests
        cache_key = None
        if method.upper() == "GET":
            cache_key = f"rc:{method}:{url}:{str(sorted(kwargs.items()))}"
            cached = self._cache.get(cache_key)
            if cached:
                # Create a mock response from cache
                import httpx
                response = httpx.Response(200, json=cached)
                return response

        self._check_circuit_breaker()

        token = await self._get_access_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"

        try:
            response = await self._client.request(method, url, headers=headers, **kwargs)

            if response.status_code == 429:
                await self._handle_rate_limit(response)

            response.raise_for_status()
            self._record_success()

            # Cache successful GET responses
            if method.upper() == "GET" and cache_key and response.status_code == 200:
                try:
                    data = response.json()
                    self._cache.set(cache_key, data)
                except Exception:
                    pass  # Skip caching if not JSON

            return response
        except httpx.HTTPStatusError as e:
            self._record_failure()
            logger.error(f"HTTP error {e.response.status_code} for {method} {url}")
            raise
        except Exception as e:
            self._record_failure()
            logger.error(f"Request failed for {method} {url}: {str(e)}")
            raise

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
