import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any

from pythonjsonlogger import jsonlogger

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get("")
        return True


def setup_logging(log_level: str = "INFO") -> None:
    log_handler = logging.StreamHandler(sys.stdout)
    
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(request_id)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"}
    )
    
    log_handler.setFormatter(formatter)
    log_handler.addFilter(RequestIdFilter())
    
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(log_handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def set_request_id(request_id: str | None = None) -> str:
    req_id = request_id or str(uuid.uuid4())
    request_id_var.set(req_id)
    return req_id


def get_request_id() -> str:
    return request_id_var.get("")
