from functools import lru_cache
from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException, Body
import httpx

from app.clients.ringcentral import RingCentralClient
from app.services.ivr import IVRService
from app.services.user_management import UserManagementService
from app.services.departments import DepartmentService, PagingGroupService
from app.services.call_queues import CallQueueService

from app.schemas.ivr import (
    CreateIVRRequest,
    IVRDetail,
    IVRListResponse,
    CallForwardingInfo,
    PresenceStatus,
    AssignDeviceRequest,
    DeviceInfo,
    VoicemailSettings,
    CreateCallHandlingRuleRequest,
    CallHandlingRule,
    ForwardingNumber,
    DepartmentInfo,
    CreateDepartmentRequest,
    PagingGroupInfo,
    CreatePagingGroupRequest,
)

router = APIRouter()


@lru_cache(maxsize=1)
def get_ringcentral_client() -> RingCentralClient:
    return RingCentralClient()


def get_ivr_service() -> IVRService:
    client = get_ringcentral_client()
    return IVRService(client)


def get_user_mgmt_service() -> UserManagementService:
    client = get_ringcentral_client()
    return UserManagementService(client)


def get_department_service() -> DepartmentService:
    client = get_ringcentral_client()
    return DepartmentService(client)


def get_paging_group_service() -> PagingGroupService:
    client = get_ringcentral_client()
    return PagingGroupService(client)


def get_call_queue_service() -> CallQueueService:
    client = get_ringcentral_client()
    return CallQueueService(client)


@router.post(
    "/ivrs",
    response_model=IVRDetail,
    summary="Create IVR/Auto-Receptionist",
    tags=["ivr"],
)
async def create_ivr(
    payload: CreateIVRRequest,
    service: IVRService = Depends(get_ivr_service),
) -> IVRDetail:
    try:
        return await service.create_ivr(payload)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/ivrs",
    response_model=IVRListResponse,
    summary="List IVR/Auto-Receptionists",
    tags=["ivr"],
)
async def list_ivrs(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=100, ge=1, le=1000, alias="perPage"),
    service: IVRService = Depends(get_ivr_service),
) -> IVRListResponse:
    try:
        return await service.list_ivrs(page=page, per_page=per_page)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/ivrs/{ivr_id}",
    response_model=IVRDetail,
    summary="Get IVR details",
    tags=["ivr"],
)
async def get_ivr(
    ivr_id: str,
    service: IVRService = Depends(get_ivr_service),
) -> IVRDetail:
    try:
        return await service.get_ivr(ivr_id)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"IVR {ivr_id} not found")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put(
    "/ivrs/{ivr_id}",
    response_model=IVRDetail,
    summary="Update IVR",
    tags=["ivr"],
)
async def update_ivr(
    ivr_id: str,
    payload: CreateIVRRequest,
    service: IVRService = Depends(get_ivr_service),
) -> IVRDetail:
    try:
        return await service.update_ivr(ivr_id, payload)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete(
    "/ivrs/{ivr_id}",
    summary="Delete IVR",
    tags=["ivr"],
)
async def delete_ivr(
    ivr_id: str,
    service: IVRService = Depends(get_ivr_service),
) -> dict[str, str]:
    try:
        success = await service.delete_ivr(ivr_id)
        if success:
            return {"status": "deleted", "ivr_id": ivr_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete IVR")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/users/{user_id}/activate",
    summary="Activate user",
    tags=["users"],
)
async def activate_user(
    user_id: str,
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> dict[str, Any]:
    try:
        return await service.activate_user(user_id)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/users/{user_id}/password-reset",
    summary="Reset user password",
    tags=["users"],
)
async def reset_password(
    user_id: str,
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> dict[str, str]:
    try:
        return await service.reset_password(user_id)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/users/{user_id}/call-forwarding",
    response_model=CallForwardingInfo,
    summary="Get call forwarding settings",
    tags=["users"],
)
async def get_call_forwarding(
    user_id: str,
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> CallForwardingInfo:
    try:
        return await service.get_call_forwarding(user_id)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put(
    "/users/{user_id}/call-forwarding",
    response_model=CallForwardingInfo,
    summary="Update call forwarding settings",
    tags=["users"],
)
async def update_call_forwarding(
    user_id: str,
    payload: CallForwardingInfo,
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> CallForwardingInfo:
    try:
        return await service.update_call_forwarding(user_id, payload)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/users/{user_id}/presence",
    response_model=PresenceStatus,
    summary="Get user presence",
    tags=["users"],
)
async def get_presence(
    user_id: str,
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> PresenceStatus:
    try:
        return await service.get_presence(user_id)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put(
    "/users/{user_id}/presence",
    response_model=PresenceStatus,
    summary="Update user presence",
    tags=["users"],
)
async def update_presence(
    user_id: str,
    payload: PresenceStatus,
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> PresenceStatus:
    try:
        return await service.update_presence(user_id, payload)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/users/{user_id}/devices",
    response_model=list[DeviceInfo],
    summary="List user devices",
    tags=["users"],
)
async def list_user_devices(
    user_id: str,
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> list[DeviceInfo]:
    try:
        return await service.list_devices(user_id)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/users/{user_id}/devices",
    response_model=DeviceInfo,
    summary="Assign device to user",
    tags=["users"],
)
async def assign_device(
    user_id: str,
    payload: AssignDeviceRequest,
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> DeviceInfo:
    try:
        return await service.assign_device(user_id, payload)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/users/{user_id}/business-hours",
    summary="Get business hours",
    tags=["users"],
)
async def get_business_hours(
    user_id: str,
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> dict[str, Any]:
    try:
        return await service.get_business_hours(user_id)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put(
    "/users/{user_id}/business-hours",
    summary="Update business hours",
    tags=["users"],
)
async def update_business_hours(
    user_id: str,
    schedule: dict[str, Any] = Body(...),
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> dict[str, Any]:
    try:
        return await service.update_business_hours(user_id, schedule)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/users/{user_id}/call-handling-rules",
    response_model=list[CallHandlingRule],
    summary="List call handling rules",
    tags=["users"],
)
async def list_call_handling_rules(
    user_id: str,
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> list[CallHandlingRule]:
    try:
        return await service.list_call_handling_rules(user_id)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/users/{user_id}/call-handling-rules",
    response_model=CallHandlingRule,
    summary="Create call handling rule",
    tags=["users"],
)
async def create_call_handling_rule(
    user_id: str,
    payload: CreateCallHandlingRuleRequest,
    service: UserManagementService = Depends(get_user_mgmt_service),
) -> CallHandlingRule:
    try:
        return await service.create_call_handling_rule(user_id, payload)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/call-queues/{queue_id}/members/bulk-add",
    summary="Bulk add call queue members",
    tags=["call-queues"],
)
async def bulk_add_queue_members(
    queue_id: str,
    member_ids: list[str] = Body(...),
    service: CallQueueService = Depends(get_call_queue_service),
) -> dict[str, Any]:
    try:
        result = await service.bulk_add_members(queue_id, member_ids)
        return {"status": "success", "queue_id": queue_id, "added_members": len(member_ids)}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/call-queues/{queue_id}/members/bulk-remove",
    summary="Bulk remove call queue members",
    tags=["call-queues"],
)
async def bulk_remove_queue_members(
    queue_id: str,
    member_ids: list[str] = Body(...),
    service: CallQueueService = Depends(get_call_queue_service),
) -> dict[str, Any]:
    try:
        result = await service.bulk_remove_members(queue_id, member_ids)
        return {"status": "success", "queue_id": queue_id, "removed_members": len(member_ids)}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/call-queues/{queue_id}/presence",
    summary="Get call queue presence",
    tags=["call-queues"],
)
async def get_queue_presence(
    queue_id: str,
    service: CallQueueService = Depends(get_call_queue_service),
) -> dict[str, Any]:
    try:
        return await service.get_queue_presence(queue_id)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/departments",
    response_model=DepartmentInfo,
    summary="Create department",
    tags=["departments"],
)
async def create_department(
    payload: CreateDepartmentRequest,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentInfo:
    try:
        return await service.create_department(payload)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/departments",
    response_model=list[DepartmentInfo],
    summary="List departments",
    tags=["departments"],
)
async def list_departments(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=100, ge=1, le=1000, alias="perPage"),
    service: DepartmentService = Depends(get_department_service),
) -> list[DepartmentInfo]:
    try:
        return await service.list_departments(page=page, per_page=per_page)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/paging-groups",
    response_model=PagingGroupInfo,
    summary="Create paging group",
    tags=["paging-groups"],
)
async def create_paging_group(
    payload: CreatePagingGroupRequest,
    service: PagingGroupService = Depends(get_paging_group_service),
) -> PagingGroupInfo:
    try:
        return await service.create_paging_group(payload)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/paging-groups",
    response_model=list[PagingGroupInfo],
    summary="List paging groups",
    tags=["paging-groups"],
)
async def list_paging_groups(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=100, ge=1, le=1000, alias="perPage"),
    service: PagingGroupService = Depends(get_paging_group_service),
) -> list[PagingGroupInfo]:
    try:
        return await service.list_paging_groups(page=page, per_page=per_page)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
