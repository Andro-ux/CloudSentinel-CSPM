def normalize_subnet(subnet):

    return {

        "service": "Subnet",

        "resource_type": "Subnet",

        "resource_id": str(subnet["id"]),

        "name": subnet["name"],

        "network": subnet["network"],

        "region": subnet["region"],

        "cidr": subnet["ip_cidr_range"],

        "private_google_access": subnet[
            "private_ip_google_access"
        ],

        "flow_logs": subnet["enable_flow_logs"],

        "description": subnet["description"],
    }