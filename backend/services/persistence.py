from datetime import datetime

from backend.database.models import Finding

from backend.services.finding_lifecycle_service import reactivate_finding


def save_findings(db, findings):

    for finding in findings:

        existing = (
            db.query(Finding)
            .filter(Finding.id == finding["id"])
            .first()
        )

        if existing:

            reactivate_finding(existing)

            existing.severity = finding["severity"]

            existing.service = finding["service"]

            existing.resource_id = finding["resource_id"]

            existing.title = finding["title"]

            existing.description = finding["description"]

            existing.recommendation = finding["recommendation"]

            existing.risk_score = finding.get("risk_score", 0)

            continue
            
        db.add(
            Finding(
                id=finding["id"],

                severity=finding["severity"],

                service=finding["service"],

                resource_id=finding["resource_id"],

                title=finding["title"],

                description=finding["description"],

                recommendation=finding["recommendation"],

                risk_score=finding.get("risk_score", 0),

                first_seen=datetime.utcnow(),

                last_seen=datetime.utcnow(),

                status="ACTIVE",
            )
        )

    db.commit()