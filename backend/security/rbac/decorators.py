from functools import wraps
from typing import Callable, Optional

from fastapi import Depends, HTTPException, status


class RBACError(Exception):
    def __init__(self, permission: str, message: str = None):
        self.permission = permission
        self.message = message or f"Permission denied: {permission}"
        super().__init__(self.message)


def require_permission(permission: str):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            security_context = kwargs.get("security_context")
            if not security_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )
            if not security_context.has_permission(permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission}",
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role_id: str):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            security_context = kwargs.get("security_context")
            if not security_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )
            if role_id not in security_context.role_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {role_id}",
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator
