from backend.utils.gcp import get_compute_client, get_project_id


def collect_subnets():

    client = get_compute_client()

    project = get_project_id()

    response = (
        client.subnetworks()
        .aggregatedList(project=project)
        .execute()
    )

    subnets = []
    seen = set()

    for region in response.get("items", {}).values():

        for subnet in region.get("subnetworks", []):

            subnet_id = str(subnet.get("id"))

            if subnet_id in seen:
                continue

            seen.add(subnet_id)

            subnets.append({
                "id": subnet_id,
                "name": subnet.get("name"),
                "network": subnet.get("network", "").split("/")[-1],
                "region": subnet.get("region", "").split("/")[-1],
                "ip_cidr_range": subnet.get("ipCidrRange"),
                "private_ip_google_access": subnet.get(
                    "privateIpGoogleAccess",
                    False,
                ),
                "enable_flow_logs": subnet.get(
                    "enableFlowLogs",
                    False,
                ),
                "description": subnet.get("description", ""),
            })

    return subnets