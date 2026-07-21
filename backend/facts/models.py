from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class FactType(str, Enum):

    PUBLIC_VM = "PUBLIC_VM"

    PUBLIC_SUBNET = "PUBLIC_SUBNET"

    PUBLIC_BUCKET = "PUBLIC_BUCKET"

    UNENCRYPTED_BUCKET = "UNENCRYPTED_BUCKET"

    OPEN_FIREWALL = "OPEN_FIREWALL"

    ADMIN_SERVICE_ACCOUNT = "ADMIN_SERVICE_ACCOUNT"

    UNUSED_SERVICE_ACCOUNT = "UNUSED_SERVICE_ACCOUNT"

    OVER_PRIVILEGED_IDENTITY = "OVER_PRIVILEGED_IDENTITY"

    FLOW_LOGS_DISABLED = "FLOW_LOGS_DISABLED"

    AUDIT_LOGGING_DISABLED = "AUDIT_LOGGING_DISABLED"

    METADATA_SERVICE_ENABLED = "METADATA_SERVICE_ENABLED"

    SHIELDED_VM_DISABLED = "SHIELDED_VM_DISABLED"

    INTERNET_REACHABLE = "INTERNET_REACHABLE"

    VERSIONING_DISABLED = "VERSIONING_DISABLED"


@dataclass(frozen=True)
class Evidence:

    provider: str

    source: str

    attribute: str

    value: Any

    timestamp: Optional[datetime] = None


@dataclass(frozen=True)
class Fact:

    id: str

    asset_id: str

    fact_type: FactType

    severity: str

    provider: str

    category: str

    evidence: Evidence

    metadata: Dict[str, Any] = field(default_factory=dict)

    description: str = ""


class FactSet:

    def __init__(self, facts: List[Fact]):

        self._facts = tuple(facts)

        self._by_asset: Dict[str, List[Fact]] = {}

        self._by_type: Dict[FactType, List[Fact]] = {}

        for fact in self._facts:

            self._by_asset.setdefault(
                fact.asset_id,
                []
            ).append(fact)

            self._by_type.setdefault(
                fact.fact_type,
                []
            ).append(fact)

    @property
    def facts(self) -> tuple:

        return self._facts

    def __iter__(self):

        return iter(self._facts)

    def __len__(self) -> int:

        return len(self._facts)

    def __contains__(self, fact: Fact) -> bool:

        return fact in self._facts

    def find_by_asset(self, asset_id: str) -> List[Fact]:

        return list(self._by_asset.get(asset_id, []))

    def find_by_type(self, fact_type: FactType) -> List[Fact]:

        return list(self._by_type.get(fact_type, []))

    def statistics(self) -> Dict[str, int]:

        stats: Dict[str, int] = {}

        for fact in self._facts:

            key = fact.fact_type.value

            stats[key] = stats.get(key, 0) + 1

        return stats

    def grouped_by_type(self) -> Dict[FactType, List[Fact]]:

        return {

            key: list(value)

            for key, value in self._by_type.items()

        }

    def grouped_by_asset(self) -> Dict[str, List[Fact]]:

        return dict(self._by_asset)
