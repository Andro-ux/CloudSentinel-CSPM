from backend.rules.finding_factory import create_finding


def evaluate_public_ip(instance):

    findings = []

    if instance["public_ip"]:

        findings.append(
            create_finding(
                rule_id="GCP-SQL-001",
                severity="HIGH",
                service="Cloud SQL",
                category="Network Exposure",
                title="Cloud SQL Has Public IP",
                description=(
                    f"Cloud SQL instance '{instance['name']}' "
                    "is publicly reachable."
                ),
                recommendation=(
                    "Disable the public IP or restrict access."
                ),
                resource_id=instance["resource_id"],
                evidence={
                    "public_ip": True
                },
                cis_control="CIS GCP 6.1",
                mitre_attack="T1190",
                references=[
                    "https://cloud.google.com/sql/docs"
                ],
            )
        )

    return findings


def evaluate_backups(instance):

    findings = []

    if not instance["backup_enabled"]:

        findings.append(
            create_finding(
                rule_id="GCP-SQL-002",
                severity="HIGH",
                service="Cloud SQL",
                category="Resilience",
                title="Automated Backups Disabled",
                description=(
                    f"Cloud SQL instance '{instance['name']}' "
                    "does not have automated backups enabled."
                ),
                recommendation=(
                    "Enable automated backups."
                ),
                resource_id=instance["resource_id"],
                evidence={
                    "backup_enabled": False
                },
                cis_control="CIS GCP 6.2",
                mitre_attack="T1490",
                references=[
                    "https://cloud.google.com/sql/docs/backup-recovery"
                ],
            )
        )

    return findings

def evaluate_sql_instance(instance):

    evaluators = [
        evaluate_public_ip,
        evaluate_backups,
    ]

    findings = []

    for evaluator in evaluators:
        findings.extend(
            evaluator(instance)
        )

    return findings    