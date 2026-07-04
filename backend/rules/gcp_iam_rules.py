from backend.rules.finding_factory import create_finding


def evaluate_service_account(sa):

    findings = []

    if "compute@developer.gserviceaccount.com" in sa["email"]:

        findings.append(
            create_finding(
                rule_id="GCP-IAM-001",
                severity="MEDIUM",
                service="IAM",
                category="Identity",
                title="Default Service Account Detected",
                description=(
                    f"{sa['email']} is the default Compute Engine service account."
                ),
                recommendation=(
                    "Create a dedicated least-privilege service account instead of using the default Compute Engine service account."
                ),
                resource_id=sa["resource_id"],
                evidence={
                    "service_account": sa["email"]
                },
                cis_control="CIS GCP 1.4",
                mitre_attack="T1078",
                references=[
                    "https://cloud.google.com/iam/docs/service-accounts"
                ],
            )
        )

    return findings