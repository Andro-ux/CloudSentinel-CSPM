from backend.utils.gcp import (
    get_compute_client,
    get_project_id,
)

from backend.utils.collector_helper import safe_execute


def collect_instances():

    compute = get_compute_client()
    project = get_project_id()

    response = safe_execute(
        compute.instances().aggregatedList(
            project=project
        )
    )

    if response is None:
        return []

    instances = []

    for _, zone in response.get("items", {}).items():

        for instance in zone.get("instances", []):

            instances.append(instance)

    return instances