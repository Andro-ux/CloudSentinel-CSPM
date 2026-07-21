import re
from typing import Optional
from backend.security.exceptions import SecurityError


def validate_username(username: str) -> None:
    if not username or len(username) < 3:
        raise SecurityError("Username must be at least 3 characters")
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise SecurityError("Username can only contain letters, numbers, underscores, and hyphens")


def validate_email(email: str) -> None:
    if not email or '@' not in email:
        raise SecurityError("Invalid email address")
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise SecurityError("Invalid email format")


def validate_organization_name(name: str) -> None:
    if not name or len(name) < 2:
        raise SecurityError("Organization name must be at least 2 characters")


def validate_api_key_name(name: str) -> None:
    if not name or len(name) < 1:
        raise SecurityError("API key name is required")
    if len(name) > 64:
        raise SecurityError("API key name must be 64 characters or less")


def validate_permission(permission: str) -> None:
    parts = permission.split(".")
    if len(parts) != 2:
        raise SecurityError(f"Invalid permission format: {permission}. Expected 'resource.action'")
    resource, action = parts
    if not resource or not action:
        raise SecurityError(f"Invalid permission format: {permission}")


def validate_role_id(role_id: str) -> None:
    if not role_id or len(role_id) < 1:
        raise SecurityError("Role ID is required")
    valid_roles = ["platform_admin", "organization_admin", "security_engineer", "analyst", "auditor", "read_only"]
    if role_id not in valid_roles:
        raise SecurityError(f"Invalid role ID: {role_id}. Must be one of {valid_roles}")
