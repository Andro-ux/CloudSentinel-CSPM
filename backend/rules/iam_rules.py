from backend.models.schemas import NormalizedResource
from backend.rules.finding_factory import create_finding


def evaluate_iam_user(resource: NormalizedResource):
    findings = []
    config = resource.configuration

    for pol in config.get("AttachedPolicies", []):
        if pol.get("PolicyName") == "AdministratorAccess":
            findings.append(
                create_finding(
                    rule_id="CS-IAM-001",
                    severity="CRITICAL",
                    service="IAM",
                    category="Identity and Access Management",
                    resource_id=resource.resource_id,
                    title="IAM User has AdministratorAccess",
                    description="User is attached to the AdministratorAccess managed policy.",
                    recommendation="Replace AdministratorAccess with least-privilege permissions.",
                    evidence={"AttachedPolicy": pol},
                    cis_control="1.16",
                    mitre_attack="T1078",
                    references=[
                        "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html"
                    ],
                )
            )

    return findings


def evaluate_iam_credential(resource: NormalizedResource):
    findings = []
    config = resource.configuration

    if (
        config.get("mfa_active", "false").lower() == "false"
        and config.get("password_enabled", "false").lower() == "true"
    ):
        findings.append(
            create_finding(
                rule_id="CS-IAM-002",
                severity="HIGH",
                service="IAM",
                category="Identity Protection",
                resource_id=resource.resource_id,
                title="MFA Not Enabled for IAM User",
                description="Console password is enabled but MFA is not configured.",
                recommendation="Enable MFA for all IAM users with console access.",
                evidence={
                    "mfa_active": config.get("mfa_active"),
                    "password_enabled": config.get("password_enabled"),
                },
                cis_control="1.2",
                mitre_attack="T1078",
                references=[
                    "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa.html"
                ],
            )
        )

    return findings
