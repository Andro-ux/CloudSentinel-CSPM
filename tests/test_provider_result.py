from backend.providers.factory import get_provider

provider = get_provider("gcp")

result = provider.scan()

print()

print("Provider:", result.provider)

print("Assets:", result.assets)

print("Summary:", result.summary)

print()

print("Findings:")

for finding in result.findings:
    print("-", finding["title"])