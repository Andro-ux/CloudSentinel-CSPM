from typing import List

from backend.facts.models import Fact, FactSet, FactType
from backend.rules.base import BaseRule
from backend.rules.models import Finding, RuleMetadata, Severity


class PublicBucketRule(BaseRule):

    def __init__(self):

        super().__init__(
            RuleMetadata(
                rule_id="CS-RULE-002",
                name="Public Unencrypted Bucket",
                description="Detects storage buckets that are both publicly accessible and lack encryption.",
                version="1.0.0",
                author="CloudSentinel Core",
            )
        )

    def evaluate(self, fact_set: FactSet) -> List[Finding]:

        findings: List[Finding] = []

        public_bucket_facts = fact_set.find_by_type(FactType.PUBLIC_BUCKET)

        unencrypted_bucket_facts = fact_set.find_by_type(FactType.UNENCRYPTED_BUCKET)

        unencrypted_ids = {f.asset_id for f in unencrypted_bucket_facts}

        for fact in public_bucket_facts:

            asset_id = fact.asset_id

            if asset_id not in unencrypted_ids:

                continue

            unencrypted_fact = next(

                (f for f in unencrypted_bucket_facts if f.asset_id == asset_id),

                None,

            )

            findings.append(

                self._make_finding(
                    rule_id=self.metadata.rule_id,
                    title="Public Unencrypted Bucket",
                    description=(
                        f"Bucket '{asset_id}' is publicly accessible and does not "
                        f"have default encryption enabled."
                    ),
                    severity=Severity.CRITICAL,
                    category="Storage",
                    asset_ids=[asset_id],
                    facts=[fact] + ([unencrypted_fact] if unencrypted_fact else []),
                    recommendation=(
                        "Enable Public Access Prevention and configure default "
                        "encryption for this bucket."
                    ),
                    references=[
                        "https://cloud.google.com/storage/docs/public-access-prevention",
                        "https://cloud.google.com/storage/docs/encryption",
                    ],
                    evidence={
                        "public_bucket": True,
                        "unencrypted": True,
                        "bucket": asset_id,
                    },
                    service="Storage",
                    resource_id=asset_id,
                )

            )

        return findings
