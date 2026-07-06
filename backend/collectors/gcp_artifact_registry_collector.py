from google.api_core.exceptions import (
    PermissionDenied,
    NotFound,
)

from backend.utils.gcp import (
    get_artifact_registry_client,
    get_project_id,
)


LOCATIONS = [
    "us-central1",
    "us-east1",
    "us-west1",
    "us-west2",
    "us-west3",
    "us-west4",
    "europe-west1",
    "europe-west2",
    "europe-west3",
    "europe-west4",
    "europe-west6",
    "asia-east1",
    "asia-east2",
    "asia-northeast1",
    "asia-northeast2",
    "asia-south1",
    "asia-southeast1",
]


def collect_repositories():

    client = get_artifact_registry_client()

    project = get_project_id()

    repositories = []

    for location in LOCATIONS:

        parent = f"projects/{project}/locations/{location}"

        try:

            repos = client.list_repositories(
                request={
                    "parent": parent
                }
            )

            repositories.extend(list(repos))

        except (PermissionDenied, NotFound):

            continue

    return repositories