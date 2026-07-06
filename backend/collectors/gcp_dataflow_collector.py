from backend.utils.gcp import (
    get_dataflow_client,
    get_project_id,
)

from backend.utils.collector_helper import safe_execute


def collect_jobs():

    client = get_dataflow_client()

    project = get_project_id()

    request = {
        "project_id": project,
        "location": "-"
    }

    response = safe_execute(
        client.list_jobs(request=request)
    )

    if response is None:
        return []

    return list(response.jobs)