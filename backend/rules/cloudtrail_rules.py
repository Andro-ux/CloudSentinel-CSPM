from backend.models.schemas import NormalizedResource
from backend.rules.finding_factory import create_finding


def evaluate_cloudtrail(resource: NormalizedResource):
    findings = []

    config = resource.configuration
    status = config.get("Status", {})

    #
    # Logging Disabled
    #
    if not status.get("IsLogging"):

        findings.append(
            create_finding(
                rule_id="CS-CT-001",
                severity="HIGH",
                service="CloudTrail",
                category="Logging & Monitoring",
                resource_id=resource.resource_id,
                title="CloudTrail Logging Disabled",
                description="CloudTrail is not actively recording AWS API activity.",
                recommendation="Enable CloudTrail logging to ensure API activity is audited.",
                evidence={
                    "Status": status
                },
                cis_control="3.1",
                mitre_attack="T1562.008",
                references=[
                    "https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html"
                ],
            )
        )

    #
    # Multi-Region Disabled
    #
    if not config.get("IsMultiRegionTrail"):

        findings.append(
            create_finding(
                rule_id="CS-CT-002",
                severity="MEDIUM",
                service="CloudTrail",
                category="Logging & Monitoring",
                resource_id=resource.resource_id,
                title="CloudTrail is not Multi-Region",
                description="The trail records events from only a single AWS Region.",
                recommendation="Enable a multi-region trail to improve visibility across the AWS account.",
                evidence={
                    "IsMultiRegionTrail": config.get("IsMultiRegionTrail")
                },
                cis_control="3.1",
                references=[
                    "https://docs.aws.amazon.com/awscloudtrail/latest/userguide/receive-cloudtrail-log-files-from-multiple-regions.html"
                ],
            )
        )

    return findings