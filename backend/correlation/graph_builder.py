from collections import defaultdict

from backend.correlation.asset_index import AssetIndex
from backend.correlation.models import AssetNode, Graph, Relationship


class GraphBuilder:

    def __init__(self):

        self.index = AssetIndex()

        self._edges = []

        self._adjacency = defaultdict(list)

        self._built = False

    def add_assets(self, assets):

        for asset in assets:

            node = AssetNode(

                id=str(asset.get("resource_id")),

                service=asset.get("service"),

                resource_type=asset.get("resource_type"),

                name=asset.get("name"),

                properties=asset,

            )

            self.index.add(node)

    def add_relationships(self, relationships):

        for rel in relationships:

            self._edges.append(rel)

            self._adjacency[rel.source].append(

                (

                    rel.target,

                    rel.relation

                )

            )

    def build(self, relationships=None):

        if self._built:

            raise RuntimeError(

                "GraphBuilder has already been built"

            )

        self._built = True

        if relationships:

            self.add_relationships(relationships)

        adjacency = {}

        for k, v in self._adjacency.items():

            adjacency[k] = list(v)

        return Graph(

            asset_index=self.index,

            edges=list(self._edges),

            adjacency=adjacency,

        )
