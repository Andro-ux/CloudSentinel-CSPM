from backend.collectors.gcp_storage_collector import collect_buckets

buckets = collect_buckets()

print()

print("Buckets Found:")

for bucket in buckets:
    print(bucket)