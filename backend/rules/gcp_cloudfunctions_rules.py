from backend.rules.finding_factory import create_finding


def evaluate_service_account(function):

    findings = []

    sa = function["service_account"]

    if sa.endswith(
        "-compute@developer.gserviceaccount.com"
    ):

        findings.append(
            create_finding(
                rule_id="GCP-FUNC-001",
                severity="HIGH",
                service="Cloud Functions",
                category="Identity",
                title="Default Service Account Used",
                description=(
                    f"Function '{function['display_name']}' "
                    "uses the default Compute Engine "
                    "service account."
                ),
                recommendation=(
                    "Assign a dedicated least-privilege "
                    "service account."
                ),
                resource_id=function["resource_id"],
                evidence={
                    "service_account": sa
                },
                cis_control="Best Practice",
                mitre_attack="T1078",
                references=[],
            )
        )

    return findings


def evaluate_ingress(function):

    findings = []

    if function["ingress"] == "ALLOW_ALL":

        findings.append(
            create_finding(
                rule_id="GCP-FUNC-002",
                severity="MEDIUM",
                service="Cloud Functions",
                category="Network Exposure",
                title="Function Allows Public Ingress",
                description=(
                    f"Function '{function['display_name']}' "
                    "accepts traffic from all sources."
                ),
                recommendation=(
                    "Restrict ingress where appropriate."
                ),
                resource_id=function["resource_id"],
                evidence={
                    "ingress": function["ingress"]
                },
                cis_control="Best Practice",
                mitre_attack="T1190",
                references=[],
            )
        )

    return findings


def evaluate_function(function):

    findings = []

    findings.extend(
        evaluate_service_account(function)
    )

    findings.extend(
        evaluate_ingress(function)
    )

    return findings