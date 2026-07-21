from typing import Set, Dict, List
from backend.security.rbac.policies import PermissionPolicy
from backend.security.rbac.roles import DEFAULT_ROLES


class PermissionRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._policy = PermissionPolicy()
            cls._instance._policy.load_from_roles({
                role_id: role.permissions for role_id, role in DEFAULT_ROLES.items()
            })
        return cls._instance

    def get_permissions(self, role_id: str) -> Set[str]:
        return self._policy.get_permissions(role_id)

    def has_permission(self, role_id: str, permission: str) -> bool:
        return self._policy.has_permission(role_id, permission)

    def list_all(self) -> Dict[str, List[str]]:
        return self._policy.list_all()


permission_registry = PermissionRegistry()
