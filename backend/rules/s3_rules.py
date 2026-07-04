from backend.models.schemas import NormalizedResource
from backend.rules.finding_factory import create_finding


def evaluate_s3_bucket(resource: NormalizedResource):
    findings = []

    config = resource.configuration

    #
    # Public Access Block
    #
    pab = config.get("PublicAccessBlockConfiguration", {})

    if (
        not pab.get("BlockPublicAcls")
        or not pab.get("BlockPublicPolicy")
        or not pab.get("IgnorePublicAcls")
        or not pab.get("RestrictPublicBuckets")
    ):

        findings.append(
            create_finding(
                rule_id="CS-S3-001",
                severity="HIGH",
                service="S3",
                category="Storage Security",
                resource_id=resource.resource_id,
                title="S3 Bucket Public Access Block Disabled",
                description="Bucket does not have all public access block settings enabled.",
                recommendation="Enable Block Public Access for this bucket.",
                evidence={
                    "PublicAccessBlockConfiguration": pab
                },
                cis_control="2.1.1",
                mitre_attack="T1530",
                references=[
                    "https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html"
                ],
            )
        )

    #
    # Encryption
    #
    enc = config.get("ServerSideEncryptionConfiguration", {})

    if not enc.get("Rules"):

        findings.append(
            create_finding(
                rule_id="CS-S3-002",
                severity="MEDIUM",
                service="S3",
                category="Encryption",
                resource_id=resource.resource_id,
                title="S3 Bucket Encryption Disabled",
                description="Bucket does not have default server-side encryption enabled.",
                recommendation="Enable SSE-S3 or SSE-KMS.",
                evidence={
                    "ServerSideEncryptionConfiguration": enc
                },
                cis_control="2.1.2",
                references=[
                    "https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-bucket-encryption.html"
                ],
            )
        )

    #
    # Public ACL
    #
    grants = config.get("Grants", [])

    for grant in grants:

        grantee = grant.get("Grantee", {})

        if grantee.get("URI") in [
            "http://acs.amazonaws.com/groups/global/AllUsers",
            "http://acs.amazonaws.com/groups/global/AuthenticatedUsers",
        ]:

            findings.append(
                create_finding(
                    rule_id="CS-S3-003",
                    severity="CRITICAL",
                    service="S3",
                    category="Access Control",
                    resource_id=resource.resource_id,
                    title="S3 Bucket has Public ACL",
                    description="Bucket ACL grants access to Everyone.",
                    recommendation="Remove all public ACL grants.",
                    evidence={
                        "Grant": grant
                    },
                    cis_control="2.1.1",
                    mitre_attack="T1530",
                    references=[
                        "https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html"
                    ],
                )
            )

    return findings