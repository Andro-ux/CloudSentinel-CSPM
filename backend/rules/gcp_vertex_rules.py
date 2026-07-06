from backend.rules.finding_factory import create_finding


def evaluate_kms(endpoint):

    findings = []

    if not endpoint["kms_key"]:

        findings.append(

            create_finding(

                rule_id="GCP-VERTEX-001",

                severity="LOW",

                service="Vertex AI",

                category="Encryption",

                title="Vertex AI Endpoint Not Using CMEK",

                description=(
                    f"Endpoint '{endpoint['display_name']}' "
                    "uses Google-managed encryption."
                ),

                recommendation=(
                    "Protect sensitive AI workloads using "
                    "Cloud KMS."
                ),

                resource_id=endpoint["resource_id"],

                evidence={
                    "kms_key": None
                },

                cis_control="Best Practice",

                mitre_attack="T1485",

                references=[],
            )
        )

    return findings


def evaluate_network(endpoint):

    findings = []

    if not endpoint["network"]:

        findings.append(

            create_finding(

                rule_id="GCP-VERTEX-002",

                severity="MEDIUM",

                service="Vertex AI",

                category="Network",

                title="Endpoint Not Attached To VPC",

                description=(
                    f"Endpoint '{endpoint['display_name']}' "
                    "is not attached to a private network."
                ),

                recommendation=(
                    "Use Private Service Connect or a VPC "
                    "for production deployments."
                ),

                resource_id=endpoint["resource_id"],

                evidence={
                    "network": None
                },

                cis_control="Best Practice",

                mitre_attack="T1190",

                references=[],
            )
        )

    return findings


def evaluate_endpoint(endpoint):

    findings = []

    findings.extend(
        evaluate_kms(endpoint)
    )

    findings.extend(
        evaluate_network(endpoint)
    )

    return findings