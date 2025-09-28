from __future__ import annotations

from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field


class ExtensionType(str, Enum):
    USER = "User"
    DIGITAL_USER = "DigitalUser"
    VIRTUAL_USER = "VirtualUser"
    DEPARTMENT = "Department"
    ANNOUNCEMENT = "AnnouncementOnly"
    TAKE_MESSAGE_ONLY = "TakeMessagesOnly"
    TOLL_FREE = "CompanyNumber"
    IVR_MENU = "IvrMenu"
    APPLICATION = "ApplicationExtension"
    # Add support for unknown extension types
    UNKNOWN = "Unknown"


class ContactInfo(BaseModel):
    first_name: Optional[str] = Field(default=None, alias="firstName")
    last_name: Optional[str] = Field(default=None, alias="lastName")
    company: Optional[str] = None
    email: Optional[str] = None


class ExtensionStatus(str, Enum):
    ENABLED = "Enabled"
    DISABLED = "Disabled"
    NOT_ACTIVATED = "NotActivated"


class CreateExtensionRequest(BaseModel):
    type: ExtensionType = Field(default=ExtensionType.USER)
    status: ExtensionStatus = Field(default=ExtensionStatus.ENABLED)
    contact: ContactInfo
    regional_settings: Optional[dict] = Field(default=None, alias="regionalSettings")
    password: Optional[str] = None


class ExtensionSummary(BaseModel):
    id: str
    extension_number: Optional[str] = Field(default=None, alias="extensionNumber")
    name: Optional[str] = None
    type: Union[ExtensionType, str]  # Allow unknown extension types as raw strings
    status: ExtensionStatus


class PagingInfo(BaseModel):
    page: int = 1
    per_page: int = Field(default=100, alias="perPage")
    total_pages: Optional[int] = Field(default=None, alias="totalPages")
    total_elements: Optional[int] = Field(default=None, alias="totalElements")


class NavigationUriObject(BaseModel):
    uri: str


class NavigationInfo(BaseModel):
    first_page: Optional[NavigationUriObject] = Field(default=None, alias="firstPage")
    next_page: Optional[NavigationUriObject] = Field(default=None, alias="nextPage")
    previous_page: Optional[NavigationUriObject] = Field(default=None, alias="previousPage")
    last_page: Optional[NavigationUriObject] = Field(default=None, alias="lastPage")


class ExtensionListResponse(BaseModel):
    records: list[ExtensionSummary]
    paging: Optional[PagingInfo] = None
    navigation: Optional[NavigationInfo] = None


class PronouncedName(BaseModel):
    type: str = "TextToSpeech"
    text: Optional[str] = None


class ContactInfoDetailed(BaseModel):
    first_name: Optional[str] = Field(default=None, alias="firstName")
    last_name: Optional[str] = Field(default=None, alias="lastName")
    company: Optional[str] = None
    email: Optional[str] = None
    email_as_login_name: Optional[bool] = Field(default=None, alias="emailAsLoginName")
    pronounced_name: Optional[PronouncedName] = Field(default=None, alias="pronouncedName")


class TimezoneInfo(BaseModel):
    uri: Optional[str] = None
    id: str
    name: str
    description: Optional[str] = None
    bias: Optional[str] = None


class CountryInfo(BaseModel):
    uri: Optional[str] = None
    id: str
    name: str
    iso_code: str = Field(alias="isoCode")
    calling_code: Optional[str] = Field(default=None, alias="callingCode")


class LanguageInfo(BaseModel):
    id: str
    name: str
    locale_code: str = Field(alias="localeCode")


class RegionalSettings(BaseModel):
    timezone: Optional[TimezoneInfo] = None
    home_country: Optional[CountryInfo] = Field(default=None, alias="homeCountry")
    language: Optional[LanguageInfo] = None
    greeting_language: Optional[LanguageInfo] = Field(default=None, alias="greetingLanguage")
    formatting_locale: Optional[LanguageInfo] = Field(default=None, alias="formattingLocale")
    time_format: Optional[str] = Field(default=None, alias="timeFormat")


class AdminPermission(BaseModel):
    enabled: bool = True


class InternationalCallingPermission(BaseModel):
    enabled: bool = True


class ExtensionPermissions(BaseModel):
    admin: Optional[AdminPermission] = None
    international_calling: Optional[InternationalCallingPermission] = Field(default=None, alias="internationalCalling")


class ProfileImage(BaseModel):
    uri: str


class SiteInfo(BaseModel):
    name: str


class ExtensionUpdateRequest(BaseModel):
    extension_number: Optional[str] = Field(default=None, alias="extensionNumber")
    contact: Optional[ContactInfoDetailed] = None
    status: Optional[ExtensionStatus] = None
    regional_settings: Optional[RegionalSettings] = Field(default=None, alias="regionalSettings")
    permissions: Optional[ExtensionPermissions] = None
    hidden: Optional[bool] = None


class ExtensionDetail(BaseModel):
    uri: str
    id: str
    extension_number: str = Field(alias="extensionNumber") 
    contact: ContactInfoDetailed
    name: str
    type: str
    status: ExtensionStatus
    regional_settings: Optional[RegionalSettings] = Field(default=None, alias="regionalSettings")
    setup_wizard_state: Optional[str] = Field(default=None, alias="setupWizardState")
    permissions: Optional[ExtensionPermissions] = None
    profile_image: Optional[ProfileImage] = Field(default=None, alias="profileImage")
    site: Optional[SiteInfo] = None
    hidden: Optional[bool] = None
    assigned_country: Optional[CountryInfo] = Field(default=None, alias="assignedCountry")
    site_access: Optional[str] = Field(default=None, alias="siteAccess")
    creation_time: Optional[str] = Field(default=None, alias="creationTime")
