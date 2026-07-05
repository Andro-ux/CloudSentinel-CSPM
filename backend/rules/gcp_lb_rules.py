from backend.rules.finding_factory import create_finding


def evaluate_load_balancer(lb):

    findings = []

    # -----------------------------------
    # GCP-LB-001
    # External Load Balancer
    # -----------------------------------

    if lb["scheme"] == "EXTERNAL":

        findings.append(
            create_finding(
                rule_id="GCP-LB-001",
                severity="LOW",
                service="Load Balancer",
                category="Network Exposure",
                title="External Load Balancer",
                description=(
                    f"Load Balancer '{lb['name']}' "
                    "is Internet-facing."
                ),
                recommendation=(
                    "Verify that public exposure is intended."
                ),
                resource_id=lb["resource_id"],
                evidence={
                    "scheme": lb["scheme"]
                },
                cis_control="Best Practice",
                mitre_attack="T1190",
                references=[
                    "https://cloud.google.com/load-balancing"
                ],
            )
        )

    # -----------------------------------
    # GCP-LB-002
    # HTTP Load Balancer
    # -----------------------------------

    if lb["ip_protocol"] == "TCP":

        if lb["port_range"] == "80":

            findings.append(
                create_finding(
                    rule_id="GCP-LB-002",
                    severity="HIGH",
                    service="Load Balancer",
                    category="Encryption",
                    title="HTTP Load Balancer",
                    description=(
                        f"Load Balancer '{lb['name']}' "
                        "appears to expose HTTP."
                    ),
                    recommendation=(
                        "Prefer HTTPS for Internet-facing applications."
                    ),
                    resource_id=lb["resource_id"],
                    evidence={
                        "port": lb["port_range"]
                    },
                    cis_control="Best Practice",
                    mitre_attack="T1040",
                    references=[
                        "https://cloud.google.com/load-balancing"
                    ],
                )
            )

    return findings