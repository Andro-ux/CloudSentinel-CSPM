from backend.rules.finding_factory import create_finding


def evaluate_route(route):

    findings = []

    # ----------------------------------------
    # GCP-ROUTE-001
    # Default Internet Route
    # ----------------------------------------

    if (
        route["destination"] == "0.0.0.0/0"
        and route["next_hop_gateway"]
    ):

        findings.append(
            create_finding(
                rule_id="GCP-ROUTE-001",
                severity="MEDIUM",
                service="Route",
                category="Network Configuration",
                title="Default Internet Route",
                description=(
                    f"Route '{route['name']}' sends "
                    "0.0.0.0/0 traffic to the Internet."
                ),
                recommendation=(
                    "Review whether unrestricted outbound Internet "
                    "access is required."
                ),
                resource_id=route["resource_id"],
                evidence={
                    "destination": route["destination"],
                    "gateway": route["next_hop_gateway"],
                },
                cis_control="Best Practice",
                mitre_attack="T1090",
                references=[
                    "https://cloud.google.com/vpc/docs/routes"
                ],
            )
        )

    # ----------------------------------------
    # GCP-ROUTE-002
    # Missing Description
    # ----------------------------------------

    if not route["description"]:

        findings.append(
            create_finding(
                rule_id="GCP-ROUTE-002",
                severity="LOW",
                service="Route",
                category="Governance",
                title="Route Missing Description",
                description=(
                    f"Route '{route['name']}' has no description."
                ),
                recommendation=(
                    "Add a meaningful description."
                ),
                resource_id=route["resource_id"],
                evidence={},
                cis_control="Internal",
                mitre_attack="T1580",
                references=[],
            )
        )

    return findings