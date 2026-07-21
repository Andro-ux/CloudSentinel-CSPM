from backend.correlation.asset_index import AssetIndex
from backend.correlation.builders.relationship_builder import RelationshipBuilder
from backend.correlation.mappers.base_mapper import BaseMapper
from backend.correlation.relationship_types import RelationshipType


class NetworkMapper(BaseMapper):

    def map(
        self,
        asset_index: AssetIndex,
        builder: RelationshipBuilder,
    ) -> None:

        self._map_firewalls(
            asset_index,
            builder
        )

        self._map_subnets(
            asset_index,
            builder
        )

    def _map_firewalls(
        self,
        asset_index: AssetIndex,
        builder: RelationshipBuilder
    ) -> None:

        firewalls = asset_index.get_by_service("Firewall")

        computes = asset_index.get_by_service("Compute")

        vm_tags = {
            vm.id: {
                tag.lower()
                for tag in vm.properties.get(
                    "metadata",
                    {}
                ).get(
                    "tags",
                    []
                )
            }

            for vm in computes
        }

        for firewall in firewalls:

            targets = [
                tag.lower()
                for tag in firewall.properties.get(
                    "target_tags",
                    []
                )
            ]

            if not targets:

                for vm in computes:
                    builder.connect(
                        firewall.id,
                        vm.id,
                        RelationshipType.PROTECTED_BY,
                    )

                continue

            for vm in computes:

                if vm_tags[vm.id].intersection(targets):
                    builder.connect(
                        firewall.id,
                        vm.id,
                        RelationshipType.PROTECTED_BY,
                    )

    def _map_subnets(
        self,
        asset_index: AssetIndex,
        builder: RelationshipBuilder
    ) -> None:

        subnets = asset_index.find_by_type("Subnet")

        for subnet in subnets:

            relationships = subnet.properties.get(
                "relationships",
                {}
            )

            for vpc_name in relationships.get(
                "vpcs",
                []
            ):

                vpc_node = asset_index.find_by_type_and_name(
                    "VPC",
                    vpc_name
                )

                if vpc_node:
                    builder.connect(
                        subnet.id,
                        vpc_node.id,
                        RelationshipType.IN_VPC,
                    )
