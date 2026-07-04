from sqlalchemy.orm import Session

from backend.inventory.service import upsert_asset
from backend.normalizers.asset import normalize_asset


def sync_asset(
    db: Session,
    *,
    account_id: int,
    service: str,
    resource_type: str,
    resource_id: str,
    name: str = "",
    arn: str = "",
    region: str = "",
    tags=None,
    configuration=None,
):
    asset = normalize_asset(
        account_id=account_id,
        service=service,
        resource_type=resource_type,
        resource_id=resource_id,
        name=name,
        arn=arn,
        region=region,
        tags=tags or {},
        configuration=configuration or {},
    )

    return upsert_asset(db, asset)