from backend.utils.gcp import (
    get_bigquery_client,
)

from google.api_core.exceptions import GoogleAPIError


def collect_datasets():

    client = get_bigquery_client()

    try:

        datasets = client.list_datasets()

        results = []

        for dataset in datasets:

            results.append(
                client.get_dataset(dataset.reference)
            )

        return results

    except GoogleAPIError as e:

        print(f"[Collector] {e}")

        return []