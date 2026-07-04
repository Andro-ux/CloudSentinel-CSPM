class CloudSentinelError(Exception):
    """Base exception for CloudSentinel."""


class CollectorError(CloudSentinelError):
    def __init__(self, collector: str, message: str):
        self.collector = collector
        self.message = message
        super().__init__(f"[{collector}] {message}")


class ScanError(CloudSentinelError):
    pass


class ConfigurationError(CloudSentinelError):
    pass


class IntegrationError(CloudSentinelError):
    pass