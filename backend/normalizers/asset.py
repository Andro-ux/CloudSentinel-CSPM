from backend.models.asset import Asset


def normalize_asset(
    *,
    account_id: int,
    service: str,
    resource_type: str,
    resource_id: str,
    name: str = "",
    arn: str = "",
    region: str = "",
    tags: dict | None = None,
    configuration: dict | None = None,
):
    return Asset(
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