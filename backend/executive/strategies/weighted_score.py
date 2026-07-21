from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.executive.models import (
    SecurityDimensions,
    SecurityScore,
    ScoreBreakdown,
)


@dataclass(frozen=True)
class ScoreWeights:

    base_score: int = 100

    network_deduction: int = 10

    identity_deduction: int = 8

    storage_deduction: int = 6

    logging_deduction: int = 3

    compute_deduction: int = 2

    public_exposure_multiplier: float = 1.5

    attack_path_multiplier: float = 1.2


class WeightedScoreStrategy:

    def __init__(self, weights: ScoreWeights = None):

        self.weights = weights or ScoreWeights()

    def calculate_score(
        self,
        findings,
        risks,
        facts,
        assets,
    ) -> SecurityScore:

        deductions: Dict[str, int] = {}

        network_score = self._score_dimension(
            "network",
            findings,
            risks,
            ["Network"],
            self.weights.network_deduction,
            deductions,
        )

        identity_score = self._score_dimension(
            "identity",
            findings,
            risks,
            ["IAM"],
            self.weights.identity_deduction,
            deductions,
        )

        storage_score = self._score_dimension(
            "storage",
            findings,
            risks,
            ["Storage"],
            self.weights.storage_deduction,
            deductions,
        )

        logging_score = self._score_dimension(
            "logging",
            findings,
            risks,
            ["Logging"],
            self.weights.logging_deduction,
            deductions,
        )

        compute_score = self._score_dimension(
            "compute",
            findings,
            risks,
            ["Compute"],
            self.weights.compute_deduction,
            deductions,
        )

        dimension_scores = {

            "network": network_score,

            "identity": identity_score,

            "storage": storage_score,

            "logging": logging_score,

            "compute": compute_score,

        }

        overall = max(
            0,

            min(

                100,

                int(

                    sum(dimension_scores.values()) / len(dimension_scores)

                ),

            ),

        )

        dimensions = SecurityDimensions(

            network=network_score,

            identity=identity_score,

            storage=storage_score,

            logging=logging_score,

            compute=compute_score,

            overall=overall,

        )

        breakdown = ScoreBreakdown(
            base_score=self.weights.base_score,
            deductions=deductions,
        )

        grade = self._grade(overall)

        return SecurityScore(
            overall=overall,
            dimensions=dimensions,
            breakdown=breakdown,
            grade=grade,
        )

    def _score_dimension(
        self,
        name: str,
        findings,
        risks,
        categories: List[str],
        base_deduction: int,
        deductions: Dict[str, int],
    ) -> int:

        category_findings = [

            f for f in findings

            if getattr(f, "category", None) in categories

        ]

        category_risks = [

            r for r in risks

            if getattr(r, "category", None) in categories

        ]

        deduction = base_deduction * len(category_findings)

        deduction += base_deduction * len(category_risks)

        deductions[f"{name}_deduction"] = min(deduction, 100)

        return max(0, 100 - min(deduction, 100))

    def _grade(self, score: int) -> str:

        if score >= 90:

            return "A"

        if score >= 80:

            return "B"

        if score >= 70:

            return "C"

        if score >= 60:

            return "D"

        return "F"
