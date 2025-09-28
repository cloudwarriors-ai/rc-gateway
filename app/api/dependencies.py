from functools import lru_cache

from ..clients.ringcentral import RingCentralClient
from ..services.extensions import ExtensionService


@lru_cache(maxsize=1)
def get_ringcentral_client() -> RingCentralClient:
    return RingCentralClient()


def get_extension_service() -> ExtensionService:
    client = get_ringcentral_client()
    return ExtensionService(client)
