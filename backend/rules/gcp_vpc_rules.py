from backend.rules.finding_factory import create_finding


def evaluate_vpc(network):

    findings = []

    # ----------------------------------------
    # GCP-VPC-001
    # Default Network
    # ----------------------------------------

    if network["name"] == "default":

        findings.append(
            create_finding(
                rule_id="GCP-VPC-001",
                severity="HIGH",
                service="VPC",
                category="Network Configuration",
                title="Default VPC Network Exists",
                description=(
                    "The default VPC network is present."
                ),
                recommendation=(
                    "Delete the default VPC network and create custom VPCs."
                ),
                resource_id=network["resource_id"],
                evidence={
                    "network": network["name"]
                },
                cis_control="CIS GCP 3.1",
                mitre_attack="T1190",
                references=[
                    "https://cloud.google.com/vpc/docs/vpc"
                ],
            )
        )

    # ----------------------------------------
    # GCP-VPC-002
    # Auto Mode Network
    # ----------------------------------------

    if network["auto_mode"]:

        findings.append(
            create_finding(
                rule_id="GCP-VPC-002",
                severity="MEDIUM",
                service="VPC",
                category="Network Configuration",
                title="Auto Mode VPC",
                description=(
                    f"VPC '{network['name']}' uses Auto Mode."
                ),
                recommendation=(
                    "Prefer Custom Mode VPCs for production environments."
                ),
                resource_id=network["resource_id"],
                evidence={
                    "auto_mode": True
                },
                cis_control="CIS GCP 3.2",
                mitre_attack="T1190",
                references=[
                    "https://cloud.google.com/vpc/docs/vpc"
                ],
            )
        )

    return findings