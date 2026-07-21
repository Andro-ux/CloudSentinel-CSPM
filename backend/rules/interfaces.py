from abc import ABC, abstractmethod
from typing import List

from backend.facts.models import FactSet
from backend.rules.models import Finding, RuleMetadata


class IRule(ABC):

    @property
    @abstractmethod
    def metadata(self) -> RuleMetadata:

        pass

    @abstractmethod
    def evaluate(self, fact_set: FactSet) -> List[Finding]:

        pass


class IRuleEngine(ABC):

    @abstractmethod
    def evaluate(self, fact_set: FactSet) -> "FindingSet":

        pass
