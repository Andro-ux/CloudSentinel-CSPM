from typing import List

from backend.facts.models import FactSet
from backend.rules.exceptions import RuleExecutionError
from backend.rules.interfaces import IRule
from backend.rules.models import Finding


class RuleRegistry:

    def __init__(self):

        self._rules: List[IRule] = []

    def register(self, rule: IRule) -> None:

        self._rules.append(rule)

    def evaluate(self, fact_set: FactSet) -> List[Finding]:

        findings: List[Finding] = []

        seen_ids = set()

        for rule in self._rules:

            try:

                rule_findings = rule.evaluate(fact_set)

                for finding in rule_findings:

                    if finding.id in seen_ids:

                        continue

                    seen_ids.add(finding.id)

                    findings.append(finding)

            except RuleExecutionError:

                raise

            except Exception as exc:

                raise RuleExecutionError(
                    rule_id=rule.metadata.rule_id,
                    original_error=exc,
                )

        return findings

    @property
    def rules(self) -> List[IRule]:

        return list(self._rules)
