from typing import List

from backend.facts.models import Fact, FactSet, FactType
from backend.rules.base import BaseRule
from backend.rules.models import Finding, RuleMetadata, Severity


class FlowLogsRule(BaseRule):

    def __init__(self):

        super().__init__(
            RuleMetadata(
                rule_id="CS-RULE-008",
                name="VPC Flow Logs Disabled",
                description="Detects subnets without VPC Flow Logs enabled.",
                version="1.0.0",
                author="CloudSentinel Core",
            )
        )

    def evaluate(self, fact_set: FactSet) -> List[Finding]:

        findings: List[Finding] = []

        for fact in fact_set.find_by_type(FactType.FLOW_LOGS_DISABLED):

            asset_id = fact.asset_id

            findings.append(

                self._make_finding(
                    rule_id=self.metadata.rule_id,
                    title="VPC Flow Logs Disabled",
                    description=fact.description,
                    severity=Severity.MEDIUM,
                    category="Logging",
                    asset_ids=[asset_id],
                    facts=[fact],
                    recommendation=(
                        "Enable VPC Flow Logs for network visibility and incident response."
                    ),
                    references=[
                        "https://cloud.google.com/vpc/docs/flow-logs"
                    ],
                    evidence=fact.evidence.value if isinstance(fact.evidence.value, dict) else {},
                    service="Network",
                    resource_id=asset_id,
                )

            )

        return findings
