from typing import List

from backend.facts.models import Fact, FactSet, FactType
from backend.rules.base import BaseRule
from backend.rules.models import Finding, RuleMetadata, Severity


class UnusedServiceAccountRule(BaseRule):

    def __init__(self):

        super().__init__(
            RuleMetadata(
                rule_id="CS-RULE-007",
                name="Unused Service Account",
                description="Detects service accounts not attached to any compute resource.",
                version="1.0.0",
                author="CloudSentinel Core",
            )
        )

    def evaluate(self, fact_set: FactSet) -> List[Finding]:

        findings: List[Finding] = []

        for fact in fact_set.find_by_type(FactType.UNUSED_SERVICE_ACCOUNT):

            asset_id = fact.asset_id

            findings.append(

                self._make_finding(
                    rule_id=self.metadata.rule_id,
                    title="Unused Service Account",
                    description=fact.description,
                    severity=Severity.LOW,
                    category="IAM",
                    asset_ids=[asset_id],
                    facts=[fact],
                    recommendation=(
                        "Delete or disable unused service accounts to reduce attack surface."
                    ),
                    references=[
                        "https://cloud.google.com/iam/docs/service-accounts"
                    ],
                    evidence=fact.evidence.value if isinstance(fact.evidence.value, dict) else {},
                    service="IAM",
                    resource_id=asset_id,
                )

            )

        return findings
