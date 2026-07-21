from typing import Dict, List, Optional, Set


class PermissionPolicy:
    def __init__(self):
        self._permissions: Dict[str, Set[str]] = {}

    def grant(self, role_id: str, permission: str) -> None:
        self._permissions.setdefault(role_id, set()).add(permission)

    def revoke(self, role_id: str, permission: str) -> None:
        if role_id in self._permissions:
            self._permissions[role_id].discard(permission)

    def get_permissions(self, role_id: str) -> Set[str]:
        return self._permissions.get(role_id, set())

    def has_permission(self, role_id: str, permission: str) -> bool:
        return permission in self._permissions.get(role_id, set())

    def load_from_roles(self, roles: Dict[str, List[str]]) -> None:
        for role_id, permissions in roles.items():
            for permission in permissions:
                self.grant(role_id, permission)

    def list_all(self) -> Dict[str, List[str]]:
        return {role_id: sorted(perms) for role_id, perms in self._permissions.items()}


class RBACPolicy:
    def __init__(self, permission_policy: PermissionPolicy = None):
        self.permission_policy = permission_policy or PermissionPolicy()
        self._role_hierarchy: Dict[str, List[str]] = {}

    def add_role(self, role_id: str, permissions: List[str]) -> None:
        for permission in permissions:
            self.permission_policy.grant(role_id, permission)

    def add_inheritance(self, child_role: str, parent_role: str) -> None:
        self._role_hierarchy.setdefault(child_role, []).append(parent_role)

    def get_effective_permissions(self, role_ids: List[str]) -> Set[str]:
        effective: Set[str] = set()
        for role_id in role_ids:
            effective.update(self.permission_policy.get_permissions(role_id))
            if role_id in self._role_hierarchy:
                for parent_role in self._role_hierarchy[role_id]:
                    effective.update(self.get_effective_permissions([parent_role]))
        return effective

    def has_permission(self, role_ids: List[str], permission: str) -> bool:
        return any(
            self.permission_policy.has_permission(role_id, permission)
            for role_id in role_ids
        )

    def load_default_roles(self, default_roles: Dict[str, List[str]]) -> None:
        self.permission_policy.load_from_roles(default_roles)
