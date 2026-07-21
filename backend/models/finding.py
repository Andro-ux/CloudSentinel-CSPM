from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Finding:

    rule_id: str

    title: str

    description: str

    severity: str

    category: str

    service: str

    resource_id: str

    resource_name: str

    recommendation: str

    frameworks: List[str] = field(default_factory=list)

    business_impact: str = ""

    likelihood: str = ""

    estimated_remediation: str = ""

    priority: str = ""

    metadata: Dict = field(default_factory=dict)