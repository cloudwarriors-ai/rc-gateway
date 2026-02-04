import logging
from typing import Any, Optional

from app.clients.ringcentral import RingCentralClient
from app.schemas.ivr import (
    CreateIVRRequest,
    IVRDetail,
    IVRListResponse,
)

logger = logging.getLogger(__name__)

IVR_ENDPOINT = "/restapi/v1.0/account/~/ivr-menus"


class IVRService:
    def __init__(self, client: RingCentralClient) -> None:
        self._client = client

    async def create_ivr(self, payload: CreateIVRRequest) -> IVRDetail:
        body = payload.dict(by_alias=True, exclude_none=True)
        response = await self._client.post(IVR_ENDPOINT, json=body)
        data = response.json()
        return IVRDetail.parse_obj(data)

    async def list_ivrs(
        self, page: int = 1, per_page: int = 100
    ) -> IVRListResponse:
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        response = await self._client.get(IVR_ENDPOINT, params=params)
        data = response.json()
        return IVRListResponse.parse_obj(data)

    async def get_ivr(self, ivr_id: str) -> IVRDetail:
        endpoint = f"{IVR_ENDPOINT}/{ivr_id}"
        response = await self._client.get(endpoint)
        data = response.json()
        return IVRDetail.parse_obj(data)

    async def update_ivr(
        self, ivr_id: str, payload: CreateIVRRequest
    ) -> IVRDetail:
        endpoint = f"{IVR_ENDPOINT}/{ivr_id}"
        body = payload.dict(by_alias=True, exclude_none=True)
        response = await self._client.put(endpoint, json=body)
        data = response.json()
        return IVRDetail.parse_obj(data)

    async def delete_ivr(self, ivr_id: str) -> bool:
        endpoint = f"{IVR_ENDPOINT}/{ivr_id}"
        try:
            await self._client.delete(endpoint)
            return True
        except Exception as e:
            logger.error(f"Failed to delete IVR {ivr_id}: {e}")
            return False
