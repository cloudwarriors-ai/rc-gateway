import logging
from typing import Any, Optional

from app.clients.ringcentral import RingCentralClient
from app.schemas.webhooks import (
    CallQueueInfo,
    CallQueueDetail,
    CallQueueListResponse,
    CreateCallQueueRequest,
)

logger = logging.getLogger(__name__)

CALL_QUEUE_ENDPOINT = "/restapi/v1.0/account/~/call-queues"


class CallQueueService:
    def __init__(self, client: RingCentralClient) -> None:
        self._client = client

    async def create_call_queue(
        self, payload: CreateCallQueueRequest
    ) -> CallQueueDetail:
        body = payload.dict(by_alias=True, exclude_none=True)
        response = await self._client.post(CALL_QUEUE_ENDPOINT, json=body)
        data = response.json()
        return CallQueueDetail.parse_obj(data)

    async def list_call_queues(
        self, page: int = 1, per_page: int = 100
    ) -> CallQueueListResponse:
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        response = await self._client.get(CALL_QUEUE_ENDPOINT, params=params)
        data = response.json()
        return CallQueueListResponse.parse_obj(data)

    async def get_call_queue(self, queue_id: str) -> CallQueueDetail:
        endpoint = f"{CALL_QUEUE_ENDPOINT}/{queue_id}"
        response = await self._client.get(endpoint)
        data = response.json()
        return CallQueueDetail.parse_obj(data)

    async def update_call_queue(
        self, queue_id: str, payload: CreateCallQueueRequest
    ) -> CallQueueDetail:
        endpoint = f"{CALL_QUEUE_ENDPOINT}/{queue_id}"
        body = payload.dict(by_alias=True, exclude_none=True)
        response = await self._client.put(endpoint, json=body)
        data = response.json()
        return CallQueueDetail.parse_obj(data)

    async def delete_call_queue(self, queue_id: str) -> bool:
        endpoint = f"{CALL_QUEUE_ENDPOINT}/{queue_id}"
        try:
            await self._client.delete(endpoint)
            return True
        except Exception as e:
            logger.error(f"Failed to delete call queue {queue_id}: {e}")
            return False

    async def bulk_add_members(
        self, queue_id: str, member_ids: list[str]
    ) -> CallQueueDetail:
        endpoint = f"{CALL_QUEUE_ENDPOINT}/{queue_id}/bulk-assign"
        body = {"addedExtensionIds": member_ids}
        response = await self._client.post(endpoint, json=body)
        data = response.json()
        return CallQueueDetail.parse_obj(data)

    async def bulk_remove_members(
        self, queue_id: str, member_ids: list[str]
    ) -> CallQueueDetail:
        endpoint = f"{CALL_QUEUE_ENDPOINT}/{queue_id}/bulk-assign"
        body = {"removedExtensionIds": member_ids}
        response = await self._client.post(endpoint, json=body)
        data = response.json()
        return CallQueueDetail.parse_obj(data)

    async def get_queue_presence(self, queue_id: str) -> dict[str, Any]:
        endpoint = f"{CALL_QUEUE_ENDPOINT}/{queue_id}/presence"
        response = await self._client.get(endpoint)
        return response.json()

    async def get_queue_statistics(self, queue_id: str) -> dict[str, Any]:
        endpoint = f"/restapi/v1.0/account/~/call-monitoring-groups/{queue_id}"
        response = await self._client.get(endpoint)
        return response.json()
