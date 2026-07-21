from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from backend.correlation.models import AssetNode, Relationship


class IKnowledgeEngine(ABC):

    @abstractmethod
    def find_asset(self, asset_id: str) -> AssetNode:

        pass

    @abstractmethod
    def find_assets(
        self,
        service: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> List[AssetNode]:

        pass

    @abstractmethod
    def find_neighbors(
        self,
        asset_id: str,
        relations: Optional[List[str]] = None,
    ) -> List[AssetNode]:

        pass

    @abstractmethod
    def find_paths(
        self,
        source: str,
        target: str,
    ) -> List[List[str]]:

        pass

    @abstractmethod
    def find_public_assets(self) -> List[AssetNode]:

        pass

    @abstractmethod
    def find_assets_with_relation(
        self,
        relation: str,
    ) -> List[tuple]:

        pass

    @abstractmethod
    def asset_exists(self, asset_id: str) -> bool:

        pass

    @abstractmethod
    def get_adjacency(self) -> Dict[str, List[tuple]]:

        pass

    @abstractmethod
    def get_edges(self) -> List[Relationship]:

        pass
