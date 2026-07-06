from backend.utils.gcp import (
    get_vertex_ai_client,
    get_project_id,
)

from backend.utils.collector_helper import safe_execute


def collect_endpoints():

    client = get_vertex_ai_client()

    parent = (
        f"projects/{get_project_id()}"
        "/locations/global"
    )

    response = safe_execute(
        client.list_endpoints(
            request={
                "parent": parent
            }
        )
    )

    if response is None:
        return []

    return list(response)