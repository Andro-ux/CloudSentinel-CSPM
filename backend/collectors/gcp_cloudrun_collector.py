from google.api_core.exceptions import (
    PermissionDenied,
    NotFound,
)

from backend.utils.gcp import (
    get_run_client,
    get_project_id,
)

LOCATIONS = [
    "us-central1",
    "us-east1",
    "us-west1",
    "europe-west1",
    "europe-west2",
    "asia-east1",
    "asia-south1",
    "asia-southeast1",
]


def collect_services():

    client = get_run_client()

    project = get_project_id()

    services = []

    for location in LOCATIONS:

        parent = (
            f"projects/{project}"
            f"/locations/{location}"
        )

        try:

            response = client.list_services(
                request={
                    "parent": parent
                }
            )

            services.extend(list(response))

        except (PermissionDenied, NotFound):

            continue

    return services