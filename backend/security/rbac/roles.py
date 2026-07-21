from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class RoleDefinition:
    id: str
    name: str
    description: str
    permissions: List[str]
    is_system: bool = False


PLATFORM_ADMIN = RoleDefinition(
    id="platform_admin",
    name="Platform Administrator",
    description="Full platform access with user management",
    permissions=[
        "system.admin",
        "users.manage",
        "roles.manage",
        "apikey.manage",
        "audit.read",
        "dashboard.read",
        "assets.read",
        "findings.read",
        "risks.read",
        "graph.read",
        "providers.read",
        "providers.manage",
        "capabilities.read",
    ],
    is_system=True,
)

ORGANIZATION_ADMIN = RoleDefinition(
    id="organization_admin",
    name="Organization Administrator",
    description="Full access within an organization",
    permissions=[
        "users.manage",
        "apikey.manage",
        "dashboard.read",
        "assets.read",
        "findings.read",
        "risks.read",
        "graph.read",
        "providers.read",
        "capabilities.read",
        "audit.read",
    ],
    is_system=True,
)

SECURITY_ENGINEER = RoleDefinition(
    id="security_engineer",
    name="Security Engineer",
    description="Security operations and analysis",
    permissions=[
        "dashboard.read",
        "assets.read",
        "findings.read",
        "risks.read",
        "graph.read",
        "providers.read",
        "capabilities.read",
    ],
    is_system=True,
)

ANALYST = RoleDefinition(
    id="analyst",
    name="Analyst",
    description="Read-only access to security data",
    permissions=[
        "dashboard.read",
        "assets.read",
        "findings.read",
        "risks.read",
        "graph.read",
    ],
    is_system=True,
)

AUDITOR = RoleDefinition(
    id="auditor",
    name="Auditor",
    description="Read-only access with audit logs",
    permissions=[
        "dashboard.read",
        "assets.read",
        "findings.read",
        "risks.read",
        "graph.read",
        "audit.read",
        "providers.read",
    ],
    is_system=True,
)

READ_ONLY = RoleDefinition(
    id="read_only",
    name="Read Only",
    description="Minimal read-only access",
    permissions=[
        "dashboard.read",
        "assets.read",
    ],
    is_system=True,
)

DEFAULT_ROLES = {
    role.id: role for role in [
        PLATFORM_ADMIN,
        ORGANIZATION_ADMIN,
        SECURITY_ENGINEER,
        ANALYST,
        AUDITOR,
        READ_ONLY,
    ]
}
