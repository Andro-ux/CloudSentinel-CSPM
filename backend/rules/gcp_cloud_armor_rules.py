from backend.rules.finding_factory import create_finding


def evaluate_cloud_armor(policy):

    findings = []

    if len(policy["rules"]) == 0:

        findings.append(

            create_finding(

                rule_id="GCP-ARMOR-001",

                severity="HIGH",

                service="Cloud Armor",

                category="Web Protection",

                title="Cloud Armor Policy Has No Rules",

                description=(
                    f"Cloud Armor policy '{policy['name']}' "
                    "contains no security rules."
                ),

                recommendation=(
                    "Configure WAF rules to protect workloads."
                ),

                resource_id=policy["resource_id"],

                evidence={
                    "rules": 0
                },

                cis_control="Best Practice",

                mitre_attack="T1190",

                references=[
                    "https://cloud.google.com/armor"
                ],
            )
        )

    return findings