from typing import List

from backend.facts.extractors.base import BaseExtractor
from backend.facts.models import Evidence, Fact, FactType
from backend.knowledge.interfaces import IKnowledgeEngine


class NetworkFactsExtractor(BaseExtractor):

    @property
    def fact_types(self) -> List[FactType]:

        return [

            FactType.PUBLIC_VM,

            FactType.PUBLIC_SUBNET,

            FactType.INTERNET_REACHABLE,

            FactType.OPEN_FIREWALL,

        ]

    def extract(self, knowledge: IKnowledgeEngine) -> List[Fact]:

        facts: List[Fact] = []

        public_vms = knowledge.find_public_assets()

        public_vm_ids = set()

        for vm in public_vms:

            public_vm_ids.add(vm.id)

            facts.append(

                Fact(

                    id=self._fact_id(
                        knowledge.get_adjacency() and "knowledge" or "mock",
                        FactType.PUBLIC_VM,
                        vm.id,
                    ),

                    asset_id=vm.id,

                    fact_type=FactType.PUBLIC_VM,

                    severity="HIGH",

                    provider=vm.properties.get("cloud", "unknown"),

                    category="Network",

                    evidence=self._make_evidence(
                        provider=vm.properties.get("cloud", "unknown"),
                        source="asset.security",
                        attribute="public_ip",
                        value=True,
                    ),

                    description=(
                        f"VM '{vm.name}' has a public IP address and is "
                        f"directly reachable from the internet."
                    ),

                )

            )

        for subnet in knowledge.find_assets(resource_type="Subnet"):

            neighbors = knowledge.find_neighbors(subnet.id)

            has_public_vm = any(

                neighbor.id in public_vm_ids

                for neighbor in neighbors

                if neighbor.resource_type == "VM"

            )

            if has_public_vm:

                facts.append(

                    Fact(

                        id=self._fact_id(
                            subnet.properties.get("cloud", "unknown"),
                            FactType.PUBLIC_SUBNET,
                            subnet.id,
                        ),

                        asset_id=subnet.id,

                        fact_type=FactType.PUBLIC_SUBNET,

                        severity="HIGH",

                        provider=subnet.properties.get("cloud", "unknown"),

                        category="Network",

                        evidence=self._make_evidence(
                            provider=subnet.properties.get("cloud", "unknown"),
                            source="asset.relationships",
                            attribute="public_vms",
                            value=True,
                        ),

                        description=(
                            f"Subnet '{subnet.name}' contains internet-accessible "
                            f"resources with public IP addresses."
                        ),

                    )

                )

        for vm in public_vms:

            facts.append(

                Fact(

                    id=self._fact_id(
                        vm.properties.get("cloud", "unknown"),
                        FactType.INTERNET_REACHABLE,
                        vm.id,
                    ),

                    asset_id=vm.id,

                    fact_type=FactType.INTERNET_REACHABLE,

                    severity="HIGH",

                    provider=vm.properties.get("cloud", "unknown"),

                    category="Network",

                    evidence=self._make_evidence(
                        provider=vm.properties.get("cloud", "unknown"),
                        source="asset.security",
                        attribute="public_ip",
                        value=True,
                    ),

                    description=(
                        f"Asset '{vm.name}' is reachable directly from "
                        f"the internet."
                    ),

                )

            )

        firewalls = knowledge.find_assets(service="Firewall")

        for firewall in firewalls:

            target_tags = firewall.properties.get("target_tags", [])

            if not target_tags:

                facts.append(

                    Fact(

                        id=self._fact_id(
                            firewall.properties.get("cloud", "unknown"),
                            FactType.OPEN_FIREWALL,
                            firewall.id,
                        ),

                        asset_id=firewall.id,

                        fact_type=FactType.OPEN_FIREWALL,

                        severity="HIGH",

                        provider=firewall.properties.get("cloud", "unknown"),

                        category="Network",

                        evidence=self._make_evidence(
                            provider=firewall.properties.get("cloud", "unknown"),
                            source="asset.properties",
                            attribute="target_tags",
                            value=target_tags,
                        ),

                        description=(
                            f"Firewall '{firewall.name}' has no target tags and "
                            f"may apply to all resources."
                        ),

                    )

                )

        return facts
