from backend.database.models import ScanHistory


def get_dashboard_history(db, limit=20):

    scans = (
        db.query(ScanHistory)
        .order_by(ScanHistory.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": scan.id,
            "provider": scan.provider,
            "timestamp": scan.timestamp.isoformat(),
            "findings": scan.findings_count,
            "resources": scan.resources_scanned,
            "critical": scan.critical,
            "high": scan.high,
            "medium": scan.medium,
            "low": scan.low,
            "status": scan.status,
        }
        for scan in scans
    ]