from backend.database.models import ScanHistory


def save_scan_history(db, result):

    summary = result.summary

    resources = sum(result.assets.values())

    scan = ScanHistory(

        provider=result.provider,

        findings_count=len(result.findings),

        resources_scanned=resources,

        critical=summary["critical"],

        high=summary["high"],

        medium=summary["medium"],

        low=summary["low"],

        status="SUCCESS",
    )

    db.add(scan)

    db.commit()