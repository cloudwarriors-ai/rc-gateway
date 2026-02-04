import logging
from datetime import datetime
from typing import Any, Optional

from app.clients.ringcentral import RingCentralClient
from app.schemas.webhooks import CallLogRecord, CallLogResponse

logger = logging.getLogger(__name__)

CALL_LOG_ENDPOINT = "/restapi/v1.0/account/~/call-log"
EXTENSION_CALL_LOG_ENDPOINT = "/restapi/v1.0/account/~/extension/{}/call-log"


class AnalyticsService:
    def __init__(self, client: RingCentralClient) -> None:
        self._client = client

    async def get_call_logs(
        self,
        page: int = 1,
        per_page: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        direction: Optional[str] = None,
    ) -> CallLogResponse:
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        
        if date_from:
            params["dateFrom"] = date_from.isoformat()
        if date_to:
            params["dateTo"] = date_to.isoformat()
        if direction:
            params["direction"] = direction

        response = await self._client.get(CALL_LOG_ENDPOINT, params=params)
        data = response.json()
        return CallLogResponse.parse_obj(data)

    async def get_extension_call_logs(
        self,
        extension_id: str,
        page: int = 1,
        per_page: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> CallLogResponse:
        endpoint = EXTENSION_CALL_LOG_ENDPOINT.format(extension_id)
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        
        if date_from:
            params["dateFrom"] = date_from.isoformat()
        if date_to:
            params["dateTo"] = date_to.isoformat()

        response = await self._client.get(endpoint, params=params)
        data = response.json()
        return CallLogResponse.parse_obj(data)

    async def get_call_log_record(self, record_id: str) -> CallLogRecord:
        endpoint = f"{CALL_LOG_ENDPOINT}/{record_id}"
        response = await self._client.get(endpoint)
        data = response.json()
        return CallLogRecord.parse_obj(data)
