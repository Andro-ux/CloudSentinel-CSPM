from backend.database.models import Asset, Finding


def update_asset_risk_scores(db):

    assets = db.query(Asset).all()

    for asset in assets:

        findings = (
            db.query(Finding)
            .filter(Finding.resource_id == asset.resource_id)
            .all()
        )

        if findings:
            asset.risk_score = max(
                finding.risk_score or 0
                for finding in findings
            )
        else:
            asset.risk_score = 0

    db.commit()