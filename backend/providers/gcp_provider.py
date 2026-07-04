from backend.providers.scan_result import ScanResult
from backend.normalizers.gcp_compute import normalize_instance
from backend.rules.gcp_compute_rules import evaluate_instance
from backend.collectors.gcp_compute_collector import collect_instances

from backend.collectors.gcp_storage_collector import collect_buckets
from backend.normalizers.gcp_storage import normalize_bucket
from backend.rules.gcp_storage import evaluate_bucket


from backend.collectors.gcp_iam_collector import collect_service_accounts

from backend.normalizers.gcp_iam import normalize_service_account

from backend.rules.gcp_iam_rules import evaluate_service_account


class GCPProvider:

    def scan(self):

        result = ScanResult(provider="gcp")

        iam_findings = self.scan_iam()
        storage_findings = self.scan_storage()
        compute_findings = self.scan_compute()
        logging_findings = self.scan_logging()

        result.findings.extend(iam_findings)
        result.findings.extend(storage_findings)
        result.findings.extend(compute_findings)
        result.findings.extend(logging_findings)

        result.assets = {
        "iam": len(collect_service_accounts()),
        "storage": len(collect_buckets()),
        "compute": len(collect_instances()),
        }

        result.calculate_summary()

        return result
    def scan_iam(self):

        findings = []

        accounts = collect_service_accounts()

        for account in accounts:

            normalized = normalize_service_account(account)

            findings.extend(
                evaluate_service_account(normalized)
            )

        return findings

    def scan_storage(self):

        findings = []

        buckets = collect_buckets()

        for bucket in buckets:

            normalized = normalize_bucket(bucket)

            findings.extend(
            evaluate_bucket(normalized)
            )

        return findings

    def scan_compute(self):

        findings = []

        instances = collect_instances()

        for instance in instances:

            normalized = normalize_instance(instance)

            findings.extend(
                evaluate_instance(normalized)
            )

        return findings

    def get_assets(self):

        assets = []

        for account in collect_service_accounts():
            assets.append(normalize_service_account(account))

        for bucket in collect_buckets():
            assets.append(normalize_bucket(bucket))

        for instance in collect_instances():
            assets.append(normalize_instance(instance))
    
        return assets    

    def scan_logging(self):
        return []