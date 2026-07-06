from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AssetNode:

    id: str

    service: str

    resource_type: str

    name: str

    properties: Dict = field(default_factory=dict)

    relationships: List[str] = field(default_factory=list)


@dataclass
class Relationship:

    source: str

    target: str

    relation: str


@dataclass
class AttackPath:

    nodes: List[str]

    title: str

    severity: str

    risk_score: int

    description: str


@dataclass
class CorrelationResult:

    attack_paths: List[AttackPath] = field(default_factory=list)

    relationships: List[Relationship] = field(default_factory=list)

    security_score: int = 100