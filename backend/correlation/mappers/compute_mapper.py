from backend.correlation.asset_index import AssetIndex
from backend.correlation.builders.relationship_builder import RelationshipBuilder
from backend.correlation.mappers.base_mapper import BaseMapper
from backend.correlation.relationship_types import RelationshipType


class ComputeMapper(BaseMapper):

    def map(
        self,
        asset_index: AssetIndex,
        builder: RelationshipBuilder,
    ) -> None:

        for asset in asset_index.get_by_service("Compute"):

            relationships = asset.properties.get("relationships", {})

            #
            # Service Accounts
            #

            for service_account in relationships.get(
                "service_accounts",
                []
            ):

                candidate = asset_index.find_by_type_and_name(
                    "ServiceAccount",
                    service_account,
                )

                if candidate:

                    builder.connect(
                        asset.id,
                        candidate.id,
                        RelationshipType.USES,
                    )

            #
            # Subnets
            #

            for subnet in relationships.get("subnets", []):

                candidate = asset_index.find_by_type_and_name(
                    "Subnet",
                    subnet,
                )

                if candidate:

                    builder.connect(
                        asset.id,
                        candidate.id,
                        RelationshipType.IN_SUBNET,
                    )

            #
            # Networks / VPCs
            #

            for network in relationships.get("networks", []):

                candidate = asset_index.find_by_type_and_name(
                    "VPC",
                    network,
                )

                if candidate:

                    builder.connect(
                        asset.id,
                        candidate.id,
                        RelationshipType.IN_VPC,
                    )