from typing import List

from backend.facts.models import Fact, FactSet, FactType
from backend.rules.base import BaseRule
from backend.rules.models import Finding, RuleMetadata, Severity


class ShieldedVMRule(BaseRule):

    def __init__(self):

        super().__init__(
            RuleMetadata(
                rule_id="CS-RULE-004",
                name="Shielded VM Disabled",
                description="Detects VMs without Shielded VM enabled.",
                version="1.0.0",
                author="CloudSentinel Core",
            )
        )

    def evaluate(self, fact_set: FactSet) -> List[Finding]:

        findings: List[Finding] = []

        for fact in fact_set.find_by_type(FactType.SHIELDED_VM_DISABLED):

            asset_id = fact.asset_id

            findings.append(

                self._make_finding(
                    rule_id=self.metadata.rule_id,
                    title="Shielded VM Disabled",
                    description=(
                        f"VM '{asset_id}' does not have Shielded VM enabled, "
                        f"reducing protection against firmware and boot-level attacks."
                    ),
                    severity=Severity.MEDIUM,
                    category="Compute",
                    asset_ids=[asset_id],
                    facts=[fact],
                    recommendation=(
                        "Enable Shielded VM with vTPM, secure boot, and integrity monitoring."
                    ),
                    references=[
                        "https://cloud.google.com/compute/shielded-vm"
                    ],
                    evidence=fact.evidence.value if isinstance(fact.evidence.value, dict) else {},
                    service="Compute",
                    resource_id=asset_id,
                )

            )

        return findings
