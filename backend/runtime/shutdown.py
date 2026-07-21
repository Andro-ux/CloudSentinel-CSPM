from typing import Optional, Dict, Any
from backend.runtime.configuration import RuntimeConfiguration
from backend.runtime.logging import get_logger


logger = get_logger("shutdown")


class ShutdownManager:
    def __init__(self, config: RuntimeConfiguration):
        self.config = config
        self._shutdown_handlers: list = []

    def register_handler(self, handler) -> None:
        self._shutdown_handlers.append(handler)

    def shutdown(self) -> None:
        logger.info("Initiating graceful shutdown")
        for handler in reversed(self._shutdown_handlers):
            try:
                logger.info(f"Running shutdown handler: {handler.__name__}")
                handler()
            except Exception as exc:
                logger.error(f"Shutdown handler failed: {handler.__name__}: {exc}")
        logger.info("Graceful shutdown complete")
