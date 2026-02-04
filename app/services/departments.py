import logging
from typing import Any

from app.clients.ringcentral import RingCentralClient
from app.schemas.ivr import (
    DepartmentInfo,
    CreateDepartmentRequest,
    PagingGroupInfo,
    CreatePagingGroupRequest,
)

logger = logging.getLogger(__name__)

DEPARTMENT_ENDPOINT = "/restapi/v1.0/account/~/department"
PAGING_GROUP_ENDPOINT = "/restapi/v1.0/account/~/paging-only-groups"


class DepartmentService:
    def __init__(self, client: RingCentralClient) -> None:
        self._client = client

    async def create_department(
        self, payload: CreateDepartmentRequest
    ) -> DepartmentInfo:
        body = payload.dict(by_alias=True, exclude_none=True)
        response = await self._client.post(DEPARTMENT_ENDPOINT, json=body)
        data = response.json()
        return DepartmentInfo.parse_obj(data)

    async def list_departments(
        self, page: int = 1, per_page: int = 100
    ) -> list[DepartmentInfo]:
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        response = await self._client.get(DEPARTMENT_ENDPOINT, params=params)
        data = response.json()
        return [DepartmentInfo.parse_obj(dept) for dept in data.get("records", [])]

    async def get_department(self, department_id: str) -> DepartmentInfo:
        endpoint = f"{DEPARTMENT_ENDPOINT}/{department_id}"
        response = await self._client.get(endpoint)
        data = response.json()
        return DepartmentInfo.parse_obj(data)

    async def update_department(
        self, department_id: str, payload: CreateDepartmentRequest
    ) -> DepartmentInfo:
        endpoint = f"{DEPARTMENT_ENDPOINT}/{department_id}"
        body = payload.dict(by_alias=True, exclude_none=True)
        response = await self._client.put(endpoint, json=body)
        data = response.json()
        return DepartmentInfo.parse_obj(data)

    async def delete_department(self, department_id: str) -> bool:
        endpoint = f"{DEPARTMENT_ENDPOINT}/{department_id}"
        try:
            await self._client.delete(endpoint)
            return True
        except Exception as e:
            logger.error(f"Failed to delete department {department_id}: {e}")
            return False


class PagingGroupService:
    def __init__(self, client: RingCentralClient) -> None:
        self._client = client

    async def create_paging_group(
        self, payload: CreatePagingGroupRequest
    ) -> PagingGroupInfo:
        body = payload.dict(by_alias=True, exclude_none=True)
        response = await self._client.post(PAGING_GROUP_ENDPOINT, json=body)
        data = response.json()
        return PagingGroupInfo.parse_obj(data)

    async def list_paging_groups(
        self, page: int = 1, per_page: int = 100
    ) -> list[PagingGroupInfo]:
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        response = await self._client.get(PAGING_GROUP_ENDPOINT, params=params)
        data = response.json()
        return [PagingGroupInfo.parse_obj(pg) for pg in data.get("records", [])]

    async def get_paging_group(self, group_id: str) -> PagingGroupInfo:
        endpoint = f"{PAGING_GROUP_ENDPOINT}/{group_id}"
        response = await self._client.get(endpoint)
        data = response.json()
        return PagingGroupInfo.parse_obj(data)

    async def update_paging_group(
        self, group_id: str, payload: CreatePagingGroupRequest
    ) -> PagingGroupInfo:
        endpoint = f"{PAGING_GROUP_ENDPOINT}/{group_id}"
        body = payload.dict(by_alias=True, exclude_none=True)
        response = await self._client.put(endpoint, json=body)
        data = response.json()
        return PagingGroupInfo.parse_obj(data)

    async def delete_paging_group(self, group_id: str) -> bool:
        endpoint = f"{PAGING_GROUP_ENDPOINT}/{group_id}"
        try:
            await self._client.delete(endpoint)
            return True
        except Exception as e:
            logger.error(f"Failed to delete paging group {group_id}: {e}")
            return False
