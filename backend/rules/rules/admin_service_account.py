from typing import List

from backend.facts.models import Fact, FactSet, FactType
from backend.rules.base import BaseRule
from backend.rules.models import Finding, RuleMetadata, Severity


class AdminServiceAccountRule(BaseRule):

    def __init__(self):

        super().__init__(
            RuleMetadata(
                rule_id="CS-RULE-006",
                name="Admin Service Account Detected",
                description="Detects service accounts with administrative or overly broad permissions.",
                version="1.0.0",
                author="CloudSentinel Core",
            )
        )

    def evaluate(self, fact_set: FactSet) -> List[Finding]:

        findings: List[Finding] = []

        for fact in fact_set.find_by_type(FactType.ADMIN_SERVICE_ACCOUNT):

            asset_id = fact.asset_id

            findings.append(

                self._make_finding(
                    rule_id=self.metadata.rule_id,
                    title="Admin Service Account Detected",
                    description=fact.description,
                    severity=Severity.HIGH,
                    category="IAM",
                    asset_ids=[asset_id],
                    facts=[fact],
                    recommendation=(
                        "Replace with a dedicated least-privilege service account "
                        "and apply the principle of least privilege."
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
