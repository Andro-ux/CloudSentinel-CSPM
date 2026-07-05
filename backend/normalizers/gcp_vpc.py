def normalize_vpc(network):

    return {
        "service": "VPC",

        "resource_type": "Network",

        "resource_id": str(network["id"]),

        "name": network["name"],

        "description": network["description"],

        "auto_mode": network["auto_create_subnetworks"],

        "routing_mode": network["routing_mode"],
    }