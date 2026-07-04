import logging

from backend.utils.gcp import get_storage_client

logger = logging.getLogger("cloudsentinel.gcp.storage")


def collect_buckets():
    client = get_storage_client()

    buckets = []

    for bucket in client.list_buckets():

        buckets.append({
            "id": bucket.id,
            "name": bucket.name,
            "location": bucket.location,
            "storage_class": bucket.storage_class,
            "public_access_prevention": bucket.iam_configuration.public_access_prevention,
            "uniform_bucket_level_access": bucket.iam_configuration.uniform_bucket_level_access_enabled,
            "versioning": bucket.versioning_enabled,
            "labels": bucket.labels,
        })

    return buckets