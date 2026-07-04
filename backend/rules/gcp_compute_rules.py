from backend.rules.finding_factory import create_finding


def evaluate_instance(instance):

    findings = []

    if instance["has_public_ip"]:

        findings.append(
            create_finding(
                rule_id="GCP-COMP-001",
                severity="HIGH",
                service="Compute",
                category="Network Exposure",
                title="VM Has Public IP",
                description=f"{instance['name']} has an external public IP address.",
                recommendation="Remove the public IP or place the VM behind Cloud NAT or a Load Balancer.",
                resource_id=instance["resource_id"],
                evidence={
                    "public_ip": True,
                    "vm": instance["name"]
                },
                cis_control="CIS GCP 4.6",
                mitre_attack="T1190",
                references=[
                    "https://cloud.google.com/compute/docs/ip-addresses"
                ]
            )
        )

    for sa in instance["service_accounts"]:

        if "-compute@developer.gserviceaccount.com" in sa:

            findings.append(
                create_finding(
                    rule_id="GCP-COMP-002",
                    severity="MEDIUM",
                    service="Compute",
                    category="Identity",
                    title="Default Compute Service Account Attached",
                    description=f"{instance['name']} is using the default Compute Engine service account.",
                    recommendation="Attach a dedicated least-privilege service account.",
                    resource_id=instance["resource_id"],
                    evidence={
                        "service_account": sa
                    },
                    cis_control="CIS GCP 1.4",
                    mitre_attack="T1078",
                    references=[
                        "https://cloud.google.com/compute/docs/access/service-accounts"
                    ]
                )
            )

    return findings