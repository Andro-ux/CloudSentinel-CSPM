from collections import defaultdict
from typing import Any, Dict, List, Optional

from backend.correlation.models import AssetNode, Relationship


class QueryCache:

    def __init__(self):

        self._neighbor_index: Dict[str, List[tuple]] = {}

        self._public_assets: Optional[List[AssetNode]] = None

        self._service_index: Dict[str, List[AssetNode]] = {}

        self._type_index: Dict[str, List[AssetNode]] = {}

        self._relation_index: Dict[str, List[tuple]] = {}

        self._initialized = False

    def initialize(self, edges: List[Relationship], nodes: List[AssetNode]):

        if self._initialized:

            return

        self._build_neighbor_index(edges)

        self._build_service_index(nodes)

        self._build_type_index(nodes)

        self._build_relation_index(edges)

        self._initialized = True

    def _build_neighbor_index(self, edges: List[Relationship]):

        index = defaultdict(list)

        for rel in edges:

            index[rel.source].append(

                (

                    rel.target,

                    rel.relation

                )

            )

            index[rel.target].append(

                (

                    rel.source,

                    rel.relation

                )

            )

        self._neighbor_index = dict(index)

    def _build_service_index(self, nodes: List[AssetNode]):

        index = defaultdict(list)

        for node in nodes:

            index[node.service].append(node)

        self._service_index = dict(index)

    def _build_type_index(self, nodes: List[AssetNode]):

        index = defaultdict(list)

        for node in nodes:

            index[node.resource_type].append(node)

        self._type_index = dict(index)

    def _build_relation_index(self, edges: List[Relationship]):

        index = defaultdict(list)

        for rel in edges:

            index[rel.relation].append(

                (

                    rel.source,

                    rel.target

                )

            )

        self._relation_index = dict(index)

    def get_neighbors(self, asset_id: str, relations: Optional[List[str]] = None) -> List[tuple]:

        raw = self._neighbor_index.get(asset_id, [])

        if relations is None:

            return list(raw)

        return [

            (target, rel)

            for target, rel in raw

            if rel in relations

        ]

    def get_service_index(self) -> Dict[str, List[AssetNode]]:

        return self._service_index

    def get_type_index(self) -> Dict[str, List[AssetNode]]:

        return self._type_index

    def get_relation_index(self) -> Dict[str, List[tuple]]:

        return self._relation_index

    def cache_public_assets(self, assets: List[AssetNode]):

        self._public_assets = list(assets)

    def get_public_assets(self) -> Optional[List[AssetNode]]:

        return self._public_assets
