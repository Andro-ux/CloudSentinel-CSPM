from backend.rules.finding_factory import create_finding


def evaluate_service_account(service):

    findings = []

    sa = service["service_account"]

    if sa.endswith(
        "-compute@developer.gserviceaccount.com"
    ):

        findings.append(
            create_finding(
                rule_id="GCP-RUN-001",
                severity="HIGH",
                service="Cloud Run",
                category="Identity",
                title="Default Service Account Used",
                description=(
                    f"Cloud Run service "
                    f"'{service['display_name']}' "
                    "uses the default Compute Engine "
                    "service account."
                ),
                recommendation=(
                    "Use a dedicated least-privilege "
                    "service account."
                ),
                resource_id=service["resource_id"],
                evidence={
                    "service_account": sa
                },
                cis_control="Best Practice",
                mitre_attack="T1078",
                references=[
                    "https://cloud.google.com/run"
                ],
            )
        )

    return findings

def evaluate_ingress(service):

    findings = []

    if service["ingress"] == "INGRESS_TRAFFIC_ALL":

        findings.append(
            create_finding(
                rule_id="GCP-RUN-002",
                severity="MEDIUM",
                service="Cloud Run",
                category="Network Exposure",
                title="Cloud Run Allows Public Ingress",
                description=(
                    f"Cloud Run service "
                    f"'{service['display_name']}' "
                    "accepts traffic from all sources."
                ),
                recommendation=(
                    "Restrict ingress where possible."
                ),
                resource_id=service["resource_id"],
                evidence={
                    "ingress": service["ingress"]
                },
                cis_control="Best Practice",
                mitre_attack="T1190",
                references=[
                    "https://cloud.google.com/run"
                ],
            )
        )

    return findings

def evaluate_cloudrun(service):

    findings = []

    findings.extend(
        evaluate_service_account(service)
    )

    findings.extend(
        evaluate_ingress(service)
    )

    return findings        