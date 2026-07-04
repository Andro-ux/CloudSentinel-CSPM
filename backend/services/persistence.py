from backend.database.models import Finding


def save_findings(db, findings):

    for finding in findings:

        existing = db.query(Finding).filter(
            Finding.id == finding["id"]
        ).first()

        if existing:
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
            )
        )

    db.commit()