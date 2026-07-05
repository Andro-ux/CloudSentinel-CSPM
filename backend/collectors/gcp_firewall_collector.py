from backend.utils.gcp import get_compute_client, get_project_id


def collect_firewall_rules():

    client = get_compute_client()

    project = get_project_id()

    response = client.firewalls().list(
        project=project
    ).execute()

    rules = []

    for firewall in response.get("items", []):

        rules.append({
            "id": firewall.get("id"),
            "name": firewall.get("name"),
            "network": firewall.get("network", "").split("/")[-1],
            "direction": firewall.get("direction"),
            "priority": firewall.get("priority"),
            "disabled": firewall.get("disabled", False),
            "source_ranges": firewall.get("sourceRanges", []),
            "destination_ranges": firewall.get("destinationRanges", []),
            "allowed": firewall.get("allowed", []),
            "denied": firewall.get("denied", []),
            "log_config": firewall.get("logConfig"),
            "target_tags": firewall.get("targetTags", []),
            "target_service_accounts": firewall.get(
                "targetServiceAccounts", []
            ),
        })

    return rules