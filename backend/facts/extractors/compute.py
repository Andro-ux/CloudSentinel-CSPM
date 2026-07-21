from typing import List

from backend.facts.extractors.base import BaseExtractor
from backend.facts.models import Evidence, Fact, FactType
from backend.knowledge.interfaces import IKnowledgeEngine


class ComputeFactsExtractor(BaseExtractor):

    @property
    def fact_types(self) -> List[FactType]:

        return [

            FactType.SHIELDED_VM_DISABLED,

            FactType.METADATA_SERVICE_ENABLED,

        ]

    def extract(self, knowledge: IKnowledgeEngine) -> List[Fact]:

        facts: List[Fact] = []

        for vm in knowledge.find_assets(resource_type="VM"):

            security = vm.properties.get("security", {})

            shielded_vm = security.get("shielded_vm", False)

            if not shielded_vm:

                facts.append(

                    Fact(

                        id=self._fact_id(
                            vm.properties.get("cloud", "unknown"),
                            FactType.SHIELDED_VM_DISABLED,
                            vm.id,
                        ),

                        asset_id=vm.id,

                        fact_type=FactType.SHIELDED_VM_DISABLED,

                        severity="MEDIUM",

                        provider=vm.properties.get("cloud", "unknown"),

                        category="Compute",

                        evidence=self._make_evidence(
                            provider=vm.properties.get("cloud", "unknown"),
                            source="asset.security",
                            attribute="shielded_vm",
                            value=False,
                        ),

                        description=(
                            f"VM '{vm.name}' does not have Shielded VM enabled, "
                            f"reducing protection against firmware and boot-level attacks."
                        ),

                    )

                )

            facts.append(

                Fact(

                    id=self._fact_id(
                        vm.properties.get("cloud", "unknown"),
                        FactType.METADATA_SERVICE_ENABLED,
                        vm.id,
                    ),

                    asset_id=vm.id,

                    fact_type=FactType.METADATA_SERVICE_ENABLED,

                    severity="LOW",

                    provider=vm.properties.get("cloud", "unknown"),

                    category="Compute",

                    evidence=self._make_evidence(
                        provider=vm.properties.get("cloud", "unknown"),
                        source="asset.properties",
                        attribute="metadata_server",
                        value=True,
                    ),

                    description=(
                        f"VM '{vm.name}' has access to the instance metadata "
                        f"server, which can expose credentials and sensitive data."
                    ),

                )

            )

        return facts
