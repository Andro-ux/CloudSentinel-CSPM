import logging
import sys
import os
import json
from typing import Optional
from datetime import datetime
from backend.runtime.configuration import LogFormat


_configured = False


def configure_logging(config=None):
    global _configured
    if _configured:
        return
    _configured = True

    if config is None:
        from backend.runtime.configuration import RuntimeConfiguration
        config = RuntimeConfiguration()

    log_level = getattr(logging, config.logging.level.upper(), logging.INFO)
    logger = logging.getLogger("cloudsentinel")
    logger.setLevel(log_level)

    if config.logging.output == "console" or config.environment.value != "production":
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.StreamHandler(sys.stdout)

    if config.logging.format == LogFormat.JSON:
        formatter = _JSONFormatter(
            include_request_id=config.logging.include_request_id,
            include_correlation_id=config.logging.include_correlation_id,
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"cloudsentinel.{name}")


class _JSONFormatter(logging.Formatter):
    def __init__(self, include_request_id: bool = True, include_correlation_id: bool = True):
        super().__init__()
        self.include_request_id = include_request_id
        self.include_correlation_id = include_correlation_id

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
        }
        if self.include_request_id and hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if self.include_correlation_id and hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)
