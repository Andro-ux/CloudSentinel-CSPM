from backend.database.models import Asset


def get_dashboard_assets(
    db,
    service=None,
    resource_type=None,
    limit=25,
    offset=0,
):

    query = db.query(Asset)

    if service:
        query = query.filter(
            Asset.service == service
        )

    if resource_type:
        query = query.filter(
            Asset.resource_type == resource_type
        )

    assets = (
        query
        .order_by(Asset.service)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "service": a.service,
            "resource_type": a.resource_type,
            "name": a.name,
            "resource_id": a.resource_id,
            "risk_score": a.risk_score,
        }
        for a in assets
    ]