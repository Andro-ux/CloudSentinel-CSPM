from dataclasses import dataclass, field
from typing import List


@dataclass
class ScanBundle:

    assets: List[dict] = field(
        default_factory=list
    )

    findings: List[dict] = field(
        default_factory=list
    )