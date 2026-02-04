from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class IVRPrompt(BaseModel):
    mode: Literal["Audio", "TextToSpeech"] = "Audio"
    audio_id: Optional[str] = Field(default=None, alias="audio")
    text: Optional[str] = None


class IVRMenuAction(BaseModel):
    action: Literal["Connect", "Voicemail", "Repeat", "ReturnToRoot", "ReturnToPrevious", "ReturnToTopLevelMenu", "DoNothing"]
    extension: Optional[dict[str, str]] = None
    phone_number: Optional[str] = Field(default=None, alias="phoneNumber")


class IVRMenuKey(BaseModel):
    key: str
    action: IVRMenuAction


class IVRMenu(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    prompt: Optional[IVRPrompt] = None
    keys: list[IVRMenuKey] = []


class CreateIVRRequest(BaseModel):
    name: str
    extension_number: Optional[str] = Field(default=None, alias="extensionNumber")
    prompt: Optional[IVRPrompt] = None
    keys: list[IVRMenuKey] = []


class IVRDetail(BaseModel):
    id: str
    uri: str
    extension_number: str = Field(alias="extensionNumber")
    name: str
    status: str
    prompt: Optional[IVRPrompt] = None
    site: Optional[dict[str, Any]] = None


class IVRListResponse(BaseModel):
    records: list[IVRDetail]
    paging: dict[str, Any]
    navigation: dict[str, Any]


class BusinessHoursSchedule(BaseModel):
    weekday_hours: Optional[dict[str, Any]] = Field(default=None, alias="weekDay")
    saturday_hours: Optional[dict[str, Any]] = Field(default=None, alias="saturday")
    sunday_hours: Optional[dict[str, Any]] = Field(default=None, alias="sunday")


class CallHandlingRule(BaseModel):
    id: Optional[str] = None
    uri: Optional[str] = None
    enabled: bool = True
    type: Literal["BusinessHours", "AfterHours", "Custom"] = "BusinessHours"
    forwarding: Optional[dict[str, Any]] = None
    greetings: Optional[list[dict[str, Any]]] = None


class CreateCallHandlingRuleRequest(BaseModel):
    type: Literal["BusinessHours", "AfterHours", "Custom"]
    enabled: bool = True
    forwarding: Optional[dict[str, Any]] = None
    greetings: Optional[list[dict[str, Any]]] = None


class ForwardingNumber(BaseModel):
    phone_number: str = Field(alias="phoneNumber")
    label: Optional[str] = None
    type: Literal["Home", "Mobile", "Work", "PhoneLine", "Outage", "Other", "BusinessMobilePhone", "ExternalCarrier", "ExtensionApps"] = "Other"
    flip_number: Optional[str] = Field(default=None, alias="flipNumber")


class CallForwardingInfo(BaseModel):
    notify_mods_on_missed_call: bool = Field(default=True, alias="notifyModsOnMissedCall")
    notify_admin_on_missed_call: bool = Field(default=False, alias="notifyAdminOnMissedCall")
    soft_phone_ring_type: Literal["Delayed", "Softphone", "None"] = Field(default="Delayed", alias="softPhoneRingType")
    ring_count: int = Field(default=4, ge=2, le=10, alias="ringCount")
    rules: list[CallHandlingRule] = []


class PresenceStatus(BaseModel):
    user_status: Literal["Offline", "Busy", "Available"] = Field(alias="userStatus")
    dnd_status: Literal["TakeAllCalls", "DoNotAcceptAnyCalls", "DoNotAcceptDepartmentCalls", "TakeDepartmentCallsOnly"] = Field(alias="dndStatus")
    message: Optional[str] = None
    allow_see_my_presence: bool = Field(default=True, alias="allowSeeMyPresence")
    ring_on_monitored_call: bool = Field(default=False, alias="ringOnMonitoredCall")
    pickup_call_on_hold: bool = Field(default=False, alias="pickUpCallsOnHold")


class DeviceInfo(BaseModel):
    id: str
    uri: str
    sku: str
    type: str
    name: str
    serial: Optional[str] = None
    status: Literal["Online", "Offline"]
    extension: Optional[dict[str, str]] = None


class AssignDeviceRequest(BaseModel):
    device_id: str = Field(alias="deviceId")
    emergency_address_id: Optional[str] = Field(default=None, alias="emergencyAddressId")


class VoicemailSettings(BaseModel):
    enabled: bool = True
    recipient_id: Optional[str] = Field(default=None, alias="recipient")
    pin: Optional[str] = None


class GreetingInfo(BaseModel):
    type: Literal["Introductory", "Announcement", "ConnectingMessage", "ConnectingAudio", "Voicemail", "Unavailable", "HoldMusic", "PronouncedName", "TemplateGreeting", "Company"]
    usage_type: Literal["UserExtensionAnsweringRule", "ExtensionAnsweringRule", "DepartmentExtensionAnsweringRule", "CompanyAnsweringRule", "CompanyAfterHoursAnsweringRule", "VoicemailExtensionAnsweringRule", "AnnouncementExtensionAnsweringRule", "SharedLinesGroupAnsweringRule"] = Field(alias="usageType")
    preset: Optional[dict[str, Any]] = None


class DepartmentInfo(BaseModel):
    id: str
    uri: str
    extension_number: str = Field(alias="extensionNumber")
    name: str
    status: str


class CreateDepartmentRequest(BaseModel):
    extension_number: Optional[str] = Field(default=None, alias="extensionNumber")
    name: str
    status: Literal["Enabled", "Disabled"] = "Enabled"


class PagingGroupInfo(BaseModel):
    id: str
    uri: str
    extension_number: str = Field(alias="extensionNumber")
    name: str
    device_ids: list[str] = Field(default=[], alias="devices")


class CreatePagingGroupRequest(BaseModel):
    extension_number: Optional[str] = Field(default=None, alias="extensionNumber")
    name: str
    device_ids: list[str] = Field(default=[], alias="devices")
