from backend.utils.gcp import get_compute_client, get_project_id


def collect_instances():
    client = get_compute_client()

    project = get_project_id()

    response = client.instances().aggregatedList(
        project=project
    ).execute()

    instances = []

    for zone, value in response.get("items", {}).items():

        for instance in value.get("instances", []):

            instances.append({
                "id": instance.get("id"),
                "name": instance.get("name"),
                "zone": instance.get("zone", "").split("/")[-1],
                "machine_type": instance.get("machineType", "").split("/")[-1],
                "status": instance.get("status"),
                "network_interfaces": instance.get("networkInterfaces", []),
                "service_accounts": instance.get("serviceAccounts", [])
            })

    return instances