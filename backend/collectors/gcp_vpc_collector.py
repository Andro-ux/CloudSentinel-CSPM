from backend.utils.gcp import get_compute_client, get_project_id


def collect_vpcs():

    client = get_compute_client()

    project = get_project_id()

    response = (
        client.networks()
        .list(project=project)
        .execute()
    )

    networks = []

    for network in response.get("items", []):

        networks.append({
            "id": network.get("id"),
            "name": network.get("name"),
            "description": network.get("description"),
            "auto_create_subnetworks": network.get(
                "autoCreateSubnetworks",
                False,
            ),
            "routing_mode": network.get("routingConfig", {}).get(
                "routingMode",
                "REGIONAL",
            ),
            "self_link": network.get("selfLink"),
        })

    return networks