from __future__ import annotations

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


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

    provider: str = ""

    confidence: float = 1.0

    metadata: Dict[str, Any] = field(default_factory=dict)

    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Graph:

    asset_index: "AssetIndex"

    edges: List[Relationship]

    adjacency: Dict[str, List[tuple]]

    @property
    def nodes(self):

        return self.asset_index.all_assets()

    def get_node(self, node_id: str):

        return self.asset_index.get(node_id)

    def get_edges(self):

        return list(self.edges)

    def get_neighbors(self, node_id: str, relations: list = None):

        neighbors = []

        for rel in self.edges:

            if relations is not None and rel.relation not in relations:

                continue

            if rel.source == node_id:

                neighbor = self.asset_index.get(rel.target)

                if neighbor:

                    neighbors.append(neighbor)

            elif rel.target == node_id:

                neighbor = self.asset_index.get(rel.source)

                if neighbor:

                    neighbors.append(neighbor)

        return neighbors


@dataclass
class AttackPath:

    nodes: List[str]

    title: str

    severity: str

    risk_score: int

    description: str

    graph_paths: List[List[str]] = field(default_factory=list)

    techniques: List[str] = field(default_factory=list)

    mitigations: List[str] = field(default_factory=list)


@dataclass
class CorrelationResult:

    attack_paths: List[AttackPath] = field(default_factory=list)

    relationships: List[Relationship] = field(default_factory=list)

    security_score: int = 100

    fact_set: FactSet | None = None

    finding_set: FindingSet | None = None

    risk_set: RiskSet | None = None

    dashboard: ExecutiveDashboard | None = None
