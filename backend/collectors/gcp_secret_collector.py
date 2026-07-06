from backend.utils.gcp import (
    get_secretmanager_client,
    get_project_id,
)


def collect_secrets():

    client = get_secretmanager_client()

    project = get_project_id()

    parent = f"projects/{project}"

    response = client.list_secrets(
        request={"parent": parent}
    )

    secrets = []

    for secret in response:

        secrets.append({

            "id": secret.name,

            "name": secret.name.split("/")[-1],

            "replication": (
                "automatic"
                if secret.replication.automatic
                else "user-managed"
            ),

            "labels": dict(secret.labels),

            "create_time": str(secret.create_time),

        })

    return secrets