from typing import List

from backend.plugins.interfaces import IProviderPlugin
from backend.plugins.models import ProviderMetadata


class AWSPlugin(IProviderPlugin):

    def get_metadata(self) -> ProviderMetadata:

        return ProviderMetadata(
            provider_id="aws",
            name="Amazon Web Services",
            version="1.0.0",
            description="AWS security scanning plugin",
            author="CloudSentinel Core",
            supported_services=[
                "ec2",
                "s3",
                "iam",
                "vpc",
                "subnet",
                "security_group",
                "lambda",
                "rds",
                "eks",
            ],
            supported_collectors=[],
            supported_normalizers=[],
            authentication_methods=["access_key", "iam_role", "sso"],
            capabilities=["scanning", "knowledge_engine", "fact_engine"],
        )

    def scan(self):

        raise NotImplementedError("AWS plugin not yet implemented")

    def get_assets(self) -> List:

        raise NotImplementedError("AWS plugin not yet implemented")

    def validate(self) -> bool:

        return True

    def get_capabilities(self) -> List[str]:

        return ["scanning", "knowledge_engine", "fact_engine"]

    def get_supported_services(self) -> List[str]:

        return self.get_metadata().supported_services
