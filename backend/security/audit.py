from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.security.models import AuditEvent
from backend.security.exceptions import SecurityError


class AuditLogger:
    def __init__(self):
        self._events: List[AuditEvent] = []

    def log_event(
        self,
        event_type: str,
        actor_type: str,
        actor_id: str,
        organization_id: int,
        resource_type: str,
        resource_id: str,
        action: str,
        status: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        event = AuditEvent(
            id=str(__import__('uuid').uuid4()),
            event_type=event_type,
            actor_type=actor_type,
            actor_id=actor_id,
            organization_id=organization_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            details=details or {},
            timestamp=datetime.utcnow(),
        )
        self._events.append(event)
        return event

    def get_events(self, organization_id: Optional[int] = None) -> List[AuditEvent]:
        if organization_id is None:
            return list(self._events)
        return [e for e in self._events if e.organization_id == organization_id]

    def clear(self) -> None:
        self._events.clear()


audit_logger = AuditLogger()
