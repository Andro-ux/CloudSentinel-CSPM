from backend.database.models import Finding


def get_dashboard_findings(
    db,
    severity=None,
    service=None,
    limit=25,
    offset=0,
):

    query = db.query(Finding)

    if severity:
        query = query.filter(
            Finding.severity == severity.upper()
        )

    if service:
        query = query.filter(
            Finding.service == service
        )

    findings = (
        query
        .order_by(Finding.risk_score.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": f.id,
            "title": f.title,
            "severity": f.severity,
            "risk_score": f.risk_score,
            "service": f.service,
            "resource_id": f.resource_id,
            "recommendation": f.recommendation,
        }
        for f in findings
    ]