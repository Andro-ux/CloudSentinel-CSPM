from typing import List, Optional

from backend.correlation.models import AssetNode, Graph, Relationship
from backend.knowledge.cache import QueryCache
from backend.knowledge.exceptions import AssetNotFound, GraphNotInitialized
from backend.knowledge.graph_query import GraphQuery
from backend.knowledge.interfaces import IKnowledgeEngine


class KnowledgeEngine(IKnowledgeEngine):

    def __init__(self, graph: Graph):

        self.graph = graph

        self.cache = QueryCache()

        self.query = GraphQuery(graph, self.cache)

        self._initialized = True

    def find_asset(self, asset_id: str) -> AssetNode:

        if not self._initialized:

            raise GraphNotInitialized()

        return self.query.find_asset(asset_id)

    def find_assets(
        self,
        service: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> List[AssetNode]:

        if not self._initialized:

            raise GraphNotInitialized()

        return self.query.find_assets(service, resource_type)

    def find_neighbors(
        self,
        asset_id: str,
        relations: Optional[List[str]] = None,
    ) -> List[AssetNode]:

        if not self._initialized:

            raise GraphNotInitialized()

        return self.query.find_neighbors(asset_id, relations)

    def find_paths(
        self,
        source: str,
        target: str,
    ) -> List[List[str]]:

        if not self._initialized:

            raise GraphNotInitialized()

        return self.query.find_paths(source, target)

    def find_public_assets(self) -> List[AssetNode]:

        if not self._initialized:

            raise GraphNotInitialized()

        return self.query.find_public_assets()

    def find_assets_with_relation(
        self,
        relation: str,
    ) -> List[tuple]:

        if not self._initialized:

            raise GraphNotInitialized()

        return self.query.find_assets_with_relation(relation)

    def asset_exists(self, asset_id: str) -> bool:

        if not self._initialized:

            raise GraphNotInitialized()

        return self.query.asset_exists(asset_id)

    def get_adjacency(self) -> dict:

        if not self._initialized:

            raise GraphNotInitialized()

        return self.graph.adjacency

    def get_edges(self) -> List[Relationship]:

        if not self._initialized:

            raise GraphNotInitialized()

        return self.graph.get_edges()
