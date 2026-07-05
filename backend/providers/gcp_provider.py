from backend.collectors.gcp_cloud_armor_collector import (
    collect_cloud_armor_policies,
)

from backend.normalizers.gcp_cloud_armor import (
    normalize_cloud_armor,
)

from backend.rules.gcp_cloud_armor_rules import (
    evaluate_cloud_armor,
)
from backend.collectors.gcp_lb_collector import collect_load_balancers
from backend.normalizers.gcp_lb import normalize_load_balancer
from backend.rules.gcp_lb_rules import evaluate_load_balancer
from backend.collectors.gcp_nat_collector import collect_nat_gateways
from backend.normalizers.gcp_nat import normalize_nat
from backend.rules.gcp_nat_rules import evaluate_nat
from backend.collectors.gcp_route_collector import collect_routes
from backend.normalizers.gcp_route import normalize_route
from backend.rules.gcp_route_rules import evaluate_route

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
        route_findings = self.scan_routes()
        nat_findings = self.scan_nat()
        lb_findings = self.scan_load_balancers()
        armor_findings = self.scan_cloud_armor()

        result.findings.extend(iam_findings)
        result.findings.extend(storage_findings)
        result.findings.extend(compute_findings)
        result.findings.extend(logging_findings)
        result.findings.extend(firewall_findings)
        result.findings.extend(vpc_findings)
        result.findings.extend(subnet_findings)
        result.findings.extend(route_findings)
        result.findings.extend(nat_findings)
        result.findings.extend(lb_findings)
        result.findings.extend(armor_findings)

        result.assets = {
        "iam": len(collect_service_accounts()),
        "storage": len(collect_buckets()),
        "compute": len(collect_instances()),
        "firewall": len(collect_firewall_rules()),
        "vpc": len(collect_vpcs()),
        "subnet": len(collect_subnets()),
        "route": len(collect_routes()),
        "nat": len(collect_nat_gateways()),
        "load_balancer": len(collect_load_balancers()),
        "cloud_armor": len(collect_cloud_armor_policies()),
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

        for route in collect_routes():
            assets.append(normalize_route(route))
        for nat in collect_nat_gateways():

            assets.append(
                normalize_nat(nat)
            )         
        for lb in collect_load_balancers():

            assets.append(
                normalize_load_balancer(lb)
            )    

        for policy in collect_cloud_armor_policies():

            assets.append(
                normalize_cloud_armor(policy)
            )    
    
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

    def scan_routes(self):

        return self.process_resources(
            collect_routes(),
            normalize_route,
            evaluate_route,
        )    

    def scan_nat(self):

        return self.process_resources(
            collect_nat_gateways(),
            normalize_nat,
            evaluate_nat,
        )    

    def scan_load_balancers(self):

        return self.process_resources(
            collect_load_balancers(),
            normalize_load_balancer,
            evaluate_load_balancer,
        )
    def scan_cloud_armor(self):

        return self.process_resources(
            collect_cloud_armor_policies(),
            normalize_cloud_armor,
            evaluate_cloud_armor,
        )        

    def scan_logging(self):
        return []



   
