from backend.collectors.gcp_compute_collector import collect_instances
from backend.normalizers.gcp_compute import normalize_instance

for vm in collect_instances():
    print(normalize_instance(vm))