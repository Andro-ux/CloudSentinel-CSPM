from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, Any


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class APIException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: Any = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(APIException):
    def __init__(self, resource: str, identifier: Any = None):
        message = f"{resource} not found"
        if identifier is not None:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__("NOT_FOUND", message, status_code=404)


class ValidationError(APIException):
    def __init__(self, message: str, details: Any = None):
        super().__init__("VALIDATION_ERROR", message, status_code=422, details=details)


class ServerError(APIException):
    def __init__(self, message: str = "Internal server error"):
        super().__init__("INTERNAL_ERROR", message, status_code=500)
