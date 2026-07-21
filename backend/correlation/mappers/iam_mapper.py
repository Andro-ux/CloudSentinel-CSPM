from backend.correlation.relationship_types import RelationshipType


class IAMMapper:

    def map(
        self,
        assets,
        builder
    ):

        #
        # Build lookup by asset name
        #

        asset_lookup = {
            asset.name: asset
            for asset in assets
        }

        #
        # Every IAM asset should expose:
        #
        # properties["members"]
        # properties["roles"]
        #

        for asset in assets:

            if asset.service != "IAM":
                continue

            members = asset.properties.get(
                "members",
                []
            )

            for member in members:

                candidate = asset_lookup.get(
                    member
                )

                if candidate:

                    builder.connect(

                        candidate.id,

                        asset.id,

                        RelationshipType.HAS_PERMISSION

                    )