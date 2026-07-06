from backend.rules.finding_factory import create_finding


def evaluate_internal_ip(cluster):

    findings = []

    if not cluster["internal_ip_only"]:

        findings.append(
            create_finding(
                rule_id="GCP-DP-001",
                severity="HIGH",
                service="Dataproc",
                category="Network",
                title="Dataproc Cluster Uses External IPs",
                description=(
                    f"Cluster '{cluster['display_name']}' "
                    "allows external IP addresses."
                ),
                recommendation=(
                    "Use internal IP only clusters whenever possible."
                ),
                resource_id=cluster["resource_id"],
                evidence={
                    "internal_ip_only": False
                },
                cis_control="Best Practice",
                mitre_attack="T1190",
                references=[],
            )
        )

    return findings


def evaluate_shielded_vm(cluster):

    findings = []

    if not cluster["shielded_vm"]:

        findings.append(
            create_finding(
                rule_id="GCP-DP-002",
                severity="MEDIUM",
                service="Dataproc",
                category="Compute Security",
                title="Shielded VM Disabled",
                description=(
                    f"Cluster '{cluster['display_name']}' "
                    "does not use Shielded VM."
                ),
                recommendation=(
                    "Enable Shielded VM Secure Boot."
                ),
                resource_id=cluster["resource_id"],
                evidence={
                    "shielded_vm": False
                },
                cis_control="Best Practice",
                mitre_attack="T1562",
                references=[],
            )
        )

    return findings


def evaluate_kms(cluster):

    findings = []

    if not cluster["kms_key"]:

        findings.append(
            create_finding(
                rule_id="GCP-DP-003",
                severity="MEDIUM",
                service="Dataproc",
                category="Encryption",
                title="Customer Managed Encryption Not Used",
                description=(
                    f"Cluster '{cluster['display_name']}' "
                    "uses Google-managed encryption."
                ),
                recommendation=(
                    "Protect disks using Cloud KMS."
                ),
                resource_id=cluster["resource_id"],
                evidence={
                    "kms_key": None
                },
                cis_control="Best Practice",
                mitre_attack="T1485",
                references=[],
            )
        )

    return findings


def evaluate_labels(cluster):

    findings = []

    if not cluster["labels"]:

        findings.append(
            create_finding(
                rule_id="GCP-DP-004",
                severity="LOW",
                service="Dataproc",
                category="Governance",
                title="Cluster Has No Labels",
                description=(
                    f"Cluster '{cluster['display_name']}' "
                    "has no labels."
                ),
                recommendation=(
                    "Apply owner, environment and cost-center labels."
                ),
                resource_id=cluster["resource_id"],
                evidence={
                    "labels": {}
                },
                cis_control="Internal",
                mitre_attack="T1580",
                references=[],
            )
        )

    return findings


def evaluate_cluster(cluster):

    findings = []

    findings.extend(
        evaluate_internal_ip(cluster)
    )

    findings.extend(
        evaluate_shielded_vm(cluster)
    )

    findings.extend(
        evaluate_kms(cluster)
    )

    findings.extend(
        evaluate_labels(cluster)
    )

    return findings