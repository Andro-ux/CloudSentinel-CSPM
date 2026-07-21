from backend.reporting.statistics import Statistics
from backend.reporting.finding_prioritizer import FindingPrioritizer
from backend.scoring.engine import RiskDomainEngine


class ExecutiveSummary:

    def generate(self, result):

        stats = Statistics().generate(result)

        prioritized = FindingPrioritizer().prioritize(
            result.findings.copy()
        )

        top_risks = prioritized[:5]

        risk = RiskDomainEngine().calculate(
            result.findings
        )

        severity = stats["severity"]

        return {

            "security_score": risk["overall"],

            "risk_level":
                "Critical" if risk["overall"] < 40 else
                "High" if risk["overall"] < 60 else
                "Medium" if risk["overall"] < 80 else
                "Low",

            "domain_scores": risk["domains"],

            "total_assets": stats["asset_count"],

            "total_findings": stats["finding_count"],

            "critical_findings":
                severity.get("critical", 0),

            "high_findings":
                severity.get("high", 0),

            "top_risks": top_risks,

            "statistics": stats

        }