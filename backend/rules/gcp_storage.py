from backend.rules.finding_factory import create_finding


def evaluate_bucket(bucket):

    findings = []

    if not bucket["versioning"]:

        findings.append(
            create_finding(
                rule_id="GCP-STORAGE-001",

                severity="MEDIUM",

                service="Storage",

                category="Data Protection",

                title="Bucket Versioning Disabled",

                description=(
                    f"Bucket '{bucket['name']}' does not have object versioning enabled."
                ),

                recommendation=(
                    "Enable object versioning to protect against accidental deletion and ransomware."
                ),

                resource_id=bucket["resource_id"],

                evidence={
                    "bucket": bucket["name"],
                    "versioning": bucket["versioning"],
                },

                cis_control="CIS GCP 5.1",

                mitre_attack="T1485",

                references=[
                    "https://cloud.google.com/storage/docs/object-versioning"
                ],
            )
        )

    if bucket["public_access_prevention"] != "enforced":

        findings.append(
            create_finding(
                rule_id="GCP-STORAGE-002",

                severity="HIGH",

                service="Storage",

                category="Public Exposure",

                title="Public Access Prevention Disabled",

                description=(
                    f"Bucket '{bucket['name']}' allows public access."
                ),

                recommendation=(
                    "Enable Public Access Prevention to prevent unintended public exposure."
                ),

                resource_id=bucket["resource_id"],

                evidence={
                    "bucket": bucket["name"],
                    "public_access_prevention": bucket["public_access_prevention"],
                },

                cis_control="CIS GCP 5.2",

                mitre_attack="T1530",

                references=[
                    "https://cloud.google.com/storage/docs/public-access-prevention"
                ],
            )
        )

    if not bucket["uniform_bucket_level_access"]:

        findings.append(
            create_finding(
                rule_id="GCP-STORAGE-003",

                severity="MEDIUM",

                service="Storage",

                category="Access Control",

                title="Uniform Bucket-Level Access Disabled",

                description=(
                    f"Bucket '{bucket['name']}' is using legacy ACLs."
                ),

                recommendation=(
                    "Enable Uniform Bucket-Level Access to simplify and strengthen access control."
                ),

                resource_id=bucket["resource_id"],

                evidence={
                    "bucket": bucket["name"],
                    "uniform_bucket_level_access": bucket["uniform_bucket_level_access"],
                },

                cis_control="CIS GCP 5.3",

                mitre_attack="T1222",

                references=[
                    "https://cloud.google.com/storage/docs/uniform-bucket-level-access"
                ],
            )
        )

    return findings