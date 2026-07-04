from backend.providers.factory import get_provider

provider = get_provider("gcp")

print(type(provider).__name__)

print()

for account in provider.collect_identity():
    print(account["email"])