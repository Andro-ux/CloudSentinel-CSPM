from datetime import datetime

from backend.database.models import Finding


def mark_existing_findings_pending(db):

    findings = (
        db.query(Finding)
        .filter(Finding.status == "ACTIVE")
        .all()
    )

    for finding in findings:
        finding.status = "PENDING"

    db.commit()


def reactivate_finding(existing):

    existing.status = "ACTIVE"

    existing.last_seen = datetime.utcnow()

    existing.resolved_at = None


def resolve_missing_findings(db):

    findings = (
        db.query(Finding)
        .filter(Finding.status == "PENDING")
        .all()
    )

    for finding in findings:

        finding.status = "RESOLVED"

        finding.resolved_at = datetime.utcnow()

    db.commit()