from typing import List

from backend.facts.interfaces import IFactEngine, IFactExtractor
from backend.facts.models import Fact, FactSet
from backend.facts.registry import FactRegistry
from backend.knowledge.interfaces import IKnowledgeEngine


class FactEngine(IFactEngine):

    def __init__(self, knowledge: IKnowledgeEngine, registry: FactRegistry):

        self.knowledge = knowledge

        self.registry = registry

    def extract(self) -> FactSet:

        facts = self.registry.extract(self.knowledge)

        return FactSet(facts)
