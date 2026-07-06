from backend.correlation.models import Relationship
from backend.correlation.mappers.base_mapper import BaseMapper


class ComputeMapper(BaseMapper):

    def map(self, asset_index):

        relationships = []

        compute_assets = asset_index.get_by_service("Compute")

        for vm in compute_assets:

            rel = vm.properties.get("relationships", {})

            #
            # VM -> Service Accounts
            #

            for sa in rel.get("service_accounts", []):

                relationships.append(

                    Relationship(

                        source=vm.id,

                        target=sa,

                        relation="USES"

                    )

                )

            #
            # VM -> Subnets
            #

            for subnet in rel.get("subnets", []):

                relationships.append(

                    Relationship(

                        source=vm.id,

                        target=subnet,

                        relation="BELONGS_TO"

                    )

                )

            #
            # VM -> Networks (VPC)
            #

            for network in rel.get("networks", []):

                relationships.append(

                    Relationship(

                        source=vm.id,

                        target=network,

                        relation="BELONGS_TO"

                    )

                )

            #
            # VM -> Disks
            #

            for disk in rel.get("disks", []):

                relationships.append(

                    Relationship(

                        source=vm.id,

                        target=disk,

                        relation="ATTACHED_TO"

                    )

                )

        return relationships