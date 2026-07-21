from abc import ABC, abstractmethod
from typing import List

from backend.facts.models import Fact, FactType
from backend.knowledge.interfaces import IKnowledgeEngine


class IFactExtractor(ABC):

    @property
    @abstractmethod
    def fact_types(self) -> List[FactType]:

        pass

    @abstractmethod
    def extract(self, knowledge: IKnowledgeEngine) -> List[Fact]:

        pass


class IFactEngine(ABC):

    @abstractmethod
    def extract(self) -> "FactSet":

        pass
