from backend.providers.gcp_provider import GCPProvider


def get_provider(provider: str):
    provider = provider.lower()

    if provider == "gcp":
        return GCPProvider()

    raise ValueError(f"Unsupported provider: {provider}")