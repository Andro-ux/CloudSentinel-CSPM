from collections import defaultdict

from backend.models.schemas import (
    ResourceRiskAssessment,
    AccountRiskAssessment,
)


def analyze_resource_risk(findings):
    grouped = defaultdict(list)

    for finding in findings:
        grouped[finding["resource_id"]].append(finding)

    assessments = []

    for resource_id, resource_findings in grouped.items():
        severity_breakdown = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "INFO": 0,
        }

        total_risk = 0

        for finding in resource_findings:
            severity = finding["severity"].upper()
            severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
            total_risk += finding.get("risk_score", 0)

        overall_risk = min(100, total_risk)

        assessments.append(
            ResourceRiskAssessment(
                resource_id=resource_id,
                service=resource_findings[0]["service"],
                overall_risk=overall_risk,
                severity_breakdown=severity_breakdown,
                finding_count=len(resource_findings),
                critical_findings=severity_breakdown["CRITICAL"],
                high_findings=severity_breakdown["HIGH"],
                medium_findings=severity_breakdown["MEDIUM"],
                low_findings=severity_breakdown["LOW"],
                top_findings=[f["title"] for f in sorted(resource_findings, key=lambda x: x.get("risk_score", 0), reverse=True)[:5]],
            )
        )

    assessments.sort(key=lambda r: r.overall_risk, reverse=True)
    return assessments


def analyze_account_risk(account_id, findings):
    resources = analyze_resource_risk(findings)

    overall_risk = 0
    if resources:
        overall_risk = min(
            100,
            round(sum(r.overall_risk for r in resources) / len(resources))
        )

    critical = sum(r.critical_findings for r in resources)
    high = sum(r.high_findings for r in resources)

    return AccountRiskAssessment(
        account_id=account_id,
        overall_risk=overall_risk,
        resource_count=len(resources),
        findings_count=len(findings),
        critical_findings=critical,
        high_findings=high,
        compliance_score=0.0,
        highest_risk_resources=resources[:10],
    )
