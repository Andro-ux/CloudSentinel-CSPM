from backend.correlation.asset_index import AssetIndex
from backend.correlation.models import AssetNode


class GraphBuilder:

    def __init__(self):

        self.index = AssetIndex()

    def add_assets(self, assets):

        for asset in assets:

            node = AssetNode(

                id=str(asset.get("resource_id")),

                service=asset.get("service"),

                resource_type=asset.get("resource_type"),

                name=asset.get(
                    "display_name",
                    asset.get("name", "")
                ),

                properties=asset,

            )

            self.index.add(node)

    def build(self):

        return self.index