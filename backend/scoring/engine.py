from collections import defaultdict

from backend.scoring.domain_map import DOMAIN_MAP
from backend.scoring.severity_weights import SEVERITY_WEIGHTS


class RiskDomainEngine:

    def calculate(self, findings):

        domain_scores = defaultdict(lambda: 100)

        contributors = defaultdict(list)

        for finding in findings:

            category = finding.get("category", "").lower()

            domain = DOMAIN_MAP.get(category)

            if not domain:
                continue

            severity = finding.get(
                "severity",
                "LOW"
            ).upper()

            deduction = SEVERITY_WEIGHTS.get(
                severity,
                0
            )

            domain_scores[domain] = max(
                0,
                domain_scores[domain] - deduction
            )

            contributors[domain].append({

                "title": finding.get(
                    "title",
                    "Unknown"
                ),

                "severity": severity,

                "deduction": deduction

            })

        if not domain_scores:

            overall = 100

        else:

            overall = int(

                sum(

                    domain_scores.values()

                )

                /

                len(

                    domain_scores

                )

            )

        grade = self._grade(
            overall
        )

        return {

            "overall": overall,

            "grade": grade,

            "domains": dict(
                domain_scores
            ),

            "contributors": dict(
                contributors
            )

        }

    def _grade(
        self,
        score
    ):

        if score >= 90:
            return "A"

        if score >= 80:
            return "B"

        if score >= 70:
            return "C"

        if score >= 60:
            return "D"

        return "F"