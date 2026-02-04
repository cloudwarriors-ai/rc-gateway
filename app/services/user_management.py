import logging
from typing import Any, Optional

from app.clients.ringcentral import RingCentralClient
from app.schemas.ivr import (
    CallForwardingInfo,
    PresenceStatus,
    DeviceInfo,
    AssignDeviceRequest,
    VoicemailSettings,
    CallHandlingRule,
    CreateCallHandlingRuleRequest,
    ForwardingNumber,
)

logger = logging.getLogger(__name__)

EXTENSION_BASE = "/restapi/v1.0/account/~/extension"


class UserManagementService:
    def __init__(self, client: RingCentralClient) -> None:
        self._client = client

    async def activate_user(self, extension_id: str) -> dict[str, Any]:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/activate"
        response = await self._client.post(endpoint)
        return response.json()

    async def reset_password(self, extension_id: str) -> dict[str, str]:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/password-reset"
        response = await self._client.post(endpoint)
        return {"status": "password_reset_sent"}

    async def get_call_forwarding(self, extension_id: str) -> CallForwardingInfo:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/forwarding-number"
        response = await self._client.get(endpoint)
        data = response.json()
        return CallForwardingInfo.parse_obj(data)

    async def update_call_forwarding(
        self, extension_id: str, payload: CallForwardingInfo
    ) -> CallForwardingInfo:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/forwarding-number"
        body = payload.dict(by_alias=True, exclude_none=True)
        response = await self._client.put(endpoint, json=body)
        data = response.json()
        return CallForwardingInfo.parse_obj(data)

    async def add_forwarding_number(
        self, extension_id: str, forwarding_number: ForwardingNumber
    ) -> ForwardingNumber:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/forwarding-number"
        body = forwarding_number.dict(by_alias=True, exclude_none=True)
        response = await self._client.post(endpoint, json=body)
        data = response.json()
        return ForwardingNumber.parse_obj(data)

    async def get_presence(self, extension_id: str) -> PresenceStatus:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/presence"
        response = await self._client.get(endpoint)
        data = response.json()
        return PresenceStatus.parse_obj(data)

    async def update_presence(
        self, extension_id: str, status: PresenceStatus
    ) -> PresenceStatus:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/presence"
        body = status.dict(by_alias=True, exclude_none=True)
        response = await self._client.put(endpoint, json=body)
        data = response.json()
        return PresenceStatus.parse_obj(data)

    async def list_devices(self, extension_id: str) -> list[DeviceInfo]:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/device"
        response = await self._client.get(endpoint)
        data = response.json()
        return [DeviceInfo.parse_obj(device) for device in data.get("records", [])]

    async def assign_device(
        self, extension_id: str, request: AssignDeviceRequest
    ) -> DeviceInfo:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/device"
        body = request.dict(by_alias=True, exclude_none=True)
        response = await self._client.post(endpoint, json=body)
        data = response.json()
        return DeviceInfo.parse_obj(data)

    async def get_voicemail_settings(self, extension_id: str) -> VoicemailSettings:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/voicemail-settings"
        response = await self._client.get(endpoint)
        data = response.json()
        return VoicemailSettings.parse_obj(data)

    async def update_voicemail_settings(
        self, extension_id: str, settings: VoicemailSettings
    ) -> VoicemailSettings:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/voicemail-settings"
        body = settings.dict(by_alias=True, exclude_none=True)
        response = await self._client.put(endpoint, json=body)
        data = response.json()
        return VoicemailSettings.parse_obj(data)

    async def list_call_handling_rules(
        self, extension_id: str
    ) -> list[CallHandlingRule]:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/answering-rule"
        response = await self._client.get(endpoint)
        data = response.json()
        return [CallHandlingRule.parse_obj(rule) for rule in data.get("records", [])]

    async def create_call_handling_rule(
        self, extension_id: str, rule: CreateCallHandlingRuleRequest
    ) -> CallHandlingRule:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/answering-rule"
        body = rule.dict(by_alias=True, exclude_none=True)
        response = await self._client.post(endpoint, json=body)
        data = response.json()
        return CallHandlingRule.parse_obj(data)

    async def update_call_handling_rule(
        self, extension_id: str, rule_id: str, rule: CreateCallHandlingRuleRequest
    ) -> CallHandlingRule:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/answering-rule/{rule_id}"
        body = rule.dict(by_alias=True, exclude_none=True)
        response = await self._client.put(endpoint, json=body)
        data = response.json()
        return CallHandlingRule.parse_obj(data)

    async def delete_call_handling_rule(
        self, extension_id: str, rule_id: str
    ) -> bool:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/answering-rule/{rule_id}"
        try:
            await self._client.delete(endpoint)
            return True
        except Exception as e:
            logger.error(f"Failed to delete call handling rule {rule_id}: {e}")
            return False

    async def get_business_hours(self, extension_id: str) -> dict[str, Any]:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/business-hours"
        response = await self._client.get(endpoint)
        return response.json()

    async def update_business_hours(
        self, extension_id: str, schedule: dict[str, Any]
    ) -> dict[str, Any]:
        endpoint = f"{EXTENSION_BASE}/{extension_id}/business-hours"
        response = await self._client.put(endpoint, json=schedule)
        return response.json()
