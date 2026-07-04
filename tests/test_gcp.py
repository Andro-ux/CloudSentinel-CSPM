from backend.collectors.gcp_iam_collector import collect_service_accounts

accounts = collect_service_accounts()

print()

print("Service Accounts Found:")

for acc in accounts:
    print(acc["email"])