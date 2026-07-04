from backend.collectors.gcp_compute_collector import collect_instances

for vm in collect_instances():
    print(vm)