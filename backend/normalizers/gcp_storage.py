def normalize_bucket(bucket):

    return {
        "cloud": "gcp",
        "service": "Storage",
        "resource_type": "Bucket",
        "resource_id": bucket["id"],
        "name": bucket["name"],
        "location": bucket["location"],
        "storage_class": bucket["storage_class"],
        "public_access_prevention": bucket["public_access_prevention"],
        "uniform_bucket_level_access": bucket["uniform_bucket_level_access"],
        "versioning": bucket["versioning"],
        "labels": bucket["labels"],
        "raw": bucket
    }