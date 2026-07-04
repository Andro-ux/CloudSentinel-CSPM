from backend.collectors.gcp_storage_collector import collect_buckets
from backend.normalizers.gcp_storage import normalize_bucket

for bucket in collect_buckets():
    print(normalize_bucket(bucket))