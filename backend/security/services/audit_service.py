from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from backend.database.models import AuditEvent as DBAuditEvent
from backend.security.models import AuditEvent


class AuditService:
    def log(
        self,
        db: Session,
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
        severity: str = "info",
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        event_id = str(__import__("uuid").uuid4())
        db_event = DBAuditEvent(
            id=event_id,
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
            severity=severity,
            details=details or {},
            timestamp=datetime.utcnow(),
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return AuditEvent(
            id=db_event.id,
            event_type=db_event.event_type,
            actor_type=db_event.actor_type,
            actor_id=db_event.actor_id,
            organization_id=db_event.organization_id,
            resource_type=db_event.resource_type,
            resource_id=db_event.resource_id,
            action=db_event.action,
            status=db_event.status,
            ip_address=db_event.ip_address,
            user_agent=db_event.user_agent,
            request_id=db_event.request_id,
            details=db_event.details or {},
            timestamp=db_event.timestamp,
        )

    def get_events(
        self,
        db: Session,
        organization_id: Optional[int] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        query = db.query(DBAuditEvent)
        if organization_id is not None:
            query = query.filter(DBAuditEvent.organization_id == organization_id)
        if event_type is not None:
            query = query.filter(DBAuditEvent.event_type == event_type)
        events = query.order_by(DBAuditEvent.timestamp.desc()).limit(limit).all()
        return [
            AuditEvent(
                id=e.id,
                event_type=e.event_type,
                actor_type=e.actor_type,
                actor_id=e.actor_id,
                organization_id=e.organization_id,
                resource_type=e.resource_type,
                resource_id=e.resource_id,
                action=e.action,
                status=e.status,
                ip_address=e.ip_address,
                user_agent=e.user_agent,
                request_id=e.request_id,
                details=e.details or {},
                timestamp=e.timestamp,
            )
            for e in events
        ]
