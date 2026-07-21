from typing import List

from backend.facts.models import Fact, FactSet, FactType
from backend.rules.base import BaseRule
from backend.rules.models import Finding, RuleMetadata, Severity


class PublicVMRule(BaseRule):

    def __init__(self):

        super().__init__(
            RuleMetadata(
                rule_id="CS-RULE-001",
                name="Public VM Detected",
                description="Detects VMs with public IP addresses exposed to the internet.",
                version="1.0.0",
                author="CloudSentinel Core",
            )
        )

    def evaluate(self, fact_set: FactSet) -> List[Finding]:

        findings: List[Finding] = []

        public_vm_facts = fact_set.find_by_type(FactType.PUBLIC_VM)

        for fact in public_vm_facts:

            asset_id = fact.asset_id

            vm_name = fact.evidence.value if isinstance(fact.evidence.value, str) else asset_id

            findings.append(

                self._make_finding(
                    rule_id=self.metadata.rule_id,
                    title="Public VM Detected",
                    description=(
                        f"VM '{asset_id}' has a public IP address and is "
                        f"directly reachable from the internet."
                    ),
                    severity=Severity.HIGH,
                    category="Network",
                    asset_ids=[asset_id],
                    facts=[fact],
                    recommendation=(
                        "Remove the public IP or place the VM behind Cloud NAT, "
                        "a bastion host, or a load balancer."
                    ),
                    references=[
                        "https://cloud.google.com/compute/docs/ip-addresses"
                    ],
                    evidence={
                        "public_ip": True,
                        "vm": asset_id,
                    },
                    service="Compute",
                    resource_id=asset_id,
                )

            )

        return findings
