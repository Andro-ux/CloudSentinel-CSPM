from abc import ABC, abstractmethod


class CloudProvider(ABC):

    @abstractmethod
    def scan(self):
        """
        Execute a complete provider scan.
        """
        pass

    @abstractmethod
    def get_assets(self):
        """
        Return all discovered assets.
        """
        pass