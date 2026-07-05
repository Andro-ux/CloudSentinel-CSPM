def normalize_load_balancer(lb):

    return {

        "service": "Load Balancer",

        "resource_type": "LoadBalancer",

        "resource_id": lb["id"],

        "name": lb["name"],

        "scheme": lb["scheme"],

        "ip_address": lb["ip_address"],

        "ip_protocol": lb["ip_protocol"],

        "port_range": lb["port_range"],

        "target": lb["target"],

        "network": lb["network"],
    }