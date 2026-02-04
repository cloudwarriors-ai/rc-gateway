import hashlib
import hmac
import logging
from typing import Any

from app.clients.ringcentral import RingCentralClient
from app.schemas.webhooks import (
    WebhookSubscriptionRequest,
    WebhookSubscriptionResponse,
    WebhookEvent,
)

logger = logging.getLogger(__name__)

WEBHOOK_ENDPOINT = "/restapi/v1.0/subscription"


class WebhookService:
    def __init__(self, client: RingCentralClient) -> None:
        self._client = client

    async def create_subscription(
        self, payload: WebhookSubscriptionRequest
    ) -> WebhookSubscriptionResponse:
        body = payload.dict(by_alias=True, exclude_none=True)
        response = await self._client.post(WEBHOOK_ENDPOINT, json=body)
        data = response.json()
        return WebhookSubscriptionResponse.parse_obj(data)

    async def list_subscriptions(self) -> list[WebhookSubscriptionResponse]:
        response = await self._client.get(WEBHOOK_ENDPOINT)
        data = response.json()
        return [
            WebhookSubscriptionResponse.parse_obj(record)
            for record in data.get("records", [])
        ]

    async def get_subscription(self, subscription_id: str) -> WebhookSubscriptionResponse:
        endpoint = f"{WEBHOOK_ENDPOINT}/{subscription_id}"
        response = await self._client.get(endpoint)
        data = response.json()
        return WebhookSubscriptionResponse.parse_obj(data)

    async def delete_subscription(self, subscription_id: str) -> bool:
        endpoint = f"{WEBHOOK_ENDPOINT}/{subscription_id}"
        try:
            await self._client.delete(endpoint)
            return True
        except Exception as e:
            logger.error(f"Failed to delete subscription {subscription_id}: {e}")
            return False

    async def renew_subscription(self, subscription_id: str) -> WebhookSubscriptionResponse:
        endpoint = f"{WEBHOOK_ENDPOINT}/{subscription_id}/renew"
        response = await self._client.post(endpoint)
        data = response.json()
        return WebhookSubscriptionResponse.parse_obj(data)

    @staticmethod
    def validate_signature(
        body: bytes, 
        signature: str, 
        validation_token: str
    ) -> bool:
        expected = hmac.new(
            validation_token.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)

    @staticmethod
    def process_event(event: WebhookEvent) -> dict[str, Any]:
        logger.info(f"Processing webhook event: {event.event} (UUID: {event.uuid})")
        
        event_type = event.event
        
        if "extension" in event_type.lower():
            logger.info(f"Extension event: {event.body}")
        elif "message" in event_type.lower():
            logger.info(f"Message event: {event.body}")
        elif "presence" in event_type.lower():
            logger.info(f"Presence event: {event.body}")
        else:
            logger.info(f"Unknown event type: {event_type}")
        
        return {
            "status": "processed",
            "event_id": event.uuid,
            "event_type": event_type
        }
