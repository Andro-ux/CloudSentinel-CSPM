from backend.intelligence.knowledge_base import KNOWLEDGE_BASE


class FindingEnricher:

    def enrich(self, findings):

        enriched = []

        for finding in findings:

            rule = finding.get("rule_id")

            metadata = KNOWLEDGE_BASE.get(
                rule,
                {}
            )

            enriched.append({

                **finding,

                **metadata

            })

        return enriched