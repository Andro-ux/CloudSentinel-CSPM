from backend.providers.factory import get_provider

provider = get_provider("gcp")

findings = provider.scan()

print()

print("Total Findings:", len(findings))

print()

for finding in findings:
    print(f"[{finding['severity']}] {finding['service']} -> {finding['title']}")