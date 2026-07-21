from typing import List

from backend.executive.interfaces import INarrativeBuilder
from backend.executive.models import ExecutiveDashboard, ExecutiveNarrative
from backend.executive.strategies.narrative import INarrativeStrategy, DefaultNarrativeStrategy


class NarrativeBuilder(INarrativeBuilder):

    def __init__(self, strategy: INarrativeStrategy = None):

        self.strategy = strategy or DefaultNarrativeStrategy()

    def build(self, dashboard: ExecutiveDashboard) -> ExecutiveNarrative:

        return self.strategy.generate_narrative(dashboard)
