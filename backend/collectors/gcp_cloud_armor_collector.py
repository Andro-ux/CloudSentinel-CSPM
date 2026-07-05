from backend.utils.gcp import (
    get_compute_client,
    get_project_id,
)


def collect_cloud_armor_policies():

    compute = get_compute_client()

    project = get_project_id()

    response = (
        compute.securityPolicies()
        .list(project=project)
        .execute()
    )

    policies = []

    for policy in response.get("items", []):

        policies.append({

            "id": str(policy.get("id")),

            "name": policy.get("name"),

            "description": policy.get("description"),

            "type": policy.get("type"),

            "rules": policy.get("rules", []),

        })

    return policies