from backend.rules.finding_factory import create_finding

def evaluate_private_cluster(cluster):

    findings = []

    if not cluster["private_cluster"]:

        findings.append(
            create_finding(
                rule_id="GCP-GKE-001",
                severity="HIGH",
                service="GKE",
                category="Network Exposure",
                title="Private Cluster Disabled",
                description=(
                    f"GKE cluster '{cluster['name']}' "
                    "is publicly accessible."
                ),
                recommendation=(
                    "Enable Private Cluster."
                ),
                resource_id=cluster["resource_id"],
                evidence={
                    "private_cluster": False
                },
                cis_control="CIS GKE 6.6",
                mitre_attack="T1190",
                references=[
                    "https://cloud.google.com/kubernetes-engine"
                ],
            )
        )

    return findings

def evaluate_network_policy(cluster):

    findings = []

    if not cluster["network_policy"]:

        findings.append(
            create_finding(
                rule_id="GCP-GKE-002",
                severity="HIGH",
                service="GKE",
                category="Network Security",
                title="Network Policy Disabled",
                description=(
                    f"GKE cluster '{cluster['name']}' "
                    "does not enforce Network Policies."
                ),
                recommendation=(
                    "Enable Kubernetes Network Policies."
                ),
                resource_id=cluster["resource_id"],
                evidence={
                    "network_policy": False
                },
                cis_control="CIS GKE 6.8",
                mitre_attack="T1562",
                references=[
                    "https://cloud.google.com/kubernetes-engine"
                ],
            )
        )

    return findings    

def evaluate_shielded_nodes(cluster):

    findings = []

    if not cluster["shielded_nodes"]:

        findings.append(
            create_finding(
                rule_id="GCP-GKE-003",
                severity="MEDIUM",
                service="GKE",
                category="Node Security",
                title="Shielded Nodes Disabled",
                description=(
                    f"GKE cluster '{cluster['name']}' "
                    "does not use Shielded Nodes."
                ),
                recommendation=(
                    "Enable Shielded GKE Nodes."
                ),
                resource_id=cluster["resource_id"],
                evidence={
                    "shielded_nodes": False
                },
                cis_control="CIS GKE 6.5",
                mitre_attack="T1068",
                references=[
                    "https://cloud.google.com/kubernetes-engine"
                ],
            )
        )

    return findings

def evaluate_workload_identity(cluster):

    findings = []

    if not cluster["workload_identity"]:

        findings.append(
            create_finding(
                rule_id="GCP-GKE-004",
                severity="HIGH",
                service="GKE",
                category="Identity",
                title="Workload Identity Disabled",
                description=(
                    f"GKE cluster '{cluster['name']}' "
                    "is not using Workload Identity."
                ),
                recommendation=(
                    "Enable Workload Identity."
                ),
                resource_id=cluster["resource_id"],
                evidence={
                    "workload_identity": False
                },
                cis_control="CIS GKE 6.3",
                mitre_attack="T1078",
                references=[
                    "https://cloud.google.com/kubernetes-engine"
                ],
            )
        )

    return findings

def evaluate_cluster(cluster):

    evaluators = [

        evaluate_private_cluster,

        evaluate_network_policy,

        evaluate_shielded_nodes,

        evaluate_workload_identity,
    ]

    findings = []

    for evaluator in evaluators:

        findings.extend(
            evaluator(cluster)
        )

    return findings            