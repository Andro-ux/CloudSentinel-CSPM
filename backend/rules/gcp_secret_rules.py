from backend.rules.finding_factory import create_finding


def evaluate_replication(secret):

    findings = []

    if secret["replication"] == "automatic":

        findings.append(
            create_finding(
                rule_id="GCP-SECRET-001",
                severity="LOW",
                service="Secret Manager",
                category="Data Protection",
                title="Automatic Secret Replication",
                description=(
                    f"Secret '{secret['name']}' "
                    "uses automatic replication."
                ),
                recommendation=(
                    "Consider user-managed replication if "
                    "specific regional control is required."
                ),
                resource_id=secret["resource_id"],
                evidence={
                    "replication": "automatic"
                },
                cis_control="Best Practice",
                mitre_attack="T1552",
                references=[
                    "https://cloud.google.com/secret-manager/docs"
                ],
            )
        )

    return findings


def evaluate_labels(secret):

    findings = []

    if not secret["labels"]:

        findings.append(
            create_finding(
                rule_id="GCP-SECRET-002",
                severity="LOW",
                service="Secret Manager",
                category="Governance",
                title="Secret Has No Labels",
                description=(
                    f"Secret '{secret['name']}' "
                    "does not have labels."
                ),
                recommendation=(
                    "Use labels for ownership and governance."
                ),
                resource_id=secret["resource_id"],
                evidence={
                    "labels": {}
                },
                cis_control="Best Practice",
                mitre_attack="T1552",
                references=[
                    "https://cloud.google.com/resource-manager/docs/creating-managing-labels"
                ],
            )
        )

    return findings


def evaluate_secret(secret):

    evaluators = [
        evaluate_replication,
        evaluate_labels,
    ]

    findings = []

    for evaluator in evaluators:
        findings.extend(
            evaluator(secret)
        )

    return findings