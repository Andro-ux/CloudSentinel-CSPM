from collections import defaultdict

from backend.scoring.weights import (
    SEVERITY_WEIGHTS,
    MAX_SCORE,
)


class ScoreEngine:

    def __init__(self, findings):

        self.findings = findings

    def calculate(self):

        deductions = defaultdict(int)

        total_deduction = 0

        for finding in self.findings:

            severity = finding["severity"]

            weight = SEVERITY_WEIGHTS.get(
                severity,
                0,
            )

            deductions[
                finding["service"]
            ] += weight

            total_deduction += weight

        overall = max(
            MAX_SCORE - total_deduction,
            0,
        )

        services = {}

        for service, deduction in deductions.items():

            services[service] = max(
                MAX_SCORE - deduction,
                0,
            )

        return {

            "overall": overall,

            "services": services,

            "deductions": dict(
                deductions
            ),
        }