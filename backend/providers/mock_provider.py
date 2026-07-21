from backend.providers.base import CloudProvider
from backend.mock_data.loader import load
from backend.normalizers.gcp_storage import normalize_bucket
from backend.rules.gcp_storage import evaluate_bucket
from backend.normalizers.gcp_iam import normalize_service_account
from backend.rules.gcp_iam_rules import evaluate_service_account
from backend.normalizers.gcp_vpc import normalize_vpc
from backend.normalizers.gcp_subnet import normalize_subnet
from backend.rules.gcp_subnet_rules import evaluate_subnet


from backend.models.scan_bundle import ScanBundle

from backend.normalizers.gcp_compute import normalize_instance

from backend.rules.gcp_compute_rules import evaluate_instance

from backend.providers.scan_result import ScanResult



class MockProvider(CloudProvider):

    def scan(self):

        print("=" * 50)
        print("MOCK PROVIDER IS RUNNING")
        print("=" * 50)

        result = ScanResult(provider="mock")

        bundle = ScanBundle()

        for resource in load("compute"):

            asset = normalize_instance(resource)

            bundle.assets.append(asset)

            bundle.findings.extend(
                evaluate_instance(asset)
            )

        for resource in load("storage"):

            asset = normalize_bucket(resource)

            bundle.assets.append(asset)

            bundle.findings.extend(
                evaluate_bucket(asset)
            )

        for resource in load("iam"):

            asset = normalize_service_account(resource)

            bundle.assets.append(asset)

            bundle.findings.extend(
                evaluate_service_account(asset)
            )

        for resource in load("vpc"):

            asset = normalize_vpc(resource)

            bundle.assets.append(asset)  

        for resource in load("subnets"):

            asset = normalize_subnet(resource)

            bundle.assets.append(asset)      

            bundle.findings.extend(
                evaluate_subnet(asset)
            )

        result.findings = bundle.findings

        result.assets = {
            "compute": len(load("compute")),
            "storage": len(load("storage")),
            "iam": len(load("iam")),
            "vpc": len(load("vpc")),
            "subnet": len(load("subnets")),
        }

        result.calculate_summary()

        result.calculate_executive_summary()

        return result

    def get_assets(self):

        

        assets = []

        for resource in load("compute"):
            assets.append(normalize_instance(resource))

        for resource in load("storage"):
            assets.append(normalize_bucket(resource))

        for resource in load("iam"):

            assets.append(
                normalize_service_account(resource))

        for resource in load("vpc"):

            assets.append(
                normalize_vpc(resource)
            )        

        for resource in load("subnets"):
            assets.append(normalize_subnet(resource))    

        return assets
   