from backend.rules.finding_factory import create_finding


def evaluate_kms(topic):

    findings = []

    if not topic["kms_key"]:

        findings.append(

            create_finding(

                rule_id="GCP-PUBSUB-001",

                severity="LOW",

                service="Pub/Sub",

                category="Encryption",

                title="Customer Managed Encryption Key Not Used",

                description=(
                    f"Topic '{topic['display_name']}' "
                    "uses Google-managed encryption."
                ),

                recommendation=(
                    "Use Cloud KMS for sensitive topics."
                ),

                resource_id=topic["resource_id"],

                evidence={
                    "kms_key": None
                },

                cis_control="Best Practice",

                mitre_attack="T1485",

                references=[],
            )
        )

    return findings

def evaluate_topic(topic):

    findings = []

    findings.extend(
        evaluate_kms(topic)
    )

    return findings    