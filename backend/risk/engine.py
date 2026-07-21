from typing import Dict, List, Optional

from backend.risk.exceptions import StrategyError
from backend.risk.interfaces import IRiskEngine, IScoreStrategy
from backend.risk.models import Risk, RiskSet
from backend.risk.strategies.weighted import WeightedScoreStrategy
from backend.rules.models import Finding, FindingSet


class RiskEngine(IRiskEngine):

    def __init__(self, strategy: IScoreStrategy = None):

        self.strategy = strategy or WeightedScoreStrategy()

    def evaluate(
        self,
        finding_set: FindingSet,
        context: Dict = None,
    ) -> RiskSet:

        if context is None:

            context = {}

        risks: List[Risk] = []

        seen_ids = set()

        for finding in finding_set:

            try:

                risk = self.strategy.score(finding, context)

                if risk.id in seen_ids:

                    continue

                seen_ids.add(risk.id)

                risks.append(risk)

            except StrategyError:

                raise

            except Exception as exc:

                raise StrategyError(
                    strategy_name=self.strategy.__class__.__name__,
                    original_error=exc,
                )

        return RiskSet(risks)
