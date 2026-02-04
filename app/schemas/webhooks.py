from typing import Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class WebhookSubscriptionRequest(BaseModel):
    event_filters: list[str] = Field(alias="eventFilters")
    delivery_mode: dict[str, str] = Field(alias="deliveryMode")
    expires_in: int = Field(default=604800, alias="expiresIn")


class WebhookSubscriptionResponse(BaseModel):
    id: str
    uri: str
    event_filters: list[str] = Field(alias="eventFilters")
    delivery_mode: dict[str, str] = Field(alias="deliveryMode")
    status: str
    creation_time: datetime = Field(alias="creationTime")
    expiration_time: datetime = Field(alias="expirationTime")


class WebhookEvent(BaseModel):
    uuid: str
    event: str
    timestamp: datetime
    subscription_id: str = Field(alias="subscriptionId")
    body: dict[str, Any]
    
    class Config:
        populate_by_name = True


class WebhookValidationRequest(BaseModel):
    validation_token: str = Field(alias="validationToken")


class WebhookValidationResponse(BaseModel):
    validation_token: str = Field(alias="validationToken")


class CallQueueInfo(BaseModel):
    id: str
    name: str
    extension_number: str = Field(alias="extensionNumber")


class CallQueueMember(BaseModel):
    id: str
    extension_number: str = Field(alias="extensionNumber")


class CreateCallQueueRequest(BaseModel):
    name: str
    extension_number: str | None = Field(default=None, alias="extensionNumber")
    members: list[CallQueueMember] | None = None


class CallQueueDetail(BaseModel):
    id: str
    uri: str
    name: str
    extension_number: str = Field(alias="extensionNumber")
    status: str
    members: list[CallQueueMember] | None = None


class CallQueueListResponse(BaseModel):
    records: list[CallQueueInfo]
    paging: dict[str, Any]
    navigation: dict[str, Any]


class PhoneNumberInfo(BaseModel):
    phone_number: str = Field(alias="phoneNumber")
    type: str
    usage_type: str = Field(alias="usageType")
    features: list[str] | None = None
    status: str | None = None


class AvailableNumbersRequest(BaseModel):
    area_code: str | None = Field(default=None, alias="areaCode")
    country_id: str = Field(default="1", alias="countryId")
    per_page: int = Field(default=10, alias="perPage")


class AvailableNumbersResponse(BaseModel):
    records: list[PhoneNumberInfo]
    paging: dict[str, Any]
    navigation: dict[str, Any]


class CallLogRecord(BaseModel):
    id: str
    uri: str
    session_id: str = Field(alias="sessionId")
    start_time: datetime = Field(alias="startTime")
    duration: int
    type: str
    direction: str
    action: str | None = None
    result: str | None = None
    from_info: dict[str, Any] = Field(alias="from")
    to_info: dict[str, Any] = Field(alias="to")
    recording: dict[str, Any] | None = None


class CallLogResponse(BaseModel):
    records: list[CallLogRecord]
    paging: dict[str, Any]
    navigation: dict[str, Any]
