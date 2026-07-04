from backend.models.schemas import NormalizedResource

def normalize_s3_bucket(bucket: dict) -> NormalizedResource:
    return NormalizedResource(
        resource_id=f"arn:aws:s3:::{bucket.get('Name')}",
        resource_type='S3Bucket',
        service='S3',
        configuration=bucket
    )
