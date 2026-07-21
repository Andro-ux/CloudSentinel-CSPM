from typing import List

from backend.facts.models import FactSet
from backend.rules.interfaces import IRuleEngine, IRule
from backend.rules.models import Finding, FindingSet
from backend.rules.registry import RuleRegistry


class RuleEngine(IRuleEngine):

    def __init__(self, registry: RuleRegistry):

        self.registry = registry

    def evaluate(self, fact_set: FactSet) -> FindingSet:

        findings = self.registry.evaluate(fact_set)

        return FindingSet(findings)
