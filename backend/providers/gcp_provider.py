from backend.collectors.gcp_subnet_collector import collect_subnets
from backend.normalizers.gcp_subnet import normalize_subnet
from backend.rules.gcp_subnet_rules import evaluate_subnet

from backend.collectors.gcp_vpc_collector import collect_vpcs
from backend.normalizers.gcp_vpc import normalize_vpc
from backend.rules.gcp_vpc_rules import evaluate_vpc

from backend.collectors.gcp_firewall_collector import collect_firewall_rules
from backend.normalizers.gcp_firewall import normalize_firewall
from backend.rules.gcp_firewall_rules import evaluate_firewall

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
        firewall_findings = self.scan_firewall()
        vpc_findings = self.scan_vpc()
        subnet_findings = self.scan_subnets()

        result.findings.extend(iam_findings)
        result.findings.extend(storage_findings)
        result.findings.extend(compute_findings)
        result.findings.extend(logging_findings)
        result.findings.extend(firewall_findings)
        result.findings.extend(vpc_findings)
        result.findings.extend(subnet_findings)

        result.assets = {
        "iam": len(collect_service_accounts()),
        "storage": len(collect_buckets()),
        "compute": len(collect_instances()),
        "firewall": len(collect_firewall_rules()),
        "vpc": len(collect_vpcs()),
        "subnet": len(collect_subnets()),
        }

        result.calculate_summary()

        return result

    def process_resources(
    self,
        resources,
        normalizer,
        evaluator,
    ):

        findings = []

        for resource in resources:

            normalized = normalizer(resource)

            findings.extend(
                evaluator(normalized)
            )

        return findings

    def scan_iam(self):

        return self.process_resources(
        collect_service_accounts(),
        normalize_service_account,
        evaluate_service_account,
    )

    def scan_storage(self):

        return self.process_resources(
        collect_buckets(),
        normalize_bucket,
        evaluate_bucket,
    )

    def scan_compute(self):
        return self.process_resources(
        collect_instances(),
        normalize_instance,
        evaluate_instance,
    )

    def get_assets(self):

        assets = []

        for account in collect_service_accounts():
            assets.append(normalize_service_account(account))

        for bucket in collect_buckets():
            assets.append(normalize_bucket(bucket))

        for instance in collect_instances():
            assets.append(normalize_instance(instance))

        for rule in collect_firewall_rules():
            assets.append(
                normalize_firewall(rule)
            )    

        for network in collect_vpcs():

            assets.append(normalize_vpc(network))

        for subnet in collect_subnets():
            assets.append(normalize_subnet(subnet))    
    
        return assets    

    def scan_firewall(self):

        return self.process_resources(
            collect_firewall_rules(),
            normalize_firewall,
            evaluate_firewall,
        )    

    def scan_vpc(self):
        return self.process_resources(
            collect_vpcs(),
            normalize_vpc,
            evaluate_vpc,
        )

    def scan_subnets(self):

        return self.process_resources(
            collect_subnets(),
            normalize_subnet,
            evaluate_subnet,
        )

    def scan_logging(self):
        return []



   
