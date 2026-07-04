from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any


@dataclass
class Asset:
    account_id: int | None
    service: str
    resource_type: str
    resource_id: str
    name: str
    arn: str | None = None
    region: str | None = None
    tags: Dict[str, str] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    status: str = "ACTIVE"
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)