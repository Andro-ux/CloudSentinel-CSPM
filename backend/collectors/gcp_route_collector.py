from backend.utils.gcp import get_compute_client, get_project_id


def collect_routes():

    client = get_compute_client()

    project = get_project_id()

    response = (
        client.routes()
        .list(project=project)
        .execute()
    )

    routes = []

    for route in response.get("items", []):

        routes.append({
            "id": route.get("id"),
            "name": route.get("name"),
            "network": route.get("network", "").split("/")[-1],
            "dest_range": route.get("destRange"),
            "priority": route.get("priority"),
            "next_hop_gateway": route.get("nextHopGateway"),
            "next_hop_instance": route.get("nextHopInstance"),
            "next_hop_ip": route.get("nextHopIp"),
            "next_hop_vpn_tunnel": route.get("nextHopVpnTunnel"),
            "tags": route.get("tags", []),
            "description": route.get("description", ""),
        })

    return routes