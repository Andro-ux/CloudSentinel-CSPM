from typing import List

from backend.facts.interfaces import IFactExtractor
from backend.facts.models import Evidence, Fact, FactType
from backend.knowledge.interfaces import IKnowledgeEngine


class BaseExtractor(IFactExtractor):

    def extract(self, knowledge: IKnowledgeEngine) -> List[Fact]:

        raise NotImplementedError

    def _make_evidence(
        self,
        provider: str,
        source: str,
        attribute: str,
        value,
    ) -> Evidence:

        return Evidence(
            provider=provider,
            source=source,
            attribute=attribute,
            value=value,
        )

    def _fact_id(self, provider: str, fact_type: FactType, asset_id: str) -> str:

        return f"{provider}-{fact_type.value}-{asset_id}"
