from backend.models.schemas import NormalizedResource

def normalize_cloudtrail(trail: dict) -> NormalizedResource:
    return NormalizedResource(
        resource_id=trail.get('TrailARN', ''),
        resource_type='CloudTrail',
        service='CloudTrail',
        configuration=trail
    )
