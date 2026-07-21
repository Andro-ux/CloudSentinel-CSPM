from typing import List

from backend.facts.extractors.base import BaseExtractor
from backend.facts.models import Evidence, Fact, FactType
from backend.knowledge.interfaces import IKnowledgeEngine


class StorageFactsExtractor(BaseExtractor):

    @property
    def fact_types(self) -> List[FactType]:

        return [

            FactType.PUBLIC_BUCKET,

            FactType.UNENCRYPTED_BUCKET,

            FactType.VERSIONING_DISABLED,

        ]

    def extract(self, knowledge: IKnowledgeEngine) -> List[Fact]:

        facts: List[Fact] = []

        for bucket in knowledge.find_assets(resource_type="Bucket"):

            public_access = bucket.properties.get(
                "public_access_prevention", ""
            ).lower()

            is_public = public_access in ("inherited", "disabled")

            if is_public:

                facts.append(

                    Fact(

                        id=self._fact_id(
                            bucket.properties.get("cloud", "unknown"),
                            FactType.PUBLIC_BUCKET,
                            bucket.id,
                        ),

                        asset_id=bucket.id,

                        fact_type=FactType.PUBLIC_BUCKET,

                        severity="HIGH",

                        provider=bucket.properties.get("cloud", "unknown"),

                        category="Storage",

                        evidence=self._make_evidence(
                            provider=bucket.properties.get("cloud", "unknown"),
                            source="asset.properties",
                            attribute="public_access_prevention",
                            value=public_access,
                        ),

                        description=(
                            f"Bucket '{bucket.name}' allows public access "
                            f"(public_access_prevention={public_access})."
                        ),

                    )

                )

            encrypted = bucket.properties.get("encryption") is not None

            if not encrypted:

                facts.append(

                    Fact(

                        id=self._fact_id(
                            bucket.properties.get("cloud", "unknown"),
                            FactType.UNENCRYPTED_BUCKET,
                            bucket.id,
                        ),

                        asset_id=bucket.id,

                        fact_type=FactType.UNENCRYPTED_BUCKET,

                        severity="MEDIUM",

                        provider=bucket.properties.get("cloud", "unknown"),

                        category="Storage",

                        evidence=self._make_evidence(
                            provider=bucket.properties.get("cloud", "unknown"),
                            source="asset.properties",
                            attribute="encryption",
                            value=False,
                        ),

                        description=(
                            f"Bucket '{bucket.name}' does not have default "
                            f"encryption enabled."
                        ),

                    )

                )

            versioning = bucket.properties.get("versioning", False)

            if not versioning:

                facts.append(

                    Fact(

                        id=self._fact_id(
                            bucket.properties.get("cloud", "unknown"),
                            FactType.VERSIONING_DISABLED,
                            bucket.id,
                        ),

                        asset_id=bucket.id,

                        fact_type=FactType.VERSIONING_DISABLED,

                        severity="MEDIUM",

                        provider=bucket.properties.get("cloud", "unknown"),

                        category="Storage",

                        evidence=self._make_evidence(
                            provider=bucket.properties.get("cloud", "unknown"),
                            source="asset.properties",
                            attribute="versioning",
                            value=False,
                        ),

                        description=(
                            f"Bucket '{bucket.name}' does not have object "
                            f"versioning enabled."
                        ),

                    )

                )

        return facts
