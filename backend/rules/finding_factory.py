from typing import Any, Dict, List

from backend.rules.risk_engine import calculate_risk_score


def create_finding(
    *,
    rule_id: str,
    severity: str,
    service: str,
    category: str,
    title: str,
    description: str,
    recommendation: str,
    resource_id: str,
    evidence: Dict[str, Any],
    cis_control: str | None = None,
    mitre_attack: str | None = None,
    references: List[str] | None = None,
):
    risk_score = calculate_risk_score(
        severity=severity,

        internet_exposed=(
            "public" in title.lower()
            or "internet" in title.lower()
        ),

        privileged=(
            "administrator" in title.lower()
        ),

        encryption_disabled=(
            "encryption" in title.lower()
        ),

        compliance_failed=(
            cis_control is not None
        ),
    )

    return {
        "id": f"{resource_id}-{rule_id}",
        "rule_id": rule_id,
        "severity": severity,
        "risk_score": risk_score,
        "service": service,
        "category": category,
        "resource_id": resource_id,
        "title": title,
        "description": description,
        "recommendation": recommendation,
        "evidence": evidence,
        "cis_control": cis_control,
        "mitre_attack": mitre_attack,
        "references": references or [],
    }