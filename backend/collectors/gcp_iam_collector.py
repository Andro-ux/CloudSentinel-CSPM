import logging

from backend.utils.gcp import get_iam_client, get_project_id

logger = logging.getLogger("cloudsentinel.gcp.iam")


def collect_service_accounts():
    client = get_iam_client()

    project_id = get_project_id()

    response = (
        client.projects()
        .serviceAccounts()
        .list(
            name=f"projects/{project_id}"
        )
        .execute()
    )

    return response.get("accounts", [])