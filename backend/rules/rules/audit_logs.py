from typing import List

from backend.facts.models import Fact, FactSet, FactType
from backend.rules.base import BaseRule
from backend.rules.models import Finding, RuleMetadata, Severity


class AuditLoggingRule(BaseRule):

    def __init__(self):

        super().__init__(
            RuleMetadata(
                rule_id="CS-RULE-009",
                name="Audit Logging Disabled",
                description="Detects projects without audit logging configuration.",
                version="1.0.0",
                author="CloudSentinel Core",
            )
        )

    def evaluate(self, fact_set: FactSet) -> List[Finding]:

        findings: List[Finding] = []

        for fact in fact_set.find_by_type(FactType.AUDIT_LOGGING_DISABLED):

            asset_id = fact.asset_id

            findings.append(

                self._make_finding(
                    rule_id=self.metadata.rule_id,
                    title="Audit Logging Disabled",
                    description=fact.description,
                    severity=Severity.HIGH,
                    category="Logging",
                    asset_ids=[asset_id],
                    facts=[fact],
                    recommendation=(
                        "Enable Cloud Audit Logs for all critical services including "
                        "Admin Activity and Data Access logs."
                    ),
                    references=[
                        "https://cloud.google.com/logging/docs/audit"
                    ],
                    evidence=fact.evidence.value if isinstance(fact.evidence.value, dict) else {},
                    service="Logging",
                    resource_id=asset_id,
                )

            )

        return findings
