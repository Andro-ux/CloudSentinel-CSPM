from backend.utils.gcp import (
    get_pubsub_publisher_client,
    get_project_id,
)


def collect_topics():

    client = get_pubsub_publisher_client()

    project = get_project_id()

    parent = client.common_project_path(
        project
    )

    topics = client.list_topics(
        request={
            "project": parent
        }
    )

    return list(topics)