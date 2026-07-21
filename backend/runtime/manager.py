import os
import time
import signal
import sys
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from backend.runtime.configuration import RuntimeConfiguration, Environment
from backend.runtime.logging import get_logger
from backend.runtime.exceptions import ConfigurationError, DependencyError, StartupError
from backend.runtime.lifecycle import LifecycleManager, LifecycleEventType
from backend.runtime.validation import ConfigurationValidator

logger = get_logger("manager")


class RuntimeManager:
    _instance = None

    def __new__(cls, config: Optional[RuntimeConfiguration] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Optional[RuntimeConfiguration] = None):
        if self._initialized:
            return
        self.config = config or self._load_config()
        self.lifecycle = LifecycleManager(self.config)
        self._startup_time: Optional[datetime] = None
        self._shutdown_time: Optional[datetime] = None
        self._health_checks: Dict[str, Callable] = {}
        self._readiness_checks: Dict[str, Callable] = {}
        self._register_signal_handlers()
        self._initialized = True

    def _load_config(self) -> RuntimeConfiguration:
        from backend.runtime.startup import ConfigurationLoader
        return ConfigurationLoader.load()

    def _register_signal_handlers(self) -> None:
        try:
            signal.signal(signal.SIGTERM, self._handle_signal)
            signal.signal(signal.SIGINT, self._handle_signal)
            if hasattr(signal, "SIGUSR2"):
                signal.signal(signal.SIGUSR2, self._handle_reload)
        except (OSError, AttributeError):
            pass

    def _handle_signal(self, signum, frame) -> None:
        logger.info(f"Received signal {signum}, initiating graceful shutdown")
        self.shutdown()
        sys.exit(0)

    def _handle_reload(self, signum, frame) -> None:
        logger.info(f"Received reload signal {signum}")
        self.lifecycle.reload()

    def validate_configuration(self) -> None:
        logger.info("Validating configuration")
        result = ConfigurationValidator.validate(self.config)
        if not result["valid"]:
            for error in result["errors"]:
                logger.error(f"Configuration error: {error}")
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(result['errors'])}")
        for warning in result["warnings"]:
            logger.warning(f"Configuration warning: {warning}")
        logger.info("Configuration validation passed")

    def startup(self) -> None:
        if self.lifecycle.is_started:
            return
        logger.info(f"Starting CloudSentinel v{self.config.app_version} in {self.config.environment.value} mode")
        self._startup_time = datetime.utcnow()
        self.validate_configuration()
        self.lifecycle.startup()
        logger.info("CloudSentinel started successfully")

    def shutdown(self) -> None:
        if self.lifecycle.is_shutdown:
            return
        logger.info("Shutting down CloudSentinel")
        self._shutdown_time = datetime.utcnow()
        self.lifecycle.shutdown()
        logger.info("CloudSentinel shut down successfully")

    def register_health_check(self, name: str, check: Callable) -> None:
        self._health_checks[name] = check

    def register_readiness_check(self, name: str, check: Callable) -> None:
        self._readiness_checks[name] = check

    def run_health_checks(self) -> Dict[str, Any]:
        results = {}
        for name, check in self._health_checks.items():
            try:
                result = check()
                results[name] = {"status": "healthy", "details": result}
            except Exception as exc:
                logger.error(f"Health check {name} failed: {exc}")
                results[name] = {"status": "unhealthy", "error": str(exc)}
        return results

    def run_readiness_checks(self) -> Dict[str, Any]:
        results = {}
        for name, check in self._readiness_checks.items():
            try:
                result = check()
                results[name] = {"status": "ready", "details": result}
            except Exception as exc:
                logger.error(f"Readiness check {name} failed: {exc}")
                results[name] = {"status": "not_ready", "error": str(exc)}
        return results

    @property
    def uptime_seconds(self) -> float:
        if self._startup_time:
            return (datetime.utcnow() - self._startup_time).total_seconds()
        return 0.0

    @property
    def is_running(self) -> bool:
        return self.lifecycle.is_started and not self.lifecycle.is_shutdown
