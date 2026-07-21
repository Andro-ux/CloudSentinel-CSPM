from typing import List

from backend.facts.extractors.base import BaseExtractor
from backend.facts.models import Evidence, Fact, FactType
from backend.knowledge.interfaces import IKnowledgeEngine


class IAMFactsExtractor(BaseExtractor):

    @property
    def fact_types(self) -> List[FactType]:

        return [

            FactType.ADMIN_SERVICE_ACCOUNT,

            FactType.UNUSED_SERVICE_ACCOUNT,

            FactType.OVER_PRIVILEGED_IDENTITY,

        ]

    def extract(self, knowledge: IKnowledgeEngine) -> List[Fact]:

        facts: List[Fact] = []

        service_accounts = knowledge.find_assets(resource_type="ServiceAccount")

        sa_ids = {sa.id for sa in service_accounts}

        used_sa_ids = set()

        for vm in knowledge.find_assets(resource_type="VM"):

            relationships = vm.properties.get("relationships", {})

            for sa_email in relationships.get("service_accounts", []):

                for sa in service_accounts:

                    if sa.name == sa_email or sa.properties.get("email") == sa_email:

                        used_sa_ids.add(sa.id)

        for sa in service_accounts:

            is_default = sa.properties.get("disabled") is False and "compute@developer" in sa.name

            is_admin = any(

                keyword in sa.name.lower()

                for keyword in ["admin", "owner", "editor", "privileged"]

            )

            if is_default or is_admin:

                facts.append(

                    Fact(

                        id=self._fact_id(
                            sa.properties.get("cloud", "unknown"),
                            FactType.ADMIN_SERVICE_ACCOUNT,
                            sa.id,
                        ),

                        asset_id=sa.id,

                        fact_type=FactType.ADMIN_SERVICE_ACCOUNT,

                        severity="MEDIUM",

                        provider=sa.properties.get("cloud", "unknown"),

                        category="IAM",

                        evidence=self._make_evidence(
                            provider=sa.properties.get("cloud", "unknown"),
                            source="asset.properties",
                            attribute="name",
                            value=sa.name,
                        ),

                        description=(
                            f"Service account '{sa.name}' appears to have "
                            f"administrative or overly broad permissions."
                        ),

                    )

                )

            if sa.id not in used_sa_ids:

                facts.append(

                    Fact(

                        id=self._fact_id(
                            sa.properties.get("cloud", "unknown"),
                            FactType.UNUSED_SERVICE_ACCOUNT,
                            sa.id,
                        ),

                        asset_id=sa.id,

                        fact_type=FactType.UNUSED_SERVICE_ACCOUNT,

                        severity="LOW",

                        provider=sa.properties.get("cloud", "unknown"),

                        category="IAM",

                        evidence=self._make_evidence(
                            provider=sa.properties.get("cloud", "unknown"),
                            source="asset.relationships",
                            attribute="used_by",
                            value=False,
                        ),

                        description=(
                            f"Service account '{sa.name}' is not attached to "
                            f"any compute resource."
                        ),

                    )

                )

            if is_default:

                facts.append(

                    Fact(

                        id=self._fact_id(
                            sa.properties.get("cloud", "unknown"),
                            FactType.OVER_PRIVILEGED_IDENTITY,
                            sa.id,
                        ),

                        asset_id=sa.id,

                        fact_type=FactType.OVER_PRIVILEGED_IDENTITY,

                        severity="MEDIUM",

                        provider=sa.properties.get("cloud", "unknown"),

                        category="IAM",

                        evidence=self._make_evidence(
                            provider=sa.properties.get("cloud", "unknown"),
                            source="asset.properties",
                            attribute="name",
                            value=sa.name,
                        ),

                        description=(
                            f"Service account '{sa.name}' is the default Compute "
                            f"Engine service account and may have excessive permissions."
                        ),

                    )

                )

        return facts
