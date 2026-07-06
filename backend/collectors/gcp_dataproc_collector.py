from backend.utils.gcp import get_dataproc_client, get_project_id
from backend.utils.collector_helper import safe_execute


REGIONS = [

    "us-central1",
    "us-east1",
    "us-east4",
    "us-west1",
    "us-west2",

    "northamerica-northeast1",

    "europe-west1",
    "europe-west2",
    "europe-west3",
    "europe-west4",

    "asia-east1",
    "asia-east2",
    "asia-south1",
    "asia-southeast1",

    "australia-southeast1",
]


def collect_clusters():

    project = get_project_id()

    clusters = []

    for region in REGIONS:

        client = get_dataproc_client(region)

        response = safe_execute(

            client.list_clusters(

                request={
                    "project_id": project,
                    "region": region,
                }

            )

        )

        if response is None:
            continue

        clusters.extend(response.clusters)

    return clusters