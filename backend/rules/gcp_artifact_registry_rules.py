from backend.rules.finding_factory import create_finding


def evaluate_immutable_tags(repo):

    findings = []

    if not repo["immutable_tags"]:

        findings.append(
            create_finding(
                rule_id="GCP-AR-001",
                severity="MEDIUM",
                service="Artifact Registry",
                category="Supply Chain",
                title="Immutable Tags Disabled",
                description=(
                    f"Repository '{repo['name']}' allows image tags to be overwritten."
                ),
                recommendation=(
                    "Enable immutable tags to prevent image tampering."
                ),
                resource_id=repo["resource_id"],
                evidence={
                    "immutable_tags": False
                },
                cis_control="CIS GCP",
                mitre_attack="T1553",
                references=[
                    "https://cloud.google.com/artifact-registry"
                ],
            )
        )

    return findings

def evaluate_kms(repo):

    findings = []

    if not repo["kms_key"]:

        findings.append(
            create_finding(
                rule_id="GCP-AR-002",
                severity="LOW",
                service="Artifact Registry",
                category="Encryption",
                title="Customer Managed Encryption Key Not Used",
                description=(
                    f"Repository '{repo['name']}' uses Google-managed encryption."
                ),
                recommendation=(
                    "Use a Cloud KMS customer-managed key for sensitive repositories."
                ),
                resource_id=repo["resource_id"],
                evidence={
                    "kms_key": None
                },
                cis_control="CIS GCP",
                mitre_attack="T1485",
                references=[
                    "https://cloud.google.com/kms"
                ],
            )
        )

    return findings

def evaluate_repository(repo):

    findings = []

    findings.extend(
        evaluate_immutable_tags(repo)
    )

    findings.extend(
        evaluate_kms(repo)
    )

    return findings        