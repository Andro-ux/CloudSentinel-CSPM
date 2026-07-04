from abc import ABC, abstractmethod


class CloudProvider(ABC):

    @abstractmethod
    def collect_identity(self):
        pass

    @abstractmethod
    def collect_storage(self):
        pass

    @abstractmethod
    def collect_compute(self):
        pass

    @abstractmethod
    def collect_logging(self):
        pass