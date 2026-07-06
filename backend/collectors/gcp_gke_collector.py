from backend.utils.gcp import (
    get_container_client,
    get_project_id,
)


def collect_clusters():

    client = get_container_client()

    project = get_project_id()

    parent = f"projects/{project}/locations/-"

    response = client.list_clusters(
        request={
            "parent": parent
        }
    )

    return response.clusters