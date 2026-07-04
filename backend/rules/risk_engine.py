SEVERITY_BASE = {
    "CRITICAL": 60,
    "HIGH": 40,
    "MEDIUM": 25,
    "LOW": 10,
    "INFO": 0,
}


def calculate_risk_score(
    *,
    severity,
    internet_exposed=False,
    privileged=False,
    encryption_disabled=False,
    compliance_failed=False,
):
    score = SEVERITY_BASE.get(severity.upper(), 0)

    if internet_exposed:
        score += 20

    if privileged:
        score += 15

    if encryption_disabled:
        score += 10

    if compliance_failed:
        score += 5

    return min(score, 100)