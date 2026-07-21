from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from backend.rules.models import Finding, FindingSet
from backend.risk.models import Risk, RiskSet


class IScoreStrategy(ABC):

    @abstractmethod
    def score(self, finding: Finding, context: Dict) -> Risk:

        pass


class IRiskEngine(ABC):

    @abstractmethod
    def evaluate(self, finding_set: FindingSet, context: Dict = None) -> RiskSet:

        pass
