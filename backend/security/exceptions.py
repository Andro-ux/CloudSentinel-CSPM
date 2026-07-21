class SecurityError(Exception):
    pass


class AuthenticationError(SecurityError):
    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(message)


class AuthorizationError(SecurityError):
    def __init__(self, permission: str, message: str = None):
        self.permission = permission
        self.message = message or f"Permission denied: {permission}"
        super().__init__(self.message)


class InvalidTokenError(AuthenticationError):
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message)


class InvalidAPIKeyError(AuthenticationError):
    def __init__(self, message: str = "Invalid or expired API key"):
        super().__init__(message)


class RateLimitExceededError(SecurityError):
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")
