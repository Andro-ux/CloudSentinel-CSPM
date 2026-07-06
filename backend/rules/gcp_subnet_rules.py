from ipaddress import ip_network

from backend.rules.finding_factory import create_finding


def evaluate_subnet(subnet):

    findings = []

    # ---------------------------------------
    # GCP-SUBNET-001
    # Flow Logs Disabled
    # ---------------------------------------

    if not subnet["flow_logs"]:

        findings.append(
            create_finding(
                rule_id="GCP-SUBNET-001",
                severity="MEDIUM",
                service="Subnet",
                category="Monitoring",
                title="VPC Flow Logs Disabled",
                description=(
                    f"Subnet '{subnet['display_name']}' does not have "
                    "VPC Flow Logs enabled."
                ),
                recommendation=(
                    "Enable VPC Flow Logs for network visibility."
                ),
                resource_id=subnet["resource_id"],
                evidence={
                    "flow_logs": False
                },
                cis_control="CIS GCP 3.9",
                mitre_attack="T1040",
                references=[
                    "https://cloud.google.com/vpc/docs/flow-logs"
                ],
            )
        )

    # ---------------------------------------
    # GCP-SUBNET-002
    # Private Google Access Disabled
    # ---------------------------------------

    if not subnet["private_google_access"]:

        findings.append(
            create_finding(
                rule_id="GCP-SUBNET-002",
                severity="MEDIUM",
                service="Subnet",
                category="Network Configuration",
                title="Private Google Access Disabled",
                description=(
                    f"Subnet '{subnet['display_name']}' does not have "
                    "Private Google Access enabled."
                ),
                recommendation=(
                    "Enable Private Google Access where appropriate."
                ),
                resource_id=subnet["resource_id"],
                evidence={
                    "private_google_access": False
                },
                cis_control="Best Practice",
                mitre_attack="T1190",
                references=[
                    "https://cloud.google.com/vpc/docs/private-google-access"
                ],
            )
        )

    # ---------------------------------------
    # GCP-SUBNET-003
    # Missing Description
    # ---------------------------------------

    if not subnet["description"]:

        findings.append(
            create_finding(
                rule_id="GCP-SUBNET-003",
                severity="LOW",
                service="Subnet",
                category="Governance",
                title="Subnet Missing Description",
                description=(
                    f"Subnet '{subnet['display_name']}' has no description."
                ),
                recommendation=(
                    "Add a meaningful description."
                ),
                resource_id=subnet["resource_id"],
                evidence={},
                cis_control="Internal",
                mitre_attack="T1580",
                references=[],
            )
        )

    # ---------------------------------------
    # GCP-SUBNET-004
    # Large CIDR
    # ---------------------------------------

    network = ip_network(subnet["cidr"], strict=False)

    if network.prefixlen < 20:

        findings.append(
            create_finding(
                rule_id="GCP-SUBNET-004",
                severity="LOW",
                service="Subnet",
                category="Network Design",
                title="Large Subnet CIDR",
                description=(
                    f"Subnet '{subnet['display_name']}' uses "
                    f"{subnet['cidr']}."
                ),
                recommendation=(
                    "Review whether a smaller subnet is sufficient."
                ),
                resource_id=subnet["resource_id"],
                evidence={
                    "cidr": subnet["cidr"]
                },
                cis_control="Internal",
                mitre_attack="T1583",
                references=[],
            )
        )

    return findings