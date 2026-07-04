from datetime import datetime

from sqlalchemy.orm import Session

from backend.database.models import Asset


def upsert_asset(
    db: Session,
    asset: Asset,
):
    existing = (
        db.query(Asset)
        .filter(
            Asset.account_id == asset.account_id,
            Asset.resource_id == asset.resource_id,
        )
        .first()
    )

    if existing:

        existing.service = asset.service
        existing.resource_type = asset.resource_type
        existing.name = asset.name
        existing.arn = asset.arn
        existing.region = asset.region
        existing.tags = asset.tags
        existing.configuration = asset.configuration

        existing.last_seen = datetime.utcnow()

        return existing

    asset.first_seen = datetime.utcnow()
    asset.last_seen = datetime.utcnow()

    db.add(asset)

    return asset


def mark_missing_assets(
    db: Session,
    account_id: int,
    active_resource_ids: set[str],
):
    assets = (
        db.query(Asset)
        .filter(Asset.account_id == account_id)
        .all()
    )

    for asset in assets:

        if asset.resource_id not in active_resource_ids:

            asset.status = "STALE"

    return len(assets)