from backend.utils.gcp import (
    get_compute_client,
    get_project_id,
)


def collect_nat_gateways():

    compute = get_compute_client()

    project = get_project_id()

    routers = (
        compute.routers()
        .aggregatedList(project=project)
        .execute()
    )

    nat_gateways = []

    for _, scoped in routers.get("items", {}).items():

        for router in scoped.get("routers", []):

            for nat in router.get("nats", []):

                nat_gateways.append({

                    "id": nat.get("name"),

                    "name": nat.get("name"),

                    "router": router.get("name"),

                    "region": router.get("region", "").split("/")[-1],

                    "nat_ip_allocate_option":
                        nat.get("natIpAllocateOption"),

                    "source_subnetwork_ranges":
                        nat.get("sourceSubnetworkIpRangesToNat"),

                    "logging":
                        nat.get("logConfig", {}).get(
                            "enable", False
                        ),

                })

    return nat_gateways