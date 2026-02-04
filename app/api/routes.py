from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Depends, Query, HTTPException
import httpx

from app.schemas.ringcentral import (
    CreateExtensionRequest, 
    ExtensionListResponse, 
    ExtensionSummary,
    ExtensionUpdateRequest,
    ExtensionDetail,
    CreateSiteRequest,
    SiteListResponse,
    SiteDetail,
    SiteUpdateRequest,
)
from app.schemas.webhooks import (
    WebhookSubscriptionRequest,
    WebhookSubscriptionResponse,
    WebhookEvent,
    WebhookValidationRequest,
    WebhookValidationResponse,
    CreateCallQueueRequest,
    CallQueueDetail,
    CallQueueListResponse,
    AvailableNumbersRequest,
    AvailableNumbersResponse,
    CallLogResponse,
)
from app.services.extensions import ExtensionService
from app.services.sites import SiteService
from app.services.webhooks import WebhookService
from app.services.call_queues import CallQueueService
from app.services.phone_numbers import PhoneNumberService
from app.services.analytics import AnalyticsService
from app.services.browser_auth import BrowserAuthService
from app.clients.ringcentral import RingCentralClient

router = APIRouter()


@lru_cache(maxsize=1)
def get_ringcentral_client() -> RingCentralClient:
    return RingCentralClient()


def get_extension_service() -> ExtensionService:
    client = get_ringcentral_client()
    return ExtensionService(client)


def get_site_service() -> SiteService:
    client = get_ringcentral_client()
    return SiteService(client)


def get_webhook_service() -> WebhookService:
    client = get_ringcentral_client()
    return WebhookService(client)


def get_call_queue_service() -> CallQueueService:
    client = get_ringcentral_client()
    return CallQueueService(client)


def get_phone_number_service() -> PhoneNumberService:
    client = get_ringcentral_client()
    return PhoneNumberService(client)


def get_analytics_service() -> AnalyticsService:
    client = get_ringcentral_client()
    return AnalyticsService(client)


def get_browser_auth_service() -> BrowserAuthService:
    return BrowserAuthService()


@router.get("/health", summary="Health check", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/auth/login", summary="Login to RingCentral via browser", tags=["authentication"])
async def login_to_ringcentral(
    service: BrowserAuthService = Depends(get_browser_auth_service)
) -> dict[str, str]:
    try:
        result = await service.login_to_ringcentral()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.post(
    "/extensions",
    response_model=ExtensionSummary,
    summary="Create RingCentral extension",
    tags=["extensions"],
)
async def create_extension(
    payload: CreateExtensionRequest, service: ExtensionService = Depends(get_extension_service)
) -> ExtensionSummary:
    try:
        return await service.create_extension(payload)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/extensions",
    response_model=ExtensionListResponse,
    summary="List RingCentral extensions",
    tags=["extensions"],
)
async def list_extensions(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=100, ge=1, le=1000, alias="perPage"),
    status: str | None = Query(default=None),
    service: ExtensionService = Depends(get_extension_service),
) -> ExtensionListResponse:
    try:
        return await service.list_extensions(page=page, per_page=per_page, status=status)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/users",
    response_model=ExtensionListResponse,
    summary="List RingCentral users (User type extensions only)",
    tags=["users"],
)
async def list_users(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=1000, alias="perPage"),
    status: str | None = Query(default=None),
    service: ExtensionService = Depends(get_extension_service),
) -> ExtensionListResponse:
    try:
        return await service.list_users(page=page, per_page=per_page, status=status)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/extensions/{extension_id}",
    response_model=ExtensionDetail,
    summary="Get detailed extension information",
    tags=["extensions"],
)
async def get_extension(
    extension_id: str,
    service: ExtensionService = Depends(get_extension_service),
) -> ExtensionDetail:
    try:
        return await service.get_extension(extension_id)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Extension {extension_id} not found")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put(
    "/extensions/{extension_id}",
    response_model=ExtensionDetail,
    summary="Update extension properties",
    tags=["extensions"],
)
async def update_extension(
    extension_id: str,
    payload: ExtensionUpdateRequest,
    service: ExtensionService = Depends(get_extension_service),
) -> ExtensionDetail:
    try:
        return await service.update_extension(extension_id, payload)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Extension {extension_id} not found")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put(
    "/extensions/{extension_id}/number",
    response_model=ExtensionDetail,
    summary="Update extension number",
    tags=["extensions"],
)
async def update_extension_number(
    extension_id: str,
    new_number: str = Query(alias="extensionNumber"),
    service: ExtensionService = Depends(get_extension_service),
) -> ExtensionDetail:
    try:
        return await service.update_extension_number(extension_id, new_number)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Extension {extension_id} not found")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Site/Location Management Endpoints

@router.post(
    "/sites",
    response_model=SiteDetail,
    summary="Create RingCentral site/location",
    tags=["sites"],
)
async def create_site(
    payload: CreateSiteRequest, 
    service: SiteService = Depends(get_site_service)
) -> SiteDetail:
    try:
        return await service.create_site(payload)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/sites",
    response_model=SiteListResponse,
    summary="List RingCentral sites/locations",
    tags=["sites"],
)
async def list_sites(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=100, ge=1, le=1000, alias="perPage"),
    service: SiteService = Depends(get_site_service),
) -> SiteListResponse:
    try:
        return await service.list_sites(page=page, per_page=per_page)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/sites/{site_id}",
    response_model=SiteDetail,
    summary="Get detailed site information",
    tags=["sites"],
)
async def get_site(
    site_id: str,
    service: SiteService = Depends(get_site_service),
) -> SiteDetail:
    try:
        return await service.get_site(site_id)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Site {site_id} not found")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put(
    "/sites/{site_id}",
    response_model=SiteDetail,
    summary="Update site properties",
    tags=["sites"],
)
async def update_site(
    site_id: str,
    payload: SiteUpdateRequest,
    service: SiteService = Depends(get_site_service),
) -> SiteDetail:
    try:
        return await service.update_site(site_id, payload)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Site {site_id} not found")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete(
    "/sites/{site_id}",
    summary="Delete site/location",
    tags=["sites"],
)
async def delete_site(
    site_id: str,
    service: SiteService = Depends(get_site_service),
) -> dict[str, str]:
    try:
        success = await service.delete_site(site_id)
        if success:
            return {"status": "deleted", "site_id": site_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete site")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Site {site_id} not found")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/webhooks/subscriptions",
    response_model=WebhookSubscriptionResponse,
    summary="Create webhook subscription",
    tags=["webhooks"],
)
async def create_webhook_subscription(
    payload: WebhookSubscriptionRequest,
    service: WebhookService = Depends(get_webhook_service),
) -> WebhookSubscriptionResponse:
    try:
        return await service.create_subscription(payload)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/webhooks/subscriptions",
    response_model=list[WebhookSubscriptionResponse],
    summary="List webhook subscriptions",
    tags=["webhooks"],
)
async def list_webhook_subscriptions(
    service: WebhookService = Depends(get_webhook_service),
) -> list[WebhookSubscriptionResponse]:
    try:
        return await service.list_subscriptions()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/webhooks/validate",
    response_model=WebhookValidationResponse,
    summary="Validate webhook",
    tags=["webhooks"],
)
async def validate_webhook(
    payload: WebhookValidationRequest,
) -> WebhookValidationResponse:
    return WebhookValidationResponse(validation_token=payload.validation_token)


@router.post(
    "/webhooks/events",
    summary="Receive webhook events",
    tags=["webhooks"],
)
async def receive_webhook_event(
    event: WebhookEvent,
    service: WebhookService = Depends(get_webhook_service),
) -> dict[str, str]:
    try:
        result = WebhookService.process_event(event)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process event: {str(e)}")


@router.post(
    "/call-queues",
    response_model=CallQueueDetail,
    summary="Create call queue",
    tags=["call-queues"],
)
async def create_call_queue(
    payload: CreateCallQueueRequest,
    service: CallQueueService = Depends(get_call_queue_service),
) -> CallQueueDetail:
    try:
        return await service.create_call_queue(payload)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/call-queues",
    response_model=CallQueueListResponse,
    summary="List call queues",
    tags=["call-queues"],
)
async def list_call_queues(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=100, ge=1, le=1000, alias="perPage"),
    service: CallQueueService = Depends(get_call_queue_service),
) -> CallQueueListResponse:
    try:
        return await service.list_call_queues(page=page, per_page=per_page)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/call-queues/{queue_id}",
    response_model=CallQueueDetail,
    summary="Get call queue details",
    tags=["call-queues"],
)
async def get_call_queue(
    queue_id: str,
    service: CallQueueService = Depends(get_call_queue_service),
) -> CallQueueDetail:
    try:
        return await service.get_call_queue(queue_id)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Call queue {queue_id} not found")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/phone-numbers/available",
    response_model=AvailableNumbersResponse,
    summary="Search available phone numbers",
    tags=["phone-numbers"],
)
async def search_available_numbers(
    area_code: str | None = Query(default=None, alias="areaCode"),
    country_id: str = Query(default="1", alias="countryId"),
    per_page: int = Query(default=10, ge=1, le=100, alias="perPage"),
    service: PhoneNumberService = Depends(get_phone_number_service),
) -> AvailableNumbersResponse:
    try:
        request = AvailableNumbersRequest(
            area_code=area_code,
            country_id=country_id,
            per_page=per_page
        )
        return await service.search_available_numbers(request)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/analytics/call-logs",
    response_model=CallLogResponse,
    summary="Get call logs",
    tags=["analytics"],
)
async def get_call_logs(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=100, ge=1, le=1000, alias="perPage"),
    direction: str | None = Query(default=None),
    service: AnalyticsService = Depends(get_analytics_service),
) -> CallLogResponse:
    try:
        return await service.get_call_logs(
            page=page, 
            per_page=per_page, 
            direction=direction
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
