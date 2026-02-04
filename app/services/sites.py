from __future__ import annotations

from typing import Any, Optional

from app.clients.ringcentral import RingCentralClient
from app.schemas.ringcentral import (
    CreateSiteRequest,
    SiteListResponse,
    SiteSummary,
    SiteDetail,
    SiteUpdateRequest,
)

SITE_ENDPOINT = "/restapi/v1.0/account/~/sites"


class SiteService:
    def __init__(self, client: RingCentralClient) -> None:
        self._client = client

    async def create_site(self, payload: CreateSiteRequest) -> SiteDetail:
        """Create a new site/location."""
        body = payload.dict(by_alias=True, exclude_none=True)
        response = await self._client.post(SITE_ENDPOINT, json=body)
        data = response.json()
        return SiteDetail.parse_obj(data)

    async def list_sites(
        self, page: int = 1, per_page: int = 100
    ) -> SiteListResponse:
        """List all sites/locations."""
        params: dict[str, Any] = {"page": page, "perPage": per_page}

        response = await self._client.get(SITE_ENDPOINT, params=params)
        data = response.json()
        return SiteListResponse.parse_obj(data)

    async def get_site(self, site_id: str) -> SiteDetail:
        """Get detailed site information by ID."""
        endpoint = f"{SITE_ENDPOINT}/{site_id}"
        response = await self._client.get(endpoint)
        data = response.json()
        return SiteDetail.parse_obj(data)

    async def update_site(
        self, site_id: str, payload: SiteUpdateRequest
    ) -> SiteDetail:
        """Update a site's properties."""
        endpoint = f"{SITE_ENDPOINT}/{site_id}"
        body = payload.dict(by_alias=True, exclude_none=True)
        response = await self._client.put(endpoint, json=body)
        data = response.json()
        return SiteDetail.parse_obj(data)

    async def delete_site(self, site_id: str) -> bool:
        """Delete a site/location."""
        endpoint = f"{SITE_ENDPOINT}/{site_id}"
        response = await self._client.delete(endpoint)
        return response.status_code == 204