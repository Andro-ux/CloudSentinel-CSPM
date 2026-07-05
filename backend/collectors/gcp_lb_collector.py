from backend.utils.gcp import (
    get_compute_client,
    get_project_id,
)


def collect_load_balancers():

    compute = get_compute_client()

    project = get_project_id()

    response = (
        compute.forwardingRules()
        .aggregatedList(project=project)
        .execute()
    )

    load_balancers = []

    seen = set()

    for _, scoped in response.get("items", {}).items():

        for rule in scoped.get("forwardingRules", []):

            rule_id = str(rule.get("id"))

            if rule_id in seen:
                continue

            seen.add(rule_id)

            load_balancers.append({

                "id": rule_id,

                "name": rule.get("name"),

                "scheme": rule.get("loadBalancingScheme"),

                "ip_address": rule.get("IPAddress"),

                "ip_protocol": rule.get("IPProtocol"),

                "port_range": rule.get("portRange"),

                "target": rule.get("target"),

                "network": rule.get("network"),

            })

    return load_balancers