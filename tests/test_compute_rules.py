from backend.collectors.gcp_compute_collector import collect_instances
from backend.normalizers.gcp_compute import normalize_instance
from backend.rules.gcp_compute_rules import evaluate_instance

for vm in collect_instances():

    normalized = normalize_instance(vm)

    findings = evaluate_instance(normalized)

    print(findings)