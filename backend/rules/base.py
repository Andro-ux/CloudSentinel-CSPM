from typing import List

from backend.facts.models import Fact, FactSet
from backend.rules.interfaces import IRule
from backend.rules.models import Finding, RuleMetadata, Severity


class BaseRule(IRule):

    def __init__(self, metadata: RuleMetadata):

        self._metadata = metadata

    @property
    def metadata(self) -> RuleMetadata:

        return self._metadata

    def _make_finding(
        self,
        rule_id: str,
        title: str,
        description: str,
        severity: Severity,
        category: str,
        asset_ids: List[str],
        facts: List[Fact],
        recommendation: str,
        references: List[str],
        evidence: dict,
        service: str = "",
        resource_id: str = "",
    ) -> Finding:

        return Finding(
            id=f"{rule_id}-{'-'.join(asset_ids)}",
            rule_id=rule_id,
            title=title,
            description=description,
            severity=severity,
            category=category,
            asset_ids=asset_ids,
            facts=facts,
            recommendation=recommendation,
            references=references,
            evidence=evidence,
            service=service,
            resource_id=resource_id,
        )
