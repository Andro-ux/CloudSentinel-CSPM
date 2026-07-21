from collections import deque
from typing import Dict, List, Optional

from backend.correlation.models import AssetNode, Graph, Relationship
from backend.knowledge.cache import QueryCache
from backend.knowledge.exceptions import AssetNotFound


class GraphQuery:

    def __init__(self, graph: Graph, cache: QueryCache):

        self.graph = graph

        self.cache = cache

        self.cache.initialize(graph.edges, graph.nodes)

    def find_asset(self, asset_id: str) -> AssetNode:

        asset = self.graph.get_node(asset_id)

        if not asset:

            raise AssetNotFound(asset_id)

        return asset

    def find_assets(
        self,
        service: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> List[AssetNode]:

        service_index = self.cache.get_service_index()

        type_index = self.cache.get_type_index()

        if service and resource_type:

            service_nodes = service_index.get(service, [])

            return [

                node for node in service_nodes

                if node.resource_type == resource_type

            ]

        if service:

            return list(service_index.get(service, []))

        if resource_type:

            return list(type_index.get(resource_type, []))

        return list(self.graph.nodes)

    def find_neighbors(
        self,
        asset_id: str,
        relations: Optional[List[str]] = None,
    ) -> List[AssetNode]:

        neighbor_tuples = self.cache.get_neighbors(asset_id, relations)

        return [

            self.graph.get_node(target)

            for target, _ in neighbor_tuples

            if self.graph.get_node(target)

        ]

    def find_paths(
        self,
        source: str,
        target: str,
    ) -> List[List[str]]:

        if not self.graph.get_node(source) or not self.graph.get_node(target):

            return []

        visited = set()

        queue = deque()

        queue.append((source, [source]))

        paths = []

        while queue:

            node, path = queue.popleft()

            if node == target:

                paths.append(path)

                continue

            if node in visited:

                continue

            visited.add(node)

            for neighbour, _ in self.graph.adjacency.get(node, []):

                if neighbour not in visited:

                    queue.append((neighbour, path + [neighbour]))

        return paths

    def find_public_assets(self) -> List[AssetNode]:

        cached = self.cache.get_public_assets()

        if cached is not None:

            return cached

        public_assets = []

        for asset in self.graph.nodes:

            security = asset.properties.get("security", {})

            if security.get("public_ip", False):

                public_assets.append(asset)

        self.cache.cache_public_assets(public_assets)

        return self.cache.get_public_assets()

    def find_assets_with_relation(
        self,
        relation: str,
    ) -> List[tuple]:

        relation_index = self.cache.get_relation_index()

        return list(relation_index.get(relation.upper().strip(), []))

    def asset_exists(self, asset_id: str) -> bool:

        return self.graph.get_node(asset_id) is not None
