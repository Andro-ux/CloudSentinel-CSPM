from backend.providers.factory import get_provider
from backend.normalizers.gcp_iam import normalize_service_account

provider = get_provider("gcp")

accounts = provider.collect_identity()

for account in accounts:
    print(normalize_service_account(account))