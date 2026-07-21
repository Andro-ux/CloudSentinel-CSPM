from typing import List

from backend.facts.exceptions import ExtractorError
from backend.facts.interfaces import IFactExtractor
from backend.facts.models import Fact, FactType
from backend.knowledge.interfaces import IKnowledgeEngine


class FactRegistry:

    def __init__(self):

        self._extractors: List[IFactExtractor] = []

    def register(self, extractor: IFactExtractor) -> None:

        self._extractors.append(extractor)

    def extract(self, knowledge: IKnowledgeEngine) -> List[Fact]:

        facts: List[Fact] = []

        seen_ids = set()

        for extractor in self._extractors:

            try:

                extracted = extractor.extract(knowledge)

                for fact in extracted:

                    if fact.id in seen_ids:

                        continue

                    seen_ids.add(fact.id)

                    facts.append(fact)

            except ExtractorError:

                raise

            except Exception as exc:

                raise ExtractorError(
                    extractor_name=extractor.__class__.__name__,
                    original_error=exc,
                )

        return facts

    @property
    def extractors(self) -> List[IFactExtractor]:

        return list(self._extractors)
