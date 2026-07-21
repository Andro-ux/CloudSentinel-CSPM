from abc import ABC, abstractmethod
from typing import Any, List


class IProviderPlugin(ABC):

    @abstractmethod
    def get_metadata(self) -> "ProviderMetadata":

        pass

    @abstractmethod
    def scan(self) -> Any:

        pass

    @abstractmethod
    def get_assets(self) -> List[Any]:

        pass

    @abstractmethod
    def validate(self) -> bool:

        pass
