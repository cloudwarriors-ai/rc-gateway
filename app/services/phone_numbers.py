import logging
from typing import Any, Optional

from app.clients.ringcentral import RingCentralClient
from app.schemas.webhooks import (
    AvailableNumbersRequest,
    AvailableNumbersResponse,
    PhoneNumberInfo,
)

logger = logging.getLogger(__name__)

PHONE_NUMBER_ENDPOINT = "/restapi/v1.0/account/~/phone-number"
AVAILABLE_NUMBERS_ENDPOINT = "/restapi/v1.0/number-pool/lookup"


class PhoneNumberService:
    def __init__(self, client: RingCentralClient) -> None:
        self._client = client

    async def search_available_numbers(
        self, request: AvailableNumbersRequest
    ) -> AvailableNumbersResponse:
        params = request.dict(by_alias=True, exclude_none=True)
        response = await self._client.get(AVAILABLE_NUMBERS_ENDPOINT, params=params)
        data = response.json()
        return AvailableNumbersResponse.parse_obj(data)

    async def list_account_phone_numbers(
        self, page: int = 1, per_page: int = 100
    ) -> list[PhoneNumberInfo]:
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        response = await self._client.get(PHONE_NUMBER_ENDPOINT, params=params)
        data = response.json()
        return [PhoneNumberInfo.parse_obj(record) for record in data.get("records", [])]

    async def get_phone_number(self, phone_number_id: str) -> PhoneNumberInfo:
        endpoint = f"{PHONE_NUMBER_ENDPOINT}/{phone_number_id}"
        response = await self._client.get(endpoint)
        data = response.json()
        return PhoneNumberInfo.parse_obj(data)
