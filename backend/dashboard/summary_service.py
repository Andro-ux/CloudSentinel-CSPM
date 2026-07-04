from sqlalchemy import func

from backend.database.models import (
    Asset,
    Finding,
    ScanHistory,
)


def get_dashboard_summary(db):

    latest_scan = (
        db.query(ScanHistory)
        .order_by(ScanHistory.timestamp.desc())
        .first()
    )

    total_assets = db.query(Asset).count()

    total_findings = db.query(Finding).count()

    assets = {}

    for service, count in (
        db.query(
            Asset.service,
            func.count(Asset.id),
        )
        .group_by(Asset.service)
        .all()
    ):
        assets[service.lower()] = count

    findings = {
        "critical": db.query(Finding).filter(
            Finding.severity == "CRITICAL"
        ).count(),

        "high": db.query(Finding).filter(
            Finding.severity == "HIGH"
        ).count(),

        "medium": db.query(Finding).filter(
            Finding.severity == "MEDIUM"
        ).count(),

        "low": db.query(Finding).filter(
            Finding.severity == "LOW"
        ).count(),
    }

    overall_risk = 0

    scores = [
        r[0]
        for r in db.query(Finding.risk_score).all()
        if r[0] is not None
    ]

    if scores:
        overall_risk = round(sum(scores) / len(scores))

    return {
        "provider": latest_scan.provider if latest_scan else None,

        "last_scan": (
            latest_scan.timestamp.isoformat()
            if latest_scan
            else None
        ),

        "total_scans": db.query(ScanHistory).count(),

        "overall_risk_score": overall_risk,

        "total_assets": total_assets,

        "total_findings": total_findings,

        "assets": assets,

        "findings": findings,
    }