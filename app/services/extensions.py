from __future__ import annotations

from typing import Any, Optional

from app.clients.ringcentral import RingCentralClient
from app.schemas.ringcentral import (
    CreateExtensionRequest,
    ExtensionListResponse,
    ExtensionSummary,
    ExtensionUpdateRequest,
    ExtensionDetail,
)

EXTENSION_ENDPOINT = "/restapi/v1.0/account/~/extension"


class ExtensionService:
    def __init__(self, client: RingCentralClient) -> None:
        self._client = client

    async def create_extension(self, payload: CreateExtensionRequest) -> ExtensionSummary:
        body = payload.dict(by_alias=True, exclude_none=True)
        response = await self._client.post(EXTENSION_ENDPOINT, json=body)
        data = response.json()
        return ExtensionSummary.parse_obj(data)

    async def list_extensions(
        self, page: int = 1, per_page: int = 100, status: Optional[str] = None
    ) -> ExtensionListResponse:
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        if status:
            params["status"] = status

        response = await self._client.get(EXTENSION_ENDPOINT, params=params)
        data = response.json()
        return ExtensionListResponse.parse_obj(data)

    async def list_users(
        self, page: int = 1, per_page: int = 100, status: Optional[str] = None
    ) -> ExtensionListResponse:
        # Get all extensions with a large page size to filter for users
        # Since we need to filter by type=User, we fetch more than requested
        fetch_size = min(1000, per_page * 10)  # Fetch more to account for filtering
        
        params: dict[str, Any] = {"page": page, "perPage": fetch_size}
        if status:
            params["status"] = status

        response = await self._client.get(EXTENSION_ENDPOINT, params=params)
        data = response.json()
        full_response = ExtensionListResponse.parse_obj(data)
        
        # Filter for User type extensions only
        user_records = []
        for ext in full_response.records:
            ext_type = ext.type
            if isinstance(ext_type, str):
                is_user = ext_type == "User"
            else:
                # Handle enum types
                is_user = str(ext_type) == "User"
            
            if is_user:
                user_records.append(ext)
        
        # Apply pagination to filtered results
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_users = user_records[start_idx:end_idx]
        
        # Update response with filtered data
        filtered_response = ExtensionListResponse(
            records=paginated_users,
            paging=full_response.paging,
            navigation=full_response.navigation
        )
        
        return filtered_response

    async def get_extension(self, extension_id: str) -> ExtensionDetail:
        """Get detailed extension information by ID."""
        endpoint = f"{EXTENSION_ENDPOINT}/{extension_id}"
        response = await self._client.get(endpoint)
        data = response.json()
        return ExtensionDetail.parse_obj(data)

    async def update_extension(
        self, extension_id: str, payload: ExtensionUpdateRequest
    ) -> ExtensionDetail:
        """Update an extension's properties."""
        endpoint = f"{EXTENSION_ENDPOINT}/{extension_id}"
        body = payload.dict(by_alias=True, exclude_none=True)
        response = await self._client.put(endpoint, json=body)
        data = response.json()
        return ExtensionDetail.parse_obj(data)

    async def update_extension_number(
        self, extension_id: str, new_extension_number: str
    ) -> ExtensionDetail:
        """Update an extension's number."""
        payload = ExtensionUpdateRequest(extension_number=new_extension_number)
        return await self.update_extension(extension_id, payload)
