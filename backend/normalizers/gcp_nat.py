def normalize_nat(nat):

    return {

        "service": "Cloud NAT",

        "resource_type": "NAT",

        "resource_id": nat["id"],

        "name": nat["name"],

        "router": nat["router"],

        "region": nat["region"],

        "nat_ip_allocate_option":
            nat["nat_ip_allocate_option"],

        "source_ranges":
            nat["source_subnetwork_ranges"],

        "logging":
            nat["logging"],
    }