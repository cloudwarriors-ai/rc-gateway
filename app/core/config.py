import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional


@dataclass
class RingCentralCredentials:
    client_id: str
    client_secret: str
    jwt: str
    base_url: str = "https://platform.ringcentral.com"
    account_id: str = "~"
    extension_id: str = "~"
    token_cache_seconds: int = 2700


@dataclass
class Settings:
    environment: str
    rc_credentials_path: Path
    rc_client_id: Optional[str]
    rc_client_secret: Optional[str]
    rc_jwt: Optional[str]
    rc_base_url: Optional[str]
    rc_account_id: Optional[str]
    rc_extension_id: Optional[str]
    rc_token_cache_seconds: Optional[int]
    redis_host: Optional[str]
    redis_port: Optional[int]
    redis_db: Optional[int]
    redis_password: Optional[str]
    cache_ttl_seconds: Optional[int]

    def load_ringcentral_credentials(self) -> RingCentralCredentials:
        data: dict[str, object] = {}

        if self.rc_credentials_path.exists():
            with self.rc_credentials_path.open("r", encoding="utf-8") as handle:
                data.update(json.load(handle))

        overrides = {
            "client_id": self.rc_client_id,
            "client_secret": self.rc_client_secret,
            "jwt": self.rc_jwt,
            "base_url": self.rc_base_url,
            "account_id": self.rc_account_id,
            "extension_id": self.rc_extension_id,
            "token_cache_seconds": self.rc_token_cache_seconds,
        }

        for key, value in overrides.items():
            if value is not None:
                data[key] = value

        missing = [field for field in ("client_id", "client_secret", "jwt") if field not in data or not data[field]]
        if missing:
            raise RuntimeError(
                "Missing RingCentral credential values: " + ", ".join(missing)
            )

        return RingCentralCredentials(**data)  # type: ignore[arg-type]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    env = os.getenv("APP_ENV", "development")
    credentials_path = Path(os.getenv("RC_CREDENTIALS_PATH", "config/rc_credentials.json"))

    raw_cache_seconds = os.getenv("RC_TOKEN_CACHE_SECONDS")
    cache_seconds = int(raw_cache_seconds) if raw_cache_seconds else None

    return Settings(
        environment=env,
        rc_credentials_path=credentials_path,
        rc_client_id=os.getenv("RC_CLIENT_ID"),
        rc_client_secret=os.getenv("RC_CLIENT_SECRET"),
        rc_jwt=os.getenv("RC_JWT"),
        rc_base_url=os.getenv("RC_BASE_URL"),
        rc_account_id=os.getenv("RC_ACCOUNT_ID"),
        rc_extension_id=os.getenv("RC_EXTENSION_ID"),
        rc_token_cache_seconds=cache_seconds,
        redis_host=os.getenv("REDIS_HOST", "localhost"),
        redis_port=int(os.getenv("REDIS_PORT", "6379")),
        redis_db=int(os.getenv("REDIS_DB", "0")),
        redis_password=os.getenv("REDIS_PASSWORD"),
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
    )
