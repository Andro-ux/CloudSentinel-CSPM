from backend.providers.factory import get_provider
from backend.normalizers.gcp_iam import normalize_service_account
from backend.rules.gcp_iam_rules import evaluate_service_account

provider = get_provider("gcp")

accounts = provider.collect_identity()

for account in accounts:

    normalized = normalize_service_account(account)

    findings = evaluate_service_account(normalized)

    if findings:
        print(findings)