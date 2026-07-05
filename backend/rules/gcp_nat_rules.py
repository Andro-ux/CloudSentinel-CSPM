from backend.rules.finding_factory import create_finding


def evaluate_nat(nat):

    findings = []

    # -----------------------------
    # GCP-NAT-001
    # -----------------------------

    if not nat["logging"]:

        findings.append(
            create_finding(
                rule_id="GCP-NAT-001",
                severity="LOW",
                service="Cloud NAT",
                category="Monitoring",
                title="Cloud NAT Logging Disabled",
                description=(
                    f"Cloud NAT '{nat['name']}' "
                    "does not have logging enabled."
                ),
                recommendation=(
                    "Enable Cloud NAT logging."
                ),
                resource_id=nat["resource_id"],
                evidence={
                    "logging": False
                },
                cis_control="Best Practice",
                mitre_attack="T1040",
                references=[
                    "https://cloud.google.com/nat/docs"
                ],
            )
        )

    return findings