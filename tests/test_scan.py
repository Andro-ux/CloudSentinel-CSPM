from backend.providers.factory import get_provider

provider = get_provider("gcp")

findings = provider.scan()

print()

print(findings)