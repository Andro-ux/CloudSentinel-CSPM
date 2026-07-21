from typing import List

from backend.facts.models import Fact, FactSet, FactType
from backend.rules.base import BaseRule
from backend.rules.models import Finding, RuleMetadata, Severity


class OpenFirewallRule(BaseRule):

    def __init__(self):

        super().__init__(
            RuleMetadata(
                rule_id="CS-RULE-003",
                name="Open Firewall Detected",
                description="Detects firewall rules with no target tags that may apply to all resources.",
                version="1.0.0",
                author="CloudSentinel Core",
            )
        )

    def evaluate(self, fact_set: FactSet) -> List[Finding]:

        findings: List[Finding] = []

        for fact in fact_set.find_by_type(FactType.OPEN_FIREWALL):

            asset_id = fact.asset_id

            findings.append(

                self._make_finding(
                    rule_id=self.metadata.rule_id,
                    title="Open Firewall Detected",
                    description=(
                        f"Firewall '{asset_id}' has no target tags and may allow "
                        f"traffic to all resources in the network."
                    ),
                    severity=Severity.HIGH,
                    category="Network",
                    asset_ids=[asset_id],
                    facts=[fact],
                    recommendation=(
                        "Add target tags to restrict this firewall rule to specific resources."
                    ),
                    references=[
                        "https://cloud.google.com/vpc/docs/using-firewalls"
                    ],
                    evidence=fact.evidence.value if isinstance(fact.evidence.value, dict) else {},
                    service="Firewall",
                    resource_id=asset_id,
                )

            )

        return findings
