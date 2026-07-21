from typing import List

from backend.facts.models import Fact, FactSet, FactType
from backend.rules.base import BaseRule
from backend.rules.models import Finding, RuleMetadata, Severity


class MetadataServiceRule(BaseRule):

    def __init__(self):

        super().__init__(
            RuleMetadata(
                rule_id="CS-RULE-005",
                name="Metadata Service Access Enabled",
                description="Detects VMs with access to the instance metadata server.",
                version="1.0.0",
                author="CloudSentinel Core",
            )
        )

    def evaluate(self, fact_set: FactSet) -> List[Finding]:

        findings: List[Finding] = []

        for fact in fact_set.find_by_type(FactType.METADATA_SERVICE_ENABLED):

            asset_id = fact.asset_id

            findings.append(

                self._make_finding(
                    rule_id=self.metadata.rule_id,
                    title="Metadata Service Access Enabled",
                    description=(
                        f"VM '{asset_id}' has access to the instance metadata server, "
                        f"which can expose credentials and sensitive data."
                    ),
                    severity=Severity.MEDIUM,
                    category="Compute",
                    asset_ids=[asset_id],
                    facts=[fact],
                    recommendation=(
                        "Disable access to the instance metadata server or restrict "
                        "workload identity federation."
                    ),
                    references=[
                        "https://cloud.google.com/compute/docs/metadata/overview"
                    ],
                    evidence=fact.evidence.value if isinstance(fact.evidence.value, dict) else {},
                    service="Compute",
                    resource_id=asset_id,
                )

            )

        return findings
