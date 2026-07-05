from backend.rules.finding_factory import create_finding


def evaluate_firewall(rule):

    findings = []

    if rule["direction"] != "INGRESS":
        return findings

    allowed = rule.get("allowed", [])

    source_ranges = rule.get("source_ranges", [])

    internet = "0.0.0.0/0" in source_ranges

    # --------------------------------------------------
    # GCP-FW-001
    # SSH Open to Internet
    # --------------------------------------------------

    for permission in allowed:

        protocol = permission.get("IPProtocol", "").lower()
        ports = permission.get("ports", [])

        if (
            internet
            and protocol == "tcp"
            and "22" in ports
        ):

            findings.append(
                create_finding(
                    rule_id="GCP-FW-001",
                    severity="HIGH",
                    service="Firewall",
                    category="Network Exposure",
                    title="SSH Open to Internet",
                    description=(
                        f"Firewall rule '{rule['name']}' allows SSH "
                        "from anywhere (0.0.0.0/0)."
                    ),
                    recommendation=(
                        "Restrict SSH access to trusted IP ranges or use IAP."
                    ),
                    resource_id=rule["resource_id"],
                    evidence={
                        "source_ranges": source_ranges,
                        "ports": ports,
                    },
                    cis_control="CIS GCP 3.6",
                    mitre_attack="T1021",
                    references=[
                        "https://cloud.google.com/firewall/docs/firewalls"
                    ],
                )
            )

    # --------------------------------------------------
    # GCP-FW-002
    # RDP Open to Internet
    # --------------------------------------------------

    for permission in allowed:

        protocol = permission.get("IPProtocol", "").lower()
        ports = permission.get("ports", [])

        if (
            internet
            and protocol == "tcp"
            and "3389" in ports
        ):

            findings.append(
                create_finding(
                    rule_id="GCP-FW-002",
                    severity="HIGH",
                    service="Firewall",
                    category="Network Exposure",
                    title="RDP Open to Internet",
                    description=(
                        f"Firewall rule '{rule['name']}' allows RDP "
                        "from anywhere."
                    ),
                    recommendation=(
                        "Restrict RDP to trusted IP ranges."
                    ),
                    resource_id=rule["resource_id"],
                    evidence={
                        "source_ranges": source_ranges,
                        "ports": ports,
                    },
                    cis_control="CIS GCP 3.6",
                    mitre_attack="T1021",
                    references=[
                        "https://cloud.google.com/firewall/docs/firewalls"
                    ],
                )
            )

    # --------------------------------------------------
    # GCP-FW-003
    # Firewall Logging Disabled
    # --------------------------------------------------

    if not rule["logging"]:

        findings.append(
            create_finding(
                rule_id="GCP-FW-003",
                severity="LOW",
                service="Firewall",
                category="Monitoring",
                title="Firewall Logging Disabled",
                description=(
                    f"Firewall rule '{rule['name']}' does not have "
                    "logging enabled."
                ),
                recommendation=(
                    "Enable firewall logging for auditability."
                ),
                resource_id=rule["resource_id"],
                evidence={
                    "logging": False
                },
                cis_control="CIS GCP 3.8",
                mitre_attack="T1562",
                references=[
                    "https://cloud.google.com/firewall/docs/firewall-rules-logging"
                ],
            )
        )

    # --------------------------------------------------
    # GCP-FW-004
    # Firewall Rule Disabled
    # --------------------------------------------------

    if rule["disabled"]:

        findings.append(
            create_finding(
                rule_id="GCP-FW-004",
                severity="LOW",
                service="Firewall",
                category="Configuration",
                title="Firewall Rule Disabled",
                description=(
                    f"Firewall rule '{rule['name']}' is disabled."
                ),
                recommendation=(
                    "Remove unused firewall rules or re-enable if required."
                ),
                resource_id=rule["resource_id"],
                evidence={
                    "disabled": True
                },
                cis_control="Internal",
                mitre_attack="T1562",
                references=[],
            )
        )

    return findings