from backend.models.schemas import NormalizedResource
from backend.rules.finding_factory import create_finding


def evaluate_security_group(resource: NormalizedResource):
    findings = []

    config = resource.configuration
    ip_permissions = config.get("IpPermissions", [])

    for perm in ip_permissions:

        from_port = perm.get("FromPort")
        to_port = perm.get("ToPort")
        ip_ranges = perm.get("IpRanges", [])

        is_public = any(
            r.get("CidrIp") == "0.0.0.0/0"
            for r in ip_ranges
        )

        if not is_public:
            continue

        #
        # Public SSH
        #
        if from_port == 22 or to_port == 22:

            findings.append(
                create_finding(
                    rule_id="CS-EC2-001",
                    severity="CRITICAL",
                    service="EC2",
                    category="Network Security",
                    resource_id=resource.resource_id,
                    title="SSH Port Exposed to Internet",
                    description="Security group allows unrestricted inbound SSH access.",
                    recommendation="Restrict SSH (22) to trusted IP addresses or VPN ranges.",
                    evidence={
                        "IpPermission": perm
                    },
                    cis_control="4.1",
                    mitre_attack="T1021.004",
                    references=[
                        "https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html"
                    ],
                )
            )

        #
        # Public RDP
        #
        if from_port == 3389 or to_port == 3389:

            findings.append(
                create_finding(
                    rule_id="CS-EC2-002",
                    severity="CRITICAL",
                    service="EC2",
                    category="Network Security",
                    resource_id=resource.resource_id,
                    title="RDP Port Exposed to Internet",
                    description="Security group allows unrestricted inbound RDP access.",
                    recommendation="Restrict RDP (3389) to trusted IP addresses.",
                    evidence={
                        "IpPermission": perm
                    },
                    cis_control="4.1",
                    mitre_attack="T1021.001",
                    references=[
                        "https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html"
                    ],
                )
            )

        #
        # All Traffic
        #
        if (
            from_port is None
            and to_port is None
            and perm.get("IpProtocol") == "-1"
        ):

            findings.append(
                create_finding(
                    rule_id="CS-EC2-003",
                    severity="CRITICAL",
                    service="EC2",
                    category="Network Security",
                    resource_id=resource.resource_id,
                    title="All Network Traffic Exposed",
                    description="Security group allows all inbound traffic from the Internet.",
                    recommendation="Restrict inbound rules to required protocols, ports and trusted IP ranges.",
                    evidence={
                        "IpPermission": perm
                    },
                    cis_control="4.1",
                    mitre_attack="T1190",
                    references=[
                        "https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html"
                    ],
                )
            )

    return findings