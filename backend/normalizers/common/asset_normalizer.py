from backend.models.asset import Asset


def create_asset(
    *,
    account_id=None,
    service,
    resource_type,
    resource_id,
    name,
    arn=None,
    region=None,
    tags=None,
    configuration=None,
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