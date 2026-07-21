class RuntimeError(Exception):
    """Base exception for runtime errors."""
    pass


class ConfigurationError(RuntimeError):
    """Raised when configuration is invalid or missing."""
    pass


class StartupError(RuntimeError):
    """Raised when startup validation fails."""
    pass


class DependencyError(RuntimeError):
    """Raised when a required dependency is unavailable."""
    pass


class HealthCheckError(RuntimeError):
    """Raised when a health check fails."""
    pass
