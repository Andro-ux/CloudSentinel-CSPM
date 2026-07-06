from backend.utils.gcp import (
    get_cloudfunctions_client,
    get_project_id,
)

from backend.utils.collector_helper import safe_execute


def collect_functions():

    client = get_cloudfunctions_client()

    parent = (
        f"projects/{get_project_id()}"
        "/locations/-"
    )

    response = safe_execute(
        client.projects()
        .locations()
        .functions()
        .list(parent=parent)
    )

    if response is None:
        return []

    return response.get(
        "functions",
        []
    )