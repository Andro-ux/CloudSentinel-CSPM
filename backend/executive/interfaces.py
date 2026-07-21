from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from backend.executive.models import (
    ExecutiveDashboard,
    ExecutiveMetrics,
    ExecutiveNarrative,
    ExecutiveSummary,
    Insight,
    Recommendation,
    SecurityScore,
    SecurityDimensions,
    ScoreBreakdown,
)


class IScoreStrategy(ABC):

    @abstractmethod
    def calculate_score(
        self,
        findings,
        risks,
        facts,
        assets,
    ) -> SecurityScore:

        pass


class INarrativeStrategy(ABC):

    @abstractmethod
    def generate_narrative(
        self,
        dashboard: ExecutiveDashboard,
    ) -> ExecutiveNarrative:

        pass


class IDashboardBuilder(ABC):

    @abstractmethod
    def build(
        self,
        summary: ExecutiveSummary,
        security_score: SecurityScore,
        dimensions: SecurityDimensions,
        breakdown: ScoreBreakdown,
        metrics: ExecutiveMetrics,
        risks,
        recommendations: List[Recommendation],
        insights: List[Insight],
        narrative: ExecutiveNarrative,
    ) -> ExecutiveDashboard:

        pass


class IMetricsBuilder(ABC):

    @abstractmethod
    def build(
        self,
        assets,
        findings,
        risks,
        facts,
        attack_paths,
    ) -> ExecutiveMetrics:

        pass


class IInsightBuilder(ABC):

    @abstractmethod
    def build(self, risks, findings, facts) -> List[Insight]:

        pass


class IRecommendationBuilder(ABC):

    @abstractmethod
    def build(self, risks, findings, facts) -> List[Recommendation]:

        pass


class INarrativeBuilder(ABC):

    @abstractmethod
    def build(self, dashboard: ExecutiveSummary) -> ExecutiveNarrative:

        pass
