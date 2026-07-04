from backend.database.models import Asset


def save_assets(db, assets):

    for asset in assets:

        existing = db.query(Asset).filter(
            Asset.resource_id == asset["resource_id"]
        ).first()

        if existing:
            continue

        db.add(
            Asset(
                service=asset["service"],
                resource_type=asset["resource_type"],
                resource_id=asset["resource_id"],
                name=asset["name"],
                risk_score=0,
                configuration=asset,
            )
        )

    db.commit()