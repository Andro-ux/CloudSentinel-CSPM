def normalize_route(route):

    return {

        "service": "Route",

        "resource_type": "Route",

        "resource_id": str(route["id"]),

        "name": route["name"],

        "network": route["network"],

        "destination": route["dest_range"],

        "priority": route["priority"],

        "next_hop_gateway": route["next_hop_gateway"],

        "next_hop_instance": route["next_hop_instance"],

        "next_hop_ip": route["next_hop_ip"],

        "next_hop_vpn_tunnel": route["next_hop_vpn_tunnel"],

        "tags": route["tags"],

        "description": route["description"],
    }