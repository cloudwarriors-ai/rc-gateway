from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Depends, Query

from app.schemas.ringcentral import (
    CreateExtensionRequest, 
    ExtensionListResponse, 
    ExtensionSummary,
    ExtensionUpdateRequest,
    ExtensionDetail
)
from app.services.extensions import ExtensionService
from app.clients.ringcentral import RingCentralClient

router = APIRouter()


@lru_cache(maxsize=1)
def get_ringcentral_client() -> RingCentralClient:
    return RingCentralClient()


def get_extension_service() -> ExtensionService:
    client = get_ringcentral_client()
    return ExtensionService(client)


@router.get("/health", summary="Health check", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post(
    "/extensions",
    response_model=ExtensionSummary,
    summary="Create RingCentral extension",
    tags=["extensions"],
)
async def create_extension(
    payload: CreateExtensionRequest, service: ExtensionService = Depends(get_extension_service)
) -> ExtensionSummary:
    return await service.create_extension(payload)


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
    return await service.list_extensions(page=page, per_page=per_page, status=status)


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
    return await service.list_users(page=page, per_page=per_page, status=status)


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
    return await service.get_extension(extension_id)


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
    return await service.update_extension(extension_id, payload)


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
    return await service.update_extension_number(extension_id, new_number)
